"""
Phase 6 Full Cycle Tests - 100% pass required.

Tests the complete 5-HOP Sovereign Pipeline:
- Orchestrator drives all engines sequentially
- Service Invoker with trace integration
- Content Quality engine feedback loop
"""

import pytest
import sys
from pathlib import Path

# Add project root to path for imports BEFORE any app imports
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from apps_rg.engines.base.sovereign_context import SovereignContext
from apps_rg.engines.orchestration.resume_orchestrator_engine import ResumeOrchestratorEngine
from apps_rg.engines.quality.content_quality_engine import ContentQualityEngine


@pytest.mark.asyncio
async def test_orchestrator_full_chain():
    """
    CRITICAL: Verify the Orchestrator drives HOP 1 -> 5 without crashing.
    """
    ctx = SovereignContext()
    # Setup Mock Data
    ctx.master_resume = {
        "experience": [{"company": "A", "bullets": ["Managed $1M budget"]}],
        "education": [],
        "skills": []
    }

    orch = ResumeOrchestratorEngine(ctx)
    result = await orch.execute("Senior Python Engineer with leadership experience")

    # Check Checkpoints
    checkpoints = result["checkpoints"]
    assert "HOP-1" in checkpoints
    assert "HOP-2" in checkpoints
    assert "HOP-3-K9" in checkpoints
    assert "HOP-4-RANK" in checkpoints
    assert "HOP-5-ATS" in checkpoints

    # Check Final Output
    assert result["status"] in ["SUCCESS", "WARNING"]

    # Verify Data Flow
    assert ctx.buffer.read("k9_competencies") is not None
    assert ctx.buffer.read("ranked_content") is not None


@pytest.mark.asyncio
async def test_quality_feedback_loop():
    """Verify Quality engine writes report."""
    ctx = SovereignContext()
    ctx.buffer.write("hop2_enrichment", {
        "experience_sections": [{"bullets": [{"bullet_text": "Responsible for nothing"}]}]
    }, "SETUP")

    engine = ContentQualityEngine(ctx)
    await engine.execute()

    report = ctx.buffer.read("quality_report")
    assert report["score"] < 100
    assert len(report["issues"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
