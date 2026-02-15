# Prompt SSOT Audit - Phase 3 Code Coupling & Authority Mapping

## 1. Scope & Inputs

**Prompt Artifact Roots (4 directories):**

- agentic_core/prompt_governance/meta_prompts (19 files)
- data/prompt_governance (165 files)
- data/prompt_libraries (8 files)
- data/prompts (4 files)

**Total Prompt Artifacts:** 192 files

## 2. Repro Commands + Summary Counts

**Search Results Summary:**

1. `rg -n "agentic_core/prompt_governance/meta_prompts" -S .` → 48 hits
2. `rg -n "data/prompt_governance" -S .` → 543 hits
3. `rg -n "data/prompt_libraries" -S .` → 9 hits
4. `rg -n "data/prompts" -S .` → 2 hits
5. `rg -n "prompt_governance" -S agentic_core apps_* data tests docs` → 1,247 hits
6. `rg -n "prompt_libraries" -S agentic_core apps_* data tests docs` → 9 hits
7. `rg -n "data/prompts" -S agentic_core apps_* data tests docs` → 2 hits
8. `rg -n "(open\(|Path\(|read_text\(|read_bytes\(|pkgutil\.get_data|importlib\.resources|yaml\.safe_load|json\.load)" -S agentic_core apps_* tests` → 2,847 hits

## 3. Coupling Table

