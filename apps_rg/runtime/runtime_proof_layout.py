"""Run-scoped runtime proof directories (Option B: real/<run_id>/, mock/<run_id>/).

Lane root: artifacts/apps_rg/runtime_proofs/<lane>/
Contract harness (pytest offline stubs): artifacts/apps_rg/runtime_proofs/contract_harness/<run_key>/...
Pointers: latest_real_run.json (latest real-bucket attempt), latest_successful_real_run.json
(accepted REAL_LLM qwen_vllm evidence for rollup), latest_mock_run.json.
Each pointer and per-run ``run_manifest.json`` include ``artifact_links`` (repo-relative paths)
plus explicit ``l2_output_repo_relative`` / ``l6_shadow_eval_package_repo_relative`` when present.
"""
from __future__ import annotations

import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal


from apps_rg.runtime.run_bundle_index import emit_lane_runtime_proof_bundle_index
from apps_rg.runtime.sections_root_manifest import require_manifest_for_modular_sections_root

Bucket = Literal["real", "mock", "plumbing"]

LATEST_SUCCESSFUL_REAL_FILENAME = "latest_successful_real_run.json"
LATEST_PLUMBING_RUN_FILENAME = "latest_plumbing_run.json"
FULL_RESUME_DIR_PREFIX = "full_resume_"

# When set (absolute or repo-relative), lane prepare/finalize and optional dependency
# resolution use ``<root>/<lane>/{mock|real}/<run_id>/`` instead of runtime_proofs.
MODULAR_R4_SECTIONS_ROOT_ENV = "APPS_RG_MODULAR_R4_SECTIONS_ROOT"
CONTRACT_HARNESS_DIR = "contract_harness"
CONTRACT_HARNESS_PREFIXES: tuple[str, ...] = (
    "_w3_contract_",
    "_w4_contract_",
    "_w6_srfs_",
    "_w6_nosrfs_",
    "_w7_exec_",
    "_w7_nosrfs_",
    "_w7_cli_smoke_",
    "_exec_l2_pool_",
    "_exec_x2_pool_",
    "_contract_test_",
)


def modular_sections_root_from_env(repo: Path) -> Path | None:
    raw = os.environ.get(MODULAR_R4_SECTIONS_ROOT_ENV, "").strip()
    if not raw:
        return None
    norm = raw.replace("\\", "/")
    if any(part == ".." for part in norm.split("/")):
        raise ValueError(f"{MODULAR_R4_SECTIONS_ROOT_ENV} must not contain .. segments ({raw!r})")
    cand = Path(raw).expanduser()
    if not cand.is_absolute():
        cand = (repo / cand).resolve()
    else:
        cand = cand.resolve()
    rr = repo.resolve()
    try:
        cand.relative_to(rr)
    except ValueError as exc:
        raise ValueError(
            f"{MODULAR_R4_SECTIONS_ROOT_ENV} must resolve inside repo_root {rr}; "
            f"outside-repo modular roots are not supported ({cand})."
        ) from exc
    return cand


def resolve_modular_latest_l2(repo: Path, lane: str) -> Path | None:
    """Path to ``l2_output.json`` from modular R4 section pointers (Phase 1+), if env is set."""
    from apps_rg.runtime.product_output_policy import product_fail_closed_runtime

    msr = modular_sections_root_from_env(repo)
    if msr is None:
        return None
    require_manifest_for_modular_sections_root(msr, env_name=MODULAR_R4_SECTIONS_ROOT_ENV)
    lane_base = msr / lane
    ptr_order = (
        (LATEST_SUCCESSFUL_REAL_FILENAME,)
        if product_fail_closed_runtime()
        else (
            "latest_mock_run.json",
            "latest_real_run.json",
            LATEST_SUCCESSFUL_REAL_FILENAME,
        )
    )
    for ptr_name in ptr_order:
        data = _read_json_dict(lane_base / ptr_name)
        if not data:
            continue
        rel = data.get("run_dir")
        if not isinstance(rel, str):
            continue
        rd = (repo / rel).resolve()
        l2 = rd / "l2_output.json"
        if l2.is_file() and (
            not product_fail_closed_runtime() or _is_accepted_real_llm_qwen_bundle(rd)
        ):
            return l2
    return None


