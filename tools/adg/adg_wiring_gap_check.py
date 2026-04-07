"""ADG Wiring Gap Checker.

Detects wiring, integration, and configuration issues in the ADG.
Answers the question: "Is infrastructure set up but wiring incomplete?"

Checks:
1. Registry Membership Gap: Are there *Agent/Provider/Strategy classes never imported by a registry?
2. Instantiation Orphan: Does anything in production actually instantiate this class?
3. Port-Adapter Gap: Does every ports/ interface have a wired adapters/ implementation?
4. Dead/Unresolved Imports: Are there broken import chains that compile but fail at runtime?
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path


class ADGWiringGapChecker:
    """Checker for wiring gaps in the ADG."""

    def __init__(self, sqlite_path: Path):
        """Initialize the checker.

        Args:
            sqlite_path: Path to ADG SQLite database
        """
        self.sqlite_path = sqlite_path

    def _connect(self) -> sqlite3.Connection:
        """Get database connection."""
        conn = sqlite3.connect(self.sqlite_path)
        conn.row_factory = sqlite3.Row
        return conn

    def check_registry_gaps(self) -> list[dict]:
        """Check for registry membership gaps.

        Find classes that should be in a registry but are never imported by it.
        Targets: AGENT_REGISTRY, MCP_REGISTRY, CAPABILITY_REGISTRY
        """
        conn = self._connect()
        cursor = conn.cursor()

        # Find registry files
        registry_files = [
            "agentic_core/agents/types/agent_registry.py",
            "agentic_core/mcp/types/mcp_registry.py",
            "agentic_core/capability/types/capability_registry.py",
        ]

        gaps = []

        for registry_file in registry_files:
            # Find classes ending in *Agent, *Provider, *Strategy
            cursor.execute(
                """
                SELECT DISTINCT n.id, n.resolved_path
                FROM nodes n
                WHERE n.entity_type = 'class'
                AND (n.resolved_path LIKE '%Agent' OR n.resolved_path LIKE '%Provider' OR n.resolved_path LIKE '%Strategy')
                AND n.resolved_path NOT LIKE '%test%'
                LIMIT 100
                """,
            )

            candidates = cursor.fetchall()

            for candidate in candidates:
                class_id = candidate[0]
                class_path = candidate[1]
                class_name = Path(class_path).stem

                # Check if this class is ever imported by the registry
                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM edges e
                    WHERE e.relation_type = 'imports'
                    AND e.dst_id = ?
                    AND e.source_file = ?
                    """,
                    (class_id, registry_file),
                )

                import_count = cursor.fetchone()[0]

                if import_count == 0:
                    gaps.append({
                        "type": "registry_gap",
                        "class_name": class_name,
                        "class_path": class_path,
                        "missing_registry": registry_file,
                        "severity": "warning",
                    })

        conn.close()
        return gaps

    def check_instantiation_orphans(self) -> list[dict]:
        """Check for instantiation orphans.

        Find classes that are defined but never instantiated in production code.
        """
        conn = self._connect()
        cursor = conn.cursor()

        # Find classes defined in production code
        cursor.execute(
            """
            SELECT DISTINCT n.id, n.resolved_path
            FROM nodes n
            WHERE n.entity_type = 'class'
            AND n.resolved_path NOT LIKE '%test%'
            AND n.resolved_path NOT LIKE '%ops_scripts%'
            LIMIT 100
            """,
        )

        candidates = cursor.fetchall()
        orphans = []

        for candidate in candidates:
            class_id = candidate[0]
            class_path = candidate[1]
            class_name = Path(class_path).stem

            # Check if this class has any "instantiates" edges
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM edges e
                WHERE e.relation_type = 'instantiates'
                AND e.dst_id = ?
                """,
                (class_id,),
            )

            instantiation_count = cursor.fetchone()[0]

            if instantiation_count == 0:
                orphans.append({
                    "type": "instantiation_orphan",
                    "class_name": class_name,
                    "class_path": class_path,
                    "severity": "info",
                })

        conn.close()
        return orphans

    def check_port_adapter_gaps(self) -> list[dict]:
        """Check for port-adapter gaps.

        Find interfaces in ports/ that lack implementations in adapters/.
        """
        conn = self._connect()
        cursor = conn.cursor()

        # Find interfaces in ports/ directories
        cursor.execute(
            """
            SELECT DISTINCT n.id, n.resolved_path
            FROM nodes n
            WHERE n.entity_type = 'class'
            AND n.resolved_path LIKE '%ports%'
            AND n.resolved_path NOT LIKE '%test%'
            LIMIT 50
            """,
        )

        port_interfaces = cursor.fetchall()
        gaps = []

        for interface in port_interfaces:
            interface_id = interface[0]
            interface_path = interface[1]
            interface_name = Path(interface_path).stem

            # Check if any class in adapters/ implements this interface
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM edges e
                JOIN nodes n ON e.src_id = n.id
                WHERE e.relation_type = 'implements'
                AND e.dst_id = ?
                AND n.resolved_path LIKE '%adapters%'
                """,
                (interface_id,),
            )

            adapter_count = cursor.fetchone()[0]

            if adapter_count == 0:
                gaps.append({
                    "type": "port_adapter_gap",
                    "interface_name": interface_name,
                    "interface_path": interface_path,
                    "severity": "warning",
                })

        conn.close()
        return gaps

    def check_dead_unresolved_imports(self) -> list[dict]:
        """Check for dead and unresolved imports.

        Dead: Imports that resolve to a module but the module is never used.
        Unresolved: Imports that don't resolve to any known module.
        """
        conn = self._connect()
        cursor = conn.cursor()

        issues = []

        # Unresolved imports
        cursor.execute(
            """
            SELECT e.id, e.src_id, e.dst_id, e.source_file, e.line_no, n.resolved_path
            FROM edges e
            JOIN nodes n ON e.src_id = n.id
            WHERE e.relation_type = 'imports'
            AND e.dst_id NOT IN (SELECT id FROM nodes WHERE entity_type = 'module')
            AND e.source_file NOT LIKE '%test%'
            LIMIT 50
            """,
        )

        for row in cursor.fetchall():
            issues.append({
                "type": "unresolved_import",
                "source_file": row[3],
                "line_no": row[4],
                "import_target": row[5],
                "severity": "error",
            })

        # Dead imports (imports that resolve but module never used)
        cursor.execute(
            """
            SELECT e.id, e.source_file, e.line_no, n.resolved_path
            FROM edges e
            JOIN nodes n ON e.src_id = n.id
            WHERE e.relation_type = 'imports'
            AND e.source_file NOT LIKE '%test%'
            AND e.dst_id IN (
                SELECT n.id FROM nodes n WHERE n.entity_type = 'module'
                AND n.id NOT IN (
                    SELECT DISTINCT e.src_id FROM edges e WHERE e.relation_type = 'uses'
                )
            )
            LIMIT 50
            """,
        )

        for row in cursor.fetchall():
            issues.append({
                "type": "dead_import",
                "source_file": row[1],
                "line_no": row[2],
                "import_target": row[3],
                "severity": "warning",
            })

        conn.close()
        return issues


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="ADG Wiring Gap Checker - Detect wiring, integration, and configuration issues",
    )
    parser.add_argument(
        "sqlite_path",
        type=Path,
        help="Path to ADG SQLite database (e.g., artifacts/adg/adg_indexed_*.sqlite)",
    )
    parser.add_argument(
        "--registry-gaps",
        action="store_true",
        help="Check for registry membership gaps",
    )
    parser.add_argument(
        "--instantiation-orphans",
        action="store_true",
        help="Check for instantiation orphans",
    )
    parser.add_argument(
        "--port-adapter-gaps",
        action="store_true",
        help="Check for port-adapter gaps",
    )
    parser.add_argument(
        "--dead-imports",
        action="store_true",
        help="Check for dead and unresolved imports",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all checks",
    )
    parser.add_argument(
        "--gate",
        action="store_true",
        help="Exit with error code 1 if any issues found (for CI/pre-commit)",
    )

    args = parser.parse_args()

    if not args.sqlite_path.exists():
        print(f"Error: SQLite database not found: {args.sqlite_path}")
        return 1

    checker = ADGWiringGapChecker(args.sqlite_path)

    # Run requested checks
    all_issues = []

    if args.registry_gaps or args.all:
        issues = checker.check_registry_gaps()
        all_issues.extend(issues)
        print(f"\nRegistry Gaps: {len(issues)}")
        for issue in issues[:10]:
            print(f"  [{issue['severity'].upper()}] {issue['class_name']} missing from {issue['missing_registry']}")

    if args.instantiation_orphans or args.all:
        issues = checker.check_instantiation_orphans()
        all_issues.extend(issues)
        print(f"\nInstantiation Orphans: {len(issues)}")
        for issue in issues[:10]:
            print(f"  [{issue['severity'].upper()}] {issue['class_name']} never instantiated")

    if args.port_adapter_gaps or args.all:
        issues = checker.check_port_adapter_gaps()
        all_issues.extend(issues)
        print(f"\nPort-Adapter Gaps: {len(issues)}")
        for issue in issues[:10]:
            print(f"  [{issue['severity'].upper()}] {issue['interface_name']} has no adapter")

    if args.dead_imports or args.all:
        issues = checker.check_dead_unresolved_imports()
        all_issues.extend(issues)
        print(f"\nDead/Unresolved Imports: {len(issues)}")
        for issue in issues[:10]:
            print(f"  [{issue['severity'].upper()}] {issue['type']}: {issue['import_target']} in {issue['source_file']}")

    # Summary
    print(f"\nTotal Issues: {len(all_issues)}")

    # Gate mode
    if args.gate and all_issues:
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
