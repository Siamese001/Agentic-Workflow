"""Phase 1 — in-process modular lane helpers (apps_rg only; no l2 envelope).

Real lane execution uses ``run_canonical_apps_rg_from_cli_primitives`` (same as ``python -m apps_rg``);
``run_dispatch_main`` raises ImportError (retired).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ModularLaneTargeting:
    """JD / briefing / title context passed to every section dispatch (mirrors PA U0 ``jd_requirements``)."""

    target_company: str = ""
    target_title: str = ""
    jd_text: str = ""
    jd_source: str = ""
    jd_digest: str = ""
    jd_ref_used: str = ""
    briefing_text: str = ""
    briefing_source: str = ""
    briefing_digest: str = ""
    briefing_ref_used: str = ""


def _recipe_briefing_ref(context: dict[str, Any]) -> str | None:
    ref = str(
        context.get("briefing_artifact_ref")
        or context.get("manual_brief")
        or context.get("manual_brief_path")
        or ""
    ).strip()
    return ref or None


def _recipe_job_description_ref(context: dict[str, Any]) -> str | None:
    r = str(context.get("job_description_ref") or "").strip()
    return r or None


def _recipe_job_description_text(context: dict[str, Any]) -> str | None:
    t = str(
        context.get("job_description_text") or context.get("jd_text") or ""
    ).strip()
    return t or None


def _recipe_jd_data(context: dict[str, Any]) -> str | None:
    d = str(context.get("jd_data") or "").strip()
    return d or None


def phase1_manual_brief_for_dispatch(targeting: ModularLaneTargeting | None) -> str:
    """Briefing argument for in-process Phase-1 lane dispatch.

    Prefer the resolved filesystem path (same as ``python -m apps_rg --manual-brief <path>``)
    so executive_summary dispatch matches section-mode CLI wiring. Fall back to inline text
    when no on-disk ref exists.
    """
    if targeting is None:
        return ""
    ref = str(targeting.briefing_ref_used or "").strip()
    if ref and ref not in {"inline:text"}:
        path = Path(ref)
        if path.is_file():
            return str(path)
    return str(targeting.briefing_text or "").strip()


def phase1_jd_dispatch_refs(targeting: ModularLaneTargeting | None) -> tuple[str, str]:
    """Return ``(job_description_ref, job_description_text)`` for Phase-1 lane dispatch."""
    if targeting is None:
        return "", ""
    ref = str(targeting.jd_ref_used or "").strip()
    if ref and not ref.startswith("inline:"):
        path = Path(ref)
        if path.is_file():
            return str(path), ""
    return "", str(targeting.jd_text or "").strip()


def modular_lane_targeting_from_recipe_context(context: dict[str, Any]) -> ModularLaneTargeting:
    """Derive CLI targeting flags from ``resolve_l2_recipe`` context (``jd_data``, ``briefing_artifact_ref``, etc.)."""
    tc = str(context.get("target_company") or "").strip()
    tr = str(context.get("target_role") or "").strip()
    from apps_rg.runtime.briefing_resolution import resolve_briefing_for_lanes
    from apps_rg.runtime.jd_resolution import resolve_jd_for_lanes

    jd_resolved = resolve_jd_for_lanes(
        job_description_ref=_recipe_job_description_ref(context),
        job_description_text=_recipe_job_description_text(context),
        jd_data=_recipe_jd_data(context),
        target_company=tc,
        target_role=tr,
    )
    title = jd_resolved.title or tr
    resolved = resolve_briefing_for_lanes(briefing_artifact_ref=_recipe_briefing_ref(context))
    return ModularLaneTargeting(
        target_company=jd_resolved.company or tc,
        target_title=title,
        jd_text=jd_resolved.description,
        jd_source=jd_resolved.jd_source.value,
        jd_digest=jd_resolved.jd_digest,
        jd_ref_used=jd_resolved.ref_used,
        briefing_text=resolved.text,
        briefing_source=resolved.briefing_source.value,
        briefing_digest=resolved.briefing_digest,
        briefing_ref_used=resolved.ref_used,
    )


def build_modular_lane_argv(*, provider: str, targeting: ModularLaneTargeting | None = None) -> list[str]:
    """Argv tokens historically passed to legacy dispatch CLIs (metadata / inventories only)."""
    pv = str(provider or "").strip().lower()
    if pv and pv != "qwen_vllm":
        raise ValueError(f"Unsupported modular lane provider {provider!r} (expected qwen_vllm).")
    argv: list[str] = ["--provider", "qwen_vllm", "--allow-non-allow-exit-zero"]
    if targeting is None:
        return argv
    if targeting.target_company:
        argv.extend(["--target-company", targeting.target_company])
    if targeting.target_title:
        argv.extend(["--target-title", targeting.target_title])
    if targeting.jd_text:
        argv.extend(["--jd-text", targeting.jd_text])
    if targeting.briefing_text:
        argv.extend(["--briefing", targeting.briefing_text])
    return argv


def lane_argv_for_provider(*, provider: str) -> list[str]:
    """Backward-compatible: provider flags only (no JD/brief — dispatch defaults apply)."""
    return build_modular_lane_argv(provider=provider, targeting=None)


def run_dispatch_main(module_qualname: str, argv: list[str]) -> int:  # noqa: ARG001
    """Removed — legacy ``*-dispatch.main`` is not callable."""
    raise ImportError(
        f"run_dispatch_main is retired ({module_qualname!r}). "
        "Use: python -m apps_rg --section <lane>"
    )


def resolve_latest_lane_run_dir(
    repo: Path,
    sections_root: Path,
    lane: str,
    *,
    lane_provider: str = "qwen_vllm",
) -> Path:
    """Pick run dir from per-lane pointers under ``sections_root/<lane>/``.

    Product fail-closed: ``latest_successful_real_run.json`` only (accepted REAL_LLM bundle).
    Legacy/test: may fall back to latest_real_run / latest_mock_run.
    """
    from apps_rg.runtime.product_output_policy import (
        lane_run_dir_meets_product_bar,
        product_fail_closed_runtime,
    )
    _ = str(lane_provider or "qwen_vllm").strip().lower()  # reserved for future provider-specific ordering
    if product_fail_closed_runtime():
        ptr_order = ("latest_successful_real_run.json",)
    else:
        ptr_order = (
            "latest_successful_real_run.json",
            "latest_real_run.json",
            "latest_mock_run.json",
        )
    for ptr in ptr_order:
        p = sections_root / lane / ptr
        if not p.is_file():
            continue
        raw = json.loads(p.read_text(encoding="utf-8"))
        rel = raw.get("run_dir") if isinstance(raw, dict) else None
        if isinstance(rel, str):
            rd = (repo / rel).resolve()
            if not rd.is_dir() or not (rd / "l2_output.json").is_file():
                continue
            if product_fail_closed_runtime():
                ok, reason = lane_run_dir_meets_product_bar(rd)
                if not ok:
                    msg = f"lane {lane!r} run_dir failed product bar ({ptr}): {reason}"
                    raise FileNotFoundError(msg)
            return rd
    msg = f"no resolvable run_dir pointer for lane {lane!r} under {sections_root}"
    raise FileNotFoundError(msg)


def build_section_provider_call_record(
    *,
    lane: str,
    candidate_index: int,
    run_dir: Path,
    artifact_dir: Path,
    self_consistency_requested: int,
    self_consistency_executed: int,
    provider_profile: str,
) -> dict[str, Any]:
    """One row for ``section_provider_calls.json`` (Phase 1 schema)."""
    l2p = run_dir / "l2_output.json"
    prov: dict[str, Any] = {}
    pr_path = run_dir / "provider_request.json"
    if pr_path.is_file():
        try:
            loaded = json.loads(pr_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            loaded = {}
        if isinstance(loaded, dict):
            prov = loaded
    prv_resp: dict[str, Any] = {}
    pr_resp_path = run_dir / "provider_response.json"
    if pr_resp_path.is_file():
        try:
            loaded2 = json.loads(pr_resp_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            loaded2 = {}
        if isinstance(loaded2, dict):
            prv_resp = loaded2
    compiled = run_dir / "compiled_prompt.txt"
    prompt_chars = len(compiled.read_text(encoding="utf-8")) if compiled.is_file() else 0

    reasoning_execution_receipt_ref: str | None = None
    trace_path = run_dir / "prompt_selection_trace.json"
    if trace_path.is_file():
        try:
            tr = json.loads(trace_path.read_text(encoding="utf-8"))
            rec = tr.get("reasoning_execution_receipt") if isinstance(tr, dict) else None
            if rec is not None:
                reasoning_execution_receipt_ref = trace_path.relative_to(artifact_dir).as_posix()
        except (json.JSONDecodeError, OSError, ValueError):
            reasoning_execution_receipt_ref = None

    l2: dict[str, Any] = {}
    if l2p.is_file():
        try:
            loaded3 = json.loads(l2p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            loaded3 = {}
        if isinstance(loaded3, dict):
            l2 = loaded3

    provider_req = str(prov.get("provider_requested") or provider_profile).strip().lower()
    attempted_any = prov.get("provider_attempted")
    provider_call_attempted: bool
    if isinstance(attempted_any, bool):
        provider_call_attempted = attempted_any
    else:
        provider_call_attempted = provider_req == "qwen_vllm"

    model_id = str(prv_resp.get("model") or prov.get("model") or "")
    max_t = prv_resp.get("max_tokens", prov.get("max_tokens", 0))
    max_tokens = int(max_t) if max_t is not None else 0
    temp_raw = prv_resp.get("temperature", prov.get("temperature", 0.0))
    temperature = float(temp_raw) if temp_raw is not None else 0.0
    top_raw = prv_resp.get("top_p", prov.get("top_p", 1.0))
    top_p = float(top_raw) if top_raw is not None else 1.0
    response_format_sent = prov.get("response_format") or prv_resp.get("response_format")
    generation_status = str(l2.get("runtime_generation_status") or "UNKNOWN")
    parsed_output_shape = str(l2.get("section_id") or lane)

    section_schema_validation_status = "unknown"
    x2p = run_dir / "x2_gate_outputs.json"
    if x2p.is_file():
        try:
            x2 = json.loads(x2p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            x2 = {}
        if isinstance(x2, dict):
            failed = int(x2.get("x2_failed") or 0)
            section_schema_validation_status = "lane_x2_pass" if failed == 0 else "lane_x2_fail"
        elif isinstance(x2, list):
            failed_ct = sum(1 for g in x2 if isinstance(g, dict) and not g.get("pass", True))
            section_schema_validation_status = "lane_x2_pass" if failed_ct == 0 else "lane_x2_fail"

    decisive_reason_code = "UNKNOWN"
    x3p = run_dir / "x3_disposition.json"
    if x3p.is_file():
        try:
            x3 = json.loads(x3p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            x3 = {}
        if isinstance(x3, dict):
            decisive_reason_code = str(x3.get("x3_code") or "UNKNOWN")

    output_ref = l2p.relative_to(artifact_dir).as_posix()

    return {
        "section_lane": lane,
        "provider_call_attempted": provider_call_attempted,
        "provider_profile": provider_profile + "_section_lane",
        "model_id": model_id,
        "candidate_index": candidate_index,
        "self_consistency_requested": self_consistency_requested,
        "self_consistency_executed": self_consistency_executed,
        "prompt_chars": prompt_chars,
        "prompt_truncated": False,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": top_p,
        "response_format_sent": response_format_sent,
        "generation_status": generation_status,
        "parsed_output_shape": parsed_output_shape,
        "section_schema_validation_status": section_schema_validation_status,
        "decisive_reason_code": decisive_reason_code,
        "output_ref": output_ref,
        "reasoning_execution_receipt_ref": reasoning_execution_receipt_ref,
    }


__all__ = [
    "ModularLaneTargeting",
    "build_modular_lane_argv",
    "build_section_provider_call_record",
    "lane_argv_for_provider",
    "modular_lane_targeting_from_recipe_context",
    "phase1_jd_dispatch_refs",
    "phase1_manual_brief_for_dispatch",
    "resolve_latest_lane_run_dir",
    "run_dispatch_main",
]
