"""Redis hot-cache ingest integration for ADG generation."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def _auto_ingest_to_redis(adg_dir: Path, sqlite_path: Path) -> None:
    """Automatically ingest the freshly-generated ADG into Redis hot cache."""
    import subprocess
    import time

    from agentic_core.config.redis_config import get_adg_cache_config

    config = get_adg_cache_config()
    ingest_script = ROOT / "tools" / "adg" / "adg_redis_ingest.py"
    if not ingest_script.exists():
        print(f"[ADG] Redis ingest skipped: script not found at {ingest_script}")
        return

    print("[ADG] Auto-ingesting to Redis hot cache...")
    start_time = time.time()
    # ruff: noqa: S603 - Python script is trusted, internal tool usage
    result = subprocess.run(
        [sys.executable, str(ingest_script), "--force"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=config.ingest_timeout,
        check=True,
    )
    print("[ADG] Redis ingest complete - ADG cache is HOT")
    lines = [line for line in result.stdout.strip().split("\n") if line.strip()]
    for line in lines[-3:]:
        print(f"      {line}")
