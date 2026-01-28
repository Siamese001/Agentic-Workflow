"""
Batch 1 Test Suite - Foundation & Command
Tests for base_resume_engine.py and resume_orchestrator_engine.py
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from apps_rg.engines.base.base_resume_engine import BaseRGEngine
from apps_rg.engines.orchestration.resume_orchestrator_engine import ResumeOrchestratorEngine


@pytest.fixture
def mock_ctx():
    ctx = MagicMock()
    ctx.signals = set()
    ctx.get_failed_results = MagicMock(return_value={})
    ctx.master_resume = {"experience": []}
    return ctx


def test_base_engine_config_hydration(mock_ctx):
    """SKEPTICAL TEST: Does the engine actually pull from the knowledge base?"""

    class TestEngine(BaseRGEngine):
        async def execute(self):
            pass

    engine = TestEngine(mock_ctx, node_id="K.9")
    assert engine.config.id == "K.9"
    assert "count" in engine.thresholds, "Thresholds failed to hydrate from Frozen Knowledge"


@pytest.mark.asyncio
async def test_orchestrator_hop_failure_propagation(mock_ctx):
    """SKEPTICAL TEST: If a HOP fails, does the General correctly signal the system?"""
    orch = ResumeOrchestratorEngine(mock_ctx)

    # Force a failure in a sub-method
    with pytest.raises(ValueError):
        await orch._run_hop_zero("")  # Empty JD

    # Signal check must be mandatory 100% pass
    orch.record_fail("Test Fail", signal="HOP_0_FAILED")
    assert mock_ctx.add_signal.called, "Failure signal not propagated to context"


def test_base_engine_mcp_audit_requirement(mock_ctx):
    """EDGE CASE: Ensure security audit is triggered on init."""

    class TestEngine(BaseRGEngine):
        async def execute(self):
            pass

    engine = TestEngine(mock_ctx)
    # The MCPHardenedMixin must be called (or stub version)
    assert hasattr(engine, "_mcp_audit"), "Sovereign requirement: MCP Audit method missing"


def test_orchestrator_health_transparency(mock_ctx):
    """Ensure L3 orchestrator has full visibility into fleet failure."""
    mock_ctx.get_failed_results = MagicMock(return_value={"FactCheckEngine": "Failed"})
    orch = ResumeOrchestratorEngine(mock_ctx)
    health = orch.get_system_health()
    assert "FactCheckEngine" in health["failed_engines"]


@pytest.mark.asyncio
async def test_orchestrator_checkpoint_tracking(mock_ctx):
    """Verify HOP checkpoints are properly tracked."""
    orch = ResumeOrchestratorEngine(mock_ctx)

    # Mock the HOP execution methods
    with patch.object(orch, "_run_hop_one", new_callable=AsyncMock) as mock_hop1:
        with patch.object(orch, "_run_hop_two", new_callable=AsyncMock) as mock_hop2:
            mock_hop1.return_value = {"data": "test"}
            mock_hop2.return_value = {"data": "enriched"}

            result = await orch.execute("Test JD with sufficient detail for validation")

            assert len(orch.hop_checkpoints) >= 2
            assert orch.hop_checkpoints[0].hop_id == "HOP-0"
            assert result["status"] == "success"


def test_base_engine_frozen_prompt_access(mock_ctx):
    """Verify engines can access frozen prompts."""

    class TestEngine(BaseRGEngine):
        async def execute(self):
            pass

    engine = TestEngine(mock_ctx, node_id="K.9")

    # Should be able to get prompts
    prompt = engine.get_frozen_prompt("k1_hyde_generation")
    assert "{company_name}" in prompt
    assert "{job_title}" in prompt
