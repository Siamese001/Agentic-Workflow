import unittest
from unittest.mock import MagicMock, patch, call
from pathlib import Path
from agentic_core.utils.core_extensions.redis import SovereignRedisClient


class TestSovereignRedisClientHandlers(unittest.TestCase):
    """Unit tests for refactored SovereignRedisClient dispatch handlers."""

    def setUp(self):
        """Initialize test client with mocked dependencies."""
        self.client = SovereignRedisClient()
        self.client._get_client = MagicMock(return_value=None)
        self.client._fallback_set = MagicMock()
        self.client._fallback_cache = {}
        self.client._audit = MagicMock()

    def test_handle_set_with_client_and_ttl(self):
        """Test _handle_set with real Redis client and TTL."""
        mock_client = MagicMock()
        self.client._get_client.return_value = mock_client
        
        result = self.client._handle_set(key='test_key', value='test_value', ttl=60)
        
        mock_client.setex.assert_called_once_with('test_key', 60, 'test_value')
        self.assertEqual(result, {'success': True})

    def test_handle_set_with_client_no_ttl(self):
        """Test _handle_set with real Redis client without TTL."""
        mock_client = MagicMock()
        self.client._get_client.return_value = mock_client
        
        result = self.client._handle_set(key='test_key', value='test_value', ttl=None)
        
        mock_client.set.assert_called_once_with('test_key', 'test_value')
        self.assertEqual(result, {'success': True})

    def test_handle_set_fallback_no_client(self):
        """Test _handle_set with fallback cache when client unavailable."""
        self.client._get_client.return_value = None
        
        result = self.client._handle_set(key='test_key', value='test_value')
        
        self.client._fallback_set.assert_called_once_with('test_key', 'test_value')
        self.assertEqual(result, {'success': True})

    def test_handle_get_with_client(self):
        """Test _handle_get with real Redis client."""
        mock_client = MagicMock()
        mock_client.get.return_value = 'test_value'
        self.client._get_client.return_value = mock_client
        
        result = self.client._handle_get(key='test_key')
        
        mock_client.get.assert_called_once_with('test_key')
        self.assertEqual(result, {'success': True, 'value': 'test_value'})

    def test_handle_get_fallback_no_client(self):
        """Test _handle_get with fallback cache when client unavailable."""
        self.client._get_client.return_value = None
        self.client._fallback_cache = {'test_key': 'cached_value'}
        
        result = self.client._handle_get(key='test_key')
        
        self.assertEqual(result, {'success': True, 'value': 'cached_value'})

    def test_handle_get_fallback_key_not_found(self):
        """Test _handle_get with fallback cache when key not found."""
        self.client._get_client.return_value = None
        self.client._fallback_cache = {}
        
        result = self.client._handle_get(key='nonexistent')
        
        self.assertEqual(result, {'success': True, 'value': None})

    def test_handle_delete_with_client(self):
        """Test _handle_delete with real Redis client."""
        mock_client = MagicMock()
        mock_client.delete.return_value = 1
        self.client._get_client.return_value = mock_client
        
        result = self.client._handle_delete(key='test_key')
        
        mock_client.delete.assert_called_once_with('test_key')
        self.assertEqual(result, {'success': True, 'deleted': 1})

    def test_handle_delete_fallback_key_exists(self):
        """Test _handle_delete with fallback cache when key exists."""
        self.client._get_client.return_value = None
        self.client._fallback_cache = {'test_key': 'value'}
        
        result = self.client._handle_delete(key='test_key')
        
        self.assertEqual(result, {'success': True, 'deleted': 1})
        self.assertNotIn('test_key', self.client._fallback_cache)

    def test_handle_delete_fallback_key_not_found(self):
        """Test _handle_delete with fallback cache when key not found."""
        self.client._get_client.return_value = None
        self.client._fallback_cache = {}
        
        result = self.client._handle_delete(key='nonexistent')
        
        self.assertEqual(result, {'success': True, 'deleted': 0})

    def test_handle_exists_with_client_true(self):
        """Test _handle_exists with real Redis client when key exists."""
        mock_client = MagicMock()
        mock_client.exists.return_value = 1
        self.client._get_client.return_value = mock_client
        
        result = self.client._handle_exists(key='test_key')
        
        mock_client.exists.assert_called_once_with('test_key')
        self.assertEqual(result, {'success': True, 'exists': True})

    def test_handle_exists_with_client_false(self):
        """Test _handle_exists with real Redis client when key not exists."""
        mock_client = MagicMock()
        mock_client.exists.return_value = 0
        self.client._get_client.return_value = mock_client
        
        result = self.client._handle_exists(key='test_key')
        
        self.assertEqual(result, {'success': True, 'exists': False})

    def test_handle_exists_fallback_true(self):
        """Test _handle_exists with fallback cache when key exists."""
        self.client._get_client.return_value = None
        self.client._fallback_cache = {'test_key': 'value'}
        
        result = self.client._handle_exists(key='test_key')
        
        self.assertEqual(result, {'success': True, 'exists': True})

    def test_handle_exists_fallback_false(self):
        """Test _handle_exists with fallback cache when key not exists."""
        self.client._get_client.return_value = None
        self.client._fallback_cache = {}
        
        result = self.client._handle_exists(key='nonexistent')
        
        self.assertEqual(result, {'success': True, 'exists': False})

    def test_handle_keys_with_client(self):
        """Test _handle_keys with real Redis client."""
        mock_client = MagicMock()
        mock_client.keys.return_value = ['key1', 'key2', 'key3']
        self.client._get_client.return_value = mock_client
        
        result = self.client._handle_keys(pattern='key*')
        
        mock_client.keys.assert_called_once_with('key*')
        self.assertEqual(result, {'success': True, 'keys': ['key1', 'key2', 'key3']})

    def test_handle_keys_fallback_with_pattern(self):
        """Test _handle_keys with fallback cache and pattern matching."""
        self.client._get_client.return_value = None
        self.client._fallback_cache = {'key1': 'v1', 'key2': 'v2', 'other': 'v3'}
        
        result = self.client._handle_keys(pattern='key*')
        
        self.assertEqual(set(result['keys']), {'key1', 'key2'})
        self.assertEqual(result['success'], True)

    def test_handle_keys_fallback_default_pattern(self):
        """Test _handle_keys with fallback cache and default pattern."""
        self.client._get_client.return_value = None
        self.client._fallback_cache = {'key1': 'v1', 'key2': 'v2'}
        
        result = self.client._handle_keys(pattern='*')
        
        self.assertEqual(set(result['keys']), {'key1', 'key2'})

    def test_handle_expire_with_client(self):
        """Test _handle_expire with real Redis client."""
        mock_client = MagicMock()
        self.client._get_client.return_value = mock_client
        
        result = self.client._handle_expire(key='test_key', ttl=3600)
        
        mock_client.expire.assert_called_once_with('test_key', 3600)
        self.assertEqual(result, {'success': True})

    def test_handle_expire_fallback_no_op(self):
        """Test _handle_expire with fallback (no-op)."""
        self.client._get_client.return_value = None
        
        result = self.client._handle_expire(key='test_key', ttl=3600)
        
        self.assertEqual(result, {'success': True})

    def test_handle_ping_with_client(self):
        """Test _handle_ping with real Redis client."""
        mock_client = MagicMock()
        self.client._get_client.return_value = mock_client
        
        result = self.client._handle_ping()
        
        mock_client.ping.assert_called_once()
        self.assertEqual(result, {'success': True, 'pong': True, 'fallback': False})

    def test_handle_ping_fallback(self):
        """Test _handle_ping with fallback."""
        self.client._get_client.return_value = None
        self.client._use_fallback = True
        
        result = self.client._handle_ping()
        
        self.assertEqual(result, {'success': True, 'pong': True, 'fallback': True})

    def test_execute_dispatch_all_operations(self):
        """Test execute dispatch routes all operations correctly."""
        mock_client = MagicMock()
        self.client._get_client.return_value = mock_client
        
        operations = {
            'set': {'key': 'k', 'value': 'v'},
            'get': {'key': 'k'},
            'delete': {'key': 'k'},
            'exists': {'key': 'k'},
            'keys': {'pattern': '*'},
            'expire': {'key': 'k', 'ttl': 60},
            'ping': {},
        }
        
        for op, payload in operations.items():
            with self.subTest(operation=op):
                result = self.client.execute(op, **payload)
                self.assertIn('success', result)
                self.assertTrue(result['success'])

    def test_execute_unsupported_operation(self):
        """Test execute with unsupported operation."""
        result = self.client.execute('unsupported_op', key='k')
        
        self.assertFalse(result['success'])
        self.assertIn('Unsupported', result['error'])

    def test_execute_with_exception_in_handler(self):
        """Test execute handles exceptions from handlers."""
        mock_client = MagicMock()
        mock_client.set.side_effect = Exception('Redis connection failed')
        self.client._get_client.return_value = mock_client
        
        result = self.client.execute('set', key='k', value='v')
        
        self.assertFalse(result['success'])
        self.assertIn('Redis connection failed', result['error'])

    def test_audit_logging_on_execute(self):
        """Test that execute calls audit logging."""
        mock_client = MagicMock()
        self.client._get_client.return_value = mock_client
        
        self.client.execute('set', key='test_key', value='test_value')
        
        self.client._audit.assert_called_once()
        call_args = self.client._audit.call_args
        self.assertEqual(call_args[0][0], 'set')
        self.assertEqual(call_args[0][1], 'test_key')


if __name__ == '__main__':
    unittest.main()
