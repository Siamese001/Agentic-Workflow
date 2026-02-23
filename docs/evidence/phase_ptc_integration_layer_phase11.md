# Phase 11 Programmatic Tool Calling Evidence

## CODE_COMMIT
8a7e7bd38b8667ec5bb73bad31c6be0093468faf

## PYTHON_VERSION
Python 3.12.10

## STATIC_INVARIANTS

### python tools/run_static_invariants.py
EXIT CODE: 1
STDOUT:
=== Static Invariants Checker ===

Loaded baseline with 1461 existing violations

1. Scanning for PowerShell usage...
FAIL: PowerShell Ban: 63 total violations found (63 new)
NEW violations:
  tools\capture_evidence.py:2:PS_STRING_LITERAL - "
Evidence capture utility for execute_ssot mutation fence implementation.

Runs commands via subprocess with argv arrays (no shell), captures stdout/stderr/exit code,
and aborts if output contains PowerShell indicators.
"
  tools\capture_evidence.py:15:PS_STRING_LITERAL - "
    Execute command and append results to evidence file.

    Args:
        argv: Command arguments as list
        evidence_file: Path to evidence markdown file

    Returns:
        Exit code from command

    Raises:
        RuntimeError: If PowerShell detected in output
    "
  tools\capture_evidence.py:38:PS_STRING_LITERAL - "powershell"
  tools\capture_evidence.py:38:PS_STRING_LITERAL - "pwsh"
  tools\capture_evidence.py:40:PS_STRING_LITERAL - "ABORT: PowerShell detected in command output.
Command: "
  tools\evidence\evidence_contract_v2.py:1:PS_STRING_LITERAL - "
Evidence Contract v2 Helper

Shared helper for consolidated evidence runners that enforces:
- Explicit CODE_COMMIT and EVIDENCE_COMMIT validation
- Hash-loop prevention
- Scope containment with allowed prefixes
- Semantic separation of file sections
- PowerShell detection and rejection
"
  tools\evidence\evidence_contract_v2.py:56:PS_STRING_LITERAL - "Execute command with PowerShell detection and return (rc, stdout, stderr)."
  tools\evidence\evidence_contract_v2.py:59:PS_STRING_LITERAL - "powershell"
  tools\evidence\evidence_contract_v2.py:59:PS_STRING_LITERAL - "pwsh"
  tools\evidence\evidence_contract_v2.py:60:PS_STRING_LITERAL - "PowerShell usage detected in command: "
  tools\evidence\phase01_determinism_util_evidence_runner.py:1:PS_STRING_LITERAL - "
Phase 1 evidence runner — Python-only, shell=False, no PowerShell.

Executes commands via subprocess argv arrays, captures output,
aborts immediately if any output contains 'pwsh' or 'PowerShell' (case-insensitive).

Writes evidence to: docs/reports/plans/phase_01_shared_determinism_util.md
"
  tools\evidence\phase01_determinism_util_evidence_runner.py:38:PS_STRING_LITERAL - "powershell"
  tools\evidence\phase01_determinism_util_evidence_runner.py:38:PS_STRING_LITERAL - "pwsh"
  tools\evidence\phase01_determinism_util_evidence_runner.py:39:PS_STRING_LITERAL - "ABORT: PowerShell detected in stderr output."
  tools\evidence\phase01b_spine_guard_evidence_runner.py:1:PS_STRING_LITERAL - "
Phase 1B evidence runner — Python-only, shell=False, no PowerShell.

Executes commands via subprocess argv arrays, captures output,
writes evidence to: docs/reports/plans/phase_01b_ci_spine_guard.md
"
  tools\evidence\phase01b_spine_guard_evidence_runner.py:36:PS_STRING_LITERAL - "powershell"
  tools\evidence\phase01b_spine_guard_evidence_runner.py:36:PS_STRING_LITERAL - "pwsh"
  tools\evidence\phase01b_spine_guard_evidence_runner.py:37:PS_STRING_LITERAL - "ABORT: PowerShell detected in stderr output."
  tools\evidence\phase02_spine_adapters_evidence_runner.py:2:PS_STRING_LITERAL - "Phase 2 Spine Adapters Evidence Runner - Deterministic Generator.

Generates verbatim evidence for Phase 2 completion.
All commands executed via subprocess with argv arrays (shell=False).
PowerShell detection via argv-level checks only (no output scanning).
"
  tools\evidence\phase02_spine_adapters_evidence_runner.py:18:PS_STRING_LITERAL - "powershell"
  tools\evidence\phase02_spine_adapters_evidence_runner.py:18:PS_STRING_LITERAL - "pwsh"
  tools\evidence\phase02_spine_adapters_evidence_runner.py:19:PS_STRING_LITERAL - "ERROR: PowerShell usage detected in command: "
  tools\evidence\phase02a_lic_spine_adapter_evidence_runner.py:1:PS_STRING_LITERAL - "
Phase 2A evidence runner — Python-only, shell=False, no PowerShell.

Writes evidence to: docs/reports/plans/phase_02a_lic_spine_adapter.md
"
  tools\evidence\phase02a_lic_spine_adapter_evidence_runner.py:26:PS_STRING_LITERAL - "powershell"
  tools\evidence\phase02a_lic_spine_adapter_evidence_runner.py:26:PS_STRING_LITERAL - "pwsh"
  tools\evidence\phase02a_lic_spine_adapter_evidence_runner.py:27:PS_STRING_LITERAL - "ABORT: PowerShell detected in stderr output."
  tools\run_phase10_arbitration_evidence.py:2:PS_STRING_LITERAL - "
Phase 10 Multi-Agent Arbitration Evidence Runner

Captures deterministic command outputs for Phase 10 closure evidence.
Uses subprocess.run with shell=False and validates no PowerShell usage.
"
  tools\run_phase10_arbitration_evidence.py:15:PS_STRING_LITERAL - "Run command with subprocess.run, ensuring no PowerShell usage."
  tools\run_phase10_arbitration_evidence.py:16:PS_STRING_LITERAL - "powershell"
  tools\run_phase10_arbitration_evidence.py:16:PS_STRING_LITERAL - "pwsh"
  tools\run_phase10_arbitration_evidence.py:17:PS_STRING_LITERAL - "FAIL: PowerShell detected in argv0: "
  tools\run_phase11_ptc_evidence.py:2:PS_STRING_LITERAL - "
