"""W7.1 — patch-run mode: re-dispatch ONLY failed lanes of an existing integrated run.

Convergence problem this solves: a full 11-lane re-roll is a casino — independent
per-roll variance means previously-green lanes can fail on the next attempt. Patch-run
makes convergence monotone: lanes that already hold an accepted REAL_LLM + X3-allow
bundle stay banked; only non-authorized lanes are re-dispatched into the SAME run dir
(new timestamped lane dir, exactly like the integrated full run), then the same
app-side aggregation chain re-runs (rollup → locked copy → final assembly → rg_output
merge → artifact gate → recipe policy → integrated lane evidence refresh).

Honest boundary (spine law): apps_rg never emits root X3. The original run's root
``x3_disposition_receipt.json`` / ``r4_run_manifest.json`` / ``terminal_ret_packet.json``
remain the historical Exit record of the failed integrated dispatch. Post-patch product
authorization is expressed through per-lane X3 dispositions, the refreshed
``integrated_lane_evidence_status.json``, and the full-success eligibility evaluation
recorded in ``patch_run_receipt.json``.

CLI:
    python -m apps_rg --patch-run <existing_run_dir> [--sections <csv>]
                      [--force-lanes <csv>] [--dry-run]

Targeting inputs are re-derived from the run dir's persisted artifacts
(``ingress_raw.json`` + per-lane ``run_manifest.json`` command + per-lane
``validated_request.json`` app_payload). Never re-asks interactively; refuses with a
clear error (exit 2) when inputs cannot be derived.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping

from apps_rg.runtime.internal.generated_lane_rollup import GENERATED_LANES
from apps_rg.runtime.runtime_proof_layout import (
    MODULAR_R4_SECTIONS_ROOT_ENV,
    find_repo_root,
)

PATCH_RUN_RECEIPT_ARTIFACT = "patch_run_receipt.json"
_WHOLE_RUN_ENVELOPE_ENV = "APPS_RG_WHOLE_RUN_ENVELOPE"
_CORRELATED_CLI_RUN_ENV = "APPS_RG_CORRELATED_CLI_RUN"

# CLI flags whose values we re-derive from a persisted lane ``run_manifest.json`` command.
_COMMAND_FLAGS_OF_INTEREST = (
    "--jd",
    "--target-level",
    "--target-company",
    "--target-role",
    "--manual-brief",
)

DispatchFn = Callable[..., dict[str, Any]]


class PatchRunInputError(Exception):
    """Input/argument error — maps to process exit 2 (same family as CLI config errors)."""

    exit_code = 2


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return raw if isinstance(raw, dict) else None


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


# --------------------------------------------------------------------- targeting


@dataclass(frozen=True)
class PatchTargeting:
    """Targeting inputs re-derived from the run dir's persisted artifacts."""

    target_company: str = ""
    target_role: str = ""
    target_level: str = ""
    job_description_ref: str = ""
    job_description_text: str = ""
    manual_brief: str = ""
    generation_mode: str = "strategic_tailor"
    sources: dict[str, str] = field(default_factory=dict)


def parse_cli_command_flags(command: str) -> dict[str, str]:
    """Parse ``--flag value...`` pairs from a persisted run_manifest ``command`` string.

    The command string is ``" ".join(sys.argv)`` from the original invocation; values
    may contain spaces but never a token starting with ``--``, so splitting on flag
    tokens is deterministic.
    """
    tokens = str(command or "").split()
    out: dict[str, str] = {}
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok.startswith("--"):
            vals: list[str] = []
            j = i + 1
            while j < len(tokens) and not tokens[j].startswith("--"):
                vals.append(tokens[j])
                j += 1
            out[tok] = " ".join(vals)
            i = j
        else:
            i += 1
    return out


def latest_lane_run_dir_any(sections_root: Path, lane: str) -> Path | None:
    """Deterministic latest lane run dir: lexicographically greatest ``real/<run_id>``.

    Lane run ids are ``<lane>_<YYYYMMDD>_<HHMMSS>`` so lexicographic order equals
    chronological order, independent of filesystem mtimes (deterministic across
    copies / checkouts).
    """
    real_root = Path(sections_root) / lane / "real"
    if not real_root.is_dir():
        return None
    candidates = sorted(
        (p for p in real_root.iterdir() if p.is_dir()),
        key=lambda p: p.name,
    )
    return candidates[-1] if candidates else None


def _lane_app_payload(run_dir: Path) -> dict[str, Any]:
    doc = _load_json(run_dir / "validated_request.json") or {}
    payload = doc.get("payload") or {}
    ap = payload.get("app_payload") if isinstance(payload, dict) else None
    return ap if isinstance(ap, dict) else {}


