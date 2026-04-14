#!/usr/bin/env python3
"""
Git Corruption Detection Script
Scans Python files for syntax errors and potential corruption patterns.
"""

import ast
import re
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    DISCOVERY_EXCLUDED_TERRITORIES,
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)
from tqdm import tqdm


def detect_corrupted_files(project_root: Path) -> list[tuple[Path, int, str]]:
    """Scan all Python files for syntax errors."""
    corrupted = []
    exclude_patterns = list(
        GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES
    )

    for py_file in tqdm(sorted(project_root.rglob("*.py")), desc="Processing", unit="item"):
        if any(pattern in str(py_file) for pattern in exclude_patterns):
            continue
        try:
            content = py_file.read_text(encoding="utf-8")
            ast.parse(content)
        except SyntaxError as exc:
            corrupted.append((py_file, exc.lineno or 0, str(exc)))
        except UnicodeDecodeError as exc:
            corrupted.append((py_file, 0, f"Encoding error: {exc}"))
        except (OSError, ValueError, TypeError) as exc:
            corrupted.append((py_file, 0, f"Parse error: {exc}"))

    return corrupted


def detect_corruption_patterns(project_root: Path) -> list[tuple[Path, int, str]]:
    """Scan for common corruption patterns in Python files."""
    patterns = {
        r"<<<<<<< HEAD": "Git merge conflict marker",
        r">>>>>>> ": "Git merge conflict marker",
        r"=======$": "Git merge conflict marker",
        r"\x00": "Null byte corruption",
        r"\ufffd": "Unicode replacement character",
        r"\.\.\.\s*\)": "Truncated function call",
        r"except\s+Exception\s+as\s+\w+:\s*\n\s*raise\s*\n": "Dead code after raise",
    }

    corruption_patterns = []
    exclude_patterns = list(
        GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES
    )

    for py_file in tqdm(sorted(project_root.rglob("*.py")), desc="Processing", unit="item"):
        if any(pattern in str(py_file) for pattern in exclude_patterns):
            continue
        try:
            content = py_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        for lineno, line in enumerate(content.splitlines(), start=1):
            for pattern, description in patterns.items():
                if re.search(pattern, line):
                    corruption_patterns.append((py_file, lineno, f"{description}: {line.strip()}"))

    return corruption_patterns
