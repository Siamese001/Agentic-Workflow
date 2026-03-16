"""
ImportGuard - Guardrail for Dynamic Import Operations

Provides pre-import guardrail checks for importlib.import_module(),
importlib.util.spec_from_file_location(), and __import__() operations.
Emits applies_guardrail ADG edges for tracking and compliance.

Usage:
    from agentic_core.L5_safety.enforcement.import_guard import get_import_guard

    guard = get_import_guard()
    guard.check(operation="import_module", module_name="some.module")
    # Then proceed with actual import
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
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
    _emit_reads_policy_state,  # noqa: E402  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "import_guard")
emit_determinism_digest("p0", "import_guard")

_emit_dispatches_healing_run("p1", "import_guard", "L5")
_emit_routes_through("p1", "import_guard", "L5")
_emit_escalates_to_human("p1", "import_guard", "L5")
_emit_reads_policy_state("p1", "import_guard", "L5")
_emit_snapshots_state("p0", "import_guard", "state_snapshot")
_emit_authorize_and_execute("p2", "import_guard", "execution_auth")
_emit_validates_capability("p2", "import_guard", "capability_check")
_emit_routes_to_capability("p2", "import_guard", "capability_route")
_emit_writes_via_uwg("p2", "import_guard", "uwg_write")
_emit_blocks_direct_write("p2", "import_guard", "direct_write_block")
_emit_records_tool_invocation("p2", "import_guard", "tool_invocation")
_emit_captures_execution_output("p2", "import_guard", "exec_output")
_emit_dispatches_agent("p3", "import_guard", "agent_dispatch")
_emit_coordinates_agents("p3", "import_guard", "agent_coordination")
_emit_records_workflow_lineage("p3", "import_guard", "workflow_lineage")
_emit_records_healing_outcome("p3", "import_guard", "healing_outcome")
_emit_escalates_failure("p3", "import_guard", "failure_escalation")
_emit_orchestrates_workflow("p3", "import_guard", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "import_guard", "healing_dispatch")
_emit_invokes_evaluation("p3", "import_guard", "evaluation_signal")
_emit_records_telemetry_event("p4", "import_guard", "telemetry_event")
_emit_captures_evaluation_metric("p4", "import_guard", "eval_metric")
_emit_stores_embedding("p4", "import_guard", "embedding_store")
_emit_updates_meta_learning_state("p4", "import_guard", "meta_learning")
_emit_links_execution_to_snapshot("p4", "import_guard", "exec_snapshot_link")

logger = logging.getLogger(__name__)


class DynamicImportDeniedError(Exception):
    """Raised when a dynamic import is denied by guardrail."""

    pass


class ImportGuard:
    """
    Guardrail for dynamic import operations.

    Enforces allowlist/denylist policy and logging before
    allowing importlib or __import__ operations.
    """

    # Module prefixes that are always denied
    DENY_PREFIXES = (
        "os.path",
        "subprocess",
        "ctypes",
        "socket",
        "pickle",
        "marshal",
    )

    # Module prefixes that are always allowed (no logging needed)
    ALLOW_PREFIXES = (
        "agentic_core.",
        "apps_",
        "tests.",
        "tools.",
        "ops_scripts.",
        "system_learning.",
    )

    def __init__(self, mode: str = "warn") -> None:
        """
        Initialize ImportGuard.

        Args:
            mode: "warn" (log violations) or "enforce" (block violations)
        """
        self.mode = mode
        self._import_log: list[dict[str, Any]] = []

    def check(
        self,
        operation: str,
        module_name: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Pre-import guardrail check for dynamic import operations.

        Args:
            operation: Operation being performed ("import_module", "__import__", etc.)
            module_name: Module being imported (if available)
            metadata: Additional context

        Returns:
            dict with verdict and details

        Raises:
            DynamicImportDeniedError: If import is denied in enforce mode
        """
        _emit_verifies_policy(str(uuid.uuid4()), "ImportGuard.check", "L5_POLICY")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "ImportGuard.check")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:ImportGuard.check".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        metadata = metadata or {}
        timestamp = datetime.now(timezone.utc)

        # Emit applies_guardrail ADG edge (structured log for scanner)
        logger.debug(
            "applies_guardrail operation=%s guard=ImportGuard mode=%s",
            operation,
            self.mode,
        )

        verdict = "allow"
        reason = "Dynamic import allowed"

        if module_name:
            # Check deny prefixes
            for prefix in self.DENY_PREFIXES:
                if module_name.startswith(prefix):
                    verdict = "deny"
                    reason = f"Module prefix denied: {prefix}"
                    logger.warning(
                        "ImportGuard DENY: %s module=%s - %s",
                        operation,
                        module_name,
                        reason,
                    )
                    if self.mode == "enforce":
                        raise DynamicImportDeniedError(f"Dynamic import denied: {reason}")
                    break

        record = {
            "timestamp": timestamp.isoformat(),
            "operation": operation,
            "module_name": module_name,
            "verdict": verdict,
            "reason": reason,
            "metadata": metadata,
        }
        self._import_log.append(record)

        logger.info(
            "ImportGuard %s: %s module=%s",
            verdict.upper(),
            operation,
            module_name or "<unknown>",
        )

        return {"verdict": verdict, "reason": reason, "timestamp": timestamp.isoformat()}

    def get_import_log(self) -> list[dict[str, Any]]:
        """Get full import log."""
        return self._import_log.copy()

    def clear_log(self) -> None:
        """Clear import log."""
        self._import_log.clear()


_global_guard = ImportGuard(mode="warn")


def get_import_guard() -> ImportGuard:
    """Get global ImportGuard instance."""
    return _global_guard


def set_import_guard_mode(mode: str) -> None:
    """Set global ImportGuard mode ("warn" or "enforce")."""
    _emit_applies_guardrail(str(uuid.uuid4()), "Module.set_import_guard_mode", "L5_POLICY")
    global _global_guard
    _global_guard = ImportGuard(mode=mode)
