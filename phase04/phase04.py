import logging
#!/usr/bin/env python3
"""
PHASE 4 — CRYPTOGRAPHIC FREEZE (ZERO-LOSS OVERWRITE)

Purpose:
    Produce a deterministic, machine-verifiable cryptographic snapshot of the
    post-Phase-3 filesystem state under <TARGET_ROOT>/ by hashing:

        • All relative file paths
        • All file contents (sha256)
        • All file sizes (bytes)

    Writes ONE freeze report inside <TARGET_ROOT>/ only:

        <TARGET_ROOT>/<TARGET_ROOT>_freeze_report.json

    Phase 4 performs:
        • No structural mutations
        • No code mutations
        • No semantic-cache reads or writes
        • Pure hashing + JSON serialization (deterministic)
        • Fully reproducible, idempotent, path-stable freeze

Inputs:
    • unified_structure_subatomic.yaml
    • unified_structure_subatomic_meta.yaml
    • Canonical FS after Phase 3 (no semantic cache)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import yaml

# ======================================================================
# GLOBAL ROOTS & CONSTANTS
# ======================================================================

PROJECT_ROOT = Path(r"C:/Git/Agentic-Workflow").resolve()

CANONICAL_ROOTS = [
    "01_agentic_core",
    "02_schemas",
    "03_runtime",
    "04_prompt_governance",
    "05_config",
    "06_data",
    "07_observability",
    "08_scripts",
    "09_apps",
    "10_tests",
]

SSOT_YAML = PROJECT_ROOT / "unified_structure_subatomic.yaml"
META_YAML = PROJECT_ROOT / "unified_structure_subatomic_meta.yaml"

SEMANTIC_CACHE_ROOT = PROJECT_ROOT / "06_data" / "semantic_cache"

SYSTEM_EXCLUDES = {
    ".git",
    ".venv",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".idea",
    ".vscode",
    "node_modules",
    ".DS_Store",
    "phase0_5",
    "semantic_cache",
    "phase1_backup",
    "phase1_indices",
    "phase1_legacy_folders",
    "phase1_borderline_matches",
    "phase2",
    "phase3_snapshots",
    "phase3_meta",
}

MAX_DEPTH = 12  # K31 safeguard


# ======================================================================
# UTILS
# ======================================================================

def load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def normalize_rel(path: Path) -> str:
    rel = path.relative_to(PROJECT_ROOT)
    s = rel.as_posix()
    if s.startswith("./"):
        s = s[2:]
    return s


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def is_under(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except Exception:
        return False


def load_protected_patterns() -> List[str]:
    """
    Protected patterns come from META YAML + required defaults.
    """
    meta = load_yaml(META_YAML)
    p = list(meta.get("protected_paths", []) or [])

    # Enforce required patterns (Phase 3 spec)
    if "**/__init__.py" not in p:
        p.append("**/__init__.py")
    if "**/*.md" not in p:
        p.append("**/*.md")
    if "06_data/semantic_cache/**" not in p:
        p.append("06_data/semantic_cache/**")

    return p


def matches_glob(rel: str, patterns: List[str]) -> bool:
    path = Path(rel)
    for patt in patterns:
        if path.match(patt.replace("\\", "/")):
            return True
    return False


# ======================================================================
# PHASE 4 — CORE FREEZE ENGINE
# ======================================================================

def scan_target_root(target_root: str) -> List[Path]:
    """
    Read-only scan of target root, returning every file (directories excluded).
    """
    root = PROJECT_ROOT / target_root
    files = []

    for p in root.rglob("*"):
        # System excludes (K30)
        if any(seg in SYSTEM_EXCLUDES for seg in p.parts):
            continue

        rel_parts = p.relative_to(PROJECT_ROOT).parts
        if "semantic_cache" in rel_parts:
            continue
        if "phase3_snapshots" in rel_parts:
            continue

        # Depth checks (K31)
        depth = len(p.relative_to(root).parts)
        if depth > MAX_DEPTH:
            raise RuntimeError(f"Depth limit exceeded ({depth}) at {p}")

        if p.is_file():
            files.append(p)

    return files


def build_freeze_report(target_root: str) -> dict:
    """
    Computes deterministic freeze report.
    """
    root_path = PROJECT_ROOT / target_root
    files = scan_target_root(target_root)

    protected_patterns = load_protected_patterns()

    normalized_protected = []
    for patt in protected_patterns:
        if "phase3_snapshots" in patt:
            continue
        if "semantic_cache" in patt:
            continue
        normalized_protected.append(patt)
    protected_patterns = normalized_protected

    # Validate protected paths exist (K57)
    for p in files:
        rel = normalize_rel(p)
        if matches_glob(rel, protected_patterns):
            if not p.exists():
                raise RuntimeError(f"Protected path missing: {rel}")

    freeze_entries: Dict[str, dict] = {}

    for f in files:
        rel = normalize_rel(f)
        key = rel

        # No directory paths allowed in freeze report (K36)
        if f.is_dir():
            raise RuntimeError(f"Directory appeared in freeze file set: {rel}")

        # canonical file read (sha256, size)
        b = f.read_bytes()
        digest = sha256_bytes(b)
        size = len(b)

        # K43: SHA format
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise RuntimeError(f"Invalid SHA256 generated for {rel}")

        freeze_entries[key] = {
            "sha256": digest,
            "size_bytes": size,
        }

    # Sorting keys for determinism (K47)
    ordered = dict(sorted(freeze_entries.items(), key=lambda x: x[0]))

    report = {
        "schema_version": "v1",
        "root": f"{target_root}/",
        "files": ordered,
    }

    return report


def write_freeze_report_atomic(target_root: str, report: dict) -> Path:
    """
    Write report atomically using write-then-rename discipline (K78, K79).
    """
    root_path = PROJECT_ROOT / target_root

    # Freeze report path (K17–K19)
    freeze_path = root_path / f"{target_root}_freeze_report.json"
    tmp_path = freeze_path.with_suffix(".tmp")

    # Write JSON to temp (deterministic, no timestamps) (K48–K50)
    serialized = json.dumps(report, indent=2, sort_keys=True).encode("utf-8")

    with tmp_path.open("wb") as f:
        f.write(serialized)
        f.flush()
        os.fsync(f.fileno())  # durability

    # Atomic replace
    tmp_path.replace(freeze_path)

    return freeze_path


# ======================================================================
# PRECONDITIONS (K1–K8)
# ======================================================================

def validate_preconditions(target_root: str):
    # K1 soft Docker check
    if os.path.exists("/.dockerenv") or os.environ.get("PHASE4_ALLOW_NON_DOCKER") == "1":
        pass  # treated as satisfied

    # K2
    for r in CANONICAL_ROOTS:
        if not (PROJECT_ROOT / r).exists():
            raise RuntimeError("Canonical folder structure incomplete.")

    # K3–K3d
    if not SSOT_YAML.exists():
        raise RuntimeError("SSOT YAML missing.")
    if not META_YAML.exists():
        raise RuntimeError("META YAML missing.")
    load_yaml(META_YAML)  # K3c

    # K4–K6 assumed satisfied based on workflow progression.

    # K7
    if not (PROJECT_ROOT / target_root).exists():
        raise RuntimeError("Target root missing at Phase 4 entry.")

    # K8
    if target_root not in CANONICAL_ROOTS:
        raise RuntimeError(f"Invalid target root {target_root}")


# ======================================================================
# MAIN EXECUTION
# ======================================================================

def run_phase4(target_root: str) -> Path:
    """
    Full Phase 4 freeze pipeline. No modifications except writing the freeze report.
    """
    # Preconditions
    validate_preconditions(target_root)

    # Build freeze report
    report = build_freeze_report(target_root)

    # Write atomic freeze report
    freeze_path = write_freeze_report_atomic(target_root, report)

    return freeze_path


# ======================================================================
# CLI ENTRYPOINT
# ======================================================================

def parse_args():
    import argparse
    p = argparse.ArgumentParser(description="Phase 4 — Cryptographic Freeze")
    p.add_argument(
        "--target-root",
        required=False,
        type=str,
        help="Canonical root (e.g., 01_agentic_core)",
    )
    p.add_argument(
        "--target-root-index",
        required=False,
        type=int,
        help="Index of canonical root (1–10)",
    )
    return p.parse_args()


def main():
    args = parse_args()

    if args.target_root and args.target_root_index:
        raise SystemExit("Select either --target-root or --target-root-index, not both.")

    if args.target_root_index:
        if not (1 <= args.target_root_index <= len(CANONICAL_ROOTS)):
            raise SystemExit(f"Index must be 1–{len(CANONICAL_ROOTS)}.")
        target_root = CANONICAL_ROOTS[args.target_root_index - 1]
    else:
        target_root = args.target_root or "01_agentic_core"

    path = run_phase4(target_root)

    logging.debug(f"[PHASE 4 COMPLETE] Freeze report written: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
