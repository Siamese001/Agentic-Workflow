# Phase 1A Validation Container
# Prevents laptop crashes by isolating validation process with resource limits
FROM python:3.11-slim

# Set working directory
WORKDIR /workspace

# Install system dependencies including timeout
RUN apt-get update && apt-get install -y \
    coreutils \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy validation script
COPY runtime/phase_1a_validation.py ./runtime/
COPY schemas/ ./schemas/

# Create non-root user for security
RUN useradd -m -u 1000 validator
RUN chown -R validator:validator /workspace
USER validator

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Default command with timeout to prevent runaway processes
CMD ["timeout", "300s", "python", "runtime/phase_1a_validation.py"]
