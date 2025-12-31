# gemini_spy.py
# L5 Telemetry Interceptor for SubAtomicEngine
# PURPOSE: Wraps the SubAtomicEngine to force visibility of all LLM transactions
# LOCATION: agentic_core/observability/telemetry/ (SSOT-compliant)

import asyncio
import time
from typing import Any


class GeminiSpy:
    """
    [L5 HARDENING] TELEMETRY INTERCEPTOR
    
    Wraps the SubAtomicEngine to force visibility of all LLM transactions.
    Ensures that 'Agentic Capabilities' are actually resulting in API calls.
    
    Features:
    - Intercepts all method calls on the wrapped engine
    - Logs prompt previews and execution times
    - Blocks unauthorized model references (OpenAI, Anthropic, etc.)
    - Detects zero-latency mutations (potential logic bugs)
    """
    
    def __init__(self, real_engine: Any):
        """
        Initialize the spy wrapper.
        
        Args:
            real_engine: The actual SubAtomicEngine instance to wrap
        """
        self._engine = real_engine

    def __getattr__(self, name: str) -> Any:
        """
        Intercept attribute access to wrap method calls with telemetry.
        
        Args:
            name: Attribute name being accessed
            
        Returns:
            Wrapped method or original attribute
        """
        # Pass through non-callable attributes immediately
        attr = getattr(self._engine, name)
        if attr is None:
            raise AttributeError(f"Engine method '{name}' is None/Missing on {type(self._engine)}")
            
        if not callable(attr) or name.startswith("_"):
            return attr

        # Check if method is async
        if asyncio.iscoroutinefunction(attr):
            async def async_wrapper(*args, **kwargs):
                # [GAP 20 HARDENING] Block unauthorized models at the wire
                if args:
                    prompt_text = str(args[0]).lower()
                    forbidden = ["openai", "anthropic", "claude", "gpt"]
                    if any(bad in prompt_text for bad in forbidden):
                        raise ValueError(f"[L5 SECURITY BLOCK] Unauthorized model reference detected in prompt.")
                
                print(f"\n[SPY] GEMINI SPY Agent triggering: {name}")
                if args:
                    try:
                        preview = str(args[0])[:120].replace('\n', ' ')
                        print(f"   -> Prompt: {preview}...")
                    except:
                        pass
                
                start_t = time.time()
                try:
                    result = await attr(*args, **kwargs)
                    duration = time.time() - start_t
                    if duration < 0.05 and name == "resilient_mutation":
                        print(f"   [!] ALERT: Zero-latency mutation detected. Check engine logic.")
                    print(f"[SPY] GEMINI SPY LLM Success ({duration:.2f}s).")
                    return result
                except (asyncio.CancelledError, SystemExit):
                    raise
                except Exception as e:
                    print(f"[SPY] GEMINI SPY LLM OR TELEMETRY FAILURE: {e}")
                    raise
            return async_wrapper
        
        def wrapper(*args, **kwargs):
            # [GAP 20 HARDENING] Block unauthorized models at the wire
            if args:
                prompt_text = str(args[0]).lower()
                forbidden = ["openai", "anthropic", "claude", "gpt"]
                if any(bad in prompt_text for bad in forbidden):
                    raise ValueError(f"[L5 SECURITY BLOCK] Unauthorized model reference detected in prompt.")
            
            print(f"\n[SPY] GEMINI SPY Agent triggering: {name}")
            if args:
                try:
                    preview = str(args[0])[:120].replace('\n', ' ')
                    print(f"   -> Prompt: {preview}...")
                except:
                    pass
            
            start_t = time.time()
            try:
                result = attr(*args, **kwargs)
                duration = time.time() - start_t
                if duration < 0.05 and name == "resilient_mutation":
                    print(f"   [!] ALERT: Zero-latency mutation detected. Check engine logic.")
                print(f"[SPY] GEMINI SPY LLM Success ({duration:.2f}s).")
                return result
            except (asyncio.CancelledError, SystemExit):
                raise
            except Exception as e:
                # Log detailed failure for debugging telemetry mismatches
                print(f"[SPY] GEMINI SPY LLM OR TELEMETRY FAILURE: {e}")
                if "successful_traces" in str(e):
                    print("   -> CAUSE: ValidationContext is missing .successful_traces list.")
                raise e
        
        return wrapper
