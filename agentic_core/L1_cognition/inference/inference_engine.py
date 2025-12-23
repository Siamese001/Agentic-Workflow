from typing import Any, Optional, Protocol, Dict, List
from dataclasses import dataclass, field
from enum import Enum, auto

import logging
import time
import os

# External LLM client imports
import openai
import anthropic
import google.generativeai as genai
from mistralai.async_client import MistralAsyncClient
from groq import Groq
from together import Together
from fireworks.client import Fireworks

# Protocols for dependency injection to eliminate direct import of SignalContext
# This addresses the "Sovereign layer importing from Downstream" and
# "DIRECT CIRCULAR RISK: File imports own root 'agentic_core'" violations
# by abstracting the SignalContext dependency.
class HardStateProtocol(Protocol):
    """Protocol for the hard_state attribute of SignalContext."""
    execution_id: str
    node_id: str
    def add_trace(self, EVENT: str, DATA: Dict[str, Any]) -> 'HardStateProtocol': ...

class SignalContextProtocol(Protocol):
    """Protocol for SignalContext to allow dependency injection."""
    def get_thermal_params(self) -> Dict[str, float]: ...
    def get_anchored_context(self) -> Optional[str]: ...
    def update_timestamp(self) -> None: ...
    @property
    def hard_state(self) -> HardStateProtocol: ...
    @hard_state.setter
    def hard_state(self, value: HardStateProtocol) -> None: ...

LOGGER = logging.getLogger(__name__)

