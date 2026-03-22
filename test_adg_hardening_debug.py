#!/usr/bin/env python3
"""
Debug test for ADG hardening implementation.
"""

import json
import sqlite3
import tempfile
from pathlib import Path

def test_wave1_provenance():
    """Test Wave 1: Provenance Hardening"""
    print("=== Wave 1: Provenance Hardening ===")

    # Test commit SHA capture
    from agentic_core.adg.extraction.static_scanner import ADGStaticScanner
    scanner = ADGStaticScanner(repo_root=Path.cwd())
    result = scanner.scan(commit_sha="test_sha_123")

    assert result.commit_sha == "test_sha_123", "Commit SHA not captured"
    assert hasattr(result, 'repo_state_hash'), "repo_state_hash missing"
    print("✓ Commit SHA capture working")
    print("✓ repo_state_hash attribute present")

def test_wave2_boundary_tagging():
    """Test Wave 2: External Dependency Normalization"""
    print("\n=== Wave 2: External Dependency Normalization ===")

    from agentic_core.adg.extraction.static_scanner import _ImportVisitor
    from agentic_core.adg.identity.normalizer import IdentityNormalizer, IdentityKind
    from unittest.mock import MagicMock

    # Test with IdentityNormalizer
    normalizer = IdentityNormalizer(Path.cwd())
    visitor = _ImportVisitor(
        module_adg_name="test_module",
        source_file="test.py",
        identity_normalizer=normalizer
    )

    assert visitor._identity_normalizer is not None, "IdentityNormalizer not passed"
    print("✓ IdentityNormalizer integration working")

    # Test boundary classification
    mock_normalizer = MagicMock()
    mock_normalizer.normalize.return_value = MagicMock(kind=IdentityKind.REPO_MODULE)

    visitor = _ImportVisitor(
        module_adg_name="test_module",
        source_file="test.py",
        identity_normalizer=mock_normalizer
    )

    edge_kind = visitor._classify_import_kind("agentic_core.L0_routing")
    assert edge_kind == "internal", f"Expected 'internal', got {edge_kind}"
    print("✓ Internal boundary tagging working")

    mock_normalizer.normalize.return_value = MagicMock(kind=IdentityKind.EXTERNAL_MODULE)
    edge_kind = visitor._classify_import_kind("requests")
    assert edge_kind == "external", f"Expected 'external', got {edge_kind}"
    print("✓ External boundary tagging working")

def test_wave3_layer_attribution():
    """Test Wave 3: Simplified Layer Attribution"""
    print("\n=== Wave 3: Simplified Layer Attribution ===")

    from tools.generate_full_adg import _infer_layer

    # Test YAML overrides
    layer = _infer_layer("agentic_core/L0_routing/config.py")
    assert layer == "L0", f"Expected 'L0', got {layer}"

    layer = _infer_layer("apps_eval/config.py")
    assert layer == "L_APP", f"Expected 'L_APP', got {layer}"

    layer = _infer_layer("tools/generate_adg.py")
    assert layer == "L_TOOLS", f"Expected 'L_TOOLS', got {layer}"

    layer = _infer_layer("pyproject.toml")
    assert layer == "L_CONFIG", f"Expected 'L_CONFIG', got {layer}"

    layer = _infer_layer("unknown/path/file.py")
    assert layer == "L_UNKNOWN", f"Expected 'L_UNKNOWN', got {layer}"

    print("✓ Layer attribution with YAML overrides working")

def test_wave4_critical_edges():
    """Test Wave 4: Critical Edge Densification"""
    print("\n=== Wave 4: Critical Edge Densification ===")

    from agentic_core.adg.extraction.static_scanner import _CriticalEdgeVisitor

    visitor = _CriticalEdgeVisitor("test_module", "test.py")

    # Test pattern matching
    assert visitor._is_determinism_seed("random.seed", None), "determinism_seed pattern failed"
    assert not visitor._is_determinism_seed("random.random", None), "Should not match random.random"

    assert visitor._is_policy_verification("verify_policy_config_unchanged", None), "policy_verification pattern failed"
    assert not visitor._is_policy_verification("some_other_func", None), "Should not match unknown function"

    assert visitor._is_guardian_gate("run_gateway_bypass_guardian", None), "guardian_gate pattern failed"
    assert not visitor._is_guardian_gate("regular_function", None), "Should not match regular function"

    print("✓ Critical edge pattern matching working")

def test_wave5_uwg_mutation_guarantees():
    """Test Wave 5: UWG Mutation Guarantees"""
    print("\n=== Wave 5: UWG Mutation Guarantees ===")

    from agentic_core.L2_execution.UniversalWriteGateway import UniversalWriteGateway

    # Test production mode validation
    try:
        UniversalWriteGateway(replay_mode=False, policy_hash="")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "policy_hash is required" in str(e), f"Wrong error message: {e}"

    try:
        UniversalWriteGateway(replay_mode=False, parent_snapshot_hash="")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "parent_snapshot_hash is required" in str(e), f"Wrong error message: {e}"

    # Test replay mode relaxation
    uwg = UniversalWriteGateway(replay_mode=True, policy_hash="", parent_snapshot_hash="")
    assert uwg.policy_hash == "", "Replay mode should allow empty policy_hash"
    assert uwg.parent_snapshot_hash == "", "Replay mode should allow empty parent_snapshot_hash"

    # Test write_through validation
    uwg = UniversalWriteGateway(
        replay_mode=False,
        policy_hash="test_policy",
        parent_snapshot_hash="test_parent"
    )

    try:
        uwg.write_through("test.txt", "content", replay_key="", mutation_signature="")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "mutation_signature is required" in str(e), f"Wrong error message: {e}"

    print("✓ UWG 4-field validation working")

def test_wave6_output_artifacts():
    """Test Wave 6: Output Artifacts"""
    print("\n=== Wave 6: Output Artifacts ===")

    from tools.generate_full_adg import _generate_standardized_reports
    from agentic_core.adg.artifact.builder_types import ADGArtifactBuilder
    from agentic_core.adg.extraction.static_scanner import ADGStaticScanner

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
            assert report_path.exists(), f"{report_name} should exist"

            # Check report is valid JSON
            with open(report_path) as f:
                data = json.load(f)
                assert "timestamp" in data, f"{report_name} missing timestamp"
                assert "schema_version" in data, f"{report_name} missing schema_version"

        # Check provenance report validation
        with open(tmpdir / "provenance_report.json") as f:
            report = json.load(f)

        validation = report["validation"]
        assert validation["has_commit_sha"], "Missing commit SHA validation"
        assert validation["has_repo_state_hash"], "Missing repo state hash validation"
        assert validation["has_scanner_digest"], "Missing scanner digest validation"
        assert validation["has_artifact_digest"], "Missing artifact digest validation"

    print("✓ Standardized reports generation working")

def main():
    """Run all debug tests."""
    print("Running ADG Hardening Debug Tests...")
    print("=" * 50)

    try:
        test_wave1_provenance()
        test_wave2_boundary_tagging()
        test_wave3_layer_attribution()
        test_wave4_critical_edges()
        test_wave5_uwg_mutation_guarantees()
        test_wave6_output_artifacts()

        print("\n" + "=" * 50)
        print("🎉 ALL TESTS PASSED! 🎉")
        print("ADG Gap Remediation implementation is working correctly!")

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    exit(main())
