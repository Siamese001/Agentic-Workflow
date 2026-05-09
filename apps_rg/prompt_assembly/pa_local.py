"""QUARANTINE NOTICE — AG-RGGOV-8: QUARANTINE_ALL_RUNTIME_HOPS

This file is QUARANTINED per the declarative ingress-only governance model.
apps_rg may NOT emit lifecycle trace contracts or make provider calls.

Original: apps_rg/prompt_assembly\pa_local.py
Quarantined: 2026-05-09
Reason: AG-RGGOV-W4-SCOPE — Runtime authority violation

Importing this module raises RuntimeError immediately.
Core L6 Observability owns all trace emission. apps_rg is ingress-only.
"""

raise RuntimeError(
    "QUARANTINE VIOLATION (AG-RGGOV-8): "
    "apps_rg.prompt_assembly\pa_local is QUARANTINED. "
    "apps_rg may NOT contain runtime authority. "
    "Core L2/L5/L6 owns execution. apps_rg is ingress-only. "
    "See: .windsurf/plans/apps-rg-declarative-ingress-only-spinal-governance-c8b3e1.md §19"
)

# Original code archived to: archives/apps_rg/quarantine_w4_20260509/prompt_assembly\pa_local.py.ORIGINAL

# QUARANTINED — Original content below for reference only — NOT EXECUTABLE:
# """APP_LOCAL_PA_COMPATIBLE prompt assembly for apps_rg.
# 
# apps_rg does not use the full canonical Prompt Assembly pipeline (C0 → PA →
# PromptEnvelope). Instead, HOP 3 and narrative HOPs produce model invocations
# directly with equivalent provenance artifacts: prompt_bom, prompt_template_hash,
# provider_lane, replay_key, token_budget_receipt.
# 
# This module provides ``capture_prompt_bom`` which wraps any LLM invocation
# to record the bill-of-materials (BOM) for that call. The BOM is written to
# ``{run_dir}/prompt_bom/{hop_name}.json`` for auditability and replay.
# 
# Plan: apps-rg-spine-deferred-followup-d4e7b2 W2.P1.
# """
# 
# from __future__ import annotations
# 
# import hashlib
# import json
# import logging
# import time
# import uuid
# from dataclasses import asdict, dataclass, field
# from pathlib import Path
# from typing import Any, Optional
# 
# from apps_rg.prompt_assembly._pa_boundary import (
#     PABoundaryStatus,
#     make_pa_boundary_receipt,
# )
# 
# _log = logging.getLogger(__name__)
# 
# 
# @dataclass(frozen=True)
# class PromptBOM:
#     """Bill of Materials for a single LLM invocation.
# 
#     Captures the minimum provenance needed to replay or audit the call.
#     W3.P1: adds pa_boundary_receipt for PA boundary lineage.
#     """
# 
#     hop_name: str
#     model: str
#     provider_lane: str  # e.g. "anthropic_claude_35_sonnet", "qwen_vllm"
#     prompt_template_hash: str
#     token_budget: int
#     replay_key: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
#     timestamp: float = field(default_factory=time.time)
#     pa_boundary_receipt: dict[str, Any] = field(default_factory=dict)
# 
#     def to_dict(self) -> dict[str, Any]:
#         """Serialize to JSON-safe dict."""
#         return asdict(self)
# 
# 
# def capture_prompt_bom(
#     *,
#     hop_name: str,
#     model: str,
#     provider_lane: str = "default",
#     prompt_template: str = "",
#     token_budget: int = 0,
#     run_dir: Optional[Path] = None,
#     # W3.P1: optional identity fields for receipt
#     request_id: str = "",
#     trace_id: str = "",
# ) -> PromptBOM:
#     """Capture a PromptBOM for an LLM invocation and optionally write to disk.
# 
#     Args:
#         hop_name: Name of the HOP making this call (e.g. "H3_orchestrator").
#         model: Model identifier (e.g. "claude-3-5-sonnet-20241022").
#         provider_lane: Provider lane string.
#         prompt_template: The prompt template text (hashed, not stored).
#         token_budget: Max tokens budgeted for this call.
#         run_dir: If provided, writes the BOM to {run_dir}/prompt_bom/{hop_name}.json.
#         request_id: Optional request ID for PA boundary receipt (W3.P1).
#         trace_id: Optional trace ID for PA boundary receipt (W3.P1).
# 
#     Returns:
#         The captured PromptBOM with pa_boundary_receipt populated.
#     """
#     template_hash = hashlib.sha256(prompt_template.encode()).hexdigest()[:16]
# 
#     # W3.P1: Emit PA boundary receipt for BOM capture (lineage evidence).
#     # This path captures minimum provenance for narrative-pipeline instrumentation.
#     # Many fields are NOT_BOUND because the narrative pipeline does not use
#     # the full canonical PA compiler path.
#     pa_receipt = make_pa_boundary_receipt(
#         request_id=request_id or "NOT_BOUND",
#         run_id="NOT_BOUND",  # BOM capture: run_id not available
#         trace_id=trace_id or "NOT_BOUND",
#         route_id="NOT_BOUND",  # BOM capture: route_id not available
#         policy_hash="NOT_BOUND",  # BOM capture: no policy hash
#         blueprint_hash="NOT_BOUND",  # BOM capture: no blueprint hash
#         prompt_hash=template_hash,  # available: template hash
#         compiled_artifact_hash="NOT_BOUND",  # BOM capture: no compiled artifact
#         bom_hash="NOT_BOUND",  # BOM capture: this IS the BOM
#         registry_hash="NOT_BOUND",  # BOM capture: no registry
#         template_hash=template_hash,  # available
#         source_refs={
#             "hop_name": hop_name,
#             "model": model,
#             "provider_lane": provider_lane,
#         },
#         lineage_refs={
#             "pa_local_consumer": "apps_rg.prompt_assembly.pa_local.capture_prompt_bom",
#             "narrative_pipeline": "true",
#         },
#         status=PABoundaryStatus.PA_BOM_RESOLVED,
#         reason_codes=["BOM_CAPTURE", "NARRATIVE_PIPELINE_INSTRUMENTATION"],
#         unavailable_fields=[
#             "run_id", "route_id", "policy_hash", "blueprint_hash",
#             "compiled_artifact_hash", "bom_hash", "registry_hash",
#         ],
#     )
# 
#     bom = PromptBOM(
#         hop_name=hop_name,
#         model=model,
#         provider_lane=provider_lane,
#         prompt_template_hash=template_hash,
#         token_budget=token_budget,
#         pa_boundary_receipt=pa_receipt.to_dict(),
#     )
# 
#     if run_dir is not None:
#         _write_bom(bom, run_dir)
# 
#     _log.debug(
#         "[pa_local] BOM captured for %s with receipt_digest=%s",
#         hop_name,
#         pa_receipt.deterministic_digest,
#     )
# 
#     return bom
# 
# 
# def _write_bom(bom: PromptBOM, run_dir: Path) -> None:
#     """Write BOM to {run_dir}/prompt_bom/{hop_name}.json."""
#     try:
#         bom_dir = run_dir / "prompt_bom"
#         bom_dir.mkdir(parents=True, exist_ok=True)
#         out_path = bom_dir / f"{bom.hop_name}.json"
#         out_path.write_text(
#             json.dumps(bom.to_dict(), indent=2, default=str),
#             encoding="utf-8",
#         )
#         _log.debug("[pa_local] Wrote prompt_bom: %s", out_path)
#     except OSError as exc:
#         _log.warning("[pa_local] Failed to write prompt_bom for %s: %s", bom.hop_name, exc)
# 
# 
# __all__ = ["PromptBOM", "capture_prompt_bom"]
# 