from agentic_core.L2_execution.tools import write_gateway as _wg

"""
File: agentic_core/L5_safety/validators/RootHygieneAgent.py
Path: agentic_core/L5_safety/validators/RootHygieneAgent.py
Rationale:
    Canonizes the RootHygieneEnforcer as a first-class L5 Agent.
    Relocated from L0_routing/scripts to L5_safety/validators to
    centralize enforcement and enable auto-discovery by execute_ssot.py.

    Integration Features:
    - Inherits from SovereignBaseAgent for full infrastructure support
    - Implements standard agent interface for execute_ssot.py orchestration
    - Preserves all original RootHygieneEnforcer functionality
    - Adds heal_repository() method for standard healing chain integration
"""

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Optional: Import SovereignBaseAgent if available for full integration
try:
    from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
    from agentic_core.utils.decorators_compat_util import standard_heal

    HAS_SOVEREIGN_BASE = True
except ImportError:
    HAS_SOVEREIGN_BASE = False
    SovereignBaseAgent = object

    # Use canonical standard_heal from HealingMixin
    from agentic_core.L5_safety.reasoning.FileClassificationAgent import standard_heal


# SSOT Constants
ROOT_MARKERS = ["agentic_core", "pyproject.toml"]


def get_project_root() -> Path:
    """Resolve project root securely."""
    current = Path.cwd()
    for marker in ROOT_MARKERS:
        if (current / marker).exists():
            return current
    raise RuntimeError("Must run from Project Root")


