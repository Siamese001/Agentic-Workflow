"""
Phase 1: Registry Verification Module
=====================================
Scans codebase for all agents, validates discovery completeness, flags orphans.

This module provides:
1. Full codebase scan for *Agent.py files
2. Cross-reference with agent_discovery_full.json
3. Orphan agent detection (in registry but missing from filesystem)
4. Missing agent detection (in filesystem but not in registry)
5. Path mismatch detection (registry path != actual path)

USAGE:
    from agentic_core.L5_safety.validators.registry_verification import RegistryVerifier
    verifier = RegistryVerifier()
    report = verifier.verify_registry()
"""

from __future__ import annotations

import ast
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Final

# SSOT imports
from agentic_core.L5_safety.validators.structure_blueprint_config import (
    AGENT_DISCOVERY_JSON,
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
)

# Excluded directories for agent scanning
EXCLUDED_DIRS: Final[frozenset[str]] = frozenset(
    {
        "archives",
        ".sovereign_healing_backup",
        "__pycache__",
        ".git",
        "node_modules",
        ".venv",
        "venv",
    }
)


@dataclass
class AgentInfo:
    """Information about a discovered agent."""

    class_name: str
    file_path: Path
    relative_path: str
    layer: str = "Unknown"
    has_agent_class: bool = False
    inheritance: list[str] = field(default_factory=list)
    key_methods: list[str] = field(default_factory=list)


@dataclass
class VerificationResult:
    """Result of registry verification."""

    total_filesystem_agents: int = 0
    total_registry_agents: int = 0
    orphan_agents: list[dict[str, Any]] = field(default_factory=list)
    missing_agents: list[AgentInfo] = field(default_factory=list)
    path_mismatches: list[dict[str, Any]] = field(default_factory=list)
    valid_agents: list[AgentInfo] = field(default_factory=list)
    coverage_percentage: float = 0.0
    is_complete: bool = False
    errors: list[str] = field(default_factory=list)


