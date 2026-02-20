"""Invariant registry for prompt governance enforcement constants.

No import-time validation side effects.
Call validate_invariant_registry() explicitly to verify schema integrity.
"""

from __future__ import annotations

READ_ONLY_ISOLATION: dict = {
    "forbidden_verbs": ["write", "modify", "update", "delete"],
    "scope": "retrieval_context",
    "authority": "L1_prompt_governance",
}

MUTATION_BLOCK_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "forbidden_verbs": {"type": "array", "items": {"type": "string"}},
        "scope": {"type": "string"},
        "authority": {"type": "string"},
    },
    "required": ["forbidden_verbs", "scope", "authority"],
    "additionalProperties": False,
}


def validate_invariant_registry() -> None:
    """Validate READ_ONLY_ISOLATION against MUTATION_BLOCK_SCHEMA.

    Raises:
        RuntimeError: If READ_ONLY_ISOLATION fails schema validation.
    """
    from agentic_core.prompt_governance.security.validators.output_schema_validator import (
        validate_against_schema,
    )

    ok, code, _ = validate_against_schema(READ_ONLY_ISOLATION, MUTATION_BLOCK_SCHEMA)
    if not ok:
        raise RuntimeError(f"invariant_registry: READ_ONLY_ISOLATION fails MUTATION_BLOCK_SCHEMA: {code}")