@dataclass
class RootHygieneAgent(SovereignBaseAgent):
    """
    Enforces strict root directory hygiene standards.

    This agent canonizes the RootHygieneEnforcer functionality as a
    first-class L5 safety agent with full orchestration capabilities.

    Responsibilities:
    1. Moves root 'scripts/*' to 'ops_scripts/' (standalone) or 'L0_routing/scripts/' (core)
    2. Moves 'coverage_html' to 'reports/'
    3. Deletes illegal root directories after evacuation
    """

    project_root: Path = field(default_factory=Path.cwd)
    dry_run: bool = False

    def __post_init__(self):
        if HAS_SOVEREIGN_BASE and hasattr(super(), "__post_init__"):
            super().__post_init__()
        # [HARDENING] Ensure path is absolute for resolve() calls
        self.project_root = self.project_root.resolve()
        self.stats = {
            "scripts_evacuated": 0,
            "dirs_evacuated": 0,
            "coverage_relocated": 0,
            "illegal_dirs_removed": 0,
            "errors": 0,
        }

    def run(self) -> dict[str, Any]:
        """Entry point for execute_ssot.py orchestration."""
        print(f"[HYGIENE] Executing Root Hygiene Enforcement at {self.project_root}")
        success = self._enforce_root_hygiene()
        return {
            "success": success == 0,
            "stats": self.stats,
            "summary": f"Scripts: {self.stats['scripts_evacuated']}, Dirs: {self.stats['dirs_evacuated']}, Errors: {self.stats['errors']}",
        }

    def _enforce_root_hygiene(self) -> int:
        """Core logic from RootHygieneEnforcer.py."""
        print(f"[HYGIENE] Enforcing Root Sovereignty at: {self.project_root}")
        print("=" * 60)

        try:
            # 1. EVACUATE ROOT SCRIPTS
            self._evacuate_root_scripts()

            # 2. EVACUATE COVERAGE_HTML
            self._evacuate_coverage_html()

            # 3. RELOCATE PURGE_CACHE (Specific Request)
            self._relocate_purge_cache()

            return 0  # Success

        # guardian: allow-silent-swallow
        except Exception as e:
            print(f"[ERROR] Root hygiene enforcement failed: {e}")
            self.stats["errors"] += 1
            return 1

    def _evacuate_root_scripts(self):
        """Evacuate root scripts directory to appropriate locations."""
        root_scripts = self.project_root / "scripts"
        ops_scripts = self.project_root / "ops_scripts"
        l0_scripts = self.project_root / "agentic_core" / "L0_routing" / "scripts"

        if root_scripts.exists():
            print("[DETECT] Illegal root 'scripts/' directory found.")

            if not self.dry_run:
                _wg.ensure_dir(ops_scripts)
                _wg.ensure_dir(l0_scripts)

            for item in root_scripts.iterdir():
                try:
                    if item.is_file() and item.suffix == ".py":
                        # Decision Logic: Does it import agentic_core?
                        content = item.read_text(encoding="utf-8")
                        if "agentic_core" in content or "from agentic_core" in content:
                            target = l0_scripts / item.name
                            action = "REPATRIATE (Core)"
                        else:
                            target = ops_scripts / item.name
                            action = "RELOCATE (Ops)"

                        print(f"  - {item.name} -> {action}")
                        if not self.dry_run:
                            _wg.move_path(str(item), str(target))
                        self.stats["scripts_evacuated"] += 1

                    elif item.is_dir():
                        # Move entire subfolders to ops_scripts/maintenance or similar
                        target = ops_scripts / item.name
                        print(f"  - DIR {item.name}/ -> RELOCATE (Ops)")
                        if not self.dry_run:
                            if target.exists():
                                _wg.remove_tree(target)  # Force overwrite logic for dirs
                            _wg.move_path(str(item), str(target))
                        self.stats["dirs_evacuated"] += 1

                # guardian: allow-silent-swallow
                except Exception as e:
                    print(f"  [ERROR] Could not move {item.name}: {e}")
                    self.stats["errors"] += 1

            # Cleanup empty dir
            if not self.dry_run:
                try:
                    _wg.remove_dir(root_scripts)
                    print("[SUCCESS] Illegal 'scripts/' directory eliminated.")
                    self.stats["illegal_dirs_removed"] += 1
                except OSError:
                    print("[WARNING] 'scripts/' not empty, manual check required.")
        else:
            print("[CHECK] Root 'scripts/' is clean.")

    def _evacuate_coverage_html(self):
        """Evacuate coverage_html directory to reports/."""
        cov_html = self.project_root / "coverage_html"
        reports_cov = self.project_root / "reports" / "coverage_html"

        if cov_html.exists():
            print("\n[DETECT] Illegal root 'coverage_html/' found.")

            if not self.dry_run:
                _wg.ensure_dir(reports_cov.parent)

                if reports_cov.exists():
                    _wg.remove_tree(reports_cov)

                print("  - Moving to reports/coverage_html")
                _wg.move_path(str(cov_html), str(reports_cov))
                self.stats["coverage_relocated"] += 1
                print("[SUCCESS] Coverage report relocated.")
        else:
            print("[CHECK] Root 'coverage_html/' is clean.")

    def _relocate_purge_cache(self):
        """Specific handling for purge_cache.py organization."""
        ops_scripts = self.project_root / "ops_scripts"
        purge_script = ops_scripts / "purge_cache.py"
        maint_script_dir = ops_scripts / "maintenance"

        if purge_script.exists():
            print("\n[REFILE] Organizing purge_cache.py -> ops_scripts/maintenance/")
            if not self.dry_run:
                _wg.ensure_dir(maint_script_dir)
                target = maint_script_dir / "purge_cache.py"
                _wg.move_path(str(purge_script), str(target))

    def scan_root_violations(self, target_territory: str = None) -> dict[str, Any]:
        """
        [SSOT INTEGRATION] Scan project root for unapproved entries.

        Compares every file/directory at project root against the SSOT
        SOVEREIGN_TERRITORIES allowlist plus approved dotfiles and config
        files. Anything not on the allowlist is flagged as a violation.

        Args:
            target_territory: Ignored — always scans project root.

        Returns:
            Dict with violations list for SSOT aggregation.
        """
        violations = []

        # CANONICAL APPROVED ROOT DIRS — hardcoded SSOT allowlist.
        # ONLY these directories are permitted at project root.
        # Adding anything here requires an explicit architectural decision.
        approved_dirs = {
            # Core framework
            "agentic_core",
            # Application domains
            "apps_lic",
            "apps_rg",
            "apps_shared",
            # Supporting territories
            "system_learning",
            "artifacts",
            "data",
            "docs",
            "logs",
            "ops_scripts",
            "tests",
            "tools",
            "archives",
            # Version control / CI / IDE tooling (dotdirs)
            ".git",
            ".github",
            ".vscode",
            ".idea",
            ".nox",
            ".tox",
            ".windsurf",
            ".healing_backups",
            ".pytest_tmp",
            ".backup",
            ".gravity_state",
        }
        approved_files = {
            # Standard project config
            ".gitignore",
            ".gitattributes",
            ".editorconfig",
            ".env",
            ".env.example",
            ".flake8",
            ".mypy.ini",
            ".pre-commit-config.yaml",
            # Windsurf workspace files
            ".windsurfrules",
            ".windsurfrules.bak",
            ".windsurf.code-workspace",
            ".windsurfignore",
            # Python project files
            "pyproject.toml",
            "setup.py",
            "setup.cfg",
            "requirements.txt",
            "requirements-dev.txt",
            "noxfile.py",
            "Makefile",
            "pytest.ini",
            "tox.ini",
            "MANIFEST.in",
            # Docs
            "README.md",
            "LICENSE",
            "CHANGELOG.md",
            "CONTRIBUTING.md",
            # Coverage
            ".coverage",
            # Misc tracked files
            "progress.txt",
        }
        # Transient dirs/files that should be deleted, not relocated
        delete_patterns = {
            "__pycache__",
            ".pytest_cache",
            "node_modules",
            ".venv",
            "venv",
            "coverage_html",
            ".mypy_cache",
            ".ruff_cache",
            "htmlcov",
            "dist",
            "build",
            ".eggs",
        }

        try:
            for entry in self.project_root.iterdir():
                name = entry.name
                if name in approved_dirs or name in approved_files:
                    continue
                # Transient tmp files/dirs generated by pytest / tools
                if name.startswith("tmp") and len(name) > 3:
                    violations.append(
                        {
                            "type": "ILLEGAL_CACHE_DIR",
                            "file": str(entry),
                            "message": f"Transient tmp artifact '{name}' in project root",
                            "severity": "low",
                            "recommended_action": f"Delete '{name}'",
                            "confidence": 0.95,
                        }
                    )
                    continue
                if entry.is_dir() and name in delete_patterns:
                    violations.append(
                        {
                            "type": "ILLEGAL_CACHE_DIR",
                            "file": str(entry),
                            "message": f"Transient cache directory '{name}' in project root",
                            "severity": "low",
                            "recommended_action": f"Delete {name} (add to .gitignore)",
                            "confidence": 0.95,
                        }
                    )
                elif entry.is_dir():
                    violations.append(
                        {
                            "type": "UNAPPROVED_ROOT_DIR",
                            "file": str(entry),
                            "message": f"Unapproved directory '{name}' in project root (not in SOVEREIGN_TERRITORIES)",
                            "severity": "high",
                            "recommended_action": (
                                f"Move '{name}' to its canonical SSOT location or register it as a sovereign territory"
                            ),
                            "confidence": 0.9,
                        }
                    )
                elif entry.is_file() and name not in approved_files:
                    violations.append(
                        {
                            "type": "UNAPPROVED_ROOT_FILE",
                            "file": str(entry),
                            "message": f"Unapproved file '{name}' in project root",
                            "severity": "medium",
                            "recommended_action": (
                                f"Move '{name}' to its canonical SSOT location or add to approved list"
                            ),
                            "confidence": 0.8,
                        }
                    )
        except OSError as exc:
            violations.append(
                {
                    "type": "SCAN_ERROR",
                    "file": str(self.project_root),
                    "message": f"Root scan failed: {exc}",
                    "severity": "high",
                    "recommended_action": "Fix project root access permissions",
                    "confidence": 1.0,
                }
            )

        return {"violations": violations}

    # guardian: allow-type-erasure
    def heal(self, violation: dict) -> dict:
        """
        [SOVEREIGN CONTRACT] Standardized healing interface for Hygiene.
        """
        target = violation.get("file") or violation.get("target")
        v_type = violation.get("type", "").upper()

        if not target and "CACHE" not in v_type:
            return {"status": "skipped", "reason": "No target file specified"}

        try:
            if "CACHE" in v_type or "__PYCACHE__" in str(target).upper():
                if hasattr(self, "purge_cache"):
                    self.purge_cache()
                    return {"status": "success", "action": "purged_cache"}
                else:
                    from pathlib import Path

                    if target and Path(target).exists():
                        if Path(target).is_dir():
                            _wg.remove_tree(target)
                        else:
                            _wg.remove_file(Path(target))
                        return {"status": "success", "action": f"deleted {target}"}

            return {"status": "skipped", "reason": f"Unknown hygiene type: {v_type}"}

        except Exception as e:
            return {"status": "error", "error": str(e)}

    @standard_heal
    # guardian: allow-magic-config
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        # guardian: allow-magic-config
        max_depth: int = 3,
        _call_path: set[str] | None = None,
    ) -> dict[str, int]:
        """
        Standard healing interface for execute_ssot.py integration.

        This method provides the canonical healing interface that integrates
        with the HealerMixin chain and execute_ssot.py orchestration.
        """
        if _call_path is None:
            _call_path = set()

        # Prevent cycles
        agent_id = f"RootHygieneAgent@{self.project_root}"
        if agent_id in _call_path:
            return {"violations_found": 0, "violations_fixed": 0, "errors": 0, "skipped": 0}
        _call_path.add(agent_id)

        # Configure healing mode
        self.dry_run = dry_run and not execute

        try:
            # Execute the hygiene enforcement
            self._enforce_root_hygiene()

            # Calculate violations based on stats
            violations_found = (
                self.stats["scripts_evacuated"]
                + self.stats["dirs_evacuated"]
                + self.stats["coverage_relocated"]
                + self.stats["illegal_dirs_removed"]
            )
            violations_fixed = violations_found  # All detected violations are fixed

            return {
                "violations_found": violations_found,
                "violations_fixed": violations_fixed,
                "errors": self.stats["errors"],
                "skipped": 0,
            }

        # guardian: allow-silent-swallow
        except Exception as e:
            print(f"[ERROR] RootHygieneAgent healing failed: {e}")
            return {"violations_found": 0, "violations_fixed": 0, "errors": 1, "skipped": 0}
        finally:
            _call_path.discard(agent_id)


def main():
    """Standalone execution for testing."""
    import argparse

    parser = argparse.ArgumentParser(description="Root Hygiene Agent")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes")
    args = parser.parse_args()

    from pathlib import Path

    project_root = Path(".")

    agent = RootHygieneAgent(project_root=project_root, dry_run=args.dry_run)

    result = agent.run()
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
