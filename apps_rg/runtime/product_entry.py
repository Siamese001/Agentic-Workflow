"""Canonical Apps RG product entry with an unavoidable signed preflight."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from apps_rg.runtime.runtime_proof_layout import (
    allocate_full_resume_artifact_dir,
    find_repo_root,
)


def _baseline_ref(repo_root: Path) -> Path:
    raw = Path(
        str(
            os.environ.get("APPS_RG_E2E_BASELINE_REF")
            or "apps_rg/config/e2e_baselines/anthropic_partnership.v1.json"
        )
    )
    return raw.resolve() if raw.is_absolute() else (repo_root / raw).resolve()


def _non_fresh_artifact_dir_result(artifact_dir: Path) -> dict[str, Any]:
    return {
        "exit_status": "error",
        "execution_status": "failed",
        "outcome_authorized": False,
        "product_authorized": False,
        "pipeline_complete": False,
        "observability_repair_required": False,
        "completion_status": "BLOCKED",
        "fault": "PRODUCT_ARTIFACT_DIR_NOT_FRESH",
        "completion_fault": "PRODUCT_ARTIFACT_DIR_NOT_FRESH",
        "artifact_dir": str(artifact_dir),
        "authority_contract_id": "apps_research_rg_e2e_authority",
    }


def run_product_whole_run_from_primitives(
    *,
    target_company: str,
    target_role: str,
    target_level: str = "",
    jd: str = "",
    job_description_ref: str = "",
    job_description_text: str = "",
    manual_brief: str = "",
    resume_path: str = "",
    source_resume_text: str = "",
    generation_mode: str = "strategic_tailor",
    artifact_dir: str = "",
) -> dict[str, Any]:
    """Run preflight and the only product-authorizing whole-run orchestrator."""

    repo = find_repo_root()
    art = allocate_full_resume_artifact_dir(repo, artifact_dir)
    if art.exists() and any(art.iterdir()):
        return _non_fresh_artifact_dir_result(art)
    art.mkdir(parents=True, exist_ok=True)

    from apps_rg.runtime.e2e_preflight import (
        E2E_PREFLIGHT_CONTINUATION_RECEIPT_FILENAME,
        run_fresh_e2e_preflight,
    )
    from apps_rg.runtime.live_judge_only_guard import assert_production_runtime

    preflight = run_fresh_e2e_preflight(
        artifact_dir=art,
        e2e_run_id=art.name,
        repo_root=repo,
        baseline_ref=_baseline_ref(repo),
        runtime_check=lambda: assert_production_runtime(
            context="apps_rg product dispatch"
        ),
    )
    if not preflight.passed:
        result = dict(preflight.result)
        result.setdefault("product_authorized", False)
        result.setdefault("pipeline_complete", False)
        result.setdefault("observability_repair_required", False)
        result["authority_contract_id"] = "apps_research_rg_e2e_authority"
        return result

    from apps_rg.runtime.orchestration.r3r4_whole_run_orchestration import (
        run_whole_run_with_route_governance,
    )

    os.environ["APPS_RG_WHOLE_RUN_ENVELOPE"] = "1"
    result = run_whole_run_with_route_governance(
        target_company=target_company,
        target_role=target_role,
        target_level=target_level,
        jd=jd,
        job_description_ref=job_description_ref,
        job_description_text=job_description_text,
        manual_brief=manual_brief,
        resume_path=resume_path,
        source_resume_text=source_resume_text,
        generation_mode=generation_mode,
        artifact_dir=str(art),
        preflight_continuation_ref=str(
            art / E2E_PREFLIGHT_CONTINUATION_RECEIPT_FILENAME
        ),
        require_fresh_preflight=True,
    )
    result["authority_contract_id"] = "apps_research_rg_e2e_authority"
    return result


__all__ = ["run_product_whole_run_from_primitives"]
