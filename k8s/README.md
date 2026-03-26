# Agentic Workflow Kubernetes Deployment

This directory contains Kubernetes manifests for deploying the complete Agentic Workflow tracing and monitoring system.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Ingress Layer                              │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│  │    Main     │ │ Monitoring  │ │   Tracing   │ │  Kong Admin │ │
│  │   Service   │ │   Service   │ │   Service   │ │   Service   │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                      Application Layer                            │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │               Agentic Workflow Core                         │ │
│  │  - Tracing Integration                                      │ │
│  │  - Runtime ADG                                              │ │
│  │  - Performance Optimization                                  │ │
│  │  - ML Anomaly Detection                                     │ │
│  │  - 3D Visualization                                         │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                │                                │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ │
│  │      Kong       │ │    Prometheus    │ │     Grafana      │ │
│  │   API Gateway   │ │   Monitoring    │ │   Visualization  │ │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                       Infrastructure Layer                        │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ │
│  │     Redis       │ │     Jaeger      │ │    PostgreSQL    │ │
│  │   Cache/Store   │ │   Tracing       │ │   Kong Database  │ │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Components

### Core Services
- **Agentic Workflow Core**: Main application with tracing, monitoring, and ML features
- **Kong API Gateway**: Request routing, security, and tracing integration
- **Redis**: Cache and storage for Runtime ADG data
- **Jaeger**: Distributed tracing collection and visualization
- **PostgreSQL**: Kong database and configuration storage

### Monitoring Stack
- **Prometheus**: Metrics collection and alerting
- **Grafana**: Visualization and dashboards
- **AlertManager**: Alert routing and notification

### Ingress Configuration
- **Main Service**: Primary application endpoints
- **Monitoring**: Grafana and Prometheus access
- **Tracing**: Jaeger UI access
- **Kong Admin**: Gateway management interface

## Quick Start

### Prerequisites
- Kubernetes cluster (v1.20+)
- kubectl configured
- Helm (optional, for additional components)
- Sufficient resources (2+ CPU, 4+ GB RAM)

### Deployment Steps

1. **Create Namespace**
   ```bash
   kubectl apply -f namespace.yaml
   ```

2. **Deploy Configuration**
   ```bash
   kubectl apply -f configmap.yaml
   kubectl apply -f secret.yaml
   ```

3. **Deploy Infrastructure**
   ```bash
   kubectl apply -f redis-deployment.yaml
   kubectl apply -f jaeger-deployment.yaml
   kubectl apply -f kong-deployment.yaml
   ```

4. **Deploy Application**
   ```bash
   kubectl apply -f agentic-workflow-deployment.yaml
   ```

5. **Deploy Monitoring**
   ```bash
   kubectl apply -f monitoring.yaml
   ```

6. **Configure Ingress**
   ```bash
   kubectl apply -f ingress.yaml
   ```

### Verification

```bash
# Check all pods
kubectl get pods -n agentic-workflow

# Check services
kubectl get services -n agentic-workflow

# Check ingress
kubectl get ingress -n agentic-workflow

# View logs
kubectl logs -f deployment/agentic-workflow-core -n agentic-workflow
```

## Configuration

### Environment Variables

Key configuration options in `configmap.yaml`:

```yaml
# Tracing
tracing.enabled: "true"
tracing.sampling.rate: "0.1"

# Performance Optimization
performance.collector.batch_size: "100"
performance.collector.compression: "true"

# ML Integration
ml.enabled: "true"
ml.anomaly_detection.enabled: "true"

# Visualization
visualization.enabled: "true"
visualization.port: "8081"
```

### Resource Limits

Default resource allocations:

| Component | CPU Request | CPU Limit | Memory Request | Memory Limit |
|-----------|-------------|-----------|----------------|-------------|
| Agentic Workflow | 200m | 1000m | 512Mi | 2Gi |
| Kong | 200m | 500m | 512Mi | 1Gi |
| Redis | 100m | 500m | 256Mi | 512Mi |
| Jaeger | 200m | 500m | 512Mi | 1Gi |
| Prometheus | 200m | 1000m | 512Mi | 2Gi |
| Grafana | 100m | 500m | 256Mi | 1Gi |

### Scaling

#### Horizontal Scaling
```bash
# Scale Agentic Workflow
kubectl scale deployment agentic-workflow-core --replicas=5 -n agentic-workflow

# Scale Kong
kubectl scale deployment kong --replicas=3 -n agentic-workflow
```

#### Vertical Scaling
Edit resource limits in deployment manifests:
```yaml
resources:
  requests:
    memory: "1Gi"
    cpu: "500m"
  limits:
    memory: "4Gi"
    cpu: "2000m"
```

## Access URLs

After deployment with LoadBalancer services:

