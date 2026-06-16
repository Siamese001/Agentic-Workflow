#!/usr/bin/env python3
"""Retired confidence-routing guard.

Current policy: keep L2 E4 same-authority repair, but do not advertise or
consume confidence-router env knobs. This script keeps the old CI entrypoint
name so run_contract_gates does not need a compatibility shim.
"""

from __future__ import annotations

import ast
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BYPASS_ENV = "HEAL_ROUTING_DEPRECATION_BYPASS"

ENV_FILES = (
    REPO_ROOT / ".env",
    REPO_ROOT / ".env.example",
)

FORBIDDEN_ENV_TEXT = (
    "HEALING_CONFIDENCE_HIGH",
    "HEALING_CONFIDENCE_MEDIUM",
    "L2 heal routing",
    "routing_thresholds_ssot",
    "generator to one model",
    "operator override",
    "pins EVERY section",
)

FORBIDDEN_IMPORTS = (
    "agentic_core.L2_execution.healers.routing_thresholds_ssot",
    "agentic_core.L3_orchestration.healers.healing_tier_config",
)

FORBIDDEN_APP_TEXT = (
    "HealingRouter",
    "ConfidenceAwareExecutor",
    "routing_thresholds_ssot",
    "HEALING_CONFIDENCE_HIGH",
    "HEALING_CONFIDENCE_MEDIUM",
)

SKIP_PARTS = {
    "__pycache__",
    ".hypothesis",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "archives",
    "artifacts",
    "docs",
    "tests",
    "venv",
}


def _rel(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path)


def _iter_python_roots() -> list[Path]:
    roots = [REPO_ROOT / "agentic_core", REPO_ROOT / "ops_scripts", REPO_ROOT / "tools"]
    roots.extend(path for path in REPO_ROOT.iterdir() if path.is_dir() and path.name.startswith("apps_"))
    return [root for root in roots if root.exists()]


def _skip(path: Path) -> bool:
    parts = path.relative_to(REPO_ROOT).parts
    return any(part in SKIP_PARTS for part in parts)


def _scan_env_files() -> list[str]:
    errors: list[str] = []
    for path in ENV_FILES:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for token in FORBIDDEN_ENV_TEXT:
            if token.lower() in text.lower():
                errors.append(f"retired healing env/config text `{token}` in {_rel(path)}")
    return errors


def _scan_imports() -> list[str]:
    errors: list[str] = []
    for root in _iter_python_roots():
        for py_path in root.rglob("*.py"):
            if _skip(py_path) or py_path == Path(__file__).resolve():
                continue
            try:
                tree = ast.parse(py_path.read_text(encoding="utf-8-sig"), filename=str(py_path))
            except SyntaxError as exc:
                errors.append(f"could not parse {_rel(py_path)}: {exc}")
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    if module in FORBIDDEN_IMPORTS:
                        errors.append(f"retired import `{module}` at {_rel(py_path)}:{node.lineno}")
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name in FORBIDDEN_IMPORTS:
                            errors.append(f"retired import `{alias.name}` at {_rel(py_path)}:{node.lineno}")
    return errors


def _scan_app_text() -> list[str]:
    errors: list[str] = []
    for app_root in (path for path in REPO_ROOT.iterdir() if path.is_dir() and path.name.startswith("apps_")):
        for path in app_root.rglob("*"):
            if path.is_dir() or _skip(path):
                continue
            if path.suffix.lower() not in {".py", ".md", ".yaml", ".yml", ".toml"}:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for token in FORBIDDEN_APP_TEXT:
                if token in text:
                    errors.append(f"apps_* must not consume retired healing router `{token}` at {_rel(path)}")
    return errors


def main() -> int:
    if os.environ.get(BYPASS_ENV) == "1":
        print(f"{BYPASS_ENV}=1 bypass active")
        return 0

    errors = [*_scan_env_files(), *_scan_imports(), *_scan_app_text()]
    if errors:
        print("retired-healing-deprecation guard FAILED", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    print("retired-healing-deprecation guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
