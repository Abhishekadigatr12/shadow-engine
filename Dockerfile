FROM python:3.11-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy and install requirements to a virtual environment
COPY requirements.txt .
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir --upgrade pip setuptools wheel && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# Final stage - use Alpine for minimal attack surface
FROM python:3.11-alpine

WORKDIR /app

# Create non-root user for security
RUN addgroup -S appuser && adduser -S -G appuser appuser

# Install only runtime dependencies
RUN apk add --no-cache curl ca-certificates

# Copy virtual environment from builder
COPY --from=builder --chown=appuser:appuser /opt/venv /opt/venv

# Copy application code
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Set PATH to use venv
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBUG=false \
    LOG_LEVEL=INFO

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
