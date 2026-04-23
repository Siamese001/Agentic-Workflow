"""Pydantic response schema for LLM-as-Judge outputs (LJH1.3).

Provides strict validation layered on top of the existing regex-based
extraction in :mod:`agentic_core.evaluation.judges.llm_judge`. When
pydantic is available (it is part of the project's environment), judge
providers SHOULD call :func:`validate_dim_response` on the final parsed
dict to surface schema violations as typed :class:`JudgeResponseError`
rather than silently coercing malformed output.

Schema (per-dimension response)::

    {
        "score": <1|2|3|4|5|"Unknown">,
        "unknown_reason": "<string-or-null>",
    }

The ``score`` field may be the literal string ``"Unknown"`` per the
LJH2.2 escape-hatch convention.
"""

from __future__ import annotations

from typing import Any

try:
    from pydantic import BaseModel, Field, ValidationError, field_validator

    _HAS_PYDANTIC = True
except ImportError:  # pragma: no cover
    _HAS_PYDANTIC = False
    ValidationError = ValueError  # type: ignore[assignment,misc]


class JudgeResponseError(ValueError):
    """Raised when a per-dimension judge response fails schema validation."""


if _HAS_PYDANTIC:

    class _DimResponseSchema(BaseModel):
        """Strict schema for one per-dimension judge response (pydantic v2)."""

        score: int | str = Field(..., description="integer 1-5 or literal 'Unknown'")
        unknown_reason: str | None = Field(default=None, max_length=2000)

        @field_validator("score")
        @classmethod
        def _validate_score(cls, v: int | str) -> int | str:
            if isinstance(v, str):
                if v.strip().lower() != "unknown":
                    raise ValueError(f"score string must be 'Unknown', got {v!r}")
                return "Unknown"
            if not 1 <= int(v) <= 5:
                raise ValueError(f"score out of range [1,5]: {v}")
            return int(v)

    def validate_dim_response(payload: dict[str, Any]) -> dict[str, Any]:
        """Validate a per-dimension response dict. Returns the canonicalized dict.

        Raises :class:`JudgeResponseError` on any schema violation.
        """
        try:
            parsed = _DimResponseSchema.model_validate(payload)
        except ValidationError as exc:
            raise JudgeResponseError(f"schema validation failed: {exc}") from exc
        return parsed.model_dump()

else:  # pragma: no cover

    def validate_dim_response(payload: dict[str, Any]) -> dict[str, Any]:
        """Fallback validator when pydantic is not installed."""
        score = payload.get("score")
        if isinstance(score, str):
            if score.strip().lower() != "unknown":
                raise JudgeResponseError(f"score string must be 'Unknown', got {score!r}")
            score = "Unknown"
        else:
            try:
                score_i = int(score) if score is not None else None
            except (TypeError, ValueError) as exc:
                raise JudgeResponseError(f"non-integer score: {score!r}") from exc
            if score_i is None or not 1 <= score_i <= 5:
                raise JudgeResponseError(f"score out of range: {score!r}")
            score = score_i
        reason = payload.get("unknown_reason")
        if reason is not None and not isinstance(reason, str):
            raise JudgeResponseError(f"unknown_reason must be string or None, got {type(reason).__name__}")
        return {"score": score, "unknown_reason": reason}


__all__ = ["JudgeResponseError", "validate_dim_response"]
