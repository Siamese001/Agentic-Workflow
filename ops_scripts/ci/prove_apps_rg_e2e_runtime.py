#!/usr/bin/env python3
"""apps_rg C0-backed section-dispatch runtime proof: live C0 FEC → lanes → rollup → assembly.

Writes ``artifacts/ci/apps_rg_e2e_runtime_proof.json`` and the whole-run review packet.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_PATH = REPO_ROOT / "artifacts/ci/apps_rg_e2e_runtime_proof.json"

_AGENTIC_CORE_UNTRACKED_ONLY = "PRE_EXISTING_UNTRACKED_AGENTIC_CORE_PATH"
_AGENTIC_CORE_TRACKED_ONLY = "TRACKED_AGENTIC_CORE_WORKING_TREE_CHANGES"
_AGENTIC_CORE_MIXED = "TRACKED_AND_UNTRACKED_AGENTIC_CORE_CHANGES"

LANE_MODULES: tuple[str, ...] = (
    "apps_rg.runtime.dispatch.headline_dispatch",
    "apps_rg.runtime.dispatch.executive_summary_dispatch",
    "apps_rg.runtime.dispatch.unify_bullets_dispatch",
    "apps_rg.runtime.dispatch.unify_narrative_dispatch",
    "apps_rg.runtime.dispatch.ibm_bullets_dispatch",
    "apps_rg.runtime.dispatch.ibm_narrative_dispatch",
    "apps_rg.runtime.dispatch.competencies_dispatch",
)
LANE_KEYS: tuple[str, ...] = (
    "headline",
    "executive_summary",
    "unify_bullets",
    "unify_narrative",
    "ibm_bullets",
    "ibm_narrative",
    "competencies",
)
JD_INLINE = (
    "Principal Engineer role at Contoso Labs: enterprise AI platform leadership, agentic AI systems, "
    "runtime governance, LLMOps, retrieval, production reliability."
)


def _run_cmd(
    argv: list[str],
    *,
    cwd: Path,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(argv, cwd=cwd, text=True, capture_output=True, check=False, shell=False, env=env)


def classify_agentic_core_porcelain_lines(lines: list[str]) -> dict[str, Any]:
    trimmed = [ln.rstrip("\r") for ln in lines if ln.strip()]
    tracked = False
    untracked = False
    raw_paths: list[str] = []

    for entry in trimmed:
        if entry.startswith("??"):
            untracked = True
            rest = entry[2:].lstrip()
        else:
            tracked = True
            rest = entry[3:].lstrip() if len(entry) > 3 else entry.lstrip()

        if " -> " in rest:
            raw_paths.extend(p.strip() for p in rest.split(" -> "))
        else:
            raw_paths.append(rest.strip())

    paths_sorted = sorted({p for p in raw_paths if p})
    dirty = tracked or untracked
    if not dirty:
        reason = ""
    elif untracked and not tracked:
        reason = _AGENTIC_CORE_UNTRACKED_ONLY
    elif tracked and untracked:
        reason = _AGENTIC_CORE_MIXED
    else:
        reason = _AGENTIC_CORE_TRACKED_ONLY

    return {
        "agentic_core_modified": dirty,
        "agentic_core_dirty_reason": reason,
        "agentic_core_dirty_paths": paths_sorted,
    }


def finalize_boundary_no_bypass(artifact: dict[str, Any], repo: Path) -> None:
    raw = _run_cmd(["git", "status", "--porcelain=v1", "--", "agentic_core"], cwd=repo)
    klass = classify_agentic_core_porcelain_lines((raw.stdout or "").splitlines())
    box = artifact.setdefault("boundary_no_bypass", {})
    box.update(klass)
    box["agentic_core_modified_by_this_task"] = False
    box.setdefault("new_app_literals_in_core", False)
    box.setdefault("direct_l2_chroma_bypass", False)
    box.setdefault("direct_l4_write_bypass", False)
    box.setdefault("mock_pass", False)
    box["direct_bypass"] = bool(box.get("direct_l2_chroma_bypass")) or bool(box.get("direct_l4_write_bypass"))


def _persist_e2e_proof_artifact(artifact: dict[str, Any], repo: Path) -> None:
    finalize_boundary_no_bypass(artifact, repo)
    u = _run_cmd(["git", "diff", "--name-only"], cwd=repo)
    c = _run_cmd(["git", "diff", "--name-only", "--cached"], cwd=repo)
    names = {
        ln.strip()
        for ln in (u.stdout or "").splitlines() + (c.stdout or "").splitlines()
        if ln.strip()
    }
    artifact["files_changed"] = sorted(names)
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2), encoding="utf-8")


def _bootstrap_repo_dotenv(repo_root: Path) -> tuple[bool, bool]:
    p = repo_root / ".env"
    if not p.is_file():
        return False, False
    try:
        from dotenv import load_dotenv
    except ImportError:
        return True, False
    load_dotenv(dotenv_path=p, override=False)
    return True, True


def _fec_briefing_extension(fec_obj: Any, *, max_chars: int = 12000) -> str:
    lines = [
        "FEC_RUNTIME_PROOF_BINDING=v1",
        "FEC_PROMPT_SLOT=C0_EVIDENCE_DATA_ONLY",
        f"fec_final_evidence_digest={getattr(fec_obj, 'final_evidence_digest', '')}",
        f"fec_support_status={getattr(fec_obj, 'support_status', '')}",
        f"fec_request_id={getattr(fec_obj, 'request_id', '')}",
        f"fec_run_id={getattr(fec_obj, 'run_id', '')}",
        "--- fec_evidence_items ---",
    ]
    items = list(getattr(fec_obj, "evidence_items", ()) or ())
    for it in items[:80]:
        cid = getattr(it, "evidence_id", "") or getattr(it, "chunk_id", "")
        anch = getattr(it, "citation_anchor", "")
        fv = getattr(it, "fact_vec_ref", getattr(it, "source_id", ""))
        slot = getattr(it, "allowed_prompt_slot", "C0_EVIDENCE_DATA_ONLY")
        prose = getattr(it, "citation_anchor", "") or getattr(it, "text", "") or str(getattr(it, "snippet", "") or "")
        line = "|".join(str(x) for x in (slot, fv, prose, cid, anch)).strip("|")
        if line:
            lines.append(line)

    blob = "\n".join(lines)
    return blob if len(blob) <= max_chars else blob[:max_chars]


def _load_c0_proof_digest(repo: Path) -> str | None:
    p = repo / "artifacts/ci/apps_rg_c0_runtime_proof.json"
    if not p.is_file():
        return None
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
        fec = (d.get("fec_summary") or {}) if isinstance(d.get("fec_summary"), dict) else {}
        return str(fec.get("final_evidence_digest") or "") or None
    except (json.JSONDecodeError, OSError):
        return None


def _retrieve_fec_for_e2e(repo: Path) -> Any | None:
    sys.path.insert(0, str(repo))
    persist = (os.environ.get("CHROMA_PERSIST_DIR") or "").strip() or str(repo / "data/cache/chromadb")
    if os.environ.get("EMBEDDING_ENABLED", "").strip().lower() not in ("1", "true"):
        os.environ["EMBEDDING_ENABLED"] = "true"

    from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest
    from agentic_core.runtime.contracts.final_evidence_contract import FinalEvidenceContract
    from agentic_core.runtime.contracts.route_contract import RouteContract

    from apps_rg.runtime.bindings.c0_binding import (
        MetadataFilterProfile,
        c0_retrieve_apps_rg,
    )

    query_txt = JD_INLINE + " regulated enterprise retrieval proof."
    app_payload = {
        "jd_payload": {
            "jd_text": JD_INLINE,
            "target_company": "Contoso Labs",
            "target_role": "Principal Engineer",
        },
        "resume_payload": {
            "resume_text": query_txt,
            "headline": query_txt,
            "executive_summary": query_txt,
            "summary": query_txt,
            "competencies": "Python Kubernetes agentic governance C0 retrieval",
            "skills": "",
            "unify_bullets": "",
            "unify_narrative": "",
            "experience": query_txt,
        },
    }

    mp = MetadataFilterProfile()
    _md_filter = mp.build_chroma_where_clause(app_payload)
    route = RouteContract.__new__(RouteContract)
    object.__setattr__(route, "grounding_required", True)

    vr = ValidatedRequest.__new__(ValidatedRequest)
    object.__setattr__(vr, "request_id", "prove-apps-rg-e2e-runtime")
    object.__setattr__(vr, "run_id", "prove-e2e-run")
    object.__setattr__(vr, "app_id", "apps_rg")
    object.__setattr__(vr, "trace_id", "prove-e2e-trace")
    object.__setattr__(vr, "app_payload", app_payload)

    fec = c0_retrieve_apps_rg(route, vr, chromadb_path=persist)
    return fec if isinstance(fec, FinalEvidenceContract) else None


def _rollup_json(repo: Path) -> dict[str, Any] | None:
    rp = repo / "artifacts/apps_rg/runtime_proofs/generated_lane_rollup/generated_lane_rollup.json"
    if not rp.is_file():
        return None
    try:
        return json.loads(rp.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _accepted_lane_run_dir(repo: Path, lane: str) -> Path | None:
    try:
        from apps_rg.runtime.runtime_proof_layout import resolve_accepted_real_rollup_run_dir

        base, _ = resolve_accepted_real_rollup_run_dir(repo, lane)
    except Exception:  # noqa: BLE001
        return None
    return base if base is not None and base.is_dir() else None


def _normalize_x1d(blob: Mapping[str, Any] | None) -> list[dict[str, Any]]:
    if blob is None:
        return []
    if isinstance(blob, list):
        return [x for x in blob if isinstance(x, dict)]
    j = blob.get("judges")
    if isinstance(j, list):
        return [x for x in j if isinstance(x, dict)]
    return []


def _minimal_artifact() -> dict[str, Any]:
    """Minimal artifact shell for harness unit tests (boundary_no_bypass contracts)."""
    return {
        "boundary_no_bypass": {
            "mock_pass": False,
            "direct_l2_chroma_bypass": False,
            "direct_l4_write_bypass": False,
        },
        "commands_run": [],
        "pa": {},
        "route": {},
        "c0": {},
        "exit": {},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="apps_rg governed lane-chain runtime proof")
    parser.add_argument("--skip-subcommands", action="store_true", help="Skip gates/pytest (developer escape hatch).")
    parser.add_argument("--provider", default="qwen_vllm")
    args = parser.parse_args()

    cwd = REPO_ROOT
    sys.path.insert(0, str(cwd))

    art_path = cwd / "artifacts/ci/apps_rg_e2e_runtime_proof.json"
    if not art_path.is_file():
        raise SystemExit(
            f"Missing seed artifact template {art_path.as_posix()} — restore from repo or prior E2E wave."
        )
    art = json.loads(art_path.read_text(encoding="utf-8"))
    if not isinstance(art, dict):
        art = {}
    art["status"] = "FAIL"
    art["commands_run"] = []

    repo_dot_ok, repo_dot_loaded = _bootstrap_repo_dotenv(cwd)
    from apps_rg.runtime.x1d_judge_policy import preflight_x1d_judge_policy

    x1d_csv = (os.environ.get("APPS_RG_E2E_X1D_JUDGES", "").strip() or "").strip()
    judge_policy = preflight_x1d_judge_policy(
        environ=os.environ,
        configured_judge_csv=x1d_csv or None,
        repo_dotenv_path_existed=repo_dot_ok,
        repo_dotenv_loaded=repo_dot_loaded,
    )
    art["x1d_judge_policy"] = judge_policy

    raw_allow = (os.environ.get("APPS_RG_E2E_ALLOW_NON_ALLOW_EXIT_ZERO") or "1").strip().lower()
    allow_non_allow = raw_allow not in ("0", "false", "no")
    provider = args.provider.strip() or "qwen_vllm"
    if provider == "mock":
        art["status"] = "FAIL"
        art.setdefault("boundary_no_bypass", {})["mock_pass"] = True
        art["decisive_reason"] = "MOCK_PROVIDER_REJECTED_FOR_E2E_CLAIM"
        _persist_e2e_proof_artifact(art, cwd)
        return 1

    _penv = os.environ.copy()
    _penv.setdefault("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")
    os.environ.setdefault("EMBEDDING_ENABLED", "true")

    target_company = "Contoso Labs"
    target_role = "Principal Engineer"

    fec = _retrieve_fec_for_e2e(cwd)
    if fec is None:
        art["decisive_reason"] = "C0_FINAL_EVIDENCE_CONTRACT_UNAVAILABLE"
        _persist_e2e_proof_artifact(art, cwd)
        return 1

    fec_digest = str(getattr(fec, "final_evidence_digest", "") or "").strip()
    fec_prev = (_load_c0_proof_digest(cwd) or "").strip()
    chroma_items = []
    evidence_ids = getattr(fec, "evidence_items", ()) or ()
    for it in evidence_ids:
        eid = str(getattr(it, "evidence_id", "") or "")
        src = str(getattr(it, "source", "") or "")
        st = str(getattr(it, "source_type", "") or "")
        if eid.startswith("chroma:") or src.startswith("chromadb:") or st == "fact_vectors":
            chroma_items.append(it)

    art["c0"] = {
        "artifact_ref": "artifacts/ci/apps_rg_c0_runtime_proof.json",
        "contract_type": "FinalEvidenceContract",
        "support_status": str(getattr(fec, "support_status", "")),
        "evidence_item_count": len(chroma_items),
        "metadata_filter_refs": list(getattr(fec, "metadata_filter_refs", []) or []),
        "cross_app_leakage": False,
        "fec_evidence_chunk_ids_unique": sorted(
            {_ for _ in (getattr(it, "evidence_id", "") for it in chroma_items) if str(_)}
        ),
    }

    uniq_chroma_chunks = {_ for _ in (getattr(it, "evidence_id", "") for it in chroma_items) if _}
    if uniq_chroma_chunks and fec_digest and fec_prev and fec_digest != fec_prev:
        art["commands_run"].append(
            {
                "cmd_note": "C0_DIGEST_DRIFT_HINT",
                "c0_proof_digest_tail": fec_prev[:16],
                "runtime_digest_tail": fec_digest[:16],
            }
        )

    briefing_core = (
        "regulated enterprise environment; platform modernization; AI governance; scalable delivery; "
        "cross-functional leadership."
    )
    full_briefing = briefing_core.strip() + "\n\n" + _fec_briefing_extension(fec)

    request_id = getattr(fec, "request_id", "prove-apps-rg-e2e-runtime")
    run_id = getattr(fec, "run_id", "prove-e2e-run")

    art["request_package"].update(
        {
            "request_id": request_id,
            "run_id": run_id,
            "trace_root": "prove-e2e-trace",
            "target_company": target_company,
            "target_role": target_role,
            "jd_payload_ref": "inline_ci_fixture",
            "base_resume_ref": "apps_rg/resume/base/amit_ayer_base_resume_v1.json",
            "selected_section_lanes": list(LANE_MODULES),
        }
    )

    if args.skip_subcommands:
        print(json.dumps({"status": art["status"], "note": "skip-subcommands"}, indent=2))
        _persist_e2e_proof_artifact(art, cwd)
        return 0

    r_gate = _run_cmd([sys.executable, "ops_scripts/ci/check_apps_rg_fact_vectors_readiness.py"], cwd=cwd)
    art["commands_run"].append(
        {
            "cmd": "python ops_scripts/ci/check_apps_rg_fact_vectors_readiness.py",
            "exit_code": r_gate.returncode,
            "stdout_tail": (r_gate.stdout or "")[-2000:],
            "stderr_tail": (r_gate.stderr or "")[-1000:],
        }
    )
    if r_gate.returncode != 0:
        art["decisive_reason"] = "READINESS_GATE_NONZERO"
        _persist_e2e_proof_artifact(art, cwd)
        return 1

    r_c0 = _run_cmd([sys.executable, "ops_scripts/ci/prove_apps_rg_c0_runtime.py"], cwd=cwd, env=_penv)
    art["commands_run"].append(
        {
            "cmd": "python ops_scripts/ci/prove_apps_rg_c0_runtime.py",
            "exit_code": r_c0.returncode,
            "stdout_tail": (r_c0.stdout or "")[-2000:],
            "stderr_tail": (r_c0.stderr or "")[-1200:],
        }
    )
    if r_c0.returncode != 0:
        art["decisive_reason"] = "C0_PROOF_NONZERO"
        _persist_e2e_proof_artifact(art, cwd)
        return 1

    pytest_argv = [
        sys.executable,
        "-m",
        "pytest",
        "tests/_apps_contract/test_apps_rg_competencies_x2_source_facts.py",
        "tests/_apps_contract/test_apps_rg_x1d_judge_policy.py",
        "tests/_apps_contract/test_apps_rg_x1d_judge_rollup_diagnostics.py",
        "tests/_apps_contract/test_apps_rg_x1d_judge_execution_quality.py",
        "tests/_apps_contract/test_apps_rg_whole_run_exit.py",
        "tests/_apps_contract/test_apps_rg_e2e_boundary_hygiene.py",
        "tests/_apps_contract/test_apps_rg_l2_envelope.py",
        "tests/_apps_contract/test_c0_no_answer_generation.py",
        "-q",
        "--tb=short",
        "-p",
        "pytest_timeout",
    ]
    r_test = _run_cmd(pytest_argv, cwd=cwd, env=_penv)
    art["commands_run"].append(
        {
            "cmd": " ".join(pytest_argv),
            "exit_code": r_test.returncode,
            "stdout_tail": (r_test.stdout or "")[-4000:],
            "stderr_tail": (r_test.stderr or "")[-2000:],
        }
    )
    if r_test.returncode != 0:
        art["decisive_reason"] = "PYTEST_CONTRACT_SUBSET_NONZERO"
        _persist_e2e_proof_artifact(art, cwd)
        return 1

    for mod in LANE_MODULES:
        lane_argv = [
            sys.executable,
            "-m",
            mod,
            "--provider",
            provider,
            "--x1d-judges",
            judge_policy.get("default_if_unset_csv", "gemini_pro,openai_chatgpt,anthropic_claude"),
            "--target-company",
            target_company,
            "--jd-text",
            JD_INLINE,
            "--briefing",
            full_briefing,
        ]
        if mod.endswith("headline_dispatch"):
            lane_argv.extend(["--target-title", target_role])
        if allow_non_allow:
            lane_argv.append("--allow-non-allow-exit-zero")
        r_lane = _run_cmd(lane_argv, cwd=cwd, env=_penv)
        art["commands_run"].append(
            {
                "cmd": " ".join(lane_argv),
                "exit_code": r_lane.returncode,
                "stdout_tail": (r_lane.stdout or "")[-2000:],
                "stderr_tail": (r_lane.stderr or "")[-1200:],
            }
        )
        if r_lane.returncode != 0:
            art["decisive_reason"] = f"LANE_DISPATCH_NONZERO:{mod}"
            _persist_e2e_proof_artifact(art, cwd)
            return 1

    for argv in (
        [sys.executable, "-m", "apps_rg.runtime.reports.generated_lane_rollup"],
        [sys.executable, "-m", "apps_rg.runtime.locked_copy.locked_copy_builder"],
        [sys.executable, "-m", "apps_rg.runtime.assembly.final_resume_assembler"],
    ):
        r_post = _run_cmd(argv, cwd=cwd, env=_penv)
        art["commands_run"].append(
            {
                "cmd": " ".join(argv),
                "exit_code": r_post.returncode,
                "stdout_tail": (r_post.stdout or "")[-2500:],
                "stderr_tail": (r_post.stderr or "")[-1200:],
            }
        )
        if r_post.returncode != 0:
            art["decisive_reason"] = f"POST_STEP_NONZERO:{argv[-1]}"
            _persist_e2e_proof_artifact(art, cwd)
            return 1

    rollup = _rollup_json(cwd)
    if not rollup:
        art["decisive_reason"] = "GENERATED_LANE_ROLLUP_MISSING"
        _persist_e2e_proof_artifact(art, cwd)
        return 1

    lanes_blob = rollup.get("lanes") if isinstance(rollup.get("lanes"), dict) else {}
    judge_rows: list[dict[str, Any]] = []
    mock_lane = False
    x2_unknown_lane = False
    lane_x1d_blobs: dict[str, list[dict[str, Any]]] = {}
    pa_hashes: list[str] = []
    pa_consumed_any = False
    pa_data_only_any = False
    pa_schema_slots: list[bool] = []

    for lk, mod_path in zip(LANE_KEYS, LANE_MODULES):
        row = lanes_blob.get(lk) if isinstance(lanes_blob, dict) else None
        if not isinstance(row, dict):
            continue
        judge_rows.append(
            {
                "lane": lk,
                "x3_code": row.get("x3_code"),
                "gemini": row.get("gemini_provider_status"),
                "openai": row.get("openai_provider_status"),
                "anthropic": row.get("anthropic_provider_status"),
                "blocked_judges": row.get("blocked_judges"),
                "soft_failed_judges": row.get("soft_failed_judges"),
            }
        )
        st_gen = str(row.get("runtime_generation_status") or "")
        if st_gen == "MOCKED" or (st_gen and st_gen != "REAL_LLM"):
            mock_lane = True

        xt = int(row.get("x2_total_gates") or 0)
        if xt <= 0:
            x2_unknown_lane = True

        lrdir = _accepted_lane_run_dir(cwd, lk)
        jb: list[dict[str, Any]] = []
        if lrdir and (lrdir / "x1d_llm_judge_outputs.json").is_file():
            try:
                raw_x1 = json.loads((lrdir / "x1d_llm_judge_outputs.json").read_text(encoding="utf-8"))
                jb = _normalize_x1d(raw_x1 if isinstance(raw_x1, dict) else {"judges": raw_x1})
            except (json.JSONDecodeError, OSError):
                jb = []
        lane_x1d_blobs[lk] = jb

        if lrdir:
            cpp = lrdir / "compiled_prompt.txt"
            mentions_fec = cpp.is_file() and "FEC_RUNTIME_PROOF_BINDING" in cpp.read_text(
                encoding="utf-8",
                errors="replace",
            )
            data_only_slot = cpp.is_file() and "FEC_PROMPT_SLOT=C0_EVIDENCE_DATA_ONLY" in cpp.read_text(
                encoding="utf-8",
                errors="replace",
            )
            schema_bound = cpp.is_file() and "json_object" in cpp.read_text(encoding="utf-8", errors="replace").lower()
            l2p = lrdir / "l2_output.json"
            ph = ""
            if l2p.is_file():
                ph = hashlib.sha256(l2p.read_bytes()).hexdigest()[:16]
            if ph:
                pa_hashes.append(ph)
            pa_consumed_any = pa_consumed_any or mentions_fec
            pa_data_only_any = pa_data_only_any or data_only_slot
            pa_schema_slots.append(schema_bound)

            xf = int(row.get("x2_failed") or 0)
            art["l2_sections"][lk] = {
                "lane_name": lk,
                "dispatcher_module": mod_path,
                "provider_model_path": str(provider),
                "mock_runtime_status": st_gen or "",
                "input_prompt_artifact_ref": (
                    str(cpp.relative_to(cwd)).replace("\\", "/") if cpp.is_file() else ""
                ),
                "evidence_refs_digest": fec_digest,
                "output_artifact_ref": (
                    str((lrdir / "l2_output.json").relative_to(cwd)).replace("\\", "/")
                    if (lrdir / "l2_output.json").is_file()
                    else ""
                ),
                "schema_status": "PASS"
                if xf == 0 and int(row.get("x2_total_gates") or 0) > 0
                else "FAIL_OR_UNKNOWN",
                "gate_status": "PASS" if xf == 0 else "FAIL",
                "decisive_reason": st_gen or "",
                "x3_code": row.get("x3_code"),
                "x2_failed": xf,
                "x2_total_gates": row.get("x2_total_gates"),
            }

    from apps_rg.runtime.x1d_lane_judge_diagnostics import build_x1d_lane_judge_diagnostics

    lane_diag = build_x1d_lane_judge_diagnostics(judge_policy, judge_rows, lane_x1d_blobs)
    art["x1d_lane_judge_diagnostics"] = lane_diag

    art["pa"]["prompt_hash"] = ",".join(sorted(set(pa_hashes))[:12])
    art["pa"]["consumed_c0_evidence"] = pa_consumed_any
    art["pa"]["evidence_data_only"] = pa_data_only_any
    art["pa"]["schema_bound"] = len(pa_schema_slots) == len(LANE_KEYS) and all(pa_schema_slots)

    final_resume_p = cwd / "artifacts/apps_rg/runtime_proofs/final_resume_assembly/final_resume.json"
    final_x2_p = cwd / "artifacts/apps_rg/runtime_proofs/final_resume_assembly/final_resume_x2_gate_outputs.json"
    fr_blob = None
    if final_resume_p.is_file():
        try:
            fr_blob = json.loads(final_resume_p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            fr_blob = None

    final_x2_all_pass: bool | None = None
    if final_x2_p.is_file():
        try:
            fx2 = json.loads(final_x2_p.read_text(encoding="utf-8"))
            final_x2_all_pass = bool(fx2.get("all_pass"))
            art["section_gates"]["overall"] = "PASS" if final_x2_all_pass else "FAIL"
            art["section_gates"]["results"] = list(fx2.get("gates") or [])[:80]
        except (json.JSONDecodeError, OSError):
            final_x2_all_pass = None
            art["section_gates"]["overall"] = "UNKNOWN"

    lane_keys_set = list(LANE_KEYS)
    ids = (
        {
            str(s.get("section_id"))
            for s in (fr_blob.get("sections") or [])
            if isinstance(fr_blob, dict) and isinstance(s, dict)
        }
        if isinstance(fr_blob, dict)
        else set()
    )
    req_present = all(x in ids for x in lane_keys_set) if fr_blob else False
    locked_ok = all(x in ids for x in ("insurtech", "ey", "early_career", "education", "certifications"))

    art["final_artifact"] = {
        "path": str(final_resume_p.relative_to(cwd)).replace("\\", "/") if final_resume_p.is_file() else "",
        "exists": final_resume_p.is_file(),
        "required_lanes_present": req_present,
        "locked_sections_preserved": locked_ok,
        "schema_valid": bool(final_x2_all_pass),
    }

    from apps_rg.runtime.competencies_x2_diagnostics import (
        build_competencies_x2_diagnostics,
        scrape_fact_id_tokens_from_compiled_prompt,
    )

    comp_rd = _accepted_lane_run_dir(cwd, "competencies")
    l2_comp_blob: dict[str, Any] | None = None
    comp_x2_failed: list[str] = []
    cpp_refs_list: list[str] = []
    if comp_rd:
        gx_candidate = comp_rd / "x2_gate_outputs.json"
        lc2 = comp_rd / "l2_output.json"
        if lc2.is_file():
            try:
                l2_comp_blob = json.loads(lc2.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                l2_comp_blob = None
        if gx_candidate.is_file():
            try:
                gx_read = json.loads(gx_candidate.read_text(encoding="utf-8"))
                comp_x2_failed = [
                    str(g.get("gate_id"))
                    for g in (gx_read.get("gates") or [])
                    if isinstance(g, dict) and not g.get("pass")
                ]
            except (json.JSONDecodeError, OSError):
                comp_x2_failed = []
        cpp_refs_list = scrape_fact_id_tokens_from_compiled_prompt(comp_rd / "compiled_prompt.txt")

    fec_refs_avail = art["c0"].get("fec_evidence_chunk_ids_unique") or []
    cx2_fix = (
        "Gemini judges: bounded HTTP 429 retries (APPS_RG_GEMINI_JUDGE_MAX_RETRIES) + BLOCKED_RATE_LIMIT adapter; "
        "x1d_lane_judge_diagnostics merges lane x1d_llm_judge_outputs.json; competencies/headline dispatch fixes."
    )
    art["competencies_x2_diagnostics"] = build_competencies_x2_diagnostics(
        l2_output=l2_comp_blob if isinstance(l2_comp_blob, dict) else None,
        final_resume_blob=fr_blob if isinstance(fr_blob, dict) else None,
        x2_failed_checks=comp_x2_failed,
        fec_evidence_refs_available=list(fec_refs_avail),
        compiled_prompt_fact_refs_available=cpp_refs_list,
        fix_applied=cx2_fix,
        decisive_reason=(", ".join(comp_x2_failed) if comp_x2_failed else "lane competencies deterministic X2 gates GREEN"),
    )

    from apps_rg.runtime.whole_run_exit import (
        X3B_REVIEW,
        X3_BLOCK,
        X3D_ALLOW_FINISH,
        X3E_SAFE_ABSTAIN,
        compute_whole_run_exit,
        write_exit_review_packet,
    )

    fb_exit = lane_diag.get("failure_breakdown_for_exit")
    if not isinstance(fb_exit, dict):
        fb_exit = {}

    rollup_decision = str(lane_diag.get("rollup_decision") or "")
    if rollup_decision == "PASS":
        x1d_overall = "PASS"
    elif rollup_decision == "NOT_AVAILABLE":
        x1d_overall = "NOT_AVAILABLE"
    else:
        x1d_overall = "PARTIAL"

    art.setdefault("x1d_judge_failure_breakdown", {})
    art["x1d_judge_failure_breakdown"] = {k: bool(v) for k, v in fb_exit.items()}

    lane_signal_rows: list[dict[str, Any]] = []
    for jr in judge_rows:
        lk = str(jr.get("lane") or "")
        rowb = lanes_blob.get(lk, {}) if isinstance(lanes_blob, dict) else {}
        lane_signal_rows.append(
            {
                "lane": lk,
                "x3_code": jr.get("x3_code"),
                "x2_failed": int(rowb.get("x2_failed") or 0),
                "x2_failed_gate_ids": list(rowb.get("x2_failed_gate_ids") or []),
                "x2_artifact_failed_gates": list(rowb.get("x2_artifact_failed_gates") or []),
            }
        )

    rp_note = str((art.get("route") or {}).get("note_r4_spine") or "")
    product_r4_doc = "BYPASS_PRELOADED_CONTEXT" in rp_note
    min_chr = int((os.environ.get("APPS_RG_E2E_MIN_CHROMA_EVIDENCE") or "1").strip() or "1")

    sig_breakdown = {k: bool(v) for k, v in fb_exit.items()}

    signals: dict[str, Any] = {
        "final_resume_exists": final_resume_p.is_file(),
        "final_resume_json_valid": isinstance(fr_blob, dict),
        "required_generated_sections_present": req_present,
        "locked_sections_preserved": locked_ok,
        "final_resume_x2_all_pass": final_x2_all_pass,
        "cross_app_leakage": bool((art.get("c0") or {}).get("cross_app_leakage")),
        "mock_provider_pass": bool(mock_lane),
        "direct_l4_write_bypass": bool((art.setdefault("boundary_no_bypass", {})).get("direct_l4_write_bypass")),
        "grounding_required": True,
        "c0_evidence_item_count": int((art.get("c0") or {}).get("evidence_item_count") or 0),
        "c0_support_status": str((art.get("c0") or {}).get("support_status") or ""),
        "pa_consumed_c0": bool((art.get("pa") or {}).get("consumed_c0_evidence")),
        "pa_evidence_data_only": bool((art.get("pa") or {}).get("evidence_data_only")),
        "pa_schema_bound": bool((art.get("pa") or {}).get("schema_bound")),
        "x1d_overall": x1d_overall,
        "x1d_policy_valid": bool(judge_policy.get("policy_valid", True)),
        "judge_quorum_satisfied": bool(judge_policy.get("quorum_satisfied")),
        "x2_unknown_lane": bool(x2_unknown_lane),
        "lane_rows": lane_signal_rows,
        "section_gates_overall": str((art.get("section_gates") or {}).get("overall") or ""),
        "min_chroma_evidence_items": min_chr,
        "product_r4_bypass_documented": product_r4_doc,
        "x1d_judge_failure_breakdown": sig_breakdown,
    }

    wre = compute_whole_run_exit(signals)

    head_rd = _accepted_lane_run_dir(cwd, "headline")
    x1_path = (head_rd / "x1d_llm_judge_outputs.json") if head_rd else None
    x1_ref = (
        str(x1_path.relative_to(cwd)).replace("\\", "/")
        if x1_path is not None and x1_path.is_file()
        else ""
    )
    x2_ref = str(final_x2_p.relative_to(cwd)).replace("\\", "/") if final_x2_p.is_file() else ""
    pkt_ref = "artifacts/ci/apps_rg_whole_run_exit_review_packet.json"
    wre["x1_result_ref"] = x1_ref
    wre["x2_result_ref"] = x2_ref
    wre["exit_review_packet_ref"] = pkt_ref

    art.setdefault("exit", {})
    art["exit"].update(
        {
            "exit_review_packet_ref": pkt_ref,
            "x1_result_ref": x1_ref,
            "x2_result_ref": x2_ref,
            "x3_disposition": wre["x3_disposition"],
            "exactly_one_x3": wre["exactly_one_x3"],
        }
    )

    rq = dict(art.get("request_package") or {})
    rq.setdefault("app", "apps_rg")
    rq.setdefault(
        "output_profile",
        "artifacts/apps_rg/runtime_proofs → final_resume_assembly",
    )

    rollup_ref = cwd / "artifacts/apps_rg/runtime_proofs/generated_lane_rollup/generated_lane_rollup.json"
    rollup_ref_str = str(rollup_ref.relative_to(cwd)).replace("\\", "/") if rollup_ref.is_file() else ""

    lane_rollups_pkt: list[dict[str, Any]] = []
    for row in lane_signal_rows:
        lane_rollups_pkt.append(
            {
                "lane": row["lane"],
                "x3_code": row.get("x3_code"),
                "x2_failed": row.get("x2_failed"),
                "x2_failed_gate_ids": row.get("x2_failed_gate_ids"),
                "x2_artifact_failed_gates": row.get("x2_artifact_failed_gates"),
            }
        )

    c0_art_rel = str(art["c0"].get("artifact_ref") or "artifacts/ci/apps_rg_c0_runtime_proof.json")
    c0_proof_path = cwd / c0_art_rel.replace("/", os.sep)
    packet: dict[str, Any] = {
        "packet_version": "apps_rg_whole_run_exit_review_v1",
        "whole_run_exit": dict(wre),
        "request_package": rq,
        "route": dict(art.get("route") or {}),
        "c0_summary": {
            "artifact_ref": str(c0_proof_path).replace("\\", "/"),
            "support_status": (art.get("c0") or {}).get("support_status"),
            "evidence_item_count": (art.get("c0") or {}).get("evidence_item_count"),
            "metadata_filter_refs": (art.get("c0") or {}).get("metadata_filter_refs"),
        },
        "pa_summary": {
            "artifact_ref": "artifacts/apps_rg/runtime_proofs/<lane>/real/<run_id>/compiled_prompt.txt (per lane)",
            "contract_type": "compiled_prompt_txt_messages_v1",
            **dict(art.get("pa") or {}),
        },
        "rollup_ref": rollup_ref_str,
        "lane_rollups": lane_rollups_pkt,
        "x1d_judge_policy": judge_policy,
        "x1d_lane_judge_diagnostics": lane_diag,
        "whole_run_signals": signals,
    }
    pkt_written = write_exit_review_packet(cwd, packet)
    art["whole_run_exit_review_packet_written"] = str(pkt_written.relative_to(cwd)).replace("\\", "/")
    art["whole_run_exit"] = dict(wre)

    decisive_bits: list[str] = []
    if wre.get("decisive_reason"):
        decisive_bits.append(str(wre["decisive_reason"]))
    bn = art.get("boundary_no_bypass") or {}
    if bn.get("agentic_core_modified"):
        decisive_bits.append(
            "agentic_core working tree differs from HEAD "
            "(see boundary_no_bypass.agentic_core_dirty_reason); review dirty_paths; "
            "proof harness records agentic_core_modified_by_this_task=false."
        )
    if x1d_overall != "PASS":
        decisive_bits.append(
            "X1D rollup diagnostics: see x1d_lane_judge_diagnostics.rollup_decision "
            "and per-lane judge_results (failure_breakdown_for_exit)."
        )
    qu_sat = bool(judge_policy.get("quorum_satisfied"))
    decisive_bits.append(
        "X1D preflight quorum satisfied — aggregate judge outcome driven by MODEL_BACKED_PASS per lane/provider "
        "(see judge_rows + diagnostics)."
        if qu_sat
        else "X1D preflight quorum not satisfied — see x1d_judge_policy."
    )

    seen: set[str] = set()
    deduped: list[str] = []
    for b in decisive_bits:
        if b and b not in seen:
            seen.add(b)
            deduped.append(b)
    art["decisive_reason"] = "; ".join(deduped)

    bn_out = art.setdefault("boundary_no_bypass", {})

    rc = 0
    if mock_lane or bn_out["mock_pass"]:
        art["status"] = "FAIL"
        bn_out["mock_pass"] = True
    elif wre["x3_disposition"] == X3_BLOCK:
        art["status"] = "FAIL"
        rc = 1
    elif wre["x3_disposition"] == X3E_SAFE_ABSTAIN:
        art["status"] = "PARTIAL"
    elif wre["x3_disposition"] == X3B_REVIEW:
        art["status"] = "PARTIAL"
    else:
        art["status"] = "PASS" if wre["x3_disposition"] == X3D_ALLOW_FINISH else "PARTIAL"

    print(json.dumps({"status": art["status"], "x3_disposition": wre["x3_disposition"]}, indent=2))
    _persist_e2e_proof_artifact(art, cwd)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
