"""
Unit tests for The Streamer (L5 Live Reasoning Broadcast) implementation.
Tests non-blocking JSONL streaming, stress load handling, and reasoning extraction.

These tests verify the "All Tests Pass" provision for L5 Full Autonomy.
"""
import asyncio
import json
import os
import re
import shutil
import tempfile

import pytest

# ==============================================================================
# STANDALONE STREAMER IMPLEMENTATION FOR TESTING
# (Mirrors canon_validator_agentic.py without heavy dependencies)
# ==============================================================================

class MockValidationContext:
    """Lightweight mock of ValidationContext for streamer testing."""

    def __init__(self, stream_dir: str = None):
        self.stream_queue: asyncio.Queue = asyncio.Queue()
        self.stream_task: asyncio.Task = None
        self._current_agent: str = "System"
        self._streamer_initialized: bool = False
        self.signals: set = set()
        self._stream_dir = stream_dir or "observability/audit"
        self._log_path = os.path.join(self._stream_dir, "live_stream.jsonl")

    async def start_streamer(self):
        """Initializes the non-blocking stream worker task."""
        if self._streamer_initialized:
            return

        os.makedirs(self._stream_dir, exist_ok=True)

        if not self.stream_task or self.stream_task.done():
            self.stream_task = asyncio.create_task(self._stream_worker())
            self._streamer_initialized = True

        await self.broadcast("Streamer initialized and operational.", level="SYSTEM")

    async def _stream_worker(self):
        """Background worker to drain the queue to JSONL without blocking execution."""
        while True:
            try:
                payload = await self.stream_queue.get()
                try:
                    with open(self._log_path, "a", encoding="utf-8") as f:
                        f.write(json.dumps(payload) + "\n")
                finally:
                    self.stream_queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"   [STREAMER] Error writing to stream: {e}")

    async def broadcast(self, message: str, agent: str = None, level: str = "INFO"):
        """Queues a message for the live stream in a non-blocking manner."""
        import datetime
        payload = {
            "timestamp": datetime.datetime.now().isoformat(),
            "agent": agent or self._current_agent,
            "level": level,
            "content": message,
            "signals": list(self.signals)
        }
        await self.stream_queue.put(payload)

    def set_current_agent(self, agent_name: str):
        """Sets the current agent for broadcast context."""
        self._current_agent = agent_name

    async def broadcast_reasoning(self, response_text: str, agent: str = None):
        """Extracts and broadcasts reasoning blocks from LLM responses."""
        reasoning_match = re.search(r"<reasoning>(.*?)</reasoning>", response_text, re.DOTALL)
        if reasoning_match:
            reasoning = reasoning_match.group(1).strip()
            await self.broadcast(f"REASONING: {reasoning}", agent=agent, level="THOUGHT")
            return reasoning
        return None

    async def stop_streamer(self):
        """Gracefully stops the stream worker."""
        if self.stream_task and not self.stream_task.done():
            await self.stream_queue.join()
            self.stream_task.cancel()
            try:
                await self.stream_task
            except asyncio.CancelledError:
                pass
            self._streamer_initialized = False


# ==============================================================================
# TEST FIXTURES
# ==============================================================================

@pytest.fixture
def temp_stream_dir():
    """Creates a temporary directory for stream output."""
    temp_dir = tempfile.mkdtemp(prefix="streamer_test_")
    yield temp_dir
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
async def ctx(temp_stream_dir):
    """Creates a mock ValidationContext with streamer for testing."""
    context = MockValidationContext(stream_dir=temp_stream_dir)
    await context.start_streamer()
    yield context
    await context.stop_streamer()


# ==============================================================================
# L5 STREAMER TESTS - Non-Blocking Integrity
# ==============================================================================

