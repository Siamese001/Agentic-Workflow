"""
Context Manager - Phase 5 Optimization
LLM context management utilities for high-reasoning agents.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Any


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

@dataclass
class ContextWindow:
    """Represents a context window for LLM."""

    messages: list[dict[str, str]]
    max_tokens: int
    current_tokens: int
    metadata: dict[str, Any]


class ContextManager:
    """LLM context management utilities."""

    def __init__(self, max_tokens: int = 4000):
        """
        Initialize context manager.

        Args:
            max_tokens: Maximum token limit for context
        """
        self.max_tokens = max_tokens
        self.messages: deque = deque()
        self.system_message: str | None = None

    def set_system_message(self, message: str) -> None:
        """
        Set system message.

        Args:
            message: System message
        """
        self.system_message = message

    def add_message(self, role: str, content: str) -> None:
        """
        Add message to context.

        Args:
            role: Message role (user/assistant/system)
            content: Message content
        """
        self.messages.append({"role": role, "content": content})

    def get_context_window(self) -> ContextWindow:
        """
        Get current context window.

        Returns:
            ContextWindow with messages and token info
        """
        messages = []

        # Add system message if set
        if self.system_message:
            messages.append({"role": "system", "content": self.system_message})

        # Add conversation messages
        messages.extend(list(self.messages))

        # Estimate tokens
        total_content = "".join(msg["content"] for msg in messages)
        current_tokens = len(total_content) // 4

        return ContextWindow(
            messages=messages,
            max_tokens=self.max_tokens,
            current_tokens=current_tokens,
            metadata={"message_count": len(messages)},
        )

    def trim_context(self, keep_recent: int = 10) -> None:
        """
        Trim context to keep only recent messages.

        Args:
            keep_recent: Number of recent messages to keep
        """
        if len(self.messages) > keep_recent:
            # Keep only the most recent messages
            self.messages = deque(list(self.messages)[-keep_recent:], maxlen=keep_recent)

    def compress_context(self) -> None:
        """Compress context by summarizing older messages."""
        if len(self.messages) <= 5:
            return

        # Keep first and last 2 messages, summarize middle
        first_messages = list(self.messages)[:2]
        last_messages = list(self.messages)[-2:]
        middle_count = len(self.messages) - 4

        # Create summary message
        summary = {
            "role": "system",
            "content": f"[{middle_count} messages summarized for context efficiency]",
        }

        # Rebuild messages
        self.messages = deque(first_messages + [summary] + last_messages)

    def clear_context(self) -> None:
        """Clear all messages from context."""
        self.messages.clear()

    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text.

        Args:
            text: Text to estimate

        Returns:
            Estimated token count
        """
        # Rough estimation: 1 token ≈ 4 characters
        return len(text) // 4

    def fits_in_context(self, additional_text: str) -> bool:
        """
        Check if additional text fits in context window.

        Args:
            additional_text: Text to check

        Returns:
            True if fits, False otherwise
        """
        current_window = self.get_context_window()
        additional_tokens = self.estimate_tokens(additional_text)

        return (current_window.current_tokens + additional_tokens) <= self.max_tokens

    def get_remaining_tokens(self) -> int:
        """
        Get remaining tokens in context window.

        Returns:
            Number of remaining tokens
        """
        current_window = self.get_context_window()
        return self.max_tokens - current_window.current_tokens

    @staticmethod
    def create_conversation_context(
        messages: list[dict[str, str]],
        max_tokens: int = 4000,
    ) -> ContextWindow:
        """
        Create context window from messages.

        Args:
            messages: List of message dictionaries
            max_tokens: Maximum token limit

        Returns:
            ContextWindow instance
        """
        total_content = "".join(msg.get("content", "") for msg in messages)
        current_tokens = len(total_content) // 4

        return ContextWindow(
            messages=messages,
            max_tokens=max_tokens,
            current_tokens=current_tokens,
            metadata={"message_count": len(messages)},
        )

    @staticmethod
    def merge_contexts(contexts: list[ContextWindow]) -> ContextWindow:
        """
        Merge multiple context windows.

        Args:
            contexts: List of ContextWindow instances

        Returns:
            Merged ContextWindow
        """
        all_messages = []
        total_tokens = 0

        for ctx in contexts:
            all_messages.extend(ctx.messages)
            total_tokens += ctx.current_tokens

        max_tokens = max(ctx.max_tokens for ctx in contexts)

        return ContextWindow(
            messages=all_messages,
            max_tokens=max_tokens,
            current_tokens=total_tokens,
            metadata={"merged_count": len(contexts)},
        )

    @staticmethod
    def prioritize_messages(
        messages: list[dict[str, str]],
        max_tokens: int,
    ) -> list[dict[str, str]]:
        """
        Prioritize messages to fit within token limit.

        Args:
            messages: List of messages
            max_tokens: Maximum token limit

        Returns:
            Prioritized list of messages
        """
        if not messages:
            return []

        # Always keep system messages
        system_messages = [msg for msg in messages if msg.get("role") == "system"]
        other_messages = [msg for msg in messages if msg.get("role") != "system"]

        # Estimate tokens
        system_tokens = sum(len(msg.get("content", "")) // 4 for msg in system_messages)
        remaining_tokens = max_tokens - system_tokens

        # Add messages from most recent until we hit limit
        prioritized = system_messages.copy()
        current_tokens = system_tokens

        for msg in reversed(other_messages):
            msg_tokens = len(msg.get("content", "")) // 4
            if current_tokens + msg_tokens <= remaining_tokens:
                prioritized.insert(len(system_messages), msg)
                current_tokens += msg_tokens
            else:
                break

        return prioritized
