# Stage 1: Base image
FROM python:3.11-slim

# Working directory inside container
WORKDIR /app

# Install system dependencies (needed for psycopg2)
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port 5000 (ALB will connect here)
EXPOSE 5000

# Health check (ECS will use this)
# Every 30 seconds, check if app is alive
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Run app with Gunicorn (production server)
# Workers: 4 = can handle 4 concurrent requests per instance
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "60"]
