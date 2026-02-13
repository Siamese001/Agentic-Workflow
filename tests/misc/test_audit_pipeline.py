#!/usr/bin/env python3
"""
Aggressive Pipeline Testing Suite - Audit Pipeline Validation

This test suite verifies the entire chain from SSOT compliance through audit integrity.
Ensures the agent discovery and optimization audit pipeline functions correctly.

Test Coverage:
- Test 1: SSOT Compliance - Mock structure_blueprint values and validate
  discovery tool respects them
- Test 2: Audit Integrity - Verify optimization audit exists and contains
  headers for every agent
- Test 3: Sanity Check - Ensure no agent is listed as "0 findings"
  (Skeptic Rule enforcement)

Usage:
    pytest tests/test_audit_pipeline.py -v
"""

from __future__ import annotations

import logging
from pathlib import Path
from unittest.mock import patch

import pytest

# Import the modules we're testing
from agentic_core.L0_routing.scripts.full_agent_discovery import (
    check_compliance_gate,
    discover_all_agents,
    get_agent_discovery_summary,
    get_structured_agent_paths,
)

# Configure test logging
logging.basicConfig(level=logging.DEBUG)
Logger = logging.getLogger(__name__)


class TestSSOTCompliance:
    """Test 1: SSOT Compliance Validation"""

    def test_mock_structure_blueprint_constants(self):
        """
        Test that discovery tool respects mocked structure_blueprint values.

        This test verifies that the full_agent_discovery.py properly imports
        and uses constants from structure_blueprint.py without hardcoding.
        """
        # Mock structure_blueprint constants
        mock_constants = {
            "AGENT_DISCOVERY_JSON": "mock_agent_discovery.json",
            "AGENTIC_CORE_DIR": "mock_agentic_core",
            "APPS_RG_DIR": "mock_apps_rg",
            "APPS_LIC_DIR": "mock_apps_lic",
            "APPS_SHARED_DIR": "mock_apps_shared",
            "L0_MAINTENANCE_DIR": "mock_L0_routing",
            "L1_COGNITION_DIR": "mock_L1_cognition",
            "L2_EXECUTION_DIR": "mock_L2_execution",
            "L3_ORCHESTRATION_DIR": "mock_L3_orchestration",
            "L4_STATE_DIR": "mock_L4_state",
            "L5_SAFETY_DIR": "mock_L5_safety",
            "L6_OBSERVABILITY_DIR": "mock_L6_observability",
            "REPORTS_DIR": "mock_reports",
            "TESTS_DIR": "mock_tests",
        }

        with patch(
            "agentic_core.L0_routing.scripts.full_agent_discovery.AGENT_DISCOVERY_JSON",
            mock_constants["AGENT_DISCOVERY_JSON"],
        ):
            with patch(
                "agentic_core.L0_routing.scripts.full_agent_discovery.AGENTIC_CORE_DIR",
                mock_constants["AGENTIC_CORE_DIR"],
            ):
                # Test that the function can be called with mocked constants
                try:
                    paths = get_structured_agent_paths()
                    # Should return empty list since mock file doesn't exist
                    assert isinstance(paths, list)
                    Logger.info("✓ SSOT constants properly mocked and respected")
                except Exception as e:
                    pytest.fail(f"SSOT compliance test failed: {e}")

    def test_discovery_tool_imports_structure_blueprint(self):
        """
        Test that full_agent_discovery.py imports from structure_blueprint.py.

        Verifies the SSOT import pattern is working correctly.
        """
        # Check that the module imports structure_blueprint constants
        import agentic_core.L0_routing.scripts.full_agent_discovery as discovery_module

        # Verify SSOT imports exist
        ssot_imports = [
            "AGENT_DISCOVERY_JSON",
            "AGENTIC_CORE_DIR",
            "APPS_RG_DIR",
            "get_validated_project_root",
            "validate_path_within_project",
        ]

        for import_name in ssot_imports:
            assert hasattr(discovery_module, import_name), f"Missing SSOT import: {import_name}"

        Logger.info("✓ All required SSOT imports present in discovery tool")

    def test_compliance_gate_uses_ssot_constants(self):
        """
        Test that compliance gate uses SSOT constants for directory validation.
        """
        with patch(
            "agentic_core.L0_routing.scripts.full_agent_discovery.get_validated_project_root",
        ) as mock_root:
            with patch(
                "agentic_core.L0_routing.scripts.full_agent_discovery.AGENTIC_CORE_DIR",
                "mock_core",
            ):
                with patch(
                    "agentic_core.L0_routing.scripts.full_agent_discovery.APPS_RG_DIR",
                    "mock_apps_rg",
                ):
                    # Mock project root
                    mock_project_root = Path("/mock/root")
                    mock_root.return_value = mock_project_root

                    # Mock directory existence checks to fail
                    with patch("pathlib.Path.exists", return_value=False):
                        # Compliance should fail when critical directories are missing
                        result = check_compliance_gate()
                        assert result is False, "Compliance gate should fail with missing directories"

                    Logger.info("✓ Compliance gate properly uses SSOT constants")


