# Use a slim Python image
FROM python:3.12-slim

# Copy the uv binary from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy project files
COPY . .

# Install dependencies using uv sync
# This will use pyproject.toml and uv.lock
RUN uv sync --frozen

# Expose Streamlit port
EXPOSE 8501

# Run the app using uv run
CMD ["uv", "run", "streamlit", "run", "application.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]