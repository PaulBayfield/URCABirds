# Dockerfile.worker

# Base image
FROM python:3.13

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the project
COPY . ./URCABIRDS

# Set the working directory
WORKDIR /URCABIRDS

# Install dependencies
RUN uv sync --frozen

# Run the worker
CMD ["uv", "run", "__main__.py"]


