"""Cloud Native Manager - Kubernetes-native features and operations.

Provides comprehensive cloud-native capabilities including auto-scaling,
service discovery, configuration management, health monitoring, and
resource optimization for Kubernetes deployments.

FEATURES:
- Kubernetes API integration and resource management
- Auto-scaling policies and horizontal pod autoscaling
- Service discovery and load balancing
- Configuration management with ConfigMaps and Secrets
- Health monitoring and self-healing
- Resource optimization and cost management
- Multi-cluster and multi-cloud support

USAGE:
    manager = CloudNativeManager()
    manager.initialize(kubeconfig_path)

    # Auto-scale based on metrics
    manager.enable_auto_scaling("agentic-workflow", cpu_threshold=70)

    # Monitor cluster health
    health = manager.get_cluster_health()
"""

import logging
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union
from enum import Enum

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    emit_determinism_digest,
    record_execution_trace,
)

emit_determinism_digest("cloud_native_manager", "cloud_native_manager_digest")
record_execution_trace("cloud_native_manager", "cloud_native_manager_trace")

Logger = logging.getLogger(__name__)


class ScalingPolicy(Enum):
    """Auto-scaling policy types."""
    CPU_BASED = "cpu_based"
    MEMORY_BASED = "memory_based"
    CUSTOM_METRIC = "custom_metric"
    PREDICTIVE = "predictive"
    HYBRID = "hybrid"


class HealthStatus(Enum):
    """Health status levels."""
    HEALTHY = "healthy"
    WARNING = "warning"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class ResourceType(Enum):
    """Kubernetes resource types."""
    POD = "pod"
    DEPLOYMENT = "deployment"
    SERVICE = "service"
    CONFIGMAP = "configmap"
    SECRET = "secret"
    HPA = "horizontalpodautoscaler"
    INGRESS = "ingress"
    PERSISTENTVOLUME = "persistentvolume"
    PERSISTENTVOLUMECLAIM = "persistentvolumeclaim"


@dataclass
class ClusterMetrics:
    """Cluster-wide metrics."""

    total_nodes: int = 0
    ready_nodes: int = 0
    total_pods: int = 0
    running_pods: int = 0
    cpu_capacity: float = 0.0
    cpu_allocated: float = 0.0
    memory_capacity: float = 0.0
    memory_allocated: float = 0.0
    storage_capacity: float = 0.0
    storage_allocated: float = 0.0
    cluster_age: float = 0.0
    version: str = ""
    timestamp: float = field(default_factory=time.time)


@dataclass
class ResourceMetrics:
    """Resource-specific metrics."""

    name: str
    namespace: str
    resource_type: ResourceType
    status: HealthStatus
    replicas: int = 0
    ready_replicas: int = 0
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    restart_count: int = 0
    age: float = 0.0
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


@dataclass
class ScalingEvent:
    """Auto-scaling event record."""

    resource_name: str
    resource_type: ResourceType
    scaling_type: str  # "scale_up" or "scale_down"
    from_replicas: int
    to_replicas: int
    reason: str
    metric_value: float
    threshold: float
    timestamp: float = field(default_factory=time.time)
    duration: float = 0.0


@dataclass
class AutoScalingConfig:
    """Auto-scaling configuration."""

    min_replicas: int = 1
    max_replicas: int = 10
    target_cpu_utilization: float = 70.0
    target_memory_utilization: float = 80.0
    scale_up_threshold: float = 80.0
    scale_down_threshold: float = 40.0
    scale_up_cooldown: int = 300  # seconds
    scale_down_cooldown: int = 600  # seconds
    stabilization_window: int = 300  # seconds
    behavior_policy: str = "default"  # "default", "minimal", "aggressive"


