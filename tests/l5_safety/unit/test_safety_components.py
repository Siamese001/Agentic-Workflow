"""
L5 Safety Unit Tests
Tests for individual safety components
"""

import pytest
from agentic_core.l5_safety import (
    ContentFilter, SafetyValidator, SafetyMonitor
)


class TestSafetyComponents:
    """Test safety functionality"""
    
    def test_content_filter_init(self):
        """Test ContentFilter initialization"""
        filter = ContentFilter()
        assert filter is not None
    
    def test_safety_validator_init(self):
        """Test SafetyValidator initialization"""
        validator = SafetyValidator()
        assert validator is not None
    
    def test_safety_monitor_init(self):
        """Test SafetyMonitor initialization"""
        monitor = SafetyMonitor()
        assert monitor is not None
