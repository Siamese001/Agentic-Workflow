"""L3 Unified KG Ingestion DAG

Orchestrates end-to-end temporal knowledge graph ingestion with configurable
failure policies, checkpointing, and observability.

Layer: L3 (Orchestration / DAGs)
Responsibilities:
- Define and execute unified ingestion DAG with 9 stages
- Coordinate L2 executors for each ingestion stage
- Handle failure policies and retry logic
- Provide checkpointing and resume capability
- Ensure observability and traceability

Non-responsibilities:
- Planning or ingestion strategy (L1)
- Direct tool calls or data processing (L2)
- State persistence or KG writes (L4)
- Safety evaluation or policy enforcement (L5)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Callable
from datetime import datetime, UTC
from enum import Enum
import asyncio
import logging
import uuid

from state.temporal_schemas import (
    IngestionBatch,
    TemporalEntity,
    TemporalTriplet,
    TemporalEvent,
)
from infrastructure.dag_engine.models import Node as DagNode, Edge as DagEdge, Graph as DagGraph
from infrastructure.dag_engine.executor import DAGExecutor
from runtime.observability import emit_node_event

# Import Neo4j mirroring functions
from l2.kg_writer import (
    insert_entity,
    insert_triplet,
    insert_event,
    batch_process_invalidation,
    ingest_transcript,
)


logger = logging.getLogger(__name__)


class IngestionStage(str, Enum):
    """Stages in the unified ingestion DAG."""
    CHUNKING = "chunking"
    STATEMENT_EXTRACTION = "statement_extraction"
    TEMPORAL_TYPE_CLASSIFICATION = "temporal_type_classification"
    TEMPORAL_VALIDITY_EXTRACTION = "temporal_validity_extraction"
    TRIPLET_EXTRACTION = "triplet_extraction"
    ENTITY_EXTRACTION_RESOLUTION = "entity_extraction_resolution"
    EVENT_EMBEDDING_GENERATION = "event_embedding_generation"
    INVALIDATION_CHECKS = "invalidation_checks"
    KG_WRITES = "kg_writes"


class FailurePolicy(str, Enum):
    """Policy for handling stage failures."""
    FAIL_FAST = "fail_fast"           # Stop immediately on failure
    CONTINUE_PARTIAL = "continue_partial"  # Continue with partial data
    RETRY_STAGE = "retry_stage"       # Retry failed stage with backoff
    SKIP_NON_CRITICAL = "skip_non_critical"  # Skip non-critical stages


class IngestionStatus(str, Enum):
    """Status of ingestion operations."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"
    CANCELLED = "cancelled"


@dataclass
class StageResult:
    """Result of executing a single ingestion stage."""
    
    stage: IngestionStage
    success: bool
    data: Any = None
    error: Optional[str] = None
    execution_time_ms: int = 0
    retry_count: int = 0
    checkpoint_saved: bool = False
    
    # Metrics
    input_count: int = 0
    output_count: int = 0
    processed_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "stage": self.stage.value,
            "success": self.success,
            "error": self.error,
            "execution_time_ms": self.execution_time_ms,
            "retry_count": self.retry_count,
            "checkpoint_saved": self.checkpoint_saved,
            "input_count": self.input_count,
            "output_count": self.output_count,
            "processed_count": self.processed_count,
        }


@dataclass
class IngestionDAGResult:
    """Complete result of ingestion DAG execution."""
    
    batch_id: str
    status: IngestionStatus
    stage_results: List[StageResult] = field(default_factory=list)
    
    # Timing
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    completed_at: Optional[datetime] = None
    
    # Aggregated metrics
    total_execution_time_ms: int = 0
    total_documents_processed: int = 0
    total_triplets_created: int = 0
    total_entities_created: int = 0
    
    # Checkpointing
    checkpoints_saved: List[IngestionStage] = field(default_factory=list)
    resume_from_stage: Optional[IngestionStage] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "batch_id": self.batch_id,
            "status": self.status.value,
            "stage_results": [r.to_dict() for r in self.stage_results],
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "total_execution_time_ms": self.total_execution_time_ms,
            "total_documents_processed": self.total_documents_processed,
            "total_triplets_created": self.total_triplets_created,
            "total_entities_created": self.total_entities_created,
            "checkpoints_saved": [s.value for s in self.checkpoints_saved],
            "resume_from_stage": self.resume_from_stage.value if self.resume_from_stage else None,
        }


