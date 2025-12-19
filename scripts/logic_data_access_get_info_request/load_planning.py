"""Scripts Load Planner - Plans data loading operations for scripts and automation.

This planner manages the loading phase for script data operations,
including source identification, data extraction strategies, and loading optimization.
Follows the canonical pattern with dataclass-first design and proper logging.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

LOGGER = logging.getLogger(__name__)


class LoadStrategy(Enum):
    """Strategies for loading data."""
    BATCH_LOAD = "batch_load"
    STREAMING_LOAD = "streaming_load"
    INCREMENTAL_LOAD = "incremental_load"
    FULL_REFRESH = "full_refresh"


class DataSourceType(Enum):
    """Types of data sources."""
    FILE_SYSTEM = "file_system"
    DATABASE = "database"
    API = "api"
    STREAM = "stream"
    CLOUD_STORAGE = "cloud_storage"


class DataFormat(Enum):
    """Supported data formats."""
    JSON = "json"
    CSV = "csv"
    PARQUET = "parquet"
    XML = "xml"
    BINARY = "binary"


@dataclass
class LoadSource:
    """Definition of a data loading source."""
    id: str
    name: str
    source_type: DataSourceType
    location: str
    format: DataFormat
    credentials: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LoadTransformation:
    """Definition of a data transformation during load."""
    id: str
    name: str
    transformation_type: str  # filter, map, reduce, aggregate
    parameters: Dict[str, Any] = field(default_factory=dict)
    conditions: List[str] = field(default_factory=list)


@dataclass
class LoadPlan:
    """Complete plan for data loading operations."""
    id: str
    name: str
    load_strategy: LoadStrategy
    sources: List[LoadSource]
    transformations: List[LoadTransformation] = field(default_factory=list)
    DESTINATION: str = ""
    batch_size: int = 1000
    parallel_workers: int = 1
    retry_attempts: int = 3
    timeout_seconds: int = 300
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LoadPlanningConfig:
    """Configuration for load planning operations."""
    enable_parallel_loading: bool = True
    enable_compression: bool = False
    enable_validation: bool = True
    max_sources_per_plan: int = 10
    default_batch_size: int = 1000
    log_level: str = "INFO"


@dataclass
class LoadPlanningResult:
    """Result of load planning operations."""
    success: bool
    load_plan: Optional[LoadPlan] = None
    estimated_duration: int = 0
    data_volume_estimate: int = 0
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ScriptsLoadPlanner:
    """Planner for scripts data loading operations."""

    def __init__(self, config: Optional[LoadPlanningConfig] = None):
        self.config = config or LoadPlanningConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(self.config.log_level)

    def plan_load(self, load_request: Dict[str, Any]) -> LoadPlanningResult:
        """Plan data loading operations.

        Args:
            load_request: Dictionary containing load requirements and sources

        Returns:
            LoadPlanningResult: Complete planning result with load plan
        """
        self.logger.info(
            f"Starting load planning for: {load_request.get('plan_name', 'unknown')}")

        try:
            # Validate input request
            self._validate_request(load_request)

            # Parse load sources
            sources = self._parse_sources(load_request)

            # Parse transformations
            transformations = self._parse_transformations(load_request)

            # Create load plan
            load_plan = self._create_load_plan(
                load_request, sources, transformations)

            # Estimate duration
            estimated_duration = self._estimate_load_duration(load_plan)

            # Estimate data volume
            data_volume = self._estimate_data_volume(load_plan)

            # Calculate resource requirements
            resource_requirements = self._calculate_resource_requirements(
                load_plan)

            result = LoadPlanningResult(
                success=True,
                load_plan=load_plan,
                estimated_duration=estimated_duration,
                data_volume_estimate=data_volume,
                resource_requirements=resource_requirements,
                metadata={
                    "planned_at": datetime.utcnow().isoformat(),
                    "plan_name": load_request.get("plan_name"),
                    "source_count": len(sources),
                    "planner": "ScriptsLoadPlanner"
                }
            )

            self.logger.info(f"Successfully planned load: {len(sources)} sources, {estimated_duration}s estimated")
            return result

        except Exception as e:
            self.logger.error(f"Load planning failed: {str(e)}")
            return LoadPlanningResult(
                success=False,
                errors=[str(e)],
                metadata={
                    "failed_at": datetime.utcnow().isoformat(),
                    "planner": "ScriptsLoadPlanner"
                }
            )

    def _validate_request(self, request: Dict[str, Any]) -> None:
        """Validate load planning request."""
        if not request:
            raise ValueError("Load planning request cannot be empty")

        if "plan_name" not in request:
            raise ValueError("Plan name is required in load planning request")

        if "sources" not in request:
            raise ValueError("Sources are required in load planning request")

    def _parse_sources(self, request: Dict[str, Any]) -> List[LoadSource]:
        """Parse load sources from request."""
        sources = []
        raw_sources = request.get("sources", [])

        for raw_source in raw_sources:
            if isinstance(raw_source, dict):
                # Map strings to enums
                source_mapping = {
                    "file_system": DataSourceType.FILE_SYSTEM,
                    "database": DataSourceType.DATABASE,
                    "api": DataSourceType.API,
                    "stream": DataSourceType.STREAM,
                    "cloud_storage": DataSourceType.CLOUD_STORAGE
                }

                format_mapping = {
                    "json": DataFormat.JSON,
                    "csv": DataFormat.CSV,
                    "parquet": DataFormat.PARQUET,
                    "xml": DataFormat.XML,
                    "binary": DataFormat.BINARY
                }

                source = LoadSource(
                    id=raw_source.get("id", f"source_{len(sources)}"),
                    name=raw_source.get("name", "unnamed"),
                    source_type=source_mapping.get(
                        raw_source.get("source_type", "file_system"),
                        DataSourceType.FILE_SYSTEM
                    ),
                    location=raw_source.get("location", ""),
                    format=format_mapping.get(
                        raw_source.get("format", "json"),
                        DataFormat.JSON
                    ),
                    credentials=raw_source.get("credentials", {}),
                    metadata=raw_source.get("metadata", {})
                )
                sources.append(source)

        # Validate source count
        if len(sources) > self.config.max_sources_per_plan:
            raise ValueError(
                f"Number of sources ({len(sources)}) exceeds maximum "
                f"({self.config.max_sources_per_plan})"
            )

        return sources

    def _parse_transformations(self, request: Dict[str, Any]) -> List[LoadTransformation]:
        """Parse load transformations from request."""
        transformations = []
        raw_transformations = request.get("transformations", [])

        for raw_transform in raw_transformations:
            if isinstance(raw_transform, dict):
                transformation = LoadTransformation(
                    id=raw_transform.get(
                        "id", f"transform_{len(transformations)}"),
                    name=raw_transform.get("name", "unnamed"),
                    transformation_type=raw_transform.get(
                        "transformation_type", "filter"),
                    parameters=raw_transform.get("parameters", {}),
                    conditions=raw_transform.get("conditions", [])
                )
                transformations.append(transformation)

        return transformations

    def _create_load_plan(
        self,
        request: Dict[str, Any],
        sources: List[LoadSource],
        transformations: List[LoadTransformation]
    ) -> LoadPlan:
        """Create load plan from request, sources, and transformations."""
        # Map strings to enums
        strategy_mapping = {
            "batch_load": LoadStrategy.BATCH_LOAD,
            "streaming_load": LoadStrategy.STREAMING_LOAD,
            "incremental_load": LoadStrategy.INCREMENTAL_LOAD,
            "full_refresh": LoadStrategy.FULL_REFRESH
        }

        load_strategy = strategy_mapping.get(
            request.get("load_strategy", "batch_load"),
            LoadStrategy.BATCH_LOAD
        )

        return LoadPlan(
            id=request.get(
                "plan_id", f"plan_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"),
            name=request.get("plan_name", "unnamed_plan"),
            load_strategy=load_strategy,
            sources=sources,
            transformations=transformations,
            DESTINATION=request.get("destination", ""),
            batch_size=request.get(
                "batch_size", self.config.default_batch_size),
            parallel_workers=request.get("parallel_workers", 1),
            retry_attempts=request.get("retry_attempts", 3),
            timeout_seconds=request.get("timeout_seconds", 300),
            metadata=request.get("metadata", {})
        )

    def _estimate_load_duration(self, plan: LoadPlan) -> int:
        """Estimate load duration in seconds."""
        base_duration = 10  # Base setup time

        # Add time based on number of sources
        source_duration = len(plan.sources) * 30

        # Add time based on transformations
        transform_duration = len(plan.transformations) * 15

        # Add time based on batch size (inverse relationship)
        batch_factor = max(1, 1000 / plan.batch_size)

        # Add time based on parallel workers (inverse relationship)
        parallel_factor = max(0.5, 1 / plan.parallel_workers)

        total_duration = (base_duration + source_duration +
                          transform_duration) * batch_factor * parallel_factor

        return int(total_duration)

    def _estimate_data_volume(self, plan: LoadPlan) -> int:
        """Estimate data volume in bytes."""
        total_volume = 0

        for source in plan.sources:
            # Simple estimation based on source type and format
            if source.source_type == DataSourceType.FILE_SYSTEM:
                if source.format == DataFormat.JSON:
                    total_volume += 1024 * 1024  # 1MB estimate
                elif source.format == DataFormat.CSV:
                    total_volume += 2 * 1024 * 1024  # 2MB estimate
                elif source.format == DataFormat.PARQUET:
                    total_volume += 512 * 1024  # 512KB estimate
            elif source.source_type == DataSourceType.DATABASE:
                total_volume += 5 * 1024 * 1024  # 5MB estimate
            elif source.source_type == DataSourceType.API:
                total_volume += 1024 * 1024  # 1MB estimate

        return total_volume

    def _calculate_resource_requirements(self, plan: LoadPlan) -> Dict[str, Any]:
        """Calculate resource requirements for the load plan."""
        requirements = {
            "cpu_cores": 1,
            "memory_mb": 512,
            "disk_mb": self._estimate_data_volume(plan) // (1024 * 1024),
            "network_bandwidth": 0
        }

        # Adjust based on parallel workers
        requirements["cpu_cores"] = plan.parallel_workers
        requirements["memory_mb"] = 512 * plan.parallel_workers

        # Adjust based on data volume
        if requirements["disk_mb"] > 1000:
            requirements["memory_mb"] = min(requirements["memory_mb"], 2048)

        # Network requirements for remote sources
        remote_sources = [
            s for s in plan.sources
            if s.source_type in [DataSourceType.API, DataSourceType.CLOUD_STORAGE, DataSourceType.DATABASE]
        ]
        if remote_sources:
            # 10 Mbps per remote so...
            requirements["network_bandwidth"] = len(remote_sources) * 10

        return requirements

# Factory function for easy instantiation


def create_scripts_load_planner(
    enable_parallel_loading: bool = True,
    enable_validation: bool = True,
    **kwargs: Dict[str, object]) -> ScriptsLoadPlanner:
    """Create a configured scripts load planner."""
    config = LoadPlanningConfig(
        enable_parallel_loading=enable_parallel_loading,
        enable_validation=enable_validation,
        **kwargs
    )
    return ScriptsLoadPlanner(config)

# Convenience function for direct usage


def plan_scripts_load(
    plan_name: str,
    sources: List[Dict[str, Any]],
    load_strategy: str = "batch_load",
    transformations: Optional[List[Dict[str, Any]]] = None,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Plan scripts data load from simple parameters.

    Args:
        plan_name: Name of the load plan
        sources: List of data source definitions
        load_strategy: Load strategy (batch_load, streaming_load, incremental_load, full_refresh)
        transformations: Optional list of transformation definitions
        config: Optional planner configuration overrides

    Returns:
        Dict: Planning result with load plan and resource requirements
    """
    # Build request
    request = {
        "plan_name": plan_name,
        "sources": sources,
        "load_strategy": load_strategy,
        "transformations": transformations or []
    }

    # Create planner and execute
    planner_config = LoadPlanningConfig(**config) if config else None
    planner = ScriptsLoadPlanner(planner_config)
    result = planner.plan_load(request)

    # Convert result to dict for JSON serialization
    return {
        "success": result.success,
        "load_plan": {
            "id": result.load_plan.id,
            "name": result.load_plan.name,
            "load_strategy": result.load_plan.load_strategy.value,
            "sources": [
                {
                    "id": s.id,
                    "name": s.name,
                    "source_type": s.source_type.value,
                    "location": s.location,
                    "format": s.format.value,
                    "credentials": s.credentials,
                    "metadata": s.metadata
                }
                for s in result.load_plan.sources
            ],
            "transformations": [
                {
                    "id": t.id,
                    "name": t.name,
                    "transformation_type": t.transformation_type,
                    "parameters": t.parameters,
                    "conditions": t.conditions
                }
                for t in result.load_plan.transformations
            ],
            "destination": result.load_plan.destination,
            "batch_size": result.load_plan.batch_size,
            "parallel_workers": result.load_plan.parallel_workers,
            "retry_attempts": result.load_plan.retry_attempts,
            "timeout_seconds": result.load_plan.timeout_seconds,
            "metadata": result.load_plan.metadata
        } if result.load_plan else None,
        "estimated_duration": result.estimated_duration,
        "data_volume_estimate": result.data_volume_estimate,
        "resource_requirements": result.resource_requirements,
        "warnings": result.warnings,
        "errors": result.errors,
        "metadata": result.metadata
    }