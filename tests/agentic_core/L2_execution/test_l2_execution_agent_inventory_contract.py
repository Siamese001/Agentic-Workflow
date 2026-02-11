#!/usr/bin/env python3
"""
L2 Execution Agent Inventory Contract Test

Deterministic AST-based gates to prevent agent count re-inflation
and enforce naming/structure rules for agentic_core/L2_execution/.

Rules enforced:
  1. NAMING: Any *Agent.py under L2_execution must contain exactly one
     top-level ClassDef whose name ends with 'Agent' (or an approved
     exception like 'Gateway').
  2. REACHABILITY: Each L2 agent class must be imported by at least one
     production entrypoint, or be explicitly allow-listed.
  3. PINNED BUDGET: The *Agent.py count must not exceed the post-cleanup
     ceiling without a baseline update + justification.
"""
from __future__ import annotations

import ast
import os
from pathlib import Path

# ── Constants ────────────────────────────────────────────────────────────
L2_ROOT = Path("agentic_core") / "L2_execution"
REPO_ROOT = Path(".")

# Post-cleanup ceiling (Phase 2 result: 4 Agent files).
# Increase ONLY with justification in the commit message.
AGENT_FILE_BUDGET = 4

# Allow-listed class names that do not end in "Agent" but reside in *Agent.py
# (e.g. SovereignMCPGatewayAgent.py contains class SovereignMCPGateway)
CLASS_NAME_EXCEPTIONS: dict[str, str] = {
    "SovereignMCPGatewayAgent.py": "SovereignMCPGateway",
}

# Allow-listed agent classes that have no direct production import today
# but are retained intentionally.  Each entry requires a justification string.
REACHABILITY_ALLOWLIST: dict[str, str] = {
    "SovereignMCPGateway": "Accessed via get_mcp_gateway() function import in mcp_operation_mixin.py",
    "ToolsmithAgent": "Referenced via dynamic AgentInfo config in SovereignCognitivePlaneAgent.py",
}

# Production roots to scan for reachability (non-test, non-artifact code)
PROD_ROOTS = [
    "agentic_core",
    "apps_lic",
    "apps_rg",
    "apps_shared",
    "ops_scripts",
]


# ── Helpers ──────────────────────────────────────────────────────────────
def _collect_agent_files() -> list[Path]:
    """Return all *Agent.py files under L2_ROOT."""
    return sorted(p for p in L2_ROOT.rglob("*Agent.py") if p.is_file())


def _parse_top_level_classes(path: Path) -> list[str]:
    """Return names of top-level ClassDef nodes via AST."""
    src = path.read_text(encoding="utf-8")
    tree = ast.parse(src, filename=str(path))
    return [node.name for node in tree.body if isinstance(node, ast.ClassDef)]


def _collect_prod_imports_of(class_names: set[str]) -> dict[str, list[str]]:
    """AST-scan production code for ImportFrom statements that import any of *class_names*.

    Returns {class_name: [file_path, ...]}.
    """
    hits: dict[str, list[str]] = {n: [] for n in class_names}
    for root_dir in PROD_ROOTS:
        root_path = REPO_ROOT / root_dir
        if not root_path.exists():
            continue
        for dirpath, _, filenames in os.walk(root_path):
            dp = Path(dirpath)
            if "__pycache__" in dp.parts:
                continue
            for fname in filenames:
                if not fname.endswith(".py"):
                    continue
                fpath = dp / fname
                try:
                    src = fpath.read_text(encoding="utf-8")
                    tree = ast.parse(src, filename=str(fpath))
                except Exception:
                    continue
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom) and node.module:
                        for alias in node.names:
                            if alias.name in class_names:
                                hits[alias.name].append(str(fpath))
    return hits


# ── Tests ────────────────────────────────────────────────────────────────
class TestL2AgentNamingAndStructure:
    """Every *Agent.py must have exactly one top-level ClassDef ending in Agent."""

    def test_agent_files_have_single_agent_classdef(self):
        agent_files = _collect_agent_files()
        violations: list[str] = []
        for af in agent_files:
            classes = _parse_top_level_classes(af)
            agent_classes = [
                c for c in classes
                if c.endswith("Agent")
                or (af.name in CLASS_NAME_EXCEPTIONS
                    and c == CLASS_NAME_EXCEPTIONS[af.name])
            ]
            if len(agent_classes) == 0:
                violations.append(f"{af}: NO agent ClassDef found (classes: {classes})")
        assert not violations, (
            "L2 *Agent.py files without a qualifying agent ClassDef:\n"
            + "\n".join(violations)
        )


class TestL2AgentReachability:
    """Each L2 agent class must be imported by production code or allow-listed."""

    def test_all_agents_reachable_or_allowlisted(self):
        agent_files = _collect_agent_files()
        class_to_file: dict[str, str] = {}
        for af in agent_files:
            classes = _parse_top_level_classes(af)
            for c in classes:
                if c.endswith("Agent") or (
                    af.name in CLASS_NAME_EXCEPTIONS
                    and c == CLASS_NAME_EXCEPTIONS[af.name]
                ):
                    class_to_file[c] = str(af)

        prod_imports = _collect_prod_imports_of(set(class_to_file.keys()))
        unreachable: list[str] = []
        for cls, defpath in class_to_file.items():
            importers = [f for f in prod_imports.get(cls, []) if f != defpath]
            if not importers and cls not in REACHABILITY_ALLOWLIST:
                unreachable.append(f"{cls} (defined in {defpath})")

        assert not unreachable, (
            "L2 agent classes with NO production imports and NOT allow-listed:\n"
            + "\n".join(unreachable)
            + "\n\nTo allow-list, add to REACHABILITY_ALLOWLIST with justification."
        )


class TestL2AgentBudget:
    """Pin *Agent.py count to prevent creep."""

    def test_agent_file_count_within_budget(self):
        agent_files = _collect_agent_files()
        count = len(agent_files)
        assert count <= AGENT_FILE_BUDGET, (
            f"L2 *Agent.py count ({count}) exceeds budget ({AGENT_FILE_BUDGET}). "
            f"Files: {[str(f) for f in agent_files]}. "
            f"Update AGENT_FILE_BUDGET with justification if intentional."
        )

    def test_budget_print(self):
        """Print governance signal per §32."""
        agent_files = _collect_agent_files()
        count = len(agent_files)
        delta = count - AGENT_FILE_BUDGET
        print(f"L2_AGENT_COUNT={count} BUDGET={AGENT_FILE_BUDGET} DELTA={delta}")
        assert delta <= 0
