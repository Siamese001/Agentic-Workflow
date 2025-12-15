# ONE COMMAND TO RULE THEM ALL — SUBATOMIC AGENTIC ARCHITECTURE 2025
# Docker-based installation for true reproducibility
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set working directory
WORKDIR /app

# Install system dependencies including Rust compiler
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Rust for jiter compilation
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Copy requirements first for better caching
COPY requirements.txt .

# OPTIMIZATION: Use --mount=type=cache to cache downloaded packages
# This prevents re-downloading all wheels on every build
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# Copy the application code (now much faster with .dockerignore)
COPY . .

# Expose Redis port (if running Redis in container)
EXPOSE 6379 8001

# Default command - keep container running for exec commands
CMD ["tail", "-f", "/dev/null"]
