"""Per-provider invoke context for apps_rg X1D panel adapters."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from apps_rg.runtime.judges.executive_summary_x1d import JudgeOutput


@dataclass
class X1dPanelProviderContext:
    """Runtime state for one provider invocation (transport-only adapters)."""

    provider_key: str
    api_key: str
    model: str
    input_hash: str
    model_source: str
    model_requested: str
    section_id: str = "executive_summary"
    artifact_base: Path | None = None
    judge_receipt: dict[str, Any] | None = None
    reasoning_effort: str | None = None
    allow_model_fallback: bool = False
    canonical_contract_hash: str | None = None
    deterministic_gate_summary: dict[str, Any] | None = None
    last_judge_output: JudgeOutput | None = field(default=None, repr=False)


__all__ = ["X1dPanelProviderContext"]