Phase 11 Programmatic Tool Calling Evidence Runner

Captures deterministic command outputs for Phase 11 closure evidence.
Uses subprocess.run with shell=False and validates no PowerShell usage.
"
  tools\run_phase11_ptc_evidence.py:15:PS_STRING_LITERAL - "Run command with subprocess.run, ensuring no PowerShell usage."
  tools\run_phase11_ptc_evidence.py:16:PS_STRING_LITERAL - "powershell"
  tools\run_phase11_ptc_evidence.py:16:PS_STRING_LITERAL - "pwsh"
  tools\run_phase11_ptc_evidence.py:17:PS_STRING_LITERAL - "FAIL: PowerShell detected in argv0: "
  tools\run_phase3_integration.py:35:PS_STRING_LITERAL - "powershell"
  tools\run_phase3_integration.py:35:PS_STRING_LITERAL - "pwsh"
  tools\run_phase3_integration.py:36:PS_STRING_LITERAL - "FORBIDDEN: argv0 contains pwsh/powershell: "
  tools\run_phase6_replay_evidence.py:2:PS_STRING_LITERAL - "
Phase 6 Deterministic Replay Engine Evidence Runner

Captures deterministic command outputs for Phase 6 closure evidence.
Uses subprocess.run with shell=False and validates no PowerShell usage.
"
  tools\run_phase6_replay_evidence.py:15:PS_STRING_LITERAL - "Run command with subprocess.run, ensuring no PowerShell usage."
  tools\run_phase6_replay_evidence.py:16:PS_STRING_LITERAL - "powershell"
  tools\run_phase6_replay_evidence.py:16:PS_STRING_LITERAL - "pwsh"
  tools\run_phase6_replay_evidence.py:17:PS_STRING_LITERAL - "FAIL: PowerShell detected in argv0: "
  tools\run_phase7_storage_evidence.py:2:PS_STRING_LITERAL - "
Phase 7 Persistent Storage Layer Evidence Runner

Captures deterministic command outputs for Phase 7 closure evidence.
Uses subprocess.run with shell=False and validates no PowerShell usage.
"
  tools\run_phase7_storage_evidence.py:15:PS_STRING_LITERAL - "Run command with subprocess.run, ensuring no PowerShell usage."
  tools\run_phase7_storage_evidence.py:16:PS_STRING_LITERAL - "powershell"
  tools\run_phase7_storage_evidence.py:16:PS_STRING_LITERAL - "pwsh"
  tools\run_phase7_storage_evidence.py:17:PS_STRING_LITERAL - "FAIL: PowerShell detected in argv0: "
  tools\run_phase8_perf_evidence.py:2:PS_STRING_LITERAL - "
Phase 8 Performance Envelope & Scaling Hardening Evidence Runner

Captures deterministic command outputs for Phase 8 closure evidence.
Uses subprocess.run with shell=False and validates no PowerShell usage.
"
  tools\run_phase8_perf_evidence.py:15:PS_STRING_LITERAL - "Run command with subprocess.run, ensuring no PowerShell usage."
  tools\run_phase8_perf_evidence.py:16:PS_STRING_LITERAL - "powershell"
  tools\run_phase8_perf_evidence.py:16:PS_STRING_LITERAL - "pwsh"
  tools\run_phase8_perf_evidence.py:17:PS_STRING_LITERAL - "FAIL: PowerShell detected in argv0: "
  tools\run_phase9_formal_checks_evidence.py:2:PS_STRING_LITERAL - "
Phase 9 Formal Verification Evidence Runner

Captures deterministic command outputs for Phase 9 closure evidence.
Uses subprocess.run with shell=False and validates no PowerShell usage.
"
  tools\run_phase9_formal_checks_evidence.py:15:PS_STRING_LITERAL - "Run command with subprocess.run, ensuring no PowerShell usage."
  tools\run_phase9_formal_checks_evidence.py:16:PS_STRING_LITERAL - "powershell"
  tools\run_phase9_formal_checks_evidence.py:16:PS_STRING_LITERAL - "pwsh"
  tools\run_phase9_formal_checks_evidence.py:17:PS_STRING_LITERAL - "FAIL: PowerShell detected in argv0: "
  tools\run_static_invariants.py:34:PS_STRING_LITERAL - "powershell_ban"
  tools\run_static_invariants.py:35:PS_STRING_LITERAL - "powershell_ban.py"
  tools\run_static_invariants.py:126:PS_STRING_LITERAL - "1. Scanning for PowerShell usage..."
  tools\run_static_invariants.py:128:PS_STRING_LITERAL - "PowerShell Ban"

