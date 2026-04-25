"""Agent routing meta spec — EQ-11 (ADR-PROMPT-ASSEMBLY-002 §11, §13).

``AgentRoutingSpec`` is a lean, frozen dataclass that bundles the five
routing-meta fields surfaced by modern model APIs:

- ``thinking_budget`` — hint for provider-side reasoning length
  (Anthropic ``thinking: {budget_tokens: N}``, Gemini
  ``thinking_config: {thinking_budget: N}``).
- ``reasoning_effort`` — OpenAI o-series ``reasoning_effort`` one of
  ``low``, ``medium``, ``high``.
- ``verbosity`` — OpenAI GPT-5 class ``verbosity`` one of ``low``,
  ``medium``, ``high``.
- ``markdown_output`` — hint for o-series ``Formatting re-enabled`` and
  Gemini markdown preference.
- ``response_schema`` — JSON Schema for structured output (threaded via
  EQ-5 to provider adapters).

All fields default to ``None`` / ``False`` so adding the spec to an
existing AgentSpec is byte-equivalent at the wire level until the
caller opts in. This keeps EQ-11 a pure back-compat extension.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


# Accepted string values for the enumerated fields. Stored here so the
# dataclass validator can reference them and tests can import the exact
# allowed sets without hardcoding.
_VALID_EFFORT = frozenset({"low", "medium", "high"})
_VALID_VERBOSITY = frozenset({"low", "medium", "high"})


@dataclass(frozen=True)
class AgentRoutingSpec:
    """Optional routing meta threaded to provider adapters.

    Every field is optional so legacy construction sites continue to
    compile and produce identical wire output. Validation happens in
    ``__post_init__`` — invalid enum values raise ``ValueError`` rather
    than silently falling through.
    """

    thinking_budget: int | None = None
    reasoning_effort: str | None = None
    verbosity: str | None = None
    markdown_output: bool = False
    response_schema: dict[str, Any] | None = field(default=None)

    def __post_init__(self) -> None:
        if self.thinking_budget is not None and self.thinking_budget < 0:
            raise ValueError(f"thinking_budget must be >= 0, got {self.thinking_budget}")
        if self.reasoning_effort is not None and self.reasoning_effort not in _VALID_EFFORT:
            raise ValueError(
                f"reasoning_effort must be one of {sorted(_VALID_EFFORT)}; got {self.reasoning_effort!r}"
            )
        if self.verbosity is not None and self.verbosity not in _VALID_VERBOSITY:
            raise ValueError(f"verbosity must be one of {sorted(_VALID_VERBOSITY)}; got {self.verbosity!r}")

    def is_default(self) -> bool:
        """Return True iff every field is at its opt-out default.

        Callers use this to decide whether to bother threading the spec
        through the adapter at all — if everything is default, the
        adapter sees no change.
        """
        return (
            self.thinking_budget is None
            and self.reasoning_effort is None
            and self.verbosity is None
            and self.markdown_output is False
            and self.response_schema is None
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a stable dict for logging / telemetry."""
        return asdict(self)

    def merge_into_extra(self, extra: dict[str, Any]) -> dict[str, Any]:
        """Fold populated fields into a ``ProviderPayload.extra`` dict.

        Fields land under the ``routing_meta`` key so downstream glue
        can find them without inspecting every top-level key. The
        caller decides how to translate ``routing_meta`` into
        provider-specific wire fields (e.g. Anthropic ``thinking={}``
        block, OpenAI ``reasoning_effort=``). The adapter does not
        second-guess the caller.
        """
        if self.is_default():
            return extra
        populated: dict[str, Any] = {}
        if self.thinking_budget is not None:
            populated["thinking_budget"] = self.thinking_budget
        if self.reasoning_effort is not None:
            populated["reasoning_effort"] = self.reasoning_effort
        if self.verbosity is not None:
            populated["verbosity"] = self.verbosity
        if self.markdown_output:
            populated["markdown_output"] = True
        if self.response_schema is not None:
            populated["response_schema"] = self.response_schema
        merged = dict(extra)
        merged["routing_meta"] = populated
        return merged


__all__ = ["AgentRoutingSpec"]
