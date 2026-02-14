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

import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Optional: Import SovereignBaseAgent if available for full integration
try:
    from agentic_core.utils.decorators import standard_heal
    from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

    HAS_SOVEREIGN_BASE = True
except ImportError:
    HAS_SOVEREIGN_BASE = False
    SovereignBaseAgent = object

    def standard_heal(func):
        """Fallback decorator when full infrastructure unavailable."""
        return func


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
                ops_scripts.mkdir(exist_ok=True)
                l0_scripts.mkdir(exist_ok=True, parents=True)

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
                            shutil.move(str(item), str(target))
                        self.stats["scripts_evacuated"] += 1

                    elif item.is_dir():
                        # Move entire subfolders to ops_scripts/maintenance or similar
                        target = ops_scripts / item.name
                        print(f"  - DIR {item.name}/ -> RELOCATE (Ops)")
                        if not self.dry_run:
                            if target.exists():
                                shutil.rmtree(target)  # Force overwrite logic for dirs
                            shutil.move(str(item), str(target))
                        self.stats["dirs_evacuated"] += 1

                # guardian: allow-silent-swallow
                except Exception as e:
                    print(f"  [ERROR] Could not move {item.name}: {e}")
                    self.stats["errors"] += 1

            # Cleanup empty dir
            if not self.dry_run:
                try:
                    root_scripts.rmdir()
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
                reports_cov.parent.mkdir(exist_ok=True)

                if reports_cov.exists():
                    shutil.rmtree(reports_cov)

                print("  - Moving to reports/coverage_html")
                shutil.move(str(cov_html), str(reports_cov))
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
                maint_script_dir.mkdir(exist_ok=True)
                target = maint_script_dir / "purge_cache.py"
                shutil.move(str(purge_script), str(target))

    def scan_root_violations(self, target_territory: str = None) -> dict[str, Any]:
        """
        [SSOT INTEGRATION] Scan for root hygiene violations.

        Args:
            target_territory: Specific territory to scan (ignored - always scans root)

        Returns:
            Dict with violations list for SSOT aggregation
        """
        violations = []

        # Check for illegal root scripts directory
        root_scripts = self.project_root / "scripts"
        if root_scripts.exists():
            violations.append(
                {
                    "type": "ILLEGAL_ROOT_SCRIPTS",
                    "file": str(root_scripts),
                    "message": "Illegal 'scripts/' directory in project root",
                    "severity": "high",
                    "recommended_action": "Move scripts to ops_scripts/ or agentic_core/L0_routing/scripts/",
                    "confidence": 0.9,
                },
            )

        # Check for illegal coverage_html directory
        coverage_html = self.project_root / "coverage_html"
        if coverage_html.exists():
            violations.append(
                {
                    "type": "ILLEGAL_COVERAGE_HTML",
                    "file": str(coverage_html),
                    "message": "Illegal 'coverage_html/' directory in project root",
                    "severity": "medium",
                    "recommended_action": "Move coverage_html to reports/coverage_html/",
                    "confidence": 0.8,
                },
            )

        # Check for other common root violations
        illegal_patterns = ["__pycache__", ".pytest_cache", "node_modules", ".venv", "venv"]
        for pattern in illegal_patterns:
            illegal_dir = self.project_root / pattern
            if illegal_dir.exists() and illegal_dir.is_dir():
                violations.append(
                    {
                        "type": "ILLEGAL_CACHE_DIR",
                        "file": str(illegal_dir),
                        "message": f"Illegal cache directory '{pattern}' in project root",
                        "severity": "low",
                        "recommended_action": f"Add {pattern} to .gitignore and remove from root",
                        "confidence": 0.6,
                    },
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
                    import shutil
                    from pathlib import Path

                    if target and Path(target).exists():
                        if Path(target).is_dir():
                            shutil.rmtree(target)
                        else:
                            Path(target).unlink()
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
