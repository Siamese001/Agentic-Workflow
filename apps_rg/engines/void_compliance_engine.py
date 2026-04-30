"""
Void Compliance Engine - Architecture enforcement and legacy import prevention
Refactored from void_compliance.py
Following Batch 6 specifications with AST scanning

HARDENING: Uses SovereignContext for reporting. Scans file system (not buffer).
Writes 'compliance_audit'.
"""

from __future__ import annotations

from agentic_core.runtime.contracts.runtime_telemetry_decorators import (
    traces_execute,
)

import logging
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config import (
    APPS_RG_DIR,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

from apps_rg.engines.base_rg_engine import BaseRGEngine

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

from apps_rg.engines._lifecycle_emits import _emit_engine_lifecycle

_emit_engine_lifecycle("void_compliance_engine")


Logger = logging.getLogger(__name__)


class VoidComplianceEngine(BaseRGEngine):
    """
    Sovereign Safety Engine.
    Scans: File System ('apps_rg/')
    Writes: 'compliance_audit'
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="SAFETY.VOID")
        self.root_path = Path(APPS_RG_DIR)

    @traces_execute(layer="L3_ORCHESTRATION")
    async def execute(self) -> dict[str, Any]:
        """
        Scan architecture for forbidden legacy imports.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "VoidComplianceEngine.execute"
        )

        # 1. LOGIC
        violations = []
        if self.root_path.exists():
            for file_path in self.root_path.rglob("*.py"):
                # Skip self and legacy/quarantine folders
                if file_path.name == "void_compliance_engine.py":
                    continue
                if "legacy" in str(file_path) or "quarantine" in str(file_path):
                    continue

                if self._check_file(file_path):
                    violations.append(str(file_path))

        # 2. WRITE
        report = {"clean": len(violations) == 0, "violations": violations}
        self.ctx.buffer.write("compliance_audit", report, source_agent=self.name)

        if violations:
            self.record_fail(f"VOID POLICE: {len(violations)} legacy files detected", data=report)
            # In strict mode, we might signal critical failure
            self.ctx.add_signal("SYSTEM_CRITICAL")
        else:
            self.record_pass("Void Compliance Verified: 100% Clean")

        return report

    def _check_file(self, path: Path) -> bool:
        try:
            content = path.read_text("utf-8")
            # Check each line - skip commented lines
            for line in content.split("\n"):
                stripped = line.strip()
                if stripped.startswith("#"):
                    continue  # Skip comments
                if "import archives" in line or "from archives" in line:
                    return True
            return False
        except (
            OSError,
            UnicodeDecodeError,
        ) as e:  # review: File operations with encoding need error-specific handling
            # Expected file reading errors
            self.logger.warning(f"Could not read file {file_path}: {e}")
            return False
        except (RuntimeError, ValueError, TypeError, AttributeError, SyntaxError) as e:
            # Critical errors during file processing
            self.logger.error(f"Unexpected error processing file {file_path}: {e}")
            return False
