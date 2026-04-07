"""Opportunity 1: Unified Query Router & Load Balancer

Implements centralized query routing, load balancing, circuit breaking,
and health monitoring for the 4-layer retrieval pattern.
"""

import asyncio
import logging
import random
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

from .implementation_plan import (
    FourLayerContractError,
    FourLayerContractGuard,
    HealthStatus,
    LayerResponse,
    LayerType,
    QueryRequest,
    QueryStatus,
)

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states."""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration."""

    failure_threshold: int = 5
    recovery_timeout_seconds: int = 60
    success_threshold: int = 3
    timeout_seconds: int = 30


@dataclass
class LoadBalancerConfig:
    """Load balancer configuration."""

    algorithm: str = "round_robin"  # round_robin, weighted, least_connections
    health_check_interval_seconds: int = 30
    max_retries: int = 3
    retry_delay_seconds: float = 1.0


class CircuitBreaker:
    """Circuit breaker implementation for layer protection."""

    CircuitState = CircuitState

    def __init__(self, layer_type: LayerType, config: CircuitBreakerConfig):
        self.layer_type = layer_type
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.last_state_change = datetime.now()

    async def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                logger.info(f"Circuit breaker for {self.layer_type} transitioning to HALF_OPEN")
            else:
                raise Exception(f"Circuit breaker OPEN for {self.layer_type}")

        try:
            result = await func(*args, **kwargs)
            if result is None:
                raise Exception("Circuit breaker operation returned no result")
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e

    def _should_attempt_reset(self) -> bool:
        """Check if circuit should attempt reset."""
        if self.last_failure_time is None:
            return False
        return (
            datetime.now() - self.last_failure_time
        ).total_seconds() >= self.config.recovery_timeout_seconds

    def _on_success(self):
        """Handle successful call."""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.success_count = 0
                logger.info(f"Circuit breaker for {self.layer_type} CLOSED")

    def _on_failure(self):
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            logger.warning(f"Circuit breaker for {self.layer_type} OPEN from HALF_OPEN")
        elif self.failure_count >= self.config.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(f"Circuit breaker for {self.layer_type} OPEN")


class LayerInstance:
    """Represents an individual layer instance for load balancing."""

    def __init__(self, instance_id: str, layer_type: LayerType, endpoint: str, weight: int = 1):
        self.instance_id = instance_id
        self.layer_type = layer_type
        self.endpoint = endpoint
        self.weight = weight
        self.healthy = True
        self.last_health_check = datetime.now()
        self.response_times = deque(maxlen=100)
        self.active_connections = 0
        self.total_requests = 0
        self.failed_requests = 0

    def add_response_time(self, response_time_ms: float):
        """Add response time for performance tracking."""
        self.response_times.append(response_time_ms)

    def get_average_response_time(self) -> float:
        """Get average response time."""
        return sum(self.response_times) / len(self.response_times) if self.response_times else 0.0

    def get_error_rate(self) -> float:
        """Get error rate."""
        return self.failed_requests / self.total_requests if self.total_requests > 0 else 0.0


class LoadBalancer:
    """Load balancer for distributing queries across layer instances."""

    def __init__(self, layer_type: LayerType, config: LoadBalancerConfig):
        self.layer_type = layer_type
        self.config = config
        self.instances: dict[str, LayerInstance] = {}
        self.current_index = 0
        self._lock = asyncio.Lock()

    def add_instance(self, instance_id: str, endpoint: str, weight: int = 1):
        """Add a layer instance."""
        self.instances[instance_id] = LayerInstance(instance_id, self.layer_type, endpoint, weight)
        logger.info(f"Added instance {instance_id} for {self.layer_type}")

    def remove_instance(self, instance_id: str):
        """Remove a layer instance."""
        if instance_id in self.instances:
            del self.instances[instance_id]
            logger.info(f"Removed instance {instance_id} for {self.layer_type}")

    async def select_instance(self) -> LayerInstance | None:
        """Select an instance based on load balancing algorithm."""
        healthy_instances = [inst for inst in self.instances.values() if inst.healthy]

        if not healthy_instances:
            return None

        async with self._lock:
            if self.config.algorithm == "round_robin":
                return self._round_robin_select(healthy_instances)
            elif self.config.algorithm == "weighted":
                return self._weighted_select(healthy_instances)
            elif self.config.algorithm == "least_connections":
                return self._least_connections_select(healthy_instances)
            else:
                return healthy_instances[0]

    def _round_robin_select(self, instances: list[LayerInstance]) -> LayerInstance:
        """Round-robin instance selection."""
        instance = instances[self.current_index % len(instances)]
        self.current_index += 1
        return instance

    def _weighted_select(self, instances: list[LayerInstance]) -> LayerInstance:
        """Weighted instance selection."""
        total_weight = sum(inst.weight for inst in instances)
        if total_weight == 0:
            return instances[0]

        rand = random.uniform(0, total_weight)
        current_weight = 0

        for instance in instances:
            current_weight += instance.weight
            if rand <= current_weight:
                return instance

        return instances[-1]

    def _least_connections_select(self, instances: list[LayerInstance]) -> LayerInstance:
        """Least connections instance selection."""
        return min(instances, key=lambda inst: inst.active_connections)


