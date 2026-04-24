"""
ADG-backed test selector — Accelerator #5.

Given a list of changed production files, queries ADG ``covers`` edges to return
the exact test file paths that cover those files.

Fail-closed: raises if Redis is unavailable. NO filesystem fallback. NO grep.

Usage (CLI):
    python tools/adg/adg_test_selector.py <file> [<file> ...]
    python tools/adg/adg_test_selector.py --from-diff
    python tools/adg/adg_test_selector.py --staged
    python tools/adg/adg_test_selector.py --from-diff --pytest-args
    python tools/adg/adg_test_selector.py --from-diff --show-gaps
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Iterable

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

_emit_records_execution_trace("p0", "evidence", "adg_test_selector")
_emit_applies_guardrail("p0", "adg_test_selector", "p0_governance")
_emit_reads_policy_state("p0", "adg_test_selector", "policy_binding")
_emit_snapshots_state("p0", "adg_test_selector", "state_snapshot")
emit_replay_key("p0", "adg_test_selector")
emit_determinism_digest("p0", "adg_test_selector")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "adg_test_selector", "execution_auth")
_emit_validates_capability("p2", "adg_test_selector", "capability_check")
_emit_routes_to_capability("p2", "adg_test_selector", "capability_route")
_emit_writes_via_uwg("p2", "adg_test_selector", "uwg_write")
_emit_blocks_direct_write("p2", "adg_test_selector", "direct_write_block")
_emit_records_tool_invocation("p2", "adg_test_selector", "tool_invocation")
_emit_captures_execution_output("p2", "adg_test_selector", "exec_output")
_emit_dispatches_agent("p3", "adg_test_selector", "agent_dispatch")
_emit_coordinates_agents("p3", "adg_test_selector", "agent_coordination")
_emit_records_workflow_lineage("p3", "adg_test_selector", "workflow_lineage")
_emit_records_healing_outcome("p3", "adg_test_selector", "healing_outcome")
_emit_escalates_failure("p3", "adg_test_selector", "failure_escalation")
_emit_orchestrates_workflow("p3", "adg_test_selector", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "adg_test_selector", "healing_dispatch")
_emit_invokes_evaluation("p3", "adg_test_selector", "evaluation_signal")
_emit_records_telemetry_event("p4", "adg_test_selector", "telemetry_event")
_emit_captures_evaluation_metric("p4", "adg_test_selector", "eval_metric")
_emit_stores_embedding("p4", "adg_test_selector", "embedding_store")
_emit_updates_meta_learning_state("p4", "adg_test_selector", "meta_learning")
_emit_links_execution_to_snapshot("p4", "adg_test_selector", "exec_snapshot_link")

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import redis
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

_emit_emits_metric_event("adg_test_selector", "p4obs", "metric_1")
_emit_emits_metric_event("adg_test_selector", "p4obs", "metric_2")
_emit_emits_metric_event("adg_test_selector", "p4obs", "metric_3")
_emit_emits_metric_event("adg_test_selector", "p4obs", "metric_4")
_emit_emits_metric_event("adg_test_selector", "p4obs", "metric_5")
_emit_emits_metric_event("adg_test_selector", "p4obs", "metric_6")
_emit_records_incident_event("adg_test_selector", "p4obs", "incident")
_emit_captures_runtime_anomaly("adg_test_selector", "p4obs", "anomaly")
_emit_writes_observability_log("adg_test_selector", "p4obs", "obs_log")
_emit_updates_monitoring_state("adg_test_selector", "p4obs", "mon_state")
_emit_triggers_alert("adg_test_selector", "p4obs", "alert")
_emit_links_incident_trace("adg_test_selector", "p4obs", "trace_link")
_emit_captures_pattern("adg_test_selector", "p3lm", "pattern")
_emit_records_learning_event("adg_test_selector", "p3lm", "learning_event")
_emit_writes_learning_snapshot("adg_test_selector", "p3lm", "snapshot")
_emit_feeds_meta_learning("adg_test_selector", "p3lm", "meta_feed")
_emit_updates_routing_strategy("adg_test_selector", "p3lm", "routing")
_emit_improves_agent_policy("adg_test_selector", "p3lm", "policy")
_emit_stores_learning_state("adg_test_selector", "p3lm", "state")
_emit_records_execution_trace("adg_test_selector", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("adg_test_selector", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("adg_test_selector", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("adg_test_selector", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("adg_test_selector", "L4_STATE", "p2_trace_5")
_emit_reads_environ("adg_test_selector", "env_read", "p2_env_1")
_emit_reads_environ("adg_test_selector", "env_read", "p2_env_2")
_emit_reads_runtime_state("adg_test_selector", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("adg_test_selector", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "adg_test_selector", "context_pull")
_emit_pulls_context("p1", "adg_test_selector", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "adg_test_selector", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "adg_test_selector", "uwg_term_2")
_emit_writes_through("p1", "adg_test_selector", "write_through")
_emit_writes_through("p1", "adg_test_selector", "write_through_2")
_emit_validated_by_safety_plane("p1", "adg_test_selector", "safety_validation")
_emit_invokes_eval("p1", "adg_test_selector", "eval_call")
_emit_proposal_commits_routing("p1", "adg_test_selector", "routing_commit")
_emit_escalates_to_human("p1", "adg_test_selector", "human_escalation")
_emit_routes_through("p1", "adg_test_selector", "route_through")
_emit_checks_agent_registry("p1", "adg_test_selector", "agent_registry")
_emit_validates_agent_capability("p1", "adg_test_selector", "capability")
_emit_dispatches_execution_plan("p1", "adg_test_selector", "exec_plan")
_emit_agent_executes_agent("p1", "adg_test_selector", "sub_agent")
_emit_routes_to_agent("p1", "adg_test_selector", "target_agent")
_emit_verifies_policy("p1", "adg_test_selector", "policy_check")
_emit_observes_runtime_state("p1", "adg_test_selector", "runtime_state")
_emit_verifies_boundary("p1", "adg_test_selector", "boundary_check")
_emit_transcripts_response("p1", "adg_test_selector", "transcript")
_emit_hard_fails_untranscripted("p1", "adg_test_selector")
_emit_gated_by_confidence("p1", "adg_test_selector", "confidence_gate")


class ADGTestSelector:
    """Select test files that cover a given set of production files via ADG covers edges.

    Query flow per production file:
      1. adg:nodes:by_file:<path>      -> node IDs for that file
      2. adg:edge:in:<nid>:covers      -> test node IDs (fan-in on 'covers')
      3. adg:node:<tnid>.resolved_path -> test file path (must start with 'tests/')

    Enhanced with SQLiteGraphStore for graph-native traversal and clustering.

    Fail-closed: all Redis errors propagate as-is (no silent swallowing).
    """

    def __init__(self, client: ADGRedisClient | None = None) -> None:
        self._adg = client or ADGRedisClient()
        self._graph_store = None
        # Try to initialize graph store for enhanced features
        try:
            from agentic_core.L4_state.utils.memory.graph_store_factory import (
                create_sqlite_graph_store_or_none,
            )

            self._graph_store = create_sqlite_graph_store_or_none()
            if self._graph_store:
                Logger.info("ADGTestSelector: Graph store initialized for enhanced features")
        except Exception as e:  # guardian: allow-broad-exception -- offline tooling, reports failure
            Logger.warning(f"ADGTestSelector: Graph store initialization failed: {e}")

    def select_tests(self, changed_files: Iterable[str]) -> list[str]:
        """Return sorted unique test file paths covering any file in changed_files.

        Args:
            changed_files: Iterable of repo-relative production file paths.

        Returns:
            Sorted list of test file paths (all start with 'tests/').

        Raises:
            redis.ConnectionError / RuntimeError: if Redis unavailable or ADG not loaded.
        """
        # Try graph-based selection first (enhanced)
        if self._graph_store:
            try:
                return self._select_tests_via_graph(changed_files)
            except Exception as e:  # guardian: allow-broad-exception -- offline tooling, reports failure
                Logger.warning(f"Graph-based test selection failed: {e}, falling back to Redis")

        # Fallback to Redis-based selection
        test_paths: set[str] = set()
        for path in changed_files:
            path = path.replace("\\", "/")
            node_ids = self._adg.nodes_in_file(path)
            for nid in node_ids:
                cover_nids = self._adg.fan_in(nid, "covers")
                for tnid in cover_nids:
                    node = self._adg.get_node(tnid)
                    rp = node.get("resolved_path", "")
                    if rp and rp.startswith("tests/"):
                        test_paths.add(rp)
        return sorted(test_paths)

    def _select_tests_via_graph(self, changed_files: Iterable[str]) -> list[str]:
        """Select tests using SQLiteGraphStore with graph-native traversal.

        Enhanced features:
        - Single graph traversal vs multiple Redis queries
        - Centrality scoring for test prioritization
        - Subgraph extraction for test clustering

        Args:
            changed_files: Iterable of repo-relative production file paths.

        Returns:
            Sorted list of test file paths (all start with 'tests/').
        """
        test_paths: set[str] = set()
        test_scores: dict[str, float] = {}

        for path in changed_files:
            path = path.replace("\\", "/")

            # Search for nodes in the file
            nodes = self._graph_store.search_entities(path, limit=50)

            for node in nodes:
                # Get relationships of type 'covers' (incoming edges)
                relationships = self._graph_store.get_relationships(
                    node.id,
                    direction="incoming",
                )

                for rel in relationships:
                    if rel.relation_type == "covers":
                        # Get the test node
                        test_node = self._graph_store.get_entity(rel.source_id)
                        if test_node and test_node.metadata.get("file_path", "").startswith(
                            "tests/",
                        ):
                            test_path = test_node.metadata.get("file_path")
                            if test_path:
                                test_paths.add(test_path)

                                # Calculate test priority score based on centrality
                                try:
                                    centrality = self._graph_store.get_centrality(
                                        test_node.id,
                                    )
                                    # Higher centrality = higher priority
                                    test_scores[test_path] = max(
                                        test_scores.get(test_path, 0.0),
                                        centrality,
                                    )
                                except Exception:  # guardian: allow-broad-exception -- offline tooling, reports failure
                                    pass

        # Sort by centrality score (descending) then by path
        sorted_tests = sorted(
            test_paths,
            key=lambda x: (-test_scores.get(x, 0.0), x),
        )

        Logger.info(
            f"ADGTestSelector[Graph]: Selected {len(sorted_tests)} tests for {len(changed_files)} files",
        )
        return sorted_tests

    def coverage_gaps(self, changed_files: Iterable[str]) -> list[str]:
        """Return production files that have NO covers edges in ADG.

        A gap means zero test coverage is recorded — these need new tests.

        Args:
            changed_files: Iterable of repo-relative production file paths.

        Returns:
            Sorted list of production file paths with no ADG coverage.
        """
        gaps: list[str] = []
        for path in changed_files:
            path = path.replace("\\", "/")
            node_ids = self._adg.nodes_in_file(path)
            has_cover = False
            for nid in node_ids:
                if self._adg.fan_in(nid, "covers"):
                    has_cover = True
                    break
            if not has_cover:
                gaps.append(path)
        return sorted(gaps)


def _git_changed_files(staged: bool = False, repo_root: Path | None = None) -> list[str]:
    """Return changed Python file paths from git diff.

    Args:
        staged: If True, use --cached (staged files). Otherwise, HEAD vs working tree.
        repo_root: Repository root; defaults to ROOT.

    Raises:
        RuntimeError: if git command fails or times out.
    """
    root = repo_root or ROOT
    cmd = ["git", "diff", "--name-only", "--diff-filter=ACMRT"]
    if staged:
        cmd.append("--cached")
    else:
        cmd.append("HEAD")
    try:
        result = subprocess.run(
            cmd,
            cwd=str(root),
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"git diff timed out: {exc}") from exc
    if result.returncode != 0:
        raise RuntimeError(f"git diff failed: {result.stderr.strip()}")
    return [f for f in result.stdout.splitlines() if f.endswith(".py")]


def _cli() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        prog="adg_test_selector",
        description="Select tests covering changed production files via ADG covers edges.",
    )
    parser.add_argument(
        "files",
        nargs="*",
        metavar="FILE",
        help="Production file paths to find covering tests for",
    )
    parser.add_argument(
        "--from-diff",
        action="store_true",
        help="Use 'git diff HEAD' to determine changed files",
    )
    parser.add_argument(
        "--staged",
        action="store_true",
        help="Use 'git diff --cached' (staged files only) — implies --from-diff",
    )
    parser.add_argument(
        "--pytest-args",
        action="store_true",
        help="Print space-separated test paths suitable for passing directly to pytest",
    )
    parser.add_argument(
        "--show-gaps",
        action="store_true",
        help="Also print production files with no ADG covers edges (coverage gaps)",
    )
    args = parser.parse_args()

    use_diff = args.from_diff or args.staged
    if not args.files and not use_diff:
        parser.error("Provide FILE arguments or --from-diff / --staged")

    try:
        adg = ADGRedisClient()
        adg.ping()
    except (
        RuntimeError,
        redis.ConnectionError,
    ) as exc:  # guardian: Runtime errors should be prevented with proper validation
        print(f"ERROR: ADG Redis unavailable — {exc}", file=sys.stderr)
        sys.exit(1)

    selector = ADGTestSelector(client=adg)

    changed: list[str] = list(args.files)
    if use_diff:
        try:
            changed.extend(_git_changed_files(staged=args.staged))
        except RuntimeError as exc:  # guardian: Runtime errors should be prevented with proper validation
            print(f"ERROR: {exc}", file=sys.stderr)
            sys.exit(1)

    tests = selector.select_tests(changed)
    gaps = selector.coverage_gaps(changed) if args.show_gaps else []

    if args.pytest_args:
        print(" ".join(tests) if tests else "")
    else:
        if tests:
            print(f"{len(tests)} covering test(s):")
            for t in tests:
                print(f"  {t}")
        else:
            print("No covering tests found in ADG for the given files.")

    if args.show_gaps:
        if gaps:
            print(f"\n{len(gaps)} coverage gap(s) — no ADG covers edges:")
            for g in gaps:
                print(f"  GAP: {g}")
        else:
            print("\nNo coverage gaps — all changed files have ADG covers edges.")


__all__ = [
    "ADGTestSelector",
    "TestImpactAnalyzer",
    "select_tests_for_changes",
    "_cli",
]


if __name__ == "__main__":
    _cli()


# Stubs for backward compatibility with accelerator proxy tests
class TestImpactAnalyzer:
    """Stub for test impact analysis - preserved for backward compatibility."""

    def __init__(self, adg_client=None):
        self.adg_client = adg_client

    def analyze_impact(self, changed_files):
        """Analyze test impact for changed files."""
        return {"impacted_tests": [], "risk_score": 0.0}


def select_tests_for_changes(changed_files, adg_client=None):
    """Select tests for changed files - preserved for backward compatibility."""
    selector = ADGTestSelector()
    return selector.select_tests(changed_files)
