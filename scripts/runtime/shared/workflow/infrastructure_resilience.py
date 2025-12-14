import time
import functools
from typing import Dict, Any, Callable
from openai import APIConnectionError, APITimeoutError as OpenAITimeout
from anthropic import APIConnectionError as AnthropicConnectionError, APITimeoutError as AnthropicTimeout
import logging


logger = logging.getLogger(__name__)
# Define a unified tuple of retryable errors
RETRYABLE_ERRORS = (
    APIConnectionError, 
    OpenAITimeout, 
    AnthropicConnectionError, 
    AnthropicTimeout,
    ConnectionError
)

def resilient_execution(fallback_model: str = "gpt-4o"):
    """
    Decorator that attempts execution with the primary configuration.
    If it fails (timeout/connection), it swaps to the fallback model.
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Extract config from kwargs if present (convention: 'config' dict passed to agents)
            config = kwargs.get('config', {})
            max_retries = config.get('infrastructure_config', {}).get('max_retries', 2)
            
            attempt = 0
            while attempt <= max_retries:
                try:
                    return func(*args, **kwargs)
                
                except RETRYABLE_ERRORS as e:
                    attempt += 1
                    logger.error(f"⚡ Circuit Breaker: Caught error {type(e).__name__} (Attempt {attempt})")
                    
                    if attempt > max_retries:
                        logger.error("💥 Circuit Breaker: Max retries exceeded. Raising exception.")
                        raise e
                    
                    # Exponential Backoff
                    sleep_time = 2 ** attempt
                    logger.info(f"⏳ Sleeping {sleep_time}s...")
                    time.sleep(sleep_time)
                    
                    # FALLBACK STRATEGY
                    # If we have a 'config' dict, we can patch it to use the fallback model
                    if 'config' in kwargs:
                        infra = kwargs['config'].get('infrastructure_config', {})
                        current_model = infra.get('primary_model', 'unknown')
                        
                        # Only switch if we haven't already
                        if current_model != fallback_model:
                            logger.info(f"🔄 Circuit Breaker: Switching {current_model} -> {fallback_model}")
                            # Patch the config dictionary in place for the next attempt
                            kwargs['config']['infrastructure_config']['primary_model'] = fallback_model
                            # If switching providers (e.g., Claude -> GPT), the client routing inside 'func' 
                            # needs to handle the model name change dynamically.
            
        return wrapper
    return decorator