2. Scanning for direct writes...
FAIL: Direct Writes: 191 total violations found (191 new)
NEW violations:
  agentic_core\L0_routing\enforcement\mutation_prohibition.py:109:DIRECT_OPEN_WRITE - open(..., mode="a")
  agentic_core\L0_routing\enforcement\mutation_prohibition.py:109:DIRECT_WITH_WRITE - with open(..., mode="a")
  agentic_core\L0_routing\enforcement\mutation_prohibition.py:259:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L0_routing\enforcement\mutation_prohibition.py:271:DIRECT_PATH_WRITE - Path.write_bytes(...)
  agentic_core\L0_routing\enforcement\mutation_prohibition.py:286:DIRECT_OPEN_WRITE - open(..., mode="w")
  agentic_core\L0_routing\enforcement\mutation_prohibition.py:286:DIRECT_WITH_WRITE - with open(..., mode="w")
  agentic_core\L0_routing\meta_control\meta_apply.py:148:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L0_routing\reasoning\SSOTFolderCleanupAgent.py:411:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L0_routing\scripts\add_dataclass_to_agents_util.py:119:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L0_routing\scripts\add_subatomic_safe_util.py:128:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L0_routing\scripts\add_subatomic_testing_to_agents_util.py:113:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L0_routing\scripts\add_subatomic_tests_util.py:147:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L0_routing\scripts\agent_analysis_config.py:308:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L0_routing\scripts\agent_capability_supplement_util.py:407:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L0_routing\scripts\align_tests_structure_util.py:42:DIRECT_OPEN_WRITE - open(..., mode="w")
  agentic_core\L0_routing\scripts\align_tests_structure_util.py:42:DIRECT_WITH_WRITE - with open(..., mode="w")
  agentic_core\L0_routing\scripts\align_tests_structure_util.py:49:DIRECT_OPEN_WRITE - open(..., mode="w")
  agentic_core\L0_routing\scripts\align_tests_structure_util.py:49:DIRECT_WITH_WRITE - with open(..., mode="w")
  agentic_core\L0_routing\scripts\auto_remediate_signatures_util.py:138:DIRECT_OPEN_WRITE - open(..., mode="w")
  agentic_core\L0_routing\scripts\auto_remediate_signatures_util.py:138:DIRECT_WITH_WRITE - with open(..., mode="w")
  agentic_core\L0_routing\scripts\bulk_hierarchy_heal_util.py:54:DIRECT_OPEN_WRITE - open(..., mode="a")
  agentic_core\L0_routing\scripts\bulk_hierarchy_heal_util.py:54:DIRECT_WITH_WRITE - with open(..., mode="a")
  agentic_core\L0_routing\scripts\bulk_hierarchy_heal_util.py:69:DIRECT_OPEN_WRITE - open(..., mode="w")
  agentic_core\L0_routing\scripts\bulk_hierarchy_heal_util.py:69:DIRECT_WITH_WRITE - with open(..., mode="w")
  agentic_core\L0_routing\scripts\bulk_mcp_harden_util.py:62:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L0_routing\scripts\bulk_mcp_harden_util.py:80:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L0_routing\scripts\c_c_measurement.py:179:DIRECT_OPEN_WRITE - open(..., mode="w")
  agentic_core\L0_routing\scripts\c_c_measurement.py:179:DIRECT_WITH_WRITE - with open(..., mode="w")
  agentic_core\L0_routing\scripts\class_info.py:699:DIRECT_OPEN_WRITE - open(..., mode="w")
  agentic_core\L0_routing\scripts\class_info.py:699:DIRECT_WITH_WRITE - with open(..., mode="w")
  agentic_core\L0_routing\scripts\class_info.py:733:DIRECT_OPEN_WRITE - open(..., mode="w")
  agentic_core\L0_routing\scripts\class_info.py:733:DIRECT_WITH_WRITE - with open(..., mode="w")
  agentic_core\L0_routing\scripts\code_entity.py:541:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L0_routing\scripts\colors.py:165:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L0_routing\scripts\core_synthesis_executor.py:247:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L0_routing\scripts\core_synthesis_executor.py:361:DIRECT_OPEN_WRITE - open(..., mode="w")
  agentic_core\L0_routing\scripts\core_synthesis_executor.py:361:DIRECT_WITH_WRITE - with open(..., mode="w")
  agentic_core\L0_routing\scripts\disposition.py:437:DIRECT_OPEN_WRITE - open(..., mode="w")
  agentic_core\L0_routing\scripts\disposition.py:437:DIRECT_WITH_WRITE - with open(..., mode="w")
  agentic_core\L0_routing\scripts\disposition.py:458:DIRECT_OPEN_WRITE - open(..., mode="w")
  agentic_core\L0_routing\scripts\disposition.py:458:DIRECT_WITH_WRITE - with open(..., mode="w")
  agentic_core\L0_routing\scripts\emoji_fixer.py:53:DIRECT_OPEN_WRITE - open(..., mode="w")
  agentic_core\L0_routing\scripts\emoji_fixer.py:53:DIRECT_WITH_WRITE - with open(..., mode="w")
  agentic_core\L0_routing\scripts\execute_ssot.py:2451:DIRECT_OPEN_WRITE - open(..., mode="w")
  agentic_core\L0_routing\scripts\execute_ssot.py:2451:DIRECT_WITH_WRITE - with open(..., mode="w")
  agentic_core\L0_routing\scripts\execute_ssot.py:2456:DIRECT_OPEN_WRITE - open(..., mode="w")
  agentic_core\L0_routing\scripts\execute_ssot.py:2456:DIRECT_WITH_WRITE - with open(..., mode="w")
  agentic_core\L0_routing\scripts\find_real_duplicates_v2_util.py:98:DIRECT_OPEN_WRITE - open(..., mode="w")
  agentic_core\L0_routing\scripts\find_real_duplicates_v2_util.py:98:DIRECT_WITH_WRITE - with open(..., mode="w")
  agentic_core\L0_routing\scripts\fission_executor_util.py:50:DIRECT_OPEN_WRITE - open(..., mode="w")
  agentic_core\L0_routing\scripts\fission_executor_util.py:50:DIRECT_WITH_WRITE - with open(..., mode="w")
  agentic_core\L0_routing\scripts\fission_executor_util.py:75:DIRECT_OPEN_WRITE - open(..., mode="w")
  agentic_core\L0_routing\scripts\fission_executor_util.py:75:DIRECT_WITH_WRITE - with open(..., mode="w")
  agentic_core\L0_routing\scripts\forensic_discovery_prep.py:316:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L0_routing\scripts\generate_dashboard_ssot_util.py:399:DIRECT_OPEN_WRITE - open(..., mode="w")
  agentic_core\L0_routing\scripts\generate_dashboard_ssot_util.py:399:DIRECT_WITH_WRITE - with open(..., mode="w")
  agentic_core\L0_routing\scripts\generate_dashboard_ssot_util.py:413:DIRECT_OPEN_WRITE - open(..., mode="w")
  agentic_core\L0_routing\scripts\generate_dashboard_ssot_util.py:413:DIRECT_WITH_WRITE - with open(..., mode="w")
  agentic_core\L0_routing\scripts\populate_ssot_folders_util.py:162:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L0_routing\scripts\populate_ssot_folders_util.py:172:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L0_routing\scripts\scan_testing_compliance_util.py:348:DIRECT_OPEN_WRITE - open(..., mode="w")
  agentic_core\L0_routing\scripts\scan_testing_compliance_util.py:348:DIRECT_WITH_WRITE - with open(..., mode="w")
  agentic_core\L0_routing\scripts\ssot_cli.py:168:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L0_routing\scripts\verify_intentional_variants_util.py:343:DIRECT_OPEN_WRITE - open(..., mode="w")
  agentic_core\L0_routing\scripts\verify_intentional_variants_util.py:343:DIRECT_WITH_WRITE - with open(..., mode="w")
  agentic_core\L0_routing\types\guardian_contract.py:937:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L0_routing\types\guardian_contract_types.py:937:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L0_routing\types\integration_contract.py:81:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L0_routing\types\integration_contract_types.py:81:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L0_routing\utils\add_test_coverage_util.py:71:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L0_routing\utils\add_test_coverage_util.py:433:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L0_routing\utils\complexity_visitor_util.py:1669:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L0_routing\utils\complexity_visitor_util.py:1691:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L0_routing\utils\core_integrity_util.py:93:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L0_routing\utils\core_integrity_util.py:152:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L0_routing\utils\file_utils_util.py:96:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L0_routing\utils\file_utils_util.py:125:DIRECT_OPEN_WRITE - open(..., mode="a")
  agentic_core\L0_routing\utils\file_utils_util.py:125:DIRECT_WITH_WRITE - with open(..., mode="a")
  agentic_core\L0_routing\utils\fix_depth_violations_util.py:51:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L0_routing\utils\fix_mission_runner_util.py:40:DIRECT_OPEN_WRITE - open(..., mode="w")
  agentic_core\L0_routing\utils\fix_mission_runner_util.py:40:DIRECT_WITH_WRITE - with open(..., mode="w")
  agentic_core\L0_routing\utils\fix_remaining_depth_util.py:25:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L0_routing\utils\fix_remaining_depth_util.py:42:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L0_routing\utils\manifest_guardian_util.py:41:DIRECT_OPEN_WRITE - open(..., mode="w")
  agentic_core\L0_routing\utils\manifest_guardian_util.py:41:DIRECT_WITH_WRITE - with open(..., mode="w")
  agentic_core\L0_routing\utils\sovereign_alignment_v2_util.py:54:DIRECT_OPEN_WRITE - open(..., mode="w")
  agentic_core\L0_routing\utils\sovereign_alignment_v2_util.py:54:DIRECT_WITH_WRITE - with open(..., mode="w")
  agentic_core\L0_routing\utils\sovereign_alignment_v2_util.py:79:DIRECT_OPEN_WRITE - open(..., mode="w")
  agentic_core\L0_routing\utils\sovereign_alignment_v2_util.py:79:DIRECT_WITH_WRITE - with open(..., mode="w")
  agentic_core\L0_routing\utils\sovereign_convergence_util.py:58:DIRECT_OPEN_WRITE - open(..., mode="w")
  agentic_core\L0_routing\utils\sovereign_convergence_util.py:58:DIRECT_WITH_WRITE - with open(..., mode="w")
  agentic_core\L0_routing\utils\structural_fix_util.py:39:DIRECT_OPEN_WRITE - open(..., mode="w")
  agentic_core\L0_routing\utils\structural_fix_util.py:39:DIRECT_WITH_WRITE - with open(..., mode="w")
  agentic_core\L0_routing\utils\structural_fix_util.py:61:DIRECT_OPEN_WRITE - open(..., mode="w")
  agentic_core\L0_routing\utils\structural_fix_util.py:61:DIRECT_WITH_WRITE - with open(..., mode="w")
  agentic_core\L0_routing\utils\trim_remaining_airlocks_util.py:54:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L3_orchestration\enforcement\mission_runner.py:576:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L3_orchestration\enforcement\mission_runner_enforcer.py:576:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L3_orchestration\engines\sovereign_rag_orchestrator.py:141:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L3_orchestration\types\telepathy_interface_types.py:141:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L4_state\storage\filesystem_store.py:115:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L4_state\utils\experience_buffer_util.py:62:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L4_state\utils\experience_buffer_util.py:98:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L5_safety\config\gravity_leak_config.py:257:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L5_safety\config\structure_blueprint\enforcement\blueprint_hash.py:61:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L5_safety\enforcement\agent_info.py:504:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L5_safety\enforcement\agent_info_enforcer.py:504:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L5_safety\enforcement\airlock_trimmer.py:47:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L5_safety\enforcement\airlock_trimmer_enforcer.py:47:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L5_safety\enforcement\fast_dashboard_e2_e_pipeline.py:118:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L5_safety\enforcement\fast_dashboard_e2_e_pipeline.py:195:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L5_safety\enforcement\fast_dashboard_e2_e_pipeline_enforcer.py:118:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L5_safety\enforcement\fast_dashboard_e2_e_pipeline_enforcer.py:195:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L5_safety\enforcement\final_airlock_trimmer.py:31:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L5_safety\enforcement\final_airlock_trimmer_enforcer.py:31:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L5_safety\enforcement\hardcoded_path_refactorer.py:194:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L5_safety\enforcement\hardcoded_path_refactorer_enforcer.py:194:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L5_safety\enforcement\mutation_prohibition.py:93:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L5_safety\enforcement\mutation_prohibition.py:105:DIRECT_PATH_WRITE - Path.write_bytes(...)
  agentic_core\L5_safety\enforcement\mutation_prohibition_enforcer.py:93:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L5_safety\enforcement\mutation_prohibition_enforcer.py:105:DIRECT_PATH_WRITE - Path.write_bytes(...)
  agentic_core\L5_safety\enforcement\pytest_config_guard.py:263:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L5_safety\enforcement\pytest_config_guard.py:271:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L5_safety\enforcement\pytest_config_guard.py:293:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L5_safety\enforcement\pytest_config_guard.py:301:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L5_safety\enforcement\pytest_config_guardrail.py:263:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L5_safety\enforcement\pytest_config_guardrail.py:271:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L5_safety\enforcement\pytest_config_guardrail.py:293:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L5_safety\enforcement\pytest_config_guardrail.py:301:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L5_safety\enforcement\sovereign_healing_engine.py:162:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L5_safety\enforcement\sovereign_healing_engine.py:199:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L5_safety\enforcement\sovereign_healing_engine.py:228:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L5_safety\enforcement\sovereign_healing_engine.py:264:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L5_safety\enforcement\sovereign_healing_engine_enforcer.py:162:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L5_safety\enforcement\sovereign_healing_engine_enforcer.py:199:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L5_safety\enforcement\sovereign_healing_engine_enforcer.py:228:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L5_safety\enforcement\sovereign_healing_engine_enforcer.py:264:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L5_safety\enforcement\ssot_import_enforcer.py:73:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L5_safety\reasoning\AutonomyGuardianAgent.py:248:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L5_safety\reasoning\CodeDeduplicationAgent.py:350:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L5_safety\reasoning\CodeDeduplicationAgent.py:386:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L5_safety\reasoning\CodeDeduplicationAgent.py:998:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L5_safety\reasoning\CodeEnforcerAgent.py:426:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L5_safety\reasoning\DependencyPruningAgent.py:124:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L5_safety\reasoning\DocstringComplianceAgent.py:118:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L5_safety\reasoning\DynamicSealAgent.py:252:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L5_safety\reasoning\FileClassificationAgent.py:3979:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L5_safety\reasoning\FileClassificationAgent.py:4033:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L5_safety\reasoning\FileClassificationAgent.py:4078:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L5_safety\reasoning\FileClassificationAgent.py:4128:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L5_safety\reasoning\GravityLeakRepairAgent.py:288:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L5_safety\reasoning\HierarchyAgent.py:1169:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L5_safety\reasoning\L5SafetyExerciserAgent.py:164:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L5_safety\reasoning\LocationHealerAgent.py:571:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L5_safety\reasoning\LocationHealerAgent.py:710:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L5_safety\reasoning\LocationHealerAgent.py:1178:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L5_safety\reasoning\LocationHealerAgent.py:1426:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L5_safety\reasoning\LocationHealerAgent.py:1693:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L5_safety\reasoning\LocationHealerAgent.py:2120:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L5_safety\reasoning\PreCommitSovereignAgent.py:318:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L5_safety\reasoning\StructureEnforcerAgent.py:393:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L5_safety\reasoning\StructureHealerAgent.py:217:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L5_safety\reasoning\StructureHealerAgent.py:271:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L5_safety\reasoning\TestGeneratorAgent.py:100:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L5_safety\types\heal_llm_seam.py:298:DIRECT_PATH_WRITE - Path.write_bytes(...)
  agentic_core\L5_safety\utils\cognitive_batch_processor_util.py:103:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L5_safety\utils\fix_inherited_invocation_util.py:120:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L5_safety\utils\force_app_depth_util.py:70:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L5_safety\utils\set_complexity_health_100_util.py:64:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L5_safety\utils\tiered_batch_util.py:95:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L5_safety\utils\unified_cst_healer_util.py:371:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L6_observability\dashboards\dashboard_generator.py:831:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L6_observability\enforcement\reasoning_streamer.py:29:DIRECT_OPEN_WRITE - open(..., mode="w")
  agentic_core\L6_observability\enforcement\reasoning_streamer_enforcer.py:29:DIRECT_OPEN_WRITE - open(..., mode="w")
  agentic_core\L6_observability\utils\fix_testing_observability_util.py:98:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L6_observability\utils\fix_testing_observability_util.py:152:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\L6_observability\utils\integrity_report_generator_util.py:387:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\interfaces\IBlackboardLeaseVerifier.py:242:DIRECT_OPEN_WRITE - open(..., mode="w")
  agentic_core\interfaces\IBlackboardLeaseVerifier.py:242:DIRECT_WITH_WRITE - with open(..., mode="w")
  agentic_core\interfaces\IBlackboardLeaseVerifierProtocol.py:242:DIRECT_OPEN_WRITE - open(..., mode="w")
  agentic_core\interfaces\IBlackboardLeaseVerifierProtocol.py:242:DIRECT_WITH_WRITE - with open(..., mode="w")
  agentic_core\mixins\atomic_execution_mixin.py:285:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\mixins\cst_healer_mixin.py:275:DIRECT_PATH_WRITE - Path.write_text(...)
  agentic_core\prompt_governance\core\prompt_assembler.py:631:DIRECT_OPEN_WRITE - open(..., mode="w")
  agentic_core\prompt_governance\core\prompt_assembler.py:631:DIRECT_WITH_WRITE - with open(..., mode="w")
  agentic_core\prompt_governance\scripts\harden_templates.py:124:DIRECT_OPEN_WRITE - open(..., mode="w")
  agentic_core\prompt_governance\scripts\harden_templates.py:124:DIRECT_WITH_WRITE - with open(..., mode="w")
  agentic_core\prompt_governance\scripts\synchronize_registry_hashes.py:30:DIRECT_OPEN_WRITE - open(..., mode="w")
  agentic_core\prompt_governance\scripts\synchronize_registry_hashes.py:30:DIRECT_WITH_WRITE - with open(..., mode="w")
  agentic_core\runtime\config\prompt_injection_loader_config.py:196:DIRECT_OPEN_WRITE - open(..., mode="w")
  agentic_core\runtime\config\prompt_injection_loader_config.py:196:DIRECT_WITH_WRITE - with open(..., mode="w")

