import unittest
import logging
from agentic_core.utils.core_extensions.migration_mixin import (
    MigrationMixin, 
    MigrationError
)

class VersionedAgent(MigrationMixin):
    _schema_version = "2.0"

    async def migrate_v1_0_to_next(self, data):
        """Simulate migration from 1.0 to 2.0."""
        data["new_field"] = data.pop("old_field")
        data["_new_version_id"] = "2.0"
        return data

class BrokenMigrationAgent(MigrationMixin):
    _schema_version = "2.0"
    # Missing migration method migrate_v1_0_to_next

class TestMigrationMixin(unittest.IsolatedAsyncioTestCase):
    
    def setUp(self):
        self.agent = VersionedAgent()
        self.logger = logging.getLogger("VersionedAgent")

    async def test_tc13_successful_migration(self):
        """TC13: Should successfully migrate data from 1.0 to 2.0."""
        old_data = {"old_field": "some_value"}
        
        with self.assertLogs(self.logger, level='INFO') as log:
            new_data = await self.agent.migrate_data(old_data, from_version="1.0")
            
            self.assertIn("new_field", new_data)
            self.assertNotIn("old_field", new_data)
            self.assertEqual(new_data["new_field"], "some_value")
            self.assertTrue(any("Migration successful" in m for m in log.output))

    async def test_tc14_no_migration_needed(self):
        """TC14: Should return data unchanged if versions match."""
        data = {"field": "value"}
        result = await self.agent.migrate_data(data, from_version="2.0")
        self.assertEqual(data, result)

    async def test_tc15_missing_migration_path(self):
        """TC15: Should raise MigrationError if migration method is missing."""
        broken_agent = BrokenMigrationAgent()
        with self.assertRaises(MigrationError):
            await broken_agent.migrate_data({"any": "data"}, from_version="1.0")

    async def test_tc16_migration_exception_handling(self):
        """TC16: Should catch and wrap exceptions inside migration methods."""
        class FailingAgent(MigrationMixin):
            _schema_version = "2.0"
            async def migrate_v1_0_to_next(self, data):
                raise ValueError("Crash")
        
        failing_agent = FailingAgent()
        with self.assertRaises(MigrationError):
            await failing_agent.migrate_data({}, from_version="1.0")

if __name__ == "__main__":
    unittest.main()
