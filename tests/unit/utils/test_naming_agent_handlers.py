import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path
from agentic_core.utils.core_extensions.NamingAgent import NamingAgent


class TestNamingAgentHealingDispatch(unittest.TestCase):
    """Unit tests for refactored NamingAgent healing dispatch handlers."""

    def setUp(self):
        """Initialize test agent with mocked dependencies."""
        self.agent = NamingAgent()
        self.agent._print_healing_summary = MagicMock()

    def test_initialize_summary(self):
        """Test _initialize_summary creates correct structure."""
        summary = self.agent._initialize_summary()
        
        self.assertEqual(summary['renamed'], 0)
        self.assertEqual(summary['collisions_blocked'], 0)
        self.assertEqual(summary['multi_agent_needs_split'], 0)
        self.assertEqual(summary['skipped'], 0)
        self.assertEqual(summary['errors'], 0)

    def test_is_agent_naming_violation_true(self):
        """Test _is_agent_naming_violation with valid violation."""
        result = self.agent._is_agent_naming_violation('AGENT FILE NAMING VIOLATION: test')
        self.assertTrue(result)

    def test_is_agent_naming_violation_false(self):
        """Test _is_agent_naming_violation with non-violation."""
        result = self.agent._is_agent_naming_violation('OTHER VIOLATION: test')
        self.assertFalse(result)

    def test_handle_renamed(self):
        """Test _handle_renamed increments counter."""
        summary = {'renamed': 0, 'collisions_blocked': 0, 'multi_agent_needs_split': 0, 'skipped': 0, 'errors': 0}
        proposal = {'new_path': '/path/to/NewAgent.py'}
        file_path = Path('/path/to/old_agent.py')
        
        with patch('builtins.print'):
            self.agent._handle_renamed(proposal, file_path, summary)
        
        self.assertEqual(summary['renamed'], 1)

    def test_handle_proposed(self):
        """Test _handle_proposed increments counter."""
        summary = {'renamed': 0, 'collisions_blocked': 0, 'multi_agent_needs_split': 0, 'skipped': 0, 'errors': 0}
        proposal = {'new_path': '/path/to/NewAgent.py'}
        file_path = Path('/path/to/old_agent.py')
        
        with patch('builtins.print'):
            self.agent._handle_proposed(proposal, file_path, summary)
        
        self.assertEqual(summary['renamed'], 1)

    def test_handle_collision(self):
        """Test _handle_collision increments counter."""
        summary = {'renamed': 0, 'collisions_blocked': 0, 'multi_agent_needs_split': 0, 'skipped': 0, 'errors': 0}
        proposal = {'best_name': 'NewAgent.py', 'error': 'File exists'}
        file_path = Path('/path/to/old_agent.py')
        
        with patch('builtins.print'):
            self.agent._handle_collision(proposal, file_path, summary)
        
        self.assertEqual(summary['collisions_blocked'], 1)

    def test_handle_multi_agent_split(self):
        """Test _handle_multi_agent_split increments counter."""
        summary = {'renamed': 0, 'collisions_blocked': 0, 'multi_agent_needs_split': 0, 'skipped': 0, 'errors': 0}
        proposal = {}
        file_path = Path('/path/to/MultiAgent.py')
        
        with patch('builtins.print'):
            self.agent._handle_multi_agent_split(proposal, file_path, summary)
        
        self.assertEqual(summary['multi_agent_needs_split'], 1)

    def test_handle_compliant(self):
        """Test _handle_compliant increments skipped counter."""
        summary = {'renamed': 0, 'collisions_blocked': 0, 'multi_agent_needs_split': 0, 'skipped': 0, 'errors': 0}
        proposal = {}
        file_path = Path('/path/to/CompliantAgent.py')
        
        self.agent._handle_compliant(proposal, file_path, summary)
        
        self.assertEqual(summary['skipped'], 1)

    def test_handle_error(self):
        """Test _handle_error increments error counter."""
        summary = {'renamed': 0, 'collisions_blocked': 0, 'multi_agent_needs_split': 0, 'skipped': 0, 'errors': 0}
        proposal = {'status': 'error', 'error': 'Unknown error'}
        file_path = Path('/path/to/BadAgent.py')
        
        with patch('builtins.print'):
            self.agent._handle_error(proposal, file_path, summary)
        
        self.assertEqual(summary['errors'], 1)

    def test_process_healing_status_dispatches_renamed(self):
        """Test _process_healing_status dispatches to correct handler."""
        summary = {'renamed': 0, 'collisions_blocked': 0, 'multi_agent_needs_split': 0, 'skipped': 0, 'errors': 0}
        proposal = {'status': 'renamed', 'new_path': '/path/to/NewAgent.py'}
        file_path = Path('/path/to/old_agent.py')
        
        with patch.object(self.agent, '_handle_renamed') as mock_handler:
            self.agent._process_healing_status(proposal, file_path, summary)
            mock_handler.assert_called_once_with(proposal, file_path, summary)

    def test_process_healing_status_dispatches_collision(self):
        """Test _process_healing_status dispatches to collision handler."""
        summary = {'renamed': 0, 'collisions_blocked': 0, 'multi_agent_needs_split': 0, 'skipped': 0, 'errors': 0}
        proposal = {'status': 'collision', 'error': 'File exists'}
        file_path = Path('/path/to/old_agent.py')
        
        with patch.object(self.agent, '_handle_collision') as mock_handler:
            self.agent._process_healing_status(proposal, file_path, summary)
            mock_handler.assert_called_once_with(proposal, file_path, summary)

    def test_process_healing_status_dispatches_error_default(self):
        """Test _process_healing_status dispatches unknown status to error handler."""
        summary = {'renamed': 0, 'collisions_blocked': 0, 'multi_agent_needs_split': 0, 'skipped': 0, 'errors': 0}
        proposal = {'status': 'unknown'}
        file_path = Path('/path/to/old_agent.py')
        
        with patch.object(self.agent, '_handle_error') as mock_handler:
            self.agent._process_healing_status(proposal, file_path, summary)
            mock_handler.assert_called_once_with(proposal, file_path, summary)

    def test_print_healing_summary(self):
        """Test _print_healing_summary prints correct format."""
        summary = {
            'renamed': 5,
            'collisions_blocked': 2,
            'multi_agent_needs_split': 1,
            'skipped': 3,
            'errors': 0
        }
        
        with patch('builtins.print') as mock_print:
            self.agent._print_healing_summary(summary)
            mock_print.assert_called_once()
            call_args = mock_print.call_args[0][0]
            self.assertIn('Renamed: 5', call_args)
            self.assertIn('Collisions: 2', call_args)
            self.assertIn('Split needed: 1', call_args)
            self.assertIn('Skipped: 3', call_args)
            self.assertIn('Errors: 0', call_args)

    def test_determine_confidence_level_high(self):
        """Test _determine_confidence_level returns HIGH for high confidence."""
        # Assuming PLACEMENT_CONFIDENCE["HIGH"] is around 0.8
        result = self.agent._determine_confidence_level(0.9)
        self.assertEqual(result, "HIGH")

    def test_determine_confidence_level_medium(self):
        """Test _determine_confidence_level returns MEDIUM for medium confidence."""
        # Assuming PLACEMENT_CONFIDENCE["MEDIUM"] is around 0.6
        result = self.agent._determine_confidence_level(0.7)
        self.assertIn(result, ["HIGH", "MEDIUM"])

    def test_determine_confidence_level_low(self):
        """Test _determine_confidence_level returns LOW for low confidence."""
        # Assuming PLACEMENT_CONFIDENCE["LOW"] is around 0.4
        result = self.agent._determine_confidence_level(0.5)
        self.assertIn(result, ["HIGH", "MEDIUM", "LOW"])

    def test_determine_confidence_level_reject(self):
        """Test _determine_confidence_level returns REJECT for very low confidence."""
        result = self.agent._determine_confidence_level(0.1)
        self.assertEqual(result, "REJECT")

    def test_determine_confidence_level_zero(self):
        """Test _determine_confidence_level returns REJECT for zero confidence."""
        result = self.agent._determine_confidence_level(0.0)
        self.assertEqual(result, "REJECT")


if __name__ == '__main__':
    unittest.main()
