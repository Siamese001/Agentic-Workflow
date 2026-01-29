"""
Phase 4 Domain Expansion Tests - 100% pass required.

Tests the Generation and Refinement engines:
- K9 Gap Closure reads from Buffer, writes to Buffer
- Weight Adjustment reads signals, writes to Buffer
- Content Optimizer reads weights from Buffer, writes optimized content
"""

import sys
from pathlib import Path

import pytest

# Add project root to path for imports BEFORE any app imports
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from apps_rg.engines.base.sovereign_context import SovereignContext
from apps_rg.engines.generation.k9_gap_closure_engine import GapClosureEngine
from apps_rg.engines.refinement.content_optimizer_engine import ContentOptimizerEngine
from apps_rg.engines.refinement.weight_adjustment_engine import WeightAdjustmentEngine


@pytest.mark.asyncio
async def test_k9_requires_upstream_data():
    """Verify K9 fails if HOP2 data is missing."""
    ctx = SovereignContext()
    # Write only mission, missing enrichment
    ctx.buffer.write("mission_input", {"job_description_keywords": ["python"]}, "SETUP")

    engine = GapClosureEngine(ctx)
    with pytest.raises(ValueError, match="Buffer missing hop2_enrichment"):
        await engine.execute()


@pytest.mark.asyncio
async def test_k9_writes_to_buffer():
    """Verify K9 output is committed to ledger."""
    ctx = SovereignContext()
    ctx.buffer.write("mission_input", {"job_description_keywords": ["python"]}, "SETUP")
    ctx.buffer.write("hop2_enrichment", {"skills": []}, "SETUP")

    engine = GapClosureEngine(ctx)
    await engine.execute()

    saved = ctx.buffer.read("k9_competencies")
    assert len(saved) == 6


@pytest.mark.asyncio
async def test_weight_adjustment_reads_signals():
    """Verify signal propagation alters weights."""
    ctx = SovereignContext()
    ctx.add_signal("ATS_FAILURE")

    engine = WeightAdjustmentEngine(ctx)
    result = await engine.execute()

    assert result["skills"] == 1.25
    assert ctx.buffer.read("adjusted_weights") == result


@pytest.mark.asyncio
async def test_optimizer_uses_weights():
    """Verify optimizer reads weights from buffer."""
    ctx = SovereignContext()
    # Mock data
    ctx.buffer.write(
        "hop2_enrichment",
        {"experience_sections": [{"bullets": [{"quantified_metrics": True}]}]},
        "SETUP",
    )
    # Mock Weights
    ctx.buffer.write("adjusted_weights", {"experience": 2.0}, "SETUP")

    engine = ContentOptimizerEngine(ctx)
    await engine.execute()

    # Check if logic ran without error (deep logic verification in unit tests)
    assert ctx.buffer.read("optimized_content") is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