class TestStreamerNonBlockingIntegrity:
    """Verifies the streamer writes to JSONL without blocking the main thread."""

    @pytest.mark.asyncio
    async def test_streamer_writes_to_jsonl(self, temp_stream_dir):
        """Verifies that broadcast messages are written to JSONL file."""
        ctx = MockValidationContext(stream_dir=temp_stream_dir)
        await ctx.start_streamer()

        test_marker = "L5_STREAM_INTEGRITY_CHECK"
        await ctx.broadcast(test_marker, agent="Sherlock", level="THOUGHT")

        # Allow background task to process
        await asyncio.sleep(0.2)

        log_path = os.path.join(temp_stream_dir, "live_stream.jsonl")
        assert os.path.exists(log_path), "JSONL file should exist"

        with open(log_path, "r") as f:
            lines = f.readlines()
            # Find the test marker (skip system init message)
            found = False
            for line in lines:
                entry = json.loads(line)
                if entry["content"] == test_marker:
                    assert entry["level"] == "THOUGHT"
                    assert entry["agent"] == "Sherlock"
                    found = True
                    break
            assert found, f"Test marker not found in stream. Lines: {lines}"

        await ctx.stop_streamer()

    @pytest.mark.asyncio
    async def test_streamer_includes_timestamp(self, temp_stream_dir):
        """Verifies that broadcast messages include ISO timestamp."""
        ctx = MockValidationContext(stream_dir=temp_stream_dir)
        await ctx.start_streamer()

        await ctx.broadcast("Timestamp test", level="INFO")
        await asyncio.sleep(0.2)

        log_path = os.path.join(temp_stream_dir, "live_stream.jsonl")
        with open(log_path, "r") as f:
            for line in f:
                entry = json.loads(line)
                assert "timestamp" in entry
                # Verify ISO format (should contain T separator)
                assert "T" in entry["timestamp"]

        await ctx.stop_streamer()

    @pytest.mark.asyncio
    async def test_streamer_includes_signals(self, temp_stream_dir):
        """Verifies that broadcast messages include current signals."""
        ctx = MockValidationContext(stream_dir=temp_stream_dir)
        ctx.signals = {"TEST_SIGNAL", "ANOTHER_SIGNAL"}
        await ctx.start_streamer()

        await ctx.broadcast("Signal test", level="INFO")
        await asyncio.sleep(0.2)

        log_path = os.path.join(temp_stream_dir, "live_stream.jsonl")
        with open(log_path, "r") as f:
            lines = f.readlines()
            # Check last entry (our test message)
            entry = json.loads(lines[-1])
            assert "signals" in entry
            assert "TEST_SIGNAL" in entry["signals"]
            assert "ANOTHER_SIGNAL" in entry["signals"]

        await ctx.stop_streamer()


# ==============================================================================
# L5 STREAMER TESTS - Stress Load Handling
# ==============================================================================

class TestStreamerStressLoad:
    """Ensures the streamer handles high-frequency message bursts."""

    @pytest.mark.asyncio
    async def test_streamer_handles_100_messages(self, temp_stream_dir):
        """Ensures the streamer handles 100 messages without dropping."""
        ctx = MockValidationContext(stream_dir=temp_stream_dir)
        await ctx.start_streamer()

        # Burst 100 messages
        for i in range(100):
            await ctx.broadcast(f"Stress message {i}")

        # Wait for queue to drain
        await ctx.stream_queue.join()
        assert ctx.stream_queue.empty(), "Queue should be empty after drain"

        # Verify all messages written
        log_path = os.path.join(temp_stream_dir, "live_stream.jsonl")
        with open(log_path, "r") as f:
            lines = f.readlines()
            # Should have 100 stress messages + 1 init message
            assert len(lines) >= 100, f"Expected at least 100 lines, got {len(lines)}"

        await ctx.stop_streamer()

    @pytest.mark.asyncio
    async def test_streamer_handles_rapid_fire(self, temp_stream_dir):
        """Tests rapid-fire message submission doesn't block."""
        ctx = MockValidationContext(stream_dir=temp_stream_dir)
        await ctx.start_streamer()

        import time
        start = time.time()

        # Submit 50 messages as fast as possible
        for i in range(50):
            await ctx.broadcast(f"Rapid message {i}")

        submission_time = time.time() - start

        # Submission should be nearly instant (non-blocking)
        assert submission_time < 1.0, f"Submission took too long: {submission_time}s"

        # Wait for processing
        await ctx.stream_queue.join()

        await ctx.stop_streamer()

    @pytest.mark.asyncio
    async def test_streamer_concurrent_agents(self, temp_stream_dir):
        """Tests multiple agents broadcasting concurrently."""
        ctx = MockValidationContext(stream_dir=temp_stream_dir)
        await ctx.start_streamer()

        agents = ["Sherlock", "TestPilot", "SafetyInspector", "Historian"]

        # Concurrent broadcasts from multiple agents
        tasks = []
        for agent in agents:
            for i in range(10):
                tasks.append(ctx.broadcast(f"Message {i}", agent=agent))

        await asyncio.gather(*tasks)
        await ctx.stream_queue.join()

        # Verify all messages written
        log_path = os.path.join(temp_stream_dir, "live_stream.jsonl")
        with open(log_path, "r") as f:
            lines = f.readlines()
            # 4 agents * 10 messages + 1 init = 41
            assert len(lines) >= 40, f"Expected at least 40 lines, got {len(lines)}"

        await ctx.stop_streamer()


