import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
from datetime import datetime
import os
import sys
import matplotlib.cm as cm
from matplotlib.colors import Normalize
from matplotlib.colorbar import ColorbarBase
from matplotlib.transforms import Bbox

# Set local library directory
local_lib = "./python_libraries"
if not os.path.exists(local_lib):
    os.makedirs(local_lib)

# Define regions with corner coordinates and output filenames
regions = [
    {
        'name': 'Thailand',
        'CornerLeft': (21.154163, 91.521542),  # (lat, lon) of upper-left
        'CornerRight': (0.354838, 109.671551), # (lat, lon) of lower-right
        'output_file': '/wD/occurrences_map.svg'
    },
    {
        'name': 'Southeast_Asia',
        'CornerLeft': (23.0, 90.0),  # Covers from Myanmar to Philippines
        'CornerRight': (-11.0, 141.0),
        'output_file': '/wD/occurrences_map_seasia.svg'
    },
    {
        'name': 'World',
        'CornerLeft': (90.0, -180.0),  # Global extent
        'CornerRight': (-90.0, 180.0),
        'output_file': '/wD/occurrences_map_world.svg'
    }
]

# Read CSV file

csv_file = "/wD/input.csv"
if len(sys.argv) > 1:
    csv_file = sys.argv[1]

outf = "output.svg"
if len(sys.argv) > 2:
    outf = sys.argv[2]

map_name = "Entero virus occuernces"
if len(sys.argv) > 3:
    map_name = sys.argv[3]

if not os.path.exists(csv_file):
    raise FileNotFoundError(f"CSV file '{csv_file}' not found. Please provide the correct file path.")
df = pd.read_csv(csv_file, sep=",", header=None, names=["name", "lat", "lon", "time"])

# Validate DataFrame structure and types
if len(df.columns) != 4:
    raise ValueError(f"CSV file must have exactly 4 columns, found {len(df.columns)}.")
df = df.dropna()
df = df[df.notnull().sum(axis=1) == 4]
for idx, row in df.iterrows():
    if not isinstance(row['name'], str) or row['name'].strip() == '':
        raise ValueError(f"Row {idx}: 'name' must be a non-empty string, found {row['name']}.")
    try:
        lat = float(row['lat'])
        lon = float(row['lon'])
        if not (-90 <= lat <= 90):
            raise ValueError(f"Row {idx}: 'lat' must be between -90 and 90, found {row['lat']}.")
        if not (-180 <= lon <= 180):
            raise ValueError(f"Row {idx}: 'lon' must be between -180 and 180, found {row['lon']}.")
    except (ValueError, TypeError):
        raise ValueError(f"Row {idx}: 'lat' and 'lon' must be valid floats, found lat={row['lat']}, lon={row['lon']}.")
    try:
        time_val = float(row['time'])
        if time_val < 0:
            raise ValueError(f"Row {idx}: 'time' must be a non-negative Unix epoch number, found {row['time']}.")
    except (ValueError, TypeError):
        raise ValueError(f"Row {idx}: 'time' must be a valid numeric Unix epoch number, found {row['time']}.")
df['lat'] = df['lat'].astype(float)
df['lon'] = df['lon'].astype(float)
df['time'] = df['time'].astype(float)
if df.empty:
    raise ValueError("No valid data points after validation. Check CSV file contents.")

# Sort by time ascending
df = df.sort_values(by="time")

# Calculate if lat/lon are precise
df['precise'] = ~((df['lat'] == df['lat'].round()) & (df['lon'] == df['lon'].round()))
df['size'] = np.where(df['precise'], 3, 10)
df['alpha'] = np.where(df['precise'], 0.8, 0.3)

# Assign shapes: star (*) for first occurrence, triangle (^) for others
df['shape'] = '^'
if len(df) > 0:
    df.iloc[0, df.columns.get_loc('shape')] = '^'

# Calculate recency in days (relative to 2025-09-30 11:53:00 +07)
current_time = datetime(2025, 9, 30, 4, 53, tzinfo=None).timestamp()  # Converted to UTC
df['recency_days'] = (current_time - df['time']) / 86400

# Aggregate data for unique coordinates (for labels)
label_df = df.groupby(['lat', 'lon']).agg({
    'name': lambda x: f"{len(x)} {x.iloc[0]}",
    'recency_days': 'min'
}).reset_index()
label_df = label_df.rename(columns={'name': 'label'})

