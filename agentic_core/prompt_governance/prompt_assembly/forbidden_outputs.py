"""PA Forbidden-Output Discipline.

The Prompt Assembly doctrine forbids each child stage from emitting any
runtime disposition or execution verb. Those belong to Runtime Gates,
L2, UWG/L4, Exit Eval, and L5 — never to PA.

This module is the SSOT for the forbidden vocabulary and provides a
single :func:`assert_no_forbidden` helper that scans an arbitrary
mapping (a receipt, manifest, or event payload) for any forbidden
token used as a status / disposition / decision string.

Doctrine reference:
    docs/reference/03_L0_Routing/Prompt Assembly/Prompt_Assembly_detailed.md
        section "FORBIDDEN OUTPUTS FROM THIS CHILD"
"""

from __future__ import annotations

from typing import Any, Iterable, Mapping


# Runtime dispositions PA must never emit.
FORBIDDEN_DISPOSITIONS: frozenset[str] = frozenset(
    {
        "ALLOW",
        "DENY",
        "CLARIFY",
        "ABSTAIN",
        "REROUTE",
        "SHRINK_SCOPE",
        "RETRY",
        "HEAL",
        "ESCALATE_HITL",
        "QUARANTINE",
        "REDACT",
        "SAFE_FALLBACK",
        "MARK_DEGRADED",
        "COMMIT_REQUEST",
        "BLOCK_COMMIT",
        "ALLOW_FINISH",
    }
)

# Execution verbs PA must never use as method/decision names in receipts.
FORBIDDEN_EXECUTION_VERBS: frozenset[str] = frozenset(
    {
        "approve_execution",
        "approve_output",
        "approve_write",
        "call_provider",
        "execute_tool",
        "mutate_l4",
    }
)

# Field names that, by doctrine, MUST carry a PA_* status (not a runtime
# disposition). When any of these fields appears in a receipt, its value
# must be a PA_* token (or an internal stage enum that maps to one).
PA_STATUS_FIELDS: frozenset[str] = frozenset(
    {
        "pa_status",
        "doctrine_status",
        "status",
        "assembly_status",
    }
)

# Decision-class field names that PA must never populate with a forbidden
# token. ``find_forbidden`` only flags string leaves whose key is one of
# these — it does NOT walk every string everywhere, because PA legitimately
# carries chunk-level classification labels (e.g. C0 chunk
# ``disposition='QUARANTINE'``) as data passed through to L2/Runtime Gates,
# not as PA's own decision. The doctrine's forbidden vocabulary applies to
# the OUTPUT of the PA stage, which is captured in these fields.
PA_DECISION_FIELDS: frozenset[str] = frozenset(
    {
        "decision",
        "doctrine_status",
        "pa_status",
        "assembly_status",
        "verdict",
        "recommended_disposition",
        "runtime_disposition",
        "stage_decision",
        "final_disposition",
    }
)


class ForbiddenOutputError(ValueError):
    """Raised when a PA receipt contains a forbidden disposition or verb."""


def _iter_decision_field_values(payload: Any, decision_fields: frozenset[str]) -> Iterable[tuple[str, str]]:
    """Yield (path, value) for every string leaf living under a decision-class key.

    The walk is field-aware: a string only emits if the key under which it
    sits is in ``decision_fields``. This intentionally ignores chunk-level
    classification labels (e.g. ``C0`` chunk records carrying a label of
    ``QUARANTINE``) which are data passed through PA, not PA's own
    decisions.

    Sequences inherit the parent key's decision-status so that decision
    fields like ``signed_fields`` (a list of strings) are still scanned
    when their parent is a decision field.
    """
    stack: list[tuple[str, Any, bool]] = [("$", payload, False)]
    while stack:
        path, node, is_decision = stack.pop()
        if isinstance(node, str):
            if is_decision:
                yield path, node
            continue
        if isinstance(node, Mapping):
            for k, v in node.items():
                child_decision = is_decision or (str(k) in decision_fields)
                stack.append((f"{path}.{k}", v, child_decision))
            continue
        if isinstance(node, (list, tuple, set, frozenset)):
            for i, v in enumerate(node):
                stack.append((f"{path}[{i}]", v, is_decision))
            continue
        # primitives — ignore.


def find_forbidden(
    payload: Any,
    *,
    decision_fields: frozenset[str] | None = None,
) -> tuple[tuple[str, str], ...]:
    """Return ``((path, token), ...)`` for every forbidden value found in
    a decision-class field.

    Scans ``payload`` for any string leaf living under a key in
    ``decision_fields`` (defaulting to :data:`PA_DECISION_FIELDS`) that
    exactly matches a forbidden disposition or execution verb.
    """
    fields = decision_fields if decision_fields is not None else PA_DECISION_FIELDS
    out: list[tuple[str, str]] = []
    forbidden = FORBIDDEN_DISPOSITIONS | FORBIDDEN_EXECUTION_VERBS
    for path, value in _iter_decision_field_values(payload, fields):
        if value in forbidden:
            out.append((path, value))
    return tuple(out)


def assert_no_forbidden(payload: Any, *, label: str = "PA receipt") -> None:
    """Raise :class:`ForbiddenOutputError` if ``payload`` carries a forbidden value.

    Intended for unit tests and for runtime self-checks at PA stage
    boundaries. The error message lists every offending path so the
    fix is unambiguous.
    """
    hits = find_forbidden(payload)
    if not hits:
        return
    detail = "; ".join(f"{path}={token!r}" for path, token in hits)
    raise ForbiddenOutputError(f"{label} contains forbidden PA output(s): {detail}")


__all__ = [
    "FORBIDDEN_DISPOSITIONS",
    "FORBIDDEN_EXECUTION_VERBS",
    "PA_STATUS_FIELDS",
    "ForbiddenOutputError",
    "assert_no_forbidden",
    "find_forbidden",
]
