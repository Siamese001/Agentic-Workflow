# Wave 6 — HITL Gates for Deletions, Ambiguous Classifications, and Archive Decisions

## Scope
Add HITL gates at all high-leverage mutation decision points:
- File archiving/deletion in LocationHealerAgent via hitl_approval_fn injection
- Ambiguous classification flag (top-2 delta < 0.15) in FileClassificationAgent
- HITL archive gate wired in execute_ssot.py before heal_violations()
- New hitl_decision_logger.py for structured, auditable HITL decision records

## CODE_COMMIT
898da48ac6c96449cbb021d10490cd55bd5dd82b

## EVIDENCE_COMMIT
PENDING

## FILES_CHANGED_CODE
agentic_core/L0_routing/scripts/execute_ssot.py
agentic_core/L5_safety/reasoning/FileClassificationAgent.py
agentic_core/L5_safety/reasoning/LocationHealerAgent.py
system_learning/engines/hitl_decision_logger.py
tests/agentic_core/test_wave6_hitl_gates.py

## FILES_CHANGED_EVIDENCE
docs/reports/evidence/wave6_evidence.md

## INSPECTED_FILES
agentic_core/L5_safety/reasoning/LocationHealerAgent.py
agentic_core/L5_safety/reasoning/FileClassificationAgent.py
agentic_core/L0_routing/scripts/execute_ssot.py
system_learning/engines/hitl_decision_logger.py
tests/agentic_core/test_wave6_hitl_gates.py

## HITL Trigger Points Implemented
1. FILE_DELETION: LocationHealerAgent._heal_via_archiving() -- hitl_approval_fn kwarg
   + self._hitl_approval_fn instance fallback injected by execute_ssot.py
2. AMBIGUOUS_CLASSIFICATION: FileClassificationAgent.classify_file_with_confidence()
   -- HITL_FLAGGED annotation when top-2 confidence delta < 0.15
3. ARCHIVE_GATE: execute_ssot.py _w6_hitl_archive_gate() wired onto
   location_validator._hitl_approval_fn before heal_violations() call
4. DECISION_LOG: system_learning/engines/hitl_decision_logger.log_hitl_decision()
   -- ASCII-only, thread-safe, appends to docs/reports/evidence/wave6_evidence.md

## pytest wave6
$ python -m pytest -q --color=no tests/agentic_core/test_wave6_hitl_gates.py
collected 8 items

tests/agentic_core/test_wave6_hitl_gates.py::test_hitl_decision_logger_exists PASSED [ 12%]
tests/agentic_core/test_wave6_hitl_gates.py::test_hitl_decision_logger_exports_log_fn PASSED [ 25%]
tests/agentic_core/test_wave6_hitl_gates.py::test_location_healer_hitl_approval_fn_param PASSED [ 37%]
tests/agentic_core/test_wave6_hitl_gates.py::test_location_healer_reads_instance_hitl_fn PASSED [ 50%]
tests/agentic_core/test_wave6_hitl_gates.py::test_file_classification_hitl_flagged_delta PASSED [ 62%]
tests/agentic_core/test_wave6_hitl_gates.py::test_file_classification_hitl_logs_decision PASSED [ 75%]
tests/agentic_core/test_wave6_hitl_gates.py::test_execute_ssot_wires_hitl_approval_fn PASSED [ 87%]
tests/agentic_core/test_wave6_hitl_gates.py::test_execute_ssot_hitl_gate_before_heal_violations PASSED [100%]

8 passed in 0.17s