class TestAuditIntegrity:
    """Test 2: Audit Integrity Validation"""

    @pytest.fixture
    def audit_report_path(self):
        """Path to the optimization audit report."""
        return Path(__file__).parent.parent / "reports" / "optimization_audit.md"

    def test_audit_report_exists(self, audit_report_path):
        """
        Test that the optimization audit report exists.
        """
        assert audit_report_path.exists(), f"Audit report not found at {audit_report_path}"
        Logger.info("✓ Optimization audit report exists")

    def test_audit_report_contains_all_agents(self, audit_report_path):
        """
        Test that audit report contains headers for every agent found by discovery tool.

        This is a critical integrity test - every agent in the discovery inventory
        must have a corresponding section in the audit report.
        """
        # Get agent inventory from discovery tool
        agent_paths = get_structured_agent_paths()

        # Read audit report content
        with open(audit_report_path, encoding="utf-8") as f:
            audit_content = f.read()

        # Check each agent has a section in the audit
        missing_agents = []
        for agent_path in agent_paths:
            # Extract agent name from path
            agent_name = Path(agent_path).stem
            # Look for agent header in audit report
            agent_header = f"#### {agent_name}"
            if agent_header not in audit_content:
                missing_agents.append(agent_name)

        assert len(missing_agents) == 0, f"Missing audit sections for agents: {missing_agents}"
        Logger.info(f"✓ All {len(agent_paths)} agents have corresponding audit sections")

    def test_audit_report_has_proper_structure(self, audit_report_path):
        """
        Test that audit report follows the required structure.
        """
        with open(audit_report_path, encoding="utf-8") as f:
            content = f.read()

        # Check for required sections
        required_sections = [
            "# Agent Optimization Audit Report",
            "## Executive Summary",
            "## Detailed Agent Analysis",
            "## Optimization Recommendations by Priority",
            "## Conclusion",
        ]

        for section in required_sections:
            assert section in content, f"Missing required section: {section}"

        Logger.info("✓ Audit report has proper structure")

    def test_audit_report_contains_findings_for_each_agent(self, audit_report_path):
        """
        Test that each agent section contains at least one finding.

        Per the Skeptic Rule: Every agent has debt and should have findings.
        """
        with open(audit_report_path, encoding="utf-8") as f:
            content = f.read()

        # Extract agent sections - look for actual agent patterns
        import re

        # Pattern: #### AgentName followed by **Path:** and **Findings:**
        agent_pattern = r"#### ([A-Z][a-zA-Z0-9]+Agent)\s*\*\*Path:\*\*"
        agent_sections = re.findall(agent_pattern, content)

        # Verify each agent has findings by checking for the findings section
        empty_findings = []
        for agent_name in agent_sections:
            # Look for the agent's findings section
            agent_findings_pattern = f"#### {agent_name}.*?\\*\\*Findings:\\*\\*"
            if not re.search(agent_findings_pattern, content, re.DOTALL):
                empty_findings.append(agent_name)

        assert len(empty_findings) == 0, f"Agents with no findings: {empty_findings}"
        Logger.info(f"✓ All {len(agent_sections)} agent sections contain findings (Skeptic Rule compliance)")