def derive_patch_targeting(repo: Path, run_dir: Path) -> PatchTargeting:
    """Re-derive targeting inputs from the run dir's persisted artifacts.

    Sources, in precedence order:
      1. root ``ingress_raw.json`` — target_company / target_role / manual_brief /
         generation_mode (written by the whole-run orchestration).
      2. any executed lane's ``run_manifest.json`` ``command`` — ``--jd`` path /
         ``--target-level`` (and company/role fallback).
      3. any executed lane's ``validated_request.json`` app_payload —
         ``job_description_text`` inline fallback when the JD file path is gone.

    Raises ``PatchRunInputError`` when company, role, or a JD source cannot be derived.
    """
    repo = Path(repo).resolve()
    run_dir = Path(run_dir).resolve()
    sources: dict[str, str] = {}

    ingress = _load_json(run_dir / "ingress_raw.json") or {}
    target_company = str(ingress.get("target_company") or "").strip()
    target_role = str(ingress.get("target_role") or "").strip()
    manual_brief = str(ingress.get("manual_brief") or "").strip()
    generation_mode = str(ingress.get("generation_mode") or "strategic_tailor").strip()
    if target_company:
        sources["target_company"] = "ingress_raw.json"
    if target_role:
        sources["target_role"] = "ingress_raw.json"
    if manual_brief:
        sources["manual_brief"] = "ingress_raw.json"

    sections_root = run_dir / "modular_r4" / "sections"
    command_flags: dict[str, str] = {}
    app_payload: dict[str, Any] = {}
    command_lane = ""
    for lane in GENERATED_LANES:
        lrd = latest_lane_run_dir_any(sections_root, lane)
        if lrd is None:
            continue
        manifest = _load_json(lrd / "run_manifest.json") or {}
        flags = parse_cli_command_flags(str(manifest.get("command") or ""))
        if flags and not command_flags:
            command_flags = flags
            command_lane = lane
        if not app_payload:
            ap = _lane_app_payload(lrd)
            if ap:
                app_payload = ap
        if command_flags and app_payload:
            break

    if not target_company:
        target_company = str(
            command_flags.get("--target-company") or app_payload.get("target_company") or ""
        ).strip()
        if target_company:
            sources["target_company"] = f"lane:{command_lane}"
    if not target_role:
        target_role = str(
            command_flags.get("--target-role") or app_payload.get("target_role") or ""
        ).strip()
        if target_role:
            sources["target_role"] = f"lane:{command_lane}"

    target_level = str(
        command_flags.get("--target-level") or app_payload.get("target_level") or ""
    ).strip()
    if target_level:
        sources["target_level"] = f"lane:{command_lane}"

    jd_ref = ""
    jd_text = ""
    jd_flag = str(command_flags.get("--jd") or "").strip()
    if jd_flag:
        cand = Path(jd_flag)
        if not cand.is_absolute():
            cand = repo / jd_flag
        if cand.is_file():
            jd_ref = str(cand.resolve())
            sources["job_description_ref"] = f"lane:{command_lane}:command:--jd"
    if not jd_ref:
        jd_text = str(app_payload.get("job_description_text") or "").strip()
        if jd_text:
            sources["job_description_text"] = "lane:validated_request.app_payload"

    if manual_brief:
        mb = Path(manual_brief)
        if not mb.is_absolute():
            mb = repo / manual_brief
        if mb.is_file():
            manual_brief = str(mb.resolve())
        else:
            # Path persisted but no longer on disk — fall back to inline briefing text.
            uc = app_payload.get("user_constraints") or {}
            inline = str(uc.get("briefing_text") or "").strip() if isinstance(uc, dict) else ""
            if inline:
                manual_brief = inline
                sources["manual_brief"] = "lane:validated_request.user_constraints.briefing_text"

    missing: list[str] = []
    if not target_company:
        missing.append("target_company")
    if not target_role:
        missing.append("target_role")
    if not jd_ref and not jd_text:
        missing.append("jd (no --jd path on disk and no persisted job_description_text)")
    if missing:
        raise PatchRunInputError(
            "patch-run cannot re-derive targeting inputs from the run dir's persisted "
            f"artifacts ({run_dir}): missing {', '.join(missing)}. "
            "Expected ingress_raw.json and/or an executed lane's run_manifest.json / "
            "validated_request.json. Patch-run never asks interactively — re-run the "
            "full integrated CLI with explicit flags instead."
        )

    return PatchTargeting(
        target_company=target_company,
        target_role=target_role,
        target_level=target_level,
        job_description_ref=jd_ref,
        job_description_text=jd_text,
        manual_brief=manual_brief,
        generation_mode=generation_mode or "strategic_tailor",
        sources=sources,
    )


# --------------------------------------------------------------------- lane states


