"""Proper import test using the package hierarchy."""
import subprocess
import sys
from pathlib import Path

WAVE2_MODULES = [
    "agentic_core.config.constants_config",
    "agentic_core.L0_routing.config.path_constants",
    "agentic_core.L1_cognition.config.react_config",
    "agentic_core.L2_execution.config.hybrid_retriever_config",
    "agentic_core.L2_execution.config.provider_type_config",
    "agentic_core.L2_execution.config.strategist_bio_writer_config",
    "agentic_core.L3_orchestration.config.orchestrator_config",
    "agentic_core.L5_safety.config.structure_blueprint_config",
    "agentic_core.L5_safety.enforcement.error_recovery_guardrail",
    "agentic_core.utils.workflow_engines.completeness",
    "apps_lic.config.archetype_indicator_config",
    "apps_lic.config.loader_config",
    "apps_lic.config.reasoning_toggles_config",
    "apps_lic.config.retry_policy_config",
    "apps_lic.types.route_types",
    "apps_lic.utils.PIISanitizerSpecialistAgent_util",
    "apps_rg.config.agent_spec_config",
    "apps_rg.config.reasoning_toggles_config",
    "apps_rg.utils.authenticity_patterns_util",
    "apps_rg.validators.regeneration_validator",
    "apps_shared.config.environment_config",
    "apps_shared.config.operational_config",
    "apps_shared.config.routing_tier_config",
    "apps_shared.enforcement.FewshotregistryStrategy",
    "apps_shared.enforcement.HardenedeventbusStrategy",
    "apps_shared.enforcement.ProvenancetrackerStrategy",
    "apps_shared.reasoning.InfrastructureOrchestrator",
    "apps_shared.reasoning.InfrastructureUpgradesOrchestrator",
    "apps_shared.types.config_format_types",
    "apps_shared.types.config_type_types",
    "apps_shared.utils.config_environment_util",
    "apps_shared.utils.request_type_util",
    "agentic_core.L6_system_learning.config.config_store",
    "apps_shared.config.pipeline_constants_config",  # the SSOT
]


def main():
    fails = []
    for mod in WAVE2_MODULES:
        r = subprocess.run(
            [sys.executable, "-c", f"import {mod}; print('OK')"],
            capture_output=True, text=True, timeout=30, cwd=".",
        )
        if r.returncode != 0:
            fails.append((mod, r.stderr.strip()))
            err_lines = r.stderr.strip().splitlines()
            # Last error line
            last = next((ln for ln in reversed(err_lines)
                        if ln.strip() and not ln.startswith(' ') and "Error" in ln), err_lines[-1] if err_lines else "")
            print(f"  FAIL  {mod}")
            print(f"        {last[:200]}")
        else:
            print(f"  OK    {mod}")
    print(f"\nTotal: {len(fails)} failures / {len(WAVE2_MODULES)} modules")
    if fails:
        print("\n=== Full errors ===")
        for mod, err in fails[:5]:
            print(f"\n--- {mod} ---")
            for line in err.splitlines()[-10:]:
                print(f"  {line}")
    return len(fails)


if __name__ == "__main__":
    sys.exit(main())
