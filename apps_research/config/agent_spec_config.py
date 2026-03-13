"""
apps_research Configuration Schemas — Autonomous Research Engine.

Pydantic models for type-safe configuration. Aligned with apps_rg pattern.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

_log = logging.getLogger(__name__)


class ArtifactModeConfig(BaseModel):
    """Configuration for a research artifact mode."""

    mode_id: str
    display_name: str
    required_sections: list[str] = Field(default_factory=list)
    max_words: int = Field(default=1500, ge=100)
    requires_source_register: bool = True
    requires_comparison_table: bool = False


class SourceRegisterConfig(BaseModel):
    """Configuration for the source register schema."""

    max_sources: int = Field(default=20, ge=1)
    required_fields: list[str] = Field(
        default_factory=lambda: ["source_id", "title", "claim_type", "confidence"]
    )
    claim_types: list[str] = Field(
        default_factory=lambda: ["direct_evidence", "interpretation", "analyst_inference", "assumption"]
    )


class ResearchGateConfig(BaseModel):
    """Quality gates for research artifacts."""

    require_source_register: bool = True
    min_sources: int = Field(default=1, ge=0)
    require_audience_declaration: bool = True
    require_purpose_declaration: bool = True
    max_unsupported_claims: int = Field(default=0, ge=0)
    require_inference_labels: bool = True
    min_quality_score: float = Field(default=0.70, ge=0.0, le=1.0)


class ResearchOutputConfig(BaseModel):
    """Output configuration."""

    output_dir: str = Field(default="reports/research")
    artifact_prefix: str = Field(default="research")
    emit_run_summary: bool = True
    emit_source_register: bool = True
    dry_run: bool = False


class ResearchAgentSpecs(BaseModel):
    """Root configuration for all apps_research agent specifications."""

    version: str = "1.0.0"
    artifact_modes: dict[str, ArtifactModeConfig] = Field(
        default_factory=lambda: {
            "brief": ArtifactModeConfig(
                mode_id="brief",
                display_name="Topic Brief",
                required_sections=["executive_summary", "key_findings", "strategic_implications"],
                max_words=1200,
            ),
            "comparison": ArtifactModeConfig(
                mode_id="comparison",
                display_name="Framework Comparison",
                required_sections=["comparison_overview", "comparison_matrix", "recommendation"],
                max_words=2000,
                requires_comparison_table=True,
            ),
            "trend": ArtifactModeConfig(
                mode_id="trend",
                display_name="Trend Scan",
                required_sections=["trend_overview", "signal_analysis", "horizon_implications"],
                max_words=1500,
            ),
            "position": ArtifactModeConfig(
                mode_id="position",
                display_name="Position Memo",
                required_sections=[
                    "position_statement",
                    "supporting_evidence",
                    "counterarguments",
                    "conclusion",
                ],
                max_words=1800,
            ),
            "thought_leadership": ArtifactModeConfig(
                mode_id="thought_leadership",
                display_name="Thought Leadership Post",
                required_sections=["hook", "insight", "evidence", "call_to_action"],
                max_words=800,
            ),
        }
    )
    source_register: SourceRegisterConfig = Field(default_factory=SourceRegisterConfig)
    gate: ResearchGateConfig = Field(default_factory=ResearchGateConfig)
    output: ResearchOutputConfig = Field(default_factory=ResearchOutputConfig)
    global_step_limit: int = Field(default=8)
    checkpoint_enabled: bool = True
    trace_persistence: bool = True


_SPEC_CACHE: ResearchAgentSpecs | None = None


def load_research_specs(spec_path: str | None = None) -> ResearchAgentSpecs:
    """Load ResearchAgentSpecs from JSON file or return defaults."""
    global _SPEC_CACHE
    if _SPEC_CACHE is not None:
        return _SPEC_CACHE

    resolved: Path | None = None
    if spec_path:
        resolved = Path(spec_path)
    else:
        default = Path(__file__).parent / "research_agent_specs.json"
        if default.exists():
            resolved = default

    if resolved and resolved.exists():
        try:
            raw: dict[str, Any] = json.loads(resolved.read_text(encoding="utf-8"))
            _SPEC_CACHE = ResearchAgentSpecs.model_validate(raw)
            return _SPEC_CACHE
        except (FileNotFoundError, json.JSONDecodeError, ValueError, OSError) as exc:
            _log.warning("[apps_research] Failed to load specs: %s — using defaults", exc)

    _SPEC_CACHE = ResearchAgentSpecs()
    return _SPEC_CACHE
