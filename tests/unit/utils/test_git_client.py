import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path
from agentic_core.utils.core_extensions.git import SovereignGitClient


class TestSovereignGitClientHandlers(unittest.TestCase):
    """Unit tests for refactored SovereignGitClient dispatch handlers."""

    def setUp(self):
        """Initialize test client with mocked dependencies."""
        self.client = SovereignGitClient(repo_root=Path('/tmp/test_repo'))
        self.client._run_git = MagicMock(return_value={'success': True, 'stdout': 'output', 'stderr': ''})
        self.client._audit = MagicMock()

    def test_handle_commit_with_files(self):
        """Test _handle_commit with files to add."""
        result = self.client._handle_commit(message='Test commit', files=['file1.py', 'file2.py'])
        
        self.assertEqual(self.client._run_git.call_count, 3)
        calls = self.client._run_git.call_args_list
        self.assertEqual(calls[0][0][0], ['add', 'file1.py'])
        self.assertEqual(calls[1][0][0], ['add', 'file2.py'])
        self.assertEqual(calls[2][0][0], ['commit', '-m', 'Test commit'])
        self.assertTrue(result['success'])

    def test_handle_commit_no_files(self):
        """Test _handle_commit without files."""
        result = self.client._handle_commit(message='Test commit', files=None)
        
        self.client._run_git.assert_called_once_with(['commit', '-m', 'Test commit'])
        self.assertTrue(result['success'])

    def test_handle_commit_default_message(self):
        """Test _handle_commit with default message."""
        result = self.client._handle_commit()
        
        self.client._run_git.assert_called_once_with(['commit', '-m', 'Sovereign commit'])
        self.assertTrue(result['success'])

    def test_handle_push_default_params(self):
        """Test _handle_push with default parameters."""
        result = self.client._handle_push()
        
        self.client._run_git.assert_called_once_with(['push', 'origin', 'HEAD'])
        self.assertTrue(result['success'])

    def test_handle_push_custom_branch_and_remote(self):
        """Test _handle_push with custom branch and remote."""
        result = self.client._handle_push(branch='feature', remote='upstream')
        
        self.client._run_git.assert_called_once_with(['push', 'upstream', 'feature'])
        self.assertTrue(result['success'])

    def test_handle_pull_default_params(self):
        """Test _handle_pull with default parameters."""
        result = self.client._handle_pull()
        
        self.client._run_git.assert_called_once_with(['pull', 'origin'])
        self.assertTrue(result['success'])

    def test_handle_pull_with_branch(self):
        """Test _handle_pull with specific branch."""
        result = self.client._handle_pull(remote='origin', branch='main')
        
        self.client._run_git.assert_called_once_with(['pull', 'origin', 'main'])
        self.assertTrue(result['success'])

    def test_handle_status(self):
        """Test _handle_status."""
        result = self.client._handle_status()
        
        self.client._run_git.assert_called_once_with(['status', '--porcelain'])
        self.assertTrue(result['success'])

    def test_handle_diff_no_file(self):
        """Test _handle_diff without specific file."""
        result = self.client._handle_diff()
        
        self.client._run_git.assert_called_once_with(['diff'])
        self.assertTrue(result['success'])

    def test_handle_diff_with_file(self):
        """Test _handle_diff with specific file."""
        result = self.client._handle_diff(file='test.py')
        
        self.client._run_git.assert_called_once_with(['diff', 'test.py'])
        self.assertTrue(result['success'])

    def test_handle_log_default_count(self):
        """Test _handle_log with default count."""
        result = self.client._handle_log()
        
        self.client._run_git.assert_called_once_with(['log', '-10', '--oneline'])
        self.assertTrue(result['success'])

    def test_handle_log_custom_count(self):
        """Test _handle_log with custom count."""
        result = self.client._handle_log(count=20)
        
        self.client._run_git.assert_called_once_with(['log', '-20', '--oneline'])
        self.assertTrue(result['success'])

    def test_handle_checkout_success(self):
        """Test _handle_checkout with valid branch."""
        result = self.client._handle_checkout(branch='feature')
        
        self.client._run_git.assert_called_once_with(['checkout', 'feature'])
        self.assertTrue(result['success'])

    def test_handle_checkout_missing_branch(self):
        """Test _handle_checkout without branch name."""
        result = self.client._handle_checkout(branch='')
        
        self.assertFalse(result['success'])
        self.assertIn('Branch required', result['error'])

    def test_handle_branch_list(self):
        """Test _handle_branch with list action."""
        result = self.client._handle_branch(action='list')
        
        self.client._run_git.assert_called_once_with(['branch', '-a'])
        self.assertTrue(result['success'])

    def test_handle_branch_create_success(self):
        """Test _handle_branch with create action and name."""
        result = self.client._handle_branch(action='create', name='feature')
        
        self.client._run_git.assert_called_once_with(['branch', 'feature'])
        self.assertTrue(result['success'])

    def test_handle_branch_create_missing_name(self):
        """Test _handle_branch with create action but no name."""
        result = self.client._handle_branch(action='create', name='')
        
        self.assertFalse(result['success'])
        self.assertIn('Branch name required', result['error'])

    def test_handle_branch_unknown_action(self):
        """Test _handle_branch with unknown action."""
        result = self.client._handle_branch(action='unknown')
        
        self.assertFalse(result['success'])
        self.assertIn('Unknown branch action', result['error'])

    def test_execute_dispatch_all_operations(self):
        """Test execute dispatch routes all operations correctly."""
        operations = {
            'commit': {'message': 'test'},
            'push': {'branch': 'main'},
            'pull': {'remote': 'origin'},
            'status': {},
            'diff': {'file': 'test.py'},
            'log': {'count': 10},
            'checkout': {'branch': 'main'},
            'branch': {'action': 'list'},
        }
        
        for op, payload in operations.items():
            with self.subTest(operation=op):
                result = self.client.execute(op, **payload)
                self.assertIn('success', result)

    def test_execute_unsupported_operation(self):
        """Test execute with unsupported operation."""
        result = self.client.execute('unsupported_op')
        
        self.assertFalse(result['success'])
        self.assertIn('Unsupported', result['error'])

    def test_execute_with_exception_in_handler(self):
        """Test execute handles exceptions from handlers."""
        self.client._run_git.side_effect = Exception('Git command failed')
        
        result = self.client.execute('status')
        
        self.assertFalse(result['success'])
        self.assertIn('Git command failed', result['error'])

    def test_audit_logging_on_execute(self):
        """Test that execute calls audit logging."""
        self.client.execute('status')
        
        self.client._audit.assert_called_once()
        call_args = self.client._audit.call_args
        self.assertEqual(call_args[0][0], 'status')


if __name__ == '__main__':
    unittest.main()
