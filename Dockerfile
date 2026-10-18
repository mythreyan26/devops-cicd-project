# Use official lightweight Python 3.12 slim base image
FROM python:3.12-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ENVIRONMENT=production \
    PORT=5000

# Install curl for container health check probes and remove package lists to keep image minimal
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create a dedicated non-root user and group for security
RUN groupadd -r appgroup && useradd -r -g appgroup -u 1000 -d /app -s /sbin/nologin appuser

# Set working directory
WORKDIR /app

# Copy dependency manifest and install packages prior to copying source code to maximize Docker cache efficiency
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application package and WSGI entrypoint
COPY app /app/app
COPY wsgi.py /app/wsgi.py

# Assign directory ownership to non-root user
RUN chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Expose the application listening port
EXPOSE 5000

# Health check probe against the /health endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1

# Run the application using Gunicorn production WSGI server
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--threads", "2", "--access-logfile", "-", "--error-logfile", "-", "wsgi:app"]
