# Multi-stage Dockerfile for Canon Validator Engine
# Prioritizes security, isolation, and minimal footprint

# ================================================
# Stage 1: Builder - Install all dependencies
# ================================================
FROM python:3.11-slim AS builder

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies for building
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
COPY requirements-test.txt .

# Install Python dependencies including test libraries
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install -r requirements-test.txt

# Copy source code
COPY . .

# ================================================
# Stage 3: Runtime - Minimal production image
# ================================================
FROM python:3.11-slim AS runtime

# Security: Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PATH="/home/appuser/.local/bin:$PATH"

# Install only runtime system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Security: Create non-root user with minimal privileges
RUN adduser --disabled-password --gecos "" appuser && \
    mkdir -p /app && \
    chown -R appuser:appuser /app

# Set working directory
WORKDIR /app

# Copy only production dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Security: Copy only runtime code from builder stage
COPY --from=builder /app/canon_validator.py /app/
COPY --from=builder /app/l5_governance_policy_filter.py /app/
COPY --from=builder /app/connection_manager.py /app/
COPY --from=builder /app/llm_client.py /app/
COPY --from=builder /app/canon_keys.py /app/
COPY --from=builder /app/main.py /app/

# Copy health check script
COPY healthcheck.py /app/
RUN chmod +x /app/healthcheck.py

# Security: Set ownership to non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose monitoring port only (internal)
EXPOSE 8080

# Health check for L4/L5 state monitoring
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python /app/healthcheck.py || exit 1

# Run the Canon Validator Engine
CMD ["python", "/app/main.py"]
