"""Test-only offline lane orchestration — not product spine proof.

Moved from ``apps_rg.runtime.internal.lane_batch.run_orchestration`` so product
packages cannot invoke offline batch rollup + package disposition.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from apps_rg.runtime.internal.lane_batch import (
    CANONICAL_BASE_RESUME_REPO_REL,
    POINTER_PATH,
    RUNTIME_PROOFS,
    SECTION_ORDER,
    find_repo_root,
    resolve_effective_base_resume,
)
from apps_rg.runtime.locked_copy.locked_copy_manifest import sha256_hex
from apps_rg.runtime.section_cli_defaults import resolve_allow_non_allow_exit_zero
from apps_rg.runtime.section_lane_temperature import default_temperature_for_section

__all__ = ["run_orchestration", "validate_base_resume_for_orchestration"]


def _merge_active_resume_pointer(repo: Path, base_resume_abs: Path) -> Callable[[], None]:
    bp = base_resume_abs.resolve()
    repo_r = repo.resolve()
    try:
        rel = bp.relative_to(repo_r).as_posix()
    except ValueError as exc:
        raise ValueError(f"--base-resume must be inside repository root: {bp}") from exc
    pointer = repo_r / POINTER_PATH
    previous = pointer.read_text(encoding="utf-8") if pointer.is_file() else None
    merged: dict[str, Any] = {}
    if previous:
        try:
            merged = json.loads(previous)
            if not isinstance(merged, dict):
                merged = {}
        except json.JSONDecodeError:
            merged = {}
    merged["active_resume_path"] = rel
    pointer.parent.mkdir(parents=True, exist_ok=True)
    pointer.write_text(json.dumps(merged, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    def restore() -> None:
        if previous is None:
            try:
                pointer.unlink()
            except OSError:
                pass
        else:
            pointer.write_text(previous, encoding="utf-8")

    return restore


def validate_base_resume_for_orchestration(
    repo: Path, base_resume_override: Path | None
) -> tuple[Path, bool, str, str]:
    eff, default_used = resolve_effective_base_resume(repo, base_resume_override)
    rr = repo.resolve()
    try:
        eff.relative_to(rr)
    except ValueError as exc:
        raise ValueError(f"base resume path must be inside repository root (got {eff})") from exc

    if not eff.is_file():
        if default_used:
            raise ValueError(
                f"canonical default base resume is missing ({CANONICAL_BASE_RESUME_REPO_REL.as_posix()}): "
                f"expected {eff}; abort before Qwen, X1D judges, or DOCX render."
            )
        raise ValueError(f"base resume (--base-resume) not found: {eff}")

    raw = eff.read_text(encoding="utf-8")
    return eff, default_used, eff.relative_to(rr).as_posix(), sha256_hex(raw)


def _run_subprocess(
    argv: Sequence[str],
    *,
    cwd: Path,
    label: str,
    extra_env: Mapping[str, str] | None = None,
) -> None:
    env = {**os.environ, **dict(extra_env or {})}
    proc = subprocess.run(
        list(argv),
        cwd=str(cwd),
        text=True,
        capture_output=True,
        shell=False,
        check=False,
        env=env,
    )
    if proc.returncode != 0:
        tail = (proc.stderr or proc.stdout or "").strip()[-4000:]
        raise RuntimeError(f"{label} failed (exit {proc.returncode}): {tail}")


def _package_x3_emit(repo: Path) -> dict[str, Any]:
    from apps_rg.runtime.internal.resume_package_disposition import emit_resume_package_artifacts
    from apps_rg.runtime.package.resume_package_manifest import resolve_resume_package_paths

    return emit_resume_package_artifacts(paths=resolve_resume_package_paths(repo_root=repo))


def _summarize_lane_x2(rollup: dict[str, Any]) -> dict[str, Any]:
    lanes = rollup.get("lanes") if isinstance(rollup.get("lanes"), dict) else {}
    out: dict[str, Any] = {}
    for lk, row in lanes.items():
        if not isinstance(row, dict):
            continue
        out[str(lk)] = {
            "runtime_generation_status": row.get("runtime_generation_status"),
            "x2_failed": row.get("x2_failed"),
            "x3_code": row.get("x3_code"),
        }
    return out


def _l6_handoff_summary(disposition: dict[str, Any]) -> dict[str, Any]:
    audit = disposition.get("l6_shadow_handoff_audit") if isinstance(disposition.get("l6_shadow_handoff_audit"), dict) else {}
    return {
        "l6_handoff_blocked": audit.get("l6_handoff_blocked"),
        "l6_handoff_agg_checks_all_true": (disposition.get("deterministic_proof_summary") or {}).get(
            "l6_handoff_agg_checks_all_true"
        ),
        "aggregate_checks": audit.get("aggregate_checks"),
    }


def _orchestrator_outcome_status(disposition: dict[str, Any]) -> str:
    if disposition.get("deterministic_blocked"):
        return "FAIL"
    code = str(disposition.get("final_x3_code") or "")
    if code == "X3_ALLOW":
        return "PASS"
    if "BLOCK" in code:
        return "FAIL"
    if code.startswith("X3_REVIEW"):
        return "PARTIAL"
    return "PARTIAL"


def run_orchestration(
    *,
    repo: Path,
    provider: str,
    x1d_judges: str,
    allow_non_allow_exit_zero: bool,
    mock_judges: bool,
    allow_test_mock_judges: bool,
    jd_text: str | None,
    briefing: str | None,
    base_resume: Path | None,
    output_docx: Path | None,
) -> dict[str, Any]:
    repo = repo.resolve()
    pv = str(provider or "").strip().lower()
    if pv and pv != "qwen_vllm":
        raise ValueError(
            f"Unsupported orchestrator --provider {provider!r} (expected qwen_vllm). "
            "Offline lane tests: set APPS_RG_QWEN_OFFLINE_CONTRACT_STUB=1 in the environment."
        )
    if mock_judges and not allow_test_mock_judges:
        raise ValueError(
            "mock_judges=True requires allow_test_mock_judges=True for orchestrated lane subprocesses."
        )
    eff_abs, default_used, base_resume_path_posix, base_resume_hash = validate_base_resume_for_orchestration(
        repo, base_resume
    )
    restore_pointer = _merge_active_resume_pointer(repo, eff_abs)
    try:
        _ = resolve_allow_non_allow_exit_zero(allow_non_allow_exit_zero)
        inputs_dir = repo / RUNTIME_PROOFS / "orchestrator_lane_inputs"
        inputs_dir.mkdir(parents=True, exist_ok=True)
        jd_path = inputs_dir / "job_description.txt"
        br_path = inputs_dir / "briefing.txt"
        jd_path.write_text(str(jd_text or "").strip() + "\n", encoding="utf-8")
        br_path.write_text(str(briefing or "").strip() + "\n", encoding="utf-8")
        jd_rel = jd_path.relative_to(repo).as_posix()
        br_rel = br_path.relative_to(repo).as_posix()
        judge_csv = str(x1d_judges or "").strip() or "gemini_pro,openai_chatgpt,anthropic_claude"

        for section in SECTION_ORDER:
            lane_argv: list[str] = [
                sys.executable,
                "-m",
                "apps_rg",
                "--section",
                section,
                "--jd",
                jd_rel,
                "--manual-brief",
                br_rel,
                "--provider",
                pv or "qwen_vllm",
                "--temperature",
                str(default_temperature_for_section(section)),
                "--x1d-judges",
                judge_csv,
            ]
            if allow_non_allow_exit_zero:
                lane_argv.append("--allow-non-allow-exit-zero")
            lane_env: dict[str, str] | None = None
            if mock_judges and allow_test_mock_judges:
                lane_env = {
                    "APPS_RG_TEST_HARNESS": "1",
                    "APPS_RG_MOCK_JUDGES": "1",
                }
            _run_subprocess(lane_argv, cwd=repo, label=f"canonical:{section}", extra_env=lane_env)

        from apps_rg.runtime.internal.generated_lane_rollup import build_rollup, render_markdown
        from apps_rg.runtime.internal.locked_copy_builder import build_locked_copy

        rollup_data = build_rollup(rollup_artifact_mode="real")
        rollup_dir = repo / RUNTIME_PROOFS / "generated_lane_rollup"
        rollup_dir.mkdir(parents=True, exist_ok=True)
        (rollup_dir / "generated_lane_rollup.json").write_text(
            json.dumps(rollup_data, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        (rollup_dir / "generated_lane_rollup.md").write_text(
            render_markdown(rollup_data),
            encoding="utf-8",
        )
        lc = build_locked_copy()
        if lc["receipt"].get("x2_failed"):
            raise RuntimeError(f"locked_copy X2 failed: {lc['receipt'].get('x2_failed_gate_ids')}")

        from apps_rg.runtime.internal.final_resume_assembler import assemble_final_resume

        asm = assemble_final_resume()
        if not asm["gates_all_pass"]:
            raise RuntimeError(f"final_resume_assembler failed: {asm['failed_gate_ids']}")

        if output_docx is not None:
            raise ValueError(
                "DOCX offline emit removed; omit --output-docx (package X3 is JSON-only by default)."
            )

        fr_x2_path = repo / RUNTIME_PROOFS / "final_resume_assembly" / "final_resume_x2_gate_outputs.json"
        fr_x2_blob = json.loads(fr_x2_path.read_text(encoding="utf-8"))

        emitted = _package_x3_emit(repo)
        disposition = emitted["resume_package_disposition"]

        rollup_path = repo / RUNTIME_PROOFS / "generated_lane_rollup" / "generated_lane_rollup.json"
        rollup = json.loads(rollup_path.read_text(encoding="utf-8"))
        lanes = rollup.get("lanes") if isinstance(rollup.get("lanes"), dict) else {}
        l6_refs: dict[str, Any] = {}
        for lk, row in lanes.items():
            if not isinstance(row, dict):
                continue
            refs = row.get("artifact_refs") if isinstance(row.get("artifact_refs"), dict) else {}
            rel = refs.get("l6_shadow_eval_package.json")
            p = repo / str(rel).replace("\\", "/") if isinstance(rel, str) else None
            l6_refs[str(lk)] = {
                "artifact_repo_relative": rel,
                "exists": bool(p and p.is_file()),
            }

        paths_out = {
            "final_resume_json": (repo / f"{RUNTIME_PROOFS}/final_resume_assembly/final_resume.json").resolve().as_posix(),
            "generated_lane_rollup": rollup_path.resolve().as_posix(),
            "locked_copy_manifest": (repo / f"{RUNTIME_PROOFS}/locked_copy/locked_copy_manifest.json").resolve().as_posix(),
            "resume_package_x3_disposition": emitted["resume_package_x3_disposition_path"].resolve().as_posix(),
            "package_manifest": emitted["resume_package_manifest_path"].resolve().as_posix(),
        }

        sec_x3 = disposition.get("section_level_x3") if isinstance(disposition.get("section_level_x3"), dict) else {}
        det_proof = disposition.get("deterministic_proof_summary") if isinstance(disposition.get("deterministic_proof_summary"), dict) else {}

        lane_codes = sorted(
            {
                str(r.get("rollup_x3_code"))
                for r in (sec_x3.get("lanes_detail") or [])
                if isinstance(r, dict) and r.get("rollup_x3_code") is not None
            },
        )

        result: dict[str, Any] = {
            "orchestrator_status": _orchestrator_outcome_status(disposition),
            "package_x3_code": disposition.get("final_x3_code"),
            "deterministic_blocked": disposition.get("deterministic_blocked"),
            "package_authorization_scope": disposition.get("authorization_scope")
            if isinstance(disposition.get("authorization_scope"), str)
            else {
                "note": "per-lane PLUMBING_ONLY contracts in lane manifests",
                "distinct_rollup_lane_x3_codes": lane_codes,
            },
            "paths": paths_out,
            "deterministic_gates_summary": det_proof,
            "generated_lane_x2_and_x3_summary": _summarize_lane_x2(rollup),
            "section_x3_summary": {
                "all_generated_lane_x3_allow": sec_x3.get("all_generated_lane_x3_allow"),
                "rollup_x3_allow_lane_keys": sec_x3.get("rollup_x3_allow_lane_keys"),
                "rollup_x3_non_allow": sec_x3.get("rollup_x3_non_allow"),
            },
            "l6_handoff_summary": {**_l6_handoff_summary(disposition), "generated_lane_l6_artifact_audit": l6_refs},
            "final_resume_assembly_result": {
                "all_pass": fr_x2_blob.get("all_pass"),
                "failed_gate_ids": fr_x2_blob.get("failed_gate_ids"),
            },
            "docx_emit_skipped": True,
            "non_generation_calls": disposition.get("non_generation_stage_guarantees"),
        }
        result["rollup_id"] = rollup.get("rollup_id")
        result["explicit_waiver_needed"] = disposition.get("explicit_waiver_needed_for_allow_when_section_review")
        result["base_resume_path"] = base_resume_path_posix
        result["base_resume_default_used"] = default_used
        result["base_resume_exists"] = True
        result["base_resume_hash"] = base_resume_hash
        from apps_rg.runtime.non_product_proof_stamp import orchestrator_non_product_stamp

        result.update(orchestrator_non_product_stamp())
        receipt_path = repo / RUNTIME_PROOFS / "orchestrator_non_product_receipt.json"
        receipt_path.parent.mkdir(parents=True, exist_ok=True)
        receipt_path.write_text(
            json.dumps(result, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        result["orchestrator_non_product_receipt"] = receipt_path.relative_to(repo).as_posix()
        return result
    finally:
        if restore_pointer:
            restore_pointer()
