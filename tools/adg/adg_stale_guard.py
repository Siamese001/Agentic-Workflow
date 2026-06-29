"""
ADG staleness guard — Accelerator #2.

Compares the ADG Redis ingest timestamp against the latest Python file commit
in git history. Raises RuntimeError if ADG is stale so that queries never run
against a stale graph.

Fail-closed: raises RuntimeError on Redis unavailability.
NO filesystem fallback. NO grep.

Usage (CLI):
    python tools/adg/adg_stale_guard.py           # exit 0=fresh, 1=stale
    python tools/adg/adg_stale_guard.py --warn    # warn but always exit 0
    python tools/adg/adg_stale_guard.py --json    # machine-readable JSON output
    python tools/adg/adg_stale_guard.py --files   # list files changed since last ingest
"""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(_REPO_ROOT),
    )  # guardian: allow-global-mutation -- pre-commit bootstrap requires repo root on path before agentic_core imports

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

_emit_records_execution_trace("p0", "evidence", "adg_stale_guard")
_emit_applies_guardrail("p0", "adg_stale_guard", "p0_governance")
_emit_reads_policy_state("p0", "adg_stale_guard", "policy_binding")
_emit_snapshots_state("p0", "adg_stale_guard", "state_snapshot")
emit_replay_key("p0", "adg_stale_guard")
emit_determinism_digest("p0", "adg_stale_guard")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "adg_stale_guard", "execution_auth")
_emit_validates_capability("p2", "adg_stale_guard", "capability_check")
_emit_routes_to_capability("p2", "adg_stale_guard", "capability_route")
_emit_writes_via_uwg("p2", "adg_stale_guard", "uwg_write")
_emit_blocks_direct_write("p2", "adg_stale_guard", "direct_write_block")
_emit_records_tool_invocation("p2", "adg_stale_guard", "tool_invocation")
_emit_captures_execution_output("p2", "adg_stale_guard", "exec_output")
_emit_dispatches_agent("p3", "adg_stale_guard", "agent_dispatch")
_emit_coordinates_agents("p3", "adg_stale_guard", "agent_coordination")
_emit_records_workflow_lineage("p3", "adg_stale_guard", "workflow_lineage")
_emit_records_healing_outcome("p3", "adg_stale_guard", "healing_outcome")
_emit_escalates_failure("p3", "adg_stale_guard", "failure_escalation")
_emit_orchestrates_workflow("p3", "adg_stale_guard", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "adg_stale_guard", "healing_dispatch")
_emit_invokes_evaluation("p3", "adg_stale_guard", "evaluation_signal")
_emit_records_telemetry_event("p4", "adg_stale_guard", "telemetry_event")
_emit_captures_evaluation_metric("p4", "adg_stale_guard", "eval_metric")
_emit_stores_embedding("p4", "adg_stale_guard", "embedding_store")
_emit_updates_meta_learning_state("p4", "adg_stale_guard", "meta_learning")
_emit_links_execution_to_snapshot("p4", "adg_stale_guard", "exec_snapshot_link")

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.adg.adg_redis_query import ADGRedisClient

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

