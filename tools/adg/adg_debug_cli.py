"""ADG Debug CLI — Command-line interface for ADG graph debugging.

Commands:
    show-node           Display node details by ID or ADG name
    show-imports        Show import edges for a node
    find-unresolved     Find unresolved imports in scope
    explain-violation   Explain a specific violation by edge ID
    compare-snapshot    Compare SQLite vs Redis for snapshot
    run-invariants      Run all invariant checks

All commands output structured JSON. No prose, no reports.
"""

from __future__ import annotations

import argparse
import json
import sys

from tools.adg.services import (
    ADGQueryService,
    BoundaryViolationCheck,
    ImportResolutionCheck,
    InvariantRunner,
    RedisParityCheck,
)


def cmd_show_node(args: argparse.Namespace) -> int:
    """Show node details."""
    with ADGQueryService(adg_dir=args.adg_dir) as service:
        service.initialize_snapshot(args.snapshot)

        # Get by ID or search by name
        if args.id:
            result = service.get_node(args.id)
        else:
            print(json.dumps({"error": "Must specify --id"}, indent=2))
            return 1

        if not result.success:
            print(json.dumps({"error": result.error}, indent=2))
            return 1

        output = {
            "node": result.data.to_dict() if hasattr(result.data, "to_dict") else vars(result.data),
            "snapshot_id": result.snapshot_id,
            "cache_hit": result.cache_hit,
        }
        print(json.dumps(output, indent=2, default=str))
        return 0


def cmd_show_imports(args: argparse.Namespace) -> int:
    """Show import edges for a node."""
    with ADGQueryService(adg_dir=args.adg_dir) as service:
        service.initialize_snapshot(args.snapshot)

        result = service.get_edges(args.id, "imports")

        if not result.success:
            print(json.dumps({"error": result.error}, indent=2))
            return 1

        output = {
            "src_id": args.id,
            "relation_type": "imports",
            "edges": [
                {
                    "id": e.id,
                    "dst_id": e.dst_id,
                    "symbol": e.symbol,
                    "source_file": e.source_file,
                    "line_no": e.line_no,
                }
                for e in result.data
            ],
            "count": len(result.data),
            "snapshot_id": result.snapshot_id,
            "cache_hit": result.cache_hit,
        }
        print(json.dumps(output, indent=2, default=str))
        return 0


def cmd_find_unresolved(args: argparse.Namespace) -> int:
    """Find unresolved imports in scope."""
    with ADGQueryService(adg_dir=args.adg_dir) as service:
        service.initialize_snapshot(args.snapshot)

        unresolved = service.find_unresolved_imports(args.scope)

        output = {
            "scope": args.scope or "all",
            "unresolved_count": len(unresolved),
            "unresolved": [
                {
                    "edge_id": u.edge_id,
                    "src_module": u.src_module,
                    "src_file": u.src_file,
                    "line_no": u.line_no,
                    "symbol": u.symbol,
                    "dst_id": u.dst_id,
                    "dst_entity_type": u.dst_entity_type,
                }
                for u in unresolved
            ],
            "snapshot_id": args.snapshot,
        }
        print(json.dumps(output, indent=2, default=str))
        return 0 if not unresolved else 1


def cmd_explain_violation(args: argparse.Namespace) -> int:
    """Explain a specific violation by edge ID."""
    with ADGQueryService(adg_dir=args.adg_dir) as service:
        service.initialize_snapshot(args.snapshot)

        # Get the edge details
        meta = service.get_snapshot_metadata()
        if not meta:
            print(json.dumps({"error": "No snapshot metadata"}, indent=2))
            return 1

        # Find the edge in unresolved imports
        unresolved = service.find_unresolved_imports(None)
        violation = next((u for u in unresolved if u.edge_id == args.edge_id), None)

        if not violation:
            print(json.dumps({
                "error": f"Edge {args.edge_id} not found in unresolved imports",
                "hint": "Use find-unresolved to list all unresolved imports",
            }, indent=2))
            return 1

        # Get destination node details
        dst_node = service.get_node(violation.dst_id)

        output = {
            "violation_type": "unresolved_import",
            "edge_id": violation.edge_id,
            "explanation": {
                "problem": f"Import resolves to entity_type='{violation.dst_entity_type}' instead of 'module'",
                "src_module": violation.src_module,
                "src_file": violation.src_file,
                "line_no": violation.line_no,
                "symbol": violation.symbol,
                "destination": {
                    "node_id": violation.dst_id,
                    "entity_type": violation.dst_entity_type,
                    "adg_name": dst_node.data.adg_name if dst_node.success else None,
                },
            },
            "remediation": f"Fix import at {violation.src_file}:{violation.line_no}",
            "snapshot_id": args.snapshot,
        }
        print(json.dumps(output, indent=2, default=str))
        return 0


