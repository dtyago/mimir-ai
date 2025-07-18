# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Set environment variables for Python
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV CHROMADB_ALLOW_RESET=true

# Install system dependencies including build tools
RUN apt-get update && apt-get install -y \
    # Build tools
    gcc \
    g++ \
    make \
    pkg-config \
    wget \
    # SQLite dependencies (we'll compile newer version)
    libsqlite3-dev \
    # OpenCV dependencies
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgthread-2.0-0 \
    # General utilities
    curl \
    && rm -rf /var/lib/apt/lists/*

# Compile and install newer SQLite from source
RUN cd /tmp && \
    wget https://www.sqlite.org/2024/sqlite-autoconf-3450100.tar.gz && \
    tar xzf sqlite-autoconf-3450100.tar.gz && \
    cd sqlite-autoconf-3450100 && \
    ./configure --prefix=/usr/local && \
    make && \
    make install && \
    ldconfig && \
    cd / && \
    rm -rf /tmp/sqlite-autoconf-*

# Set environment variable to use the new SQLite
ENV LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH

# Upgrade pip and install wheel for better package builds
RUN pip install --upgrade pip setuptools wheel

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY static/ ./static/
COPY start.sh ./
COPY .env* ./

# Create necessary directories with proper permissions
RUN mkdir -p data/{chromadb,uploads,tmp,logs} tmp/uploads && \
    chmod -R 755 data tmp && \
    chmod 700 data/chromadb && \
    chmod +x start.sh

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash mimir && \
    chown -R mimir:mimir /app
USER mimir

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command for production
ENV ENVIRONMENT=production
CMD ["./start.sh"]
