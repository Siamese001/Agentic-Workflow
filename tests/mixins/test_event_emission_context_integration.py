import unittest
from agentic_core.utils.core_extensions.context_propagation_mixin import ContextPropagationMixin, trace_id_var
from agentic_core.utils.core_extensions.event_emission_mixin import EventEmissionMixin, SovereignEvent

class TracedEventAgent(ContextPropagationMixin, EventEmissionMixin):
    @ContextPropagationMixin.trace_context
    async def do_traced_emit(self):
        # Emit without explicit trace_id to ensure contextvar is used
        event = self.emit_event("integration.test", {"key": "val"})
        return event

class TestEventEmissionContextIntegration(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.agent = TracedEventAgent()

    async def test_tc23_event_includes_context_trace_id(self):
        event = await self.agent.do_traced_emit()
        self.assertIsInstance(event, SovereignEvent)
        self.assertIsNotNone(event.trace_id)
        self.assertEqual(event.trace_id, trace_id_var.get())

    async def test_tc24_event_payload_includes_span_id(self):
        event = await self.agent.do_traced_emit()
        self.assertIn("span_id", event.payload)
        self.assertIsNotNone(event.payload["span_id"])

if __name__ == "__main__":
    unittest.main()
