from typing import Any, Optional, Protocol, Dict, List
from dataclasses import dataclass, field
from enum import Enum, auto
import re

import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from scripts.runtime.shared.multi_provider_clients import Provider, get_client

from agentic_core.L1_cognition.context.signal_context import SignalContext

LOGGER = logging.getLogger(__name__)

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
    context: SignalContext
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
            "stream": request.stream
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
            self._client_cache[provider] = get_client(provider)
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
    context: SignalContext,
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
    context: SignalContext,
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
    context: SignalContext,
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