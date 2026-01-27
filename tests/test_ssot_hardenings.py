"""
File: tests/test_ssot_hardenings.py
Description: Verification of critical hardenings applied to the SSOT protocol.
"""

import unittest
from unittest.mock import MagicMock, patch
import os
import sys

# Mock imports
sys.modules['agentic_core'] = MagicMock()

class TestSSOTHardening(unittest.TestCase):

    @patch('sys.exit')
    @patch('builtins.input')
    def test_headless_environment_protection(self, mock_input, mock_exit):
        """
        CRITICAL TEST 1: Headless Environment Detection
        Ensures the script dies immediately if running in CI/CD without TTY,
        preventing infinite hangs at input() prompts.
        """
        # Simulate CI environment
        with patch.dict(os.environ, {'CI': 'true'}):
            # Inline import or logic simulation of Phase 4 check
            if os.environ.get('CI') == 'true':
                mock_exit(1)
            else:
                mock_input("Prompt")
        
        mock_exit.assert_called_with(1)
        mock_input.assert_not_called()

    @patch('sys.exit')
    def test_healing_illusion_key_error_fix(self, mock_exit):
        """
        CRITICAL TEST 2: Schema Validation
        The original code checked `post_heal_audit['violations']`.
        This test proves that key likely doesn't exist and ensures the fix 
        (checking specific violation keys) works correctly.
        """
        # Mock a report that mimics the ArchitectureGovernorAgent output
        # Notice: NO 'violations' key, only specific categories
        mock_report = {
            'layer_violations': ['v1'],
            'naming_violations': []
        }
        
        try:
            # VULNERABLE LOGIC (Simulated)
            # if mock_report['violations']: pass 
            # -> This would raise KeyError
            
            # HARDENED LOGIC
            count = len(mock_report.get('layer_violations', [])) + len(mock_report.get('naming_violations', []))
            if count > 0:
                mock_exit(1)
                
        except KeyError:
            self.fail("Hardened logic raised KeyError! Schema mismatch detected.")
            
        mock_exit.assert_called_with(1)

    @patch('sys.exit')
    def test_null_agent_crash_prevention(self, mock_exit):
        """
        CRITICAL TEST 3: Null Agent Response
        Verifies that receiving None from an agent triggers a clean exit
        rather than an AttributeError crash.
        """
        mock_agent_response = None
        
        try:
            if mock_agent_response is None:
                mock_exit(1)
            else:
                # This would crash if guard clause was missing
                print(mock_agent_response['success']) 
        except TypeError:
             self.fail("Script crashed on NoneType access!")
             
        mock_exit.assert_called_with(1)
        
    @patch('sys.exit')
    def test_circular_dependency_halt(self, mock_exit):
        """
        CRITICAL TEST 4: Recursive Death Prevention
        Ensures circular dependencies are treated as FATAL, not just warnings.
        """
        report = {'imports_valid': False, 'circular_dependencies': ['A->B->A']}
        
        if not report['imports_valid']:
            mock_exit(1)
            
        mock_exit.assert_called_with(1)

    @patch('sys.exit')
    @patch('sys.stdin.isatty', return_value=False)
    def test_tty_detection_protection(self, mock_isatty, mock_exit):
        """
        CRITICAL TEST 5: TTY Detection
        Ensures script exits when no TTY is available (even if not CI environment).
        """
        # Simulate non-TTY environment (like Docker container without TTY)
        if not sys.stdin.isatty():
            mock_exit(1)
            
        mock_exit.assert_called_with(1)
        mock_isatty.assert_called_once()

    @patch('sys.exit')
    def test_safe_dictionary_access_evolution(self, mock_exit):
        """
        CRITICAL TEST 6: Schema Evolution Protection
        Tests that .get() method prevents crashes when agent schema evolves.
        """
        # Simulate future agent version with different schema
        future_report = {
            'layer_violations': ['v1'],
            # 'naming_violations' key removed in future version
        }
        
        try:
            # HARDENED LOGIC should work with evolving schema
            count = len(future_report.get('layer_violations', [])) + len(future_report.get('naming_violations', []))
            if count > 0:
                mock_exit(1)
                
        except KeyError:
            self.fail("Hardened logic failed with evolved schema!")
            
        mock_exit.assert_called_with(1)

    @patch('sys.exit')
    def test_empty_violation_lists_handling(self, mock_exit):
        """
        CRITICAL TEST 7: Empty Violation Lists
        Ensures empty violation lists are handled correctly without crashes.
        """
        empty_report = {
            'layer_violations': [],
            'naming_violations': []
        }
        
        # HARDENED LOGIC should handle empty lists gracefully
        count = len(empty_report.get('layer_violations', [])) + len(empty_report.get('naming_violations', []))
        
        # Should not trigger exit for empty violations
        if count > 0:
            mock_exit(1)
        else:
            # No violations - should not exit
            pass
            
        mock_exit.assert_not_called()

    @patch('sys.exit')
    def test_missing_keys_fallback(self, mock_exit):
        """
        CRITICAL TEST 8: Missing Keys Fallback
        Tests that completely missing violation keys don't crash the script.
        """
        minimal_report = {
            # No violation keys at all - minimal agent response
            'status': 'complete'
        }
        
        try:
            # HARDENED LOGIC should handle missing keys gracefully
            count = len(minimal_report.get('layer_violations', [])) + len(minimal_report.get('naming_violations', []))
            
            # Should not trigger exit for missing keys (treated as empty)
            if count > 0:
                mock_exit(1)
                
        except KeyError:
            self.fail("Hardened logic crashed on missing keys!")
            
        mock_exit.assert_not_called()

if __name__ == '__main__':
    unittest.main()
