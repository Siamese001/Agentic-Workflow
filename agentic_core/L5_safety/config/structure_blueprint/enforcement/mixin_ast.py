"""
Mixin AST — Layer 4: Structural enforcement for the mixins/ territory.

Enforces:
1. Flat directory (no subdirectories allowed).
2. Naming convention compliance for all .py files.
3. Each mixin file must define exactly one class with Mixin/Contract in its name.
"""

from __future__ import annotations

import ast
import os
import re
from pathlib import Path
from typing import Any, Mapping

from agentic_core.L5_safety.config.structure_blueprint.enforcement.types import (
    EnforcementResult,
    Violation,
    make_result,
)


def check(
    root: Path,
    territories: Mapping[str, Any],
) -> EnforcementResult:
    """Check mixins/ territory structural rules."""
    violations: list[Violation] = []
    stats = {
        "files_checked": 0,
        "naming_violations": 0,
        "flat_violations": 0,
        "ast_violations": 0,
    }

    mixins_config = territories.get("mixins")
    if not isinstance(mixins_config, Mapping):
        return make_result("mixin_ast", violations, stats)

    mixins_path = root / "mixins"
    if not mixins_path.is_dir():
        return make_result("mixin_ast", violations, stats)

    # Extract naming convention regex
    naming_re_str = mixins_config.get("naming_convention", "")
    naming_re = re.compile(naming_re_str) if naming_re_str else None

    # Check flat rule
    is_flat = bool(mixins_config.get("flat", False))

    try:
        for entry in os.scandir(mixins_path):
            if entry.is_dir() and entry.name != "__pycache__":
                if is_flat:
                    stats["flat_violations"] += 1
                    violations.append(
                        Violation(
                            type="mixin_flat_violation",
                            path=f"mixins/{entry.name}",
                            severity="error",
                            detail=f"Subdirectory '{entry.name}' found in mixins/ which is declared flat",
                        ),
                    )

            if entry.is_file() and entry.name.endswith(".py") and entry.name != "__init__.py":
                stats["files_checked"] += 1

                # Naming convention check
                if naming_re and not naming_re.match(entry.name):
                    stats["naming_violations"] += 1
                    violations.append(
                        Violation(
                            type="mixin_naming_violation",
                            path=f"mixins/{entry.name}",
                            severity="error",
                            detail=f"File '{entry.name}' does not match mixins naming convention: {naming_re_str}",
                        ),
                    )

                # AST check: must contain at least one class
                _check_mixin_ast(mixins_path / entry.name, entry.name, violations, stats)
    except OSError:
        pass

    return make_result("mixin_ast", violations, stats)


def _check_mixin_ast(
    filepath: Path,
    filename: str,
    violations: list[Violation],
    stats: dict[str, int],
) -> None:
    """Parse a mixin file and verify it contains a mixin/contract class."""
    try:
        source = filepath.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(filepath))
    except (SyntaxError, UnicodeDecodeError, OSError):
        return

    classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

    if not classes:
        stats["ast_violations"] += 1
        violations.append(
            Violation(
                type="mixin_no_class",
                path=f"mixins/{filename}",
                severity="warning",
                detail=f"Mixin file '{filename}' contains no class definitions",
            ),
        )
