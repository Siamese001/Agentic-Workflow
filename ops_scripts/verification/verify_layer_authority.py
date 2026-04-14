#!/usr/bin/env python3
"""
ADG Layer Authority Verification

Enforces layer authority rules:
NO DIRECT EDGES WITHOUT MEDIATED INTERFACE:
- L0 -> L_RUNTIME
- L1 -> L_RUNTIME
- L2 -> L_RUNTIME
- L3 -> L_RUNTIME
- L_TOOLS -> L_RUNTIME
- L_SL -> L_RUNTIME

ENFORCE NO UNAPPROVED UPWARD CONTROL FLOW:
- L0 -> L2
- L1 -> L2
- any disallowed cross-layer contract

ALL WRITES MUST:
- terminate_at_uwg
- record authority
- record mutation receipt
- record trace linkage

ADD VIOLATION TYPES:
- layer_violation
- uwg_bypass
- runtime_boundary_breach
- unknown_l4_identity
- unauthorized_write
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path
from typing import Any
from tqdm import tqdm

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class LayerAuthorityError(Exception):
    """Raised when layer authority verification fails."""

    pass


class ADGLayerAuthorityVerifier:
    """Verifies ADG layer authority compliance."""

    # Define layer hierarchy and allowed transitions
    LAYER_HIERARCHY = {
        "L0": 0,
        "L1": 1,
        "L2": 2,
        "L3": 3,
        "L4": 4,
        "L5": 5,
        "L6": 6,
        "L_RUNTIME": 10,
        "L_TOOLS": 11,
        "L_SL": 12,
        "L_APP": 13,
        "L_OPS": 14,
        "L_PG": 15,
        "L_SHARED": 16,
        "L_TEST": 17,
        "UNKNOWN": 99,
    }

    # Disallowed direct edges to runtime
    DISALLOWED_DIRECT_TO_RUNTIME = {
        "L0",
        "L1",
        "L2",
        "L3",
        "L_TOOLS",
        "L_SL",
    }

    # Disallowed upward control flow
    DISALLOWED_UPWARD_FLOW = {
        ("L0", "L2"),
        ("L1", "L2"),
        # Add more as needed
    }

    # Write-related edge types that require UWG termination
    WRITE_EDGE_TYPES = {
        "writes_to",
        "writes_through",
        "invokes_provider",
        "invokes_dynamic",
        "executes_action",
        "invokes_tool",
    }

    def __init__(self, adg_dir: Path):
        self.adg_dir = Path(adg_dir)
        self.sqlite_path = self._find_sqlite_database()
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def _find_sqlite_database(self) -> Path:
        """Find the latest SQLite database."""
        sqlite_files = list(self.adg_dir.glob("adg_indexed_*.sqlite"))
        if not sqlite_files:
            raise LayerAuthorityError("No SQLite database found")

        return max(sqlite_files, key=lambda p: p.stat().st_mtime)

    def _get_layer_for_node(self, node_id: int) -> str:
        """Get layer for a specific node."""
        try:
            with sqlite3.connect(self.sqlite_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT layer FROM nodes WHERE id = ?", (node_id,))
                result = cursor.fetchone()
                return result[0] if result else "UNKNOWN"
        except Exception as e:
            raise LayerAuthorityError(f"Failed to get layer for node {node_id}: {e}")

    def _check_layer_violation_edge(self, src_layer: str, dst_layer: str, relation_type: str) -> str | None:
        """Check if an edge violates layer authority rules."""

        # Skip external modules
        if src_layer == "UNKNOWN" or dst_layer == "UNKNOWN":
            return None

        # Check for direct edges to runtime from disallowed layers
        if (
            dst_layer == "L_RUNTIME"
            and src_layer in self.DISALLOWED_DIRECT_TO_RUNTIME
            and relation_type in ["calls", "invokes_provider"]
        ):
            return f"Direct {relation_type} from {src_layer} to L_RUNTIME without mediation"

        # Check for disallowed upward control flow
        if (src_layer, dst_layer) in self.DISALLOWED_UPWARD_FLOW:
            return f"Disallowed upward control flow from {src_layer} to {dst_layer}"

        # Check for general layer violations (crossing too many layers)
        src_level = self.LAYER_HIERARCHY.get(src_layer, 99)
        dst_level = self.LAYER_HIERARCHY.get(dst_layer, 99)

        # Allow some flexibility for non-hierarchical layers
        if src_level < 10 and dst_level < 10:
            if abs(dst_level - src_level) > 2 and relation_type in ["calls", "writes_to"]:
                return f"Large layer jump from {src_layer} to {dst_layer} via {relation_type}"

        return None

    def _verify_layer_authority_compliance(self) -> dict[str, Any]:
        """Verify layer authority compliance across all edges."""
        print("🏗️  Verifying layer authority compliance...")

        try:
            with sqlite3.connect(self.sqlite_path) as conn:
                cursor = conn.cursor()

                # Get all cross-layer edges for first-party modules
                cursor.execute("""
                    SELECT e.id, e.src_id, e.dst_id, e.relation_type, e.symbol,
                           n_src.adg_name as src_name, n_src.layer as src_layer,
                           n_dst.adg_name as dst_name, n_dst.layer as dst_layer
                    FROM edges e
                    JOIN nodes n_src ON e.src_id = n_src.id
                    JOIN nodes n_dst ON e.dst_id = n_dst.id
                    WHERE n_src.layer != n_dst.layer
                    AND n_src.identity_kind NOT IN ('external_module', 'external_provider')
                    AND n_dst.identity_kind NOT IN ('external_module', 'external_provider')
                    AND n_src.layer != 'UNKNOWN' AND n_dst.layer != 'UNKNOWN'
                """)

                cross_layer_edges = cursor.fetchall()
                print(f"   📊 Analyzing {len(cross_layer_edges)} cross-layer edges")

                violations = []
                for edge in tqdm(cross_layer_edges, desc="Processing", unit="item"):
                    (
                        edge_id,
                        src_id,
                        dst_id,
                        relation_type,
                        symbol,
                        src_name,
                        src_layer,
                        dst_name,
                        dst_layer,
                    ) = edge

                    violation = self._check_layer_violation_edge(
                        src_layer,
                        dst_layer,
                        relation_type,
                    )

                    if violation:
                        violations.append(
                            {
                                "edge_id": edge_id,
                                "src_module": src_name,
                                "dst_module": dst_name,
                                "src_layer": src_layer,
                                "dst_layer": dst_layer,
                                "relation_type": relation_type,
                                "symbol": symbol,
                                "violation": violation,
                            }
                        )

                # Summary by violation type
                violation_summary = {}
                for v in violations:
                    violation_type = v["violation"].split(":")[0] if ":" in v["violation"] else v["violation"]
                    violation_summary[violation_type] = violation_summary.get(violation_type, 0) + 1

                print(f"   📊 Found {len(violations)} layer authority violations")
                for vtype, count in violation_summary.items():
                    print(f"      {vtype}: {count}")

                return {
                    "total_cross_layer_edges": len(cross_layer_edges),
                    "violations": violations,
                    "violation_summary": violation_summary,
                    "violation_count": len(violations),
                }

        except Exception as e:
            raise LayerAuthorityError(f"Layer authority compliance check failed: {e}")

    def _verify_uwg_termination_for_writes(self) -> dict[str, Any]:
        """Verify all write operations terminate at UWG."""
        print("🛡️  Verifying UWG termination for write operations...")

        try:
            with sqlite3.connect(self.sqlite_path) as conn:
                cursor = conn.cursor()

                # Find modules with write operations and collapse multiple write edge types per module
                write_modules_by_id: dict[int, dict[str, Any]] = {}
                placeholders = ",".join(["?" for _ in self.WRITE_EDGE_TYPES])

                cursor.execute(
                    f"""
                    SELECT e.src_id, n.adg_name, n.layer, e.relation_type
                    FROM edges e
                    JOIN nodes n ON e.src_id = n.id
                    WHERE e.relation_type IN ({placeholders})
                    AND n.identity_kind NOT IN ('external_module', 'external_provider')
                """,
                    list(self.WRITE_EDGE_TYPES),
                )

                for module_id, module_name, layer, write_type in tqdm(
                    cursor.fetchall(), desc="Indexing write modules", unit="row", leave=False
                ):
                    module_entry = write_modules_by_id.setdefault(
                        module_id,
                        {
                            "module_id": module_id,
                            "module_name": module_name,
                            "layer": layer,
                            "write_types": set(),
                        },
                    )
                    module_entry["write_types"].add(write_type)

                write_modules = []
                for module in write_modules_by_id.values():
                    module["write_types"] = sorted(module["write_types"])
                    write_modules.append(module)

                print(f"   📊 Found {len(write_modules)} modules with write operations")

                # Check UWG termination for each write module
                uwg_violations = []
                for module in tqdm(write_modules, desc="Processing", unit="item"):
                    cursor.execute(
                        """
                        SELECT COUNT(*) FROM edges
                        WHERE src_id = ? AND relation_type = 'execution_terminates_at_uwg'
                    """,
                        (module["module_id"],),
                    )

                    has_uwg_termination = cursor.fetchone()[0] > 0

                    if not has_uwg_termination:
                        uwg_violations.append(
                            {
                                "module_name": module["module_name"],
                                "layer": module["layer"],
                                "write_types": module["write_types"],
                                "violation": "Write-capable module without UWG termination",
                            }
                        )

                print(f"   📊 UWG violations: {len(uwg_violations)}")

                return {
                    "write_modules": len(write_modules),
                    "uwg_compliant": len(write_modules) - len(uwg_violations),
                    "uwg_violations": uwg_violations,
                    "uwg_compliance_rate": (len(write_modules) - len(uwg_violations))
                    / max(1, len(write_modules)),
                }

        except Exception as e:
            raise LayerAuthorityError(f"UWG termination verification failed: {e}")

    def _verify_l4_identity_completeness(self) -> dict[str, Any]:
        """Verify L4 modules have complete identity."""
        print("🎯 Verifying L4 identity completeness...")

        try:
            with sqlite3.connect(self.sqlite_path) as conn:
                cursor = conn.cursor()

                # Get all L4 modules
                cursor.execute("""
                    SELECT id, adg_name, layer, identity_kind, confidence, resolved_path
                    FROM nodes
                    WHERE layer = 'L4' AND entity_type = 'module'
                """)

                l4_modules = []
                for row in tqdm(cursor.fetchall(), desc="Processing", unit="item"):
                    l4_modules.append(
                        {
                            "id": row[0],
                            "name": row[1],
                            "layer": row[2],
                            "identity_kind": row[3],
                            "confidence": row[4],
                            "resolved_path": row[5],
                        }
                    )

                print(f"   📊 Found {len(l4_modules)} L4 modules")

                # Check for identity issues
                identity_issues = []
                for module in tqdm(l4_modules, desc="Processing", unit="item"):
                    issues = []

                    if module["layer"] == "UNKNOWN":
                        issues.append("Unknown layer classification")

                    if module["identity_kind"] in ["external_module", "external_provider"]:
                        issues.append("External identity in L4")

                    if module["confidence"] == "LOW":
                        issues.append("Low confidence identity")

                    if not module["resolved_path"]:
                        issues.append("Missing resolved path")

                    if issues:
                        identity_issues.append(
                            {
                                "module_name": module["name"],
                                "issues": issues,
                            }
                        )

                print(f"   📊 L4 identity issues: {len(identity_issues)}")

                return {
                    "total_l4_modules": len(l4_modules),
                    "identity_issues": len(identity_issues),
                    "identity_compliance_rate": (len(l4_modules) - len(identity_issues))
                    / max(1, len(l4_modules)),
                    "issue_details": identity_issues,
                }

        except Exception as e:
            raise LayerAuthorityError(f"L4 identity verification failed: {e}")

    def _verify_unauthorized_write_detection(self) -> dict[str, Any]:
        """Verify detection of unauthorized writes."""
        print("🚫 Verifying unauthorized write detection...")

        try:
            with sqlite3.connect(self.sqlite_path) as conn:
                cursor = conn.cursor()

                # Check for existing unauthorized write violations
                cursor.execute("""
                    SELECT COUNT(*) FROM edges
                    WHERE relation_type IN ('layer_violation', 'layer_authority_violation', 'uwg_bypass', 'unauthorized_write')
                """)

                existing_violations = cursor.fetchone()[0]

                # Look for potential unauthorized writes (writes without proper authority)
                cursor.execute(
                    """
                    SELECT DISTINCT e.src_id, n.adg_name, n.layer, e.relation_type
                    FROM edges e
                    JOIN nodes n ON e.src_id = n.id
                    WHERE e.relation_type IN ({})
                    AND n.identity_kind NOT IN ('external_module', 'external_provider')
                    AND NOT EXISTS (
                        SELECT 1 FROM edges e2
                        WHERE e2.src_id = e.src_id
                        AND e2.relation_type = 'execution_terminates_at_uwg'
                    )
                """.format(",".join(["?" for _ in self.WRITE_EDGE_TYPES])),
                    list(self.WRITE_EDGE_TYPES),
                )

                potential_unauthorized_by_module: dict[tuple[str, str], dict[str, Any]] = {}
                for _, module_name, layer, write_type in tqdm(
                    cursor.fetchall(), desc="Checking unauthorized writes", unit="row", leave=False
                ):
                    key = (module_name, layer)
                    module_entry = potential_unauthorized_by_module.setdefault(
                        key,
                        {
                            "module_name": module_name,
                            "layer": layer,
                            "write_types": set(),
                        },
                    )
                    module_entry["write_types"].add(write_type)

                potential_unauthorized = []
                for module in potential_unauthorized_by_module.values():
                    module["write_types"] = sorted(module["write_types"])
                    potential_unauthorized.append(module)

                print(f"   📊 Existing write violations: {existing_violations}")
                print(f"   📊 Potential unauthorized writes: {len(potential_unauthorized)}")

                return {
                    "existing_violations": existing_violations,
                    "potential_unauthorized": len(potential_unauthorized),
                    "unauthorized_details": potential_unauthorized,
                }

        except Exception as e:
            raise LayerAuthorityError(f"Unauthorized write detection failed: {e}")

    def _write_json_report(self, output_path: Path, payload: dict[str, Any]) -> None:
        """Persist report atomically with parent directory creation."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = output_path.with_suffix(output_path.suffix + ".tmp")
        tmp_path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
        tmp_path.replace(output_path)

    def verify(self) -> dict[str, Any]:
        """Run complete layer authority verification."""
        print("🔍 Starting ADG Layer Authority Verification...")
        print(f"📁 ADG Directory: {self.adg_dir}")
        print(f"🗄️  SQLite Database: {self.sqlite_path.name}")

        # Verify layer authority compliance
        layer_compliance = self._verify_layer_authority_compliance()

        # Verify UWG termination for writes
        uwg_compliance = self._verify_uwg_termination_for_writes()

        # Verify L4 identity completeness
        l4_identity = self._verify_l4_identity_completeness()

        # Verify unauthorized write detection
        unauthorized_writes = self._verify_unauthorized_write_detection()

        # Determine overall status
        critical_issues = (
            layer_compliance["violation_count"] > 0
            or len(uwg_compliance["uwg_violations"]) > 0
            or l4_identity["identity_issues"] > 0
        )

        # Prepare result
        result = {
            "status": "FAIL" if critical_issues else "PASS",
            "layer_compliance": layer_compliance,
            "uwg_compliance": uwg_compliance,
            "l4_identity": l4_identity,
            "unauthorized_writes": unauthorized_writes,
            "errors": self.errors,
            "warnings": self.warnings,
            "summary": {
                "layer_violations": layer_compliance["violation_count"],
                "uwg_violations": len(uwg_compliance["uwg_violations"]),
                "l4_identity_issues": l4_identity["identity_issues"],
                "unauthorized_writes": unauthorized_writes["potential_unauthorized"],
                "uwg_compliance_rate": uwg_compliance["uwg_compliance_rate"],
                "l4_identity_compliance_rate": l4_identity["identity_compliance_rate"],
            },
        }

        # Print results
        if self.errors:
            print("\n❌ LAYER AUTHORITY VERIFICATION FAILED")
            for error in self.errors:
                print(f"   • {error}")

        if self.warnings:
            print("\n⚠️  Warnings:")
            for warning in self.warnings:
                print(f"   • {warning}")

        if critical_issues:
            print("\n❌ LAYER AUTHORITY ISSUES FOUND")
            print(f"   • Layer violations: {layer_compliance['violation_count']}")
            print(f"   • UWG violations: {len(uwg_compliance['uwg_violations'])}")
            print(f"   • L4 identity issues: {l4_identity['identity_issues']}")
        else:
            print("\n✅ LAYER AUTHORITY VERIFICATION PASSED")
            print(f"📊 UWG compliance: {uwg_compliance['uwg_compliance_rate']:.1%}")
            print(f"📊 L4 identity compliance: {l4_identity['identity_compliance_rate']:.1%}")

        return result


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Verify ADG layer authority")
    parser.add_argument(
        "--adg-dir",
        type=Path,
        default=Path("artifacts/adg"),
        help="Path to ADG artifacts directory",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Path to save verification report",
    )

    args = parser.parse_args()

    try:
        verifier = ADGLayerAuthorityVerifier(args.adg_dir)
        result = verifier.verify()

        if args.output:
            verifier._write_json_report(args.output, result)
            print(f"📄 Report saved to: {args.output}")

        return 0 if result["status"] == "PASS" else 1

    except LayerAuthorityError as e:  # guardian: LayerAuthorityError should be handled with specific context
        print(f"❌ Verification failed: {e}")
        return 1
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
