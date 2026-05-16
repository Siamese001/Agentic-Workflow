"""Phase 0 modular R4 API — shared runner (artifact-local; optional via ``GenerateResumeStep`` flag).

Writes **only** under ``Path(artifact_dir) / \"modular_r4\"`` for pipeline artifacts
(does not use ``artifacts/apps_rg/runtime_proofs`` for canonical outputs).

See ``.cursor/plans/apps-rg-r4-modular-section-migration-d4e8a1.md``.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Final

from apps_rg.l2_recipe.modular_lane_adapter import (
    build_section_provider_call_record,
    lane_argv_for_provider,
    resolve_latest_lane_run_dir,
    run_dispatch_main,
)
from apps_rg.l2_recipe.modular_lane_recipe_policy import summarize_modular_lane_recipe_policy
from apps_rg.l2_recipe.modular_r4_generation_result import ModularR4GenerationResult
from apps_rg.l2_recipe.modular_rg_output_builder import (
    build_rg_output_from_modular_sections,
    extract_lane_l2_from_assembled_final,
)
from apps_rg.l2_recipe.rg_output_jsonschema_validate import validate_rg_output_object
from apps_rg.runtime.assembly.final_resume_assembler import assemble_final_resume
from apps_rg.runtime.assembly.final_resume_manifest import FinalResumePaths
from apps_rg.runtime.locked_copy.locked_copy_builder import build_locked_copy
from apps_rg.runtime.reports.generated_lane_rollup import (
    GENERATED_LANES,
    build_modular_lane_rollup,
)
from apps_rg.runtime.runtime_proof_layout import MODULAR_R4_SECTIONS_ROOT_ENV

# Same seven modules as ``apps_rg.runtime.orchestrate_full_resume`` (single SSOT).
LANE_DISPATCH_MODULES: Final[tuple[str, ...]] = (
    "apps_rg.runtime.dispatch.headline_dispatch",
    "apps_rg.runtime.dispatch.executive_summary_dispatch",
    "apps_rg.runtime.dispatch.unify_bullets_dispatch",
    "apps_rg.runtime.dispatch.unify_narrative_dispatch",
    "apps_rg.runtime.dispatch.ibm_bullets_dispatch",
    "apps_rg.runtime.dispatch.ibm_narrative_dispatch",
    "apps_rg.runtime.dispatch.competencies_dispatch",
)


PHASE0_PATH_INVENTORY_NOTES: dict[str, Any] = {
    "subprocess_cwd": (
        "orchestrate_full_resume.run_orchestration uses subprocess with cwd=repo root; "
        "lane argv: python -m <LANE_DISPATCH_MODULES[i]> ..."
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


def _phase1_missing_lane_record(lane: str, i: int, sc_req: int, sc_exe: int, prof: str) -> dict[str, Any]:
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
        "decisive_reason_code": "PHASE1_NO_RUN_DIR",
        "output_ref": "",
        "reasoning_execution_receipt_ref": None,
    }


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
    phase1_lane_provider: str = "mock"
    self_consistency_requested: int = 0


def run_modular_resume_generation(
    input_package: ModularResumeInputPackage,
    artifact_dir: Path | str,
    run_id: str,
    profile: ModularResumeProfile | None = None,
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
    lanes_executed = 0
    lane_outputs_valid = False
    final_merge_attempted = False
    rg_output_merge_receipt_rel: str | None = None

    if profile.phase1_invoke_real_lanes:
        sections_root = modular_root / "sections"
        sections_root.mkdir(parents=True, exist_ok=True)
        prev_env = os.environ.get(MODULAR_R4_SECTIONS_ROOT_ENV)
        os.environ[MODULAR_R4_SECTIONS_ROOT_ENV] = str(sections_root.resolve())
        lane_argv = lane_argv_for_provider(provider=profile.phase1_lane_provider)
        lane_run_dirs: dict[str, Path] = {}
        try:
            for lane, mod in zip(GENERATED_LANES, LANE_DISPATCH_MODULES):
                try:
                    rc = run_dispatch_main(mod, lane_argv)
                    lane_exec_status[lane] = "ok" if rc == 0 else f"exit_{rc}"
                except Exception as exc:
                    lane_exec_status[lane] = f"error:{exc!s}"
            for lane in GENERATED_LANES:
                try:
                    lane_run_dirs[lane] = resolve_latest_lane_run_dir(
                        repo,
                        sections_root,
                        lane,
                        lane_provider=profile.phase1_lane_provider,
                    )
                except FileNotFoundError as exc:
                    lane_exec_status[lane] = lane_exec_status.get(lane, "") + f"|missing_pointer:{exc}"

            _write_json(
                modular_root / "phase1_lane_inventory.json",
                {"run_id": run_id, "lane_status": lane_exec_status, "sections_root_rel": _rel_under_repo(sections_root, repo)},
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
                base_json = repo / "apps_rg" / "resume" / "base" / "amit_ayer_base_resume_v1.json"
                paths = FinalResumePaths(
                    repo_root=repo,
                    rollup_json=rollup_dir / "generated_lane_rollup.json",
                    locked_manifest=locked_dir / "locked_copy_manifest.json",
                    locked_x2=locked_dir / "locked_copy_x2_gate_outputs.json",
                    base_resume=base_json,
                    output_dir=modular_root / "final_resume_assembly",
                )
                asm = assemble_final_resume(paths)
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
                    section_call_records.append(
                        _phase1_missing_lane_record(lane, i, sc_req, sc_exe, prof),
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
            if prev_env is None:
                os.environ.pop(MODULAR_R4_SECTIONS_ROOT_ENV, None)
            else:
                os.environ[MODULAR_R4_SECTIONS_ROOT_ENV] = prev_env

        lanes_executed = sum(
            1 for lane in GENERATED_LANES if lane in lane_run_dirs and lane_run_dirs[lane].is_dir()
        )
        lane_outputs_valid = bool(rollup_blob is not None and assembly_gates_ok is True)

    elif use_phase0_synthetic:
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
        base_json = repo / "apps_rg" / "resume" / "base" / "amit_ayer_base_resume_v1.json"
        paths = FinalResumePaths(
            repo_root=repo,
            rollup_json=rollup_dir / "generated_lane_rollup.json",
            locked_manifest=locked_dir / "locked_copy_manifest.json",
            locked_x2=locked_dir / "locked_copy_x2_gate_outputs.json",
            base_resume=base_json,
            output_dir=modular_root / "final_resume_assembly",
        )
        asm = assemble_final_resume(paths)
        assembly_gates_ok = bool(asm.get("gates_all_pass"))
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
    failure = "phase0_incomplete"
    gen_resume: dict[str, Any] | None = None
    final_schema_valid = False

    if profile.phase1_invoke_real_lanes:
        assembled_path = modular_root / "final_resume_assembly" / "final_resume.json"
        build_ok = False
        merged_err = "phase1_no_assembler_final"
        gen_resume = None
        final_schema_valid = False
        if assembly_gates_ok is True and assembled_path.is_file():
            final_merge_attempted = True
            canonical_base = repo / "apps_rg" / "resume" / "base" / "amit_ayer_base_resume_v1.json"
            base_resume_obj = json.loads(canonical_base.read_text(encoding="utf-8"))
            lane_map = extract_lane_l2_from_assembled_final(assembled_path)
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
        if rollup_blob is None:
            decisive = "FAIL"
            failure = "phase1_incomplete_lane_artifacts"
        elif assembly_gates_ok is False:
            decisive = "FAIL"
            failure = "deterministic_assembly_gates_failed"
        elif assembly_gates_ok is True and build_ok:
            decisive = "PASS"
            failure = ""
            pass_source = "merged_rg_output"
        elif assembly_gates_ok is True:
            decisive = "PARTIAL"
            failure = merged_err or "modular_rg_output_merge_failed"
            pass_source = "none"
        else:
            decisive = "FAIL"
            failure = "deterministic_assembly_failed_unknown"
        out_fr = modular_root / "outputs" / "final_resume.json"
        _write_json(
            schema_receipt_path,
            {
                "receipt_id": "rg_output_schema_validation_receipt.phase1.v2",
                "validated_at_utc": datetime.now(timezone.utc).isoformat(),
                "final_schema_valid": final_schema_valid,
                "error": merged_err if not build_ok else "",
                "assembler_final_resume_relpath": (
                    assembled_path.relative_to(art).as_posix() if assembled_path.is_file() else None
                ),
                "rg_output_final_resume_relpath": (
                    out_fr.relative_to(art).as_posix() if out_fr.is_file() else None
                ),
                "rg_output_merge_receipt_relpath": rg_output_merge_receipt_rel,
                "fixture_validated_ok": fixture_ok,
                "fixture_error": fixture_err if not fixture_ok else "",
                "fixture_path": str(input_package.rg_output_fixture_path) if input_package.rg_output_fixture_path else None,
                "note": (
                    "Phase 1 v2: deterministic rg_output merge from lane L2 snapshots + base resume; "
                    "PASS requires outputs/final_resume.json validates as rg_output_schema (not assembler JSON)."
                ),
            },
        )
    else:
        final_schema_valid = bool(fixture_ok)
        gen_resume = None
        if not profile.run_phase0_synthetic_assembly:
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
                    decisive = "PARTIAL"
                    failure = fixture_err
            else:
                decisive = "PARTIAL"
                failure = (
                    "rg_output_fixture_validation_skipped"
                    if not profile.validate_rg_output_fixture
                    else "rg_output_fixture_path_missing"
                )
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
