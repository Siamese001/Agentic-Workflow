#!/usr/bin/env python3
"""
Basic test for Phase 2.1 implementation.
"""

import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch

# Import the module we're testing
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools"))

try:
    from fix_high_severity_silent_swallowers import HighSeveritySilentSwallowerFixer
    CAN_IMPORT = True
except ImportError as e:
    print(f"Cannot import fix_high_severity_silent_swallowers: {e}")
    CAN_IMPORT = False


class TestPhase21Basic:
    """Basic tests for Phase 2.1 implementation."""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            yield workspace
    
    def test_can_import_fixer(self):
        """Test that we can import the fixer class."""
        if not CAN_IMPORT:
            pytest.skip("Cannot import fix_high_severity_silent_swallowers")
        
        # Test instantiation
        assert HighSeveritySilentSwallowerFixer is not None
    
    @pytest.mark.skipif(not CAN_IMPORT, reason="Cannot import fixer")
    def test_fixer_with_empty_violations(self, temp_workspace):
        """Test fixer with empty violations."""
        # Create tools directory and empty violations file
        tools_dir = temp_workspace / "tools"
        tools_dir.mkdir()
        violations_file = tools_dir / "silent_swallower_report.json"
        with open(violations_file, 'w') as f:
            json.dump({'violations': []}, f)
        
        with patch('fix_high_severity_silent_swallowers.PROJECT_ROOT', temp_workspace):
            fixer = HighSeveritySilentSwallowerFixer()
            
            # Should handle empty list gracefully
            assert len(fixer.violations) == 0
            assert fixer.fixes_applied == 0
    
    @pytest.mark.skipif(not CAN_IMPORT, reason="Cannot import fixer")
    def test_fixer_with_sample_violations(self, temp_workspace):
        """Test fixer with sample violations."""
        sample_violations = {
            'scan_timestamp': '2026-03-24T19:30:00Z',
            'total_violations': 1,
            'violations': [
                {
                    'file_path': 'test_file.py',
                    'line_number': 10,
                    'exception_type': 'ImportError',
                    'handler_body': ['pass'],
                    'context': 'import optional_dependency',
                    'severity': 'HIGH'
                }
            ]
        }
        
        # Create tools directory and violations file
        tools_dir = temp_workspace / "tools"
        tools_dir.mkdir()
        violations_file = tools_dir / "silent_swallower_report.json"
        with open(violations_file, 'w') as f:
            json.dump(sample_violations, f)
        
        with patch('fix_high_severity_silent_swallowers.PROJECT_ROOT', temp_workspace):
            fixer = HighSeveritySilentSwallowerFixer()
            
            # Should load violations
            assert len(fixer.violations) == 1
            assert fixer.violations[0]['exception_type'] == 'ImportError'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
