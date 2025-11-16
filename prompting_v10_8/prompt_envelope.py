from typing import Any, Dict, Optional

from pydantic import BaseModel


class PromptEnvelope(BaseModel):
    # SECTION 1 — High-level framing (system meta-rules)
    framing: str

    # SECTION 2 — Context (merged from state, retrieved evidence, config)
    context: Dict[str, Any]

    # SECTION 3 — Reasoning Scaffolding (hidden)
    reasoning: str

    # SECTION 4 — Explicit task instructions for the model
    instructions: str

    # SECTION 5 — Tool interface, available capabilities, constraints
    tool_context: Dict[str, Any]

    # SECTION 6 — Centralized safety signals (injection/policy/constitution)
    safety_context: Dict[str, Any]

    # SECTION 7 — Output schema (required JSON structure)
    output_schema: Dict[str, Any]

    # Raw template preserved for v10.7 compatibility
    raw_template: Optional[str] = None
