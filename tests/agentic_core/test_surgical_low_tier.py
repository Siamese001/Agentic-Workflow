"""
Tests for Phase 4: Low Tier Remediation

Tests surgical healing integration for agents with 1-2 violations:
- AgentPermission (1)
- AutonomousThreatEvolutionAgent (1)
- CheckpointManagerAgent (1)
- CodeDeduplicationAgent (2)
- CredentialScannerAgent (1)
- CodeValidatorAgent (1)
- NamingAgent (1)
- NervousSystemAgent (1)
- PineconeSovereignAgent (2)
- PreCommitSovereignAgent (1)
- ReportLocationAgent (1)
- RootHygieneAgent (1)
- SubAtomicRegistryAgent (1)
- SystemArchitectAgent (1)
- ValidationOrchestratorAgent (1)
"""

import tempfile
from pathlib import Path

import pytest
from agentic_core.L5_safety.enforcement.SurgicalHealingAdapter import (
    SurgicalHealingAdapter,
)


class TestAgentPermissionIntegration:
    """Tests for AgentPermission surgical healing."""

    def test_adapter_with_restore_checkpoint(self):
        """Test restore checkpoint detection."""
        source = "class AgentPermission: pass\n"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source)
            temp_path = Path(f.name)

        try:
            adapter = SurgicalHealingAdapter(agent_name="AgentPermission")

            detection_result = {
                "type": "checkpoint_mismatch",
                "line": 1,
                "message": "Checkpoint restore mismatch",
            }

            context = adapter.create_context_from_detection(
                file_path=temp_path,
                detection_result=detection_result,
                detection_method="restore_checkpoint",
            )

            assert context is not None
            assert context.detector_agent == "AgentPermission"
        finally:
            temp_path.unlink()


class TestAutonomousThreatEvolutionAgentIntegration:
    """Tests for AutonomousThreatEvolutionAgent surgical healing."""

    def test_adapter_with_recent_detections(self):
        """Test recent detections loading."""
        source = "class AutonomousThreatEvolutionAgent: pass\n"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source)
            temp_path = Path(f.name)

        try:
            adapter = SurgicalHealingAdapter(agent_name="AutonomousThreatEvolutionAgent")

            detection_result = {
                "type": "detection_mismatch",
                "line": 1,
                "message": "Detection loading mismatch",
            }

            context = adapter.create_context_from_detection(
                file_path=temp_path,
                detection_result=detection_result,
                detection_method="_load_recent_detections",
            )

            assert context is not None
        finally:
            temp_path.unlink()


class TestCheckpointManagerAgentIntegration:
    """Tests for CheckpointManagerAgent surgical healing."""

    def test_adapter_with_list_checkpoints(self):
        """Test checkpoint listing."""
        source = "class CheckpointManagerAgent: pass\n"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source)
            temp_path = Path(f.name)

        try:
            adapter = SurgicalHealingAdapter(agent_name="CheckpointManagerAgent")

            detection_result = {
                "type": "list_mismatch",
                "line": 1,
                "message": "Checkpoint list mismatch",
            }

            context = adapter.create_context_from_detection(
                file_path=temp_path,
                detection_result=detection_result,
                detection_method="list_checkpoints",
            )

            assert context is not None
        finally:
            temp_path.unlink()


class TestCodeDeduplicationAgentIntegration:
    """Tests for CodeDeduplicationAgent surgical healing."""

    def test_adapter_with_dead_code(self):
        """Test dead code detection."""
        source = "class CodeDeduplicationAgent: pass\n"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source)
            temp_path = Path(f.name)

        try:
            adapter = SurgicalHealingAdapter(agent_name="CodeDeduplicationAgent")

            detection_results = [
                {"type": "dead_code", "line": 1, "message": "Dead code detected"},
                {"type": "scan_dead", "line": 1, "message": "Scan dead code"},
            ]

            context = adapter.create_batch_context(
                file_path=temp_path,
                detection_results=detection_results,
                detection_method="detect_dead_code",
            )

            assert context is not None
            assert len(context.violations) == 2
        finally:
            temp_path.unlink()


class TestCredentialScannerAgentIntegration:
    """Tests for CredentialScannerAgent surgical healing."""

    def test_adapter_with_credential_scan(self):
        """Test credential scanning."""
        source = "class CredentialScannerAgent: pass\n"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source)
            temp_path = Path(f.name)

        try:
            adapter = SurgicalHealingAdapter(agent_name="CredentialScannerAgent")

            detection_result = {
                "type": "credential_found",
                "line": 1,
                "message": "Potential credential detected",
            }

            context = adapter.create_context_from_detection(
                file_path=temp_path,
                detection_result=detection_result,
                detection_method="scan_for_credentials",
            )

            assert context is not None
        finally:
            temp_path.unlink()


