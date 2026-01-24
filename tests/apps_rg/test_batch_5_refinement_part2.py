"""
Batch 5 Test Suite - Refinement Domain Part 2
Tests for section_ranker_engine.py and template_optimizer_engine.py
"""

import pytest
from unittest.mock import MagicMock
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from apps_rg.engines.refinement.section_ranker_engine import SectionRankerEngine
from apps_rg.engines.refinement.template_optimizer_engine import TemplateOptimizerEngine


@pytest.mark.asyncio
async def test_section_ranker_technical_order():
    """VERIFICATION: Ensure Technical roles prioritize Skills."""
    ctx = MagicMock()
    engine = SectionRankerEngine(ctx)
    
    # Mock config strategy injection
    engine.strategies = {
        "technical": ["skills", "experience", "education"]
    }
    
    raw_resume = {
        "education": "BS CS",
        "experience": "Dev",
        "skills": "Python"
    }
    
    ordered = await engine.execute(raw_resume, role_type="technical")
    keys = list(ordered.keys())
    
    # "skills" should be index 0
    assert keys[0] == "skills"
    # "education" should be index 2
    assert keys[2] == "education"


@pytest.mark.asyncio
async def test_section_ranker_orphan_preservation():
    """EDGE CASE: Ensure non-standard sections (e.g., 'Hobbies') are not deleted."""
    ctx = MagicMock()
    engine = SectionRankerEngine(ctx)
    engine.strategies = {"default": ["experience"]}
    
    raw_resume = {
        "experience": "Work",
        "hobbies": "Fishing"  # Orphan
    }
    
    ordered = await engine.execute(raw_resume, role_type="default")
    
    assert "hobbies" in ordered
    # Orphan should be at the end
    assert list(ordered.keys())[-1] == "hobbies"


@pytest.mark.asyncio
async def test_template_optimizer_detection_logic():
    """VERIFICATION: Verify keyword detection maps correctly."""
    ctx = MagicMock()
    engine = TemplateOptimizerEngine(ctx)
    
    jd_executive = "Looking for a Vice President to lead the division."
    jd_entry = "Seeking a junior associate for an internship."
    
    assert engine._detect_job_type(jd_executive) == "executive"
    assert engine._detect_job_type(jd_entry) == "entry_level"


@pytest.mark.asyncio
async def test_template_optimizer_fallback():
    """Verify fallback recommendations work when config is unavailable."""
    ctx = MagicMock()
    engine = TemplateOptimizerEngine(ctx)
    engine.config = None  # Simulate missing config
    
    result = await engine.execute("Software engineer position")
    
    assert result["job_type"] == "technical"
    assert "recommended_templates" in result


@pytest.mark.asyncio
async def test_section_ranker_executive_order():
    """Verify executive roles prioritize summary."""
    ctx = MagicMock()
    engine = SectionRankerEngine(ctx)
    
    raw_resume = {
        "skills": "Leadership",
        "summary": "Executive summary",
        "experience": "Work history"
    }
    
    ordered = await engine.execute(raw_resume, role_type="executive")
    keys = list(ordered.keys())
    
    # Summary should come before skills for executive
    assert keys.index("summary") < keys.index("skills")
