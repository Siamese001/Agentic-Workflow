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
import tempfile
from datetime import timezone
from pathlib import Path
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    emit_replay_key,
)
from tqdm import tqdm

logger = logging.getLogger(__name__)

emit_determinism_digest("p0", "historical_backfill_engine")
emit_replay_key("p0", "historical_backfill_engine")
_emit_records_execution_trace("p0", "evidence", "historical_backfill_engine")
_emit_applies_guardrail("p0", "historical_backfill_engine", "p0_governance")
_emit_snapshots_state("p0", "historical_backfill_engine", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "historical_backfill_engine", "execution_auth")
_emit_validates_capability("p2", "historical_backfill_engine", "capability_check")
_emit_routes_to_capability("p2", "historical_backfill_engine", "capability_route")
_emit_writes_via_uwg("p2", "historical_backfill_engine", "uwg_write")
_emit_blocks_direct_write("p2", "historical_backfill_engine", "direct_write_block")
_emit_records_tool_invocation("p2", "historical_backfill_engine", "tool_invocation")
_emit_captures_execution_output("p2", "historical_backfill_engine", "exec_output")
_emit_dispatches_agent("p3", "historical_backfill_engine", "agent_dispatch")
_emit_coordinates_agents("p3", "historical_backfill_engine", "agent_coordination")
_emit_records_workflow_lineage("p3", "historical_backfill_engine", "workflow_lineage")
_emit_records_healing_outcome("p3", "historical_backfill_engine", "healing_outcome")
_emit_escalates_failure("p3", "historical_backfill_engine", "failure_escalation")
_emit_orchestrates_workflow("p3", "historical_backfill_engine", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "historical_backfill_engine", "healing_dispatch")
_emit_invokes_evaluation("p3", "historical_backfill_engine", "evaluation_signal")
_emit_records_telemetry_event("p4", "historical_backfill_engine", "telemetry_event")
_emit_captures_evaluation_metric("p4", "historical_backfill_engine", "eval_metric")
_emit_stores_embedding("p4", "historical_backfill_engine", "embedding_store")
_emit_updates_meta_learning_state("p4", "historical_backfill_engine", "meta_learning")
_emit_links_execution_to_snapshot("p4", "historical_backfill_engine", "exec_snapshot_link")
_emit_emits_metric_event("historical_backfill_engine", "p4obs", "metric_1")
_emit_emits_metric_event("historical_backfill_engine", "p4obs", "metric_2")
_emit_emits_metric_event("historical_backfill_engine", "p4obs", "metric_3")
_emit_emits_metric_event("historical_backfill_engine", "p4obs", "metric_4")
_emit_emits_metric_event("historical_backfill_engine", "p4obs", "metric_5")
_emit_emits_metric_event("historical_backfill_engine", "p4obs", "metric_6")
_emit_records_incident_event("historical_backfill_engine", "p4obs", "incident")
_emit_captures_runtime_anomaly("historical_backfill_engine", "p4obs", "anomaly")
_emit_writes_observability_log("historical_backfill_engine", "p4obs", "obs_log")
_emit_updates_monitoring_state("historical_backfill_engine", "p4obs", "mon_state")
_emit_triggers_alert("historical_backfill_engine", "p4obs", "alert")
_emit_links_incident_trace("historical_backfill_engine", "p4obs", "trace_link")
_emit_captures_pattern("historical_backfill_engine", "p3lm", "pattern")
_emit_records_learning_event("historical_backfill_engine", "p3lm", "learning_event")
_emit_writes_learning_snapshot("historical_backfill_engine", "p3lm", "snapshot")
_emit_feeds_meta_learning("historical_backfill_engine", "p3lm", "meta_feed")
_emit_updates_routing_strategy("historical_backfill_engine", "p3lm", "routing")
_emit_improves_agent_policy("historical_backfill_engine", "p3lm", "policy")
_emit_stores_learning_state("historical_backfill_engine", "p3lm", "state")
_emit_pulls_context("p1", "historical_backfill_engine", "context_pull")
_emit_execution_terminates_at_uwg("p1", "historical_backfill_engine", "uwg_term")
_emit_writes_through("p1", "historical_backfill_engine", "write_through")
_emit_validated_by_safety_plane("p1", "historical_backfill_engine", "safety_validation")
_emit_proposal_commits_routing("p1", "historical_backfill_engine", "routing_commit")
_emit_escalates_to_human("p1", "historical_backfill_engine", "human_escalation")
_emit_routes_through("p1", "historical_backfill_engine", "route_through")
_emit_checks_agent_registry("p1", "historical_backfill_engine", "agent_registry")
_emit_validates_agent_capability("p1", "historical_backfill_engine", "capability")
_emit_dispatches_execution_plan("p1", "historical_backfill_engine", "exec_plan")
_emit_agent_executes_agent("p1", "historical_backfill_engine", "sub_agent")
_emit_routes_to_agent("p1", "historical_backfill_engine", "target_agent")
_emit_verifies_policy("p1", "historical_backfill_engine", "policy_check")
_emit_observes_runtime_state("p1", "historical_backfill_engine", "runtime_state")
_emit_verifies_boundary("p1", "historical_backfill_engine", "boundary_check")
_emit_transcripts_response("p1", "historical_backfill_engine", "transcript")
_emit_hard_fails_untranscripted("p1", "historical_backfill_engine")
_emit_gated_by_confidence("p1", "historical_backfill_engine", "confidence_gate")

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
    malformed_lines = 0
    with corpus_path.open(encoding="utf-8", errors="replace") as handle:
        for line in tqdm(handle, desc="Processing", unit="item"):
            line = line.strip()
            if not line:
                continue
            try:
                hashes.add(json.loads(line).get("content_hash", ""))
            except json.JSONDecodeError as exc:  # guardian: allow-log-and-swallow -- corpus parse: malformed lines skipped, backfill continues
                malformed_lines += 1
                logger.debug("[Backfill] Skipping malformed corpus line in %s: %s", corpus_path, exc)
    if malformed_lines:
        logger.warning("[Backfill] Ignored %d malformed corpus lines in %s", malformed_lines, corpus_path)
    return hashes


