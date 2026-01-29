"""
Batch 4 Test Suite - Refinement Domain Part 1
Tests for weight_adjustment_engine.py and content_optimizer_engine.py
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from apps_rg.engines.refinement.content_optimizer_engine import ContentOptimizerEngine
from apps_rg.engines.refinement.weight_adjustment_engine import WeightAdjustmentEngine


@pytest.mark.asyncio
async def test_weight_adjustment_ats_signal():
    """SKEPTICAL TEST: Does the engine correctly respond to an ATS_FAILURE signal?"""
    ctx = MagicMock()
    ctx.signals = {"ATS_FAILURE"}
    engine = WeightAdjustmentEngine(ctx)

    data = {"skills": "Python, Java", "education": "BS CS"}
    result = await engine.execute(data)

    assert result["skills"]["applied_weight"] == 1.25
    assert result["education"]["applied_weight"] == 1.0


@pytest.mark.asyncio
async def test_content_optimizer_impact_sorting():
    """EDGE CASE: Ensure quantified bullets are ranked higher than generic ones."""
    ctx = MagicMock()
    engine = ContentOptimizerEngine(ctx)

    bullets = [
        {"bullet_text": "Managed a team.", "quantified_metrics": []},
        {"bullet_text": "Increased sales by 50%.", "quantified_metrics": ["50%"]},
        {"bullet_text": "Led a project.", "quantified_metrics": []},
    ]

    section = {"bullets": bullets}
    optimized = await engine.execute([section])

    # "Increased sales" should be at index 0
    assert "50%" in optimized[0]["bullets"][0]["bullet_text"]
    # "Led" (power verb) should be at index 1
    assert "Led" in optimized[0]["bullets"][1]["bullet_text"]


@pytest.mark.asyncio
async def test_weight_engine_no_signal_neutrality():
    """Ensure weights remain 1.0 if no corrective signals are present."""
    ctx = MagicMock()
    ctx.signals = set()
    engine = WeightAdjustmentEngine(ctx)

    data = {"experience": "..."}
    result = await engine.execute(data)
    assert result["experience"]["applied_weight"] == 1.0


@pytest.mark.asyncio
async def test_weight_adjustment_quality_signal():
    """Verify QUALITY_FAILURE signal increases experience weight."""
    ctx = MagicMock()
    ctx.signals = {"QUALITY_FAILURE"}
    engine = WeightAdjustmentEngine(ctx)

    data = {"experience": "Work history", "skills": "Tech skills"}
    result = await engine.execute(data)

    assert result["experience"]["applied_weight"] == 1.30


@pytest.mark.asyncio
async def test_content_optimizer_power_verb_scoring():
    """Verify power verbs increase impact score."""
    ctx = MagicMock()
    engine = ContentOptimizerEngine(ctx)

    bullet_with_power = {"bullet_text": "Led strategic initiatives", "quantified_metrics": []}
    bullet_generic = {"bullet_text": "Worked on projects", "quantified_metrics": []}

    score_power = engine._calculate_impact_score(bullet_with_power)
    score_generic = engine._calculate_impact_score(bullet_generic)

    assert score_power > score_generic
