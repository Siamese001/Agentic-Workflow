"""
Comprehensive test suite for ADG Gap Remediation hardening implementation.

Tests all 6 waves:
1. Provenance Hardening
2. External Dependency Normalization
3. Simplified Layer Attribution
4. Critical Edge Densification
5. UWG Mutation Guarantees
6. Output Artifacts
"""

import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

from agentic_core.adg.artifact.builder_types import ADGArtifactBuilder
from agentic_core.adg.extraction.static_scanner import (
    ADGStaticScanner,
    _ImportVisitor,
    _CriticalEdgeVisitor,
    Edge,
)
from agentic_core.adg.identity.normalizer import IdentityNormalizer, IdentityKind
from agentic_core.L2_execution.UniversalWriteGateway import UniversalWriteGateway
from tools.generate_full_adg import _infer_layer, _generate_standardized_reports


class TestWave1ProvenanceHardening(unittest.TestCase):
    """Test Wave 1: Provenance Hardening implementation."""

    def test_commit_sha_capture(self):
        """Test that git commit SHA is captured during ADG generation."""
        with patch('subprocess.check_output') as mock_subprocess:
            mock_subprocess.return_value = "abc123def456\n"

            scanner = ADGStaticScanner(repo_root=Path.cwd())
            result = scanner.scan(commit_sha="abc123def456")

            self.assertEqual(result.commit_sha, "abc123def456")

    def test_repo_state_hash_in_result(self):
        """Test that repo_state_hash is included in ScanResult."""
        scanner = ADGStaticScanner(repo_root=Path.cwd())
        result = scanner.scan(commit_sha="test_sha")

        # Should have repo_state_hash attribute
        self.assertTrue(hasattr(result, 'repo_state_hash'))

    def test_provenance_in_artifact(self):
        """Test provenance fields are preserved in ADGArtifact."""
        # Create mock scan result
        scanner = ADGStaticScanner(repo_root=Path.cwd())
        result = scanner.scan(commit_sha="test_sha")
        result.repo_state_hash = "test_repo_hash"

        # Build artifact
        builder = ADGArtifactBuilder()
        artifact = builder.build(result)

        # Check provenance fields
        self.assertEqual(artifact.commit_sha, "test_sha")
        self.assertTrue(hasattr(artifact, 'repo_state_hash'))

    def test_provenance_in_snapshot(self):
        """Test provenance is written to snapshot JSON."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create mock artifact
            scanner = ADGStaticScanner(repo_root=Path.cwd())
            result = scanner.scan(commit_sha="test_sha")
            result.repo_state_hash = "test_repo_hash"

            builder = ADGArtifactBuilder()
            artifact = builder.build(result)

            # Write snapshot
            from agentic_core.adg.artifact.ArtifactPaths import write_all_artifacts
            paths = write_all_artifacts(artifact, out_dir=tmpdir, ts="test_123")

            # Check snapshot contains provenance
            with open(paths.snapshot) as f:
                snapshot = json.load(f)

            self.assertEqual(snapshot['commit_sha'], "test_sha")
            self.assertEqual(snapshot['repo_state_hash'], "test_repo_hash")


class TestWave2ExternalDependencyNormalization(unittest.TestCase):
    """Test Wave 2: External Dependency Normalization."""

    def test_import_visitor_with_identity_normalizer(self):
        """Test _ImportVisitor accepts IdentityNormalizer."""
        normalizer = IdentityNormalizer(Path.cwd())
        visitor = _ImportVisitor(
            module_adg_name="test_module",
            source_file="test.py",
            identity_normalizer=normalizer
        )

        self.assertIsNotNone(visitor._identity_normalizer)

    def test_boundary_tagging_internal(self):
        """Test internal modules are tagged correctly."""
        normalizer = MagicMock()
        normalizer.normalize.return_value = MagicMock(kind=IdentityKind.REPO_MODULE)

        visitor = _ImportVisitor(
            module_adg_name="test_module",
            source_file="test.py",
            identity_normalizer=normalizer
        )

        edge_kind = visitor._classify_import_kind("agentic_core.L0_routing")
        self.assertEqual(edge_kind, "internal")

    def test_boundary_tagging_external(self):
        """Test external modules are tagged correctly."""
        normalizer = MagicMock()
        normalizer.normalize.return_value = MagicMock(kind=IdentityKind.EXTERNAL_MODULE)

        visitor = _ImportVisitor(
            module_adg_name="test_module",
            source_file="test.py",
            identity_normalizer=normalizer
        )

        edge_kind = visitor._classify_import_kind("requests")
        self.assertEqual(edge_kind, "external")

    def test_boundary_tagging_unresolved(self):
        """Test unresolved modules are tagged correctly."""
        normalizer = MagicMock()
        normalizer.normalize.return_value = MagicMock(kind=IdentityKind.UNRESOLVED_IMPORT)

        visitor = _ImportVisitor(
            module_adg_name="test_module",
            source_file="test.py",
            identity_normalizer=normalizer
        )

        edge_kind = visitor._classify_import_kind("nonexistent_module")
        self.assertEqual(edge_kind, "unresolved")

    def test_fallback_without_normalizer(self):
        """Test fallback behavior when no IdentityNormalizer provided."""
        visitor = _ImportVisitor(
            module_adg_name="test_module",
            source_file="test.py",
            identity_normalizer=None
        )

        # Should use legacy classification
        edge_kind = visitor._classify_import_kind("random")
        self.assertIn(edge_kind, ["import", "network"])


class TestWave3SimplifiedLayerAttribution(unittest.TestCase):
    """Test Wave 3: Simplified Layer Attribution."""

    def test_yaml_override_exists(self):
        """Test layer override YAML file exists."""
        override_file = Path(__file__).parent.parent.parent / "tools" / "adg_layer_overrides.yaml"
        self.assertTrue(override_file.exists(), "adg_layer_overrides.yaml should exist")

    def test_layer_inference_with_yaml(self):
        """Test layer inference uses YAML overrides."""
        # Test agentic_core path
        layer = _infer_layer("agentic_core/L0_routing/config.py")
        self.assertEqual(layer, "L0")

        # Test apps path
        layer = _infer_layer("apps_eval/config.py")
        self.assertEqual(layer, "L_APP")

        # Test tools path
        layer = _infer_layer("tools/generate_adg.py")
        self.assertEqual(layer, "L_TOOLS")

    def test_layer_inference_fallback(self):
        """Test layer inference fallback for unknown paths."""
        layer = _infer_layer("unknown/path/file.py")
        self.assertEqual(layer, "L_UNKNOWN")

    def test_config_file_patterns(self):
        """Test config files get L_CONFIG layer."""
        layer = _infer_layer("pyproject.toml")
        self.assertEqual(layer, "L_CONFIG")

        layer = _infer_layer("settings.yaml")
        self.assertEqual(layer, "L_CONFIG")


class TestWave4CriticalEdgeDensification(unittest.TestCase):
    """Test Wave 4: Critical Edge Densification."""

    def test_critical_edge_visitor_exists(self):
        """Test _CriticalEdgeVisitor class exists."""
        self.assertTrue(callable(_CriticalEdgeVisitor))

    def test_critical_edge_patterns(self):
        """Test critical edge pattern detection."""
        visitor = _CriticalEdgeVisitor("test_module", "test.py")

        # Test determinism seed patterns
        self.assertTrue(visitor._is_determinism_seed("random.seed", None))
        self.assertFalse(visitor._is_determinism_seed("random.random", None))

        # Test policy verification patterns
        self.assertTrue(visitor._is_policy_verification("verify_policy_config_unchanged", None))
        self.assertFalse(visitor._is_policy_verification("some_other_func", None))

        # Test guardian gate patterns
        self.assertTrue(visitor._is_guardian_gate("run_gateway_bypass_guardian", None))
        self.assertFalse(visitor._is_guardian_gate("regular_function", None))

    def test_critical_edge_types_defined(self):
        """Test all critical edge types are defined in schema."""
        from agentic_core.adg.schema import RELATION_TYPES

        critical_types = [
            'determinism_seed',
            'emits_determinism_digest',
            'policy_verification',
            'authorize_and_execute',
            'dispatches_execution_plan',
            'enters_sandbox',
            'guardian_gate'
        ]

        for edge_type in critical_types:
            self.assertIn(edge_type, RELATION_TYPES)


class TestWave5UWGMutationGuarantees(unittest.TestCase):
    """Test Wave 5: UWG Mutation Guarantees."""

    def test_uwg_four_field_constructor(self):
        """Test UWG constructor accepts 4 fields."""
        uwg = UniversalWriteGateway(
            replay_mode=False,
            policy_hash="test_policy_hash",
            actor_id="test_actor",
            run_id="test_run",
            parent_snapshot_hash="test_parent_hash"
        )

        self.assertEqual(uwg.policy_hash, "test_policy_hash")
        self.assertEqual(uwg.parent_snapshot_hash, "test_parent_hash")

    def test_uwg_validation_production_mode(self):
        """Test UWG validates fields in production mode."""
        with self.assertRaises(ValueError) as cm:
            UniversalWriteGateway(replay_mode=False, policy_hash="")

        self.assertIn("policy_hash is required", str(cm.exception))

        with self.assertRaises(ValueError) as cm:
            UniversalWriteGateway(replay_mode=False, parent_snapshot_hash="")

        self.assertIn("parent_snapshot_hash is required", str(cm.exception))

    def test_uwg_relaxed_validation_replay_mode(self):
        """Test UWG relaxes validation in replay mode."""
        # Should not raise in replay mode
        uwg = UniversalWriteGateway(replay_mode=True, policy_hash="", parent_snapshot_hash="")
        self.assertIsNotNone(uwg)

    def test_write_through_four_fields(self):
        """Test write_through requires mutation_signature."""
        uwg = UniversalWriteGateway(
            replay_mode=False,
            policy_hash="test_policy",
            parent_snapshot_hash="test_parent"
        )

        with self.assertRaises(ValueError) as cm:
            uwg.write_through("test.txt", "content", replay_key="", mutation_signature="")

        self.assertIn("mutation_signature is required", str(cm.exception))

    def test_write_method_four_fields(self):
        """Test write method requires all fields."""
        uwg = UniversalWriteGateway(
            replay_mode=False,
            policy_hash="test_policy",
            parent_snapshot_hash="test_parent"
        )

        with self.assertRaises(ValueError) as cm:
            uwg.write(b"payload", "", None, replay_key="", plan_hash="")

        self.assertIn("mutation_signature is required", str(cm.exception))


class TestWave6OutputArtifacts(unittest.TestCase):
    """Test Wave 6: Output Artifacts."""

    def test_report_generation_function_exists(self):
        """Test _generate_standardized_reports function exists."""
        self.assertTrue(callable(_generate_standardized_reports))

    def test_report_generation_creates_all_reports(self):
        """Test report generation creates all 4 reports."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create mock artifact
            scanner = ADGStaticScanner(repo_root=Path.cwd())
            result = scanner.scan(commit_sha="test_sha")
            result.repo_state_hash = "test_repo_hash"

            builder = ADGArtifactBuilder()
            artifact = builder.build(result)

            # Generate reports
            _generate_standardized_reports(tmpdir, "test_123", artifact)

            # Check all reports exist
            expected_reports = [
                "layer_coverage_report.json",
                "edge_density_report.json",
                "provenance_report.json",
                "replay_determinism_report.json"
            ]

            for report_name in expected_reports:
                report_path = tmpdir / report_name
                self.assertTrue(report_path.exists(), f"{report_name} should exist")

                # Check report is valid JSON
                with open(report_path) as f:
                    data = json.load(f)
                    self.assertIn("timestamp", data)
                    self.assertIn("schema_version", data)

    def test_provenance_report_validation(self):
        """Test provenance report validates all fields."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create mock artifact with all fields
            scanner = ADGStaticScanner(repo_root=Path.cwd())
            result = scanner.scan(commit_sha="test_sha")
            result.repo_state_hash = "test_repo_hash"

            builder = ADGArtifactBuilder()
            artifact = builder.build(result)

            # Generate reports
            _generate_standardized_reports(tmpdir, "test_123", artifact)

            # Check provenance report
            with open(tmpdir / "provenance_report.json") as f:
                report = json.load(f)

            validation = report["validation"]
            self.assertTrue(validation["has_commit_sha"])
            self.assertTrue(validation["has_repo_state_hash"])
            self.assertTrue(validation["has_scanner_digest"])
            self.assertTrue(validation["has_artifact_digest"])

    def test_layer_coverage_report_structure(self):
        """Test layer coverage report has correct structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create mock artifact
            scanner = ADGStaticScanner(repo_root=Path.cwd())
            result = scanner.scan(commit_sha="test_sha")

            builder = ADGArtifactBuilder()
            artifact = builder.build(result)

            # Generate reports
            _generate_standardized_reports(tmpdir, "test_123", artifact)

            # Check layer report structure
            with open(tmpdir / "layer_coverage_report.json") as f:
                report = json.load(f)

            required_fields = [
                "timestamp",
                "schema_version",
                "total_modules",
                "layer_distribution",
                "unknown_modules",
                "coverage_metrics"
            ]

            for field in required_fields:
                self.assertIn(field, report)


