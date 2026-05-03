"""apps_lic AgentSpec root — prompt-reception and HOP topology wiring.

Plans:
- prompt-reception-followups-a7b3c4 (delta fix for phase RH5B.1) — original scaffold
- apps-core-contract-rectification-a8f3c2 Phase 2.2 — expanded to full HOP topology

apps_lic runs a 9-stage HOP pipeline declared in ``hop_pipeline.py``. This
root inherits :class:`PromptReceptionSpec` for uniform prompt-reception
wiring and adds per-HOP stage configuration models reflecting the
topology in ``hop_pipeline.py``.

Backward compatibility
----------------------
Per-component config modules (``archetype_indicator_config.py``,
``loader_config.py``, ``reasoning_toggles_config.py``, etc.) remain the
SSOT for their domain-specific settings. This root provides the reception-
pipeline fields and stage-level timeout/criticality declarations that the
spine queries at dispatch time.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from apps_shared.config.prompt_reception_spec import PromptReceptionSpec


class LicHopStageSpec(BaseModel):
    """Per-stage configuration for a single LIC HOP stage."""

    timeout_sec: int = Field(default=30, ge=1)
    criticality: str = Field(
        default="required",
        pattern="^(required|optional|best_effort)$",
    )
    retry_on_low_score: bool = Field(
        default=False,
        description="Trigger retry-on-low policy for this stage's primary dim",
    )


class LicHopTopologySpec(BaseModel):
    """Timeout and criticality declarations for all 9 LIC HOP stages.

    Stage names mirror those in ``apps_lic/config/hop_pipeline.py``.
    """

    profile_analysis: LicHopStageSpec = Field(default_factory=LicHopStageSpec)
    research: LicHopStageSpec = Field(default_factory=LicHopStageSpec)
    sender_grounding: LicHopStageSpec = Field(default_factory=LicHopStageSpec)
    routing: LicHopStageSpec = Field(default_factory=LicHopStageSpec)
    generation: LicHopStageSpec = Field(
        default_factory=lambda: LicHopStageSpec(timeout_sec=60, retry_on_low_score=True),
    )
    validation: LicHopStageSpec = Field(default_factory=LicHopStageSpec)
    gate_decision: LicHopStageSpec = Field(
        default_factory=lambda: LicHopStageSpec(timeout_sec=15),
    )
    qa_report: LicHopStageSpec = Field(default_factory=LicHopStageSpec)
    integration: LicHopStageSpec = Field(default_factory=LicHopStageSpec)


class LicAgentSpecs(PromptReceptionSpec, BaseModel):
    """Root AgentSpec for apps_lic — full 9-stage HOP topology.

    Inherits :class:`PromptReceptionSpec` fields:

    - ``adapter_version: Literal['v1', 'v2']`` (default ``'v2'``)
    - ``exemplar_task_class: str | None`` (default ``None``)

    Adds apps_lic-specific topology declarations:

    - ``hop_topology``: per-stage timeout/criticality for all 9 HOP stages
    """

    version: str = "1.0.0"
    hop_topology: LicHopTopologySpec = Field(default_factory=LicHopTopologySpec)


__all__ = ["LicAgentSpecs", "LicHopTopologySpec", "LicHopStageSpec"]