@dataclass
class IngestionDAGConfig:
    """Configuration for ingestion DAG execution."""
    
    # Failure policy
    failure_policy: FailurePolicy = FailurePolicy.CONTINUE_PARTIAL
    max_retries_per_stage: int = 3
    retry_backoff_seconds: int = 5
    
    # Checkpointing
    enable_checkpointing: bool = True
    checkpoint_stages: Set[IngestionStage] = field(default_factory=lambda: {
        IngestionStage.CHUNKING,
        IngestionStage.TRIPLET_EXTRACTION,
        IngestionStage.ENTITY_EXTRACTION_RESOLUTION,
    })
    
    # Performance
    max_concurrent_stages: int = 3
    stage_timeout_minutes: int = 30
    batch_size_limits: Dict[str, int] = field(default_factory=lambda: {
        "max_documents": 1000,
        "max_triplets": 5000,
        "max_entities": 2000,
    })
    
    # Observability
    enable_detailed_logging: bool = True
    emit_stage_events: bool = True
    
    # Quality gates
    min_quality_threshold: float = 0.7
    require_validation: bool = True


class UnifiedKGIngestionDAG:
    """Unified DAG for temporal knowledge graph ingestion.
    
    This orchestrates the complete ingestion pipeline from raw documents
    to persisted temporal KG data with configurable failure handling
    and checkpointing support.
    """
    
    def __init__(
        self,
        l2_executors: Dict[str, Callable],
        l4_state_manager: Optional[Any] = None,
        config: Optional[IngestionDAGConfig] = None,
    ):
        """Initialize the ingestion DAG.
        
        Args:
            l2_executors: Dictionary of L2 executor functions
            l4_state_manager: L4 state manager for checkpointing
            config: DAG configuration
        """
        self.l2_executors = l2_executors
        self.l4_state_manager = l4_state_manager
        self.config = config or IngestionDAGConfig()
        
        # Stage definitions
        self.stages = self._define_stages()
        self.stage_dependencies = self._define_stage_dependencies()
        
        # Execution tracking
        self.active_executions: Dict[str, IngestionDAGResult] = {}
        self.execution_history: List[IngestionDAGResult] = []
    
    def _define_stages(self) -> Dict[IngestionStage, Dict[str, Any]]:
        """Define all ingestion stages with their configurations."""
        return {
            IngestionStage.CHUNKING: {
                "executor": "chunker",
                "critical": True,
                "timeout_minutes": 15,
                "description": "Split documents into processable chunks",
            },
            IngestionStage.STATEMENT_EXTRACTION: {
                "executor": "statement_extractor",
                "critical": True,
                "timeout_minutes": 20,
                "description": "Extract factual statements from chunks",
            },
            IngestionStage.TEMPORAL_TYPE_CLASSIFICATION: {
                "executor": "temporal_classifier",
                "critical": False,
                "timeout_minutes": 10,
                "description": "Classify temporal types of statements",
            },
            IngestionStage.TEMPORAL_VALIDITY_EXTRACTION: {
                "executor": "temporal_validity_extractor",
                "critical": True,
                "timeout_minutes": 15,
                "description": "Extract temporal validity ranges",
            },
            IngestionStage.TRIPLET_EXTRACTION: {
                "executor": "triplet_extractor",
                "critical": True,
                "timeout_minutes": 25,
                "description": "Extract subject-predicate-object triplets",
            },
            IngestionStage.ENTITY_EXTRACTION_RESOLUTION: {
                "executor": "entity_resolver",
                "critical": True,
                "timeout_minutes": 20,
                "description": "Extract and resolve entities",
            },
            IngestionStage.EVENT_EMBEDDING_GENERATION: {
                "executor": "embedding_generator",
                "critical": False,
                "timeout_minutes": 30,
                "description": "Generate embeddings for events",
            },
            IngestionStage.INVALIDATION_CHECKS: {
                "executor": "invalidation_checker",
                "critical": True,
                "timeout_minutes": 10,
                "description": "Perform invalidation checks",
            },
            IngestionStage.KG_WRITES: {
                "executor": "kg_writer",
                "critical": True,
                "timeout_minutes": 20,
                "description": "Write data to knowledge graph (SQLite + Neo4j mirror)",
            },
        }
    
    def _define_stage_dependencies(self) -> Dict[IngestionStage, List[IngestionStage]]:
        """Define dependencies between stages."""
        return {
            IngestionStage.CHUNKING: [],
            IngestionStage.STATEMENT_EXTRACTION: [IngestionStage.CHUNKING],
            IngestionStage.TEMPORAL_TYPE_CLASSIFICATION: [IngestionStage.STATEMENT_EXTRACTION],
            IngestionStage.TEMPORAL_VALIDITY_EXTRACTION: [IngestionStage.STATEMENT_EXTRACTION],
            IngestionStage.TRIPLET_EXTRACTION: [
                IngestionStage.STATEMENT_EXTRACTION,
                IngestionStage.TEMPORAL_VALIDITY_EXTRACTION,
            ],
            IngestionStage.ENTITY_EXTRACTION_RESOLUTION: [IngestionStage.TRIPLET_EXTRACTION],
            IngestionStage.EVENT_EMBEDDING_GENERATION: [
                IngestionStage.TRIPLET_EXTRACTION,
                IngestionStage.ENTITY_EXTRACTION_RESOLUTION,
            ],
            IngestionStage.INVALIDATION_CHECKS: [
                IngestionStage.TRIPLET_EXTRACTION,
                IngestionStage.ENTITY_EXTRACTION_RESOLUTION,
            ],
            IngestionStage.KG_WRITES: [
                IngestionStage.TRIPLET_EXTRACTION,
                IngestionStage.ENTITY_EXTRACTION_RESOLUTION,
                IngestionStage.INVALIDATION_CHECKS,
            ],
        }
    
    async def execute_ingestion_dag(
        self,
        batch: IngestionBatch,
        source_data: Dict[str, Any],
        resume_from_checkpoint: bool = False,
    ) -> IngestionDAGResult:
        """Execute the complete ingestion DAG.
        
        Args:
            batch: Ingestion batch metadata
            source_data: Source documents and metadata
            resume_from_checkpoint: Whether to resume from last checkpoint
            
        Returns:
            IngestionDAGResult with execution results
        """
        execution_id = f"ingestion_{batch.batch_id}_{datetime.now(UTC).strftime('%Y%m%d%H%M%S%f')}"
        
        result = IngestionDAGResult(
            batch_id=batch.batch_id,
            status=IngestionStatus.RUNNING,
        )
        
        try:
            # Track execution
            self.active_executions[execution_id] = result
            
            # Load checkpoint if resuming
            if resume_from_checkpoint and self.config.enable_checkpointing:
                await self._load_checkpoint(result)
            
            # Build and execute DAG
            dag = self._build_ingestion_dag(result)
            await self._execute_dag_with_policy(dag, result, source_data)
            
            # Determine final status
            result.status = self._determine_final_status(result)
            result.completed_at = datetime.now(UTC)
            
            # Save final checkpoint
            if self.config.enable_checkpointing:
                await self._save_checkpoint(result, IngestionStage.KG_WRITES)
            
        except Exception as e:
            logger.error(f"Ingestion DAG execution failed: {str(e)}")
            result.status = IngestionStatus.FAILED
            result.completed_at = datetime.now(UTC)
        
        finally:
            # Move from active to history
            if execution_id in self.active_executions:
                del self.active_executions[execution_id]
            self.execution_history.append(result)
            
            # Limit history size
            if len(self.execution_history) > 100:
                self.execution_history = self.execution_history[-100:]
        
        return result
    
    def _build_ingestion_dag(self, result: IngestionDAGResult) -> DagGraph:
        """Build the ingestion DAG based on current state."""
        
        # Determine which stages to include
        stages_to_execute = self._get_stages_to_execute(result)
        
        # Create DAG nodes
        nodes = {}
        for stage in stages_to_execute:
            nodes[stage.value] = DagNode(
                id=stage.value,
                fn=self._create_stage_executor(stage),
                metadata={
                    "stage": stage.value,
                    "critical": self.stages[stage]["critical"],
                    "timeout_minutes": self.stages[stage]["timeout_minutes"],
                },
            )
        
        # Create DAG edges based on dependencies
        edges = []
        for stage in stages_to_execute:
            dependencies = self.stage_dependencies.get(stage, [])
            for dep in dependencies:
                if dep in stages_to_execute:
                    edges.append(DagEdge(source=dep.value, target=stage.value))
        
        return DagGraph(nodes=nodes, edges=edges)
    
    def _get_stages_to_execute(self, result: IngestionDAGResult) -> List[IngestionStage]:
        """Determine which stages need to be executed."""
        all_stages = list(IngestionStage)
        
        # If resuming from checkpoint, skip completed stages
        if result.resume_from_stage:
            resume_index = all_stages.index(result.resume_from_stage)
            return all_stages[resume_index:]
        
        # Otherwise, execute all stages
        return all_stages
    
    def _create_stage_executor(self, stage: IngestionStage) -> Callable:
        """Create an executor function for a specific stage."""
        async def stage_executor(dag_ctx: Dict[str, Any]) -> Dict[str, Any]:
            return await self._execute_stage(stage, dag_ctx)
        
        return stage_executor
    
    async def _execute_dag_with_policy(
        self,
        dag: DagGraph,
        result: IngestionDAGResult,
        source_data: Dict[str, Any],
    ) -> None:
        """Execute DAG with failure policy handling."""
        
        try:
            # Execute DAG with timeout
            executor = DAGExecutor(dag, agent_registry=None)
            dag_context = {
                "result": result,
                "source_data": source_data,
                "config": self.config,
                "l2_executors": self.l2_executors,
            }
            
            await asyncio.wait_for(
                executor.run(ctx=dag_context),
                timeout=self.config.stage_timeout_minutes * len(dag.nodes) * 60
            )
            
        except asyncio.TimeoutError:
            raise Exception(f"Ingestion DAG timed out")
    
    async def _execute_stage(
        self,
        stage: IngestionStage,
        dag_ctx: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute a single ingestion stage."""
        result = dag_ctx["result"]
        source_data = dag_ctx["source_data"]
        
        start_time = datetime.now(UTC)
        stage_config = self.stages[stage]
        
        try:
            # Emit stage start event
            if self.config.emit_stage_events:
                emit_node_event(
                    node=f"ingestion.{stage.value}",
                    status="start",
                    details={"batch_id": result.batch_id}
                )
            
            # Get executor function
            executor_name = stage_config["executor"]
            if executor_name not in self.l2_executors:
                raise Exception(f"Executor {executor_name} not available")
            
            executor = self.l2_executors[executor_name]
            
            # Prepare stage input
            stage_input = await self._prepare_stage_input(stage, result, source_data)
            
            # Execute stage with retry logic
            stage_output = await self._execute_with_retry(
                executor, stage_input, stage, result
            )
            
            # Mirror to Neo4j for specific stages
            if stage == IngestionStage.ENTITY_EXTRACTION_RESOLUTION:
                await self._mirror_entities_to_neo4j(stage_output)
            elif stage == IngestionStage.TRIPLET_EXTRACTION:
                await self._mirror_triplets_to_neo4j(stage_output)
            elif stage == IngestionStage.INVALIDATION_CHECKS:
                await self._mirror_invalidations_to_neo4j(stage_output)
            elif stage == IngestionStage.KG_WRITES:
                await self._mirror_complete_transcript_to_neo4j(stage_output)
            
            # Calculate execution time
            execution_time = int((datetime.now(UTC) - start_time).total_seconds() * 1000)
            
            # Create stage result
            stage_result = StageResult(
                stage=stage,
                success=True,
                data=stage_output,
                execution_time_ms=execution_time,
                input_count=len(stage_input) if isinstance(stage_input, list) else 1,
                output_count=len(stage_output) if isinstance(stage_output, list) else 1,
                processed_count=stage_output.get("processed_count", 0) if isinstance(stage_output, dict) else 1,
            )
            
            # Save checkpoint if configured
            if self.config.enable_checkpointing and stage in self.config.checkpoint_stages:
                await self._save_checkpoint(result, stage)
                stage_result.checkpoint_saved = True
            
            # Add to results
            result.stage_results.append(stage_result)
            
            # Update aggregated metrics
            self._update_aggregated_metrics(result, stage_result)
            
            # Emit stage completion event
            if self.config.emit_stage_events:
                emit_node_event(
                    node=f"ingestion.{stage.value}",
                    status="success",
                    details={
                        "batch_id": result.batch_id,
                        "execution_time_ms": execution_time,
                        "output_count": stage_result.output_count,
                    }
                )
            
            return {
                "success": True,
                "stage_output": stage_output,
                "execution_time_ms": execution_time,
            }
            
        except Exception as e:
            execution_time = int((datetime.now(UTC) - start_time).total_seconds() * 1000)
            
            logger.error(f"Stage {stage.value} failed: {str(e)}")
            
            # Create failure result
            stage_result = StageResult(
                stage=stage,
                success=False,
                error=str(e),
                execution_time_ms=execution_time,
            )
            
            result.stage_results.append(stage_result)
            
            # Handle failure based on policy
            if self.config.failure_policy == FailurePolicy.FAIL_FAST:
                if stage_config["critical"]:
                    raise Exception(f"Critical stage {stage.value} failed")
            
            # Emit failure event
            if self.config.emit_stage_events:
                emit_node_event(
                    node=f"ingestion.{stage.value}",
                    status="error",
                    details={
                        "batch_id": result.batch_id,
                        "error": str(e),
                        "execution_time_ms": execution_time,
                    }
                )
            
            return {
                "success": False,
                "error": str(e),
                "execution_time_ms": execution_time,
            }
    
    async def _execute_with_retry(
        self,
        executor: Callable,
        stage_input: Any,
        stage: IngestionStage,
        result: IngestionDAGResult,
    ) -> Any:
        """Execute stage with retry logic."""
        last_error = None
        
        for attempt in range(self.config.max_retries_per_stage + 1):
            try:
                # Execute the stage
                stage_output = await executor(stage_input)
                
                # Validate output if required
                if self.config.require_validation:
                    await self._validate_stage_output(stage, stage_output)
                
                return stage_output
                
            except Exception as e:
                last_error = e
                
                if attempt < self.config.max_retries_per_stage:
                    logger.warning(f"Stage {stage.value} attempt {attempt + 1} failed, retrying: {str(e)}")
                    
                    # Update retry count in result
                    for sr in result.stage_results:
                        if sr.stage == stage:
                            sr.retry_count = attempt + 1
                            break
                    
                    # Backoff before retry
                    await asyncio.sleep(self.config.retry_backoff_seconds * (attempt + 1))
                else:
                    logger.error(f"Stage {stage.value} failed after {attempt + 1} attempts: {str(e)}")
                    raise
        
        raise last_error
    
    async def _prepare_stage_input(
        self,
        stage: IngestionStage,
        result: IngestionDAGResult,
        source_data: Dict[str, Any],
    ) -> Any:
        """Prepare input data for a specific stage."""
        
        # Get outputs from dependency stages
        dependencies = self.stage_dependencies.get(stage, [])
        
        if not dependencies:
            # First stage, use source data
            return source_data
        
        # Aggregate outputs from dependencies
        dependency_outputs = {}
        for dep in dependencies:
            dep_result = next((r for r in result.stage_results if r.stage == dep), None)
            if dep_result and dep_result.success:
                dependency_outputs[dep.value] = dep_result.data
        
        return dependency_outputs
    
    async def _validate_stage_output(
        self,
        stage: IngestionStage,
        output: Any,
    ) -> None:
        """Validate stage output quality."""
        
        # Basic validation - check for required structure
        if output is None:
            raise Exception(f"Stage {stage.value} returned None output")
        
        # Stage-specific validation would go here
        # For now, just ensure output is not empty for critical stages
        if self.stages[stage]["critical"]:
            if isinstance(output, list) and len(output) == 0:
                raise Exception(f"Critical stage {stage.value} returned empty results")
            elif isinstance(output, dict) and output.get("count", 0) == 0:
                raise Exception(f"Critical stage {stage.value} returned no processed items")
    
    async def _save_checkpoint(
        self,
        result: IngestionDAGResult,
        stage: IngestionStage,
    ) -> None:
        """Save checkpoint for a stage."""
        if not self.l4_state_manager:
            return
        
        try:
            checkpoint_data = {
                "batch_id": result.batch_id,
                "stage": stage.value,
                "stage_results": [r.to_dict() for r in result.stage_results],
                "timestamp": datetime.now(UTC).isoformat(),
            }
            
            # Save to L4 (implementation depends on state manager)
            await self.l4_state_manager.save_checkpoint(
                f"ingestion_checkpoint_{result.batch_id}_{stage.value}",
                checkpoint_data
            )
            
            result.checkpoints_saved.append(stage)
            
        except Exception as e:
            logger.warning(f"Failed to save checkpoint for stage {stage.value}: {str(e)}")
    
    async def _load_checkpoint(self, result: IngestionDAGResult) -> None:
        """Load checkpoint to resume execution."""
        if not self.l4_state_manager:
            return
        
        try:
            # Find the latest checkpoint
            checkpoint_id = f"ingestion_checkpoint_{result.batch_id}"
            checkpoint_data = await self.l4_state_manager.load_checkpoint(checkpoint_id)
            
            if checkpoint_data:
                # Restore stage results from checkpoint
                result.stage_results = [
                    StageResult(**r) for r in checkpoint_data.get("stage_results", [])
                ]
                
                # Set resume stage
                last_stage = checkpoint_data.get("stage")
                if last_stage:
                    result.resume_from_stage = IngestionStage(last_stage)
                
                logger.info(f"Resuming ingestion from stage: {last_stage}")
            
        except Exception as e:
            logger.warning(f"Failed to load checkpoint: {str(e)}")
    
    def _determine_final_status(self, result: IngestionDAGResult) -> IngestionStatus:
        """Determine final execution status based on stage results."""
        
        if not result.stage_results:
            return IngestionStatus.FAILED
        
        failed_stages = [r for r in result.stage_results if not r.success]
        critical_failures = [
            r for r in failed_stages
            if self.stages[r.stage]["critical"]
        ]
        
        if not failed_stages:
            return IngestionStatus.COMPLETED
        elif critical_failures:
            return IngestionStatus.FAILED
        else:
            return IngestionStatus.PARTIAL
    
    def _update_aggregated_metrics(
        self,
        result: IngestionDAGResult,
        stage_result: StageResult,
    ) -> None:
        """Update aggregated metrics from stage result."""
        
        # Update execution time
        result.total_execution_time_ms += stage_result.execution_time_ms
        
        # Update counts based on stage type
        if stage_result.stage == IngestionStage.CHUNKING:
            result.total_documents_processed += stage_result.processed_count
        elif stage_result.stage == IngestionStage.TRIPLET_EXTRACTION:
            result.total_triplets_created += stage_result.processed_count
        elif stage_result.stage == IngestionStage.ENTITY_EXTRACTION_RESOLUTION:
            result.total_entities_created += stage_result.processed_count
    
    def get_execution_status(self, batch_id: str) -> Optional[IngestionDAGResult]:
        """Get status of an ingestion execution."""
        for execution in self.active_executions.values():
            if execution.batch_id == batch_id:
                return execution
        return None
    
    def list_active_executions(self) -> List[IngestionDAGResult]:
        """List all currently active executions."""
        return list(self.active_executions.values())


# =============================================================================
# Convenience Functions
# =============================================================================

async def ingest_documents(
    documents: List[Dict[str, Any]],
    l2_executors: Dict[str, Callable],
    l4_state_manager: Optional[Any] = None,
    config: Optional[IngestionDAGConfig] = None,
) -> IngestionDAGResult:
    """Ingest documents using the unified DAG."""
    from state.temporal_schemas import IngestionBatch
    
    # Create ingestion batch
    batch = IngestionBatch(
        batch_id=f"batch_{uuid.uuid4().hex[:8]}",
        source_id="document_ingestion",
        document_count=len(documents),
        triplet_count=0,  # Will be updated during processing
    )
    
    # Create DAG and execute
    dag = UnifiedKGIngestionDAG(
        l2_executors=l2_executors,
        l4_state_manager=l4_state_manager,
        config=config,
    )
    
    source_data = {"documents": documents}
    return await dag.execute_ingestion_dag(batch, source_data)


# =============================================================================
# Neo4j Mirroring Helper Methods
# =============================================================================

async def _mirror_entities_to_neo4j(stage_output: Any) -> None:
    """Mirror resolved entities to Neo4j."""
    try:
        if isinstance(stage_output, dict) and "entities" in stage_output:
            entities = stage_output["entities"]
            for entity in entities:
                if isinstance(entity, TemporalEntity):
                    await insert_entity(entity)
    except Exception:
        # Neo4j mirroring is optional - don't fail ingestion
        pass


async def _mirror_triplets_to_neo4j(stage_output: Any) -> None:
    """Mirror extracted triplets to Neo4j."""
    try:
        if isinstance(stage_output, dict) and "triplets" in stage_output:
            triplets = stage_output["triplets"]
            for triplet in triplets:
                if isinstance(triplet, TemporalTriplet):
                    await insert_triplet(triplet)
    except Exception:
        # Neo4j mirroring is optional - don't fail ingestion
        pass


async def _mirror_invalidations_to_neo4j(stage_output: Any) -> None:
    """Mirror invalidation updates to Neo4j."""
    try:
        if isinstance(stage_output, dict) and "events" in stage_output:
            events = stage_output["events"]
            invalidation_events = [
                e for e in events 
                if isinstance(e, TemporalEvent) and e.event_type in ["invalidation", "expiration"]
            ]
            await batch_process_invalidation(invalidation_events)
    except Exception:
        # Neo4j mirroring is optional - don't fail ingestion
        pass


async def _mirror_complete_transcript_to_neo4j(stage_output: Any) -> None:
    """Mirror complete transcript data to Neo4j."""
    try:
        if isinstance(stage_output, dict):
            transcript_id = stage_output.get("transcript_id", f"transcript_{uuid.uuid4().hex[:8]}")
            
            entities = stage_output.get("entities", [])
            triplets = stage_output.get("triplets", [])
            events = stage_output.get("events", [])
            
            # Filter for proper types
            temporal_entities = [e for e in entities if isinstance(e, TemporalEntity)]
            temporal_triplets = [t for t in triplets if isinstance(t, TemporalTriplet)]
            temporal_events = [e for e in events if isinstance(e, TemporalEvent)]
            
            await ingest_transcript(transcript_id, temporal_entities, temporal_triplets, temporal_events)
    except Exception:
        # Neo4j mirroring is optional - don't fail ingestion
        pass


# Add helper methods to UnifiedKGIngestionDAG class
UnifiedKGIngestionDAG._mirror_entities_to_neo4j = staticmethod(_mirror_entities_to_neo4j)
UnifiedKGIngestionDAG._mirror_triplets_to_neo4j = staticmethod(_mirror_triplets_to_neo4j)
UnifiedKGIngestionDAG._mirror_invalidations_to_neo4j = staticmethod(_mirror_invalidations_to_neo4j)
UnifiedKGIngestionDAG._mirror_complete_transcript_to_neo4j = staticmethod(_mirror_complete_transcript_to_neo4j)


__all__ = [
    "IngestionStage",
    "FailurePolicy",
    "IngestionStatus",
    "StageResult",
    "IngestionDAGResult",
    "IngestionDAGConfig",
    "UnifiedKGIngestionDAG",
    "ingest_documents",
]