HITL_DECISION_1: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\apps_shared\utils\l1_health_benchmark_util.py
  Violation=LAYER PREFIX VIOLATION: Filename has forbidden prefix 'l1_' | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_2: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\apps_shared\utils\l5_autonomous_orchestrator_util.py
  Violation=LAYER PREFIX VIOLATION: Filename has forbidden prefix 'l5_' | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_3: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\ops_scripts\general\l0_import_model.py
  Violation=LAYER PREFIX VIOLATION: Filename has forbidden prefix 'l0_' | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_4: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\system_learning\engines\l0_threshold_tuner.py
  Violation=LAYER PREFIX VIOLATION: Filename has forbidden prefix 'l0_' | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_5: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\system_learning\engines\l4_audit_reader.py
  Violation=LAYER PREFIX VIOLATION: Filename has forbidden prefix 'l4_' | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_6: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\system_learning\engines\l4_state_writer.py
  Violation=LAYER PREFIX VIOLATION: Filename has forbidden prefix 'l4_' | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_7: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\system_learning\engines\l4_version_store.py
  Violation=LAYER PREFIX VIOLATION: Filename has forbidden prefix 'l4_' | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_8: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\unit\test_SovereignBaseAgent.py
  Violation=CRITICAL: Base Agents must reside in 'agentic_core/base_agents/', not 'unit' | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_9: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_10: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_11: Agent=SovereignDecisionEngine | File=ArchitectureGovernorAgent
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_12: Agent=SovereignDecisionEngine | File=LocationAgent
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_13: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\artifacts\consolidation\backups\agentic_core__L1_cognition__reasoning__StrategistAgent.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_14: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\artifacts\consolidation\backups\agentic_core__L2_execution__reasoning__RgStrategicPlannerAgent.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_15: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\artifacts\consolidation\backups\agentic_core__L2_execution__reasoning__UiValidationAgent.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_16: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\artifacts\consolidation\backups\agentic_core__L3_orchestration__reasoning__DagRuntimeInspectorAgent.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_17: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\artifacts\consolidation\backups\agentic_core__L4_state__reasoning__CartographerAgent.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_18: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\artifacts\consolidation\backups\agentic_core__L5_safety__reasoning__DependencyDiplomatAgent.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_19: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\artifacts\consolidation\backups\agentic_core__L5_safety__reasoning__GlobalComplianceAggregatorAgent.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_20: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\artifacts\consolidation\backups\agentic_core__L5_safety__reasoning__OmniContextAgent.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_21: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\artifacts\consolidation\backups\agentic_core__L5_safety__reasoning__SemanticMapperAgent.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_22: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\artifacts\consolidation\backups\agentic_core__L5_safety__reasoning__SemanticTerritoryMapperAgent.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_23: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\artifacts\consolidation\backups\agentic_core__L5_safety__reasoning__SignatureVerifierAgent.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_24: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\artifacts\consolidation\backups\agentic_core__L5_safety__reasoning__TokenBudgetInspectorAgent.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_25: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\artifacts\consolidation\backups\agentic_core__L6_observability__reasoning__CoordinateObservabilityOperationsAgent.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_26: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\artifacts\consolidation\backups\agentic_core__L6_observability__reasoning__DeadlockDetectorAgent.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_27: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\artifacts\consolidation\backups\agentic_core__L6_observability__reasoning__DebateSynthesisAgent.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_28: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\artifacts\consolidation\backups\agentic_core__L6_observability__reasoning__RuntimeTelemetryAgent.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_29: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\artifacts\consolidation\backups\agentic_core__L6_observability__reasoning__StrategicObservationAgent.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_30: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\artifacts\consolidation\backups\agentic_core__L6_observability__reasoning__TrackObservabilityCostAgent.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_31: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\artifacts\consolidation\backups\agentic_core__runtime__utils__discovery_util.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_32: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\artifacts\consolidation\backups\apps_lic__engines__CampaignBalanceAgent.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_33: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\artifacts\consolidation\backups\apps_lic__engines__DeliverabilityAgent.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_34: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\artifacts\consolidation\backups\apps_lic__engines__Hop1ProfileAnalysisAgent.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_35: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\artifacts\consolidation\backups\apps_lic__engines__Hop2ResearchAgent.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_36: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\artifacts\consolidation\backups\apps_lic__engines__HOP3SenderGroundingAgent.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_37: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\artifacts\consolidation\backups\apps_lic__engines__Hop4RoutingAgent.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_38: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\artifacts\consolidation\backups\apps_lic__engines__HOP5GenerationAgent.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_39: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\artifacts\consolidation\backups\apps_lic__engines__Hop6ValidationAgent.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_40: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\artifacts\consolidation\backups\apps_lic__engines__HOP7GateDecisionAgent.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_41: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\artifacts\consolidation\backups\apps_lic__engines__HOP8QAReportAgent.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_42: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\artifacts\consolidation\backups\apps_lic__engines__HOP9IntegrationAgent.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_43: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\artifacts\consolidation\backups\apps_lic__engines__IntelligenceLibrarianAgent.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_44: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\artifacts\consolidation\backups\apps_lic__engines__LeadQualityAgent.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_45: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\artifacts\consolidation\backups\apps_lic__engines__LicReflectionAgent.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_46: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\artifacts\consolidation\backups\apps_lic__engines__LicTemplateOptimizerAgent.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_47: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\artifacts\consolidation\backups\apps_lic__engines__MessageArchitectAgent.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_48: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\artifacts\consolidation\backups\apps_lic__engines__MessageComplianceAgent.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_49: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\artifacts\consolidation\backups\apps_lic__engines__MessageDiversityValidator.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_50: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\artifacts\consolidation\backups\apps_lic__engines__OutreachLearningAgent.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_51: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\artifacts\consolidation\backups\apps_lic__engines__OutreachProactiveAgent.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_52: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\artifacts\consolidation\backups\apps_rg__reasoning__ATSCompatibilityAgent.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_53: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\artifacts\consolidation\backups\apps_rg__reasoning__BrandComplianceAgent.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_54: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\artifacts\consolidation\backups\apps_rg__reasoning__CampaignPlannerAgent.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_55: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\artifacts\consolidation\backups\apps_rg__reasoning__ContentStrategyAgent.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_56: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\artifacts\consolidation\backups\apps_rg__reasoning__FactCheckAgent.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_57: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\artifacts\consolidation\backups\apps_rg__reasoning__RgStrategicPlannerAgent.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_58: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\artifacts\consolidation\backups\apps_rg__reasoning__RgTemplateOptimizerAgent.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_59: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\artifacts\consolidation\backups\apps_rg__reasoning__SectionBalanceAgent.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_60: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\artifacts\windsurf\legacy\_capture_evidence.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_61: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\artifacts\windsurf\legacy\_run_entry1.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_62: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\artifacts\windsurf\legacy\_run_entry2.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_63: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_64: Agent=SovereignDecisionEngine | File=FileClassificationAgent
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_65: Agent=SovereignDecisionEngine | File=LocationAgent
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_66: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\data\prompt_governance\safety\constitutional_principle_types.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_67: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\data\prompt_governance\safety\const_ai_impl.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_68: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\data\prompt_governance\safety\const_ai_impl_impl_impl_impl.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_69: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\data\prompt_governance\safety\const_final.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_70: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\data\prompt_governance\safety\const_final_impl_impl_impl_impl.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_71: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\data\prompt_governance\safety\__init__.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_72: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\data\prompt_governance\versioning\PromptTemplate.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_73: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\data\prompt_governance\versioning\__init__.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_74: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\data\sdks_mcps\client_wrappers\anthropic_client.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_75: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\data\sdks_mcps\client_wrappers\openai_client.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_76: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\data\sdks_mcps\client_wrappers\vertex_client.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_77: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\data\sdks_mcps\client_wrappers\__init__.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_78: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\data\sdks_mcps\reference_clients\minimal_anthropic.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_79: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\data\sdks_mcps\reference_clients\minimal_openai.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_80: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\data\sdks_mcps\reference_clients\minimal_vertex.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_81: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\data\sdks_mcps\validation\validate_mcps.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_82: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_83: Agent=SovereignDecisionEngine | File=FileClassificationAgent
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_84: Agent=SovereignDecisionEngine | File=LocationAgent
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_85: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\docs\reports\assessments\prompt-modules\validation\assemble.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_86: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\docs\reports\assessments\prompt-modules\validation\validate_assembly.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_87: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_88: Agent=SovereignDecisionEngine | File=LocationAgent
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_89: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\ops_scripts\dev_tools\l0_scripts\add_agent_suffix_plan_util.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_90: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\ops_scripts\dev_tools\l0_scripts\analyze_agent_count_waterfall_util.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_91: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\ops_scripts\dev_tools\l0_scripts\analyze_app_files_util.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_92: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\ops_scripts\dev_tools\l0_scripts\analyze_archive_util.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_93: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\ops_scripts\dev_tools\l0_scripts\analyze_extract.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_94: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\ops_scripts\dev_tools\l0_scripts\ast_layer_stats_util.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_95: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\ops_scripts\dev_tools\l0_scripts\audit_all_agents_mro_util.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_96: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\ops_scripts\dev_tools\l0_scripts\audit_code_quality_metrics_util.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_97: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\ops_scripts\dev_tools\l0_scripts\audit_complexity_health_util.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_98: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\ops_scripts\dev_tools\l0_scripts\audit_dashboard_naming_util.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_99: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\ops_scripts\dev_tools\l0_scripts\audit_dashboard_ssot_flow_util.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_100: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\ops_scripts\dev_tools\l0_scripts\audit_dashboard_ssot_util.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_101: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\ops_scripts\dev_tools\l0_scripts\audit_live_runtime_consolidation_util.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_102: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\ops_scripts\dev_tools\l0_scripts\audit_residual_rglob_util.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_103: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\ops_scripts\dev_tools\l0_scripts\audit_status.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_104: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\ops_scripts\dev_tools\l0_scripts\audit_table_validation_parity_util.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_105: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\ops_scripts\dev_tools\l0_scripts\budget_auditor_util.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_106: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\ops_scripts\dev_tools\l0_scripts\bulk_agent_rename_util.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_107: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\ops_scripts\dev_tools\l0_scripts\callable_report.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_108: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\ops_scripts\dev_tools\l0_scripts\clean_dashboard_html_util.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_109: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\ops_scripts\dev_tools\l0_scripts\compare_dashboard_data_util.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_110: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\ops_scripts\dev_tools\l0_scripts\complete_terminal_alignment_util.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_111: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\ops_scripts\dev_tools\l0_scripts\complexity.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_112: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\ops_scripts\dev_tools\l0_scripts\complexity_reducer.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_113: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\ops_scripts\dev_tools\l0_scripts\comprehensive_agent_audit_util.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_114: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\ops_scripts\dev_tools\l0_scripts\dashboard_live_server_util.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_115: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\ops_scripts\dev_tools\l0_scripts\dashboard_qa_deep_audit_util.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_116: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\ops_scripts\dev_tools\l0_scripts\dashboard_style_report_util.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_117: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\ops_scripts\dev_tools\l0_scripts\dashboard_verifier.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_118: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\ops_scripts\dev_tools\l0_scripts\debug_dashboard_rendering_util.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_119: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\ops_scripts\dev_tools\l0_scripts\deep_deprecation_audit_v2_util.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_120: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\ops_scripts\dev_tools\l0_scripts\detailed_territory_report_util.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_121: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\ops_scripts\dev_tools\l0_scripts\detailed_territory_subterritory_report_util.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_122: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\ops_scripts\dev_tools\l0_scripts\diagnose_dashboard_live_util.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_123: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\ops_scripts\dev_tools\l0_scripts\diagnose_user_dashboard_view_util.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_124: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\ops_scripts\dev_tools\l0_scripts\enforce_dashboard_freshness_util.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_125: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\ops_scripts\dev_tools\l0_scripts\extract_dashboard_errors_util.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_126: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\ops_scripts\dev_tools\l0_scripts\extract_layer_stats_util.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_127: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\ops_scripts\dev_tools\l0_scripts\finalize_architecture_safe_util.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_128: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\ops_scripts\dev_tools\l0_scripts\finalize_architecture_simple_util.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_129: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\ops_scripts\dev_tools\l0_scripts\finalize_architecture_util.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_130: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\ops_scripts\dev_tools\l0_scripts\finalize_sovereign_structure_util.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_131: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\ops_scripts\dev_tools\l0_scripts\find_and_fix_all_missing_heal_util.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_132: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\ops_scripts\dev_tools\l0_scripts\find_and_fix_missing_heal_util.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_133: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\ops_scripts\dev_tools\l0_scripts\fix_all_imports_comprehensive_util.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_134: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\ops_scripts\dev_tools\l0_scripts\fix_all_invocations_util.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_135: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\ops_scripts\dev_tools\l0_scripts\fix_apps_lic_engines_util.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_136: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\ops_scripts\dev_tools\l0_scripts\fix_healer_mixin_imports_util.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_137: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\ops_scripts\dev_tools\l0_scripts\fix_heal_schema_violations_util.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_138: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\ops_scripts\dev_tools\l0_scripts\fix_imports_emergency_util.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_139: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_140: Agent=SovereignDecisionEngine | File=FileClassificationAgent
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_141: Agent=SovereignDecisionEngine | File=LocationAgent
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_142: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\system_learning\depth_aligned\depth_aligned\__init__.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_143: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\system_learning\engines\arbitration\engine.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_144: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\system_learning\engines\arbitration\types.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_145: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\system_learning\engines\arbitration\__init__.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_146: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\system_learning\engines\confidence\engine.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_147: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\system_learning\engines\confidence\types.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_148: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\system_learning\engines\confidence\__init__.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_149: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\system_learning\engines\correlation\engine.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_150: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\system_learning\engines\correlation\types.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_151: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\system_learning\engines\correlation\__init__.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_152: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\system_learning\engines\fingerprinting\engine.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_153: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\system_learning\engines\fingerprinting\types.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_154: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\system_learning\engines\fingerprinting\__init__.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_155: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_156: Agent=SovereignDecisionEngine | File=FileClassificationAgent
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_157: Agent=SovereignDecisionEngine | File=LocationAgent
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_158: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\architecture\conftest.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_159: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\architecture\test_apps_ssot_shared_enforcement.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_160: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\architecture\test_artifacts_guard.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_161: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\architecture\test_cache_guard.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_162: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\architecture\test_classification_hardening.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_163: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\architecture\test_compile_time_frozen_governance.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_164: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\architecture\test_docs_structure_guard.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_165: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\architecture\test_environment_independence.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_166: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\architecture\test_invariants.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_167: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\architecture\test_layer_write_sovereignty.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_168: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\architecture\test_logs_guard.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_169: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\architecture\test_longpaths_bypass.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_170: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\architecture\test_mathematical_determinism.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_171: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\architecture\test_module_collision_guard.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_172: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\architecture\test_no_credentials_in_repo.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_173: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\architecture\test_prompt_governance_no_orphans.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_174: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\architecture\test_prompt_root_boundary.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_175: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\architecture\test_sovereign_gateway_boundary.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_176: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\architecture\test_tests_ssot_invariant.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_177: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\architecture\__init__.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_178: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\behavioral\capture_golden.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_179: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\behavioral\conftest.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_180: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\behavioral\verify_golden.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_181: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\contracts\conftest.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_182: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\contracts\test_agent_artifact_emission.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_183: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\contracts\test_agent_execute_contract.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_184: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\contracts\test_agent_guard_integration.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_185: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\contracts\test_agent_inheritance.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_186: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\contracts\test_agent_prod_hygiene.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_187: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\contracts\test_agent_reachability.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_188: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\contracts\test_agent_structural_identity.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_189: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\contracts\test_guardian_quarantine_contract.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_190: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\contracts\test_hardening_negative.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_191: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\contracts\test_minimum_behavioral_bar.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_192: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\contracts\test_structure_mirror_contract.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_193: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\contracts\_discover_debt.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_194: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\contracts\_scanner.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_195: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\contracts\__init__.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_196: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\core\test_active_set_fingerprint.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_197: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\core\test_active_set_snapshot_check.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_198: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\core\test_active_set_ssot_check.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_199: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\core\test_baseline_import_no_guardrail_fire.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_200: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\core\test_baseline_io.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_201: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\core\test_classification_contract.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_202: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\core\test_dependency_verifier_exit_code.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_203: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\core\test_executor_dispatch_runtime_equivalence.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_204: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\core\test_executor_dispatch_snapshot.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_205: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\core\test_executor_smoke.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_206: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\core\test_governance_coverage_check.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_207: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\core\test_hop_migration_structure.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_208: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_209: Agent=SovereignDecisionEngine | File=FileClassificationAgent
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_210: Agent=SovereignDecisionEngine | File=LocationAgent
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_211: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tools\depth_aligned\depth_aligned\canonical_hash.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_212: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tools\depth_aligned\depth_aligned\capture_evidence.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_213: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tools\depth_aligned\depth_aligned\check_vram.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_214: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tools\depth_aligned\depth_aligned\dry_run_apps_lic.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_215: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tools\depth_aligned\depth_aligned\embedding_rtx5090_optimizer.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_216: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tools\depth_aligned\depth_aligned\rag_reranker_shim.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_217: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tools\depth_aligned\depth_aligned\run_phase10_arbitration_evidence.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_218: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tools\depth_aligned\depth_aligned\run_phase11_final_evidence.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_219: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tools\depth_aligned\depth_aligned\run_phase11_ptc_evidence.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_220: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tools\depth_aligned\depth_aligned\run_phase3_integration.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_221: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tools\depth_aligned\depth_aligned\run_phase6_replay_evidence.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_222: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tools\depth_aligned\depth_aligned\run_phase7_storage_evidence.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_223: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tools\depth_aligned\depth_aligned\run_phase8_perf_evidence.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_224: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tools\depth_aligned\depth_aligned\run_phase9_formal_checks_evidence.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_225: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tools\depth_aligned\depth_aligned\run_replay_execute_ssot_plan.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_226: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tools\depth_aligned\depth_aligned\run_static_invariants.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_227: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tools\depth_aligned\depth_aligned\seed_direct_writes_baseline.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_228: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tools\depth_aligned\depth_aligned\test_vllm_boundary.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_229: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tools\depth_aligned\depth_aligned\vllm_boundary_client.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_230: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tools\depth_aligned\depth_aligned\wave1_audit.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_231: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tools\depth_aligned\depth_aligned\wave3_verification.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_232: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tools\depth_aligned\depth_aligned\__init__.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_233: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_234: Agent=SovereignDecisionEngine | File=FileClassificationAgent
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_1: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_2: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_3: Agent=SovereignDecisionEngine | File=ArchitectureGovernorAgent
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_4: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\data\sdks_mcps\client_wrappers\__init__.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_5: Agent=SovereignDecisionEngine | File=LocationAgent
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_6: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\core\test_lic_validation_capability_structure.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_7: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\core\test_mro_new_diamond_check.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_8: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\core\test_repo_structure.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_9: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\core\__init__.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_10: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\depth_aligned\conftest.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_11: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\e2e\test_anomaly_remediation_pipeline_fixture_repo.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_12: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\e2e\test_batch_performance_optimization.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_13: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\e2e\test_canon_key_removal.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_14: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\e2e\test_cognitive_subset.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_15: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\e2e\test_complete_mission_workflow.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_16: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\e2e\test_import_resolution.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_17: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\e2e\test_layer_isolation.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_18: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\e2e\test_lic_rg_parity.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_19: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\e2e\test_location_agent_telemetry.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_20: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\e2e\test_manifest_completion.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_21: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\e2e\test_meta_learning_e2e.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_22: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\e2e\test_mission_dry_run.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_23: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\e2e\test_mission_script_integrity.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_24: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\e2e\test_mro_refactor.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_25: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\e2e\test_phase5_invariants_fixture_repo.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_26: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\e2e\test_sovereign_validation_e2e.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_27: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\e2e\__init__.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_28: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\e2e\__init___1.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_29: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\e2e\__init___2.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_30: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\enforcement\conftest.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_31: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\enforcement\test_constitutional_validator.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_32: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\enforcement\test_folder_purity_governance.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_33: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\enforcement\test_folder_purity_invariants.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_34: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\enforcement\test_phase_acceptance_guard.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_35: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\enforcement\test_pytest_config_guard.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_36: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\enforcement\test_windsurfrules_budget_and_evidence_gate.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_37: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\fixtures\embedding_provider_registry_fixture.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_38: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\fixtures\test_testing_utils.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_39: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\fixtures\__init__.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_40: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\goldens\allowlist_goldens.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_41: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\goldens\test_allowlist_goldens.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_42: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\goldens\__init__.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_43: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\conftest.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_44: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_agent_execution_policy_application.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_45: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_agent_execution_profiles.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_46: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_agent_heal_audit.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_47: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_architectural_invariants.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_48: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_authority_boundaries.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_49: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_blast_radius.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_50: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_canonical_serializer.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_51: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_canonical_serializer_ssot.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_52: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_capability_revocation.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_53: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_cross_layer_import_freeze.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_54: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_embedding_invariants.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_55: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_escalation_monotonicity.py
  Violation=Location violation | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_56: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_57: Agent=SovereignDecisionEngine | File=FileClassificationAgent
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_1: Agent=SovereignDecisionEngine | File=LocationAgent
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_1: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_2: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_1: Agent=SovereignDecisionEngine | File=arch_governor
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_1: Agent=SovereignDecisionEngine | File=arch_governor
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_1: Agent=SovereignDecisionEngine | File=arch_governor
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_1: Agent=SovereignDecisionEngine | File=arch_governor
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_1: Agent=SovereignDecisionEngine | File=arch_governor
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_1: Agent=SovereignDecisionEngine | File=arch_governor
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_1: Agent=SovereignDecisionEngine | File=arch_governor
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_2: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_3: Agent=SovereignDecisionEngine | File=file_classification
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_4: Agent=SovereignDecisionEngine | File=observability_probe
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_5: Agent=SovereignDecisionEngine | File=arch_governor
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_6: Agent=SovereignDecisionEngine | File=cognitive_disposition
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_7: Agent=SovereignDecisionEngine | File=cognitive_disposition
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_8: Agent=SovereignDecisionEngine | File=arch_governor
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_9: Agent=SovereignDecisionEngine | File=file_classification
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_1: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_1: Agent=SovereignDecisionEngine | File=arch_governor
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_1: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_2: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_3: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_4: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_5: Agent=SovereignDecisionEngine | File=HierarchyAgent
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_6: Agent=SovereignDecisionEngine | File=ArchitectureGovernorAgent
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_7: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_8: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_9: Agent=SovereignDecisionEngine | File=ArchitectureGovernorAgent
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_10: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_11: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_12: Agent=SovereignDecisionEngine | File=FileClassificationAgent
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_13: Agent=SovereignDecisionEngine | File=ArchitectureGovernorAgent
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_14: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_15: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_16: Agent=SovereignDecisionEngine | File=ArchitectureGovernorAgent
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_17: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_18: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_19: Agent=SovereignDecisionEngine | File=ArchitectureGovernorAgent
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_20: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_21: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_22: Agent=SovereignDecisionEngine | File=ArchitectureGovernorAgent
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_23: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_24: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_25: Agent=SovereignDecisionEngine | File=ArchitectureGovernorAgent
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_26: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_27: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_28: Agent=SovereignDecisionEngine | File=LocationAgent
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_29: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_30: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_31: Agent=SovereignDecisionEngine | File=ArchitectureGovernorAgent
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_32: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_33: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_34: Agent=SovereignDecisionEngine | File=ArchitectureGovernorAgent
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_35: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_36: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_37: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_38: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_39: Agent=SovereignDecisionEngine | File=ArchitectureGovernorAgent
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_40: Agent=SovereignDecisionEngine | File=LocationAgent
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_41: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_42: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_43: Agent=SovereignDecisionEngine | File=FileClassificationAgent
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_44: Agent=SovereignDecisionEngine | File=ArchitectureGovernorAgent
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_45: Agent=SovereignDecisionEngine | File=LocationAgent
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_46: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_47: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_48: Agent=SovereignDecisionEngine | File=FileClassificationAgent
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_49: Agent=SovereignDecisionEngine | File=ArchitectureGovernorAgent
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_50: Agent=SovereignDecisionEngine | File=LocationAgent
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_51: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_52: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_1: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_2: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_3: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\system_learning\adapters\l1_meta_adapter.py
  Violation=LAYER PREFIX VIOLATION: Filename has forbidden prefix 'l1_' | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_4: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\system_learning\engines\l0_threshold_tuner.py
  Violation=LAYER PREFIX VIOLATION: Filename has forbidden prefix 'l0_' | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_5: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\system_learning\engines\l1_model_proposer.py
  Violation=LAYER PREFIX VIOLATION: Filename has forbidden prefix 'l1_' | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_6: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\system_learning\engines\l3_efficiency_tuner.py
  Violation=LAYER PREFIX VIOLATION: Filename has forbidden prefix 'l3_' | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_7: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\system_learning\engines\l4_audit_reader.py
  Violation=LAYER PREFIX VIOLATION: Filename has forbidden prefix 'l4_' | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_8: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\system_learning\engines\l4_state_writer.py
  Violation=LAYER PREFIX VIOLATION: Filename has forbidden prefix 'l4_' | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_9: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\system_learning\engines\l4_version_store.py
  Violation=LAYER PREFIX VIOLATION: Filename has forbidden prefix 'l4_' | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_10: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\system_learning\engines\l5_policy_proposer.py
  Violation=LAYER PREFIX VIOLATION: Filename has forbidden prefix 'l5_' | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_11: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_12: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_13: Agent=SovereignDecisionEngine | File=HierarchyAgent
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_14: Agent=SovereignDecisionEngine | File=ArchitectureGovernorAgent
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_15: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_16: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_17: Agent=SovereignDecisionEngine | File=ArchitectureGovernorAgent
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_18: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_19: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_20: Agent=SovereignDecisionEngine | File=FileClassificationAgent
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_21: Agent=SovereignDecisionEngine | File=ArchitectureGovernorAgent
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_22: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_23: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_24: Agent=SovereignDecisionEngine | File=ArchitectureGovernorAgent
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_25: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_26: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_27: Agent=SovereignDecisionEngine | File=ArchitectureGovernorAgent
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_28: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_29: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_30: Agent=SovereignDecisionEngine | File=ArchitectureGovernorAgent
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_31: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_32: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_33: Agent=SovereignDecisionEngine | File=ArchitectureGovernorAgent
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_34: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_35: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_36: Agent=SovereignDecisionEngine | File=LocationAgent
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_37: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_38: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_39: Agent=SovereignDecisionEngine | File=ArchitectureGovernorAgent
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_40: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_41: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_42: Agent=SovereignDecisionEngine | File=ArchitectureGovernorAgent
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_43: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_44: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_45: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_46: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_47: Agent=SovereignDecisionEngine | File=ArchitectureGovernorAgent
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_48: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_49: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_50: Agent=SovereignDecisionEngine | File=ArchitectureGovernorAgent
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_51: Agent=SovereignDecisionEngine | File=LocationAgent
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_52: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_53: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_54: Agent=SovereignDecisionEngine | File=FileClassificationAgent
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_55: Agent=SovereignDecisionEngine | File=ArchitectureGovernorAgent
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_56: Agent=SovereignDecisionEngine | File=LocationAgent
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_57: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_58: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_59: Agent=SovereignDecisionEngine | File=FileClassificationAgent
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_60: Agent=SovereignDecisionEngine | File=ArchitectureGovernorAgent
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_1: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_2: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_3: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\system_learning\adapters\l1_meta_adapter.py
  Violation=LAYER PREFIX VIOLATION: Filename has forbidden prefix 'l1_' | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_4: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\system_learning\engines\l0_threshold_tuner.py
  Violation=LAYER PREFIX VIOLATION: Filename has forbidden prefix 'l0_' | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_5: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\system_learning\engines\l1_model_proposer.py
  Violation=LAYER PREFIX VIOLATION: Filename has forbidden prefix 'l1_' | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_6: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\system_learning\engines\l3_efficiency_tuner.py
  Violation=LAYER PREFIX VIOLATION: Filename has forbidden prefix 'l3_' | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_7: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\system_learning\engines\l4_audit_reader.py
  Violation=LAYER PREFIX VIOLATION: Filename has forbidden prefix 'l4_' | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_8: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\system_learning\engines\l4_state_writer.py
  Violation=LAYER PREFIX VIOLATION: Filename has forbidden prefix 'l4_' | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_9: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\system_learning\engines\l4_version_store.py
  Violation=LAYER PREFIX VIOLATION: Filename has forbidden prefix 'l4_' | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_10: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\system_learning\engines\l5_policy_proposer.py
  Violation=LAYER PREFIX VIOLATION: Filename has forbidden prefix 'l5_' | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_11: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_12: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_13: Agent=SovereignDecisionEngine | File=HierarchyAgent
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_14: Agent=SovereignDecisionEngine | File=ArchitectureGovernorAgent
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_15: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_16: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_17: Agent=SovereignDecisionEngine | File=ArchitectureGovernorAgent
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_18: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_19: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_20: Agent=SovereignDecisionEngine | File=FileClassificationAgent
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_21: Agent=SovereignDecisionEngine | File=ArchitectureGovernorAgent
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_22: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_23: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_24: Agent=SovereignDecisionEngine | File=ArchitectureGovernorAgent
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_25: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_26: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_27: Agent=SovereignDecisionEngine | File=ArchitectureGovernorAgent
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_28: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_29: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_30: Agent=SovereignDecisionEngine | File=ArchitectureGovernorAgent
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_31: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_32: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_33: Agent=SovereignDecisionEngine | File=ArchitectureGovernorAgent
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_34: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_35: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_36: Agent=SovereignDecisionEngine | File=LocationAgent
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_37: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_38: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_39: Agent=SovereignDecisionEngine | File=ArchitectureGovernorAgent
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_40: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_41: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_42: Agent=SovereignDecisionEngine | File=ArchitectureGovernorAgent
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_43: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_44: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_45: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_46: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_47: Agent=SovereignDecisionEngine | File=ArchitectureGovernorAgent
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_1: Agent=FileClassificationAgent | File=C:\Users\amita\AppData\Local\Temp\pytest-of-amita\pytest-56\test_confidence_low_for_mixed_0\hybrid.py
  Violation=AMBIGUOUS_CLASSIFICATION | Proposed=TYPES | Decision=FLAGGED_FOR_REVIEW
  delta=0.125
  top3=[('TYPES', 0.5), ('CONFIG', 0.375), ('VALIDATOR', 0.125)]

HITL_DECISION_1: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_2: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_3: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_4: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_5: Agent=SovereignDecisionEngine | File=HierarchyAgent
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_6: Agent=SovereignDecisionEngine | File=ArchitectureGovernorAgent
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_7: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_8: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_9: Agent=SovereignDecisionEngine | File=ArchitectureGovernorAgent
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_10: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_11: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_12: Agent=SovereignDecisionEngine | File=FileClassificationAgent
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_13: Agent=SovereignDecisionEngine | File=ArchitectureGovernorAgent
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_14: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_15: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_16: Agent=SovereignDecisionEngine | File=ArchitectureGovernorAgent
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_17: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_18: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_19: Agent=SovereignDecisionEngine | File=ArchitectureGovernorAgent
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_20: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_21: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_22: Agent=SovereignDecisionEngine | File=ArchitectureGovernorAgent
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_23: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_24: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_25: Agent=SovereignDecisionEngine | File=ArchitectureGovernorAgent
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_26: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_27: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_28: Agent=SovereignDecisionEngine | File=LocationAgent
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_29: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_30: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_31: Agent=SovereignDecisionEngine | File=ArchitectureGovernorAgent
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_32: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_33: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_34: Agent=SovereignDecisionEngine | File=ArchitectureGovernorAgent
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_35: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_36: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_37: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_38: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_39: Agent=SovereignDecisionEngine | File=ArchitectureGovernorAgent
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_40: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_41: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_42: Agent=SovereignDecisionEngine | File=ArchitectureGovernorAgent
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_43: Agent=SovereignDecisionEngine | File=LocationAgent
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_44: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_45: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_46: Agent=SovereignDecisionEngine | File=FileClassificationAgent
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_47: Agent=SovereignDecisionEngine | File=ArchitectureGovernorAgent
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_48: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_49: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_50: Agent=SovereignDecisionEngine | File=ArchitectureGovernorAgent
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_1: Agent=SovereignDecisionEngine | File=Unknown
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_1: Agent=SovereignDecisionEngine | File=Unknown
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_1: Agent=SovereignDecisionEngine | File=Unknown
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_1: Agent=SovereignDecisionEngine | File=Unknown
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_1: Agent=SovereignDecisionEngine | File=Unknown
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_1: Agent=SovereignDecisionEngine | File=Unknown
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_1: Agent=SovereignDecisionEngine | File=Unknown
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_2: Agent=SovereignDecisionEngine | File=arch_governor
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_3: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_4: Agent=SovereignDecisionEngine | File=observability_probe
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_5: Agent=SovereignDecisionEngine | File=cognitive_disposition
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_6: Agent=SovereignDecisionEngine | File=file_classification
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_7: Agent=SovereignDecisionEngine | File=arch_governor
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_8: Agent=SovereignDecisionEngine | File=cognitive_disposition
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_9: Agent=SovereignDecisionEngine | File=arch_governor
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_10: Agent=SovereignDecisionEngine | File=file_classification
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_11: Agent=FileClassificationAgent | File=C:\Users\amita\AppData\Local\Temp\pytest-of-amita\pytest-148\test_confidence_low_for_mixed_0\hybrid.py
  Violation=AMBIGUOUS_CLASSIFICATION | Proposed=TYPES | Decision=FLAGGED_FOR_REVIEW
  delta=0.125
  top3=[('TYPES', 0.5), ('CONFIG', 0.375), ('VALIDATOR', 0.125)]

