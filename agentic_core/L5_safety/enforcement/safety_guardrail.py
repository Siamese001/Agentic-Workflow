from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_routes_through,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "safety_guardrail")
emit_determinism_digest("p0", "safety_guardrail")

_emit_dispatches_healing_run("p1", "safety_guardrail", "L5")
_emit_routes_through("p1", "safety_guardrail", "L5")
_emit_escalates_to_human("p1", "safety_guardrail", "L5")
_emit_reads_policy_state("p1", "safety_guardrail", "L5")

_emit_applies_guardrail("p0", "safety_guardrail", "p0_governance")
_emit_snapshots_state("p0", "safety_guardrail", "state_snapshot")

"\nL5 Safety: SafetyGuardrail\nEnforces Zero-Loss principles during code mutation.\n"
import ast
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
)


class SafetyGuardrail:
    """Enforces Zero-Loss principles during mutation."""

    # guardian: allow-magic-config
    def __init__(self, deletion_limit: int = 110):
        """
        Initialize SafetyGuardrail.

        Args:
            deletion_limit: Maximum number of lines that can be deleted in standard mode
        """
        self.deletion_limit = deletion_limit

    def verify_change(
        self, original_code: str, new_code: str, fission_active: bool = False
    ) -> tuple[bool, str]:
        """
        Verify that code changes are safe and don't violate zero-loss principles.

        Args:
            original_code: Original code before mutation
            new_code: New code after mutation
            fission_active: Whether atomic fission is active (allows mass deletion)

        Returns:
            Tuple of (is_safe, message)
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "SafetyGuardrail.verify_change")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:SafetyGuardrail.verify_change".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if not new_code.strip():
            return (False, "Safety Block: Attempted to wipe file.")
        try:
            ast.parse(new_code)
        except SyntaxError as e:
            return (False, f"Safety Block: Mutation introduced syntax error: {e.msg} at line {e.lineno}")
        orig_len: Any = len(original_code.splitlines())
        new_len: Any = len(new_code.splitlines())
        delta: Any = orig_len - new_len
        if delta == 0 and original_code == new_code and (not fission_active):
            return (False, "Safety Block: Mutation resulted in no change (possible engine failure).")
        if fission_active:
            return (True, "Fission Whitelist: Mass deletion permitted for Facade.")
        if delta > self.deletion_limit:
            return (False, f"Safety Block: Mass deletion detected ({delta} lines).")
        return (True, "Safety Pass.")
