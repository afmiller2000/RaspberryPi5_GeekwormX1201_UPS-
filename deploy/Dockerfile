# Dockerfile for Raspberry Pi Geekworm X1201 UPS Monitor
FROM python:3.11-slim-bullseye

# Install system dependencies
RUN apt-get update && apt-get install -y \
    i2c-tools \
    python3-dev \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd --create-home --shell /bin/bash app
USER app
WORKDIR /home/app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=app:app . .

# Create data directories
RUN mkdir -p data/logs data/snapshots data/calibrations

# Expose any ports if needed (none for this application)
# EXPOSE 8080

# Environment variables
ENV PYTHONPATH=/home/app/src
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python src/cli.py --status || exit 1

# Default command
CMD ["python", "src/cli.py", "--monitor", "--interval", "10"]