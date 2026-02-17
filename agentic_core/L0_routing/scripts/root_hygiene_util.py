"""
File: agentic_core/L0_routing/scripts/RootHygieneEnforcer.py
Path: agentic_core/L0_routing/scripts/RootHygieneEnforcer.py
Rationale:
    Actively enforces the new Root Hygiene laws defined in structure_blueprint.
    1. Moves root 'scripts/*' to 'ops_scripts/' (standalone) or 'L0_routing/scripts/' (core).
    2. Moves 'coverage_html' to 'reports/'.
    3. Deletes the illegal root directories after evacuation.
"""

import shutil
from pathlib import Path

from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write

# SSOT Constants
ROOT_MARKERS = ["agentic_core", "pyproject.toml"]


def get_project_root() -> Path:
    """Resolve project root securely."""
    current = Path.cwd()
    for marker in ROOT_MARKERS:
        if (current / marker).exists():
            return current
    raise RuntimeError("Must run from Project Root")


def enforce_root_hygiene():
    root = get_project_root()
    print(f"[HYGIENE] Enforcing Root Sovereignty at: {root}")
    print("=" * 60)

    # 1. EVACUATE ROOT SCRIPTS
    root_scripts = root / "scripts"
    ops_scripts = root / "ops_scripts"
    l0_scripts = root / "agentic_core" / "L0_routing" / "scripts"

    if root_scripts.exists():
        print("[DETECT] Illegal root 'scripts/' directory found.")
        ops_scripts.mkdir(exist_ok=True)
        l0_scripts.mkdir(exist_ok=True, parents=True)

        for item in root_scripts.iterdir():
            if item.is_file() and item.suffix == ".py":
                # Decision Logic: Does it import agentic_core?
                try:
                    content = item.read_text(encoding="utf-8")
                    if "agentic_core" in content or "from agentic_core" in content:
                        target = l0_scripts / item.name
                        action = "REPATRIATE (Core)"
                    else:
                        target = ops_scripts / item.name
                        action = "RELOCATE (Ops)"

                    print(f"  - {item.name} -> {action}")
                    assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
                    shutil.move(str(item), str(target))
                # guardian: allow-silent-swallow
                except Exception as e:
                    print(f"  [ERROR] Could not move {item.name}: {e}")

            elif item.is_dir():
                # Move entire subfolders to ops_scripts/maintenance or similar
                # For simplicity in this phase, dump to ops_scripts root or map specific folders
                target = ops_scripts / item.name
                print(f"  - DIR {item.name}/ -> RELOCATE (Ops)")
                if target.exists():
                    assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
                    shutil.rmtree(target)  # Force overwrite logic for dirs
                assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
                shutil.move(str(item), str(target))

        # Cleanup empty dir
        try:
            root_scripts.rmdir()
            print("[SUCCESS] Illegal 'scripts/' directory eliminated.")
        except OSError:
            print("[WARNING] 'scripts/' not empty, manual check required.")
    else:
        print("[CHECK] Root 'scripts/' is clean.")

    # 2. EVACUATE COVERAGE_HTML
    cov_html = root / "coverage_html"
    reports_cov = root / "reports" / "coverage_html"

    if cov_html.exists():
        print("\n[DETECT] Illegal root 'coverage_html/' found.")
        reports_cov.parent.mkdir(exist_ok=True)

        if reports_cov.exists():
            assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
            shutil.rmtree(reports_cov)

        print("  - Moving to reports/coverage_html")
        assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
        shutil.move(str(cov_html), str(reports_cov))
        print("[SUCCESS] Coverage report relocated.")
    else:
        print("[CHECK] Root 'coverage_html/' is clean.")

    # 3. RELOCATE PURGE_CACHE (Specific Request)
    # Checks if it ended up in ops_scripts during step 1, or needs specific handling
    purge_script = ops_scripts / "purge_cache.py"
    maint_script_dir = ops_scripts / "maintenance"
    if purge_script.exists():
        maint_script_dir.mkdir(exist_ok=True)
        target = maint_script_dir / "purge_cache.py"
        print("\n[REFILE] Organizing purge_cache.py -> ops_scripts/maintenance/")
        assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
        shutil.move(str(purge_script), str(target))


if __name__ == "__main__":
    enforce_root_hygiene()
