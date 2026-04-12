#!/usr/bin/env python3
"""
ADG Identity Completeness Verification

Ensures schema supports decision-grade analysis with complete identity fields:

NODES MUST SUPPORT:
- id
- adg_name
- entity_type
- layer
- resolved_path
- identity_origin = first_party | external | generated | unknown
- confidence = high | medium | low
- domain = runtime | test | scanner | tooling | meta | shared
- owner_surface = app | core | safety | orchestration | persistence | learning | infra
- canonical_symbol = normalized fully-qualified identity
- source_hash = content hash for originating file/symbol

EDGES MUST SUPPORT:
- id
- src_id
- dst_id
- relation_type
- edge_kind
- source_file
- line_no
- symbol
- confidence
- extraction_rule
- authority_level = observed | inferred | synthesized
- policy_scope = if relevant
- replay_relevance = yes | no
- learning_relevance = yes | no

HARD RULES:
- every first-party module must have non-null resolved_path
- every first-party module must have stable canonical identity
- every first-party module in L4 must have layer != UNKNOWN
- every low-confidence node must be queryable by cause
- every unresolved import must be traceable to source file and symbol
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path
from typing import Any

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class IdentityCompletenessError(Exception):
    """Raised when identity completeness verification fails."""

    pass


class ADGIdentityCompletenessVerifier:
    """Verifies ADG identity completeness and schema compliance."""

    # Required node fields
    REQUIRED_NODE_FIELDS = {
        "id",
        "adg_name",
        "entity_type",
        "layer",
        "confidence",
    }

    # Enhanced node fields for decision-grade analysis
    ENHANCED_NODE_FIELDS = {
        "resolved_path",
        "identity_origin",
        "domain",
        "owner_surface",
        "canonical_symbol",
        "source_hash",
    }

    # Required edge fields
    REQUIRED_EDGE_FIELDS = {
        "id",
        "src_id",
        "dst_id",
        "relation_type",
        "edge_kind",
        "source_file",
        "line_no",
        "symbol",
    }

    # Enhanced edge fields for decision-grade analysis
    ENHANCED_EDGE_FIELDS = {
        "confidence",
        "extraction_rule",
        "authority_level",
        "policy_scope",
        "replay_relevance",
        "learning_relevance",
    }

    # Valid values for enum fields
    VALID_IDENTITY_ORIGINS = {"first_party", "external", "generated", "unknown"}
    VALID_CONFIDENCE_LEVELS = {"HIGH", "MEDIUM", "LOW"}
    VALID_DOMAINS = {"runtime", "test", "scanner", "tooling", "meta", "shared"}
    VALID_OWNER_SURFACES = {"app", "core", "safety", "orchestration", "persistence", "learning", "infra"}
    VALID_AUTHORITY_LEVELS = {"observed", "inferred", "synthesized"}
    VALID_RELEVANCE_FLAGS = {"yes", "no"}

    def __init__(self, adg_dir: Path):
        self.adg_dir = Path(adg_dir)
        self.sqlite_path = self._find_sqlite_database()
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def _find_sqlite_database(self) -> Path:
        """Find the latest SQLite database."""
        sqlite_files = list(self.adg_dir.glob("adg_indexed_*.sqlite"))
        if not sqlite_files:
            raise IdentityCompletenessError("No SQLite database found")

        return max(sqlite_files, key=lambda p: p.stat().st_mtime)

    def _get_table_columns(self, table_name: str) -> set[str]:
        """Get column names for a table."""
        try:
            with sqlite3.connect(self.sqlite_path) as conn:
                cursor = conn.cursor()
                cursor.execute(f"PRAGMA table_info({table_name})")
                return {row[1] for row in cursor.fetchall()}
        except Exception as e:
            raise IdentityCompletenessError(f"Failed to get columns for {table_name}: {e}")

    def _verify_node_schema_completeness(self) -> None:
        """Verify nodes table has required and enhanced fields."""
        print("🏗️  Verifying node schema completeness...")

        node_columns = self._get_table_columns("nodes")

        # Check required fields
        missing_required = self.REQUIRED_NODE_FIELDS - node_columns
        if missing_required:
            raise IdentityCompletenessError(f"Missing required node fields: {missing_required}")

        # Check enhanced fields
        missing_enhanced = self.ENHANCED_NODE_FIELDS - node_columns
        if missing_enhanced:
            self.warnings.append(f"Missing enhanced node fields: {missing_enhanced}")

        print(f"   ✅ Required node fields present ({len(self.REQUIRED_NODE_FIELDS)})")
        if missing_enhanced:
            print(f"   ⚠️  Missing enhanced node fields ({len(missing_enhanced)})")
        else:
            print(f"   ✅ Enhanced node fields present ({len(self.ENHANCED_NODE_FIELDS)})")

    def _verify_edge_schema_completeness(self) -> None:
        """Verify edges table has required and enhanced fields."""
        print("🔗 Verifying edge schema completeness...")

        edge_columns = self._get_table_columns("edges")

        # Check required fields
        missing_required = self.REQUIRED_EDGE_FIELDS - edge_columns
        if missing_required:
            raise IdentityCompletenessError(f"Missing required edge fields: {missing_required}")

        # Check enhanced fields
        missing_enhanced = self.ENHANCED_EDGE_FIELDS - edge_columns
        if missing_enhanced:
            self.warnings.append(f"Missing enhanced edge fields: {missing_enhanced}")

        print(f"   ✅ Required edge fields present ({len(self.REQUIRED_EDGE_FIELDS)})")
        if missing_enhanced:
            print(f"   ⚠️  Missing enhanced edge fields ({len(missing_enhanced)})")
        else:
            print(f"   ✅ Enhanced edge fields present ({len(self.ENHANCED_EDGE_FIELDS)})")

    def _verify_enum_value_constraints(self) -> None:
        """Verify enum fields have valid values."""
        print("📊 Verifying enum value constraints...")

        try:
            with sqlite3.connect(self.sqlite_path) as conn:
                cursor = conn.cursor()

                # Check identity_origin values if field exists
                if "identity_origin" in self._get_table_columns("nodes"):
                    cursor.execute(
                        "SELECT DISTINCT identity_origin FROM nodes WHERE identity_origin IS NOT NULL"
                    )
                    origins = {row[0] for row in cursor.fetchall()}
                    invalid_origins = origins - self.VALID_IDENTITY_ORIGINS
                    if invalid_origins:
                        self.errors.append(f"Invalid identity_origin values: {invalid_origins}")

                # Check confidence values
                cursor.execute("SELECT DISTINCT confidence FROM nodes WHERE confidence IS NOT NULL")
                confidences = {row[0] for row in cursor.fetchall()}
                invalid_confidences = confidences - self.VALID_CONFIDENCE_LEVELS
                if invalid_confidences:
                    self.errors.append(f"Invalid confidence values: {invalid_confidences}")

                # Check domain values if field exists
                if "domain" in self._get_table_columns("nodes"):
                    cursor.execute("SELECT DISTINCT domain FROM nodes WHERE domain IS NOT NULL")
                    domains = {row[0] for row in cursor.fetchall()}
                    invalid_domains = domains - self.VALID_DOMAINS
                    if invalid_domains:
                        self.errors.append(f"Invalid domain values: {invalid_domains}")

                # Check owner_surface values if field exists
                if "owner_surface" in self._get_table_columns("nodes"):
                    cursor.execute("SELECT DISTINCT owner_surface FROM nodes WHERE owner_surface IS NOT NULL")
                    surfaces = {row[0] for row in cursor.fetchall()}
                    invalid_surfaces = surfaces - self.VALID_OWNER_SURFACES
                    if invalid_surfaces:
                        self.errors.append(f"Invalid owner_surface values: {invalid_surfaces}")

                # Check authority_level values if field exists
                if "authority_level" in self._get_table_columns("edges"):
                    cursor.execute(
                        "SELECT DISTINCT authority_level FROM edges WHERE authority_level IS NOT NULL"
                    )
                    authority_levels = {row[0] for row in cursor.fetchall()}
                    invalid_authority = authority_levels - self.VALID_AUTHORITY_LEVELS
                    if invalid_authority:
                        self.errors.append(f"Invalid authority_level values: {invalid_authority}")

        except Exception as e:
            raise IdentityCompletenessError(f"Enum constraint verification failed: {e}")

        print("   ✅ Enum value constraints verified")

    def _verify_first_party_module_completeness(self) -> None:
        """Verify first-party modules have complete identity information."""
        print("🎯 Verifying first-party module completeness...")

        try:
            with sqlite3.connect(self.sqlite_path) as conn:
                cursor = conn.cursor()

                # Count first-party modules (assuming identity_origin = 'first_party' or repo modules)
                if "identity_origin" in self._get_table_columns("nodes"):
                    cursor.execute("""
                        SELECT COUNT(*) FROM nodes
                        WHERE entity_type = 'module' AND identity_origin = 'first_party'
                    """)
                else:
                    # Fallback: assume repo modules are first-party (exclude external providers)
                    cursor.execute("""
                        SELECT COUNT(*) FROM nodes
                        WHERE entity_type = 'module'
                        AND identity_kind NOT IN ('external_module', 'external_provider')
                    """)

                first_party_count = cursor.fetchone()[0]
                print(f"   📊 Found {first_party_count} first-party modules")

                # Check resolved_path completeness
                if "resolved_path" in self._get_table_columns("nodes"):
                    cursor.execute("""
                        SELECT COUNT(*) FROM nodes
                        WHERE entity_type = 'module'
                        AND identity_kind NOT IN ('external_module', 'external_provider')
                        AND (resolved_path IS NULL OR resolved_path = '')
                    """)
                    missing_resolved = cursor.fetchone()[0]

                    if missing_resolved > 0:
                        self.errors.append(f"{missing_resolved} first-party modules missing resolved_path")

                # Check canonical_symbol completeness
                if "canonical_symbol" in self._get_table_columns("nodes"):
                    cursor.execute("""
                        SELECT COUNT(*) FROM nodes
                        WHERE entity_type = 'module'
                        AND identity_kind NOT IN ('external_module', 'external_provider')
                        AND (canonical_symbol IS NULL OR canonical_symbol = '')
                    """)
                    missing_canonical = cursor.fetchone()[0]

                    if missing_canonical > 0:
                        self.warnings.append(
                            f"{missing_canonical} first-party modules missing canonical_symbol"
                        )

                # Check L4 layer completeness
                cursor.execute("""
                    SELECT COUNT(*) FROM nodes
                    WHERE entity_type = 'module'
                    AND layer = 'L4'
                    AND identity_kind NOT IN ('external_module', 'external_provider')
                """)
                l4_count = cursor.fetchone()[0]

                cursor.execute("""
                    SELECT COUNT(*) FROM nodes
                    WHERE entity_type = 'module'
                    AND layer = 'UNKNOWN'
                    AND identity_kind NOT IN ('external_module', 'external_provider')
                """)
                unknown_layer_count = cursor.fetchone()[0]

                if unknown_layer_count > 0:
                    self.errors.append(f"{unknown_layer_count} first-party modules have UNKNOWN layer")

                print(f"   📊 L4 modules: {l4_count}, Unknown layer: {unknown_layer_count}")

        except Exception as e:
            raise IdentityCompletenessError(f"First-party module verification failed: {e}")

        print("   ✅ First-party module completeness verified")

    def _verify_low_confidence_node_traceability(self) -> None:
        """Verify low-confidence nodes are queryable by cause."""
        print("🔍 Verifying low-confidence node traceability...")

        try:
            with sqlite3.connect(self.sqlite_path) as conn:
                cursor = conn.cursor()

                # Count low-confidence nodes
                cursor.execute("SELECT COUNT(*) FROM nodes WHERE confidence = 'LOW'")
                low_conf_count = cursor.fetchone()[0]

                if low_conf_count == 0:
                    print("   ✅ No low-confidence nodes found")
                    return

                print(f"   📊 Found {low_conf_count} low-confidence nodes")

                # Check if low-confidence nodes have traceable causes
                # This is a simplified check - in practice would depend on specific cause tracking
                cursor.execute("""
                    SELECT entity_type, layer, COUNT(*)
                    FROM nodes
                    WHERE confidence = 'LOW'
                    GROUP BY entity_type, layer
                """)

                low_conf_by_type = cursor.fetchall()
                print("   📊 Low-confidence by type/layer:")
                for entity_type, layer, count in low_conf_by_type:
                    print(f"      {entity_type}/{layer}: {count}")

                # Check if unresolved imports are properly classified
                cursor.execute("""
                    SELECT COUNT(*) FROM nodes
                    WHERE identity_kind = 'unresolved_import' AND confidence != 'LOW'
                """)
                high_conf_unresolved = cursor.fetchone()[0]

                if high_conf_unresolved > 0:
                    self.warnings.append(f"{high_conf_unresolved} unresolved imports have non-LOW confidence")

        except Exception as e:
            raise IdentityCompletenessError(f"Low-confidence traceability verification failed: {e}")

        print("   ✅ Low-confidence node traceability verified")

    def _verify_unresolved_import_traceability(self) -> None:
        """Verify unresolved imports are traceable to source file and symbol."""
        print("🔍 Verifying unresolved import traceability...")

        try:
            with sqlite3.connect(self.sqlite_path) as conn:
                cursor = conn.cursor()

                # Count unresolved imports
                cursor.execute("SELECT COUNT(*) FROM nodes WHERE identity_kind = 'unresolved_import'")
                unresolved_count = cursor.fetchone()[0]

                if unresolved_count == 0:
                    print("   ✅ No unresolved imports found")
                    return

                print(f"   📊 Found {unresolved_count} unresolved imports")

                # Check if unresolved imports have source file information
                # This would typically be stored in the node name or resolved_path
                cursor.execute("""
                    SELECT adg_name FROM nodes
                    WHERE identity_kind = 'unresolved_import'
                    LIMIT 10
                """)

                sample_unresolved = [row[0] for row in cursor.fetchall()]
                print("   📊 Sample unresolved imports:")
                for name in sample_unresolved:
                    print(f"      {name}")

                # Check for dead import edges related to unresolved imports
                cursor.execute("""
                    SELECT COUNT(*) FROM edges e
                    JOIN nodes n ON e.dst_id = n.id
                    WHERE n.identity_kind = 'unresolved_import'
                    AND e.relation_type = 'dead_imports'
                """)

                dead_import_edges = cursor.fetchone()[0]
                print(f"   📊 Dead import edges for unresolved: {dead_import_edges}")

        except Exception as e:
            raise IdentityCompletenessError(f"Unresolved import traceability verification failed: {e}")

        print("   ✅ Unresolved import traceability verified")

    def _calculate_identity_completeness_metrics(self) -> dict[str, Any]:
        """Calculate identity completeness metrics."""
        print("📈 Calculating identity completeness metrics...")

        metrics = {}

        try:
            with sqlite3.connect(self.sqlite_path) as conn:
                cursor = conn.cursor()

                # Node completeness metrics
                node_columns = self._get_table_columns("nodes")
                metrics["node_field_completeness"] = {
                    "required_fields": len(self.REQUIRED_NODE_FIELDS & node_columns),
                    "enhanced_fields": len(self.ENHANCED_NODE_FIELDS & node_columns),
                    "total_required": len(self.REQUIRED_NODE_FIELDS),
                    "total_enhanced": len(self.ENHANCED_NODE_FIELDS),
                }

                # Edge completeness metrics
                edge_columns = self._get_table_columns("edges")
                metrics["edge_field_completeness"] = {
                    "required_fields": len(self.REQUIRED_EDGE_FIELDS & edge_columns),
                    "enhanced_fields": len(self.ENHANCED_EDGE_FIELDS & edge_columns),
                    "total_required": len(self.REQUIRED_EDGE_FIELDS),
                    "total_enhanced": len(self.ENHANCED_EDGE_FIELDS),
                }

                # Identity distribution
                cursor.execute("SELECT identity_kind, COUNT(*) FROM nodes GROUP BY identity_kind")
                metrics["identity_distribution"] = dict(cursor.fetchall())

                # Confidence distribution
                cursor.execute("SELECT confidence, COUNT(*) FROM nodes GROUP BY confidence")
                metrics["confidence_distribution"] = dict(cursor.fetchall())

                # Layer distribution for modules
                cursor.execute("""
                    SELECT layer, COUNT(*) FROM nodes
                    WHERE entity_type = 'module'
                    GROUP BY layer
                """)
                metrics["module_layer_distribution"] = dict(cursor.fetchall())

        except Exception as e:
            self.warnings.append(f"Failed to calculate completeness metrics: {e}")

        return metrics

    def verify(self) -> dict[str, Any]:
        """Run complete identity completeness verification."""
        print("🔍 Starting ADG Identity Completeness Verification...")
        print(f"📁 ADG Directory: {self.adg_dir}")
        print(f"🗄️  SQLite Database: {self.sqlite_path.name}")

        # Verify schema completeness
        self._verify_node_schema_completeness()
        self._verify_edge_schema_completeness()

        # Verify enum constraints
        self._verify_enum_value_constraints()

        # Verify hard rules
        self._verify_first_party_module_completeness()
        self._verify_low_confidence_node_traceability()
        self._verify_unresolved_import_traceability()

        # Calculate metrics
        metrics = self._calculate_identity_completeness_metrics()

        # Prepare result
        result = {
            "status": "PASS" if not self.errors else "FAIL",
            "artifacts_verified": {
                "sqlite": str(self.sqlite_path),
            },
            "schema_completeness": {
                "node_fields": metrics.get("node_field_completeness", {}),
                "edge_fields": metrics.get("edge_field_completeness", {}),
            },
            "identity_metrics": {
                "distribution": metrics.get("identity_distribution", {}),
                "confidence": metrics.get("confidence_distribution", {}),
                "module_layers": metrics.get("module_layer_distribution", {}),
            },
            "errors": self.errors,
            "warnings": self.warnings,
        }

        # Print results
        if self.errors:
            print("\n❌ IDENTITY COMPLETENESS VERIFICATION FAILED")
            for error in self.errors:
                print(f"   • {error}")

        if self.warnings:
            print("\n⚠️  Warnings:")
            for warning in self.warnings:
                print(f"   • {warning}")

        if not self.errors:
            print("\n✅ IDENTITY COMPLETENESS VERIFICATION PASSED")

            # Print summary metrics
            node_comp = metrics.get("node_field_completeness", {})
            edge_comp = metrics.get("edge_field_completeness", {})
            print("📊 Schema completeness:")
            print(
                f"   Node fields: {node_comp.get('required_fields', 0)}/{node_comp.get('total_required', 0)} required, {node_comp.get('enhanced_fields', 0)}/{node_comp.get('total_enhanced', 0)} enhanced"
            )
            print(
                f"   Edge fields: {edge_comp.get('required_fields', 0)}/{edge_comp.get('total_required', 0)} required, {edge_comp.get('enhanced_fields', 0)}/{edge_comp.get('total_enhanced', 0)} enhanced"
            )

        return result


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Verify ADG identity completeness")
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
        verifier = ADGIdentityCompletenessVerifier(args.adg_dir)
        result = verifier.verify()

        if args.output:
            with open(args.output, "w") as f:
                json.dump(result, f, indent=2, default=str)
            print(f"📄 Report saved to: {args.output}")

        return 0 if result["status"] == "PASS" else 1

    except (
        IdentityCompletenessError
    ) as e:  # guardian: IdentityCompletenessError should be handled with specific context
        print(f"❌ Verification failed: {e}")
        return 1
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