def resolve_effective_lane_l2_path(repo: Path, lane: str) -> Path | None:
    """Prefer modular per-lane pointers when ``APPS_RG_MODULAR_R4_SECTIONS_ROOT`` is active."""
    hit = resolve_modular_latest_l2(repo, lane)
    if hit is not None:
        return hit
    return resolve_latest_real_l2(repo, lane)


def find_repo_root(start: Path | None = None) -> Path:
    here = (start or Path(__file__)).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "apps_rg" / "resume" / "base").exists():
            return parent
    return Path.cwd()


def is_integrated_whole_run_dir_name(name: str) -> bool:
    """True for ``full_resume_<id>`` integrated CLI run folders under ``runtime_proofs``."""
    return str(name or "").strip().startswith(FULL_RESUME_DIR_PREFIX)


def _whole_run_envelope_active() -> bool:
    return os.environ.get("APPS_RG_WHOLE_RUN_ENVELOPE", "").strip().lower() in (
        "1",
        "true",
        "yes",
    )


def _modular_root_uses_flat_lane_dirs(msr: Path) -> bool:
    """``APPS_RG_MODULAR_R4_SECTIONS_ROOT`` points at ``<full_resume_*>/lanes``."""
    if not _whole_run_envelope_active():
        return False
    resolved = msr.resolve()
    return resolved.name == "lanes" and is_integrated_whole_run_dir_name(resolved.parent.name)


def allocate_full_resume_artifact_dir(repo: Path, explicit: str = "") -> Path:
    """Default whole-run artifact root: ``artifacts/apps_rg/runtime_proofs/full_resume_<id>``."""
    if str(explicit).strip():
        return Path(explicit).expanduser().resolve()
    rid = uuid.uuid4().hex[:12]
    out = repo / "artifacts" / "apps_rg" / "runtime_proofs" / f"{FULL_RESUME_DIR_PREFIX}{rid}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def resolve_phase1_sections_root(artifact_dir: Path, modular_root: Path) -> Path:
    """Phase-1 lane proofs: flat ``lanes/<lane>/`` for integrated runs; else ``modular_r4/sections``."""
    art = Path(artifact_dir).resolve()
    if is_integrated_whole_run_dir_name(art.name):
        lanes = art / "lanes"
        lanes.mkdir(parents=True, exist_ok=True)
        return lanes
    sections = modular_root / "sections"
    sections.mkdir(parents=True, exist_ok=True)
    return sections


def lane_root(repo: Path, lane: str) -> Path:
    return repo / "artifacts" / "apps_rg" / "runtime_proofs" / lane


def contract_harness_root(repo: Path) -> Path:
    """Pytest/contract offline scratch — not product lane rollup inputs."""
    return repo / "artifacts" / "apps_rg" / "runtime_proofs" / CONTRACT_HARNESS_DIR


def is_contract_harness_run_key(name: str) -> bool:
    return any(str(name).startswith(p) for p in CONTRACT_HARNESS_PREFIXES)
  # guardian: allow-return-none-swallow -- P2 burndown: fail-soft optional boundary

def contract_harness_run_dir(repo: Path, run_key: str, *parts: str) -> Path:
    path = contract_harness_root(repo) / run_key
    for part in parts:
        path = path / part
    return path


def proof_bucket_for_provider(provider: str) -> Bucket:
    """Mock harness runs land in ``mock/``; live ``qwen_vllm`` generation uses ``real/``."""
    if str(provider or "").strip().lower() == "mock":
        return "mock"
    return "real"


def run_dir(repo: Path, lane: str, bucket: Bucket, run_id: str) -> Path:
    return lane_root(repo, lane) / bucket / run_id


def rel_posix(path: Path, repo: Path) -> str:
    return path.resolve().relative_to(repo.resolve()).as_posix()


def prepare_runtime_proof_run_dir(
    repo: Path,
    lane: str,
    provider: str,
    run_id: str,
    *,
    placement_bucket: Bucket | None = None,
) -> Path:
    bucket: Bucket = placement_bucket if placement_bucket is not None else proof_bucket_for_provider(provider)
    msr = modular_sections_root_from_env(repo)
    if msr is not None:
        require_manifest_for_modular_sections_root(msr, env_name=MODULAR_R4_SECTIONS_ROOT_ENV)
        if _modular_root_uses_flat_lane_dirs(msr):
            rd = msr / lane
            rd.mkdir(parents=True, exist_ok=True)
            return rd
        rd = msr / lane / bucket / run_id
        rd.mkdir(parents=True, exist_ok=True)
        return rd
    rd = run_dir(repo, lane, bucket, run_id)
    rd.mkdir(parents=True, exist_ok=True)
    return rd


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _read_json_dict(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):  # guardian: allow-return-none-swallow -- P2 burndown: fail-soft optional boundary
        return None
    return raw if isinstance(raw, dict) else None