class TestCodeValidatorAgentIntegration:
    """Tests for CodeValidatorAgent surgical healing."""

    def test_adapter_with_mcp_validation(self):
        """Test MCP validation."""
        source = "class CodeValidatorAgent: pass\n"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source)
            temp_path = Path(f.name)

        try:
            adapter = SurgicalHealingAdapter(agent_name="CodeValidatorAgent")

            detection_result = {
                "type": "mcp_violation",
                "line": 1,
                "message": "MCP validation issue",
            }

            context = adapter.create_context_from_detection(
                file_path=temp_path,
                detection_result=detection_result,
                detection_method="validate_mcp",
            )

            assert context is not None
        finally:
            temp_path.unlink()


class TestNamingAgentIntegration:
    """Tests for NamingAgent surgical healing."""

    def test_adapter_with_naming_validation(self):
        """Test naming validation."""
        source = "class NamingAgent: pass\n"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source)
            temp_path = Path(f.name)

        try:
            adapter = SurgicalHealingAdapter(agent_name="NamingAgent")

            detection_result = {
                "type": "naming_violation",
                "line": 1,
                "message": "Naming convention violation",
            }

            context = adapter.create_context_from_detection(
                file_path=temp_path,
                detection_result=detection_result,
                detection_method="validate_naming",
            )

            assert context is not None
        finally:
            temp_path.unlink()


class TestNervousSystemAgentIntegration:
    """Tests for NervousSystemAgent surgical healing."""

    def test_adapter_with_nervous_system(self):
        """Test nervous system detection."""
        source = "class NervousSystemAgent: pass\n"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source)
            temp_path = Path(f.name)

        try:
            adapter = SurgicalHealingAdapter(agent_name="NervousSystemAgent")

            detection_result = {
                "type": "system_issue",
                "line": 1,
                "message": "Nervous system issue",
            }

            context = adapter.create_context_from_detection(
                file_path=temp_path,
                detection_result=detection_result,
                detection_method="check_nervous_system",
            )

            assert context is not None
        finally:
            temp_path.unlink()


class TestPineconeSovereignAgentIntegration:
    """Tests for PineconeSovereignAgent surgical healing."""

    def test_adapter_with_pinecone_operations(self):
        """Test Pinecone operations."""
        source = "class PineconeSovereignAgent: pass\n"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source)
            temp_path = Path(f.name)

        try:
            adapter = SurgicalHealingAdapter(agent_name="PineconeSovereignAgent")

            detection_results = [
                {"type": "pinecone_op", "line": 1, "message": "Pinecone op 1"},
                {"type": "pinecone_op", "line": 1, "message": "Pinecone op 2"},
            ]

            context = adapter.create_batch_context(
                file_path=temp_path,
                detection_results=detection_results,
                detection_method="pinecone_operations",
            )

            assert context is not None
            assert len(context.violations) == 2
        finally:
            temp_path.unlink()


class TestPreCommitSovereignAgentIntegration:
    """Tests for PreCommitSovereignAgent surgical healing."""

    def test_adapter_with_precommit(self):
        """Test pre-commit validation."""
        source = "class PreCommitSovereignAgent: pass\n"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source)
            temp_path = Path(f.name)

        try:
            adapter = SurgicalHealingAdapter(agent_name="PreCommitSovereignAgent")

            detection_result = {
                "type": "precommit_issue",
                "line": 1,
                "message": "Pre-commit issue",
            }

            context = adapter.create_context_from_detection(
                file_path=temp_path,
                detection_result=detection_result,
                detection_method="validate_precommit",
            )

            assert context is not None
        finally:
            temp_path.unlink()


class TestReportLocationAgentIntegration:
    """Tests for ReportLocationAgent surgical healing."""

    def test_adapter_with_report_location(self):
        """Test report location validation."""
        source = "class ReportLocationAgent: pass\n"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source)
            temp_path = Path(f.name)

        try:
            adapter = SurgicalHealingAdapter(agent_name="ReportLocationAgent")

            detection_result = {
                "type": "location_issue",
                "line": 1,
                "message": "Report location issue",
            }

            context = adapter.create_context_from_detection(
                file_path=temp_path,
                detection_result=detection_result,
                detection_method="validate_location",
            )

            assert context is not None
        finally:
            temp_path.unlink()