def classify_lane_state(repo: Path, run_dir: Path, lane: str) -> dict[str, Any]:
    """Classify one lane's current state from on-disk evidence (env-independent).

    AUTHORIZED iff ``latest_successful_real_run.json`` resolves to a run dir that
    meets the product lane bar (REAL_LLM + product PASS + X3 allow family) — the same
    bar ``resolve_latest_lane_run_dir`` applies on the product fail-closed path.
    """
    from apps_rg.runtime.integrated_lane_evidence_packaging import (
        _lane_x3_from_artifact_dir,
        load_integrated_lane_pre_run_failure,
    )
    from apps_rg.runtime.product_output_policy import lane_run_dir_meets_product_bar

    sections_root = Path(run_dir) / "modular_r4" / "sections"
    lane_base = sections_root / lane
    out: dict[str, Any] = {
        "lane": lane,
        "authorized": False,
        "state": "NOT_RUN",
        "reason": "",
        "run_dir": None,
        "run_id": None,
    }

    ptr = _load_json(lane_base / "latest_successful_real_run.json")
    if ptr:
        rel = str(ptr.get("run_dir") or "").strip()
        rd = (Path(repo) / rel).resolve() if rel and not Path(rel).is_absolute() else Path(rel)
        if rel and rd.is_dir():
            ok, reason = lane_run_dir_meets_product_bar(rd)
            x3 = _lane_x3_from_artifact_dir(rd) or "UNKNOWN"
            if ok:
                out.update(
                    {
                        "authorized": True,
                        "state": f"AUTHORIZED:{x3}",
                        "run_dir": str(rd),
                        "run_id": str(ptr.get("run_id") or rd.name),
                        "reason": "ok",
                    }
                )
                return out
            out["reason"] = reason

    # Non-authorized: derive the most specific available state.
    pre_run = load_integrated_lane_pre_run_failure(Path(run_dir), lane) or {}
    blocker = str(pre_run.get("blocker") or "").strip()
    latest = latest_lane_run_dir_any(sections_root, lane)
    if latest is not None:
        x3 = _lane_x3_from_artifact_dir(latest)
        if x3:
            out.update(
                {
                    "state": f"EXECUTED_{x3}",
                    "run_dir": str(latest),
                    "run_id": latest.name,
                    "reason": out["reason"] or f"x3_not_authorized:{x3}",
                }
            )
            return out
    if blocker:
        out.update({"state": f"PRE_RUN_BLOCKED:{blocker}", "reason": blocker})
        return out
    out["reason"] = out["reason"] or "no_lane_run_dir"
    return out


def classify_all_lane_states(repo: Path, run_dir: Path) -> dict[str, dict[str, Any]]:
    return {lane: classify_lane_state(repo, run_dir, lane) for lane in GENERATED_LANES}


def select_patch_lanes(
    lane_states: Mapping[str, Mapping[str, Any]],
    *,
    sections_csv: str = "",
    force_lanes_csv: str = "",
) -> list[str]:
    """Target lanes in canonical dependency order (``GENERATED_LANES``).

    Default (no ``--sections``): exactly the non-authorized lanes. Explicit
    ``--sections`` must name known lanes; an authorized lane is refused unless it is
    also named in ``--force-lanes``.
    """
    force = {s.strip() for s in str(force_lanes_csv or "").split(",") if s.strip()}
    unknown_force = sorted(force - set(GENERATED_LANES))
    if unknown_force:
        raise PatchRunInputError(f"--force-lanes names unknown lane(s): {', '.join(unknown_force)}")

    explicit = [s.strip() for s in str(sections_csv or "").split(",") if s.strip()]
    if explicit:
        unknown = sorted(set(explicit) - set(GENERATED_LANES))
        if unknown:
            raise PatchRunInputError(
                f"--sections names unknown lane(s): {', '.join(unknown)}. "
                f"Known lanes: {', '.join(GENERATED_LANES)}"
            )
        targets = {lane for lane in explicit}
    else:
        targets = {
            lane
            for lane, st in lane_states.items()
            if not bool(st.get("authorized"))
        }

    blocked = sorted(
        lane
        for lane in targets
        if bool(lane_states.get(lane, {}).get("authorized")) and lane not in force
    )
    if blocked:
        raise PatchRunInputError(
            f"refusing to re-dispatch authorized lane(s) {', '.join(blocked)} — green lanes "
            "stay banked. Name them in --force-lanes to override."
        )
    return [lane for lane in GENERATED_LANES if lane in targets]


# --------------------------------------------------------------------- plan


@dataclass
class PatchPlan:
    repo: Path
    run_dir: Path
    targeting: PatchTargeting
    lane_states: dict[str, dict[str, Any]]
    target_lanes: list[str]
    force_lanes: tuple[str, ...] = ()


