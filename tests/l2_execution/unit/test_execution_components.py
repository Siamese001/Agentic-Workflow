"""
L2 Execution Unit Tests
Tests for individual execution components
"""

import pytest
from agentic_core.l2_execution import (
    BrowserTool, FileOpsTool, APITool,
    ToolInvocation, Validation, ErrorHandling
)


class TestExecutionTools:
    """Test execution tool functionality"""
    
    def test_browser_tool_init(self):
        """Test BrowserTool initialization"""
        tool = BrowserTool()
        assert tool is not None
    
    def test_file_ops_tool_init(self):
        """Test FileOpsTool initialization"""
        tool = FileOpsTool()
        assert tool is not None
    
    def test_api_tool_init(self):
        """Test APITool initialization"""
        tool = APITool()
        assert tool is not None


class TestExecutionEngine:
    """Test execution engine functionality"""
    
    def test_tool_invocation_init(self):
        """Test ToolInvocation initialization"""
        engine = ToolInvocation()
        assert engine is not None
    
    def test_validation_init(self):
        """Test Validation initialization"""
        validator = Validation()
        assert validator is not None
    
    def test_error_handling_init(self):
        """Test ErrorHandling initialization"""
        handler = ErrorHandling()
        assert handler is not None
