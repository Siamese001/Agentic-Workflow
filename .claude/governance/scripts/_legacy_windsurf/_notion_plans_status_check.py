#!/usr/bin/env python3
"""Re-export — SSOT is ``.claude/governance/scripts/_notion_plans_status_check.py``."""
from __future__ import annotations

import importlib.util
from pathlib import Path

_SSOT_PATH = (
    Path(__file__).resolve().parents[2]
    / ".cursor"
    / "scripts"
    / "_notion_plans_status_check.py"
)
_spec = importlib.util.spec_from_file_location(
    "_notion_plans_status_check_ssot",
    _SSOT_PATH,
)
if _spec is None or _spec.loader is None:
    raise ImportError(f"Cannot load Plans status SSOT from {_SSOT_PATH}")
_ssot = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_ssot)

PLANS_DB_ID = _ssot.PLANS_DB_ID
PLANS_DATA_SOURCE_ID = _ssot.PLANS_DATA_SOURCE_ID
BACKLOG_DB_ID = _ssot.BACKLOG_DB_ID
BACKLOG_DATA_SOURCE_ID = _ssot.BACKLOG_DATA_SOURCE_ID
CANONICAL_STATUSES = _ssot.CANONICAL_STATUSES
CANONICAL_STATUSES_LOWER = _ssot.CANONICAL_STATUSES_LOWER
PLANS_STATUSES_AI_SUMMARY_ENFORCED = _ssot.PLANS_STATUSES_AI_SUMMARY_ENFORCED
STALE_EQUIVALENTS = _ssot.STALE_EQUIVALENTS
FORBIDDEN_PLANS_STATUSES = _ssot.FORBIDDEN_PLANS_STATUSES
Violation = _ssot.Violation
WaitingForViolation = _ssot.WaitingForViolation
decide = _ssot.decide
check = _ssot.check
decide_waiting_for = _ssot.decide_waiting_for
decide_waiting_for_quality = _ssot.decide_waiting_for_quality

__all__ = [
    "PLANS_DB_ID",
    "PLANS_DATA_SOURCE_ID",
    "BACKLOG_DB_ID",
    "BACKLOG_DATA_SOURCE_ID",
    "CANONICAL_STATUSES",
    "CANONICAL_STATUSES_LOWER",
    "PLANS_STATUSES_AI_SUMMARY_ENFORCED",
    "STALE_EQUIVALENTS",
    "FORBIDDEN_PLANS_STATUSES",
    "Violation",
    "WaitingForViolation",
    "decide",
    "check",
    "decide_waiting_for",
    "decide_waiting_for_quality",
]
