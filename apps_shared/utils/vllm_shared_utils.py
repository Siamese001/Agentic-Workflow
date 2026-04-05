"""VLLM Shared Utilities - Common vLLM patterns and utilities.

This module provides shared vLLM functionality that can be used across
different apps_* modules to reduce code duplication and ensure consistency.
"""

from __future__ import annotations

import logging
from typing import Any

# guardian: allow-silent-degradation -- Qwen vLLM is optional for shared utilities; graceful fallback to no-op
try:
    from apps_qwen import (
        AppsQwenGateway,
        AppsQwenInferenceWorker,
        AppsQwenRequest,
        apps_qwen_telemetry,
    )
    from apps_qwen.apps_qwen_config import (
        AppsQwenModelConfig,
        AppsQwenPromptConfig,
    )

    _QWEN_AVAILABLE = True
except ImportError:
    AppsQwenGateway = None  # type: ignore[assignment]
    AppsQwenRequest = None  # type: ignore[assignment]
    AppsQwenInferenceWorker = None  # type: ignore[assignment]
    apps_qwen_telemetry = None  # type: ignore[assignment]
    AppsQwenModelConfig = None  # type: ignore[assignment]
    AppsQwenPromptConfig = None  # type: ignore[assignment]
    _QWEN_AVAILABLE = False

_log = logging.getLogger(__name__)


