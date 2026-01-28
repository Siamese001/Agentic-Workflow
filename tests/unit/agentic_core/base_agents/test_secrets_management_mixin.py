# TESTS DEPTH VIOLATION — 2026-01-18 05:21:41
# tests\mixins\test_secrets_management_mixin.py was depth 3, MUST be 2.

import unittest
import os
import logging
from unittest.mock import patch, MagicMock
from agentic_core.utils.core_extensions.secrets_management_mixin import (
    SecretsManagementMixin, 
    SecretAccessError
)

# Mock Agent Class
class SecureAgent(SecretsManagementMixin):
    pass

class TestSecretsManagementMixin(unittest.IsolatedAsyncioTestCase):
    
    def setUp(self):
        # Capture logs to verify auditing
        self.agent = SecureAgent()
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("SecureAgent")

    async def test_tc1_retrieve_existing_secret(self):
        """TC1: Should successfully retrieve an existing environment variable."""
        with patch.dict(os.environ, {"TEST_API_KEY": "super_secret_value"}):
            with self.assertLogs(self.logger, level='INFO') as log:
                value = await self.agent.get_secret("TEST_API_KEY")
                self.assertEqual(value, "super_secret_value")
                
                # Verify Audit Log
                self.assertTrue(any("AUDIT: Secret access" in m for m in log.output))
                self.assertTrue(any("Status='ALLOWED'" in m for m in log.output))

    async def test_tc2_missing_secret_raises_error(self):
        """TC2: Should raise SecretAccessError when key is missing and no default."""
        with self.assertRaises(SecretAccessError):
            with self.assertLogs(self.logger, level='INFO') as log:
                await self.agent.get_secret("NON_EXISTENT_KEY")
                # Verify Audit Log records DENIED
                self.assertTrue(any("Status='DENIED'" in m for m in log.output))

    async def test_tc3_default_fallback(self):
        """TC3: Should return default value if key missing, and log as ALLOWED."""
        with self.assertLogs(self.logger, level='INFO') as log:
            value = await self.agent.get_secret("MISSING_KEY", default="fallback_value")
            self.assertEqual(value, "fallback_value")
            self.assertTrue(any("Status='ALLOWED'" in m for m in log.output))

    def test_tc4_environment_context(self):
        """TC4: Should correctly identify the environment context."""
        with patch.dict(os.environ, {"SOVEREIGN_ENV": "PROD"}):
            prod_agent = SecureAgent()
            self.assertEqual(prod_agent._env_context, "PROD")

if __name__ == "__main__":
    unittest.main()
