from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, ValidationError


class PromptSchema(BaseModel):
    """Governed prompt schema used by the Prompt CMS.

    This is intentionally independent from PromptDefinition so that
    governance can evolve without breaking core runtime models.
    """

    id: str
    role: str = "system"
    objective: str
    instructions: str
    examples: List[Dict[str, Any]] = Field(default_factory=list)
    allowed_tools: List[str] = Field(default_factory=list)
    safety_tags: List[str] = Field(default_factory=list)
    version: str = "1.0.0"


def validate_prompt(prompt: Dict[str, Any] | PromptSchema) -> PromptSchema:
    """Validate a prompt payload and return a PromptSchema.

    This is a thin wrapper around Pydantic validation that also enforces
    a few basic governance rules (non-empty id/objective/instructions).
    """

    if isinstance(prompt, PromptSchema):
        data = prompt.model_dump()
    else:
        data = dict(prompt)

    try:
        schema = PromptSchema(**data)
    except ValidationError as exc:  # pragma: no cover - exercised indirectly
        raise ValueError(f"Invalid prompt schema: {exc}") from exc

    if not schema.id.strip():
        raise ValueError("Prompt id must not be empty")
    if not schema.objective.strip():
        raise ValueError("Prompt objective must not be empty")
    if not schema.instructions.strip():
        raise ValueError("Prompt instructions must not be empty")

    return schema



