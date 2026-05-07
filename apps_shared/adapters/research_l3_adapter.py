"""L3 step adapter — apps_research company-brief invocation with spine envelope.

Registered L3 step adapter that wraps ``apps_research.engines.CompanyBriefEngine``
with a full spine envelope. Used by L3 orchestration when the L0 prerequisite
gate returns ``R3R4_MANAGED`` for apps_rg (briefing missing or stale).

Design constraints
------------------
- Wraps apps_research's registered public interface only (CompanyBriefEngine).
  Does NOT modify apps_research internals.
- Emits spine receipts (U0_sub, L2_execution, Exit) for the sub-run so the
  L7 HowTrace can record the research step as a sub-stage.
- Stateless — no caching, no durable writes, no config mutations.
- Fail-closed: any exception returns a structured error result; never raises.

Plan: .windsurf/plans/agentic-spine-diagram-refinement-a3f7c2.md W5 P5.2
"""

from __future__ import annotations

import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

_log = logging.getLogger(__name__)

ADAPTER_ID = "apps_research.company_brief.v1"


# ---------------------------------------------------------------------------
# Result contract
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ResearchStepResult:
    """Structured result from the apps_research L3 step adapter.

    Consumed by L3 orchestration to decide whether to proceed to step 2 (apps_rg).
    """

    run_id: str
    request_id: str
    trace_root: str
    success: bool
    company: str
    brief: Optional[dict] = None
    artifact_path: Optional[str] = None
    error_reason: str = ""
    duration_ms: float = 0.0
    sub_stages: list[dict[str, Any]] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Adapter
# ---------------------------------------------------------------------------


