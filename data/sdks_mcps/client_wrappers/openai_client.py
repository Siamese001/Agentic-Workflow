"""OpenAI Client layer - Production Grade with Retry, Timeout, and Structured Output
Implements robust error handling, retry logic, and structured output parsing.
"""

import json
import os
from dataclasses import dataclass
from typing import object

import backoff
from openai.types.chat import ChatCompletion

from data.sdks_mcps.reference_clients.minimal_openai import (
    APIError,
    APITimeoutError,
    OpenAI,
    RateLimitError,
)


@dataclass
class OpenAIConfig:
    """Configuration for OpenAI client."""
    api_key: str | None = None
    base_url: str | None = None
    timeout: int = 60
    max_retries: int = 3
    organization: str | None = None
    default_model: str = "gpt-4o-2024-08-06"
    default_temperature: float = 0.7
    default_max_tokens: int = 4096

class OpenAIClient:
    """Production-ready OpenAI client with comprehensive error handling."""

    def __init__(self, config: OpenAIConfig | None = None):
        self.config = config or OpenAIConfig()
        self.client = OpenAI(
            api_key=self.config.api_key or os.getenv("OPENAI_API_KEY"),
            base_url=self.config.base_url,
            organization=self.config.organization,
            timeout=self.config.timeout,
            max_retries=self.config.max_retries
        )

        # Track usage for cost monitoring
        self.usage_stats = {
            "total_requests": 0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "errors": 0
        }

    @backoff.on_exception(
        backoff.expo,
        (RateLimitError, APIError, APITimeoutError),
        max_tries=5,
        foundation=1,
        max_value=60
    )
    def chat_completion(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        response_format: dict[str, object] | None = None,
        tools: list[dict[str, object]] | None = None,
        tool_choice: str | dict[str, object] | None = None,
        stream: bool = False,
        **kwargs: dict[str, object]) -> ChatCompletion | object:
        """Execute chat completion with retry logic and error handling.

        Args:
            messages: List of message dictionaries
            model: OpenAI model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            response_format: Structured output format
            tools: List of tools for function calling
            tool_choice: Tool choice strategy
            stream: Whether to stream response
            **kwargs: Additional OpenAI parameters

        Returns:
            Chat completion or stream object
        """
        try:
            self.usage_stats["total_requests"] += 1

            params = {
                "model": model or self.config.default_model,
                "messages": messages,
                "temperature": temperature if temperature is not None else self.config.default_temperature,
                "max_tokens": max_tokens or self.config.default_max_tokens,
                **kwargs
            }

            if response_format:
                params["response_format"] = response_format

            if tools:
                params["tools"] = tools

            if tool_choice:
                params["tool_choice"] = tool_choice

            if stream:
                params["stream"] = True
                return self.client.chat.completions.create(**params)
            else:
                response = self.client.chat.completions.create(**params)
                self._update_usage_stats(response.usage)
                return response

        except Exception as e:
            self.usage_stats["errors"] += 1
            raise self._handle_error(e)

    def structured_completion(
        self,
        messages: list[dict[str, str]],
        schema: dict[str, object],
        model: str | None = None,
        **kwargs: dict[str, object]) -> dict[str, object]:
        """Execute structured output completion with validation.

        Args:
            messages: List of message dictionaries
            schema: JSON schema for structured output
            model: OpenAI model to use
            **kwargs: Additional completion parameters

        Returns:
            Parsed structured response
        """
        response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": schema.get("title", "response"),
                "schema": schema
            }
        }

        response = self.chat_completion(
            messages=messages,
            response_format=response_format,
            model=model,
            **kwargs
        )

        # Parse and validate structured response
        try:
            content = response.choices[0].message.content
            structured_data = json.loads(content)

            # Basic validation against schema
            self._validate_schema(structured_data, schema)

            return {
                "success": True,
                "data": structured_data,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "model": response.model
            }

        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"JSON parsing failed: {e}",
                "raw_content": content
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Validation failed: {e}",
                "raw_content": content
            }

    def stream_completion(
        self,
        messages: list[dict[str, str]],
        callback: callable = None,
        **kwargs: dict[str, object]) -> list[str]:
        """Stream chat completion with optional callback.

        Args:
            messages: List of message dictionaries
            callback: Function to call with each chunk
            **kwargs: Additional completion parameters

        Returns:
            List of accumulated chunks
        """
        stream = self.chat_completion(messages=messages, stream=True, **kwargs)
        chunks = []

        for chunk in stream:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                chunks.append(content)

                if callback:
                    callback(content)

        return chunks

    def batch_completion(
        self,
        batch_requests: list[dict[str, object]],
        concurrent_limit: int = 5
    ) -> list[dict[str, object]]:
        """Execute multiple completions with controlled concurrency.

        Args:
            batch_requests: List of completion request dictionaries
            concurrent_limit: Maximum concurrent requests

        Returns:
            List of completion results
        """
        import concurrent.futures

        def process_request(request_data):
            try:
                return {
                    "success": True,
                    "response": self.chat_completion(**request_data),
                    "request_id": request_data.get("id", "unknown")
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "request_id": request_data.get("id", "unknown")
                }

        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_limit) as executor:
            futures = [executor.submit(process_request, req) for req in batch_requests]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]

        return results

    def _update_usage_stats(self, usage):
        """Update usage statistics for monitoring."""
        if usage:
            self.usage_stats["total_tokens"] += usage.total_tokens
            # Approximate cost calculation (update with current pricing)
            cost = (usage.prompt_tokens * 0.0025 + usage.completion_tokens * 0.01) / 1000
            self.usage_stats["total_cost"] += cost

    def _validate_schema(self, data: object, schema: dict[str, object]): # Changed Any to object for consistency
        """Basic schema validation for structured output."""
        schema_type = schema.get("type")

        if schema_type == "object":
            if not isinstance(data, dict):
                raise ValueError(f"Expected object, got {type(data)}")

            required = schema.get("required", [])
            for prop in required:
                if prop not in data:
                    raise ValueError(f"Missing required property: {prop}")

        elif schema_type == "array":
            if not isinstance(data, list):
                raise ValueError(f"Expected array, got {type(data)}")

        elif schema_type == "string":
            if not isinstance(data, str):
                raise ValueError(f"Expected string, got {type(data)}")

        elif schema_type == "number":
            if not isinstance(data, (int, float)):
                raise ValueError(f"Expected number, got {type(data)}")

        elif schema_type == "boolean":
            if not isinstance(data, bool):
                raise ValueError(f"Expected boolean, got {type(data)}")

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
        return self.usage_stats.copy()

    def reset_usage_stats(self):
        """Reset usage statistics."""
        self.usage_stats = {
            "total_requests": 0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "errors": 0
        }

# builder function for easy instantiation
def create_openai_client(
    api_key: str | None = None,
    model: str = "gpt-4o-2024-08-06",
    **kwargs: dict[str, object]) -> OpenAIClient:
    """Create configured OpenAI client.

    Args:
        api_key: OpenAI API key
        model: Default model
        **kwargs: Additional configuration

    Returns:
        Configured OpenAI client
    """
    config = OpenAIConfig(api_key=api_key, default_model=model, **kwargs)
    return OpenAIClient(config)

# Example usage
if __name__ == "__main__":
    # Create client
    client = create_openai_client()

    # Simple completion
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain quantum computing in 100 words."}
    ]

    try:
        response = client.chat_completion(messages)

        # Structured output
        schema = {
            "type": "object",
            "properties": {
                "summary": {"type": "string"},
                "key_points": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["summary"]
        }

        structured = client.structured_completion(
            messages=messages,
            schema=schema
        )

        # Usage stats

    except Exception:
        pass # Added pass to complete the try-except block
