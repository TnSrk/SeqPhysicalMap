# Use lean Debian 13 (Trixie) slim base image
FROM ubuntu:noble

# Install dependencies: Python3, NCBI BLAST+, NCBI Entrez Utilities, jq, csvkit, R, xmltodict
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3 \
    python3-venv python3-pandas \
    python3-xmltodict \
    ncbi-blast+ \
    ncbi-tools-bin \
    jq \
    csvkit \
    #r-base \
    && rm -rf /var/lib/apt/lists/*

# Create and activate a virtual environment for Python packages
#RUN python3-pip -c pip install pandas numpy matplotlib geopandas geodatasets multipart
RUN python3 -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

# Install multipart in the virtual environment
RUN pip3 install --no-cache-dir multipart pandas numpy matplotlib geopandas geodatasets

# Create directories for uploads and output
RUN mkdir -p /tmp/uploads /tmp/output

# Set working directory
WORKDIR /app

# Copy the Python server script
COPY server.py .

# Expose port 8080
EXPOSE 8080

# No CMD or ENTRYPOINT to avoid auto-starting (OCI standard)
# User will run `python3 server.py` manually
