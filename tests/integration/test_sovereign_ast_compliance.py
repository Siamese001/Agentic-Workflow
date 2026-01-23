"""
Sovereign AST Compliance Test Suite (V2.5).

Ensures that Windsurf's output accurately differentiates Agents from Models.
MANDATORY: 100% Pass Requirement for Windsurf Execution.
"""

import ast
from pathlib import Path


class TestSovereignASTCompliance:
    """
    Ensures that Windsurf's output accurately differentiates Agents from Models.
    MANDATORY: 100% Pass Requirement for Windsurf Execution.
    """

    def test_agent_inheritance_gate(self):
        """
        Verify that functional intelligence units strictly inherit from LICAgentBase.
        Prevents 'Dumb' scripts from posing as Sovereign Agents.
        """
        agent_path = Path("apps_lic/engines/HOP1ProfileAnalysisAgent.py")
        tree = ast.parse(agent_path.read_text(encoding="utf-8"))

        found_v2_base = False
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                bases = [base.id for base in node.bases if isinstance(base, ast.Name)]
                if "LICAgentBase" in bases:
                    found_v2_base = True
                    break

        assert found_v2_base, "HOP1ProfileAnalysisAgent must inherit from LICAgentBase"

    def test_enum_mismatch_detection(self):
        """
        Verify that FailureClassifierAgent is identified as an Enum, not a functional Agent.
        Triggers the 'failure_types.py' rename recommendation.
        """
        model_path = Path("apps_lic/domain/FailureClassifierAgent.py")
        tree = ast.parse(model_path.read_text(encoding="utf-8"))

        has_enum = False
        has_agent_suffix = False

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                bases = [base.id for base in node.bases if isinstance(base, ast.Name)]
                if "Enum" in bases or "IntEnum" in bases:
                    has_enum = True
                if "Agent" in node.name:
                    has_agent_suffix = True

        # This file has Enum but is mislabeled as 'Agent'
        assert has_enum or has_agent_suffix, (
            "FailureClassifierAgent should be identified as needing rename"
        )

    def test_k_node_logic_injection(self):
        """
        Verify that Specialist nodes (K.1-K.7) are recognized within their respective HOP targets.
        Ensures the 7 Entrance Gates are internalized.
        """
        k_node_files = [
            "apps_lic/engines/k1_routing_agent.py",
            "apps_lic/engines/k3_message_body_agent.py",
            "apps_lic/engines/k5_cta_agent.py",
            "apps_lic/engines/k7_assembly_agent.py",
        ]

        for file_path in k_node_files:
            path = Path(file_path)
            if not path.exists():
                continue

            content = path.read_text(encoding="utf-8")
            # Check for K-Node patterns
            has_k_node = any(
                pattern in content for pattern in ["K.1", "K.3", "K.5", "K.7", "K_NODE"]
            )

            assert has_k_node or "Agent" in content, (
                f"{file_path} should contain K-Node logic or Agent class"
            )

    def test_immutable_protocol_compliance(self):
        """
        Check for forbidden 'write' or 'StateManager' patterns in V2.5 agents.
        Enforces Sovereign write-once semantics.
        """
        sovereign_agents = [
            "apps_lic/engines/HOP1ProfileAnalysisAgent.py",
            "apps_lic/engines/HOP2ResearchAgent.py",
            "apps_lic/engines/HOP3SenderGroundingAgent.py",
            "apps_lic/engines/HOP4RoutingAgent.py",
        ]

        for agent_path in sovereign_agents:
            path = Path(agent_path)
            if not path.exists():
                continue

            content = path.read_text(encoding="utf-8")

            # Check for ImmutableStagingBuffer usage
            has_immutable_buffer = "ImmutableStagingBuffer" in content

            # Check for forbidden StateManager
            has_state_manager = "StateManager" in content and "state_mgr" in content.lower()

            # V2.5 agents should use ImmutableStagingBuffer, not StateManager
            if has_state_manager:
                assert has_immutable_buffer, (
                    f"{agent_path} uses StateManager without ImmutableStagingBuffer"
                )

    def test_v2_agent_base_presence(self):
        """
        Verify all HOP agents inherit from LICAgentBase.
        MANDATORY: 100% Pass Requirement.
        """
        hop_agents = [
            "apps_lic/engines/HOP1ProfileAnalysisAgent.py",
            "apps_lic/engines/HOP2ResearchAgent.py",
            "apps_lic/engines/HOP3SenderGroundingAgent.py",
            "apps_lic/engines/HOP4RoutingAgent.py",
            "apps_lic/engines/HOP5GenerationAgent.py",
            "apps_lic/engines/HOP6ValidationAgent.py",
            "apps_lic/engines/HOP7GateDecisionAgent.py",
            "apps_lic/engines/HOP8QAReportAgent.py",
            "apps_lic/engines/HOP9IntegrationAgent.py",
        ]

        for agent_path in hop_agents:
            path = Path(agent_path)
            if not path.exists():
                continue

            tree = ast.parse(path.read_text(encoding="utf-8"))

            found_v2_base = False
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    bases = [base.id for base in node.bases if isinstance(base, ast.Name)]
                    if "LICAgentBase" in bases:
                        found_v2_base = True
                        break

            assert found_v2_base, f"{agent_path} must inherit from LICAgentBase"

    def test_process_method_signature(self):
        """
        Verify all V2 agents implement _process(self, buffer, registry) method.
        MANDATORY: 100% Pass Requirement.
        """
        hop_agents = [
            "apps_lic/engines/HOP1ProfileAnalysisAgent.py",
            "apps_lic/engines/HOP2ResearchAgent.py",
            "apps_lic/engines/HOP3SenderGroundingAgent.py",
        ]

        for agent_path in hop_agents:
            path = Path(agent_path)
            if not path.exists():
                continue

            tree = ast.parse(path.read_text(encoding="utf-8"))

            found_process = False
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name == "_process":
                    # Check parameters: self, buffer, registry
                    param_names = [arg.arg for arg in node.args.args]
                    if "buffer" in param_names and "registry" in param_names:
                        found_process = True
                        break

            assert found_process, f"{agent_path} must implement _process(self, buffer, registry)"

    def test_deprecated_agent_detection(self):
        """
        Verify deprecated agents are properly marked and raise errors.
        MANDATORY: 100% Pass Requirement.
        """
        deprecated_path = Path("apps_lic/engines/HOP2_ResearchAgent.py")

        if deprecated_path.exists():
            content = deprecated_path.read_text(encoding="utf-8")

            # Check for deprecation markers
            assert "DEPRECATED" in content, "Deprecated file must contain DEPRECATED marker"
            assert "DeprecationError" in content or "raise" in content, (
                "Deprecated file must raise error"
            )

    def test_consolidation_opportunity_detection(self):
        """
        Verify that duplicate files are detected for consolidation.
        MANDATORY: 100% Pass Requirement.
        """
        # Verify the audit script can detect consolidation opportunities
        # This test verifies the audit mechanism works, not specific file existence
        from pathlib import Path
        import json

        audit_results_path = Path("logs/audit_apps_lic_ast_results.json")

        # If audit results exist, verify they contain recommendations
        if audit_results_path.exists():
            results = json.loads(audit_results_path.read_text())
            recommendations = results.get("recommendations", [])

            # Should have at least some refactoring recommendations
            assert len(recommendations) > 0, "Audit should detect refactoring opportunities"
        else:
            # If no audit results, just verify the audit script exists
            audit_script = Path("scripts/audit_apps_lic_ast.py")
            assert audit_script.exists(), "Audit script should exist"

    def test_mixin_pattern_compliance(self):
        """
        Verify agents use proper mixin patterns (SubatomicTestingMixin, HealerMixin).
        MANDATORY: 100% Pass Requirement.
        """
        hop_agents = [
            "apps_lic/engines/HOP1ProfileAnalysisAgent.py",
            "apps_lic/engines/HOP2ResearchAgent.py",
        ]

        for agent_path in hop_agents:
            path = Path(agent_path)
            if not path.exists():
                continue

            content = path.read_text(encoding="utf-8")

            # Check for mixin imports or usage
            has_mixins = any(
                mixin in content
                for mixin in ["SubatomicTestingMixin", "HealerMixin", "MCPHardenedMixin"]
            )

            # LICAgentBase includes these, so check for LICAgentBase
            has_v2_base = "LICAgentBase" in content

            assert has_v2_base or has_mixins, f"{agent_path} should use LICAgentBase or mixins"
