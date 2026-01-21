"""
RG Workflow Orchestrator - DAG-based workflow execution for resume generation.

Ported from: archives/legacy_resume_gen/Microservices Model/orchestrator.py
"""

import hashlib
import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set


class HopStatus(Enum):
    """Status of a workflow hop."""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class GateDecision(Enum):
    """Decision from a validation gate."""

    PASS = "PASS"
    FAIL = "FAIL"
    WARN = "WARN"
    SKIP = "SKIP"


@dataclass
class HopInput:
    """Input specification for a hop."""

    artifact_id: str
    required: bool = True
    description: str = ""


@dataclass
class HopOutput:
    """Output specification for a hop."""

    artifact_id: str
    description: str = ""


@dataclass
class RetryPolicy:
    """Retry policy for a hop."""

    max_retries: int = 3
    backoff_seconds: float = 1.0
    backoff_multiplier: float = 2.0


@dataclass
class HopSpec:
    """Specification for a workflow hop."""

    id: str
    script: str
    description: str
    inputs: List[HopInput] = field(default_factory=list)
    outputs: List[HopOutput] = field(default_factory=list)
    retry_policy: RetryPolicy = field(default_factory=RetryPolicy)
    extra_args: List[str] = field(default_factory=list)


@dataclass
class WorkflowSpec:
    """Specification for a complete workflow."""

    name: str
    version: str
    hops: List[HopSpec]


@dataclass
class Artifact:
    """A workflow Artifact (file)."""

    id: str
    path: Path
    hash: str
    is_ready: bool = False
    is_static: bool = False


@dataclass
class HopCheckpoint:
    """Checkpoint for a completed hop."""

    hop_id: str
    status: HopStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    output_artifacts: List[str] = field(default_factory=list)
    error_message: Optional[str] = None


@dataclass
class ValidationResult:
    """Result from a validation gate."""

    gate_id: str
    decision: GateDecision
    message: str
    details: Dict[str, object] = field(default_factory=dict)


class WorkflowSpecError(Exception):
    """Error in workflow specification."""

    pass


class HopExecutionError(Exception):
    """Error during hop execution."""

    pass