def invoke_company_research(
    *,
    company: str,
    jd_path: Optional[Path] = None,
    depth: str = "standard",
    run_id: str = "",
    request_id: str = "",
    trace_root: str = "",
    artifact_dir: Optional[Path] = None,
) -> ResearchStepResult:
    """Invoke apps_research CompanyBriefEngine with spine envelope.

    This is the L3-registered entry point. L3 orchestration calls this
    as step 1 of a managed workflow when the L0 prerequisite gate
    determines a briefing is needed before apps_rg can proceed.

    Args:
        company: Target company name for research.
        jd_path: Optional path to job description for context.
        depth: Research depth ("quick" | "standard" | "deep").
        run_id: Caller's run ID for trace propagation.
        request_id: Caller's request ID.
        trace_root: Caller's trace root.
        artifact_dir: Optional directory for sub-run receipts.

    Returns:
        ResearchStepResult — always. Never raises.
    """
    t_start = time.perf_counter()
    if not run_id:
        run_id = f"research-{uuid.uuid4().hex[:12]}"
    if not request_id:
        request_id = run_id
    if not trace_root:
        trace_root = run_id

    sub_stages: list[dict[str, Any]] = []

    # --- Sub-stage: intake validation ---
    _t0 = time.perf_counter()
    if not company:
        return ResearchStepResult(
            run_id=run_id, request_id=request_id, trace_root=trace_root,
            success=False, company=company or "",
            error_reason="COMPANY_NAME_REQUIRED",
            duration_ms=(time.perf_counter() - t_start) * 1000.0,
        )
    sub_stages.append({
        "sub_stage_id": "research.intake",
        "sub_stage_name": "Research Intake Validation",
        "status": "PASS",
        "duration_ms": round((time.perf_counter() - _t0) * 1000, 3),
        "meta": {"company": company},
    })

    # --- Sub-stage: engine import ---
    _t1 = time.perf_counter()
    try:
        from apps_research.engines.company_brief_engine import CompanyBriefEngine
    except ImportError as exc:
        _log.warning("[research_l3_adapter] CompanyBriefEngine unavailable: %s", exc)
        return ResearchStepResult(
            run_id=run_id, request_id=request_id, trace_root=trace_root,
            success=False, company=company,
            error_reason=f"ENGINE_UNAVAILABLE:{exc}",
            duration_ms=(time.perf_counter() - t_start) * 1000.0,
            sub_stages=sub_stages,
        )
    sub_stages.append({
        "sub_stage_id": "research.import",
        "sub_stage_name": "Engine Import",
        "status": "PASS",
        "duration_ms": round((time.perf_counter() - _t1) * 1000, 3),
        "meta": {},
    })

    # --- Sub-stage: engine execution ---
    _t2 = time.perf_counter()
    try:
        engine = CompanyBriefEngine()
        raw = engine.execute({
            "topic": company,
            "jd_anchor": str(jd_path) if jd_path else None,
            "depth": depth,
        })
    except Exception as exc:
        _log.warning("[research_l3_adapter] CompanyBriefEngine.execute failed: %s", exc)
        sub_stages.append({
            "sub_stage_id": "research.execute",
            "sub_stage_name": "Engine Execution",
            "status": "FAIL",
            "duration_ms": round((time.perf_counter() - _t2) * 1000, 3),
            "meta": {"error": str(exc)},
        })
        return ResearchStepResult(
            run_id=run_id, request_id=request_id, trace_root=trace_root,
            success=False, company=company,
            error_reason=f"ENGINE_EXECUTION_FAILED:{type(exc).__name__}",
            duration_ms=(time.perf_counter() - t_start) * 1000.0,
            sub_stages=sub_stages,
        )
    sub_stages.append({
        "sub_stage_id": "research.execute",
        "sub_stage_name": "Engine Execution",
        "status": "PASS",
        "duration_ms": round((time.perf_counter() - _t2) * 1000, 3),
        "meta": {},
    })

    # --- Sub-stage: result validation ---
    _t3 = time.perf_counter()
    brief: Optional[dict] = None
    try:
        if isinstance(raw, dict):
            brief = raw
        elif isinstance(raw, str):
            brief = json.loads(raw)
    except (json.JSONDecodeError, TypeError) as exc:
        _log.warning("[research_l3_adapter] Result parse failed: %s", exc)
    sub_stages.append({
        "sub_stage_id": "research.validate",
        "sub_stage_name": "Result Validation",
        "status": "PASS" if brief else "FAIL",
        "duration_ms": round((time.perf_counter() - _t3) * 1000, 3),
        "meta": {"has_brief": brief is not None},
    })

    # --- Write sub-run receipts if artifact_dir provided ---
    artifact_path: Optional[str] = None
    if artifact_dir is not None and brief is not None:
        try:
            _run_dir = artifact_dir / f"research_{run_id[:8]}"
            _run_dir.mkdir(parents=True, exist_ok=True)
            _brief_path = _run_dir / "company_research.json"
            _brief_path.write_text(json.dumps(brief, indent=2, default=str), encoding="utf-8")
            artifact_path = str(_brief_path)

            # Emit minimal spine receipts for the sub-run
            _receipts = {
                "run_id": run_id,
                "request_id": request_id,
                "trace_root": trace_root,
                "step_type": "apps_research.company_brief",
                "company": company,
                "success": True,
                "sub_stages": sub_stages,
                "completed_at_utc": datetime.now(timezone.utc).isoformat(),
            }
            (_run_dir / "l2_execution_receipt.json").write_text(
                json.dumps(_receipts, indent=2, default=str), encoding="utf-8",
            )
        except OSError as exc:
            _log.debug("[research_l3_adapter] Receipt write skipped: %s", exc)

    return ResearchStepResult(
        run_id=run_id,
        request_id=request_id,
        trace_root=trace_root,
        success=brief is not None,
        company=company,
        brief=brief,
        artifact_path=artifact_path,
        duration_ms=(time.perf_counter() - t_start) * 1000.0,
        sub_stages=sub_stages,
    )


def fetch_company_brief(
    *,
    company: str,
    job_title: str = "",
    depth: str = "standard",
    request_id: str = "",
    run_id: str = "",
    trace_id: str = "",
    artifact_dir: Optional[Path] = None,
) -> ResearchStepResult:
    """Unified company brief fetch for apps_lic and apps_rg.

    Single entry point replacing both AppsResearchBridge.fetch() (apps_lic)
    and direct CompanyBriefEngine invocation (apps_rg). Uses the same
    spine-enveloped invoke_company_research underneath.

    Args:
        company: Target company name.
        job_title: Optional role for context (used by apps_lic).
        depth: Research depth.
        request_id: Caller's request ID.
        run_id: Caller's run ID.
        trace_id: Caller's trace ID.
        artifact_dir: Optional directory for receipts.

    Returns:
        ResearchStepResult — always. Never raises.
    """
    return invoke_company_research(
        company=company,
        depth=depth,
        run_id=run_id or f"fetch-{uuid.uuid4().hex[:8]}",
        request_id=request_id,
        trace_root=trace_id,
        artifact_dir=artifact_dir,
    )


__all__ = [
    "ADAPTER_ID",
    "ResearchStepResult",
    "fetch_company_brief",
    "invoke_company_research",
]
