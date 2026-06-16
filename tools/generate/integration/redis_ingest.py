"""Redis hot-cache ingest integration for ADG generation."""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path


def _discover_repo_root(start: Path) -> Path:
    """Best-effort repository root discovery for direct script and package execution."""
    for candidate in (start, *start.parents):
        if (candidate / "agentic_core").exists() or (candidate / ".git").exists():
            return candidate
        if candidate.name == "tools" and (candidate / "generate").exists():
            return candidate.parent
    return start.parents[3] if len(start.parents) > 3 else start.parent


ROOT = _discover_repo_root(Path(__file__).resolve().parent)


def _auto_ingest_to_redis(adg_dir: Path, sqlite_path: Path) -> None:
    """Automatically ingest the freshly-generated ADG into Redis hot cache."""
    from agentic_core.config.redis_config import get_adg_cache_config

    config = get_adg_cache_config()
    ingest_script = ROOT / "tools" / "adg" / "adg_redis_ingest.py"
    if not ingest_script.exists():
        print(f"[ADG] Redis ingest skipped: script not found at {ingest_script}")
        return

    if not sqlite_path.exists():
        print(f"[ADG] Redis ingest skipped: SQLite artifact not found at {sqlite_path}")
        return

    timeout_s = max(int(getattr(config, "ingest_timeout", 0) or 0), 1)
    print(f"[ADG] Auto-ingesting to Redis hot cache from {sqlite_path.name}...")
    start_time = time.monotonic()
    try:
        # ruff: noqa: S603 - Python script is trusted, internal tool usage
        result = subprocess.run(
            [sys.executable, str(ingest_script), "--force", "--sqlite", str(sqlite_path)],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=timeout_s,
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        stderr = (exc.stderr or "").strip()[:300]
        stdout = (exc.stdout or "").strip()[:300]
        print(f"[ADG] WARNING: Redis ingest failed (exit {exc.returncode})")
        if stdout:
            print(f"      stdout: {stdout}")
        if stderr:
            print(f"      stderr: {stderr}")
        return
    except subprocess.TimeoutExpired:
        elapsed = time.monotonic() - start_time
        print(f"[ADG] WARNING: Redis ingest timed out after {elapsed:.1f}s")
        return
    except FileNotFoundError:
        print("[ADG] WARNING: Python executable not found for Redis ingest; skipping")
        return
    except OSError as exc:
        print(f"[ADG] WARNING: Redis ingest could not start: {exc}")
        return

    elapsed = time.monotonic() - start_time
    print(f"[ADG] Redis ingest complete - ADG cache is HOT ({elapsed:.1f}s)")
    lines = [line for line in result.stdout.strip().splitlines() if line.strip()]
    for line in lines[-3:]:
        print(f"      {line}")