HITL_DECISION_12: Agent=SovereignDecisionEngine | File=Unknown
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_13: Agent=FileClassificationAgent | File=C:\Users\amita\AppData\Local\Temp\pytest-of-amita\pytest-148\test_confidence_low_for_mixed_1\hybrid.py
  Violation=AMBIGUOUS_CLASSIFICATION | Proposed=TYPES | Decision=FLAGGED_FOR_REVIEW
  delta=0.125
  top3=[('TYPES', 0.5), ('CONFIG', 0.375), ('VALIDATOR', 0.125)]

HITL_DECISION_14: Agent=SovereignDecisionEngine | File=arch_governor
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_15: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_16: Agent=SovereignDecisionEngine | File=observability_probe
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_17: Agent=SovereignDecisionEngine | File=cognitive_disposition
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_18: Agent=SovereignDecisionEngine | File=file_classification
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_19: Agent=SovereignDecisionEngine | File=arch_governor
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_20: Agent=SovereignDecisionEngine | File=cognitive_disposition
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_21: Agent=SovereignDecisionEngine | File=arch_governor
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_22: Agent=SovereignDecisionEngine | File=file_classification
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_23: Agent=SovereignDecisionEngine | File=AgentA
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_24: Agent=SovereignDecisionEngine | File=AgentA
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_25: Agent=SovereignDecisionEngine | File=AgentA
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_26: Agent=SovereignDecisionEngine | File=AgentA
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_27: Agent=SovereignDecisionEngine | File=Unknown
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_28: Agent=SovereignDecisionEngine | File=AgentA
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_29: Agent=SovereignDecisionEngine | File=AgentA
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_30: Agent=SovereignDecisionEngine | File=AgentA
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_31: Agent=SovereignDecisionEngine | File=AgentA
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_1: Agent=SovereignDecisionEngine | File=Unknown
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_2: Agent=SovereignDecisionEngine | File=arch_governor
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_1: Agent=SovereignDecisionEngine | File=Unknown
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_2: Agent=SovereignDecisionEngine | File=arch_governor
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_3: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_4: Agent=SovereignDecisionEngine | File=file_classification
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_5: Agent=SovereignDecisionEngine | File=arch_governor
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_6: Agent=SovereignDecisionEngine | File=cognitive_disposition
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_7: Agent=SovereignDecisionEngine | File=observability_probe
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_8: Agent=SovereignDecisionEngine | File=cognitive_disposition
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_1: Agent=SovereignDecisionEngine | File=Unknown
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_9: Agent=SovereignDecisionEngine | File=arch_governor
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_10: Agent=SovereignDecisionEngine | File=file_classification
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_2: Agent=SovereignDecisionEngine | File=AgentA
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_3: Agent=SovereignDecisionEngine | File=AgentA
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_4: Agent=SovereignDecisionEngine | File=AgentA
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_11: Agent=FileClassificationAgent | File=C:\Users\amita\AppData\Local\Temp\pytest-of-amita\pytest-153\test_confidence_low_for_mixed_0\hybrid.py
  Violation=AMBIGUOUS_CLASSIFICATION | Proposed=TYPES | Decision=FLAGGED_FOR_REVIEW
  delta=0.125
  top3=[('TYPES', 0.5), ('CONFIG', 0.375), ('VALIDATOR', 0.125)]

HITL_DECISION_5: Agent=SovereignDecisionEngine | File=AgentA
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_1: Agent=SovereignDecisionEngine | File=Unknown
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_1: Agent=SovereignDecisionEngine | File=Unknown
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_1: Agent=SovereignDecisionEngine | File=LocationAgent
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_2: Agent=SovereignDecisionEngine | File=TestAgent1
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_3: Agent=SovereignDecisionEngine | File=TestAgent2
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_1: Agent=SovereignDecisionEngine | File=AgentA
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_2: Agent=SovereignDecisionEngine | File=AgentA
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_3: Agent=SovereignDecisionEngine | File=AgentA
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_12: Agent=SovereignDecisionEngine | File=Unknown
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_13: Agent=FileClassificationAgent | File=C:\Users\amita\AppData\Local\Temp\pytest-of-amita\pytest-153\test_confidence_low_for_mixed_1\hybrid.py
  Violation=AMBIGUOUS_CLASSIFICATION | Proposed=TYPES | Decision=FLAGGED_FOR_REVIEW
  delta=0.125
  top3=[('TYPES', 0.5), ('CONFIG', 0.375), ('VALIDATOR', 0.125)]

HITL_DECISION_14: Agent=SovereignDecisionEngine | File=arch_governor
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_15: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_16: Agent=SovereignDecisionEngine | File=file_classification
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_17: Agent=SovereignDecisionEngine | File=arch_governor
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_18: Agent=SovereignDecisionEngine | File=cognitive_disposition
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_19: Agent=SovereignDecisionEngine | File=observability_probe
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_20: Agent=SovereignDecisionEngine | File=cognitive_disposition
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_21: Agent=SovereignDecisionEngine | File=arch_governor
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_22: Agent=SovereignDecisionEngine | File=file_classification
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_1: Agent=SovereignDecisionEngine | File=AgentA
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_2: Agent=SovereignDecisionEngine | File=AgentA
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_1: Agent=SovereignDecisionEngine | File=AgentA
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_23: Agent=SovereignDecisionEngine | File=AgentA
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_24: Agent=SovereignDecisionEngine | File=AgentA
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_25: Agent=SovereignDecisionEngine | File=AgentA
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_26: Agent=SovereignDecisionEngine | File=AgentA
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_27: Agent=SovereignDecisionEngine | File=Unknown
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_28: Agent=SovereignDecisionEngine | File=AgentA
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_29: Agent=SovereignDecisionEngine | File=AgentA
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_30: Agent=SovereignDecisionEngine | File=AgentA
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_31: Agent=SovereignDecisionEngine | File=AgentA
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_1: Agent=SovereignDecisionEngine | File=LocationAgent
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_2: Agent=SovereignDecisionEngine | File=TestAgent1
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_1: Agent=SovereignDecisionEngine | File=AgentA
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_2: Agent=SovereignDecisionEngine | File=AgentA
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_1: Agent=SovereignDecisionEngine | File=LocationAgent
  Violation=TIER_ESCALATION:GEMINI_2_5_PRO | Proposed=GEMINI_2_5_PRO | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_2: Agent=SovereignDecisionEngine | File=TestAgent1
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_1: Agent=SovereignDecisionEngine | File=Unknown
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_1: Agent=SovereignDecisionEngine | File=AgentA
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_2: Agent=SovereignDecisionEngine | File=AgentA
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_1: Agent=SovereignDecisionEngine | File=AgentA
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_1: Agent=SovereignDecisionEngine | File=Unknown
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_2: Agent=SovereignDecisionEngine | File=arch_governor
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_1: Agent=SovereignDecisionEngine | File=Unknown
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_1: Agent=FileClassificationAgent | File=C:\Users\amita\AppData\Local\Temp\pytest-of-amita\pytest-191\test_confidence_low_for_mixed_0\hybrid.py
  Violation=AMBIGUOUS_CLASSIFICATION | Proposed=TYPES | Decision=FLAGGED_FOR_REVIEW
  delta=0.125
  top3=[('TYPES', 0.5), ('CONFIG', 0.375), ('VALIDATOR', 0.125)]

HITL_DECISION_1: Agent=SovereignDecisionEngine | File=arch_governor
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_1: Agent=SovereignDecisionEngine | File=Unknown
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_1: Agent=SovereignDecisionEngine | File=Unknown
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_1: Agent=SovereignDecisionEngine | File=arch_governor
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_1: Agent=SovereignDecisionEngine | File=arch_governor
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_1: Agent=FileClassificationAgent | File=C:\Users\amita\AppData\Local\Temp\pytest-of-amita\pytest-218\test_confidence_low_for_mixed_0\hybrid.py
  Violation=AMBIGUOUS_CLASSIFICATION | Proposed=TYPES | Decision=FLAGGED_FOR_REVIEW
  delta=0.125
  top3=[('TYPES', 0.5), ('CONFIG', 0.375), ('VALIDATOR', 0.125)]

HITL_DECISION_1: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\evaluation\retrieval\l4_registries.py
  Violation=LAYER PREFIX VIOLATION: Filename has forbidden prefix 'l4_' | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_2: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\L2_execution\types\l2_phase_spec.py
  Violation=LAYER PREFIX VIOLATION: Filename has forbidden prefix 'l2_' | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_3: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\utils\workflow_engines\l5_safety_aliases.py
  Violation=LAYER PREFIX VIOLATION: Filename has forbidden prefix 'l5_' | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_4: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_5: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_6: Agent=SovereignDecisionEngine | File=ArchitectureGovernorAgent
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_1: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\evaluation\retrieval\l4_registries.py
  Violation=LAYER PREFIX VIOLATION: Filename has forbidden prefix 'l4_' | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_2: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\L2_execution\types\l2_phase_spec.py
  Violation=LAYER PREFIX VIOLATION: Filename has forbidden prefix 'l2_' | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_3: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\utils\workflow_engines\l5_safety_aliases.py
  Violation=LAYER PREFIX VIOLATION: Filename has forbidden prefix 'l5_' | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_4: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_5: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_6: Agent=SovereignDecisionEngine | File=ArchitectureGovernorAgent
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_1: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\evaluation\retrieval\l4_registries.py
  Violation=LAYER PREFIX VIOLATION: Filename has forbidden prefix 'l4_' | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_2: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\L2_execution\types\l2_phase_spec.py
  Violation=LAYER PREFIX VIOLATION: Filename has forbidden prefix 'l2_' | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_3: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\utils\workflow_engines\l5_safety_aliases.py
  Violation=LAYER PREFIX VIOLATION: Filename has forbidden prefix 'l5_' | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_4: Agent=SovereignDecisionEngine | File=reconciler
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_5: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_6: Agent=SovereignDecisionEngine | File=ArchitectureGovernorAgent
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_1: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\evaluation\retrieval\l4_registries.py
  Violation=LAYER PREFIX VIOLATION: Filename has forbidden prefix 'l4_' | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_2: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\L2_execution\types\l2_phase_spec.py
  Violation=LAYER PREFIX VIOLATION: Filename has forbidden prefix 'l2_' | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_3: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_4: Agent=SovereignDecisionEngine | File=ArchitectureGovernorAgent
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_1: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\evaluation\retrieval\l4_registries.py
  Violation=LAYER PREFIX VIOLATION: Filename has forbidden prefix 'l4_' | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_2: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\L2_execution\types\l2_phase_spec.py
  Violation=LAYER PREFIX VIOLATION: Filename has forbidden prefix 'l2_' | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_3: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_4: Agent=SovereignDecisionEngine | File=ArchitectureGovernorAgent
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_1: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\evaluation\retrieval\l4_registries.py
  Violation=LAYER PREFIX VIOLATION: Filename has forbidden prefix 'l4_' | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_2: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\L2_execution\types\l2_phase_spec.py
  Violation=LAYER PREFIX VIOLATION: Filename has forbidden prefix 'l2_' | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_3: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_4: Agent=SovereignDecisionEngine | File=ArchitectureGovernorAgent
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_1: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_2: Agent=SovereignDecisionEngine | File=ArchitectureGovernorAgent
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_1: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_2: Agent=SovereignDecisionEngine | File=ArchitectureGovernorAgent
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_1: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_2: Agent=SovereignDecisionEngine | File=ArchitectureGovernorAgent
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_1: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_2: Agent=SovereignDecisionEngine | File=ArchitectureGovernorAgent
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_1: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_2: Agent=SovereignDecisionEngine | File=ArchitectureGovernorAgent
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_1: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_2: Agent=SovereignDecisionEngine | File=ArchitectureGovernorAgent
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_1: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_2: Agent=SovereignDecisionEngine | File=ArchitectureGovernorAgent
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_1: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_2: Agent=SovereignDecisionEngine | File=ArchitectureGovernorAgent
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_1: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_2: Agent=SovereignDecisionEngine | File=ArchitectureGovernorAgent
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_1: Agent=SovereignDecisionEngine | File=location
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_2: Agent=SovereignDecisionEngine | File=ArchitectureGovernorAgent
  Violation=TIER_ESCALATION:QWEN_VLLM | Proposed=QWEN_VLLM | Decision=HITL-TIER-AUTO-APPROVED (non-interactive)

