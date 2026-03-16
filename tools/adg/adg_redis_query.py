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

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "adg_redis_query")
_emit_applies_guardrail("p0", "adg_redis_query", "p0_governance")
_emit_reads_policy_state("p0", "adg_redis_query", "policy_binding")
_emit_snapshots_state("p0", "adg_redis_query", "state_snapshot")
emit_replay_key("p0", "adg_redis_query")
emit_determinism_digest("p0", "adg_redis_query")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

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
        "search-files", aliases=["--search-files"], help="Find files whose path contains TERM"
    )
    p_sf.add_argument("term", help="Substring to search for in file paths")

    p_sn = sub.add_parser(
        "search-nodes", aliases=["--search-nodes"], help="Find nodes whose adg_name contains TERM"
    )
    p_sn.add_argument(
        "term", nargs="?", default="", help="Substring to search for in node names (default: all)"
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
    except (RuntimeError, redis.ConnectionError) as exc:
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
                    f"  [{node.get('layer', '?')}] {node.get('adg_name', '?')}  ({node.get('resolved_path', '?')})"
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


if __name__ == "__main__":
    _cli()
