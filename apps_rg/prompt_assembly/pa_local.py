"""APP_LOCAL_PA_COMPATIBLE prompt assembly for apps_rg.

apps_rg does not use the full canonical Prompt Assembly pipeline (C0 → PA →
PromptEnvelope). Instead, HOP 3 and narrative HOPs produce model invocations
directly with equivalent provenance artifacts: prompt_bom, prompt_template_hash,
provider_lane, replay_key, token_budget_receipt.

This module provides ``capture_prompt_bom`` which wraps any LLM invocation
to record the bill-of-materials (BOM) for that call. The BOM is written to
``{run_dir}/prompt_bom/{hop_name}.json`` for auditability and replay.

Plan: apps-rg-spine-deferred-followup-d4e7b2 W2.P1.
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Optional

_log = logging.getLogger(__name__)


@dataclass(frozen=True)
class PromptBOM:
    """Bill of Materials for a single LLM invocation.

    Captures the minimum provenance needed to replay or audit the call.
    """

    hop_name: str
    model: str
    provider_lane: str  # e.g. "anthropic_claude_35_sonnet", "qwen_vllm"
    prompt_template_hash: str
    token_budget: int
    replay_key: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to JSON-safe dict."""
        return asdict(self)


def capture_prompt_bom(
    *,
    hop_name: str,
    model: str,
    provider_lane: str = "default",
    prompt_template: str = "",
    token_budget: int = 0,
    run_dir: Optional[Path] = None,
) -> PromptBOM:
    """Capture a PromptBOM for an LLM invocation and optionally write to disk.

    Args:
        hop_name: Name of the HOP making this call (e.g. "H3_orchestrator").
        model: Model identifier (e.g. "claude-3-5-sonnet-20241022").
        provider_lane: Provider lane string.
        prompt_template: The prompt template text (hashed, not stored).
        token_budget: Max tokens budgeted for this call.
        run_dir: If provided, writes the BOM to {run_dir}/prompt_bom/{hop_name}.json.

    Returns:
        The captured PromptBOM.
    """
    template_hash = hashlib.sha256(prompt_template.encode()).hexdigest()[:16]

    bom = PromptBOM(
        hop_name=hop_name,
        model=model,
        provider_lane=provider_lane,
        prompt_template_hash=template_hash,
        token_budget=token_budget,
    )

    if run_dir is not None:
        _write_bom(bom, run_dir)

    return bom


def _write_bom(bom: PromptBOM, run_dir: Path) -> None:
    """Write BOM to {run_dir}/prompt_bom/{hop_name}.json."""
    try:
        bom_dir = run_dir / "prompt_bom"
        bom_dir.mkdir(parents=True, exist_ok=True)
        out_path = bom_dir / f"{bom.hop_name}.json"
        out_path.write_text(
            json.dumps(bom.to_dict(), indent=2, default=str),
            encoding="utf-8",
        )
        _log.debug("[pa_local] Wrote prompt_bom: %s", out_path)
    except OSError as exc:
        _log.warning("[pa_local] Failed to write prompt_bom for %s: %s", bom.hop_name, exc)


__all__ = ["PromptBOM", "capture_prompt_bom"]
