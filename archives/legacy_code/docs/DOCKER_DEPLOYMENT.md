# Docker Deployment Guide
## Canon Validator Engine - Secure Containerization

### Overview
This guide covers the secure deployment of the Canon Validator Engine using Docker Compose with hardened security configurations.

### Prerequisites
- Docker Engine 20.10+
- Docker Compose 2.0+
- Minimum 4GB RAM available
- API keys for external services (Gemini, Tavily)

### Quick Start

1. **Prepare Environment**
   ```bash
   # Copy the production environment template
   cp .env.production.template .env.production

   # Edit with your actual API keys and secrets
   nano .env.production
   ```

2. **Build and Deploy**
   ```bash
   # Build the image (runs all 88 tests during build)
   docker-compose build

   # Start all services
   docker-compose up -d
   ```

3. **Verify Deployment**
   ```bash
   # Check service status
   docker-compose ps

   # View logs
   docker-compose logs -f validator

   # Test health check
   curl http://localhost:8080/health
   ```

### Security Features

#### Multi-Stage Build
- **Stage 1 (Builder)**: Installs all dependencies including test libraries
- **Stage 2 (Tester)**: Executes full test suite, fails build if any test fails
- **Stage 3 (Runtime)**: Minimal production image with only runtime dependencies

#### Container Security
- **Non-root User**: Runs as `appuser` (UID/GID: 1000)
- **Minimal Attack Surface**: Only essential files copied to runtime image
- **Read-only Considerations**: Can add `--read-only` flag for additional hardening

#### Network Isolation
- **Private Network**: Services communicate via isolated `canon_net` bridge
- **Redis Protection**: No external port exposure, password-protected
- **Internal Monitoring**: Only port 8080 exposed for health checks

#### Resource Limits
- **CPU**: Limited to 1.0 core (reservable: 0.5)
- **Memory**: Limited to 2GB (reservable: 1GB)
- **Redis**: Limited to 512MB with LRU eviction

### Configuration

#### Environment Variables
Key variables in `.env.production`:
- `GEMINI_API_KEY`: LLM provider authentication
- `TAVILY_API_KEY`: Search service authentication
- `REDIS_PASSWORD`: State store encryption
- `EBP_ENABLED`: Emergency Bailout Protocol toggle

#### Volume Mounts
- `./workspace:/app/workspace`: Git workspace (read-write)
- `./logs:/app/logs`: Application logs (read-write)
- `redis_data:/data`: Redis persistence (Docker volume)

### Monitoring

#### Health Checks
The health check (`healthcheck.py`) monitors:
1. **L4 Redis Connectivity**: Ping and basic operations
2. **EBP Status**: Ensures blackout is not active
3. **L5 Audit Trail**: Validates observation structure
4. **Process Health**: Checks validator responsiveness

#### Logs
- Application logs: `docker-compose logs validator`
- Redis logs: `docker-compose logs redis`
- Real-time: Add `-f` flag for streaming

### Troubleshooting

#### Build Failures
```bash
# Check test failures
docker-compose build --no-cache validator 2>&1 | grep -A 10 "FAILED"

# Common causes:
# - Missing API keys in environment
# - Test failures in tests/apps_cv/
# - Missing dependencies in requirements.txt
```

#### Runtime Issues
```bash
# Check container status
docker-compose ps

# Enter container for debugging
docker-compose exec validator bash

# Check Redis connection
docker-compose exec redis redis-cli ping
```

#### Performance Tuning
- Adjust `REDIS_MAXMEMORY` based on workload
- Tune `LLM_REQUESTS_PER_MINUTE` for rate limiting
- Modify resource limits in `docker-compose.yml`

### Security Best Practices

1. **Secrets Management**
   - Never commit `.env.production` to version control
   - Use external secret managers in production
   - Rotate API keys regularly

2. **Network Security**
   - Keep Redis port internal (no host binding)
   - Use VPN or private networks for external access
   - Monitor network traffic with security tools

3. **Container Hardening**
   - Enable `--read-only` filesystem for production
   - Use `tmpfs` for `/tmp` and `/var/tmp`
   - Regular security scans of images

4. **Monitoring & Alerts**
   - Set up alerts for health check failures
   - Monitor EBP triggers
   - Track resource usage patterns

### Scaling Considerations

#### Horizontal Scaling
- Deploy multiple validator instances behind load balancer
- Use Redis Cluster for state management
- Implement session affinity if needed

#### Vertical Scaling
- Increase CPU/memory limits in `docker-compose.yml`
- Adjust Redis memory and eviction policies
- Monitor performance metrics

### Backup & Recovery

#### Redis Data
```bash
# Create backup
docker-compose exec redis redis-cli BGSAVE

# Copy backup
docker cp canon-redis:/data/dump.rdb ./backups/
```

#### Configuration
- Version control `.env.production.template`
- Document custom configurations
- Maintain disaster recovery procedures

### Compliance Notes

- **GDPR**: Ensure no PII in logs or workspace
- **SOC2**: Maintain audit trails in L5
- **ISO 27001**: Follow security best practices
- **HIPAA**: Additional encryption for healthcare data

### Support

For issues or questions:
1. Check logs: `docker-compose logs`
2. Verify configuration: `.env.production`
3. Run health check manually
4. Review test suite: `pytest tests/apps_cv/`