| Service | URL | Description |
|---------|-----|-------------|
| Main Application | http://agentic-workflow.local | Primary application |
| 3D Visualization | http://agentic-workflow.local:8081 | Interactive 3D traces |
| Grafana | http://monitoring.agentic-workflow.local | Monitoring dashboards |
| Prometheus | http://monitoring.agentic-workflow.local/prometheus | Metrics endpoint |
| Jaeger | http://tracing.agentic-workflow.local | Tracing UI |
| Kong Admin | http://kong-admin.agentic-workflow.local | Gateway management |

## Monitoring and Alerting

### Prometheus Metrics

Key metrics exposed:
- `http_requests_total`: HTTP request count
- `http_request_duration_seconds`: Request latency
- `tracing_spans_total`: Tracing span count
- `runtime_adg_nodes_total`: Runtime ADG nodes
- `ml_anomalies_detected_total`: ML anomaly count

### Grafana Dashboards

Pre-configured dashboards:
- **Agentic Workflow Overview**: System health and performance
- **Tracing Analytics**: Jaeger metrics and trace analysis
- **ML Anomaly Detection**: Model performance and anomaly trends
- **Resource Utilization**: CPU, memory, and network metrics

### Alert Rules

Critical alerts:
- **AgenticWorkflowDown**: Service unavailable
- **HighErrorRate**: Error rate > 5%
- **HighResponseTime**: 95th percentile > 1s
- **RedisDown**: Cache service unavailable
- **JaegerCollectorDown**: Tracing collector unavailable

## Security

### Network Policies

Apply network policies for enhanced security:
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: agentic-workflow-netpol
  namespace: agentic-workflow
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: agentic-workflow
    ports:
    - protocol: TCP
      port: 8080
```

### RBAC

Service accounts and permissions:
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: agentic-workflow
  namespace: agentic-workflow
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: agentic-workflow-role
  namespace: agentic-workflow
rules:
- apiGroups: [""]
  resources: ["pods", "services"]
  verbs: ["get", "list", "watch"]
```

## Troubleshooting

### Common Issues

1. **Pods not starting**
   ```bash
   kubectl describe pod <pod-name> -n agentic-workflow
   kubectl logs <pod-name> -n agentic-workflow
   ```

2. **Service connectivity issues**
   ```bash
   kubectl get endpoints -n agentic-workflow
   kubectl port-forward service/<service-name> <local-port>:<service-port> -n agentic-workflow
   ```

3. **Ingress not working**
   ```bash
   kubectl describe ingress <ingress-name> -n agentic-workflow
   kubectl get ingress -n agentic-workflow -o yaml
   ```

4. **Resource constraints**
   ```bash
   kubectl top pods -n agentic-workflow
   kubectl describe node <node-name>
   ```

### Debug Commands

```bash
# Check cluster resources
kubectl get nodes
kubectl top nodes

# Check namespace resources
kubectl get all -n agentic-workflow
kubectl top pods -n agentic-workflow

# Debug specific pod
kubectl exec -it <pod-name> -n agentic-workflow -- /bin/bash
kubectl logs -f <pod-name> -n agentic-workflow --previous

# Check events
kubectl get events -n agentic-workflow --sort-by='.lastTimestamp'
```

## Maintenance

### Rolling Updates

```bash
# Update application image
kubectl set image deployment/agentic-workflow-core agentic-workflow=new-image:tag -n agentic-workflow

# Update configuration
kubectl apply -f configmap.yaml
kubectl rollout restart deployment/agentic-workflow-core -n agentic-workflow
```

### Backup and Restore

```bash
# Backup configurations
kubectl get all -n agentic-workflow -o yaml > backup.yaml

# Backup persistent data
kubectl exec -it postgres-0 -n agentic-workflow -- pg_dump kong > kong-backup.sql

# Restore
kubectl apply -f backup.yaml
kubectl exec -it postgres-0 -n agentic-workflow -- psql kong < kong-backup.sql
```

### Cleanup

```bash
# Delete all resources
kubectl delete namespace agentic-workflow

# Or delete individual components
kubectl delete -f .
```

## Production Considerations

### High Availability
- Deploy multiple replicas of critical services
- Use anti-affinity rules for pod distribution
- Configure persistent storage with replication
- Set up proper backup procedures

### Performance Tuning
- Adjust resource limits based on actual usage
- Optimize JVM settings for Java applications
- Tune database connections and pool sizes
- Configure appropriate cache sizes

### Security Hardening
- Enable RBAC and least privilege access
- Use network policies to restrict traffic
- Enable pod security policies
- Regularly update base images and dependencies
- Configure secrets management

### Monitoring Enhancement
- Set up comprehensive logging
- Configure distributed tracing sampling
- Implement custom metrics and alerts
- Set up log aggregation and analysis
- Configure SLA monitoring and reporting

## Support

For issues and questions:
1. Check pod logs and events
2. Verify resource availability
3. Review configuration files
4. Consult Kubernetes documentation
5. Check component-specific documentation

---

**Note**: This deployment is designed for production use with proper resource management, monitoring, and security considerations. Adjust configurations based on your specific requirements and environment.