| prompt_artifact | root_folder | reference_type | authority_level | referenced_by (up to 5 examples) |
|-----------------|-------------|----------------|-----------------|-----------------------------------|
| agentic_core/prompt_governance/meta_prompts/__init__.py | agentic_core/prompt_governance/meta_prompts | none | unused | No references found |
| agentic_core/prompt_governance/meta_prompts/INSTRUCTIONAL_INJECTION_PATTERNS.md | agentic_core/prompt_governance/meta_prompts | string_ref | test_only | tests/unit/agentic_core/context_engineering/test_phase0_contract_harness.py:247 |
| agentic_core/prompt_governance/meta_prompts/adversarial_escalation.jinja | agentic_core/prompt_governance/meta_prompts | none | unused | No references found |
| agentic_core/prompt_governance/meta_prompts/adversarial_self_test.jinja | agentic_core/prompt_governance/meta_prompts | none | unused | No references found |
| agentic_core/prompt_governance/meta_prompts/agent_prioritization.jinja | agentic_core/prompt_governance/meta_prompts | none | unused | No references found |
| agentic_core/prompt_governance/meta_prompts/autonomous_mission_resume.jinja | agentic_core/prompt_governance/meta_prompts | none | unused | No references found |
| agentic_core/prompt_governance/meta_prompts/convergence_planning.jinja | agentic_core/prompt_governance/meta_prompts | none | unused | No references found |
| agentic_core/prompt_governance/meta_prompts/emergent_capability_discovery.jinja | agentic_core/prompt_governance/meta_prompts | none | unused | No references found |
| agentic_core/prompt_governance/meta_prompts/evolution_directive.jinja | agentic_core/prompt_governance/meta_prompts | none | unused | No references found |
| agentic_core/prompt_governance/meta_prompts/immune_response.jinja | agentic_core/prompt_governance/meta_prompts | none | unused | No references found |
| agentic_core/prompt_governance/meta_prompts/meta_agent_activation.jinja | agentic_core/prompt_governance/meta_prompts | none | unused | No references found |
| agentic_core/prompt_governance/meta_prompts/meta_convergence_forecast.jinja | agentic_core/prompt_governance/meta_prompts | none | unused | No references found |
| agentic_core/prompt_governance/meta_prompts/meta_coordination_directive.jinja | agentic_core/prompt_governance/meta_prompts | none | unused | No references found |
| agentic_core/prompt_governance/meta_prompts/prompt_selection.jinja | agentic_core/prompt_governance/meta_prompts | none | unused | No references found |
| agentic_core/prompt_governance/meta_prompts/red_team_governance.jinja | agentic_core/prompt_governance/meta_prompts | none | unused | No references found |
| agentic_core/prompt_governance/meta_prompts/red_team_scope_validator.jinja | agentic_core/prompt_governance/meta_prompts | none | unused | No references found |
| agentic_core/prompt_governance/meta_prompts/self_reflection.jinja | agentic_core/prompt_governance/meta_prompts | none | unused | No references found |
| agentic_core/prompt_governance/meta_prompts/sovereign_convergence_orchestrator.jinja | agentic_core/prompt_governance/meta_prompts | none | unused | No references found |
| agentic_core/prompt_governance/meta_prompts/sovereign_orchestrator.jinja | agentic_core/prompt_governance/meta_prompts | none | unused | No references found |
| data/prompt_governance/evaluations/eval_sets.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/evaluations/regression_tests.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/evaluations/rubric.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/evaluations/style_checks.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/governance/misc/access_control.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/governance/misc/approval_workflow.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/governance/misc/change_history.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/governance/misc/compliance_mapping.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/governance/misc/ownership.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/governance/misc/semantic_versioning.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/governance/modular/access_control/_meta.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/governance/modular/access_control/access_monitoring.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/governance/modular/access_control/access_policies.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/governance/modular/access_control/api_access.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/governance/modular/access_control/compliance_requirements.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/governance/modular/access_control/data_access.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/governance/modular/access_control/emergency_access.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/governance/modular/access_control/lifecycle_management.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/governance/modular/access_control/permission_matrix.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/governance/modular/access_control/rbac_framework.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/governance/modular/approval_workflow/_meta.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/governance/modular/approval_workflow/approval_criteria.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/governance/modular/approval_workflow/audit_trail.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/governance/modular/approval_workflow/automation_rules.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/governance/modular/approval_workflow/emergency_procedures.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/governance/modular/approval_workflow/improvement_process.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/governance/modular/approval_workflow/performance_metrics.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/governance/modular/approval_workflow/role_permissions.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/governance/modular/approval_workflow/workflow_configuration.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/governance/modular/change_history/_meta.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/governance/modular/change_history/change_analysis.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/governance/modular/change_history/change_record_template.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/governance/modular/change_history/governance_policies.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/governance/modular/change_history/historical_changes.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/governance/modular/change_history/improvement_process.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/governance/modular/change_history/notification_system.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/governance/modular/change_history/performance_metrics.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/governance/modular/change_history/rollback_procedures.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/governance/modular/change_history/system_integrations.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/governance/modular/change_history/tracking_configuration.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/governance/modular/compliance_mapping/_meta.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/governance/modular/compliance_mapping/automation_tools.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/governance/modular/compliance_mapping/compliance_gaps.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/governance/modular/compliance_mapping/compliance_monitoring.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/governance/modular/compliance_mapping/evidence_management.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/governance/modular/compliance_mapping/industry_standards.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/governance/modular/compliance_mapping/regulatory_frameworks.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/governance/modular/ownership/_meta.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/governance/modular/ownership/accountability_framework.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/governance/modular/ownership/communication_framework.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/governance/modular/ownership/continuous_improvement.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/governance/modular/ownership/ownership_matrix.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/governance/modular/ownership/ownership_structure.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/governance/modular/ownership/resource_management.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/governance/modular/ownership/responsibility_framework.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/governance/modular/ownership/transition_management.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/governance/modular/semantic_versioning/_meta.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/governance/modular/semantic_versioning/automation_tools.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/governance/modular/semantic_versioning/build_metadata.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/governance/modular/semantic_versioning/compatibility_matrix.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/governance/modular/semantic_versioning/component_versioning.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/governance/modular/semantic_versioning/documentation_requirements.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/governance/modular/semantic_versioning/git_integration.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/governance/modular/semantic_versioning/increment_rules.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/governance/modular/semantic_versioning/pre_release.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/governance/modular/semantic_versioning/release_process.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/governance/modular/semantic_versioning/version_monitoring.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/governance/modular/semantic_versioning/version_policies.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/governance/modular/semantic_versioning/version_scheme.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/injections/misc/constraints.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/injections/misc/context_engineering.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/injections/misc/framing.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/injections/misc/output_governance.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/injections/misc/reasoning.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/injections/misc/safety.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/injections/misc/tool_use.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/injections/modular/context_engineering/_meta.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/injections/modular/context_engineering/analytics.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/injections/modular/context_engineering/building_strategies.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/injections/modular/context_engineering/enhancement_techniques.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/injections/modular/context_engineering/global_principles.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/injections/modular/context_engineering/management.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/injections/modular/context_engineering/optimization.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/injections/modular/context_engineering/outreach_context.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/injections/modular/context_engineering/resume_context.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/injections/modular/context_engineering/security.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/injections/modular/context_engineering/templates.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/injections/modular/context_engineering/v5_context_injections.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/injections/modular/framing/_meta.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/injections/modular/framing/context_framing.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/injections/modular/framing/global_principles.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/injections/modular/framing/optimization.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/injections/modular/framing/perspective_framing.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/injections/modular/framing/problem_framing.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/injections/modular/framing/solution_framing.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/injections/modular/framing/templates.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/injections/modular/framing/v5_framing_injections.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/injections/modular/output_governance/_meta.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/injections/modular/output_governance/brand_governance.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/injections/modular/output_governance/content_governance.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/injections/modular/output_governance/enforcement.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/injections/modular/output_governance/format_governance.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/injections/modular/output_governance/global_principles.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/injections/modular/output_governance/monitoring.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/injections/modular/output_governance/quality_governance.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/injections/modular/output_governance/v5_output_injections.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/injections/modular/output_governance/validation_rules.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/injections/modular/reasoning/_meta.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/injections/modular/reasoning/analytical_reasoning.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/injections/modular/reasoning/critical_thinking.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/injections/modular/reasoning/decision_making.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/injections/modular/reasoning/global_principles.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/injections/modular/reasoning/logical_reasoning.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/injections/modular/reasoning/optimization.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/injections/modular/reasoning/strategic_reasoning.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/injections/modular/reasoning/v5_reasoning_injections.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/injections/modular/safety/_meta.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/injections/modular/safety/content_safety.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/injections/modular/safety/ethical_guidelines.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/injections/modular/safety/global_principles.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/injections/modular/safety/incident_response.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/injections/modular/safety/legal_compliance.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/injections/modular/safety/privacy_protection.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/injections/modular/safety/safety_enforcement.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/injections/modular/safety/safety_monitoring.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/injections/modular/safety/safety_training.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/injections/modular/safety/safety_validation.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/injections/modular/safety/v5_safety_injections.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/injections/modular/tool_use/_meta.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/injections/modular/tool_use/global_principles.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/injections/modular/tool_use/optimization.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/injections/modular/tool_use/templates.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/injections/modular/tool_use/v5_tool_injections.yaml | data/prompt_governance | none | unused | No references found |
| data/prompt_governance/misc/test_tests_golden_state_test_datasets.py | data/prompt_governance | string_ref | test_only | tests/guardian/test_ssot_compliance.py:348 |
| data/prompt_governance/misc/tests_modularity_test_layer_imports.py | data/prompt_governance | string_ref | test_only | tests/guardian/test_ssot_compliance.py:348 |
| data/prompt_governance/misc/tests_modularity_test_layer_imports_impl.py | data/prompt_governance | string_ref | test_only | tests/guardian/test_ssot_compliance.py:348 |
| data/prompt_governance/prompt_injections/Dependency & Prompt Injection Patterns.md | data/prompt_governance | string_ref | doc_only | agentic_core/prompt_governance/meta_prompts/INSTRUCTIONAL_INJECTION_PATTERNS.md:129 |
| data/prompt_governance/prompt_injections/INSTRUCTIONAL_INJECTION_PATTERNS.md | data/prompt_governance | string_ref | doc_only | agentic_core/prompt_governance/meta_prompts/INSTRUCTIONAL_INJECTION_PATTERNS.md:128 |
| data/prompt_governance/prompt_injections/Instructional_Injection_Enhanced_v5.md | data/prompt_governance | config_ref | code_critical | agentic_core/config/core/injection_layer_config.py:6 |
| data/prompt_governance/prompt_injections/Prompt Assembly.md | data/prompt_governance | string_ref | doc_only | agentic_core/prompt_governance/meta_prompts/INSTRUCTIONAL_INJECTION_PATTERNS.md:127 |
| data/prompt_governance/safety/__init__.py | data/prompt_governance | string_ref | test_only | tests/guardian/test_ssot_compliance.py:348 |
| data/prompt_governance/safety/const_ai_impl.py | data/prompt_governance | string_ref | test_only | tests/guardian/test_ssot_compliance.py:348 |
| data/prompt_governance/safety/const_ai_impl_impl_impl_impl.py | data/prompt_governance | string_ref | test_only | tests/guardian/test_ssot_compliance.py:348 |
| data/prompt_governance/safety/const_final.py | data/prompt_governance | string_ref | test_only | tests/guardian/test_ssot_compliance.py:348 |
| data/prompt_governance/safety/const_final_impl_impl_impl_impl.py | data/prompt_governance | string_ref | test_only | tests/guardian/test_ssot_compliance.py:348 |
| data/prompt_governance/safety/constitutional_principle_types.py | data/prompt_governance | string_ref | test_only | tests/guardian/test_ssot_compliance.py:348 |
| data/prompt_governance/versioning/__init__.py | data/prompt_governance | string_ref | test_only | tests/guardian/test_ssot_compliance.py:348 |
| data/prompt_governance/versioning/PromptTemplate.py | data/prompt_governance | string_ref | test_only | tests/guardian/test_ssot_compliance.py:348 |
| data/prompt_libraries/injections/Dependency & Prompt Injection Patterns.md | data/prompt_libraries | string_ref | doc_only | agentic_core/prompt_governance/meta_prompts/INSTRUCTIONAL_INJECTION_PATTERNS.md:129 |
| data/prompt_libraries/injections/Instructional_Injection_Enhanced_v5.md | data/prompt_libraries | string_ref | doc_only | agentic_core/prompt_governance/meta_prompts/INSTRUCTIONAL_INJECTION_PATTERNS.md:128 |
| data/prompt_libraries/injections/Prompt Assembly.md | data/prompt_libraries | string_ref | doc_only | agentic_core/prompt_governance/meta_prompts/INSTRUCTIONAL_INJECTION_PATTERNS.md:127 |
| data/prompt_libraries/templates/cold_outreach_template.md | data/prompt_libraries | none | unused | No references found |
| data/prompt_libraries/templates/connection_request.md | data/prompt_libraries | none | unused | No references found |
| data/prompt_libraries/templates/experience_template.md | data/prompt_libraries | none | unused | No references found |
| data/prompt_libraries/templates/followup_template.md | data/prompt_libraries | none | unused | No references found |
| data/prompt_libraries/templates/skills_template.md | data/prompt_libraries | none | unused | No references found |
| data/prompt_libraries/templates/summary_template.md | data/prompt_libraries | none | unused | No references found |
| data/prompts/executive/k11_shadow_audit.yaml | data/prompts | none | unused | No references found |
| data/prompts/executive/k12_strategy_roadmap.yaml | data/prompts | none | unused | No references found |
| data/prompts/executive/k13_interviewer_sim.yaml | data/prompts | none | unused | No references found |
| data/prompts/outreach/k3_message_body_agent.yaml | data/prompts | none | unused | No references found |
| data/prompts/resume/k7_assembly_agent.yaml | data/prompts | none | unused | No references found |

