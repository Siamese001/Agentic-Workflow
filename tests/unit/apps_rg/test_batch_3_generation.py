"""
Batch 3 Test Suite - Generation Domain
Tests for k9_gap_closure_engine.py and service_invoker_engine.py
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from apps_rg.engines.generation.k9_gap_closure_engine import GapClosureEngine, CompetencyItem
from apps_rg.engines.generation.service_invoker_engine import ServiceInvokerEngine


@pytest.mark.asyncio
async def test_k9_zero_tolerance_on_count():
    """SKEPTICAL TEST: Does the engine block a response that isn't exactly 6 items?"""
    ctx = MagicMock()
    ctx.target_industry = "Technology"
    ctx.add_signal = MagicMock()

    engine = GapClosureEngine(ctx)

    # Mock LLM returning only 5 items
    engine.call_llm = AsyncMock(return_value="Item 1, Item 2, Item 3, Item 4, Item 5")
    # Mock parser to return 5 objects
    engine._parse_output = MagicMock(return_value=[CompetencyItem("T", "D", 25)] * 5)

    # This should trigger record_fail and signal
    await engine.execute(["gap1"], ["skill1"])

    assert ctx.add_signal.called or engine.ctx.add_signal.called


@pytest.mark.asyncio
async def test_k9_word_count_balance():
    """EDGE CASE: Validate the VG_COMPETENCY_BALANCE global rule."""
    ctx = MagicMock()
    engine = GapClosureEngine(ctx)

    items = [
        CompetencyItem("Good", "This is a perfectly balanced description.", 25),
        CompetencyItem("Too Short", "Brief.", 2),  # Violation
        CompetencyItem("Too Long", " ".join(["word"] * 50), 50),  # Violation
    ]

    issues = engine._validate_word_counts(items)
    assert len(issues) == 2
    assert "2 words" in issues[0]
    assert "50 words" in issues[1]


@pytest.mark.asyncio
async def test_service_invoker_telemetry():
    """Verify that the invoker records duration_ms correctly."""
    ctx = MagicMock()
    engine = ServiceInvokerEngine(ctx)
    engine.call_llm = AsyncMock(return_value="Success")

    result = await engine.execute("test_action", {"prompt": "test"})

    assert result["success"] is True
    assert "duration_ms" in result
    assert result["duration_ms"] >= 0


@pytest.mark.asyncio
async def test_service_invoker_error_handling():
    """Verify service invoker handles errors gracefully."""
    ctx = MagicMock()
    engine = ServiceInvokerEngine(ctx)

    # Missing prompt should raise error
    result = await engine.execute("test_action", {})

    assert result["success"] is False
    assert "error" in result


@pytest.mark.asyncio
async def test_k9_gap_identification():
    """Verify gap closure identifies missing keywords."""
    ctx = MagicMock()
    ctx.target_industry = "Technology"
    engine = GapClosureEngine(ctx)

    jd_keywords = ["Python", "AWS", "Docker", "Kubernetes"]
    candidate_skills = ["Python", "AWS"]

    # Mock LLM call
    engine.call_llm = AsyncMock(return_value="Generated competencies")

    await engine.execute(jd_keywords, candidate_skills)

    # Verify LLM was called with gap keywords
    call_args = engine.call_llm.call_args[0][0]
    assert "Docker" in call_args or "Kubernetes" in call_args
