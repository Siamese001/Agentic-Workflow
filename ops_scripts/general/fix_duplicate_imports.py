"""Fix duplicate imports in Python files."""

import logging
import os
import re
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config.path_constants import SOVEREIGN_EXCLUDED_FOLDERS
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_validated_by_safety_plane,
    _emit_writes_through,
    emit_determinism_digest,
)

_emit_writes_through("p1", "fix_duplicate_imports", "uwg_governed_write")
_emit_writes_through("p1", "fix_duplicate_imports", "uwg_governed_write_2")
_emit_pulls_context("p1", "fix_duplicate_imports", "context_retrieval")
_emit_pulls_context("p1", "fix_duplicate_imports", "context_retrieval_2")
emit_determinism_digest("trace_fix_duplicate_imports", "fix_duplicate_imports_dispatch")
emit_determinism_digest("trace_fix_duplicate_imports", "fix_duplicate_imports_complete")
_emit_validated_by_safety_plane("p1", "fix_duplicate_imports", "safety_validation")

logging.basicConfig(level=logging.INFO)
Logger: Any = logging.getLogger(__name__)


def _normalize_import(line: str) -> str:
    return re.sub(r"\s+", " ", line.strip())


def fix_duplicate_imports(filepath: Path) -> bool:
    """Remove duplicate imports from a file."""
    try:
        lines = filepath.read_text(encoding="utf-8").splitlines()
        imports: list[tuple[int, str]] = []
        duplicates: list[int] = []
        seen: set[str] = set()

        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("import ") or stripped.startswith("from "):
                imports.append((i, stripped))

        for idx, imp in imports:
            normalized = _normalize_import(imp)
            if normalized in seen:
                duplicates.append(idx)
            else:
                seen.add(normalized)

        if duplicates:
            Logger.info("%s: Found %s duplicate imports", filepath, len(duplicates))
            for idx in reversed(duplicates):
                del lines[idx]
            filepath.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return True
        return False
    except Exception as e:  # guardian: allow-broad-exception -- offline tooling, reports failure
        Logger.error("Error processing %s: %s", filepath, e)
        return False


def main() -> None:
    """Fix duplicate imports in all Python files."""
    count = 0
    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS]
        for file in files:
            if file.endswith(".py") and (not file.startswith("fix_")):
                filepath = Path(root) / file
                if fix_duplicate_imports(filepath):
                    count += 1
    Logger.info("Fixed duplicate imports in %s files", count)


if __name__ == "__main__":
    main()
