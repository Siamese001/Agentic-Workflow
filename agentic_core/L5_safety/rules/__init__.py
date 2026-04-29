"""
G15 — Hard-vs-Remediable Rule Tagging.

Per ADR-070 L5 Guardrail Family Catalog (2026-04-29).
Phase: W4 P8 W3/P8.15 — `.windsurf/plans/w4-p8-guardrail-family-e93f8a.md`

Every L5 enforcement rule MUST be tagged with one of two dispositions:

  HARD       — violation halts execution, no recovery path; the request is
               rejected. Used for safety-critical invariants (e.g. PII leak,
               egress to malicious domain, capability token forgery).

  REMEDIABLE — violation is a remediation candidate. The request is
               quarantined and a healer/repair path is invoked. Recovery
               is allowed if the healer succeeds. Used for repairable
               problems (e.g. malformed structured output, missing
               required field, recoverable schema drift).

Tag distinction is critical for the assurance plane: HARD rules drive
fail-closed circuits; REMEDIABLE rules drive the healer pipeline. Every
rule must declare which class it is — untagged rules are forbidden.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class RuleDisposition(str, Enum):
    """Two-class taxonomy for L5 rule tagging — exhaustive."""

    HARD = "hard"
    REMEDIABLE = "remediable"


@dataclass(frozen=True)
class TaggedRule:
    """A rule annotated with its hard-vs-remediable disposition. Immutable."""

    rule_id: str  # e.g. "G08-egress-pii-block"
    disposition: RuleDisposition
    family: str  # G-id, e.g. "G08"
    description: str
    rationale: str  # why HARD vs REMEDIABLE — required so future authors can audit


def assert_disposition(rule: TaggedRule, expected: RuleDisposition) -> None:
    """Raise AssertionError if rule's disposition is not as expected.

    Used in tests to lock in the disposition contract for safety-critical rules.
    """
    if rule.disposition is not expected:
        raise AssertionError(
            f"Rule {rule.rule_id} (family {rule.family}) expected {expected.value}, "
            f"got {rule.disposition.value}. Changing a rule's disposition requires "
            f"Author-Gate approval per ADR-070 G15."
        )


__all__ = ["RuleDisposition", "TaggedRule", "assert_disposition"]
