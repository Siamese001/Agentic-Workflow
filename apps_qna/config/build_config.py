"""Build-time configuration for the card-pack builder."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class QnaBuildConfig(BaseModel):
    """Configuration for one CardPackBuilder.build() invocation."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    template_set: Literal["v1"] = "v1"
    """Template set version. Bumps go through SVP review."""

    template_dir: Path | None = None
    """Override the bundled templates directory. Useful for testing."""

    output_format: Literal["markdown"] = "markdown"
    """Output format. v1 only emits markdown."""

    force: bool = False
    """If True, overwrite an existing output directory; else FileExistsError."""

    multi_interviewer_mode: Literal["panel", "single"] = "single"
    """`panel` materializes one Lens card per interviewer; `single` collapses
    to one. Auto-set to `panel` if interviewers list has length > 1."""

    include_research_register: bool = True
    """If False, omit the source-register block from the company overlay even
    when ResearchInputs.source_register is populated."""

    line_ending: Literal["lf", "crlf"] = "lf"
    """Output line ending. LF is the deterministic default."""

    extra_specialist_overrides: dict[str, list[str]] = Field(default_factory=dict)
    """Per-route override for which specialist cards to load. Keys are route
    IDs from route_registry.yaml; values are filename lists. Off by default."""