def _provider_requested_lower(run_dir: Path) -> str:
    """Best-effort provider_requested from artifacts under a run (or lane) directory."""
    for name in ("provider_request.json", "run_manifest.json"):
        d = _read_json_dict(run_dir / name)
        if d:
            pq = str(d.get("provider_requested") or "").strip().lower()
            if pq:
                return pq
    return ""


def is_accepted_real_llm_qwen_bundle(run_dir: Path) -> bool:
    """Public: REAL_LLM + provider_requested qwen_vllm under ``run_dir``."""
    return _is_accepted_real_llm_qwen_bundle(run_dir)


def _is_accepted_real_llm_qwen_bundle(run_dir: Path) -> bool:
    """Rollup/eligibility: REAL_LLM L2 exists and provider_requested is qwen_vllm."""
    l2_path = run_dir / "l2_output.json"
    if not l2_path.is_file():
        return False
    l2 = _read_json_dict(l2_path)
    if not l2:
        return False
    if str(l2.get("runtime_generation_status", "")).strip() != "REAL_LLM":
        return False
    return _provider_requested_lower(run_dir) == "qwen_vllm"


# Repo-relative paths written under each proof run_dir (presence-checked at finalize).
_RUNTIME_PROOF_LINK_FILENAMES: tuple[str, ...] = (
    "l2_output.json",
    "l6_shadow_eval_package.json",
    "l6_shadow_learning.json",
    "l6_future_run_proposals.json",
    "x3_disposition.json",
    "x2_gate_outputs.json",
    "x1d_llm_judge_outputs.json",
    "provider_request.json",
    "compiled_prompt.txt",
    "command_output.txt",
    "real_l2_generation_result.json",
    "prompt_selection_trace.json",
    "section_input_usage_ledger.json",
    "canonical_claim_ledger_v2.json",
    "text_claim_coverage.json",
    "parsed_output.json",
    "selected_fact_plan.json",
    "runtime_payload.json",
    "provider_response.json",
    "c0_metrics.json",
)


def collect_runtime_proof_artifact_links(repo: Path, artifact_dir: Path) -> dict[str, str]:
    """Map filename → repo-relative POSIX path for artifacts present under ``artifact_dir``."""
    ad = artifact_dir.resolve()
    rr = repo.resolve()
    out: dict[str, str] = {}
    for name in _RUNTIME_PROOF_LINK_FILENAMES:
        p = ad / name
        if p.is_file():
            out[name] = rel_posix(p, rr)
    return out


def _should_write_latest_successful_real(
    bucket: Bucket,
    provider_requested: str,
    runtime_generation_status: str,
    artifact_dir: Path,
) -> bool:
    if bucket != "real":
        return False
    if str(provider_requested).strip().lower() != "qwen_vllm":
        return False
    if runtime_generation_status != "REAL_LLM":
        return False
    if not (artifact_dir / "l2_output.json").is_file():
        return False
    return True


