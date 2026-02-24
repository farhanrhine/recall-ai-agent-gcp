# ==============================================================================
# DOCKERFILE - Recall AI Agent
# ==============================================================================
# This Dockerfile builds a container for the FastAPI/SFA Pro application.
#
# BUILD COMMAND:
#   docker build -t recall-ai-agent-gcp:v1 .
#
# RUN COMMAND:
#   docker run -p 8080:8080 --env-file .env recall-ai-agent-gcp:v1
#
# FOR KUBERNETES:
#   docker build -t farhanrhine/recall-ai-agent-gcp:latest .
#   docker push farhanrhine/recall-ai-agent-gcp:latest
# ==============================================================================

# Use Python 3.12 slim image (matches pyproject.toml requires-python >= 3.12)
FROM python:3.12-slim

# Copy the uv binary from the official image (fastest way to get uv)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory inside container
# - Creates isolated /app folder inside the container
WORKDIR /app

# Set environment variables
# - Prevents Python from writing .pyc files
# - Ensures output is sent straight to terminal (for logging)
# - Enable bytecode compilation for performance
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_COMPILE_BYTECODE=1

# Install system dependencies
# - curl needed for health checks
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files first (for Docker layer caching)
# - This way, dependencies are only reinstalled when pyproject.toml or uv.lock changes
COPY pyproject.toml .
COPY uv.lock .

# Install Python dependencies using uv
# - Using --frozen to ensure exact versions from uv.lock are installed
RUN uv sync --frozen

# Copy the rest of the application code
COPY . .

# Expose port 8080 (FastAPI default in main.py)
EXPOSE 8080

# Health check - Kubernetes/Docker can use this to check if app is alive
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8080/ || exit 1

# Run the FastAPI application
# - Using 'uv run' to ensure the virtual environment created by 'uv sync' is used
CMD ["uv", "run", "python", "main.py"]