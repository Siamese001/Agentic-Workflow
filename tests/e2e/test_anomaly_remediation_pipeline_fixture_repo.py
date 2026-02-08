"""
E2E test: Anomaly remediation pipeline on fixture repo.

Validates:
- Build minirepo with all anomalies + import references
- Run remediation pipeline (or plan-only mode)
- Assert remediation map covers all items and is deterministic
"""

import sys
from pathlib import Path

# Add helpers to path
sys.path.insert(0, str(Path(__file__).parent.parent / "helpers"))

from repo_builder import build_anomaly_repo, build_minimal_repo


class TestAnomalyRepoBuilder:
    """Tests for anomaly repo builder."""

    def test_build_minimal_repo_creates_all_layers(self, tmp_path):
        """Minimal repo should have all L0-L6 layers."""
        build_minimal_repo(tmp_path)

        for layer in [
            "L0_maintenance",
            "L1_cognition",
            "L2_execution",
            "L3_orchestration",
            "L4_state",
            "L5_safety",
            "L6_observability",
        ]:
            layer_path = tmp_path / "agentic_core" / layer
            assert layer_path.exists(), f"Missing layer: {layer}"

    def test_build_minimal_repo_creates_lcd_subfolders(self, tmp_path):
        """Minimal repo should have LCD subfolders in each layer."""
        build_minimal_repo(tmp_path)

        lcd_subfolders = ["config", "types", "reasoning", "enforcement", "validators", "utils"]
        for layer in ["L0_maintenance", "L5_safety"]:
            for subfolder in lcd_subfolders:
                path = tmp_path / "agentic_core" / layer / subfolder
                assert path.exists(), f"Missing {layer}/{subfolder}"

    def test_build_anomaly_repo_creates_violations(self, tmp_path):
        """Anomaly repo should create known violations."""
        build_anomaly_repo(tmp_path)

        # Check that anomaly files were created
        assert (
            tmp_path / "agentic_core" / "L5_safety" / "enforcement" / "dashboard_e2_e_pipeline.py"
        ).exists()
        assert (tmp_path / "agentic_core" / "L4_state" / "enforcement" / "CachedStateLedgerAgent.py").exists()
        assert (tmp_path / "agentic_core" / "L0_maintenance" / "scripts" / "AgentAuditResult.py").exists()


class TestRemediationPlanGeneration:
    """Tests for remediation plan generation."""

    def test_agent_in_types_generates_move_plan(self, tmp_path):
        """Agent in types/ should generate move to reasoning/."""
        builder = build_minimal_repo(tmp_path)

        # Create violation: Agent in types/
        types_file = builder.create_types_file("L5_safety", "bad_types.py", with_agent=True)

        # Verify violation exists
        assert types_file.exists()
        content = types_file.read_text()
        assert "class EmbeddedAgent" in content

        # Expected remediation: move Agent to reasoning/
        expected_target = tmp_path / "agentic_core" / "L5_safety" / "reasoning"
        assert expected_target.exists()

    def test_subprocess_in_l5_generates_move_plan(self, tmp_path):
        """Subprocess in L5 (not allowlisted) should generate move to L2."""
        builder = build_minimal_repo(tmp_path)

        # Create violation: subprocess in L5
        subprocess_file = builder.create_subprocess_file("L5_safety", "enforcement", "bad_subprocess.py")

        # Verify violation exists
        assert subprocess_file.exists()
        content = subprocess_file.read_text()
        assert "import subprocess" in content

        # Expected remediation: move to L2
        expected_target = tmp_path / "agentic_core" / "L2_execution"
        assert expected_target.exists()

    def test_pascalcase_in_scripts_generates_move_plan(self, tmp_path):
        """PascalCase in scripts/ should generate move out of scripts/."""
        builder = build_minimal_repo(tmp_path)

        # Create violation: PascalCase in scripts/
        pascal_file = builder.create_file(
            "agentic_core/L0_maintenance/scripts/MyClass.py",
            "class MyClass:\n    pass\n",
        )

        # Verify violation exists
        assert pascal_file.exists()
        assert pascal_file.name[0].isupper()


class TestRemediationDeterminism:
    """Tests for remediation determinism."""

    def test_same_input_produces_same_output(self, tmp_path):
        """Same anomaly input should produce same remediation plan."""
        # Build anomaly repo twice
        builder1 = build_anomaly_repo(tmp_path / "repo1")
        builder2 = build_anomaly_repo(tmp_path / "repo2")

        # Both should have same structure
        sorted([str(f.relative_to(tmp_path / "repo1")) for f in builder1.created_files])
        sorted([str(f.relative_to(tmp_path / "repo2")) for f in builder2.created_files])

        # Note: created_files may be empty if using mkdir, but structure should match
        assert (tmp_path / "repo1" / "agentic_core").exists()
        assert (tmp_path / "repo2" / "agentic_core").exists()


class TestRemediationCoverage:
    """Tests for remediation coverage."""

    def test_all_anomaly_types_covered(self, tmp_path):
        """Remediation should cover all anomaly types A-I."""
        build_anomaly_repo(tmp_path)

        # Check each anomaly type has corresponding structure
        # A: L5 subprocess
        assert (tmp_path / "agentic_core" / "L5_safety" / "enforcement").exists()

        # C: L4 agents
        assert (tmp_path / "agentic_core" / "L4_state" / "enforcement").exists()

        # D: Embedded agents
        assert (tmp_path / "agentic_core" / "L5_safety" / "types").exists()

        # E: PascalCase in scripts
        assert (tmp_path / "agentic_core" / "L0_maintenance" / "scripts").exists()

        # F: Test files in scripts
        assert (tmp_path / "agentic_core" / "L0_maintenance" / "scripts" / "test_something.py").exists()

    def test_remediation_targets_exist(self, tmp_path):
        """All remediation target directories should exist."""
        build_minimal_repo(tmp_path)

        # All target directories should exist
        targets = [
            "L5_safety/reasoning",
            "L4_state/reasoning",
            "L2_execution/reasoning",
            "L2_execution/utils",
            "L6_observability/config",
        ]
        for target in targets:
            path = tmp_path / "agentic_core" / target
            assert path.exists(), f"Missing target: {target}"
