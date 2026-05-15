"""Run-scoped runtime proof directories (Option B: real/<run_id>/, mock/<run_id>/).

Lane root: artifacts/apps_rg/runtime_proofs/<lane>/
Pointers: latest_real_run.json, latest_mock_run.json (relative run_dir + metadata).
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

Bucket = Literal["real", "mock"]


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
    rd = run_dir(repo, lane, bucket, run_id)
    rd.mkdir(parents=True, exist_ok=True)
    return rd


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


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
    _write_json(lane_root(repo, lane) / ptr_name, pointer)


def load_latest_pointer(repo: Path, lane: str, bucket: Bucket) -> dict[str, Any] | None:
    ptr = lane_root(repo, lane) / ("latest_real_run.json" if bucket == "real" else "latest_mock_run.json")
    if not ptr.is_file():
        return None
    try:
        data = json.loads(ptr.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    return data if isinstance(data, dict) else None


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
    """L2 path for latest successful real-bucket pointer, or legacy flat l2_output.json."""
    rd = resolve_run_dir_from_pointer(repo, lane, "real")
    if rd and (rd / "l2_output.json").is_file():
        return rd / "l2_output.json"
    legacy = lane_root(repo, lane) / "l2_output.json"
    if legacy.is_file():
        return legacy
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
        rd = resolve_run_dir_from_pointer(repo, lane, "real")
        if rd:
            return rd
        # Migration: flat lane dir if it looks like a real artifact (not mock-only)
        legacy = lane_root(repo, lane) / "l2_output.json"
        if legacy.is_file():
            try:
                l2 = json.loads(legacy.read_text(encoding="utf-8"))
                if l2.get("runtime_generation_status") == "REAL_LLM":
                    return lane_root(repo, lane)
            except (json.JSONDecodeError, OSError):
                return lane_root(repo, lane)
        return None
    # "all" — not used for per-lane collect; rollup uses real only by contract
    return resolve_run_dir_from_pointer(repo, lane, "real")
