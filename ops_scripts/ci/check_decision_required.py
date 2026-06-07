#!/usr/bin/env python3
"""
check_decision_required.py — W4.2 pre-commit gate.

If a commit touches paths on the Author-Gate trigger list (derived from
`.claude/schemas/author_gate_triggers.yaml`), require that a decision
row exists in the refactor_decision_ledger within --recent-hours AND
whose `normalized_intent` or `request_summary` overlaps the changed paths.

Intent: catch silent refactors that bypass the Author-Gate entirely.

Exit codes:
    0 — no trigger paths touched, or a matching decision exists
    1 — trigger paths touched, NO matching decision
    2 — script error

Bypass: DECISION_REQUIRED_BYPASS=1 (logged). Use for whitespace/comment-only
fixes where the Author-Gate is genuinely overkill.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LEDGER_DB = REPO_ROOT / ".claude" / "state" / "refactor_decisions" / "refactor_decision_ledger.sqlite"
TRIGGERS_YAML = REPO_ROOT / ".claude" / "schemas" / "author_gate_triggers.yaml"
VIOLATIONS_LOG = REPO_ROOT / "artifacts" / "governance" / "decision_required_violations.jsonl"
BYPASS_LOG = REPO_ROOT / "artifacts" / "governance" / "decision_required_bypass.jsonl"

# Fallback trigger paths if author_gate_triggers.yaml cannot be parsed.
# These are the narrow set we KNOW are always gate-class (harness infra).
_FALLBACK_TRIGGER_PATHS = (
    ".claude/governance/scripts/",
    ".claude/rules/",
    ".claude/skills/",
    "ops_scripts/ci/",
    "agentic_core/L5_safety/",
    "agentic_core/L0_routing/",
)


def _log(path: Path, payload: dict) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(
                json.dumps(
                    {
                        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                        **payload,
                    }
                )
                + "\n"
            )
    except OSError:
        # guardian: allow-silent-swallow -- log unwritable: non-fatal
        pass


def _staged_files() -> list[str]:
    try:
        r = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True,
            text=True,
            timeout=10,
            shell=False,
            cwd=str(REPO_ROOT),
            check=False,
        )
        if r.returncode != 0:
            return []
        return [ln.strip() for ln in r.stdout.splitlines() if ln.strip()]
    except (subprocess.TimeoutExpired, OSError):
        return []


def _load_trigger_paths() -> tuple[str, ...]:
    """Extract trigger path prefixes from the YAML, or fall back to defaults."""
    if not TRIGGERS_YAML.exists():
        return _FALLBACK_TRIGGER_PATHS
    try:
        text = TRIGGERS_YAML.read_text(encoding="utf-8")
    except OSError:
        return _FALLBACK_TRIGGER_PATHS
    # Heuristic: pull any lines mentioning path prefixes ending in '/'
    paths: list[str] = []
    for m in re.finditer(r"[\"']([\w./_-]+/)[\"']", text):
        paths.append(m.group(1))
    if not paths:
        return _FALLBACK_TRIGGER_PATHS
    return tuple(sorted(set(paths)))


def _find_matching_decisions(conn: sqlite3.Connection, files: list[str], since_iso: str) -> list[dict]:
    """Return decisions whose intent/summary overlaps any changed file path."""
    try:
        rows = list(
            conn.execute(
                "SELECT decision_id, created_at, decision_type, normalized_intent, "
                "request_summary, selected_option_id FROM decisions WHERE created_at >= ?",
                (since_iso,),
            )
        )
    except sqlite3.Error:
        return []
    matches: list[dict] = []
    for r in rows:
        decision_id, created_at, dtype, intent, summary, selected = r
        blob = f"{intent or ''} {summary or ''}".lower()
        for f in files:
            fp = f.lower()
            # Match by directory prefix or basename token
            if fp in blob:
                matches.append(
                    {
                        "decision_id": decision_id,
                        "created_at": created_at,
                        "decision_type": dtype,
                        "matched_file": f,
                    }
                )
                break
            # Also try directory prefix (2 segments)
            segs = fp.split("/", 2)
            if len(segs) >= 2:
                prefix = "/".join(segs[:2])
                if prefix in blob:
                    matches.append(
                        {
                            "decision_id": decision_id,
                            "created_at": created_at,
                            "decision_type": dtype,
                            "matched_file": f,
                        }
                    )
                    break
    return matches


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Require Author-Gate decision for commits touching trigger paths (W4.2)"
    )
    ap.add_argument("--recent-hours", type=int, default=24)
    args = ap.parse_args()

    if os.environ.get("DECISION_REQUIRED_BYPASS") == "1":
        _log(BYPASS_LOG, {"reason": "env"})
        print("[check_decision_required] BYPASS (env). Logged.", file=sys.stderr)
        return 0

    files = _staged_files()
    if not files:
        print("[check_decision_required] OK — no staged files", file=sys.stderr)
        return 0

    trigger_paths = _load_trigger_paths()
    touched = [f for f in files if any(f.startswith(p) for p in trigger_paths)]
    if not touched:
        print(
            f"[check_decision_required] OK — {len(files)} file(s) staged; none on trigger paths",
            file=sys.stderr,
        )
        return 0

    print(f"[check_decision_required] {len(touched)} trigger-path file(s) staged:", file=sys.stderr)
    for f in touched[:10]:
        print(f"  {f}", file=sys.stderr)

    if not LEDGER_DB.exists():
        print(
            f"[check_decision_required] FAIL — trigger paths touched but ledger not present at {LEDGER_DB}",
            file=sys.stderr,
        )
        _log(VIOLATIONS_LOG, {"reason": "ledger_missing", "touched": touched})
        return 1

    since = (datetime.now(timezone.utc) - timedelta(hours=args.recent_hours)).isoformat(timespec="seconds")

    try:
        conn = sqlite3.connect(f"file:{LEDGER_DB}?mode=ro", uri=True, timeout=5)
    except sqlite3.Error as exc:
        print(f"[check_decision_required] script error: {exc}", file=sys.stderr)
        return 2

    try:
        matches = _find_matching_decisions(conn, touched, since)
    finally:
        conn.close()

    if not matches:
        print(
            f"[check_decision_required] FAIL — trigger paths touched but no "
            f"matching decision in last {args.recent_hours}h. Stage your "
            f"DECISION_CAPTURED marker or set DECISION_REQUIRED_BYPASS=1 with "
            f"justification.",
            file=sys.stderr,
        )
        _log(
            VIOLATIONS_LOG,
            {
                "reason": "no_matching_decision",
                "touched_files": touched[:50],
                "recent_hours": args.recent_hours,
            },
        )
        return 1

    print(f"[check_decision_required] PASS — {len(matches)} matching decision(s) found", file=sys.stderr)
    for m in matches[:5]:
        print(f"  {m['decision_id']}  {m['decision_type']}  matched={m['matched_file']}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (sqlite3.Error, OSError) as exc:
        print(f"[check_decision_required] script error: {exc}", file=sys.stderr)
        sys.exit(2)
