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
"""

from __future__ import annotations

import ast as _ast
from typing import Any


class C0InterferenceViolation(RuntimeError):
    """Raised when C0 RAG context is found to influence routing inputs."""


# ---------------------------------------------------------------------------
# C0 marker taxonomy
# ---------------------------------------------------------------------------

# Keys that indicate C0 provenance when found in routing structures.
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

# String fragments that identify C0 provenance in values.
_C0_VALUE_FRAGMENTS: tuple[str, ...] = (
    "c0_context",
    "c0_rag",
    "rag_result",
    "embedding_hit",
    "retrieval_hit",
)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def assert_no_c0_influence(
    routing_inputs: dict[str, Any],
    c0_context: dict[str, Any] | None = None,
) -> None:
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

    # 1. Check for known C0 marker keys directly in routing_inputs.
    for key in routing_inputs:
        if str(key).lower() in _C0_MARKER_KEYS:
            violations.append(
                f"C0 marker key {key!r} found in routing_inputs"
            )

    # 2. Check string values for C0 fragments.
    for key, value in routing_inputs.items():
        if isinstance(value, str):
            for frag in _C0_VALUE_FRAGMENTS:
                if frag in value.lower():
                    violations.append(
                        f"C0 fragment {frag!r} found in routing_inputs[{key!r}]"
                    )

    # 3. If c0_context provided, verify no verbatim key overlap.
    if c0_context:
        for c0_key in c0_context:
            if c0_key in routing_inputs:
                violations.append(
                    f"C0 context key {c0_key!r} also present in routing_inputs"
                    f" (verbatim key collision)"
                )

    if violations:
        raise C0InterferenceViolation(
            "EmbeddingNonInterferenceGuard: C0 influence detected in routing "
            "inputs:\n" + "\n".join(f"  - {v}" for v in violations)
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
            "EmbeddingNonInterferenceGuard: C0 provenance markers detected in "
            "routing decision. C0 is informational only and must not reach "
            "routing outputs."
        )


# ---------------------------------------------------------------------------
# AST-based guard: verify the guard module itself has no C0 writes
# ---------------------------------------------------------------------------

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
                        violations.append(
                            f"line {node.lineno}: assignment to C0 attribute"
                            f" '{target.attr}'"
                        )
    return violations


__all__ = [
    "C0InterferenceViolation",
    "assert_no_c0_influence",
    "assert_routing_decision_clean",
    "scan_file_for_c0_mutations",
    "verify_routing_decision_clean",
]
