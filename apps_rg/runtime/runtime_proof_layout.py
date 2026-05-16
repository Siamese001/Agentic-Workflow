"""Run-scoped runtime proof directories (Option B: real/<run_id>/, mock/<run_id>/).

Lane root: artifacts/apps_rg/runtime_proofs/<lane>/
Pointers: latest_real_run.json (latest real-bucket attempt), latest_successful_real_run.json
(accepted REAL_LLM qwen_vllm evidence for rollup), latest_mock_run.json.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

Bucket = Literal["real", "mock"]

LATEST_SUCCESSFUL_REAL_FILENAME = "latest_successful_real_run.json"

# When set (absolute or repo-relative), lane prepare/finalize and optional dependency
# resolution use ``<root>/<lane>/{mock|real}/<run_id>/`` instead of runtime_proofs.
MODULAR_R4_SECTIONS_ROOT_ENV = "APPS_RG_MODULAR_R4_SECTIONS_ROOT"


def modular_sections_root_from_env(repo: Path) -> Path | None:
    raw = os.environ.get(MODULAR_R4_SECTIONS_ROOT_ENV, "").strip()
    if not raw:
        return None
    cand = Path(raw).expanduser()
    if not cand.is_absolute():
        cand = (repo / cand).resolve()
    return cand.resolve()


def resolve_modular_latest_l2(repo: Path, lane: str) -> Path | None:
    """Path to ``l2_output.json`` from modular R4 section pointers (Phase 1+), if env is set."""
    msr = modular_sections_root_from_env(repo)
    if msr is None:
        return None
    lane_base = msr / lane
    for ptr_name in (
        "latest_mock_run.json",
        "latest_real_run.json",
        LATEST_SUCCESSFUL_REAL_FILENAME,
    ):
        data = _read_json_dict(lane_base / ptr_name)
        if not data:
            continue
        rel = data.get("run_dir")
        if not isinstance(rel, str):
            continue
        rd = (repo / rel).resolve()
        l2 = rd / "l2_output.json"
        if l2.is_file():
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


def lane_root(repo: Path, lane: str) -> Path:
    return repo / "artifacts" / "apps_rg" / "runtime_proofs" / lane


def proof_bucket_for_provider(provider: str) -> Bucket:
    return "mock" if provider == "mock" else "real"


def run_dir(repo: Path, lane: str, bucket: Bucket, run_id: str) -> Path:
    return lane_root(repo, lane) / bucket / run_id


def rel_posix(path: Path, repo: Path) -> str:
    return path.relative_to(repo).as_posix()


def prepare_runtime_proof_run_dir(repo: Path, lane: str, provider: str, run_id: str) -> Path:
    bucket = proof_bucket_for_provider(provider)
    msr = modular_sections_root_from_env(repo)
    if msr is not None:
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
    except (json.JSONDecodeError, OSError):
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
) -> None:
    """Write run_manifest.json and latest_{real|mock}_run.json under lane root."""
    bucket = proof_bucket_for_provider(provider)
    generated_at_utc = datetime.now(timezone.utc).isoformat()
    cmd = command if command is not None else " ".join(sys.argv)
    manifest: dict[str, Any] = {
        "run_id": run_id,
        "generated_at_utc": generated_at_utc,
        "provider_requested": provider_requested,
        "provider_attempted": provider_attempted,
        "runtime_generation_status": runtime_generation_status,
        "command": cmd,
        "section_id": section_id,
    }
    _write_json(artifact_dir / "run_manifest.json", manifest)
    run_dir_rel = rel_posix(artifact_dir, repo)
    pointer: dict[str, Any] = {
        "run_id": run_id,
        "run_dir": run_dir_rel,
        "generated_at_utc": generated_at_utc,
        "provider_requested": provider_requested,
        "provider_attempted": provider_attempted,
        "runtime_generation_status": runtime_generation_status,
        "command": cmd,
        "section_id": section_id,
    }
    ptr_name = "latest_real_run.json" if bucket == "real" else "latest_mock_run.json"
    msr = modular_sections_root_from_env(repo)
    ptr_root = (msr / lane) if msr is not None else lane_root(repo, lane)
    _write_json(ptr_root / ptr_name, pointer)
    if _should_write_latest_successful_real(
        bucket,
        provider_requested,
        runtime_generation_status,
        artifact_dir,
    ):
        _write_json(ptr_root / LATEST_SUCCESSFUL_REAL_FILENAME, pointer)


def load_latest_pointer(repo: Path, lane: str, bucket: Bucket) -> dict[str, Any] | None:
    ptr = lane_root(repo, lane) / ("latest_real_run.json" if bucket == "real" else "latest_mock_run.json")
    if not ptr.is_file():
        return None
    try:
        data = json.loads(ptr.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    return data if isinstance(data, dict) else None


def load_latest_successful_real_pointer(repo: Path, lane: str) -> dict[str, Any] | None:
    ptr = lane_root(repo, lane) / LATEST_SUCCESSFUL_REAL_FILENAME
    if not ptr.is_file():
        return None
    try:
        data = json.loads(ptr.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
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


def resolve_accepted_real_rollup_run_dir(repo: Path, lane: str) -> tuple[Path | None, str]:
    """Accepted REAL_LLM qwen_vllm evidence — never follows latest_real_run.json alone.

    Returns (run_directory_or_none, resolution_tag).
    """
    rd = resolve_run_dir_from_latest_successful_pointer(repo, lane)
    if rd:
        return rd, "latest_successful_real_run.json"

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
            except (json.JSONDecodeError, OSError):
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
