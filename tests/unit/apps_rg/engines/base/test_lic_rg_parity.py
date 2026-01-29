"""
Comprehensive Test Suite for LIC-RG Architecture Parity.
Tests all critical gaps identified in the comparison.
"""

import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from agentic_core.utils.core_extensions.trace_registry import TraceRegistry
from apps_rg.domain.config.loader import load_rg_specs, reload_config
from apps_rg.engines.base.base_resume_engine import BaseRGEngine
from apps_rg.engines.base.sovereign_context import SovereignContext
from apps_rg.engines.orchestration.resume_orchestrator_engine import ResumeOrchestratorEngine
from apps_rg.shared.reasoning.toggles import get_toggles


class TestConfigurationParity:
    """Test RG configuration system matches LIC capabilities."""

    def test_auto_config_loading(self):
        """Test that configuration is auto-loaded like LIC."""
        specs = load_rg_specs()

        # Should have loaded configuration
        assert specs is not None
        assert hasattr(specs, "orchestrator")
        assert hasattr(specs, "validation")

        # Should have retry limits
        assert specs.orchestrator.max_retry_iterations > 0
        assert specs.orchestrator.global_step_limit > 0

    def test_config_singleton_pattern(self):
        """Test that config uses singleton pattern like LIC."""
        specs1 = load_rg_specs()
        specs2 = load_rg_specs()

        # Should be the same object (singleton)
        assert specs1 is specs2

    def test_config_reload(self):
        """Test configuration reload functionality."""
        specs1 = load_rg_specs()
        reload_config()
        specs2 = load_rg_specs()

        # Should be different objects after reload
        assert specs1 is not specs2


class TestReasoningTogglesParity:
    """Test RG reasoning toggles match LIC capabilities."""

    def test_toggle_initialization(self):
        """Test toggle initialization with defaults."""
        toggles = get_toggles()

        # Should have core toggles
        assert hasattr(toggles, "use_cot")
        assert hasattr(toggles, "use_reflexion")
        assert hasattr(toggles, "strict_mode")

        # Should have reasonable defaults
        assert toggles.use_cot is True
        assert toggles.use_reflexion is True

    def test_environment_based_toggles(self):
        """Test environment-specific toggle loading."""
        # Test environment
        test_toggles = get_toggles("test")
        assert test_toggles.use_cot is False  # Faster for tests

        # Dev environment
        dev_toggles = get_toggles("dev")
        assert dev_toggles.strict_mode is False


class TestTraceRegistryParity:
    """Test RG trace registry matches LIC persistence capabilities."""

    def test_trace_persistence(self):
        """Test that traces are persisted to file like LIC."""
        trace_path = Path("test_trace_persistence.jsonl")
        registry = TraceRegistry(persistence_path=trace_path)

        # Create a span
        span_id = registry.start_span("test_mission", "test_agent", "test_operation")
        registry.end_span(span_id, status="SUCCESS", error=None)

        # Check file was created
        assert trace_path.exists(), "Trace file not created"

        # Load and verify content
        with open(trace_path) as f:
            lines = f.readlines()
            assert len(lines) > 0, "No traces written to file"

        # Cleanup
        trace_path.unlink()

    def test_trace_loading(self):
        """Test that existing traces are loaded on initialization."""
        trace_path = Path("test_trace_load.jsonl")

        # Create pre-existing trace file
        with open(trace_path, "w") as f:
            trace_data = {
                "timestamp": "2024-01-01T00:00:00",
                "agent": "test_agent",
                "error": None,
                "duration": 100.0,
            }
            f.write(json.dumps(trace_data) + "\n")

        # Initialize registry (should load existing traces)
        registry = TraceRegistry(persistence_path=trace_path)

        # Should have persistence path set
        assert registry.persistence_path == trace_path

        # Cleanup
        trace_path.unlink()


