"""W2 — Shared utilities for the integrated-runtime verifier scripts.

Each verifier script imports from this module to keep their own logic
small. SSOT for the artifact dir resolution, envelope-shape probing,
and the harness-stamp regex.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LATEST = REPO_ROOT / "artifacts" / "certification" / "integrated_runtime" / "latest"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agentic_core.runtime.artifacts.integrated_runtime_emitter import (  # noqa: E402
    W2_ALL_ARTIFACT_FILENAMES,
    W2_ARTIFACT_FILENAMES,
    W2_CHAIN_LINKAGE,
    W2_MW_ARTIFACT_FILENAMES,
    W2_MW_CHAIN_LINKAGE,
    is_harness_stamp,
)


# ─────────────────────────────────────────────────────────────────────
# Result + exit codes
# ─────────────────────────────────────────────────────────────────────


# Exit code conventions:
#   0 = PASS
#   2 = FAIL_CLOSED (verifier-detected violation)
#   3 = HARNESS_ERROR (unexpected exception)
EXIT_PASS = 0
EXIT_FAIL_CLOSED = 2
EXIT_HARNESS_ERROR = 3


def resolve_artifact_dir(arg: str | None = None) -> Path:
    """Resolve which artifact dir to inspect (CLI arg > env var > latest/)."""
    import os as _os
    if arg:
        return Path(arg).resolve()
    env = _os.environ.get("W2_ARTIFACT_DIR")
    if env:
        return Path(env).resolve()
    return DEFAULT_LATEST


def load_envelope(artifact_dir: Path, filename: str) -> dict[str, Any]:
    """Load and return one artifact envelope. Raises FileNotFoundError."""
    p = artifact_dir / filename
    if not p.exists():
        raise FileNotFoundError(f"missing artifact: {filename!r} in {artifact_dir}")
    return json.loads(p.read_text(encoding="utf-8"))


def load_payload(artifact_dir: Path, filename: str) -> dict[str, Any]:
    """Load just the .payload of an artifact envelope."""
    env = load_envelope(artifact_dir, filename)
    if not isinstance(env, dict) or "payload" not in env:
        raise ValueError(f"{filename}: not a valid W2 artifact envelope")
    return env["payload"]


def fail(reason_code: str, detail: str = "") -> int:
    print(f"FAIL_CLOSED: {reason_code}" + (f" — {detail}" if detail else ""))
    return EXIT_FAIL_CLOSED


def passed(message: str) -> int:
    print(f"PASS: {message}")
    return EXIT_PASS


def detect_chain_kind(artifact_dir: Path) -> str:
    """Return the chain_kind from the manifest.

    Recognized values: ``R1B`` (default), ``MANAGED_WORKFLOW``,
    ``R1A_EXACT_CACHE``, ``R5_FALLBACK``, ``UWG_BLOCK_PATH``. The last
    three reuse the R1B chain shape (same artifact set, possibly with
    a small additive extension); the chain_kind tag distinguishes them
    so verifiers can apply family-specific invariants.
    """
    try:
        env = load_envelope(artifact_dir, "integrated_runtime_artifact_manifest.json")
    except FileNotFoundError:
        return "R1B"
    payload = env.get("payload", {}) if isinstance(env, dict) else {}
    kind = payload.get("chain_kind") if isinstance(payload, dict) else None
    if kind in (
        "MANAGED_WORKFLOW",
        "R1A_EXACT_CACHE",
        "R5_FALLBACK",
        "UWG_BLOCK_PATH",
        # W4 plan fortknox-100pct-static-runtime-gap-9a3d4f:
        "UWG_COMMIT_PATH",
        "R3_GROUNDED_READ",
        "R4_SINGLE_ACTION",
        "MANAGED_WORKFLOW_REAL_EXECUTION",
    ):
        return kind
    return "R1B"


def chain_filenames_for(kind: str) -> tuple[str, ...]:
    """Chain artifact-filenames tuple for the given chain_kind.

    R1A / R5 / UWG_BLOCK reuse the R1B chain shape. UWG_BLOCK adds two
    extra integrated artifacts (commit_request, uwg_blocked_commit_receipt)
    handled separately by the family-specific verifier — not by this
    common loader.
    """
    if kind == "MANAGED_WORKFLOW":
        return W2_MW_ARTIFACT_FILENAMES
    return W2_ARTIFACT_FILENAMES


def chain_linkage_for(kind: str) -> tuple[tuple[str, str | None], ...]:
    """Chain linkage tuples for the given chain_kind."""
    if kind == "MANAGED_WORKFLOW":
        return W2_MW_CHAIN_LINKAGE
    return W2_CHAIN_LINKAGE


__all__ = [
    "DEFAULT_LATEST",
    "EXIT_FAIL_CLOSED",
    "EXIT_HARNESS_ERROR",
    "EXIT_PASS",
    "REPO_ROOT",
    "W2_ALL_ARTIFACT_FILENAMES",
    "W2_ARTIFACT_FILENAMES",
    "W2_CHAIN_LINKAGE",
    "W2_MW_ARTIFACT_FILENAMES",
    "W2_MW_CHAIN_LINKAGE",
    "chain_filenames_for",
    "chain_linkage_for",
    "detect_chain_kind",
    "fail",
    "is_harness_stamp",
    "load_envelope",
    "load_payload",
    "passed",
    "resolve_artifact_dir",
]