def build_patch_plan(
    run_dir: Path | str,
    *,
    sections_csv: str = "",
    force_lanes_csv: str = "",
) -> PatchPlan:
    rd = Path(str(run_dir)).expanduser()
    if not rd.is_dir():
        raise PatchRunInputError(f"--patch-run dir does not exist: {rd}")
    rd = rd.resolve()
    sections_root = rd / "modular_r4" / "sections"
    if not sections_root.is_dir():
        raise PatchRunInputError(
            f"--patch-run dir has no modular_r4/sections tree (not an integrated modular "
            f"run dir): {rd}"
        )
    repo = find_repo_root(rd)
    try:
        rd.relative_to(repo)
    except ValueError as exc:
        raise PatchRunInputError(
            f"--patch-run dir {rd} does not resolve inside a repo root ({repo})."
        ) from exc

    targeting = derive_patch_targeting(repo, rd)
    lane_states = classify_all_lane_states(repo, rd)
    target_lanes = select_patch_lanes(
        lane_states,
        sections_csv=sections_csv,
        force_lanes_csv=force_lanes_csv,
    )
    force = tuple(s.strip() for s in str(force_lanes_csv or "").split(",") if s.strip())
    return PatchPlan(
        repo=repo,
        run_dir=rd,
        targeting=targeting,
        lane_states=lane_states,
        target_lanes=target_lanes,
        force_lanes=force,
    )


def render_patch_plan(plan: PatchPlan) -> str:
    t = plan.targeting
    jd_desc = t.job_description_ref or (
        f"inline_text({len(t.job_description_text)} chars)" if t.job_description_text else "(none)"
    )
    brief_desc = t.manual_brief if t.manual_brief and Path(t.manual_brief).is_file() else (
        f"inline_text({len(t.manual_brief)} chars)" if t.manual_brief else "(none)"
    )
    lines = [
        f"PATCH RUN PLAN run_dir={plan.run_dir}",
        f"targeting: company={t.target_company!r} role={t.target_role!r} "
        f"level={t.target_level!r} mode={t.generation_mode}",
        f"  jd: {jd_desc}",
        f"  brief: {brief_desc}",
        "lane states:",
    ]
    for lane in GENERATED_LANES:
        st = plan.lane_states[lane]
        marker = "PATCH" if lane in plan.target_lanes else "keep "
        lines.append(f"  [{marker}] {lane:<22} {st['state']}")
    order = ", ".join(plan.target_lanes) if plan.target_lanes else "(none — all lanes authorized)"
    lines.append(f"target lanes (dispatch order): {order}")
    return "\n".join(lines)


# --------------------------------------------------------------------- dispatch


def _default_dispatch_lane(
    *,
    plan: PatchPlan,
    lane: str,
    lane_provider: str,
) -> dict[str, Any]:
    """Dispatch one lane exactly like the integrated full run's serial Phase-1 loop."""
    from apps_rg.runtime.orchestration.canonical_dispatch import (
        run_canonical_apps_rg_from_cli_primitives,
    )
    from apps_rg.runtime.section_cli_defaults import (
        CLI_PROVIDER_RESOLUTION_CLI_OVERRIDE,
        resolve_cli_x1d_judges,
    )
    from apps_rg.runtime.section_lane_temperature import default_temperature_for_section

    t = plan.targeting
    result = run_canonical_apps_rg_from_cli_primitives(
        target_company=t.target_company,
        target_role=t.target_role,
        jd="",
        job_description_ref=t.job_description_ref,
        job_description_text=t.job_description_text,
        manual_brief=t.manual_brief,
        resume_path="",
        source_resume_text="",
        generation_mode="strategic_tailor",
        artifact_dir="",
        section=lane,
        lane_provider=lane_provider,
        lane_provider_resolution_source=CLI_PROVIDER_RESOLUTION_CLI_OVERRIDE,
        lane_temperature=default_temperature_for_section(lane),
        lane_x1d_judges=resolve_cli_x1d_judges(None, section_id=lane),
    )
    return dict(result) if isinstance(result, dict) else {}