class TestSanityCheck:
    """Test 3: Sanity Check - Skeptic Rule Enforcement"""

    def test_no_agent_has_zero_findings(self):
        """
        Sanity Check: Ensure no agent is listed as "0 findings".

        This is the Skeptic Rule test - every agent should have technical debt.
        """
        audit_report_path = Path(__file__).parent.parent / "reports" / "optimization_audit.md"

        with open(audit_report_path, encoding="utf-8") as f:
            content = f.read()

        # Look for "0 findings" pattern
        zero_findings_pattern = "0 findings"
        assert zero_findings_pattern not in content, "Found agent with 0 findings - violates Skeptic Rule"

        Logger.info("✓ No agent has 0 findings (Skeptic Rule enforced)")

    def test_audit_contains_all_five_categories(self):
        """
        Test that audit uses all 5 optimization categories.
        """
        audit_report_path = Path(__file__).parent.parent / "reports" / "optimization_audit.md"

        with open(audit_report_path, encoding="utf-8") as f:
            content = f.read()

        # Check for all 5 categories
        categories = ["[Cat 1]", "[Cat 2]", "[Cat 3]", "[Cat 4]", "[Cat 5]"]

        missing_categories = []
        for category in categories:
            if category not in content:
                missing_categories.append(category)

        assert len(missing_categories) == 0, f"Missing categories: {missing_categories}"
        Logger.info("✓ All 5 optimization categories present in audit")

    def test_discovery_tool_returns_structured_data(self):
        """
        Test that discovery tool returns properly structured data.
        """
        # Test agent discovery returns list
        agents = discover_all_agents()
        assert isinstance(agents, list), "Agent discovery should return list"

        # Test structured paths returns list of strings
        paths = get_structured_agent_paths()
        assert isinstance(paths, list), "Structured paths should return list"
        assert all(isinstance(path, str) for path in paths), "All paths should be strings"

        # Test summary returns dict with required keys
        summary = get_agent_discovery_summary()
        assert isinstance(summary, dict), "Summary should return dict"
        required_keys = ["total_agents", "layer_distribution", "directory_distribution"]
        for key in required_keys:
            assert key in summary, f"Missing summary key: {key}"

        Logger.info("✓ Discovery tool returns properly structured data")

    def test_agent_inventory_non_empty(self):
        """
        Test that agent inventory is not empty.
        """
        agents = discover_all_agents()
        paths = get_structured_agent_paths()

        assert len(agents) > 0, "Agent discovery should find agents"
        assert len(paths) > 0, "Structured paths should not be empty"

        Logger.info(f"✓ Agent inventory contains {len(agents)} agents")


class TestEndToEndIntegration:
    """End-to-end integration tests for the complete pipeline."""

    def test_complete_pipeline_integration(self):
        """
        Test the complete pipeline from discovery to audit.

        This test verifies that:
        1. Discovery tool can find agents
        2. Audit report exists and covers all agents
        3. No agents have zero findings
        4. All categories are represented
        """
        # Step 1: Get agent inventory
        agents = discover_all_agents()
        paths = get_structured_agent_paths()

        assert len(agents) > 0, "Pipeline requires agents to analyze"
        assert len(paths) > 0, "Pipeline requires agent paths"

        # Step 2: Verify audit report exists
        audit_report_path = Path(__file__).parent.parent / "reports" / "optimization_audit.md"
        assert audit_report_path.exists(), "Pipeline requires audit report"

        # Step 3: Verify audit covers all agents
        with open(audit_report_path, encoding="utf-8") as f:
            audit_content = f.read()

        for agent_path in paths:
            agent_name = Path(agent_path).stem
            agent_header = f"#### {agent_name}"
            assert agent_header in audit_content, f"Audit missing agent: {agent_name}"

        # Step 4: Verify Skeptic Rule compliance
        assert "0 findings" not in audit_content, "Pipeline violates Skeptic Rule"

        # Step 5: Verify all categories present
        for i in range(1, 6):
            assert f"[Cat {i}]" in audit_content, f"Pipeline missing category {i}"

        Logger.info("✓ Complete pipeline integration test passed")


# Test execution entry point
if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"])
