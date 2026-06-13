"""Policy Decision Point (PDP) — shared decision primitives for hook scripts (P6).

Pattern: Microsoft Entra Authorization Fabric — separate Policy Enforcement
Points (hook scripts that call this module) from Policy Decision Points
(pure functions in this package).

PEP  = docs/archive/windsurf/legacy-tree/governance_scripts/*.py (hooks) + ops_scripts/ci/check_*.py (CI gates)
PDP  = tools/policy/decisions/*.py (this package)

Benefits:
    - Decision logic is pure (no I/O, no stdin, no env access) → easy unit tests
    - Multiple PEPs can share one PDP (hook + CI gate agree by construction)
    - Policy changes land in one place, not N hook scripts

This is a scaffold. Over time, extract decision logic from hook scripts
one at a time. Do NOT refactor all hooks at once — ship the pattern, adopt
incrementally.

Initial PDPs:
    adg_first — ADG-first dependency analysis enforcement decision
"""

from __future__ import annotations

from .adg_first import (
    AdgFirstDecision,
    AdgFirstVerdict,
    classify_grep_for_deps,
)

__all__ = [
    "AdgFirstDecision",
    "AdgFirstVerdict",
    "classify_grep_for_deps",
]
