"""Prompt Injection Loader - Dynamic prompt enhancement for Subatomic Hops.

This module provides a system for loading and applying prompt injection patterns
to enhance the quality and specificity of outputs, particularly for resumes
and messages.
"""

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .instructional_injections import get_instructional_injections

try:
    from agentic_core.L5_safety.validators.prompt_governance_types import (
        InjectionConfig,
        InjectionMatch,
        InjectionPattern,
        InjectionScope,
        InjectionType,
        MicroStage,
    )
except ImportError:
    # Fallback classes
    @dataclass
    class InjectionConfig:
        pattern: str = "default"
        type: str = "instructional"
        scope: str = "all"
        injection_dir: Path = Path("data/injections")
        enable_yaml_loader: bool = False
        enable_caching: bool = True

    @dataclass
    class InjectionMatch:
        pattern: str
        matched: bool
        confidence: float

    @dataclass
    class InjectionPattern:
        id: str
        name: str
        type: str
        description: str
        template: str
        variables: list[str]
        scope: str
        priority: int
        enabled: bool

    # Simple string-based fallback for remaining types
    InjectionScope = str
    InjectionType = str
    MicroStage = str

logger = logging.getLogger(__name__)


class PromptInjectionLoader:
    """Loads and applies prompt injection patterns."""

    def __init__(self, config: InjectionConfig | None = None):
        """Initialize the injection loader.

        Args:
            config: Optional configuration
        """
        self.config = config or InjectionConfig()
        self.injections: dict[str, InjectionPattern] = {}
        self.cache: dict[str, list[InjectionMatch]] = {}

        # Load injections
        self._load_injections()

        logger.info(f"Initialized PromptInjectionLoader with {len(self.injections)} patterns")

    def _load_injections(self) -> None:
        """Load injection patterns from files."""
        injection_dir = self.config.injection_dir

        # Create directory if it doesn't exist
        injection_dir.mkdir(parents=True, exist_ok=True)

        # Load built-in injections if directory is empty
        if not any(injection_dir.iterdir()):
            self._create_builtin_injections()

        # Load all JSON files
        for file_path in injection_dir.glob("*.json"):
            try:
                with open(file_path, encoding="utf-8") as f:
                    data = json.load(f)

                if isinstance(data, list):
                    # Multiple injections in file
                    for item in data:
                        injection = InjectionPattern(**item)
                        self.injections[injection.id] = injection
                else:
                    # Single injection
                    injection = InjectionPattern(**data)
                    self.injections[injection.id] = injection

                logger.debug(f"Loaded injection {injection.id} from {file_path}")

            except Exception as e:
                logger.error(f"Failed to load {file_path}: {e}")

        # Load instructional injections
        self._load_instructional_injections()

    def _load_instructional_injections(self) -> None:
        """Load all 30 instructional injection patterns."""

        # Try YAML loader if enabled
        if self.config.enable_yaml_loader:
            try:
                self._load_instructional_injections_from_yaml()
                return
            except Exception as e:
                logger.warning(f"YAML loader failed, falling back to markdown: {e}")

        # Fallback to markdown-based loading
        self._load_instructional_injections_from_markdown()

    def _load_instructional_injections_from_yaml(self) -> None:
        """Load instructional injections from YAML corpus."""
        try:
            from agentic_core.config.core.yaml_injection_loader import get_yaml_loader
        except ImportError:
            raise ImportError("YAML loader not available")

        yaml_loader = get_yaml_loader()
        all_patterns = yaml_loader.load_all_patterns()

        for layer_name, patterns in all_patterns.items():
            for pattern in patterns:
                # Convert to our InjectionPattern format
                injection_pattern = InjectionPattern(
                    id=f"yaml_{layer_name}_{pattern.id}",
                    name=pattern.name,
                    type="instructional",
                    description=pattern.description,
                    template=pattern.template,
                    variables=[],  # YAML patterns don't have explicit variables
                    scope="instructional",
                    priority=5,
                    enabled=pattern.enabled,
                )

                self.injections[injection_pattern.id] = injection_pattern
                logger.debug(f"Loaded YAML instructional injection {injection_pattern.id}")

    def _load_instructional_injections_from_markdown(self) -> None:
        """Load instructional injections from markdown (original behavior)."""
        instructional_injections = get_instructional_injections()

        for injection in instructional_injections:
            # Convert to our InjectionPattern format
            pattern = InjectionPattern(
                id=injection.id,
                name=injection.name,
                type="instructional",
                description=injection.description,
                template=injection.template,
                variables=[],
                scope="instructional",
                priority=5,
                enabled=True,
            )

            self.injections[injection.id] = pattern
            logger.debug(f"Loaded markdown instructional injection {injection.id}")

    def _create_builtin_injections(self) -> None:
        """Create built-in injection patterns."""
        builtin_injections = [
            # Resume enhancement injections
            {
                "id": "resume_achievement_quantification",
                "name": "Achievement Quantification",
                "type": "resume_enhancement",
                "description": "Adds metrics and quantification to achievements",
                "template": "Transform this achievement by adding specific metrics: '{achievement}'. Include numbers, percentages, or measurable impact.",
                "variables": ["achievement"],
                "scope": "resume_experience",
                "priority": 8,
            },
            {
                "id": "resume_action_verb_enhancement",
                "name": "Action Verb Enhancement",
                "type": "resume_enhancement",
                "description": "Replaces weak verbs with strong action verbs",
                "template": "Enhance this responsibility with stronger action verbs: '{responsibility}'. Use verbs like 'orchestrated', 'pioneered', 'revolutionized'.",
                "variables": ["responsibility"],
                "scope": "resume_bullets",
                "priority": 7,
            },
        ]

        for injection_data in builtin_injections:
            # Create simple injection pattern
            pattern = InjectionPattern(
                id=injection_data["id"],
                name=injection_data["name"],
                type=injection_data["type"],
                description=injection_data["description"],
                template=injection_data["template"],
                variables=injection_data.get("variables", []),
                scope=injection_data["scope"],
                priority=injection_data["priority"],
                enabled=True,
            )

            self.injections[injection_data["id"]] = pattern

    def save_injection(self, injection_id: str, injection: InjectionPattern) -> None:
        """Save an injection pattern to file."""
        file_path = self.config.injection_dir / f"{injection_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(injection, f, indent=2, default=str)

    def find_matching_injections(
        self,
        hop_type: str,
        stage: str,
        context: dict[str, Any],
        content: str | None = None,
    ) -> list[InjectionMatch]:
        """Find injections matching the given context.

        Args:
            hop_type: Type of hop executing
            stage: Current stage (as string, e.g., "PRE_CHECK", "THINK")
            context: Execution context
            content: Optional content to analyze

        Returns:
            List of matching injection patterns
        """
        cache_key = f"{hop_type}:{stage}:{hash(str(context))}"

        if self.config.enable_caching and cache_key in self.cache:
            return self.cache[cache_key]

        matches = []

        for injection_id, injection in self.injections.items():
            if not injection.enabled:
                continue

            # Simple matching logic - can be enhanced
            confidence = self._calculate_match_confidence(injection, hop_type, stage, context, content)

            if confidence > 0.5:
                match = InjectionMatch(
                    pattern=injection_id,
                    matched=True,
                    confidence=confidence,
                )
                matches.append(match)

        # Sort by confidence
        matches.sort(key=lambda m: m.confidence, reverse=True)

        if self.config.enable_caching:
            self.cache[cache_key] = matches

        return matches

    def _calculate_match_confidence(
        self,
        injection: InjectionPattern,
        hop_type: str,
        stage: str,
        context: dict[str, Any],
        content: str | None,
    ) -> float:
        """Calculate confidence score for injection matching.

        Args:
            injection: Injection pattern to evaluate
            hop_type: Type of hop
            stage: Current stage
            context: Execution context
            content: Optional content

        Returns:
            Confidence score between 0.0 and 1.0
        """
        confidence = 0.0

        # Basic matching logic
        if hasattr(injection, 'scope') and injection.scope == hop_type:
            confidence += 0.3

        if hasattr(injection, 'type') and injection.type == "instructional":
            confidence += 0.2

        # Add more sophisticated matching logic here

        return min(confidence, 1.0)

    def apply_injections(
        self,
        base_prompt: str,
        hop_type: str,
        stage: str,
        context: dict[str, Any],
        content: str | None = None,
    ) -> str:
        """Apply matching injections to a base prompt.

        Args:
            base_prompt: Base prompt to enhance
            hop_type: Type of hop executing
            stage: Current stage
            context: Execution context
            content: Optional content to analyze

        Returns:
            Enhanced prompt with injections applied
        """
        matches = self.find_matching_injections(hop_type, stage, context, content)

        enhanced_prompt = base_prompt

        for match in matches:
            if match.matched and match.confidence > 0.7:
                injection = self.injections[match.pattern]
                if hasattr(injection, 'template'):
                    enhanced_prompt += f"\n\n{injection.template}"

        return enhanced_prompt


# Convenience function
def get_injection_loader(config: InjectionConfig | None = None) -> PromptInjectionLoader:
    """Get a configured injection loader instance.

    Args:
        config: Optional configuration

    Returns:
        Configured PromptInjectionLoader instance
    """
    return PromptInjectionLoader(config)
