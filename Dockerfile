# ====================================================================
# STAGE 1: BUILDER - Installs ALL heavy dependencies (Cache Layer)
# ====================================================================
FROM python:3.11-slim as builder

# Set environment variables for non-interactive installs
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# 1. Install system dependencies needed for Python packages (e.g., git, gcc)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /tmp/build

# 2. Copy only requirements files first to leverage caching
# If requirements.txt doesn't change, Docker skips the pip install step.
COPY requirements.txt .
COPY requirements-test.txt .
COPY pyproject.toml .

# 3. The CRITICAL step: Install all dependencies
# This is the step that takes 386.2s, so we must cache it aggressively.
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-test.txt

# ====================================================================
# STAGE 2: RUNTIME - Creates the final, lean image for execution
# ====================================================================
FROM python:3.11-slim as runtime

# Define App User (as per your original Docker Compose)
ARG USER_ID=1000
ARG GROUP_ID=1000
RUN groupadd -r appgroup -g $GROUP_ID && \
    useradd --no-log-init -r -g appgroup -u $USER_ID appuser

# Set environment variables
ENV PYTHONUNBUFFERED=1

# 1. Install necessary system tools for runtime (often lighter than builder stage)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    # Add any essential runtime dependencies here (e.g., openssl, libpq-dev for postgres)
    # If using Redis-cli in a healthcheck, add redis-tools
    redis-tools \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2. Copy installed dependencies from the builder stage
# This is much faster than running pip install again.
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/

# 3. Copy the rest of the application code
# This is the only step that changes often, thus keeping the install step cached.
COPY . /app

# Set ownership to the non-root user
RUN chown -R appuser:appgroup /app

# Switch to the non-root user
USER appuser

# Define the entry point for containers
ENTRYPOINT ["python"]
