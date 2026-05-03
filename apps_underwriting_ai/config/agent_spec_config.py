"""apps_underwriting_ai agent spec configuration.

Minimal Pydantic schemas for the underwriting agent specification. Mirrors
the apps_rfp pattern but stripped to the essential fields for the skeleton
build. Heavy lifecycle-trace shims are intentionally omitted — this app
imports lifecycle telemetry directly from
``agentic_core.runtime.contracts.lifecycle_trace_contract`` where needed.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field

from apps_shared.config.prompt_reception_spec import PromptReceptionSpec

_log = logging.getLogger(__name__)


class UnderwritingThresholds(BaseModel):
    """Quality gate thresholds for underwriting decisions."""

    min_evidence_records: int = Field(
        default=1,
        ge=0,
        description="Minimum evidence records before APPROVE is permitted.",
    )
    max_unresolved_documents: int = Field(
        default=0,
        ge=0,
        description="Maximum unresolved reconciliations before REFER is forced.",
    )
    require_feature_vector: bool = Field(
        default=True,
        description="Whether risk features must be derived before decision.",
    )


class UnderwritingAgentSpec(BaseModel):
    """Agent spec contract for apps_underwriting_ai."""

    spec_version: str = Field(default="1.0.0")
    agent_id: str = Field(default="underwriting_decision_agent")
    capability_class: str = Field(default="underwriting_decision")
    thresholds: UnderwritingThresholds = Field(default_factory=UnderwritingThresholds)
    metadata: dict[str, Any] = Field(default_factory=dict)


class UnderwritingConfig(BaseModel):
    """Top-level config for apps_underwriting_ai runs."""

    agent_spec: UnderwritingAgentSpec = Field(default_factory=UnderwritingAgentSpec)
    artifact_dir: str = Field(default="underwriting_artifacts/")


def load_spec(spec_path: Path | str) -> UnderwritingAgentSpec:
    """Load an UnderwritingAgentSpec from a YAML file.

    Args:
        spec_path: Path to spec YAML.

    Returns:
        Validated UnderwritingAgentSpec.

    Raises:
        FileNotFoundError: If spec_path does not exist.
        pydantic.ValidationError: If the spec fails validation.
    """
    p = Path(spec_path)
    if not p.exists():
        raise FileNotFoundError(f"underwriting spec not found: {spec_path}")
    raw = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    return UnderwritingAgentSpec.model_validate(raw)


class UnderwritingAgentSpecs(PromptReceptionSpec, BaseModel):
    """Root AgentSpec for apps_underwriting_ai.

    Inherits :class:`PromptReceptionSpec` fields:

    - ``adapter_version: Literal['v1', 'v2']`` (default ``'v2'``)
    - ``exemplar_task_class: str | None`` (default ``None``)

    Adds apps_underwriting_ai-specific topology declarations via
    ``UnderwritingAgentSpec`` and ``UnderwritingConfig``.

    Plan: apps-core-contract-rectification-a8f3c2 Phase 2.2
    """

    version: str = "1.0.0"
    agent_spec: UnderwritingAgentSpec = Field(default_factory=UnderwritingAgentSpec)


__all__ = [
    "UnderwritingAgentSpec",
    "UnderwritingAgentSpecs",
    "UnderwritingConfig",
    "UnderwritingThresholds",
    "load_spec",
]
