import pathlib
import shutil

BASE_DIR = pathlib.Path(__file__).parent.parent.parent


def execute_phase2():
    """Phase 2: MEDIUM Risk Migration - 5 files"""

    migrations = [
        (
            "ops_scripts/test_batch_performance_optimization.py",
            "tests/e2e/ops_scripts/test_batch_performance_optimization.py",
        ),
        (
            "ops_scripts/test_location_agent_telemetry.py",
            "tests/e2e/ops_scripts/test_location_agent_telemetry.py",
        ),
        (
            "ops_scripts/test_mission_script_integrity.py",
            "tests/e2e/ops_scripts/test_mission_script_integrity.py",
        ),
        ("ops_scripts/test_phase1_interface.py", "tests/e2e/ops_scripts/test_phase1_interface.py"),
        ("ops_scripts/test_phase2_interface.py", "tests/e2e/ops_scripts/test_phase2_interface.py"),
    ]

    for src_rel, dest_rel in migrations:
        src = BASE_DIR / src_rel
        dest = BASE_DIR / dest_rel

        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dest))
        print(f"✅ Moved: {src_rel} → {dest_rel}")

    return True


if __name__ == "__main__":
    execute_phase2()
