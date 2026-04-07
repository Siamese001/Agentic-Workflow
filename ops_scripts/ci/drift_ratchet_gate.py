"""
ADG Drift Ratchet Gate — Pre-commit / CI Layer 1
=================================================
Fails if the drift composite score has regressed from the stored baseline.

Baseline stored in Redis: adg:drift:baseline (STRING, no TTL — persistent).
Baseline JSON schema:
  {"score": 0.749062, "uncovered_modules": [...], "timestamp": 1773446651.66}

Exit codes:
  0 — score did not regress (or first run — baseline written)
  1 — score regressed or highest-blast module newly uncovered
  2 — drift keys stale / missing and rescore also failed

Usage:
    python ops_scripts/ci/drift_ratchet_gate.py           # check mode
    python ops_scripts/ci/drift_ratchet_gate.py --promote # force-write new baseline

Pre-commit hook entry in .pre-commit-config.yaml:
    - id: drift-ratchet
      name: T3g: Drift Score Ratchet
      entry: python ops_scripts/ci/drift_ratchet_gate.py
      language: system
      pass_filenames: false
      always_run: true
"""

from __future__ import annotations

import argparse
import json
import logging
import subprocess
import sys
import time
from pathlib import Path

import redis

logger = logging.getLogger(__name__)

REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0
STALE_HOURS = 2.0
EPSILON = 0.005  # allow tiny float noise before flagging regression
RESCORE_TIMEOUT_S = 180
PROJECT_ROOT = Path(__file__).resolve().parents[2]
BASELINE_KEY = "adg:drift:baseline"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _connect() -> redis.Redis:
    return redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)


def _rescore() -> bool:
    """Re-run drift_score.py synchronously. Return True on success."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "tools.adg.drift_score"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=RESCORE_TIMEOUT_S,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, OSError) as exc:    # guardian: Add error context logging
        logger.error("[drift-ratchet] rescore failed: %s", exc)
        return False


def _read_current(r: redis.Redis) -> tuple[float, list[str], list[dict], float] | None:
    """
    Read current drift state from Redis.

    Returns (composite_score, uncovered_list, blast_top, timestamp)
    or None if keys are missing.
    """
    score_raw = r.get("adg:drift:score")
    if score_raw is None:
        return None
    subscores = r.hgetall("adg:drift:subscores")
    ts = float(subscores.get("timestamp", 0))
    uncovered = r.lrange("adg:drift:uncovered", 0, -1)
    blast_raw = r.lrange("adg:drift:blast_top", 0, 0)  # just the top entry
    blast_top: list[dict] = []
    for x in blast_raw:
        try:
            blast_top.append(json.loads(x))
        except json.JSONDecodeError:
            pass
    return float(score_raw), list(uncovered), blast_top, ts


def _read_baseline(r: redis.Redis) -> dict | None:
    """Return parsed baseline dict or None if not set."""
    raw = r.get(BASELINE_KEY)
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def _write_baseline(r: redis.Redis, score: float, uncovered: list[str]) -> None:
    """Persist new baseline (no TTL — intentionally permanent until promoted)."""
    baseline = {
        "score": round(score, 6),
        "uncovered_modules": sorted(uncovered),
        "timestamp": time.time(),
    }
    r.set(BASELINE_KEY, json.dumps(baseline))
    logger.info("[drift-ratchet] baseline written: score=%.4f", score)


# ---------------------------------------------------------------------------
# Core check
# ---------------------------------------------------------------------------


def check(promote: bool = False) -> int:
    """
    Run the ratchet check.

    Args:
        promote: If True, unconditionally write the current score as the new baseline.

    Returns:
        Exit code (0=pass, 1=fail, 2=error).
    """
    try:
        r = _connect()
        r.ping()
    except redis.RedisError as exc:
        print(f"[drift-ratchet] ERROR: cannot connect to Redis: {exc}")
        return 2

    # Read current drift state
    state = _read_current(r)

    if state is None:
        print("[drift-ratchet] adg:drift:score not found — rescoring ...")
        ok = _rescore()
        if not ok:
            print("[drift-ratchet] ERROR: rescore failed, cannot check drift")
            return 2
        state = _read_current(r)
        if state is None:
            print("[drift-ratchet] ERROR: score still missing after rescore")
            return 2

    current_score, uncovered, blast_top, ts = state
    age_hours = (time.time() - ts) / 3600

    # Stale check: rescore if older than threshold
    if age_hours > STALE_HOURS:
        print(f"[drift-ratchet] score is {age_hours:.1f}h old (threshold={STALE_HOURS}h) — rescoring ...")
        ok = _rescore()
        if ok:
            state = _read_current(r)
            if state:
                current_score, uncovered, blast_top, ts = state
        else:
            print("[drift-ratchet] WARNING: rescore failed, using stale score")

    # Promote mode: force-write baseline and exit
    if promote:
        _write_baseline(r, current_score, uncovered)
        print(f"[drift-ratchet] PROMOTED baseline: score={current_score:.4f}")
        return 0

    # First run: write baseline and pass
    baseline = _read_baseline(r)
    if baseline is None:
        print(f"[drift-ratchet] no baseline found — writing current as baseline (score={current_score:.4f})")
        _write_baseline(r, current_score, uncovered)
        return 0

    prior_score = baseline["score"]
    prior_uncovered = set(baseline.get("uncovered_modules", []))
    new_uncovered = set(uncovered)

    # Ratchet rule 1: composite score must not increase beyond epsilon
    if current_score > prior_score + EPSILON:
        delta = current_score - prior_score
        new_modules = sorted(new_uncovered - prior_uncovered)
        print(f"[drift-ratchet] FAIL: score regressed {prior_score:.4f} → {current_score:.4f} (+{delta:.4f})")
        if new_modules:
            print(f"[drift-ratchet] Newly uncovered modules ({len(new_modules)}):")
            for m in new_modules[:10]:
                print(f"  NEW UNCOVERED: {m}")
            if len(new_modules) > 10:
                print(f"  ... and {len(new_modules) - 10} more")
        print("[drift-ratchet] Fix: add tests that create `covers` edges for the listed modules,")
        print("[drift-ratchet]      then re-run: python -m tools.adg.adg_redis_ingest --force")
        return 1

    # Ratchet rule 2: highest-blast module must not be newly uncovered
    if blast_top:
        top_path = blast_top[0].get("path", "")
        if top_path and top_path in (new_uncovered - prior_uncovered):
            print(f"[drift-ratchet] FAIL: highest blast module newly uncovered: {blast_top[0]}")
            return 1

    # Pass — update baseline if score improved beyond epsilon
    if current_score < prior_score - EPSILON:
        _write_baseline(r, current_score, uncovered)
        print(f"[drift-ratchet] baseline improved: {prior_score:.4f} → {current_score:.4f}")
    else:
        print(f"[drift-ratchet] PASS: score={current_score:.4f} (baseline={prior_score:.4f})")

    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description="ADG drift ratchet gate")
    parser.add_argument(
        "--promote",
        action="store_true",
        help="Force-write current score as the new baseline",
    )
    args = parser.parse_args()
    sys.exit(check(promote=args.promote))


if __name__ == "__main__":
    main()
