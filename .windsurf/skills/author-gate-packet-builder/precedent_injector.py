#!/usr/bin/env python3
"""
precedent_injector.py — Thin wrapper around lookup_refactor_decisions.py.

Invoked by emit_packet.py and usable standalone. Given a decision_type + intent,
returns a precedent verdict block suitable for embedding in an AUTHOR_GATE_PACKET.

STDIN (JSON):
    {
        "decision_type": "refactor_scope",
        "normalized_intent": "Extract L2 adapter",
        "repo_area": "agentic_core/L2_execution",
        "limit": 3
    }

STDOUT (JSON):
    {
        "verdict": "strong" | "suggestive" | "none",
        "matched_ids": ["dec_..."],
        "summary": "Prior decision (YYYY-MM-DD): <selected_option_id> — <outcome_label>",
        "raw": { ... full lookup output ... }
    }

CONSTITUTIONAL
    - subprocess.run with argv, shell=False, timeout=20
    - UTF-8 stdio
    - Specific exceptions: subprocess.TimeoutExpired, OSError, json.JSONDecodeError
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
# Canonical lookup implementation (SSOT under .cursor/skills).
LOOKUP_SCRIPT = (
    REPO_ROOT / ".cursor" / "skills" / "refactor-decision-memory" / "lookup_refactor_decisions.py"
)


def _summarize(match: dict[str, Any]) -> str:
    created = (match.get("created_at") or "")[:10]
    selected = match.get("selected_option_id") or "(no selection)"
    outcome = "success" if match.get("tests_passed") else "inconclusive"
    if match.get("rollback_required"):
        outcome = "rolled back"
    return f"Prior decision ({created}): {selected} — {outcome}"


def inject(query: dict[str, Any]) -> dict[str, Any]:
    if not LOOKUP_SCRIPT.exists():
        return {"verdict": "none", "matched_ids": [], "summary": "lookup script missing", "raw": None}

    try:
        result = subprocess.run(
            [sys.executable, str(LOOKUP_SCRIPT)],
            input=json.dumps(query),
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            shell=False,
            timeout=20,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {"verdict": "none", "matched_ids": [], "summary": "lookup timed out", "raw": None}
    except OSError as exc:
        return {"verdict": "none", "matched_ids": [], "summary": f"lookup failed: {exc}", "raw": None}

    if result.returncode != 0:
        return {
            "verdict": "none",
            "matched_ids": [],
            "summary": f"lookup exit {result.returncode}: {result.stderr.strip()[:120]}",
            "raw": None,
        }

    try:
        raw = json.loads(result.stdout or "{}")
    except json.JSONDecodeError:
        return {"verdict": "none", "matched_ids": [], "summary": "lookup emitted invalid JSON", "raw": None}

    verdict = raw.get("verdict", "none")
    matches = raw.get("matches") or []
    matched_ids = [m.get("decision_id") for m in matches if m.get("decision_id")][:5]

    if not matches:
        summary = "no precedent found"
    else:
        summary = _summarize(matches[0])
        if len(matches) > 1:
            summary += f" (+{len(matches) - 1} more)"

    return {
        "verdict": verdict,
        "matched_ids": matched_ids,
        "summary": summary,
        "raw": raw,
    }


def main() -> int:
    try:
        query_raw = sys.stdin.read()
        query = json.loads(query_raw) if query_raw.strip() else {}
    except json.JSONDecodeError as exc:
        print(json.dumps({"verdict": "none", "summary": f"bad stdin JSON: {exc}"}), file=sys.stdout)
        return 1

    out = inject(query)
    json.dump(out, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
