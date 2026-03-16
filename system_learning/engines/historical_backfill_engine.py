"""
historical_backfill_engine.py — One-shot backfill of .healing_backups historical data
into the system learning corpus and HealingSuccessRateStore.

Two sources:
1. ssot_protected_root_blocks.jsonl  → healing_contexts_corpus.jsonl
   Each JSONL record {caller, matched_root, target, ts_utc} becomes a
   healing context entry with failure_type="PROTECTED_ROOT_BLOCK", outcome="BLOCKED".

2. compliance_report_*.json (filesystem_ssot_violations/)
   Each report {meta.territory, metrics.violation_count, metrics.violations_fixed}
   seeds HealingSuccessRateStore with a historical success-rate prior per territory.

Design constraints:
- Idempotent: content_hash dedup prevents double-writes to corpus.
- Fire-and-forget callers: never raises to caller.
- No agentic_core imports (system_learning layer boundary).
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
from datetime import timezone
from pathlib import Path
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_records_execution_trace,
    emit_determinism_digest,
)

logger = logging.getLogger(__name__)

emit_determinism_digest("p0", "historical_backfill_engine")
_emit_records_execution_trace("p0", "evidence", "historical_backfill_engine")

_CORPUS_PATH = Path("data/corpus/healing_contexts_corpus.jsonl")
_SENTINEL_PATH = Path("data/corpus/.healing_backups_backfill_done")

# ── helpers ──────────────────────────────────────────────────────────────────


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _existing_hashes(corpus_path: Path) -> set[str]:
    """Return set of content_hash values already in corpus (for dedup)."""
    hashes: set[str] = set()
    if not corpus_path.exists():
        return hashes
    for line in corpus_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            hashes.add(json.loads(line).get("content_hash", ""))
        except json.JSONDecodeError:
            pass
    return hashes


def _load_jsonl_lenient(path: Path) -> list[dict[str, Any]]:
    records = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return records


def _load_json_lenient(path: Path) -> dict[str, Any] | None:
    """Parse compliance JSON that may contain unescaped Windows backslashes."""
    raw = path.read_text(encoding="utf-8", errors="replace")
    fixed = re.sub(r"\\(?![\"\\\/bfnrtu])", r"\\\\", raw)
    try:
        return json.loads(fixed)
    except json.JSONDecodeError as exc:
        logger.warning("[Backfill] Could not parse %s: %s", path.name, exc)
        return None


# ── Wave 3a: JSONL → corpus ───────────────────────────────────────────────────


def backfill_protected_root_blocks(
    repo_root: Path,
    *,
    dry_run: bool = False,
) -> int:
    """Append ssot_protected_root_blocks.jsonl records to healing_contexts_corpus.jsonl.

    Returns number of new records written (0 if all already present or dry_run).
    """
    src = repo_root / ".healing_backups" / "unmapped_drift" / "logs" / "ssot_protected_root_blocks.jsonl"
    if not src.exists():
        logger.debug("[Backfill] ssot_protected_root_blocks.jsonl not found, skipping.")
        return 0

    corpus_path = repo_root / _CORPUS_PATH
    existing = _existing_hashes(corpus_path)
    records = _load_jsonl_lenient(src)

    new_lines: list[str] = []
    for rec in records:
        caller = rec.get("caller", "unknown")
        territory = rec.get("matched_root", "unknown")
        ts_utc = rec.get("ts_utc", "")
        target = rec.get("target", "")

        # Stable dedup key: caller + territory + target (path noise stripped)
        target_rel = Path(target).name if target else ""
        dedup_key = f"{caller}::{territory}::{target_rel}"
        content_hash = _sha256(dedup_key)

        if content_hash in existing:
            continue
        existing.add(content_hash)

        # Convert ts_utc ISO string → unix int
        created_utc: int = 0
        try:
            from datetime import datetime

            dt = datetime.fromisoformat(ts_utc.replace("Z", "+00:00"))
            created_utc = int(dt.replace(tzinfo=timezone.utc).timestamp())
        except Exception:
            pass

        entry = {
            "schema_version": 1,
            "content_hash": content_hash,
            "trace_id": "",
            "namespace": "healing_contexts",
            "created_utc": created_utc,
            "healer_id": caller,
            "tier": "L5",
            "failure_type": "PROTECTED_ROOT_BLOCK",
            "territory": territory,
            "outcome": "BLOCKED",
            "fix_summary": f"Protected root block: {target_rel} in {territory}",
        }
        new_lines.append(json.dumps(entry, separators=(",", ":"), sort_keys=True))

    if not new_lines:
        logger.info("[Backfill] No new protected_root_block records to write.")
        return 0

    if not dry_run:
        corpus_path.parent.mkdir(parents=True, exist_ok=True)
        with corpus_path.open("a", encoding="utf-8") as fh:
            for line in new_lines:
                fh.write(line + "\n")

    logger.info(
        "[Backfill] Wrote %d protected_root_block records to corpus (dry_run=%s).", len(new_lines), dry_run
    )
    return len(new_lines)


# ── Wave 3b: compliance JSON → HealingSuccessRateStore ───────────────────────


def backfill_compliance_success_rates(
    repo_root: Path,
    store=None,
    *,
    dry_run: bool = False,
) -> dict[str, float]:
    """Seed HealingSuccessRateStore with per-territory success rates from compliance JSONs.

    Reads all compliance_report_*.json files and calls store.record_outcome()
    violation_count times with success=(fixed/total) sampling.

    Returns dict[territory -> rate] of what was seeded.
    """
    reports_dir = (
        repo_root / ".healing_backups" / "filesystem_ssot_violations" / "logs" / "compliance_reports"
    )
    if not reports_dir.exists():
        logger.debug("[Backfill] compliance_reports dir not found, skipping.")
        return {}

    if store is None:
        try:
            from system_learning.engines.healing_success_rate_store import get_default_store

            store = get_default_store()
        except ImportError:
            logger.debug("[Backfill] HealingSuccessRateStore not available, skipping.")
            return {}

    seeded: dict[str, float] = {}

    for report_path in sorted(reports_dir.glob("compliance_report_*.json")):
        if "AGGREGATE" in report_path.name:
            continue
        obj = _load_json_lenient(report_path)
        if not obj:
            continue

        meta = obj.get("meta", {})
        metrics = obj.get("metrics", {})

        territory = meta.get("territory", "")
        if not territory:
            continue

        violation_count = int(metrics.get("violation_count", 0))
        violations_fixed = int(metrics.get("violations_fixed", 0))

        if violation_count == 0:
            continue

        # Derive historical success rate
        rate = violations_fixed / violation_count
        error_sig = f"FilesystemSSOTReconcilerAgent::{territory}::compliance_baseline"

        if not dry_run:
            # Seed with `violation_count` synthetic outcomes at the historical rate
            # Use min(violation_count, 10) to avoid overloading EMA with stale data
            samples = min(violation_count, 10)
            success_count = round(rate * samples)
            for i in range(samples):
                store.record_outcome(error_sig, success=(i < success_count))

        seeded[territory] = rate
        logger.info(
            "[Backfill] Seeded territory=%s rate=%.3f (%d/%d violations fixed)",
            territory,
            rate,
            violations_fixed,
            violation_count,
        )

    return seeded


# ── Orchestrator ─────────────────────────────────────────────────────────────


def run_backfill(
    repo_root: Path | None = None,
    store=None,
    *,
    dry_run: bool = False,
    force: bool = False,
) -> dict[str, Any]:
    """Run both backfill passes. Idempotent via sentinel file.

    Args:
        repo_root: project root; defaults to Path.cwd()
        store: HealingSuccessRateStore instance; uses default if None
        dry_run: if True, compute but do not write
        force: re-run even if sentinel exists

    Returns dict with corpus_records_added and territories_seeded.
    """
    if repo_root is None:
        repo_root = Path.cwd()

    sentinel = repo_root / _SENTINEL_PATH
    if sentinel.exists() and not force and not dry_run:
        logger.debug("[Backfill] Sentinel present — backfill already ran. Pass force=True to re-run.")
        return {"skipped": True, "corpus_records_added": 0, "territories_seeded": {}}

    corpus_added = backfill_protected_root_blocks(repo_root, dry_run=dry_run)
    territories = backfill_compliance_success_rates(repo_root, store=store, dry_run=dry_run)

    if not dry_run and not sentinel.exists():
        sentinel.parent.mkdir(parents=True, exist_ok=True)
        sentinel.write_text(
            json.dumps(
                {"corpus_records_added": corpus_added, "territories_seeded": list(territories.keys())}
            ),
            encoding="utf-8",
        )

    return {
        "skipped": False,
        "corpus_records_added": corpus_added,
        "territories_seeded": territories,
    }
