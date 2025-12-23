# Use official Python slim image for smaller size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (if needed)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy operator code
COPY src/operator.py .

# Create non-root user for security
# The operator group already exists in the base image, so we use -g to add user to it
RUN groupadd -f -g 1000 operator && \
    useradd -m -u 1000 -g operator operator && \
    chown -R operator:operator /app

# Switch to non-root user
USER operator

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Health check (optional, kopf doesn't expose HTTP by default)
# HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
#   CMD python -c "import sys; sys.exit(0)"

# Run the operator
ENTRYPOINT ["kopf", "run"]
CMD ["/app/operator.py", "--verbose"]