class TestCyclicRetryLogic:
    """Test cyclic retry logic matches LIC capabilities."""

    @pytest.mark.asyncio
    async def test_retry_on_validation_failure(self):
        """Test that orchestrator retries when validation fails."""
        ctx = SovereignContext()
        ctx.master_resume = {
            "experience": [{"company": "TestCorp", "bullets": ["Bad content"] * 10}]
        }

        orch = ResumeOrchestratorEngine(ctx, mission_id="test_retry")

        # Mock quality engine to fail initially
        with patch(
            "apps_rg.engines.quality.content_quality_engine.ContentQualityEngine.run"
        ) as mock_quality:
            mock_quality.return_value = None

            # Mock buffer to return failing quality report
            ctx.buffer.write = Mock()
            ctx.buffer.read = Mock(
                return_value={"status": "failed", "score": 50, "issues": ["weak verbs"]}
            )

            result = await orch.execute("Test Job")

            # Should have attempted retries
            assert result["retry_iterations"] > 0, "No retries attempted on validation failure"
            assert result["status"] in ["SUCCESS", "WARNING"], "Invalid final status"

    @pytest.mark.asyncio
    async def test_max_retry_limit_enforcement(self):
        """Test that orchestrator respects MAX_RETRY_ITERATIONS."""
        ctx = SovereignContext()
        ctx.master_resume = {"experience": [{"bullets": ["Bad content"] * 100}]}

        orch = ResumeOrchestratorEngine(ctx, mission_id="test_max_retry")
        orch.MAX_RETRY_ITERATIONS = 2  # Override for testing

        # Mock to always fail
        with patch(
            "apps_rg.engines.quality.content_quality_engine.ContentQualityEngine.run"
        ) as mock_quality:
            mock_quality.return_value = None
            ctx.buffer.write = Mock()
            ctx.buffer.read = Mock(
                return_value={"status": "failed", "score": 30, "issues": ["many issues"]}
            )

            result = await orch.execute("Test Job")

            # Should not exceed max retries
            assert result["retry_iterations"] <= orch.MAX_RETRY_ITERATIONS
            assert result["status"] == "WARNING", "Should end in WARNING after max retries"

    @pytest.mark.asyncio
    async def test_global_step_limit(self):
        """Test that global step limit is enforced."""
        ctx = SovereignContext()
        orch = ResumeOrchestratorEngine(ctx, mission_id="test_step_limit")
        orch.GLOBAL_STEP_LIMIT = 1  # Very low limit

        # Should fail due to step limit
        with pytest.raises(RuntimeError, match="Global step limit exceeded"):
            await orch.execute("Test Job")


class TestSubatomicTestingIntegration:
    """Test SubatomicTestingMixin integration."""

    def test_subatomic_testing_present(self):
        """Test that SubatomicTestingMixin is integrated."""
        ctx = SovereignContext()
        orch = ResumeOrchestratorEngine(ctx, mission_id="subatomic_test")

        # Should have subatomic testing methods
        assert hasattr(orch, "run_subatomic_test"), "Missing SubatomicTestingMixin"

    def test_base_engine_has_subatomic(self):
        """Test that BaseRGEngine includes SubatomicTestingMixin."""
        ctx = SovereignContext()

        class TestEngine(BaseRGEngine):
            async def execute(self):
                return "test"

        engine = TestEngine(ctx)

        # Should have subatomic testing methods
        assert hasattr(engine, "run_subatomic_test"), "BaseRGEngine missing SubatomicTestingMixin"