def hash_file(filepath: Path) -> str:
    """Calculate SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


class DAGBuilder:
    """Builder for workflow DAG."""

    def __init__(self) -> None:
        """Initialize the DAG builder."""
        self._nodes: Dict[str, HopSpec] = {}
        self._edges: List[tuple[str, str]] = []
        self._artifact_producers: Dict[str, str] = {}

    def add_hop(self, hop: HopSpec) -> "DAGBuilder":
        """Add a hop to the DAG."""
        if hop.id in self._nodes:
            raise WorkflowSpecError(f"Duplicate hop ID: {hop.id}")

        self._nodes[hop.id] = hop

        # Track Artifact producers
        for output in hop.outputs:
            if output.artifact_id in self._artifact_producers:
                raise WorkflowSpecError(
                    f"Duplicate Artifact output: {output.artifact_id}"
                )
            self._artifact_producers[output.artifact_id] = hop.id

        return self

    def build_edges(self) -> "DAGBuilder":
        """Build edges based on input/output dependencies."""
        for hop_id, hop in self._nodes.items():
            for input_spec in hop.inputs:
                artifact_id = input_spec.artifact_id
                if artifact_id.startswith("static_"):
                    continue  # Static inputs don't create dependencies

                producer_hop_id = self._artifact_producers.get(artifact_id)
                if not producer_hop_id:
                    if input_spec.required:
                        raise WorkflowSpecError(
                            f"Unresolved dependency: Hop '{hop_id}' requires "
                            f"Artifact '{artifact_id}'"
                        )
                else:
                    self._edges.append((producer_hop_id, hop_id))

        return self

    def get_execution_order(self) -> List[str]:
        """Get topological execution order."""
        # Build adjacency list
        in_degree: Dict[str, int] = {node: 0 for node in self._nodes}
        adjacency: Dict[str, List[str]] = {node: [] for node in self._nodes}

        for source, target in self._edges:
            adjacency[source].append(target)
            in_degree[target] += 1

        # Kahn's algorithm for topological sort
        queue = [node for node, degree in in_degree.items() if degree == 0]
        order: List[str] = []

        while queue:
            node = queue.pop(0)
            order.append(node)

            for neighbor in adjacency[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(order) != len(self._nodes):
            raise WorkflowSpecError("Workflow contains cycles")

        return order

    def validate(self) -> List[str]:
        """Validate the DAG and return any issues."""
        issues: List[str] = []

        # Check for cycles
        try:
            self.get_execution_order()
        except WorkflowSpecError as e:
            issues.append(str(e))

        return issues


class RGWorkflowOrchestrator:
    """
    Orchestrator for resume generation workflow.

    A spec-driven orchestrator that executes a workflow as a
    Directed Acyclic Graph (DAG), ensuring cryptographic provenance
    for all data artifacts.
    """

    VERSION = "16.0"

    def __init__(
        self,
        workflow_spec: Optional[WorkflowSpec] = None,
        run_base_dir: str = "./pipeline_runs",
    ) -> None:
        """
        Initialize the orchestrator.

        Args:
            workflow_spec: Workflow specification
            run_base_dir: foundation directory for run outputs
        """
        self.workflow_id = str(uuid.uuid4())[:8]
        self.Logger = logging.getLogger(__name__)
        self.run_base_dir = Path(run_base_dir)
        self.run_dir: Optional[Path] = None

        self.spec = workflow_spec
        self.artifacts: Dict[str, Artifact] = {}
        self.hop_checkpoints: List[HopCheckpoint] = []
        self.validation_results: List[ValidationResult] = []

        self._dag_builder: Optional[DAGBuilder] = None
        self._hop_executors: Dict[str, Callable[..., Any]] = {}

    def load_spec_from_file(self, spec_path: Path) -> None:
        """Load workflow spec from a JSON file."""
        if not spec_path.exists():
            raise WorkflowSpecError(f"Workflow spec not found: {spec_path}")

        with open(spec_path, "r", encoding="utf-8") as f:
            spec_data = json.load(f)

        hops = []
        for hop_data in spec_data.get("hops", []):
            hops.append(
                HopSpec(
                    id=hop_data["id"],
                    script=hop_data["script"],
                    description=hop_data["description"],
                    inputs=[HopInput(**inp) for inp in hop_data.get("inputs", [])],
                    outputs=[HopOutput(**out) for out in hop_data.get("outputs", [])],
                    retry_policy=RetryPolicy(**hop_data.get("retry_policy", {})),
                    extra_args=hop_data.get("extra_args", []),
                )
            )

        self.spec = WorkflowSpec(
            name=spec_data["name"],
            version=spec_data["version"],
            hops=hops,
        )

    def register_hop_executor(
        self,
        hop_id: str,
        executor: Callable[..., Any],
    ) -> None:
        """Register a executor function for a hop."""
        self._hop_executors[hop_id] = executor

    def setup_run_directory(
        self,
        company_name: str,
        job_title: str,
    ) -> Path:
        """Set up the run directory for this workflow execution."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_company = company_name.replace(" ", "_").replace("/", "_")
        self.run_dir = self.run_base_dir / f"{timestamp}_{self.workflow_id}_{safe_company}"
        self.run_dir.mkdir(parents=True, exist_ok=True)

        self.Logger.info(f"Run directory: {self.run_dir}")
        return self.run_dir

    def register_static_artifact(
        self,
        artifact_id: str,
        path: Path,
    ) -> None:
        """Register a static input Artifact."""
        if not path.exists():
            raise FileNotFoundError(f"Static Artifact not found: {path}")

        file_hash = hash_file(path)
        self.artifacts[artifact_id] = Artifact(
            id=artifact_id,
            path=path,
            hash=file_hash,
            is_ready=True,
            is_static=True,
        )

    def build_dag(self) -> DAGBuilder:
        """Build the workflow DAG from the spec."""
        if self.spec is None:
            raise WorkflowSpecError("No workflow spec loaded")

        self._dag_builder = DAGBuilder()
        for hop in self.spec.hops:
            self._dag_builder.add_hop(hop)

        self._dag_builder.build_edges()
        return self._dag_builder

    def get_execution_order(self) -> List[str]:
        """Get the execution order for hops."""
        if self._dag_builder is None:
            self.build_dag()
        return self._dag_builder.get_execution_order()

    def execute_hop(
        self,
        hop_id: str,
        context: Dict[str, object],
    ) -> HopCheckpoint:
        """
        Execute a single hop.

        Args:
            hop_id: ID of the hop to execute
            context: Execution context

        Returns:
            HopCheckpoint with execution results
        """
        Checkpoint = HopCheckpoint(
            hop_id=hop_id,
            status=HopStatus.RUNNING,
            start_time=datetime.now(),
        )

        try:
            executor = self._hop_executors.get(hop_id)
            if executor is None:
                raise HopExecutionError(f"No executor registered for hop: {hop_id}")

            # Execute the executor
            result = executor(context, self.artifacts)

            # Update Checkpoint
            Checkpoint.status = HopStatus.COMPLETED
            Checkpoint.end_time = datetime.now()

            if isinstance(result, dict) and "output_artifacts" in result:
                Checkpoint.output_artifacts = result["output_artifacts"]

        except (ValueError, TypeError, RuntimeError, KeyError) as e:
            Checkpoint.status = HopStatus.FAILED
            Checkpoint.end_time = datetime.now()
            Checkpoint.error_message = str(e)
            self.Logger.error(f"Hop {hop_id} failed: {e}")

        self.hop_checkpoints.append(Checkpoint)
        return Checkpoint

    def execute_workflow(
        self,
        context: Dict[str, object],
    ) -> Dict[str, object]:
        """
        Execute the complete workflow.

        Args:
            context: Initial execution context

        Returns:
            Workflow execution results
        """
        self.Logger.info(f"Starting workflow execution: {self.workflow_id}")

        execution_order = self.get_execution_order()
        self.Logger.info(f"Execution order: {execution_order}")

        results: Dict[str, object] = {
            "workflow_id": self.workflow_id,
            "status": "RUNNING",
            "hops_completed": [],
            "hops_failed": [],
        }

        for hop_id in execution_order:
            self.Logger.info(f"Executing hop: {hop_id}")
            Checkpoint = self.execute_hop(hop_id, context)

            if Checkpoint.status == HopStatus.COMPLETED:
                results["hops_completed"].append(hop_id)
            else:
                results["hops_failed"].append(hop_id)
                results["status"] = "FAILED"
                results["error"] = Checkpoint.error_message
                break

        if results["status"] != "FAILED":
            results["status"] = "COMPLETED"

        self.Logger.info(f"Workflow completed with status: {results['status']}")
        return results

    def get_checkpoint(self, hop_id: str) -> Optional[HopCheckpoint]:
        """Get Checkpoint for a specific hop."""
        for Checkpoint in self.hop_checkpoints:
            if Checkpoint.hop_id == hop_id:
                return Checkpoint
        return None

    def get_all_checkpoints(self) -> List[HopCheckpoint]:
        """Get all hop checkpoints."""
        return self.hop_checkpoints.copy()

    def add_validation_result(self, result: ValidationResult) -> None:
        """Add a validation result."""
        self.validation_results.append(result)

    def get_validation_results(self) -> List[ValidationResult]:
        """Get all validation results."""
        return self.validation_results.copy()

    def export_execution_log(self, output_path: Optional[Path] = None) -> Path:
        """Export execution log to a JSON file."""
        if output_path is None:
            if self.run_dir is None:
                output_path = Path(f"execution_log_{self.workflow_id}.json")
            else:
                output_path = self.run_dir / "execution_log.json"

        log_data = {
            "workflow_id": self.workflow_id,
            "version": self.VERSION,
            "spec_name": self.spec.name if self.spec else None,
            "spec_version": self.spec.version if self.spec else None,
            "checkpoints": [
                {
                    "hop_id": cp.hop_id,
                    "status": cp.status.value,
                    "start_time": cp.start_time.isoformat(),
                    "end_time": cp.end_time.isoformat() if cp.end_time else None,
                    "output_artifacts": cp.output_artifacts,
                    "error_message": cp.error_message,
                }
                for cp in self.hop_checkpoints
            ],
            "validation_results": [
                {
                    "gate_id": vr.gate_id,
                    "decision": vr.decision.value,
                    "message": vr.message,
                    "details": vr.details,
                }
                for vr in self.validation_results
            ],
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(log_data, f, indent=2)

        return output_path


def create_orchestrator(
    workflow_spec: Optional[WorkflowSpec] = None,
    run_base_dir: str = "./pipeline_runs",
) -> RGWorkflowOrchestrator:
    """builder function to create an orchestrator."""
    return RGWorkflowOrchestrator(workflow_spec, run_base_dir)


def load_workflow_spec(spec_path: Path) -> WorkflowSpec:
    """Load a workflow spec from a file."""
    orchestrator = RGWorkflowOrchestrator()
    orchestrator.load_spec_from_file(spec_path)
    return orchestrator.spec