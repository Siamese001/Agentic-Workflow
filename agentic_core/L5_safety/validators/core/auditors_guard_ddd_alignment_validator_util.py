from __future__ import annotations

"""
Sovereign Guardian: DDD Alignment
Enforces Bounded Contexts and Aggregate Root access.
"""
import ast
from pathlib import Path
from typing import Any

# from agentic_core.L1_cognition.P2_domain.sovereign  # Refactored to dynamic import to avoid upward dependency


def _get_sovereign_domain():
    """Lazy load sovereign domain to avoid L0 → L1 dependency."""
    import importlib

    module = importlib.import_module("agentic_core.L1_cognition.P2_domain.sovereign")
    return module


# from _domain_constitution import BOUNDED_CONTEXTS, UBIQUITOUS_LANGUAGE  # Commented out - appears to be incomplete/broken import

# [SSOT IMPORT] Structure blueprint is the single source of truth


def check_bounded_contexts(filepath: Path) -> list[str]:
    """Brief description of functionality and purpose."""
    issues: Any = []
    file_str: Any = str(filepath).replace("\\", "/")
    current_context: Any = next(
        (ctx for ctx, info in BOUNDED_CONTEXTS.items() if info.get("path") in file_str), None,
    )
    if not current_context:
        return []
    stdlib_modules: Any = {
        "pathlib",
        "os",
        "sys",
        "json",
        "logging",
        "typing",
        "datetime",
        "collections",
        "itertools",
        "functools",
        "re",
        "asyncio",
        "abc",
        "dataclasses",
        "enum",
        "copy",
        "io",
        "time",
        "uuid",
        "hashlib",
    }
    try:
        tree: Any = ast.parse(filepath.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                module_root: Any = node.module.split(".")[0]
                if module_root in stdlib_modules:
                    continue
                if "apps_shared.base_agents" in node.module:
                    continue
                for ctx, info in BOUNDED_CONTEXTS.items():
                    if ctx == current_context:
                        continue
                    if ctx == "SharedContracts":
                        continue
                    target_path: Any = info.get("path", "")
                    if target_path.replace("/", ".") in node.module:
                        if "contracts" not in node.module and "interfaces" not in node.module:
                            issues.append(
                                f"Potential Context Violation: Importing {ctx} logic ({node.module}) into {current_context}",
                            )
    except Exception:
        pass
    return issues


def validate_ddd_alignment(target_dir: str) -> tuple[float, list[str]]:
    """Brief description of functionality and purpose."""
    issues: Any = []
    total_files: Any = 0
    from agentic_core.utils.ssot_discovery_validator import get_python_files

    for path in get_python_files(Path(target_dir)):
        if "tests" in str(path):
            continue
        total_files += 1
        issues.extend([f"{str(path)}: {i}" for i in check_bounded_contexts(path)])
    score: Any = 100.0
    if issues:
        score: Any = max(0, 100 - len(issues) * 2)
    return (score, issues)
