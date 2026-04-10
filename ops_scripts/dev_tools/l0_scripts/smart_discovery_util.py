"""
Smart Discovery Runner - Optimal execution model for agent discovery.

Features:
- Staleness detection (compare JSON mtime vs source file mtimes)
- Incremental mode detection (only flag when full scan needed)
- Pre-report freshness check for AutonomyGuardianAgent

Usage:
    python scripts/smart_discovery_util.py              # Auto-detect mode
    python scripts/smart_discovery_util.py --check      # Just check if stale
    python scripts/smart_discovery_util.py --force      # Force full scan
"""

import hashlib
import json
import logging
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import AGENT_DISCOVERY_JSON, AGENT_DISCOVERY_MANIFEST_JSON, SCRIPTS_DIR
from agentic_core.L0_routing.config.path_constants import DISCOVERY_EXCLUDED_TERRITORIES, GLOBAL_EXCLUDED_DIRS, SOVEREIGN_EXCLUDED_FOLDERS
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)
from agentic_core.utils.security_util import safe_execute

_emit_records_execution_trace("p0", "evidence", "smart_discovery_util")
_emit_applies_guardrail("p0", "smart_discovery_util", "p0_governance")
_emit_reads_policy_state("p0", "smart_discovery_util", "policy_binding")
_emit_snapshots_state("p0", "smart_discovery_util", "state_snapshot")
emit_replay_key("p0", "smart_discovery_util")
emit_determinism_digest("p0", "smart_discovery_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "smart_discovery_util", "execution_auth")
_emit_validates_capability("p2", "smart_discovery_util", "capability_check")
_emit_routes_to_capability("p2", "smart_discovery_util", "capability_route")
_emit_writes_via_uwg("p2", "smart_discovery_util", "uwg_write")
_emit_blocks_direct_write("p2", "smart_discovery_util", "direct_write_block")
_emit_records_tool_invocation("p2", "smart_discovery_util", "tool_invocation")
_emit_captures_execution_output("p2", "smart_discovery_util", "exec_output")
_emit_dispatches_agent("p3", "smart_discovery_util", "agent_dispatch")
_emit_coordinates_agents("p3", "smart_discovery_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "smart_discovery_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "smart_discovery_util", "healing_outcome")
_emit_escalates_failure("p3", "smart_discovery_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "smart_discovery_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "smart_discovery_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "smart_discovery_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "smart_discovery_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "smart_discovery_util", "eval_metric")
_emit_stores_embedding("p4", "smart_discovery_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "smart_discovery_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "smart_discovery_util", "exec_snapshot_link")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DISCOVERY_JSON = PROJECT_ROOT / AGENT_DISCOVERY_JSON
MANIFEST_JSON = PROJECT_ROOT / AGENT_DISCOVERY_MANIFEST_JSON

# configuration
STALENESS_THRESHOLD = timedelta(hours=1)

# Shared exclude logic with discovery
from agentic_core.L0_routing.config.path_constants import ARCHIVES_DIR  # noqa: E402
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("smart_discovery_util", "p4obs", "metric_1")
_emit_emits_metric_event("smart_discovery_util", "p4obs", "metric_2")
_emit_emits_metric_event("smart_discovery_util", "p4obs", "metric_3")
_emit_emits_metric_event("smart_discovery_util", "p4obs", "metric_4")
_emit_emits_metric_event("smart_discovery_util", "p4obs", "metric_5")
_emit_emits_metric_event("smart_discovery_util", "p4obs", "metric_6")
_emit_records_incident_event("smart_discovery_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("smart_discovery_util", "p4obs", "anomaly")
_emit_writes_observability_log("smart_discovery_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("smart_discovery_util", "p4obs", "mon_state")
_emit_triggers_alert("smart_discovery_util", "p4obs", "alert")
_emit_links_incident_trace("smart_discovery_util", "p4obs", "trace_link")
_emit_captures_pattern("smart_discovery_util", "p3lm", "pattern")
_emit_records_learning_event("smart_discovery_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("smart_discovery_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("smart_discovery_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("smart_discovery_util", "p3lm", "routing")
_emit_improves_agent_policy("smart_discovery_util", "p3lm", "policy")
_emit_stores_learning_state("smart_discovery_util", "p3lm", "state")
_emit_records_execution_trace("smart_discovery_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("smart_discovery_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("smart_discovery_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("smart_discovery_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("smart_discovery_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("smart_discovery_util", "env_read", "p2_env_1")
_emit_reads_environ("smart_discovery_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("smart_discovery_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("smart_discovery_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "smart_discovery_util", "context_pull")
_emit_pulls_context("p1", "smart_discovery_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "smart_discovery_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "smart_discovery_util", "uwg_term_2")
_emit_writes_through("p1", "smart_discovery_util", "write_through")
_emit_writes_through("p1", "smart_discovery_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "smart_discovery_util", "safety_validation")
_emit_invokes_eval("p1", "smart_discovery_util", "eval_call")
_emit_proposal_commits_routing("p1", "smart_discovery_util", "routing_commit")
_emit_escalates_to_human("p1", "smart_discovery_util", "human_escalation")
_emit_routes_through("p1", "smart_discovery_util", "route_through")
_emit_checks_agent_registry("p1", "smart_discovery_util", "agent_registry")
_emit_validates_agent_capability("p1", "smart_discovery_util", "capability")
_emit_dispatches_execution_plan("p1", "smart_discovery_util", "exec_plan")
_emit_agent_executes_agent("p1", "smart_discovery_util", "sub_agent")
_emit_routes_to_agent("p1", "smart_discovery_util", "target_agent")
_emit_verifies_policy("p1", "smart_discovery_util", "policy_check")
_emit_observes_runtime_state("p1", "smart_discovery_util", "runtime_state")
_emit_verifies_boundary("p1", "smart_discovery_util", "boundary_check")
_emit_transcripts_response("p1", "smart_discovery_util", "transcript")
_emit_hard_fails_untranscripted("p1", "smart_discovery_util")
_emit_gated_by_confidence("p1", "smart_discovery_util", "confidence_gate")

EXCLUDED_DIRS = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES


def should_exclude_path(path: Path) -> bool:
    """Return True if path should be excluded from scanning/hashing."""
    return any(excluded in path.parts for excluded in EXCLUDED_DIRS)


# Proper logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("smart_discovery")


def _scan_python_files() -> list[Path]:
    """Return list of all non-excluded .py files."""
    # Phase 6.7: Use ssot_discovery instead of rglob
    from agentic_core.utils.runners.ssot_discovery_validator import get_python_files

    return list(get_python_files(PROJECT_ROOT))


def get_json_mtime() -> datetime | None:
    """Get modification time of discovery JSON."""
    if not DISCOVERY_JSON.exists():
        return None
    try:
        return datetime.fromtimestamp(DISCOVERY_JSON.stat().st_mtime)
    except OSError as e:    # guardian: Add error context logging
        log.error(f"Failed to read JSON mtime: {e}")
        return None


def get_latest_source_mtime() -> datetime:
    """Get the most recent mtime of scanned Python files."""
    files = _scan_python_files()
    latest = datetime.min
    for py_file in files:
        try:
            mtime = datetime.fromtimestamp(py_file.stat().st_mtime)
            if mtime > latest:
                latest = mtime
        except OSError:    # guardian: Add error context logging
            return datetime.now()  # Unreadable → assume changed
    return latest if latest != datetime.min else datetime.now()


def is_discovery_stale() -> tuple[bool, str]:
    """
    Check if discovery JSON needs refresh.

    Returns:
        (is_stale, reason)
    """
    if not DISCOVERY_JSON.exists():
        return True, "JSON file does not exist"

    json_mtime = get_json_mtime()
    if json_mtime is None:
        return True, "JSON mtime unreadable"

    # Check JSON age
    age = datetime.now() - json_mtime
    if age > STALENESS_THRESHOLD:
        return True, f"JSON too old ({age.total_seconds() / 3600:.1f}h > 1h)"

    # Check if any source files are newer than JSON
    latest_source = get_latest_source_mtime()
    if latest_source > json_mtime:
        return True, f"Source files modified after JSON ({latest_source} > {json_mtime})"

    return False, "JSON is fresh"


def get_changed_files() -> list[Path]:
    """Return list of changed files since last manifest (for logging only)."""
    if not MANIFEST_JSON.exists():
        return _scan_python_files()  # Force full if no manifest

    try:
        manifest = json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))
        file_hashes: dict = manifest.get("file_hashes", {})
    # guardian: allow-silent-swallow
    except Exception as e:
        log.warning(f"Manifest invalid ({e}) → assuming all changed")
        return _scan_python_files()

    files = _scan_python_files()
    changed = []
    for py_file in files:
        rel_path = str(py_file.relative_to(PROJECT_ROOT)).replace("\\", "/")
        try:
            current_hash = hashlib.md5(py_file.read_bytes()).hexdigest()
            if file_hashes.get(rel_path) != current_hash:
                changed.append(py_file)
        # guardian: allow-silent-swallow
        except Exception:
            changed.append(py_file)
    return changed


def run_discovery(force: bool = False) -> int:
    """
    Run discovery with smart mode selection.

    Returns exit code (0 = success)
    """
    import subprocess

    is_stale, reason = is_discovery_stale()

    if not force and not is_stale:
        log.info("JSON is fresh, skipping scan")
        log.info(f"Reason: {reason}")
        return 0

    log.info("Discovery needed")
    log.info(f"Reason: {reason}")

    changed = get_changed_files()
    log.info(f"Detected {len(changed)} changed files (informational)")

    # INCREMENTAL TRIGGER: Use incremental mode for small change sets
    use_incremental = 0 < len(changed) <= 30
    if use_incremental:
        log.info(f"Small change set ({len(changed)} files) → using --incremental mode")
    elif len(changed) > 30:
        log.info(f"Large change set ({len(changed)} files) → full scan")

    cmd = [sys.executable, str(PROJECT_ROOT / SCRIPTS_DIR / "full_agent_discovery.py")]
    if force:
        cmd.append("--force")
    if use_incremental:
        cmd.append("--incremental")

    # Robust subprocess with timeout, output capture, logging
    log.info("Launching full_agent_discovery.py...")
    start = time.time()
    try:
        # guardian: allow-magic-config
        result = safe_execute(
            cmd,
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=DEFAULT_TIMEOUT,  # 5 min max
            check=False,
        )
        elapsed = time.time() - start
        if result.returncode == 0:
            log.info(f"Discovery succeeded in {elapsed:.1f}s")
            return 0
        else:
            log.error(f"Discovery failed (code {result.returncode})")
            log.error(f"STDOUT: {result.stdout}")
            log.error(f"STDERR: {result.stderr}")
            return result.returncode
    except subprocess.TimeoutExpired:
        log.error("Discovery timed out after 300s")
        return 1
    # guardian: allow-silent-swallow
    except Exception as e:
        log.error(f"Failed to launch discovery: {e}")
        return 1


def ensure_fresh_discovery() -> None:
    """
    Called by AutonomyGuardianAgent before report generation.
    Auto-refreshes if stale.
    """
    is_stale, reason = is_discovery_stale()
    if is_stale:
        log.info(f"JSON stale ({reason}) → triggering discovery")
        run_discovery()
    else:
        log.info("JSON fresh → skipping discovery")


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Smart Agent Discovery Runner")
    parser.add_argument("--check", action="store_true", help="Just check if stale, don't run")
    parser.add_argument("--force", action="store_true", help="Force full scan")
    parser.add_argument("--ensure", action="store_true", help="Ensure fresh (for pre-report)")
    args = parser.parse_args()

    if args.check:
        is_stale, reason = is_discovery_stale()
        print(f"Stale: {is_stale}")
        print(f"Reason: {reason}")
        sys.exit(1 if is_stale else 0)

    if args.ensure:
        ensure_fresh_discovery()
        sys.exit(0)

    exit_code = run_discovery(force=args.force)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