class VLLMSharedManager:
    """Shared vLLM manager with common patterns and utilities."""

    def __init__(self, app_name: str, model_config: dict[str, Any] | None = None):
        """Initialize shared vLLM manager.

        Args:
            app_name: Name of the application using vLLM
            model_config: Optional model configuration overrides
        """
        self.app_name = app_name
        self._qwen_gateway = None
        self._qwen_inference_worker = None
        self._qwen_session_id = None
        self._qwen_enabled = True

        if _QWEN_AVAILABLE:
            self._initialize_vllm(model_config or {})
        else:
            self._qwen_enabled = False
            _log.warning(f"Qwen vLLM not available for {app_name}")

    def _initialize_vllm(self, model_config: dict[str, Any]) -> None:
        """Initialize vLLM components with error handling."""
        try:
            # Initialize Qwen gateway
            model_id = model_config.get("model_id", "Qwen/Qwen2.5-7B-Instruct")
            self._qwen_gateway = AppsQwenGateway(model_id=model_id)

            # Initialize inference worker
            config = AppsQwenModelConfig(
                model_id=model_id,
                max_tokens=model_config.get("max_tokens", 2048),
                temperature=model_config.get("temperature", 0.3),
                confidence_threshold=0.7,
                timeout_seconds=60,
            )
            self._qwen_inference_worker = AppsQwenInferenceWorker(config)

            # Start telemetry session
            if apps_qwen_telemetry is not None:
                self._qwen_session_id = apps_qwen_telemetry.start_session(self.app_name)

            _log.info(f"Initialized vLLM for {self.app_name} with model {model_id}")

        except Exception as e:
            _log.error(f"Failed to initialize vLLM for {self.app_name}: {e}")
            self._qwen_enabled = False

    async def generate_response(
        self,
        prompt: str,
        confidence_threshold: float = 0.7,
        max_tokens: int | None = None,
        temperature: float | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Generate vLLM response with common pattern.

        Args:
            prompt: Input prompt for generation
            confidence_threshold: Minimum confidence threshold
            max_tokens: Override max tokens for this request
            temperature: Override temperature for this request
            metadata: Optional metadata to include in response

        Returns:
            Dictionary with response and metadata
        """
        if not self._qwen_enabled or self._qwen_gateway is None:
            return {"success": False, "error": "vllm_unavailable", "content": None, "app_name": self.app_name}

        # Validate input parameters
        if not prompt or not prompt.strip():
            return {"success": False, "error": "empty_prompt", "content": None, "app_name": self.app_name}

        if confidence_threshold < 0 or confidence_threshold > 1:
            return {"success": False, "error": "invalid_confidence_threshold", "content": None, "app_name": self.app_name}

        try:
            # Create Qwen request
            request = AppsQwenRequest(
                app_name=self.app_name,
                prompt=prompt,
                confidence_threshold=confidence_threshold,
                max_tokens=max_tokens or 2048,
                temperature=temperature or 0.3,
            )

            # Record telemetry start
            if apps_qwen_telemetry is not None and self._qwen_session_id is not None:
                apps_qwen_telemetry.record_request_start(
                    session_id=self._qwen_session_id,
                    app_name=self.app_name,
                    model_id="Qwen/Qwen2.5-7B-Instruct",
                )

            # Perform inference
            response = await self._qwen_gateway.infer(request)

            # Record telemetry result
            if apps_qwen_telemetry is not None and self._qwen_session_id is not None:
                if response.success:
                    apps_qwen_telemetry.record_request_success(
                        session_id=self._qwen_session_id,
                        app_name=self.app_name,
                        model_id=response.model_used,
                        latency_ms=response.latency_ms,
                        confidence=response.confidence,
                        tokens_used=len(prompt.split()) + len(response.response.split())
                        if response.response
                        else 0,
                    )
                else:
                    apps_qwen_telemetry.record_request_error(
                        session_id=self._qwen_session_id,
                        app_name=self.app_name,
                        model_id=response.model_used,
                        error_message=response.error_message or "unknown_error",
                    )

            # Build response with metadata
            result = {
                "success": response.success,
                "content": response.response,
                "confidence": response.confidence,
                "model_used": response.model_used,
                "latency_ms": response.latency_ms,
                "app_name": self.app_name,
                "error_message": response.error_message,
            }

            if metadata:
                result["metadata"] = metadata

            return result

        except Exception as e:
            _log.error(f"vLLM generation failed for {self.app_name}: {e}")
            return {
                "success": False,
                "error": f"generation_failed: {str(e)}",
                "content": None,
                "app_name": self.app_name,
            }

    def is_available(self) -> bool:
        """Check if vLLM is available and initialized."""
        return self._qwen_enabled and self._qwen_gateway is not None


class VLLMPromptTemplates:
    """Shared prompt templates for common vLLM use cases."""

    @staticmethod
    def analysis_prompt(content: str, analysis_type: str, context: dict[str, Any] | None = None) -> str:
        """Generate analysis prompt template.

        Args:
            content: Content to analyze
            analysis_type: Type of analysis (risk, compliance, quality, etc.)
            context: Optional context information

        Returns:
            Formatted prompt string
        """
        context_text = ""
        if context:
            for key, value in context.items():
                context_text += f"{key.title()}: {value}\n"

        prompt = f"""ANALYSIS REQUEST

ANALYSIS TYPE: {analysis_type}

CONTEXT:
{context_text}

CONTENT TO ANALYZE:
{content}

INSTRUCTIONS:
Please provide a thorough analysis that includes:
1. Executive Summary
2. Key Findings
3. Risk Assessment (if applicable)
4. Recommendations
5. Supporting Evidence

Ensure the analysis is objective, comprehensive, and actionable.
"""

        return prompt

    @staticmethod
    def generation_prompt(
        task: str, requirements: list[str], constraints: list[str] | None = None, style: str = "professional"
    ) -> str:
        """Generate content creation prompt template.

        Args:
            task: Description of the generation task
            requirements: List of requirements for the output
            constraints: Optional constraints to consider
            style: Output style (professional, casual, technical, etc.)

        Returns:
            Formatted prompt string
        """
        requirements_text = ""
        for i, req in enumerate(requirements, 1):
            requirements_text += f"{i}. {req}\n"

        constraints_text = ""
        if constraints:
            for constraint in constraints:
                constraints_text += f"- {constraint}\n"

        prompt = f"""CONTENT GENERATION REQUEST

TASK: {task}
STYLE: {style}

REQUIREMENTS:
{requirements_text}

CONSTRAINTS:
{constraints_text}

INSTRUCTIONS:
Please generate content that meets all requirements while respecting the constraints.
Ensure the output is:
1. Well-structured and coherent
2. Appropriate for the intended audience
3. Free of errors and inconsistencies
4. Aligned with the specified style guidelines

Focus on quality, clarity, and relevance.
"""

        return prompt

    @staticmethod
    def comparison_prompt(
        items: list[dict[str, Any]], criteria: list[str], comparison_type: str = "general"
    ) -> str:
        """Generate comparison prompt template.

        Args:
            items: List of items to compare
            criteria: List of comparison criteria
            comparison_type: Type of comparison (technical, business, etc.)

        Returns:
            Formatted prompt string
        """
        items_text = ""
        for i, item in enumerate(items, 1):
            items_text += f"ITEM {i}:\n"
            for key, value in item.items():
                items_text += f"{key.title()}: {value}\n"
            items_text += "---\n"

        criteria_text = ""
        for criterion in criteria:
            criteria_text += f"- {criterion}\n"

        prompt = f"""COMPARISON ANALYSIS REQUEST

COMPARISON TYPE: {comparison_type}

ITEMS TO COMPARE:
{items_text}

COMPARISON CRITERIA:
{criteria_text}

INSTRUCTIONS:
Please provide a comprehensive comparison analysis that includes:
1. Overview of each item
2. Detailed comparison across all criteria
3. Strengths and weaknesses of each item
4. Recommendations based on specific use cases
5. Summary table of key differences

Ensure the comparison is fair, objective, and based on the provided criteria.
"""

        return prompt


class VLLMConfigPresets:
    """Predefined vLLM configuration presets for different use cases."""

    @staticmethod
    def creative_config() -> dict[str, Any]:
        """Configuration for creative content generation."""
        return {
            "model_id": "Qwen/Qwen2.5-7B-Instruct",
            "max_tokens": 3072,
            "temperature": 0.7,
            "confidence_threshold": 0.6,
        }

    @staticmethod
    def analytical_config() -> dict[str, Any]:
        """Configuration for analytical tasks."""
        return {
            "model_id": "Qwen/Qwen2.5-7B-Instruct",
            "max_tokens": 2048,
            "temperature": 0.2,
            "confidence_threshold": 0.8,
        }

    @staticmethod
    def professional_config() -> dict[str, Any]:
        """Configuration for professional/business content."""
        return {
            "model_id": "Qwen/Qwen2.5-7B-Instruct",
            "max_tokens": 2560,
            "temperature": 0.3,
            "confidence_threshold": 0.75,
        }

    @staticmethod
    def technical_config() -> dict[str, Any]:
        """Configuration for technical documentation."""
        return {
            "model_id": "Qwen/Qwen2.5-7B-Instruct",
            "max_tokens": 3584,
            "temperature": 0.1,
            "confidence_threshold": 0.85,
        }

    @staticmethod
    def research_config() -> dict[str, Any]:
        """Configuration for research synthesis."""
        return {
            "model_id": "Qwen/Qwen2.5-7B-Instruct",
            "max_tokens": 4096,
            "temperature": 0.4,
            "confidence_threshold": 0.7,
        }


# Utility functions for common vLLM operations
def validate_vllm_response(response: dict[str, Any]) -> bool:
    """Validate vLLM response structure.

    Args:
        response: Response dictionary from vLLM generation

    Returns:
        True if response is valid, False otherwise
    """
    required_fields = ["success", "content", "confidence", "model_used"]
    return all(field in response for field in required_fields)


def extract_response_metadata(response: dict[str, Any]) -> dict[str, Any]:
    """Extract metadata from vLLM response.

    Args:
        response: Response dictionary from vLLM generation

    Returns:
        Dictionary with extracted metadata
    """
    metadata = {
        "success": response.get("success", False),
        "confidence": response.get("confidence", 0.0),
        "model_used": response.get("model_used", "unknown"),
        "latency_ms": response.get("latency_ms", 0),
        "app_name": response.get("app_name", "unknown"),
    }

    if "content" in response and response["content"]:
        metadata["content_length"] = len(response["content"])
        metadata["word_count"] = len(response["content"].split())

    if "error_message" in response:
        metadata["error"] = response["error_message"]

    return metadata