HITL_DECISION_1: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\metrics_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/telemetry | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_2: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\performance_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/telemetry | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_3: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\ssot_adaptive_execution_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/missions | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_4: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\ssot_audit_trail_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/audit | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_5: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\metrics_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/telemetry | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_6: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\performance_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/telemetry | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_7: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\ssot_adaptive_execution_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/missions | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_8: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\ssot_audit_trail_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/audit | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_9: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\metrics_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/telemetry | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_10: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\performance_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/telemetry | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_11: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\ssot_adaptive_execution_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/missions | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_12: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\ssot_audit_trail_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/audit | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_13: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\apps_shared\utils\canon_error_util.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination agentic_core/L0_routing/utils | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_14: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\apps_shared\utils\health_metrics_util.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/telemetry | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_15: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\e2e\test_gemini_qwen_e2e.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_16: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_key_derivation.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_17: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_negative_control_exit0_tamper.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_18: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_replay_determinism_invariants.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_19: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req016_020_fail_closed.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_20: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req085_086_hil.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_21: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req091_tier3_freeze.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_22: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req095_prompt_determinism.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_23: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req106_replay_sandbox.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_24: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req157_302_trace_replay.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_25: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req158_303_hash_chain_tamper.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_26: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req239_240_quorum.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_27: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req245_248_hil_ttl.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_28: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req346_347_tier3_authority.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_29: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req413_provider_binding_determinism.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_30: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req416_critical_dual_enforcement.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_31: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req_p1_freeze_complete_revocation.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_32: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req_p1_freeze_timing.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_33: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_seam_contracts.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_34: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_shadow_replay.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_35: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_standard_heal_no_routing_contract.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_36: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\guardian\test_certification_evidence_hygiene.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_37: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\guardian\test_contract_compatibility.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_38: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\guardian\test_guardian_manifest.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_39: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\guardian\test_scan_budget_integrity.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_40: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\guardian\test_ssot_heal_runner_preflight.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_41: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\guardian\test_v15_p10_1_review_summary.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_42: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\misc\test_verification_gate_simple.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_43: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\ssot_equivalence\test_execute_ssot_inventory_contract.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_44: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\system_learning\w1_strong_determinism_test.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_45: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\unit\test_phase5_l4_violation_persistence.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_46: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\unit_min_deps\test_apps_lic_spine_adapter.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_47: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\unit_min_deps\test_apps_rg_spine_adapter.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_48: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\unit_min_deps\test_determinism_util.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_49: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\unit_min_deps\test_inspector_mro_contracts.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_50: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\unit_min_deps\test_root_hygiene_contract.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_51: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\unit_min_deps\test_spine_cross_app_contract.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_1: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\metrics_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/telemetry | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_2: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\performance_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/telemetry | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_3: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\ssot_adaptive_execution_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/missions | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_4: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\ssot_audit_trail_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/audit | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_5: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\metrics_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/telemetry | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_6: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\performance_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/telemetry | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_7: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\ssot_adaptive_execution_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/missions | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_8: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\ssot_audit_trail_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/audit | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_9: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\metrics_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/telemetry | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_10: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\performance_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/telemetry | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_11: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\ssot_adaptive_execution_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/missions | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_12: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\ssot_audit_trail_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/audit | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_13: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\apps_shared\utils\canon_error_util.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination agentic_core/L0_routing/utils | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_14: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\apps_shared\utils\health_metrics_util.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/telemetry | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_15: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\e2e\test_gemini_qwen_e2e.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_16: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_key_derivation.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_17: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_negative_control_exit0_tamper.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_18: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_replay_determinism_invariants.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_19: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req016_020_fail_closed.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_20: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req085_086_hil.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_21: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req091_tier3_freeze.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_22: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req095_prompt_determinism.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_23: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req106_replay_sandbox.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_24: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req157_302_trace_replay.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_25: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req158_303_hash_chain_tamper.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_26: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req239_240_quorum.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_27: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req245_248_hil_ttl.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_28: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req346_347_tier3_authority.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_29: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req413_provider_binding_determinism.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_30: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req416_critical_dual_enforcement.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_31: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req_p1_freeze_complete_revocation.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_32: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req_p1_freeze_timing.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_33: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_seam_contracts.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_34: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_shadow_replay.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_35: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_standard_heal_no_routing_contract.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_36: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\guardian\test_certification_evidence_hygiene.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_37: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\guardian\test_contract_compatibility.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_38: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\guardian\test_guardian_manifest.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_39: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\guardian\test_scan_budget_integrity.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_40: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\guardian\test_ssot_heal_runner_preflight.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_41: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\guardian\test_v15_p10_1_review_summary.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_42: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\misc\test_verification_gate_simple.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_43: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\ssot_equivalence\test_execute_ssot_inventory_contract.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_44: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\system_learning\w1_strong_determinism_test.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_45: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\unit\test_phase5_l4_violation_persistence.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_46: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\unit_min_deps\test_apps_lic_spine_adapter.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_47: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\unit_min_deps\test_apps_rg_spine_adapter.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_48: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\unit_min_deps\test_determinism_util.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_49: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\unit_min_deps\test_inspector_mro_contracts.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_50: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\unit_min_deps\test_root_hygiene_contract.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_51: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\unit_min_deps\test_spine_cross_app_contract.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_1: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\metrics_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/telemetry | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_2: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\performance_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/telemetry | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_3: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\ssot_adaptive_execution_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/missions | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_4: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\ssot_audit_trail_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/audit | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_5: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\ssot_circuit_breaker_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden keyword 'class Sovereign' for destination agentic_core/L0_routing/scripts | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_6: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\ssot_metrics_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/telemetry | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_7: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\ssot_mixin_stack.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden keyword 'class Sovereign' for destination agentic_core/L0_routing/scripts | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_8: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\subatomic_testing_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_9: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\runtime\execution_bound_token.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/missions | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_10: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\runtime\execution_trace.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/missions | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_11: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\metrics_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/telemetry | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_12: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\performance_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/telemetry | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_13: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\ssot_adaptive_execution_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/missions | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_14: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\ssot_audit_trail_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/audit | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_15: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\ssot_circuit_breaker_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden keyword 'class Sovereign' for destination agentic_core/L0_routing/scripts | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_16: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\ssot_metrics_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/telemetry | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_17: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\ssot_mixin_stack.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden keyword 'class Sovereign' for destination agentic_core/L0_routing/scripts | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_18: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\subatomic_testing_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_19: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\runtime\execution_bound_token.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/missions | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_20: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\runtime\execution_trace.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/missions | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_21: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\metrics_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/telemetry | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_22: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\performance_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/telemetry | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_23: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\ssot_adaptive_execution_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/missions | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_24: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\ssot_audit_trail_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/audit | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_25: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\ssot_circuit_breaker_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden keyword 'class Sovereign' for destination agentic_core/L0_routing/scripts | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_26: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\ssot_metrics_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/telemetry | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_27: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\ssot_mixin_stack.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden keyword 'class Sovereign' for destination agentic_core/L0_routing/scripts | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_28: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\subatomic_testing_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_29: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\runtime\execution_bound_token.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/missions | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_30: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\runtime\execution_trace.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/missions | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_31: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\apps_shared\utils\canon_error_util.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination agentic_core/L0_routing/utils | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_32: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\apps_shared\utils\health_metrics_util.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/telemetry | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_33: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\e2e\test_gemini_qwen_e2e.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_34: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_key_derivation.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_35: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_negative_control_exit0_tamper.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_36: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_replay_determinism_invariants.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_37: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req016_020_fail_closed.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_38: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req085_086_hil.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_39: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req091_tier3_freeze.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_40: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req095_prompt_determinism.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_41: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req106_replay_sandbox.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_42: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req157_302_trace_replay.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_43: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req158_303_hash_chain_tamper.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_44: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req239_240_quorum.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_45: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req245_248_hil_ttl.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_46: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req346_347_tier3_authority.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_47: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req413_provider_binding_determinism.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_48: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req416_critical_dual_enforcement.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_49: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req_p1_freeze_complete_revocation.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_50: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req_p1_freeze_timing.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_51: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_seam_contracts.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_52: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_shadow_replay.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_53: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_standard_heal_no_routing_contract.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_54: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\guardian\test_certification_evidence_hygiene.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_55: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\guardian\test_contract_compatibility.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_56: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\guardian\test_guardian_manifest.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_57: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\guardian\test_scan_budget_integrity.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_58: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\guardian\test_ssot_heal_runner_preflight.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_59: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\guardian\test_v15_p10_1_review_summary.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_60: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\misc\test_verification_gate_simple.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_61: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\ssot_equivalence\test_execute_ssot_inventory_contract.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_62: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\system_learning\w1_strong_determinism_test.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_63: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\unit\test_phase5_l4_violation_persistence.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_64: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\unit_min_deps\test_apps_lic_spine_adapter.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_65: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\unit_min_deps\test_apps_rg_spine_adapter.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_66: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\unit_min_deps\test_determinism_util.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_67: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\unit_min_deps\test_inspector_mro_contracts.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_68: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\unit_min_deps\test_root_hygiene_contract.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_69: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\unit_min_deps\test_spine_cross_app_contract.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_1: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\metrics_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/telemetry | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_2: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\performance_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/telemetry | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_3: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\ssot_adaptive_execution_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/missions | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_4: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\ssot_audit_trail_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/audit | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_5: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\ssot_circuit_breaker_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden keyword 'class Sovereign' for destination agentic_core/L0_routing/scripts | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_6: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\ssot_metrics_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/telemetry | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_7: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\ssot_mixin_stack.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden keyword 'class Sovereign' for destination agentic_core/L0_routing/scripts | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_8: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\subatomic_testing_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_9: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\runtime\execution_bound_token.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/missions | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_10: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\runtime\execution_trace.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/missions | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_11: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\metrics_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/telemetry | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_12: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\performance_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/telemetry | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_13: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\ssot_adaptive_execution_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/missions | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_14: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\ssot_audit_trail_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/audit | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_15: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\ssot_circuit_breaker_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden keyword 'class Sovereign' for destination agentic_core/L0_routing/scripts | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_16: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\ssot_metrics_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/telemetry | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_17: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\ssot_mixin_stack.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden keyword 'class Sovereign' for destination agentic_core/L0_routing/scripts | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_18: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\subatomic_testing_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_19: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\runtime\execution_bound_token.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/missions | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_20: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\runtime\execution_trace.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/missions | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_21: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\metrics_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/telemetry | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_22: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\performance_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/telemetry | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_23: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\ssot_adaptive_execution_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/missions | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_24: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\ssot_audit_trail_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/audit | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_25: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\ssot_circuit_breaker_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden keyword 'class Sovereign' for destination agentic_core/L0_routing/scripts | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_26: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\ssot_metrics_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/telemetry | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_27: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\ssot_mixin_stack.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden keyword 'class Sovereign' for destination agentic_core/L0_routing/scripts | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_28: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\subatomic_testing_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_29: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\runtime\execution_bound_token.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/missions | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_30: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\runtime\execution_trace.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/missions | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_31: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\apps_shared\utils\canon_error_util.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination agentic_core/L0_routing/utils | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_32: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\apps_shared\utils\health_metrics_util.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/telemetry | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_33: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\e2e\test_gemini_qwen_e2e.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_34: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_key_derivation.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_35: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_negative_control_exit0_tamper.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_36: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_replay_determinism_invariants.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_37: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req016_020_fail_closed.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_38: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req085_086_hil.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_39: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req091_tier3_freeze.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_40: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req095_prompt_determinism.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_41: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req106_replay_sandbox.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_42: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req157_302_trace_replay.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_43: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req158_303_hash_chain_tamper.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_44: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req239_240_quorum.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_45: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req245_248_hil_ttl.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_46: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req346_347_tier3_authority.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_47: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req413_provider_binding_determinism.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_48: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req416_critical_dual_enforcement.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_49: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req_p1_freeze_complete_revocation.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_50: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req_p1_freeze_timing.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_51: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_seam_contracts.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_52: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_shadow_replay.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_53: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_standard_heal_no_routing_contract.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_54: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\guardian\test_certification_evidence_hygiene.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_55: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\guardian\test_contract_compatibility.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_56: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\guardian\test_guardian_manifest.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_57: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\guardian\test_scan_budget_integrity.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_58: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\guardian\test_ssot_heal_runner_preflight.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_59: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\guardian\test_v15_p10_1_review_summary.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_60: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\misc\test_verification_gate_simple.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_61: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\ssot_equivalence\test_execute_ssot_inventory_contract.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_62: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\system_learning\w1_strong_determinism_test.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_63: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\unit\test_phase5_l4_violation_persistence.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_64: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\unit_min_deps\test_apps_lic_spine_adapter.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_65: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\unit_min_deps\test_apps_rg_spine_adapter.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_66: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\unit_min_deps\test_determinism_util.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_67: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\unit_min_deps\test_inspector_mro_contracts.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_68: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\unit_min_deps\test_root_hygiene_contract.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_69: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\unit_min_deps\test_spine_cross_app_contract.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_1: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\metrics_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/telemetry | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_2: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\performance_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/telemetry | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_3: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\ssot_adaptive_execution_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/missions | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_4: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\ssot_audit_trail_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/audit | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_5: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\ssot_circuit_breaker_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden keyword 'class Sovereign' for destination agentic_core/L0_routing/scripts | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_6: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\ssot_metrics_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/telemetry | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_7: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\ssot_mixin_stack.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden keyword 'class Sovereign' for destination agentic_core/L0_routing/scripts | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_8: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\subatomic_testing_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_9: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\runtime\execution_bound_token.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/missions | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_10: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\runtime\execution_trace.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/missions | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_11: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\metrics_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/telemetry | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_12: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\performance_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/telemetry | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_13: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\ssot_adaptive_execution_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/missions | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_14: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\ssot_audit_trail_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/audit | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_15: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\ssot_circuit_breaker_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden keyword 'class Sovereign' for destination agentic_core/L0_routing/scripts | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_16: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\ssot_metrics_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/telemetry | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_17: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\ssot_mixin_stack.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden keyword 'class Sovereign' for destination agentic_core/L0_routing/scripts | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_18: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\subatomic_testing_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_19: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\runtime\execution_bound_token.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/missions | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_20: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\runtime\execution_trace.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/missions | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_21: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\metrics_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/telemetry | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_22: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\performance_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/telemetry | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_23: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\ssot_adaptive_execution_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/missions | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_24: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\ssot_audit_trail_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/audit | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_25: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\ssot_circuit_breaker_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden keyword 'class Sovereign' for destination agentic_core/L0_routing/scripts | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_26: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\ssot_metrics_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/telemetry | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_27: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\ssot_mixin_stack.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden keyword 'class Sovereign' for destination agentic_core/L0_routing/scripts | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_28: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\subatomic_testing_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_29: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\runtime\execution_bound_token.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/missions | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_30: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\runtime\execution_trace.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/missions | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_31: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\apps_shared\utils\canon_error_util.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination agentic_core/L0_routing/utils | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_32: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\apps_shared\utils\health_metrics_util.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/telemetry | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_33: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\e2e\test_gemini_qwen_e2e.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_34: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_key_derivation.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_35: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_negative_control_exit0_tamper.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_36: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_replay_determinism_invariants.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_37: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req016_020_fail_closed.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_38: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req085_086_hil.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_39: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req091_tier3_freeze.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_40: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req095_prompt_determinism.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_41: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req106_replay_sandbox.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_42: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req157_302_trace_replay.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_43: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req158_303_hash_chain_tamper.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_44: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req239_240_quorum.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_45: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req245_248_hil_ttl.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_46: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req346_347_tier3_authority.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_47: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req413_provider_binding_determinism.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_48: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req416_critical_dual_enforcement.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_49: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req_p1_freeze_complete_revocation.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_50: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_req_p1_freeze_timing.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_51: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_seam_contracts.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_52: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_shadow_replay.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_53: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\governance\test_standard_heal_no_routing_contract.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_54: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\guardian\test_certification_evidence_hygiene.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_55: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\guardian\test_contract_compatibility.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_56: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\guardian\test_guardian_manifest.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_57: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\guardian\test_scan_budget_integrity.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_58: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\guardian\test_ssot_heal_runner_preflight.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_59: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\guardian\test_v15_p10_1_review_summary.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_60: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\misc\test_verification_gate_simple.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_61: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\ssot_equivalence\test_execute_ssot_inventory_contract.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_62: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\system_learning\w1_strong_determinism_test.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_63: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\unit\test_phase5_l4_violation_persistence.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_64: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\unit_min_deps\test_apps_lic_spine_adapter.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_65: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\unit_min_deps\test_apps_rg_spine_adapter.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_66: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\unit_min_deps\test_determinism_util.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_67: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\unit_min_deps\test_inspector_mro_contracts.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_68: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\unit_min_deps\test_root_hygiene_contract.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_69: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\tests\unit_min_deps\test_spine_cross_app_contract.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/coverage | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=resume_writer | Decision=corrected_to=code_reviewer
  decision_type=routing_correction
  wrong_target=resume_writer
  correct_target=code_reviewer
  confidence=0.3

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=resume_writer | Decision=corrected_to=code_reviewer
  decision_type=routing_correction
  wrong_target=resume_writer
  correct_target=code_reviewer
  confidence=0.0

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=resume_writer | Decision=corrected_to=code_reviewer
  decision_type=routing_correction
  wrong_target=resume_writer
  correct_target=code_reviewer
  confidence=0.0

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=a | Decision=corrected_to=b
  decision_type=routing_correction
  wrong_target=a
  correct_target=b
  confidence=0.0

HITL_DECISION_2: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=b | Decision=corrected_to=c
  decision_type=routing_correction
  wrong_target=b
  correct_target=c
  confidence=0.0

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=wrong | Decision=corrected_to=correct
  decision_type=routing_correction
  wrong_target=wrong
  correct_target=correct
  confidence=0.0

HITL_DECISION_2: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=wrong | Decision=corrected_to=correct
  decision_type=routing_correction
  wrong_target=wrong
  correct_target=correct
  confidence=0.0

HITL_DECISION_3: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=wrong | Decision=corrected_to=correct
  decision_type=routing_correction
  wrong_target=wrong
  correct_target=correct
  confidence=0.0

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=a | Decision=corrected_to=b
  decision_type=routing_correction
  wrong_target=a
  correct_target=b
  confidence=0.0

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=c | Decision=corrected_to=d
  decision_type=routing_correction
  wrong_target=c
  correct_target=d
  confidence=0.0

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=a | Decision=corrected_to=b
  decision_type=routing_correction
  wrong_target=a
  correct_target=b
  confidence=0.0

HITL_DECISION_2: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=c | Decision=corrected_to=d
  decision_type=routing_correction
  wrong_target=c
  correct_target=d
  confidence=0.0

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=wrong | Decision=corrected_to=correct
  decision_type=routing_correction
  wrong_target=wrong
  correct_target=correct
  confidence=0.0

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=wrong | Decision=corrected_to=correct
  decision_type=routing_correction
  wrong_target=wrong
  correct_target=correct
  confidence=0.35

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=wrong | Decision=corrected_to=correct
  decision_type=routing_correction
  wrong_target=wrong
  correct_target=correct
  confidence=0.5
  trace_id=t-123
  run_id=r-456

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=wrong | Decision=corrected_to=correct
  decision_type=routing_correction
  wrong_target=wrong
  correct_target=correct
  confidence=0.1

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=wrong | Decision=corrected_to=correct
  decision_type=routing_correction
  wrong_target=wrong
  correct_target=correct
  confidence=0.0

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=wrong | Decision=corrected_to=correct
  decision_type=routing_correction
  wrong_target=wrong
  correct_target=correct
  confidence=0.3

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to= | Decision=corrected_to=
  decision_type=routing_correction
  wrong_target=
  correct_target=
  confidence=0.0

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=a | Decision=corrected_to=b
  decision_type=routing_correction
  wrong_target=a
  correct_target=b
  confidence=0.99

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=a | Decision=corrected_to=b
  decision_type=routing_correction
  wrong_target=a
  correct_target=b
  confidence=0.0

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=x | Decision=corrected_to=y
  decision_type=routing_correction
  wrong_target=x
  correct_target=y
  confidence=0.5

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=w | Decision=corrected_to=c
  decision_type=routing_correction
  wrong_target=w
  correct_target=c
  confidence=0.3

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=w | Decision=corrected_to=c
  decision_type=routing_correction
  wrong_target=w
  correct_target=c
  confidence=0.1

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=resume_writer | Decision=corrected_to=code_reviewer
  decision_type=routing_correction
  wrong_target=resume_writer
  correct_target=code_reviewer
  confidence=0.0

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=resume_writer | Decision=corrected_to=code_reviewer
  decision_type=routing_correction
  wrong_target=resume_writer
  correct_target=code_reviewer
  confidence=0.0

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=a | Decision=corrected_to=b
  decision_type=routing_correction
  wrong_target=a
  correct_target=b
  confidence=0.0

HITL_DECISION_2: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=b | Decision=corrected_to=c
  decision_type=routing_correction
  wrong_target=b
  correct_target=c
  confidence=0.0

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=wrong | Decision=corrected_to=correct
  decision_type=routing_correction
  wrong_target=wrong
  correct_target=correct
  confidence=0.0

HITL_DECISION_2: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=wrong | Decision=corrected_to=correct
  decision_type=routing_correction
  wrong_target=wrong
  correct_target=correct
  confidence=0.0

HITL_DECISION_3: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=wrong | Decision=corrected_to=correct
  decision_type=routing_correction
  wrong_target=wrong
  correct_target=correct
  confidence=0.0

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=a | Decision=corrected_to=b
  decision_type=routing_correction
  wrong_target=a
  correct_target=b
  confidence=0.0

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=c | Decision=corrected_to=d
  decision_type=routing_correction
  wrong_target=c
  correct_target=d
  confidence=0.0

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=a | Decision=corrected_to=b
  decision_type=routing_correction
  wrong_target=a
  correct_target=b
  confidence=0.0

HITL_DECISION_2: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=c | Decision=corrected_to=d
  decision_type=routing_correction
  wrong_target=c
  correct_target=d
  confidence=0.0

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=wrong | Decision=corrected_to=correct
  decision_type=routing_correction
  wrong_target=wrong
  correct_target=correct
  confidence=0.0

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=wrong | Decision=corrected_to=correct
  decision_type=routing_correction
  wrong_target=wrong
  correct_target=correct
  confidence=0.35

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=wrong | Decision=corrected_to=correct
  decision_type=routing_correction
  wrong_target=wrong
  correct_target=correct
  confidence=0.5
  trace_id=t-123
  run_id=r-456

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=wrong | Decision=corrected_to=correct
  decision_type=routing_correction
  wrong_target=wrong
  correct_target=correct
  confidence=0.1

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=wrong | Decision=corrected_to=correct
  decision_type=routing_correction
  wrong_target=wrong
  correct_target=correct
  confidence=0.0

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=wrong | Decision=corrected_to=correct
  decision_type=routing_correction
  wrong_target=wrong
  correct_target=correct
  confidence=0.3

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to= | Decision=corrected_to=
  decision_type=routing_correction
  wrong_target=
  correct_target=
  confidence=0.0

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=a | Decision=corrected_to=b
  decision_type=routing_correction
  wrong_target=a
  correct_target=b
  confidence=0.99

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=a | Decision=corrected_to=b
  decision_type=routing_correction
  wrong_target=a
  correct_target=b
  confidence=0.0

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=x | Decision=corrected_to=y
  decision_type=routing_correction
  wrong_target=x
  correct_target=y
  confidence=0.5

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=w | Decision=corrected_to=c
  decision_type=routing_correction
  wrong_target=w
  correct_target=c
  confidence=0.3

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=w | Decision=corrected_to=c
  decision_type=routing_correction
  wrong_target=w
  correct_target=c
  confidence=0.1

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=resume_writer | Decision=corrected_to=code_reviewer
  decision_type=routing_correction
  wrong_target=resume_writer
  correct_target=code_reviewer
  confidence=0.0

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=resume_writer | Decision=corrected_to=code_reviewer
  decision_type=routing_correction
  wrong_target=resume_writer
  correct_target=code_reviewer
  confidence=0.0

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=a | Decision=corrected_to=b
  decision_type=routing_correction
  wrong_target=a
  correct_target=b
  confidence=0.0