def _dispatch_patch_lanes(
    plan: PatchPlan,
    *,
    lane_provider: str,
    dispatch_fn: DispatchFn | None = None,
) -> dict[str, dict[str, Any]]:
    """Serial dispatch of target lanes with the full run's upstream + fault semantics."""
    from apps_rg.runtime.integrated_lane_evidence_packaging import (
        emit_integrated_lane_pre_run_failure,
    )
    from apps_rg.runtime.product_output_policy import (
        phase1_dispatch_hard_failed,
        product_fail_closed_runtime,
    )
    from apps_rg.runtime.reasoning.employment_bullet_pool import REQUIRED_BULLET_IDS
    from apps_rg.runtime.section_execution_plan import NARRATIVE_UPSTREAM_BULLET_LANE
    from apps_rg.runtime.validators.companion_bullet_finalization import (
        PRE_RUN_UPSTREAM_NOT_FINALIZED_BLOCKER,
        companion_accepted_in_modular_sections_root,
    )

    dispatch = dispatch_fn or _default_dispatch_lane
    repo = plan.repo
    sections_root = plan.run_dir / "modular_r4" / "sections"
    results: dict[str, dict[str, Any]] = {}
    aborted = False
    abort_reason = ""

    for lane in plan.target_lanes:
        if aborted:
            results[lane] = {"prior_abort": abort_reason, "exit_status": "error"}
            emit_integrated_lane_pre_run_failure(
                sections_root=sections_root,
                integrated_dir=plan.run_dir,
                repo_root=repo,
                lane_id=lane,
                blocker="PHASE1_PRIOR_LANE_FAILED",
                dispatch_result=results[lane],
                lane_exec_status="pre_run_blocked:PHASE1_PRIOR_LANE_FAILED",
            )
            continue
        upstream = NARRATIVE_UPSTREAM_BULLET_LANE.get(lane)
        if upstream is not None:
            expected_ids = tuple(REQUIRED_BULLET_IDS.get(upstream, ()))
            if not companion_accepted_in_modular_sections_root(
                repo,
                sections_root,
                upstream_section_id=upstream,
                expected_bullet_ids=expected_ids,
            ):
                results[lane] = {
                    "fault": "upstream_not_finalized",
                    "upstream_lane": upstream,
                    "exit_status": "error",
                }
                emit_integrated_lane_pre_run_failure(
                    sections_root=sections_root,
                    integrated_dir=plan.run_dir,
                    repo_root=repo,
                    lane_id=lane,
                    blocker=PRE_RUN_UPSTREAM_NOT_FINALIZED_BLOCKER,
                    dispatch_result=results[lane],
                    lane_exec_status=(
                        f"pre_run_blocked:{PRE_RUN_UPSTREAM_NOT_FINALIZED_BLOCKER}"
                    ),
                )
                continue
        try:
            results[lane] = dispatch(plan=plan, lane=lane, lane_provider=lane_provider)
        except Exception as exc:  # guardian: allow-broad-exception -- mirror full-run phase1 lane fail-soft loop
            results[lane] = {"fault": "exception", "error": str(exc), "exit_status": "error"}
        if product_fail_closed_runtime() and phase1_dispatch_hard_failed(results[lane]):
            aborted = True
            abort_reason = f"dispatch_failed:{lane}"
    return results


# --------------------------------------------------------------------- aggregation


