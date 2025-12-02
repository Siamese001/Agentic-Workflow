# Phase 1A Validation Container Setup

## Overview

This containerized setup prevents laptop crashes by isolating the Phase 1A validation process with strict resource limits and read-only filesystem access.

## Prerequisites

- Docker Desktop installed and running
- At least 1GB available disk space
- Administrator privileges (for Docker Desktop)

## Quick Start

### 1. Start Docker Desktop

Launch Docker Desktop from your Start menu or Applications folder. Wait for it to show "Docker Desktop is running".

### 2. Build and Run the Container

```bash
# Build the container
docker build -t agentic-workflow-phase1a .

# Run validation with resource limits
docker-compose up --build
```

### 3. Alternative: Direct Docker Run

```bash
# Run with explicit resource limits
docker run --rm \
  --memory=512m \
  --cpus=1.0 \
  --read-only \
  --mount type=bind,source="$(pwd)",target=/workspace \
  agentic-workflow-phase1a
```

## Resource Limits

- **Memory**: 512MB max (prevents memory exhaustion crashes)
- **CPU**: 1.0 core max (prevents CPU overload)
- **Filesystem**: Read-only mount (enforces Phase 1A non-destructive behavior)
- **Network**: Internal only (no external access)

## Safety Features

- Non-root user execution
- Read-only repository mount
- No external network access
- Health checks and automatic restart
- Resource constraints prevent system overload

## Troubleshooting

### Docker Desktop Not Running

```
ERROR: error during connect: Head "http://%2F%2F.%2Fpipe%2FdockerDesktopLinuxEngine/_ping"
```
**Solution**: Start Docker Desktop from your applications menu

### Permission Issues
```
ERROR: permission denied while trying to connect to Docker daemon
```
**Solution**: Run as administrator or add your user to docker group

### Out of Memory

```bash
ERROR: Container killed due to memory limit
```

**Solution**: Increase memory limit in docker-compose.yml:

```yaml
deploy:
  resources:
    limits:
      memory: 1G  # Increase from 512M
```

## Monitoring

```bash
# Check container status
docker-compose ps

# View resource usage
docker stats agentic-workflow-phase1a

# View logs
docker-compose logs -f phase1a-validation
```

## Cleanup

```bash
# Stop and remove container
docker-compose down

# Remove image
docker rmi agentic-workflow-phase1a
```

## Production Considerations

For CI/CD or production, consider:

- Kubernetes deployment with resource quotas
- Jenkins/GitHub Actions with Docker-in-Docker
- Cloud Run/AWS Fargate for serverless execution
