#!/usr/bin/env python3
"""W5: follow-on closeout compiler + honest release claims."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from apps_rg.fact_inventory.graph_skills_deferred_followup_closeout import build_followup_closeout

REPORTS = REPO / "docs" / "reports" / "apps_rg"
OUT = REPORTS / "graph_skills_deferred_followup_closeout.json"


def _git_commit() -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO,
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        )
        return out.stdout.strip()
    except (subprocess.SubprocessError, OSError):
        return "unknown"


def main() -> int:
    REPORTS.mkdir(parents=True, exist_ok=True)
    doc = build_followup_closeout(REPO, git_commit=_git_commit())
    OUT.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": doc.get("status"), "claims_release_eligible": doc.get("claims_release_eligible")}, indent=2))
    return 0 if doc.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
