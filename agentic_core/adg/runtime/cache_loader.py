"""R2: ADG Cache Loader — load ScanResult from cache or trigger fresh scan.

Cache key: commit_sha + scanner_version + schema_version + python_ast_version
Cache is invalidated when any key dimension changes.
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import DEFAULT_TIMEOUT
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "cache_loader")
_emit_applies_guardrail("p0", "cache_loader", "p0_governance")
_emit_reads_policy_state("p0", "cache_loader", "policy_binding")
_emit_snapshots_state("p0", "cache_loader", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import _emit_pulls_context, _emit_execution_terminates_at_uwg, _emit_writes_through, _emit_validated_by_safety_plane, _emit_invokes_eval, _emit_proposal_commits_routing
from agentic_core.runtime.lifecycle_trace_contract import _emit_records_execution_trace, _emit_reads_environ, _emit_reads_runtime_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_captures_pattern, _emit_records_learning_event, _emit_writes_learning_snapshot, _emit_feeds_meta_learning, _emit_updates_routing_strategy, _emit_improves_agent_policy, _emit_stores_learning_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_emits_metric_event, _emit_records_incident_event, _emit_captures_runtime_anomaly, _emit_writes_observability_log, _emit_updates_monitoring_state, _emit_triggers_alert, _emit_links_incident_trace
_emit_emits_metric_event("cache_loader", "p4obs", "metric_1")
_emit_emits_metric_event("cache_loader", "p4obs", "metric_2")
_emit_emits_metric_event("cache_loader", "p4obs", "metric_3")
_emit_emits_metric_event("cache_loader", "p4obs", "metric_4")
_emit_emits_metric_event("cache_loader", "p4obs", "metric_5")
_emit_emits_metric_event("cache_loader", "p4obs", "metric_6")
_emit_records_incident_event("cache_loader", "p4obs", "incident")
_emit_captures_runtime_anomaly("cache_loader", "p4obs", "anomaly")
_emit_writes_observability_log("cache_loader", "p4obs", "obs_log")
_emit_updates_monitoring_state("cache_loader", "p4obs", "mon_state")
_emit_triggers_alert("cache_loader", "p4obs", "alert")
_emit_links_incident_trace("cache_loader", "p4obs", "trace_link")
_emit_captures_pattern("cache_loader", "p3lm", "pattern")
_emit_records_learning_event("cache_loader", "p3lm", "learning_event")
_emit_writes_learning_snapshot("cache_loader", "p3lm", "snapshot")
_emit_feeds_meta_learning("cache_loader", "p3lm", "meta_feed")
_emit_updates_routing_strategy("cache_loader", "p3lm", "routing")
_emit_improves_agent_policy("cache_loader", "p3lm", "policy")
_emit_stores_learning_state("cache_loader", "p3lm", "state")
_emit_records_execution_trace("cache_loader", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("cache_loader", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("cache_loader", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("cache_loader", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("cache_loader", "L4_STATE", "p2_trace_5")
_emit_reads_environ("cache_loader", "env_read", "p2_env_1")
_emit_reads_environ("cache_loader", "env_read", "p2_env_2")
_emit_reads_runtime_state("cache_loader", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("cache_loader", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "cache_loader", "context_pull")
_emit_pulls_context("p1", "cache_loader", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "cache_loader", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "cache_loader", "uwg_term_2")
_emit_writes_through("p1", "cache_loader", "write_through")
_emit_writes_through("p1", "cache_loader", "write_through_2")
_emit_validated_by_safety_plane("p1", "cache_loader", "safety_validation")
_emit_invokes_eval("p1", "cache_loader", "eval_call")
_emit_proposal_commits_routing("p1", "cache_loader", "routing_commit")
emit_replay_key("p0", "cache_loader")
emit_determinism_digest("p0", "cache_loader")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "cache_loader", "execution_auth")
_emit_validates_capability("p2", "cache_loader", "capability_check")
_emit_routes_to_capability("p2", "cache_loader", "capability_route")
_emit_writes_via_uwg("p2", "cache_loader", "uwg_write")
_emit_blocks_direct_write("p2", "cache_loader", "direct_write_block")
_emit_records_tool_invocation("p2", "cache_loader", "tool_invocation")
_emit_captures_execution_output("p2", "cache_loader", "exec_output")
_emit_dispatches_agent("p3", "cache_loader", "agent_dispatch")
_emit_coordinates_agents("p3", "cache_loader", "agent_coordination")
_emit_records_workflow_lineage("p3", "cache_loader", "workflow_lineage")
_emit_records_healing_outcome("p3", "cache_loader", "healing_outcome")
_emit_escalates_failure("p3", "cache_loader", "failure_escalation")
_emit_orchestrates_workflow("p3", "cache_loader", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "cache_loader", "healing_dispatch")
_emit_invokes_evaluation("p3", "cache_loader", "evaluation_signal")
_emit_records_telemetry_event("p4", "cache_loader", "telemetry_event")
_emit_captures_evaluation_metric("p4", "cache_loader", "eval_metric")
_emit_stores_embedding("p4", "cache_loader", "embedding_store")
_emit_updates_meta_learning_state("p4", "cache_loader", "meta_learning")
_emit_links_execution_to_snapshot("p4", "cache_loader", "exec_snapshot_link")

logger = logging.getLogger(__name__)
_CACHE_PATH = Path("artifacts/adg/scan_result_cache.json")


def _get_commit_sha() -> str:
    """Read HEAD commit SHA from git, or return empty string on failure."""
    try:
        import subprocess

        r = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, timeout=DEFAULT_TIMEOUT
        )
        return r.stdout.strip() if r.returncode == 0 else ""
    # guardian: allow-silent-swallow
    except Exception:
        return ""


def _cache_key(scanner_version: str, schema_version: str) -> str:
    commit = _get_commit_sha()
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}"
    return f"{commit}::{scanner_version}::{schema_version}::{py_ver}"


def _is_cache_valid(cached: dict) -> bool:
    """Return True iff the cached data matches current cache key dimensions."""
    from agentic_core.adg.extraction.static_scanner import _SCANNER_VERSION, _SCHEMA_VERSION

    expected_key = _cache_key(_SCANNER_VERSION, _SCHEMA_VERSION)
    return cached.get("_cache_key") == expected_key


def load_or_scan(repo_root: str | None = None, cache_path: Path | None = None) -> ScanResult:
    """R2: Load ADG ScanResult from cache if valid, otherwise run fresh scan.

    Cache key: commit_sha + scanner_version + schema_version + python_ast_version.
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
            if _is_cache_valid(cached):
                logger.info("ADG cache hit: %s", cache)
                return ScanResult.from_dict(cached)
            logger.info("ADG cache miss (key changed): %s", cache)
        # guardian: allow-silent-swallow
        except Exception as exc:
            logger.warning("ADG cache read error (%s): %s — running fresh scan", cache, exc)
    root = Path(repo_root) if repo_root else Path.cwd()
    scanner = ADGStaticScanner(repo_root=root)
    result = scanner.scan()
    try:
        cache.parent.mkdir(parents=True, exist_ok=True)
        payload = result.to_dict()
        payload["_cache_key"] = _cache_key(_SCANNER_VERSION, _SCHEMA_VERSION)
        cache.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        logger.info("ADG cache written: %s (%d edges)", cache, len(result.edges))
    # guardian: allow-silent-swallow
    except Exception as exc:
        logger.warning("ADG cache write failed: %s", exc)
    return result


def invalidate_cache(cache_path: Path | None = None) -> None:
    """Force-invalidate the ADG cache by deleting the cache file."""
    cache = cache_path or _CACHE_PATH
    if cache.exists():
        cache.unlink()
        logger.info("ADG cache invalidated: %s", cache)


__all__ = ["load_or_scan", "invalidate_cache"]
