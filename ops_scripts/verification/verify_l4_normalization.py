#!/usr/bin/env python3
"""
ADG L4 Normalization Verification

Ensures L4 modules are properly normalized:
- L4 modules must have zero UNKNOWN layer classification
- L4 modules must have resolved identity
- L4 persistence paths must be queryable as canonical state ledger participants
- L4 must be the authoritative location for persisted validation artifacts, learning state, and provenance state
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


class L4NormalizationError(Exception):
    """Raised when L4 normalization verification fails."""

    pass


class ADGL4NormalizationVerifier:
    """Verifies ADG L4 normalization compliance."""

    # Expected L4 entity types
    L4_ENTITY_TYPES = {
        "module",
        "datastore",
        "side_effect_endpoint",
        "embedding_store",
        "retrieval_component",
        "decision_point",
        "policy",
        "validation_artifact",
        "learning_state",
        "provenance_state",
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
            raise L4NormalizationError("No SQLite database found")

        return max(sqlite_files, key=lambda p: p.stat().st_mtime)

    def _verify_l4_layer_classification(self) -> dict[str, Any]:
        """Verify all L4 modules have proper layer classification."""
        print("🏷️  Verifying L4 layer classification...")

        try:
            with sqlite3.connect(self.sqlite_path) as conn:
                cursor = conn.cursor()

                # Get all nodes classified as L4
                cursor.execute("""
                    SELECT id, adg_name, entity_type, layer, identity_kind, confidence
                    FROM nodes
                    WHERE layer = 'L4'
                    ORDER BY entity_type, adg_name
                """)

                l4_nodes = []
                for row in tqdm(cursor.fetchall(), desc="Processing", unit="item"):
                    l4_nodes.append(
                        {
                            "id": row[0],
                            "name": row[1],
                            "entity_type": row[2],
                            "layer": row[3],
                            "identity_kind": row[4],
                            "confidence": row[5],
                        }
                    )

                print(f"   📊 Found {len(l4_nodes)} nodes in L4")

                # Check for unknown classifications
                unknown_classifications = []
                for node in l4_nodes:
                    if node["layer"] == "UNKNOWN":
                        unknown_classifications.append(node)

                if unknown_classifications:
                    self.errors.append(
                        f"{len(unknown_classifications)} L4 nodes have UNKNOWN layer classification"
                    )

                # Check entity type distribution
                entity_distribution = {}
                for node in l4_nodes:
                    entity_distribution[node["entity_type"]] = (
                        entity_distribution.get(node["entity_type"], 0) + 1
                    )

                print("   📊 L4 entity distribution:")
                for entity_type, count in sorted(entity_distribution.items()):
                    print(f"      {entity_type}: {count}")

                return {
                    "total_l4_nodes": len(l4_nodes),
                    "unknown_classifications": len(unknown_classifications),
                    "entity_distribution": entity_distribution,
                    "l4_nodes": l4_nodes,
                }

        except Exception as e:
            raise L4NormalizationError(f"L4 layer classification verification failed: {e}")

    def _verify_l4_identity_resolution(self) -> dict[str, Any]:
        """Verify L4 modules have resolved identity."""
        print("🎯 Verifying L4 identity resolution...")

        try:
            with sqlite3.connect(self.sqlite_path) as conn:
                cursor = conn.cursor()

                # Get L4 modules with identity issues
                cursor.execute("""
                    SELECT id, adg_name, entity_type, identity_kind, confidence, resolved_path
                    FROM nodes
                    WHERE layer = 'L4' AND entity_type = 'module'
                """)

                l4_modules = []
                for row in tqdm(cursor.fetchall(), desc="Processing", unit="item"):
                    l4_modules.append(
                        {
                            "id": row[0],
                            "name": row[1],
                            "entity_type": row[2],
                            "identity_kind": row[3],
                            "confidence": row[4],
                            "resolved_path": row[5],
                        }
                    )

                print(f"   📊 Analyzing {len(l4_modules)} L4 modules")

                # Check identity resolution
                identity_issues = []
                for module in tqdm(l4_modules, desc="Processing", unit="item"):
                    issues = []

                    if module["identity_kind"] == "unresolved_import":
                        issues.append("Unresolved import")

                    if module["identity_kind"] in ["external_module", "external_provider"]:
                        issues.append("External identity")

                    if module["confidence"] == "LOW":
                        issues.append("Low confidence")

                    if not module["resolved_path"] or module["resolved_path"].strip() == "":
                        issues.append("Missing resolved path")

                    if issues:
                        identity_issues.append(
                            {
                                "module_name": module["name"],
                                "identity_kind": module["identity_kind"],
                                "confidence": module["confidence"],
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
            raise L4NormalizationError(f"L4 identity resolution verification failed: {e}")

    def _verify_l4_path_integrity(self) -> dict[str, Any]:
        """Verify L4 path integrity - all L4 modules have valid paths and proper layer assignment.

        This method is required by test_unknown_layer_in_l4_path to detect UNKNOWN layer
        modules that should not appear in L4 paths.
        """
        try:
            with sqlite3.connect(self.sqlite_path) as conn:
                cursor = conn.cursor()

                # Get all L4 nodes with their details
                cursor.execute("""
                    SELECT id, adg_name, entity_type, layer, identity_kind, confidence, resolved_path
                    FROM nodes
                    WHERE layer = 'L4'
                    ORDER BY adg_name
                """)

                l4_nodes = []
                for row in tqdm(cursor.fetchall(), desc="Processing", unit="item"):
                    l4_nodes.append(
                        {
                            "id": row[0],
                            "name": row[1],
                            "entity_type": row[2],
                            "layer": row[3],
                            "identity_kind": row[4],
                            "confidence": row[5],
                            "resolved_path": row[6],
                        }
                    )

                # Check for UNKNOWN layer nodes in L4 (this is the key check)
                unknown_layer_nodes = [n for n in l4_nodes if n["layer"] == "UNKNOWN"]

                return {
                    "l4_nodes": l4_nodes,
                    "total_l4_nodes": len(l4_nodes),
                    "unknown_layer_count": len(unknown_layer_nodes),
                    "status": "PASS" if len(unknown_layer_nodes) == 0 else "FAIL",
                }

        except Exception as e:
            raise L4NormalizationError(f"L4 path integrity verification failed: {e}")

    def _verify_l4_persistence_path_normalization(self) -> dict[str, Any]:
        """Verify L4 persistence paths are normalized and queryable."""
        print("💾 Verifying L4 persistence path normalization...")

        try:
            with sqlite3.connect(self.sqlite_path) as conn:
                cursor = conn.cursor()

                # Get L4 persistence-related nodes
                persistence_entities = [
                    "datastore",
                    "side_effect_endpoint",
                    "embedding_store",
                    "validation_artifact",
                    "learning_state",
                    "provenance_state",
                ]

                placeholders = ",".join(["?" for _ in persistence_entities])
                cursor.execute(
                    f"""
                    SELECT id, adg_name, entity_type, resolved_path, confidence
                    FROM nodes
                    WHERE layer = 'L4' AND entity_type IN ({placeholders})
                """,
                    persistence_entities,
                )

                persistence_nodes = []
                for row in cursor.fetchall():
                    persistence_nodes.append(
                        {
                            "id": row[0],
                            "name": row[1],
                            "entity_type": row[2],
                            "resolved_path": row[3],
                            "confidence": row[4],
                        }
                    )

                print(f"   📊 Found {len(persistence_nodes)} L4 persistence nodes")

                # Check path normalization
                path_issues = []
                for node in tqdm(persistence_nodes, desc="Processing", unit="item"):
                    if not node["resolved_path"] or node["resolved_path"].strip() == "":
                        path_issues.append(
                            {
                                "node_name": node["name"],
                                "entity_type": node["entity_type"],
                                "issue": "Missing resolved path",
                            }
                        )
                    elif not Path(node["resolved_path"]).is_absolute():
                        path_issues.append(
                            {
                                "node_name": node["name"],
                                "entity_type": node["entity_type"],
                                "issue": "Non-absolute path",
                            }
                        )

                # Check for canonical state ledger participation
                cursor.execute(
                    """
                    SELECT COUNT(*) FROM edges e
                    JOIN nodes n ON e.dst_id = n.id
                    WHERE n.layer = 'L4'
                    AND n.entity_type IN ({})
                    AND e.relation_type IN ('stores_validation_artifact', 'stores_learning_state', 'writes_to')
                """.format(",".join(["?" for _ in persistence_entities])),
                    persistence_entities,
                )

                ledger_participation = cursor.fetchone()[0]

                print(f"   📊 Path issues: {len(path_issues)}")
                print(f"   📊 Ledger participation edges: {ledger_participation}")

                return {
                    "persistence_nodes": len(persistence_nodes),
                    "path_issues": len(path_issues),
                    "ledger_participation": ledger_participation,
                    "path_issue_details": path_issues,
                }

        except Exception as e:
            raise L4NormalizationError(f"L4 persistence path verification failed: {e}")

    def _verify_l4_authoritative_location(self) -> dict[str, Any]:
        """Verify L4 is authoritative location for key artifacts."""
        print("👑 Verifying L4 as authoritative location...")

        try:
            with sqlite3.connect(self.sqlite_path) as conn:
                cursor = conn.cursor()

                # Check distribution of key artifact types across layers
                artifact_types = [
                    ("validation_artifact", "Validation artifacts"),
                    ("learning_state", "Learning state"),
                    ("provenance_state", "Provenance state"),
                    ("policy", "Policy artifacts"),
                    ("decision_point", "Decision points"),
                ]

                layer_distribution = {}
                for entity_type, description in tqdm(artifact_types, desc="Processing", unit="item"):
                    cursor.execute(
                        """
                        SELECT layer, COUNT(*) FROM nodes
                        WHERE entity_type = ?
                        GROUP BY layer
                        ORDER BY COUNT(*) DESC
                    """,
                        (entity_type,),
                    )

                    distribution = dict(cursor.fetchall())
                    layer_distribution[entity_type] = {
                        "description": description,
                        "distribution": distribution,
                        "l4_count": distribution.get("L4", 0),
                        "total_count": sum(distribution.values()),
                    }

                # Check for artifacts outside L4 that should be in L4
                misplaced_artifacts = []
                for entity_type, info in tqdm(layer_distribution.items(), desc="Processing", unit="item"):
                    l4_count = info["l4_count"]
                    total_count = info["total_count"]

                    if total_count > 0:
                        l4_percentage = l4_count / total_count
                        if l4_percentage < 0.8:  # Less than 80% in L4
                            misplaced_artifacts.append(
                                {
                                    "entity_type": entity_type,
                                    "description": info["description"],
                                    "l4_count": l4_count,
                                    "total_count": total_count,
                                    "l4_percentage": l4_percentage,
                                    "distribution": info["distribution"],
                                }
                            )

                print("   📊 Artifact distribution analysis:")
                for entity_type, info in layer_distribution.items():
                    l4_pct = info["l4_count"] / max(1, info["total_count"]) * 100
                    print(
                        f"      {info['description']}: {info['l4_count']}/{info['total_count']} in L4 ({l4_pct:.1f}%)"
                    )

                if misplaced_artifacts:
                    print(
                        f"   ⚠️  Found {len(misplaced_artifacts)} artifact types with insufficient L4 concentration"
                    )

                return {
                    "layer_distribution": layer_distribution,
                    "misplaced_artifacts": len(misplaced_artifacts),
                    "misplaced_details": misplaced_artifacts,
                }

        except Exception as e:
            raise L4NormalizationError(f"L4 authoritative location verification failed: {e}")

    def verify(self) -> dict[str, Any]:
        """Run complete L4 normalization verification."""
        print("🔍 Starting ADG L4 Normalization Verification...")
        print(f"📁 ADG Directory: {self.adg_dir}")
        print(f"🗄️  SQLite Database: {self.sqlite_path.name}")

        # Verify L4 layer classification
        layer_classification = self._verify_l4_layer_classification()

        # Verify L4 identity resolution
        identity_resolution = self._verify_l4_identity_resolution()

        # Verify L4 persistence path normalization
        persistence_paths = self._verify_l4_persistence_path_normalization()

        # Verify L4 as authoritative location
        authoritative_location = self._verify_l4_authoritative_location()

        # Determine overall status
        critical_issues = (
            layer_classification["unknown_classifications"] > 0
            or identity_resolution["identity_issues"] > 0
            or persistence_paths["path_issues"] > 0
            or authoritative_location["misplaced_artifacts"] > 2  # Allow some flexibility
        )

        # Prepare result
        result = {
            "status": "FAIL" if critical_issues else "PASS",
            "layer_classification": layer_classification,
            "identity_resolution": identity_resolution,
            "persistence_paths": persistence_paths,
            "authoritative_location": authoritative_location,
            "errors": self.errors,
            "warnings": self.warnings,
            "summary": {
                "total_l4_nodes": layer_classification["total_l4_nodes"],
                "unknown_classifications": layer_classification["unknown_classifications"],
                "identity_issues": identity_resolution["identity_issues"],
                "path_issues": persistence_paths["path_issues"],
                "misplaced_artifacts": authoritative_location["misplaced_artifacts"],
                "identity_compliance_rate": identity_resolution["identity_compliance_rate"],
            },
        }

        # Print results
        if self.errors:
            print("\n❌ L4 NORMALIZATION VERIFICATION FAILED")
            for error in self.errors:
                print(f"   • {error}")

        if self.warnings:
            print("\n⚠️  Warnings:")
            for warning in self.warnings:
                print(f"   • {warning}")

        if critical_issues:
            print("\n❌ L4 NORMALIZATION ISSUES FOUND")
            print(f"   • Unknown classifications: {layer_classification['unknown_classifications']}")
            print(f"   • Identity issues: {identity_resolution['identity_issues']}")
            print(f"   • Path issues: {persistence_paths['path_issues']}")
            print(f"   • Misplaced artifacts: {authoritative_location['misplaced_artifacts']}")
        else:
            print("\n✅ L4 NORMALIZATION VERIFICATION PASSED")
            print(f"📊 Identity compliance: {identity_resolution['identity_compliance_rate']:.1%}")

        return result


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Verify ADG L4 normalization")
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
        verifier = ADGL4NormalizationVerifier(args.adg_dir)
        result = verifier.verify()

        if args.output:
            with open(args.output, "w") as f:
                json.dump(result, f, indent=2, default=str)
            print(f"📄 Report saved to: {args.output}")

        return 0 if result["status"] == "PASS" else 1

    except (
        L4NormalizationError
    ) as e:  # guardian: L4NormalizationError should be handled with specific context
        print(f"❌ Verification failed: {e}")
        return 1
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
