"""Egress Blocking Rules — blocks internal labels, fake precision, vendor-first.

W4.1: Egress verifier that checks rendered cards against blocking rules
before they leave the L2 pipeline.

Plan: .windsurf/plans/apps-qna-spine-integration-e9c5b3.md W4.1
"""

from __future__ import annotations

import re
from typing import Any

_BLOCKED_PATTERNS: tuple[tuple[str, str], ...] = (
    ("fake_precision", r"\b\d{2,}\s*%\s*(improvement|lift|gain|reduction)\b"),
    ("vendor_first", r"^(AWS|Azure|GCP|OpenAI|Anthropic)\s"),
    ("internal_label", r"\b(PROJ-\d{4}|INTERNAL-ONLY|CONFIDENTIAL)\b"),
)


def check_egress(
    *,
    cards: dict[str, str],
) -> dict[str, Any]:
    """Check rendered cards against egress blocking rules.

    Args:
        cards: Dict of card_id -> rendered content.

    Returns:
        Egress check result with violations and pass/fail status.
    """
    violations: list[dict[str, str]] = []

    for card_id, content in cards.items():
        for rule_name, pattern in _BLOCKED_PATTERNS:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                violations.append({
                    "card_id": card_id,
                    "rule": rule_name,
                    "match": str(match),
                })

    return {
        "passed": len(violations) == 0,
        "violations": tuple(violations),
        "cards_checked": len(cards),
    }


__all__ = ["check_egress"]
