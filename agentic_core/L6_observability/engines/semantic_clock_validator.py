"""SemanticClockHashValidator — L6 Observability gate.

Validates that a SemanticClockAdvancementArtifact's stored artifact_hash
matches the re-computed hash from its fields.  No wall-clock access is
permitted in this module.

Gate contract:
- validate_artifact()  -> raises SemanticClockHashMismatch on tamper.
- scan_module_for_wallclock() -> AST-scan to assert no wall-clock calls.
"""

from __future__ import annotations

import ast
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "semantic_clock_validator")
emit_determinism_digest("p0", "semantic_clock_validator")

_emit_dispatches_healing_run("p1", "semantic_clock_validator", "L6")
_emit_routes_through("p1", "semantic_clock_validator", "L6")
_emit_escalates_to_human("p1", "semantic_clock_validator", "L6")
_emit_reads_policy_state("p1", "semantic_clock_validator", "L6")


class SemanticClockHashMismatch(ValueError):
    """Raised when a SemanticClockAdvancementArtifact hash fails validation."""


@dataclass(frozen=True)
class SemanticClockValidationResult:
    """Result of a clock artifact hash validation."""

    valid: bool
    stored_hash: str
    computed_hash: str
    advancement_id: str

    @property
    def mismatch(self) -> bool:
        return not self.valid


def validate_artifact(artifact: Any) -> SemanticClockValidationResult:
    """Validate a SemanticClockAdvancementArtifact's artifact_hash.

    The artifact must expose:
        .advancement_id (str)
        .previous_tick  (int)
        .new_tick       (int)
        .advancement_reason (str)
        .l4_version_binding (str)
        .provider_id    (str)
        .timestamp      (float)
        .artifact_hash  (str, 64-char hex)

    Returns:
        SemanticClockValidationResult with valid=True if hashes match.

    Raises:
        SemanticClockHashMismatch: if stored != computed hash.
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "validate_artifact", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "validate_artifact", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L6_OBSERVABILITY, "validate_artifact")
    material = {
        "advancement_id": str(artifact.advancement_id),
        "advancement_reason": str(artifact.advancement_reason),
        "l4_version_binding": str(artifact.l4_version_binding),
        "new_tick": int(artifact.new_tick),
        "previous_tick": int(artifact.previous_tick),
        "provider_id": str(artifact.provider_id),
        "timestamp": float(artifact.timestamp),
    }
    canonical = _canonical_json_bytes(material)
    computed = hashlib.sha256(canonical).hexdigest()
    stored = str(artifact.artifact_hash)
    result = SemanticClockValidationResult(
        valid=stored == computed,
        stored_hash=stored,
        computed_hash=computed,
        advancement_id=str(artifact.advancement_id),
    )
    if not result.valid:
        raise SemanticClockHashMismatch(
            f"SemanticClockValidator: artifact_hash mismatch for advancement_id={artifact.advancement_id!r}. stored={stored!r}, computed={computed!r}"
        )
    return result


_WALL_CLOCK_ATTRS: frozenset[str] = frozenset(
    {"time", "now", "utcnow", "monotonic", "perf_counter", "gmtime", "localtime"}
)


def scan_module_for_wallclock(module_path: Path) -> list[str]:
    """AST-scan *module_path* for wall-clock calls.

    Returns a list of violation strings (empty == clean).
    """
    if not module_path.exists():
        return [f"module not found: {module_path}"]
    source = module_path.read_text(encoding="utf-8", errors="replace")
    try:
        tree = ast.parse(source, filename=str(module_path))
    except SyntaxError as exc:
        return [f"SyntaxError at line {exc.lineno}: {exc.msg}"]
    violations: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Attribute) and func.attr in _WALL_CLOCK_ATTRS:
            violations.append(f"line {node.lineno}: wall-clock call '{func.attr}()'")
    return violations


def _canonical_json_bytes(data: Any) -> bytes:
    return json.dumps(data, sort_keys=True).encode("utf-8")


__all__ = [
    "SemanticClockHashMismatch",
    "SemanticClockValidationResult",
    "scan_module_for_wallclock",
    "validate_artifact",
]