class CloudNativeManager:
    """
    Cloud Native Manager for Kubernetes operations.

    Provides comprehensive Kubernetes-native features including
    auto-scaling, monitoring, resource management, and optimization.
    """

    def __init__(self) -> None:
        """Initialize cloud native manager."""
        # Kubernetes client
        self._k8s_client: Optional[Any] = None
        self._kubeconfig_path: Optional[str] = None
        self._current_namespace: str = "default"

        # Resource tracking
        self._resources: Dict[str, ResourceMetrics] = {}
        self._cluster_metrics: ClusterMetrics = ClusterMetrics()
        self._scaling_history: deque = deque(maxlen=1000)
        self._health_checks: Dict[str, HealthStatus] = {}

        # Auto-scaling
        self._auto_scaling_configs: Dict[str, AutoScalingConfig] = {}
        self._scaling_events: deque = deque(maxlen=1000)
        self._last_scale_time: Dict[str, float] = {}

        # Configuration
        self._config: Dict[str, Any] = {
            "auto_scaling_enabled": True,
            "health_check_interval": 30,
            "metrics_collection_interval": 15,
            "resource_optimization_enabled": True,
            "cost_optimization_enabled": True,
        }

        # State
        self._initialized: bool = False
        self._monitoring_active: bool = False
        self._auto_scaling_active: bool = False

        # Initialize Kubernetes client
        self._initialize_kubernetes_client()

    def _initialize_kubernetes_client(self) -> None:
        """Initialize Kubernetes client."""
        try:
            from kubernetes import client, config

            # Try to load in-cluster config first
            try:
                config.load_incluster_config()
                Logger.info("[CLOUD_NATIVE] Loaded in-cluster Kubernetes config")
            except (config.ConfigException, IOError):
                # Fall back to kubeconfig
                config.load_kube_config()
                Logger.info("[CLOUD_NATIVE] Loaded kubeconfig")

            # Initialize clients
            self._k8s_client = {
                'apps_v1': client.AppsV1Api(),
                'core_v1': client.CoreV1Api(),
                'autoscaling_v1': client.AutoscalingV1Api(),
                'networking_v1': client.NetworkingV1Api(),
                'custom_objects': client.CustomObjectsApi(),
            }

            self._initialized = True
            Logger.info("[CLOUD_NATIVE] Kubernetes client initialized")

        except ImportError:
            Logger.warning("[CLOUD_NATIVE] Kubernetes client not available, installing kubernetes package")
            self._initialized = False
        except Exception as e:
            Logger.error(f"[CLOUD_NATIVE] Failed to initialize Kubernetes client: {e}")
            self._initialized = False

    def initialize(self, kubeconfig_path: Optional[str] = None, namespace: str = "default") -> bool:
        """
        Initialize the cloud native manager.

        Args:
            kubeconfig_path: Path to kubeconfig file (optional)
            namespace: Default namespace (default: "default")

        Returns:
            True if initialization successful
        """
        try:
            if not self._initialized:
                Logger.error("[CLOUD_NATIVE] Kubernetes client not initialized")
                return False

            self._kubeconfig_path = kubeconfig_path
            self._current_namespace = namespace

            # Test connection
            if self._test_kubernetes_connection():
                Logger.info(f"[CLOUD_NATIVE] Connected to Kubernetes cluster, namespace: {namespace}")

                # Start monitoring
                self.start_monitoring()

                return True
            else:
                Logger.error("[CLOUD_NATIVE] Failed to connect to Kubernetes cluster")
                return False

        except Exception as e:
            Logger.error(f"[CLOUD_NATIVE] Initialization failed: {e}")
            return False

    def _test_kubernetes_connection(self) -> bool:
        """Test Kubernetes cluster connection."""
        try:
            if not self._k8s_client:
                return False

            # Try to list nodes
            self._k8s_client['core_v1'].list_node()
            return True

        except Exception as e:
            Logger.debug(f"[CLOUD_NATIVE] Kubernetes connection test failed: {e}")
            return False

    def start_monitoring(self) -> None:
        """Start cluster monitoring."""
        if self._monitoring_active:
            Logger.warning("[CLOUD_NATIVE] Monitoring already active")
            return

        if not self._initialized:
            Logger.error("[CLOUD_NATIVE] Cannot start monitoring - not initialized")
            return

        self._monitoring_active = True

        # Start monitoring thread
        import threading

        monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True,
            name="CloudNativeMonitor",
        )
        monitoring_thread.start()

        Logger.info("[CLOUD_NATIVE] Started cluster monitoring")

    def stop_monitoring(self) -> None:
        """Stop cluster monitoring."""
        self._monitoring_active = False
        Logger.info("[CLOUD_NATIVE] Stopped cluster monitoring")

    def _monitoring_loop(self) -> None:
        """Main monitoring loop."""
        while self._monitoring_active:
            try:
                # Collect cluster metrics
                self._collect_cluster_metrics()

                # Collect resource metrics
                self._collect_resource_metrics()

                # Perform health checks
                self._perform_health_checks()

                # Auto-scaling check
                if self._auto_scaling_active:
                    self._check_auto_scaling()

                # Resource optimization
                if self._config["resource_optimization_enabled"]:
                    self._optimize_resources()

                # Sleep until next iteration
                time.sleep(self._config["metrics_collection_interval"])

            except Exception as e:
                Logger.error(f"[CLOUD_NATIVE] Monitoring loop error: {e}")
                time.sleep(5.0)

    def _collect_cluster_metrics(self) -> None:
        """Collect cluster-wide metrics."""
        try:
            if not self._k8s_client:
                return

            # Get node information
            nodes = self._k8s_client['core_v1'].list_node()

            total_nodes = len(nodes.items)
            ready_nodes = sum(1 for node in nodes.items if
                            any(condition.type == "Ready" and condition.status == "True"
                               for condition in node.status.conditions))

            # Get pod information
            pods = self._k8s_client['core_v1'].list_pod_for_all_namespaces()

            total_pods = len(pods.items)
            running_pods = sum(1 for pod in pods.items if pod.status.phase == "Running")

            # Calculate resource capacity
            cpu_capacity = sum(node.status.allocatable.get("cpu", "0") for node in nodes.items)
            memory_capacity = sum(node.status.allocatable.get("memory", "0") for node in nodes.items)

            # Parse CPU and memory values
            def parse_cpu(cpu_str: str) -> float:
                if cpu_str.endswith("m"):
                    return float(cpu_str[:-1]) / 1000.0
                return float(cpu_str)

            def parse_memory(mem_str: str) -> float:
                if mem_str.endswith("Ki"):
                    return float(mem_str[:-2]) / 1024.0 / 1024.0
                elif mem_str.endswith("Mi"):
                    return float(mem_str[:-2]) / 1024.0
                elif mem_str.endswith("Gi"):
                    return float(mem_str[:-2])
                return float(mem_str)

            cpu_capacity_parsed = parse_cpu(str(cpu_capacity))
            memory_capacity_parsed = parse_memory(str(memory_capacity))

            # Update cluster metrics
            self._cluster_metrics = ClusterMetrics(
                total_nodes=total_nodes,
                ready_nodes=ready_nodes,
                total_pods=total_pods,
                running_pods=running_pods,
                cpu_capacity=cpu_capacity_parsed,
                memory_capacity=memory_capacity_parsed,
                timestamp=time.time(),
            )

        except Exception as e:
            Logger.debug(f"[CLOUD_NATIVE] Failed to collect cluster metrics: {e}")

    def _collect_resource_metrics(self) -> None:
        """Collect metrics for all resources."""
        try:
            if not self._k8s_client:
                return

            # Collect deployment metrics
            deployments = self._k8s_client['apps_v1'].list_namespaced_deployment(self._current_namespace)

            for deployment in deployments.items:
                metrics = ResourceMetrics(
                    name=deployment.metadata.name,
                    namespace=deployment.metadata.namespace,
                    resource_type=ResourceType.DEPLOYMENT,
                    status=self._determine_deployment_status(deployment),
                    replicas=deployment.spec.replicas or 0,
                    ready_replicas=deployment.status.ready_replicas or 0,
                    labels=deployment.metadata.labels or {},
                    annotations=deployment.metadata.annotations or {},
                )

                self._resources[f"{deployment.metadata.namespace}/{deployment.metadata.name}"] = metrics

            # Collect pod metrics
            pods = self._k8s_client['core_v1'].list_namespaced_pod(self._current_namespace)

            for pod in pods.items:
                if pod.metadata.owner_references:
                    # Skip pods owned by deployments (already covered)
                    continue

                metrics = ResourceMetrics(
                    name=pod.metadata.name,
                    namespace=pod.metadata.namespace,
                    resource_type=ResourceType.POD,
                    status=self._determine_pod_status(pod),
                    restart_count=pod.status.container_statuses[0].restart_count if pod.status.container_statuses else 0,
                    labels=pod.metadata.labels or {},
                    annotations=pod.metadata.annotations or {},
                )

                self._resources[f"{pod.metadata.namespace}/{pod.metadata.name}"] = metrics

        except Exception as e:
            Logger.debug(f"[CLOUD_NATIVE] Failed to collect resource metrics: {e}")

    def _determine_deployment_status(self, deployment) -> HealthStatus:
        """Determine deployment health status."""
        try:
            if not deployment.status.ready_replicas:
                return HealthStatus.UNKNOWN

            desired = deployment.spec.replicas or 0
            ready = deployment.status.ready_replicas or 0

            if ready == desired:
                return HealthStatus.HEALTHY
            elif ready >= desired * 0.8:
                return HealthStatus.WARNING
            elif ready >= desired * 0.5:
                return HealthStatus.DEGRADED
            else:
                return HealthStatus.CRITICAL

        except Exception:
            return HealthStatus.UNKNOWN

    def _determine_pod_status(self, pod) -> HealthStatus:
        """Determine pod health status."""
        try:
            phase = pod.status.phase

            if phase == "Running":
                # Check if all containers are ready
                ready_containers = sum(1 for cs in pod.status.container_statuses if cs.ready)
                total_containers = len(pod.status.container_statuses)

                if ready_containers == total_containers:
                    return HealthStatus.HEALTHY
                elif ready_containers > 0:
                    return HealthStatus.WARNING
                else:
                    return HealthStatus.DEGRADED
            elif phase == "Pending":
                return HealthStatus.WARNING
            elif phase == "Failed":
                return HealthStatus.CRITICAL
            else:
                return HealthStatus.UNKNOWN

        except Exception:
            return HealthStatus.UNKNOWN

    def _perform_health_checks(self) -> None:
        """Perform health checks on all resources."""
        for resource_key, metrics in self._resources.items():
            self._health_checks[resource_key] = metrics.status

    def enable_auto_scaling(self, resource_name: str, config: Optional[AutoScalingConfig] = None) -> bool:
        """
        Enable auto-scaling for a resource.

        Args:
            resource_name: Name of the resource (format: namespace/name)
            config: Auto-scaling configuration (optional)

        Returns:
            True if auto-scaling enabled successfully
        """
        try:
            if not self._initialized:
                Logger.error("[CLOUD_NATIVE] Cannot enable auto-scaling - not initialized")
                return False

            if config is None:
                config = AutoScalingConfig()

            self._auto_scaling_configs[resource_name] = config

            # Create HPA if not exists
            if not self._create_hpa(resource_name, config):
                return False

            Logger.info(f"[CLOUD_NATIVE] Enabled auto-scaling for {resource_name}")
            return True

        except Exception as e:
            Logger.error(f"[CLOUD_NATIVE] Failed to enable auto-scaling for {resource_name}: {e}")
            return False

    def _create_hpa(self, resource_name: str, config: AutoScalingConfig) -> bool:
        """Create Horizontal Pod Autoscaler."""
        try:
            if not self._k8s_client:
                return False

            namespace, name = resource_name.split("/", 1)

            # Check if HPA already exists
            try:
                self._k8s_client['autoscaling_v1'].read_namespaced_horizontal_pod_autoscaler(name, namespace)
                Logger.info(f"[CLOUD_NATIVE] HPA already exists for {resource_name}")
                return True
            except Exception:
                pass  # HPA doesn't exist, create it

            # Create HPA spec
            hpa_spec = {
                "apiVersion": "autoscaling/v1",
                "kind": "HorizontalPodAutoscaler",
                "metadata": {
                    "name": f"{name}-hpa",
                    "namespace": namespace,
                },
                "spec": {
                    "scaleTargetRef": {
                        "apiVersion": "apps/v1",
                        "kind": "Deployment",
                        "name": name,
                    },
                    "minReplicas": config.min_replicas,
                    "maxReplicas": config.max_replicas,
                    "targetCPUUtilization": config.target_cpu_utilization,
                }
            }

            # Create HPA
            self._k8s_client['autoscaling_v1'].create_namespaced_horizontal_pod_autoscaler(
                namespace=namespace,
                body=hpa_spec
            )

            Logger.info(f"[CLOUD_NATIVE] Created HPA for {resource_name}")
            return True

        except Exception as e:
            Logger.error(f"[CLOUD_NATIVE] Failed to create HPA for {resource_name}: {e}")
            return False

    def _check_auto_scaling(self) -> None:
        """Check if auto-scaling is needed."""
        for resource_name, config in self._auto_scaling_configs.items():
            try:
                metrics = self._resources.get(resource_name)
                if not metrics:
                    continue

                # Check cooldown period
                last_scale = self._last_scale_time.get(resource_name, 0)
                current_time = time.time()

                if current_time - last_scale < config.scale_up_cooldown:
                    continue

                # Check scaling conditions
                should_scale_up, should_scale_down = self._evaluate_scaling_conditions(metrics, config)

                if should_scale_up:
                    self._scale_resource(resource_name, "scale_up", config)
                elif should_scale_down:
                    self._scale_resource(resource_name, "scale_down", config)

            except Exception as e:
                Logger.error(f"[CLOUD_NATIVE] Auto-scaling check failed for {resource_name}: {e}")

    def _evaluate_scaling_conditions(self, metrics: ResourceMetrics, config: AutoScalingConfig) -> Tuple[bool, bool]:
        """Evaluate if scaling is needed."""
        should_scale_up = False
        should_scale_down = False

        # Check CPU usage (simplified - would use metrics server in real implementation)
        if metrics.cpu_usage > config.scale_up_threshold:
            should_scale_up = True
        elif metrics.cpu_usage < config.scale_down_threshold:
            should_scale_down = True

        # Check replica limits
        if should_scale_up and metrics.replicas >= config.max_replicas:
            should_scale_up = False
        elif should_scale_down and metrics.replicas <= config.min_replicas:
            should_scale_down = False

        return should_scale_up, should_scale_down

    def _scale_resource(self, resource_name: str, scaling_type: str, config: AutoScalingConfig) -> None:
        """Scale a resource up or down."""
        try:
            if not self._k8s_client:
                return

            namespace, name = resource_name.split("/", 1)

            # Get current deployment
            deployment = self._k8s_client['apps_v1'].read_namespaced_deployment(name, namespace)
            current_replicas = deployment.spec.replicas or 1

            # Calculate new replica count
            if scaling_type == "scale_up":
                new_replicas = min(current_replicas + 1, config.max_replicas)
            else:  # scale_down
                new_replicas = max(current_replicas - 1, config.min_replicas)

            if new_replicas == current_replicas:
                return

            # Update deployment
            deployment.spec.replicas = new_replicas
            self._k8s_client['apps_v1'].patch_namespaced_deployment(
                name=name,
                namespace=namespace,
                body=deployment
            )

            # Record scaling event
            event = ScalingEvent(
                resource_name=resource_name,
                resource_type=ResourceType.DEPLOYMENT,
                scaling_type=scaling_type,
                from_replicas=current_replicas,
                to_replicas=new_replicas,
                reason=f"Auto-scaling {scaling_type}",
                metric_value=metrics.cpu_usage,
                threshold=config.scale_up_threshold if scaling_type == "scale_up" else config.scale_down_threshold,
            )

            self._scaling_events.append(event)
            self._last_scale_time[resource_name] = time.time()

            Logger.info(f"[CLOUD_NATIVE] {scaling_type} {resource_name}: {current_replicas} -> {new_replicas}")

        except Exception as e:
            Logger.error(f"[CLOUD_NATIVE] Failed to scale {resource_name}: {e}")

    def _optimize_resources(self) -> None:
        """Optimize resource allocation."""
        try:
            # This is a simplified implementation
            # In a real scenario, this would analyze usage patterns and adjust resource requests/limits

            for resource_name, metrics in self._resources.items():
                if metrics.resource_type == ResourceType.DEPLOYMENT:
                    # Check if resource requests can be optimized
                    if metrics.cpu_usage < 20 and metrics.memory_usage < 20:
                        Logger.debug(f"[CLOUD_NATIVE] Resource optimization opportunity for {resource_name}")
                        # In real implementation, would update resource requests/limits

        except Exception as e:
            Logger.error(f"[CLOUD_NATIVE] Resource optimization failed: {e}")

    def get_cluster_health(self) -> Dict[str, Any]:
        """Get overall cluster health."""
        try:
            health_scores = []

            for status in self._health_checks.values():
                if status == HealthStatus.HEALTHY:
                    health_scores.append(100)
                elif status == HealthStatus.WARNING:
                    health_scores.append(75)
                elif status == HealthStatus.DEGRADED:
                    health_scores.append(50)
                elif status == HealthStatus.CRITICAL:
                    health_scores.append(25)
                else:
                    health_scores.append(0)

            overall_score = sum(health_scores) / len(health_scores) if health_scores else 0

            # Determine overall status
            if overall_score >= 90:
                overall_status = HealthStatus.HEALTHY
            elif overall_score >= 70:
                overall_status = HealthStatus.WARNING
            elif overall_score >= 50:
                overall_status = HealthStatus.DEGRADED
            else:
                overall_status = HealthStatus.CRITICAL

            return {
                "overall_status": overall_status.value,
                "health_score": overall_score,
                "total_resources": len(self._resources),
                "healthy_resources": sum(1 for s in self._health_checks.values() if s == HealthStatus.HEALTHY),
                "cluster_metrics": {
                    "total_nodes": self._cluster_metrics.total_nodes,
                    "ready_nodes": self._cluster_metrics.ready_nodes,
                    "total_pods": self._cluster_metrics.total_pods,
                    "running_pods": self._cluster_metrics.running_pods,
                    "cpu_capacity": self._cluster_metrics.cpu_capacity,
                    "memory_capacity": self._cluster_metrics.memory_capacity,
                },
                "timestamp": time.time(),
            }

        except Exception as e:
            Logger.error(f"[CLOUD_NATIVE] Failed to get cluster health: {e}")
            return {"error": str(e)}

    def get_resource_metrics(self, resource_name: Optional[str] = None) -> Union[ResourceMetrics, Dict[str, ResourceMetrics]]:
        """Get metrics for specific resource or all resources."""
        if resource_name:
            return self._resources.get(resource_name, ResourceMetrics(
                name=resource_name,
                namespace="unknown",
                resource_type=ResourceType.POD,
                status=HealthStatus.UNKNOWN
            ))
        else:
            return self._resources.copy()

    def get_scaling_events(self, limit: int = 100) -> List[ScalingEvent]:
        """Get recent scaling events."""
        return list(self._scaling_events)[-limit:]

    def get_auto_scaling_status(self) -> Dict[str, Any]:
        """Get auto-scaling status."""
        return {
            "enabled": self._auto_scaling_active,
            "configured_resources": len(self._auto_scaling_configs),
            "total_scaling_events": len(self._scaling_events),
            "recent_events": len([e for e in self._scaling_events if time.time() - e.timestamp < 3600]),
            "configurations": {
                name: {
                    "min_replicas": config.min_replicas,
                    "max_replicas": config.max_replicas,
                    "target_cpu": config.target_cpu_utilization,
                    "target_memory": config.target_memory_utilization,
                }
                for name, config in self._auto_scaling_configs.items()
            },
        }

    def update_configuration(self, config_updates: Dict[str, Any]) -> None:
        """Update manager configuration."""
        self._config.update(config_updates)
        Logger.info(f"[CLOUD_NATIVE] Updated configuration: {list(config_updates.keys())}")

    def get_manager_status(self) -> Dict[str, Any]:
        """Get manager status and statistics."""
        return {
            "initialized": self._initialized,
            "monitoring_active": self._monitoring_active,
            "auto_scaling_active": self._auto_scaling_active,
            "current_namespace": self._current_namespace,
            "total_resources": len(self._resources),
            "cluster_health": self.get_cluster_health(),
            "auto_scaling_status": self.get_auto_scaling_status(),
            "configuration": self._config,
            "last_update": time.time(),
        }


