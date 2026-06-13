"""Surgically stage only the audit-uncovered-gates plan files for commit."""
import subprocess
from pathlib import Path

# Wave 2 — SSOT magic constant consolidation (45 files)
WAVE2 = [
    "agentic_core/L0_routing/config/path_constants.py",
    "agentic_core/L1_cognition/config/react_config.py",
    "agentic_core/L2_execution/config/hybrid_retriever_config.py",
    "agentic_core/L2_execution/config/provider_type_config.py",
    "agentic_core/L2_execution/config/strategist_bio_writer_config.py",
    "agentic_core/L3_orchestration/config/orchestrator_config.py",
    "agentic_core/L5_safety/config/structure_blueprint_config.py",
    "agentic_core/L5_safety/enforcement/error_recovery_guardrail.py",
    "agentic_core/config/constants_config.py",
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

# Wave 3 — NOTION literal SSOT
WAVE3 = [
    "docs/archive/windsurf/legacy-tree/governance_scripts/plan_driven_closer.py",
    "docs/archive/windsurf/legacy-tree/governance_scripts/post_agent_adr_registry_capture.py",
    "docs/archive/windsurf/legacy-tree/governance_scripts/post_agent_deferred_scope_capture.py",
    "docs/archive/windsurf/legacy-tree/governance_scripts/post_agent_next_step_capture.py",
    "docs/archive/windsurf/legacy-tree/governance_scripts/post_commit_phase_closer.py",
    "docs/archive/windsurf/legacy-tree/governance_scripts/rollback_bad_patches.py",
    "ops_scripts/ci/check_notion_plan_file_drift.py",
    "tools/reports/recover_deferred_scope_pendings.py",
]

# Wave 5 — pre-commit wiring
WAVE5 = [".pre-commit-config.yaml"]

# Wave B — observability hook for human_approval_adapter
WAVEB = ["agentic_core/L5_safety/adapters/human_approval_adapter.py"]

# Untracked: plan, SSOT, gates, baselines, tests, triage, analysis tools
UNTRACKED = [
    "docs/archive/windsurf/legacy-tree/plans/audit-uncovered-gates-and-remediation-627368.md",
    "docs/archive/windsurf/legacy-tree/governance_scripts/_notion_constants.py",
    "ops_scripts/ci/check_ssot_magic_constants.py",
    "ops_scripts/ci/check_observability_on_high_fanin.py",
    "ops_scripts/ci/check_external_service_literal_ssot.py",
    "ops_scripts/ci/check_cross_mainline_dispatcher.py",
    "ops_scripts/ci/check_env_var_in_config_layer.py",
    "ops_scripts/ci/check_violation_aging_sla.py",
    "ops_scripts/ci/baselines/audit_ssot_magic_constants.json",
    "ops_scripts/ci/baselines/audit_observability_high_fanin.json",
    "ops_scripts/ci/baselines/audit_external_service_literal_ssot.json",
    "ops_scripts/ci/baselines/audit_cross_mainline_dispatcher.json",
    "ops_scripts/ci/baselines/audit_env_var_in_config_layer.json",
    "ops_scripts/ci/baselines/audit_violation_aging_sla.json",
    "tests/unit/ops_scripts/ci/test_audit_gates.py",
    "docs/reports/audit_6_disposition_triage.csv",
]

ALL = WAVE2 + WAVE3 + WAVE5 + WAVEB + UNTRACKED

# Verify each exists
missing = [f for f in ALL if not Path(f).exists()]
if missing:
    print("MISSING FILES (will be skipped):")
    for f in missing:
        print(f"  {f}")

# Stage
to_stage = [f for f in ALL if Path(f).exists()]
print(f"\nStaging {len(to_stage)} files...")
r = subprocess.run(["git", "add", "--", *to_stage], capture_output=True, text=True, timeout=60)
print(f"git add: exit={r.returncode}")
if r.stderr:
    print(r.stderr)

# Show summary
r2 = subprocess.run(["git", "diff", "--cached", "--stat"], capture_output=True, text=True, timeout=30)
# Print last line (summary) and total count
lines = r2.stdout.splitlines()
print(f"\nStaged: {len(lines)-1} files")
if lines:
    print(lines[-1])
