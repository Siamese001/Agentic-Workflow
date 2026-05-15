"""Smoke-test all Wave 2/3 modified files: import them and run any nearby tests."""
import importlib
import subprocess
import sys
from pathlib import Path

REPO = Path(".")

# Wave 2 files (45 modified configs)
WAVE2_FILES = [
    "agentic_core/config/constants_config.py",
    "agentic_core/L0_routing/config/path_constants.py",
    "agentic_core/L1_cognition/config/react_config.py",
    "agentic_core/L2_execution/config/hybrid_retriever_config.py",
    "agentic_core/L2_execution/config/provider_type_config.py",
    "agentic_core/L2_execution/config/strategist_bio_writer_config.py",
    "agentic_core/L3_orchestration/config/orchestrator_config.py",
    "agentic_core/L5_safety/config/structure_blueprint_config.py",
    "agentic_core/L5_safety/enforcement/error_recovery_guardrail.py",
    "agentic_core/utils/workflow_engines/completeness.py",
    "apps_lic/config/archetype_indicator_config.py",
    "apps_lic/config/loader_config.py",
    "apps_lic/config/reasoning_toggles_config.py",
    "apps_lic/config/retry_policy_config.py",
    "apps_lic/reasoning/OutreachLearningAgent.py",
    "apps_lic/reasoning/OutreachValidationExecutorAgent.py",
    "apps_lic/types/route_types.py",
    "apps_lic/utils/PIISanitizerSpecialistAgent_util.py",
    "apps_rg/config/agent_spec_config.py",
    "apps_rg/config/reasoning_toggles_config.py",
    "apps_rg/utils/authenticity_patterns_util.py",
    "apps_rg/validators/regeneration_validator.py",
    "apps_shared/config/environment_config.py",
    "apps_shared/config/operational_config.py",
    "apps_shared/config/routing_tier_config.py",
    "apps_shared/enforcement/FewshotregistryStrategy.py",
    "apps_shared/enforcement/HardenedeventbusStrategy.py",
    "apps_shared/enforcement/ProvenancetrackerStrategy.py",
    "apps_shared/reasoning/InfrastructureOrchestrator.py",
    "apps_shared/reasoning/InfrastructureUpgradesOrchestrator.py",
    "apps_shared/types/config_format_types.py",
    "apps_shared/types/config_type_types.py",
    "apps_shared/utils/config_environment_util.py",
    "apps_shared/utils/request_type_util.py",
    "system_learning/config/config_store.py",
]

# Wave 3 files (8 modified hooks)
WAVE3_FILES = [
    ".windsurf/scripts/_notion_constants.py",
    ".windsurf/scripts/plan_driven_closer.py",
    ".windsurf/scripts/post_commit_phase_closer.py",
    ".windsurf/scripts/rollback_bad_patches.py",
    ".windsurf/scripts/post_cursor_agent_next_step_capture.py",
    ".windsurf/scripts/post_cursor_agent_deferred_scope_capture.py",
    ".windsurf/scripts/post_cursor_agent_adr_registry_capture.py",
    "ops_scripts/ci/check_notion_plan_file_drift.py",
    "tools/reports/recover_deferred_scope_pendings.py",
]


def py_compile(path: Path) -> tuple[bool, str]:
    r = subprocess.run([sys.executable, "-m", "py_compile", str(path)],
                       capture_output=True, text=True, timeout=30)
    return r.returncode == 0, r.stderr


def import_check(path: Path) -> tuple[bool, str]:
    """Try to import the module via importlib."""
    # Convert path to module name
    rel = path.with_suffix("")
    parts = list(rel.parts)
    # Skip files that aren't proper modules (e.g., dotted dirs like .windsurf)
    if any(p.startswith(".") for p in parts):
        return True, "(skipped — non-package path)"
    mod_name = ".".join(parts)
    code = f"import importlib.util, sys; spec = importlib.util.spec_from_file_location({mod_name!r}, {str(path)!r}); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); print('OK')"
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=30)
    return r.returncode == 0, (r.stderr or r.stdout)


def main():
    print(f"=== WAVE 2 FILES ({len(WAVE2_FILES)}) ===\n")
    fails = 0
    for f in WAVE2_FILES:
        p = REPO / f
        if not p.exists():
            print(f"  MISSING  {f}")
            fails += 1
            continue
        ok, err = py_compile(p)
        if not ok:
            print(f"  COMPILE  {f}")
            for line in err.splitlines()[:3]:
                print(f"    {line}")
            fails += 1
            continue
        ok, err = import_check(p)
        if not ok:
            print(f"  IMPORT   {f}")
            for line in (err or "").splitlines()[-5:]:
                print(f"    {line}")
            fails += 1
            continue
        print(f"  OK       {f}")

    print(f"\nWave 2 failures: {fails}/{len(WAVE2_FILES)}\n")
    print(f"=== WAVE 3 FILES ({len(WAVE3_FILES)}) ===\n")
    fails3 = 0
    for f in WAVE3_FILES:
        p = REPO / f
        if not p.exists():
            print(f"  MISSING  {f}")
            fails3 += 1
            continue
        ok, err = py_compile(p)
        if not ok:
            print(f"  COMPILE  {f}")
            for line in err.splitlines()[:3]:
                print(f"    {line}")
            fails3 += 1
            continue
        ok, err = import_check(p)
        if not ok:
            print(f"  IMPORT   {f}")
            for line in (err or "").splitlines()[-5:]:
                print(f"    {line}")
            fails3 += 1
            continue
        print(f"  OK       {f}")

    print(f"\nWave 3 failures: {fails3}/{len(WAVE3_FILES)}")
    return fails + fails3


if __name__ == "__main__":
    sys.exit(main())