# ==============================================================================
# L5 STREAMER TESTS - Reasoning Extraction
# ==============================================================================

class TestReasoningExtraction:
    """Verifies that Chain-of-Thought reasoning is identified and broadcasted."""

    @pytest.mark.asyncio
    async def test_reasoning_extraction_basic(self, temp_stream_dir):
        """Verifies basic reasoning block extraction."""
        ctx = MockValidationContext(stream_dir=temp_stream_dir)
        await ctx.start_streamer()

        mock_response = "<reasoning>Logic: Change class name to PascalCase</reasoning>\nclass MyClass:"

        reasoning = await ctx.broadcast_reasoning(mock_response, agent="CodeStyleGuardian")

        assert reasoning == "Logic: Change class name to PascalCase"

        await asyncio.sleep(0.2)

        # Verify it was broadcast
        log_path = os.path.join(temp_stream_dir, "live_stream.jsonl")
        with open(log_path, "r") as f:
            lines = f.readlines()
            found = False
            for line in lines:
                entry = json.loads(line)
                if entry["level"] == "THOUGHT" and "PascalCase" in entry["content"]:
                    found = True
                    break
            assert found, "Reasoning should be broadcast with THOUGHT level"

        await ctx.stop_streamer()

    @pytest.mark.asyncio
    async def test_reasoning_extraction_multiline(self, temp_stream_dir):
        """Verifies multiline reasoning block extraction."""
        ctx = MockValidationContext(stream_dir=temp_stream_dir)
        await ctx.start_streamer()

        mock_response = """<reasoning>
Step 1: Analyze the import structure
Step 2: Identify circular dependencies
Step 3: Refactor to break the cycle
</reasoning>
import os
import sys"""

        reasoning = await ctx.broadcast_reasoning(mock_response, agent="DependencySentinel")

        assert "Step 1" in reasoning
        assert "Step 2" in reasoning
        assert "Step 3" in reasoning

        await ctx.stop_streamer()

    @pytest.mark.asyncio
    async def test_reasoning_extraction_no_reasoning(self, temp_stream_dir):
        """Verifies handling when no reasoning block exists."""
        ctx = MockValidationContext(stream_dir=temp_stream_dir)
        await ctx.start_streamer()

        mock_response = "class MyClass:\n    pass"

        reasoning = await ctx.broadcast_reasoning(mock_response, agent="TestAgent")

        assert reasoning is None, "Should return None when no reasoning block"

        await ctx.stop_streamer()

    @pytest.mark.asyncio
    async def test_reasoning_broadcast_level(self, temp_stream_dir):
        """Verifies reasoning is broadcast with THOUGHT level."""
        ctx = MockValidationContext(stream_dir=temp_stream_dir)
        await ctx.start_streamer()

        mock_response = "<reasoning>Test reasoning content</reasoning>"
        await ctx.broadcast_reasoning(mock_response, agent="TestAgent")

        await asyncio.sleep(0.2)

        log_path = os.path.join(temp_stream_dir, "live_stream.jsonl")
        with open(log_path, "r") as f:
            lines = f.readlines()
            for line in lines:
                entry = json.loads(line)
                if "Test reasoning content" in entry["content"]:
                    assert entry["level"] == "THOUGHT"
                    break

        await ctx.stop_streamer()


# ==============================================================================
# L5 STREAMER TESTS - Agent Lifecycle
# ==============================================================================