def aggregate_patched_run(
    plan: PatchPlan,
    *,
    lane_dispatch_results: Mapping[str, Mapping[str, Any]],
    lane_provider: str,
    run_token: str,
) -> dict[str, Any]:
    """Re-run the integrated run's app-side aggregation chain with the SAME functions.

    Mirrors the Phase-1 tail of ``run_modular_resume_generation``: lane run-dir
    materialization → generated_lane_rollup → locked copy → final resume assembly →
    rg_output merge → outputs/generated_resume.json → artifact gate → recipe lane
    policy → ``finalize_integrated_run_lane_evidence`` (evidence status + RUN_LINKS).
    """
    from apps_rg.l2_recipe.modular_lane_adapter import build_section_provider_call_record
    from apps_rg.l2_recipe.modular_lane_recipe_policy import (
        summarize_modular_lane_recipe_policy,
    )
    from apps_rg.l2_recipe.modular_resume_generation import (
        LANE_DISPATCH_MODULES,
        ModularResumeInputPackage,
        _phase1_materialize_lane_run_dir,
        _phase1_missing_lane_record,
    )
    from apps_rg.l2_recipe.modular_rg_output_builder import (
        build_rg_output_from_modular_sections,
        load_lane_l2_from_section_refs,
    )
    from apps_rg.l2_recipe.resume_artifact_gate import (
        merge_manifest_after_artifact_gate,
        persist_json_product_outputs,
        verify_full_resume_artifact_bundle,
    )
    from apps_rg.runtime.assembly.final_resume_manifest import FinalResumePaths
    from apps_rg.runtime.integrated_lane_evidence_packaging import (
        emit_integrated_lane_pre_run_failure,
        finalize_integrated_run_lane_evidence,
    )
    from apps_rg.runtime.internal.final_resume_assembler import assemble_final_resume
    from apps_rg.runtime.internal.generated_lane_rollup import build_modular_lane_rollup
    from apps_rg.runtime.internal.locked_copy_builder import build_locked_copy
    from apps_rg.runtime.product_output_policy import product_fail_closed_runtime
    from apps_rg.runtime.resume_resolution import load_lane_base_resume_json

    repo = plan.repo
    art = plan.run_dir
    modular_root = art / "modular_r4"
    sections_root = modular_root / "sections"
    dispatch_results: dict[str, dict[str, Any]] = {
        k: dict(v) for k, v in lane_dispatch_results.items()
    }
    lane_exec_status: dict[str, str] = {}

    lane_run_dirs: dict[str, Path] = {}
    for lane in GENERATED_LANES:
        rd = _phase1_materialize_lane_run_dir(
            repo=repo,
            sections_root=sections_root,
            integrated_dir=art,
            lane=lane,
            lane_provider=lane_provider,
            lane_dispatch_results=dispatch_results,
            lane_exec_status=lane_exec_status,
            emit_integrated_lane_pre_run_failure=emit_integrated_lane_pre_run_failure,
            product_fail_closed=product_fail_closed_runtime(),
        )
        if rd is not None:
            lane_run_dirs[lane] = rd

    rollup_blob: dict[str, Any] | None = None
    assembly_gates_ok: bool | None = None
    section_output_refs: dict[str, str] = {}
    merge_receipt_rel: str | None = None
    rg_output_merge_receipt_rel: str | None = None
    gen_resume: dict[str, Any] | None = None
    final_schema_valid = False
    build_ok = False
    merged_err = "patch_merge_not_attempted"
    lane_load_errors: dict[str, str] = {}

    if len(lane_run_dirs) == len(GENERATED_LANES):
        rollup_blob = build_modular_lane_rollup(repo, lane_run_dirs)
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
        base_resume_obj, canonical_base_resume_path, _ = load_lane_base_resume_json(repo_root=repo)
        paths = FinalResumePaths(
            repo_root=repo,
            rollup_json=rollup_dir / "generated_lane_rollup.json",
            locked_manifest=locked_dir / "locked_copy_manifest.json",
            locked_x2=locked_dir / "locked_copy_x2_gate_outputs.json",
            base_resume=canonical_base_resume_path,
            output_dir=modular_root / "final_resume_assembly",
        )
        asm = assemble_final_resume(paths, skip_preflight=False)
        assembly_gates_ok = bool(asm.get("gates_all_pass"))
        receipt_path = asm["paths"]["receipt"]
        try:
            merge_receipt_rel = receipt_path.relative_to(art).as_posix()
        except ValueError:
            merge_receipt_rel = str(receipt_path)

        if assembly_gates_ok:
            input_package = ModularResumeInputPackage(
                repo_root=repo,
                target_company=plan.targeting.target_company,
                target_role=plan.targeting.target_role,
            )
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
                run_id=run_token,
                reject_mocked_lanes=True,
            )
            build_ok = bool(build.ok)
            merged_err = build.failure_reason or build.schema_error or ""
            final_schema_valid = bool(build.schema_valid and build.ok)
            gen_resume = build.rg_output if build_ok else None
            merge_out = modular_root / "outputs" / "rg_output_merge_receipt.json"
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
    else:
        assembly_gates_ok = False

    # Section provider call records — same shapes as the full run.
    section_call_records: list[dict[str, Any]] = []
    for i, lane in enumerate(GENERATED_LANES):
        rd = lane_run_dirs.get(lane)
        if rd is None or not rd.is_dir():
            from apps_rg.runtime.integrated_lane_evidence_packaging import (
                load_integrated_lane_pre_run_failure,
            )

            pre_run = load_integrated_lane_pre_run_failure(art, lane)
            decisive = str((pre_run or {}).get("blocker") or "PHASE1_NO_RUN_DIR")
            section_call_records.append(
                _phase1_missing_lane_record(
                    lane,
                    i,
                    0,
                    0,
                    lane_provider,
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
                self_consistency_requested=0,
                self_consistency_executed=0,
                provider_profile=lane_provider,
            ),
        )

    recipe_lane_policy = summarize_modular_lane_recipe_policy(
        section_call_records,
        enforce_product_lane_requirements=True,
    )

    # Decisive status — same rules as the full run's Phase-1 branch.
    decisive = "FAIL"
    failure = ""
    if rollup_blob is None:
        failure = "phase1_incomplete_lane_artifacts"
    elif assembly_gates_ok is False:
        failure = "deterministic_assembly_gates_failed"
    elif lane_load_errors:
        failure = "lane_l2_load_errors:" + ";".join(
            f"{k}={v}" for k, v in sorted(lane_load_errors.items())
        )
    elif build_ok:
        decisive = "PASS"
    elif assembly_gates_ok is True:
        failure = merged_err or "modular_rg_output_merge_failed"
    else:
        failure = "deterministic_assembly_failed_unknown"

    if recipe_lane_policy.get("fatal_lane_failures"):
        decisive = "FAIL"
        failure = "fatal_lane_recipe_policy:" + "; ".join(
            f'{f["section_lane"]}:{f.get("decisive_reason_code") or ""}'
            for f in recipe_lane_policy["fatal_lane_failures"][:8]
        )

    # Artifact gate (full-run ResumeArtifactGateStep equivalent).
    artifact_gate_status = "not_attempted"
    if decisive == "PASS" and isinstance(gen_resume, dict) and gen_resume:
        try:
            persist_json_product_outputs(art, generated_resume=gen_resume)
            rep = verify_full_resume_artifact_bundle(art)
            merge_manifest_after_artifact_gate(art, shape_rep=rep)
            artifact_gate_status = "verified"
        except RuntimeError as exc:
            decisive = "FAIL"
            failure = str(exc)
            artifact_gate_status = "failed"

    # Evidence status refresh + parent RUN_LINKS (same finalizer as the full run).
    finalize_integrated_run_lane_evidence(
        repo,
        art,
        correlation_id=run_token,
        section_call_records=section_call_records,
        recipe_lane_policy=recipe_lane_policy,
    )

    _write_json(
        modular_root / "section_provider_calls.json",
        {
            "schema_version": "apps_rg.section_provider_calls.phase1.v2",
            "run_id": run_token,
            "modular_root_rel": "modular_r4",
            "provider_call_count": sum(
                1 for r in section_call_records if r.get("provider_call_attempted") is True
            ),
            "locked_sections_provider_calls_detected": False,
            "real_lane_invocation_attempted": True,
            "records": section_call_records,
            "lane_dispatch_modules": list(LANE_DISPATCH_MODULES),
            "decisive_status": decisive,
            "pass_source": "merged_rg_output_direct_lanes" if decisive == "PASS" else "",
            "recipe_lane_policy": recipe_lane_policy,
            "patch_run": True,
        },
    )

    from apps_rg.runtime.orchestration.canonical_dispatch import (
        _augment_integrated_manifest_with_apps_rg_docx,
    )

    _augment_integrated_manifest_with_apps_rg_docx(art)

    eligibility: dict[str, Any] = {"eligible": False, "reasons": ["output_manifest_missing"]}
    manifest_doc = _load_json(art / "apps_rg_output_manifest.json")
    if manifest_doc is not None:
        from apps_rg.runtime.package.apps_rg_full_resume_x3_eligibility import (
            evaluate_apps_rg_full_success_eligibility,
        )

        ok, reasons = evaluate_apps_rg_full_success_eligibility(
            manifest=manifest_doc,
            run_root=art,
        )
        eligibility = {"eligible": ok, "reasons": reasons}

    return {
        "decisive_status": decisive,
        "failure_reason": failure,
        "lanes_resolved": sorted(lane_run_dirs),
        "lane_run_dirs": {k: str(v) for k, v in lane_run_dirs.items()},
        "assembly_gates_ok": assembly_gates_ok,
        "merge_receipt_rel": merge_receipt_rel,
        "rg_output_merge_receipt_rel": rg_output_merge_receipt_rel,
        "final_schema_valid": final_schema_valid,
        "artifact_gate_status": artifact_gate_status,
        "recipe_lane_policy": recipe_lane_policy,
        "full_success_eligibility": eligibility,
    }


