#!/usr/bin/env python3
"""KPI K1 — churn × complexity dashboard (plan W6.3, CodeScene formula).

Per-file hotspot score = ``git_change_count × cyclomatic_complexity``.
Git churn is computed from ``git log --numstat`` over a rolling
window (default 90 days); complexity is AST-based (same engine as
Q2).

Tier: K (KPI, never CI-blocking). Emits a summary row per run to
``artifacts/cursor/kpi_churn_complexity.jsonl`` for trending.
"""

from __future__ import annotations

import ast
import json
import os
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from tqdm import tqdm

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ops_scripts.ci._adg_wiring_gate_base import (  # noqa: E402
    LOG_DIR,
    Violation,
    WiringGate,
    cli_exit,
)

WINDOW_DAYS = 90
TOP_N = 30
KPI_SINK = LOG_DIR / "kpi_churn_complexity.jsonl"

PRODUCTION_ROOTS = (
    "agentic_core/",
    "apps_eval/",
    "apps_exec/",
    "apps_lic/",
    "apps_research/",
    "apps_rfp/",
    "apps_rg/",
    "apps_shared/",
    "apps_underwriting_ai/",
    "system_learning/",
    "infrastructure/",
)


def _git_churn(window_days: int) -> dict[str, int]:
    """Return {rel_path: commit_count} over the last ``window_days``."""
    since = f"{window_days}.days.ago"
    try:
        out = subprocess.run(
            ["git", "log", f"--since={since}", "--name-only", "--pretty=format:"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
            timeout=60,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return {}
    counts: dict[str, int] = {}
    for line in out.stdout.splitlines():
        line = line.strip().replace("\\", "/")
        if not line or not line.endswith(".py"):
            continue
        if not line.startswith(PRODUCTION_ROOTS):
            continue
        counts[line] = counts.get(line, 0) + 1
    return counts


def _complexity_of(path: Path) -> int:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except (OSError, SyntaxError):
        return 0
    score = 0
    for node in ast.walk(tree):
        if isinstance(
            node,
            (ast.If, ast.For, ast.AsyncFor, ast.While, ast.Try, ast.With, ast.AsyncWith, ast.ExceptHandler),
        ):
            score += 1
        elif isinstance(node, ast.BoolOp):
            score += max(0, len(node.values) - 1)
        elif isinstance(node, ast.IfExp):
            score += 1
    return score


class ChurnComplexityKpiGate(WiringGate):
    gate_id = "K1_churn_complexity_kpi"
    tier = "K"

    def run(self, _conn: sqlite3.Connection) -> list[Violation]:
        churn = _git_churn(WINDOW_DAYS)
        scores: list[tuple[str, int, int, int]] = []
        for rel, change_count in tqdm(list(churn.items()), desc="K1_churn_cx", unit="file"):
            py = REPO_ROOT / rel
            if not py.exists():
                continue
            cx = _complexity_of(py)
            if cx == 0:
                continue
            scores.append((rel, change_count, cx, change_count * cx))
        scores.sort(key=lambda t: t[3], reverse=True)
        top = scores[:TOP_N]

        # Emit KPI row to sink.
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        with KPI_SINK.open("a", encoding="utf-8") as fh:
            fh.write(
                json.dumps(
                    {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "window_days": WINDOW_DAYS,
                        "total_files_touched": len(churn),
                        "top_n": TOP_N,
                        "top_files": [
                            {"path": p, "commits": c, "complexity": cx, "score": s} for p, c, cx, s in top
                        ],
                    }
                )
                + "\n"
            )
        return []  # K-tier: never blocks


def main() -> int:
    _ = os.environ.get("GIT_AUTHOR", "")  # noqa: F841  (keep env explicit)
    return cli_exit(ChurnComplexityKpiGate().execute())


if __name__ == "__main__":
    sys.exit(main())