HITL_DECISION_2: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=b | Decision=corrected_to=c
  decision_type=routing_correction
  wrong_target=b
  correct_target=c
  confidence=0.0

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=wrong | Decision=corrected_to=correct
  decision_type=routing_correction
  wrong_target=wrong
  correct_target=correct
  confidence=0.0

HITL_DECISION_2: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=wrong | Decision=corrected_to=correct
  decision_type=routing_correction
  wrong_target=wrong
  correct_target=correct
  confidence=0.0

HITL_DECISION_3: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=wrong | Decision=corrected_to=correct
  decision_type=routing_correction
  wrong_target=wrong
  correct_target=correct
  confidence=0.0

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=a | Decision=corrected_to=b
  decision_type=routing_correction
  wrong_target=a
  correct_target=b
  confidence=0.0

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=c | Decision=corrected_to=d
  decision_type=routing_correction
  wrong_target=c
  correct_target=d
  confidence=0.0

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=a | Decision=corrected_to=b
  decision_type=routing_correction
  wrong_target=a
  correct_target=b
  confidence=0.0

HITL_DECISION_2: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=c | Decision=corrected_to=d
  decision_type=routing_correction
  wrong_target=c
  correct_target=d
  confidence=0.0

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=wrong | Decision=corrected_to=correct
  decision_type=routing_correction
  wrong_target=wrong
  correct_target=correct
  confidence=0.0

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=wrong | Decision=corrected_to=correct
  decision_type=routing_correction
  wrong_target=wrong
  correct_target=correct
  confidence=0.35

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=wrong | Decision=corrected_to=correct
  decision_type=routing_correction
  wrong_target=wrong
  correct_target=correct
  confidence=0.5
  trace_id=t-123
  run_id=r-456

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=wrong | Decision=corrected_to=correct
  decision_type=routing_correction
  wrong_target=wrong
  correct_target=correct
  confidence=0.1

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=wrong | Decision=corrected_to=correct
  decision_type=routing_correction
  wrong_target=wrong
  correct_target=correct
  confidence=0.0

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=wrong | Decision=corrected_to=correct
  decision_type=routing_correction
  wrong_target=wrong
  correct_target=correct
  confidence=0.3

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to= | Decision=corrected_to=
  decision_type=routing_correction
  wrong_target=
  correct_target=
  confidence=0.0

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=a | Decision=corrected_to=b
  decision_type=routing_correction
  wrong_target=a
  correct_target=b
  confidence=0.99

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=a | Decision=corrected_to=b
  decision_type=routing_correction
  wrong_target=a
  correct_target=b
  confidence=0.0

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=x | Decision=corrected_to=y
  decision_type=routing_correction
  wrong_target=x
  correct_target=y
  confidence=0.5

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=w | Decision=corrected_to=c
  decision_type=routing_correction
  wrong_target=w
  correct_target=c
  confidence=0.3

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=w | Decision=corrected_to=c
  decision_type=routing_correction
  wrong_target=w
  correct_target=c
  confidence=0.1

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=resume_writer | Decision=corrected_to=code_reviewer
  decision_type=routing_correction
  wrong_target=resume_writer
  correct_target=code_reviewer
  confidence=0.0

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=resume_writer | Decision=corrected_to=code_reviewer
  decision_type=routing_correction
  wrong_target=resume_writer
  correct_target=code_reviewer
  confidence=0.0

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=a | Decision=corrected_to=b
  decision_type=routing_correction
  wrong_target=a
  correct_target=b
  confidence=0.0

HITL_DECISION_2: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=b | Decision=corrected_to=c
  decision_type=routing_correction
  wrong_target=b
  correct_target=c
  confidence=0.0

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=wrong | Decision=corrected_to=correct
  decision_type=routing_correction
  wrong_target=wrong
  correct_target=correct
  confidence=0.0

HITL_DECISION_2: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=wrong | Decision=corrected_to=correct
  decision_type=routing_correction
  wrong_target=wrong
  correct_target=correct
  confidence=0.0

HITL_DECISION_3: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=wrong | Decision=corrected_to=correct
  decision_type=routing_correction
  wrong_target=wrong
  correct_target=correct
  confidence=0.0

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=a | Decision=corrected_to=b
  decision_type=routing_correction
  wrong_target=a
  correct_target=b
  confidence=0.0

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=c | Decision=corrected_to=d
  decision_type=routing_correction
  wrong_target=c
  correct_target=d
  confidence=0.0

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=a | Decision=corrected_to=b
  decision_type=routing_correction
  wrong_target=a
  correct_target=b
  confidence=0.0

HITL_DECISION_2: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=c | Decision=corrected_to=d
  decision_type=routing_correction
  wrong_target=c
  correct_target=d
  confidence=0.0

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=wrong | Decision=corrected_to=correct
  decision_type=routing_correction
  wrong_target=wrong
  correct_target=correct
  confidence=0.0

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=wrong | Decision=corrected_to=correct
  decision_type=routing_correction
  wrong_target=wrong
  correct_target=correct
  confidence=0.35

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=wrong | Decision=corrected_to=correct
  decision_type=routing_correction
  wrong_target=wrong
  correct_target=correct
  confidence=0.5
  trace_id=t-123
  run_id=r-456

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=wrong | Decision=corrected_to=correct
  decision_type=routing_correction
  wrong_target=wrong
  correct_target=correct
  confidence=0.1

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=wrong | Decision=corrected_to=correct
  decision_type=routing_correction
  wrong_target=wrong
  correct_target=correct
  confidence=0.0

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=wrong | Decision=corrected_to=correct
  decision_type=routing_correction
  wrong_target=wrong
  correct_target=correct
  confidence=0.3

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to= | Decision=corrected_to=
  decision_type=routing_correction
  wrong_target=
  correct_target=
  confidence=0.0

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=a | Decision=corrected_to=b
  decision_type=routing_correction
  wrong_target=a
  correct_target=b
  confidence=0.99

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=a | Decision=corrected_to=b
  decision_type=routing_correction
  wrong_target=a
  correct_target=b
  confidence=0.0

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=x | Decision=corrected_to=y
  decision_type=routing_correction
  wrong_target=x
  correct_target=y
  confidence=0.5

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=w | Decision=corrected_to=c
  decision_type=routing_correction
  wrong_target=w
  correct_target=c
  confidence=0.3

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=w | Decision=corrected_to=c
  decision_type=routing_correction
  wrong_target=w
  correct_target=c
  confidence=0.1

HITL_DECISION_1: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\interfaces\execution.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/missions | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_2: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\interfaces\execution_contracts.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/missions | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_3: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\interfaces\meta_learning.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden keyword 'class Sovereign' for destination agentic_core/L0_routing/scripts | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_1: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\base_agents\SovereignBaseAgent.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden keyword 'class Sovereign' for destination agentic_core/L0_routing/scripts | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_2: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\L2_execution\trace_context.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/missions | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_3: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\L2_execution\trace_context.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/missions | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_1: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\L2_execution\trace_context.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/missions | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_2: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\atomic_execution_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/missions | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_3: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\L2_execution\trace_context.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/missions | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_4: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\atomic_execution_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/missions | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_5: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\L2_execution\trace_context.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/missions | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_6: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\atomic_execution_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/missions | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_7: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\hardening_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/security | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_1: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\L2_execution\trace_context.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/missions | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_2: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\adaptive_execution_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/missions | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_3: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\atomic_execution_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/missions | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_4: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\audit_trail_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/audit | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_5: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\event_emission_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/missions | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_6: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\hardening_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/security | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_7: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\mcp_hardened_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/security | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_8: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\L2_execution\trace_context.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/missions | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_9: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\adaptive_execution_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/missions | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_10: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\atomic_execution_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/missions | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_11: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\audit_trail_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/audit | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_12: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\event_emission_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/missions | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_13: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\hardening_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/security | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_14: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\mcp_hardened_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/security | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_15: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\L2_execution\trace_context.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/missions | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_16: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\adaptive_execution_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/missions | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_17: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\atomic_execution_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/missions | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_18: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\audit_trail_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/audit | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_19: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\event_emission_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/missions | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_20: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\hardening_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/security | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_21: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\mcp_hardened_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/security | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_22: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\L2_execution\trace_context.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/missions | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_23: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\adaptive_execution_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/missions | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_24: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\atomic_execution_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/missions | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_25: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\audit_trail_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/audit | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_26: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\event_emission_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/missions | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_27: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\hardening_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/security | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_28: Agent=LocationHealerAgent | File=C:\Git\Agentic-Workflow\agentic_core\mixins\mcp_hardened_mixin.py
  Violation=ARTIFACT ROUTING VIOLATION: Forbidden extension .py for destination docs/reports/security | Proposed=ARCHIVE | Decision=APPROVED

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=resume_writer | Decision=corrected_to=code_reviewer
  decision_type=routing_correction
  wrong_target=resume_writer
  correct_target=code_reviewer
  confidence=0.0

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=resume_writer | Decision=corrected_to=code_reviewer
  decision_type=routing_correction
  wrong_target=resume_writer
  correct_target=code_reviewer
  confidence=0.0

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=a | Decision=corrected_to=b
  decision_type=routing_correction
  wrong_target=a
  correct_target=b
  confidence=0.0

HITL_DECISION_2: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=b | Decision=corrected_to=c
  decision_type=routing_correction
  wrong_target=b
  correct_target=c
  confidence=0.0

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=wrong | Decision=corrected_to=correct
  decision_type=routing_correction
  wrong_target=wrong
  correct_target=correct
  confidence=0.0

HITL_DECISION_2: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=wrong | Decision=corrected_to=correct
  decision_type=routing_correction
  wrong_target=wrong
  correct_target=correct
  confidence=0.0

HITL_DECISION_3: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=wrong | Decision=corrected_to=correct
  decision_type=routing_correction
  wrong_target=wrong
  correct_target=correct
  confidence=0.0

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=a | Decision=corrected_to=b
  decision_type=routing_correction
  wrong_target=a
  correct_target=b
  confidence=0.0

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=c | Decision=corrected_to=d
  decision_type=routing_correction
  wrong_target=c
  correct_target=d
  confidence=0.0

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=a | Decision=corrected_to=b
  decision_type=routing_correction
  wrong_target=a
  correct_target=b
  confidence=0.0

HITL_DECISION_2: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=c | Decision=corrected_to=d
  decision_type=routing_correction
  wrong_target=c
  correct_target=d
  confidence=0.0

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=wrong | Decision=corrected_to=correct
  decision_type=routing_correction
  wrong_target=wrong
  correct_target=correct
  confidence=0.0

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=wrong | Decision=corrected_to=correct
  decision_type=routing_correction
  wrong_target=wrong
  correct_target=correct
  confidence=0.35

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=wrong | Decision=corrected_to=correct
  decision_type=routing_correction
  wrong_target=wrong
  correct_target=correct
  confidence=0.5
  trace_id=t-123
  run_id=r-456

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=wrong | Decision=corrected_to=correct
  decision_type=routing_correction
  wrong_target=wrong
  correct_target=correct
  confidence=0.1

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=wrong | Decision=corrected_to=correct
  decision_type=routing_correction
  wrong_target=wrong
  correct_target=correct
  confidence=0.0

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=wrong | Decision=corrected_to=correct
  decision_type=routing_correction
  wrong_target=wrong
  correct_target=correct
  confidence=0.3

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to= | Decision=corrected_to=
  decision_type=routing_correction
  wrong_target=
  correct_target=
  confidence=0.0

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=a | Decision=corrected_to=b
  decision_type=routing_correction
  wrong_target=a
  correct_target=b
  confidence=0.99

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=a | Decision=corrected_to=b
  decision_type=routing_correction
  wrong_target=a
  correct_target=b
  confidence=0.0

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=x | Decision=corrected_to=y
  decision_type=routing_correction
  wrong_target=x
  correct_target=y
  confidence=0.5

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=w | Decision=corrected_to=c
  decision_type=routing_correction
  wrong_target=w
  correct_target=c
  confidence=0.3

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=w | Decision=corrected_to=c
  decision_type=routing_correction
  wrong_target=w
  correct_target=c
  confidence=0.1

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=resume_writer | Decision=corrected_to=code_reviewer
  decision_type=routing_correction
  wrong_target=resume_writer
  correct_target=code_reviewer
  confidence=0.0

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=resume_writer | Decision=corrected_to=code_reviewer
  decision_type=routing_correction
  wrong_target=resume_writer
  correct_target=code_reviewer
  confidence=0.0

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=a | Decision=corrected_to=b
  decision_type=routing_correction
  wrong_target=a
  correct_target=b
  confidence=0.0

HITL_DECISION_2: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=b | Decision=corrected_to=c
  decision_type=routing_correction
  wrong_target=b
  correct_target=c
  confidence=0.0

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=wrong | Decision=corrected_to=correct
  decision_type=routing_correction
  wrong_target=wrong
  correct_target=correct
  confidence=0.0

HITL_DECISION_2: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=wrong | Decision=corrected_to=correct
  decision_type=routing_correction
  wrong_target=wrong
  correct_target=correct
  confidence=0.0

HITL_DECISION_3: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=wrong | Decision=corrected_to=correct
  decision_type=routing_correction
  wrong_target=wrong
  correct_target=correct
  confidence=0.0

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=a | Decision=corrected_to=b
  decision_type=routing_correction
  wrong_target=a
  correct_target=b
  confidence=0.0

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=c | Decision=corrected_to=d
  decision_type=routing_correction
  wrong_target=c
  correct_target=d
  confidence=0.0

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=a | Decision=corrected_to=b
  decision_type=routing_correction
  wrong_target=a
  correct_target=b
  confidence=0.0

HITL_DECISION_2: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=c | Decision=corrected_to=d
  decision_type=routing_correction
  wrong_target=c
  correct_target=d
  confidence=0.0

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=wrong | Decision=corrected_to=correct
  decision_type=routing_correction
  wrong_target=wrong
  correct_target=correct
  confidence=0.0

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=wrong | Decision=corrected_to=correct
  decision_type=routing_correction
  wrong_target=wrong
  correct_target=correct
  confidence=0.35

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=wrong | Decision=corrected_to=correct
  decision_type=routing_correction
  wrong_target=wrong
  correct_target=correct
  confidence=0.5
  trace_id=t-123
  run_id=r-456

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=wrong | Decision=corrected_to=correct
  decision_type=routing_correction
  wrong_target=wrong
  correct_target=correct
  confidence=0.1

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=wrong | Decision=corrected_to=correct
  decision_type=routing_correction
  wrong_target=wrong
  correct_target=correct
  confidence=0.0

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=wrong | Decision=corrected_to=correct
  decision_type=routing_correction
  wrong_target=wrong
  correct_target=correct
  confidence=0.3

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to= | Decision=corrected_to=
  decision_type=routing_correction
  wrong_target=
  correct_target=
  confidence=0.0

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=a | Decision=corrected_to=b
  decision_type=routing_correction
  wrong_target=a
  correct_target=b
  confidence=0.99

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=a | Decision=corrected_to=b
  decision_type=routing_correction
  wrong_target=a
  correct_target=b
  confidence=0.0

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=x | Decision=corrected_to=y
  decision_type=routing_correction
  wrong_target=x
  correct_target=y
  confidence=0.5

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=w | Decision=corrected_to=c
  decision_type=routing_correction
  wrong_target=w
  correct_target=c
  confidence=0.3

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=w | Decision=corrected_to=c
  decision_type=routing_correction
  wrong_target=w
  correct_target=c
  confidence=0.1

HITL_DECISION_1: Agent=Agent-7 | File=module_7_0.py
  Violation=violation-7-0 | Proposed=fix-7-0 | Decision=APPROVE

HITL_DECISION_2: Agent=Agent-0 | File=module_0_0.py
  Violation=violation-0-0 | Proposed=fix-0-0 | Decision=APPROVE

HITL_DECISION_3: Agent=Agent-1 | File=module_1_0.py
  Violation=violation-1-0 | Proposed=fix-1-0 | Decision=APPROVE

HITL_DECISION_4: Agent=Agent-2 | File=module_2_0.py
  Violation=violation-2-0 | Proposed=fix-2-0 | Decision=APPROVE

HITL_DECISION_5: Agent=Agent-3 | File=module_3_0.py
  Violation=violation-3-0 | Proposed=fix-3-0 | Decision=APPROVE

HITL_DECISION_6: Agent=Agent-4 | File=module_4_0.py
  Violation=violation-4-0 | Proposed=fix-4-0 | Decision=APPROVE

HITL_DECISION_7: Agent=Agent-5 | File=module_5_0.py
  Violation=violation-5-0 | Proposed=fix-5-0 | Decision=APPROVE

HITL_DECISION_8: Agent=Agent-6 | File=module_6_0.py
  Violation=violation-6-0 | Proposed=fix-6-0 | Decision=APPROVE

HITL_DECISION_9: Agent=Agent-7 | File=module_7_1.py
  Violation=violation-7-1 | Proposed=fix-7-1 | Decision=REJECT

HITL_DECISION_10: Agent=Agent-0 | File=module_0_1.py
  Violation=violation-0-1 | Proposed=fix-0-1 | Decision=REJECT

HITL_DECISION_11: Agent=Agent-1 | File=module_1_1.py
  Violation=violation-1-1 | Proposed=fix-1-1 | Decision=REJECT

HITL_DECISION_12: Agent=Agent-2 | File=module_2_1.py
  Violation=violation-2-1 | Proposed=fix-2-1 | Decision=REJECT

HITL_DECISION_13: Agent=Agent-3 | File=module_3_1.py
  Violation=violation-3-1 | Proposed=fix-3-1 | Decision=REJECT

