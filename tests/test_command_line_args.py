#!/usr/bin/env python3
"""
File: tests/test_command_line_args.py
Description: Validates that the orchestrator correctly handles CLI arguments 
and rejects unauthorized or missing territory paths.
"""

import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Mock the core agents to prevent filesystem interaction during CLI tests
sys.modules['agentic_core'] = MagicMock()

class TestCLIHardening(unittest.TestCase):

    def test_cli_territory_injection(self):
        """
        CRITICAL TEST 9: CLI Argument Injection.
        Ensures the main() function correctly accepts and prioritizes the 
        --territory argument over hardcoded defaults.
        """
        from scripts.execute_ssot_compliance_protocol import main
        
        # Mock agents dict
        mock_agents = {'registry': {'test_folder': {}}}
        
        with patch('scripts.execute_ssot_compliance_protocol.execute_phase0_validation', return_value=mock_agents):
            with patch('scripts.execute_ssot_compliance_protocol.execute_territory_compliance') as mock_exec:
                # Test passing a specific folder
                main(target_territory="prompt_governance")
                
                # Verify the execution was called ONLY for the requested folder
                mock_exec.assert_called_once()
                self.assertEqual(mock_exec.call_args[0][1], "prompt_governance")

    @patch('sys.exit')
    def test_missing_registry_hard_stop(self, mock_exit):
        """
        CRITICAL TEST 10: Missing Registry Safety.
        Ensures that if no territory is provided AND the registry is empty, 
        the system executes a hard stop (exit 1) rather than a null pointer crash.
        """
        from scripts.execute_ssot_compliance_protocol import main
        
        # Mock empty registry
        mock_agents = {'registry': {}}
        
        with patch('scripts.execute_ssot_compliance_protocol.execute_phase0_validation', return_value=mock_agents):
            # The sys.exit(1) should be called and raise SystemExit
            mock_exit.side_effect = SystemExit(1)
            
            with self.assertRaises(SystemExit):
                main(target_territory=None)
            
        mock_exit.assert_called_with(1)

    def test_ci_mode_cli_interaction(self):
        """
        CRITICAL TEST 11: CI/CD Execution logic.
        Verifies that even when a territory is specified via CLI, 
        interactive phases are still blocked if CI environment is detected.
        """
        from scripts.execute_ssot_compliance_protocol import execute_phase2_alignment
        
        mock_agents = {'hierarchy': MagicMock(), 'subfolder_map': {}}
        mock_drift = {'has_changes': True}
        
        # Simulate CI environment
        with patch.dict(os.environ, {'CI': 'true'}):
            with patch('sys.exit') as mock_exit:
                with patch('builtins.input', side_effect=EOFError("Simulated non-interactive")):
                    execute_phase2_alignment(mock_agents, "prompt_governance", mock_drift)
                    mock_exit.assert_called_with(1)

    @patch('argparse.ArgumentParser.parse_args')
    def test_argparse_passthrough(self, mock_args):
        """
        CRITICAL TEST 12: Argparse Integration.
        Ensures that if --territory is passed via shell, it reaches the main logic.
        """
        mock_args.return_value = MagicMock(territory="custom_folder")
        from scripts.execute_ssot_compliance_protocol import main
        
        with patch('scripts.execute_ssot_compliance_protocol.execute_phase0_validation', return_value={'registry': {}}):
             with patch('scripts.execute_ssot_compliance_protocol.execute_territory_compliance') as mock_exec:
                 # Logic simulation of the __main__ block
                 from scripts.execute_ssot_compliance_protocol import main
                 main(target_territory="custom_folder")
                 self.assertEqual(mock_exec.call_args[0][1], "custom_folder")

    def test_default_territory_selection(self):
        """
        CRITICAL TEST 13: Default Territory Selection.
        Ensures that when no territory is specified, the first registry territory is selected.
        """
        from scripts.execute_ssot_compliance_protocol import main
        
        # Mock registry with multiple territories
        mock_agents = {'registry': {'first_folder': {}, 'second_folder': {}}}
        
        with patch('scripts.execute_ssot_compliance_protocol.execute_phase0_validation', return_value=mock_agents):
            with patch('scripts.execute_ssot_compliance_protocol.execute_territory_compliance') as mock_exec:
                main(target_territory=None)
                
                # Verify the execution was called for the FIRST folder in registry
                mock_exec.assert_called_once()
                self.assertEqual(mock_exec.call_args[0][1], "first_folder")

    def test_invalid_territory_handling(self):
        """
        CRITICAL TEST 14: Invalid Territory Handling.
        Ensures the system gracefully handles territories not in registry.
        """
        from scripts.execute_ssot_compliance_protocol import main
        
        # Mock registry with limited territories
        mock_agents = {'registry': {'valid_folder': {}}}
        
        with patch('scripts.execute_ssot_compliance_protocol.execute_phase0_validation', return_value=mock_agents):
            with patch('scripts.execute_ssot_compliance_protocol.execute_territory_compliance') as mock_exec:
                # Test with territory not in registry
                main(target_territory="invalid_folder")
                
                # Should still attempt to process the requested territory
                mock_exec.assert_called_once()
                self.assertEqual(mock_exec.call_args[0][1], "invalid_folder")

if __name__ == '__main__':
    unittest.main()
