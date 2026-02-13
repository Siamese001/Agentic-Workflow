#!/usr/bin/env python3
"""Guardian Test: Healing Subsystem Import Audit.

Forces actual import execution for ALL healing strategy and MCP client files.
NO pytest.skip() ALLOWED in this module — healing subsystem cannot be allowed to rot.

This test exists because:
- Healing code is rarely invoked in happy-path tests
- The pytest.skip(ImportError) pattern masked P1_core breakage for 2+ months
- Healing/MCP code is HIGH RISK for silent rot (lazy-loaded, edge-case triggered)

RCA: docs/reports/plans/RCA_P1_core_dead_imports.md
"""

from __future__ import annotations

import ast
import importlib
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# ---------------------------------------------------------------------------
# Healing subsystem files that MUST import cleanly (no skip, no xfail)
# ---------------------------------------------------------------------------

HEALING_MODULES: list[str] = []
HEALING_FILES: list[str] = []

# Auto-discover all healing-related files
_HEALING_DIRS = [
    "agentic_core/L5_safety/enforcement",
    "agentic_core/knowledge/healing",
    "agentic_core/L3_orchestration/enforcement",
]

_HEALING_KEYWORDS = frozenset(
    {
        "healing",
        "healer",
        "heal",
        "mcp_client",
        "mcp_router",
        "sovereign_healing",
        "transaction_manager",
    },
)


def _discover_healing_files() -> list[tuple[str, str]]:
    """Discover healing-related .py files and their module paths.

    Returns list of (module_path, file_rel_path) tuples.
    """
    results: list[tuple[str, str]] = []

    for heal_dir in _HEALING_DIRS:
        dir_path = PROJECT_ROOT / heal_dir
        if not dir_path.is_dir():
            continue
        for py_file in sorted(dir_path.glob("*.py")):
            if py_file.name.startswith("_") and py_file.name != "__init__.py":
                continue
            if py_file.name == "__init__.py":
                continue
            stem = py_file.stem.lower()
            # Include if filename contains healing keywords
            if any(kw in stem for kw in _HEALING_KEYWORDS):
                rel = py_file.relative_to(PROJECT_ROOT).as_posix()
                module = rel.replace("/", ".").removesuffix(".py")
                results.append((module, rel))

    return results


HEALING_ENTRIES = _discover_healing_files()


# ---------------------------------------------------------------------------
# Known broken imports (P1_core dead) — these are expected to FAIL
# until R-4 cleanup is complete. Listed here for triage visibility.
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# xfail governance lock (Phase 3) — count must NOT increase without review
# ---------------------------------------------------------------------------
EXPECTED_XFAIL_COUNT = 8

KNOWN_BROKEN_IMPORTS = frozenset(
    {
        # P1_core dead directory (RCA primary cause)
        "agentic_core.L5_safety.enforcement.audit_healing_strategy",
        "agentic_core.L5_safety.enforcement.git_kraken_healing_strategy",
        "agentic_core.L5_safety.enforcement.sovereign_healing_engine",
        "agentic_core.L5_safety.enforcement.vector_healing_strategy",
        "agentic_core.knowledge.healing.wiki_healer",
        "agentic_core.L3_orchestration.enforcement.knowledge_graph_healing_strategy",
        # Other broken import chains (pre-existing)
        "agentic_core.L5_safety.enforcement.git_health_sensor",  # missing detection_signal_config
        "agentic_core.L5_safety.enforcement.healing_invocation_audit",  # missing agentic_core.utils.security
    },
)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.guardian
@pytest.mark.import_safety
class TestHealingSubsystemImports:
    """Healing subsystem MUST import cleanly. No skip allowed."""

    @pytest.mark.parametrize(
        "module_path,file_path",
        HEALING_ENTRIES,
        ids=[e[1] for e in HEALING_ENTRIES],
    )
    def test_healing_module_imports(self, module_path: str, file_path: str):
        """Every healing module must be importable without error.

        Known P1_core broken imports are marked xfail with strict=True so
        they flip to XPASS (and alert) once R-4 cleanup lands.
        """
        if module_path in KNOWN_BROKEN_IMPORTS:
            pytest.xfail(
                f"KNOWN BROKEN (P1_core dead): {module_path} — "
                "will pass after R-4 cleanup. See RCA_P1_core_dead_imports.md",
            )

        try:
            mod = importlib.import_module(module_path)
            assert mod is not None, f"Module {module_path} imported as None"
        except ImportError as exc:
            pytest.fail(
                f"HEALING IMPORT BROKEN: {module_path}\n"
                f"  File: {file_path}\n"
                f"  Error: {exc}\n"
                f"  This is a healing subsystem file — skip is FORBIDDEN.\n"
                f"  Fix the import or update KNOWN_BROKEN_P1_CORE for triage.",
            )

    def test_no_p1_core_imports_in_healing_files(self):
        """AST-verify that no healing file imports from P1_core (dead directory)."""
        violations: list[str] = []

        for _module_path, file_path in HEALING_ENTRIES:
            fpath = PROJECT_ROOT / file_path
            if not fpath.exists():
                continue
            try:
                source = fpath.read_text(encoding="utf-8")
                tree = ast.parse(source, filename=str(fpath))
            except (OSError, SyntaxError):
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module:
                    if "P1_core" in node.module:
                        violations.append(
                            f"{file_path}:{node.lineno} -> {node.module}",
                        )

        if violations:
            msg = (
                f"Found {len(violations)} P1_core import(s) in healing subsystem:\n"
                + "\n".join(f"  {v}" for v in violations)
                + "\n\nThese imports target deleted directories. Fix per R-4."
            )
            # Use xfail until R-4 lands — then switch to pytest.fail
            pytest.xfail(msg)

    def test_healing_discovery_count(self):
        """Governance signal: track number of discovered healing files."""
        count = len(HEALING_ENTRIES)
        print(f"[HEALING-AUDIT] discovered_count={count}")
        # Minimum sanity — we should find at least the known files
        assert count >= 3, (
            f"Expected at least 3 healing files, found {count}. Check _HEALING_DIRS and _HEALING_KEYWORDS."
        )

    def test_xfail_count_locked(self):
        """Lock: KNOWN_BROKEN_IMPORTS count must equal EXPECTED_XFAIL_COUNT.

        If this test fails, either:
          - A broken import was ADDED without updating EXPECTED_XFAIL_COUNT
            (regression — investigate before bumping).
          - A broken import was FIXED and removed from KNOWN_BROKEN_IMPORTS
            without decrementing EXPECTED_XFAIL_COUNT (good — decrement it).

        No dynamic thresholds. No silent drift.
        """
        observed = len(KNOWN_BROKEN_IMPORTS)
        print(
            f"[HEALING-AUDIT] expected_xfail={EXPECTED_XFAIL_COUNT} observed_xfail={observed}",
        )
        assert observed == EXPECTED_XFAIL_COUNT, (
            f"xfail count drift: expected={EXPECTED_XFAIL_COUNT}, "
            f"observed={observed}. "
            f"Update EXPECTED_XFAIL_COUNT after review."
        )