def finalize_runtime_proof_run(
    repo: Path,
    lane: str,
    provider: str,
    artifact_dir: Path,
    *,
    run_id: str,
    section_id: str,
    runtime_generation_status: str,
    provider_requested: str,
    provider_attempted: Any,
    command: str | None = None,
    bundle_proof_strict: bool = False,
    run_bundle_index_document_metadata: dict[str, Any] | None = None,
    placement_bucket: Bucket | None = None,
    **manifest_extras: Any,
) -> None:
    """Write run_manifest.json and latest_{real|mock|plumbing}_run.json under lane root."""
    bucket: Bucket = placement_bucket if placement_bucket is not None else proof_bucket_for_provider(provider)
    generated_at_utc = datetime.now(timezone.utc).isoformat()
    cmd = command if command is not None else " ".join(sys.argv)
    run_dir_rel = rel_posix(artifact_dir, repo)
    artifact_links = collect_runtime_proof_artifact_links(repo, artifact_dir)

    manifest: dict[str, Any] = {
        "run_id": run_id,
        "generated_at_utc": generated_at_utc,
        "provider_requested": provider_requested,
        "provider_attempted": provider_attempted,
        "runtime_generation_status": runtime_generation_status,
        "runtime_proof_placement_bucket": bucket,
        "command": cmd,
        "section_id": section_id,
        "run_dir_repo_relative": run_dir_rel,
        "artifact_links": artifact_links,
    }
    manifest.update({k: v for k, v in manifest_extras.items()})
    from apps_rg.runtime.bindings.section_lane_c0_metrics import c0_metrics_run_manifest_fields

    manifest.update(c0_metrics_run_manifest_fields(artifact_dir))
    if "l2_output.json" in artifact_links:
        manifest["l2_output_repo_relative"] = artifact_links["l2_output.json"]
    if "l6_shadow_eval_package.json" in artifact_links:
        manifest["l6_shadow_eval_package_repo_relative"] = artifact_links["l6_shadow_eval_package.json"]
    _write_json(artifact_dir / "run_manifest.json", manifest)

    pointer: dict[str, Any] = {
        "run_id": run_id,
        "run_dir": run_dir_rel,
        "generated_at_utc": generated_at_utc,  # guardian: allow-return-none-swallow -- P2 burndown: fail-soft optional boundary
        "provider_requested": provider_requested,
        "provider_attempted": provider_attempted,
        "runtime_generation_status": runtime_generation_status,
        "runtime_proof_placement_bucket": bucket,
        "command": cmd,
        "section_id": section_id,
        "run_dir_repo_relative": run_dir_rel,
        "artifact_links": artifact_links,
    }
    if "l2_output.json" in artifact_links:
        pointer["l2_output_repo_relative"] = artifact_links["l2_output.json"]  # guardian: allow-return-none-swallow -- P2 burndown: fail-soft optional boundary
    if "l6_shadow_eval_package.json" in artifact_links:
        pointer["l6_shadow_eval_package_repo_relative"] = artifact_links["l6_shadow_eval_package.json"]
    ptr_name = (
        "latest_real_run.json"
        if bucket == "real"
        else ("latest_mock_run.json" if bucket == "mock" else LATEST_PLUMBING_RUN_FILENAME)
    )
    msr = modular_sections_root_from_env(repo)
    if msr is not None:
        require_manifest_for_modular_sections_root(msr, env_name=MODULAR_R4_SECTIONS_ROOT_ENV)
    ptr_root = (msr / lane) if msr is not None else lane_root(repo, lane)
    _write_json(ptr_root / ptr_name, pointer)
    if _should_write_latest_successful_real(
        bucket,
        provider_requested,
        runtime_generation_status,
        artifact_dir,
    ):
        _write_json(ptr_root / LATEST_SUCCESSFUL_REAL_FILENAME, pointer)

    emit_lane_runtime_proof_bundle_index(
        repo,
        lane,
        artifact_dir,
        run_id=run_id,
        proof_contract_strict=bundle_proof_strict,
        document_metadata=run_bundle_index_document_metadata,
    )

    if os.environ.get("APPS_RG_WHOLE_RUN_ENVELOPE", "").strip() in ("1", "true", "yes"):
        from apps_rg.runtime.integrated_lane_evidence_packaging import (
            maybe_finalize_lane_evidence_package,
        )

        cid = os.environ.get("APPS_RG_CORRELATED_CLI_RUN", "").strip() or None
        maybe_finalize_lane_evidence_package(
            repo,
            artifact_dir,
            section_id=section_id,
            run_id=run_id,
            correlation_id=cid,
        )


def load_latest_pointer(repo: Path, lane: str, bucket: Bucket) -> dict[str, Any] | None:
    ptr = lane_root(repo, lane) / ("latest_real_run.json" if bucket == "real" else "latest_mock_run.json")
    if not ptr.is_file():
        return None
    try:
        data = json.loads(ptr.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):  # guardian: allow-return-none-swallow -- P2 burndown: fail-soft optional boundary
        return None
    return data if isinstance(data, dict) else None


def load_latest_successful_real_pointer(repo: Path, lane: str) -> dict[str, Any] | None:
    ptr = lane_root(repo, lane) / LATEST_SUCCESSFUL_REAL_FILENAME
    if not ptr.is_file():
        return None
    try:
        data = json.loads(ptr.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):  # guardian: allow-return-none-swallow -- P2 burndown: fail-soft optional boundary
        return None
    return data if isinstance(data, dict) else None


