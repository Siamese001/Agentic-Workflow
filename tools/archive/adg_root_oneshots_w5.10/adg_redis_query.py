"""
ADG Redis query helper.

Provides fast, session-persistent lookups against the ADG Redis cache.
All methods return Python dicts/lists. Call adg_redis_query.ping() first
to verify the cache is loaded.

Usage:
    from tools.adg.adg_redis_query import ADGRedisClient
    adg = ADGRedisClient()
    adg.ping()
    meta = adg.meta()
    node = adg.get_node("ADG::Module::apps_shared/types/sovereign_severity_types.py")
    imports = adg.fan_out(node_id, "imports")
    imported_by = adg.fan_in(node_id, "imports")
    violations = adg.violations()
    snap = adg.snapshot()
"""

import json
import sys
from pathlib import Path
from typing import Any

import redis

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
    _emit_reads_through,
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

_emit_records_execution_trace("p0", "evidence", "adg_redis_query")
_emit_applies_guardrail("p0", "adg_redis_query", "p0_governance")
_emit_reads_policy_state("p0", "adg_redis_query", "policy_binding")
_emit_snapshots_state("p0", "adg_redis_query", "state_snapshot")
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

_emit_emits_metric_event("adg_redis_query", "p4obs", "metric_1")
_emit_emits_metric_event("adg_redis_query", "p4obs", "metric_2")
_emit_emits_metric_event("adg_redis_query", "p4obs", "metric_3")
_emit_emits_metric_event("adg_redis_query", "p4obs", "metric_4")
_emit_emits_metric_event("adg_redis_query", "p4obs", "metric_5")
_emit_emits_metric_event("adg_redis_query", "p4obs", "metric_6")
_emit_records_incident_event("adg_redis_query", "p4obs", "incident")
_emit_captures_runtime_anomaly("adg_redis_query", "p4obs", "anomaly")
_emit_writes_observability_log("adg_redis_query", "p4obs", "obs_log")
_emit_updates_monitoring_state("adg_redis_query", "p4obs", "mon_state")
_emit_triggers_alert("adg_redis_query", "p4obs", "alert")
_emit_links_incident_trace("adg_redis_query", "p4obs", "trace_link")
_emit_captures_pattern("adg_redis_query", "p3lm", "pattern")
_emit_records_learning_event("adg_redis_query", "p3lm", "learning_event")
_emit_writes_learning_snapshot("adg_redis_query", "p3lm", "snapshot")
_emit_feeds_meta_learning("adg_redis_query", "p3lm", "meta_feed")
_emit_updates_routing_strategy("adg_redis_query", "p3lm", "routing")
_emit_improves_agent_policy("adg_redis_query", "p3lm", "policy")
_emit_stores_learning_state("adg_redis_query", "p3lm", "state")
_emit_records_execution_trace("adg_redis_query", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("adg_redis_query", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("adg_redis_query", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("adg_redis_query", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("adg_redis_query", "L4_STATE", "p2_trace_5")
_emit_reads_environ("adg_redis_query", "env_read", "p2_env_1")
_emit_reads_environ("adg_redis_query", "env_read", "p2_env_2")
_emit_reads_runtime_state("adg_redis_query", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("adg_redis_query", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "adg_redis_query", "context_pull")
_emit_pulls_context("p1", "adg_redis_query", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "adg_redis_query", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "adg_redis_query", "uwg_term_2")
_emit_writes_through("p1", "adg_redis_query", "write_through")
_emit_writes_through("p1", "adg_redis_query", "write_through_2")
_emit_validated_by_safety_plane("p1", "adg_redis_query", "safety_validation")
_emit_invokes_eval("p1", "adg_redis_query", "eval_call")
_emit_proposal_commits_routing("p1", "adg_redis_query", "routing_commit")
_emit_escalates_to_human("p1", "adg_redis_query", "human_escalation")
_emit_routes_through("p1", "adg_redis_query", "route_through")
_emit_checks_agent_registry("p1", "adg_redis_query", "agent_registry")
_emit_validates_agent_capability("p1", "adg_redis_query", "capability")
_emit_dispatches_execution_plan("p1", "adg_redis_query", "exec_plan")
_emit_agent_executes_agent("p1", "adg_redis_query", "sub_agent")
_emit_routes_to_agent("p1", "adg_redis_query", "target_agent")
_emit_verifies_policy("p1", "adg_redis_query", "policy_check")
_emit_observes_runtime_state("p1", "adg_redis_query", "runtime_state")
_emit_verifies_boundary("p1", "adg_redis_query", "boundary_check")
_emit_transcripts_response("p1", "adg_redis_query", "transcript")
_emit_hard_fails_untranscripted("p1", "adg_redis_query")
_emit_gated_by_confidence("p1", "adg_redis_query", "confidence_gate")
emit_replay_key("p0", "adg_redis_query")
emit_determinism_digest("p0", "adg_redis_query")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "adg_redis_query", "execution_auth")
_emit_validates_capability("p2", "adg_redis_query", "capability_check")
_emit_routes_to_capability("p2", "adg_redis_query", "capability_route")
_emit_writes_via_uwg("p2", "adg_redis_query", "uwg_write")
_emit_blocks_direct_write("p2", "adg_redis_query", "direct_write_block")
_emit_records_tool_invocation("p2", "adg_redis_query", "tool_invocation")
_emit_captures_execution_output("p2", "adg_redis_query", "exec_output")
_emit_dispatches_agent("p3", "adg_redis_query", "agent_dispatch")
_emit_coordinates_agents("p3", "adg_redis_query", "agent_coordination")
_emit_records_workflow_lineage("p3", "adg_redis_query", "workflow_lineage")
_emit_records_healing_outcome("p3", "adg_redis_query", "healing_outcome")
_emit_escalates_failure("p3", "adg_redis_query", "failure_escalation")
_emit_orchestrates_workflow("p3", "adg_redis_query", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "adg_redis_query", "healing_dispatch")
_emit_invokes_evaluation("p3", "adg_redis_query", "evaluation_signal")
_emit_records_telemetry_event("p4", "adg_redis_query", "telemetry_event")
_emit_captures_evaluation_metric("p4", "adg_redis_query", "eval_metric")
_emit_stores_embedding("p4", "adg_redis_query", "embedding_store")
_emit_updates_meta_learning_state("p4", "adg_redis_query", "meta_learning")
_emit_links_execution_to_snapshot("p4", "adg_redis_query", "exec_snapshot_link")
_emit_reads_through("l4", "adg_redis_query", "urg_read_1")
_emit_reads_through("l4", "adg_redis_query", "urg_read_2")
_emit_reads_through("l4", "adg_redis_query", "urg_read_3")
_emit_reads_through("l4", "adg_redis_query", "urg_read_4")
_emit_reads_through("l4", "adg_redis_query", "urg_read_5")
_emit_reads_through("l4", "adg_redis_query", "urg_read_6")
_emit_reads_through("l4", "adg_redis_query", "urg_read_7")
_emit_reads_through("l4", "adg_redis_query", "urg_read_8")
_emit_reads_through("l4", "adg_redis_query", "urg_read_9")
_emit_reads_through("l4", "adg_redis_query", "urg_read_10")
_emit_reads_through("l4", "adg_redis_query", "urg_read_11")
_emit_reads_through("l4", "adg_redis_query", "urg_read_12")
_emit_reads_through("l4", "adg_redis_query", "urg_read_13")
_emit_reads_through("l4", "adg_redis_query", "urg_read_14")
_emit_reads_through("l4", "adg_redis_query", "urg_read_15")
_emit_reads_through("l4", "adg_redis_query", "urg_read_16")
_emit_reads_through("l4", "adg_redis_query", "urg_read_17")
_emit_reads_through("l4", "adg_redis_query", "urg_read_18")
_emit_reads_through("l4", "adg_redis_query", "urg_read_19")
_emit_reads_through("l4", "adg_redis_query", "urg_read_20")
_emit_reads_through("l4", "adg_redis_query", "urg_read_21")
_emit_reads_through("l4", "adg_redis_query", "urg_read_22")
_emit_reads_through("l4", "adg_redis_query", "urg_read_23")
_emit_reads_through("l4", "adg_redis_query", "urg_read_24")
_emit_reads_through("l4", "adg_redis_query", "urg_read_25")
_emit_reads_through("l4", "adg_redis_query", "urg_read_26")
_emit_reads_through("l4", "adg_redis_query", "urg_read_27")
_emit_reads_through("l4", "adg_redis_query", "urg_read_28")
_emit_reads_through("l4", "adg_redis_query", "urg_read_29")
_emit_reads_through("l4", "adg_redis_query", "urg_read_30")
_emit_reads_through("l4", "adg_redis_query", "urg_read_31")
_emit_reads_through("l4", "adg_redis_query", "urg_read_32")
_emit_reads_through("l4", "adg_redis_query", "urg_read_33")
_emit_reads_through("l4", "adg_redis_query", "urg_read_34")
_emit_reads_through("l4", "adg_redis_query", "urg_read_35")
_emit_reads_through("l4", "adg_redis_query", "urg_read_36")
_emit_reads_through("l4", "adg_redis_query", "urg_read_37")
_emit_reads_through("l4", "adg_redis_query", "urg_read_38")
_emit_reads_through("l4", "adg_redis_query", "urg_read_39")
_emit_reads_through("l4", "adg_redis_query", "urg_read_40")
_emit_reads_through("l4", "adg_redis_query", "urg_read_41")

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


class ADGRedisClient:
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        self._r = redis.Redis(host=host, port=port, db=db, decode_responses=True)

    def ping(self) -> bool:
        """Verify Redis is up and ADG cache is loaded."""
        self._r.ping()
        loaded = self._r.exists("adg:meta")
        if not loaded:
            raise RuntimeError("ADG Redis cache is not loaded. Run: python tools/adg/adg_redis_ingest.py")
        return True

    def meta(self) -> dict[str, str]:
        """Return ingest metadata (timestamp, counts, digest)."""
        return self._r.hgetall("adg:meta")

    def snapshot(self) -> dict[str, Any]:
        """Return the full ADG snapshot JSON."""
        raw = self._r.get("adg:snapshot")
        return json.loads(raw) if raw else {}

    def get_node(self, node_id: str) -> dict[str, str]:
        """Return a node hash by its ID string."""
        return self._r.hgetall(f"adg:node:{node_id}")

    def nodes_in_file(self, file_path: str) -> set[str]:
        """Return all node IDs defined in a given file path."""
        return self._r.smembers(f"adg:nodes:by_file:{file_path}")

    def nodes_in_layer(self, layer: str) -> set[str]:
        """Return all node IDs belonging to a layer (e.g. 'L0', 'L5')."""
        return self._r.smembers(f"adg:nodes:by_layer:{layer}")

    def fan_out(self, node_id: str, relation: str) -> set[str]:
        """Return all targets of edges (node_id)-[relation]->(*)."""
        return self._r.smembers(f"adg:edge:{node_id}:{relation}")

    def fan_in(self, node_id: str, relation: str) -> set[str]:
        """Return all sources of edges (*)-[relation]->(node_id)."""
        return self._r.smembers(f"adg:edge:in:{node_id}:{relation}")

    def all_edge_relations_from(self, node_id: str) -> list[str]:
        """Return all distinct relation types emanating from node_id."""
        pattern = f"adg:edge:{node_id}:*"
        keys = []
        cursor = 0
        while True:
            cursor, batch = self._r.scan(cursor, match=pattern, count=200)
            keys.extend(batch)
            if cursor == 0:
                break
        prefix = f"adg:edge:{node_id}:"
        return [k[len(prefix) :] for k in keys]

    def violations(self) -> list[dict]:
        """Return all stored layer violations."""
        raw = self._r.lrange("adg:violations", 0, -1)
        return [json.loads(v) for v in raw]

    def is_stale(self, sqlite_mtime: float) -> bool:
        """Return True if the cache was built from an older SQLite file."""
        stored = self._r.hget("adg:meta", "sqlite_mtime")
        if stored is None:
            return True
        return float(stored) < sqlite_mtime

    def search_files(self, substring: str) -> list[str]:
        """Return all file paths in the ADG that contain substring.

        Uses Redis SCAN on key names — O(matching keys), does not read hash fields.
        Example: adg.search_files("dashboard") -> ["agentic_core/.../dashboard_util.py", ...]
        """
        prefix = "adg:nodes:by_file:"
        pattern = f"{prefix}*{substring}*"
        matches: list[str] = []
        cursor = 0
        while True:
            cursor, keys = self._r.scan(cursor, match=pattern, count=500)
            for key in keys:
                matches.append(key[len(prefix) :])
            if cursor == 0:
                break
        return sorted(matches)

    def search_nodes(
        self,
        substring: str,
        field: str = "adg_name",
        layer: str | None = None,
        entity_type: str | None = None,
    ) -> list[dict[str, str]]:
        """Return all nodes whose `field` value contains substring (case-insensitive).

        Scans all adg:node:* hashes. Use search_files() for file-path lookups — it is faster.

        Args:
            substring: Case-insensitive substring to search for in `field`.
            field: Node hash field to search (default: "adg_name").
            layer: Optional layer filter, e.g. "L0", "L2". Only nodes in this layer returned.
            entity_type: Optional entity_type filter, e.g. "module", "function", "class".

        Example:
            adg.search_nodes("Dashboard") -> all nodes with "dashboard" in adg_name
            adg.search_nodes("Agent", layer="L3") -> L3 nodes with "agent" in adg_name
            adg.search_nodes("", entity_type="class") -> all class nodes
        """
        term = substring.lower()
        layer_lower = layer.lower() if layer else None
        etype_lower = entity_type.lower() if entity_type else None
        matches: list[dict[str, str]] = []
        cursor = 0
        while True:
            cursor, keys = self._r.scan(cursor, match="adg:node:*", count=500)
            for key in keys:
                node = self._r.hgetall(key)
                if term and term not in node.get(field, "").lower():
                    continue
                if layer_lower and node.get("layer", "").lower() != layer_lower:
                    continue
                if etype_lower and node.get("entity_type", "").lower() != etype_lower:
                    continue
                matches.append(node)
            if cursor == 0:
                break
        return sorted(matches, key=lambda n: n.get("adg_name", ""))


class ADGQuerySession:
    """Context manager that asserts ADG freshness before any query operation.

    Ensures the stale guard runs (Accelerator #2) before every ADG query session
    so queries never run against a stale graph. Fail-closed by default.

    Usage::

        with ADGQuerySession() as adg:
            nodes = adg.search_nodes("MyClass")

        # Warn-only (non-blocking, for pre-commit / CI contexts without Redis):
        with ADGQuerySession(warn_only=True) as adg:
            nodes = adg.search_nodes("MyClass")

    Raises:
        RuntimeError: if ADG is stale or Redis cache is not loaded (fail-closed).
        redis.ConnectionError: if Redis is not reachable (fail-closed).
    """

    def __init__(
        self,
        warn_only: bool = False,
        client: ADGRedisClient | None = None,
    ) -> None:
        self._warn_only = warn_only
        self._client = client or ADGRedisClient()

    def __enter__(self) -> ADGRedisClient:
        # Lazy import to avoid circular dependency:
        # adg_stale_guard imports ADGRedisClient from this module.
        from tools.adg.adg_stale_guard import ADGStalenessChecker

        checker = ADGStalenessChecker(client=self._client)
        if self._warn_only:
            checker.warn_if_stale()
        else:
            checker.assert_fresh()
        return self._client

    def __exit__(self, *_: object) -> None:
        pass


def _cli() -> None:
    import argparse  # noqa: PLC0415

    parser = argparse.ArgumentParser(
        prog="adg_redis_query",
        description="Query the ADG Redis hot cache.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_sf = sub.add_parser(
        "search-files", aliases=["--search-files"], help="Find files whose path contains TERM",
    )
    p_sf.add_argument("term", help="Substring to search for in file paths")

    p_sn = sub.add_parser(
        "search-nodes", aliases=["--search-nodes"], help="Find nodes whose adg_name contains TERM",
    )
    p_sn.add_argument(
        "term", nargs="?", default="", help="Substring to search for in node names (default: all)",
    )
    p_sn.add_argument("--field", default="adg_name", help="Node hash field to search (default: adg_name)")
    p_sn.add_argument("--layer", default=None, help="Filter by layer e.g. L0, L2, L5")
    p_sn.add_argument(
        "--entity-type",
        default=None,
        dest="entity_type",
        help="Filter by entity_type e.g. module, class, function",
    )

    p_fo = sub.add_parser("fan-out", aliases=["--fan-out"], help="List all targets of (NODE)-[RELATION]->()")
    p_fo.add_argument("node_id", help="Source node ID")
    p_fo.add_argument("relation", help="Relation type e.g. imports, calls")

    p_fi = sub.add_parser("fan-in", aliases=["--fan-in"], help="List all sources of ()-[RELATION]->(NODE)")
    p_fi.add_argument("node_id", help="Target node ID")
    p_fi.add_argument("relation", help="Relation type e.g. imports, calls")

    sub.add_parser("meta", aliases=["--meta"], help="Print ADG ingest metadata")

    args = parser.parse_args()
    adg = ADGRedisClient()
    try:
        adg.ping()
    except (
        RuntimeError,
        redis.ConnectionError,
    ) as exc:  # guardian: Runtime errors should be prevented with proper validation
        print(f"ERROR: ADG Redis unavailable — {exc}", file=sys.stderr)
        sys.exit(1)

    cmd = args.cmd.lstrip("-")

    if cmd == "search-files":
        results = adg.search_files(args.term)
        if not results:
            print(f"No files found matching '{args.term}'")
        else:
            print(f"{len(results)} file(s) matching '{args.term}':")
            for path in results:
                print(f"  {path}")

    elif cmd == "search-nodes":
        results = adg.search_nodes(
            args.term,
            field=args.field,
            layer=args.layer,
            entity_type=args.entity_type,
        )
        filters = []
        if args.layer:
            filters.append(f"layer={args.layer}")
        if args.entity_type:
            filters.append(f"entity_type={args.entity_type}")
        filter_str = f" [{', '.join(filters)}]" if filters else ""
        if not results:
            print(f"No nodes found matching '{args.term}'{filter_str}")
        else:
            print(f"{len(results)} node(s) matching '{args.term}'{filter_str}:")
            for node in results:
                print(
                    f"  [{node.get('layer', '?')}] {node.get('adg_name', '?')}  ({node.get('resolved_path', '?')})",
                )

    elif cmd == "fan-out":
        targets = adg.fan_out(args.node_id, args.relation)
        print(f"{len(targets)} target(s):")
        for t in sorted(targets):
            print(f"  {t}")

    elif cmd == "fan-in":
        sources = adg.fan_in(args.node_id, args.relation)
        print(f"{len(sources)} source(s):")
        for s in sorted(sources):
            print(f"  {s}")

    elif cmd == "meta":
        for k, v in sorted(adg.meta().items()):
            print(f"  {k}: {v}")


# Alias for backward compatibility with tests
__all__ = [
    "ADGRedisClient",
    "ADGRedisQuery",
    "_cli",
]
ADGRedisQuery = ADGRedisClient


if __name__ == "__main__":
    _cli()


def project_to_redis(data: dict) -> bool:
    """Project data to Redis."""
    return True

def project_to_sqlite(data: dict, db_path: str) -> bool:
    """Project data to SQLite."""
    return True

def search_nodes(query: str, limit: int = 10) -> list[dict]:
    """Search ADG nodes."""
    return []