# Calculate adaptive jitter (fixed 0.5 degrees)
jitter_width = 0.5
jitter_height = 0.5
np.random.seed(123)
df['lon_jitter'] = df['lon'] + np.random.uniform(-jitter_width, jitter_width, len(df))
df['lat_jitter'] = df['lat'] + np.random.uniform(-jitter_height, jitter_height, len(df))
label_df['lon_jitter'] = label_df['lon'] + np.random.uniform(-jitter_width, jitter_width, len(label_df))
label_df['lat_jitter'] = label_df['lat'] + np.random.uniform(-jitter_height, jitter_height, len(label_df))

# Create GeoDataFrame for points
gdf = gpd.GeoDataFrame(
    df, geometry=gpd.points_from_xy(df['lon_jitter'], df['lat_jitter']), crs="EPSG:4326"
)

# Load the Natural Earth shapefile
shapefile_path = "/wD/shapefiles/ne_110m_admin_0_countries.shp"
if not os.path.exists(shapefile_path):
    raise FileNotFoundError(f"Shapefile '{shapefile_path}' not found. Ensure it is included in the Docker image.")
world = gpd.read_file(shapefile_path)

# Calculate max recency for normalization (shared across all plots)
max_recency = gdf['recency_days'].max() if not gdf.empty else 1.0
if max_recency <= 0:
    max_recency = 1.0

# Plot for each region
for region in regions:
    CornerLeft = region['CornerLeft']
    CornerRight = region['CornerRight']
    #output_file = region['output_file']
    output_file = outf+"_"+region['name']+".svg"

    # Validate corner coordinates
    if CornerLeft[0] < CornerRight[0]:
        raise ValueError(f"{region['name']}: CornerLeft latitude must be greater than CornerRight latitude.")
    if CornerLeft[1] > CornerRight[1]:
        raise ValueError(f"{region['name']}: CornerLeft longitude must be less than CornerRight longitude.")

    # Extend boundaries by 20% on all sides
    lon_span = CornerRight[1] - CornerLeft[1]
    lat_span = CornerLeft[0] - CornerRight[0]
    extended_left_lon = CornerLeft[1] - lon_span * 0.2
    extended_right_lon = CornerRight[1] + lon_span * 0.2
    extended_top_lat = CornerLeft[0] + lat_span * 0.2
    extended_bottom_lat = CornerRight[0] - lat_span * 0.2
    extended_lon_span = extended_right_lon - extended_left_lon
    aspect_ratio = extended_lon_span / (extended_top_lat - extended_bottom_lat)

    # Create the map
    fig = plt.figure(figsize=(10, 10 / aspect_ratio))
    ax = fig.add_subplot(111)

    # Plot the world map
    world.plot(ax=ax, color='lightgray', edgecolor='white')

    # Set map boundaries (extended region)
    ax.set_xlim(extended_left_lon, extended_right_lon)
    ax.set_ylim(extended_bottom_lat, extended_top_lat)

    # Use RdYlGn colormap (reversed: recent=red, older=green)
    cmap = plt.cm.RdYlGn
    norm = Normalize(vmin=0, vmax=max_recency)

    # Plot points
    for idx, point in gdf.iterrows():
        ax.scatter(
            point['lon_jitter'], point['lat_jitter'],
            s=point['size'] * 200,
            facecolors='none',
            edgecolors=cmap(norm(point['recency_days'])),
            alpha=point['alpha'],
            marker=point['shape']
        )

    # Add labels
    for idx, point in label_df.iterrows():
        ax.text(
            point['lon_jitter'], point['lat_jitter'], point['label'],
            fontsize=8, ha='center', va='bottom'
        )

    # Add colorbar on the left side
    cbar_ax = fig.add_axes([0.05, 0.15, 0.02, 0.7])
    cbar = ColorbarBase(cbar_ax, cmap=cmap, norm=norm, orientation='vertical')
    cbar.set_label('Days Since Occurrence', fontsize=12)
    cbar.ax.tick_params(labelsize=10)

    # Add title
    plt.title(map_name, fontsize=14)

    # Remove axes
    ax.set_axis_off()

    # Define the bounding box for SVG cropping (include map and colorbar)
    ax_bbox = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    cbar_bbox = cbar_ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    svg_bbox = Bbox.union([ax_bbox, cbar_bbox])
    #if outf != "output.svg":
    #    output_file = outf
    # Save to SVG with cropped bounds
    plt.savefig(output_file, format="svg", bbox_inches=svg_bbox)
    plt.close()

    print(f"Map saved to {output_file}")
print(f"Max recency: {max_recency:.2f} days")