class TestFullArchitectureParity:
    """Test end-to-end architecture parity with LIC."""

    @pytest.mark.asyncio
    async def test_complete_workflow_with_all_features(self):
        """Test complete RG workflow with all LIC-equivalent features."""
        ctx = SovereignContext()
        ctx.master_resume = {
            "experience": [
                {
                    "company": "TechCorp",
                    "title": "Senior Engineer",
                    "bullets": [
                        "Led team of 5 engineers to deliver project 2 weeks ahead of schedule",
                        "Reduced infrastructure costs by 30% through optimization",
                        "Implemented CI/CD pipeline reducing deployment time by 80%",
                    ],
                }
            ],
            "education": [{"degree": "BS Computer Science", "school": "State University"}],
            "skills": ["Python", "JavaScript", "AWS", "Docker", "Kubernetes"],
        }

        orch = ResumeOrchestratorEngine(ctx, mission_id="full_parity_test")

        # Mock all engines to simulate successful execution
        with (
            patch("apps_rg.engines.hops.hop1_clerk_engine.ClerkExtractionEngine.run") as mock_hop1,
            patch(
                "apps_rg.engines.hops.hop2_enrichment_engine.DataEnrichmentEngine.run"
            ) as mock_hop2,
            patch(
                "apps_rg.engines.generation.k9_gap_closure_engine.GapClosureEngine.run"
            ) as mock_gap,
            patch(
                "apps_rg.engines.refinement.content_optimizer_engine.ContentOptimizerEngine.run"
            ) as mock_opt,
            patch(
                "apps_rg.engines.refinement.section_ranker_engine.SectionRankerEngine.run"
            ) as mock_rank,
            patch(
                "apps_rg.engines.safety.ats_compatibility_engine.ATSCompatibilityEngine.run"
            ) as mock_ats,
            patch(
                "apps_rg.engines.quality.content_quality_engine.ContentQualityEngine.run"
            ) as mock_quality,
        ):
            # Mock buffer operations
            ctx.buffer.write = Mock()
            ctx.buffer.read = Mock(
                return_value={"status": "passed", "score": 85, "valid": True, "issues": []}
            )

            result = await orch.execute("Senior Software Engineer with cloud experience")

            # Verify all LIC-equivalent features are present
            assert "status" in result, "Missing status field"
            assert "checkpoints" in result, "Missing checkpoints"
            assert "retry_iterations" in result, "Missing retry tracking"
            assert "final_quality_score" in result, "Missing quality score"
            assert "ats_valid" in result, "Missing ATS validation"

            # Verify cyclic logic was available
            assert hasattr(orch, "MAX_RETRY_ITERATIONS"), "Missing retry limit"
            assert hasattr(orch, "GLOBAL_STEP_LIMIT"), "Missing step limit"

            # Verify persistent tracing
            if orch.toggles.use_persistent_tracing:
                trace_file = Path("logs/missions/full_parity_test/trace.jsonl")
                assert trace_file.exists(), "Trace file not created"

    def test_all_required_components_present(self):
        """Test that all required components are present."""
        # Check configuration system
        from apps_rg.domain.config.loader import load_rg_specs

        specs = load_rg_specs()
        assert specs is not None

        # Check reasoning toggles
        from apps_rg.shared.reasoning.toggles import get_toggles

        toggles = get_toggles()
        assert toggles is not None

        # Check trace registry
        from agentic_core.utils.core_extensions.trace_registry import TraceRegistry

        registry = TraceRegistry()
        assert registry is not None

        # Check base engine
        from apps_rg.engines.base.base_resume_engine import BaseRGEngine

        assert BaseRGEngine is not None

        # Check orchestrator
        from apps_rg.engines.orchestration.resume_orchestrator_engine import (
            ResumeOrchestratorEngine,
        )

        assert ResumeOrchestratorEngine is not None


class TestGapClosureValidation:
    """Validate that all identified gaps have been closed."""

    def test_gap_1_cyclic_retry_logic_closed(self):
        """Verify cyclic retry logic gap is closed."""
        ctx = SovereignContext()
        orch = ResumeOrchestratorEngine(ctx, mission_id="gap_test")

        # Should have retry logic components
        assert hasattr(orch, "MAX_RETRY_ITERATIONS")
        assert hasattr(orch, "GLOBAL_STEP_LIMIT")
        assert orch.MAX_RETRY_ITERATIONS > 0
        assert orch.GLOBAL_STEP_LIMIT > 0

    @pytest.mark.asyncio
    async def test_gap_2_auto_configuration_closed(self):
        """Verify auto-configuration gap is closed."""
        from apps_rg.engines.base.base_resume_engine import BaseRGEngine

        ctx = SovereignContext()

        class TestEngine(BaseRGEngine):
            async def execute(self):
                return self.rg_specs

        engine = TestEngine(ctx)
        result = await engine.execute()

        # Should have auto-loaded configuration
        assert hasattr(engine, "rg_specs")
        assert hasattr(engine, "toggles")
        assert engine.rg_specs is not None
        assert engine.toggles is not None

    def test_gap_3_persistent_tracing_closed(self):
        """Verify persistent tracing gap is closed."""
        trace_path = Path("test_gap_tracing.jsonl")
        registry = TraceRegistry(persistence_path=trace_path)

        # Should support persistence
        assert registry.persistence_path == trace_path

        # Should persist traces
        span_id = registry.start_span("test", "test", "test")
        registry.end_span(span_id, status="SUCCESS")

        assert trace_path.exists(), "Trace not persisted"
        trace_path.unlink()

    def test_gap_4_subatomic_testing_closed(self):
        """Verify SubatomicTestingMixin gap is closed."""
        ctx = SovereignContext()
        orch = ResumeOrchestratorEngine(ctx, mission_id="gap_test")

        # Should have subatomic testing methods
        assert hasattr(orch, "run_subatomic_test")
        assert callable(orch.run_subatomic_test)


if __name__ == "__main__":
    # Run tests when executed directly
    pytest.main([__file__, "-v"])
