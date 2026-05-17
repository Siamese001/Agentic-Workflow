#!/usr/bin/env python3
"""
check_heal_routing_threshold_ssot.py — Confidence heal-band SSOT sentinels.

Rules (confidence-routing-ssot-cleanup-b7e2f1 W4 subset):
    1. ``ConfidenceScorer`` sources numeric bounds only through routing SSOT helpers.
    2. Deprecated ``path_constants`` HEALING_CONFIDENCE_* float aliases have **zero** prod imports (tests exempt).
    3. Forbidden legacy strings ``SOVEREIGN_HIGH_CONFIDENCE`` /
       ``SOVEREIGN_MEDIUM_CONFIDENCE`` do not appear in ``.env.example`` or docs markdown.
    4. Env consumer map cites the new heal knobs.

Bypass: HEAL_ROUTING_SSOT_BYPASS=1
"""

from __future__ import annotations

import ast
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
HEALERS_DIR = REPO_ROOT / "agentic_core" / "L2_execution" / "healers"
CONF_SCORER = HEALERS_DIR / "confidence_scorer.py"
MAP_PATH = REPO_ROOT / "docs" / "wave_g" / "G2b_provider_gateway" / "env_key_consumer_map.md"
FORBIDDEN_SOVEREIGN = ("SOVEREIGN_HIGH_CONFIDENCE", "SOVEREIGN_MEDIUM_CONFIDENCE")
DEPRECATED_PATH_NAMES = ("HEALING_CONFIDENCE_X", "HEALING_CONFIDENCE_Y")
BYPASS_ENV = "HEAL_ROUTING_SSOT_BYPASS"


class _ForbiddenImport(ast.NodeVisitor):
    """Detect legacy path_constants heal confidence imports."""

    def __init__(self) -> None:
        self.hits: list[tuple[int, str]] = []

    def visit_ImportFrom(self, node: ast.ImportFrom):  # noqa: N802
        mod = node.module or ""
        if mod != "agentic_core.L0_routing.config.path_constants":
            return self.generic_visit(node)
        if node.names is None:
            return self.generic_visit(node)
        for alias in node.names:
            if alias.name in DEPRECATED_PATH_NAMES:
                self.hits.append((node.lineno, alias.name))
        return self.generic_visit(node)


def _scan_deprecated_imports() -> list[tuple[str, int, str]]:
    violations: list[tuple[str, int, str]] = []
    for py in REPO_ROOT.rglob("*.py"):
        parts = py.parts
        if "__pycache__" in parts or "venv" in parts or ".venv" in parts:
            continue
        rel = str(py.relative_to(REPO_ROOT)).replace("\\", "/")
        if "/tests/" in f"/{rel}/" or rel.startswith("tests/"):
            continue
        if py == REPO_ROOT / "tools" / "routing" / "calibrate_thresholds.py":
            continue

        tree = ast.parse(py.read_text(encoding="utf-8"), filename=str(py))
        finder = _ForbiddenImport()
        finder.visit(tree)
        for lineno, name in finder.hits:
            violations.append((rel, lineno, name))
    return violations


def main() -> int:
    if os.environ.get(BYPASS_ENV) == "1":
        print(f"{BYPASS_ENV}=1 bypass active")
        return 0

    errors: list[str] = []

    text = CONF_SCORER.read_text(encoding="utf-8")
    if "routing_thresholds_ssot" not in text:
        errors.append(f"{CONF_SCORER.relative_to(REPO_ROOT)} must import routing_thresholds_ssot")

    if not MAP_PATH.exists():
        errors.append("env consumer map missing")
    else:
        map_txt = MAP_PATH.read_text(encoding="utf-8")
        for knob in ("HEALING_CONFIDENCE_HIGH", "HEALING_CONFIDENCE_MEDIUM"):
            if knob not in map_txt:
                errors.append(f"env_key_consumer_map.md missing `{knob}` registry row")

    for token in FORBIDDEN_SOVEREIGN:
        dotenv = REPO_ROOT / ".env.example"
        if token in dotenv.read_text(encoding="utf-8"):
            errors.append(f".env.example must not advertise deprecated `{token}`")

        doc_root = REPO_ROOT / "docs"
        for md_path in sorted(doc_root.rglob("*.md")):
            if token in md_path.read_text(encoding="utf-8"):
                errors.append(f"docs leakage `{token}` at {md_path.relative_to(REPO_ROOT)}")

    for rel, lineno, name in _scan_deprecated_imports():
        errors.append(f"deprecated import {name} at {rel}:{lineno}")

    if errors:
        print("❌ heal-routing-threshold-ssot gate FAILED", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    print("✅ heal-routing-threshold-ssot gate passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
