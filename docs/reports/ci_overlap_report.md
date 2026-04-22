# CI-Overlap Report: Agents/Scripts Overlapping with CI Logic

- ADG snapshot: `adg_indexed_04212026_1548.sqlite`
- Backend: `degraded_sqlite` — ADG MCP unhealthy (`no such table: nodes` on stale service handle); queried canonical SQLite directly. `DEGRADED_FALLBACK: reason=adg_mcp_stale_service_handle`
- Note: current snapshot has **no materialized views (`mv_*`)** and **no P-views (`v_p*`)** — analysis used raw `nodes`/`edges` tables and `relation_type='imports'` fan-in/fan-out as the graph-layer primitive.
- CI modules surveyed: 92  (= `ops_scripts/ci/**`, `.github/workflows/**`, `.windsurf/scripts/**`, `ops_scripts/enforcement/**`)
- Agents surveyed: 516  (= `*Agent.py` + `apps_*/engines/**`)
- Scripts surveyed: 742  (= `tools/**`, `ops_scripts/**` excluding CI)

## Key Findings (executive summary)

1. **Zero direct import edges between agents/scripts and CI modules.** No agent/script imports a CI gate, and no CI gate imports an agent/script. CI logic is architecturally isolated from the runtime agent plane — a healthy sign.
2. **Most "overlap" is shared dependency surface** (weight-1 shared imports of common utilities: `path_resolver`, `progress_display`, `adg.core.*`, `models`, etc.). This is legitimate shared infrastructure, not functional duplication.
3. **Zero genuine duplication after content inspection.** 5 rows matched by filename collision, but content diff reveals all are distinct:

| Agent/Script | CI Counterpart | Material? | Notes |
|---|---|---|---|
| `ops_scripts/general/install_git_hooks.py` | `.windsurf/scripts/install_git_hooks.py` | **No** | Installs **pre-commit** hook (Pascal Sovereignty). Windsurf one installs **post-commit** hook (HITL outcome binder). Complementary, not duplicate. Consider renaming to `install_precommit_hook.py` / `install_postcommit_hook.py` for clarity. |
| `tools/graphdb/cli.py` | `ops_scripts/ci/adg_gates/cli.py` | No | Different subpackage; basename collision only. |
| `tools/graphdb/agent_integration/cli.py` | `ops_scripts/ci/adg_gates/cli.py` | No | Same. |
| `tools/adg/prompt_assembly/cli.py` | `ops_scripts/ci/adg_gates/cli.py` | No | Same. |
| `tools/adg/cache/__init__.py` | `ops_scripts/ci/adg_gates/__init__.py` | No | `__init__.py` collisions are package-scope noise. |

**Lesson:** filename-collision (`name_dup` weight 5) is a **false-positive-prone signal**. Strengthen next iteration by adding a content-hash or AST-signature check before flagging duplication.

4. **High-score agents are dependency-neighbors, not CI duplicates.** The top 20 agents (scores 11–20) all show `→CI=0, ←CI=0, name_dup=N`. Their high scores come from sharing 11–20 common imports with the CI surface (typical for any module that uses path/ADG/progress utilities). These are not overlap concerns.

## Scoring

- `shared_imports_with_ci` (weight 1): count of distinct modules the node imports that CI also imports
- `calls_into_ci` (weight 3): imports that land directly on a CI module (node invokes CI logic)
- `called_by_ci` (weight 3): CI modules that import this node (CI invokes the node)
- `file_name_overlap` (weight 5): same basename as any CI module (duplicate-name signal)
- Material threshold: score >= 2

## Agents with material CI overlap (454)

