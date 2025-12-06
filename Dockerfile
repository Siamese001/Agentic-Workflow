# Agentic-Workflow Pipeline Dockerfile
# SUPER-PROMPT v3.5 - Zero-Loss Docker Execution

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first for layer caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Set Python path
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Default command: run the pipeline
CMD ["python", "phase05/run_pipeline.py"]
