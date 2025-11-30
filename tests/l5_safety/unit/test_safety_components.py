"""
L5 Safety Unit Tests
Tests for individual safety components
"""

import pytest
from agentic_core.l5_safety import (
    ContentFilter, Guardrail, Auditor
)


class TestSafetyComponents:
    """Test safety functionality"""
    
    def test_content_filter_init(self):
        """Test ContentFilter initialization"""
        filter = ContentFilter()
        assert filter is not None
    
    def test_guardrail_init(self):
        """Test Guardrail initialization"""
        guardrail = Guardrail()
        assert guardrail is not None
    
    def test_auditor_init(self):
        """Test Auditor initialization"""
        auditor = Auditor()
        assert auditor is not None
