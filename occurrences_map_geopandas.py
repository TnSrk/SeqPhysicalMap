import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
from datetime import datetime
import os
import matplotlib.cm as cm
from matplotlib.colors import Normalize

# Set local library directory
local_lib = "./python_libraries"
if not os.path.exists(local_lib):
    os.makedirs(local_lib)

# Read CSV file
csv_file = "/wD/input.csv"
if not os.path.exists(csv_file):
    raise FileNotFoundError(f"CSV file '{csv_file}' not found. Please provide the correct file path.")
df = pd.read_csv(csv_file, sep=",", header=None, names=["name", "lat", "lon", "time"])

# Debug: Print raw data
print("Raw data from CSV:")
print(df)

# Validate data
df = df.dropna()
df = df[(df['lat'] >= -90) & (df['lat'] <= 90) & (df['lon'] >= -180) & (df['lon'] <= 180)]
if df.empty:
    raise ValueError("No valid data points after validation. Check lat/lon values in the CSV file.")
print("Validated data:")
print(df)

# Sort by time ascending
df = df.sort_values(by="time")

# Calculate if lat/lon are precise
df['precise'] = ~((df['lat'] == df['lat'].round()) & (df['lon'] == df['lon'].round()))
df['size'] = np.where(df['precise'], 3, 10)
df['alpha'] = np.where(df['precise'], 0.8, 0.3)

# Assign shapes: star (*) for first occurrence, triangle (^) for others
df['shape'] = '^'
if len(df) > 0:
    df.iloc[0, df.columns.get_loc('shape')] = '*'

# Calculate recency in days (relative to 2025-09-11 00:00:00 UTC)
current_time = datetime(2025, 9, 11).timestamp()
df['recency_days'] = (current_time - df['time']) / 86400

# Debug recency calculation
print("Current time (epoch):", current_time)
print("Sample recency_days:")
print(df[['name', 'time', 'recency_days']].head())

# Aggregate data for unique coordinates (for labels)
label_df = df.groupby(['lat', 'lon']).agg({
    'name': lambda x: f"{len(x)} {x.iloc[0]}",
    'recency_days': 'min'
}).reset_index()
label_df = label_df.rename(columns={'name': 'label'})

# Debug label_df
print("Label data frame:")
print(label_df)

# Calculate adaptive jitter (fixed 0.5 degrees for full map)
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

# Create the map with GeoPandas (full world map)
fig, ax = plt.subplots(figsize=(56, 28))

# Load the pre-installed Natural Earth shapefile
shapefile_path = "/wD/shapefiles/ne_110m_admin_0_countries.shp"
if not os.path.exists(shapefile_path):
    raise FileNotFoundError(f"Shapefile '{shapefile_path}' not found. Ensure it is included in the Docker image.")
world = gpd.read_file(shapefile_path)

# Plot the world map (landmasses only, no ocean fill)
world.plot(ax=ax, color='lightgray', edgecolor='white')

# Calculate max recency for normalization
max_recency = gdf['recency_days'].max()
if max_recency <= 0:
    max_recency = 1.0  # Avoid issues if all data is current

# Use RdYlGn colormap (reversed so recent is red, older is green)
cmap = plt.cm.RdYlGn  # Red to Green colormap, reversed

# Plot points with unfilled shapes, sizes, colors, and transparency
for idx, point in gdf.iterrows():
    normalized_recency = point['recency_days'] / max_recency
    ax.scatter(
        point['lon_jitter'], point['lat_jitter'],
        s=point['size'] * 350,
        facecolors='none',  # Unfilled shapes
        edgecolors=cmap(normalized_recency),  # Use RdYlGn_r colormap (red for recent, green for older)
        alpha=point['alpha'],
        marker=point['shape']
    )

# Add labels
for idx, point in label_df.iterrows():
    ax.text(
        point['lon_jitter'], point['lat_jitter'], point['label'],
        fontsize=6, ha='center', va='bottom'
    )

# Add colorbar with actual recency range
norm = Normalize(vmin=0, vmax=max_recency)
sm = cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
cbar = plt.colorbar(sm, ax=ax, label="Recency (days ago)", shrink=0.5, aspect=30, pad=0.1)
cbar.ax.tick_params(labelsize=6)

# Add title
plt.title("Occurrences", fontsize=10)

# Remove axes to avoid any "cage" effect
ax.set_axis_off()

# Adjust layout to prevent clipping
plt.tight_layout()

# Save to SVG
plt.savefig("/wD/occurrences_map.svg", format="svg", bbox_inches="tight")
plt.close()

print("Map saved to /wD/occurrences_map.svg")
print(f"Max recency: {max_recency:.2f} days")
