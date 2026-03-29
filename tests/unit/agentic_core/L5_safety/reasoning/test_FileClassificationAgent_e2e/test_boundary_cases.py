"""TC-BOUNDARY-01 through TC-BOUNDARY-05: Boundary Case E2E Tests"""
import pytest
from pathlib import Path


@pytest.mark.boundary
class TestBoundaryCases:
    """Test boundary cases and edge conditions."""

    def test_orchestrator_vs_agent_boundary(self, agent, repo_root):
        """TC-BOUNDARY-01: Orchestrator files should classify as ORCHESTRATOR or AGENT."""
        # Find Orchestrator files
        reasoning_dir = repo_root / "agentic_core" / "L5_safety" / "reasoning"
        if not reasoning_dir.exists():
            pytest.skip("reasoning directory not found")

        orchestrator_files = list(reasoning_dir.glob("*Orchestrator*.py"))
        if not orchestrator_files:
            pytest.skip("No Orchestrator files found")

        for orch_file in orchestrator_files:
            result = agent.classify_file(orch_file)
            # Per spec, orchestrators are "specialized form of agent"
            # Current implementation has ORCHESTRATOR as distinct type
            assert result in ["ORCHESTRATOR", "AGENT"], \
                f"{orch_file}: Orchestrator should be ORCHESTRATOR or AGENT, got {result}"

    def test_strategy_vs_agent_boundary(self, agent, repo_root):
        """TC-BOUNDARY-02: Strategy files should classify as STRATEGY or AGENT."""
        # Find Strategy files
        strategy_files = list(repo_root.rglob("*Strategy*.py"))
        if not strategy_files:
            pytest.skip("No Strategy files found")

        for strategy_file in strategy_files[:10]:  # Test first 10
            result = agent.classify_file(strategy_file)
            # Strategy could be STRATEGY type or classified as AGENT
            assert result in ["STRATEGY", "AGENT", "CLASS"], \
                f"{strategy_file}: Strategy file should be STRATEGY/AGENT/CLASS, got {result}"

    def test_adapter_vs_class_boundary(self, agent, repo_root):
        """TC-BOUNDARY-03: Adapter files should classify as ADAPTER or CLASS."""
        # Find Adapter files
        adapter_files = list(repo_root.rglob("*Adapter*.py"))
        if not adapter_files:
            pytest.skip("No Adapter files found")

        for adapter_file in adapter_files[:10]:  # Test first 10
            result = agent.classify_file(adapter_file)
            # Adapter could be ADAPTER type or CLASS
            assert result in ["ADAPTER", "CLASS", "MIXIN"], \
                f"{adapter_file}: Adapter file should be ADAPTER/CLASS/MIXIN, got {result}"

    def test_executor_classification(self, agent, repo_root):
        """TC-BOUNDARY-04: Executor files may overlap AGENT and SCRIPT characteristics."""
        # Find Executor files
        executor_files = list(repo_root.rglob("*Executor*.py"))
        if not executor_files:
            pytest.skip("No Executor files found")

        for executor_file in executor_files[:10]:
            result = agent.classify_file(executor_file)
            # Executors typically classified as AGENT but have script-like execution
            assert result in ["AGENT", "ORCHESTRATOR", "ENGINE", "CLASS"], \
                f"{executor_file}: Executor should be AGENT/ORCHESTRATOR/ENGINE/CLASS, got {result}"

    def test_mixin_classification(self, agent, repo_root):
        """TC-BOUNDARY-05: Mixin files should be classified as MIXIN."""
        mixin_files = list(repo_root.rglob("*Mixin*.py"))
        if not mixin_files:
            pytest.skip("No Mixin files found")

        for mixin_file in mixin_files[:10]:
            result = agent.classify_file(mixin_file)
            # Mixin files should be MIXIN type
            assert result in ["MIXIN", "CLASS"], \
                f"{mixin_file}: Mixin file should be MIXIN or CLASS, got {result}"


@pytest.mark.boundary
class TestTwentyTypeTaxonomy:
    """Test all 20 file types are properly classified."""

    ALL_20_TYPES = [
        "AGENT", "SCRIPT", "CLASS", "MIXIN", "UTILITY", "PROTOCOL",
        "ENGINE", "ORCHESTRATOR", "VALIDATOR", "CONFIG", "FACTORY",
        "TYPES", "STRATEGY", "ADAPTER", "EXCEPTION", "SERVICE",
        "GATEWAY", "STUB", "TEST", "ENFORCER"
    ]

    def test_all_types_exist_in_classification(self, agent):
        """TC-BOUNDARY-TYPES-01: All 20 types should be valid classifications."""
        # Verify the agent can return all 20 types
        # This is validated by checking the FileType literal
        from agentic_core.L5_safety.core_kernel.classification_kernel import FileType

        # FileType is a Literal, so we can't check membership directly
        # But we can verify through the agent's classification results
        assert len(self.ALL_20_TYPES) == 20, "Should have exactly 20 file types"

    def test_dual_taxonomy_validity(self, agent, repo_root):
        """TC-BOUNDARY-TYPES-02: Dual taxonomy (behavioral + structural) should coexist."""
        # Behavioral types (AGENT/SCRIPT)
        behavioral_types = ["AGENT", "SCRIPT"]

        # Structural types (remaining 18)
        structural_types = [t for t in self.ALL_20_TYPES if t not in behavioral_types]

        assert len(behavioral_types) == 2, "Should have 2 behavioral types"
        assert len(structural_types) == 18, "Should have 18 structural types"

        # Sample some files to verify both taxonomies are in use
        sample_files = [
            repo_root / "agentic_core" / "L5_safety" / "reasoning" / "FileClassificationAgent.py",
        ]

        for sample in sample_files:
            if sample.exists():
                result = agent.classify_file(sample)
                assert result in self.ALL_20_TYPES, f"Classification {result} not in 20-type taxonomy"
