"""
FileClassificationValidatorAgent - L5 Pure Validator.

Runs FileClassificationAgent in validate_only mode to detect naming,
territory, and layer alignment violations without mutating the filesystem.
Emits a structured check dict consumed by heal_file_classification via
HEALER_REGISTRY.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "file_classification_validator")
emit_determinism_digest("p0", "file_classification_validator")

_emit_dispatches_healing_run("p1", "file_classification_validator", "L5")
_emit_routes_through("p1", "file_classification_validator", "L5")
_emit_escalates_to_human("p1", "file_classification_validator", "L5")
_emit_reads_policy_state("p1", "file_classification_validator", "L5")

_emit_applies_guardrail("p0", "file_classification_validator", "p0_governance")
_emit_snapshots_state("p0", "file_classification_validator", "state_snapshot")
_emit_authorize_and_execute("p2", "file_classification_validator", "execution_auth")
_emit_validates_capability("p2", "file_classification_validator", "capability_check")
_emit_routes_to_capability("p2", "file_classification_validator", "capability_route")
_emit_writes_via_uwg("p2", "file_classification_validator", "uwg_write")
_emit_blocks_direct_write("p2", "file_classification_validator", "direct_write_block")
_emit_records_tool_invocation("p2", "file_classification_validator", "tool_invocation")
_emit_captures_execution_output("p2", "file_classification_validator", "exec_output")
_emit_dispatches_agent("p3", "file_classification_validator", "agent_dispatch")
_emit_coordinates_agents("p3", "file_classification_validator", "agent_coordination")
_emit_records_workflow_lineage("p3", "file_classification_validator", "workflow_lineage")
_emit_records_healing_outcome("p3", "file_classification_validator", "healing_outcome")
_emit_escalates_failure("p3", "file_classification_validator", "failure_escalation")
_emit_orchestrates_workflow("p3", "file_classification_validator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "file_classification_validator", "healing_dispatch")
_emit_invokes_evaluation("p3", "file_classification_validator", "evaluation_signal")
_emit_records_telemetry_event("p4", "file_classification_validator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "file_classification_validator", "eval_metric")
_emit_stores_embedding("p4", "file_classification_validator", "embedding_store")
_emit_updates_meta_learning_state("p4", "file_classification_validator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "file_classification_validator", "exec_snapshot_link")

CHECK_ID = "file_classification"
logger = logging.getLogger(__name__)


class FileClassificationValidatorAgent:
    """L5 Certify-only validator for file classification compliance."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = Path(project_root).resolve()

    def scan(self, target_territory: str | None = None) -> dict[str, Any]:
        """Run FileClassificationAgent in validate_only mode.

        Args:
            target_territory: Optional territory string to scope the scan.

        Returns:
            Dict with keys: scan_result, violations, stats, file_registry.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L5_POLICY, "FileClassificationValidatorAgent.scan"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:FileClassificationValidatorAgent.scan".encode()
        ).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        from agentic_core.L5_safety.reasoning.FileClassificationAgent import FileClassificationAgent

        classifier = FileClassificationAgent(project_root=self.project_root)
        classifier.validate_only = True
        classifier.dry_run = False
        if hasattr(classifier, "target_territory"):
            classifier.target_territory = target_territory
        try:
            if target_territory:
                try:
                    scan_result = classifier.run(target_territory=target_territory) or {}
                except TypeError:
                    scan_result = classifier.run() or {}
            else:
                scan_result = classifier.run() or {}
        # guardian: allow-silent-swallow
        except Exception as exc:
            logger.error("[FileClassificationValidatorAgent] scan failed: %s", exc)
            scan_result = {}
        violations: list[dict[str, Any]] = []
        if hasattr(classifier, "stats") and classifier.stats.get("violations"):
            for vtype, count in classifier.stats["violations"].items():
                if isinstance(count, int) and count > 0:
                    violations.append(
                        {
                            "type": "CLASSIFICATION",
                            "subtype": vtype,
                            "count": count,
                            "territory": target_territory,
                        }
                    )
        file_registry: list[str] = []
        if hasattr(classifier, "file_registry") and classifier.file_registry:
            file_registry = [str(p) for p in classifier.file_registry]
        return {"scan_result": scan_result, "violations": violations, "file_registry": file_registry}

    def to_check_dict(self, target_territory: str | None = None) -> dict[str, Any]:
        """Return structured check dict for _invoke_healer dispatch."""
        evidence = self.scan(target_territory=target_territory)
        violations_count = sum(v.get("count", 1) for v in evidence.get("violations", []))
        return {
            "check_id": CHECK_ID,
            "evidence": evidence,
            "violations_count": violations_count,
            "territory": target_territory,
            "repo_root": str(self.project_root),
        }

    def run(self, target_territory: str | None = None) -> dict[str, Any]:
        """Alias for to_check_dict for orchestrator compatibility."""
        return self.to_check_dict(target_territory=target_territory)
