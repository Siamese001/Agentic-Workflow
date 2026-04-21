"""Runtime HITL escalation class taxonomy.

Per ADR-023 §3.1, L5 owns escalation classification. This module enumerates
the class names and their SSOT-level properties. Thresholds, timeouts, and
approver pools are resolved at runtime by ``hitl_policy`` against
``config/runtime_hitl_policy.yaml``.

Classes (G4 defaults, see ADR-023):
- ``financial``      — monetary or commitment-bearing actions (timeout 3600s)
- ``safety``         — physical/operational safety impact (timeout 1800s)
- ``regulated``      — compliance-bound actions (timeout 7200s)
- ``novel_context``  — novelty score above threshold (timeout 900s)
- ``low_confidence`` — model confidence below threshold (timeout 600s)
- ``policy_override``— explicit policy-override request (timeout 86400s)
"""

from __future__ import annotations

from enum import Enum
from typing import Final


class HitlClass(str, Enum):
    """Runtime HITL escalation class. String-valued for YAML/JSON round-trip."""

    FINANCIAL = "financial"
    SAFETY = "safety"
    REGULATED = "regulated"
    NOVEL_CONTEXT = "novel_context"
    LOW_CONFIDENCE = "low_confidence"
    POLICY_OVERRIDE = "policy_override"


HitlClassName = str  # Type alias for string form, used in public APIs.


ALL_CLASSES: Final[tuple[HitlClass, ...]] = tuple(HitlClass)

CLASS_NAMES: Final[frozenset[str]] = frozenset(c.value for c in HitlClass)


def is_valid_class(name: str) -> bool:
    """Return True if ``name`` is a recognized HITL class."""
    return name in CLASS_NAMES


__all__ = [
    "ALL_CLASSES",
    "CLASS_NAMES",
    "HitlClass",
    "HitlClassName",
    "is_valid_class",
]