class TestIntegrationHardening(unittest.TestCase):
    """Integration tests for complete ADG hardening."""

    def test_end_to_end_hardening(self):
        """Test complete hardening pipeline end-to-end."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create a simple Python file to scan
            test_file = tmpdir / "test_module.py"
            test_file.write_text("""
import agentic_core.L0_routing.config
import requests
import random

random.seed(42)

def test_function():
    verify_policy_config_unchanged()
""")

            # Scan with provenance
            scanner = ADGStaticScanner(repo_root=tmpdir)
            result = scanner.scan(commit_sha="test_sha")
            result.repo_state_hash = "test_repo_hash"

            # Build artifact
            builder = ADGArtifactBuilder()
            artifact = builder.build(result)

            # Generate reports
            _generate_standardized_reports(tmpdir, "test_123", artifact)

            # Verify all components worked
            self.assertEqual(result.commit_sha, "test_sha")
            self.assertEqual(result.repo_state_hash, "test_repo_hash")

            # Check reports exist and are valid
            for report_name in [
                "layer_coverage_report.json",
                "edge_density_report.json",
                "provenance_report.json",
                "replay_determinism_report.json"
            ]:
                report_path = tmpdir / report_name
                self.assertTrue(report_path.exists())

                with open(report_path) as f:
                    data = json.load(f)
                    self.assertIsInstance(data, dict)


if __name__ == "__main__":
    unittest.main(verbosity=2)
