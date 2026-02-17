
$ uname -a
Linux Agentic01 6.6.87.2-microsoft-standard-WSL2 #1 SMP PREEMPT_DYNAMIC Thu Jun  5 18:30:46 UTC 2025 x86_64 x86_64 x86_64 GNU/Linux

$ echo /bin/bash
/bin/bash

$ pwd
/mnt/c/Git/Agentic-Workflow

$ which python3
/usr/bin/python3

$ python3 --version
Python 3.12.3

$ git --version
git version 2.43.0

$ git rev-parse --show-toplevel
/mnt/c/Git/Agentic-Workflow

$ git status
On branch gravity-healing
Your branch and 'origin/gravity-healing' have diverged,
and have 1 and 1 different commits each, respectively.
  (use "git pull" if you want to integrate the remote branch with yours)

All conflicts fixed but you are still merging.
  (use "git commit" to conclude merge)

Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   agentic_core/L0_routing/utils/subprocess_runner.py

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	.tmp/
	agentic_core/L5_safety/runners/reasoning_runner.py
	docs/reports/environment/
	docs/reports/guardian/phase14_reasoning_namespace_elimination.md


$ git rev-parse HEAD
47a883f1803035c4fd9d715832aa8990fcdbbcbc

$ git config --get core.autocrlf
false

$ python3 -
WSL Python execution OK