HITL_DECISION_14: Agent=Agent-4 | File=module_4_1.py
  Violation=violation-4-1 | Proposed=fix-4-1 | Decision=REJECT

HITL_DECISION_15: Agent=Agent-5 | File=module_5_1.py
  Violation=violation-5-1 | Proposed=fix-5-1 | Decision=REJECT

HITL_DECISION_16: Agent=Agent-6 | File=module_6_1.py
  Violation=violation-6-1 | Proposed=fix-6-1 | Decision=REJECT

HITL_DECISION_17: Agent=Agent-7 | File=module_7_2.py
  Violation=violation-7-2 | Proposed=fix-7-2 | Decision=APPROVE

HITL_DECISION_18: Agent=Agent-0 | File=module_0_2.py
  Violation=violation-0-2 | Proposed=fix-0-2 | Decision=APPROVE

HITL_DECISION_19: Agent=Agent-1 | File=module_1_2.py
  Violation=violation-1-2 | Proposed=fix-1-2 | Decision=APPROVE

HITL_DECISION_20: Agent=Agent-2 | File=module_2_2.py
  Violation=violation-2-2 | Proposed=fix-2-2 | Decision=APPROVE

HITL_DECISION_21: Agent=Agent-3 | File=module_3_2.py
  Violation=violation-3-2 | Proposed=fix-3-2 | Decision=APPROVE

HITL_DECISION_22: Agent=Agent-4 | File=module_4_2.py
  Violation=violation-4-2 | Proposed=fix-4-2 | Decision=APPROVE

HITL_DECISION_23: Agent=Agent-5 | File=module_5_2.py
  Violation=violation-5-2 | Proposed=fix-5-2 | Decision=APPROVE

HITL_DECISION_24: Agent=Agent-6 | File=module_6_2.py
  Violation=violation-6-2 | Proposed=fix-6-2 | Decision=APPROVE

HITL_DECISION_25: Agent=Agent-7 | File=module_7_3.py
  Violation=violation-7-3 | Proposed=fix-7-3 | Decision=REJECT

HITL_DECISION_26: Agent=Agent-0 | File=module_0_3.py
  Violation=violation-0-3 | Proposed=fix-0-3 | Decision=REJECT

HITL_DECISION_27: Agent=Agent-1 | File=module_1_3.py
  Violation=violation-1-3 | Proposed=fix-1-3 | Decision=REJECT

HITL_DECISION_28: Agent=Agent-2 | File=module_2_3.py
  Violation=violation-2-3 | Proposed=fix-2-3 | Decision=REJECT

HITL_DECISION_29: Agent=Agent-3 | File=module_3_3.py
  Violation=violation-3-3 | Proposed=fix-3-3 | Decision=REJECT

HITL_DECISION_30: Agent=Agent-4 | File=module_4_3.py
  Violation=violation-4-3 | Proposed=fix-4-3 | Decision=REJECT

HITL_DECISION_31: Agent=Agent-5 | File=module_5_3.py
  Violation=violation-5-3 | Proposed=fix-5-3 | Decision=REJECT

HITL_DECISION_32: Agent=Agent-6 | File=module_6_3.py
  Violation=violation-6-3 | Proposed=fix-6-3 | Decision=REJECT

HITL_DECISION_33: Agent=Agent-7 | File=module_7_4.py
  Violation=violation-7-4 | Proposed=fix-7-4 | Decision=APPROVE

HITL_DECISION_34: Agent=Agent-0 | File=module_0_4.py
  Violation=violation-0-4 | Proposed=fix-0-4 | Decision=APPROVE

HITL_DECISION_35: Agent=Agent-1 | File=module_1_4.py
  Violation=violation-1-4 | Proposed=fix-1-4 | Decision=APPROVE

HITL_DECISION_36: Agent=Agent-2 | File=module_2_4.py
  Violation=violation-2-4 | Proposed=fix-2-4 | Decision=APPROVE

HITL_DECISION_37: Agent=Agent-3 | File=module_3_4.py
  Violation=violation-3-4 | Proposed=fix-3-4 | Decision=APPROVE

HITL_DECISION_38: Agent=Agent-4 | File=module_4_4.py
  Violation=violation-4-4 | Proposed=fix-4-4 | Decision=APPROVE

HITL_DECISION_39: Agent=Agent-5 | File=module_5_4.py
  Violation=violation-5-4 | Proposed=fix-5-4 | Decision=APPROVE

HITL_DECISION_40: Agent=Agent-6 | File=module_6_4.py
  Violation=violation-6-4 | Proposed=fix-6-4 | Decision=APPROVE

HITL_DECISION_41: Agent=Agent-7 | File=module_7_5.py
  Violation=violation-7-5 | Proposed=fix-7-5 | Decision=REJECT

HITL_DECISION_42: Agent=Agent-0 | File=module_0_5.py
  Violation=violation-0-5 | Proposed=fix-0-5 | Decision=REJECT

HITL_DECISION_43: Agent=Agent-1 | File=module_1_5.py
  Violation=violation-1-5 | Proposed=fix-1-5 | Decision=REJECT

HITL_DECISION_44: Agent=Agent-2 | File=module_2_5.py
  Violation=violation-2-5 | Proposed=fix-2-5 | Decision=REJECT

HITL_DECISION_45: Agent=Agent-3 | File=module_3_5.py
  Violation=violation-3-5 | Proposed=fix-3-5 | Decision=REJECT

HITL_DECISION_46: Agent=Agent-4 | File=module_4_5.py
  Violation=violation-4-5 | Proposed=fix-4-5 | Decision=REJECT

HITL_DECISION_47: Agent=Agent-5 | File=module_5_5.py
  Violation=violation-5-5 | Proposed=fix-5-5 | Decision=REJECT

HITL_DECISION_48: Agent=Agent-5 | File=module_5_6.py
  Violation=violation-5-6 | Proposed=fix-5-6 | Decision=APPROVE

HITL_DECISION_49: Agent=Agent-7 | File=module_7_6.py
  Violation=violation-7-6 | Proposed=fix-7-6 | Decision=APPROVE

HITL_DECISION_50: Agent=Agent-0 | File=module_0_6.py
  Violation=violation-0-6 | Proposed=fix-0-6 | Decision=APPROVE

HITL_DECISION_51: Agent=Agent-1 | File=module_1_6.py
  Violation=violation-1-6 | Proposed=fix-1-6 | Decision=APPROVE

HITL_DECISION_52: Agent=Agent-2 | File=module_2_6.py
  Violation=violation-2-6 | Proposed=fix-2-6 | Decision=APPROVE

HITL_DECISION_53: Agent=Agent-3 | File=module_3_6.py
  Violation=violation-3-6 | Proposed=fix-3-6 | Decision=APPROVE

HITL_DECISION_54: Agent=Agent-4 | File=module_4_6.py
  Violation=violation-4-6 | Proposed=fix-4-6 | Decision=APPROVE

HITL_DECISION_55: Agent=Agent-6 | File=module_6_5.py
  Violation=violation-6-5 | Proposed=fix-6-5 | Decision=REJECT

HITL_DECISION_56: Agent=Agent-5 | File=module_5_7.py
  Violation=violation-5-7 | Proposed=fix-5-7 | Decision=REJECT

HITL_DECISION_57: Agent=Agent-7 | File=module_7_7.py
  Violation=violation-7-7 | Proposed=fix-7-7 | Decision=REJECT

HITL_DECISION_58: Agent=Agent-0 | File=module_0_7.py
  Violation=violation-0-7 | Proposed=fix-0-7 | Decision=REJECT

HITL_DECISION_59: Agent=Agent-1 | File=module_1_7.py
  Violation=violation-1-7 | Proposed=fix-1-7 | Decision=REJECT

HITL_DECISION_60: Agent=Agent-2 | File=module_2_7.py
  Violation=violation-2-7 | Proposed=fix-2-7 | Decision=REJECT

HITL_DECISION_61: Agent=Agent-3 | File=module_3_7.py
  Violation=violation-3-7 | Proposed=fix-3-7 | Decision=REJECT

HITL_DECISION_62: Agent=Agent-4 | File=module_4_7.py
  Violation=violation-4-7 | Proposed=fix-4-7 | Decision=REJECT

HITL_DECISION_63: Agent=Agent-6 | File=module_6_6.py
  Violation=violation-6-6 | Proposed=fix-6-6 | Decision=APPROVE

HITL_DECISION_64: Agent=Agent-5 | File=module_5_8.py
  Violation=violation-5-8 | Proposed=fix-5-8 | Decision=APPROVE

HITL_DECISION_65: Agent=Agent-7 | File=module_7_8.py
  Violation=violation-7-8 | Proposed=fix-7-8 | Decision=APPROVE

HITL_DECISION_66: Agent=Agent-0 | File=module_0_8.py
  Violation=violation-0-8 | Proposed=fix-0-8 | Decision=APPROVE

HITL_DECISION_67: Agent=Agent-1 | File=module_1_8.py
  Violation=violation-1-8 | Proposed=fix-1-8 | Decision=APPROVE

HITL_DECISION_68: Agent=Agent-2 | File=module_2_8.py
  Violation=violation-2-8 | Proposed=fix-2-8 | Decision=APPROVE

HITL_DECISION_69: Agent=Agent-3 | File=module_3_8.py
  Violation=violation-3-8 | Proposed=fix-3-8 | Decision=APPROVE

HITL_DECISION_70: Agent=Agent-4 | File=module_4_8.py
  Violation=violation-4-8 | Proposed=fix-4-8 | Decision=APPROVE

HITL_DECISION_71: Agent=Agent-6 | File=module_6_7.py
  Violation=violation-6-7 | Proposed=fix-6-7 | Decision=REJECT

HITL_DECISION_72: Agent=Agent-5 | File=module_5_9.py
  Violation=violation-5-9 | Proposed=fix-5-9 | Decision=REJECT

HITL_DECISION_73: Agent=Agent-7 | File=module_7_9.py
  Violation=violation-7-9 | Proposed=fix-7-9 | Decision=REJECT

HITL_DECISION_74: Agent=Agent-0 | File=module_0_9.py
  Violation=violation-0-9 | Proposed=fix-0-9 | Decision=REJECT

HITL_DECISION_75: Agent=Agent-1 | File=module_1_9.py
  Violation=violation-1-9 | Proposed=fix-1-9 | Decision=REJECT

HITL_DECISION_76: Agent=Agent-2 | File=module_2_9.py
  Violation=violation-2-9 | Proposed=fix-2-9 | Decision=REJECT

HITL_DECISION_77: Agent=Agent-3 | File=module_3_9.py
  Violation=violation-3-9 | Proposed=fix-3-9 | Decision=REJECT

HITL_DECISION_78: Agent=Agent-4 | File=module_4_9.py
  Violation=violation-4-9 | Proposed=fix-4-9 | Decision=REJECT

HITL_DECISION_79: Agent=Agent-6 | File=module_6_8.py
  Violation=violation-6-8 | Proposed=fix-6-8 | Decision=APPROVE

HITL_DECISION_80: Agent=Agent-6 | File=module_6_9.py
  Violation=violation-6-9 | Proposed=fix-6-9 | Decision=REJECT

HITL_DECISION_1: Agent=Agent-7 | File=module_7_0.py
  Violation=violation-7-0 | Proposed=fix-7-0 | Decision=APPROVE

HITL_DECISION_2: Agent=Agent-0 | File=module_0_0.py
  Violation=violation-0-0 | Proposed=fix-0-0 | Decision=APPROVE

HITL_DECISION_3: Agent=Agent-1 | File=module_1_0.py
  Violation=violation-1-0 | Proposed=fix-1-0 | Decision=APPROVE

HITL_DECISION_4: Agent=Agent-2 | File=module_2_0.py
  Violation=violation-2-0 | Proposed=fix-2-0 | Decision=APPROVE

HITL_DECISION_5: Agent=Agent-5 | File=module_5_0.py
  Violation=violation-5-0 | Proposed=fix-5-0 | Decision=APPROVE

HITL_DECISION_6: Agent=Agent-6 | File=module_6_0.py
  Violation=violation-6-0 | Proposed=fix-6-0 | Decision=APPROVE

HITL_DECISION_7: Agent=Agent-4 | File=module_4_0.py
  Violation=violation-4-0 | Proposed=fix-4-0 | Decision=APPROVE

HITL_DECISION_8: Agent=Agent-3 | File=module_3_0.py
  Violation=violation-3-0 | Proposed=fix-3-0 | Decision=APPROVE

HITL_DECISION_9: Agent=Agent-7 | File=module_7_1.py
  Violation=violation-7-1 | Proposed=fix-7-1 | Decision=REJECT

HITL_DECISION_10: Agent=Agent-0 | File=module_0_1.py
  Violation=violation-0-1 | Proposed=fix-0-1 | Decision=REJECT

HITL_DECISION_11: Agent=Agent-1 | File=module_1_1.py
  Violation=violation-1-1 | Proposed=fix-1-1 | Decision=REJECT

HITL_DECISION_12: Agent=Agent-2 | File=module_2_1.py
  Violation=violation-2-1 | Proposed=fix-2-1 | Decision=REJECT

HITL_DECISION_13: Agent=Agent-5 | File=module_5_1.py
  Violation=violation-5-1 | Proposed=fix-5-1 | Decision=REJECT

HITL_DECISION_14: Agent=Agent-6 | File=module_6_1.py
  Violation=violation-6-1 | Proposed=fix-6-1 | Decision=REJECT

HITL_DECISION_15: Agent=Agent-4 | File=module_4_1.py
  Violation=violation-4-1 | Proposed=fix-4-1 | Decision=REJECT

HITL_DECISION_16: Agent=Agent-3 | File=module_3_1.py
  Violation=violation-3-1 | Proposed=fix-3-1 | Decision=REJECT

HITL_DECISION_17: Agent=Agent-7 | File=module_7_2.py
  Violation=violation-7-2 | Proposed=fix-7-2 | Decision=APPROVE

HITL_DECISION_18: Agent=Agent-0 | File=module_0_2.py
  Violation=violation-0-2 | Proposed=fix-0-2 | Decision=APPROVE

HITL_DECISION_19: Agent=Agent-1 | File=module_1_2.py
  Violation=violation-1-2 | Proposed=fix-1-2 | Decision=APPROVE

HITL_DECISION_20: Agent=Agent-2 | File=module_2_2.py
  Violation=violation-2-2 | Proposed=fix-2-2 | Decision=APPROVE

HITL_DECISION_21: Agent=Agent-5 | File=module_5_2.py
  Violation=violation-5-2 | Proposed=fix-5-2 | Decision=APPROVE

HITL_DECISION_22: Agent=Agent-6 | File=module_6_2.py
  Violation=violation-6-2 | Proposed=fix-6-2 | Decision=APPROVE

HITL_DECISION_23: Agent=Agent-4 | File=module_4_2.py
  Violation=violation-4-2 | Proposed=fix-4-2 | Decision=APPROVE

HITL_DECISION_24: Agent=Agent-3 | File=module_3_2.py
  Violation=violation-3-2 | Proposed=fix-3-2 | Decision=APPROVE

HITL_DECISION_25: Agent=Agent-7 | File=module_7_3.py
  Violation=violation-7-3 | Proposed=fix-7-3 | Decision=REJECT

HITL_DECISION_26: Agent=Agent-0 | File=module_0_3.py
  Violation=violation-0-3 | Proposed=fix-0-3 | Decision=REJECT

HITL_DECISION_27: Agent=Agent-1 | File=module_1_3.py
  Violation=violation-1-3 | Proposed=fix-1-3 | Decision=REJECT

HITL_DECISION_28: Agent=Agent-2 | File=module_2_3.py
  Violation=violation-2-3 | Proposed=fix-2-3 | Decision=REJECT

HITL_DECISION_29: Agent=Agent-5 | File=module_5_3.py
  Violation=violation-5-3 | Proposed=fix-5-3 | Decision=REJECT

HITL_DECISION_30: Agent=Agent-6 | File=module_6_3.py
  Violation=violation-6-3 | Proposed=fix-6-3 | Decision=REJECT

HITL_DECISION_31: Agent=Agent-4 | File=module_4_3.py
  Violation=violation-4-3 | Proposed=fix-4-3 | Decision=REJECT

HITL_DECISION_32: Agent=Agent-3 | File=module_3_3.py
  Violation=violation-3-3 | Proposed=fix-3-3 | Decision=REJECT

HITL_DECISION_33: Agent=Agent-7 | File=module_7_4.py
  Violation=violation-7-4 | Proposed=fix-7-4 | Decision=APPROVE

HITL_DECISION_34: Agent=Agent-0 | File=module_0_4.py
  Violation=violation-0-4 | Proposed=fix-0-4 | Decision=APPROVE

HITL_DECISION_35: Agent=Agent-1 | File=module_1_4.py
  Violation=violation-1-4 | Proposed=fix-1-4 | Decision=APPROVE

HITL_DECISION_36: Agent=Agent-2 | File=module_2_4.py
  Violation=violation-2-4 | Proposed=fix-2-4 | Decision=APPROVE

HITL_DECISION_37: Agent=Agent-5 | File=module_5_4.py
  Violation=violation-5-4 | Proposed=fix-5-4 | Decision=APPROVE

HITL_DECISION_38: Agent=Agent-6 | File=module_6_4.py
  Violation=violation-6-4 | Proposed=fix-6-4 | Decision=APPROVE

HITL_DECISION_39: Agent=Agent-4 | File=module_4_4.py
  Violation=violation-4-4 | Proposed=fix-4-4 | Decision=APPROVE

HITL_DECISION_40: Agent=Agent-3 | File=module_3_4.py
  Violation=violation-3-4 | Proposed=fix-3-4 | Decision=APPROVE

HITL_DECISION_41: Agent=Agent-7 | File=module_7_5.py
  Violation=violation-7-5 | Proposed=fix-7-5 | Decision=REJECT

HITL_DECISION_42: Agent=Agent-0 | File=module_0_5.py
  Violation=violation-0-5 | Proposed=fix-0-5 | Decision=REJECT

HITL_DECISION_43: Agent=Agent-1 | File=module_1_5.py
  Violation=violation-1-5 | Proposed=fix-1-5 | Decision=REJECT

HITL_DECISION_44: Agent=Agent-2 | File=module_2_5.py
  Violation=violation-2-5 | Proposed=fix-2-5 | Decision=REJECT

