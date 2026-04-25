"""ADG MV/P-view Redis projection integration for ADG generation.

Runs AFTER `_auto_ingest_to_redis` so the nodes/edges cache is already hot
before we layer materialized-view and P-view projections on top.

Fail-soft: any failure logs a WARNING and returns — never blocks ADG generation.
"""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path


def _discover_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "agentic_core").exists() or (candidate / ".git").exists():
            return candidate
        if candidate.name == "tools" and (candidate / "generate").exists():
            return candidate.parent
    return start.parents[3] if len(start.parents) > 3 else start.parent


ROOT = _discover_repo_root(Path(__file__).resolve().parent)
DEFAULT_TIMEOUT_S = 30


def _auto_project_mvs_to_redis(sqlite_path: Path, timeout_s: int = DEFAULT_TIMEOUT_S) -> None:
    """Project freshly-generated ADG MVs + P-views into Redis (fail-soft)."""
    project_script = ROOT / "tools" / "adg" / "adg_mv_project.py"
    if not project_script.exists():
        print(f"[ADG] MV projection skipped: script not found at {project_script}")
        return

    if not sqlite_path.exists():
        print(f"[ADG] MV projection skipped: SQLite artifact not found at {sqlite_path}")
        return

    print(f"[ADG] Auto-projecting MVs + P-views from {sqlite_path.name}...")
    start_time = time.monotonic()
    try:
        # ruff: noqa: S603 - Python script is trusted, internal tool usage
        result = subprocess.run(
            [sys.executable, str(project_script), "--force", "--sqlite", str(sqlite_path)],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=max(timeout_s, 1),
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        stderr = (exc.stderr or "").strip()[:300]
        stdout = (exc.stdout or "").strip()[:300]
        print(f"[ADG] WARNING: MV projection failed (exit {exc.returncode})")
        if stdout:
            print(f"      stdout: {stdout}")
        if stderr:
            print(f"      stderr: {stderr}")
        return
    except subprocess.TimeoutExpired:
        elapsed = time.monotonic() - start_time
        print(f"[ADG] WARNING: MV projection timed out after {elapsed:.1f}s")
        return
    except FileNotFoundError:
        print("[ADG] WARNING: Python executable not found for MV projection; skipping")
        return
    except OSError as exc:
        print(f"[ADG] WARNING: MV projection could not start: {exc}")
        return

    elapsed = time.monotonic() - start_time
    print(f"[ADG] MV projection complete - MV cache is HOT ({elapsed:.1f}s)")
    lines = [line for line in result.stdout.strip().splitlines() if line.strip()]
    # Print the summary + first few per-view rows (bounded output).
    for line in lines[:8]:
        print(f"      {line}")
