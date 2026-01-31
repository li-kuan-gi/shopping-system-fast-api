# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code directly to /app
COPY src/ ./

# Expose port (Zeabur will set PORT environment variable)
EXPOSE 8000

# Run the application with uvicorn
# Use host 0.0.0.0 to accept connections from outside the container
# Use PORT environment variable for Zeabur compatibility
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