class TestRootHygieneAgentIntegration:
    """Tests for RootHygieneAgent surgical healing."""

    def test_adapter_with_root_hygiene(self):
        """Test root hygiene validation."""
        source = "class RootHygieneAgent: pass\n"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source)
            temp_path = Path(f.name)

        try:
            adapter = SurgicalHealingAdapter(agent_name="RootHygieneAgent")

            detection_result = {
                "type": "hygiene_issue",
                "line": 1,
                "message": "Root hygiene issue",
            }

            context = adapter.create_context_from_detection(
                file_path=temp_path,
                detection_result=detection_result,
                detection_method="check_hygiene",
            )

            assert context is not None
        finally:
            temp_path.unlink()


class TestSubAtomicRegistryAgentIntegration:
    """Tests for SubAtomicRegistryAgent surgical healing."""

    def test_adapter_with_registry(self):
        """Test registry validation."""
        source = "class SubAtomicRegistryAgent: pass\n"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source)
            temp_path = Path(f.name)

        try:
            adapter = SurgicalHealingAdapter(agent_name="SubAtomicRegistryAgent")

            detection_result = {
                "type": "registry_issue",
                "line": 1,
                "message": "Registry issue",
            }

            context = adapter.create_context_from_detection(
                file_path=temp_path,
                detection_result=detection_result,
                detection_method="validate_registry",
            )

            assert context is not None
        finally:
            temp_path.unlink()


class TestSystemArchitectAgentIntegration:
    """Tests for SystemArchitectAgent surgical healing."""

    def test_adapter_with_architecture(self):
        """Test architecture validation."""
        source = "class SystemArchitectAgent: pass\n"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source)
            temp_path = Path(f.name)

        try:
            adapter = SurgicalHealingAdapter(agent_name="SystemArchitectAgent")

            detection_result = {
                "type": "architecture_issue",
                "line": 1,
                "message": "Architecture issue",
            }

            context = adapter.create_context_from_detection(
                file_path=temp_path,
                detection_result=detection_result,
                detection_method="validate_architecture",
            )

            assert context is not None
        finally:
            temp_path.unlink()


class TestValidationOrchestratorAgentIntegration:
    """Tests for ValidationOrchestratorAgent surgical healing."""

    def test_adapter_with_orchestration(self):
        """Test orchestration validation."""
        source = "class ValidationOrchestratorAgent: pass\n"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source)
            temp_path = Path(f.name)

        try:
            adapter = SurgicalHealingAdapter(agent_name="ValidationOrchestratorAgent")

            detection_result = {
                "type": "orchestration_issue",
                "line": 1,
                "message": "Orchestration issue",
            }

            context = adapter.create_context_from_detection(
                file_path=temp_path,
                detection_result=detection_result,
                detection_method="orchestrate_validation",
            )

            assert context is not None
        finally:
            temp_path.unlink()


class TestLowTierGenericTemplate:
    """Tests for generic low tier template application."""

    def test_template_applies_to_all_agents(self):
        """Test that template works for all low tier agents."""
        low_tier_agents = [
            "AgentPermission",
            "AutonomousThreatEvolutionAgent",
            "CheckpointManagerAgent",
            "CodeDeduplicationAgent",
            "CredentialScannerAgent",
            "CodeValidatorAgent",
            "NamingAgent",
            "NervousSystemAgent",
            "PineconeSovereignAgent",
            "PreCommitSovereignAgent",
            "ReportLocationAgent",
            "RootHygieneAgent",
            "SubAtomicRegistryAgent",
            "SystemArchitectAgent",
            "ValidationOrchestratorAgent",
        ]

        source = "def test(): pass\n"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source)
            temp_path = Path(f.name)

        try:
            for agent_name in low_tier_agents:
                adapter = SurgicalHealingAdapter(agent_name=agent_name)

                detection_result = {
                    "type": "generic_violation",
                    "line": 1,
                    "message": f"Generic violation for {agent_name}",
                }

                context = adapter.create_context_from_detection(
                    file_path=temp_path,
                    detection_result=detection_result,
                    detection_method="generic_detection",
                )

                assert context is not None, f"Failed for {agent_name}"
                assert context.detector_agent == agent_name
        finally:
            temp_path.unlink()

    def test_surgical_healing_for_low_tier(self):
        """Test surgical healing applies for low tier agents."""
        source = "def my_func():\n    pass\n"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source)
            temp_path = Path(f.name)

        try:
            adapter = SurgicalHealingAdapter(agent_name="NamingAgent")

            detection_result = {
                "type": "functiondef",
                "line": 1,
                "message": "Naming issue",
                "expected_pattern": "TODO: Fix naming",
            }

            context = adapter.create_context_from_detection(
                file_path=temp_path,
                detection_result=detection_result,
                detection_method="validate_naming",
            )

            context.violations[0].fix_type = "insert"

            result = adapter.apply_surgical_healing(context)

            assert result.status == "success"
        finally:
            temp_path.unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