| Score | Layer | Agent | shared | →CI | ←CI | name_dup |
|------:|-------|-------|-------:|----:|----:|:--------:|
| 20 | L5 | `agentic_core/L5_safety/reasoning/LocationHealerAgent.py` | 20 | 0 | 0 |  |
| 19 | L5 | `agentic_core/L5_safety/reasoning/FileClassificationAgent.py` | 19 | 0 | 0 |  |
| 19 | L5 | `agentic_core/L5_safety/reasoning/PascalSovereigntyAgent.py` | 19 | 0 | 0 |  |
| 17 | L5 | `agentic_core/L5_safety/reasoning/CodeHealerAgent.py` | 17 | 0 | 0 |  |
| 16 | L2 | `agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py` | 16 | 0 | 0 |  |
| 16 | L3 | `agentic_core/L3_orchestration/reasoning/UnifiedAgent.py` | 16 | 0 | 0 |  |
| 16 | L5 | `agentic_core/L5_safety/reasoning/ArchitectureGovernorAgent.py` | 16 | 0 | 0 |  |
| 16 | L5 | `agentic_core/L5_safety/reasoning/GenerativeGuardAgent.py` | 16 | 0 | 0 |  |
| 16 | L5 | `agentic_core/L5_safety/reasoning/HygieneGuardianAgent.py` | 16 | 0 | 0 |  |
| 15 | L3 | `agentic_core/L3_orchestration/reasoning/engines/decomposition_orchestrator.py` | 15 | 0 | 0 |  |
| 15 | L5 | `agentic_core/L5_safety/reasoning/AutonomyGuardianAgent.py` | 15 | 0 | 0 |  |
| 15 | L5 | `agentic_core/L5_safety/reasoning/GovernanceAgent.py` | 15 | 0 | 0 |  |
| 15 | L5 | `agentic_core/L5_safety/reasoning/PreCommitSovereignAgent.py` | 15 | 0 | 0 |  |
| 15 | L5 | `agentic_core/L5_safety/reasoning/RedSentinelAgent.py` | 15 | 0 | 0 |  |
| 15 | L5 | `agentic_core/L5_safety/reasoning/SelfUpdatingSafetyEngineAgent.py` | 15 | 0 | 0 |  |
| 15 | L5 | `agentic_core/L5_safety/validators/HygieneGuardianAgent.py` | 15 | 0 | 0 |  |
| 15 | L_SL | `system_learning/engines/embedding_service_factory.py` | 15 | 0 | 0 |  |
| 15 | L_SL | `system_learning/engines/historical_backfill_engine.py` | 15 | 0 | 0 |  |
| 14 | L3 | `agentic_core/L3_orchestration/reasoning/engines/orchestrator_engine.py` | 14 | 0 | 0 |  |
| 14 | L5 | `agentic_core/L5_safety/reasoning/DDDAlignmentAgent.py` | 14 | 0 | 0 |  |
| 14 | L5 | `agentic_core/L5_safety/reasoning/GravityLeakRepairAgent.py` | 14 | 0 | 0 |  |
| 14 | L5 | `agentic_core/L5_safety/reasoning/SovereignActionPlaneAgent.py` | 14 | 0 | 0 |  |
| 14 | L5 | `agentic_core/L5_safety/reasoning/SystemArchitectAgent.py` | 14 | 0 | 0 |  |
| 14 | L_SL | `system_learning/engines/cross_repo_system_learning_import.py` | 14 | 0 | 0 |  |
| 13 | L1 | `agentic_core/L1_cognition/reasoning/MetaLearningAgent.py` | 13 | 0 | 0 |  |
| 13 | L5 | `agentic_core/L5_safety/reasoning/DuplicateCodeDetectorAgent.py` | 13 | 0 | 0 |  |
| 13 | L5 | `agentic_core/L5_safety/reasoning/GitHygieneAgent.py` | 13 | 0 | 0 |  |
| 13 | L5 | `agentic_core/L5_safety/reasoning/ReportLocationAgent.py` | 13 | 0 | 0 |  |
| 13 | L5 | `agentic_core/L5_safety/reasoning/SafetyDetectorAgent.py` | 13 | 0 | 0 |  |
| 13 | L5 | `agentic_core/L5_safety/reasoning/SprawlInspectorAgent.py` | 13 | 0 | 0 |  |
| 13 | L5 | `agentic_core/L5_safety/reasoning/StructuralValidatorAgent.py` | 13 | 0 | 0 |  |
| 13 | L5 | `agentic_core/L5_safety/reasoning/StructureEnforcerAgent.py` | 13 | 0 | 0 |  |
| 13 | L5 | `agentic_core/L5_safety/reasoning/StructureHealerAgent.py` | 13 | 0 | 0 |  |
| 13 | L5 | `agentic_core/L5_safety/reasoning/TestGeneratorAgent.py` | 13 | 0 | 0 |  |
| 13 | L_APP | `apps_lic/reasoning/OutreachSignalRouterAgent.py` | 13 | 0 | 0 |  |
| 13 | L_SL | `system_learning/engines/seed_pack_build_cli.py` | 13 | 0 | 0 |  |
| 12 | L1 | `agentic_core/L1_cognition/reasoning/ASTValidatorAgent.py` | 12 | 0 | 0 |  |
| 12 | L3 | `agentic_core/L3_orchestration/reasoning/DagEngineAgent.py` | 12 | 0 | 0 |  |
| 12 | L3 | `agentic_core/L3_orchestration/reasoning/engines/proactive_fission_scanner.py` | 12 | 0 | 0 |  |
| 12 | L5 | `agentic_core/L5_safety/reasoning/AutonomousThreatEvolutionAgent.py` | 12 | 0 | 0 |  |
| 12 | L5 | `agentic_core/L5_safety/reasoning/IntegrityGateExecutorAgent.py` | 12 | 0 | 0 |  |
| 12 | L5 | `agentic_core/L5_safety/reasoning/PredictiveCostAuditorAgent.py` | 12 | 0 | 0 |  |
| 12 | L5 | `agentic_core/L5_safety/reasoning/ResourceManagerAgent.py` | 12 | 0 | 0 |  |
| 12 | L5 | `agentic_core/L5_safety/reasoning/SafetyExecutorAgent.py` | 12 | 0 | 0 |  |
| 12 | L5 | `agentic_core/L5_safety/reasoning/SafetyInspectorAgent.py` | 12 | 0 | 0 |  |
| 12 | L5 | `agentic_core/L5_safety/reasoning/SecurityManagerAgent.py` | 12 | 0 | 0 |  |
| 12 | L5 | `agentic_core/L5_safety/reasoning/StructuralEngineerAgent.py` | 12 | 0 | 0 |  |
| 12 | L_APP | `apps_lic/reasoning/GovernanceShieldAgent.py` | 12 | 0 | 0 |  |
| 12 | L_APP | `apps_lic/reasoning/OutreachLearningAgent.py` | 12 | 0 | 0 |  |
| 12 | L_SL | `system_learning/engines/pattern_analysis_engine.py` | 12 | 0 | 0 |  |
| 12 | L_SL | `system_learning/engines/seed_embedding_pack_builder.py` | 12 | 0 | 0 |  |
| 11 | L2 | `agentic_core/L2_execution/reasoning/EmbeddingSovereignAgent.py` | 11 | 0 | 0 |  |
| 11 | L3 | `agentic_core/L3_orchestration/reasoning/FissionManagerAgent.py` | 11 | 0 | 0 |  |
| 11 | L3 | `agentic_core/L3_orchestration/reasoning/NervousSystemAgent.py` | 11 | 0 | 0 |  |
| 11 | L3 | `agentic_core/L3_orchestration/reasoning/engines/deterministic_orchestrator.py` | 11 | 0 | 0 |  |
| 11 | L3 | `agentic_core/L3_orchestration/reasoning/engines/graph_aware_indexer.py` | 11 | 0 | 0 |  |
| 11 | L3 | `agentic_core/L3_orchestration/reasoning/engines/prompt_chain_engine.py` | 11 | 0 | 0 |  |
| 11 | L3 | `agentic_core/L3_orchestration/reasoning/engines/sovereign_mcp_router.py` | 11 | 0 | 0 |  |
| 11 | L3 | `agentic_core/L3_orchestration/reasoning/engines/sovereign_redis_orchestrator.py` | 11 | 0 | 0 |  |
| 11 | L5 | `agentic_core/L5_safety/reasoning/CognitiveDispositionAgent.py` | 11 | 0 | 0 |  |
| 11 | L5 | `agentic_core/L5_safety/reasoning/RegressionOracleAgent.py` | 11 | 0 | 0 |  |
| 11 | L5 | `agentic_core/L5_safety/reasoning/TerritoryChangeHandlerAgent.py` | 11 | 0 | 0 |  |
| 11 | L6 | `agentic_core/L6_observability/utils/engines/semantic_clock_validator.py` | 11 | 0 | 0 |  |
| 11 | L_APP | `apps_exec/engines/brief_retrieval_engine.py` | 11 | 0 | 0 |  |
| 11 | L_APP | `apps_exec/engines/ingestion_engine.py` | 11 | 0 | 0 |  |
| 11 | L_APP | `apps_lic/engines/control_plane.py` | 11 | 0 | 0 |  |
| 11 | L_APP | `apps_research/engines/research_retrieval_engine.py` | 11 | 0 | 0 |  |
| 11 | L_APP | `apps_rg/reasoning/ContentQualityAgent.py` | 11 | 0 | 0 |  |
| 11 | L_APP | `apps_shared/reasoning/BaseDispatchAgent.py` | 11 | 0 | 0 |  |
| 11 | L_SL | `system_learning/engines/healing_config_optimizer.py` | 11 | 0 | 0 |  |
| 11 | L_SL | `system_learning/engines/l3_efficiency_tuner.py` | 11 | 0 | 0 |  |
| 11 | L_SL | `system_learning/engines/l4_state_writer.py` | 11 | 0 | 0 |  |
| 11 | L_SL | `system_learning/engines/shadow_drift_analyzer.py` | 11 | 0 | 0 |  |
| 11 | L_SL | `system_learning/engines/signal_grouping_engine.py` | 11 | 0 | 0 |  |
| 10 | L2 | `agentic_core/L2_execution/reasoning/RedisSovereignAgent.py` | 10 | 0 | 0 |  |
| 10 | L3 | `agentic_core/L3_orchestration/reasoning/SemanticGatekeeperAgent.py` | 10 | 0 | 0 |  |
| 10 | L3 | `agentic_core/L3_orchestration/reasoning/engines/autonomous_execution_engine.py` | 10 | 0 | 0 |  |
| 10 | L3 | `agentic_core/L3_orchestration/reasoning/engines/autonomous_workflow_engine.py` | 10 | 0 | 0 |  |
| 10 | L3 | `agentic_core/L3_orchestration/reasoning/engines/coordinator_capability_orchestrator.py` | 10 | 0 | 0 |  |
| 10 | L3 | `agentic_core/L3_orchestration/reasoning/engines/handshake_state_machine.py` | 10 | 0 | 0 |  |

