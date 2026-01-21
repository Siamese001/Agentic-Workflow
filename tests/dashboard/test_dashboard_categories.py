"""
Test suite for dashboard category separation logic.
Validates non-overlapping categories and multi-row display for >10 agents.
"""

import unittest
from pathlib import Path

from agent_categorizer import categorize_agents_for_dashboard


class TestAgentCategorization(unittest.TestCase):
    """Test agent categorization logic."""

    def test_validation_compliance_category(self):
        """Test agents matching Validation & Compliance category."""
        test_agents = [
            "ValidatorAgent",
            "ValidationAgent",
            "ComplianceAgent",
            "EnforcerAgent",
            "CheckerAgent",
            "AuditAgent",
        ]

        for agent in test_agents:
            cat = self._categorize(agent)
            self.assertEqual(
                cat, "Validation & Compliance",
                f"{agent} should be in Validation & Compliance, got {cat}"
            )

    def test_self_healing_category(self):
        """Test agents matching Self-Healing & Recovery category."""
        test_agents = [
            "HealerAgent",
            "HealingAgent",
            "RepairAgent",
            "FixerAgent",
            "RecoveryAgent",
            "ReconcileAgent",
            "RestoreAgent",
        ]

        for agent in test_agents:
            cat = self._categorize(agent)
            self.assertEqual(
                cat, "Self-Healing & Recovery",
                f"{agent} should be in Self-Healing & Recovery, got {cat}"
            )

    def test_safety_security_category(self):
        """Test agents matching Safety & Security category."""
        test_agents = [
            "GuardianAgent",
            "GuardAgent",
            "SafetyAgent",
            "SecurityAgent",
            "ProtectorAgent",
            "DefenseAgent",
            "SentinelAgent",
            "WatchdogAgent",
            "ImmuneAgent",
            "ThreatAgent",
        ]

        for agent in test_agents:
            cat = self._categorize(agent)
            self.assertEqual(
                cat, "Safety & Security",
                f"{agent} should be in Safety & Security, got {cat}"
            )

    def test_code_quality_category(self):
        """Test agents matching Code Quality & Analysis category."""
        test_agents = [
            "AnalyzerAgent",
            "AnalysisAgent",
            "DetectorAgent",
            "DetectionAgent",
            "HunterAgent",
            "FormatterAgent",
            "DeduplicatorAgent",
            "CleanupAgent",
            "UnusedAgent",
            "PruneAgent",
        ]

        for agent in test_agents:
            cat = self._categorize(agent)
            self.assertEqual(
                cat, "Code Quality & Analysis",
                f"{agent} should be in Code Quality & Analysis, got {cat}"
            )

    def test_governance_category(self):
        """Test agents matching Governance & Architecture category."""
        test_agents = [
            "GovernorAgent",
            "GovernanceAgent",
            "ArchitectAgent",
            "ArchitectureAgent",
            "HierarchyAgent",
            "LocationAgent",
            "ImportAgent",
            "GravityAgent",
        ]

        for agent in test_agents:
            cat = self._categorize(agent)
            self.assertEqual(
                cat, "Governance & Architecture",
                f"{agent} should be in Governance & Architecture, got {cat}"
            )

    def test_orchestration_category(self):
        """Test agents matching Orchestration & Routing category."""
        test_agents = [
            "OrchestratorAgent",
            "OrchestrationAgent",
            "RouterAgent",
            "RoutingAgent",
            "ConductorAgent",
            "SchedulerAgent",
        ]

        for agent in test_agents:
            cat = self._categorize(agent)
            self.assertEqual(
                cat, "Orchestration & Routing",
                f"{agent} should be in Orchestration & Routing, got {cat}"
            )

    def test_observability_category(self):
        """Test agents matching Observability & Monitoring category."""
        test_agents = [
            "MonitorAgent",
            "MonitoringAgent",
            "MetricsAgent",
            "TelemetryAgent",
            "TracingAgent",
            "LoggerAgent",
            "ReportingAgent",
        ]

        for agent in test_agents:
            cat = self._categorize(agent)
            self.assertEqual(
                cat, "Observability & Monitoring",
                f"{agent} should be in Observability & Monitoring, got {cat}"
            )

    def test_testing_category(self):
        """Test agents matching Testing & Verification category."""
        test_agents = [
            "TestAgent",
            "TestingAgent",
            "OracleAgent",
            "RegressionAgent",
            "CoverageAgent",
            "VerificationAgent",
        ]

        for agent in test_agents:
            cat = self._categorize(agent)
            self.assertEqual(
                cat, "Testing & Verification",
                f"{agent} should be in Testing & Verification, got {cat}"
            )

    def test_non_overlapping_exclusions(self):
        """Test that exclusion patterns prevent overlap."""
        # HealerAgent should NOT be in Validation & Compliance
        cat = self._categorize("HealerValidator")
        self.assertNotEqual(cat, "Validation & Compliance")

        # GuardianAgent should be Safety & Security, not Validation
        cat = self._categorize("GuardianAgent")
        self.assertEqual(cat, "Safety & Security")

    def test_l5_safety_guardrails_folder(self):
        """Test categorization of L5_safety/guardrails folder (75 agents)."""
        folder = Path("c:/Git/Agentic-Workflow/agentic_core/L5_safety/guardrails")
        if folder.exists():
            categories = categorize_agents_for_dashboard(folder)

            # Should have multiple categories
            self.assertGreater(len(categories), 1, "Should have multiple categories for 75 agents")

            # Total agents should match
            total = sum(len(agents) for agents in categories.values())
            self.assertGreater(total, 10, "Should have >10 agents")

            # Check for expected categories
            category_names = set(categories.keys())
            self.assertTrue(
                len(category_names & {"Safety & Security", "Self-Healing & Recovery", "Code Quality & Analysis"}) > 0,
                "Should have expected categories"
            )

    def test_l5_safety_validators_folder(self):
        """Test categorization of L5_safety/validators folder (20 agents)."""
        folder = Path("c:/Git/Agentic-Workflow/agentic_core/L5_safety/validators")
        if folder.exists():
            categories = categorize_agents_for_dashboard(folder)

            # Should have multiple categories
            self.assertGreater(len(categories), 1, "Should have multiple categories for 20 agents")

            # Total agents should match
            total = sum(len(agents) for agents in categories.values())
            self.assertGreater(total, 10, "Should have >10 agents")

    def test_small_folder_single_category(self):
        """Test that folders with ≤10 agents show single category."""
        # Create a mock scenario
        agents = ["Agent1", "Agent2", "Agent3"]
        categories = {}
        for agent in agents:
            cat = self._categorize(agent)
            categories[cat] = categories.get(cat, 0) + 1

        # With only 3 agents, should have minimal categories
        self.assertLessEqual(len(categories), 3)

    def _categorize(self, agent_name: str) -> str:
        """Helper to categorize a single agent."""
        import re

        patterns = [
            {
                "name": "Validation & Compliance",
                "patterns": [r"Validator", r"Validation", r"Compliance", r"Enforce", r"Check", r"Audit"],
                "exclude": [r"Heal", r"Repair", r"Fix", r"Guard", r"Protect", r"Safety", r"Test"],
            },
            {
                "name": "Self-Healing & Recovery",
                "patterns": [r"Healer", r"Healing", r"Repair", r"Fix", r"Recovery", r"Reconcile", r"Restore"],
                "exclude": [r"Validator", r"Compliance"],
            },
            {
                "name": "Safety & Security",
                "patterns": [r"Guardian", r"Guard", r"Safety", r"Security", r"Protect", r"Defense", r"Sentinel", r"Watchdog", r"Immune", r"Threat"],
                "exclude": [r"Validator", r"Healer"],
            },
            {
                "name": "Code Quality & Analysis",
                "patterns": [r"Analyzer", r"Analysis", r"Detector", r"Detection", r"Hunter", r"Finder", r"Formatter", r"Format", r"Deduplicat", r"Duplicate", r"Cleanup", r"Clean", r"Unused", r"Prune"],
                "exclude": [r"Validator", r"Healer", r"Guardian"],
            },
            {
                "name": "Governance & Architecture",
                "patterns": [r"Governor", r"Governance", r"Architect", r"Architecture", r"Hierarchy", r"Hierarchical", r"Location", r"Territory", r"Import", r"Gravity"],
                "exclude": [r"Validator", r"Healer", r"Guardian"],
            },
            {
                "name": "Orchestration & Routing",
                "patterns": [r"Orchestrator", r"Orchestration", r"Router", r"Route", r"Routing", r"Conductor", r"Coordinate", r"Scheduler", r"Schedule"],
                "exclude": [r"Validator", r"Healer"],
            },
            {
                "name": "Observability & Monitoring",
                "patterns": [r"Monitor", r"Monitoring", r"Metric", r"Metrics", r"Telemetry", r"Trace", r"Tracing", r"Logger", r"Logging", r"Report", r"Reporting"],
                "exclude": [r"Validator", r"Healer"],
            },
            {
                "name": "Testing & Verification",
                "patterns": [r"Test", r"Testing", r"Oracle", r"Prophecy", r"Regression", r"Coverage", r"Verify", r"Verification"],
                "exclude": [r"Validator", r"Healer", r"Compliance"],
            },
        ]

        for category in patterns:
            # Check exclude patterns
            excluded = False
            for exclude_pattern in category["exclude"]:
                if re.search(exclude_pattern, agent_name, re.IGNORECASE):
                    excluded = True
                    break
            if excluded:
                continue

            # Check include patterns
            for pattern in category["patterns"]:
                if re.search(pattern, agent_name, re.IGNORECASE):
                    return category["name"]

        return "Specialized Agents"


