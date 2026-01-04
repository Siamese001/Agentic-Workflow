import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path
from agentic_core.utils.core_extensions.redis import SovereignRedisClient
from agentic_core.utils.core_extensions.git import SovereignGitClient


class TestSovereignRedisClientIntegration(unittest.TestCase):
    """Integration tests for SovereignRedisClient full flows."""

    def setUp(self):
        """Initialize test client."""
        self.client = SovereignRedisClient()

    def test_redis_full_flow_set_get(self):
        """Test full set/get flow with fallback."""
        self.client._get_client = MagicMock(return_value=None)
        self.client._fallback_cache = {}
        
        # Set operation
        set_result = self.client.execute('set', key='test_key', value='test_value')
        self.assertTrue(set_result['success'])
        self.assertIn('test_key', self.client._fallback_cache)
        
        # Get operation
        get_result = self.client.execute('get', key='test_key')
        self.assertTrue(get_result['success'])
        self.assertEqual(get_result['value'], 'test_value')

    def test_redis_full_flow_set_delete_get(self):
        """Test set/delete/get flow."""
        self.client._get_client = MagicMock(return_value=None)
        self.client._fallback_cache = {}
        
        # Set
        self.client.execute('set', key='test_key', value='test_value')
        self.assertIn('test_key', self.client._fallback_cache)
        
        # Delete
        delete_result = self.client.execute('delete', key='test_key')
        self.assertTrue(delete_result['success'])
        self.assertEqual(delete_result['deleted'], 1)
        self.assertNotIn('test_key', self.client._fallback_cache)
        
        # Get (should return None)
        get_result = self.client.execute('get', key='test_key')
        self.assertTrue(get_result['success'])
        self.assertIsNone(get_result['value'])

    def test_redis_full_flow_exists_check(self):
        """Test exists check flow."""
        self.client._get_client = MagicMock(return_value=None)
        self.client._fallback_cache = {}
        
        # Set
        self.client.execute('set', key='test_key', value='test_value')
        
        # Check exists
        exists_result = self.client.execute('exists', key='test_key')
        self.assertTrue(exists_result['success'])
        self.assertTrue(exists_result['exists'])
        
        # Check non-existent
        exists_result = self.client.execute('exists', key='nonexistent')
        self.assertTrue(exists_result['success'])
        self.assertFalse(exists_result['exists'])

    def test_redis_full_flow_keys_pattern(self):
        """Test keys pattern matching flow."""
        self.client._get_client = MagicMock(return_value=None)
        self.client._fallback_cache = {}
        
        # Set multiple keys
        self.client.execute('set', key='user:1', value='alice')
        self.client.execute('set', key='user:2', value='bob')
        self.client.execute('set', key='config:timeout', value='30')
        
        # Get keys matching pattern
        keys_result = self.client.execute('keys', pattern='user:*')
        self.assertTrue(keys_result['success'])
        self.assertEqual(set(keys_result['keys']), {'user:1', 'user:2'})

    def test_redis_dispatch_routing_consistency(self):
        """Test that dispatch routing is consistent across operations."""
        mock_client = MagicMock()
        self.client._get_client = MagicMock(return_value=mock_client)
        
        operations = ['set', 'get', 'delete', 'exists', 'keys', 'expire', 'ping']
        
        for op in operations:
            with self.subTest(operation=op):
                result = self.client.execute(op, key='test')
                self.assertIn('success', result)


class TestSovereignGitClientIntegration(unittest.TestCase):
    """Integration tests for SovereignGitClient full flows."""

    def setUp(self):
        """Initialize test client."""
        self.client = SovereignGitClient(repo_root=Path('/tmp/test_repo'))

    def test_git_full_flow_commit_push(self):
        """Test full commit/push flow."""
        self.client._run_git = MagicMock(return_value={'success': True, 'stdout': 'ok', 'stderr': ''})
        
        # Commit
        commit_result = self.client.execute('commit', message='Test commit', files=['test.py'])
        self.assertTrue(commit_result['success'])
        
        # Verify add was called
        add_calls = [call for call in self.client._run_git.call_args_list if 'add' in call[0][0]]
        self.assertEqual(len(add_calls), 1)
        
        # Push
        push_result = self.client.execute('push', branch='main', remote='origin')
        self.assertTrue(push_result['success'])

    def test_git_full_flow_checkout_status(self):
        """Test checkout/status flow."""
        self.client._run_git = MagicMock(return_value={'success': True, 'stdout': 'ok', 'stderr': ''})
        
        # Checkout
        checkout_result = self.client.execute('checkout', branch='feature')
        self.assertTrue(checkout_result['success'])
        self.client._run_git.assert_called_with(['checkout', 'feature'])
        
        # Status
        status_result = self.client.execute('status')
        self.assertTrue(status_result['success'])
        self.client._run_git.assert_called_with(['status', '--porcelain'])

    def test_git_full_flow_branch_operations(self):
        """Test branch list/create flow."""
        self.client._run_git = MagicMock(return_value={'success': True, 'stdout': 'ok', 'stderr': ''})
        
        # List branches
        list_result = self.client.execute('branch', action='list')
        self.assertTrue(list_result['success'])
        
        # Create branch
        create_result = self.client.execute('branch', action='create', name='feature')
        self.assertTrue(create_result['success'])

    def test_git_dispatch_routing_consistency(self):
        """Test that dispatch routing is consistent across operations."""
        self.client._run_git = MagicMock(return_value={'success': True, 'stdout': 'ok', 'stderr': ''})
        
        operations = ['commit', 'push', 'pull', 'status', 'diff', 'log', 'checkout', 'branch']
        
        for op in operations:
            with self.subTest(operation=op):
                result = self.client.execute(op, branch='main', message='test')
                self.assertIn('success', result)


class TestDispatchPatternConsistency(unittest.TestCase):
    """Test consistency of dispatch pattern across refactored clients."""

    def test_redis_dispatch_error_handling(self):
        """Test Redis dispatch handles errors consistently."""
        client = SovereignRedisClient()
        
        # Unsupported operation
        result = client.execute('invalid_op', key='test')
        self.assertFalse(result['success'])
        self.assertIn('Unsupported', result['error'])

    def test_git_dispatch_error_handling(self):
        """Test Git dispatch handles errors consistently."""
        client = SovereignGitClient()
        
        # Unsupported operation
        result = client.execute('invalid_op')
        self.assertFalse(result['success'])
        self.assertIn('Unsupported', result['error'])

    def test_redis_handler_isolation(self):
        """Test that Redis handlers are properly isolated."""
        client = SovereignRedisClient()
        client._get_client = MagicMock(return_value=None)
        client._fallback_cache = {}
        
        # Set creates entry
        client.execute('set', key='k1', value='v1')
        self.assertIn('k1', client._fallback_cache)
        
        # Delete removes entry
        client.execute('delete', key='k1')
        self.assertNotIn('k1', client._fallback_cache)
        
        # Other keys unaffected
        client.execute('set', key='k2', value='v2')
        self.assertIn('k2', client._fallback_cache)

    def test_git_handler_isolation(self):
        """Test that Git handlers are properly isolated."""
        client = SovereignGitClient()
        client._run_git = MagicMock(return_value={'success': True, 'stdout': 'ok', 'stderr': ''})
        
        # Each operation calls _run_git independently
        client.execute('status')
        call_count_1 = client._run_git.call_count
        
        client.execute('log')
        call_count_2 = client._run_git.call_count
        
        self.assertEqual(call_count_2 - call_count_1, 1)


if __name__ == '__main__':
    unittest.main()
