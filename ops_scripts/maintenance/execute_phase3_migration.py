import pathlib
import shutil

BASE_DIR = pathlib.Path(__file__).parent.parent.parent


def execute_phase3():
    """Phase 3: HIGH Risk Migration Batch 1 - 10 files"""

    migrations = [
        (
            "ops_scripts/test_autonomous_decision_making.py",
            "tests/e2e/ops_scripts/test_autonomous_decision_making.py",
        ),
        (
            "ops_scripts/test_autonomous_end_to_end.py",
            "tests/e2e/ops_scripts/test_autonomous_end_to_end.py",
        ),
        (
            "ops_scripts/test_complete_mission_workflow.py",
            "tests/e2e/ops_scripts/test_complete_mission_workflow.py",
        ),
        (
            "ops_scripts/test_hop2_sovereign_strategist.py",
            "tests/e2e/ops_scripts/test_hop2_sovereign_strategist.py",
        ),
        (
            "ops_scripts/test_hop3_hop4_hop5_foundation.py",
            "tests/e2e/ops_scripts/test_hop3_hop4_hop5_foundation.py",
        ),
        (
            "ops_scripts/test_hop6_hop7_crucible_governor.py",
            "tests/e2e/ops_scripts/test_hop6_hop7_crucible_governor.py",
        ),
        (
            "ops_scripts/test_hop8_hop9_persistence_handoff.py",
            "tests/e2e/ops_scripts/test_hop8_hop9_persistence_handoff.py",
        ),
        (
            "ops_scripts/test_hop_orchestrator_master.py",
            "tests/e2e/ops_scripts/test_hop_orchestrator_master.py",
        ),
        ("ops_scripts/test_lic_rg_parity.py", "tests/e2e/ops_scripts/test_lic_rg_parity.py"),
        (
            "ops_scripts/test_master_verification_simulation.py",
            "tests/e2e/ops_scripts/test_master_verification_simulation.py",
        ),
    ]

    for src_rel, dest_rel in migrations:
        src = BASE_DIR / src_rel
        dest = BASE_DIR / dest_rel

        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dest))
        print(f"✅ Moved: {src_rel} → {dest_rel}")

    return True


if __name__ == "__main__":
    execute_phase3()
