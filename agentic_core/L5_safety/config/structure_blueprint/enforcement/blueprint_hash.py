"""
Blueprint Hash — Layer 5: SHA-256 integrity hash over blueprint .py files.

Computes a deterministic hash of all .py files in the structure_blueprint package.
Detects unauthorized modifications between CI runs per AD-4.

Usage:
    --update-blueprint-hash   Recompute and write hash (local-only, forbidden in CI).
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from agentic_core.L5_safety.config.structure_blueprint.enforcement.types import (
    EnforcementResult,
    Violation,
    make_result,
)

HASH_FILE = "blueprint_integrity.sha256"


def compute_hash(blueprint_dir: Path) -> str:
    """Compute SHA-256 over all .py files in the blueprint package (sorted, deterministic)."""
    h = hashlib.sha256()

    py_files: list[Path] = sorted(p for p in blueprint_dir.rglob("*.py") if "__pycache__" not in str(p))

    for py_file in py_files:
        rel = py_file.relative_to(blueprint_dir).as_posix()
        h.update(rel.encode("utf-8"))
        try:
            h.update(py_file.read_bytes())
        except OSError:
            h.update(b"<unreadable>")

    return h.hexdigest()


def check(
    blueprint_dir: Path,
    update: bool = False,
) -> EnforcementResult:
    """Check blueprint integrity hash. If update=True, rewrite the hash file."""
    violations: list[Violation] = []
    stats = {
        "files_hashed": 0,
        "hash_match": False,
        "updated": False,
    }

    current_hash = compute_hash(blueprint_dir)
    stats["files_hashed"] = len(list(blueprint_dir.rglob("*.py")))

    hash_path = blueprint_dir / HASH_FILE

    if update:
        hash_path.write_text(current_hash + "\n", encoding="utf-8")
        stats["updated"] = True
        stats["hash_match"] = True
        return make_result("blueprint_hash", violations, stats)

    if not hash_path.exists():
        violations.append(
            Violation(
                type="missing_hash_file",
                path=str(hash_path.relative_to(blueprint_dir.parent.parent.parent.parent)),
                severity="warning",
                detail=(
                    f"Blueprint hash file '{HASH_FILE}' not found. "
                    "Run with --update-blueprint-hash to initialize."
                ),
            ),
        )
        return make_result("blueprint_hash", violations, stats)

    stored_hash = hash_path.read_text(encoding="utf-8").strip()

    if stored_hash == current_hash:
        stats["hash_match"] = True
    else:
        violations.append(
            Violation(
                type="hash_mismatch",
                path=str(hash_path.relative_to(blueprint_dir.parent.parent.parent.parent)),
                severity="error",
                detail=(
                    f"Blueprint hash mismatch: stored={stored_hash[:16]}... "
                    f"current={current_hash[:16]}... — unauthorized modification detected"
                ),
            ),
        )

    return make_result("blueprint_hash", violations, stats)
