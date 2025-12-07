"""
OpenAI SDK Streaming Best Practices
Version: 2.0
Compatible with: openai>=1.0.0

Production-ready patterns for streaming completions with proper error handling,
token counting, and graceful degradation.
"""

from openai import OpenAI
from openai import APIError, RateLimitError, APIConnectionError
import time
from typing import Generator, Optional
import logging

logger = logging.getLogger(__name__)


def stream_completion(
    client: OpenAI,
    messages: list[dict],
    model: str = "gpt-4o-mini",
    max_retries: int = 3,
    timeout: float = 30.0,
) -> Generator[str, None, None]:
    """
    Stream a chat completion with production-grade error handling.

    Args:
        client: Initialized OpenAI client
        messages: List of message dicts with 'role' and 'content'
        model: Model identifier
        max_retries: Maximum retry attempts for transient errors
        timeout: Request timeout in seconds

    Yields:
        Content chunks as they arrive

    Raises:
        APIError: After max_retries exhausted
    """
    for attempt in range(max_retries):
        try:
            stream = client.chat.completions.create(
                model=model,
                messages=messages,
                stream=True,
                timeout=timeout,
            )

            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

            return  # Success, exit retry loop

        except RateLimitError as e:
            wait_time = 2 ** attempt
            logger.warning(f"Rate limited, waiting {wait_time}s (attempt {attempt + 1})")
            time.sleep(wait_time)

        except APIConnectionError as e:
            if attempt == max_retries - 1:
                raise
            logger.warning(f"Connection error, retrying (attempt {attempt + 1})")
            time.sleep(1)

        except APIError as e:
            logger.error(f"API error: {e}")
            raise


def stream_with_token_counting(
    client: OpenAI,
    messages: list[dict],
    model: str = "gpt-4o-mini",
) -> tuple[str, dict]:
    """
    Stream completion while tracking token usage.

    Returns:
        Tuple of (full_response, usage_stats)
    """
    full_response = []
    usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

    stream = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True,
        stream_options={"include_usage": True},
    )

    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            full_response.append(content)
            print(content, end="", flush=True)

        # Final chunk contains usage
        if chunk.usage:
            usage = {
                "prompt_tokens": chunk.usage.prompt_tokens,
                "completion_tokens": chunk.usage.completion_tokens,
                "total_tokens": chunk.usage.total_tokens,
            }

    print()  # Newline after streaming
    return "".join(full_response), usage


# Example usage
if __name__ == "__main__":
    client = OpenAI()

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain streaming in 2 sentences."},
    ]

    print("=== Basic Streaming ===")
    for chunk in stream_completion(client, messages):
        print(chunk, end="", flush=True)
    print()

    print("\n=== Streaming with Token Counting ===")
    response, usage = stream_with_token_counting(client, messages)
    print(f"Usage: {usage}")
