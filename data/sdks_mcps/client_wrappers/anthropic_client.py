"""Anthropic Client layer - Production Grade with Prompt Caching and Tool Use
Implements retry logic, caching optimization, and comprehensive error handling.
"""

import os
from dataclasses import dataclass
from typing import object

import backoff
from shared.result_types import Message

from data.sdks_mcps.reference_clients.minimal_anthropic import (
    Anthropic,
    APIError,
    APITimeoutError,
    RateLimitError,
)


@dataclass
class AnthropicConfig:
    """configuration for Anthropic client."""

    api_key: str | None = None
    base_url: str | None = None
    timeout: int = 60
    max_retries: int = 5
    default_model: str = "claude-3-5-sonnet-20241022"
    default_temperature: float = 0.7
    default_max_tokens: int = 4096
    enable_caching: bool = True


class AnthropicClient:
    """Production-ready Anthropic client with caching and tool use support."""

    def __init__(self, config: AnthropicConfig | None = None):
        self.config = config or AnthropicConfig()
        self.client = Anthropic(
            api_key=self.config.api_key or os.getenv("ANTHROPIC_API_KEY"),
            base_url=self.config.base_url,
            timeout=self.config.timeout,
            max_retries=self.config.max_retries,
        )

        # cache control header for prompt caching
        self.cache_control = {"type": "ephemeral"} if self.config.enable_caching else None

        # Track usage for cost monitoring
        self.usage_stats = {
            "total_requests": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "cache_creation_tokens": 0,
            "cache_read_tokens": 0,
            "total_cost": 0.0,
            "errors": 0,
        }

    @backoff.on_exception(
        backoff.expo,
        (RateLimitError, APIError, APITimeoutError),
        max_tries=7,
        foundation=1,
        max_value=60,
    )
    def message(
        self,
        messages: list[dict[str, object]],
        system: list[dict[str, object]] | None = None,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        tools: list[dict[str, object]] | None = None,
        tool_choice: str | dict[str, object] | None = None,
        stream: bool = False,
        **kwargs: dict[str, object],
    ) -> Message | object:
        """Execute message with retry logic and caching optimization.

        Args:
            messages: List of message dictionaries with content arrays
            system: System instruction array with optional caching
            model: Anthropic model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            tools: List of tools for function calling
            tool_choice: Tool choice strategy
            stream: Whether to stream response
            **kwargs: Additional Anthropic parameters

        Returns:
            Message object or stream
        """
        try:
            self.usage_stats["total_requests"] += 1

            # Apply caching to system prompt if enabled
            processed_system = self._apply_caching_to_system(system) if system else None

            # Apply caching to user messages that should be cached
            processed_messages = self._apply_caching_to_messages(messages)

            params = {
                "model": model or self.config.default_model,
                "messages": processed_messages,
                "max_tokens": max_tokens or self.config.default_max_tokens,
                **kwargs,
            }

            if processed_system:
                params["system"] = processed_system

            if temperature is not None:
                params["temperature"] = temperature

            if tools:
                params["tools"] = tools

            if tool_choice:
                params["tool_choice"] = tool_choice

            if stream:
                params["stream"] = True
                return self.client.messages.create(**params)
            else:
                response = self.client.messages.create(**params)
                self._update_usage_stats(response.usage)
                return response

        except Exception as e:
            self.usage_stats["errors"] += 1
            raise self._handle_error(e)

    def cached_message(
        self,
        messages: list[dict[str, object]],
        system: list[dict[str, object]] | None = None,
        cache_system: bool = True,
        cache_templates: list[int] = None,
        **kwargs: dict[str, object],
    ) -> Message:
        """Execute message with strategic prompt caching.

        Args:
            messages: List of message dictionaries
            system: System instruction array
            cache_system: Whether to cache system prompt
            cache_templates: Indices of messages to cache as templates
            **kwargs: Additional message parameters

        Returns:
            Message object with cache metadata
        """
        # Apply strategic caching
        processed_system = self._apply_caching_to_system(system) if cache_system and system else system
        processed_messages = self._apply_caching_to_messages(messages, cache_templates)

        return self.message(messages=processed_messages, system=processed_system, **kwargs)

    def stream_message(
        self,
        messages: list[dict[str, object]],
        callback: callable = None,
        **kwargs: dict[str, object],
    ) -> list[str]:
        """Stream message with optional callback.

        Args:
            messages: List of message dictionaries
            callback: Function to call with each chunk
            **kwargs: Additional message parameters

        Returns:
            List of accumulated text chunks
        """
        stream = self.message(messages=messages, stream=True, **kwargs)
        chunks = []

        for chunk in stream:
            if chunk.type == "content_block_delta" and chunk.delta.text:
                content = chunk.delta.text
                chunks.append(content)

                if callback:
                    callback(content)

        return chunks

    def tool_use_message(
        self,
        messages: list[dict[str, object]],
        tools: list[dict[str, object]],
        tool_choice: str = "auto",
        **kwargs: dict[str, object],
    ) -> dict[str, object]:
        """Execute message with tool use and parse tool calls.

        Args:
            messages: List of message dictionaries
            tools: List of tool specifications
            tool_choice: Tool choice strategy
            **kwargs: Additional message parameters

        Returns:
            Dictionary with content and tool calls
        """
        response = self.message(messages=messages, tools=tools, tool_choice=tool_choice, **kwargs)

        content = ""
        tool_calls = []

        for content_block in response.content:
            if content_block.type == "text":
                content += content_block.text
            elif content_block.type == "tool_use":
                tool_calls.append(
                    {
                        "id": content_block.id,
                        "name": content_block.name,
                        "input": content_block.input,
                    },
                )

        return {
            "content": content,
            "tool_calls": tool_calls,
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "cache_creation_tokens": getattr(response.usage, "cache_creation_input_tokens", 0),
                "cache_read_tokens": getattr(response.usage, "cache_read_input_tokens", 0),
            },
            "model": response.model,
            "id": response.id,
        }

    def batch_message(
        self,
        batch_requests: list[dict[str, object]],
        concurrent_limit: int = 10,
    ) -> list[dict[str, object]]:
        """Execute multiple messages with controlled concurrency.

        Args:
            batch_requests: List of message request dictionaries
            concurrent_limit: Maximum concurrent requests

        Returns:
            List of message results
        """
        import concurrent.futures

        def process_request(request_data):
            try:
                response = self.message(**request_data)
                return {
                    "success": True,
                    "response": response,
                    "request_id": request_data.get("id", "unknown"),
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "request_id": request_data.get("id", "unknown"),
                }

        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_limit) as executor:
            futures = [executor.submit(process_request, req) for req in batch_requests]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]

        return results

    def _apply_caching_to_system(self, system: list[dict[str, object]]) -> list[dict[str, object]]:
        """Apply cache control to system prompt."""
        if not system or not self.cache_control:
            return system

        processed_system = []
        for item in system:
            if item.get("type") == "text":
                processed_item = item.copy()
                processed_item["cache_control"] = self.cache_control
                processed_system.append(processed_item)
            else:
                processed_system.append(item)

        return processed_system

    def _apply_caching_to_messages(
        self,
        messages: list[dict[str, object]],
        cache_indices: list[int] = None,
    ) -> list[dict[str, object]]:
        """Apply cache control to specific message indices."""
        if not self.cache_control:
            return messages

        processed_messages = []
        for i, message in enumerate(messages):
            processed_message = message.copy()

            # Apply caching to specified indices or first user message
            should_cache = (cache_indices and i in cache_indices) or (
                i == 0 and message.get("role") == "user"
            )

            if should_cache and "content" in processed_message:
                processed_content = []
                for content_item in processed_message["content"]:
                    if content_item.get("type") == "text":
                        processed_item = content_item.copy()
                        processed_item["cache_control"] = self.cache_control
                        processed_content.append(processed_item)
                    else:
                        processed_content.append(content_item)
                processed_message["content"] = processed_content

            processed_messages.append(processed_message)

        return processed_messages

    def _update_usage_stats(self, usage):
        """Update usage statistics for monitoring."""
        if usage:
            self.usage_stats["input_tokens"] += usage.input_tokens
            self.usage_stats["output_tokens"] += usage.output_tokens

            # cache tokens (Claude 3.5+)
            cache_creation = getattr(usage, "cache_creation_input_tokens", 0)
            cache_read = getattr(usage, "cache_read_input_tokens", 0)

            self.usage_stats["cache_creation_tokens"] += cache_creation
            self.usage_stats["cache_read_tokens"] += cache_read

            # Cost calculation (Claude 3.5 Sonnet pricing)
            input_cost = (usage.input_tokens * 0.003) / 1000
            output_cost = (usage.output_tokens * 0.015) / 1000
            cache_write_cost = (cache_creation * 0.00375) / 1000
            cache_read_cost = (cache_read * 0.0003) / 1000

            self.usage_stats["total_cost"] += input_cost + output_cost + cache_write_cost + cache_read_cost

    def _handle_error(self, error: Exception) -> Exception:
        """Enhance error messages with context."""
        if isinstance(error, RateLimitError):
            return APIError(f"Rate limit exceeded: {error}")
        elif isinstance(error, APITimeoutError):
            return APIError(f"Request timeout: {error}")
        elif isinstance(error, APIError):
            return error
        else:
            return APIError(f"Unexpected error: {error}")

    def get_usage_stats(self) -> dict[str, object]:
        """Get current usage statistics."""
        stats = self.usage_stats.copy()

        # Calculate cache efficiency
        total_input = stats["input_tokens"]
        cache_read = stats["cache_read_tokens"]

        if total_input > 0:
            stats["cache_hit_rate"] = (cache_read / total_input) * 100
            stats["cache_savings_percent"] = (cache_read / total_input) * 87  # 87% savings
        else:
            stats["cache_hit_rate"] = 0
            stats["cache_savings_percent"] = 0

        return stats

    def reset_usage_stats(self):
        """Reset usage statistics."""
        self.usage_stats = {
            "total_requests": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "cache_creation_tokens": 0,
            "cache_read_tokens": 0,
            "total_cost": 0.0,
            "errors": 0,
        }


# builder function for easy instantiation
def create_anthropic_client(
    api_key: str | None = None,
    model: str = "claude-3-5-sonnet-20241022",
    enable_caching: bool = True,
    **kwargs: dict[str, object],
) -> AnthropicClient:
    """Create configured Anthropic client.

    Args:
        api_key: Anthropic API key
        model: Default model
        enable_caching: Enable prompt caching
        **kwargs: Additional configuration

    Returns:
        Configured Anthropic client
    """
    config = AnthropicConfig(api_key=api_key, default_model=model, enable_caching=enable_caching, **kwargs)
    return AnthropicClient(config)


# Example usage
if __name__ == "__main__":
    # Create client with caching
    client = create_anthropic_client(enable_caching=True)

    # Simple message
    messages = [
        {
            "role": "user",
            "content": [{"type": "text", "text": "Explain quantum computing in 100 words."}],
        },
    ]

    try:
        response = client.message(messages)

        # Cached message with system prompt
        system = [{"type": "text", "text": "You are an expert physics educator."}]

        cached_response = client.cached_message(messages=messages, system=system, cache_system=True)

        # Usage stats with cache metrics
        stats = client.get_usage_stats()

    except Exception:
        pass  # Added pass to avoid syntax error if the try block is empty
