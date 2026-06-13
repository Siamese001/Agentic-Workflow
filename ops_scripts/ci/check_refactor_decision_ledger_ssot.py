#!/usr/bin/env python3
"""
check_refactor_decision_ledger_ssot.py — W2 ledger SSOT enforcement.

Part A — Forbidden writes: Python sources must not construct the legacy
``.claude/state/refactor_decisions`` path tuple (writers must use
``tools.refactor_decisions.ledger_paths`` and the Cursor SSOT).

Part B — Mirror drift (informational by default): if both SQLite files exist,
report decision row-count delta. Set LEDGER_SSOT_DRIFT_FAIL_CLOSED=1 to fail when
counts differ (use after mirror is meant to be synced or retired).

Exit codes:
  0 — no forbidden patterns; drift OK or advisory only
  1 — forbidden legacy path construction found, or drift fail-closed
  2 — script error

Bypass: REFACTOR_LEDGER_SSOT_BYPASS=1 logs and exits 0.

Constitutional: UTF-8 stdio, specific exceptions only where needed.
"""

from __future__ import annotations

import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.refactor_decisions.ledger_paths import (  # noqa: E402
    REFACTOR_DECISION_LEDGER_DB,
    REFACTOR_DECISION_LEDGER_DB_WINDSURF_LEGACY,
)

BYPASS_LOG = REPO_ROOT / "artifacts" / "governance" / "refactor_ledger_ssot_bypass.jsonl"
DRIFT_LOG = REPO_ROOT / "artifacts" / "governance" / "refactor_ledger_ssot_drift.jsonl"

# Tuple-style paths copy-pasted into writers before W2 (forbid reintroduction).
_FORBIDDEN_TOKENS = (
    '"docs/archive/windsurf/legacy-tree" / "state" / "refactor_decisions"',
    "'docs/archive/windsurf/legacy-tree' / 'state' / 'refactor_decisions'",
)

_ALLOWLIST_FILES = frozenset(
    {
        "tools/governance_legacy/migrate_refactor_decision_ledger.py",
        "tools/refactor_decisions/ledger_paths.py",
        "ops_scripts/ci/check_notion_decision_parity.py",
        "ops_scripts/ci/check_refactor_decision_ledger_ssot.py",
    }
)

_ALLOWLIST_DIR_PREFIXES = (
    "tests/",
    "docs/",
)


def _log(path: Path, payload: dict) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(
                json.dumps(
                    {
                        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                        **payload,
                    }
                )
                + "\n"
            )
    except OSError:
        pass


def _is_allowlisted(rel_posix: str) -> bool:
    if rel_posix.startswith(_ALLOWLIST_DIR_PREFIXES):
        return True
    return rel_posix in _ALLOWLIST_FILES


def _scan_forbidden() -> list[str]:
    violations: list[str] = []
    for path in sorted(REPO_ROOT.rglob("*.py")):
        rel = path.relative_to(REPO_ROOT).as_posix()
        if "node_modules" in rel or ".venv" in rel:
            continue
        if _is_allowlisted(rel):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        for tok in _FORBIDDEN_TOKENS:
            if tok in text:
                violations.append(f"{rel}: contains forbidden legacy path tuple `{tok[:40]}...`")
                break
    return violations


def _count_decisions(db: Path) -> int | None:
    if not db.exists():
        return None
    try:
        conn = sqlite3.connect(str(db), timeout=5)
    except sqlite3.Error:
        return None
    try:
        row = conn.execute("SELECT COUNT(*) FROM decisions").fetchone()
        return int(row[0]) if row else 0
    except sqlite3.Error:
        return None
    finally:
        conn.close()


def main() -> int:
    if os.environ.get("REFACTOR_LEDGER_SSOT_BYPASS", "").strip() == "1":
        _log(BYPASS_LOG, {"reason": "env REFACTOR_LEDGER_SSOT_BYPASS=1"})
        print("[refactor_ledger_ssot] BYPASS — env set", file=sys.stderr)
        return 0

    violations = _scan_forbidden()
    if violations:
        print("[refactor_ledger_ssot] FAIL — forbidden legacy writer path tuple(s):", file=sys.stderr)
        for v in violations[:50]:
            print(f"  {v}", file=sys.stderr)
        if len(violations) > 50:
            print(f"  ... ({len(violations) - 50} more)", file=sys.stderr)
        return 1

    cur_n = _count_decisions(REFACTOR_DECISION_LEDGER_DB)
    leg_n = _count_decisions(REFACTOR_DECISION_LEDGER_DB_WINDSURF_LEGACY)
    drift_payload = {
        "cursor_decisions": cur_n,
        "legacy_mirror_decisions": leg_n,
        "drift": None if cur_n is None or leg_n is None else abs(cur_n - leg_n),
    }
    _log(DRIFT_LOG, drift_payload)

    if cur_n is not None and leg_n is not None and cur_n != leg_n:
        msg = (
            f"[refactor_ledger_ssot] INFO — mirror drift: cursor_decisions={cur_n} "
            f"legacy_mirror_decisions={leg_n} (delta={drift_payload['drift']})"
        )
        print(msg, file=sys.stderr)
        if os.environ.get("LEDGER_SSOT_DRIFT_FAIL_CLOSED", "").strip() in ("1", "true", "yes"):
            print(
                "[refactor_ledger_ssot] FAIL — LEDGER_SSOT_DRIFT_FAIL_CLOSED=1 and counts differ",
                file=sys.stderr,
            )
            return 1
    else:
        print(
            "[refactor_ledger_ssot] PASS — no forbidden legacy writer tuples; "
            f"drift snapshot cursor={cur_n} legacy={leg_n}",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
