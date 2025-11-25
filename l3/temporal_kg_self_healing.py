"""L3 Temporal KG Self-Healing Controller

Orchestrates self-healing workflows for temporal knowledge graph maintenance.
Monitors KG inconsistencies and coordinates repair operations through L2 executors.

Layer: L3 (Orchestration / DAGs)
Responsibilities:
- Monitor temporal KG for inconsistencies and conflicts
- Orchestrate self-healing workflows using L2 executors
- Coordinate conflict detection, resolution, and validation
- Schedule periodic maintenance and repair cycles

Non-responsibilities:
- Planning or reasoning (L1)
- Direct tool calls or execution (L2)
- State mutation or persistence (L4)
- Safety evaluation or policy enforcement (L5)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Callable
from datetime import datetime, UTC, timedelta
from enum import Enum
import asyncio
import logging

from l4.temporal_schemas import (
    TemporalTriplet,
    TemporalEntity,
    ConflictDetection,
    ConflictType,
    TemporalKGState,
    TemporalEvent,
)
from infra.dag_engine.models import Node as DagNode, Edge as DagEdge, Graph as DagGraph
from infra.dag_engine.executor import DAGExecutor


logger = logging.getLogger(__name__)


class HealingTrigger(str, Enum):
    """Types of triggers for self-healing workflows."""
    SCHEDULED = "scheduled"           # Periodic maintenance
    CONFLICT_DETECTED = "conflict_detected"  # Active conflict found
    STALE_DATA = "stale_data"         # Data freshness issues
    MANUAL = "manual"                 # Manual initiation
    THRESHOLD_EXCEEDED = "threshold_exceeded"  # Quality thresholds exceeded


class HealingStatus(str, Enum):
    """Status of healing workflows."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class HealingWorkflow:
    """Orchestration specification for a self-healing workflow."""
    
    workflow_id: str
    trigger: HealingTrigger
    status: HealingStatus = HealingStatus.PENDING
    
    # Configuration
    conflict_types: List[ConflictType] = field(default_factory=list)
    entity_filters: List[str] = field(default_factory=list)
    temporal_scope: Optional[Dict[str, Any]] = None
    
    # Execution tracking
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Results
    conflicts_detected: List[ConflictDetection] = field(default_factory=list)
    conflicts_resolved: List[str] = field(default_factory=list)
    entities_processed: List[str] = field(default_factory=list)
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "workflow_id": self.workflow_id,
            "trigger": self.trigger.value,
            "status": self.status.value,
            "conflict_types": [ct.value for ct in self.conflict_types],
            "entity_filters": self.entity_filters,
            "temporal_scope": self.temporal_scope,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "conflicts_detected": [c.to_dict() for c in self.conflicts_detected],
            "conflicts_resolved": self.conflicts_resolved,
            "entities_processed": self.entities_processed,
            "metadata": self.metadata,
        }


@dataclass
class HealingOrchestrationConfig:
    """Configuration for healing orchestration."""
    
    # Scheduling
    scheduled_interval_hours: int = 24
    max_concurrent_workflows: int = 3
    workflow_timeout_minutes: int = 60
    
    # Thresholds
    conflict_threshold: int = 10  # Trigger healing if conflicts > threshold
    staleness_threshold_days: int = 30
    quality_threshold: float = 0.7
    
    # Execution limits
    max_entities_per_workflow: int = 1000
    max_conflicts_per_resolution: int = 50
    
    # Safety
    require_approval_for_dangerous_operations: bool = True
    backup_before_major_changes: bool = True


