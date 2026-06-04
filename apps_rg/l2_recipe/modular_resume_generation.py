"""Phase 0 modular R4 API — shared runner (artifact-local; optional via ``GenerateResumeStep`` flag).

PHASE0_SMOKE_ONLY: synthetic lane payloads here are wiring stubs — forbidden as product-shape proof.

Writes **only** under ``Path(artifact_dir) / \"modular_r4\"`` for pipeline artifacts
(does not use ``artifacts/apps_rg/runtime_proofs`` for canonical outputs).

See ``.cursor/plans/apps-rg-r4-modular-section-migration-d4e8a1.md``.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Final

from apps_rg.l2_recipe.modular_lane_adapter import (
    ModularLaneTargeting,
    build_modular_lane_argv,
    build_section_provider_call_record,
    phase1_jd_dispatch_refs,
    phase1_manual_brief_for_dispatch,
    resolve_latest_lane_run_dir,
)
from apps_rg.l2_recipe.modular_lane_recipe_policy import summarize_modular_lane_recipe_policy
from apps_rg.l2_recipe.modular_r4_generation_result import ModularR4GenerationResult
from apps_rg.l2_recipe.modular_rg_output_builder import (
    build_rg_output_from_modular_sections,
    load_lane_l2_from_section_refs,
)
from apps_rg.l2_recipe.rg_output_jsonschema_validate import validate_rg_output_object
from apps_rg.runtime.internal.final_resume_assembler import assemble_final_resume
from apps_rg.runtime.assembly.final_resume_manifest import FinalResumePaths
from apps_rg.runtime.internal.locked_copy_builder import build_locked_copy
from apps_rg.runtime.orchestration.canonical_dispatch import run_canonical_apps_rg_from_cli_primitives
from apps_rg.runtime.internal.generated_lane_rollup import (
    GENERATED_LANES,
    build_modular_lane_rollup,
)
from apps_rg.runtime.resume_resolution import load_lane_base_resume_json
from apps_rg.runtime.run_bundle_index import repo_relative_posix
from apps_rg.runtime.runtime_proof_layout import (
    MODULAR_R4_SECTIONS_ROOT_ENV,
    resolve_phase1_sections_root,
)
from apps_rg.runtime.section_cli_defaults import (
    CLI_PROVIDER_RESOLUTION_CLI_OVERRIDE,
    resolve_cli_x1d_judges,
)
from apps_rg.runtime.section_lane_temperature import default_temperature_for_section
from apps_rg.runtime.sections_root_manifest import emit_sections_root_manifest, log_sections_manifest_write_failed

# Same seven modules as ``apps_rg.runtime.internal.lane_batch`` (single SSOT).
# competencies_dispatch remains listed for legacy argparse/import tooling parity — canonical lane runtime:
# apps_rg.runtime.sections.competencies_lane (selected-section entry via python -m apps_rg --section competencies).
LANE_DISPATCH_MODULES: Final[tuple[str, ...]] = (
    "apps_rg.runtime.sections.headline_lane",
    "apps_rg.runtime.sections.executive_summary_lane",
    "apps_rg.runtime.sections.unify_bullets_lane",
    "apps_rg.runtime.sections.unify_narrative_lane",
    "apps_rg.runtime.sections.ibm_bullets_lane",
    "apps_rg.runtime.sections.ibm_narrative_lane",
    "apps_rg.runtime.sections.competencies_lane",
)


PHASE0_PATH_INVENTORY_NOTES: dict[str, Any] = {
    "subprocess_cwd": (
        "modular Phase1 invokes in-process run_canonical_apps_rg_from_cli_primitives per lane "
        "(same surface as python -m apps_rg --section); offline batch is tests.helpers.offline_lane_orchestration only; "
        "lane order matches GENERATED_LANES."
    ),
    "runtime_proofs_strings": [
        "orchestrate_full_resume.RUNTIME_PROOFS = artifacts/apps_rg/runtime_proofs",
        "generated_lane_rollup.RUNTIME_PROOFS under repo/artifacts/.../runtime_proofs",
        "locked_copy_builder.ARTIFACT_REL = artifacts/apps_rg/runtime_proofs/locked_copy",
        "final_resume_manifest.DEFAULT_*_REL under runtime_proofs",
        "resume_package_manifest.RUNTIME_PROOFS",
    ],
    "lane_run_layout": "artifacts/apps_rg/runtime_proofs/<lane>/{real|mock}/<run_id>/",
    "r4_modular_replacement": (
        "run_modular_resume_generation writes under artifact_dir/modular_r4 only; "
        "no runtime_proofs dependency for canonical R4 modular outputs when this API is used."
    ),
    "modular_r4_sections_env": (
        f"When {MODULAR_R4_SECTIONS_ROOT_ENV} is set, dispatch prepare/finalize scope pointers "
        "to <env_root>/<lane>/latest_*.json and run directories under "
        "<env_root>/<lane>/{{mock|real}}/<run_id>/ (Phase 1 real lane invocation)."
    ),
}


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _rel_under_repo(path: Path, repo: Path) -> str:
    try:
        return path.resolve().relative_to(repo.resolve()).as_posix()
    except ValueError:
        return str(path.resolve()).replace("\\", "/")


def _phase0_stub_lane_record(lane: str, i: int) -> dict[str, Any]:
    return {
        "section_lane": lane,
        "provider_call_attempted": False,
        "provider_profile": "phase0_synthetic",
        "model_id": "none",
        "candidate_index": i,
        "self_consistency_requested": 1,
        "self_consistency_executed": 0,
        "prompt_chars": 0,
        "prompt_truncated": False,
        "max_tokens": 0,
        "temperature": 0.0,
        "top_p": 1.0,
        "response_format_sent": None,
        "generation_status": "PHASE0_SYNTHETIC_STUB",
        "parsed_output_shape": "lane_l2_stub",
        "section_schema_validation_status": "skipped_phase0",
        "decisive_reason_code": "PHASE0_NO_PROVIDER",
        "output_ref": f"modular_r4/lanes/{lane}/real/phase0_synthetic/l2_output.json",
        "reasoning_execution_receipt_ref": None,
    }


def _phase1_missing_lane_record(
    lane: str,
    i: int,
    sc_req: int,
    sc_exe: int,
    prof: str,
    *,
    decisive_reason_code: str = "PHASE1_NO_RUN_DIR",
) -> dict[str, Any]:
    return {
        "section_lane": lane,
        "provider_call_attempted": False,
        "provider_profile": f"{prof}_section_lane",
        "model_id": "",
        "candidate_index": i,
        "self_consistency_requested": sc_req,
        "self_consistency_executed": sc_exe,
        "prompt_chars": 0,
        "prompt_truncated": False,
        "max_tokens": 0,
        "temperature": 0.0,
        "top_p": 1.0,
        "response_format_sent": None,
        "generation_status": "MISSING_LANE_RUN",
        "parsed_output_shape": "none",
        "section_schema_validation_status": "missing",
        "decisive_reason_code": str(decisive_reason_code or "PHASE1_NO_RUN_DIR"),
        "output_ref": "",
        "reasoning_execution_receipt_ref": None,
    }


def _phase1_lane_dispatch_status(result: dict[str, Any] | None) -> str:
    """Summarize in-process lane dispatch for ``phase1_lane_inventory``."""
    res = result if isinstance(result, dict) else {}
    fault = str(res.get("fault") or "").strip()
    exit_st = str(res.get("exit_status") or "").strip().lower()
    if fault == "temperature_range":
        return "exit_2"
    if fault:
        return f"dispatch_error:{fault}"
    if exit_st == "error":
        return "dispatch_error:lane_exit_error"
    if exit_st == "success":
        return "ok"
    return f"dispatch_status:{exit_st or 'unknown'}"


def _phase1_materialize_lane_run_dir(
    *,
    repo: Path,
    sections_root: Path,
    integrated_dir: Path,
    lane: str,
    lane_provider: str,
    lane_dispatch_results: dict[str, dict[str, Any]],
    lane_exec_status: dict[str, str],
    emit_integrated_lane_pre_run_failure: Any,
    product_fail_closed: bool,
) -> Path | None:
    """Resolve lane run_dir from pointers for recipe rollup (decoupled from dispatch exit_status).

    ``phase1_aborted`` blocks subsequent **dispatch** waves only; every lane gets a resolve
    attempt so on-disk successes (e.g. executive_summary X3_ALLOW) are not hidden.
    """
    from apps_rg.l2_recipe.modular_lane_adapter import resolve_latest_lane_run_dir
    from apps_rg.runtime.product_output_policy import lane_run_dir_meets_product_bar

    try:
        run_dir = resolve_latest_lane_run_dir(
            repo,
            sections_root,
            lane,
            lane_provider=lane_provider,
        )
    except FileNotFoundError as exc:  # guardian: allow-return-none-swallow -- P2 burndown: fail-soft optional boundary
        lane_exec_status[lane] = f"{lane_exec_status.get(lane, '')}|missing_pointer:{exc}".strip(
            "|"
        )
        dispatch = lane_dispatch_results.get(lane) or {}
        fault = str(dispatch.get("fault") or "").strip()
        blocker = fault or "PHASE1_NO_RUN_DIR"
        if not fault and str(dispatch.get("exit_status") or "").lower() == "error":
            blocker = "LANE_DISPATCH_EXIT_ERROR"
        emit_integrated_lane_pre_run_failure(
            sections_root=sections_root,
            integrated_dir=integrated_dir,
            repo_root=repo,
            lane_id=lane,
            blocker=blocker,
            dispatch_result=dispatch,
            lane_exec_status=str(lane_exec_status.get(lane) or ""),
        )
        return None

    if product_fail_closed:
        ok, bar_reason = lane_run_dir_meets_product_bar(run_dir)
        if not ok:
            emit_integrated_lane_pre_run_failure(
                sections_root=sections_root,
                integrated_dir=integrated_dir,
                repo_root=repo,
                lane_id=lane,
                blocker=f"LANE_PRODUCT_BAR_FAILED:{bar_reason}",
                dispatch_result=lane_dispatch_results.get(lane) or {},
                lane_exec_status=lane_exec_status.get(lane, ""),
            )
            return None

    return run_dir


def _minimal_judge_blob() -> dict[str, Any]:
    return {
        "judges": [
            {"provider_key": "gemini_pro", "provider_status": "OK", "pass": True},
            {"provider_key": "openai_chatgpt", "provider_status": "OK", "pass": True},
            {"provider_key": "anthropic_claude", "provider_status": "OK", "pass": True},
        ],
    }


def _minimal_x2_blob() -> dict[str, Any]:
    return {
        "gate_family": "lane_x2_phase0_synthetic",
        "gates": [{"gate_id": "phase0_stub", "pass": True}],
        "x2_passed": 1,
        "x2_failed": 0,
        "total_x2_gates": 1,
        "failed_gates": [],
    }


def _minimal_l2_blob(lane: str, *, run_id: str) -> dict[str, Any]:
    common = {
        "run_id": run_id,
        "section_id": lane,
        "runtime_generation_status": "MOCKED",
        "product_quality_status": "PHASE0_SYNTHETIC",
    }
    if lane == "headline":
        return {**common, "headline_line": "Phase0 synthetic headline | R4 modular readiness"}
    if lane == "executive_summary":
        return {
            **common,
            "resume_display_text": (
                "Phase0 synthetic executive summary for modular R4 API readiness proof only."
            ),
        }
    if lane in ("unify_narrative", "ibm_narrative"):
        return {
            **common,
            "narrative_sentence": (
                "Phase0 synthetic narrative sentence with sufficient length for assembly proof."
            ),
        }
    if lane in ("unify_bullets", "ibm_bullets"):
        return {
            **common,
            "bullets": [
                {
                    "text": (
                        "Phase0 synthetic achievement bullet with enough characters for deterministic "
                        "merge and assembler gates."
                    ),
                    "source_fact_id": "phase0_synthetic",
                    "has_metric": False,
                },
                {
                    "text": (
                        "Second Phase0 bullet text to satisfy multi-bullet structural expectations "
                        "where applicable."
                    ),
                    "source_fact_id": "phase0_synthetic",
                    "has_metric": False,
                },
                {
                    "text": (
                        "Third Phase0 bullet text so list-based sections have minimal depth."
                    ),
                    "source_fact_id": "phase0_synthetic",
                    "has_metric": False,
                },
            ],
        }
    if lane == "competencies":
        return {
            **common,
            "competencies": [
                {
                    "category_label": "Phase0 Synthetic",
                    "terms": [{"text": "modular readiness", "source_fact_id": "phase0_synthetic"}],
                    "source_fact_ids": ["phase0_synthetic"],
                },
            ],
        }
    return common


def _write_synthetic_lane_bundle(repo: Path, modular_root: Path, lane: str) -> str:
    run_id = f"phase0_{lane}_synthetic"
    run_dir = modular_root / "lanes" / lane / "real" / "phase0_synthetic"
    run_dir.mkdir(parents=True, exist_ok=True)
    rid = run_id
    _write_json(run_dir / "l2_output.json", _minimal_l2_blob(lane, run_id=rid))
    _write_json(run_dir / "x2_gate_outputs.json", _minimal_x2_blob())
    _write_json(run_dir / "x1d_llm_judge_outputs.json", _minimal_judge_blob())
    _write_json(
        run_dir / "x3_disposition.json",
        {
            "x3_code": "X3_ALLOW",
            "authorization_scope": "PHASE0_SYNTHETIC",
            "runtime_generation_status": "MOCKED",
            "proceed_to_runtime": True,
        },
    )
    _write_json(run_dir / "l6_shadow_eval_package.json", {"offline_only": True})
    try:
        rel = run_dir.resolve().relative_to(repo.resolve()).as_posix()
    except ValueError:
        rel = run_dir.resolve().as_posix()
    return rel


def _synthetic_lane_row(repo: Path, modular_root: Path, lane: str) -> dict[str, Any]:
    rel_run = _write_synthetic_lane_bundle(repo, modular_root, lane)
    return {
        "lane_key": lane,
        "section_id": lane,
        "rollup_source_run_dir": rel_run,
        "latest_successful_real_artifact_path": rel_run,
        "accepted_real_evidence_resolution": "latest_successful_real_run.json",
        "runtime_generation_status": "MOCKED",
        "x2_passed": 1,
        "x2_failed": 0,
        "x2_total_gates": 1,
        "x2_failed_gate_ids": [],
        "x2_artifact_failed_gates": [],
        "gemini_provider_status": "OK",
        "openai_provider_status": "OK",
        "anthropic_provider_status": "OK",
        "soft_failed_judges": [],
        "blocked_judges": [],
        "x3_code": "X3_ALLOW",
        "authorization_scope": "PHASE0_SYNTHETIC",
        "proceed_to_runtime": True,
        "l6_offline_only": True,
        "artifact_refs": {n: f"{rel_run}/{n}" for n in [
            "l2_output.json",
            "x2_gate_outputs.json",
            "x1d_llm_judge_outputs.json",
            "x3_disposition.json",
            "l6_shadow_eval_package.json",
        ]},
    }


def _build_synthetic_rollup(repo: Path, modular_root: Path) -> dict[str, Any]:
    lanes = {lane: _synthetic_lane_row(repo, modular_root, lane) for lane in GENERATED_LANES}
    now = datetime.now(timezone.utc).isoformat()
    return {
        "rollup_id": f"phase0_generated_lane_rollup_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
        "generated_at_utc": now,
        "repo_root": str(repo.resolve()).replace("\\", "/"),
        "current_rollup_artifact_mode": "phase0_synthetic",
        "rollup_artifact_mode_arg": "phase0_synthetic",
        "lanes": lanes,
        "summary": {
            "lane_keys": list(GENERATED_LANES),
            "phase0_synthetic": True,
        },
    }


@dataclass
class ModularResumeInputPackage:
    """Inputs for modular generation (expanded in later phases)."""

    repo_root: Path
    target_company: str = ""
    target_role: str = ""
    jd_text: str | None = None
    briefing_text: str | None = None
    rg_output_fixture_path: Path | None = None


@dataclass
class ModularResumeProfile:
    """Execution profile (Phase 0 synthetic assembly + optional fixture validation)."""

    run_phase0_synthetic_assembly: bool = True
    validate_rg_output_fixture: bool = True
    phase1_invoke_real_lanes: bool = False
    phase1_lane_provider: str = "qwen_vllm"
    self_consistency_requested: int = 0
    parallel_phase1_lanes: bool = False
    phase1_max_parallel: int = 2
    phase1_allow_non_allow_exit_zero: bool = False


_PLUMBING_ASSEMBLY_PROVIDERS = frozenset({"mock", "mocked", "stub"})


def _assembly_plumbing_mode(profile: ModularResumeProfile, *, use_phase0_synthetic: bool) -> bool:
    """Real integrated Phase 1 never skips whole-résumé judges (fail-closed product)."""
    if profile.phase1_invoke_real_lanes:
        return False
    if use_phase0_synthetic:
        return True
    prov = str(profile.phase1_lane_provider or "").strip().lower()
    return prov in _PLUMBING_ASSEMBLY_PROVIDERS or prov.startswith("mock")


def _assemble_modular_final_resume(
    paths: FinalResumePaths,
    *,
    plumbing_mode: bool,
) -> dict[str, Any]:
    """Phase 0 / mock Phase 1: structural assembly only. Real Phase 1: aggregate full-resume judge."""
    saved: dict[str, str | None] = {}
    if plumbing_mode:
        for key in ("APPS_RG_ASSEMBLY_STRUCTURAL_ONLY", "APPS_RG_FULL_RESUME_LLM_COHERENCE_REVIEW"):
            saved[key] = os.environ.get(key)
        os.environ["APPS_RG_ASSEMBLY_STRUCTURAL_ONLY"] = "1"
        os.environ["APPS_RG_FULL_RESUME_LLM_COHERENCE_REVIEW"] = "0"
    try:
        return assemble_final_resume(paths, skip_preflight=plumbing_mode)
    finally:
        for key, val in saved.items():
            if val is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = val


def run_modular_resume_generation(
    input_package: ModularResumeInputPackage,
    artifact_dir: Path | str,
    run_id: str,
    profile: ModularResumeProfile | None = None,
    *,
    lane_targeting: ModularLaneTargeting | None = None,
) -> ModularR4GenerationResult:
    """Run Phase 0 modular pipeline under ``artifact_dir/modular_r4`` (R4-local).

    Does **not** call ``run_apps_rg_l2_envelope``. Does **not** write canonical
    outputs under ``runtime_proofs``. No DOCX export here.
    """
    profile = profile or ModularResumeProfile()
    repo = input_package.repo_root.resolve()
    art = Path(str(artifact_dir)).resolve()
    modular_root = art / "modular_r4"
    try:
        art.relative_to(repo)
    except ValueError as exc:
        raise ValueError(
            "artifact_dir must be inside input_package.repo_root for Phase 0 path-relative contracts "
            f"(got artifact_dir={art}, repo_root={repo})"
        ) from exc
    modular_root.mkdir(parents=True, exist_ok=True)

    rel_mod = modular_root.relative_to(repo).as_posix()

    _write_json(art / "modular_r4" / "phase0_path_inventory.json", PHASE0_PATH_INVENTORY_NOTES)

    use_phase0_synthetic = profile.run_phase0_synthetic_assembly and not profile.phase1_invoke_real_lanes
    real_lane_invocation_attempted = bool(profile.phase1_invoke_real_lanes)

    merge_receipt_rel: str | None = None
    assembly_gates_ok: bool | None = None
    section_output_refs: dict[str, str] = {}
    rollup_blob: dict[str, Any] | None = None
    section_call_records: list[dict[str, Any]] = []
    lane_exec_status: dict[str, str] = {}
    provider_call_total = 0
    locked_provider = False
    pass_source = ""
    merged_err = ""
    phase0_blocked_on_product_fail_closed = False
    lanes_executed = 0
    lane_outputs_valid = False
    final_merge_attempted = False
    rg_output_merge_receipt_rel: str | None = None

    if profile.phase1_invoke_real_lanes:
        sections_root = resolve_phase1_sections_root(art, modular_root)
        try:
            emit_sections_root_manifest(
                repo_root=repo,
                sections_root_abs=sections_root,
                source_env_literal=MODULAR_R4_SECTIONS_ROOT_ENV,
                correlation_id=None,
                integrated_run_ref=repo_relative_posix(repo, art.resolve()),
                run_links_ref=None,
                notes=f"scoped Phase 1 sections root modular_r4/{rel_mod}/sections (run_id={run_id})",
            )
        except OSError as exc:
            log_sections_manifest_write_failed("run_modular_resume_generation_phase1", exc)
            raise
        prev_env = os.environ.get(MODULAR_R4_SECTIONS_ROOT_ENV)
        os.environ[MODULAR_R4_SECTIONS_ROOT_ENV] = str(sections_root.resolve())
        lane_argv = build_modular_lane_argv(
            provider=profile.phase1_lane_provider,
            targeting=lane_targeting,
        )
        lane_run_dirs: dict[str, Path] = {}
        lane_dispatch_results: dict[str, dict[str, Any]] = {}  # guardian: allow-broad-exception -- P2 burndown: fail-soft optional boundary
        _ = lane_argv  # argv shape retained for phase1_lane_inventory metadata
        lane_mock_j_for_phase1 = False
        tc = str(lane_targeting.target_company or "") if lane_targeting is not None else ""
        tr = str(lane_targeting.target_title or "") if lane_targeting is not None else ""
        jd_ref, jd_txt = phase1_jd_dispatch_refs(lane_targeting)
        br_dispatch = phase1_manual_brief_for_dispatch(lane_targeting)
        x1d_eff = resolve_cli_x1d_judges(None)
        prev_whole_run_env = os.environ.get("APPS_RG_WHOLE_RUN_ENVELOPE")
        prev_corr_env = os.environ.get("APPS_RG_CORRELATED_CLI_RUN")
        os.environ["APPS_RG_WHOLE_RUN_ENVELOPE"] = "1"
        os.environ["APPS_RG_CORRELATED_CLI_RUN"] = _rel_under_repo(art, repo)
        try:
            from apps_rg.runtime.integrated_lane_evidence_packaging import (
                emit_integrated_lane_pre_run_failure,
            )

            from apps_rg.runtime.validators.companion_bullet_finalization import (
                PRE_RUN_UPSTREAM_NOT_FINALIZED_BLOCKER,
                companion_accepted_in_modular_sections_root,
            )
            from apps_rg.runtime.validators.ibm_bullets_x2 import IBM_BULLET_IDS
            from apps_rg.runtime.validators.unify_bullets_x2 import UNIFY_BULLET_IDS

            _narrative_upstream: dict[str, tuple[str, tuple[str, ...]]] = {
                "unify_narrative": ("unify_bullets", UNIFY_BULLET_IDS),
                "ibm_narrative": ("ibm_bullets", IBM_BULLET_IDS),
            }

            from apps_rg.runtime.product_output_policy import (
                PHASE1_PRIOR_LANE_FAILED_BLOCKER,
                lane_run_dir_meets_product_bar,
                phase1_dispatch_hard_failed,
                product_fail_closed_runtime,
            )

            phase1_aborted = False
            phase1_abort_reason = ""

            from apps_rg.runtime.orchestration.managed_section_lane_dispatcher import (
                dispatch_phase1_lanes_managed,
            )
            from apps_rg.runtime.orchestration.section_lane_concurrency import (
                phase1_parallel_enabled,
                resolve_max_parallel,
            )
            from apps_rg.runtime.orchestration.section_lane_executor import (
                LaneExecutionContext,
            )

            _parallel_phase1 = phase1_parallel_enabled(
                profile_flag=bool(profile.parallel_phase1_lanes)
            )
            _max_par = resolve_max_parallel(default=int(profile.phase1_max_parallel or 2))
            from apps_rg.runtime.section_cli_defaults import (
                resolve_phase1_lane_allow_non_allow_exit_zero,
            )

            _phase1_allow_exit = resolve_phase1_lane_allow_non_allow_exit_zero(
                bool(profile.phase1_allow_non_allow_exit_zero)
            )

            def _phase1_dispatch_one_lane(**kwargs: Any) -> dict[str, Any]:
                nonlocal phase1_aborted, phase1_abort_reason
                lane = str(kwargs.get("section") or "")
                if phase1_aborted:
                    return {"prior_abort": phase1_abort_reason, "exit_status": "error"}
                upstream_spec = _narrative_upstream.get(lane)
                if upstream_spec is not None:
                    upstream_lane, expected_ids = upstream_spec
                    if not companion_accepted_in_modular_sections_root(
                        repo,
                        sections_root,
                        upstream_section_id=upstream_lane,
                        expected_bullet_ids=expected_ids,
                    ):
                        emit_integrated_lane_pre_run_failure(
                            sections_root=sections_root,
                            integrated_dir=art,
                            repo_root=repo,
                            lane_id=lane,
                            blocker=PRE_RUN_UPSTREAM_NOT_FINALIZED_BLOCKER,
                            dispatch_result={
                                "fault": "upstream_not_finalized",
                                "upstream_lane": upstream_lane,
                            },
                            lane_exec_status=f"pre_run_blocked:{PRE_RUN_UPSTREAM_NOT_FINALIZED_BLOCKER}",
                        )
                        return {
                            "fault": "upstream_not_finalized",
                            "upstream_lane": upstream_lane,
                            "exit_status": "error",
                        }
                try:
                    result = run_canonical_apps_rg_from_cli_primitives(**kwargs)
                    res = dict(result) if isinstance(result, dict) else {}
                    if product_fail_closed_runtime() and phase1_dispatch_hard_failed(res):
                        phase1_aborted = True
                        phase1_abort_reason = f"dispatch_failed:{lane}"
                    return res
                except Exception as exc:  # guardian: allow-broad-exception -- P2 burndown: fail-soft optional boundary
                    if product_fail_closed_runtime():
                        phase1_aborted = True
                        phase1_abort_reason = f"dispatch_exception:{lane}:{exc!s}"
                    return {"fault": "exception", "error": str(exc), "exit_status": "error"}

            _lane_ctx = LaneExecutionContext(
                sections_root=str(sections_root.resolve()),
                target_company=tc,
                target_role=tr,
                job_description_ref=jd_ref,
                job_description_text=jd_txt,
                manual_brief=br_dispatch,
                lane_provider=profile.phase1_lane_provider,
                lane_x1d_judges=x1d_eff,
                lane_mock_judges=lane_mock_j_for_phase1,
                lane_allow_non_allow_exit_zero=_phase1_allow_exit,
            )

            if _parallel_phase1:
                _outcomes = dispatch_phase1_lanes_managed(
                    GENERATED_LANES,
                    _lane_ctx,
                    dispatch_fn=_phase1_dispatch_one_lane,
                    parallel=True,
                    max_parallel=_max_par,
                    should_skip_remaining_waves=lambda: phase1_aborted,
                )
                for lane, oc in _outcomes.items():
                    lane_dispatch_results[lane] = dict(oc.dispatch_result)
                    if oc.exec_status.startswith("pre_run_blocked:"):
                        lane_exec_status[lane] = oc.exec_status
                    else:
                        lane_exec_status[lane] = _phase1_lane_dispatch_status(
                            lane_dispatch_results[lane]
                        )
                    if oc.exec_status.startswith("error:") and not lane_dispatch_results[lane].get(
                        "fault"
                    ):
                        lane_exec_status[lane] = oc.exec_status
            else:
                for lane in GENERATED_LANES:
                    os.environ[MODULAR_R4_SECTIONS_ROOT_ENV] = str(sections_root.resolve())
                    if phase1_aborted:
                        emit_integrated_lane_pre_run_failure(
                            sections_root=sections_root,
                            integrated_dir=art,
                            repo_root=repo,
                            lane_id=lane,
                            blocker=PHASE1_PRIOR_LANE_FAILED_BLOCKER,
                            dispatch_result={"prior_abort": phase1_abort_reason},
                            lane_exec_status=f"pre_run_blocked:{PHASE1_PRIOR_LANE_FAILED_BLOCKER}",
                        )
                        lane_exec_status[lane] = f"pre_run_blocked:{PHASE1_PRIOR_LANE_FAILED_BLOCKER}"
                        continue
                    upstream_spec = _narrative_upstream.get(lane)
                    if upstream_spec is not None:
                        upstream_lane, expected_ids = upstream_spec
                        if not companion_accepted_in_modular_sections_root(
                            repo,
                            sections_root,
                            upstream_section_id=upstream_lane,
                            expected_bullet_ids=expected_ids,
                        ):
                            emit_integrated_lane_pre_run_failure(
                                sections_root=sections_root,
                                integrated_dir=art,
                                repo_root=repo,
                                lane_id=lane,
                                blocker=PRE_RUN_UPSTREAM_NOT_FINALIZED_BLOCKER,
                                dispatch_result={
                                    "fault": "upstream_not_finalized",
                                    "upstream_lane": upstream_lane,
                                },
                                lane_exec_status=f"pre_run_blocked:{PRE_RUN_UPSTREAM_NOT_FINALIZED_BLOCKER}",
                            )
                            lane_dispatch_results[lane] = {
                                "fault": "upstream_not_finalized",
                                "upstream_lane": upstream_lane,
                                "exit_status": "error",
                            }
                            lane_exec_status[lane] = f"pre_run_blocked:{PRE_RUN_UPSTREAM_NOT_FINALIZED_BLOCKER}"
                            continue
                    try:
                        result = run_canonical_apps_rg_from_cli_primitives(
                            target_company=tc,
                            target_role=tr,
                            jd="",
                            job_description_ref=jd_ref,
                            job_description_text=jd_txt,
                            manual_brief=br_dispatch,
                            resume_path="",
                            source_resume_text="",
                            generation_mode="strategic_tailor",
                            artifact_dir="",
                            section=lane,
                            lane_provider=profile.phase1_lane_provider,
                            lane_provider_resolution_source=CLI_PROVIDER_RESOLUTION_CLI_OVERRIDE,
                            lane_temperature=default_temperature_for_section(lane),
                            lane_x1d_judges=x1d_eff,
                            lane_mock_judges=lane_mock_j_for_phase1,
                            lane_allow_non_allow_exit_zero=_phase1_allow_exit,
                        )
                        lane_dispatch_results[lane] = dict(result) if isinstance(result, dict) else {}
                        lane_exec_status[lane] = _phase1_lane_dispatch_status(lane_dispatch_results[lane])
                        if product_fail_closed_runtime() and phase1_dispatch_hard_failed(
                            lane_dispatch_results[lane]
                        ):
                            phase1_aborted = True
                            phase1_abort_reason = f"dispatch_failed:{lane}:{lane_exec_status[lane]}"
                    except Exception as exc:  # guardian: allow-broad-exception -- P2 burndown: fail-soft optional boundary
                        lane_exec_status[lane] = f"error:{exc!s}"
                        lane_dispatch_results[lane] = {"fault": "exception", "error": str(exc)}
                        if product_fail_closed_runtime():
                            phase1_aborted = True
                            phase1_abort_reason = f"dispatch_exception:{lane}:{exc!s}"
            _product_fail_closed = product_fail_closed_runtime()
            for lane in GENERATED_LANES:
                run_dir = _phase1_materialize_lane_run_dir(
                    repo=repo,
                    sections_root=sections_root,
                    integrated_dir=art,
                    lane=lane,
                    lane_provider=profile.phase1_lane_provider,
                    lane_dispatch_results=lane_dispatch_results,
                    lane_exec_status=lane_exec_status,
                    emit_integrated_lane_pre_run_failure=emit_integrated_lane_pre_run_failure,
                    product_fail_closed=_product_fail_closed,
                )
                if run_dir is not None:
                    lane_run_dirs[lane] = run_dir

            inv_extra: dict[str, Any] = {
                "run_id": run_id,
                "lane_status": lane_exec_status,
                "sections_root_rel": _rel_under_repo(sections_root, repo),
                "phase1_parallel_enabled": _parallel_phase1,
                "phase1_max_parallel": _max_par if _parallel_phase1 else 1,
                "phase1_allow_non_allow_exit_zero_effective": _phase1_allow_exit,
            }
            if lane_targeting is not None:
                inv_extra["lane_argv_targeting"] = asdict(lane_targeting)
            _write_json(
                modular_root / "phase1_lane_inventory.json",
                inv_extra,
            )

            if len(lane_run_dirs) == len(GENERATED_LANES):
                rollup_blob = build_modular_lane_rollup(repo, lane_run_dirs)
            else:
                rollup_blob = None

            if rollup_blob is not None:
                for lane in GENERATED_LANES:
                    row = rollup_blob["lanes"].get(lane)
                    if isinstance(row, dict):
                        rel_run = str(row.get("rollup_source_run_dir") or "")
                        if rel_run:
                            section_output_refs[lane] = f"{rel_run}/l2_output.json"
                rollup_dir = modular_root / "generated_lane_rollup"
                rollup_dir.mkdir(parents=True, exist_ok=True)
                _write_json(rollup_dir / "generated_lane_rollup.json", rollup_blob)

                build_locked_copy(repo, modular_output_root=modular_root)

                locked_dir = modular_root / "locked_copy"
                _, canonical_base_resume_path, _ = load_lane_base_resume_json(repo_root=repo)
                paths = FinalResumePaths(
                    repo_root=repo,
                    rollup_json=rollup_dir / "generated_lane_rollup.json",
                    locked_manifest=locked_dir / "locked_copy_manifest.json",
                    locked_x2=locked_dir / "locked_copy_x2_gate_outputs.json",
                    base_resume=canonical_base_resume_path,
                    output_dir=modular_root / "final_resume_assembly",
                )
                plumbing = _assembly_plumbing_mode(profile, use_phase0_synthetic=False)
                asm = _assemble_modular_final_resume(paths, plumbing_mode=plumbing)
                assembly_gates_ok = bool(asm.get("gates_all_pass"))
                receipt_path = asm["paths"]["receipt"]
                try:
                    merge_receipt_rel = receipt_path.relative_to(art).as_posix()
                except ValueError:
                    merge_receipt_rel = str(receipt_path)
            else:
                assembly_gates_ok = False

            sc_req = profile.self_consistency_requested
            sc_exe = 0
            prof = profile.phase1_lane_provider
            for i, lane in enumerate(GENERATED_LANES):
                rd = lane_run_dirs.get(lane)
                if rd is None or not rd.is_dir():
                    pre_run = None
                    try:
                        from apps_rg.runtime.integrated_lane_evidence_packaging import (
                            load_integrated_lane_pre_run_failure,
                        )

                        pre_run = load_integrated_lane_pre_run_failure(art, lane)
                    except ImportError:
                        pre_run = None
                    decisive = str((pre_run or {}).get("blocker") or "PHASE1_NO_RUN_DIR")
                    section_call_records.append(
                        _phase1_missing_lane_record(
                            lane,
                            i,
                            sc_req,
                            sc_exe,
                            prof,
                            decisive_reason_code=decisive,
                        ),
                    )
                    continue
                section_call_records.append(
                    build_section_provider_call_record(
                        lane=lane,
                        candidate_index=i,
                        run_dir=rd,
                        artifact_dir=art,
                        self_consistency_requested=sc_req,
                        self_consistency_executed=sc_exe,
                        provider_profile=prof,
                    ),
                )
            provider_call_total = sum(1 for r in section_call_records if r.get("provider_call_attempted") is True)
        finally:
            if prev_whole_run_env is None:
                os.environ.pop("APPS_RG_WHOLE_RUN_ENVELOPE", None)
            else:
                os.environ["APPS_RG_WHOLE_RUN_ENVELOPE"] = prev_whole_run_env
            if prev_corr_env is None:
                os.environ.pop("APPS_RG_CORRELATED_CLI_RUN", None)
            else:
                os.environ["APPS_RG_CORRELATED_CLI_RUN"] = prev_corr_env
            if prev_env is None:
                os.environ.pop(MODULAR_R4_SECTIONS_ROOT_ENV, None)
            else:
                os.environ[MODULAR_R4_SECTIONS_ROOT_ENV] = prev_env

        lanes_executed = sum(
            1 for lane in GENERATED_LANES if lane in lane_run_dirs and lane_run_dirs[lane].is_dir()
        )
        lane_outputs_valid = bool(rollup_blob is not None and assembly_gates_ok is True)

    elif use_phase0_synthetic:
        from apps_rg.runtime.product_output_policy import product_fail_closed_runtime

        if product_fail_closed_runtime():
            phase0_blocked_on_product_fail_closed = True
            section_call_records = [
                _phase0_stub_lane_record(lane, i) for i, lane in enumerate(GENERATED_LANES)
            ]
            rollup_blob = None
            assembly_gates_ok = False
            merge_receipt_rel = None
            decisive = "FAIL"
            failure = "phase0_synthetic_not_permitted_on_product_fail_closed_path"
            pass_source = "none"
            lanes_executed = 0
            lane_outputs_valid = False
            _write_json(
                art / "modular_r4" / "phase0_product_fail_closed_block.json",
                {
                    "blocked": True,
                    "reason": failure,
                    "note": "Product runs require phase1_invoke_real_lanes; phase0 stubs are plumbing-only.",
                },
            )
        else:
            for i, lane in enumerate(GENERATED_LANES):
                section_call_records.append(_phase0_stub_lane_record(lane, i))
            rollup_blob = _build_synthetic_rollup(repo, modular_root)
            for lane in GENERATED_LANES:
                row = rollup_blob["lanes"].get(lane)
                if isinstance(row, dict):
                    rel_run = str(row.get("rollup_source_run_dir") or "")
                    if rel_run:
                        section_output_refs[lane] = f"{rel_run}/l2_output.json"
            rollup_dir = modular_root / "generated_lane_rollup"
            rollup_dir.mkdir(parents=True, exist_ok=True)
            _write_json(rollup_dir / "generated_lane_rollup.json", rollup_blob)

            build_locked_copy(repo, modular_output_root=modular_root)

            locked_dir = modular_root / "locked_copy"
            _, canonical_base_resume_path, _ = load_lane_base_resume_json(repo_root=repo)
            paths = FinalResumePaths(
                repo_root=repo,
                rollup_json=rollup_dir / "generated_lane_rollup.json",
                locked_manifest=locked_dir / "locked_copy_manifest.json",
                locked_x2=locked_dir / "locked_copy_x2_gate_outputs.json",
                base_resume=canonical_base_resume_path,
                output_dir=modular_root / "final_resume_assembly",
            )
            plumbing = _assembly_plumbing_mode(profile, use_phase0_synthetic=True)
            asm = _assemble_modular_final_resume(paths, plumbing_mode=plumbing)
            assembly_gates_ok = bool(asm.get("structural_x2_all_pass"))
            receipt_path = asm["paths"]["receipt"]
            try:
                merge_receipt_rel = receipt_path.relative_to(art).as_posix()
            except ValueError:
                merge_receipt_rel = str(receipt_path)

            lanes_executed = len(GENERATED_LANES)
            lane_outputs_valid = bool(assembly_gates_ok is True)

    schema_receipt_path = modular_root / "rg_output_schema_validation_receipt.json"
    fixture_ok = False
    fixture_err = "no_fixture_provided"
    fixture_candidate: dict[str, Any] | None = None
    if profile.validate_rg_output_fixture:
        p = input_package.rg_output_fixture_path
        if p is not None and p.is_file():
            raw_txt = p.read_text(encoding="utf-8")
            fixture_candidate = json.loads(raw_txt)
            fixture_ok, fixture_err = validate_rg_output_object(fixture_candidate)
        elif p is not None:
            fixture_err = "rg_output_fixture_path_not_found"
        else:
            fixture_err = "rg_output_fixture_path_missing"

    decisive: Any = "FAIL"
    failure = (
        "phase0_synthetic_not_permitted_on_product_fail_closed_path"
        if phase0_blocked_on_product_fail_closed
        else "phase0_incomplete"
    )
    gen_resume: dict[str, Any] | None = None
    final_schema_valid = False

    if profile.phase1_invoke_real_lanes:
        assembled_path = modular_root / "final_resume_assembly" / "final_resume.json"
        build_ok = False
        merged_err = "phase1_merge_not_attempted"
        gen_resume = None
        final_schema_valid = False
        lane_load_errors: dict[str, str] = {}
        if assembly_gates_ok is True:
            final_merge_attempted = True
            base_resume_obj, _, _ = load_lane_base_resume_json(repo_root=repo)
            rollup_lanes = rollup_blob.get("lanes") if isinstance(rollup_blob, dict) else {}
            lane_map, lane_load_errors = load_lane_l2_from_section_refs(
                repo,
                section_output_refs,
                rollup_lanes=rollup_lanes if isinstance(rollup_lanes, dict) else None,
            )
            build = build_rg_output_from_modular_sections(
                lane_l2_by_id=lane_map,
                base_resume=base_resume_obj,
                input_package=input_package,
                modular_root=modular_root,
                artifact_dir=art,
                run_id=run_id,
                reject_mocked_lanes=True,
            )
            build_ok = bool(build.ok)
            merged_err = build.failure_reason or build.schema_error or ""
            final_schema_valid = bool(build.schema_valid and build.ok)
            gen_resume = build.rg_output if build_ok else None
            merge_out = modular_root / "outputs" / "rg_output_merge_receipt.json"
            merge_out.parent.mkdir(parents=True, exist_ok=True)
            _write_json(merge_out, build.merge_receipt)
            try:
                rg_output_merge_receipt_rel = merge_out.relative_to(art).as_posix()
            except ValueError:
                rg_output_merge_receipt_rel = str(merge_out).replace("\\", "/")
            if build_ok and gen_resume is not None:
                prod_out = art / "outputs" / "generated_resume.json"
                prod_out.parent.mkdir(parents=True, exist_ok=True)
                prod_out.write_text(
                    json.dumps(gen_resume, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
        if rollup_blob is None:
            decisive = "FAIL"
            failure = "phase1_incomplete_lane_artifacts"
        elif assembly_gates_ok is False:
            decisive = "FAIL"
            failure = "deterministic_assembly_gates_failed"
        elif lane_load_errors:
            decisive = "FAIL"
            failure = "lane_l2_load_errors:" + ";".join(
                f"{k}={v}" for k, v in sorted(lane_load_errors.items())
            )
        elif build_ok:
            decisive = "PASS"
            failure = ""
            pass_source = "merged_rg_output_direct_lanes"
        elif assembly_gates_ok is True:
            decisive = "FAIL"
            failure = merged_err or "modular_rg_output_merge_failed"
            pass_source = "none"
        else:
            decisive = "FAIL"
            failure = "deterministic_assembly_failed_unknown"
        out_fr = modular_root / "outputs" / "final_resume.json"
        _write_json(
            schema_receipt_path,
            {
                "receipt_id": "rg_output_schema_validation_receipt.phase1.v3",
                "validated_at_utc": datetime.now(timezone.utc).isoformat(),
                "final_schema_valid": final_schema_valid,
                "error": merged_err if not build_ok else "",
                "lane_l2_load_errors": lane_load_errors,
                "assembler_final_resume_relpath": (
                    assembled_path.relative_to(art).as_posix() if assembled_path.is_file() else None
                ),
                "rg_output_final_resume_relpath": (
                    out_fr.relative_to(art).as_posix() if out_fr.is_file() else None
                ),
                "generated_resume_json_relpath": (
                    "outputs/generated_resume.json"
                    if (art / "outputs" / "generated_resume.json").is_file()
                    else None
                ),
                "rg_output_merge_receipt_relpath": rg_output_merge_receipt_rel,
                "assembly_gates_all_pass": assembly_gates_ok,
                "fixture_validated_ok": fixture_ok,
                "fixture_error": fixture_err if not fixture_ok else "",
                "fixture_path": str(input_package.rg_output_fixture_path) if input_package.rg_output_fixture_path else None,
                "note": (
                    "Phase 1 v3: rg_output merge from lane l2_output.json refs (not assembler bridge); "
                    "PASS requires assembly gates_all_pass + valid outputs/generated_resume.json."
                ),
            },
        )
    else:
        final_schema_valid = bool(fixture_ok)
        gen_resume = None
        if phase0_blocked_on_product_fail_closed:
            decisive = "FAIL"
        elif not profile.run_phase0_synthetic_assembly:
            decisive = "FAIL"
            failure = "phase0_synthetic_assembly_disabled"
            assembly_gates_ok = None
        elif assembly_gates_ok is False:
            decisive = "FAIL"
            failure = "deterministic_assembly_gates_failed"
        elif assembly_gates_ok is True:
            if profile.validate_rg_output_fixture and input_package.rg_output_fixture_path is not None:
                if fixture_ok and fixture_candidate is not None:
                    decisive = "PASS"
                    failure = ""
                    gen_resume = fixture_candidate
                    pass_source = "fixture_rg_output"
                else:
                    from apps_rg.runtime.product_output_policy import product_fail_closed_runtime

                    if product_fail_closed_runtime():
                        decisive = "FAIL"
                    else:
                        decisive = "PARTIAL"
                    failure = fixture_err
            else:
                from apps_rg.runtime.product_output_policy import product_fail_closed_runtime

                failure = (
                    "rg_output_fixture_validation_skipped"
                    if not profile.validate_rg_output_fixture
                    else "rg_output_fixture_path_missing"
                )
                decisive = "FAIL" if product_fail_closed_runtime() else "PARTIAL"
        else:
            decisive = "FAIL"
            failure = "deterministic_assembly_failed_unknown"
        _write_json(
            schema_receipt_path,
            {
                "receipt_id": "rg_output_schema_validation_receipt.phase0.v1",
                "validated_at_utc": datetime.now(timezone.utc).isoformat(),
                "final_schema_valid": final_schema_valid,
                "error": fixture_err if not fixture_ok else "",
                "fixture_path": str(input_package.rg_output_fixture_path) if input_package.rg_output_fixture_path else None,
                "note": (
                    "Phase 0: validates optional fixture JSON only; assembler output remains "
                    "final_resume_assembler_v1, not rg_output_schema."
                ),
            },
        )

    recipe_lane_policy = summarize_modular_lane_recipe_policy(
        section_call_records,
        enforce_product_lane_requirements=bool(profile.phase1_invoke_real_lanes),
    )
    if profile.phase1_invoke_real_lanes:
        from apps_rg.runtime.integrated_lane_evidence_packaging import (
            finalize_integrated_run_lane_evidence,
        )

        finalize_integrated_run_lane_evidence(
            repo,
            art,
            correlation_id=run_id,
            section_call_records=section_call_records,
            recipe_lane_policy=recipe_lane_policy,
        )
    if profile.phase1_invoke_real_lanes and recipe_lane_policy.get("fatal_lane_failures"):
        decisive = "FAIL"
        failure = "fatal_lane_recipe_policy:" + "; ".join(
            f'{f["section_lane"]}:{f.get("decisive_reason_code") or ""}'
            for f in recipe_lane_policy["fatal_lane_failures"][:8]
        )
        pass_source = ""

    section_calls_path = modular_root / "section_provider_calls.json"
    calls_schema = (
        "apps_rg.section_provider_calls.phase1.v2"
        if profile.phase1_invoke_real_lanes
        else "apps_rg.section_provider_calls.phase0.v1"
    )
    locked_provider = any(str(r.get("section_lane")) == "full_resume" for r in section_call_records)
    _write_json(
        section_calls_path,
        {
            "schema_version": calls_schema,
            "run_id": run_id,
            "modular_root_rel": rel_mod,
            "provider_call_count": provider_call_total,
            "locked_sections_provider_calls_detected": locked_provider,
            "real_lane_invocation_attempted": real_lane_invocation_attempted,
            "records": section_call_records,
            "lane_dispatch_modules": list(LANE_DISPATCH_MODULES),
            "decisive_status": decisive,
            "pass_source": pass_source,
            "recipe_lane_policy": recipe_lane_policy,
        },
    )

    schema_rel = schema_receipt_path.relative_to(art).as_posix()

    return ModularR4GenerationResult(
        generated_resume=gen_resume,
        section_provider_calls_ref=section_calls_path.relative_to(art).as_posix(),
        section_output_refs=section_output_refs,
        merge_receipt_ref=merge_receipt_rel,
        schema_validation_receipt_ref=schema_rel,
        final_schema_valid=final_schema_valid,
        decisive_status=decisive,
        failure_reason=failure,
        provider_call_count=provider_call_total,
        locked_sections_provider_calls_detected=locked_provider,
        lanes_executed=lanes_executed,
        lane_outputs_valid=lane_outputs_valid,
        final_merge_attempted=final_merge_attempted,
        rg_output_merge_receipt_ref=rg_output_merge_receipt_rel,
        extras={
            "modular_root_rel": rel_mod,
            "assembly_gates_all_pass": assembly_gates_ok,
            "lane_count": len(GENERATED_LANES),
            "pass_source": pass_source,
            "real_lane_invocation_attempted": real_lane_invocation_attempted,
            "phase1_lane_status": lane_exec_status if profile.phase1_invoke_real_lanes else {},
            "lanes_executed": lanes_executed,
            "lane_outputs_valid": lane_outputs_valid,
            "final_merge_attempted": final_merge_attempted,
            "recipe_lane_policy": recipe_lane_policy,
        },
    )


__all__ = [
    "LANE_DISPATCH_MODULES",
    "ModularResumeInputPackage",
    "ModularResumeProfile",
    "PHASE0_PATH_INVENTORY_NOTES",
    "run_modular_resume_generation",
]