class HealthChecker:
    """Health monitoring for layer instances."""

    def __init__(self, check_interval_seconds: int = 30):
        self.check_interval = check_interval_seconds
        self.health_status: dict[str, HealthStatus] = {}
        self._running = False

    async def start_monitoring(self, load_balancers: dict[LayerType, LoadBalancer]):
        """Start health monitoring."""
        self._running = True
        while self._running:
            await self._perform_health_checks(load_balancers)
            await asyncio.sleep(self.check_interval)

    async def stop_monitoring(self):
        """Stop health monitoring."""
        self._running = False

    async def _perform_health_checks(self, load_balancers: dict[LayerType, LoadBalancer]):
        """Perform health checks on all instances."""
        tasks = []

        for layer_type, load_balancer in load_balancers.items():
            for instance in load_balancer.instances.values():
                tasks.append(self._check_instance_health(instance))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _check_instance_health(self, instance: LayerInstance):
        """Check health of individual instance."""
        start_time = time.time()

        try:
            # Simulate health check - in real implementation, this would ping the endpoint
            await asyncio.sleep(0.01)  # Simulate network latency

            response_time = (time.time() - start_time) * 1000
            instance.healthy = True
            instance.last_health_check = datetime.now()
            instance.add_response_time(response_time)

            # Update health status
            self.health_status[instance.instance_id] = HealthStatus(
                component_id=instance.instance_id,
                layer_type=instance.layer_type,
                healthy=True,
                last_check=datetime.now(),
                response_time_ms=response_time,
                error_rate=instance.get_error_rate(),
                throughput=instance.total_requests
                / max(1, (datetime.now() - instance.last_health_check).total_seconds()),
            )

        except Exception as e:
            instance.healthy = False
            instance.last_health_check = datetime.now()
            instance.failed_requests += 1

            logger.warning(f"Health check failed for {instance.instance_id}: {e}")

            self.health_status[instance.instance_id] = HealthStatus(
                component_id=instance.instance_id,
                layer_type=instance.layer_type,
                healthy=False,
                last_check=datetime.now(),
                response_time_ms=0.0,
                error_rate=1.0,
                throughput=0.0,
                details={"error": str(e)},
            )


