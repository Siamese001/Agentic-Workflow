"""EmbeddingNonInterferenceGuard — L5 Safety enforcement.

Asserts that C0 RAG embedding context does NOT appear in routing decision
inputs.  C0 is informational only: it must never mutate tier selection,
policy evaluation, or manifest content.

Guard contract:
- assert_no_c0_influence(routing_inputs, c0_context) raises
  C0InterferenceViolation if any C0 key/value leaks into routing_inputs.
- verify_routing_decision_clean(decision) checks a RoutingDecision dict for
  embedded C0 markers.

Invariants:
  - No wall-clock access.
  - Deterministic: same inputs -> same result.
  - Fail-closed: if analysis raises, guard defaults to VIOLATION.

# guardian: allow-direct-prompt-compilation
"""

from __future__ import annotations

import ast as _ast
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)


class C0InterferenceViolation(RuntimeError):
    """Raised when C0 RAG context is found to influence routing inputs."""


_C0_FORBIDDEN_FIELDS: frozenset[str] = frozenset(
    {"route_mode", "execution_tier", "safety_threshold", "policy_hash"}
)
_C0_MARKER_KEYS: frozenset[str] = frozenset(
    {
        "c0_context",
        "c0_embedding",
        "c0_rag",
        "c0_retrieval",
        "c0_score",
        "embedding_context",
        "embedding_hits",
        "embedding_results",
        "rag_context",
        "rag_hits",
        "rag_results",
        "retrieval_context",
        "retrieval_results",
    }
)
_C0_VALUE_FRAGMENTS: tuple[str, ...] = (
    "c0_context",
    "c0_rag",
    "rag_result",
    "embedding_hit",
    "retrieval_hit",
)


def assert_c0_context_clean(c0_context: dict[str, Any]) -> None:
    """Assert that *c0_context* does not contain routing-influencing fields.

    C0 context is strictly informational.  The presence of any field from
    ``_C0_FORBIDDEN_FIELDS`` means C0 is leaking into routing / execution
    tier / safety configuration — a hard violation.

    Args:
        c0_context: The C0 context dict to inspect.

    Raises:
        C0InterferenceViolation: if any forbidden field is present.
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "assert_c0_context_clean", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "assert_c0_context_clean", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L5_SAFETY, "assert_c0_context_clean")
    violations = [
        f"forbidden field {field!r} present in c0_context"
        for field in _C0_FORBIDDEN_FIELDS
        if field in c0_context
    ]
    if violations:
        raise C0InterferenceViolation(
            "EmbeddingNonInterferenceGuard: C0 context carries routing-influencing fields that violate the informational boundary:\n"
            + "\n".join(f"  - {v}" for v in violations)
        )


def assert_no_c0_influence(routing_inputs: dict[str, Any], c0_context: dict[str, Any] | None = None) -> None:
    """Assert that *routing_inputs* contains no C0 RAG markers.

    Args:
        routing_inputs: The dict of inputs passed to the routing tier
            (e.g. RoutingInputs fields, manifest dict).
        c0_context: Optional C0 context dict.  If provided, we additionally
            verify that none of its keys/values appear verbatim in
            routing_inputs.

    Raises:
        C0InterferenceViolation: if any C0 marker is detected.
    """
    violations: list[str] = []
    for key in routing_inputs:
        if str(key).lower() in _C0_MARKER_KEYS:
            violations.append(f"C0 marker key {key!r} found in routing_inputs")
    for key, value in routing_inputs.items():
        if isinstance(value, str):
            for frag in _C0_VALUE_FRAGMENTS:
                if frag in value.lower():
                    violations.append(f"C0 fragment {frag!r} found in routing_inputs[{key!r}]")
    if c0_context:
        assert_c0_context_clean(c0_context)
        for c0_key in c0_context:
            if c0_key in routing_inputs:
                # guardian: allow-direct-prompt-compilation
                violations.append(
                    f"C0 context key {c0_key!r} also present in routing_inputs (verbatim key collision)"
                )
    if violations:
        raise C0InterferenceViolation(
            "EmbeddingNonInterferenceGuard: C0 influence detected in routing inputs:\n"
            + "\n".join(f"  - {v}" for v in violations)
        )


def verify_routing_decision_clean(decision: dict[str, Any]) -> bool:
    """Return True if *decision* contains no C0 provenance markers.

    Does NOT raise; returns False on detection so callers can log and decide
    whether to hard-fail.
    """
    for key in decision:
        if str(key).lower() in _C0_MARKER_KEYS:
            return False
    for value in decision.values():
        if isinstance(value, str):
            for frag in _C0_VALUE_FRAGMENTS:
                if frag in value.lower():
                    return False
    return True


def assert_routing_decision_clean(decision: dict[str, Any]) -> None:
    """Raise C0InterferenceViolation if *decision* carries C0 markers."""
    if not verify_routing_decision_clean(decision):
        raise C0InterferenceViolation(
            "EmbeddingNonInterferenceGuard: C0 provenance markers detected in routing decision. C0 is informational only and must not reach routing outputs."
        )


def scan_file_for_c0_mutations(source_path: Any) -> list[str]:
    """AST-scan *source_path* for writes to C0-marker attributes.

    Returns a list of violation strings (empty == clean).
    """
    from pathlib import Path

    path = Path(source_path)
    if not path.exists():
        return [f"file not found: {path}"]
    source = path.read_text(encoding="utf-8", errors="replace")
    try:
        tree = _ast.parse(source, filename=str(path))
    except SyntaxError as exc:
        return [f"SyntaxError at line {exc.lineno}: {exc.msg}"]
    violations: list[str] = []
    for node in _ast.walk(tree):
        if isinstance(node, _ast.Assign):
            for target in node.targets:
                if isinstance(target, _ast.Attribute):
                    if target.attr.lower() in _C0_MARKER_KEYS:
                        violations.append(f"line {node.lineno}: assignment to C0 attribute '{target.attr}'")
    return violations


__all__ = [
    "C0InterferenceViolation",
    "assert_c0_context_clean",
    "assert_no_c0_influence",
    "assert_routing_decision_clean",
    "scan_file_for_c0_mutations",
    "verify_routing_decision_clean",
]
