"""Reliability utilities including retry decorators."""

import asyncio
from functools import wraps


def rate_limited_retry(max_retries: int = 5, base_delay: float = 2.0):
    """Decorator to handle Gemini 429 errors with exponential backoff."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if "429" in str(e) or "quota" in str(e).lower():
                        wait = base_delay * (2 ** attempt)
                        if attempt < max_retries - 1:
                            await asyncio.sleep(wait)
                        else:
                            raise
                    else:
                        raise
            return None
        return wrapper
    return decorator