def resolve_run_dir_from_latest_successful_pointer(repo: Path, lane: str) -> Path | None:
    data = load_latest_successful_real_pointer(repo, lane)
    if not data:
        return None
    rel = data.get("run_dir")
    if not isinstance(rel, str):
        return None
    p = (repo / rel).resolve()
    if not p.is_dir():
        return None
    return p if _is_accepted_real_llm_qwen_bundle(p) else None


def _migration_latest_real_llm_qwen_run_dir(repo: Path, lane: str) -> Path | None:
    """When successful pointer is absent or stale, pick newest eligible real-bucket run."""
    root = lane_root(repo, lane) / "real"
    if not root.is_dir():
        return None
    best_mtime: float = -1.0
    best_rd: Path | None = None
    for child in sorted(root.iterdir()):
        if not child.is_dir():
            continue
        l2p = child / "l2_output.json"
        if not l2p.is_file():
            continue
        if not _is_accepted_real_llm_qwen_bundle(child):
            continue
        mtime = l2p.stat().st_mtime
        if mtime > best_mtime:
            best_mtime = mtime
            best_rd = child
    return best_rd

  # guardian: allow-return-none-swallow -- P2 burndown: fail-soft optional boundary
def resolve_accepted_real_rollup_run_dir(repo: Path, lane: str) -> tuple[Path | None, str]:
    """Accepted REAL_LLM qwen_vllm evidence — never follows latest_real_run.json alone.

    Returns (run_directory_or_none, resolution_tag).
    """
    from apps_rg.runtime.product_output_policy import product_fail_closed_runtime

    rd = resolve_run_dir_from_latest_successful_pointer(repo, lane)
    if rd:
        return rd, "latest_successful_real_run.json"

    if product_fail_closed_runtime():
        return None, "missing_successful_real_run_product_fail_closed"

    rd = _migration_latest_real_llm_qwen_run_dir(repo, lane)
    if rd:
        return rd, "migration_real_llm_qwen_vllm_scan"

    legacy_root = lane_root(repo, lane)
    leg_l2 = legacy_root / "l2_output.json"
    if leg_l2.is_file() and _is_accepted_real_llm_qwen_bundle(legacy_root):
        return legacy_root, "legacy_flat_real_llm_qwen_vllm"

    return None, "missing_successful_real_run"


def resolve_run_dir_from_pointer(repo: Path, lane: str, bucket: Bucket) -> Path | None:
    data = load_latest_pointer(repo, lane, bucket)
    if not data:
        return None
    rel = data.get("run_dir")
    if not isinstance(rel, str):
        return None
    p = repo / rel
    return p if p.is_dir() else None


def resolve_latest_real_l2(repo: Path, lane: str) -> Path | None:
    """L2 path for accepted REAL_LLM qwen_vllm evidence (same resolution as real rollup)."""
    rd, _ = resolve_accepted_real_rollup_run_dir(repo, lane)
    if rd and (rd / "l2_output.json").is_file():
        return rd / "l2_output.json"
    return None


def resolve_latest_mock_run_dir(repo: Path, lane: str) -> Path | None:
    return resolve_run_dir_from_pointer(repo, lane, "mock")


def resolve_rollup_run_dir(
    repo: Path,
    lane: str,
    *,
    artifact_mode: Literal["real", "mock", "all"],
) -> Path | None:
    """Rollup default: latest real run only. mock mode uses latest mock."""
    if artifact_mode == "mock":
        rd = resolve_run_dir_from_pointer(repo, lane, "mock")
        if rd:
            return rd
        legacy = lane_root(repo, lane) / "l2_output.json"
        if legacy.is_file():
            try:
                l2 = json.loads(legacy.read_text(encoding="utf-8"))
                if l2.get("runtime_generation_status") == "MOCKED":
                    return lane_root(repo, lane)
            except (json.JSONDecodeError, OSError):  # guardian: allow-return-none-swallow -- P2 burndown: fail-soft optional boundary
                return None
        return None
    if artifact_mode == "real":
        rd, tag = resolve_accepted_real_rollup_run_dir(repo, lane)
        if rd is None or tag == "missing_successful_real_run":
            return None
        return rd
    # "all" — align with accepted real evidence (avoid latest_real_attempt alone)
    rd, tag = resolve_accepted_real_rollup_run_dir(repo, lane)
    if rd is not None and tag != "missing_successful_real_run":
        return rd
    return None
