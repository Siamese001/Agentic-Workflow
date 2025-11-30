"""
Runtime utilities for model execution and sandbox controls.

Provides model invocation with sandbox configuration, resource limits,
and execution monitoring for the agentic system.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, UTC
import logging
import time
import uuid

logger = logging.getLogger(__name__)


@dataclass
class SandboxConfig:
    """Configuration for model execution sandbox."""
    enabled: bool = True
    timeout_seconds: int = 30
    memory_limit_mb: int = 512
    allow_network: bool = False
    max_tokens: Optional[int] = None
    temperature: float = 0.7
    top_p: float = 0.9
    max_retries: int = 3
    retry_delay: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> List[str]:
        """Validate sandbox configuration."""
        errors = []
        if self.timeout_seconds <= 0:
            errors.append("timeout_seconds must be positive")
        if self.memory_limit_mb <= 0:
            errors.append("memory_limit_mb must be positive")
        if not 0.0 <= self.temperature <= 2.0:
            errors.append("temperature must be between 0.0 and 2.0")
        if not 0.0 <= self.top_p <= 1.0:
            errors.append("top_p must be between 0.0 and 1.0")
        return errors


@dataclass
class ModelInvocationResult:
    """Result of model invocation with metadata."""
    content: str
    model: str
    tokens_used: Optional[int] = None
    execution_time_ms: Optional[float] = None
    sandbox_used: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    invocation_id: str = field(default_factory=lambda: str(uuid.uuid4()))


class ModelExecutor:
    """Handles model execution with sandbox controls and monitoring."""

    def __init__(self, default_config: Optional[SandboxConfig] = None):
        """Initialize model executor with default configuration."""
        self.default_config = default_config or SandboxConfig()
        self.execution_history: List[ModelInvocationResult] = []
        self.max_history = 100

    def invoke_model(
        self,
        model: str,
        prompt: str,
        config: Optional[SandboxConfig] = None,
        **kwargs
    ) -> ModelInvocationResult:
        """
        Invoke a model with the given prompt and configuration.

        Args:
            model: Model identifier (e.g., "gpt-4", "claude-3")
            prompt: Input prompt for the model
            config: Sandbox configuration for execution
            **kwargs: Additional model parameters

        Returns:
            ModelInvocationResult with response and metadata
        """
        # Use provided config or default
        sandbox_config = config or self.default_config

        # Validate configuration
        validation_errors = sandbox_config.validate()
        if validation_errors:
            raise ValueError(f"Invalid sandbox configuration: {', '.join(validation_errors)}")

        # Record execution start
        start_time = time.time()
        invocation_id = str(uuid.uuid4())

        try:
            # Mock model invocation (in real implementation, this would call actual LLM APIs)
            logger.info(f"Invoking model {model} with sandbox config: {sandbox_config.enabled}")

            # Simulate model processing time
            processing_time = min(len(prompt) * 0.01, sandbox_config.timeout_seconds * 0.8)
            time.sleep(processing_time)

            # Generate mock response based on prompt
            response = self._generate_mock_response(model, prompt, sandbox_config)

            # Calculate execution metrics
            execution_time_ms = (time.time() - start_time) * 1000
            tokens_used = len(response.split()) + len(prompt.split())

            # Create result
            result = ModelInvocationResult(
                content=response,
                model=model,
                tokens_used=tokens_used,
                execution_time_ms=execution_time_ms,
                sandbox_used=sandbox_config.enabled,
                metadata={
                    "invocation_id": invocation_id,
                    "prompt_length": len(prompt),
                    "response_length": len(response),
                    "config": {
                        "timeout": sandbox_config.timeout_seconds,
                        "memory_limit": sandbox_config.memory_limit_mb,
                        "temperature": sandbox_config.temperature,
                        "top_p": sandbox_config.top_p
                    }
                }
            )

            # Store in history
            self._add_to_history(result)

            logger.info(f"Model invocation completed: {invocation_id}, "
                       f"tokens: {tokens_used}, time: {execution_time_ms:.2f}ms")

            return result

        except Exception as e:
            logger.error(f"Model invocation failed: {invocation_id}, error: {str(e)}")
            raise RuntimeError(f"Model invocation failed: {str(e)}") from e

    def _generate_mock_response(self, model: str, prompt: str, config: SandboxConfig) -> str:
        """Generate mock response based on model and prompt."""
        # Simple mock response generation
        if "draft" in prompt.lower():
            return f"Generated draft content based on your request. This is a mock response from {model} with temperature {config.temperature}."
        elif "analyze" in prompt.lower():
            return f"Analysis completed. Key insights identified and recommendations provided. Response from {model}."
        elif "summarize" in prompt.lower():
            return f"Summary: The main points have been extracted and condensed. Generated by {model}."
        else:
            return f"Response from {model}: I have processed your request and generated this appropriate response."

    def _add_to_history(self, result: ModelInvocationResult) -> None:
        """Add result to execution history."""
        self.execution_history.append(result)
        if len(self.execution_history) > self.max_history:
            self.execution_history.pop(0)

    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics."""
        if not self.execution_history:
            return {"total_invocations": 0}

        total_invocations = len(self.execution_history)
        total_tokens = sum(r.tokens_used or 0 for r in self.execution_history)
        avg_time = sum(r.execution_time_ms or 0 for r in self.execution_history) / total_invocations

        return {
            "total_invocations": total_invocations,
            "total_tokens_used": total_tokens,
            "average_execution_time_ms": avg_time,
            "last_invocation": self.execution_history[-1].timestamp.isoformat() if self.execution_history else None
        }

    def clear_history(self) -> None:
        """Clear execution history."""
        self.execution_history.clear()