class RegistryVerifier:
    """Verifies agent registry completeness against filesystem."""

    def __init__(self, project_root: Path | None = None):
        """Initialize verifier with project root."""
        self.project_root = project_root or self._find_project_root()
        self.discovery_path = self._find_discovery_json()

    def _find_project_root(self) -> Path:
        """Find project root by looking for pyproject.toml or .git."""
        current = Path(__file__).resolve()
        for parent in current.parents:
            if (parent / "pyproject.toml").exists() or (parent / ".git").exists():
                return parent
        return Path.cwd()

    def _find_discovery_json(self) -> Path:
        """Find the agent discovery JSON file."""
        # Check L0_maintenance location first (SSOT location)
        l0_path = self.project_root / AGENTIC_CORE_DIR / "L0_maintenance" / AGENT_DISCOVERY_JSON
        if l0_path.exists():
            return l0_path
        # Fallback to root
        root_path = self.project_root / AGENT_DISCOVERY_JSON
        if root_path.exists():
            return root_path
        return l0_path  # Return expected path even if not found

    def _is_excluded(self, path: Path) -> bool:
        """Check if path should be excluded from scanning."""
        path_parts = set(path.parts)
        return bool(path_parts & EXCLUDED_DIRS)

    def _is_test_file(self, path: Path) -> bool:
        """Check if path is a test file."""
        return "tests" in path.parts or path.name.startswith("test_")

    def _extract_layer(self, relative_path: str) -> str:
        """Extract layer from relative path."""
        parts = Path(relative_path).parts
        if len(parts) < 2:
            return "Root"

        first_dir = parts[0]
        if first_dir == AGENTIC_CORE_DIR:
            if len(parts) >= 2:
                second_dir = parts[1]
                if second_dir.startswith("L") and "_" in second_dir:
                    return second_dir.split("_")[0]  # L0, L1, etc.
                if second_dir == "base_agents":
                    return "Base"
                return second_dir.capitalize()
        elif first_dir == APPS_RG_DIR:
            return "Apps_RG"
        elif first_dir == APPS_LIC_DIR:
            return "Apps_LIC"
        elif first_dir == APPS_SHARED_DIR:
            return "Apps_Shared"
        return "Unknown"

    def _parse_agent_file(self, file_path: Path) -> AgentInfo | None:
        """Parse an agent file to extract class information."""
        try:
            if not file_path.exists():
                return None
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(content)
        except (SyntaxError, UnicodeDecodeError, OSError, FileNotFoundError):
            return None

        relative_path = str(file_path.relative_to(self.project_root))

        # Find agent classes
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name.endswith("Agent"):
                # Extract inheritance
                bases = []
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        bases.append(base.id)
                    elif isinstance(base, ast.Attribute):
                        bases.append(base.attr)

                # Extract methods
                methods = [
                    n.name
                    for n in node.body
                    if isinstance(n, ast.FunctionDef | ast.AsyncFunctionDef)
                ]

                return AgentInfo(
                    class_name=node.name,
                    file_path=file_path,
                    relative_path=relative_path,
                    layer=self._extract_layer(relative_path),
                    has_agent_class=True,
                    inheritance=bases,
                    key_methods=methods[:10],  # Limit to first 10 methods
                )

        return None

    def scan_filesystem(self) -> list[AgentInfo]:
        """Scan filesystem for all agent files."""
        agents: list[AgentInfo] = []

        for agent_file in self.project_root.rglob("*Agent.py"):
            # Skip excluded directories
            if self._is_excluded(agent_file):
                continue
            # Skip test files
            if self._is_test_file(agent_file):
                continue

            agent_info = self._parse_agent_file(agent_file)
            if agent_info and agent_info.has_agent_class:
                agents.append(agent_info)

        return agents

    def load_registry(self) -> list[dict[str, Any]]:
        """Load agent registry from JSON file."""
        if not self.discovery_path.exists():
            return []

        try:
            with open(self.discovery_path, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return []

    def verify_registry(self) -> VerificationResult:
        """Perform full registry verification."""
        result = VerificationResult()

        # Scan filesystem
        filesystem_agents = self.scan_filesystem()
        result.total_filesystem_agents = len(filesystem_agents)

        # Load registry
        registry_agents = self.load_registry()
        result.total_registry_agents = len(registry_agents)

        # Build lookup maps
        fs_by_class = {a.class_name: a for a in filesystem_agents}
        fs_by_path = {a.relative_path.replace("\\", "/"): a for a in filesystem_agents}

        registry_by_class = {a.get("class_name", ""): a for a in registry_agents}

        # Check for orphan agents (in registry but not in filesystem)
        for reg_agent in registry_agents:
            class_name = reg_agent.get("class_name", "")
            reg_path = reg_agent.get("path", "").replace("\\", "/")

            if class_name not in fs_by_class:
                result.orphan_agents.append(
                    {
                        "class_name": class_name,
                        "registry_path": reg_path,
                        "reason": "Class not found in filesystem",
                    }
                )
            elif reg_path not in fs_by_path:
                # Path mismatch - class exists but at different location
                actual_agent = fs_by_class[class_name]
                result.path_mismatches.append(
                    {
                        "class_name": class_name,
                        "registry_path": reg_path,
                        "actual_path": actual_agent.relative_path.replace("\\", "/"),
                        "reason": "Path mismatch between registry and filesystem",
                    }
                )

        # Check for missing agents (in filesystem but not in registry)
        for fs_agent in filesystem_agents:
            if fs_agent.class_name not in registry_by_class:
                result.missing_agents.append(fs_agent)
            else:
                result.valid_agents.append(fs_agent)

        # Calculate coverage
        if result.total_filesystem_agents > 0:
            result.coverage_percentage = (
                len(result.valid_agents) / result.total_filesystem_agents * 100
            )

        result.is_complete = (
            len(result.orphan_agents) == 0
            and len(result.missing_agents) == 0
            and len(result.path_mismatches) == 0
        )

        return result

    def generate_report(self, result: VerificationResult) -> str:
        """Generate markdown report from verification result."""
        lines = [
            "# Phase 1: Registry Verification Report",
            "",
            "## Summary",
            "",
            f"- **Total Filesystem Agents:** {result.total_filesystem_agents}",
            f"- **Total Registry Agents:** {result.total_registry_agents}",
            f"- **Valid Agents:** {len(result.valid_agents)}",
            f"- **Missing from Registry:** {len(result.missing_agents)}",
            f"- **Orphan Agents:** {len(result.orphan_agents)}",
            f"- **Path Mismatches:** {len(result.path_mismatches)}",
            f"- **Coverage:** {result.coverage_percentage:.1f}%",
            f"- **Status:** {'PASS' if result.is_complete else 'FAIL'}",
            "",
        ]

        if result.orphan_agents:
            lines.extend(
                [
                    "## Orphan Agents (In Registry, Not in Filesystem)",
                    "",
                    "| Class Name | Registry Path | Reason |",
                    "|------------|---------------|--------|",
                ]
            )
            for orphan in result.orphan_agents:
                cls = orphan["class_name"]
                path = orphan["registry_path"]
                reason = orphan["reason"]
                lines.append(f"| {cls} | {path} | {reason} |")
            lines.append("")

        if result.path_mismatches:
            lines.extend(
                [
                    "## Path Mismatches",
                    "",
                    "| Class Name | Registry Path | Actual Path |",
                    "|------------|---------------|-------------|",
                ]
            )
            for mismatch in result.path_mismatches:
                cls = mismatch["class_name"]
                reg = mismatch["registry_path"]
                act = mismatch["actual_path"]
                lines.append(f"| {cls} | {reg} | {act} |")
            lines.append("")

        if result.missing_agents:
            lines.extend(
                [
                    "## Missing from Registry (In Filesystem, Not in Registry)",
                    "",
                    "| Class Name | File Path | Layer |",
                    "|------------|-----------|-------|",
                ]
            )
            for agent in result.missing_agents[:50]:
                lines.append(f"| {agent.class_name} | {agent.relative_path} | {agent.layer} |")
            if len(result.missing_agents) > 50:
                remaining = len(result.missing_agents) - 50
                lines.append(f"| ... | ({remaining} more) | ... |")
            lines.append("")

        return "\n".join(lines)


def run_verification() -> VerificationResult:
    """Run registry verification and return result."""
    verifier = RegistryVerifier()
    return verifier.verify_registry()


if __name__ == "__main__":
    verifier = RegistryVerifier()
    result = verifier.verify_registry()
    report = verifier.generate_report(result)
    print(report)
