"""Prompt Registry (CMS) for Constitutional Assets.

Phase 4 - Pillar 13: Prompt Governance (CMS)
Central repository for managing constitutional prompts as versioned assets.

Features:
- Centralized prompt storage
- Categorization and tagging
- Non-engineer friendly management
- Separation from code
"""

import json
import logging

logger = logging.getLogger(__name__)


class PromptCategory(Enum):
    """Prompt categories."""

    SYSTEM_INSTRUCTION = "system_instruction"
    SAFETY_POLICY = "safety_policy"
    REASONING_TEMPLATE = "reasoning_template"
    TASK_TEMPLATE = "task_template"
    VALIDATION_RULE = "validation_rule"
    EXAMPLE = "example"


@dataclass
class PromptTemplate:
    """Prompt template with metadata."""

    template_id: str
    name: str
    category: PromptCategory
    content: str
    version: str
    description: str = ""
    tags: list[str] = field(default_factory=list)
    variables: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "template_id": self.template_id,
            "name": self.name,
            "category": self.category.value,
            "content": self.content,
            "version": self.version,
            "description": self.description,
            "tags": self.tags,
            "variables": self.variables,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PromptTemplate":
        """Create from dictionary."""
        return cls(
            template_id=data["template_id"],
            name=data["name"],
            category=PromptCategory(data["category"]),
            content=data["content"],
            version=data["version"],
            description=data.get("description", ""),
            tags=data.get("tags", []),
            variables=data.get("variables", []),
            metadata=data.get("metadata", {}),
        )

    def render(self, **kwargs) -> str:
        """Render template with variables.

        Args:
            **kwargs: Variable values

        Returns:
            Rendered prompt
        """
        content = self.content

        for var in self.variables:
            if var in kwargs:
                placeholder = f"{{{var}}}"
                content = content.replace(placeholder, str(kwargs[var]))

        return content


class PromptRegistry:
    """Central registry for constitutional prompt assets.

    Features:
    - Template storage and retrieval
    - Category-based organization
    - Tag-based search
    - Version management
    - Persistence to disk
    """

    def __init__(
        self,
        registry_path: Path | None = None,
        enable_logging: bool = True,
    ):
        """Initialize prompt registry.

        Args:
            registry_path: Path to registry file
            enable_logging: Enable logging
        """
        self.registry_path = registry_path or Path("prompt_governance/registry/prompts.json")
        self.enable_logging = enable_logging

        self._templates: dict[str, PromptTemplate] = {}
        self._load_registry()

        if self.enable_logging:
            logger.info(
                "prompt_registry_initialized",
                extra={
                    "template_count": len(self._templates),
                    "registry_path": str(self.registry_path),
                },
            )

    def register(self, template: PromptTemplate) -> None:
        """Register a prompt template.

        Args:
            template: Prompt template
        """
        self._templates[template.template_id] = template
        self._save_registry()

        if self.enable_logging:
            logger.info(
                "template_registered",
                extra={
                    "template_id": template.template_id,
                    "category": template.category.value,
                    "version": template.version,
                },
            )

    def get(self, template_id: str) -> PromptTemplate | None:
        """Get a prompt template.

        Args:
            template_id: Template identifier

        Returns:
            PromptTemplate or None
        """
        return self._templates.get(template_id)

    def find_by_category(
        self,
        category: PromptCategory,
    ) -> list[PromptTemplate]:
        """Find templates by category.

        Args:
            category: Prompt category

        Returns:
            List of matching templates
        """
        return [t for t in self._templates.values() if t.category == category]

    def find_by_tag(self, tag: str) -> list[PromptTemplate]:
        """Find templates by tag.

        Args:
            tag: Tag to search for

        Returns:
            List of matching templates
        """
        return [t for t in self._templates.values() if tag in t.tags]

    def search(self, query: str) -> list[PromptTemplate]:
        """Search templates by name or description.

        Args:
            query: Search query

        Returns:
            List of matching templates
        """
        query_lower = query.lower()

        return [
            t
            for t in self._templates.values()
            if query_lower in t.name.lower() or query_lower in t.description.lower()
        ]

    def list_all(self) -> list[PromptTemplate]:
        """List all templates.

        Returns:
            List of all templates
        """
        return list(self._templates.values())

    def delete(self, template_id: str) -> bool:
        """Delete a template.

        Args:
            template_id: Template identifier

        Returns:
            True if deleted
        """
        if template_id in self._templates:
            del self._templates[template_id]
            self._save_registry()

            if self.enable_logging:
                logger.info("template_deleted", extra={"template_id": template_id})

            return True

        return False

    def _load_registry(self) -> None:
        """Load registry from disk."""
        if not self.registry_path.exists():
            self._create_default_templates()
            return

        try:
            with open(self.registry_path) as f:
                data = json.load(f)

            for template_data in data.get("templates", []):
                template = PromptTemplate.from_dict(template_data)
                self._templates[template.template_id] = template

        except Exception as e:
            if self.enable_logging:
                logger.error(
                    "failed_to_load_registry",
                    extra={"error": str(e)},
                    exc_info=True,
                )
            self._create_default_templates()

    def _save_registry(self) -> None:
        """Save registry to disk."""
        try:
            # Ensure directory exists
            self.registry_path.parent.mkdir(parents=True, exist_ok=True)

            data = {
                "version": "1.0.0",
                "templates": [t.to_dict() for t in self._templates.values()],
            }

            with open(self.registry_path, "w") as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            if self.enable_logging:
                logger.error(
                    "failed_to_save_registry",
                    extra={"error": str(e)},
                    exc_info=True,
                )

    def _create_default_templates(self) -> None:
        """Create default prompt templates."""
        # System instruction
        system_template = PromptTemplate(
            template_id="system_default",
            name="Default System Instruction",
            category=PromptCategory.SYSTEM_INSTRUCTION,
            content="You are a helpful AI assistant. You follow safety guidelines and provide accurate, helpful responses.",
            version="1.0.0",
            description="Default system instruction for agents",
            tags=["default", "system"],
        )
        self._templates[system_template.template_id] = system_template

        # Safety policy
        safety_template = PromptTemplate(
            template_id="safety_default",
            name="Default Safety Policy",
            category=PromptCategory.SAFETY_POLICY,
            content="Do not provide harmful, illegal, or unethical content. Refuse requests that violate safety guidelines.",
            version="1.0.0",
            description="Default safety policy",
            tags=["default", "safety"],
        )
        self._templates[safety_template.template_id] = safety_template

        # Reasoning template
        reasoning_template = PromptTemplate(
            template_id="react_default",
            name="ReAct Reasoning Template",
            category=PromptCategory.REASONING_TEMPLATE,
            content="Think step-by-step:\n1. Thought: {thought}\n2. Action: {action}\n3. Observation: {observation}",
            version="1.0.0",
            description="Default ReAct reasoning template",
            tags=["default", "reasoning", "react"],
            variables=["thought", "action", "observation"],
        )
        self._templates[reasoning_template.template_id] = reasoning_template

        self._save_registry()


def create_prompt_registry(
    registry_path: Path | None = None,
) -> PromptRegistry:
    """Factory function to create prompt registry.

    Args:
        registry_path: Optional registry path

    Returns:
        PromptRegistry instance
    """
    return PromptRegistry(registry_path=registry_path)