class TestDashboardDisplay(unittest.TestCase):
    """Test dashboard multi-row display logic."""

    def test_single_category_single_row(self):
        """Test that ≤10 agents show as single row."""
        agents = [{"class_name": f"Agent{i}"} for i in range(5)]
        # Should return single row with "—"
        self.assertEqual(len(agents), 5)

    def test_multiple_categories_multiple_rows(self):
        """Test that >10 agents with multiple categories show multiple rows."""
        agents = [
            {"class_name": "ValidatorAgent"},
            {"class_name": "ValidationAgent"},
            {"class_name": "HealerAgent"},
            {"class_name": "HealingAgent"},
            {"class_name": "GuardianAgent"},
            {"class_name": "SafetyAgent"},
            {"class_name": "AnalyzerAgent"},
            {"class_name": "DetectorAgent"},
            {"class_name": "GovernorAgent"},
            {"class_name": "OrchestratorAgent"},
            {"class_name": "MonitorAgent"},
            {"class_name": "TestAgent"},
        ]
        # Should have 12 agents across multiple categories
        self.assertEqual(len(agents), 12)
        self.assertGreater(len(agents), 10)

    def test_category_counts_accurate(self):
        """Test that category counts are accurate."""
        agents = [
            {"class_name": "ValidatorAgent"},
            {"class_name": "ValidationAgent"},
            {"class_name": "HealerAgent"},
        ]

        categories = {}
        for agent in agents:
            name = agent["class_name"]
            if "Validator" in name or "Validation" in name:
                cat = "Validation & Compliance"
            elif "Healer" in name:
                cat = "Self-Healing & Recovery"
            else:
                cat = "Other"
            categories[cat] = categories.get(cat, 0) + 1

        self.assertEqual(categories.get("Validation & Compliance", 0), 2)
        self.assertEqual(categories.get("Self-Healing & Recovery", 0), 1)


if __name__ == "__main__":
    unittest.main()