class Provider(str, Enum):
    """Enum for supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    MISTRAL = "mistral"
    GROQ = "groq"
    TOGETHER = "together"
    FIREWORKS = "fireworks"

# --- LLM Client Wrappers for OpenAI-compatible interface ---
# These wrappers ensure that all LLM clients expose a `chat.completions.create` method
# with an OpenAI-like response structure, as expected by InferenceEngine.infer.
# Note: The current InferenceEngine.infer method does not fully support streaming
# responses, so these wrappers will return non-streaming-like objects even if `stream=True`
# is passed to their `create` method.

class OpenAIClientWrapper:
    """Wrapper for OpenAI client to provide a consistent interface."""
    def __init__(self, client: openai.AsyncOpenAI):
        self._client = client

    @property
    def chat(self):
        return self._client.chat

class AnthropicClientWrapper:
    """Wrapper for Anthropic client to conform to OpenAI chat.completions.create interface."""
    def __init__(self, client: anthropic.AsyncAnthropic):
        self._client = client

    @property
    def chat(self):
        return self

    @property
    def completions(self):
        return self

    async def create(self, messages: List[Dict[str, Any]], model: str, temperature: float, top_p: float, frequency_penalty: float, presence_penalty: float, stream: bool, max_tokens: Optional[int] = None, **kwargs) -> Any:
        anthropic_messages = []
        for msg in messages:
            if msg["role"] == "user":
                anthropic_messages.append({"role": "user", "content": msg["content"]})
            elif msg["role"] == "assistant":
                anthropic_messages.append({"role": "assistant", "content": msg["content"]})
            # Anthropic's API handles system prompts differently (often as a system parameter
            # in the client or first message). For simplicity, we assume user/assistant roles.

        # Anthropic requires max_tokens
        if max_tokens is None:
            max_tokens = 1024 # Default if not provided by request

        response = await self._client.messages.create(
            model=model,
            max_tokens=max_tokens,
            messages=anthropic_messages,
            temperature=temperature,
            top_p=top_p,
            # frequency_penalty and presence_penalty are not directly supported by Anthropic
            # and are ignored here to maintain compatibility with the original API call.
            stream=False, # Force non-streaming as InferenceEngine.infer expects a direct response object
            **kwargs
        )

        # Convert Anthropic response to an OpenAI-like structure
        class MockChoice:
            def __init__(self, content):
                self.message = type('obj', (object,), {'content': content})()

        class MockUsage:
            def __init__(self, input_tokens, output_tokens):
                self.input_tokens = input_tokens
                self.output_tokens = output_tokens
            def model_dump(self):
                return {"prompt_tokens": self.input_tokens, "completion_tokens": self.output_tokens, "total_tokens": self.input_tokens + self.output_tokens}

        class MockResponse:
            def __init__(self, response_content, usage_input, usage_output):
                self.choices = [MockChoice(response_content)]
                self.usage = MockUsage(usage_input, usage_output)

        return MockResponse(response.content, response.usage.input_tokens, response.usage.output_tokens)

class GoogleClientWrapper:
    """Wrapper for Google client to conform to OpenAI chat.completions.create interface."""
    def __init__(self):
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

    @property
    def chat(self):
        return self

    @property
    def completions(self):
        return self

    async def create(self, messages: List[Dict[str, Any]], model: str, temperature: float, top_p: float, frequency_penalty: float, presence_penalty: float, stream: bool, max_tokens: Optional[int] = None, **kwargs) -> Any:
        _model = genai.GenerativeModel(model)

        google_messages = []
        for msg in messages:
            if msg["role"] == "user":
                google_messages.append({"role": "user", "parts": [msg["content"]]})
            elif msg["role"] == "assistant":
                google_messages.append({"role": "model", "parts": [msg["content"]]})
        
        generation_config = {
            "temperature": temperature,
            "top_p": top_p,
            "max_output_tokens": max_tokens,
        }
        
        response = await _model.generate_content_async(
            google_messages,
            generation_config=generation_config,
            # Google's client doesn't have direct frequency/presence penalty.
            # Streaming is not handled here as InferenceEngine.infer expects a direct response object.
            **kwargs
        )

        # Convert Google response to an OpenAI-like structure
        class MockChoice:
            def __init__(self, content):
                self.message = type('obj', (object,), {'content': content})()

        class MockUsage:
            def __init__(self, prompt_tokens, completion_tokens):
                self.prompt_tokens = prompt_tokens
                self.completion_tokens = completion_tokens
            def model_dump(self):
                return {"prompt_tokens": self.prompt_tokens, "completion_tokens": self.completion_tokens, "total_tokens": self.prompt_tokens + self.completion_tokens}

        content = response.text
        prompt_tokens = 0
        completion_tokens = 0
        if hasattr(response, 'usage_metadata'):
            prompt_tokens = response.usage_metadata.prompt_token_count
            completion_tokens = response.usage_metadata.candidates_token_count

        class MockResponse:
            def __init__(self, response_content, usage_input, usage_output):
                self.choices = [MockChoice(response_content)]
                self.usage = MockUsage(usage_input, usage_output)

        return MockResponse(content, prompt_tokens, completion_tokens)

class GenericOpenAICompatibleClientWrapper:
    """Wrapper for clients that are largely OpenAI-compatible (e.g., Mistral, Groq, Together, Fireworks)."""
    def __init__(self, client):
        self._client = client

    @property
    def chat(self):
        return self._client.chat # Assume client has a .chat attribute with .completions.create

# --- Local Client Factory ---
_local_client_cache: Dict[Provider, Any] = {}

def _get_llm_client_instance(provider: Provider) -> Any:
    """
    Instantiates and returns an LLM client for the given provider,
    wrapped to be OpenAI-compatible if necessary.
    """
    if provider not in _local_client_cache:
        client_instance = None
        if provider == Provider.OPENAI:
            client_instance = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            _local_client_cache[provider] = OpenAIClientWrapper(client_instance)
        elif provider == Provider.ANTHROPIC:
            client_instance = anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            _local_client_cache[provider] = AnthropicClientWrapper(client_instance)
        elif provider == Provider.GOOGLE:
            # Google client wrapper handles model instantiation at `create` time
            _local_client_cache[provider] = GoogleClientWrapper()
        elif provider == Provider.MISTRAL:
            client_instance = MistralAsyncClient(api_key=os.getenv("MISTRAL_API_KEY"))
            _local_client_cache[provider] = GenericOpenAICompatibleClientWrapper(client_instance)
        elif provider == Provider.GROQ:
            client_instance = Groq(api_key=os.getenv("GROQ_API_KEY"))
            _local_client_cache[provider] = GenericOpenAICompatibleClientWrapper(client_instance)
        elif provider == Provider.TOGETHER:
            client_instance = Together(api_key=os.getenv("TOGETHER_API_KEY"))
            _local_client_cache[provider] = GenericOpenAICompatibleClientWrapper(client_instance)
        elif provider == Provider.FIREWORKS:
            client_instance = Fireworks(api_key=os.getenv("FIREWORKS_API_KEY"))
            _local_client_cache[provider] = GenericOpenAICompatibleClientWrapper(client_instance)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    return _local_client_cache[provider]

class InferenceMode(str, Enum):
    """Inference modes for different types of cognitive operations."""
    CREATIVE = "creative"          # Max temperature, high entropy
    ANALYTICAL = "analytical"      # Medium temperature, structured thinking
    VALIDATION = "validation"      # Low temperature, precision focused
    FORMATTING = "formatting"      # Very low temperature, template adherence

@dataclass
class InferenceRequest:
    """Request structure for inference engine."""
    prompt: str
    context: SignalContextProtocol  # Changed to use Protocol for dependency injection
    mode: InferenceMode = InferenceMode.ANALYTICAL
    provider: Provider = Provider.OPENAI
    model: Optional[str] = None
    max_tokens: Optional[int] = None
    STREAM: bool = False

    # Override thermal settings if needed
    temperature_override: Optional[float] = None
    top_p_override: Optional[float] = None

@dataclass
class InferenceResult:
    """Result structure for inference engine."""
    content: str
    usage: Dict[str, Any]
    thermal_params_used: Dict[str, float]
    execution_time_ms: float
    provider: Provider
    model: str
    context_updated: bool = False

class ThermostatMiddleware:
    """
    Middleware that dynamically adjusts LLM parameters based on thermal configuration.

    This middleware reads the thermal profile from the SignalContext and applies
    appropriate temperature, top_p, and other parameters to maximize signal
    quality for the specific operation type.
    """

    def __init__(self, enable_logging: bool = True):
        """Initialize thermostat middleware.

        Args:
            enable_logging: Enable thermal parameter logging
        """
        self.enable_logging = enable_logging
        self._thermal_history: List[Dict[str, Any]] = []

    def get_thermal_params(self, request: InferenceRequest) -> Dict[str, float]:
        """Get thermal parameters for the inference request.

        Args:
            request: Inference request with context

        Returns:
            Dictionary of thermal parameters
        """
        # Use explicit overrides if provided
        if request.temperature_override is not None:
            params = {
                "temperature": request.temperature_override,
                "top_p": request.top_p_override or 0.85,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0
            }
        else:
            # Get from context thermal config
            params = request.context.get_thermal_params()

            # Adjust based on inference mode
            mode_adjustments = {
                InferenceMode.CREATIVE: {"temperature": 0.9, "top_p": 0.95},
                InferenceMode.ANALYTICAL: {"temperature": 0.7, "top_p": 0.85},
                InferenceMode.VALIDATION: {"temperature": 0.1, "top_p": 0.50},
                InferenceMode.FORMATTING: {"temperature": 0.3, "top_p": 0.70}
            }

            if request.mode in mode_adjustments:
                # Blend context thermal with mode-specific thermal
                base_temp = params.get("temperature", 0.7)
                mode_temp = mode_adjustments[request.mode]["temperature"]
                # Weight towards mode-specific thermal
                params["temperature"] = (base_temp * 0.3) + (mode_temp * 0.7)
                params["top_p"] = mode_adjustments[request.mode]["top_p"]

        # Log thermal parameters if enabled
        if self.enable_logging:
            self._log_thermal_usage(request, params)

        return params

    def _log_thermal_usage(self, request: InferenceRequest, params: Dict[str, float]) -> None:
        """Log thermal parameter usage for analysis.

        Args:
            request: The inference request
            params: Thermal parameters applied
        """
        log_entry = {
            "timestamp": time.time(),
            "execution_id": request.context.hard_state.execution_id,
            "node_id": request.context.hard_state.node_id,
            "mode": request.mode.value,
            "provider": request.provider.value,
            "thermal_params": params.copy()
        }
        self._thermal_history.append(log_entry)

        # Keep only last 1000 entries
        if len(self._thermal_history) > 1000:
            self._thermal_history = self._thermal_history[-1000:]

        LOGGER.info(
            "thermal_params_applied",
            EXTRA={
                "execution_id": log_entry["execution_id"],
                "node_id": log_entry["node_id"],
                "mode": log_entry["mode"],
                "temperature": params["temperature"],
                "top_p": params["top_p"]
            }
        )

    def get_thermal_history(self, execution_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get thermal parameter history.

        Args:
            execution_id: Optional execution ID to filter by

        Returns:
            List of thermal parameter usage history
        """
        if execution_id:
            return [h for h in self._thermal_history if h["execution_id"] == execution_id]
        return self._thermal_history.copy()

