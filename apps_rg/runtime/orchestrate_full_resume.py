"""Single-entry apps_rg offline + lane-generation orchestrator (no agentic_core).

Runs section dispatches → rollup → locked copy → assembly → DOCX manifest → render → resume package X3.
Post–lane steps (8–13) invoke no providers, Qwen, or judges."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable, Sequence

from apps_rg.runtime.locked_copy.locked_copy_manifest import sha256_hex

RUNTIME_PROOFS = "artifacts/apps_rg/runtime_proofs"
PLANNED_DOCX_REL = f"{RUNTIME_PROOFS}/docx/amit_ayer_resume_v1.docx"
POINTER_PATH = Path("apps_rg/resume/base/active_base_resume_pointer.json")
CANONICAL_BASE_RESUME_REPO_REL = Path("apps_rg/resume/base/amit_ayer_base_resume_v1.json")

from apps_rg.l2_recipe.modular_resume_generation import LANE_DISPATCH_MODULES

LANE_MODULES: tuple[str, ...] = LANE_DISPATCH_MODULES


def find_repo_root(start: Path | None = None) -> Path:
    here = (start or Path(__file__)).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "apps_rg" / "resume" / "base").exists():
            return parent
    return Path.cwd()


def _read_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def _merge_active_resume_pointer(repo: Path, base_resume_abs: Path) -> Callable[[], None]:
    """Merge active_resume_path into pointer JSON; restore previous file on close."""
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


def resolve_effective_base_resume(repo: Path, base_resume_override: Path | None) -> tuple[Path, bool]:
    """Return (resolved absolute Path, whether canonical default path was used)."""
    rr = repo.resolve()
    if base_resume_override is None:
        return (rr / CANONICAL_BASE_RESUME_REPO_REL).resolve(), True
    cand = base_resume_override if base_resume_override.is_absolute() else (rr / base_resume_override)
    return cand.resolve(), False


def validate_base_resume_for_orchestration(repo: Path, base_resume_override: Path | None) -> tuple[Path, bool, str, str]:
    """
    Fail fast before any subprocess if default or override resume is absent.

    Returns (effective_path_abs, default_used, posix_rel, sha256_hex_digest).
    """
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
                f"expected {eff}; abort before Qwen, X1D judges, or DOCX render. "
                "Restore amit_ayer_base_resume_v1.json or pass --base-resume to an alternate file "
                "under the workspace."
            )
        raise ValueError(
            f"base resume (--base-resume) not found: {eff}; abort before Qwen, X1D judges, or DOCX render."
        )

    raw = eff.read_text(encoding="utf-8")
    bhash = sha256_hex(raw)
    posix_rel = eff.relative_to(rr).as_posix()
    return eff, default_used, posix_rel, bhash


def _run_subprocess(argv: Sequence[str], *, cwd: Path, label: str) -> None:
    proc = subprocess.run(
        list(argv),
        cwd=str(cwd),
        text=True,
        capture_output=True,
        shell=False,
        check=False,
    )
    if proc.returncode != 0:
        tail = (proc.stderr or proc.stdout or "").strip()[-4000:]
        raise RuntimeError(f"{label} failed (exit {proc.returncode}): {tail}")


def _run_docx_emit(repo: Path, planned_docx_posix: str) -> dict[str, Any]:
    from apps_rg.runtime.render.docx_manifest_builder import (
        PLANNED_DOCX_POSIX,
        build_docx_manifest,
        resolve_docx_manifest_paths,
    )
    from apps_rg.runtime.render.docx_renderer import DocxRendererPaths, build_docx_from_final_resume

    _ = PLANNED_DOCX_POSIX  # default reference
    mf_paths = resolve_docx_manifest_paths(repo, planned_docx_posix=planned_docx_posix)
    mf = build_docx_manifest(mf_paths)
    if not mf["gates_all_pass"]:
        raise RuntimeError(f"docx_manifest_builder X2 failed: {mf['failed_gate_ids']}")
    norm_rel = planned_docx_posix.replace("\\", "/")
    out_docx = (repo / norm_rel).resolve()
    dr = DocxRendererPaths(
        repo_root=repo,
        final_resume_json=mf_paths.final_resume_json,
        docx_manifest_json=mf_paths.output_dir / "docx_manifest.json",
        output_dir=out_docx.parent,
        output_docx=out_docx,
    )
    dx = build_docx_from_final_resume(dr)
    if not dx["gates_all_pass"]:
        raise RuntimeError(f"docx_renderer X2 failed: {dx['failed_gate_ids']}")
    return {"manifest": mf, "render": dx}


def _package_x3_emit(repo: Path) -> dict[str, Any]:
    from apps_rg.runtime.package.resume_package_manifest import resolve_resume_package_paths
    from apps_rg.runtime.package.resume_package_x3 import emit_resume_package_artifacts

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
    allow_test_mock_provider: bool,
    jd_text: str | None,
    briefing: str | None,
    base_resume: Path | None,
    output_docx: Path | None,
) -> dict[str, Any]:
    repo = repo.resolve()
    pv = str(provider or "").strip().lower()
    if pv == "mock" and not allow_test_mock_provider:
        raise ValueError(
            "`--provider mock` requires `--allow-test-mock-provider` for orchestrated lane subprocesses. "
            "Mock provider is test-only plumbing evidence and is not runtime proof. "
            "Runtime proof requires REAL_LLM generation (`--provider qwen_vllm`)."
        )
    if mock_judges and not allow_test_mock_judges:
        raise ValueError(
            "`--mock-judges` requires `--allow-test-mock-judges` for orchestrated lane subprocesses. "
            "Mock judges are test-only evaluator plumbing and cannot produce runtime proof."
        )
    eff_abs, default_used, base_resume_path_posix, base_resume_hash = validate_base_resume_for_orchestration(repo, base_resume)
    restore_pointer = _merge_active_resume_pointer(repo, eff_abs)
    try:
        for mod in LANE_MODULES:
            lane_argv = [
                sys.executable,
                "-m",
                mod,
                "--provider",
                provider,
                "--x1d-judges",
                x1d_judges,
            ]
            if pv == "mock":
                lane_argv.append("--allow-test-mock-provider")
            if allow_non_allow_exit_zero:
                lane_argv.append("--allow-non-allow-exit-zero")
            if mock_judges:
                lane_argv.append("--mock-judges")
                lane_argv.append("--allow-test-mock-judges")
            if jd_text is not None:
                lane_argv.extend(["--jd-text", jd_text])
            if briefing is not None:
                lane_argv.extend(["--briefing", briefing])
            _run_subprocess(lane_argv, cwd=repo, label=f"dispatch:{mod}")

        _run_subprocess([sys.executable, "-m", "apps_rg.runtime.reports.generated_lane_rollup"], cwd=repo, label="rollup")
        _run_subprocess([sys.executable, "-m", "apps_rg.runtime.locked_copy.locked_copy_builder"], cwd=repo, label="locked_copy")
        _run_subprocess(
            [sys.executable, "-m", "apps_rg.runtime.assembly.final_resume_assembler"], cwd=repo, label="final_resume_assembler"
        )

        planned_rel = PLANNED_DOCX_REL.replace("\\", "/")
        if output_docx is not None:
            outp = output_docx if output_docx.is_absolute() else (repo / output_docx)
            outp = outp.resolve()
            if outp.name != "amit_ayer_resume_v1.docx":
                raise ValueError(
                    f"--output-docx basename must be amit_ayer_resume_v1.docx for DOCX X2 (got {outp.name!r})",
                )
            planned_rel = str(outp.relative_to(repo.resolve()).as_posix())
        dx_bundle = _run_docx_emit(repo, planned_rel)
        mf = dx_bundle["manifest"]
        dx = dx_bundle["render"]

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

        docx_final = repo / planned_rel.replace("\\", "/")
        paths_out = {
            "final_docx": docx_final.resolve().as_posix(),
            "final_resume_json": (repo / f"{RUNTIME_PROOFS}/final_resume_assembly/final_resume.json").resolve().as_posix(),
            "generated_lane_rollup": rollup_path.resolve().as_posix(),
            "locked_copy_manifest": (repo / f"{RUNTIME_PROOFS}/locked_copy/locked_copy_manifest.json").resolve().as_posix(),
            "docx_manifest": (repo / f"{RUNTIME_PROOFS}/docx_manifest/docx_manifest.json").resolve().as_posix(),
            "docx_render_manifest": (repo / f"{RUNTIME_PROOFS}/docx/docx_render_manifest.json").resolve().as_posix(),
            "resume_package_x3_disposition": emitted["resume_package_x3_disposition_path"]
            .resolve()
            .as_posix(),
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
                "note": (
                    "X3 disposition does not expose a single-package authorization_scope; "
                    "see per-lane PLUMBING_ONLY contracts in lane manifests."
                ),
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
            "docx_manifest_result": {
                "gates_all_pass": mf.get("gates_all_pass"),
                "failed_gate_ids": mf.get("failed_gate_ids"),
            },
            "docx_render_result": {
                "gates_all_pass": dx.get("gates_all_pass"),
                "failed_gate_ids": dx.get("failed_gate_ids"),
            },
            "non_generation_calls": disposition.get("non_generation_stage_guarantees"),
        }
        result["rollup_id"] = rollup.get("rollup_id")
        result["explicit_waiver_needed"] = disposition.get("explicit_waiver_needed_for_allow_when_section_review")
        result["base_resume_path"] = base_resume_path_posix
        result["base_resume_default_used"] = default_used
        result["base_resume_exists"] = True
        result["base_resume_hash"] = base_resume_hash
        return result
    finally:
        if restore_pointer:
            restore_pointer()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="apps_rg end-to-end resume proof + DOCX refresh (seven lanes → package X3).")
    parser.add_argument("--provider", choices=["mock", "qwen_vllm"], default="qwen_vllm")
    parser.add_argument("--x1d-judges", default="gemini_pro,openai_chatgpt,anthropic_claude")
    parser.add_argument("--mock-judges", action="store_true", help="Forward to lanes (requires `--allow-test-mock-judges`).")
    parser.add_argument(
        "--allow-test-mock-judges",
        action="store_true",
        help=(
            "Required when using `--mock-judges`: forwards test-only hatch to each lane subprocess. "
            "Mock judges cannot produce runtime proof."
        ),
    )
    parser.add_argument(
        "--allow-test-mock-provider",
        action="store_true",
        help=(
            "Required when using `--provider mock`: forwards `--allow-test-mock-provider` to each lane subprocess. "
            "Plumbing-only; not REAL_LLM runtime proof."
        ),
    )
    parser.add_argument("--allow-non-allow-exit-zero", action="store_true")
    parser.add_argument(
        "--base-resume",
        type=Path,
        default=None,
        help=(
            "Optional: override active_resume_path merge (repo-relative or absolute). "
            f"Default when omitted: {CANONICAL_BASE_RESUME_REPO_REL.as_posix()}"
        ),
    )
    parser.add_argument("--job-description", type=Path, default=None, dest="jd_path")
    parser.add_argument("--briefing", type=Path, default=None, dest="briefing_path")
    parser.add_argument(
        "--output-docx",
        type=Path,
        default=None,
        help=f"Must stay basename amit_ayer_resume_v1.docx (default {PLANNED_DOCX_REL}).",
    )
    args = parser.parse_args(argv)

    repo = find_repo_root()
    jd_txt = _read_text_file(args.jd_path) if args.jd_path else None
    br_txt = _read_text_file(args.briefing_path) if args.briefing_path else None

    try:
        out = run_orchestration(
            repo=repo,
            provider=args.provider,
            x1d_judges=args.x1d_judges,
            allow_non_allow_exit_zero=args.allow_non_allow_exit_zero,
            mock_judges=args.mock_judges,
            allow_test_mock_judges=args.allow_test_mock_judges,
            allow_test_mock_provider=args.allow_test_mock_provider,
            jd_text=jd_txt,
            briefing=br_txt,
            base_resume=args.base_resume,
            output_docx=args.output_docx,
        )
    except (RuntimeError, ValueError) as exc:
        sys.stderr.write(f"ORCHESTRATOR_BLOCKED: {exc}\n")
        return 2

    print(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    sts = str(out["orchestrator_status"]).upper()
    if sts == "FAIL":
        return 1
    if args.allow_non_allow_exit_zero:
        return 0
    return 0 if sts == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