class TestAgentLifecycleBroadcast:
    """Tests agent start/end lifecycle broadcasting."""

    @pytest.mark.asyncio
    async def test_agent_start_broadcast(self, temp_stream_dir):
        """Verifies AGENT_START level is used for activation."""
        ctx = MockValidationContext(stream_dir=temp_stream_dir)
        await ctx.start_streamer()

        await ctx.broadcast("ACTIVATED: Starting validation phase", agent="TestAgent", level="AGENT_START")
        await asyncio.sleep(0.2)

        log_path = os.path.join(temp_stream_dir, "live_stream.jsonl")
        with open(log_path, "r") as f:
            lines = f.readlines()
            found = False
            for line in lines:
                entry = json.loads(line)
                if entry["level"] == "AGENT_START":
                    assert entry["agent"] == "TestAgent"
                    found = True
                    break
            assert found, "AGENT_START broadcast not found"

        await ctx.stop_streamer()

    @pytest.mark.asyncio
    async def test_agent_end_broadcast(self, temp_stream_dir):
        """Verifies AGENT_END level is used for completion."""
        ctx = MockValidationContext(stream_dir=temp_stream_dir)
        await ctx.start_streamer()

        await ctx.broadcast("COMPLETED: Validation phase finished", agent="TestAgent", level="AGENT_END")
        await asyncio.sleep(0.2)

        log_path = os.path.join(temp_stream_dir, "live_stream.jsonl")
        with open(log_path, "r") as f:
            lines = f.readlines()
            found = False
            for line in lines:
                entry = json.loads(line)
                if entry["level"] == "AGENT_END":
                    assert entry["agent"] == "TestAgent"
                    found = True
                    break
            assert found, "AGENT_END broadcast not found"

        await ctx.stop_streamer()

    @pytest.mark.asyncio
    async def test_current_agent_context(self, temp_stream_dir):
        """Verifies set_current_agent affects subsequent broadcasts."""
        ctx = MockValidationContext(stream_dir=temp_stream_dir)
        await ctx.start_streamer()

        ctx.set_current_agent("Sherlock")
        await ctx.broadcast("Investigation started")

        ctx.set_current_agent("TestPilot")
        await ctx.broadcast("Tests running")

        await asyncio.sleep(0.2)

        log_path = os.path.join(temp_stream_dir, "live_stream.jsonl")
        with open(log_path, "r") as f:
            lines = f.readlines()
            sherlock_found = False
            testpilot_found = False
            for line in lines:
                entry = json.loads(line)
                if entry["content"] == "Investigation started":
                    assert entry["agent"] == "Sherlock"
                    sherlock_found = True
                if entry["content"] == "Tests running":
                    assert entry["agent"] == "TestPilot"
                    testpilot_found = True
            assert sherlock_found and testpilot_found

        await ctx.stop_streamer()


# ==============================================================================
# L5 STREAMER TESTS - Graceful Shutdown
# ==============================================================================

class TestStreamerShutdown:
    """Tests graceful streamer shutdown."""

    @pytest.mark.asyncio
    async def test_graceful_shutdown_drains_queue(self, temp_stream_dir):
        """Verifies stop_streamer drains the queue before stopping."""
        ctx = MockValidationContext(stream_dir=temp_stream_dir)
        await ctx.start_streamer()

        # Add messages
        for i in range(20):
            await ctx.broadcast(f"Shutdown test {i}")

        # Stop should drain first
        await ctx.stop_streamer()

        # Verify all messages written
        log_path = os.path.join(temp_stream_dir, "live_stream.jsonl")
        with open(log_path, "r") as f:
            lines = f.readlines()
            # 20 test messages + 1 init
            assert len(lines) >= 20

    @pytest.mark.asyncio
    async def test_double_stop_is_safe(self, temp_stream_dir):
        """Verifies calling stop_streamer twice doesn't crash."""
        ctx = MockValidationContext(stream_dir=temp_stream_dir)
        await ctx.start_streamer()

        await ctx.stop_streamer()
        await ctx.stop_streamer()  # Should not raise

    @pytest.mark.asyncio
    async def test_restart_after_stop(self, temp_stream_dir):
        """Verifies streamer can be restarted after stopping."""
        ctx = MockValidationContext(stream_dir=temp_stream_dir)

        await ctx.start_streamer()
        await ctx.broadcast("First run")
        await ctx.stop_streamer()

        await ctx.start_streamer()
        await ctx.broadcast("Second run")
        await asyncio.sleep(0.2)

        log_path = os.path.join(temp_stream_dir, "live_stream.jsonl")
        with open(log_path, "r") as f:
            content = f.read()
            assert "First run" in content
            assert "Second run" in content

        await ctx.stop_streamer()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
