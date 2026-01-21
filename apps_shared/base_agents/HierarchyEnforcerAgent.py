
# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: engine, memory, orchestrator, prompt, state, workflow
# This boosts alignment detection — review and integrate appropriately

from __future__ import annotations

from dataclasses import dataclass

#!/usr/bin/env python3
"""
HierarchyEnforcerAgent - Ensures L4 structure compliance
"""

from pathlib import Path
from typing import Any

from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin

from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.utils.core_extensions.subatomic_testing_mixin import SubatomicTestingMixin
from agentic_core.utils.core_extensions.timeout_decorator import timeout


@dataclass
class HierarchyEnforcerAgent(MCPHardenedMixin, SubatomicTestingMixin, HealerMixin):
    """
    Enforces the canonical L4 hierarchy across agentic_core.
    Drills down from L2 -> L3 -> L4 to ensure all required directories exist.
    """

    def __init__(self, project_root: Path, ctx: Any) -> None:
        """Initialize the instance."""
        from agentic_core.L5_safety.validators.structure_blueprint import (
            CORE_L3_SUBFOLDER_MAP,
            CORE_L4_SUBFOLDER_MAP,
            SOVEREIGN_REGISTRY,
        )
        self.canon_structure = SOVEREIGN_REGISTRY  # Legacy bridge – migrate to SOVEREIGN_REGISTRY
        self.l3_map = CORE_L3_SUBFOLDER_MAP
        self.l4_map = CORE_L4_SUBFOLDER_MAP
        self.project_root = project_root
        self.ctx = ctx

        # [DEPTH ARCHIVAL] Where depth-drift goes to die
        from agentic_core.L5_safety.validators.structure_blueprint import DEPRECATION_ARCHIVE
        self.archive_root = project_root / DEPRECATION_ARCHIVE / "depth_violations"
        self.archive_root.mkdir(parents=True, exist_ok=True)

    def enforce_hierarchy(self) -> dict[str, Any]:
        """
        Enforce L4 structure across all required directories.
        Returns dict of actions taken.
        """
        actions = []

        # Get L2 structure from CANON_STRUCTURE
        l2_structure = self.canon_structure["agentic_core"]["subfolders"]

        for l2_name in l2_structure:
            l2_path = self.project_root / "agentic_core" / l2_name
            if not l2_path.exists():
                continue

            # Check if this L2 has L3 requirements
            expected_l3 = set(self.l3_map.get(l2_name, []))

            for l3_name in expected_l3:
                l3_path = l2_path / l3_name
                if not l3_path.exists(): continue

                # [L4 DRILL DOWN]
                expected_l4 = set(self.l4_map.get(l3_name, []))
                actual_l4 = {p.name for p in l3_path.iterdir() if p.is_dir() and not p.name.startswith(".")}

                for missing_l4 in expected_l4 - actual_l4:
                    l4_path = l3_path / missing_l4
                    l4_path.mkdir(parents=True, exist_ok=True)
                    (l4_path / "__init__.py").touch()
                    actions.append(f"CREATED L4: {l2_name}/{l3_name}/{missing_l4}")
                    created.append(f"CREATED L4: {l2_name}/{l3_name}/{missing_l4}")

        return {
            "created": created,
            "archived": archived,
        }

    @timeout(300)
    def heal_repository(self, dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: set | None = None) -> dict[str, int]:
        """Observability metrics agent - operational only."""
        super().heal_repository(dry_run, execute, depth, max_depth, _call_path)
        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            print(f"[{agent_name}] Observability metrics - operational only")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)

    def enforce_depth_precision(self) -> list[str]:
        """
        # CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)
        super().heal_repository()

        Apps depth enforcement. If it's not depth 3, it gets archived.
        """
        from agentic_core.L5_safety.validators.structure_blueprint import SOVEREIGN_REGISTRY
        apps_exact_depth = SOVEREIGN_REGISTRY["apps_rg"]["depth"]  # Legacy bridge – migrate to SOVEREIGN_REGISTRY
        actions = []

        # [APPS DEPTH 3] Target all files under apps_* (Universal enforcement)
        for file_path in self.project_root.rglob("*"):
            if file_path.is_dir() or any(part.startswith(".") for part in file_path.parts):
                continue

            rel = file_path.relative_to(self.project_root)
            if not rel.parts[0].startswith("apps_"):
                continue

            # [FIX] Depth = folder level where file resides, not path length
            depth = len(rel.parts) - 1  # Subtract 1 because file itself is not a level
            if depth != apps_exact_depth:
                # ARCHIVE THE DRIFT
                archive_path = self.archive_root / "apps_depth" / rel
                archive_path.parent.mkdir(parents=True, exist_ok=True)

                explanation = f"# APPS DEPTH VIOLATION ARCHIVED — {__import__('datetime').datetime.now().isoformat()}\nfrom agentic_core.utils.core_extensions.subatomic_testing_mixin import SubatomicTestingMixin\nfrom agentic_core.utils.core_extensions.mcp_hardened_mixin import MCPHardenedMixin\nimport logging\n\nLogger = logging.getLogger(__name__)\n"
                explanation += f"# {rel} was depth {depth}, but apps_* MUST be exactly {apps_exact_depth}.\n\n"

                try:
                    content = file_path.read_text(encoding="utf-8", errors="ignore")
                    archive_path.write_text(explanation + content, encoding="utf-8")
                    file_path.unlink()
                    actions.append(f"ARCHIVED apps_* drift: {rel}")
                    self.ctx.report("DepthEnforcer", 1, True, f"Archived {rel} (apps depth {depth})")
                except Exception as e:
                    actions.append(f"APPS ARCHIVE FAILED: {rel} — {e}")

        return actions

    def enforce_tests_depth(self) -> list[str]:
        """
        Tests depth enforcement. If it's not depth 3, it gets archived.
        """
        from agentic_core.L5_safety.validators.structure_blueprint import SOVEREIGN_REGISTRY
        tests_exact_depth = SOVEREIGN_REGISTRY["tests"]["depth"]  # Legacy bridge – migrate to SOVEREIGN_REGISTRY
        actions = []

        # [TESTS DEPTH 3] Target all files under tests/ (Universal enforcement)
        for file_path in self.project_root.rglob("*"):
            if file_path.is_dir() or any(part.startswith(".") for part in file_path.parts):
                continue

            rel = file_path.relative_to(self.project_root)
            if rel.parts[0] != "tests":
                continue

            # [FIX] Depth = folder level where file resides, not path length
            depth = len(rel.parts) - 1  # Subtract 1 because file itself is not a level
            if depth != tests_exact_depth:
                # ARCHIVE THE DRIFT
                archive_path = self.archive_root / "tests_depth" / rel
                archive_path.parent.mkdir(parents=True, exist_ok=True)

                explanation = f"# TESTS DEPTH VIOLATION ARCHIVED — {__import__('datetime').datetime.now().isoformat()}\n"
                explanation += f"# {rel} was depth {depth}, but tests MUST be exactly {tests_exact_depth}.\n\n"

                try:
                    content = file_path.read_text(encoding="utf-8", errors="ignore")
                    archive_path.write_text(explanation + content, encoding="utf-8")
                    file_path.unlink()
                    actions.append(f"ARCHIVED tests drift: {rel}")
                except Exception as e:
                    actions.append(f"TESTS ARCHIVE FAILED: {rel} — {e}")

        return actions

    def enforce_universal_depth(self) -> list[str]:
        """
        Universal depth enforcement for all file types under agentic_core.
        Archives non-Python files that violate depth 4 rule.
        """
        from agentic_core.L5_safety.validators.structure_blueprint import (
            SOVEREIGN_REGISTRY,
        )
        agentic_core_exact_depth = SOVEREIGN_REGISTRY["agentic_core"]["depth"]  # Legacy bridge – migrate to SOVEREIGN_REGISTRY
        actions = []

        # [UNIVERSAL ENFORCEMENT] Target common data/doc extensions
        target_exts = {".json", ".md", ".yaml", ".yml", ".toml", ".txt"}
        for file_path in self.project_root.rglob("*"):
            if file_path.is_dir() or any(part.startswith(".") for part in file_path.parts):
                continue

            if file_path.suffix.lower() not in target_exts:
                continue

            rel = file_path.relative_to(self.project_root)
            if rel.parts[0] == "agentic_core":
                # [FIX] Depth = folder level where file resides, not path length
                depth = len(rel.parts) - 1  # Subtract 1 because file itself is not a level
                if depth != agentic_core_exact_depth:
                    # [ARCHIVE UNIVERSAL DRIFT]
                    archive_path = self.archive_root / "non_python" / rel
                    archive_path.parent.mkdir(parents=True, exist_ok=True)

                    header = f"# UNIVERSAL DEPTH VIOLATION — {__import__('datetime').datetime.now().isoformat()}\n"
                    header += f"# File {rel} was at depth {depth}, but MUST be {agentic_core_exact_depth}.\n\n"

                    try:
                        # We handle text files directly; binaries might need different logic
                        content = file_path.read_text(encoding="utf-8", errors="ignore")
                        archive_path.write_text(header + content, encoding="utf-8")
                        file_path.unlink()
                        actions.append(f"ARCHIVED non-python drift: {rel}")
                    except Exception as e:
                        actions.append(f"FAILED to archive non-python {rel}: {e}")

        return actions

    def validate_hierarchy(self) -> dict[str, Any]:
        """
        Validate L4 structure compliance.
        Returns validation report.
        """
        violations = []

        # Get L2 structure from CANON_STRUCTURE
        l2_structure = self.canon_structure["agentic_core"]["subfolders"]

        for l2_name in l2_structure:
            l2_path = self.project_root / "agentic_core" / l2_name
            if not l2_path.exists():
                continue

            expected_l3 = set(self.l3_map.get(l2_name, []))

            for l3_name in expected_l3:
                l3_path = l2_path / l3_name
                if not l3_path.exists(): continue

                expected_l4 = set(self.l4_map.get(l3_name, []))
                actual_l4 = {p.name for p in l3_path.iterdir() if p.is_dir() and not p.name.startswith(".")}

                missing_l4 = expected_l4 - actual_l4
                if missing_l4:
                    violations.append({
                        "path": f"{l2_name}/{l3_name}",
                        "Missing": list(missing_l4)
                    })

        return {
            "status": "validated",
            "violations": violations,
            "compliant": len(violations) == 0
        }

    async def execute(self, ctx: Any) -> Any:
        """Execute execute operation."""
        issues = self.enforce_hierarchy()
        issues.extend(self.enforce_depth_precision())
        issues.extend(self.enforce_tests_depth())
        issues.extend(self.enforce_universal_depth())
        if issues:
            print(f"   [HEALING] HierarchyEnforcerAgent: {len(issues)} actions taken")