HITL_DECISION_45: Agent=Agent-5 | File=module_5_5.py
  Violation=violation-5-5 | Proposed=fix-5-5 | Decision=REJECT

HITL_DECISION_46: Agent=Agent-6 | File=module_6_5.py
  Violation=violation-6-5 | Proposed=fix-6-5 | Decision=REJECT

HITL_DECISION_47: Agent=Agent-4 | File=module_4_5.py
  Violation=violation-4-5 | Proposed=fix-4-5 | Decision=REJECT

HITL_DECISION_48: Agent=Agent-3 | File=module_3_5.py
  Violation=violation-3-5 | Proposed=fix-3-5 | Decision=REJECT

HITL_DECISION_49: Agent=Agent-7 | File=module_7_6.py
  Violation=violation-7-6 | Proposed=fix-7-6 | Decision=APPROVE

HITL_DECISION_50: Agent=Agent-0 | File=module_0_6.py
  Violation=violation-0-6 | Proposed=fix-0-6 | Decision=APPROVE

HITL_DECISION_51: Agent=Agent-1 | File=module_1_6.py
  Violation=violation-1-6 | Proposed=fix-1-6 | Decision=APPROVE

HITL_DECISION_52: Agent=Agent-2 | File=module_2_6.py
  Violation=violation-2-6 | Proposed=fix-2-6 | Decision=APPROVE

HITL_DECISION_53: Agent=Agent-5 | File=module_5_6.py
  Violation=violation-5-6 | Proposed=fix-5-6 | Decision=APPROVE

HITL_DECISION_54: Agent=Agent-6 | File=module_6_6.py
  Violation=violation-6-6 | Proposed=fix-6-6 | Decision=APPROVE

HITL_DECISION_55: Agent=Agent-4 | File=module_4_6.py
  Violation=violation-4-6 | Proposed=fix-4-6 | Decision=APPROVE

HITL_DECISION_56: Agent=Agent-3 | File=module_3_6.py
  Violation=violation-3-6 | Proposed=fix-3-6 | Decision=APPROVE

HITL_DECISION_57: Agent=Agent-7 | File=module_7_7.py
  Violation=violation-7-7 | Proposed=fix-7-7 | Decision=REJECT

HITL_DECISION_58: Agent=Agent-0 | File=module_0_7.py
  Violation=violation-0-7 | Proposed=fix-0-7 | Decision=REJECT

HITL_DECISION_59: Agent=Agent-1 | File=module_1_7.py
  Violation=violation-1-7 | Proposed=fix-1-7 | Decision=REJECT

HITL_DECISION_60: Agent=Agent-2 | File=module_2_7.py
  Violation=violation-2-7 | Proposed=fix-2-7 | Decision=REJECT

HITL_DECISION_61: Agent=Agent-5 | File=module_5_7.py
  Violation=violation-5-7 | Proposed=fix-5-7 | Decision=REJECT

HITL_DECISION_62: Agent=Agent-6 | File=module_6_7.py
  Violation=violation-6-7 | Proposed=fix-6-7 | Decision=REJECT

HITL_DECISION_63: Agent=Agent-4 | File=module_4_7.py
  Violation=violation-4-7 | Proposed=fix-4-7 | Decision=REJECT

HITL_DECISION_64: Agent=Agent-3 | File=module_3_7.py
  Violation=violation-3-7 | Proposed=fix-3-7 | Decision=REJECT

HITL_DECISION_65: Agent=Agent-7 | File=module_7_8.py
  Violation=violation-7-8 | Proposed=fix-7-8 | Decision=APPROVE

HITL_DECISION_66: Agent=Agent-0 | File=module_0_8.py
  Violation=violation-0-8 | Proposed=fix-0-8 | Decision=APPROVE

HITL_DECISION_67: Agent=Agent-1 | File=module_1_8.py
  Violation=violation-1-8 | Proposed=fix-1-8 | Decision=APPROVE

HITL_DECISION_68: Agent=Agent-2 | File=module_2_8.py
  Violation=violation-2-8 | Proposed=fix-2-8 | Decision=APPROVE

HITL_DECISION_69: Agent=Agent-5 | File=module_5_8.py
  Violation=violation-5-8 | Proposed=fix-5-8 | Decision=APPROVE

HITL_DECISION_70: Agent=Agent-6 | File=module_6_8.py
  Violation=violation-6-8 | Proposed=fix-6-8 | Decision=APPROVE

HITL_DECISION_71: Agent=Agent-4 | File=module_4_8.py
  Violation=violation-4-8 | Proposed=fix-4-8 | Decision=APPROVE

HITL_DECISION_72: Agent=Agent-3 | File=module_3_8.py
  Violation=violation-3-8 | Proposed=fix-3-8 | Decision=APPROVE

HITL_DECISION_73: Agent=Agent-7 | File=module_7_9.py
  Violation=violation-7-9 | Proposed=fix-7-9 | Decision=REJECT

HITL_DECISION_74: Agent=Agent-0 | File=module_0_9.py
  Violation=violation-0-9 | Proposed=fix-0-9 | Decision=REJECT

HITL_DECISION_75: Agent=Agent-1 | File=module_1_9.py
  Violation=violation-1-9 | Proposed=fix-1-9 | Decision=REJECT

HITL_DECISION_76: Agent=Agent-2 | File=module_2_9.py
  Violation=violation-2-9 | Proposed=fix-2-9 | Decision=REJECT

HITL_DECISION_77: Agent=Agent-5 | File=module_5_9.py
  Violation=violation-5-9 | Proposed=fix-5-9 | Decision=REJECT

HITL_DECISION_78: Agent=Agent-6 | File=module_6_9.py
  Violation=violation-6-9 | Proposed=fix-6-9 | Decision=REJECT

HITL_DECISION_79: Agent=Agent-4 | File=module_4_9.py
  Violation=violation-4-9 | Proposed=fix-4-9 | Decision=REJECT

HITL_DECISION_80: Agent=Agent-3 | File=module_3_9.py
  Violation=violation-3-9 | Proposed=fix-3-9 | Decision=REJECT

HITL_DECISION_1: Agent=Agent-7 | File=module_7_0.py
  Violation=violation-7-0 | Proposed=fix-7-0 | Decision=APPROVE

HITL_DECISION_2: Agent=Agent-0 | File=module_0_0.py
  Violation=violation-0-0 | Proposed=fix-0-0 | Decision=APPROVE

HITL_DECISION_3: Agent=Agent-1 | File=module_1_0.py
  Violation=violation-1-0 | Proposed=fix-1-0 | Decision=APPROVE

HITL_DECISION_4: Agent=Agent-5 | File=module_5_0.py
  Violation=violation-5-0 | Proposed=fix-5-0 | Decision=APPROVE

HITL_DECISION_5: Agent=Agent-6 | File=module_6_0.py
  Violation=violation-6-0 | Proposed=fix-6-0 | Decision=APPROVE

HITL_DECISION_6: Agent=Agent-4 | File=module_4_0.py
  Violation=violation-4-0 | Proposed=fix-4-0 | Decision=APPROVE

HITL_DECISION_7: Agent=Agent-3 | File=module_3_0.py
  Violation=violation-3-0 | Proposed=fix-3-0 | Decision=APPROVE

HITL_DECISION_8: Agent=Agent-2 | File=module_2_0.py
  Violation=violation-2-0 | Proposed=fix-2-0 | Decision=APPROVE

HITL_DECISION_9: Agent=Agent-7 | File=module_7_1.py
  Violation=violation-7-1 | Proposed=fix-7-1 | Decision=REJECT

HITL_DECISION_10: Agent=Agent-0 | File=module_0_1.py
  Violation=violation-0-1 | Proposed=fix-0-1 | Decision=REJECT

HITL_DECISION_11: Agent=Agent-1 | File=module_1_1.py
  Violation=violation-1-1 | Proposed=fix-1-1 | Decision=REJECT

HITL_DECISION_12: Agent=Agent-5 | File=module_5_1.py
  Violation=violation-5-1 | Proposed=fix-5-1 | Decision=REJECT

HITL_DECISION_13: Agent=Agent-6 | File=module_6_1.py
  Violation=violation-6-1 | Proposed=fix-6-1 | Decision=REJECT

HITL_DECISION_14: Agent=Agent-4 | File=module_4_1.py
  Violation=violation-4-1 | Proposed=fix-4-1 | Decision=REJECT

HITL_DECISION_15: Agent=Agent-3 | File=module_3_1.py
  Violation=violation-3-1 | Proposed=fix-3-1 | Decision=REJECT

HITL_DECISION_16: Agent=Agent-2 | File=module_2_1.py
  Violation=violation-2-1 | Proposed=fix-2-1 | Decision=REJECT

HITL_DECISION_17: Agent=Agent-7 | File=module_7_2.py
  Violation=violation-7-2 | Proposed=fix-7-2 | Decision=APPROVE

HITL_DECISION_18: Agent=Agent-0 | File=module_0_2.py
  Violation=violation-0-2 | Proposed=fix-0-2 | Decision=APPROVE

HITL_DECISION_19: Agent=Agent-1 | File=module_1_2.py
  Violation=violation-1-2 | Proposed=fix-1-2 | Decision=APPROVE

HITL_DECISION_20: Agent=Agent-5 | File=module_5_2.py
  Violation=violation-5-2 | Proposed=fix-5-2 | Decision=APPROVE

HITL_DECISION_21: Agent=Agent-6 | File=module_6_2.py
  Violation=violation-6-2 | Proposed=fix-6-2 | Decision=APPROVE

HITL_DECISION_22: Agent=Agent-4 | File=module_4_2.py
  Violation=violation-4-2 | Proposed=fix-4-2 | Decision=APPROVE

HITL_DECISION_23: Agent=Agent-3 | File=module_3_2.py
  Violation=violation-3-2 | Proposed=fix-3-2 | Decision=APPROVE

HITL_DECISION_24: Agent=Agent-2 | File=module_2_2.py
  Violation=violation-2-2 | Proposed=fix-2-2 | Decision=APPROVE

HITL_DECISION_25: Agent=Agent-7 | File=module_7_3.py
  Violation=violation-7-3 | Proposed=fix-7-3 | Decision=REJECT

HITL_DECISION_26: Agent=Agent-0 | File=module_0_3.py
  Violation=violation-0-3 | Proposed=fix-0-3 | Decision=REJECT

HITL_DECISION_27: Agent=Agent-1 | File=module_1_3.py
  Violation=violation-1-3 | Proposed=fix-1-3 | Decision=REJECT

HITL_DECISION_28: Agent=Agent-5 | File=module_5_3.py
  Violation=violation-5-3 | Proposed=fix-5-3 | Decision=REJECT

HITL_DECISION_29: Agent=Agent-6 | File=module_6_3.py
  Violation=violation-6-3 | Proposed=fix-6-3 | Decision=REJECT

HITL_DECISION_30: Agent=Agent-4 | File=module_4_3.py
  Violation=violation-4-3 | Proposed=fix-4-3 | Decision=REJECT

HITL_DECISION_31: Agent=Agent-3 | File=module_3_3.py
  Violation=violation-3-3 | Proposed=fix-3-3 | Decision=REJECT

HITL_DECISION_32: Agent=Agent-2 | File=module_2_3.py
  Violation=violation-2-3 | Proposed=fix-2-3 | Decision=REJECT

HITL_DECISION_33: Agent=Agent-7 | File=module_7_4.py
  Violation=violation-7-4 | Proposed=fix-7-4 | Decision=APPROVE

HITL_DECISION_34: Agent=Agent-0 | File=module_0_4.py
  Violation=violation-0-4 | Proposed=fix-0-4 | Decision=APPROVE

HITL_DECISION_35: Agent=Agent-1 | File=module_1_4.py
  Violation=violation-1-4 | Proposed=fix-1-4 | Decision=APPROVE

HITL_DECISION_36: Agent=Agent-5 | File=module_5_4.py
  Violation=violation-5-4 | Proposed=fix-5-4 | Decision=APPROVE

HITL_DECISION_37: Agent=Agent-6 | File=module_6_4.py
  Violation=violation-6-4 | Proposed=fix-6-4 | Decision=APPROVE

HITL_DECISION_38: Agent=Agent-4 | File=module_4_4.py
  Violation=violation-4-4 | Proposed=fix-4-4 | Decision=APPROVE

HITL_DECISION_39: Agent=Agent-3 | File=module_3_4.py
  Violation=violation-3-4 | Proposed=fix-3-4 | Decision=APPROVE

HITL_DECISION_40: Agent=Agent-2 | File=module_2_4.py
  Violation=violation-2-4 | Proposed=fix-2-4 | Decision=APPROVE

HITL_DECISION_41: Agent=Agent-7 | File=module_7_5.py
  Violation=violation-7-5 | Proposed=fix-7-5 | Decision=REJECT

HITL_DECISION_42: Agent=Agent-0 | File=module_0_5.py
  Violation=violation-0-5 | Proposed=fix-0-5 | Decision=REJECT

HITL_DECISION_43: Agent=Agent-1 | File=module_1_5.py
  Violation=violation-1-5 | Proposed=fix-1-5 | Decision=REJECT

HITL_DECISION_44: Agent=Agent-5 | File=module_5_5.py
  Violation=violation-5-5 | Proposed=fix-5-5 | Decision=REJECT

HITL_DECISION_45: Agent=Agent-6 | File=module_6_5.py
  Violation=violation-6-5 | Proposed=fix-6-5 | Decision=REJECT

HITL_DECISION_46: Agent=Agent-4 | File=module_4_5.py
  Violation=violation-4-5 | Proposed=fix-4-5 | Decision=REJECT

HITL_DECISION_47: Agent=Agent-3 | File=module_3_5.py
  Violation=violation-3-5 | Proposed=fix-3-5 | Decision=REJECT

HITL_DECISION_48: Agent=Agent-2 | File=module_2_5.py
  Violation=violation-2-5 | Proposed=fix-2-5 | Decision=REJECT

HITL_DECISION_49: Agent=Agent-7 | File=module_7_6.py
  Violation=violation-7-6 | Proposed=fix-7-6 | Decision=APPROVE

HITL_DECISION_50: Agent=Agent-0 | File=module_0_6.py
  Violation=violation-0-6 | Proposed=fix-0-6 | Decision=APPROVE

HITL_DECISION_51: Agent=Agent-1 | File=module_1_6.py
  Violation=violation-1-6 | Proposed=fix-1-6 | Decision=APPROVE

HITL_DECISION_52: Agent=Agent-5 | File=module_5_6.py
  Violation=violation-5-6 | Proposed=fix-5-6 | Decision=APPROVE

HITL_DECISION_53: Agent=Agent-6 | File=module_6_6.py
  Violation=violation-6-6 | Proposed=fix-6-6 | Decision=APPROVE

HITL_DECISION_54: Agent=Agent-4 | File=module_4_6.py
  Violation=violation-4-6 | Proposed=fix-4-6 | Decision=APPROVE

HITL_DECISION_55: Agent=Agent-3 | File=module_3_6.py
  Violation=violation-3-6 | Proposed=fix-3-6 | Decision=APPROVE

HITL_DECISION_56: Agent=Agent-2 | File=module_2_6.py
  Violation=violation-2-6 | Proposed=fix-2-6 | Decision=APPROVE

HITL_DECISION_57: Agent=Agent-7 | File=module_7_7.py
  Violation=violation-7-7 | Proposed=fix-7-7 | Decision=REJECT

HITL_DECISION_58: Agent=Agent-0 | File=module_0_7.py
  Violation=violation-0-7 | Proposed=fix-0-7 | Decision=REJECT

HITL_DECISION_59: Agent=Agent-1 | File=module_1_7.py
  Violation=violation-1-7 | Proposed=fix-1-7 | Decision=REJECT

HITL_DECISION_60: Agent=Agent-5 | File=module_5_7.py
  Violation=violation-5-7 | Proposed=fix-5-7 | Decision=REJECT

HITL_DECISION_61: Agent=Agent-6 | File=module_6_7.py
  Violation=violation-6-7 | Proposed=fix-6-7 | Decision=REJECT

HITL_DECISION_62: Agent=Agent-4 | File=module_4_7.py
  Violation=violation-4-7 | Proposed=fix-4-7 | Decision=REJECT

HITL_DECISION_63: Agent=Agent-3 | File=module_3_7.py
  Violation=violation-3-7 | Proposed=fix-3-7 | Decision=REJECT

HITL_DECISION_64: Agent=Agent-2 | File=module_2_7.py
  Violation=violation-2-7 | Proposed=fix-2-7 | Decision=REJECT

HITL_DECISION_65: Agent=Agent-7 | File=module_7_8.py
  Violation=violation-7-8 | Proposed=fix-7-8 | Decision=APPROVE

HITL_DECISION_66: Agent=Agent-0 | File=module_0_8.py
  Violation=violation-0-8 | Proposed=fix-0-8 | Decision=APPROVE

HITL_DECISION_67: Agent=Agent-1 | File=module_1_8.py
  Violation=violation-1-8 | Proposed=fix-1-8 | Decision=APPROVE

HITL_DECISION_68: Agent=Agent-5 | File=module_5_8.py
  Violation=violation-5-8 | Proposed=fix-5-8 | Decision=APPROVE

HITL_DECISION_69: Agent=Agent-6 | File=module_6_8.py
  Violation=violation-6-8 | Proposed=fix-6-8 | Decision=APPROVE

HITL_DECISION_70: Agent=Agent-4 | File=module_4_8.py
  Violation=violation-4-8 | Proposed=fix-4-8 | Decision=APPROVE

HITL_DECISION_71: Agent=Agent-3 | File=module_3_8.py
  Violation=violation-3-8 | Proposed=fix-3-8 | Decision=APPROVE

HITL_DECISION_72: Agent=Agent-2 | File=module_2_8.py
  Violation=violation-2-8 | Proposed=fix-2-8 | Decision=APPROVE

HITL_DECISION_73: Agent=Agent-7 | File=module_7_9.py
  Violation=violation-7-9 | Proposed=fix-7-9 | Decision=REJECT

HITL_DECISION_74: Agent=Agent-0 | File=module_0_9.py
  Violation=violation-0-9 | Proposed=fix-0-9 | Decision=REJECT

