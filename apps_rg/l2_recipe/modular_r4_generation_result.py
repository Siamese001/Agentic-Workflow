"""Phase 0 — apps_rg-owned result contract for modular R4 resume generation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


DecisiveStatus = Literal["PASS", "FAIL", "PARTIAL", "BLOCKED"]


@dataclass
class ModularR4GenerationResult:
    """Shared return type for ``run_modular_resume_generation`` (R4 modular path).

    ``GenerateResumeStep`` (future) may set ``context["generated_resume"]`` only when
    ``ok_for_recipe_context()`` is True.
    """

    generated_resume: dict[str, Any] | None
    section_provider_calls_ref: str
    section_output_refs: dict[str, str]
    merge_receipt_ref: str | None
    schema_validation_receipt_ref: str
    final_schema_valid: bool
    decisive_status: DecisiveStatus
    failure_reason: str
    provider_call_count: int
    locked_sections_provider_calls_detected: bool
    lanes_executed: int = 0
    lane_outputs_valid: bool = False
    final_merge_attempted: bool = False
    rg_output_merge_receipt_ref: str | None = None
    extras: dict[str, Any] = field(default_factory=dict)

    def ok_for_recipe_context(self) -> bool:
        """Mirror future GenerateResumeStep guard (same predicates)."""
        pol = self.extras.get("recipe_lane_policy") if isinstance(self.extras, dict) else None
        if isinstance(pol, dict) and pol.get("fatal_lane_failures"):
            return False
        return (
            self.decisive_status == "PASS"
            and self.final_schema_valid
            and self.lane_outputs_valid
            and isinstance(self.generated_resume, dict)
            and bool(self.generated_resume)
        )


__all__ = ["DecisiveStatus", "ModularR4GenerationResult"]
