"""Universal Prompt Provider System for the entire agentic suite.

Provides a centralized, version-controlled system for managing prompts
across all agent domains: executive, resume generation, outreach, and utilities.
"""

import os
import yaml
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum


class AgentDomain(Enum):
    """Domains of agents in the system."""
    EXECUTIVE = "executive"
    RESUME = "resume"
    OUTREACH = "outreach"
    UTILITY = "utility"


@dataclass
class PromptTemplate:
    """A prompt template with metadata."""
    name: str
    version: str
    domain: AgentDomain
    template: str
    variables: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    examples: List[Dict[str, str]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def render(self, context: Dict[str, Any]) -> str:
        """Render the template with context variables.

        Args:
            context: Variables to inject into template

        Returns:
            Rendered prompt string
        """
        # Simple string replacement for now
        # Could upgrade to Jinja2 for complex templates
        rendered = self.template
        for key, value in context.items():
            rendered = rendered.replace(f"{{{key}}}", str(value))
        return rendered


class PromptVersionRegistry:
    """Registry for managing prompt versions."""

    def __init__(self, prompts_dir: Optional[str] = None):
        """Initialize the registry.

        Args:
            prompts_dir: Directory containing prompt templates
        """
        if prompts_dir is None:
            prompts_dir = os.path.join(os.path.dirname(__file__), "..", "..", "prompts")

        self.prompts_dir = Path(prompts_dir)
        self.templates: Dict[str, Dict[str, PromptTemplate]] = {}
        self.logger = logging.getLogger("PromptVersionRegistry")

        # Load all templates
        self._load_all_templates()

    def _load_all_templates(self):
        """Load all prompt templates from YAML files."""
        if not self.prompts_dir.exists():
            self.logger.warning(f"Prompts directory not found: {self.prompts_dir}")
            return

        for domain_dir in self.prompts_dir.iterdir():
            if not domain_dir.is_dir():
                continue

            domain_name = domain_dir.name
            if domain_name not in [d.value for d in AgentDomain]:
                self.logger.warning(f"Unknown domain: {domain_name}")
                continue

            domain = AgentDomain(domain_name)
            self.templates[domain.value] = {}

            for yaml_file in domain_dir.glob("*.yaml"):
                try:
                    with open(yaml_file, 'r') as f:
                        data = yaml.safe_load(f)

                    template = PromptTemplate(
                        name=data['name'],
                        version=data['version'],
                        domain=domain,
                        template=data['template'],
                        variables=data.get('variables', []),
                        constraints=data.get('constraints', []),
                        examples=data.get('examples', []),
                        metadata=data.get('metadata', {})
                    )

                    self.templates[domain.value][template.name] = template
                    self.
                        .logger.
                        .debug(f"Loaded template: {domain_name}/{template.
                        .name} v{template.
                        .version}")

                except Exception as e:
                    self.logger.error(f"Failed to load {yaml_file}: {e}")

    def get_template(self,
        domain: AgentDomain,
        name: str,
        version: Optional[str] = None) -> Optional[PromptTemplate]:
        """Get a prompt template.

        Args:
            domain: Agent domain
            name: Template name
            version: Specific version (latest if None)

        Returns:
            PromptTemplate or None if not found
        """
        domain_templates = self.templates.get(domain.value, {})
        template = domain_templates.get(name)

        if template is None:
            return None

        # Handle version selection when multiple versions exist
        return template

    def list_templates(self, domain: Optional[AgentDomain] = None) -> Dict[str, List[str]]:
        """List all available templates.

        Args:
            domain: Optional domain filter

        Returns:
            Dictionary of domain -> list of template names
        """
        if domain:
            return {domain.value: list(self.templates.get(domain.value, {}).keys())}

        return {d: list(templates.keys()) for d, templates in self.templates.items()}


class UniversalPromptProvider(ABC):
    """Base class for all prompt providers."""

    def __init__(self, registry: PromptVersionRegistry, template_name: str):
        """Initialize the provider.

        Args:
            registry: Prompt version registry
            template_name: Name of the template to use
        """
        self.registry = registry
        self.template_name = template_name
        self.domain = self._get_domain()
        self.template = registry.get_template(self.domain, template_name)

        if self.template is None:
            raise ValueError(f"Template not found: {self.domain.value}/{template_name}")

    @abstractmethod
    def _get_domain(self) -> AgentDomain:
        """Get the agent domain."""
        pass

    def get_system_prompt(self, context: Dict[str, Any]) -> str:
        """Get the rendered system prompt.

        Args:
            context: Context variables for rendering

        Returns:
            Rendered prompt string
        """
        return self.template.render(context)

    def get_constraints(self) -> str:
        """Get prompt constraints."""
        return "\n".join(self.template.constraints)

    def get_examples(self) -> List[Dict[str, str]]:
        """Get few-shot examples."""
        return self.template.examples


class LegacyPromptProvider(UniversalPromptProvider):
    """Provider for agents with hardcoded prompts (backward compatibility)."""

    def __init__(self, hardcoded_prompt: str):
        """Initialize with hardcoded prompt.

        Args:
            hardcoded_prompt: The existing hardcoded prompt
        """
        self.hardcoded_prompt = hardcoded_prompt
        # Create a dummy registry for compatibility
        registry = PromptVersionRegistry()
        super().__init__(registry, "legacy")

    def _get_domain(self) -> AgentDomain:
        return AgentDomain.UTILITY

    def get_system_prompt(self, context: Dict[str, Any]) -> str:
        """Return the hardcoded prompt."""
        return self.hardcoded_prompt


class PromptProviderFactory:
    """Factory for creating prompt providers."""

    def __init__(self, registry: Optional[PromptVersionRegistry] = None):
        """Initialize the factory.

        Args:
            registry: Optional prompt registry
        """
        self.registry = registry or PromptVersionRegistry()

    def create_provider(
        self,
        domain: AgentDomain,
        template_name: str,
        fallback_prompt: Optional[str] = None
    ) -> UniversalPromptProvider:
        """Create a prompt provider.

        Args:
            domain: Agent domain
            template_name: Template name
            fallback_prompt: Optional fallback for backward compatibility

        Returns:
            Prompt provider instance
        """
        try:
            # Try to create a typed provider
            provider_class = self._get_provider_class(domain)
            return provider_class(self.registry, template_name)
        except ValueError:
            # Fall back to legacy provider
            if fallback_prompt:
                return LegacyPromptProvider(fallback_prompt)
            raise

    def _get_provider_class(self, domain: AgentDomain) -> type:
        """Get the provider class for a domain.

        Args:
            domain: Agent domain

        Returns:
            Provider class
        """
        # Will be expanded as we add domain-specific providers
        providers = {
            AgentDomain.EXECUTIVE: ExecutivePromptProvider,
            AgentDomain.RESUME: ResumePromptProvider,
            AgentDomain.OUTREACH: OutreachPromptProvider,
            AgentDomain.UTILITY: UtilityPromptProvider,
        }

        return providers.get(domain, UniversalPromptProvider)


# Domain-specific provider classes
class ExecutivePromptProvider(UniversalPromptProvider):
    """Provider for executive agents."""

    def _get_domain(self) -> AgentDomain:
        return AgentDomain.EXECUTIVE


class ResumePromptProvider(UniversalPromptProvider):
    """Provider for resume generation agents."""

    def _get_domain(self) -> AgentDomain:
        return AgentDomain.RESUME


class OutreachPromptProvider(UniversalPromptProvider):
    """Provider for outreach agents."""

    def _get_domain(self) -> AgentDomain:
        return AgentDomain.OUTREACH


class UtilityPromptProvider(UniversalPromptProvider):
    """Provider for utility agents."""

    def _get_domain(self) -> AgentDomain:
        return AgentDomain.UTILITY