class TemporalKGSelfHealingController:
    """Orchestrates self-healing workflows for temporal knowledge graph.
    
    This controller monitors the temporal KG for issues and orchestrates
    appropriate healing workflows using L2 executors for actual repairs.
    """
    
    def __init__(
        self,
        l2_executors: Dict[str, Callable],
        l4_state_manager: Optional[Any] = None,
        config: Optional[HealingOrchestrationConfig] = None,
    ):
        """Initialize the self-healing controller.
        
        Args:
            l2_executors: Dictionary of L2 executor functions
            l4_state_manager: L4 state manager for reading/writing KG state
            config: Orchestration configuration
        """
        self.l2_executors = l2_executors
        self.l4_state_manager = l4_state_manager
        self.config = config or HealingOrchestrationConfig()
        
        # Workflow tracking
        self.active_workflows: Dict[str, HealingWorkflow] = {}
        self.workflow_history: List[HealingWorkflow] = []
        
        # Metrics
        self.metrics = {
            "workflows_initiated": 0,
            "conflicts_detected": 0,
            "conflicts_resolved": 0,
            "entities_processed": 0,
            "last_healing_cycle": None,
        }
    
    async def run_temporal_kg_self_heal_cycle(
        self,
        trigger: HealingTrigger = HealingTrigger.SCHEDULED,
        scope: Optional[Dict[str, Any]] = None,
    ) -> HealingWorkflow:
        """Run a complete self-healing cycle.
        
        Args:
            trigger: What triggered this healing cycle
            scope: Optional scope limitations
            
        Returns:
            HealingWorkflow with execution results
        """
        workflow_id = f"healing_{datetime.now(UTC).strftime('%Y%m%d%H%M%S%f')}"
        
        workflow = HealingWorkflow(
            workflow_id=workflow_id,
            trigger=trigger,
            temporal_scope=scope,
        )
        
        try:
            # Check if we can start a new workflow
            if len(self.active_workflows) >= self.config.max_concurrent_workflows:
                workflow.status = HealingStatus.FAILED
                workflow.metadata["error"] = "Maximum concurrent workflows exceeded"
                return workflow
            
            # Start the workflow
            workflow.status = HealingStatus.RUNNING
            workflow.started_at = datetime.now(UTC)
            self.active_workflows[workflow_id] = workflow
            
            # Execute healing DAG
            await self._execute_healing_dag(workflow)
            
            # Mark as completed
            workflow.status = HealingStatus.COMPLETED
            workflow.completed_at = datetime.now(UTC)
            
            # Update metrics
            self.metrics["workflows_initiated"] += 1
            self.metrics["conflicts_detected"] += len(workflow.conflicts_detected)
            self.metrics["conflicts_resolved"] += len(workflow.conflicts_resolved)
            self.metrics["entities_processed"] += len(workflow.entities_processed)
            self.metrics["last_healing_cycle"] = workflow.completed_at.isoformat()
            
        except Exception as e:
            logger.error(f"Self-healing workflow {workflow_id} failed: {str(e)}")
            workflow.status = HealingStatus.FAILED
            workflow.completed_at = datetime.now(UTC)
            workflow.metadata["error"] = str(e)
        
        finally:
            # Move from active to history
            if workflow_id in self.active_workflows:
                del self.active_workflows[workflow_id]
            self.workflow_history.append(workflow)
            
            # Limit history size
            if len(self.workflow_history) > 100:
                self.workflow_history = self.workflow_history[-100:]
        
        return workflow
    
    async def schedule_conflict_detection_and_repair(
        self,
        conflict_types: Optional[List[ConflictType]] = None,
        entity_filters: Optional[List[str]] = None,
    ) -> HealingWorkflow:
        """Schedule conflict detection and repair workflow.
        
        Args:
            conflict_types: Specific conflict types to address
            entity_filters: Entity filters to limit scope
            
        Returns:
            HealingWorkflow for the scheduled operation
        """
        scope = {
            "conflict_types": [ct.value for ct in conflict_types] if conflict_types else None,
            "entity_filters": entity_filters,
        }
        
        return await self.run_temporal_kg_self_heal_cycle(
            trigger=HealingTrigger.CONFLICT_DETECTED,
            scope=scope,
        )
    
    async def _execute_healing_dag(self, workflow: HealingWorkflow) -> None:
        """Execute the healing workflow as a DAG."""
        
        # Build healing DAG
        dag = self._build_healing_dag(workflow)
        
        # Execute DAG with timeout
        try:
            executor = DAGExecutor(dag, agent_registry=None)
            dag_context = {"workflow": workflow, "config": self.config}
            
            # Run with timeout
            await asyncio.wait_for(
                executor.run(ctx=dag_context),
                timeout=self.config.workflow_timeout_minutes * 60
            )
            
        except asyncio.TimeoutError:
            raise Exception(f"Healing workflow timed out after {self.config.workflow_timeout_minutes} minutes")
    
    def _build_healing_dag(self, workflow: HealingWorkflow) -> DagGraph:
        """Build a DAG for the healing workflow."""
        
        # Define DAG nodes
        nodes = {
            "conflict_detection": DagNode(
                id="conflict_detection",
                fn=self._node_conflict_detection,
                metadata={"step": "detect_conflicts"},
            ),
            "conflict_analysis": DagNode(
                id="conflict_analysis",
                fn=self._node_conflict_analysis,
                metadata={"step": "analyze_conflicts"},
            ),
            "entity_resolution": DagNode(
                id="entity_resolution",
                fn=self._node_entity_resolution,
                metadata={"step": "resolve_entities"},
            ),
            "triplet_repair": DagNode(
                id="triplet_repair",
                fn=self._node_triplet_repair,
                metadata={"step": "repair_triplets"},
            ),
            "temporal_invalidation": DagNode(
                id="temporal_invalidation",
                fn=self._node_temporal_invalidation,
                metadata={"step": "invalidate_temporal"},
            ),
            "validation": DagNode(
                id="validation",
                fn=self._node_validation,
                metadata={"step": "validate_repairs"},
            ),
        }
        
        # Define DAG edges (dependencies)
        edges = [
            DagEdge(source="conflict_detection", target="conflict_analysis"),
            DagEdge(source="conflict_analysis", target="entity_resolution"),
            DagEdge(source="conflict_analysis", target="triplet_repair"),
            DagEdge(source="entity_resolution", target="temporal_invalidation"),
            DagEdge(source="triplet_repair", target="temporal_invalidation"),
            DagEdge(source="temporal_invalidation", target="validation"),
        ]
        
        return DagGraph(nodes=nodes, edges=edges)
    
    async def _node_conflict_detection(self, dag_ctx: Dict[str, Any]) -> Dict[str, Any]:
        """Detect conflicts in the temporal KG."""
        workflow = dag_ctx["workflow"]
        
        try:
            # Call L2 executor for conflict detection
            if "conflict_detector" not in self.l2_executors:
                raise Exception("Conflict detector executor not available")
            
            detection_result = await self.l2_executors["conflict_detector"](
                temporal_scope=workflow.temporal_scope,
                conflict_types=workflow.conflict_types,
                entity_filters=workflow.entity_filters,
            )
            
            # Update workflow with detected conflicts
            if detection_result.get("success", False):
                conflicts = detection_result.get("conflicts", [])
                workflow.conflicts_detected = [
                    ConflictDetection(**c) for c in conflicts
                ]
            
            return {
                "conflicts_detected": len(workflow.conflicts_detected),
                "detection_success": detection_result.get("success", False),
            }
            
        except Exception as e:
            logger.error(f"Conflict detection failed: {str(e)}")
            return {"conflicts_detected": 0, "detection_success": False, "error": str(e)}
    
    async def _node_conflict_analysis(self, dag_ctx: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze detected conflicts and prioritize repairs."""
        workflow = dag_ctx["workflow"]
        
        try:
            # Analyze conflicts by type and severity
            conflict_summary = {}
            for conflict in workflow.conflicts_detected:
                conflict_type = conflict.conflict_type.value
                if conflict_type not in conflict_summary:
                    conflict_summary[conflict_type] = {
                        "count": 0,
                        "severity_distribution": {},
                        "affected_triplets": set(),
                    }
                
                conflict_summary[conflict_type]["count"] += 1
                severity = conflict.severity
                if severity not in conflict_summary[conflict_type]["severity_distribution"]:
                    conflict_summary[conflict_type]["severity_distribution"][severity] = 0
                conflict_summary[conflict_type]["severity_distribution"][severity] += 1
                conflict_summary[conflict_type]["affected_triplets"].update(conflict.affected_triplets)
            
            # Prioritize by severity and count
            prioritized_conflicts = sorted(
                workflow.conflicts_detected,
                key=lambda c: (c.severity, len(c.affected_triplets)),
                reverse=True
            )
            
            return {
                "conflict_summary": conflict_summary,
                "prioritized_count": len(prioritized_conflicts),
                "analysis_success": True,
            }
            
        except Exception as e:
            logger.error(f"Conflict analysis failed: {str(e)}")
            return {"analysis_success": False, "error": str(e)}
    
    async def _node_entity_resolution(self, dag_ctx: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve entity identity conflicts."""
        workflow = dag_ctx["workflow"]
        
        try:
            # Filter for entity identity conflicts
            entity_conflicts = [
                c for c in workflow.conflicts_detected
                if c.conflict_type == ConflictType.ENTITY_IDENTITY_CONFLICT
            ]
            
            if not entity_conflicts:
                return {"entities_resolved": 0, "resolution_success": True}
            
            # Call L2 executor for entity resolution
            if "entity_resolver" not in self.l2_executors:
                raise Exception("Entity resolver executor not available")
            
            resolution_result = await self.l2_executors["entity_resolver"](
                conflicts=entity_conflicts,
                max_entities=self.config.max_entities_per_workflow,
            )
            
            if resolution_result.get("success", False):
                resolved_entities = resolution_result.get("resolved_entities", [])
                workflow.entities_processed.extend(resolved_entities)
            
            return {
                "entities_resolved": len(resolved_entities),
                "resolution_success": resolution_result.get("success", False),
            }
            
        except Exception as e:
            logger.error(f"Entity resolution failed: {str(e)}")
            return {"entities_resolved": 0, "resolution_success": False, "error": str(e)}
    
    async def _node_triplet_repair(self, dag_ctx: Dict[str, Any]) -> Dict[str, Any]:
        """Repair conflicting triplets."""
        workflow = dag_ctx["workflow"]
        
        try:
            # Filter for triplet conflicts (excluding entity identity)
            triplet_conflicts = [
                c for c in workflow.conflicts_detected
                if c.conflict_type != ConflictType.ENTITY_IDENTITY_CONFLICT
            ]
            
            if not triplet_conflicts:
                return {"triplets_repaired": 0, "repair_success": True}
            
            # Call L2 executor for triplet repair
            if "triplet_repairer" not in self.l2_executors:
                raise Exception("Triplet repairer executor not available")
            
            repair_result = await self.l2_executors["triplet_repairer"](
                conflicts=triplet_conflicts,
                max_conflicts=self.config.max_conflicts_per_resolution,
            )
            
            if repair_result.get("success", False):
                repaired_triplets = repair_result.get("repaired_triplet_ids", [])
                workflow.conflicts_resolved.extend(repaired_triplets)
            
            return {
                "triplets_repaired": len(repaired_triplets),
                "repair_success": repair_result.get("success", False),
            }
            
        except Exception as e:
            logger.error(f"Triplet repair failed: {str(e)}")
            return {"triplets_repaired": 0, "repair_success": False, "error": str(e)}
    
    async def _node_temporal_invalidation(self, dag_ctx: Dict[str, Any]) -> Dict[str, Any]:
        """Apply temporal invalidation logic."""
        workflow = dag_ctx["workflow"]
        
        try:
            # Call L2 executor for temporal invalidation
            if "temporal_invalidator" not in self.l2_executors:
                raise Exception("Temporal invalidator executor not available")
            
            invalidation_result = await self.l2_executors["temporal_invalidator"](
                resolved_entities=workflow.entities_processed,
                resolved_triplets=workflow.conflicts_resolved,
                temporal_scope=workflow.temporal_scope,
            )
            
            return {
                "invalidations_applied": invalidation_result.get("invalidation_count", 0),
                "invalidation_success": invalidation_result.get("success", False),
            }
            
        except Exception as e:
            logger.error(f"Temporal invalidation failed: {str(e)}")
            return {"invalidations_applied": 0, "invalidation_success": False, "error": str(e)}
    
    async def _node_validation(self, dag_ctx: Dict[str, Any]) -> Dict[str, Any]:
        """Validate repair results."""
        workflow = dag_ctx["workflow"]
        
        try:
            # Call L2 executor for validation
            if "repair_validator" not in self.l2_executors:
                raise Exception("Repair validator executor not available")
            
            validation_result = await self.l2_executors["repair_validator"](
                workflow_id=workflow.workflow_id,
                resolved_entities=workflow.entities_processed,
                resolved_triplets=workflow.conflicts_resolved,
            )
            
            return {
                "validation_success": validation_result.get("success", False),
                "validation_score": validation_result.get("score", 0.0),
                "remaining_issues": validation_result.get("remaining_issues", 0),
            }
            
        except Exception as e:
            logger.error(f"Validation failed: {str(e)}")
            return {"validation_success": False, "error": str(e)}
    
    def get_workflow_status(self, workflow_id: str) -> Optional[HealingWorkflow]:
        """Get the status of a specific workflow."""
        return self.active_workflows.get(workflow_id)
    
    def list_active_workflows(self) -> List[HealingWorkflow]:
        """List all currently active workflows."""
        return list(self.active_workflows.values())
    
    def get_healing_metrics(self) -> Dict[str, Any]:
        """Get healing controller metrics."""
        return {
            **self.metrics,
            "active_workflows": len(self.active_workflows),
            "total_workflows": len(self.workflow_history),
            "success_rate": (
                len([w for w in self.workflow_history if w.status == HealingStatus.COMPLETED]) /
                max(1, len(self.workflow_history))
            ),
        }


# =============================================================================
# Convenience Functions
# =============================================================================

async def run_scheduled_healing_cycle(
    l2_executors: Dict[str, Callable],
    l4_state_manager: Optional[Any] = None,
) -> HealingWorkflow:
    """Run a scheduled healing cycle."""
    controller = TemporalKGSelfHealingController(
        l2_executors=l2_executors,
        l4_state_manager=l4_state_manager,
    )
    
    return await controller.run_temporal_kg_self_heal_cycle(
        trigger=HealingTrigger.SCHEDULED
    )


async def repair_conflicts(
    conflict_types: List[ConflictType],
    l2_executors: Dict[str, Callable],
    entity_filters: Optional[List[str]] = None,
) -> HealingWorkflow:
    """Repair specific types of conflicts."""
    controller = TemporalKGSelfHealingController(
        l2_executors=l2_executors,
    )
    
    return await controller.schedule_conflict_detection_and_repair(
        conflict_types=conflict_types,
        entity_filters=entity_filters,
    )


__all__ = [
    "HealingTrigger",
    "HealingStatus",
    "HealingWorkflow",
    "HealingOrchestrationConfig",
    "TemporalKGSelfHealingController",
    "run_scheduled_healing_cycle",
    "repair_conflicts",
]
