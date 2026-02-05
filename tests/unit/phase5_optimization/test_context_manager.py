"""
Phase 5 Optimization Tests - Context Manager
Tests for LLM context management utilities.
"""

import pytest
from apps_shared.llm.context_manager import ContextManager, ContextWindow


class TestContextWindow:
    """Test ContextWindow dataclass."""

    def test_context_window_creation(self):
        """Test creating ContextWindow."""
        window = ContextWindow(
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=4000,
            current_tokens=100,
            metadata={},
        )

        assert len(window.messages) == 1
        assert window.max_tokens == 4000
        assert window.current_tokens == 100


class TestContextManager:
    """Test ContextManager functionality."""

    def test_initialization(self):
        """Test context manager initialization."""
        manager = ContextManager(max_tokens=2000)

        assert manager.max_tokens == 2000
        assert len(manager.messages) == 0

    def test_set_system_message(self):
        """Test setting system message."""
        manager = ContextManager()
        manager.set_system_message("You are helpful")

        assert manager.system_message == "You are helpful"

    def test_add_message(self):
        """Test adding message."""
        manager = ContextManager()
        manager.add_message("user", "Hello")

        assert len(manager.messages) == 1
        assert manager.messages[0]["role"] == "user"
        assert manager.messages[0]["content"] == "Hello"

    def test_add_multiple_messages(self):
        """Test adding multiple messages."""
        manager = ContextManager()
        manager.add_message("user", "Hello")
        manager.add_message("assistant", "Hi there")
        manager.add_message("user", "How are you?")

        assert len(manager.messages) == 3

    def test_get_context_window_no_system(self):
        """Test getting context window without system message."""
        manager = ContextManager()
        manager.add_message("user", "Test")

        window = manager.get_context_window()

        assert len(window.messages) == 1
        assert window.messages[0]["role"] == "user"

    def test_get_context_window_with_system(self):
        """Test getting context window with system message."""
        manager = ContextManager()
        manager.set_system_message("System")
        manager.add_message("user", "Test")

        window = manager.get_context_window()

        assert len(window.messages) == 2
        assert window.messages[0]["role"] == "system"
        assert window.messages[1]["role"] == "user"

    def test_trim_context_within_limit(self):
        """Test trimming context within limit."""
        manager = ContextManager()
        for i in range(5):
            manager.add_message("user", f"Message {i}")

        manager.trim_context(keep_recent=10)

        assert len(manager.messages) == 5

    def test_trim_context_exceeds_limit(self):
        """Test trimming context that exceeds limit."""
        manager = ContextManager()
        for i in range(15):
            manager.add_message("user", f"Message {i}")

        manager.trim_context(keep_recent=5)

        assert len(manager.messages) == 5
        # Should keep most recent
        assert "Message 14" in manager.messages[-1]["content"]

    def test_compress_context_few_messages(self):
        """Test compressing context with few messages."""
        manager = ContextManager()
        for i in range(3):
            manager.add_message("user", f"Message {i}")

        manager.compress_context()

        # Should not compress with only 3 messages
        assert len(manager.messages) == 3

    def test_compress_context_many_messages(self):
        """Test compressing context with many messages."""
        manager = ContextManager()
        for i in range(10):
            manager.add_message("user", f"Message {i}")

        manager.compress_context()

        # Should compress to first 2 + summary + last 2
        assert len(manager.messages) == 5
        # Check for summary message
        assert any("summarized" in msg["content"] for msg in manager.messages)

    def test_clear_context(self):
        """Test clearing context."""
        manager = ContextManager()
        manager.add_message("user", "Test")
        manager.add_message("assistant", "Response")

        manager.clear_context()

        assert len(manager.messages) == 0

    def test_estimate_tokens(self):
        """Test token estimation."""
        manager = ContextManager()
        text = "A" * 100

        tokens = manager.estimate_tokens(text)

        assert tokens == 25  # 100 / 4

    def test_fits_in_context_true(self):
        """Test checking if text fits in context."""
        manager = ContextManager(max_tokens=1000)
        manager.add_message("user", "Short message")

        fits = manager.fits_in_context("Additional short text")

        assert fits is True

    def test_fits_in_context_false(self):
        """Test checking if text doesn't fit in context."""
        manager = ContextManager(max_tokens=100)
        manager.add_message("user", "A" * 300)

        fits = manager.fits_in_context("A" * 200)

        assert fits is False

    def test_get_remaining_tokens(self):
        """Test getting remaining tokens."""
        manager = ContextManager(max_tokens=1000)
        manager.add_message("user", "A" * 100)  # ~25 tokens

        remaining = manager.get_remaining_tokens()

        assert remaining > 0
        assert remaining < 1000

    def test_create_conversation_context(self):
        """Test creating conversation context."""
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"},
        ]

        window = ContextManager.create_conversation_context(messages, max_tokens=2000)

        assert len(window.messages) == 2
        assert window.max_tokens == 2000
        assert window.current_tokens > 0

    def test_merge_contexts(self):
        """Test merging contexts."""
        ctx1 = ContextWindow(
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=1000,
            current_tokens=10,
            metadata={},
        )
        ctx2 = ContextWindow(
            messages=[{"role": "assistant", "content": "Hi"}],
            max_tokens=1000,
            current_tokens=5,
            metadata={},
        )

        merged = ContextManager.merge_contexts([ctx1, ctx2])

        assert len(merged.messages) == 2
        assert merged.current_tokens == 15

    def test_prioritize_messages_within_limit(self):
        """Test prioritizing messages within limit."""
        messages = [
            {"role": "system", "content": "System"},
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi"},
        ]

        result = ContextManager.prioritize_messages(messages, max_tokens=1000)

        assert len(result) == 3

    def test_prioritize_messages_exceeds_limit(self):
        """Test prioritizing messages that exceed limit."""
        messages = [
            {"role": "system", "content": "System"},
            {"role": "user", "content": "A" * 100},
            {"role": "assistant", "content": "B" * 100},
            {"role": "user", "content": "C" * 100},
        ]

        result = ContextManager.prioritize_messages(messages, max_tokens=50)

        # Should keep system message and as many recent as fit
        assert any(msg["role"] == "system" for msg in result)
        assert len(result) < len(messages)

    def test_prioritize_messages_empty(self):
        """Test prioritizing empty messages."""
        result = ContextManager.prioritize_messages([], max_tokens=1000)

        assert result == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