$ python3 -m agentic_core.L0_routing.scripts.run_all_guardians --format json
{
  "artifact_class": "aggregate",
  "artifacts": [],
  "certification_hash": "b1e7803a59283669486882f32209207cf51773c807a536933600b6dd571c2da0",
  "checks": [
    {
      "check_id": "guardian_architecture_governance",
      "details": "Architecture governance: 1/2 checks failed (1077 files scanned)",
      "evidence": {
        "check_count": 2,
        "checks": [
          {
            "check_id": "import_compliance",
            "details": "94 upward import violation(s) detected",
            "evidence": {
              "violation_count": 94,
              "violations": [
                {
                  "import_line": "from agentic_core.L2_execution.enforcement.healer_pipe_order import ...",
                  "line_number": 54,
                  "path": "agentic_core/L0_routing/enforcement/v15_execution_gateway.py",
                  "source_layer": "L0",
                  "target_layer": "L2"
                },
                {
                  "import_line": "from agentic_core.L6_observability.types.vigilance_event_types import ...",
                  "line_number": 16,
                  "path": "agentic_core/L0_routing/enforcement/vigilance_routing.py",
                  "source_layer": "L0",
                  "target_layer": "L6"
                },
                {
                  "import_line": "from agentic_core.L2_execution.types.capability_token_types import ...",
                  "line_number": 29,
                  "path": "agentic_core/L0_routing/meta_control/meta_apply.py",
                  "source_layer": "L0",
                  "target_layer": "L2"
                },
                {
                  "import_line": "from agentic_core.L5_safety.reasoning.CognitiveDispositionAgent import ...",
                  "line_number": 158,
                  "path": "agentic_core/L0_routing/reasoning/SSOTFolderCleanupAgent.py",
                  "source_layer": "L0",
                  "target_layer": "L5"
                },
                {
                  "import_line": "from agentic_core.L5_safety.enforcement.archival_gatekeeper import ...",
                  "line_number": 172,
                  "path": "agentic_core/L0_routing/reasoning/SSOTFolderCleanupAgent.py",
                  "source_layer": "L0",
                  "target_layer": "L5"
                },
                {
                  "import_line": "from agentic_core.L5_safety.reasoning.FileClassificationAgent import ...",
                  "line_number": 284,
                  "path": "agentic_core/L0_routing/reasoning/SSOTFolderCleanupAgent.py",
                  "source_layer": "L0",
                  "target_layer": "L5"
                },
                {
                  "import_line": "from agentic_core.L5_safety.enforcement.CodeDeduplicationAgent import ...",
                  "line_number": 30,
                  "path": "agentic_core/L0_routing/scripts/agent_validation_util.py",
                  "source_layer": "L0",
                  "target_layer": "L5"
                },
                {
                  "import_line": "from agentic_core.L5_safety.validators.AutonomyGuardianAgent import ...",
                  "line_number": 469,
                  "path": "agentic_core/L0_routing/scripts/colors.py",
                  "source_layer": "L0",
                  "target_layer": "L5"
                },
                {
                  "import_line": "from agentic_core.L3_orchestration.Orchestrator import ...",
                  "line_number": 592,
                  "path": "agentic_core/L0_routing/scripts/colors.py",
                  "source_layer": "L0",
                  "target_layer": "L3"
                },
                {
                  "import_line": "from agentic_core.L5_safety.validators.healing_strategy import ...",
                  "line_number": 593,
                  "path": "agentic_core/L0_routing/scripts/colors.py",
                  "source_layer": "L0",
                  "target_layer": "L5"
                },
                {
                  "import_line": "from agentic_core.L3_orchestration.Orchestrator import ...",
                  "line_number": 667,
                  "path": "agentic_core/L0_routing/scripts/colors.py",
                  "source_layer": "L0",
                  "target_layer": "L3"
                },
                {
                  "import_line": "from agentic_core.L4_state.reasoning.CheckpointManagerAgent import ...",
                  "line_number": 670,
                  "path": "agentic_core/L0_routing/scripts/colors.py",
                  "source_layer": "L0",
                  "target_layer": "L4"
                },
                {
                  "import_line": "from agentic_core.L5_safety.validators.healing_strategy import ...",
                  "line_number": 673,
                  "path": "agentic_core/L0_routing/scripts/colors.py",
                  "source_layer": "L0",
                  "target_layer": "L5"
                },
                {
                  "import_line": "from agentic_core.L5_safety.validators.AutonomyGuardianAgent import ...",
                  "line_number": 728,
                  "path": "agentic_core/L0_routing/scripts/colors.py",
                  "source_layer": "L0",
                  "target_layer": "L5"
                },
                {
                  "import_line": "from agentic_core.L3_orchestration.reasoning.mission_controller_convergence import ...",
                  "line_number": 85,
                  "path": "agentic_core/L0_routing/scripts/coverage.py",
                  "source_layer": "L0",
                  "target_layer": "L3"
                },
                {
                  "import_line": "from agentic_core.L5_safety.validators.CognitiveDispositionAgent import ...",
                  "line_number": 613,
                  "path": "agentic_core/L0_routing/scripts/execute_ssot.py",
                  "source_layer": "L0",
                  "target_layer": "L5"
                },
                {
                  "import_line": "from agentic_core.L3_orchestration.reasoning.subatomic_testing_mixin import ...",
                  "line_number": 18,
                  "path": "agentic_core/L0_routing/scripts/execution_context.py",
                  "source_layer": "L0",
                  "target_layer": "L3"
                },
                {
                  "import_line": "from agentic_core.L3_orchestration.reasoning.forward_rolling_config_types import ...",
                  "line_number": 22,
                  "path": "agentic_core/L0_routing/scripts/forward_rolling_facade.py",
                  "source_layer": "L0",
                  "target_layer": "L3"
                },
                {
                  "import_line": "from agentic_core.L3_orchestration.reasoning.recursion_monitor_types import ...",
                  "line_number": 27,
                  "path": "agentic_core/L0_routing/scripts/forward_rolling_facade.py",
                  "source_layer": "L0",
                  "target_layer": "L3"
                },
                {
                  "import_line": "from agentic_core.L3_orchestration.reasoning.recursive_orchestration_types import ...",
                  "line_number": 31,
                  "path": "agentic_core/L0_routing/scripts/forward_rolling_facade.py",
                  "source_layer": "L0",
                  "target_layer": "L3"
                },
                {
                  "import_line": "from agentic_core.L3_orchestration.types import ...",
                  "line_number": 35,
                  "path": "agentic_core/L0_routing/scripts/forward_rolling_facade.py",
                  "source_layer": "L0",
                  "target_layer": "L3"
                },
                {
                  "import_line": "from agentic_core.L3_orchestration.types.context_pruning_types import ...",
                  "line_number": 40,
                  "path": "agentic_core/L0_routing/scripts/forward_rolling_facade.py",
                  "source_layer": "L0",
                  "target_layer": "L3"
                },
                {
                  "import_line": "from agentic_core.L5_safety.core_kernel.classification_kernel import ...",
                  "line_number": 58,
                  "path": "agentic_core/L0_routing/scripts/full_agent_discovery.py",
                  "source_layer": "L0",
                  "target_layer": "L5"
                },
                {
                  "import_line": "from agentic_core.L5_safety.core_kernel.classification_kernel import ...",
                  "line_number": 211,
                  "path": "agentic_core/L0_routing/scripts/full_agent_discovery.py",
                  "source_layer": "L0",
                  "target_layer": "L5"
                },
                {
                  "import_line": "from agentic_core.L1_cognition.P2_domain.context import ...",
                  "line_number": 21,
                  "path": "agentic_core/L0_routing/scripts/hardened_orchestrator_wrapper_util.py",
                  "source_layer": "L0",
                  "target_layer": "L1"
                },
                {
                  "import_line": "from agentic_core.L2_execution.scripts.remediation_dispatcher import ...",
                  "line_number": 82,
                  "path": "agentic_core/L0_routing/scripts/l0_execute.py",
                  "source_layer": "L0",
                  "target_layer": "L2"
                },
                {
                  "import_line": "from agentic_core.L5_safety.enforcement.ssot_scanner import ...",
                  "line_number": 183,
                  "path": "agentic_core/L0_routing/scripts/run_guardian_architecture_governance.py",
                  "source_layer": "L0",
                  "target_layer": "L5"
                },
                {
                  "import_line": "from agentic_core.L5_safety.core_kernel.classification_kernel import ...",
                  "line_number": 161,
                  "path": "agentic_core/L0_routing/scripts/run_guardian_classification_compliance.py",
                  "source_layer": "L0",
                  "target_layer": "L5"
                },
                {
                  "import_line": "from agentic_core.L5_safety.validators.HygieneGuardianAgent import ...",
                  "line_number": 15,
                  "path": "agentic_core/L0_routing/scripts/run_hygiene_naming_audit_util.py",
                  "source_layer": "L0",
                  "target_layer": "L5"
                },
                {
                  "import_line": "from agentic_core.L5_safety.reasoning.NamingAgent import ...",
                  "line_number": 13,
                  "path": "agentic_core/L0_routing/scripts/run_naming_law_check_util.py",
                  "source_layer": "L0",
                  "target_layer": "L5"
                },
                {
                  "import_line": "from agentic_core.L5_safety.reasoning.NamingAgent import ...",
                  "line_number": 14,
                  "path": "agentic_core/L0_routing/scripts/run_naming_scan_util.py",
                  "source_layer": "L0",
                  "target_layer": "L5"
                },
                {
                  "import_line": "from agentic_core.L5_safety.reasoning.StructureEnforcerAgent import ...",
                  "line_number": 18,
                  "path": "agentic_core/L0_routing/scripts/run_sovereign_compliance_audit_util.py",
                  "source_layer": "L0",
                  "target_layer": "L5"
                },
                {
                  "import_line": "from agentic_core.L5_safety.validators.canonical_truth_validator import ...",
                  "line_number": 28,
                  "path": "agentic_core/L0_routing/scripts/scan_testing_compliance_util.py",
                  "source_layer": "L0",
                  "target_layer": "L5"
                },
                {
                  "import_line": "from agentic_core.L5_safety.validators.canonical_truth_validator import ...",
                  "line_number": 19,
                  "path": "agentic_core/L0_routing/scripts/ssot_audit_util.py",
                  "source_layer": "L0",
                  "target_layer": "L5"
                },
                {
                  "import_line": "from agentic_core.L6_observability.meta_learning.MetaLearningAgent import ...",
                  "line_number": 67,
                  "path": "agentic_core/L0_routing/scripts/verify_mro_util.py",
                  "source_layer": "L0",
                  "target_layer": "L6"
                },
                {
                  "import_line": "from agentic_core.L5_safety.reasoning.LocationValidatorAgent import ...",
                  "line_number": 78,
                  "path": "agentic_core/L0_routing/scripts/verify_mro_util.py",
                  "source_layer": "L0",
                  "target_layer": "L5"
                },
                {
                  "import_line": "from agentic_core.L5_safety.enforcement.artifact_emission_prohibition import ...",
                  "line_number": 20,
                  "path": "agentic_core/L0_routing/types/v15_types.py",
                  "source_layer": "L0",
                  "target_layer": "L5"
                },
                {
                  "import_line": "from agentic_core.L5_safety.validators.dashboard_ssot_definitions_config import ...",
                  "line_number": 66,
                  "path": "agentic_core/L0_routing/utils/complexity_visitor_util.py",
                  "source_layer": "L0",
                  "target_layer": "L5"
                },
                {
                  "import_line": "from agentic_core.L5_safety.utils.canonical_truth_util import ...",
                  "line_number": 113,
                  "path": "agentic_core/L0_routing/utils/complexity_visitor_util.py",
                  "source_layer": "L0",
                  "target_layer": "L5"
                },
                {
                  "import_line": "from agentic_core.L5_safety.core_kernel.classification_kernel import ...",
                  "line_number": 1119,
                  "path": "agentic_core/L0_routing/utils/complexity_visitor_util.py",
                  "source_layer": "L0",
                  "target_layer": "L5"
                },
                {
                  "import_line": "from agentic_core.L5_safety.reasoning.verification_gate_adapter import ...",
                  "line_number": 53,
                  "path": "agentic_core/L0_routing/utils/component_util.py",
                  "source_layer": "L0",
                  "target_layer": "L5"
                },
                {
                  "import_line": "from agentic_core.L5_safety.reasoning.human_review_adapter import ...",
                  "line_number": 92,
                  "path": "agentic_core/L0_routing/utils/component_util.py",
                  "source_layer": "L0",
                  "target_layer": "L5"
                },
                {
                  "import_line": "from agentic_core.L3_orchestration.engines.action_router import ...",
                  "line_number": 19,
                  "path": "agentic_core/L1_cognition/engines/cognitive_engine.py",
                  "source_layer": "L1",
                  "target_layer": "L3"
                },
                {
                  "import_line": "from agentic_core.L2_execution.reasoning.EmbeddingSovereignAgent import ...",
                  "line_number": 88,
                  "path": "agentic_core/L1_cognition/engines/memory_embedder.py",
                  "source_layer": "L1",
                  "target_layer": "L2"
                },
                {
                  "import_line": "from agentic_core.L4_state.reasoning.RedisSovereignAgent import ...",
                  "line_number": 125,
                  "path": "agentic_core/L1_cognition/engines/meta_client.py",
                  "source_layer": "L1",
                  "target_layer": "L4"
                },
                {
                  "import_line": "from agentic_core.L4_state.reasoning.PineconeSovereignAgent import ...",
                  "line_number": 141,
                  "path": "agentic_core/L1_cognition/engines/meta_client.py",
                  "source_layer": "L1",
                  "target_layer": "L4"
                },
                {
                  "import_line": "from agentic_core.L2_execution.reasoning.EmbeddingSovereignAgent import ...",
                  "line_number": 429,
                  "path": "agentic_core/L1_cognition/engines/meta_client.py",
                  "source_layer": "L1",
                  "target_layer": "L2"
                },
                {
                  "import_line": "from agentic_core.L5_safety.validators.unified_cst_healer import ...",
                  "line_number": 370,
                  "path": "agentic_core/L1_cognition/reasoning/ASTValidatorAgent.py",
                  "source_layer": "L1",
                  "target_layer": "L5"
                },
                {
                  "import_line": "from agentic_core.L5_safety.enforcement.activation_gate import ...",
                  "line_number": 27,
                  "path": "agentic_core/L2_execution/config/unified_workflow_config.py",
                  "source_layer": "L2",
                  "target_layer": "L5"
                },
                {
                  "import_line": "from agentic_core.L5_safety.enforcement.activation_gate import ...",
                  "line_number": 29,
                  "path": "agentic_core/L2_execution/enforcement/dashboard_e2_e_pipeline.py",
                  "source_layer": "L2",
                  "target_layer": "L5"
                },
                {
                  "import_line": "from agentic_core.L5_safety.enforcement.activation_gate import ...",
                  "line_number": 29,
                  "path": "agentic_core/L2_execution/enforcement/dashboard_e2_e_pipeline_enforcer.py",
                  "source_layer": "L2",
                  "target_layer": "L5"
                },
                {
                  "import_line": "from agentic_core.L3_orchestration.reasoning.mcp_manager import ...",
                  "line_number": 12,
                  "path": "agentic_core/L2_execution/enforcement/sovereign_filesystem_mcp.py",
                  "source_layer": "L2",
                  "target_layer": "L3"
                },
                {
                  "import_line": "from agentic_core.L3_orchestration.reasoning.mcp_manager import ...",
                  "line_number": 12,
                  "path": "agentic_core/L2_execution/enforcement/sovereign_filesystem_mcp_enforcer.py",
                  "source_layer": "L2",
                  "target_layer": "L3"
                },
                {
                  "import_line": "from agentic_core.L4_state.reasoning.PineconeSovereignAgent import ...",
                  "line_number": 30,
                  "path": "agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py",
                  "source_layer": "L2",
                  "target_layer": "L4"
                },
                {
                  "import_line": "from agentic_core.L4_state.reasoning.RedisSovereignAgent import ...",
                  "line_number": 33,
                  "path": "agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py",
                  "source_layer": "L2",
                  "target_layer": "L4"
                },
                {
                  "import_line": "from agentic_core.L5_safety.reasoning.StructureValidatorAgent import ...",
                  "line_number": 54,
                  "path": "agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py",
                  "source_layer": "L2",
                  "target_layer": "L5"
                },
                {
                  "import_line": "from agentic_core.L3_orchestration.reasoning.StateManagementAgent import ...",
                  "line_number": 61,
                  "path": "agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py",
                  "source_layer": "L2",
                  "target_layer": "L3"
                },
                {
                  "import_line": "from agentic_core.L4_state.reasoning.CheckpointManagerAgent import ...",
                  "line_number": 64,
                  "path": "agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py",
                  "source_layer": "L2",
                  "target_layer": "L4"
                },
                {
                  "import_line": "from agentic_core.L5_safety.reasoning.CodeEnforcerAgent import ...",
                  "line_number": 67,
                  "path": "agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py",
                  "source_layer": "L2",
                  "target_layer": "L5"
                },
                {
                  "import_line": "from agentic_core.L5_safety.reasoning.CodeEnforcerAgent import ...",
                  "line_number": 115,
                  "path": "agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py",
                  "source_layer": "L2",
                  "target_layer": "L5"
                },
                {
                  "import_line": "from agentic_core.L5_safety.reasoning.ResourceManagerAgent import ...",
                  "line_number": 116,
                  "path": "agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py",
                  "source_layer": "L2",
                  "target_layer": "L5"
                },
                {
                  "import_line": "from agentic_core.L5_safety.reasoning.SecurityManagerAgent import ...",
                  "line_number": 119,
                  "path": "agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py",
                  "source_layer": "L2",
                  "target_layer": "L5"
                },
                {
                  "import_line": "from agentic_core.L5_safety.reasoning.StructureEnforcerAgent import ...",
                  "line_number": 122,
                  "path": "agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py",
                  "source_layer": "L2",
                  "target_layer": "L5"
                },
                {
                  "import_line": "from agentic_core.L5_safety.reasoning.StructureHealerAgent_types import ...",
                  "line_number": 160,
                  "path": "agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py",
                  "source_layer": "L2",
                  "target_layer": "L5"
                },
                {
                  "import_line": "from agentic_core.L5_safety.reasoning.CodeDetectorAgent import ...",
                  "line_number": 164,
                  "path": "agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py",
                  "source_layer": "L2",
                  "target_layer": "L5"
                },
                {
                  "import_line": "from agentic_core.L5_safety.reasoning.CodeHealerAgent import ...",
                  "line_number": 165,
                  "path": "agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py",
                  "source_layer": "L2",
                  "target_layer": "L5"
                },
                {
                  "import_line": "from agentic_core.L5_safety.reasoning.SafetyDetectorAgent import ...",
                  "line_number": 166,
                  "path": "agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py",
                  "source_layer": "L2",
                  "target_layer": "L5"
                },
                {
                  "import_line": "from agentic_core.L5_safety.reasoning.SafetyExecutorAgent import ...",
                  "line_number": 167,
                  "path": "agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py",
                  "source_layer": "L2",
                  "target_layer": "L5"
                },
                {
                  "import_line": "from agentic_core.L5_safety.reasoning.StructureValidatorAgent import ...",
                  "line_number": 210,
                  "path": "agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py",
                  "source_layer": "L2",
                  "target_layer": "L5"
                },
                {
                  "import_line": "from agentic_core.L3_orchestration.types.approval_contract import ...",
                  "line_number": 35,
                  "path": "agentic_core/L2_execution/scripts/remediation_dispatcher.py",
                  "source_layer": "L2",
                  "target_layer": "L3"
                },
                {
                  "import_line": "from agentic_core.L5_safety.validators.GovernanceAgent import ...",
                  "line_number": 84,
                  "path": "agentic_core/L3_orchestration/enforcement/mission_runner.py",
                  "source_layer": "L3",
                  "target_layer": "L5"
                },
                {
                  "import_line": "from agentic_core.L5_safety.validators.GovernanceAgent import ...",
                  "line_number": 84,
                  "path": "agentic_core/L3_orchestration/enforcement/mission_runner_enforcer.py",
                  "source_layer": "L3",
                  "target_layer": "L5"
                },
                {
                  "import_line": "from agentic_core.L5_safety.validators.HygieneGuardianAgent import ...",
                  "line_number": 107,
                  "path": "agentic_core/L3_orchestration/enforcement/safety_strategy.py",
                  "source_layer": "L3",
                  "target_layer": "L5"
                },
                {
                  "import_line": "from agentic_core.L5_safety.reasoning.NamingAgent import ...",
                  "line_number": 113,
                  "path": "agentic_core/L3_orchestration/enforcement/safety_strategy.py",
                  "source_layer": "L3",
                  "target_layer": "L5"
                },
                {
                  "import_line": "from agentic_core.L5_safety.reasoning.LocationAgent import ...",
                  "line_number": 117,
                  "path": "agentic_core/L3_orchestration/enforcement/safety_strategy.py",
                  "source_layer": "L3",
                  "target_layer": "L5"
                },
                {
                  "import_line": "from agentic_core.L5_safety.reasoning.StructureEnforcerAgent import ...",
                  "line_number": 121,
                  "path": "agentic_core/L3_orchestration/enforcement/safety_strategy.py",
                  "source_layer": "L3",
                  "target_layer": "L5"
                },
                {
                  "import_line": "from agentic_core.L5_safety.validators.StructuralHealerAgent import ...",
                  "line_number": 127,
                  "path": "agentic_core/L3_orchestration/enforcement/safety_strategy.py",
                  "source_layer": "L3",
                  "target_layer": "L5"
                },
                {
                  "import_line": "from agentic_core.L5_safety.reasoning.CodeEnforcerAgent import ...",
                  "line_number": 67,
                  "path": "agentic_core/L3_orchestration/engines/AgentFactory.py",
                  "source_layer": "L3",
                  "target_layer": "L5"
                },
                {
                  "import_line": "from agentic_core.L5_safety.reasoning.ResourceManagerAgent import ...",
                  "line_number": 26,
                  "path": "agentic_core/L3_orchestration/engines/autonomous_execution_engine.py",
                  "source_layer": "L3",
                  "target_layer": "L5"
                },
                {
                  "import_line": "from agentic_core.L4_state.checkpoint_manager import ...",
                  "line_number": 35,
                  "path": "agentic_core/L3_orchestration/engines/autonomous_execution_engine.py",
                  "source_layer": "L3",
                  "target_layer": "L4"
                },
                {
                  "import_line": "from agentic_core.L5_safety.validators.credential_types import ...",
                  "line_number": 404,
                  "path": "agentic_core/L3_orchestration/engines/orchestrator_engine.py",
                  "source_layer": "L3",
                  "target_layer": "L5"
                },
                {
                  "import_line": "from agentic_core.L4_state.P1_core.ValidationContext import ...",
                  "line_number": 104,
                  "path": "agentic_core/L3_orchestration/engines/sovereign_mcp_router.py",
                  "source_layer": "L3",
                  "target_layer": "L4"
                },
                {
                  "import_line": "from agentic_core.L4_state.P1_core.ValidationContext import ...",
                  "line_number": 127,
                  "path": "agentic_core/L3_orchestration/engines/sovereign_mcp_router.py",
                  "source_layer": "L3",
                  "target_layer": "L4"
                },
                {
                  "import_line": "from agentic_core.L6_observability.reasoning.layer_decorator import ...",
                  "line_number": 18,
                  "path": "agentic_core/L3_orchestration/reasoning/CoverageAgent.py",
                  "source_layer": "L3",
                  "target_layer": "L6"
                },
                {
                  "import_line": "from agentic_core.L5_safety.reasoning.InspectorExecutor import ...",
                  "line_number": 7,
                  "path": "agentic_core/L3_orchestration/reasoning/DagRuntimeInspectorAgent.py",
                  "source_layer": "L3",
                  "target_layer": "L5"
                },
                {
                  "import_line": "from agentic_core.L5_safety.validators.GovernanceAgent import ...",
                  "line_number": 87,
                  "path": "agentic_core/L3_orchestration/reasoning/NervousSystemAgent.py",
                  "source_layer": "L3",
                  "target_layer": "L5"
                },
                {
                  "import_line": "from agentic_core.L5_safety.reasoning.LocationAgent import ...",
                  "line_number": 95,
                  "path": "agentic_core/L3_orchestration/reasoning/NervousSystemAgent.py",
                  "source_layer": "L3",
                  "target_layer": "L5"
                },
                {
                  "import_line": "from agentic_core.L5_safety.enforcement.HierarchyAgent import ...",
                  "line_number": 102,
                  "path": "agentic_core/L3_orchestration/reasoning/NervousSystemAgent.py",
                  "source_layer": "L3",
                  "target_layer": "L5"
                },
                {
                  "import_line": "from agentic_core.L5_safety.reasoning.CodeHealerAgent import ...",
                  "line_number": 110,
                  "path": "agentic_core/L3_orchestration/reasoning/NervousSystemAgent.py",
                  "source_layer": "L3",
                  "target_layer": "L5"
                },
                {
                  "import_line": "from agentic_core.L6_observability.reasoning.CoverageAgent import ...",
                  "line_number": 234,
                  "path": "agentic_core/L3_orchestration/reasoning/NervousSystemAgent.py",
                  "source_layer": "L3",
                  "target_layer": "L6"
                },
                {
                  "import_line": "from agentic_core.L6_observability.dashboards.data_generator import ...",
                  "line_number": 22,
                  "path": "agentic_core/L5_safety/reasoning/AutonomyGuardianAgent.py",
                  "source_layer": "L5",
                  "target_layer": "L6"
                },
                {
                  "import_line": "from agentic_core.L6_observability.reasoning.layer_decorator import ...",
                  "line_number": 11,
                  "path": "agentic_core/L5_safety/reasoning/L5SafetyExerciserAgent.py",
                  "source_layer": "L5",
                  "target_layer": "L6"
                },
                {
                  "import_line": "from agentic_core.L6_observability.reasoning.ObservabilityProbeExecutor import ...",
                  "line_number": 51,
                  "path": "agentic_core/L5_safety/runners/agent_roster_runner.py",
                  "source_layer": "L5",
                  "target_layer": "L6"
                },
                {
                  "import_line": "from agentic_core.L5_safety.config.structure_blueprint_config import ...",
                  "line_number": 40,
                  "path": "agentic_core/base_agents/L0RoutingBase.py",
                  "source_layer": "L0",
                  "target_layer": "L5"
                }
              ]
            },
            "status": "FAIL"
          },
          {
            "check_id": "layer_gravity",
            "details": "All agents in correct layers",
            "evidence": {
              "violation_count": 0,
              "violations": []
            },
            "status": "PASS"
          }
        ],
        "guardian_id": "architecture_governance",
        "status": "FAIL"
      },
      "status": "FAIL"
    },
    {
      "check_id": "guardian_classification_compliance",
      "details": "Classification compliance: 2/2 checks failed (1496 files scanned)",
      "evidence": {
        "check_count": 2,
        "checks": [
          {
            "check_id": "naming_compliance",
            "details": "26 compound suffix conflict(s) detected",
            "evidence": {
              "violation_count": 26,
              "violations": [
                {
                  "conflicting_tags": [
                    "ADAPTER",
                    "UTILITY"
                  ],
                  "filename": "local_disk_adapter_util.py",
                  "path": "agentic_core/L4_state/utils/local_disk_adapter_util.py",
                  "pattern_matched": "_adapter_util$"
                },
                {
                  "conflicting_tags": [
                    "AGENT",
                    "MIXIN"
                  ],
                  "filename": "domain_agent_mixin.py",
                  "path": "agentic_core/mixins/domain_agent_mixin.py",
                  "pattern_matched": "_agent_mixin$"
                },
                {
                  "conflicting_tags": [
                    "AGENT",
                    "MIXIN"
                  ],
                  "filename": "feature_flagged_agent_mixin.py",
                  "path": "agentic_core/mixins/feature_flagged_agent_mixin.py",
                  "pattern_matched": "_agent_mixin$"
                },
                {
                  "conflicting_tags": [
                    "AGENT",
                    "MIXIN"
                  ],
                  "filename": "healer_agent_mixin.py",
                  "path": "agentic_core/mixins/healer_agent_mixin.py",
                  "pattern_matched": "_agent_mixin$"
                },
                {
                  "conflicting_tags": [
                    "STRATEGY",
                    "TYPES"
                  ],
                  "filename": "expansion_strategy_types.py",
                  "path": "agentic_core/runtime/types/expansion_strategy_types.py",
                  "pattern_matched": "_strategy_types$"
                },
                {
                  "conflicting_tags": [
                    "AGENT",
                    "CONFIG"
                  ],
                  "filename": "placeholder_detector_agent_config.py",
                  "path": "apps_lic/config/placeholder_detector_agent_config.py",
                  "pattern_matched": "_agent_config$"
                },
                {
                  "conflicting_tags": [
                    "AGENT",
                    "TYPES"
                  ],
                  "filename": "app_content_validator_agent_types.py",
                  "path": "apps_lic/types/app_content_validator_agent_types.py",
                  "pattern_matched": "_agent_types$"
                },
                {
                  "conflicting_tags": [
                    "GUARDRAIL",
                    "TYPES"
                  ],
                  "filename": "code_quality_guardrail_types.py",
                  "path": "apps_lic/types/code_quality_guardrail_types.py",
                  "pattern_matched": "_guardrail_types$"
                },
                {
                  "conflicting_tags": [
                    "AGENT",
                    "TYPES"
                  ],
                  "filename": "competitor_recon_agent_types.py",
                  "path": "apps_lic/types/competitor_recon_agent_types.py",
                  "pattern_matched": "_agent_types$"
                },
                {
                  "conflicting_tags": [
                    "AGENT",
                    "TYPES"
                  ],
                  "filename": "stack_modernization_agent_types.py",
                  "path": "apps_lic/types/stack_modernization_agent_types.py",
                  "pattern_matched": "_agent_types$"
                },
                {
                  "conflicting_tags": [
                    "AGENT",
                    "TYPES"
                  ],
                  "filename": "gap_closure_architect_agent_types.py",
                  "path": "apps_rg/types/gap_closure_architect_agent_types.py",
                  "pattern_matched": "_agent_types$"
                },
                {
                  "conflicting_tags": [
                    "CONFIG",
                    "TYPES"
                  ],
                  "filename": "app_config_types.py",
                  "path": "apps_shared/types/app_config_types.py",
                  "pattern_matched": "_config_types$"
                },
                {
                  "conflicting_tags": [
                    "MANAGER",
                    "TYPES"
                  ],
                  "filename": "checkpoint_manager_types.py",
                  "path": "apps_shared/types/checkpoint_manager_types.py",
                  "pattern_matched": "_manager_types$"
                },
                {
                  "conflicting_tags": [
                    "ORCHESTRATOR",
                    "TYPES"
                  ],
                  "filename": "execution_orchestrator_types.py",
                  "path": "apps_shared/types/execution_orchestrator_types.py",
                  "pattern_matched": "_orchestrator_types$"
                },
                {
                  "conflicting_tags": [
                    "ORCHESTRATOR",
                    "TYPES"
                  ],
                  "filename": "feedback_loop_orchestrator_types.py",
                  "path": "apps_shared/types/feedback_loop_orchestrator_types.py",
                  "pattern_matched": "_orchestrator_types$"
                },
                {
                  "conflicting_tags": [
                    "MANAGER",
                    "TYPES"
                  ],
                  "filename": "memory_manager_types.py",
                  "path": "apps_shared/types/memory_manager_types.py",
                  "pattern_matched": "_manager_types$"
                },
                {
                  "conflicting_tags": [
                    "MIXIN",
                    "UTILITY"
                  ],
                  "filename": "analysis_mixin_util.py",
                  "path": "apps_shared/utils/analysis_mixin_util.py",
                  "pattern_matched": "_mixin_util$"
                },
                {
                  "conflicting_tags": [
                    "UTILITY",
                    "VALIDATOR"
                  ],
                  "filename": "input_validator_util.py",
                  "path": "apps_shared/utils/input_validator_util.py",
                  "pattern_matched": "_validator_util$"
                },
                {
                  "conflicting_tags": [
                    "UTILITY",
                    "VALIDATOR"
                  ],
                  "filename": "json_parser_validator_util.py",
                  "path": "apps_shared/utils/json_parser_validator_util.py",
                  "pattern_matched": "_validator_util$"
                },
                {
                  "conflicting_tags": [
                    "ADAPTER",
                    "UTILITY"
                  ],
                  "filename": "open_telemetry_tracing_adapter_util.py",
                  "path": "apps_shared/utils/open_telemetry_tracing_adapter_util.py",
                  "pattern_matched": "_adapter_util$"
                },
                {
                  "conflicting_tags": [
                    "MIXIN",
                    "UTILITY"
                  ],
                  "filename": "orchestration_mixin_util.py",
                  "path": "apps_shared/utils/orchestration_mixin_util.py",
                  "pattern_matched": "_mixin_util$"
                },
                {
                  "conflicting_tags": [
                    "FACTORY",
                    "UTILITY"
                  ],
                  "filename": "router_factory_util.py",
                  "path": "apps_shared/utils/router_factory_util.py",
                  "pattern_matched": "_factory_util$"
                },
                {
                  "conflicting_tags": [
                    "CONFIG",
                    "UTILITY"
                  ],
                  "filename": "security_config_util.py",
                  "path": "apps_shared/utils/security_config_util.py",
                  "pattern_matched": "_config_util$"
                },
                {
                  "conflicting_tags": [
                    "UTILITY",
                    "VALIDATOR"
                  ],
                  "filename": "text_processing_validator_util.py",
                  "path": "apps_shared/utils/text_processing_validator_util.py",
                  "pattern_matched": "_validator_util$"
                },
                {
                  "conflicting_tags": [
                    "MIXIN",
                    "UTILITY"
                  ],
                  "filename": "validation_mixin_util.py",
                  "path": "apps_shared/utils/validation_mixin_util.py",
                  "pattern_matched": "_mixin_util$"
                },
                {
                  "conflicting_tags": [
                    "MANAGER",
                    "VALIDATOR"
                  ],
                  "filename": "validation_context_manager_validator.py",
                  "path": "apps_shared/validators/validation_context_manager_validator.py",
                  "pattern_matched": "_manager_validator$"
                }
              ]
            },
            "status": "FAIL"
          },
          {
            "check_id": "territory_compliance",
            "details": "145 territory violation(s) detected",
            "evidence": {
              "violation_count": 145,
              "violations": [
                {
                  "classified_as": "UTILITY",
                  "current_folder": "config",
                  "expected_folder": "utils",
                  "filename": "path_constants.py",
                  "path": "agentic_core/L0_routing/config/path_constants.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "config",
                  "expected_folder": "utils",
                  "filename": "structure_blueprint_data.py",
                  "path": "agentic_core/L0_routing/config/structure_blueprint_data.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "enforcement",
                  "expected_folder": "utils",
                  "filename": "boot_sequence_enforcer.py",
                  "path": "agentic_core/L0_routing/enforcement/boot_sequence_enforcer.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "enforcement",
                  "expected_folder": "utils",
                  "filename": "mutation_prohibition.py",
                  "path": "agentic_core/L0_routing/enforcement/mutation_prohibition.py"
                },
                {
                  "classified_as": "EXCEPTION",
                  "current_folder": "enforcement",
                  "expected_folder": "types",
                  "filename": "v15_p3_contracts.py",
                  "path": "agentic_core/L0_routing/enforcement/v15_p3_contracts.py"
                },
                {
                  "classified_as": "EXCEPTION",
                  "current_folder": "enforcement",
                  "expected_folder": "types",
                  "filename": "v15_p4_contracts.py",
                  "path": "agentic_core/L0_routing/enforcement/v15_p4_contracts.py"
                },
                {
                  "classified_as": "EXCEPTION",
                  "current_folder": "enforcement",
                  "expected_folder": "types",
                  "filename": "v15_p5_contracts.py",
                  "path": "agentic_core/L0_routing/enforcement/v15_p5_contracts.py"
                },
                {
                  "classified_as": "EXCEPTION",
                  "current_folder": "enforcement",
                  "expected_folder": "types",
                  "filename": "v15_p6_contracts.py",
                  "path": "agentic_core/L0_routing/enforcement/v15_p6_contracts.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "enforcement",
                  "expected_folder": "utils",
                  "filename": "v15_runtime_guard.py",
                  "path": "agentic_core/L0_routing/enforcement/v15_runtime_guard.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "enforcement",
                  "expected_folder": "utils",
                  "filename": "vigilance_routing.py",
                  "path": "agentic_core/L0_routing/enforcement/vigilance_routing.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "scripts",
                  "expected_folder": "utils",
                  "filename": "add_subatomic_safe_util.py",
                  "path": "agentic_core/L0_routing/scripts/add_subatomic_safe_util.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "scripts",
                  "expected_folder": "utils",
                  "filename": "add_subatomic_testing_to_agents_util.py",
                  "path": "agentic_core/L0_routing/scripts/add_subatomic_testing_to_agents_util.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "scripts",
                  "expected_folder": "utils",
                  "filename": "add_subatomic_tests_util.py",
                  "path": "agentic_core/L0_routing/scripts/add_subatomic_tests_util.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "scripts",
                  "expected_folder": "utils",
                  "filename": "cache_init_util.py",
                  "path": "agentic_core/L0_routing/scripts/cache_init_util.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "scripts",
                  "expected_folder": "utils",
                  "filename": "check_from_utils_duplicates_util.py",
                  "path": "agentic_core/L0_routing/scripts/check_from_utils_duplicates_util.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "scripts",
                  "expected_folder": "utils",
                  "filename": "check_sovereign_base_util.py",
                  "path": "agentic_core/L0_routing/scripts/check_sovereign_base_util.py"
                },
                {
                  "classified_as": "TYPES",
                  "current_folder": "scripts",
                  "expected_folder": "types",
                  "filename": "code_entity.py",
                  "path": "agentic_core/L0_routing/scripts/code_entity.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "scripts",
                  "expected_folder": "utils",
                  "filename": "compare_autonomy_guardian_files_util.py",
                  "path": "agentic_core/L0_routing/scripts/compare_autonomy_guardian_files_util.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "scripts",
                  "expected_folder": "utils",
                  "filename": "comprehensive_archive_check_util.py",
                  "path": "agentic_core/L0_routing/scripts/comprehensive_archive_check_util.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "scripts",
                  "expected_folder": "utils",
                  "filename": "count_territories_util.py",
                  "path": "agentic_core/L0_routing/scripts/count_territories_util.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "scripts",
                  "expected_folder": "utils",
                  "filename": "debug_drilldown_util.py",
                  "path": "agentic_core/L0_routing/scripts/debug_drilldown_util.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "scripts",
                  "expected_folder": "utils",
                  "filename": "debug_invocation_pipeline_util.py",
                  "path": "agentic_core/L0_routing/scripts/debug_invocation_pipeline_util.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "scripts",
                  "expected_folder": "utils",
                  "filename": "debug_target_mismatch_util.py",
                  "path": "agentic_core/L0_routing/scripts/debug_target_mismatch_util.py"
                },
                {
                  "classified_as": "TYPES",
                  "current_folder": "scripts",
                  "expected_folder": "types",
                  "filename": "disposition.py",
                  "path": "agentic_core/L0_routing/scripts/disposition.py"
                },
                {
                  "classified_as": "TYPES",
                  "current_folder": "scripts",
                  "expected_folder": "types",
                  "filename": "execute_ssot.py",
                  "path": "agentic_core/L0_routing/scripts/execute_ssot.py"
                },
                {
                  "classified_as": "TYPES",
                  "current_folder": "scripts",
                  "expected_folder": "types",
                  "filename": "file_analysis.py",
                  "path": "agentic_core/L0_routing/scripts/file_analysis.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "scripts",
                  "expected_folder": "utils",
                  "filename": "find_agents_in_low_heal_territories_util.py",
                  "path": "agentic_core/L0_routing/scripts/find_agents_in_low_heal_territories_util.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "scripts",
                  "expected_folder": "utils",
                  "filename": "find_base_class_agents_util.py",
                  "path": "agentic_core/L0_routing/scripts/find_base_class_agents_util.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "scripts",
                  "expected_folder": "utils",
                  "filename": "find_infrastructure_target_issue_util.py",
                  "path": "agentic_core/L0_routing/scripts/find_infrastructure_target_issue_util.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "scripts",
                  "expected_folder": "utils",
                  "filename": "find_low_heal_territories_util.py",
                  "path": "agentic_core/L0_routing/scripts/find_low_heal_territories_util.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "scripts",
                  "expected_folder": "utils",
                  "filename": "find_low_typed_documented_util.py",
                  "path": "agentic_core/L0_routing/scripts/find_low_typed_documented_util.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "scripts",
                  "expected_folder": "utils",
                  "filename": "find_missing_agents_util.py",
                  "path": "agentic_core/L0_routing/scripts/find_missing_agents_util.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "scripts",
                  "expected_folder": "utils",
                  "filename": "find_missing_invocation_util.py",
                  "path": "agentic_core/L0_routing/scripts/find_missing_invocation_util.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "scripts",
                  "expected_folder": "utils",
                  "filename": "find_missing_invocations_util.py",
                  "path": "agentic_core/L0_routing/scripts/find_missing_invocations_util.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "scripts",
                  "expected_folder": "utils",
                  "filename": "find_non_hardened_l0_util.py",
                  "path": "agentic_core/L0_routing/scripts/find_non_hardened_l0_util.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "scripts",
                  "expected_folder": "utils",
                  "filename": "find_open_heal_invocations_util.py",
                  "path": "agentic_core/L0_routing/scripts/find_open_heal_invocations_util.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "scripts",
                  "expected_folder": "utils",
                  "filename": "find_remaining_missing_heal_util.py",
                  "path": "agentic_core/L0_routing/scripts/find_remaining_missing_heal_util.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "scripts",
                  "expected_folder": "utils",
                  "filename": "fission_executor_util.py",
                  "path": "agentic_core/L0_routing/scripts/fission_executor_util.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "scripts",
                  "expected_folder": "utils",
                  "filename": "investigate_sovereign_base_util.py",
                  "path": "agentic_core/L0_routing/scripts/investigate_sovereign_base_util.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "scripts",
                  "expected_folder": "utils",
                  "filename": "layer_summary_util.py",
                  "path": "agentic_core/L0_routing/scripts/layer_summary_util.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "scripts",
                  "expected_folder": "utils",
                  "filename": "list_layer_agents_util.py",
                  "path": "agentic_core/L0_routing/scripts/list_layer_agents_util.py"
                },
                {
                  "classified_as": "STRATEGY",
                  "current_folder": "scripts",
                  "expected_folder": "enforcement",
                  "filename": "reasoning.py",
                  "path": "agentic_core/L0_routing/scripts/reasoning.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "scripts",
                  "expected_folder": "utils",
                  "filename": "run_naming_scan_util.py",
                  "path": "agentic_core/L0_routing/scripts/run_naming_scan_util.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "scripts",
                  "expected_folder": "utils",
                  "filename": "verify_all_checkpoint_files_util.py",
                  "path": "agentic_core/L0_routing/scripts/verify_all_checkpoint_files_util.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "scripts",
                  "expected_folder": "utils",
                  "filename": "verify_base_agent_names_util.py",
                  "path": "agentic_core/L0_routing/scripts/verify_base_agent_names_util.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "scripts",
                  "expected_folder": "utils",
                  "filename": "verify_heal_invocation_util.py",
                  "path": "agentic_core/L0_routing/scripts/verify_heal_invocation_util.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "scripts",
                  "expected_folder": "utils",
                  "filename": "verify_health_calculation_util.py",
                  "path": "agentic_core/L0_routing/scripts/verify_health_calculation_util.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "scripts",
                  "expected_folder": "utils",
                  "filename": "verify_manifest_cleanliness_util.py",
                  "path": "agentic_core/L0_routing/scripts/verify_manifest_cleanliness_util.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "scripts",
                  "expected_folder": "utils",
                  "filename": "verify_row_order_util.py",
                  "path": "agentic_core/L0_routing/scripts/verify_row_order_util.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "scripts",
                  "expected_folder": "utils",
                  "filename": "verify_territory_counts_util.py",
                  "path": "agentic_core/L0_routing/scripts/verify_territory_counts_util.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "types",
                  "expected_folder": "utils",
                  "filename": "v15_artifact_typed.py",
                  "path": "agentic_core/L0_routing/types/v15_artifact_typed.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "types",
                  "expected_folder": "utils",
                  "filename": "v15_artifact_typed_types.py",
                  "path": "agentic_core/L0_routing/types/v15_artifact_typed_types.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "types",
                  "expected_folder": "utils",
                  "filename": "v15_artifact_validate.py",
                  "path": "agentic_core/L0_routing/types/v15_artifact_validate.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "types",
                  "expected_folder": "utils",
                  "filename": "v15_artifact_validate_types.py",
                  "path": "agentic_core/L0_routing/types/v15_artifact_validate_types.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "types",
                  "expected_folder": "utils",
                  "filename": "v15_artifact_validation_types.py",
                  "path": "agentic_core/L0_routing/types/v15_artifact_validation_types.py"
                },
                {
                  "classified_as": "SCRIPT",
                  "current_folder": "utils",
                  "expected_folder": "scripts",
                  "filename": "add_test_coverage_util.py",
                  "path": "agentic_core/L0_routing/utils/add_test_coverage_util.py"
                },
                {
                  "classified_as": "TYPES",
                  "current_folder": "utils",
                  "expected_folder": "types",
                  "filename": "complexity_visitor_util.py",
                  "path": "agentic_core/L0_routing/utils/complexity_visitor_util.py"
                },
                {
                  "classified_as": "FACTORY",
                  "current_folder": "utils",
                  "expected_folder": "enforcement",
                  "filename": "component_util.py",
                  "path": "agentic_core/L0_routing/utils/component_util.py"
                },
                {
                  "classified_as": "SCRIPT",
                  "current_folder": "utils",
                  "expected_folder": "scripts",
                  "filename": "fix_all_tunnels_util.py",
                  "path": "agentic_core/L0_routing/utils/fix_all_tunnels_util.py"
                },
                {
                  "classified_as": "SCRIPT",
                  "current_folder": "utils",
                  "expected_folder": "scripts",
                  "filename": "fix_depth_violations_util.py",
                  "path": "agentic_core/L0_routing/utils/fix_depth_violations_util.py"
                },
                {
                  "classified_as": "SCRIPT",
                  "current_folder": "utils",
                  "expected_folder": "scripts",
                  "filename": "fix_mission_runner_util.py",
                  "path": "agentic_core/L0_routing/utils/fix_mission_runner_util.py"
                },
                {
                  "classified_as": "SCRIPT",
                  "current_folder": "utils",
                  "expected_folder": "scripts",
                  "filename": "fix_remaining_depth_util.py",
                  "path": "agentic_core/L0_routing/utils/fix_remaining_depth_util.py"
                },
                {
                  "classified_as": "SCRIPT",
                  "current_folder": "utils",
                  "expected_folder": "scripts",
                  "filename": "force_annexation_util.py",
                  "path": "agentic_core/L0_routing/utils/force_annexation_util.py"
                },
                {
                  "classified_as": "SCRIPT",
                  "current_folder": "utils",
                  "expected_folder": "scripts",
                  "filename": "gravity_audit_util.py",
                  "path": "agentic_core/L0_routing/utils/gravity_audit_util.py"
                },
                {
                  "classified_as": "SCRIPT",
                  "current_folder": "utils",
                  "expected_folder": "scripts",
                  "filename": "scorched_earth_merge_util.py",
                  "path": "agentic_core/L0_routing/utils/scorched_earth_merge_util.py"
                },
                {
                  "classified_as": "SCRIPT",
                  "current_folder": "utils",
                  "expected_folder": "scripts",
                  "filename": "sovereign_alignment_v2_util.py",
                  "path": "agentic_core/L0_routing/utils/sovereign_alignment_v2_util.py"
                },
                {
                  "classified_as": "SCRIPT",
                  "current_folder": "utils",
                  "expected_folder": "scripts",
                  "filename": "sovereign_convergence_util.py",
                  "path": "agentic_core/L0_routing/utils/sovereign_convergence_util.py"
                },
                {
                  "classified_as": "SCRIPT",
                  "current_folder": "utils",
                  "expected_folder": "scripts",
                  "filename": "structural_fix_util.py",
                  "path": "agentic_core/L0_routing/utils/structural_fix_util.py"
                },
                {
                  "classified_as": "SCRIPT",
                  "current_folder": "utils",
                  "expected_folder": "scripts",
                  "filename": "trim_remaining_airlocks_util.py",
                  "path": "agentic_core/L0_routing/utils/trim_remaining_airlocks_util.py"
                },
                {
                  "classified_as": "STRATEGY",
                  "current_folder": "types",
                  "expected_folder": "enforcement",
                  "filename": "result_types.py",
                  "path": "agentic_core/L1_cognition/types/result_types.py"
                },
                {
                  "classified_as": "SERVICE",
                  "current_folder": "enforcement",
                  "expected_folder": "utils",
                  "filename": "SovereignLLMGateway.py",
                  "path": "agentic_core/L2_execution/enforcement/SovereignLLMGateway.py"
                },
                {
                  "classified_as": "ORCHESTRATOR",
                  "current_folder": "enforcement",
                  "expected_folder": "reasoning",
                  "filename": "dashboard_e2_e_pipeline.py",
                  "path": "agentic_core/L2_execution/enforcement/dashboard_e2_e_pipeline.py"
                },
                {
                  "classified_as": "ORCHESTRATOR",
                  "current_folder": "enforcement",
                  "expected_folder": "reasoning",
                  "filename": "dashboard_e2_e_pipeline_enforcer.py",
                  "path": "agentic_core/L2_execution/enforcement/dashboard_e2_e_pipeline_enforcer.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "enforcement",
                  "expected_folder": "utils",
                  "filename": "healer_pipe_order.py",
                  "path": "agentic_core/L2_execution/enforcement/healer_pipe_order.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "enforcement",
                  "expected_folder": "utils",
                  "filename": "healer_pipe_order_enforcer.py",
                  "path": "agentic_core/L2_execution/enforcement/healer_pipe_order_enforcer.py"
                },
                {
                  "classified_as": "EXCEPTION",
                  "current_folder": "scripts",
                  "expected_folder": "types",
                  "filename": "remediation_dispatcher.py",
                  "path": "agentic_core/L2_execution/scripts/remediation_dispatcher.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "types",
                  "expected_folder": "utils",
                  "filename": "healer_registry.py",
                  "path": "agentic_core/L2_execution/types/healer_registry.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "types",
                  "expected_folder": "utils",
                  "filename": "healer_registry_types.py",
                  "path": "agentic_core/L2_execution/types/healer_registry_types.py"
                },
                {
                  "classified_as": "EXCEPTION",
                  "current_folder": "utils",
                  "expected_folder": "types",
                  "filename": "staging_buffer_util.py",
                  "path": "agentic_core/L2_execution/utils/staging_buffer_util.py"
                },
                {
                  "classified_as": "ORCHESTRATOR",
                  "current_folder": "config",
                  "expected_folder": "reasoning",
                  "filename": "orchestrator_config.py",
                  "path": "agentic_core/L3_orchestration/config/orchestrator_config.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "reasoning",
                  "expected_folder": "utils",
                  "filename": "DagRuntimeInspectorAgent.py",
                  "path": "agentic_core/L3_orchestration/reasoning/DagRuntimeInspectorAgent.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "types",
                  "expected_folder": "utils",
                  "filename": "state_validation_types.py",
                  "path": "agentic_core/L4_state/types/state_validation_types.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "enforcement",
                  "expected_folder": "utils",
                  "filename": "blueprint_hash.py",
                  "path": "agentic_core/L5_safety/config/structure_blueprint/enforcement/blueprint_hash.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "enforcement",
                  "expected_folder": "utils",
                  "filename": "cross_layer.py",
                  "path": "agentic_core/L5_safety/config/structure_blueprint/enforcement/cross_layer.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "enforcement",
                  "expected_folder": "utils",
                  "filename": "leaf_node.py",
                  "path": "agentic_core/L5_safety/config/structure_blueprint/enforcement/leaf_node.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "enforcement",
                  "expected_folder": "utils",
                  "filename": "mixin_ast.py",
                  "path": "agentic_core/L5_safety/config/structure_blueprint/enforcement/mixin_ast.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "enforcement",
                  "expected_folder": "utils",
                  "filename": "territory_diff.py",
                  "path": "agentic_core/L5_safety/config/structure_blueprint/enforcement/territory_diff.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "enforcement",
                  "expected_folder": "utils",
                  "filename": "volatile_rules.py",
                  "path": "agentic_core/L5_safety/config/structure_blueprint/enforcement/volatile_rules.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "config",
                  "expected_folder": "utils",
                  "filename": "structure_blueprint_config.py",
                  "path": "agentic_core/L5_safety/config/structure_blueprint_config.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "enforcement",
                  "expected_folder": "utils",
                  "filename": "activation_gate.py",
                  "path": "agentic_core/L5_safety/enforcement/activation_gate.py"
                },
                {
                  "classified_as": "SCRIPT",
                  "current_folder": "enforcement",
                  "expected_folder": "scripts",
                  "filename": "airlock_trimmer.py",
                  "path": "agentic_core/L5_safety/enforcement/airlock_trimmer.py"
                },
                {
                  "classified_as": "SCRIPT",
                  "current_folder": "enforcement",
                  "expected_folder": "scripts",
                  "filename": "airlock_trimmer_enforcer.py",
                  "path": "agentic_core/L5_safety/enforcement/airlock_trimmer_enforcer.py"
                },
                {
                  "classified_as": "SERVICE",
                  "current_folder": "enforcement",
                  "expected_folder": "utils",
                  "filename": "archival_gatekeeper.py",
                  "path": "agentic_core/L5_safety/enforcement/archival_gatekeeper.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "enforcement",
                  "expected_folder": "utils",
                  "filename": "artifact_emission_prohibition.py",
                  "path": "agentic_core/L5_safety/enforcement/artifact_emission_prohibition.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "enforcement",
                  "expected_folder": "utils",
                  "filename": "artifact_emission_prohibition_enforcer.py",
                  "path": "agentic_core/L5_safety/enforcement/artifact_emission_prohibition_enforcer.py"
                },
                {
                  "classified_as": "SCRIPT",
                  "current_folder": "enforcement",
                  "expected_folder": "scripts",
                  "filename": "circular_import_fixer.py",
                  "path": "agentic_core/L5_safety/enforcement/circular_import_fixer.py"
                },
                {
                  "classified_as": "SCRIPT",
                  "current_folder": "enforcement",
                  "expected_folder": "scripts",
                  "filename": "circular_import_fixer_enforcer.py",
                  "path": "agentic_core/L5_safety/enforcement/circular_import_fixer_enforcer.py"
                },
                {
                  "classified_as": "SERVICE",
                  "current_folder": "enforcement",
                  "expected_folder": "utils",
                  "filename": "context_session_manager.py",
                  "path": "agentic_core/L5_safety/enforcement/context_session_manager.py"
                },
                {
                  "classified_as": "ORCHESTRATOR",
                  "current_folder": "enforcement",
                  "expected_folder": "reasoning",
                  "filename": "fast_dashboard_e2_e_pipeline.py",
                  "path": "agentic_core/L5_safety/enforcement/fast_dashboard_e2_e_pipeline.py"
                },
                {
                  "classified_as": "ORCHESTRATOR",
                  "current_folder": "enforcement",
                  "expected_folder": "reasoning",
                  "filename": "fast_dashboard_e2_e_pipeline_enforcer.py",
                  "path": "agentic_core/L5_safety/enforcement/fast_dashboard_e2_e_pipeline_enforcer.py"
                },
                {
                  "classified_as": "SCRIPT",
                  "current_folder": "enforcement",
                  "expected_folder": "scripts",
                  "filename": "final_airlock_trimmer.py",
                  "path": "agentic_core/L5_safety/enforcement/final_airlock_trimmer.py"
                },
                {
                  "classified_as": "SCRIPT",
                  "current_folder": "enforcement",
                  "expected_folder": "scripts",
                  "filename": "final_airlock_trimmer_enforcer.py",
                  "path": "agentic_core/L5_safety/enforcement/final_airlock_trimmer_enforcer.py"
                },
                {
                  "classified_as": "SCRIPT",
                  "current_folder": "enforcement",
                  "expected_folder": "scripts",
                  "filename": "hardcoded_path_refactorer.py",
                  "path": "agentic_core/L5_safety/enforcement/hardcoded_path_refactorer.py"
                },
                {
                  "classified_as": "SCRIPT",
                  "current_folder": "enforcement",
                  "expected_folder": "scripts",
                  "filename": "hardcoded_path_refactorer_enforcer.py",
                  "path": "agentic_core/L5_safety/enforcement/hardcoded_path_refactorer_enforcer.py"
                },
                {
                  "classified_as": "AGENT",
                  "current_folder": "enforcement",
                  "expected_folder": "reasoning",
                  "filename": "input_validation_guardrail.py",
                  "path": "agentic_core/L5_safety/enforcement/input_validation_guardrail.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "enforcement",
                  "expected_folder": "utils",
                  "filename": "mission_utils.py",
                  "path": "agentic_core/L5_safety/enforcement/mission_utils.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "enforcement",
                  "expected_folder": "utils",
                  "filename": "mission_utils_enforcer.py",
                  "path": "agentic_core/L5_safety/enforcement/mission_utils_enforcer.py"
                },
                {
                  "classified_as": "SCRIPT",
                  "current_folder": "enforcement",
                  "expected_folder": "scripts",
                  "filename": "module_collision_guard.py",
                  "path": "agentic_core/L5_safety/enforcement/module_collision_guard.py"
                },
                {
                  "classified_as": "SCRIPT",
                  "current_folder": "enforcement",
                  "expected_folder": "scripts",
                  "filename": "module_collision_guardrail.py",
                  "path": "agentic_core/L5_safety/enforcement/module_collision_guardrail.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "enforcement",
                  "expected_folder": "utils",
                  "filename": "mutation_prohibition.py",
                  "path": "agentic_core/L5_safety/enforcement/mutation_prohibition.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "enforcement",
                  "expected_folder": "utils",
                  "filename": "mutation_prohibition_enforcer.py",
                  "path": "agentic_core/L5_safety/enforcement/mutation_prohibition_enforcer.py"
                },
                {
                  "classified_as": "SCRIPT",
                  "current_folder": "enforcement",
                  "expected_folder": "scripts",
                  "filename": "namespace_medic.py",
                  "path": "agentic_core/L5_safety/enforcement/namespace_medic.py"
                },
                {
                  "classified_as": "SCRIPT",
                  "current_folder": "enforcement",
                  "expected_folder": "scripts",
                  "filename": "namespace_medic_enforcer.py",
                  "path": "agentic_core/L5_safety/enforcement/namespace_medic_enforcer.py"
                },
                {
                  "classified_as": "SERVICE",
                  "current_folder": "enforcement",
                  "expected_folder": "utils",
                  "filename": "process_guard.py",
                  "path": "agentic_core/L5_safety/enforcement/process_guard.py"
                },
                {
                  "classified_as": "EXCEPTION",
                  "current_folder": "enforcement",
                  "expected_folder": "types",
                  "filename": "process_guardrail.py",
                  "path": "agentic_core/L5_safety/enforcement/process_guardrail.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "enforcement",
                  "expected_folder": "utils",
                  "filename": "rg_execution_safety_enforcer.py",
                  "path": "agentic_core/L5_safety/enforcement/rg_execution_safety_enforcer.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "enforcement",
                  "expected_folder": "utils",
                  "filename": "safe_subprocess_handler.py",
                  "path": "agentic_core/L5_safety/enforcement/safe_subprocess_handler.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "enforcement",
                  "expected_folder": "utils",
                  "filename": "safe_subprocess_handler_enforcer.py",
                  "path": "agentic_core/L5_safety/enforcement/safe_subprocess_handler_enforcer.py"
                },
                {
                  "classified_as": "EXCEPTION",
                  "current_folder": "enforcement",
                  "expected_folder": "types",
                  "filename": "secure_error_handler_enforcer.py",
                  "path": "agentic_core/L5_safety/enforcement/secure_error_handler_enforcer.py"
                },
                {
                  "classified_as": "SCRIPT",
                  "current_folder": "enforcement",
                  "expected_folder": "scripts",
                  "filename": "ssot_import_enforcer.py",
                  "path": "agentic_core/L5_safety/enforcement/ssot_import_enforcer.py"
                },
                {
                  "classified_as": "AGENT",
                  "current_folder": "enforcement",
                  "expected_folder": "reasoning",
                  "filename": "toxic_dependency_auditor.py",
                  "path": "agentic_core/L5_safety/enforcement/toxic_dependency_auditor.py"
                },
                {
                  "classified_as": "AGENT",
                  "current_folder": "enforcement",
                  "expected_folder": "reasoning",
                  "filename": "toxic_dependency_auditor_enforcer.py",
                  "path": "agentic_core/L5_safety/enforcement/toxic_dependency_auditor_enforcer.py"
                },
                {
                  "classified_as": "AGENT",
                  "current_folder": "enforcement",
                  "expected_folder": "reasoning",
                  "filename": "verification_gate.py",
                  "path": "agentic_core/L5_safety/enforcement/verification_gate.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "types",
                  "expected_folder": "utils",
                  "filename": "heal_model_map.py",
                  "path": "agentic_core/L5_safety/types/heal_model_map.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "types",
                  "expected_folder": "utils",
                  "filename": "heal_model_map_types.py",
                  "path": "agentic_core/L5_safety/types/heal_model_map_types.py"
                },
                {
                  "classified_as": "SCRIPT",
                  "current_folder": "utils",
                  "expected_folder": "scripts",
                  "filename": "extract_pattern_util.py",
                  "path": "agentic_core/L5_safety/utils/extract_pattern_util.py"
                },
                {
                  "classified_as": "SCRIPT",
                  "current_folder": "utils",
                  "expected_folder": "scripts",
                  "filename": "fix_inherited_invocation_util.py",
                  "path": "agentic_core/L5_safety/utils/fix_inherited_invocation_util.py"
                },
                {
                  "classified_as": "SCRIPT",
                  "current_folder": "utils",
                  "expected_folder": "scripts",
                  "filename": "force_app_depth_util.py",
                  "path": "agentic_core/L5_safety/utils/force_app_depth_util.py"
                },
                {
                  "classified_as": "SCRIPT",
                  "current_folder": "utils",
                  "expected_folder": "scripts",
                  "filename": "forge_fortress_util.py",
                  "path": "agentic_core/L5_safety/utils/forge_fortress_util.py"
                },
                {
                  "classified_as": "SCRIPT",
                  "current_folder": "utils",
                  "expected_folder": "scripts",
                  "filename": "pre_deploy_check_util.py",
                  "path": "agentic_core/L5_safety/utils/pre_deploy_check_util.py"
                },
                {
                  "classified_as": "SCRIPT",
                  "current_folder": "utils",
                  "expected_folder": "scripts",
                  "filename": "set_complexity_health_100_util.py",
                  "path": "agentic_core/L5_safety/utils/set_complexity_health_100_util.py"
                },
                {
                  "classified_as": "SCRIPT",
                  "current_folder": "utils",
                  "expected_folder": "scripts",
                  "filename": "sovereign_lock_util.py",
                  "path": "agentic_core/L5_safety/utils/sovereign_lock_util.py"
                },
                {
                  "classified_as": "SCRIPT",
                  "current_folder": "utils",
                  "expected_folder": "scripts",
                  "filename": "ssot_folder_check_util.py",
                  "path": "agentic_core/L5_safety/utils/ssot_folder_check_util.py"
                },
                {
                  "classified_as": "EXCEPTION",
                  "current_folder": "utils",
                  "expected_folder": "types",
                  "filename": "subprocess_security_util.py",
                  "path": "agentic_core/L5_safety/utils/subprocess_security_util.py"
                },
                {
                  "classified_as": "SCRIPT",
                  "current_folder": "utils",
                  "expected_folder": "scripts",
                  "filename": "validate_dashboard_data_sourcing_util.py",
                  "path": "agentic_core/L5_safety/utils/validate_dashboard_data_sourcing_util.py"
                },
                {
                  "classified_as": "SCRIPT",
                  "current_folder": "utils",
                  "expected_folder": "scripts",
                  "filename": "validate_dashboard_ssot_util.py",
                  "path": "agentic_core/L5_safety/utils/validate_dashboard_ssot_util.py"
                },
                {
                  "classified_as": "SCRIPT",
                  "current_folder": "utils",
                  "expected_folder": "scripts",
                  "filename": "validate_path_ssot_util.py",
                  "path": "agentic_core/L5_safety/utils/validate_path_ssot_util.py"
                },
                {
                  "classified_as": "SCRIPT",
                  "current_folder": "utils",
                  "expected_folder": "scripts",
                  "filename": "verify_no_mock_data_util.py",
                  "path": "agentic_core/L5_safety/utils/verify_no_mock_data_util.py"
                },
                {
                  "classified_as": "SCRIPT",
                  "current_folder": "utils",
                  "expected_folder": "scripts",
                  "filename": "verify_semantic_meta_learning_util.py",
                  "path": "agentic_core/L5_safety/utils/verify_semantic_meta_learning_util.py"
                },
                {
                  "classified_as": "UTILITY",
                  "current_folder": "validators",
                  "expected_folder": "utils",
                  "filename": "ddd_alignment_validator.py",
                  "path": "agentic_core/L5_safety/validators/ddd_alignment_validator.py"
                },
                {
                  "classified_as": "SCRIPT",
                  "current_folder": "validators",
                  "expected_folder": "scripts",
                  "filename": "structure_drift_validator.py",
                  "path": "agentic_core/L5_safety/validators/structure_drift_validator.py"
                },
                {
                  "classified_as": "SERVICE",
                  "current_folder": "enforcement",
                  "expected_folder": "utils",
                  "filename": "agent_monitor.py",
                  "path": "agentic_core/L6_observability/enforcement/agent_monitor.py"
                },
                {
                  "classified_as": "SERVICE",
                  "current_folder": "enforcement",
                  "expected_folder": "utils",
                  "filename": "agent_monitor_enforcer.py",
                  "path": "agentic_core/L6_observability/enforcement/agent_monitor_enforcer.py"
                },
                {
                  "classified_as": "SERVICE",
                  "current_folder": "enforcement",
                  "expected_folder": "utils",
                  "filename": "rag_telemetry_collector.py",
                  "path": "agentic_core/L6_observability/enforcement/rag_telemetry_collector.py"
                },
                {
                  "classified_as": "SCRIPT",
                  "current_folder": "utils",
                  "expected_folder": "scripts",
                  "filename": "fix_testing_observability_util.py",
                  "path": "agentic_core/L6_observability/utils/fix_testing_observability_util.py"
                }
              ]
            },
            "status": "FAIL"
          }
        ],
        "guardian_id": "classification_compliance",
        "status": "FAIL"
      },
      "status": "FAIL"
    },
    {
      "check_id": "guardian_drift_detection",
      "details": "Drift detection: 1/1 checks failed",
      "evidence": {
        "check_count": 1,
        "checks": [
          {
            "check_id": "root_drift",
            "details": "Root drift detected: 1 forbidden root folder(s); 1 duplicate SSOT folder(s)",
            "evidence": {
              "archived_files_at_root": [],
              "duplicate_folders": [
                {
                  "name": "logs",
                  "root_path": "logs",
                  "ssot_path": "agentic_core/L0_routing/logs"
                }
              ],
              "forbidden_folders": [
                "logs"
              ]
            },
            "status": "FAIL"
          }
        ],
        "guardian_id": "drift_detection",
        "status": "FAIL"
      },
      "status": "FAIL"
    },
    {
      "check_id": "guardian_hierarchy_compliance",
      "details": "Hierarchy compliance: 2/2 checks passed",
      "evidence": {
        "check_count": 2,
        "checks": [
          {
            "check_id": "missing_structure",
            "details": "All L2/L3 directories present per blueprint",
            "evidence": {
              "violation_count": 0,
              "violations": []
            },
            "status": "PASS"
          },
          {
            "check_id": "subfolder_compliance",
            "details": "All subfolders approved per CORE_SUBFOLDER_MAP",
            "evidence": {
              "violation_count": 0,
              "violations": []
            },
            "status": "PASS"
          }
        ],
        "guardian_id": "hierarchy_compliance",
        "status": "PASS"
      },
      "status": "PASS"
    },
    {
      "check_id": "guardian_hygiene",
      "details": "Guardian hygiene crashed: name 'ROOT_WHITELIST' is not defined",
      "evidence": {},
      "status": "FAIL"
    },
    {
      "check_id": "guardian_location_alignment",
      "details": "Location alignment: 2/2 checks failed",
      "evidence": {
        "check_count": 2,
        "checks": [
          {
            "check_id": "misplaced_files",
            "details": "Scan error: name 'ROOT_WHITELIST' is not defined",
            "evidence": {},
            "status": "FAIL"
          },
          {
            "check_id": "missing_directories",
            "details": "Scan error: name 'ROOT_WHITELIST' is not defined",
            "evidence": {},
            "status": "FAIL"
          }
        ],
        "guardian_id": "location_alignment",
        "status": "ERROR"
      },
      "status": "FAIL"
    },
    {
      "check_id": "guardian_manifest_integrity",
      "details": "Manifest integrity: SKIP (manifest.json absent)",
      "evidence": {
        "check_count": 1,
        "checks": [
          {
            "check_id": "manifest_exists",
            "details": "manifest.json not found \u2014 integrity check not applicable",
            "evidence": {},
            "status": "SKIP"
          }
        ],
        "guardian_id": "manifest_integrity",
        "status": "PASS"
      },
      "status": "PASS"
    }
  ],
  "guardian_id": "combined",
  "index": {
    "architecture_governance": {
      "artifacts": [],
      "status": "FAIL"
    },
    "classification_compliance": {
      "artifacts": [],
      "status": "FAIL"
    },
    "drift_detection": {
      "artifacts": [],
      "status": "FAIL"
    },
    "hierarchy_compliance": {
      "artifacts": [],
      "status": "PASS"
    },
    "hygiene": {
      "artifacts": [],
      "status": "ERROR"
    },
    "location_alignment": {
      "artifacts": [],
      "status": "ERROR"
    },
    "manifest_integrity": {
      "artifacts": [],
      "status": "PASS"
    }
  },
  "metrics": {
    "guardian_count": 7,
    "guardians_error": 2,
    "guardians_failed": 3,
    "guardians_passed": 2,
    "per_guardian": [
      {
        "checks": 2,
        "guardian_id": "architecture_governance",
        "status": "FAIL"
      },
      {
        "checks": 2,
        "guardian_id": "classification_compliance",
        "status": "FAIL"
      },
      {
        "checks": 1,
        "guardian_id": "drift_detection",
        "status": "FAIL"
      },
      {
        "checks": 2,
        "guardian_id": "hierarchy_compliance",
        "status": "PASS"
      },
      {
        "error": "name 'ROOT_WHITELIST' is not defined",
        "guardian_id": "hygiene",
        "status": "ERROR"
      },
      {
        "checks": 2,
        "guardian_id": "location_alignment",
        "status": "ERROR"
      },
      {
        "checks": 1,
        "guardian_id": "manifest_integrity",
        "status": "PASS"
      }
    ],
    "total_checks": 10
  },
  "remediation_hints": [
    "Create missing sovereign root directories",
    "Fix upward import violations: lower layers must not import from higher layers",
    "Move agents to their assigned layer per the SSOT scanner classification",
    "Move archived/backup/old files to archives/",
    "Move misplaced files into recognized subfolders (config/, types/, reasoning/, engines/, etc.)",
    "Move misplaced files to correct LCD folders per classification",
    "Remove duplicate folders that shadow SSOT locations",
    "Remove forbidden root folders (scripts/, logs/, coverage_html/, observability/)",
    "Remove or relocate backup/temp files (.bak, .backup, .old, .tmp)",
    "Rename files with compound suffix conflicts (keep terminal suffix only)"
  ],
  "status": "ERROR",
  "summary": "2 guardian(s) errored, 3 failed out of 7",
  "v15_commit_hash": "HEAD",
  "v15_signature": "3ab7d93ff38b02ef12cbe7f01db24ffb224821c2708da02522a3a6e7cb93fefc",
  "v15_trace_id": "adf8c662086aa389a49223400889f548012995223de2c0e621a2044551990bb7",
  "version": 3
}
pytest not found, attempting to install...
error: externally-managed-environment

× This environment is externally managed
╰─> To install Python packages system-wide, try apt install
    python3-xyz, where xyz is the package you are trying to
    install.

    If you wish to install a non-Debian-packaged Python package,
    create a virtual environment using python3 -m venv path/to/venv.
    Then use path/to/venv/bin/python and path/to/venv/bin/pip. Make
    sure you have python3-full installed.

    If you wish to install a non-Debian packaged Python application,
    it may be easiest to use pipx install xyz, which will manage a
    virtual environment for you. Make sure you have pipx installed.

    See /usr/share/doc/python3.12/README.venv for more information.

note: If you believe this is a mistake, please contact your Python installation or OS distribution provider. You can override this, at the risk of breaking your Python installation or OS, by passing --break-system-packages.
hint: See PEP 668 for the detailed specification.

$ python3 -m pytest -q --tb=no
/usr/bin/python3: No module named pytest
CONVERGE_CONFIDENCE_PERCENT: 95