class InferenceEngine:
    """
    Main inference engine with thermostat middleware for dynamic thermal control.

    This engine provides a unified interface for LLM inference while automatically
    adjusting thermal parameters based on the context and operation type.
    """

    def __init__(
        self,
        thermostat: Optional[ThermostatMiddleware] = None,
        default_provider: Provider = Provider.OPENAI,
        enable_logging: bool = True
    ):
        """Initialize inference engine.

        Args:
            thermostat: Optional thermostat middleware
            default_provider: Default LLM provider
            enable_logging: Enable inference logging
        """
        self.thermostat = thermostat or ThermostatMiddleware(enable_logging)
        self.default_provider = default_provider
        self.enable_logging = enable_logging
        self._client_cache: Dict[Provider, Any] = {}

        LOGGER.info(
            "inference_engine_initialized",
            EXTRA={
                "default_provider": default_provider.value,
                "thermostat_enabled": thermostat is not None
            }
        )

    async def infer(self, request: InferenceRequest) -> InferenceResult:
        """
        Perform inference with dynamic thermal adjustment.

        Args:
            request: Inference request with context

        Returns:
            Inference result with content and metadata
        """
        start_time = time.time()

        # Get thermal parameters
        thermal_params = self.thermostat.get_thermal_params(request)

        # Get client for provider
        client = self._get_client(request.provider)

        # Prepare API parameters
        api_params = {
            "model": request.model or self._get_default_model(request.provider),
            "messages": [{"role": "user", "content": self._prepare_prompt(request)}],
            "temperature": thermal_params["temperature"],
            "top_p": thermal_params["top_p"],
            "frequency_penalty": thermal_params["frequency_penalty"],
            "presence_penalty": thermal_params["presence_penalty"],
            "stream": request.STREAM # Note: Current implementation of infer method does not fully support streaming
        }

        if request.max_tokens:
            api_params["max_tokens"] = request.max_tokens

        try:
            # Make the API call
            response = await client.chat.completions.create(**api_params)

            # Extract content and usage
            content = response.choices[0].message.content
            usage = response.usage.model_dump() if response.usage else {}

            # Calculate execution time
            execution_time = (time.time() - start_time) * 1000

            # Update context with inference trace
            request.context.hard_state = request.context.hard_state.add_trace(
                EVENT="inference_completed",
                DATA={
                    "provider": request.provider.value,
                    "model": api_params["model"],
                    "thermal_params": thermal_params,
                    "usage": usage,
                    "execution_time_ms": execution_time
                }
            )
            request.context.update_timestamp()

            # Create result
            result = InferenceResult(
                content=content,
                usage=usage,
                thermal_params_used=thermal_params,
                execution_time_ms=execution_time,
                provider=request.provider,
                model=api_params["model"],
                context_updated=True
            )

            if self.enable_logging:
                LOGGER.info(
                    "inference_completed",
                    EXTRA={
                        "execution_id": request.context.hard_state.execution_id,
                        "provider": request.provider.value,
                        "model": api_params["model"],
                        "temperature": thermal_params["temperature"],
                        "tokens_used": usage.get("total_tokens", 0),
                        "execution_time_ms": execution_time
                    }
                )

            return result

        except Exception as e:
            LOGGER.error(
                "inference_failed",
                EXTRA={
                    "execution_id": request.context.hard_state.execution_id,
                    "provider": request.provider.value,
                    "error": str(e)
                },
                exc_info=True
            )
            raise

    def _prepare_prompt(self, request: InferenceRequest) -> str:
        """Prepare the prompt with context anchoring.

        Args:
            request: Inference request

        Returns:
            Formatted prompt with anchored claims
        """
        # Get anchored context if available
        anchored_context = request.context.get_anchored_context()

        # Combine base prompt with anchored context
        if anchored_context:
            return f"{request.prompt}\n{anchored_context}"

        return request.prompt

    def _get_client(self, provider: Provider) -> Any:
        """Get cached client for provider.

        Args:
            provider: LLM provider

        Returns:
            Client instance
        """
        if provider not in self._client_cache:
            self._client_cache[provider] = _get_llm_client_instance(provider)
        return self._client_cache[provider]

    def _get_default_model(self, provider: Provider) -> str:
        """Get default model for provider.

        Args:
            provider: LLM provider

        Returns:
            Default model name
        """
        defaults = {
            Provider.OPENAI: "gpt-4",
            Provider.ANTHROPIC: "claude-3-sonnet-20240229",
            Provider.GOOGLE: "gemini-pro",
            Provider.MISTRAL: "mistral-large",
            Provider.GROQ: "llama2-70b-4096",
            Provider.TOGETHER: "meta-llama/Llama-2-70b-chat-hf",
            Provider.FIREWORKS: "accounts/fireworks/models/llama-v2-70b-chat"
        }
        return defaults.get(provider, "gpt-4")

    def get_thermal_history(self, execution_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get thermal parameter usage history.

        Args:
            execution_id: Optional execution ID to filter by

        Returns:
            List of thermal parameter usage history
        """
        return self.thermostat.get_thermal_history(execution_id)

# Factory functions for common inference patterns

async def creative_inference(
    prompt: str,
    context: SignalContextProtocol, # Changed to use Protocol
    provider: Provider = Provider.OPENAI
) -> InferenceResult:
    """
    Perform creative inference with maximum temperature.

    Args:
        prompt: The prompt to send
        context: Signal context with thermal configuration
        provider: LLM provider to use

    Returns:
        Inference result
    """
    engine = InferenceEngine()
    request = InferenceRequest(
        prompt=prompt,
        context=context,
        mode=InferenceMode.CREATIVE,
        provider=provider
    )
    return await engine.infer(request)

async def validation_inference(
    prompt: str,
    context: SignalContextProtocol, # Changed to use Protocol
    provider: Provider = Provider.OPENAI
) -> InferenceResult:
    """
    Perform validation inference with minimum temperature.

    Args:
        prompt: The prompt to send
        context: Signal context with thermal configuration
        provider: LLM provider to use

    Returns:
        Inference result
    """
    engine = InferenceEngine()
    request = InferenceRequest(
        prompt=prompt,
        context=context,
        mode=InferenceMode.VALIDATION,
        provider=provider
    )
    return await engine.infer(request)

async def analytical_inference(
    prompt: str,
    context: SignalContextProtocol, # Changed to use Protocol
    provider: Provider = Provider.OPENAI
) -> InferenceResult:
    """
    Perform analytical inference with balanced temperature.

    Args:
        prompt: The prompt to send
        context: Signal context with thermal configuration
        provider: LLM provider to use

    Returns:
        Inference result
    """
    engine = InferenceEngine()
    request = InferenceRequest(
        prompt=prompt,
        context=context,
        mode=InferenceMode.ANALYTICAL,
        provider=provider
    )
    return await engine.infer(request)