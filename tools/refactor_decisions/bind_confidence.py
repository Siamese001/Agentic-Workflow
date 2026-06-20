"""Bind-confidence classification for Author-Gate outcome binding (plan W1).

Tiers: high, medium, low, disputed — see `.codex/plans/author-gate-learning-harden-f4e8a2.md`.
Pure helpers (no I/O) except optional JSON file parse for CI receipts.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# CI receipt payload completeness
CI_FULL = "full"
CI_PARTIAL = "partial"
CI_ABSENT = "absent"

BIND_HIGH = "high"
BIND_MEDIUM = "medium"
BIND_LOW = "low"
BIND_DISPUTED = "disputed"


@dataclass(frozen=True)
class BindConfidenceInput:
    """Inputs for tiering (all optional fields have safe defaults)."""

    scope_files: frozenset[str]
    commit_files: frozenset[str]
    decision_created_at_iso: str
    commit_timestamp_iso: str
    binding_window_seconds: int
    ci_receipt_status: str
    direct_sha_bind: bool
    overlapping_commit_count: int
    operator_disputed: bool = False


def default_binding_window_seconds() -> int:
    raw = os.environ.get("AG_BIND_WINDOW_SECONDS", "").strip()
    if raw.isdigit():
        return max(60, int(raw))
    return 1209600  # 14 days


def parse_ci_receipt(path: Path | None) -> tuple[str, dict[str, Any]]:
    """Read CI receipt JSON; return (ci_receipt_status, meta).

    Expected shape (flexible):
      - ``complete`: true + ``conclusion`` or ``status`` -> full
      - ``complete``: false or missing fields -> partial
      - missing file -> absent
    """
    if path is None or not path.is_file():
        return CI_ABSENT, {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, json.JSONDecodeError):
        return CI_PARTIAL, {"error": "unreadable_json"}
    if not isinstance(data, dict):
        return CI_PARTIAL, {}
    complete = data.get("complete")
    if complete is True:
        return CI_FULL, data
    if complete is False:
        return CI_PARTIAL, data
    # Heuristic: presence of conclusion/status implies a full receipt
    if data.get("conclusion") is not None or data.get("status") is not None:
        return CI_FULL, data
    return CI_PARTIAL, data


def _parse_iso(ts: str) -> datetime | None:
    if not ts or not isinstance(ts, str):
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return None


def commit_within_binding_window(
    decision_created_at_iso: str,
    commit_timestamp_iso: str,
    window_seconds: int,
) -> bool:
    """True iff commit is strictly after decision and within ``window_seconds``."""
    dec_dt = _parse_iso(decision_created_at_iso)
    com_dt = _parse_iso(commit_timestamp_iso)
    if dec_dt is None or com_dt is None:
        return False
    delta = (com_dt - dec_dt).total_seconds()
    if delta < 0:
        return False
    return delta <= float(window_seconds)


def meaningful_file_overlap(scope_files: frozenset[str], commit_files: frozenset[str]) -> bool:
    """Non-empty normalized path overlap."""
    if not scope_files or not commit_files:
        return False
    sa = {p.replace("\\", "/") for p in scope_files}
    sb = {p.replace("\\", "/") for p in commit_files}
    return bool(sa & sb)


def classify_bind_confidence(inp: BindConfidenceInput) -> tuple[str, str]:
    """Return (bind_confidence_tier, ci_receipt_status echo)."""
    ci = inp.ci_receipt_status
    if inp.operator_disputed:
        return BIND_DISPUTED, ci

    in_window = commit_within_binding_window(
        inp.decision_created_at_iso,
        inp.commit_timestamp_iso,
        inp.binding_window_seconds,
    )
    overlap = meaningful_file_overlap(inp.scope_files, inp.commit_files)

    ambiguous = inp.overlapping_commit_count > 1

    # Weak overlap / no overlap when we expected scope: downgrade
    if not inp.direct_sha_bind and inp.scope_files and not overlap:
        return BIND_LOW, ci
    if inp.direct_sha_bind and inp.scope_files and not overlap:
        return BIND_LOW, ci

    if ambiguous or not in_window:
        return BIND_LOW, ci

    if overlap and in_window and not ambiguous and ci == CI_FULL:
        return BIND_HIGH, ci
    if overlap and in_window and not ambiguous and ci in (CI_ABSENT, CI_PARTIAL):
        return BIND_MEDIUM, ci

    return BIND_LOW, ci


def dispute_id_set_from_env() -> frozenset[str]:
    """Parse AG_BIND_DISPUTE_DECISION_IDS=comma,separated."""
    raw = os.environ.get("AG_BIND_DISPUTE_DECISION_IDS", "").strip()
    if not raw:
        return frozenset()
    return frozenset(x.strip() for x in raw.split(",") if x.strip())


def ci_receipt_path_from_env() -> Path | None:
    p = os.environ.get("AG_BIND_CI_RECEIPT_PATH", "").strip()
    return Path(p) if p else None


def refine_outcome_label_with_ci(
    label: str,
    flags: dict[str, int],
    ci_receipt_status: str,
    ci_meta: dict[str, Any],
) -> tuple[str, dict[str, int]]:
    """If CI receipt is *full*, let conclusion override ``undecided`` / success signal."""
    if ci_receipt_status != CI_FULL:
        return label, flags
    conclusion = str(ci_meta.get("conclusion") or ci_meta.get("status") or "").lower()
    out_flags = dict(flags)
    if conclusion in ("failure", "failed", "fail"):
        out_flags["regression_found"] = 1
        out_flags["tests_passed"] = 0
        return "rework", out_flags
    if conclusion in ("success", "passed", "pass", "ok"):
        out_flags["tests_passed"] = 1
        if label == "undecided":
            return "success", out_flags
    return label, out_flags