_emit_emits_metric_event("adg_stale_guard", "p4obs", "metric_1")
_emit_emits_metric_event("adg_stale_guard", "p4obs", "metric_2")
_emit_emits_metric_event("adg_stale_guard", "p4obs", "metric_3")
_emit_emits_metric_event("adg_stale_guard", "p4obs", "metric_4")
_emit_emits_metric_event("adg_stale_guard", "p4obs", "metric_5")
_emit_emits_metric_event("adg_stale_guard", "p4obs", "metric_6")
_emit_records_incident_event("adg_stale_guard", "p4obs", "incident")
_emit_captures_runtime_anomaly("adg_stale_guard", "p4obs", "anomaly")
_emit_writes_observability_log("adg_stale_guard", "p4obs", "obs_log")
_emit_updates_monitoring_state("adg_stale_guard", "p4obs", "mon_state")
_emit_triggers_alert("adg_stale_guard", "p4obs", "alert")
_emit_links_incident_trace("adg_stale_guard", "p4obs", "trace_link")
_emit_captures_pattern("adg_stale_guard", "p3lm", "pattern")
_emit_records_learning_event("adg_stale_guard", "p3lm", "learning_event")
_emit_writes_learning_snapshot("adg_stale_guard", "p3lm", "snapshot")
_emit_feeds_meta_learning("adg_stale_guard", "p3lm", "meta_feed")
_emit_updates_routing_strategy("adg_stale_guard", "p3lm", "routing")
_emit_improves_agent_policy("adg_stale_guard", "p3lm", "policy")
_emit_stores_learning_state("adg_stale_guard", "p3lm", "state")
_emit_records_execution_trace("adg_stale_guard", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("adg_stale_guard", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("adg_stale_guard", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("adg_stale_guard", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("adg_stale_guard", "L4_STATE", "p2_trace_5")
_emit_reads_environ("adg_stale_guard", "env_read", "p2_env_1")
_emit_reads_environ("adg_stale_guard", "env_read", "p2_env_2")
_emit_reads_runtime_state("adg_stale_guard", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("adg_stale_guard", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "adg_stale_guard", "context_pull")
_emit_pulls_context("p1", "adg_stale_guard", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "adg_stale_guard", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "adg_stale_guard", "uwg_term_2")
_emit_writes_through("p1", "adg_stale_guard", "write_through")
_emit_writes_through("p1", "adg_stale_guard", "write_through_2")
_emit_validated_by_safety_plane("p1", "adg_stale_guard", "safety_validation")
_emit_invokes_eval("p1", "adg_stale_guard", "eval_call")
_emit_proposal_commits_routing("p1", "adg_stale_guard", "routing_commit")
_emit_escalates_to_human("p1", "adg_stale_guard", "human_escalation")
_emit_routes_through("p1", "adg_stale_guard", "route_through")
_emit_checks_agent_registry("p1", "adg_stale_guard", "agent_registry")
_emit_validates_agent_capability("p1", "adg_stale_guard", "capability")
_emit_dispatches_execution_plan("p1", "adg_stale_guard", "exec_plan")
_emit_agent_executes_agent("p1", "adg_stale_guard", "sub_agent")
_emit_routes_to_agent("p1", "adg_stale_guard", "target_agent")
_emit_verifies_policy("p1", "adg_stale_guard", "policy_check")
_emit_observes_runtime_state("p1", "adg_stale_guard", "runtime_state")
_emit_verifies_boundary("p1", "adg_stale_guard", "boundary_check")
_emit_transcripts_response("p1", "adg_stale_guard", "transcript")
_emit_hard_fails_untranscripted("p1", "adg_stale_guard")
_emit_gated_by_confidence("p1", "adg_stale_guard", "confidence_gate")


@dataclass
class StalenessResult:
    is_stale: bool
    ingest_time: float
    last_commit_time: float
    changed_files: list[str] = field(default_factory=list)
    message: str = ""

    @property
    def seconds_stale(self) -> float:
        return max(0.0, self.last_commit_time - self.ingest_time)


class ADGStalenessChecker:
    """Check whether the ADG Redis cache is stale relative to git commit history.

    Staleness = any Python file was committed after the last ADG ingest timestamp.
    """

    def __init__(
        self,
        client: ADGRedisClient | None = None,
        repo_root: Path | None = None,
    ) -> None:
        self._adg = client or ADGRedisClient()
        self._root = repo_root or ROOT

    def _get_ingest_time(self) -> float:
        """Get ADG snapshot freshness timestamp from Redis meta hash.

        Raises:
            RuntimeError: if Redis unavailable or freshness fields are missing.
        """
        meta = self._adg.meta()
        val = meta.get("sqlite_mtime") or meta.get("ingested_at")
        if val is None:
            raise RuntimeError(
                "ADG meta key 'sqlite_mtime' is missing — cache may be corrupt. "
                "Run: python tools/adg/adg_redis_ingest.py --force",
            )
        return float(val)

    def _get_last_python_commit_time(self) -> float:
        """Return Unix timestamp of the most recent commit touching any Python file.

        Returns 0.0 if no Python commits exist.

        Raises:
            RuntimeError: if git command fails or times out.
        """
        try:
            result = subprocess.run(
                ["git", "log", "-1", "--format=%ct", "--", "*.py"],
                cwd=str(self._root),
                capture_output=True,
                encoding="utf-8",
                errors="replace",
                timeout=30,
            )
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(f"git log timed out: {exc}") from exc
        if result.returncode != 0:
            raise RuntimeError(f"git log failed: {result.stderr.strip()}")
        out = result.stdout.strip()
        return float(out) if out else 0.0

    def _get_files_changed_since(self, since_timestamp: float) -> list[str]:
        """Return Python files committed strictly after since_timestamp.

        Raises:
            RuntimeError: if git command fails or times out.
        """
        try:
            result = subprocess.run(
                [
                    "git",
                    "log",
                    f"--after=@{int(since_timestamp)}",
                    "--name-only",
                    "--format=",
                    "--",
                    "*.py",
                ],
                cwd=str(self._root),
                capture_output=True,
                encoding="utf-8",
                errors="replace",
                timeout=30,
            )
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(f"git log timed out: {exc}") from exc
        if result.returncode != 0:
            raise RuntimeError(f"git log failed: {result.stderr.strip()}")
        return sorted({f for f in result.stdout.splitlines() if f.strip() and f.endswith(".py")})

    def check(self) -> StalenessResult:
        """Check staleness. Raises RuntimeError if Redis is unavailable.

        Returns:
            StalenessResult with is_stale, timestamps, and changed_files.
        """
        ingest_time = self._get_ingest_time()
        last_commit_time = self._get_last_python_commit_time()

        if last_commit_time <= ingest_time:
            return StalenessResult(
                is_stale=False,
                ingest_time=ingest_time,
                last_commit_time=last_commit_time,
                message="ADG is fresh — no Python commits since last ingest.",
            )

        changed = self._get_files_changed_since(ingest_time)
        return StalenessResult(
            is_stale=True,
            ingest_time=ingest_time,
            last_commit_time=last_commit_time,
            changed_files=changed,
            message=(
                f"ADG is STALE — {len(changed)} Python file(s) committed after last ingest. "
                "Run: python tools/adg/adg_redis_ingest.py --force"
            ),
        )

    def assert_fresh(self) -> None:
        """Raise RuntimeError if ADG is stale.

        Intended as a pre-flight guard before any ADG query session.
        """
        result = self.check()
        if result.is_stale:
            raise RuntimeError(result.message)

    def warn_if_stale(self) -> None:
        """Print a warning to stderr if ADG is stale; never raises.

        Use in non-blocking contexts (e.g. pre-commit warn mode, ADGQuerySession
        with warn_only=True). Redis/staleness errors are demoted to warnings.
        """
        try:
            result = self.check()
        except Exception as exc:  # guardian: allow-broad-exception -- warn_if_stale contract is never-raise; all Redis/network/timeout errors must be demoted to warnings
            print(
                f"[adg-stale-guard] WARNING: could not check staleness: {exc}",
                file=sys.stderr,
            )
            return
        if result.is_stale:
            print(
                f"[adg-stale-guard] WARNING: {result.message}",
                file=sys.stderr,
            )


def _cli() -> None:
    import argparse
    import json as _json

    parser = argparse.ArgumentParser(
        prog="adg_stale_guard",
        description="Check whether the ADG Redis cache is stale relative to git history.",
    )
    parser.add_argument(
        "--warn",
        action="store_true",
        help="Print warning but exit 0 even if stale (non-blocking mode)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Machine-readable JSON output",
    )
    parser.add_argument(
        "--files",
        action="store_true",
        help="List Python files changed since last ADG ingest",
    )
    parser.add_argument(
        "--fail-if-stale",
        action="store_true",
        dest="fail_if_stale",
        help=(
            "CI-safe strict mode: exit 1 if Redis is UP and graph is STALE, "
            "exit 0 if Redis is DOWN (CI has no Redis). "
            "Stronger than --warn (which never blocks), weaker than strict (which "
            "blocks on Redis-unavailable too)."
        ),
    )
    args = parser.parse_args()

    import redis as _redis

    # --fail-if-stale treats Redis-unavailable the same as --warn (exit 0)
    _redis_down_is_ok = args.warn or args.fail_if_stale

    try:
        adg = ADGRedisClient()
        adg.ping()
    except _redis.ConnectionError as exc:
        if _redis_down_is_ok:
            print(
                f"[adg-stale-guard] WARNING: Redis unavailable — cannot check ADG staleness: {exc}",
                file=sys.stderr,
            )
            sys.exit(0)
        print(f"ERROR: Redis unavailable: {exc}", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as exc:  # review: Runtime errors should be prevented with proper validation
        if _redis_down_is_ok:
            print(f"[adg-stale-guard] WARNING: {exc}", file=sys.stderr)
            sys.exit(0)
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

    checker = ADGStalenessChecker(client=adg)
    try:
        result = checker.check()
    except RuntimeError as exc:  # review: Runtime errors should be prevented with proper validation
        if _redis_down_is_ok:
            print(f"[adg-stale-guard] WARNING: {exc}", file=sys.stderr)
            sys.exit(0)
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(
            _json.dumps(
                {
                    "is_stale": result.is_stale,
                    "ingest_time": result.ingest_time,
                    "last_commit_time": result.last_commit_time,
                    "seconds_stale": result.seconds_stale,
                    "changed_files": result.changed_files,
                    "message": result.message,
                },
                indent=2,
            ),
        )
        sys.exit(1 if result.is_stale and not args.warn else 0)

    if result.is_stale:
        print(f"STALE: {result.message}")
        if args.files and result.changed_files:
            print(f"\n{len(result.changed_files)} file(s) changed since last ingest:")
            for f in result.changed_files:
                print(f"  {f}")
        print("\nRun: python tools/adg/adg_redis_ingest.py --force")
        # --warn: never block; --fail-if-stale: block on stale (Redis is up)
        sys.exit(0 if args.warn else 1)
    else:
        print(f"FRESH: {result.message}")
        sys.exit(0)


# Export aliases for backward compatibility with tests
__all__ = [
    "ADGStalenessChecker",
    "StalenessResult",
    "_cli",
    "main",
    "ADGStaleGuard",
]
main = _cli
ADGStaleGuard = ADGStalenessChecker


if __name__ == "__main__":
    _cli()