class UnifiedQueryRouter:
    """Unified query router with load balancing and circuit breaking."""

    def __init__(self, l4_rate_limit_per_minute: int = 30):
        self.load_balancers: dict[LayerType, LoadBalancer] = {}
        self.circuit_breakers: dict[LayerType, CircuitBreaker] = {
            layer_type: CircuitBreaker(layer_type, CircuitBreakerConfig())
            for layer_type in LayerType
        }
        self.health_checker = HealthChecker()
        self.query_stats = defaultdict(lambda: {"total": 0, "success": 0, "failed": 0})
        self._routing_rules = []
        self._lock = asyncio.Lock()
        self.contract_guard = FourLayerContractGuard(
            l4_rate_limit_per_minute=l4_rate_limit_per_minute,
        )

    def add_layer_instances(self, layer_type: LayerType, instances: list[tuple[str, str, int]]):
        """Add instances for a layer."""
        config = LoadBalancerConfig()
        load_balancer = LoadBalancer(layer_type, config)

        for instance_id, endpoint, weight in instances:
            load_balancer.add_instance(instance_id, endpoint, weight)

        self.load_balancers[layer_type] = load_balancer

        # Add circuit breaker
        circuit_config = CircuitBreakerConfig()
        self.circuit_breakers[layer_type] = CircuitBreaker(layer_type, circuit_config)

        logger.info(f"Added {len(instances)} instances for {layer_type}")

    async def start_health_monitoring(self):
        """Start health monitoring."""
        asyncio.create_task(self.health_checker.start_monitoring(self.load_balancers))

    async def stop_health_monitoring(self):
        """Stop health monitoring."""
        await self.health_checker.stop_monitoring()

    async def route_query(self, request: QueryRequest, target_layers: list[LayerType]) -> list[LayerResponse]:
        """Route query through specified layers."""
        responses = []

        try:
            self.contract_guard.validate_query_request(request)
            self.contract_guard.validate_layer_sequence(target_layers)

            if LayerType.AGENTIC_ACTION in target_layers:
                security_context = request.security_context or {}
                user_id = security_context.get("user_id") or request.query_id
                self.contract_guard.enforce_l4_rate_limit(user_id)
        except FourLayerContractError as e:    # guardian: FourLayerContractError should be handled with specific context
            fail_layer = target_layers[0] if target_layers else LayerType.REDIS_EXACT_MATCH
            return [
                LayerResponse(
                    layer_type=fail_layer,
                    status=QueryStatus.FAILED,
                    error_message=f"Contract violation: {e}",
                ),
            ]

        for layer_type in target_layers:
            try:
                response = await self._execute_layer_query(request, layer_type)
                responses.append(response)

                # Update stats
                self.query_stats[layer_type.value]["total"] += 1
                if response.status == QueryStatus.COMPLETED:
                    self.query_stats[layer_type.value]["success"] += 1
                else:
                    self.query_stats[layer_type.value]["failed"] += 1

                # Stop routing if layer fails
                if response.status in [QueryStatus.FAILED, QueryStatus.CIRCUIT_OPEN]:
                    break

            except Exception as e:
                logger.error(f"Error routing query to {layer_type}: {e}")

                error_response = LayerResponse(
                    layer_type=layer_type, status=QueryStatus.FAILED, error_message=str(e),
                )
                responses.append(error_response)
                break

        return responses

    async def _execute_layer_query(self, request: QueryRequest, layer_type: LayerType) -> LayerResponse:
        """Execute query on specific layer."""
        if layer_type not in self.load_balancers:
            return LayerResponse(
                layer_type=layer_type,
                status=QueryStatus.FAILED,
                error_message=f"No instances configured for {layer_type}",
            )

        load_balancer = self.load_balancers[layer_type]
        circuit_breaker = self.circuit_breakers[layer_type]

        # Select instance
        instance = await load_balancer.select_instance()
        if not instance:
            return LayerResponse(
                layer_type=layer_type,
                status=QueryStatus.FAILED,
                error_message=f"No healthy instances available for {layer_type}",
            )

        # Execute with circuit breaker protection
        try:
            return await circuit_breaker.call(self._simulate_layer_execution, request, layer_type, instance)
        except Exception as e:
            if "Circuit breaker OPEN" in str(e):
                return LayerResponse(
                    layer_type=layer_type,
                    status=QueryStatus.CIRCUIT_OPEN,
                    error_message="Circuit breaker is open",
                )
            else:
                return LayerResponse(layer_type=layer_type, status=QueryStatus.FAILED, error_message=str(e))

    async def _simulate_layer_execution(
        self, request: QueryRequest, layer_type: LayerType, instance: LayerInstance,
    ) -> LayerResponse:
        """Simulate layer execution (placeholder for actual implementation)."""
        start_time = time.time()
        instance.active_connections += 1
        instance.total_requests += 1

        try:
            # Simulate processing time based on layer type
            processing_times = {
                LayerType.REDIS_EXACT_MATCH: random.uniform(1, 5),
                LayerType.SEMANTIC_CACHE: random.uniform(10, 50),
                LayerType.RAG_RETRIEVAL: random.uniform(100, 500),
                LayerType.AGENTIC_ACTION: random.uniform(200, 1000),
            }

            processing_time = processing_times.get(layer_type, 100)
            await asyncio.sleep(processing_time / 1000)  # Convert to seconds

            # Simulate success/failure based on layer type
            success_rates = {
                LayerType.REDIS_EXACT_MATCH: 0.99,
                LayerType.SEMANTIC_CACHE: 0.95,
                LayerType.RAG_RETRIEVAL: 0.90,
                LayerType.AGENTIC_ACTION: 0.85,
            }

            if random.random() < success_rates.get(layer_type, 0.9):
                response_time = (time.time() - start_time) * 1000
                instance.add_response_time(response_time)

                return LayerResponse(
                    layer_type=layer_type,
                    status=QueryStatus.COMPLETED,
                    data=f"Mock response from {layer_type.value}",
                    processing_time_ms=response_time,
                    cache_hit=random.random() < 0.3,
                )
            else:
                instance.failed_requests += 1
                raise Exception(f"Simulated failure in {layer_type}")

        finally:
            instance.active_connections -= 1

    def get_routing_stats(self) -> dict[str, Any]:
        """Get routing statistics."""
        return {
            "query_stats": dict(self.query_stats),
            "health_status": {k: v.__dict__ for k, v in self.health_checker.health_status.items()},
            "instance_count": {layer.value: len(lb.instances) for layer, lb in self.load_balancers.items()},
            "circuit_status": {layer.value: cb.state.value for layer, cb in self.circuit_breakers.items()},
        }

    def get_layer_health(self) -> dict[LayerType, dict[str, Any]]:
        """Get health status for all layers."""
        health_report = {}

        for layer_type, load_balancer in self.load_balancers.items():
            healthy_instances = sum(1 for inst in load_balancer.instances.values() if inst.healthy)
            total_instances = len(load_balancer.instances)

            avg_response_time = 0.0
            if load_balancer.instances:
                response_times = [
                    inst.get_average_response_time() for inst in load_balancer.instances.values()
                ]
                avg_response_time = sum(response_times) / len(response_times)

            health_report[layer_type] = {
                "healthy_instances": healthy_instances,
                "total_instances": total_instances,
                "health_percentage": (healthy_instances / total_instances * 100)
                if total_instances > 0
                else 0,
                "average_response_time_ms": avg_response_time,
                "circuit_state": self.circuit_breakers[layer_type].state.value,
            }

        return health_report
