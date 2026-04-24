"""Qwen vLLM Inference Configuration.

Core configuration for Qwen v2.5 vLLM inference in agentic_core.
Provides model configurations and prompt templates for L3 orchestration inference services.
"""
# guardian: allow-config_with_logic -- ADG violation exemption

from __future__ import annotations

from dataclasses import dataclass

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_applies_guardrail,
    _emit_records_execution_trace,
)


@dataclass(frozen=True)
class QwenModelConfig:
    """Configuration for Qwen model in inference context."""

    model_id: str
    max_tokens: int
    temperature: float
    confidence_threshold: float
    timeout_seconds: int


@dataclass(frozen=True)
class QwenPromptConfig:
    """Configuration for prompt templates by app."""

    app_name: str
    prompt_templates: dict[str, str]
    default_template: str


class QwenInferenceConfig:
    """Central configuration manager for Qwen vLLM inference."""

    # Model configurations for different use cases
    MODEL_CONFIGS: dict[str, QwenModelConfig] = {
        "fast_inference": QwenModelConfig(
            model_id="Qwen/Qwen2.5-7B-Instruct",
            max_tokens=1024,
            temperature=0.1,
            confidence_threshold=0.6,
            timeout_seconds=30,
        ),
        "complex_reasoning": QwenModelConfig(
            model_id="Qwen/Qwen2.5-14B-Instruct-AWQ",
            max_tokens=2048,
            temperature=0.2,
            confidence_threshold=0.7,
            timeout_seconds=60,
        ),
        "evaluation": QwenModelConfig(
            model_id="Qwen/Qwen2.5-7B-Instruct",
            max_tokens=1536,
            temperature=0.05,
            confidence_threshold=0.8,
            timeout_seconds=45,
        ),
    }

    # App-specific prompt configurations
    APP_PROMPT_CONFIGS: dict[str, QwenPromptConfig] = {
        "apps_eval": QwenPromptConfig(
            app_name="apps_eval",
            prompt_templates={
                "code_review": "Please review this code for quality, security, and best practices:\n\n{code}",
                "test_generation": "Generate comprehensive unit tests for this function:\n\n{function}",
                "performance_analysis": "Analyze the performance characteristics of this code:\n\n{code}",
                "architecture_review": "Evaluate this architectural design:\n\n{design}",
            },
            default_template="code_review",
        ),
        "apps_research": QwenPromptConfig(
            app_name="apps_research",
            prompt_templates={
                "synthesis": "Synthesize these research findings into a coherent summary:\n\n{findings}",
                "analysis": "Analyze this research data for key insights:\n\n{data}",
                "literature_review": "Review this literature and identify gaps:\n\n{literature}",
            },
            default_template="synthesis",
        ),
        "apps_rg": QwenPromptConfig(
            app_name="apps_rg",
            prompt_templates={
                "resume_analysis": "Analyze this resume for the given job requirements:\n\nResume: {resume}\n\nRequirements: {requirements}",
                "job_matching": "Calculate match score between candidate and job:\n\nCandidate: {candidate}\n\nJob: {job}",
                "gap_analysis": "Identify skill gaps for this career transition:\n\n{profile}",
            },
            default_template="resume_analysis",
        ),
        "apps_lic": QwenPromptConfig(
            app_name="apps_lic",
            prompt_templates={
                "lead_scoring": "Score this lead based on qualification and intent:\n\n{lead}",
                "campaign_optimization": "Optimize this campaign for better conversion:\n\n{campaign}",
                "outreach_generation": "Generate personalized outreach message:\n\n{profile}",
            },
            default_template="lead_scoring",
        ),
    }

    @classmethod
    def get_model_config(cls, use_case: str) -> QwenModelConfig:
        """Get model configuration for specific use case.

        Args:
            use_case: Type of inference task

        Returns:
            Model configuration

        Raises:
            ValueError: If use case not found
        """
        if use_case not in cls.MODEL_CONFIGS:
            _emit_applies_guardrail("qwen_inference_config", "model_config_validation", "L3_ORCHESTRATION")
            raise ValueError(f"Unknown use case: {use_case}")

        return cls.MODEL_CONFIGS[use_case]

    @classmethod
    def get_prompt_config(cls, app_name: str) -> QwenPromptConfig:
        """Get prompt configuration for specific app.

        Args:
            app_name: Name of the app

        Returns:
            Prompt configuration

        Raises:
            ValueError: If app not found
        """
        if app_name not in cls.APP_PROMPT_CONFIGS:
            _emit_applies_guardrail("qwen_inference_config", "prompt_config_validation", "L3_ORCHESTRATION")
            raise ValueError(f"Unknown app: {app_name}")

        return cls.APP_PROMPT_CONFIGS[app_name]

    @classmethod
    def validate_configuration(cls) -> bool:
        """Validate all configurations are complete.

        Returns:
            True if configuration is valid
        """
        _emit_records_execution_trace("qwen_inference_config", "L3_ORCHESTRATION", "validation")

        # Basic validation - all configs have required fields
        for name, config in cls.MODEL_CONFIGS.items():
            if not config.model_id or config.confidence_threshold <= 0:
                return False

        for name, config in cls.APP_PROMPT_CONFIGS.items():
            if not config.app_name or not config.prompt_templates:
                return False

        return True


# Backward compatibility aliases
AppsQwenModelConfig = QwenModelConfig
AppsQwenPromptConfig = QwenPromptConfig
AppsQwenConfig = QwenInferenceConfig