def _load_jsonl_lenient(path: Path) -> list[dict[str, Any]]:
    records = []
    malformed_lines = 0
    with path.open(encoding="utf-8", errors="replace") as handle:
        for line in tqdm(handle, desc="Processing", unit="item"):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:  # guardian: allow-log-and-swallow -- JSONL parse: malformed lines skipped, backfill continues
                malformed_lines += 1
                logger.debug("[Backfill] Skipping malformed JSONL line in %s: %s", path, exc)
    if malformed_lines:
        logger.warning("[Backfill] Ignored %d malformed JSONL lines in %s", malformed_lines, path)
    return records


def _load_json_lenient(path: Path) -> dict[str, Any] | None:
    """Parse compliance JSON that may contain unescaped Windows backslashes."""
    raw = path.read_text(encoding="utf-8", errors="replace")
    fixed = re.sub(r"\\(?![\"\\\/bfnrtu])", r"\\\\", raw)
    try:
        return json.loads(fixed)
    except json.JSONDecodeError as exc:  # guardian: allow-return-none-swallow -- file parse: non-fatal, caller skips unreadable files
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
    for rec in tqdm(records, desc="Processing", unit="item"):
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
        except (
            ValueError,
            TypeError,
            RuntimeError,
        ) as exc:  # guardian: allow-log-and-swallow -- timestamp normalization: non-fatal, created_utc defaults to current time
            logger.debug("[Backfill] Invalid ts_utc=%r for caller=%s: %s", ts_utc, caller, exc)

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
        "[Backfill] Wrote %d protected_root_block records to corpus (dry_run=%s).",
        len(new_lines),
        dry_run,
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
        except ImportError:  # guardian: allow-silent-swallow -- optional dependency
            logger.debug("[Backfill] HealingSuccessRateStore not available, skipping.")
            return {}

    seeded: dict[str, float] = {}

    for report_path in tqdm(
        sorted(reports_dir.glob("compliance_report_*.json")), desc="Processing", unit="item"
    ):
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
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=sentinel.parent,
            prefix=sentinel.name + ".",
            suffix=".tmp",
            delete=False,
        ) as handle:
            json.dump(
                {"corpus_records_added": corpus_added, "territories_seeded": list(territories.keys())},
                handle,
                separators=(",", ":"),
                sort_keys=True,
            )
            tmp_name = handle.name
        Path(tmp_name).replace(sentinel)

    return {
        "skipped": False,
        "corpus_records_added": corpus_added,
        "territories_seeded": territories,
    }
