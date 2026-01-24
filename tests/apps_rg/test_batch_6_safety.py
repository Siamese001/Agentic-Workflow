"""
Batch 6 Test Suite - Safety Domain
Tests for void_compliance_engine.py and ats_compatibility_engine.py
"""

import pytest
from unittest.mock import MagicMock, patch, mock_open
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from apps_rg.engines.safety.void_compliance_engine import VoidComplianceEngine
from apps_rg.engines.safety.ats_compatibility_engine import ATSCompatibilityEngine


@pytest.mark.asyncio
async def test_void_compliance_detects_legacy():
    """CRITICAL: Ensure the engine halts on legacy imports."""
    ctx = MagicMock()
    engine = VoidComplianceEngine(ctx)
    
    # Create a dummy file with a forbidden import
    with patch("pathlib.Path.rglob") as mock_glob:
        mock_file = MagicMock()
        mock_file.name = "dirty_file.py"
        mock_file.read_text = MagicMock(return_value="import archives.legacy_code")
        mock_glob.return_value = [mock_file]
        
        # We expect a RuntimeError (or SystemExit in production)
        with pytest.raises(RuntimeError) as exc:
            await engine.execute("test_path")
        
        assert "VOID COMPLIANCE FAILURE" in str(exc.value)


@pytest.mark.asyncio
async def test_ats_detects_tables():
    """EDGE CASE: Detect HTML table artifacts in resume data."""
    ctx = MagicMock()
    ctx.add_signal = MagicMock()
    engine = ATSCompatibilityEngine(ctx)
    
    dirty_resume = {
        "summary": "Professional <table><tr><td>Bad content</td></tr></table>"
    }
    
    result = await engine.execute(dirty_resume)
    
    assert result["compatible"] is False
    assert "HTML Table Detected" in result["issues"]
    # Ensure signal was sent to context
    assert ctx.add_signal.called


@pytest.mark.asyncio
async def test_ats_clean_pass():
    """Verify a clean resume passes with no signals."""
    ctx = MagicMock()
    ctx.add_signal = MagicMock()
    engine = ATSCompatibilityEngine(ctx)
    
    clean_resume = {
        "experience": [{"company": "A", "title": "B"}],
        "education": "University"
    }
    
    result = await engine.execute(clean_resume)
    
    assert result["compatible"] is True
    assert not ctx.add_signal.called


@pytest.mark.asyncio
async def test_void_compliance_ast_parsing():
    """Verify AST parsing correctly identifies forbidden imports."""
    ctx = MagicMock()
    engine = VoidComplianceEngine(ctx)
    
    # Test with actual Python code
    test_code = """
import os
from archives.legacy import OldEngine
import sys
"""
    
    with patch("pathlib.Path.read_text", return_value=test_code):
        violations = engine._audit_file(Path("test.py"))
    
    assert len(violations) > 0
    assert any("archives" in v for v in violations)


@pytest.mark.asyncio
async def test_ats_missing_sections():
    """Verify ATS engine detects missing required sections."""
    ctx = MagicMock()
    engine = ATSCompatibilityEngine(ctx)
    
    incomplete_resume = {
        "summary": "Professional summary"
        # Missing experience and education
    }
    
    result = await engine.execute(incomplete_resume)
    
    assert result["compatible"] is False
    assert any("Missing Standard Sections" in issue for issue in result["issues"])


@pytest.mark.asyncio
async def test_void_compliance_clean_architecture():
    """Verify clean architecture passes void compliance."""
    ctx = MagicMock()
    engine = VoidComplianceEngine(ctx)
    
    clean_code = """
import os
from apps_rg.engines.base import BaseRGEngine
"""
    
    with patch("pathlib.Path.read_text", return_value=clean_code):
        violations = engine._audit_file(Path("test.py"))
    
    assert len(violations) == 0
