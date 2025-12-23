# ONE COMMAND TO RULE THEM ALL — SUBATOMIC AGENTIC ARCHITECTURE 2025
# Docker-based installation for true reproducibility
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies including Rust compiler
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Rust for jiter compilation
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies with exact versions
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Create verification script
COPY verify_installation.py /app/verify_installation.py

# Expose Redis port (if running Redis in container)
EXPOSE 6379 8001

# Default command
CMD ["python", "verify_installation.py"]
