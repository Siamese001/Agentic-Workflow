"""
Prompt Category Taxonomy

10 prompt categories per the reference taxonomy:
1. USER_PROMPT (Intent) - Raw request, ZERO authority
2. INSTRUCTIONAL (The Books) - Identity/mixins, GOVERNED authority
3. INJECTIONS (Role Fencing) - Semantic fences, BINDING authority
4. EXEMPLARS (Golden Context) - Few-shot examples, GUIDING authority
5. DEPENDENCY (Context Widening) - RAG/context, INFORMATIONAL authority
6. META_COGNITIVE (Internal Monologue) - Chain/Tree of Thought, PRIVATE authority
7. SYNTHESIS (Pattern Analysis) - Telemetry summaries, ANALYTIC authority
8. SYSTEM_STATE (The Rulebooks) - Safety rules, ABSOLUTE authority
9. HEALING_PROPOSAL (The Correction) - Revised plan, PROPOSED authority
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.L2_execution.reasoning import AuthorityLevel, AuthoritySlot


class PromptCategory(Enum):
    """
    10 prompt categories with authority levels per taxonomy.

    Each category maps to a specific authority slot (S0/I0/D0/C0/U0)
    and has defined semantics for the assembly process.
    """

    # ZERO authority - Raw intent (U0)
    USER_PROMPT = (
        "USER PROMPT",
        "Raw request or task from end-user. Contains the 'What' but not the 'How.'",
        AuthorityLevel.ZERO,
        "U0",
    )

    # GOVERNED authority - Identity/mixins (I0)
    INSTRUCTIONAL = (
        "INSTRUCTIONAL",
        "Identity and specialized manuals. Defines agent capabilities.",
        AuthorityLevel.GOVERNED,
        "I0",
    )

    # BINDING authority - Semantic fences (D0)
    INJECTIONS = (
        "INJECTIONS",
        "Semantic fences applied during assembly to scope agent access.",
        AuthorityLevel.BINDING,
        "D0",
    )

    # GUIDING authority - Few-shot examples (C0)
    EXEMPLARS = (
        "EXEMPLARS",
        "Best-in-class few-shot examples guiding output style.",
        AuthorityLevel.INFO,
        "C0",
    )

    # INFORMATIONAL authority - RAG/context (C0)
    DEPENDENCY = (
        "DEPENDENCY",
        "Real-time context retrieved via RAG or Elevator Shaft.",
        AuthorityLevel.INFO,
        "C0",
    )

    # PRIVATE authority - Chain/Tree of Thought (C0)
    META_COGNITIVE = (
        "META-COGNITIVE",
        "Hidden Chain/Tree of Thought forcing internal reasoning.",
        AuthorityLevel.INFO,
        "C0",
    )

    # ANALYTIC authority - Telemetry synthesis (I0)
    SYNTHESIS = (
        "SYNTHESIS",
        "Summarizes telemetry into actionable configuration proposals.",
        AuthorityLevel.GOVERNED,
        "I0",
    )

    # ABSOLUTE authority - Safety rules (S0)
    SYSTEM_STATE = (
        "SYSTEM/STATE",
        "Mandatory safety rules and constitutions.",
        AuthorityLevel.ABSOLUTE,
        "S0",
    )

    # PROPOSED authority - Revised plan (D0/I0 depending on state)
    HEALING_PROPOSAL = (
        "HEALING PROPOSAL",
        "Revised action plan after L2 failure.",
        AuthorityLevel.BINDING,
        "D0",
    )

    def __init__(self, label: str, description: str, authority: AuthorityLevel, slot_code: str):
        self.label = label
        self.description = description
        self.authority_level = authority
        self.slot_code = slot_code

    @classmethod
    def from_slot_code(cls, code: str) -> list["PromptCategory"]:
        """Get all categories that map to a given slot code."""
        code = code.upper()
        return [c for c in cls if c.slot_code == code]

    @classmethod
    def from_authority_level(cls, level: AuthorityLevel) -> list["PromptCategory"]:
        """Get all categories with a given authority level."""
        return [c for c in cls if c.authority_level == level]


@dataclass
class CategoryTemplate:
    """
    Template definition for a specific prompt category.

    Links category metadata with template file and required variables.
    """

    category: PromptCategory
    template_id: str
    template_path: str
    required_variables: list[str] = field(default_factory=list)
    optional_variables: list[str] = field(default_factory=list)
    default_values: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate_variables(self, provided: dict[str, Any]) -> tuple[list[str], list[str]]:
        """
        Validate provided variables.

        Returns (missing_required, unknown_vars).
        """
        missing = [v for v in self.required_variables if v not in provided]
        unknown = [k for k in provided if k not in self.required_variables + self.optional_variables]
        return missing, unknown

    def merge_with_defaults(self, provided: dict[str, Any]) -> dict[str, Any]:
        """Merge provided variables with defaults."""
        result = dict(self.default_values)
        result.update(provided)
        return result

    def to_slot(self, content: str, source_layer: str = "L4") -> AuthoritySlot:
        """Convert this template to an authority slot."""
        return AuthoritySlot(
            slot_type=self.category.slot_code,
            content=content,
            authority_level=self.category.authority_level,
            source_layer=source_layer,
            metadata={
                "category": self.category.name,
                "template_id": self.template_id,
            },
        )


@dataclass
class CategoryRegistryEntry:
    """Registry entry for a loaded category template."""

    category: PromptCategory
    template: CategoryTemplate
    loaded_content: str | None = None
    git_commit_hash: str = "unknown"
    version: str = "1.0"


class PromptCategoryRegistry:
    """
    Registry for prompt category templates.

    Maintains loaded templates and provides lookup by category,
    slot code, or authority level.
    """

    def __init__(self) -> None:
        self._entries: dict[PromptCategory, CategoryRegistryEntry] = {}

    def register(self, entry: CategoryRegistryEntry) -> None:
        """Register a category template."""
        self._entries[entry.category] = entry

    def get(self, category: PromptCategory) -> CategoryRegistryEntry | None:
        """Get registry entry for a category."""
        return self._entries.get(category)

    def get_by_slot(self, slot_code: str) -> list[CategoryRegistryEntry]:
        """Get all entries for a slot code."""
        slot_code = slot_code.upper()
        return [e for e in self._entries.values() if e.category.slot_code == slot_code]

    def get_by_authority(self, level: AuthorityLevel) -> list[CategoryRegistryEntry]:
        """Get all entries for an authority level."""
        return [e for e in self._entries.values() if e.category.authority_level == level]

    def list_categories(self) -> list[PromptCategory]:
        """List all registered categories."""
        return list(self._entries.keys())

    def is_registered(self, category: PromptCategory) -> bool:
        """Check if a category is registered."""
        return category in self._entries


# Category-specific template paths (convention: {slot_code}_{category_snake}.j2)
CATEGORY_TEMPLATE_PATHS: dict[PromptCategory, str] = {
    PromptCategory.SYSTEM_STATE: "templates/S0_system_state.j2",
    PromptCategory.INSTRUCTIONAL: "templates/I0_instructional.j2",
    PromptCategory.INJECTIONS: "templates/D0_injections.j2",
    PromptCategory.HEALING_PROPOSAL: "templates/D0_healing_proposal.j2",
    PromptCategory.EXEMPLARS: "templates/C0_exemplars.j2",
    PromptCategory.DEPENDENCY: "templates/C0_dependency.j2",
    PromptCategory.META_COGNITIVE: "templates/C0_meta_cognitive.j2",
    PromptCategory.SYNTHESIS: "templates/I0_synthesis.j2",
    PromptCategory.USER_PROMPT: "templates/U0_user_prompt.j2",
}


def get_default_template_path(category: PromptCategory) -> str:
    """Get default template path for a category."""
    return CATEGORY_TEMPLATE_PATHS.get(category, f"templates/{category.slot_code}_{category.name.lower()}.j2")
