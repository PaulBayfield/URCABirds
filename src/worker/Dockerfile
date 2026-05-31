# Dockerfile.worker

# Base image
FROM python:3.13-slim

# Install uv
RUN pip install uv

RUN apt-get update && apt-get install -y --no-install-recommends portaudio19-dev && rm -rf /var/lib/apt/lists/*

# Copy the project
COPY . ./URCABIRDS

# Set the working directory
WORKDIR /URCABIRDS

# Install dependencies
RUN uv sync

# Run the worker
CMD ["uv", "run", "__main__.py"]