HITL_DECISION_75: Agent=Agent-1 | File=module_1_9.py
  Violation=violation-1-9 | Proposed=fix-1-9 | Decision=REJECT

HITL_DECISION_76: Agent=Agent-5 | File=module_5_9.py
  Violation=violation-5-9 | Proposed=fix-5-9 | Decision=REJECT

HITL_DECISION_77: Agent=Agent-6 | File=module_6_9.py
  Violation=violation-6-9 | Proposed=fix-6-9 | Decision=REJECT

HITL_DECISION_78: Agent=Agent-4 | File=module_4_9.py
  Violation=violation-4-9 | Proposed=fix-4-9 | Decision=REJECT

HITL_DECISION_79: Agent=Agent-3 | File=module_3_9.py
  Violation=violation-3-9 | Proposed=fix-3-9 | Decision=REJECT

HITL_DECISION_80: Agent=Agent-2 | File=module_2_9.py
  Violation=violation-2-9 | Proposed=fix-2-9 | Decision=REJECT

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=L2_SANDBOX | Decision=corrected_to=L5_COMPLIANCE
  decision_type=routing_correction
  wrong_target=L2_SANDBOX
  correct_target=L5_COMPLIANCE
  confidence=0.45
  reason=policy_mismatch

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=L2_SANDBOX | Decision=corrected_to=L5_COMPLIANCE
  decision_type=routing_correction
  wrong_target=L2_SANDBOX
  correct_target=L5_COMPLIANCE
  confidence=0.45
  reason=policy_mismatch

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=L2_SANDBOX | Decision=corrected_to=L5_COMPLIANCE
  decision_type=routing_correction
  wrong_target=L2_SANDBOX
  correct_target=L5_COMPLIANCE
  confidence=0.45
  reason=policy_mismatch

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=L2_SANDBOX | Decision=corrected_to=L5_COMPLIANCE
  decision_type=routing_correction
  wrong_target=L2_SANDBOX
  correct_target=L5_COMPLIANCE
  confidence=0.45
  reason=policy_mismatch

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=L2_SANDBOX | Decision=corrected_to=L5_COMPLIANCE
  decision_type=routing_correction
  wrong_target=L2_SANDBOX
  correct_target=L5_COMPLIANCE
  confidence=0.45
  reason=policy_mismatch

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=L2_SANDBOX | Decision=corrected_to=L5_COMPLIANCE
  decision_type=routing_correction
  wrong_target=L2_SANDBOX
  correct_target=L5_COMPLIANCE
  confidence=0.45
  reason=policy_mismatch

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=L2_SANDBOX | Decision=corrected_to=L5_COMPLIANCE
  decision_type=routing_correction
  wrong_target=L2_SANDBOX
  correct_target=L5_COMPLIANCE
  confidence=0.45
  reason=policy_mismatch

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=L2_SANDBOX | Decision=corrected_to=L5_COMPLIANCE
  decision_type=routing_correction
  wrong_target=L2_SANDBOX
  correct_target=L5_COMPLIANCE
  confidence=0.45
  reason=policy_mismatch

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=L2_SANDBOX | Decision=corrected_to=L5_COMPLIANCE
  decision_type=routing_correction
  wrong_target=L2_SANDBOX
  correct_target=L5_COMPLIANCE
  confidence=0.45
  reason=policy_mismatch

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=L2_SANDBOX | Decision=corrected_to=L5_COMPLIANCE
  decision_type=routing_correction
  wrong_target=L2_SANDBOX
  correct_target=L5_COMPLIANCE
  confidence=0.45
  reason=policy_mismatch

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=L2_SANDBOX | Decision=corrected_to=L5_COMPLIANCE
  decision_type=routing_correction
  wrong_target=L2_SANDBOX
  correct_target=L5_COMPLIANCE
  confidence=0.45
  reason=policy_mismatch

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=L2_SANDBOX | Decision=corrected_to=L5_COMPLIANCE
  decision_type=routing_correction
  wrong_target=L2_SANDBOX
  correct_target=L5_COMPLIANCE
  confidence=0.45
  reason=policy_mismatch

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=L2_SANDBOX | Decision=corrected_to=L5_COMPLIANCE
  decision_type=routing_correction
  wrong_target=L2_SANDBOX
  correct_target=L5_COMPLIANCE
  confidence=0.45
  reason=policy_mismatch

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=L2_SANDBOX | Decision=corrected_to=L5_COMPLIANCE
  decision_type=routing_correction
  wrong_target=L2_SANDBOX
  correct_target=L5_COMPLIANCE
  confidence=0.45
  reason=policy_mismatch

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=L2_SANDBOX | Decision=corrected_to=L5_COMPLIANCE
  decision_type=routing_correction
  wrong_target=L2_SANDBOX
  correct_target=L5_COMPLIANCE
  confidence=0.45
  reason=policy_mismatch

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=L2_SANDBOX | Decision=corrected_to=L5_COMPLIANCE
  decision_type=routing_correction
  wrong_target=L2_SANDBOX
  correct_target=L5_COMPLIANCE
  confidence=0.45
  reason=policy_mismatch

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=L2_SANDBOX | Decision=corrected_to=L5_COMPLIANCE
  decision_type=routing_correction
  wrong_target=L2_SANDBOX
  correct_target=L5_COMPLIANCE
  confidence=0.45
  reason=policy_mismatch

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=L2_SANDBOX | Decision=corrected_to=L5_COMPLIANCE
  decision_type=routing_correction
  wrong_target=L2_SANDBOX
  correct_target=L5_COMPLIANCE
  confidence=0.45
  reason=policy_mismatch

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=L2_SANDBOX | Decision=corrected_to=L5_COMPLIANCE
  decision_type=routing_correction
  wrong_target=L2_SANDBOX
  correct_target=L5_COMPLIANCE
  confidence=0.45
  reason=policy_mismatch

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=L2_SANDBOX | Decision=corrected_to=L5_COMPLIANCE
  decision_type=routing_correction
  wrong_target=L2_SANDBOX
  correct_target=L5_COMPLIANCE
  confidence=0.45
  reason=policy_mismatch

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=L2_SANDBOX | Decision=corrected_to=L5_COMPLIANCE
  decision_type=routing_correction
  wrong_target=L2_SANDBOX
  correct_target=L5_COMPLIANCE
  confidence=0.45
  reason=policy_mismatch

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=L2_SANDBOX | Decision=corrected_to=L5_COMPLIANCE
  decision_type=routing_correction
  wrong_target=L2_SANDBOX
  correct_target=L5_COMPLIANCE
  confidence=0.45
  reason=policy_mismatch

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=L2_SANDBOX | Decision=corrected_to=L5_COMPLIANCE
  decision_type=routing_correction
  wrong_target=L2_SANDBOX
  correct_target=L5_COMPLIANCE
  confidence=0.45
  reason=policy_mismatch

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=L2_SANDBOX | Decision=corrected_to=L5_COMPLIANCE
  decision_type=routing_correction
  wrong_target=L2_SANDBOX
  correct_target=L5_COMPLIANCE
  confidence=0.45
  reason=policy_mismatch

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=L2_SANDBOX | Decision=corrected_to=L5_COMPLIANCE
  decision_type=routing_correction
  wrong_target=L2_SANDBOX
  correct_target=L5_COMPLIANCE
  confidence=0.45
  reason=policy_mismatch

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=L2_SANDBOX | Decision=corrected_to=L5_COMPLIANCE
  decision_type=routing_correction
  wrong_target=L2_SANDBOX
  correct_target=L5_COMPLIANCE
  confidence=0.45
  reason=policy_mismatch

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=L2_SANDBOX | Decision=corrected_to=L5_COMPLIANCE
  decision_type=routing_correction
  wrong_target=L2_SANDBOX
  correct_target=L5_COMPLIANCE
  confidence=0.45
  reason=policy_mismatch

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=L2_SANDBOX | Decision=corrected_to=L5_COMPLIANCE
  decision_type=routing_correction
  wrong_target=L2_SANDBOX
  correct_target=L5_COMPLIANCE
  confidence=0.45
  reason=policy_mismatch

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=L2_SANDBOX | Decision=corrected_to=L5_COMPLIANCE
  decision_type=routing_correction
  wrong_target=L2_SANDBOX
  correct_target=L5_COMPLIANCE
  confidence=0.45
  reason=policy_mismatch

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=L2_SANDBOX | Decision=corrected_to=L5_COMPLIANCE
  decision_type=routing_correction
  wrong_target=L2_SANDBOX
  correct_target=L5_COMPLIANCE
  confidence=0.45
  reason=policy_mismatch

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=L2_SANDBOX | Decision=corrected_to=L5_COMPLIANCE
  decision_type=routing_correction
  wrong_target=L2_SANDBOX
  correct_target=L5_COMPLIANCE
  confidence=0.45
  reason=policy_mismatch

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=L2_SANDBOX | Decision=corrected_to=L5_COMPLIANCE
  decision_type=routing_correction
  wrong_target=L2_SANDBOX
  correct_target=L5_COMPLIANCE
  confidence=0.45
  reason=policy_mismatch

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=L2_SANDBOX | Decision=corrected_to=L5_COMPLIANCE
  decision_type=routing_correction
  wrong_target=L2_SANDBOX
  correct_target=L5_COMPLIANCE
  confidence=0.45
  reason=policy_mismatch

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=L2_SANDBOX | Decision=corrected_to=L5_COMPLIANCE
  decision_type=routing_correction
  wrong_target=L2_SANDBOX
  correct_target=L5_COMPLIANCE
  confidence=0.45
  reason=policy_mismatch

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=L2_SANDBOX | Decision=corrected_to=L5_COMPLIANCE
  decision_type=routing_correction
  wrong_target=L2_SANDBOX
  correct_target=L5_COMPLIANCE
  confidence=0.45
  reason=policy_mismatch

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=L2_SANDBOX | Decision=corrected_to=L5_COMPLIANCE
  decision_type=routing_correction
  wrong_target=L2_SANDBOX
  correct_target=L5_COMPLIANCE
  confidence=0.45
  reason=policy_mismatch

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=L2_SANDBOX | Decision=corrected_to=L5_COMPLIANCE
  decision_type=routing_correction
  wrong_target=L2_SANDBOX
  correct_target=L5_COMPLIANCE
  confidence=0.45
  reason=policy_mismatch

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=L2_SANDBOX | Decision=corrected_to=L5_COMPLIANCE
  decision_type=routing_correction
  wrong_target=L2_SANDBOX
  correct_target=L5_COMPLIANCE
  confidence=0.45
  reason=policy_mismatch

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=L2_SANDBOX | Decision=corrected_to=L5_COMPLIANCE
  decision_type=routing_correction
  wrong_target=L2_SANDBOX
  correct_target=L5_COMPLIANCE
  confidence=0.45
  reason=policy_mismatch

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=L2_SANDBOX | Decision=corrected_to=L5_COMPLIANCE
  decision_type=routing_correction
  wrong_target=L2_SANDBOX
  correct_target=L5_COMPLIANCE
  confidence=0.45
  reason=policy_mismatch

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=L2_SANDBOX | Decision=corrected_to=L5_COMPLIANCE
  decision_type=routing_correction
  wrong_target=L2_SANDBOX
  correct_target=L5_COMPLIANCE
  confidence=0.45
  reason=policy_mismatch

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=L2_SANDBOX | Decision=corrected_to=L5_COMPLIANCE
  decision_type=routing_correction
  wrong_target=L2_SANDBOX
  correct_target=L5_COMPLIANCE
  confidence=0.45
  reason=policy_mismatch

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=L2_SANDBOX | Decision=corrected_to=L5_COMPLIANCE
  decision_type=routing_correction
  wrong_target=L2_SANDBOX
  correct_target=L5_COMPLIANCE
  confidence=0.45
  reason=policy_mismatch

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=L2_SANDBOX | Decision=corrected_to=L5_COMPLIANCE
  decision_type=routing_correction
  wrong_target=L2_SANDBOX
  correct_target=L5_COMPLIANCE
  confidence=0.45
  reason=policy_mismatch

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=L2_SANDBOX | Decision=corrected_to=L5_COMPLIANCE
  decision_type=routing_correction
  wrong_target=L2_SANDBOX
  correct_target=L5_COMPLIANCE
  confidence=0.45
  reason=policy_mismatch

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=L2_SANDBOX | Decision=corrected_to=L5_COMPLIANCE
  decision_type=routing_correction
  wrong_target=L2_SANDBOX
  correct_target=L5_COMPLIANCE
  confidence=0.45
  reason=policy_mismatch

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=L2_SANDBOX | Decision=corrected_to=L5_COMPLIANCE
  decision_type=routing_correction
  wrong_target=L2_SANDBOX
  correct_target=L5_COMPLIANCE
  confidence=0.45
  reason=policy_mismatch

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=L2_SANDBOX | Decision=corrected_to=L5_COMPLIANCE
  decision_type=routing_correction
  wrong_target=L2_SANDBOX
  correct_target=L5_COMPLIANCE
  confidence=0.45
  reason=policy_mismatch

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=L2_SANDBOX | Decision=corrected_to=L5_COMPLIANCE
  decision_type=routing_correction
  wrong_target=L2_SANDBOX
  correct_target=L5_COMPLIANCE
  confidence=0.45
  reason=policy_mismatch

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=L2_SANDBOX | Decision=corrected_to=L5_COMPLIANCE
  decision_type=routing_correction
  wrong_target=L2_SANDBOX
  correct_target=L5_COMPLIANCE
  confidence=0.45
  reason=policy_mismatch

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=L2_SANDBOX | Decision=corrected_to=L5_COMPLIANCE
  decision_type=routing_correction
  wrong_target=L2_SANDBOX
  correct_target=L5_COMPLIANCE
  confidence=0.45
  reason=policy_mismatch

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=L2_SANDBOX | Decision=corrected_to=L5_COMPLIANCE
  decision_type=routing_correction
  wrong_target=L2_SANDBOX
  correct_target=L5_COMPLIANCE
  confidence=0.45
  reason=policy_mismatch

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=L2_SANDBOX | Decision=corrected_to=L5_COMPLIANCE
  decision_type=routing_correction
  wrong_target=L2_SANDBOX
  correct_target=L5_COMPLIANCE
  confidence=0.45
  reason=policy_mismatch

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=L2_SANDBOX | Decision=corrected_to=L5_COMPLIANCE
  decision_type=routing_correction
  wrong_target=L2_SANDBOX
  correct_target=L5_COMPLIANCE
  confidence=0.45
  reason=policy_mismatch

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=L2_SANDBOX | Decision=corrected_to=L5_COMPLIANCE
  decision_type=routing_correction
  wrong_target=L2_SANDBOX
  correct_target=L5_COMPLIANCE
  confidence=0.45
  reason=policy_mismatch

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=L2_SANDBOX | Decision=corrected_to=L5_COMPLIANCE
  decision_type=routing_correction
  wrong_target=L2_SANDBOX
  correct_target=L5_COMPLIANCE
  confidence=0.45
  reason=policy_mismatch

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=L2_SANDBOX | Decision=corrected_to=L5_COMPLIANCE
  decision_type=routing_correction
  wrong_target=L2_SANDBOX
  correct_target=L5_COMPLIANCE
  confidence=0.45
  reason=policy_mismatch

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=L2_SANDBOX | Decision=corrected_to=L5_COMPLIANCE
  decision_type=routing_correction
  wrong_target=L2_SANDBOX
  correct_target=L5_COMPLIANCE
  confidence=0.45
  reason=policy_mismatch

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=L2_SANDBOX | Decision=corrected_to=L5_COMPLIANCE
  decision_type=routing_correction
  wrong_target=L2_SANDBOX
  correct_target=L5_COMPLIANCE
  confidence=0.45
  reason=policy_mismatch

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=L2_SANDBOX | Decision=corrected_to=L5_COMPLIANCE
  decision_type=routing_correction
  wrong_target=L2_SANDBOX
  correct_target=L5_COMPLIANCE
  confidence=0.45
  reason=policy_mismatch

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=L2_SANDBOX | Decision=corrected_to=L5_COMPLIANCE
  decision_type=routing_correction
  wrong_target=L2_SANDBOX
  correct_target=L5_COMPLIANCE
  confidence=0.45
  reason=policy_mismatch

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=L2_SANDBOX | Decision=corrected_to=L5_COMPLIANCE
  decision_type=routing_correction
  wrong_target=L2_SANDBOX
  correct_target=L5_COMPLIANCE
  confidence=0.45
  reason=policy_mismatch

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=L2_SANDBOX | Decision=corrected_to=L5_COMPLIANCE
  decision_type=routing_correction
  wrong_target=L2_SANDBOX
  correct_target=L5_COMPLIANCE
  confidence=0.45
  reason=policy_mismatch

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=L2_SANDBOX | Decision=corrected_to=L5_COMPLIANCE
  decision_type=routing_correction
  wrong_target=L2_SANDBOX
  correct_target=L5_COMPLIANCE
  confidence=0.45
  reason=policy_mismatch

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=L2_SANDBOX | Decision=corrected_to=L5_COMPLIANCE
  decision_type=routing_correction
  wrong_target=L2_SANDBOX
  correct_target=L5_COMPLIANCE
  confidence=0.45
  reason=policy_mismatch

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=L2_SANDBOX | Decision=corrected_to=L5_COMPLIANCE
  decision_type=routing_correction
  wrong_target=L2_SANDBOX
  correct_target=L5_COMPLIANCE
  confidence=0.45
  reason=policy_mismatch

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=L2_SANDBOX | Decision=corrected_to=L5_COMPLIANCE
  decision_type=routing_correction
  wrong_target=L2_SANDBOX
  correct_target=L5_COMPLIANCE
  confidence=0.45
  reason=policy_mismatch

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=L2_SANDBOX | Decision=corrected_to=L5_COMPLIANCE
  decision_type=routing_correction
  wrong_target=L2_SANDBOX
  correct_target=L5_COMPLIANCE
  confidence=0.45
  reason=policy_mismatch

HITL_DECISION_1: Agent=AgenticRouter | File=agentic_core/L0_routing/engines/agentic_router.py
  Violation=ROUTING_MISCLASSIFICATION | Proposed=route_to=L2_SANDBOX | Decision=corrected_to=L5_COMPLIANCE
  decision_type=routing_correction
  wrong_target=L2_SANDBOX
  correct_target=L5_COMPLIANCE
  confidence=0.45
  reason=policy_mismatch