def cmd_compare_snapshot(args: argparse.Namespace) -> int:
    """Compare SQLite vs Redis for snapshot."""
    with ADGQueryService(adg_dir=args.adg_dir) as service:
        service.initialize_snapshot(args.snapshot)

        meta = service.get_snapshot_metadata()
        if not meta:
            print(json.dumps({"error": "No snapshot metadata"}, indent=2))
            return 1

        output = {
            "snapshot_id": meta.snapshot_id,
            "sqlite": {
                "path": meta.sqlite_path,
                "digest": meta.sqlite_digest,
                "node_count": meta.node_count,
                "edge_count": meta.edge_count,
            },
            "redis": {
                "digest": meta.redis_digest,
            },
            "parity": {
                "coherent": meta.projection_coherent,
                "match": meta.sqlite_digest == meta.redis_digest,
            },
        }
        print(json.dumps(output, indent=2, default=str))
        return 0 if meta.projection_coherent else 1


def cmd_run_invariants(args: argparse.Namespace) -> int:
    """Run all invariant checks."""
    runner = InvariantRunner()

    # Register checks
    runner.register_check(ImportResolutionCheck())
    runner.register_check(BoundaryViolationCheck())
    runner.register_check(RedisParityCheck())

    # Build policy pack
    policy_pack = {
        "name": args.policy or "default",
        "forbidden_patterns": ["archives."],
        "protected_scopes": ["apps_lic", "apps_rg", "apps_eval", "apps_exec", "apps_research", "apps_rfp", "apps_shared"],
    }

    with ADGQueryService(adg_dir=args.adg_dir) as service:
        service.initialize_snapshot(args.snapshot)
        results = runner.run_all(service, policy_pack)

        print(runner.to_json())

        # Return non-zero if violations found
        return 1 if runner.has_violations() else 0


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="adg-debug",
        description="ADG Debug CLI — Direct graph queries, no reports",
    )
    parser.add_argument(
        "--snapshot",
        default="04022026_2140",
        help="ADG snapshot ID (default: 04022026_2140)",
    )
    parser.add_argument(
        "--adg-dir",
        default="artifacts/adg",
        help="Directory containing ADG SQLite files",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # show-node
    show_node = subparsers.add_parser("show-node", help="Display node details")
    show_node.add_argument("--id", type=int, required=True, help="Node ID")
    show_node.set_defaults(func=cmd_show_node)

    # show-imports
    show_imports = subparsers.add_parser("show-imports", help="Show import edges")
    show_imports.add_argument("--id", type=int, required=True, help="Source node ID")
    show_imports.set_defaults(func=cmd_show_imports)

    # find-unresolved
    find_unresolved = subparsers.add_parser("find-unresolved", help="Find unresolved imports")
    find_unresolved.add_argument("--scope", default=None, help="Scope filter (e.g., apps_lic)")
    find_unresolved.set_defaults(func=cmd_find_unresolved)

    # explain-violation
    explain = subparsers.add_parser("explain-violation", help="Explain a violation")
    explain.add_argument("--edge-id", type=int, required=True, help="Edge ID")
    explain.set_defaults(func=cmd_explain_violation)

    # compare-snapshot
    compare = subparsers.add_parser("compare-snapshot", help="Compare SQLite vs Redis")
    compare.set_defaults(func=cmd_compare_snapshot)

    # run-invariants
    invariants = subparsers.add_parser("run-invariants", help="Run all invariant checks")
    invariants.add_argument("--policy", default="default", help="Policy pack name")
    invariants.set_defaults(func=cmd_run_invariants)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