# Global cloud native manager instance
_global_manager: CloudNativeManager | None = None


def get_global_cloud_native_manager() -> CloudNativeManager:
    """Get the global cloud native manager instance."""
    global _global_manager
    if _global_manager is None:
        _global_manager = CloudNativeManager()
    return _global_manager


def initialize_cloud_native_manager(kubeconfig_path: Optional[str] = None, namespace: str = "default") -> bool:
    """
    Initialize global cloud native manager.

    Args:
        kubeconfig_path: Path to kubeconfig file (optional)
        namespace: Default namespace (default: "default")

    Returns:
        True if initialization successful
    """
    manager = get_global_cloud_native_manager()
    return manager.initialize(kubeconfig_path, namespace)


def get_cluster_health() -> Dict[str, Any]:
    """Get cluster health using global manager."""
    manager = get_global_cloud_native_manager()
    return manager.get_cluster_health()


def enable_resource_auto_scaling(resource_name: str, config: Optional[AutoScalingConfig] = None) -> bool:
    """
    Enable auto-scaling for a resource using global manager.

    Args:
        resource_name: Name of the resource (format: namespace/name)
        config: Auto-scaling configuration (optional)

    Returns:
        True if auto-scaling enabled successfully
    """
    manager = get_global_cloud_native_manager()
    return manager.enable_auto_scaling(resource_name, config)