## Scripts with material CI overlap (705)

| Score | Layer | Script | shared | →CI | ←CI | name_dup |
|------:|-------|--------|-------:|----:|----:|:--------:|
| 19 | L_OPS | `ops_scripts/dev_tools/L0_routing_scripts/full_agent_discovery.py` | 19 | 0 | 0 |  |
| 18 | L_OPS | `ops_scripts/dev_tools/L0_routing_scripts/forensic_discovery_prep.py` | 18 | 0 | 0 |  |
| 17 | L_OPS | `ops_scripts/dev_tools/L0_routing_scripts/_ssot_types.py` | 17 | 0 | 0 |  |
| 17 | L_OPS | `ops_scripts/dev_tools/l0_scripts/smart_discovery_util.py` | 17 | 0 | 0 |  |
| 16 | L_OPS | `ops_scripts/dev_tools/L0_routing_scripts/_ssot_routing.py` | 16 | 0 | 0 |  |
| 16 | L_TOOLS | `tools/guardian/scripts/rename_low_signal_tests.py` | 16 | 0 | 0 |  |
| 15 | L_OPS | `ops_scripts/dev_tools/L0_routing_scripts/run_guardian_architecture_governance.py` | 15 | 0 | 0 |  |
| 15 | L_OPS | `ops_scripts/dev_tools/L0_routing_scripts/run_guardian_classification_compliance.py` | 15 | 0 | 0 |  |
| 15 | L_OPS | `ops_scripts/dev_tools/L2_execution_scripts/remediation_dispatcher.py` | 15 | 0 | 0 |  |
| 15 | L_OPS | `ops_scripts/general/ast_import_audit.py` | 15 | 0 | 0 |  |
| 15 | L_OPS | `ops_scripts/general/clean_duplicates_enhanced.py` | 15 | 0 | 0 |  |
| 15 | L_TOOLS | `tools/adg/adg_ci_lane_gate.py` | 15 | 0 | 0 |  |
| 15 | L_TOOLS | `tools/eval/retrieval_benchmark.py` | 15 | 0 | 0 |  |
| 14 | L_OPS | `ops_scripts/dev_tools/L0_routing_scripts/colors.py` | 14 | 0 | 0 |  |
| 14 | L_OPS | `ops_scripts/dev_tools/L0_routing_scripts/run_guardian_c0_sovereignty.py` | 14 | 0 | 0 |  |
| 14 | L_OPS | `ops_scripts/dev_tools/L0_routing_scripts/run_guardian_change_package_activation.py` | 14 | 0 | 0 |  |
| 14 | L_OPS | `ops_scripts/dev_tools/L0_routing_scripts/run_guardian_cross_layer_mutation.py` | 14 | 0 | 0 |  |
| 14 | L_OPS | `ops_scripts/dev_tools/L0_routing_scripts/run_guardian_escalation_determinism.py` | 14 | 0 | 0 |  |
| 14 | L_OPS | `ops_scripts/dev_tools/L0_routing_scripts/run_guardian_gateway_bypass.py` | 14 | 0 | 0 |  |
| 14 | L_OPS | `ops_scripts/dev_tools/l0_scripts/pascal_sovereignty_fixer.py` | 14 | 0 | 0 |  |
| 13 | L_OPS | `ops_scripts/dev_tools/L0_routing_scripts/_ssot_reporting.py` | 13 | 0 | 0 |  |
| 13 | L_OPS | `ops_scripts/dev_tools/L0_routing_scripts/class_info.py` | 13 | 0 | 0 |  |
| 13 | L_OPS | `ops_scripts/dev_tools/L0_routing_scripts/fission_executor_util.py` | 13 | 0 | 0 |  |
| 13 | L_OPS | `ops_scripts/dev_tools/L0_routing_scripts/run_all_guardians.py` | 13 | 0 | 0 |  |
| 13 | L_OPS | `ops_scripts/dev_tools/L0_routing_scripts/run_guardian_location_alignment.py` | 13 | 0 | 0 |  |
| 13 | L_OPS | `ops_scripts/dev_tools/L3_orchestration_scripts/guardian_heal_orchestrator.py` | 13 | 0 | 0 |  |
| 13 | L_OPS | `ops_scripts/dev_tools/l0_scripts/rescue_reviewer.py` | 13 | 0 | 0 |  |
| 13 | L_OPS | `ops_scripts/dev_tools/l0_scripts/syntax_healer.py` | 13 | 0 | 0 |  |
| 13 | L_OPS | `ops_scripts/dev_tools/l0_scripts/zombie_vaccinator.py` | 13 | 0 | 0 |  |
| 13 | L_OPS | `ops_scripts/general/state_snapshot.py` | 13 | 0 | 0 |  |
| 13 | L_TOOLS | `tools/adg/adg_stale_guard.py` | 13 | 0 | 0 |  |
| 13 | L_TOOLS | `tools/generate/ingestion/ingest_curated_agent_docs.py` | 13 | 0 | 0 |  |
| 13 | L_TOOLS | `tools/graphdb/cli.py` | 8 | 0 | 0 | Y |
| 12 | L_OPS | `ops_scripts/dev_tools/L0_routing/fix_all_tunnels_util.py` | 12 | 0 | 0 |  |
| 12 | L_OPS | `ops_scripts/dev_tools/L0_routing/force_annexation_util.py` | 12 | 0 | 0 |  |
| 12 | L_OPS | `ops_scripts/dev_tools/L0_routing/scorched_earth_merge_util.py` | 12 | 0 | 0 |  |
| 12 | L_OPS | `ops_scripts/dev_tools/L0_routing_scripts/chunk_type.py` | 12 | 0 | 0 |  |
| 12 | L_OPS | `ops_scripts/dev_tools/L0_routing_scripts/execution.py` | 12 | 0 | 0 |  |
| 12 | L_OPS | `ops_scripts/dev_tools/L0_routing_scripts/flatten_scripts_directory_util.py` | 12 | 0 | 0 |  |
| 12 | L_OPS | `ops_scripts/dev_tools/L0_routing_scripts/verify_intentional_variants_util.py` | 12 | 0 | 0 |  |
| 12 | L_OPS | `ops_scripts/dev_tools/L0_routing_scripts/verify_manifest_util.py` | 12 | 0 | 0 |  |
| 12 | L_OPS | `ops_scripts/dev_tools/l0_scripts/sync_mcp_util.py` | 12 | 0 | 0 |  |
| 12 | L_OPS | `ops_scripts/general/architecture_gap_analyzer.py` | 12 | 0 | 0 |  |
| 12 | L_OPS | `ops_scripts/general/benchmark_batch_optimization.py` | 12 | 0 | 0 |  |
| 12 | L_OPS | `ops_scripts/general/remediate_naming_audit.py` | 12 | 0 | 0 |  |
| 12 | L_OPS | `ops_scripts/verification/verify_adg_provenance.py` | 12 | 0 | 0 |  |
| 12 | L_TOOLS | `tools/generate/graph_projection.py` | 12 | 0 | 0 |  |
| 12 | L_TOOLS | `tools/graphdb/agent_integration/phase3/adaptive_learning.py` | 12 | 0 | 0 |  |
| 12 | L_TOOLS | `tools/graphdb/agent_integration/phase3/health_monitoring.py` | 12 | 0 | 0 |  |
| 11 | L_OPS | `ops_scripts/dev_tools/L0_routing/sovereign_alignment_v2_util.py` | 11 | 0 | 0 |  |
| 11 | L_OPS | `ops_scripts/dev_tools/L0_routing/sovereign_convergence_util.py` | 11 | 0 | 0 |  |
| 11 | L_OPS | `ops_scripts/dev_tools/L0_routing/structural_fix_util.py` | 11 | 0 | 0 |  |
| 11 | L_OPS | `ops_scripts/dev_tools/L0_routing_scripts/_ssot_validation_artifacts.py` | 11 | 0 | 0 |  |
| 11 | L_OPS | `ops_scripts/dev_tools/L0_routing_scripts/action_capability.py` | 11 | 0 | 0 |  |
| 11 | L_OPS | `ops_scripts/dev_tools/L0_routing_scripts/agent_capability_supplement_util.py` | 11 | 0 | 0 |  |
| 11 | L_OPS | `ops_scripts/dev_tools/L0_routing_scripts/archive_duplicate_tests_util.py` | 11 | 0 | 0 |  |
| 11 | L_OPS | `ops_scripts/dev_tools/L0_routing_scripts/bulk_hierarchy_heal_util.py` | 11 | 0 | 0 |  |
| 11 | L_OPS | `ops_scripts/dev_tools/L0_routing_scripts/collision_resolver.py` | 11 | 0 | 0 |  |
| 11 | L_OPS | `ops_scripts/dev_tools/L0_routing_scripts/drift.py` | 11 | 0 | 0 |  |
| 11 | L_OPS | `ops_scripts/dev_tools/L0_routing_scripts/execution_context.py` | 11 | 0 | 0 |  |
| 11 | L_OPS | `ops_scripts/dev_tools/L0_routing_scripts/run_guardian_contract_integrity.py` | 11 | 0 | 0 |  |
| 11 | L_OPS | `ops_scripts/dev_tools/L0_routing_scripts/run_hygiene_guardian_util.py` | 11 | 0 | 0 |  |
| 11 | L_OPS | `ops_scripts/dev_tools/L0_routing_scripts/ssot_cli.py` | 11 | 0 | 0 |  |
| 11 | L_OPS | `ops_scripts/dev_tools/l0_scripts/generate_structural_changes_report_util.py` | 11 | 0 | 0 |  |
| 11 | L_OPS | `ops_scripts/dev_tools/l0_scripts/swarm_scheduler.py` | 11 | 0 | 0 |  |
| 11 | L_OPS | `ops_scripts/dev_tools/l0_scripts/syntax_scar_repairer.py` | 11 | 0 | 0 |  |
| 11 | L_OPS | `ops_scripts/dev_tools/l0_scripts/tooling_add_docstrings_util.py` | 11 | 0 | 0 |  |
| 11 | L_OPS | `ops_scripts/general/aggressive_dedup.py` | 11 | 0 | 0 |  |
| 11 | L_OPS | `ops_scripts/general/install_git_hooks.py` | 6 | 0 | 0 | Y |
| 11 | L_OPS | `ops_scripts/general/logic_signature.py` | 11 | 0 | 0 |  |
| 11 | L_OPS | `ops_scripts/maintenance/execute_final_consolidation.py` | 11 | 0 | 0 |  |
| 11 | L_OPS | `ops_scripts/maintenance/run_classification.py` | 11 | 0 | 0 |  |
| 11 | L_OPS | `ops_scripts/root_scripts/create_discovery_snapshot.py` | 11 | 0 | 0 |  |
| 11 | L_OPS | `ops_scripts/verification/verify_apps_refactor_complete.py` | 11 | 0 | 0 |  |
| 11 | L_TOOLS | `tools/adg/adg_redis_ingest.py` | 11 | 0 | 0 |  |
| 11 | L_TOOLS | `tools/adg/cache/__init__.py` | 6 | 0 | 0 | Y |
| 11 | L_TOOLS | `tools/adg/prompt_assembly/cli.py` | 6 | 0 | 0 | Y |
| 11 | L_TOOLS | `tools/generate/generate_full_adg.py` | 11 | 0 | 0 |  |
| 11 | L_TOOLS | `tools/graphdb/agent_integration/cli.py` | 6 | 0 | 0 | Y |
| 11 | L_TOOLS | `tools/graphdb/agent_integration/phase3/autonomous_governance.py` | 11 | 0 | 0 |  |
| 11 | L_TOOLS | `tools/graphdb/agent_integration/phase4/multi_dimensional_analysis.py` | 11 | 0 | 0 |  |
| 11 | L_TOOLS | `tools/graphdb/agent_integration/phase4/swarm_intelligence.py` | 11 | 0 | 0 |  |
| 11 | L_TOOLS | `tools/graphdb/agent_integration/phase4/temporal_intelligence.py` | 11 | 0 | 0 |  |
| 11 | L_TOOLS | `tools/maintenance/audit_exclusion_staleness.py` | 11 | 0 | 0 |  |
| 10 | L_OPS | `ops_scripts/dev_tools/L0_routing/add_test_coverage_util.py` | 10 | 0 | 0 |  |
| 10 | L_OPS | `ops_scripts/dev_tools/L0_routing/gravity_audit_util.py` | 10 | 0 | 0 |  |
| 10 | L_OPS | `ops_scripts/dev_tools/L0_routing/ssot_discovery_util.py` | 10 | 0 | 0 |  |
| 10 | L_OPS | `ops_scripts/dev_tools/L0_routing/ssot_folder_cleanup_util.py` | 10 | 0 | 0 |  |
| 10 | L_OPS | `ops_scripts/dev_tools/L0_routing_scripts/_ssot_meta_learning.py` | 10 | 0 | 0 |  |
| 10 | L_OPS | `ops_scripts/dev_tools/L0_routing_scripts/add_subatomic_safe_util.py` | 10 | 0 | 0 |  |
| 10 | L_OPS | `ops_scripts/dev_tools/L0_routing_scripts/aggressive_dedup_util.py` | 10 | 0 | 0 |  |
| 10 | L_OPS | `ops_scripts/dev_tools/L0_routing_scripts/archive_duplicates_util.py` | 10 | 0 | 0 |  |
| 10 | L_OPS | `ops_scripts/dev_tools/L0_routing_scripts/bloat_analysis_util.py` | 10 | 0 | 0 |  |
| 10 | L_OPS | `ops_scripts/dev_tools/L0_routing_scripts/c_c_measurement.py` | 10 | 0 | 0 |  |
| 10 | L_OPS | `ops_scripts/dev_tools/L0_routing_scripts/debris_hunter.py` | 10 | 0 | 0 |  |
| 10 | L_OPS | `ops_scripts/dev_tools/L0_routing_scripts/demo_cli_functionality_util.py` | 10 | 0 | 0 |  |
| 10 | L_OPS | `ops_scripts/dev_tools/L0_routing_scripts/extract_agent_duplicates_util.py` | 10 | 0 | 0 |  |
| 10 | L_OPS | `ops_scripts/dev_tools/L0_routing_scripts/file_analysis.py` | 10 | 0 | 0 |  |
| 10 | L_OPS | `ops_scripts/dev_tools/L0_routing_scripts/find_missing_invocation_util.py` | 10 | 0 | 0 |  |
| 10 | L_OPS | `ops_scripts/dev_tools/L0_routing_scripts/gatekeeper_lock_util.py` | 10 | 0 | 0 |  |
| 10 | L_OPS | `ops_scripts/dev_tools/L0_routing_scripts/identify_low_quality_agents_util.py` | 10 | 0 | 0 |  |
| 10 | L_OPS | `ops_scripts/dev_tools/L0_routing_scripts/run_guardian_drift_detection.py` | 10 | 0 | 0 |  |
| 10 | L_OPS | `ops_scripts/dev_tools/L0_routing_scripts/run_guardian_hierarchy_compliance.py` | 10 | 0 | 0 |  |
| 10 | L_OPS | `ops_scripts/dev_tools/L0_routing_scripts/run_guardian_hygiene.py` | 10 | 0 | 0 |  |
| 10 | L_OPS | `ops_scripts/dev_tools/L0_routing_scripts/sovereign_precommit_no_hardcoded_util.py` | 10 | 0 | 0 |  |
| 10 | L_OPS | `ops_scripts/dev_tools/L0_routing_scripts/sovereign_precommit_no_raw_prompts_util.py` | 10 | 0 | 0 |  |
| 10 | L_OPS | `ops_scripts/dev_tools/L0_routing_scripts/validate_drilldown_util.py` | 10 | 0 | 0 |  |
| 10 | L_OPS | `ops_scripts/dev_tools/L0_routing_scripts/verify_agent_status_util.py` | 10 | 0 | 0 |  |
| 10 | L_OPS | `ops_scripts/dev_tools/L0_routing_scripts/verify_manifest_cleanliness_util.py` | 10 | 0 | 0 |  |
| 10 | L_OPS | `ops_scripts/dev_tools/l0_scripts/mock_subatomic_hop.py` | 10 | 0 | 0 |  |
| 10 | L_OPS | `ops_scripts/dev_tools/l0_scripts/standardize_base_agent_names_util.py` | 10 | 0 | 0 |  |
| 10 | L_OPS | `ops_scripts/dev_tools/l0_scripts/workflow_track_changes_util.py` | 10 | 0 | 0 |  |
| 10 | L_OPS | `ops_scripts/general/fix_duplicate_imports.py` | 10 | 0 | 0 |  |
| 10 | L_OPS | `ops_scripts/general/quick_hang_finder.py` | 10 | 0 | 0 |  |
| 10 | L_OPS | `ops_scripts/general/restore_app_agents.py` | 10 | 0 | 0 |  |
| 10 | L_OPS | `ops_scripts/general/restore_from_healing_backup.py` | 10 | 0 | 0 |  |
| 10 | L_OPS | `ops_scripts/general/run_file_classification_heal_agentic_core.py` | 10 | 0 | 0 |  |
| 10 | L_OPS | `ops_scripts/general/test_territory_mirror_enforcer.py` | 10 | 0 | 0 |  |
| 10 | L_OPS | `ops_scripts/maintenance/batch_restore_tests.py` | 10 | 0 | 0 |  |
| 10 | L_OPS | `ops_scripts/maintenance/execute_tiered_purge.py` | 10 | 0 | 0 |  |