3. Scanning for non-deterministic serialization...
OK: Determinism Serialization: No violations found

4. Scanning for PTC invariants...
OK: PTC Invariants: No violations found

=== Summary ===
Total violations: 254 (254 new)
FAIL: 254 new violations found
FAIL: Please fix new violations before proceeding


## PTC_TEST_RUN_1

### pytest -q tests/unit_min_deps/ -k "ptc"
EXIT CODE: 0
STDOUT:
[1m============================= test session starts =============================[0m
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 511 items / 447 deselected / 64 selected

tests/unit_min_deps/test_ptc.py::test_tool_arg_validation [32mPASSED[0m[32m         [  3%][0m
tests/unit_min_deps/test_ptc.py::test_tool_spec_validation [32mPASSED[0m[32m        [  6%][0m
tests/unit_min_deps/test_ptc.py::test_tool_call_validation [32mPASSED[0m[32m        [ 10%][0m
tests/unit_min_deps/test_ptc.py::test_deterministic_registry_listing [32mPASSED[0m[32m [ 13%][0m
tests/unit_min_deps/test_ptc.py::test_duplicate_tool_id_rejected [32mPASSED[0m[32m  [ 17%][0m
tests/unit_min_deps/test_ptc.py::test_unsorted_args_rejected [32mPASSED[0m[32m      [ 20%][0m
tests/unit_min_deps/test_ptc.py::test_call_id_stable [32mPASSED[0m[32m              [ 24%][0m
tests/unit_min_deps/test_ptc.py::test_canonical_json [32mPASSED[0m[32m              [ 27%][0m
tests/unit_min_deps/test_ptc.py::test_sha256_hex [32mPASSED[0m[32m                  [ 31%][0m
tests/unit_min_deps/test_ptc.py::test_tool_spec_serialization [32mPASSED[0m[32m     [ 34%][0m
tests/unit_min_deps/test_ptc.py::test_global_registry [32mPASSED[0m[32m             [ 37%][0m
tests/unit_min_deps/test_ptc.py::test_tool_invoker_validation [32mPASSED[0m[32m     [ 41%][0m
tests/unit_min_deps/test_ptc.py::test_tool_invoker_powershell_ban [32mPASSED[0m[32m [ 44%][0m
tests/unit_min_deps/test_ptc.py::test_tool_invoker_truncation [32mPASSED[0m[32m     [ 48%][0m
tests/unit_min_deps/test_ptc.py::test_tool_call_store [32mPASSED[0m[32m             [ 51%][0m
tests/unit_min_deps/test_ptc.py::test_tool_call_store_deterministic_ordering [32mPASSED[0m[32m [ 55%][0m
tests/unit_min_deps/test_ptc.py::test_builtin_repo_rg_tool [32mPASSED[0m[32m        [ 58%][0m
tests/unit_min_deps/test_ptc.py::test_builtin_expr_eval_tool [32mPASSED[0m[32m      [ 62%][0m
tests/unit_min_deps/test_ptc.py::test_builtin_tools_deterministic [32mPASSED[0m[33m [ 65%][0m
tests/unit_min_deps/test_ptc.py::test_builtin_tools_registration [32mPASSED[0m[33m  [ 68%][0m
tests/unit_min_deps/test_ptc.py::test_execute_ssot_ptc_integration [32mPASSED[0m[33m [ 72%][0m
tests/unit_min_deps/test_ptc.py::test_ptc_plan_output_stable [32mPASSED[0m[33m      [ 75%][0m
tests/unit_min_deps/test_ptc.py::test_ptc_invariants_scanner [32mPASSED[0m[33m      [ 79%][0m
tests/unit_min_deps/test_ptc.py::test_static_includes_ptc [32mPASSED[0m[33m         [ 82%][0m
tests/unit_min_deps/test_ptc_write_contract.py::TestPTCWriteContract::test_tool_registry_exists_and_must_route_via_write_gateway [32mPASSED[0m[33m [ 86%][0m
tests/unit_min_deps/test_ptc_write_contract.py::TestPTCWriteContract::test_write_gateway_is_canonical_write_layer [32mPASSED[0m[33m [ 89%][0m
tests/unit_min_deps/test_ptc_write_contract.py::TestPTCWriteContract::test_write_gateway_functions_accept_allow_override [32mPASSED[0m[33m [ 93%][0m
tests/unit_min_deps/test_ptc_write_contract.py::TestPTCWriteContract::test_future_tool_contract_enforcement_ready [32mPASSED[0m[33m [ 96%][0m
tests/unit_min_deps/test_ptc_write_contract.py::TestPTCWriteContract::test_l2_execution_tools_do_not_expose_raw_write_primitives [32mPASSED[0m[33m [100%][0m

[33m============================== warnings summary ===============================[0m
tests/unit_min_deps/test_ptc.py: 19 warnings
  C:\Git\Agentic-Workflow\agentic_core\L3_orchestration\ptc\builtin_tools.py:219: DeprecationWarning: ast.Num is deprecated and will be removed in Python 3.14; use ast.Constant instead
    if isinstance(node, ast.Num):  # Python < 3.8

tests/unit_min_deps/test_ptc.py::test_builtin_expr_eval_tool
tests/unit_min_deps/test_ptc.py::test_builtin_expr_eval_tool
tests/unit_min_deps/test_ptc.py::test_builtin_expr_eval_tool
tests/unit_min_deps/test_ptc.py::test_builtin_expr_eval_tool
tests/unit_min_deps/test_ptc.py::test_builtin_expr_eval_tool
tests/unit_min_deps/test_ptc.py::test_builtin_expr_eval_tool
tests/unit_min_deps/test_ptc.py::test_builtin_tools_deterministic
tests/unit_min_deps/test_ptc.py::test_builtin_tools_deterministic
  C:\Git\Agentic-Workflow\agentic_core\L3_orchestration\ptc\builtin_tools.py:223: DeprecationWarning: ast.Str is deprecated and will be removed in Python 3.14; use ast.Constant instead
    elif isinstance(node, ast.Str):  # Python < 3.8

tests/unit_min_deps/test_ptc.py::test_builtin_expr_eval_tool
tests/unit_min_deps/test_ptc.py::test_builtin_expr_eval_tool
tests/unit_min_deps/test_ptc.py::test_builtin_expr_eval_tool
tests/unit_min_deps/test_ptc.py::test_builtin_expr_eval_tool
tests/unit_min_deps/test_ptc.py::test_builtin_expr_eval_tool
tests/unit_min_deps/test_ptc.py::test_builtin_expr_eval_tool
tests/unit_min_deps/test_ptc.py::test_builtin_tools_deterministic
tests/unit_min_deps/test_ptc.py::test_builtin_tools_deterministic
  C:\Git\Agentic-Workflow\agentic_core\L3_orchestration\ptc\builtin_tools.py:225: DeprecationWarning: ast.NameConstant is deprecated and will be removed in Python 3.14; use ast.Constant instead
    elif isinstance(node, ast.NameConstant):

tests/unit_min_deps/test_ptc.py: 10 warnings
  C:\Git\Agentic-Workflow\agentic_core\L3_orchestration\ptc\builtin_tools.py:220: DeprecationWarning: Attribute n is deprecated and will be removed in Python 3.14; use value instead
    return node.n

tests/unit_min_deps/test_ptc.py::test_ptc_invariants_scanner
tests/unit_min_deps/test_ptc.py::test_ptc_invariants_scanner
  C:\Git\Agentic-Workflow\agentic_core\L5_safety\static_checks\ptc_invariants.py:64: DeprecationWarning: ast.Str is deprecated and will be removed in Python 3.14; use ast.Constant instead
    if isinstance(arg, ast.Str) or isinstance(arg, ast.Constant):

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== GUARDIAN LAYER SUMMARY ============================
Guardian tests run: 1
Passed: 29
Failed: 0
Errors: 0

\u2705 GUARDIAN STATUS: PASS
All architectural integrity checks passed.
======================================  =======================================
============================ slowest 10 durations =============================
40.20s call     tests/unit_min_deps/test_ptc.py::test_static_includes_ptc
0.21s call     tests/unit_min_deps/test_ptc.py::test_ptc_invariants_scanner
0.18s call     tests/unit_min_deps/test_ptc.py::test_ptc_plan_output_stable
0.09s call     tests/unit_min_deps/test_ptc.py::test_execute_ssot_ptc_integration
0.07s call     tests/unit_min_deps/test_ptc_write_contract.py::TestPTCWriteContract::test_tool_registry_exists_and_must_route_via_write_gateway
0.01s call     tests/unit_min_deps/test_ptc.py::test_builtin_repo_rg_tool
0.01s call     tests/unit_min_deps/test_ptc_write_contract.py::TestPTCWriteContract::test_l2_execution_tools_do_not_expose_raw_write_primitives

(3 durations < 0.005s hidden.  Use -vv to show these durations.)
[33m============== [32m29 passed[0m, [33m[1m447 deselected[0m, [33m[1m47 warnings[0m[33m in 40.97s[0m[33m ===============[0m


## PTC_TEST_RUN_2

### pytest -q tests/unit_min_deps/ -k "ptc"
EXIT CODE: 0
STDOUT:
[1m============================= test session starts =============================[0m
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 511 items / 447 deselected / 64 selected

tests/unit_min_deps/test_ptc.py::test_tool_arg_validation [32mPASSED[0m[32m         [  3%][0m
tests/unit_min_deps/test_ptc.py::test_tool_spec_validation [32mPASSED[0m[32m        [  6%][0m
tests/unit_min_deps/test_ptc.py::test_tool_call_validation [32mPASSED[0m[32m        [ 10%][0m
tests/unit_min_deps/test_ptc.py::test_deterministic_registry_listing [32mPASSED[0m[32m [ 13%][0m
tests/unit_min_deps/test_ptc.py::test_duplicate_tool_id_rejected [32mPASSED[0m[32m  [ 17%][0m
tests/unit_min_deps/test_ptc.py::test_unsorted_args_rejected [32mPASSED[0m[32m      [ 20%][0m
tests/unit_min_deps/test_ptc.py::test_call_id_stable [32mPASSED[0m[32m              [ 24%][0m
tests/unit_min_deps/test_ptc.py::test_canonical_json [32mPASSED[0m[32m              [ 27%][0m
tests/unit_min_deps/test_ptc.py::test_sha256_hex [32mPASSED[0m[32m                  [ 31%][0m
tests/unit_min_deps/test_ptc.py::test_tool_spec_serialization [32mPASSED[0m[32m     [ 34%][0m
tests/unit_min_deps/test_ptc.py::test_global_registry [32mPASSED[0m[32m             [ 37%][0m
tests/unit_min_deps/test_ptc.py::test_tool_invoker_validation [32mPASSED[0m[32m     [ 41%][0m
tests/unit_min_deps/test_ptc.py::test_tool_invoker_powershell_ban [32mPASSED[0m[32m [ 44%][0m
tests/unit_min_deps/test_ptc.py::test_tool_invoker_truncation [32mPASSED[0m[32m     [ 48%][0m
tests/unit_min_deps/test_ptc.py::test_tool_call_store [32mPASSED[0m[32m             [ 51%][0m
tests/unit_min_deps/test_ptc.py::test_tool_call_store_deterministic_ordering [32mPASSED[0m[32m [ 55%][0m
tests/unit_min_deps/test_ptc.py::test_builtin_repo_rg_tool [32mPASSED[0m[32m        [ 58%][0m
tests/unit_min_deps/test_ptc.py::test_builtin_expr_eval_tool [32mPASSED[0m[32m      [ 62%][0m
tests/unit_min_deps/test_ptc.py::test_builtin_tools_deterministic [32mPASSED[0m[33m [ 65%][0m
tests/unit_min_deps/test_ptc.py::test_builtin_tools_registration [32mPASSED[0m[33m  [ 68%][0m
tests/unit_min_deps/test_ptc.py::test_execute_ssot_ptc_integration [32mPASSED[0m[33m [ 72%][0m
tests/unit_min_deps/test_ptc.py::test_ptc_plan_output_stable [32mPASSED[0m[33m      [ 75%][0m
tests/unit_min_deps/test_ptc.py::test_ptc_invariants_scanner [32mPASSED[0m[33m      [ 79%][0m
tests/unit_min_deps/test_ptc.py::test_static_includes_ptc [32mPASSED[0m[33m         [ 82%][0m
tests/unit_min_deps/test_ptc_write_contract.py::TestPTCWriteContract::test_tool_registry_exists_and_must_route_via_write_gateway [32mPASSED[0m[33m [ 86%][0m
tests/unit_min_deps/test_ptc_write_contract.py::TestPTCWriteContract::test_write_gateway_is_canonical_write_layer [32mPASSED[0m[33m [ 89%][0m
tests/unit_min_deps/test_ptc_write_contract.py::TestPTCWriteContract::test_write_gateway_functions_accept_allow_override [32mPASSED[0m[33m [ 93%][0m
tests/unit_min_deps/test_ptc_write_contract.py::TestPTCWriteContract::test_future_tool_contract_enforcement_ready [32mPASSED[0m[33m [ 96%][0m
tests/unit_min_deps/test_ptc_write_contract.py::TestPTCWriteContract::test_l2_execution_tools_do_not_expose_raw_write_primitives [32mPASSED[0m[33m [100%][0m

[33m============================== warnings summary ===============================[0m
tests/unit_min_deps/test_ptc.py: 19 warnings
  C:\Git\Agentic-Workflow\agentic_core\L3_orchestration\ptc\builtin_tools.py:219: DeprecationWarning: ast.Num is deprecated and will be removed in Python 3.14; use ast.Constant instead
    if isinstance(node, ast.Num):  # Python < 3.8

tests/unit_min_deps/test_ptc.py::test_builtin_expr_eval_tool
tests/unit_min_deps/test_ptc.py::test_builtin_expr_eval_tool
tests/unit_min_deps/test_ptc.py::test_builtin_expr_eval_tool
tests/unit_min_deps/test_ptc.py::test_builtin_expr_eval_tool
tests/unit_min_deps/test_ptc.py::test_builtin_expr_eval_tool
tests/unit_min_deps/test_ptc.py::test_builtin_expr_eval_tool
tests/unit_min_deps/test_ptc.py::test_builtin_tools_deterministic
tests/unit_min_deps/test_ptc.py::test_builtin_tools_deterministic
  C:\Git\Agentic-Workflow\agentic_core\L3_orchestration\ptc\builtin_tools.py:223: DeprecationWarning: ast.Str is deprecated and will be removed in Python 3.14; use ast.Constant instead
    elif isinstance(node, ast.Str):  # Python < 3.8

tests/unit_min_deps/test_ptc.py::test_builtin_expr_eval_tool
tests/unit_min_deps/test_ptc.py::test_builtin_expr_eval_tool
tests/unit_min_deps/test_ptc.py::test_builtin_expr_eval_tool
tests/unit_min_deps/test_ptc.py::test_builtin_expr_eval_tool
tests/unit_min_deps/test_ptc.py::test_builtin_expr_eval_tool
tests/unit_min_deps/test_ptc.py::test_builtin_expr_eval_tool
tests/unit_min_deps/test_ptc.py::test_builtin_tools_deterministic
tests/unit_min_deps/test_ptc.py::test_builtin_tools_deterministic
  C:\Git\Agentic-Workflow\agentic_core\L3_orchestration\ptc\builtin_tools.py:225: DeprecationWarning: ast.NameConstant is deprecated and will be removed in Python 3.14; use ast.Constant instead
    elif isinstance(node, ast.NameConstant):

tests/unit_min_deps/test_ptc.py: 10 warnings
  C:\Git\Agentic-Workflow\agentic_core\L3_orchestration\ptc\builtin_tools.py:220: DeprecationWarning: Attribute n is deprecated and will be removed in Python 3.14; use value instead
    return node.n

tests/unit_min_deps/test_ptc.py::test_ptc_invariants_scanner
tests/unit_min_deps/test_ptc.py::test_ptc_invariants_scanner
  C:\Git\Agentic-Workflow\agentic_core\L5_safety\static_checks\ptc_invariants.py:64: DeprecationWarning: ast.Str is deprecated and will be removed in Python 3.14; use ast.Constant instead
    if isinstance(arg, ast.Str) or isinstance(arg, ast.Constant):

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== GUARDIAN LAYER SUMMARY ============================
Guardian tests run: 1
Passed: 29
Failed: 0
Errors: 0

\u2705 GUARDIAN STATUS: PASS
All architectural integrity checks passed.
======================================  =======================================
============================ slowest 10 durations =============================
38.56s call     tests/unit_min_deps/test_ptc.py::test_static_includes_ptc
0.21s call     tests/unit_min_deps/test_ptc.py::test_ptc_invariants_scanner
0.17s call     tests/unit_min_deps/test_ptc.py::test_ptc_plan_output_stable
0.09s call     tests/unit_min_deps/test_ptc.py::test_execute_ssot_ptc_integration
0.07s call     tests/unit_min_deps/test_ptc_write_contract.py::TestPTCWriteContract::test_tool_registry_exists_and_must_route_via_write_gateway
0.01s call     tests/unit_min_deps/test_ptc.py::test_builtin_repo_rg_tool
0.01s call     tests/unit_min_deps/test_ptc_write_contract.py::TestPTCWriteContract::test_l2_execution_tools_do_not_expose_raw_write_primitives
0.01s call     tests/unit_min_deps/test_ptc.py::test_tool_call_store_deterministic_ordering

(2 durations < 0.005s hidden.  Use -vv to show these durations.)
[33m============== [32m29 passed[0m, [33m[1m447 deselected[0m, [33m[1m47 warnings[0m[33m in 39.35s[0m[33m ===============[0m


## EXECUTE_SSOT_PTC_PLAN

### python -m agentic_core.L0_routing.scripts.execute_ssot_entrypoint --legacy --plan --ptc-plan
EXIT CODE: 0
STDOUT:
PHASE 1: Discovery
  - reconciler.detect_root_drift
    # filesystem SSOT drift detection
  - location.run
    # location validation (confidence gated heal)
  - file_classification.run (validate_only=True, dry_run=True)
    # file classification early detection

PHASE 2: Reconciliation
  - reconciler.heal
    # drift reconciliation (confidence gated)

PHASE 2.5: Structural Alignment & Sovereignty
  - hierarchy.heal_hierarchy
    # hierarchy alignment (confidence gated)
  - file_classification.heal_repository
    # sovereignty purge (confidence gated, not dry_run, not validate)

PHASE 3: Architectural Validation
  - arch_governor.comprehensive_territory_audit
    # territory audit
  - system_architect.validate_core_architecture
    # architecture validation

PHASE 4: Healing
  - arch_governor.generate_healing_plan
    # healing plan generation
  - arch_governor.execute_healing_plan
    # healing plan execution

PHASE 4.5: Additional Agents
  - conversational_repair.scan_violations
    # conversational repair scan
  - root_hygiene.scan_root_violations
    # root hygiene scan (if registered)

PHASE 5: Certification
  - *.aggregate
    # final aggregation and certification

=== PROGRAMMATIC TOOL CALLING ===
{"artifact_ref":{"kind":"tool_call","logical_id":"55a25da241434a526dc174bd6d100c7111d6c352823047510b9aad82b270cbc9","path":"tool_call\\55a25da241434a526dc174bd6d100c7111d6c352823047510b9aad82b270cbc9\\v0001.json","version":1},"summary":"PTC executed 1 tool calls for plan context","tool_calls":[{"args":{"expr":"2 + 3 * 4"},"call_id":"55a25da241434a526dc174bd6d100c7111d6c352823047510b9aad82b270cbc9","exit_code":0,"stderr":"","stdout":"14","tool_id":"expr_eval","truncated":false}]}



## STORED_TOOL_CALL_ARTIFACTS

Found 1 tool call artifacts:
  - expr_eval/55a25da241434a526dc174bd6d100c7111d6c352823047510b9aad82b270cbc9

## SCOPE_VERIFICATION

### git diff --name-only
EXIT CODE: 0
STDOUT:
agentic_core/L0_routing/scripts/execute_ssot.py
agentic_core/L3_orchestration/ptc/tool_call_store.py
agentic_core/L4_state/storage/filesystem_store.py
tests/unit_min_deps/test_ptc.py
tools/run_static_invariants.py


### git status --porcelain
EXIT CODE: 0
STDOUT:
 M agentic_core/L0_routing/scripts/execute_ssot.py
 M agentic_core/L3_orchestration/ptc/tool_call_store.py
 M agentic_core/L4_state/storage/filesystem_store.py
 M tests/unit_min_deps/test_ptc.py
 M tools/run_static_invariants.py
?? docs/reports/plans/DEGRADATION_MATRIX.md
?? docs/store/
