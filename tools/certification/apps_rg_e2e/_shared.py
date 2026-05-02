"""Shared helpers for the apps_rg e2e proof harness.

Kept deliberately small — one file, pure functions, no side effects beyond
disk reads and SHA256 computation. Both emitters import from here.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROOF_SCHEMA_VERSION = "apps_rg_e2e_proof/2026-05-01/v1"
APP_NAME = "apps_rg"
ENTRYPOINT_COMMAND = "python -m apps_rg"

REPO_ROOT = Path(__file__).resolve().parents[3]
CERT_DIR = REPO_ROOT / "artifacts" / "certification" / "apps_rg_e2e"
RUNS_ROOT = REPO_ROOT / "artifacts" / "apps_rg" / "runs"
ADG_DIR = REPO_ROOT / "artifacts" / "adg"


def utc_now_iso() -> str:
    """ISO-8601 UTC timestamp with trailing Z."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str | None:
    """Compute SHA256 of a file; return None if the file does not exist.

    Reads in 64 KiB chunks so we do not load large DOCX/JSON artifacts
    into memory all at once.
    """
    if not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_head() -> tuple[str, bool]:
    """Return (short_sha, dirty_bool) for the current working tree.

    Graceful fallback to ('UNKNOWN', False) when git is unavailable — the
    harness must never crash because of environment issues (the point is
    to honestly capture what it sees).
    """
    try:
        sha = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=10, shell=False, check=True,
            cwd=str(REPO_ROOT),
        ).stdout.strip()
    except (subprocess.SubprocessError, FileNotFoundError, OSError):
        return ("UNKNOWN", False)
    try:
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, timeout=10, shell=False, check=True,
            cwd=str(REPO_ROOT),
        ).stdout
    except (subprocess.SubprocessError, FileNotFoundError, OSError):
        return (sha, False)
    return (sha, bool(status.strip()))


def latest_run_dir() -> Path | None:
    if not RUNS_ROOT.exists():
        return None
    runs = sorted(
        (p for p in RUNS_ROOT.iterdir() if p.is_dir() and p.name[:8].isdigit()),
        key=lambda p: p.name,
        reverse=True,
    )
    return runs[0] if runs else None


def latest_adg_snapshot() -> Path | None:
    if not ADG_DIR.exists():
        return None
    snaps = sorted(ADG_DIR.glob("adg_indexed_*.sqlite"), key=lambda p: p.stat().st_mtime, reverse=True)
    return snaps[0] if snaps else None


def relative_to_repo(path: Path | None) -> str | None:
    if path is None:
        return None
    try:
        return str(path.resolve().relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def write_json(path: Path, payload: dict[str, Any]) -> tuple[str, int]:
    """Write JSON deterministically and return (sha256, byte_length)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False).encode("utf-8")
    path.write_bytes(data)
    return (sha256_bytes(data), len(data))


def detect_mock_or_fixture_mode() -> tuple[bool, bool]:
    """Best-effort detection of mock/fixture flags in the environment.

    mock_mode_detected is True when any APPS_RG_* mock flag is set. Fixture
    mode is True when apps_rg is pointed at the test fixtures directory.
    """
    env = os.environ
    mock_keys = ("APPS_RG_MOCK", "APPS_RG_MOCK_MODE", "APPS_RG_USE_MOCKS", "NARRATIVE_MOCK")
    mock = any(env.get(k) for k in mock_keys)
    fixture_keys = ("APPS_RG_FIXTURE_MODE", "APPS_RG_FIXTURE_DIR")
    fixture = any(env.get(k) for k in fixture_keys)
    return (mock, fixture)


def spine_signal_scan(src: str) -> dict[str, bool]:
    """Scan a source file for runtime-spine wiring signals.

    Two acceptable wiring patterns:

    (a) **Direct contract use** — file imports/mentions canonical contract
        types (RouteContract, L1PlanContract, ExitReviewPacket, etc.).
    (b) **Adapter-based wiring** — file imports the apps_rg spine
        adapter (``governed_run`` from ``apps_rg.runtime``) which emits
        the contracts under the hood.

    Either is sufficient. The blocking-gap test
    ``apps_rg_main_does_not_import_any_runtime_spine_contract`` clears
    when ANY of these signals fires.

    Used by BOTH emit_proof_bundle (to build blocking_gaps) AND the
    verifier test (to validate that blocking_gaps were computed honestly).
    """
    return {
        # Direct contract references
        "RouteContract":        "RouteContract" in src,
        "L1PlanContract":       "L1PlanContract" in src,
        "L3StepContract":       "L3StepContract" in src,
        "ExitReviewPacket":     "ExitReviewPacket" in src,
        "RuntimeExhaustBundle": "RuntimeExhaustBundle" in src,
        "SovereignBaseAgent":   "SovereignBaseAgent" in src,
        "agentic_core.L0_routing": "from agentic_core.L0_routing" in src,
        "agentic_core.L3_orchestration": "from agentic_core.L3_orchestration" in src,
        # Adapter-based wiring (apps_rg's chosen integration path)
        "governed_run_adapter": "from apps_rg.runtime" in src and "governed_run" in src,
    }
