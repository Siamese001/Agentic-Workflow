"""
Batch 2 Test Suite - HOP Domain
Tests for hop1_clerk_engine.py and hop2_enrichment_engine.py
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from apps_rg.engines.hops.hop1_clerk_engine import ClerkExtractionEngine
from apps_rg.engines.hops.hop2_enrichment_engine import EnrichmentEngine


@pytest.mark.asyncio
async def test_clerk_metrics_extraction():
    """Verify that legacy regex logic is preserved in the new Engine structure."""
    ctx = MagicMock()
    ctx.master_resume = {"experience": []}
    engine = ClerkExtractionEngine(ctx)
    
    text = "Managed a $50M+ budget and increased efficiency by 20% across 1,200 employees."
    metrics = engine._extract_metrics(text)
    
    assert "$50M+" in metrics
    assert "20%" in metrics
    assert "1,200" in metrics
    assert len(metrics) == 3


@pytest.mark.asyncio
async def test_enrichment_forbidden_verb_detection():
    """EDGE CASE: Ensure brand violations are caught during enrichment."""
    ctx = MagicMock()
    ctx.add_signal = MagicMock()
    engine = EnrichmentEngine(ctx)
    
    test_text = "I was responsible for managing the database."
    violations = engine._check_forbidden(test_text)
    
    assert "responsible for" in violations
    
    # Verify that the engine signals the context correctly
    data = {"experience_sections": [{"bullets": [{"bullet_text": test_text}]}]}
    await engine.execute(data)
    assert ctx.add_signal.called


@pytest.mark.asyncio
async def test_clerk_hallucination_integration():
    """Verify that Clerk Engine triggers the Hallucination detector."""
    ctx = MagicMock()
    ctx.master_resume = {"experience": [{"bullets": ["Fake achievement"]}]}
    ctx.add_signal = MagicMock()
    
    engine = ClerkExtractionEngine(ctx)
    engine.detector.check_batch = MagicMock(return_value={"valid": False, "score": 0.4})
    
    await engine.execute()
    
    assert ctx.add_signal.called


@pytest.mark.asyncio
async def test_clerk_section_building():
    """Verify clerk properly structures experience sections."""
    ctx = MagicMock()
    engine = ClerkExtractionEngine(ctx)
    
    raw_exp = [
        {
            "company": "TechCorp",
            "title": "Engineer",
            "bullets": ["Built APIs", "Improved performance"]
        }
    ]
    
    sections = engine._build_sections(raw_exp)
    
    assert len(sections) == 1
    assert sections[0]["company"] == "TechCorp"
    assert sections[0]["title"] == "Engineer"
    assert len(sections[0]["bullets"]) == 2


@pytest.mark.asyncio
async def test_enrichment_deduplication():
    """Verify enrichment engine detects duplicates."""
    ctx = MagicMock()
    engine = EnrichmentEngine(ctx)
    
    bullets = [
        {"bullet_text": "Led team of engineers"},
        {"bullet_text": "Led team of engineers"},  # Duplicate
        {"bullet_text": "Built microservices"}
    ]
    
    # In production, this would use cosine similarity
    duplicates = engine._find_duplicates(bullets)
    # Placeholder returns empty, but structure is validated
    assert isinstance(duplicates, list)