## Top 15 scripts — direct CI edges


### `ops_scripts/dev_tools/L0_routing_scripts/full_agent_discovery.py` (score 19)

### `ops_scripts/dev_tools/L0_routing_scripts/forensic_discovery_prep.py` (score 18)

### `ops_scripts/dev_tools/L0_routing_scripts/_ssot_types.py` (score 17)

### `ops_scripts/dev_tools/l0_scripts/smart_discovery_util.py` (score 17)

### `ops_scripts/dev_tools/L0_routing_scripts/_ssot_routing.py` (score 16)

### `tools/guardian/scripts/rename_low_signal_tests.py` (score 16)

### `ops_scripts/dev_tools/L0_routing_scripts/run_guardian_architecture_governance.py` (score 15)

### `ops_scripts/dev_tools/L0_routing_scripts/run_guardian_classification_compliance.py` (score 15)

### `ops_scripts/dev_tools/L2_execution_scripts/remediation_dispatcher.py` (score 15)

### `ops_scripts/general/ast_import_audit.py` (score 15)

### `ops_scripts/general/clean_duplicates_enhanced.py` (score 15)

### `tools/adg/adg_ci_lane_gate.py` (score 15)

### `tools/eval/retrieval_benchmark.py` (score 15)

### `ops_scripts/dev_tools/L0_routing_scripts/colors.py` (score 14)

### `ops_scripts/dev_tools/L0_routing_scripts/run_guardian_c0_sovereignty.py` (score 14)

## Top 10 agents — direct CI edges


### `agentic_core/L5_safety/reasoning/LocationHealerAgent.py` (score 20)

### `agentic_core/L5_safety/reasoning/FileClassificationAgent.py` (score 19)

### `agentic_core/L5_safety/reasoning/PascalSovereigntyAgent.py` (score 19)

### `agentic_core/L5_safety/reasoning/CodeHealerAgent.py` (score 17)

### `agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py` (score 16)

### `agentic_core/L3_orchestration/reasoning/UnifiedAgent.py` (score 16)

### `agentic_core/L5_safety/reasoning/ArchitectureGovernorAgent.py` (score 16)

### `agentic_core/L5_safety/reasoning/GenerativeGuardAgent.py` (score 16)

### `agentic_core/L5_safety/reasoning/HygieneGuardianAgent.py` (score 16)

### `agentic_core/L3_orchestration/reasoning/engines/decomposition_orchestrator.py` (score 15)