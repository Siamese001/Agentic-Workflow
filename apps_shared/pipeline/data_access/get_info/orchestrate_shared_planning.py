"""Shared Planning Orchestrator - Coordinates shared resource and service operations.

This orchestrator manages the planning phase for shared operations,
including resource sharing, service coordination, and common utility management.
Follows the canonical pattern with dataclass-first design and proper logging.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ResourceType(Enum):
    """Types of shared resources."""
    DATABASE = "database"
    CACHE = "cache"
    QUEUE = "queue"
    STORAGE = "storage"
    API_GATEWAY = "api_gateway"
    MESSAGE_BUS = "message_bus"


class SharingPolicy(Enum):
    """Policies for resource sharing."""
    SHARED = "shared"
    DEDICATED = "dedicated"
    POOL = "pool"
    ISOLATED = "isolated"


class AccessLevel(Enum):
    """Access levels for shared resources."""
    READ_ONLY = "read_only"
    READ_WRITE = "read_write"
    ADMIN = "admin"
    OWNER = "owner"


@dataclass
class SharedResource:
    """Definition of a shared resource."""
    id: str
    name: str
    resource_type: ResourceType
    sharing_policy: SharingPolicy
    access_level: AccessLevel
    endpoint: Optional[str] = None
    credentials: Dict[str, Any] = field(default_factory=dict)
    limits: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)


@dataclass
class ServiceDependency:
    """Definition of a service dependency."""
    service_id: str
    service_name: str
    version: str
    required_resources: List[str] = field(default_factory=list)
    provides_resources: List[str] = field(default_factory=list)
    endpoints: Dict[str, str] = field(default_factory=dict)


@dataclass
class SharingPlan:
    """Plan for resource sharing across services."""
    shared_resources: List[SharedResource]
    service_dependencies: List[ServiceDependency]
    access_matrix: Dict[str, Dict[str, AccessLevel]] = field(default_factory=dict)
    conflict_resolution: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SharedPlanningConfig:
    """Configuration for shared planning orchestrator."""
    enable_resource_pooling: bool = True
    enable_access_control: bool = True
    enable_conflict_detection: bool = True
    max_shared_resources: int = 100
    default_sharing_policy: SharingPolicy = SharingPolicy.SHARED
    log_level: str = "INFO"


@dataclass
class SharedPlanningResult:
    """Result of shared planning orchestration."""
    success: bool
    sharing_plan: Optional[SharingPlan] = None
    resource_allocations: Dict[str, Any] = field(default_factory=dict)
    access_grants: List[Dict[str, Any]] = field(default_factory=list)
    conflicts: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class SharedPlanningOrchestrator:
    """Orchestrator for planning shared operations."""

    def __init__(self, config: Optional[SharedPlanningConfig] = None):
        self.config = config or SharedPlanningConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(self.config.log_level)

    def execute(self, shared_request: Dict[str, Any]) -> SharedPlanningResult:
        """Execute the shared planning orchestration.
        
        Args:
            shared_request: Dictionary containing shared resource requirements
            
        Returns:
            SharedPlanningResult: Complete planning result with sharing plan and allocations
        """
        self.logger.info(f"Starting shared planning for: {shared_request.get('domain', 'unknown')}")
        
        try:
            # Validate input request
            self._validate_request(shared_request)
            
            # Parse shared resources
            shared_resources = self._parse_shared_resources(shared_request)
            
            # Parse service dependencies
            service_dependencies = self._parse_service_dependencies(shared_request)
            
            # Create sharing plan
            sharing_plan = self._create_sharing_plan(shared_resources, service_dependencies)
            
            # Calculate resource allocations
            resource_allocations = self._calculate_resource_allocations(sharing_plan)
            
            # Generate access grants
            access_grants = self._generate_access_grants(sharing_plan)
            
            # Detect conflicts
            conflicts = self._detect_conflicts(sharing_plan) if self.config.enable_conflict_detection else []
            
            result = SharedPlanningResult(
                success=len(conflicts) == 0,
                sharing_plan=sharing_plan,
                resource_allocations=resource_allocations,
                access_grants=access_grants,
                conflicts=conflicts,
                metadata={
                    "planned_at": datetime.utcnow().isoformat(),
                    "domain": shared_request.get("domain"),
                    "resource_count": len(shared_resources),
                    "service_count": len(service_dependencies),
                    "orchestrator": "SharedPlanningOrchestrator"
                }
            )
            
            self.logger.info(f"Successfully planned shared resources: {len(shared_resources)} resources, {len(service_dependencies)} services")
            return result
            
        except Exception as e:
            self.logger.error(f"Shared planning failed: {str(e)}")
            return SharedPlanningResult(
                success=False,
                errors=[str(e)],
                metadata={
                    "failed_at": datetime.utcnow().isoformat(),
                    "orchestrator": "SharedPlanningOrchestrator"
                }
            )

    def _validate_request(self, request: Dict[str, Any]) -> None:
        """Validate shared planning request."""
        if not request:
            raise ValueError("Shared request cannot be empty")
        
        if "domain" not in request:
            raise ValueError("Domain is required in shared request")

    def _parse_shared_resources(self, request: Dict[str, Any]) -> List[SharedResource]:
        """Parse shared resources from request."""
        resources = []
        raw_resources = request.get("shared_resources", [])
        
        for raw_resource in raw_resources:
            if isinstance(raw_resource, dict):
                # Map strings to enums
                resource_mapping = {
                    "database": ResourceType.DATABASE,
                    "cache": ResourceType.CACHE,
                    "queue": ResourceType.QUEUE,
                    "storage": ResourceType.STORAGE,
                    "api_gateway": ResourceType.API_GATEWAY,
                    "message_bus": ResourceType.MESSAGE_BUS
                }
                
                sharing_mapping = {
                    "shared": SharingPolicy.SHARED,
                    "dedicated": SharingPolicy.DEDICATED,
                    "pool": SharingPolicy.POOL,
                    "isolated": SharingPolicy.ISOLATED
                }
                
                access_mapping = {
                    "read_only": AccessLevel.READ_ONLY,
                    "read_write": AccessLevel.READ_WRITE,
                    "admin": AccessLevel.ADMIN,
                    "owner": AccessLevel.OWNER
                }
                
                resource = SharedResource(
                    id=raw_resource.get("id", f"resource_{len(resources)}"),
                    name=raw_resource.get("name", "unnamed"),
                    resource_type=resource_mapping.get(
                        raw_resource.get("type", "database"),
                        ResourceType.DATABASE
                    ),
                    sharing_policy=sharing_mapping.get(
                        raw_resource.get("sharing_policy", "shared"),
                        SharingPolicy.SHARED
                    ),
                    access_level=access_mapping.get(
                        raw_resource.get("access_level", "read_write"),
                        AccessLevel.READ_WRITE
                    ),
                    endpoint=raw_resource.get("endpoint"),
                    credentials=raw_resource.get("credentials", {}),
                    limits=raw_resource.get("limits", {}),
                    tags=raw_resource.get("tags", [])
                )
                resources.append(resource)
        
        return resources

    def _parse_service_dependencies(self, request: Dict[str, Any]) -> List[ServiceDependency]:
        """Parse service dependencies from request."""
        dependencies = []
        raw_dependencies = request.get("service_dependencies", [])
        
        for raw_dep in raw_dependencies:
            if isinstance(raw_dep, dict):
                dependency = ServiceDependency(
                    service_id=raw_dep.get("service_id", f"service_{len(dependencies)}"),
                    service_name=raw_dep.get("service_name", "unnamed"),
                    version=raw_dep.get("version", "1.0.0"),
                    required_resources=raw_dep.get("required_resources", []),
                    provides_resources=raw_dep.get("provides_resources", []),
                    endpoints=raw_dep.get("endpoints", {})
                )
                dependencies.append(dependency)
        
        return dependencies

    def _create_sharing_plan(
        self, 
        resources: List[SharedResource], 
        dependencies: List[ServiceDependency]
    ) -> SharingPlan:
        """Create sharing plan from resources and dependencies."""
        # Build access matrix
        access_matrix = {}
        
        for service in dependencies:
            service_access = {}
            for resource in resources:
                if resource.id in service.required_resources:
                    service_access[resource.id] = resource.access_level
                else:
                    service_access[resource.id] = AccessLevel.READ_ONLY
            access_matrix[service.service_id] = service_access
        
        return SharingPlan(
            shared_resources=resources,
            service_dependencies=dependencies,
            access_matrix=access_matrix,
            conflict_resolution={
                "strategy": "priority_based",
                "rules": [
                    "owner_access_overrides",
                    "dedicated_resources_isolated",
                    "pool_resources_shared"
                ]
            }
        )

    def _calculate_resource_allocations(self, plan: SharingPlan) -> Dict[str, Any]:
        """Calculate resource allocations based on sharing plan."""
        allocations = {}
        
        for resource in plan.shared_resources:
            resource_allocations = {
                "consumers": [],
                "providers": [],
                "total_capacity": resource.limits.get("capacity", "unlimited"),
                "used_capacity": 0,
                "utilization_percentage": 0.0
            }
            
            # Find consumers and providers
            for service in plan.service_dependencies:
                if resource.id in service.required_resources:
                    resource_allocations["consumers"].append(service.service_id)
                if resource.id in service.provides_resources:
                    resource_allocations["providers"].append(service.service_id)
            
            allocations[resource.id] = resource_allocations
        
        return allocations

    def _generate_access_grants(self, plan: SharingPlan) -> List[Dict[str, Any]]:
        """Generate access grants based on sharing plan."""
        grants = []
        
        for service_id, access_map in plan.access_matrix.items():
            for resource_id, access_level in access_map.items():
                if access_level != AccessLevel.READ_ONLY:  # Only grant explicit access
                    grant = {
                        "service_id": service_id,
                        "resource_id": resource_id,
                        "access_level": access_level.value,
                        "granted_at": datetime.utcnow().isoformat(),
                        "expires_at": None  # No expiration by default
                    }
                    grants.append(grant)
        
        return grants

    def _detect_conflicts(self, plan: SharingPlan) -> List[Dict[str, Any]]:
        """Detect conflicts in sharing plan."""
        conflicts = []
        
        # Check for resource over-allocation
        for resource in plan.shared_resources:
            consumer_count = sum(
                1 for service in plan.service_dependencies 
                if resource.id in service.required_resources
            )
            
            max_consumers = resource.limits.get("max_consumers", 10)
            if consumer_count > max_consumers:
                conflicts.append({
                    "type": "over_allocation",
                    "resource_id": resource.id,
                    "message": f"Resource {resource.name} has {consumer_count} consumers, max allowed: {max_consumers}"
                })
        
        # Check for access level conflicts
        for resource in plan.shared_resources:
            if resource.sharing_policy == SharingPolicy.DEDICATED:
                consumers = [
                    service.service_id for service in plan.service_dependencies
                    if resource.id in service.required_resources
                ]
                if len(consumers) > 1:
                    conflicts.append({
                        "type": "access_conflict",
                        "resource_id": resource.id,
                        "message": f"Dedicated resource {resource.name} cannot be shared by multiple services: {consumers}"
                    })
        
        return conflicts


# Factory function for easy instantiation
def create_shared_planning_orchestrator(
    enable_resource_pooling: bool = True,
    enable_access_control: bool = True,
    **kwargs
) -> SharedPlanningOrchestrator:
    """Create a configured shared planning orchestrator."""
    config = SharedPlanningConfig(
        enable_resource_pooling=enable_resource_pooling,
        enable_access_control=enable_access_control,
        **kwargs
    )
    return SharedPlanningOrchestrator(config)


# Convenience function for direct usage
def plan_shared_resources(
    domain: str,
    shared_resources: List[Dict[str, Any]],
    service_dependencies: Optional[List[Dict[str, Any]]] = None,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Plan shared resources from simple parameters.
    
    Args:
        domain: Domain name for the shared resources
        shared_resources: List of shared resource definitions
        service_dependencies: Optional list of service dependencies
        config: Optional orchestrator configuration overrides
        
    Returns:
        Dict: Planning result with sharing plan and allocations
    """
    # Build request
    request = {
        "domain": domain,
        "shared_resources": shared_resources,
        "service_dependencies": service_dependencies or []
    }
    
    # Create orchestrator and execute
    orchestrator_config = SharedPlanningConfig(**config) if config else None
    orchestrator = SharedPlanningOrchestrator(orchestrator_config)
    result = orchestrator.execute(request)
    
    # Convert result to dict for JSON serialization
    return {
        "success": result.success,
        "sharing_plan": {
            "shared_resources": [
                {
                    "id": r.id,
                    "name": r.name,
                    "resource_type": r.resource_type.value,
                    "sharing_policy": r.sharing_policy.value,
                    "access_level": r.access_level.value,
                    "endpoint": r.endpoint,
                    "limits": r.limits,
                    "tags": r.tags
                }
                for r in result.sharing_plan.shared_resources
            ],
            "service_dependencies": [
                {
                    "service_id": s.service_id,
                    "service_name": s.service_name,
                    "version": s.version,
                    "required_resources": s.required_resources,
                    "provides_resources": s.provides_resources,
                    "endpoints": s.endpoints
                }
                for s in result.sharing_plan.service_dependencies
            ],
            "access_matrix": {
                service_id: {
                    resource_id: access.value
                    for resource_id, access in access_map.items()
                }
                for service_id, access_map in result.sharing_plan.access_matrix.items()
            },
            "conflict_resolution": result.sharing_plan.conflict_resolution
        } if result.sharing_plan else None,
        "resource_allocations": result.resource_allocations,
        "access_grants": result.access_grants,
        "conflicts": result.conflicts,
        "warnings": result.warnings,
        "errors": result.errors,
        "metadata": result.metadata
