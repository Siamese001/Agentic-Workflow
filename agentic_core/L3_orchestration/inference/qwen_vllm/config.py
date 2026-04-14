from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class QwenModelConfig:
    model_id: str
    max_tokens: int
    temperature: float
    confidence_threshold: float
    timeout_seconds: int

    def __post_init__(self) -> None:
        if not isinstance(self.model_id, str) or not self.model_id.strip():
            raise ValueError("model_id must be a non-empty string")
        if self.max_tokens <= 0:
            raise ValueError("max_tokens must be positive")
        if not 0.0 <= self.temperature <= 2.0:
            raise ValueError("temperature must be between 0 and 2")
        if not 0.0 <= self.confidence_threshold <= 1.0:
            raise ValueError("confidence_threshold must be between 0 and 1")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")


@dataclass(frozen=True)
class QwenPromptConfig:
    app_name: str
    prompt_templates: dict[str, str]
    default_template: str

    def __post_init__(self) -> None:
        if not isinstance(self.app_name, str) or not self.app_name.strip():
            raise ValueError("app_name must be a non-empty string")
        if not isinstance(self.prompt_templates, dict) or not self.prompt_templates:
            raise ValueError("prompt_templates must be a non-empty dict")
        if self.default_template not in self.prompt_templates:
            raise ValueError("default_template must exist in prompt_templates")
        for key, value in self.prompt_templates.items():
            if not isinstance(key, str) or not key.strip():
                raise ValueError("prompt template keys must be non-empty strings")
            if not isinstance(value, str):
                raise ValueError("prompt template values must be strings")

    def render(self, template_name: str | None = None, **kwargs: object) -> str:
        key = template_name or self.default_template
        if key not in self.prompt_templates:
            raise KeyError(key)
        return self.prompt_templates[key].format(**kwargs)


class QwenInferenceConfig:
    MODEL_CONFIGS: ClassVar[dict[str, QwenModelConfig]] = {
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
            timeout_seconds=45,
        ),
    }

    @classmethod
    def get_model_config(cls, profile: str) -> QwenModelConfig:
        key = str(profile or "").strip()
        if key not in cls.MODEL_CONFIGS:
            raise KeyError(f"unknown qwen inference profile: {profile!r}")
        return cls.MODEL_CONFIGS[key]

    @classmethod
    def list_profiles(cls) -> tuple[str, ...]:
        return tuple(sorted(cls.MODEL_CONFIGS))

    @classmethod
    def has_profile(cls, profile: str) -> bool:
        return str(profile or "").strip() in cls.MODEL_CONFIGS


__all__ = ["QwenInferenceConfig", "QwenModelConfig", "QwenPromptConfig"]
