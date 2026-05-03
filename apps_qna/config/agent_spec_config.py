"""apps_qna AgentSpec root — prompt-reception wiring anchor.

Plan: apps-core-contract-rectification-a8f3c2 Phase 2.1

apps_qna previously used ``build_config.py`` (``QnaBuildConfig``) as its
primary configuration surface. This file introduces the ``QnaAgentSpecs``
root that inherits :class:`PromptReceptionSpec` so the prompt-reception
pipeline can query ``adapter_version`` and ``exemplar_task_class`` uniformly
across all apps. Backward compatibility with ``build_config.py`` is preserved
— callers may continue using ``QnaBuildConfig`` for build-time configuration.

Design notes
------------
apps_qna is a pack-builder; its "agents" are the builder stages (pack
assembly, route selection, card generation) rather than HOP stages. The
topology is linear and controlled by the card_pack_builder module.
This AgentSpec carries the reception-pipeline fields and build-time topology
declarations that are consumption-contract rather than implementation detail.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from apps_shared.config.prompt_reception_spec import PromptReceptionSpec


class QnaPackBuilderSpec(BaseModel):
    """Configuration for the QnA card-pack builder stage topology."""

    template_set: str = Field(default="v1", description="Template set version")
    output_format: str = Field(default="markdown", description="Output format (v1: markdown only)")
    multi_interviewer_mode: str = Field(
        default="single",
        description="panel = one Lens card per interviewer; single = collapse to one",
    )
    include_research_register: bool = Field(
        default=True,
        description="Include source-register block in company overlay",
    )
    max_cards_per_pack: int = Field(default=50, ge=1, le=200)


class QnaRouteSpec(BaseModel):
    """Reception-side routing declarations for apps_qna."""

    primary_task_class: str = Field(
        default="qna_pack_build",
        description="Primary task class for rubric/threshold binding",
    )
    route_registry_ref: str = Field(
        default="apps_qna/config/route_registry.yaml",
        description="On-disk SSOT for route profiles",
    )


class QnaAgentSpecs(PromptReceptionSpec, BaseModel):
    """Root AgentSpec for apps_qna.

    Inherits :class:`PromptReceptionSpec` fields:

    - ``adapter_version: Literal['v1', 'v2']`` (default ``'v2'``)
    - ``exemplar_task_class: str | None`` (default ``None``)

    Adds apps_qna-specific topology declarations:

    - ``pack_builder``: card-pack builder stage configuration
    - ``route``: routing / task-class declarations
    """

    version: str = "1.0.0"
    pack_builder: QnaPackBuilderSpec = Field(default_factory=QnaPackBuilderSpec)
    route: QnaRouteSpec = Field(default_factory=QnaRouteSpec)


__all__ = ["QnaAgentSpecs", "QnaPackBuilderSpec", "QnaRouteSpec"]