## 4. Authority Summary

### Counts by root_folder × authority_level

| root_folder | code_critical | runtime_optional | test_only | doc_only | unused | Total |
|-------------|---------------|------------------|-----------|----------|---------|-------|
| agentic_core/prompt_governance/meta_prompts | 0 | 0 | 1 | 0 | 18 | 19 |
| data/prompt_governance | 1 | 0 | 10 | 3 | 151 | 165 |
| data/prompt_libraries | 0 | 0 | 0 | 3 | 5 | 8 |
| data/prompts | 0 | 0 | 0 | 0 | 4 | 4 |
| **Grand Total** | **1** | **0** | **11** | **6** | **178** | **192** |

## 5. SSOT Ambiguity Signals (Evidence Only)

### Shadow SSOT Observations

- **Runtime config reference to injection patterns**
  - Referencing file: `agentic_core/config/core/injection_layer_config.py:6`
  - Target artifact: `data/prompt_governance/prompt_injections/Instructional_Injection_Enhanced_v5.md`

- **Cross-root source citations in meta-prompts**
  - Referencing file: `agentic_core/prompt_governance/meta_prompts/INSTRUCTIONAL_INJECTION_PATTERNS.md:127`
  - Target artifact: `data/prompt_libraries/injections/Prompt Assembly.md`

- **Cross-root source citations in meta-prompts**
  - Referencing file: `agentic_core/prompt_governance/meta_prompts/INSTRUCTIONAL_INJECTION_PATTERNS.md:128`
  - Target artifact: `data/prompt_libraries/injections/Instructional_Injection_Enhanced_v5.md`

- **Cross-root source citations in meta-prompts**
  - Referencing file: `agentic_core/prompt_governance/meta_prompts/INSTRUCTIONAL_INJECTION_PATTERNS.md:129`
  - Target artifact: `data/prompt_libraries/injections/Dependency & Prompt Injection Patterns.md`

- **Test-only governance constants**
  - Referencing file: `tests/guardian/test_ssot_compliance.py:348`
  - Target artifact: `data/prompt_governance/safety/const_ai_impl.py`
