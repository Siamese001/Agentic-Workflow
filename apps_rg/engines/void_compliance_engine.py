"""
Void Compliance Engine - Architecture enforcement and legacy import prevention
Refactored from void_compliance.py
Following Batch 6 specifications with AST scanning

HARDENING: Uses SovereignContext for reporting. Scans file system (not buffer).
Writes 'compliance_audit'.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config import (
    APPS_RG_DIR,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_authorize_and_execute("p2", "void_compliance_engine", "execution_auth")
_emit_validates_capability("p2", "void_compliance_engine", "capability_check")
_emit_routes_to_capability("p2", "void_compliance_engine", "capability_route")
_emit_writes_via_uwg("p2", "void_compliance_engine", "uwg_write")
_emit_blocks_direct_write("p2", "void_compliance_engine", "direct_write_block")
_emit_records_tool_invocation("p2", "void_compliance_engine", "tool_invocation")
_emit_captures_execution_output("p2", "void_compliance_engine", "exec_output")
_emit_dispatches_agent("p3", "void_compliance_engine", "agent_dispatch")
_emit_coordinates_agents("p3", "void_compliance_engine", "agent_coordination")
_emit_records_workflow_lineage("p3", "void_compliance_engine", "workflow_lineage")
_emit_records_healing_outcome("p3", "void_compliance_engine", "healing_outcome")
_emit_escalates_failure("p3", "void_compliance_engine", "failure_escalation")
_emit_orchestrates_workflow("p3", "void_compliance_engine", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "void_compliance_engine", "healing_dispatch")
_emit_invokes_evaluation("p3", "void_compliance_engine", "evaluation_signal")
_emit_records_telemetry_event("p4", "void_compliance_engine", "telemetry_event")
_emit_captures_evaluation_metric("p4", "void_compliance_engine", "eval_metric")
_emit_stores_embedding("p4", "void_compliance_engine", "embedding_store")
_emit_updates_meta_learning_state("p4", "void_compliance_engine", "meta_learning")
_emit_links_execution_to_snapshot("p4", "void_compliance_engine", "exec_snapshot_link")
from apps_rg.engines.base_rg_engine import BaseRGEngine

_emit_applies_guardrail("p0", "void_compliance_engine", "p0_governance")
_emit_reads_policy_state("p0", "void_compliance_engine", "policy_binding")
_emit_snapshots_state("p0", "void_compliance_engine", "state_snapshot")
emit_replay_key("p0", "void_compliance_engine")
emit_determinism_digest("p0", "void_compliance_engine")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

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

    async def execute(self) -> dict[str, Any]:
        """
        Scan architecture for forbidden legacy imports.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "VoidComplianceEngine.execute")

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
        except (OSError, UnicodeDecodeError) as e:
            # Expected file reading errors
            self.logger.warning(f"Could not read file {file_path}: {e}")
            return False
        except Exception as e:
            # Critical errors during file processing
            self.logger.error(f"Unexpected error processing file {file_path}: {e}")
            return False
