# Overlay Verification — vs `tech_debt_audit.json`

**Generated**: 2026-04-25T00:12:19.763010+00:00
**Overlay snapshot**: `artifacts/adg/adg_debt_overlay_20260425_000925.sqlite`
**Audit snapshot**:   `docs/reports/plans/tech_debt_audit.json`

Each row asks: did the overlay detector and the canonical audit agree on what's debt? `intersection` is items both found; `only_audit` are items the audit found but the overlay missed (potential false negatives); `only_overlay` are items the overlay found that the audit missed (potential false positives, OR genuine new finds).

| Category | Audit | Overlay | ∩ | only_overlay | only_audit | Prec | Rec |
|---|---:|---:|---:|---:|---:|---:|---:|
| `dead_import` | 511 | 515 | 510 | 5 | 1 | 0.99 | 1.00 |
| `namespace_pkg_import` | 2731 | 2741 | 2730 | 11 | 1 | 1.00 | 1.00 |
| `import_error_fallback_stub` | 66 | 69 | 66 | 3 | 0 | 0.96 | 1.00 |
| `module_duplicate` | 53 | 69 | 47 | 22 | 6 | 0.68 | 0.89 |
| `stale_all_export` | 810 | 794 | 794 | 0 | 16 | 1.00 | 0.98 |
| `module_load_action_call` | 589 | 1703 | 585 | 1118 | 4 | 0.34 | 0.99 |
| `rename_shim_module` | 8 | 5 | 4 | 1 | 4 | 0.80 | 0.50 |

## Per-Category Notes

### `dead_import`

- audit found: **511**
- overlay found: **515**
- intersection: **510**
- precision: **0.9902912621359223**, recall: **0.9980430528375733**
- examples in audit but missed by overlay (sample):
    - `('agentic_core/interfaces/IBlackboardLeaseVerifierProtocol.py', 'agentic_core.L5_safety.config.structure_blueprint.ssot')`
- examples in overlay but missed by audit (sample):
    - `('tests/unit/ops_scripts/test_ssot_phases_deleted_wave_f1.py', 'ops_scripts.dev_tools.L0_routing_scripts._ssot_phases')`
    - `('tests/conftest.py', 'agentic_core.L0_routing.scripts')`
    - `('agentic_core/L3_orchestration/reasoning/engines/agent_gym_engine.py', 'agentic_core.L3_orchestration.reasoning.agent_gym_types')`
    - `('tests/ops_scripts/ci/test_adg_gate_policy_enhancement.py', 'ops_scripts.ci.adg_critical_defect_gate')`
    - `('tests/unit/ops_scripts/ci/test_guardian_quality_scanner.py', 'ops_scripts.ci.guardian_quality_scanner')`

### `namespace_pkg_import`

- audit found: **2731**
- overlay found: **2741**
- intersection: **2730**
- precision: **0.9959868661072602**, recall: **0.9996338337605273**
- examples in audit but missed by overlay (sample):
    - `('agentic_core/interfaces/determinism.py', 'agentic_core.runtime.contracts.lifecycle_trace_contract')`
- examples in overlay but missed by audit (sample):
    - `('tests/unit/tools/generate/test_generate_full_adg_failfast.py', 'tools.generate.utils.file_utils')`
    - `('tests/unit/agentic_core/L4_state/enforcement/test_elevator_shaft_consistency_enforcer_behavior.py', 'agentic_core.L6_observability.utils.engines.semantic_clock_validator')`
    - `('apps_exec/_optional_agentic_core.py', 'agentic_core.runtime.contracts.lifecycle_trace_contract')`
    - `('tests/tools/mcp/test_heartbeat_authority.py', 'tools.mcp.mcp_heartbeat')`
    - `('tools/generate/validation/gates.py', 'tools.generate.integration.deferred_failures')`

### `import_error_fallback_stub`

- audit found: **66**
- overlay found: **69**
- intersection: **66**
- precision: **0.9565217391304348**, recall: **1.0**
- examples in overlay but missed by audit (sample):
    - `('agentic_core/interfaces/mixins.py', 'MetaLearningMixin')`
    - `('agentic_core/interfaces/mixins.py', 'HealingPolicyMixin')`
    - `('agentic_core/interfaces/validators.py', 'RuleFailure')`

### `module_duplicate`