# --------------------------------------------------------------------- execute


def execute_patch_run(
    plan: PatchPlan,
    *,
    dry_run: bool = False,
    dispatch_fn: DispatchFn | None = None,
    aggregate_fn: Callable[..., dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Run the patch plan: dispatch target lanes, re-aggregate, write receipt.

    Returns a result dict including ``exit_code`` (0 only when all 11 lanes are
    authorized post-patch AND the aggregation decisive status is PASS — same outcome
    bar as the integrated full run).
    """
    if dry_run:
        print(render_patch_plan(plan), flush=True)
        print("DRY RUN: patch-run plan only — no lanes dispatched, nothing executed.", flush=True)
        return {"exit_code": 0, "dry_run": True, "target_lanes": list(plan.target_lanes)}

    from apps_rg.l2_recipe.r4_generation_mode import resolve_apps_rg_modular_lane_provider
    from apps_rg.runtime.run_bundle_index import repo_relative_posix
    from apps_rg.runtime.runtime_proof_layout import (
        require_manifest_for_modular_sections_root,
    )
    from apps_rg.runtime.sections_root_manifest import emit_sections_root_manifest

    repo_here = find_repo_root()
    if repo_here.resolve() != plan.repo.resolve():
        raise PatchRunInputError(
            f"patch-run execution requires the run dir's repo root ({plan.repo}) to be the "
            f"active checkout ({repo_here}); run patch-run from that checkout "
            "(dry-run works from anywhere)."
        )

    lane_provider = resolve_apps_rg_modular_lane_provider()
    sections_root = plan.run_dir / "modular_r4" / "sections"
    if not (sections_root / "sections_root_manifest.json").is_file():
        emit_sections_root_manifest(
            repo_root=plan.repo,
            sections_root_abs=sections_root,
            source_env_literal=MODULAR_R4_SECTIONS_ROOT_ENV,
            correlation_id=None,
            integrated_run_ref=repo_relative_posix(plan.repo, plan.run_dir.resolve()),
            run_links_ref=None,
            notes=f"patch_run sections root (run_dir={plan.run_dir.name})",
        )

    prior_states = {lane: plan.lane_states[lane]["state"] for lane in GENERATED_LANES}
    run_token = f"patch_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"

    saved_env = {
        name: os.environ.get(name)
        for name in (MODULAR_R4_SECTIONS_ROOT_ENV, _WHOLE_RUN_ENVELOPE_ENV, _CORRELATED_CLI_RUN_ENV)
    }
    os.environ[MODULAR_R4_SECTIONS_ROOT_ENV] = str(sections_root.resolve())
    os.environ[_WHOLE_RUN_ENVELOPE_ENV] = "1"
    os.environ[_CORRELATED_CLI_RUN_ENV] = repo_relative_posix(plan.repo, plan.run_dir.resolve())
    try:
        require_manifest_for_modular_sections_root(
            sections_root, env_name=MODULAR_R4_SECTIONS_ROOT_ENV
        )
        dispatch_results = _dispatch_patch_lanes(
            plan,
            lane_provider=lane_provider,
            dispatch_fn=dispatch_fn,
        )
        aggregate = aggregate_fn or aggregate_patched_run
        agg = aggregate(
            plan,
            lane_dispatch_results=dispatch_results,
            lane_provider=lane_provider,
            run_token=run_token,
        )
    finally:
        for name, val in saved_env.items():
            if val is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = val

    new_states_full = classify_all_lane_states(plan.repo, plan.run_dir)
    new_states = {lane: new_states_full[lane]["state"] for lane in GENERATED_LANES}
    lane_dir_chosen = {
        lane: new_states_full[lane].get("run_dir") for lane in GENERATED_LANES
    }
    all_authorized = all(bool(new_states_full[lane]["authorized"]) for lane in GENERATED_LANES)
    decisive = str(agg.get("decisive_status") or "FAIL")
    exit_code = 0 if (all_authorized and decisive == "PASS") else 1

    receipt = {
        "schema_version": "apps_rg_patch_run_receipt_v1",
        "generated_at_utc": _utc_now(),
        "run_dir": str(plan.run_dir),
        "run_token": run_token,
        "patched_lanes": list(plan.target_lanes),
        "force_lanes": list(plan.force_lanes),
        "prior_states": prior_states,
        "new_states": new_states,
        "lane_dir_chosen_per_lane": lane_dir_chosen,
        "lane_dispatch_results": {
            lane: {
                "exit_status": str(res.get("exit_status") or ""),
                "x3_disposition": str(res.get("x3_disposition") or ""),
                "fault": str(res.get("fault") or ""),
                "artifact_dir": str(res.get("artifact_dir") or ""),
            }
            for lane, res in dispatch_results.items()
        },
        "targeting_sources": dict(plan.targeting.sources),
        "lane_provider": lane_provider,
        "decisive_status": decisive,
        "failure_reason": str(agg.get("failure_reason") or ""),
        "all_lanes_authorized": all_authorized,
        "full_success_eligibility": agg.get("full_success_eligibility"),
        "exit_code": exit_code,
        "explicit_non_claims": [
            "patch-run does not re-emit root X3 — root x3_disposition_receipt.json / "
            "r4_run_manifest.json / terminal_ret_packet.json remain the original "
            "integrated run's Exit record (apps_rg never emits X3)",
            "authorized lanes were not re-dispatched (banked evidence preserved)",
            "locked deterministic sections untouched",
        ],
    }
    _write_json(plan.run_dir / PATCH_RUN_RECEIPT_ARTIFACT, receipt)

    print(
        f"patch_run completed: decisive_status={decisive} "
        f"all_lanes_authorized={all_authorized} exit_code={exit_code}",
        flush=True,
    )
    print(f"patch_run_receipt={(plan.run_dir / PATCH_RUN_RECEIPT_ARTIFACT).as_posix()}", flush=True)

    return {
        "exit_code": exit_code,
        "dry_run": False,
        "decisive_status": decisive,
        "all_lanes_authorized": all_authorized,
        "patched_lanes": list(plan.target_lanes),
        "prior_states": prior_states,
        "new_states": new_states,
        "receipt_path": str(plan.run_dir / PATCH_RUN_RECEIPT_ARTIFACT),
        "aggregation": agg,
    }


def run_patch_from_cli(args: Any) -> int:
    """CLI entry: ``python -m apps_rg --patch-run <run_dir> [...]``."""
    try:
        plan = build_patch_plan(
            str(getattr(args, "patch_run", "") or ""),
            sections_csv=str(getattr(args, "sections", "") or ""),
            force_lanes_csv=str(getattr(args, "force_lanes", "") or ""),
        )
    except PatchRunInputError as exc:
        print(f"ERROR: {exc}", flush=True)
        return PatchRunInputError.exit_code

    if not bool(getattr(args, "dry_run", False)):
        print(render_patch_plan(plan), flush=True)

    try:
        result = execute_patch_run(plan, dry_run=bool(getattr(args, "dry_run", False)))
    except PatchRunInputError as exc:
        print(f"ERROR: {exc}", flush=True)
        return PatchRunInputError.exit_code
    return int(result.get("exit_code", 1))


__all__ = [
    "PATCH_RUN_RECEIPT_ARTIFACT",
    "PatchPlan",
    "PatchRunInputError",
    "PatchTargeting",
    "aggregate_patched_run",
    "build_patch_plan",
    "classify_all_lane_states",
    "classify_lane_state",
    "derive_patch_targeting",
    "execute_patch_run",
    "latest_lane_run_dir_any",
    "parse_cli_command_flags",
    "render_patch_plan",
    "run_patch_from_cli",
    "select_patch_lanes",
]
