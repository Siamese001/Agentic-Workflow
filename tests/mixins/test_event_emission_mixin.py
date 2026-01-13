import unittest
import logging
from agentic_core.utils.core_extensions.event_emission_mixin import (
    EventEmissionMixin, 
    SovereignEvent
)

class ObservableAgent(EventEmissionMixin):
    @EventEmissionMixin.observe_execution("task_alpha")
    async def do_work(self, fail=False):
        if fail:
            raise ValueError("Intentional Failure")
        return "Success"

class TestEventEmissionMixin(unittest.IsolatedAsyncioTestCase):
    
    def setUp(self):
        self.agent = ObservableAgent()
        self.logger = logging.getLogger("ObservableAgent")

    async def test_tc9_manual_emission(self):
        """TC9: Should correctly structure and emit a manual event."""
        with self.assertLogs(self.logger, level='INFO') as log:
            event = self.agent.emit_event("manual_test", {"key": "val"}, severity="INFO")
            
            self.assertIsInstance(event, SovereignEvent)
            self.assertEqual(event.event_type, "manual_test")
            self.assertEqual(event.source_agent, "ObservableAgent")
            self.assertTrue(any("EVENT [manual_test]" in m for m in log.output))

    async def test_tc10_decorator_lifecycle_success(self):
        """TC10: Decorator should emit both .started and .completed events."""
        with self.assertLogs(self.logger, level='INFO') as log:
            await self.agent.do_work(fail=False)
            
            output = "\n".join(log.output)
            self.assertIn("task_alpha.started", output)
            self.assertIn("task_alpha.completed", output)
            self.assertIn("'success': True", output)

    async def test_tc11_decorator_lifecycle_failure(self):
        """TC11: Decorator should emit .failed event with ERROR severity on exception."""
        with self.assertRaises(ValueError):
            with self.assertLogs(self.logger, level='ERROR') as log:
                await self.agent.do_work(fail=True)
                
                output = "\n".join(log.output)
                self.assertIn("task_alpha.failed", output)
                self.assertIn("Intentional Failure", output)

    def test_tc12_event_id_uniqueness(self):
        """TC12: Each event should have a unique UUID."""
        e1 = self.agent.emit_event("test1")
        e2 = self.agent.emit_event("test2")
        self.assertNotEqual(e1.event_id, e2.event_id)

if __name__ == "__main__":
    unittest.main()