- audit found: **53**
- overlay found: **69**
- intersection: **47**
- precision: **0.6811594202898551**, recall: **0.8867924528301887**
- examples in audit but missed by overlay (sample):
    - `('tools/archive/interfaces_dead_code_20260405/IOrchestratorProtocol.py', 'b263da5883e3')`
    - `('agentic_core/adg/analysis/confidence.py', '3743018c926a')`
    - `('docs/reference/Testing/Agentic Testing.py', 'be8ff07e1716')`
    - `('agentic_core/adg/analysis/EdgeConfidence.py', '3743018c926a')`
    - `('tools/reference/Testing/Agentic Testing.py', 'be8ff07e1716')`
- examples in overlay but missed by audit (sample):
    - `('apps_rfp/config/__init__.py', 'fc59eec49d4c')`
    - `('tests/unit/agentic_core/mixins/test_safety_mixin.py', 'c07529daeec8')`
    - `('tools/archive/adg_root_oneshots_w5.10/adg_1653_final_complete_fix.py', '4a4ffd0c4f00')`
    - `('tests/unit/agentic_core/mixins/test_instructional_injection_mixin.py', 'c07529daeec8')`
    - `('tests/unit/agentic_core/prompt_governance/core/test_invariant_registry.py', 'c07529daeec8')`

### `stale_all_export`

- audit found: **810**
- overlay found: **794**
- intersection: **794**
- precision: **1.0**, recall: **0.980246913580247**
- examples in audit but missed by overlay (sample):
    - `('agentic_core/evaluation/judges/llm_judges.py', 'judge_gov_003')`
    - `('apps_shared/enforcement/core/event_bus.py', 'get_event_bus')`
    - `('apps_shared/reasoning/health_check.py', 'initialize_system_health_checks')`
    - `('agentic_core/evaluation/judges/llm_judges.py', 'run_llm_judge')`
    - `('apps_shared/enforcement/circuit_breaker.py', 'get_circuit_breaker_registry')`

### `module_load_action_call`

- audit found: **589**
- overlay found: **1703**
- intersection: **585**
- precision: **0.3435114503816794**, recall: **0.9932088285229203**
- examples in audit but missed by overlay (sample):
    - `('ops_scripts/maintenance/archive_duplicates.py',)`
    - `('ops_scripts/maintenance/execute_convergence.py',)`
    - `('ops_scripts/maintenance/execute_final_consolidation.py',)`
    - `('agentic_core/interfaces/determinism.py',)`
- examples in overlay but missed by audit (sample):
    - `('apps_research/config/agent_spec_config.py',)`
    - `('agentic_core/L2_execution/reasoning/l2_tool_registry.py',)`
    - `('system_learning/engines/trace_feature_extractor.py',)`
    - `('agentic_core/L2_execution/reasoning/SovereignMCPGatewayAgent.py',)`
    - `('agentic_core/mixins/subatomic_testing_mixin.py',)`

### `rename_shim_module`

- audit found: **8**
- overlay found: **5**
- intersection: **4**
- precision: **0.8**, recall: **0.5**
- examples in audit but missed by overlay (sample):
    - `('.windsurf/scripts/pre_author_gate.py',)`
    - `('tools/archive/adg_critical_defect_gate.py',)`
    - `('.windsurf/skills/author-gate-packet-builder/emit_packet.py',)`
    - `('ops_scripts/root_scripts/fix_generated_tests.py',)`
- examples in overlay but missed by audit (sample):
    - `('apps_lic/types/action_call_generator_types.py',)`

## Verdict

- `import_error_fallback_stub`: recall = 100.00% → ✅ FULL
- `namespace_pkg_import`: recall = 99.96% → ✅ FULL
- `dead_import`: recall = 99.80% → ✅ FULL
- `module_load_action_call`: recall = 99.32% → ✅ FULL
- `stale_all_export`: recall = 98.02% → ✅ FULL
- `module_duplicate`: recall = 88.68% → 🟢 STRONG
- `rename_shim_module`: recall = 50.00% → 🟡 PARTIAL

**Headline finding**: each detector category, by category, shows whether the overlay would have caught the canonical audit's findings. Recall ≥ 0.95 means the overlay would have surfaced essentially everything the audit did. Numbers below 0.80 indicate detection logic that needs tuning before upstreaming into the canonical ADG generator.