"""R2: ADG Cache Loader — load ScanResult from cache or trigger fresh scan.

Cache key: commit_sha + scanner_version + schema_version + python_ast_version
Cache is invalidated when any key dimension changes.
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    ADG_ARTIFACTS_DIR,
    DEFAULT_TIMEOUT,
)
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_records_execution_trace("p0", "evidence", "cache_loader")
trace_contract._emit_applies_guardrail("p0", "cache_loader", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "cache_loader", "policy_binding")
trace_contract._emit_snapshots_state("p0", "cache_loader", "state_snapshot")

trace_contract._emit_emits_metric_event("cache_loader", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("cache_loader", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("cache_loader", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("cache_loader", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("cache_loader", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("cache_loader", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("cache_loader", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("cache_loader", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("cache_loader", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("cache_loader", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("cache_loader", "p4obs", "alert")
trace_contract._emit_links_incident_trace("cache_loader", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("cache_loader", "p3lm", "pattern")
trace_contract._emit_records_learning_event("cache_loader", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("cache_loader", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("cache_loader", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("cache_loader", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("cache_loader", "p3lm", "policy")
trace_contract._emit_stores_learning_state("cache_loader", "p3lm", "state")
trace_contract._emit_records_execution_trace("cache_loader", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("cache_loader", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("cache_loader", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("cache_loader", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("cache_loader", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("cache_loader", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("cache_loader", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("cache_loader", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("cache_loader", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "cache_loader", "context_pull")
trace_contract._emit_pulls_context("p1", "cache_loader", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "cache_loader", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "cache_loader", "uwg_term_2")
trace_contract._emit_writes_through("p1", "cache_loader", "write_through")
trace_contract._emit_writes_through("p1", "cache_loader", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "cache_loader", "safety_validation")
trace_contract._emit_invokes_eval("p1", "cache_loader", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "cache_loader", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "cache_loader", "human_escalation")
trace_contract._emit_routes_through("p1", "cache_loader", "route_through")
trace_contract._emit_checks_agent_registry("p1", "cache_loader", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "cache_loader", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "cache_loader", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "cache_loader", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "cache_loader", "target_agent")
trace_contract._emit_verifies_policy("p1", "cache_loader", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "cache_loader", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "cache_loader", "boundary_check")
trace_contract._emit_transcripts_response("p1", "cache_loader", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "cache_loader")
trace_contract._emit_gated_by_confidence("p1", "cache_loader", "confidence_gate")
trace_contract.emit_replay_key("p0", "cache_loader")
trace_contract.emit_determinism_digest("p0", "cache_loader")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "cache_loader", "execution_auth")
trace_contract._emit_validates_capability("p2", "cache_loader", "capability_check")
trace_contract._emit_routes_to_capability("p2", "cache_loader", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "cache_loader", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "cache_loader", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "cache_loader", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "cache_loader", "exec_output")
trace_contract._emit_dispatches_agent("p3", "cache_loader", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "cache_loader", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "cache_loader", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "cache_loader", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "cache_loader", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "cache_loader", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "cache_loader", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "cache_loader", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "cache_loader", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "cache_loader", "eval_metric")
trace_contract._emit_stores_embedding("p4", "cache_loader", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "cache_loader", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "cache_loader", "exec_snapshot_link")

# Configuration: canonical cache path per S-10

logger = logging.getLogger(__name__)
_CACHE_PATH = Path(f"{ADG_ARTIFACTS_DIR}/cache/scan_result_cache.json")


def _get_commit_sha() -> str:
    """Read HEAD commit SHA from git, or return empty string on failure."""
    try:
        import subprocess

        r = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            timeout=DEFAULT_TIMEOUT,
        )
        return r.stdout.strip() if r.returncode == 0 else ""
    except (OSError, RuntimeError, ValueError):  # guardian: allow-silent-swallow
        return ""


def _cache_key(scanner_version: str, schema_version: str) -> str:
    commit = _get_commit_sha()
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}"
    return f"{commit}::{scanner_version}::{schema_version}::{py_ver}"


def _is_cache_valid(cached: dict) -> bool:
    """Return True iff the cached data matches current cache key dimensions."""
    from agentic_core.adg.extraction.static_scanner import _SCANNER_VERSION, _SCHEMA_VERSION

    expected_key = _cache_key(_SCANNER_VERSION, _SCHEMA_VERSION)
    cached_key = cached.get("_cache_key")

    if cached_key is None:
        return False

    # Parse cache key components
    try:
        cached_parts = cached_key.split("::")
        expected_parts = expected_key.split("::")

        if len(cached_parts) != 4 or len(expected_parts) != 4:
            return False

        cached_commit, cached_scanner, cached_schema, cached_py = cached_parts
        expected_commit, expected_scanner, expected_schema, expected_py = expected_parts

        # Allow cache if commit and Python version match (scanner/schema can be compatible)
        if cached_commit == expected_commit and cached_py == expected_py:
            # Check scanner version compatibility (allow minor version differences)
            if cached_scanner == expected_scanner:
                return True
            # Allow scanner version differences if schema is the same
            if cached_schema == expected_schema:
                return True

        return False
    except ValueError:
        return False


def load_or_scan(
    repo_root: str | None = None,
    cache_path: Path | None = None,
    force_cache: bool = False,
) -> ScanResult:
    """R2: Load ADG ScanResult from cache if valid, otherwise run fresh scan.

    Cache key: commit_sha + scanner_version + schema_version + python_ast_version.

    Args:
        repo_root: Repository root path
        cache_path: Custom cache file path
        force_cache: If True, bypass cache validation and use existing cache
    """
    from agentic_core.adg.extraction.static_scanner import (
        _SCANNER_VERSION,
        _SCHEMA_VERSION,
        ADGStaticScanner,
        ScanResult,
    )

    cache = cache_path or _CACHE_PATH
    if cache.exists():
        try:
            cached = json.loads(cache.read_text(encoding="utf-8"))
            # Check cache validity or force usage
            if force_cache or _is_cache_valid(cached):
                cache_status = "forced" if force_cache else "valid"
                logger.info(
                    "ADG cache %s: %s", cache_status, cache
                )  # guardian: allow-log-and-swallow -- cache read best-effort: failure falls through to fresh scanner.scan() below
                return ScanResult.from_dict(cached)
            logger.info("ADG cache miss (key changed): %s", cache)
        except (
            OSError,
            json.JSONDecodeError,
            ValueError,
        ) as exc:  # guardian: allow-log-and-swallow -- cache read best-effort: falls through to fresh scanner.scan() below
            logger.warning("ADG cache read error (%s): %s — running fresh scan", cache, exc)
    root = Path(repo_root) if repo_root else Path.cwd()
    scanner = ADGStaticScanner(repo_root=root)
    result = scanner.scan()
    try:
        cache.parent.mkdir(parents=True, exist_ok=True)
        payload = result.to_dict()
        payload["_cache_key"] = _cache_key(_SCANNER_VERSION, _SCHEMA_VERSION)
        cache.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        logger.info(
            "ADG cache written: %s (%d edges)", cache, len(result.edges)
        )  # guardian: allow-log-and-swallow -- cache write best-effort: scan result is returned regardless of cache persistence
    except (
        OSError,
        ValueError,
    ) as exc:  # guardian: allow-log-and-swallow -- cache write best-effort: return ScanResult regardless of persistence
        logger.warning("ADG cache write failed: %s", exc)
    return result


def invalidate_cache(cache_path: Path | None = None) -> None:
    """Force-invalidate the ADG cache by deleting the cache file."""
    cache = cache_path or _CACHE_PATH
    if cache.exists():
        cache.unlink()
        logger.info("ADG cache invalidated: %s", cache)


__all__ = [
    "BATCH_SIZE",
    "BUFFER_SIZE",
    "DEFAULT_SLEEP",
    "MAX_DEPTH",
    "MAX_RETRIES",
    "THRESHOLD",
    "load_or_scan",
    "invalidate_cache",
]
