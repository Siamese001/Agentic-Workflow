"""
Orphan Agent Detection Guardian
================================
Validates that all discovered agents are properly integrated into the codebase.

This test suite ensures:
1. All agents in agent_discovery_full.json are referenced somewhere
2. No agents exist only in isolation (orphans)
3. Agents have proper test coverage
4. Agents are imported/used in production code or orchestration

USAGE:
    pytest tests/guardian/test_orphan_agents.py -v

EXPECTED RESULT:
    100% pass rate - orphan agents indicate dead code or missing integration
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Set

import pytest

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class TestOrphanAgentDetection:
    """Test suite for orphan agent detection and remediation tracking"""

    # ==========================================================================
    # KNOWN ORPHAN AGENTS (Documented - tracked for remediation)
    # These are agents with minimal references that are scheduled for review.
    # New orphan agents will cause test failures.
    # ==========================================================================

    KNOWN_ORPHAN_AGENTS: Set[str] = {
        # Legacy agents in archive folders
        "HOPOrchestratorAgent",
        # Stub agents awaiting implementation
        "ContentStrategyAgent",
        "IntelligenceLibrarianAgent",
        # Agents with only self-tests (acceptable pattern)
        "AppContentValidatorAgent",
        # === L1 Cognition Layer Orphans ===
        "LLMPromptGovernorAgent",
        "UnifiedASTValidatorAgent",
        # === L2 Execution Layer Orphans ===
        "HistorianAgent",
        # === L3 Orchestration Layer Orphans ===
        "DomainPlannerAgent",
        "DecompositionOrchestratorAgent",
        # === L4 State Layer Orphans ===
        "GravityStateAgent",
        "UiValidationAgent",
        "UnifiedCheckpointManagerAgent",
        "UnifiedStateManagementAgent",
        # === L5 Safety Layer Orphans - Red Teaming ===
        "AdversarialProbeAgent",
        "BoundaryTestingAgent",
        "ChaosEngineeringAgent",
        "PromptInjectionAgent",
        # === L5 Safety Layer Orphans - Guardrails ===
        "CostGovernorAgent",
        "DependencyPruningAgent",
        "HallucinationHunterAgent",
        # === L5 Safety Layer Orphans - Validators ===
        "GlobalComplianceAggregatorAgent",
        "GospelSyncAgent",
        "InterfaceBoundaryAgent",
        "OmniContextAgent",
        "PolicyNeuralAutoImmuneAgent",
        "PreCommitSovereignAgent",
        "SemanticDebuggerAgent",
        "SherlockAgent",
        "TestGeneratorAgent",
        # === L5 Safety Layer Orphans - Unified ===
        "UnifiedCodeDetectorAgent",
        "UnifiedCodeEnforcerAgent",
        "UnifiedCodeHealerAgent",
        "UnifiedResourceManagerAgent",
        "UnifiedSafetyDetectorAgent",
        "UnifiedSafetyExecutorAgent",
        "UnifiedSecurityManagerAgent",
        "UnifiedStructureEnforcerAgent",
        "UnifiedStructureHealerAgent",
        # === L6 Observability Layer Orphans ===
        "SovereignObservabilityAgent",
        # === Apps LIC HOP Pipeline Orphans ===
        "HOP3SenderGroundingAgent",
        "HOP4RoutingAgent",
        "HOP5GenerationAgent",
        "HOP6ValidationAgent",
        "HOP7GateDecisionAgent",
        "HOP8QAReportAgent",
        "HOP9IntegrationAgent",
    }

    # Agents that are legitimately standalone (base classes, mixins, etc.)
    STANDALONE_AGENTS: Set[str] = {
        "SovereignBaseAgent",
        "L0MaintenanceBaseAgent",
        "L1CognitionBaseAgent",
        "L2ExecutionBaseAgent",
        "L3OrchestrationBaseAgent",
        "L4StateBaseAgent",
        "L5SafetyBaseAgent",
        "L6ObservabilityBaseAgent",
        "LICAgentBase",
        "RGAgentBase",
    }

    # Minimum reference threshold for non-orphan status
    MIN_REFERENCES = 2  # At least own file + one other reference

    @pytest.fixture(scope="class")
    def agent_discovery_data(self) -> List[Dict]:
        """Load agent discovery data from SSOT JSON"""
        discovery_path = PROJECT_ROOT / "agent_discovery_full.json"
        if not discovery_path.exists():
            pytest.skip("agent_discovery_full.json not found - run discovery first")

        with open(discovery_path, "r", encoding="utf-8") as f:
            return json.load(f)

    @pytest.fixture(scope="class")
    def agent_reference_map(self, agent_discovery_data) -> Dict[str, Set[str]]:
        """Build a map of agent class names to files that reference them"""
        agent_classes = {agent["class_name"] for agent in agent_discovery_data}
        references: Dict[str, Set[str]] = {name: set() for name in agent_classes}

        # Scan Python files for agent references
        scan_dirs = [
            PROJECT_ROOT / "agentic_core",
            PROJECT_ROOT / "apps_lic",
            PROJECT_ROOT / "apps_rg",
            PROJECT_ROOT / "apps_shared",
        ]

        for scan_dir in scan_dirs:
            if not scan_dir.exists():
                continue

            for py_file in scan_dir.rglob("*.py"):
                # Skip cache and test directories for production reference count
                if "__pycache__" in str(py_file):
                    continue

                try:
                    content = py_file.read_text(encoding="utf-8")
                    for agent_class in agent_classes:
                        if agent_class in content:
                            references[agent_class].add(str(py_file.relative_to(PROJECT_ROOT)))
                except Exception:
                    continue

        return references

    @pytest.fixture(scope="class")
    def test_reference_map(self, agent_discovery_data) -> Dict[str, Set[str]]:
        """Build a map of agent class names to test files that reference them"""
        agent_classes = {agent["class_name"] for agent in agent_discovery_data}
        references: Dict[str, Set[str]] = {name: set() for name in agent_classes}

        # Scan test files for agent references
        tests_dir = PROJECT_ROOT / "tests"
        if not tests_dir.exists():
            return references

        for py_file in tests_dir.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue

            try:
                content = py_file.read_text(encoding="utf-8")
                for agent_class in agent_classes:
                    if agent_class in content:
                        references[agent_class].add(str(py_file.relative_to(PROJECT_ROOT)))
            except Exception:
                continue

        return references

    # ==========================================================================
    # ORPHAN DETECTION TESTS
    # ==========================================================================

    def test_agent_discovery_exists(self):
        """Verify agent_discovery_full.json exists and is valid"""
        discovery_path = PROJECT_ROOT / "agent_discovery_full.json"
        assert discovery_path.exists(), "agent_discovery_full.json must exist"

        with open(discovery_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert isinstance(data, list), "Discovery data must be a list"
        assert len(data) > 0, "Discovery data must not be empty"

    def test_all_agents_have_file_path(self, agent_discovery_data):
        """Verify all discovered agents have valid file paths"""
        missing_paths = []
        for agent in agent_discovery_data:
            if not agent.get("path"):
                missing_paths.append(agent.get("class_name", "Unknown"))

        assert not missing_paths, f"Agents missing file paths: {missing_paths}"

    def test_no_new_orphan_agents(self, agent_discovery_data, agent_reference_map):
        """Verify no new orphan agents exist beyond known exceptions"""
        orphan_agents = []

        for agent in agent_discovery_data:
            class_name = agent["class_name"]

            # Skip known orphans and standalone agents
            if class_name in self.KNOWN_ORPHAN_AGENTS:
                continue
            if class_name in self.STANDALONE_AGENTS:
                continue

            # Check reference count
            ref_count = len(agent_reference_map.get(class_name, set()))
            if ref_count < self.MIN_REFERENCES:
                orphan_agents.append(
                    {
                        "class_name": class_name,
                        "path": agent.get("path", "Unknown"),
                        "references": ref_count,
                    }
                )

        if orphan_agents:
            orphan_report = "\n".join(
                f"  - {o['class_name']} ({o['path']}): {o['references']} refs"
                for o in orphan_agents
            )
            pytest.fail(
                f"Found {len(orphan_agents)} new orphan agents:\n{orphan_report}\n\n"
                "Add to KNOWN_ORPHAN_AGENTS if intentional, or integrate properly."
            )

    def test_known_orphans_still_exist(self, agent_discovery_data):
        """Verify known orphan agents still exist (for tracking)"""
        discovered_classes = {agent["class_name"] for agent in agent_discovery_data}

        # Check which known orphans have been removed (good!)
        removed_orphans = self.KNOWN_ORPHAN_AGENTS - discovered_classes

        if removed_orphans:
            # This is informational - orphans being removed is good
            print(f"\nINFO: {len(removed_orphans)} known orphans have been removed:")
            for orphan in removed_orphans:
                print(f"  - {orphan}")
            print("Consider removing these from KNOWN_ORPHAN_AGENTS set.")

    def test_agents_have_test_coverage(self, agent_discovery_data, test_reference_map):
        """Verify agents have at least one test file referencing them"""
        untested_agents = []

        for agent in agent_discovery_data:
            class_name = agent["class_name"]

            # Skip base/standalone agents
            if class_name in self.STANDALONE_AGENTS:
                continue

            # Check test reference count
            test_refs = test_reference_map.get(class_name, set())
            if len(test_refs) == 0:
                untested_agents.append(
                    {
                        "class_name": class_name,
                        "path": agent.get("path", "Unknown"),
                    }
                )

        # Report but don't fail - test coverage is advisory
        if untested_agents:
            print(f"\nADVISORY: {len(untested_agents)} agents lack test coverage:")
            for agent in untested_agents[:10]:  # Show first 10
                print(f"  - {agent['class_name']} ({agent['path']})")
            if len(untested_agents) > 10:
                print(f"  ... and {len(untested_agents) - 10} more")

    def test_legacy_archive_agents_documented(self, agent_discovery_data):
        """Verify agents in legacy/archive folders are documented as orphans"""
        archive_agents = []

        for agent in agent_discovery_data:
            path = agent.get("path", "").replace("\\", "/")
            class_name = agent["class_name"]

            # Check if in archive/legacy folder
            if "legacy" in path.lower() or "archive" in path.lower():
                if class_name not in self.KNOWN_ORPHAN_AGENTS:
                    archive_agents.append(
                        {
                            "class_name": class_name,
                            "path": path,
                        }
                    )

        if archive_agents:
            report = "\n".join(f"  - {a['class_name']} ({a['path']})" for a in archive_agents)
            pytest.fail(
                f"Found {len(archive_agents)} archive agents not in "
                f"KNOWN_ORPHAN_AGENTS:\n{report}\n\n"
                "Add to KNOWN_ORPHAN_AGENTS or remove from archive."
            )

    # ==========================================================================
    # ORPHAN AGENT INVENTORY TESTS
    # ==========================================================================

    def test_orphan_inventory_report(self, agent_discovery_data, agent_reference_map):
        """Generate orphan agent inventory for documentation"""
        inventory = {
            "total_agents": len(agent_discovery_data),
            "known_orphans": len(self.KNOWN_ORPHAN_AGENTS),
            "standalone_agents": len(self.STANDALONE_AGENTS),
            "well_integrated": 0,
            "low_integration": 0,
        }

        for agent in agent_discovery_data:
            class_name = agent["class_name"]
            if class_name in self.STANDALONE_AGENTS:
                continue

            ref_count = len(agent_reference_map.get(class_name, set()))
            if ref_count >= self.MIN_REFERENCES:
                inventory["well_integrated"] += 1
            else:
                inventory["low_integration"] += 1

        # Report inventory
        print("\n=== ORPHAN AGENT INVENTORY ===")
        print(f"Total Agents: {inventory['total_agents']}")
        print(f"Known Orphans: {inventory['known_orphans']}")
        print(f"Standalone (Base): {inventory['standalone_agents']}")
        print(f"Well Integrated: {inventory['well_integrated']}")
        print(f"Low Integration: {inventory['low_integration']}")

        # This test always passes - it's for reporting
        assert True


class TestOrphanAgentRemediation:
    """Test suite for orphan agent remediation tracking"""

    def test_remediation_plan_exists(self):
        """Verify orphan remediation is tracked in documentation"""
        # Check for remediation documentation
        docs_to_check = [
            PROJECT_ROOT / "docs" / "reports" / "ORPHAN_AGENT_REMEDIATION.md",
            PROJECT_ROOT / "ORPHAN_AGENTS_REPORT.md",
        ]

        # This is advisory - we'll create the report if it doesn't exist
        for doc in docs_to_check:
            if doc.exists():
                print(f"\nFound remediation doc: {doc}")
                return

        print("\nADVISORY: No orphan remediation documentation found.")
        print("Consider creating ORPHAN_AGENTS_REPORT.md to track remediation.")

    def test_no_duplicate_agent_classes(self, agent_discovery_data=None):
        """Verify no duplicate agent class names exist"""
        discovery_path = PROJECT_ROOT / "agent_discovery_full.json"
        if not discovery_path.exists():
            pytest.skip("agent_discovery_full.json not found")

        with open(discovery_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        class_names = [agent["class_name"] for agent in data]
        duplicates = [name for name in class_names if class_names.count(name) > 1]

        if duplicates:
            unique_duplicates = list(set(duplicates))
            pytest.fail(
                f"Found {len(unique_duplicates)} duplicate agent class names: {unique_duplicates}"
            )