# Global model executor instance
_model_executor = ModelExecutor()


def invoke_model(
    model: str,
    prompt: str,
    sandbox: Optional[SandboxConfig] = None,
    **kwargs
) -> str:
    """
    Invoke a model with the given prompt and sandbox configuration.

    This is the main entry point for model invocation used throughout the system.

    Args:
        model: Model identifier (e.g., "gpt-4", "claude-3")
        prompt: Input prompt for the model
        sandbox: Sandbox configuration for execution
        **kwargs: Additional model parameters

    Returns:
        Model response string

    Raises:
        ValueError: If sandbox configuration is invalid
        RuntimeError: If model invocation fails
    """
    result = _model_executor.invoke_model(model, prompt, sandbox, **kwargs)
    return result.content


def invoke_model_with_result(
    model: str,
    prompt: str,
    sandbox: Optional[SandboxConfig] = None,
    **kwargs
) -> ModelInvocationResult:
    """
    Invoke a model and return the full result with metadata.

    Args:
        model: Model identifier
        prompt: Input prompt for the model
        sandbox: Sandbox configuration for execution
        **kwargs: Additional model parameters

    Returns:
        Complete ModelInvocationResult with metadata
    """
    return _model_executor.invoke_model(model, prompt, sandbox, **kwargs)


def get_model_executor() -> ModelExecutor:
    """Get the global model executor instance."""
    return _model_executor


def configure_model_executor(config: SandboxConfig) -> None:
    """Configure the global model executor with new default settings."""
    global _model_executor
    _model_executor = ModelExecutor(config)


# Utility functions for model management
def list_available_models() -> List[str]:
    """List available model identifiers."""
    return [
        "gpt-4",
        "gpt-3.5-turbo",
        "claude-3-opus",
        "claude-3-sonnet",
        "llama-2-70b",
        "mock-model"
    ]


def validate_model_id(model: str) -> bool:
    """Validate that a model identifier is supported."""
    available_models = list_available_models()
    return model in available_models


__all__ = [
    "SandboxConfig",
    "ModelInvocationResult",
    "ModelExecutor",
    "invoke_model",
    "invoke_model_with_result",
    "get_model_executor",
    "configure_model_executor",
    "list_available_models",
    "validate_model_id"
]





