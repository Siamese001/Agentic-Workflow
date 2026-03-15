"""Embedding Input Guard - Privacy Boundary for Embedding Seam.

Provides structural guarantees for privacy and data boundaries before text
is passed to an embedding model.
"""

import hashlib
import re
from dataclasses import dataclass
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace


class EmbeddingInputViolation(ValueError):
    """Raised when input text violates embedding policies."""

    pass


@dataclass(frozen=True)
class GuardedText:
    """A wrapper for text that has passed privacy and boundary checks."""

    redacted_text: str
    hash: str
    size: int


class EmbeddingInputGuard:
    """Enforces privacy and data boundary controls at the embedding seam."""

    # Allowlist of fields that are permitted to be embedded.
    ALLOWED_FIELDS = {
        "u0_user_prompt",
        "failure_signal.error_message",
        "pattern_text",
        "rag_query",
    }

    # Patterns for redacting sensitive information.
    REDACTION_PATTERNS = [
        re.compile(r"sk-[a-zA-Z0-9]{20,}"),  # API keys
        re.compile(r"Bearer [a-zA-Z0-9\-_.+/=]+"),  # Bearer tokens
        re.compile(
            r"[a-f0-9]{8}-?[a-f0-9]{4}-?[a-f0-9]{4}-?[a-f0-9]{4}-?[a-f0-9]{12}", re.IGNORECASE
        ),  # UUIDs
        re.compile(r"[\w\.-]+@[\w\.-]+\.\w+"),  # Emails
    ]

    @classmethod
    def guard(cls, text: str, field_name: str) -> GuardedText:
        """Guard and redact input text before embedding."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "EmbeddingInputGuard.guard")

        if field_name not in cls.ALLOWED_FIELDS:
            raise EmbeddingInputViolation(f"Field '{field_name}' is not allowed for embedding.")

        redacted_text = text
        for pattern in cls.REDACTION_PATTERNS:
            redacted_text = pattern.sub("[REDACTED]", redacted_text)

        text_hash = hashlib.sha256(redacted_text.encode("utf-8")).hexdigest()

        return GuardedText(
            redacted_text=redacted_text,
            hash=text_hash,
            size=len(redacted_text),
        )
