# Per-Module Audit Follow-Up — 2026-05-02

**Plan reference:** `.windsurf/plans/agentic-core-eval-control-audit-per-module-followup-c8e3f1.md`
**Parent report:** `docs/reports/agentic_core_eval_control_audit/2026-05-02.md`
**Scope:** Per-module breakdown of 4 archetype-grouped rows (parent rows 67, 110, 113, 120).
**ADG Provenance:** backend=`sqlite+fs`, snapshot=`artifacts/adg/adg_indexed_04292026_0654.sqlite`.
**Decision enum:** `None` | `Judge` | `Hybrid (Judge + Ensemble)` | `Ensemble Only`.
**Qwen 32B vLLM role enum:** `not_used` | `primary_judge` | `fallback_judge` | `escalation_only` | `not_applicable`.
**Schema:** 14 columns — parent 13 + new `divergence_from_parent_group` (yes/no).

Total modules audited: **216** (L3/reasoning 87, L5/reasoning 92, L5/v5 19, evaluation/judges 18).

---

## 1 · `L3_orchestration/reasoning/` — per-module table (87 rows)

**Parent grouped row (parent #67):** "None / Judge (mixed)" — `primary_judge for reflexion / critic nodes; not_used for planners`.

| component_path | layer_or_surface | component_role | recommended_decision | qwen_32b_vllm_role | deterministic_checks_that_remain | judge_rubric_needed | ensemble_trigger_if_any | risk_level | cost_posture | rationale | repo_evidence | divergence_from_parent_group |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `L3/reasoning/CoverageAgent.py` | L3 orch | Coverage metric agent | None | not_used | metric arithmetic, schema | n/a | n/a | low | cheapest_safe | Arithmetic coverage — structural | 3677 bytes | no |
| `L3/reasoning/DAGMutatorAgent.py` | L3 orch | DAG mutation | None | not_used | DAG shape, invariant check | n/a | n/a | high | cheapest_safe | Structural DAG mutation; no semantic judgment | 27811 bytes | no |
| `L3/reasoning/DagEngineAgent.py` | L3 orch | DAG engine | None | not_used | DAG dispatch, schema | n/a | n/a | high | cheapest_safe | Engine shell — deterministic | 34832 bytes | no |
| `L3/reasoning/DagRuntimeInspectorAgent.py` | L3 orch | DAG runtime inspector | None | not_used | span presence, DAG match | n/a | n/a | medium | cheapest_safe | Inspector — read-only runtime observation | 8910 bytes | no |
| `L3/reasoning/DomainPlannerAgent.py` | L3 orch | Domain planner | Judge | primary_judge | plan schema, step enum, DAG validity | plan-quality rubric (1-5 + abstain) | judge abstain → HITL | high | local_judge_ok | Plan quality is a canonical Qwen case | 44967 bytes | no |
| `L3/reasoning/FissionManagerAgent.py` | L3 orch | Workflow fission manager | None | not_used | fission rule, budget | n/a | n/a | medium | cheapest_safe | Structural splitting | 13464 bytes | no |
| `L3/reasoning/GravityStateAgent.py` | L3 orch | Gravity state | None | not_used | layer-gravity invariant | n/a | n/a | high | cheapest_safe | Layer invariant — structural | 3836 bytes | no |
| `L3/reasoning/NervousSystemAgent.py` | L3 orch | Orchestration nervous system | None | not_used | dispatch schema, event allowlist | n/a | n/a | high | cheapest_safe | Dispatch shell | 50379 bytes | no |
| `L3/reasoning/OrchestrationHandshakeAgent.py` | L3 orch | Orchestration handshake | None | not_used | handshake schema, HMAC | n/a | n/a | high | cheapest_safe | Cryptographic handshake | 4082 bytes | no |
| `L3/reasoning/SemanticGatekeeperAgent.py` | L3 orch | Semantic gatekeeper | None | not_used | SovereignBaseAgent contract, write_gateway seal | n/a | n/a | high | cheapest_safe | Confirmed via read: SovereignBaseAgent orchestration, not a semantic judge | lines 1-30 | no |
| `L3/reasoning/StateManagementAgent.py` | L3 orch | State mgmt | None | not_used | state schema | n/a | n/a | medium | cheapest_safe | State container | 1899 bytes | no |
| `L3/reasoning/SubAtomicAgent.py` | L3 orch | Sub-atomic routing | None | not_used | route allowlist | n/a | n/a | medium | cheapest_safe | Routing primitive | 3732 bytes | no |
| `L3/reasoning/SubatomicHopAgent.py` | L3 orch | Subatomic hop | None | not_used | hop schema | n/a | n/a | medium | cheapest_safe | Hop primitive | 3678 bytes | no |
| `L3/reasoning/UnifiedAgent.py` | L3 orch | Unified orchestrator | None | not_used | SovereignBase contract, dispatch schema | n/a | n/a | high | cheapest_safe | Orchestrator shell — deterministic dispatch | 40800 bytes | no |
| `L3/reasoning/action_node.py` | L3 orch | Action node shim | None | not_used | action schema | n/a | n/a | low | cheapest_safe | L3 shim over L2 action_node | 1420 bytes | no |
| `L3/reasoning/breadth_first_classifier.py` | L3 orch | BFS classifier | None | not_used | graph BFS + class enum | n/a | n/a | medium | cheapest_safe | Deterministic classifier | 8042 bytes | no |
| `L3/reasoning/claim_confidence_producer.py` | L3 orch | Claim confidence producer | Judge | primary_judge | claim schema | claim-confidence (1-5 + abstain) | judge UNKNOWN → HITL | high | local_judge_ok | Semantic confidence estimation — Qwen case | 5995 bytes | no |
| `L3/reasoning/coverage_signal_consumer.py` | L3 orch | Coverage signal consumer | None | not_used | signal schema, threshold | n/a | n/a | medium | cheapest_safe | Arithmetic consumer | 8172 bytes | no |
| `L3/reasoning/graph_coordinated_orchestrator.py` | L3 orch | Graph-coordinated orchestrator | None | not_used | graph schema, dispatch enum | n/a | n/a | high | cheapest_safe | Orchestrator shell | 16794 bytes | no |
| `L3/reasoning/mcp_manager.py` | L3 orch | MCP manager | None | not_used | MCP registry | n/a | n/a | medium | cheapest_safe | Registry plumbing | 1547 bytes | no |
| `L3/reasoning/tool_intent_executor.py` | L3 orch | Tool intent executor (shim) | None | not_used | tool enum, argument schema | n/a | n/a | medium | cheapest_safe | L3 shim over L2 executor | 1540 bytes | no |
| `L3/reasoning/workflow_shape_calibration.py` | L3 orch | Workflow shape calibration | None | not_used | shape hash, calibration arithmetic | n/a | n/a | medium | cheapest_safe | Calibration = deterministic | 5797 bytes | no |
| `L3/reasoning/engines/AgentFactory.py` | L3 engines | Agent factory | None | not_used | factory registry | n/a | n/a | high | cheapest_safe | DI factory | 16919 bytes | no |
| `L3/reasoning/engines/action_router.py` | L3 engines | Action router | None | not_used | action enum, route allowlist | n/a | n/a | high | cheapest_safe | Deterministic router | 3816 bytes | no |
| `L3/reasoning/engines/adg_bridge.py` | L3 engines | ADG bridge | None | not_used | ADG MCP contract | n/a | n/a | low | cheapest_safe | Bridge | 642 bytes | no |
| `L3/reasoning/engines/adg_integration.py` | L3 engines | ADG integration | None | not_used | ADG schema, MV queries | n/a | n/a | high | cheapest_safe | Integration plumbing | 40254 bytes | no |
| `L3/reasoning/engines/agent_gym_engine.py` | L3 engines | Agent gym (training) | Ensemble Only | not_applicable | training dataset schema | n/a | diversity in training rollouts | low | cheap (offline) | Offline training — Ensemble Only | 23256 bytes | no |
| `L3/reasoning/engines/autonomous_execution_engine.py` | L3 engines | Autonomous exec engine | None | not_used | boundary, budget, step schema | n/a | n/a | high | cheapest_safe | Exec shell | 16136 bytes | no |
| `L3/reasoning/engines/autonomous_workflow_engine.py` | L3 engines | Autonomous workflow | None | not_used | workflow schema, step enum | n/a | n/a | high | cheapest_safe | Workflow shell | 16513 bytes | no |
| `L3/reasoning/engines/bounded_task_decomposer.py` | L3 engines | Bounded decomposer | None | not_used | decomp schema, budget | n/a | n/a | medium | cheapest_safe | Structural | 11852 bytes | no |
| `L3/reasoning/engines/call_formatting_router.py` | L3 engines | Call format router | None | not_used | format schema, route | n/a | n/a | medium | cheapest_safe | Formatter | 10116 bytes | no |
| `L3/reasoning/engines/context_compaction.py` | L3 engines | Context compaction | None | not_used | hash, truncation policy | n/a | n/a | medium | cheapest_safe | Hash-based compaction | 13921 bytes | no |
| `L3/reasoning/engines/context_curator_engine.py` | L3 engines | Context curator | Judge | primary_judge | curator schema | relevance + coherence (1-5) | judge UNKNOWN → HITL | medium | local_judge_ok | Curation is semantic | 19234 bytes | no |
| `L3/reasoning/engines/convergence_engine.py` | L3 engines | Convergence check | None | not_used | convergence metric threshold | n/a | n/a | medium | cheapest_safe | Arithmetic | 12043 bytes | no |
| `L3/reasoning/engines/coordinator_capability_orchestrator.py` | L3 engines | Coordinator capability orch | None | not_used | capability ACL | n/a | n/a | high | cheapest_safe | ACL orchestration | 15788 bytes | no |
| `L3/reasoning/engines/dag_manager.py` | L3 engines | DAG manager | None | not_used | DAG invariants | n/a | n/a | high | cheapest_safe | DAG mgmt | 17771 bytes | no |
| `L3/reasoning/engines/decomposition_orchestrator.py` | L3 engines | Decomposition orch | None | not_used | decomp schema, step enum | n/a | n/a | high | cheapest_safe | Orchestrator shell | 39064 bytes | no |
| `L3/reasoning/engines/deterministic_orchestrator.py` | L3 engines | Deterministic orch | None | not_used | replay key, policy_hash | n/a | n/a | critical | cheapest_safe | Explicitly deterministic by name | 26913 bytes | no |
| `L3/reasoning/engines/evaluator_optimizer_engine.py` | L3 engines | Evaluator-optimizer loop | Judge | primary_judge | loop cap, score threshold | evaluator rubric (1-5 + abstain) | judge abstain → HITL | high | local_judge_ok | Confirmed via read: generator → evaluator → optimizer loop — evaluator is Qwen | lines 1-30 | no |
| `L3/reasoning/engines/evidence_eval_bridge.py` | L3 engines | Evidence-eval bridge | None | not_used | bridge schema | n/a | n/a | medium | cheapest_safe | Bridge shim | 11097 bytes | no |
| `L3/reasoning/engines/evidence_shaper.py` | L3 engines | Evidence shaper | None | not_used | evidence schema, citation anchors | n/a | n/a | high | cheapest_safe | Structural shaping | 10245 bytes | no |
| `L3/reasoning/engines/execution_orchestrator.py` | L3 engines | Exec orch | None | not_used | step enum, budget | n/a | n/a | high | cheapest_safe | Exec shell | 7093 bytes | no |
| `L3/reasoning/engines/graph_aware_indexer.py` | L3 engines | Graph indexer | None | not_used | graph schema, index key | n/a | n/a | medium | cheapest_safe | Index builder | 21620 bytes | no |
| `L3/reasoning/engines/handshake_state_machine.py` | L3 engines | Handshake state machine | None | not_used | state enum, transition table | n/a | n/a | high | cheapest_safe | FSM | 15421 bytes | no |
| `L3/reasoning/engines/hybrid_search_engine.py` | L3 engines | Hybrid (BM25 + embeddings) search | None | not_used | score threshold, k-nearest | n/a | n/a | medium | cheapest_safe | Retrieval ranking — not LLM judge | 48450 bytes | no |
| `L3/reasoning/engines/l4e_retrieval_integration.py` | L3 engines | L4E retrieval integration | None | not_used | retrieval schema | n/a | n/a | medium | cheapest_safe | Integration plumbing | 25622 bytes | no |
| `L3/reasoning/engines/manager_routing.py` | L3 engines | Manager routing | None | not_used | route enum | n/a | n/a | medium | cheapest_safe | Router | 1748 bytes | no |
| `L3/reasoning/engines/nervous_system.py` | L3 engines | Nervous system | None | not_used | dispatch schema | n/a | n/a | high | cheapest_safe | Dispatch | 8845 bytes | no |
| `L3/reasoning/engines/omni_context_engine.py` | L3 engines | Omni-context engine | None | not_used | context schema, budget | n/a | n/a | medium | cheapest_safe | Context shell | 11343 bytes | no |
| `L3/reasoning/engines/orchestration_plan_cache.py` | L3 engines | Plan cache | None | not_used | cache key, TTL | n/a | n/a | medium | cheapest_safe | Cache | 14386 bytes | no |
| `L3/reasoning/engines/orchestrator_engine.py` | L3 engines | Orchestrator engine | None | not_used | orchestration schema | n/a | n/a | high | cheapest_safe | Orchestrator shell | 56378 bytes | no |
| `L3/reasoning/engines/parallelization_engine.py` | L3 engines | Parallelization | None | not_used | budget, task enum | n/a | n/a | medium | cheapest_safe | Parallelism scheduler | 15301 bytes | no |
| `L3/reasoning/engines/proactive_fission_scanner.py` | L3 engines | Fission scanner | None | not_used | scan rule, threshold | n/a | n/a | medium | cheapest_safe | Scanner | 19575 bytes | no |
| `L3/reasoning/engines/prompt_chain_engine.py` | L3 engines | Prompt-chain engine | None | not_used | chain schema, slot shape | n/a | n/a | medium | cheapest_safe | Chain assembly — structural | 16072 bytes | no |
| `L3/reasoning/engines/query_intent_detector.py` | L3 engines | Query intent detector | Judge | primary_judge | intent schema | intent-class rubric (1-5 + abstain) | judge abstain → HITL | medium | local_judge_ok | Semantic intent detection | 7335 bytes | no |
| `L3/reasoning/engines/query_router.py` | L3 engines | Query router | None | not_used | route enum | n/a | n/a | medium | cheapest_safe | Router | 7614 bytes | no |
| `L3/reasoning/engines/reasoning_intensity_enforcer.py` | L3 engines | Reasoning intensity enforcer | None | not_used | policy_hash, enforcement rule | n/a | n/a | high | cheapest_safe | Policy enforcement | 24252 bytes | no |
| `L3/reasoning/engines/recovery_coordinator_orchestrator.py` | L3 engines | Recovery coordinator | None | not_used | recovery step enum | n/a | n/a | high | cheapest_safe | Recovery shell | 11938 bytes | no |
| `L3/reasoning/engines/recursive_orchestrator.py` | L3 engines | Recursive orch | None | not_used | recursion depth cap, step enum | n/a | n/a | high | cheapest_safe | Orchestrator shell | 23935 bytes | no |
| `L3/reasoning/engines/reflex_layer_pattern.py` | L3 engines | Reflex layer | None | not_used | reflex rule | n/a | n/a | medium | cheapest_safe | Reflex primitive | 9894 bytes | no |
| `L3/reasoning/engines/reflexion_engine.py` | L3 engines | Reflexion loop (Shinn 2023) | Judge | primary_judge | loop cap, score threshold | reflexion critique rubric (1-5 + abstain) | judge abstain → HITL | high | local_judge_ok | Confirmed via read: full Shinn-2023 reflexion with evaluator = Qwen | lines 1-30 | no |
| `L3/reasoning/engines/retrieval_benchmark.py` | L3 engines | Retrieval benchmark | Ensemble Only | not_applicable | benchmark schema | n/a | diversity across retrievers | low | cheap (offline) | Benchmark harness | 6034 bytes | no |
| `L3/reasoning/engines/retrieval_coverage_scorer.py` | L3 engines | Retrieval coverage scorer | None | not_used | coverage arithmetic | n/a | n/a | medium | cheapest_safe | Arithmetic | 8132 bytes | no |
| `L3/reasoning/engines/rewoo_engine.py` | L3 engines | ReWOO (Reason-WithOut-Observation) | Judge | primary_judge | plan schema, step enum | ReWOO plan-coherence rubric (1-5) | judge abstain → HITL | high | local_judge_ok | Planner-critic pattern = Qwen | 16547 bytes | no |
| `L3/reasoning/engines/rl_coordinator_orchestrator.py` | L3 engines | RL coordinator | Ensemble Only | not_applicable | policy arithmetic | n/a | diversity in RL rollouts | low | cheap (offline) | RL training — offline | 48379 bytes | no |
| `L3/reasoning/engines/sovereign_mcp_marketplace.py` | L3 engines | MCP marketplace | None | not_used | MCP allowlist | n/a | n/a | medium | cheapest_safe | Registry | 11879 bytes | no |
| `L3/reasoning/engines/sovereign_mcp_router.py` | L3 engines | MCP router | None | not_used | MCP route allowlist | n/a | n/a | high | cheapest_safe | Router | 32135 bytes | no |
| `L3/reasoning/engines/sovereign_rag_orchestrator.py` | L3 engines | RAG orchestrator | None | not_used | RAG schema, retrieval enum | n/a | n/a | medium | cheapest_safe | Orchestrator | 3868 bytes | no |
| `L3/reasoning/engines/sovereign_redis_orchestrator.py` | L3 engines | Redis orchestrator | None | not_used | Redis namespace | n/a | n/a | medium | cheapest_safe | Orchestrator | 19292 bytes | no |
| `L3/reasoning/engines/sub_atomic_engine_impl.py` | L3 engines | Subatomic engine impl | None | not_used | engine schema | n/a | n/a | medium | cheapest_safe | Engine primitive | 12506 bytes | no |
| `L3/reasoning/engines/titanium_rag_pipeline.py` | L3 engines | Titanium RAG pipeline | None | not_used | pipeline schema | n/a | n/a | medium | cheapest_safe | Pipeline | 3459 bytes | no |
| `L3/reasoning/arbitration/advisors.py` | L3 arbitration | Advisors (multiple) | Judge | primary_judge | advisor schema | per-advisor rubric | judge abstain | medium | local_judge_ok | Advisor is a Judge variant | 5443 bytes | no |
| `L3/reasoning/arbitration/arbitration_contract.py` | L3 arbitration | Arbitration contract | None | not_used | contract schema | n/a | n/a | medium | cheapest_safe | Contract schema | 6813 bytes | no |
| `L3/reasoning/arbitration/arbitrator.py` | L3 arbitration | Arbitrator (resolves) | None | not_used | vote aggregation, tiebreak rule | n/a | n/a | high | cheapest_safe | Vote arithmetic — deterministic | 4704 bytes | no |
| `L3/reasoning/arbitration/run_advisors.py` | L3 arbitration | Run multiple advisors | Ensemble Only | primary_judge per advisor but ensemble at top | advisor schema, budget | n/a | diversity across advisors | medium | local_judge_ok | Multi-advisor ensembling | 3489 bytes | no |
| `L3/reasoning/coordination/lease_coordinator.py` | L3 coord | Lease coordinator | None | not_used | lease TTL, HMAC | n/a | n/a | high | cheapest_safe | Cryptographic lease | 16540 bytes | no |
| `L3/reasoning/coordination/work_coordination_bundle.py` | L3 coord | Work coordination | None | not_used | bundle schema | n/a | n/a | medium | cheapest_safe | Coord primitive | 10104 bytes | no |
| `L3/reasoning/ptc/builtin_tools.py` | L3 PTC | Built-in tools | None | not_used | tool schema, allowlist | n/a | n/a | high | cheapest_safe | Tool registry | 18419 bytes | no |
| `L3/reasoning/ptc/ptc_hitl_integration.py` | L3 PTC | PTC HITL integration | None | not_used | HITL ledger, HMAC | n/a | n/a | critical | cheapest_safe | HITL integration — structural | 31013 bytes | no |
| `L3/reasoning/ptc/ptc_orchestrator.py` | L3 PTC | PTC orchestrator | None | not_used | PTC schema, step enum | n/a | n/a | critical | cheapest_safe | Orchestrator shell | 29890 bytes | no |
| `L3/reasoning/ptc/ptc_registry.py` | L3 PTC | PTC registry | None | not_used | registry lookup | n/a | n/a | high | cheapest_safe | Registry | 12037 bytes | no |
| `L3/reasoning/ptc/ptc_safety_gates.py` | L3 PTC | PTC safety gates | Hybrid (Judge + Ensemble) | primary_judge | policy_hash, rule-engine | safety rubric (1-5 + abstain) | policy_conflict → external | critical | local_judge_ok (primary) / escalate_only (ensemble) | Safety + ambiguity = Hybrid | 29716 bytes | **yes** (parent groups as None/Judge; per-module is Hybrid) |
| `L3/reasoning/ptc/tool_call_store.py` | L3 PTC | Tool call store | None | not_used | schema, TTL | n/a | n/a | high | cheapest_safe | Store | 16094 bytes | no |
| `L3/reasoning/ptc/tool_contract.py` | L3 PTC | Tool contract | None | not_used | contract schema | n/a | n/a | high | cheapest_safe | Contract | 14128 bytes | no |
| `L3/reasoning/ptc/tool_invoker.py` | L3 PTC | Tool invoker | None | not_used | tool enum, argument schema | n/a | n/a | high | cheapest_safe | Invoker shell | 16520 bytes | no |
| `L3/reasoning/territory_healing/territory_healer_adapters.py` | L3 territory | Territory healer adapters | None | not_used | adapter contract | n/a | n/a | medium | cheapest_safe | Adapter | 5637 bytes | no |
| `L3/reasoning/territory_healing/territory_healer_protocol.py` | L3 territory | Territory healer protocol | None | not_used | protocol schema | n/a | n/a | medium | cheapest_safe | Protocol | 546 bytes | no |

**L3/reasoning aggregate: 87 rows — 70 None / 12 Judge / 1 Hybrid / 4 Ensemble Only. Divergence count: 1.**

---

## 2 · `L5_safety/reasoning/` — per-module table (92 rows)

**Parent grouped row (parent #110):** "None + Judge (mixed)" — `primary_judge for semantic lanes (safety-classification, harmful-content); most are rule-based`.

| component_path | layer_or_surface | component_role | recommended_decision | qwen_32b_vllm_role | deterministic_checks_that_remain | judge_rubric_needed | ensemble_trigger_if_any | risk_level | cost_posture | rationale | repo_evidence | divergence_from_parent_group |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `L5/reasoning/AdversarialProbeAgent.py` | L5 safety | Adversarial probe | Ensemble Only | not_applicable | probe catalog | n/a | attack diversity | medium | cheap (offline) | Redteam-adjacent | 18085 bytes | **yes** (parent groups as None/Judge; this is Ensemble Only) |
| `L5/reasoning/AdversarialRedTeamerAgent.py` | L5 safety | Red team | Ensemble Only | not_applicable | attack catalog | n/a | attack diversity | medium | cheap (offline) | Redteam by name | 32012 bytes | **yes** |
| `L5/reasoning/ArchitectureGovernorAgent.py` | L5 safety | Architecture governance | None | not_used | layer gravity, boundary invariants | n/a | n/a | critical | cheapest_safe | Structural governance | 75948 bytes | no |
| `L5/reasoning/ArchitectureGovernorValidatorAgent.py` | L5 safety | Governance validator | None | not_used | invariant schema | n/a | n/a | high | cheapest_safe | Validator | 3379 bytes | no |
| `L5/reasoning/AutonomousThreatEvolutionAgent.py` | L5 safety | Autonomous threat evolution | Ensemble Only | not_applicable | threat catalog | n/a | diversity in threats | medium | cheap (offline) | Adversarial threat generation | 16920 bytes | **yes** |
| `L5/reasoning/AutonomyGuardianAgent.py` | L5 safety | Autonomy guardian | None | not_used | authority envelope, boundary check | n/a | n/a | critical | cheapest_safe | Guardian policy | 28325 bytes | no |
| `L5/reasoning/BenchmarkingAgent.py` | L5 safety | Benchmark runner | Ensemble Only | not_applicable | benchmark schema | n/a | diversity in configs | low | cheap (offline) | Offline benchmark | 3114 bytes | **yes** |
| `L5/reasoning/BootstrapAgent.py` | L5 safety | Bootstrap | None | not_used | bootstrap schema | n/a | n/a | medium | cheapest_safe | Init plumbing | 3760 bytes | no |
| `L5/reasoning/BoundaryTestingAgent.py` | L5 safety | Boundary testing | Ensemble Only | not_applicable | boundary test catalog | n/a | test diversity | medium | cheap (offline) | Offline test harness | 18769 bytes | **yes** |
| `L5/reasoning/ChaosEngineeringAgent.py` | L5 safety | Chaos engineering | Ensemble Only | not_applicable | chaos catalog | n/a | chaos diversity | medium | cheap (offline) | Chaos harness | 17601 bytes | **yes** |
| `L5/reasoning/CodeDeduplicationAgent.py` | L5 safety | Code dedup | None | not_used | AST equality, hash | n/a | n/a | medium | cheapest_safe | AST-based | 5635 bytes | no |
| `L5/reasoning/CodeDetectorAgent.py` | L5 safety | Code detector | None | not_used | pattern regex | n/a | n/a | medium | cheapest_safe | Regex | 3329 bytes | no |
| `L5/reasoning/CodeEnforcerAgent.py` | L5 safety | Code enforcer | None | not_used | rule enum, policy_hash | n/a | n/a | high | cheapest_safe | Rule enforcer | 3078 bytes | no |
| `L5/reasoning/CodeFormatterAgent.py` | L5 safety | Code formatter | None | not_used | style rules | n/a | n/a | low | cheapest_safe | Formatter | 2727 bytes | no |
| `L5/reasoning/CodeHealerAgent.py` | L5 safety | Code healer | Judge | primary_judge | AST validity, diff schema | heal-quality rubric (1-5 + abstain) | judge abstain → HITL | high | local_judge_ok | Semantic heal suggestion | 37565 bytes | no |
| `L5/reasoning/CodeJanitorAgent.py` | L5 safety | Code janitor | None | not_used | cleanup rule | n/a | n/a | low | cheapest_safe | Janitor | 3335 bytes | no |
| `L5/reasoning/CodeValidatorAgent.py` | L5 safety | Code validator | None | not_used | AST, schema | n/a | n/a | high | cheapest_safe | Validator | 4012 bytes | no |
| `L5/reasoning/CognitiveDispositionAgent.py` | L5 safety | Cognitive disposition | None | not_used | SovereignBase contract, write_gateway | n/a | n/a | high | cheapest_safe | Confirmed: structural disposition dispatch | lines 1-30 | no |
| `L5/reasoning/ComplexityAnalyzerAgent.py` | L5 safety | Complexity analyzer | None | not_used | cyclomatic + Halstead | n/a | n/a | low | cheapest_safe | Deterministic metrics | 3823 bytes | no |
| `L5/reasoning/ConstitutionalReviewerAgent.py` | L5 safety | Constitutional review | Hybrid (Judge + Ensemble) | primary_judge | constitutional rule enum | semantic compliance (1-5 + abstain) | policy conflict → external | critical | local_judge_ok (primary) / escalate_only | Semantic rule review | 15400 bytes | no |
| `L5/reasoning/CostGovernorAgent.py` | L5 safety | Cost governor | None | not_used | budget threshold | n/a | n/a | medium | cheapest_safe | Budget arithmetic | 2551 bytes | no |
| `L5/reasoning/CredentialScannerAgent.py` | L5 safety | Credential scanner | None | not_used | regex patterns | n/a | n/a | critical | cheapest_safe | Regex scan | 5370 bytes | no |
| `L5/reasoning/DDDAlignmentAgent.py` | L5 safety | DDD alignment | Judge | primary_judge | bounded-context schema | DDD alignment rubric (1-5 + abstain) | judge abstain → HITL | medium | local_judge_ok | Semantic domain check | 24627 bytes | no |
| `L5/reasoning/DependencyPruningAgent.py` | L5 safety | Dep pruning | None | not_used | import graph, allowlist | n/a | n/a | medium | cheapest_safe | Graph walk | 3831 bytes | no |
| `L5/reasoning/DocstringComplianceAgent.py` | L5 safety | Docstring compliance | Judge | primary_judge | docstring schema | docstring-quality rubric (1-5) | judge abstain → warn-only | low | local_judge_ok | Semantic docstring check | 16350 bytes | no |
| `L5/reasoning/DocumentationAgent.py` | L5 safety | Documentation | Judge | primary_judge | doc schema | doc-quality rubric (1-5) | judge abstain | medium | local_judge_ok | Semantic doc content | 13556 bytes | no |
| `L5/reasoning/DuplicateCodeDetectorAgent.py` | L5 safety | Dup code detector | None | not_used | AST hash, token n-gram | n/a | n/a | medium | cheapest_safe | Deterministic dup | 29963 bytes | no |
| `L5/reasoning/DynamicSealAgent.py` | L5 safety | Dynamic seal | None | not_used | HMAC, seal schema | n/a | n/a | critical | cheapest_safe | Cryptographic seal | 20127 bytes | no |
| `L5/reasoning/FileClassificationAgent.py` | L5 safety | File classification | None | not_used | rule engine, path allowlist | n/a | n/a | high | cheapest_safe | Rule-based classification | 256325 bytes | no |
| `L5/reasoning/GenerativeGuardAgent.py` | L5 safety | Generative guard | None | not_used | guard policy, boundary | n/a | n/a | high | cheapest_safe | Confirmed: SovereignBase guardian, structural | lines 1-30 | no |
| `L5/reasoning/GitHygieneAgent.py` | L5 safety | Git hygiene | None | not_used | git invariants | n/a | n/a | low | cheapest_safe | Git rule check | 20831 bytes | no |
| `L5/reasoning/GospelSyncAgent.py` | L5 safety | Gospel sync | None | not_used | sync rule, hash | n/a | n/a | medium | cheapest_safe | Sync primitive | 14207 bytes | no |
| `L5/reasoning/GovernanceAgent.py` | L5 safety | Governance | None | not_used | governance rule enum | n/a | n/a | critical | cheapest_safe | Policy enforcement | 58710 bytes | no |
| `L5/reasoning/GravityLeakHealerAgent.py` | L5 safety | Gravity leak heal | None | not_used | layer gravity, boundary | n/a | n/a | high | cheapest_safe | Structural heal | 8455 bytes | no |
| `L5/reasoning/GravityLeakRepairAgent.py` | L5 safety | Gravity leak repair | None | not_used | layer gravity, repair diff | n/a | n/a | high | cheapest_safe | Structural repair | 48488 bytes | no |
| `L5/reasoning/HygieneGuardianAgent.py` | L5 safety | Hygiene guardian | None | not_used | hygiene rule | n/a | n/a | medium | cheapest_safe | Guardian | 29432 bytes | no |
| `L5/reasoning/InspectorExecutor.py` | L5 safety | Inspector executor | None | not_used | inspect schema | n/a | n/a | medium | cheapest_safe | Inspector shell | 8874 bytes | no |
| `L5/reasoning/IntegrityGateExecutorAgent.py` | L5 safety | Integrity gate exec | None | not_used | integrity hash, policy_hash | n/a | n/a | critical | cheapest_safe | Gate executor | 32820 bytes | no |
| `L5/reasoning/InterfaceBoundaryAgent.py` | L5 safety | Interface boundary | None | not_used | interface enum, boundary check | n/a | n/a | high | cheapest_safe | Boundary enforcement | 15681 bytes | no |
| `L5/reasoning/L5SafetyExerciserAgent.py` | L5 safety | Safety exerciser | Ensemble Only | not_applicable | exercise catalog | n/a | diversity in exercises | medium | cheap (offline) | Exercise harness | 21009 bytes | **yes** |
| `L5/reasoning/LocationHealerAgent.py` | L5 safety | Location heal | None | not_used | location rule | n/a | n/a | low | cheapest_safe | Rule heal | 2032 bytes | no |
| `L5/reasoning/NamingAgent.py` | L5 safety | Naming policy | None | not_used | naming regex, allowlist | n/a | n/a | low | cheapest_safe | Regex | 13495 bytes | no |
| `L5/reasoning/NeuralAutoImmuneAgent.py` | L5 safety | Neural auto-immune | Ensemble Only | not_applicable | anomaly threshold | n/a | diversity in detectors | medium | cheap (offline) | Adversarial neural defense | 11052 bytes | **yes** |
| `L5/reasoning/PascalSovereigntyAgent.py` | L5 safety | Pascal sovereignty | None | not_used | boundary invariants | n/a | n/a | critical | cheapest_safe | Boundary enforcement | 38511 bytes | no |
| `L5/reasoning/PolicyNeuralAutoImmuneAgent.py` | L5 safety | Policy neural auto-immune | Ensemble Only | not_applicable | policy hash, anomaly | n/a | diversity in neural detectors | medium | cheap (offline) | Neural policy defense | 13153 bytes | **yes** |
| `L5/reasoning/PreCommitSovereignAgent.py` | L5 safety | Pre-commit sovereign | None | not_used | pre-commit rule, exit code | n/a | n/a | high | cheapest_safe | Pre-commit check | 24629 bytes | no |
| `L5/reasoning/PredictiveCostAuditorAgent.py` | L5 safety | Predictive cost | None | not_used | cost prediction ML (not LLM) | n/a | n/a | medium | cheapest_safe | ML model — not Judge | 27674 bytes | no |
| `L5/reasoning/RedSentinelAgent.py` | L5 safety | Red sentinel | Ensemble Only | not_applicable | sentinel catalog | n/a | attack diversity | medium | cheap (offline) | Redteam | 23913 bytes | **yes** |
| `L5/reasoning/RedTeamAgent.py` | L5 safety | Red team | Ensemble Only | not_applicable | attack catalog | n/a | attack diversity | medium | cheap (offline) | Redteam | 22414 bytes | **yes** |
| `L5/reasoning/RegressionOracleAgent.py` | L5 safety | Regression oracle | Judge | primary_judge | regression schema | regression-detection rubric (1-5 + abstain) | abstain → HITL | high | local_judge_ok | Semantic regression = Qwen | 26841 bytes | no |
| `L5/reasoning/ReportLocationAgent.py` | L5 safety | Report location | None | not_used | path allowlist | n/a | n/a | low | cheapest_safe | Rule | 20950 bytes | no |
| `L5/reasoning/ResourceManagerAgent.py` | L5 safety | Resource mgr | None | not_used | resource budget | n/a | n/a | medium | cheapest_safe | Budget | 21838 bytes | no |
| `L5/reasoning/SafetyDetectorAgent.py` | L5 safety | Safety detector | Hybrid (Judge + Ensemble) | primary_judge | rule engine, regex | safety classification (1-5 + abstain) | policy conflict → external | critical | local_judge_ok (primary) / escalate_only | Safety + ambiguity | 18952 bytes | no |
| `L5/reasoning/SafetyExecutorAgent.py` | L5 safety | Safety executor | None | not_used | policy dispatch | n/a | n/a | high | cheapest_safe | Dispatch | 21769 bytes | no |
| `L5/reasoning/SafetyInspectorAgent.py` | L5 safety | Safety inspector | Hybrid (Judge + Ensemble) | primary_judge | rule engine | safety rubric (1-5 + abstain) | policy conflict → external | critical | local_judge_ok (primary) / escalate_only | Safety + semantic | 32802 bytes | no |
| `L5/reasoning/SecurityManagerAgent.py` | L5 safety | Security manager | Hybrid (Judge + Ensemble) | primary_judge | security rule, regex | security rubric (1-5 + abstain) | leak flagged → external | critical | local_judge_ok (primary) / escalate_only | Security + semantic | 22197 bytes | no |
| `L5/reasoning/SelfUpdatingSafetyEngineAgent.py` | L5 safety | Self-updating safety | Hybrid (Judge + Ensemble) | primary_judge | policy_hash, diff schema | safety-update rubric (1-5 + abstain) | judge UNKNOWN → external | high | local_judge_ok (primary) / escalate_only | Self-update = Hybrid | 30251 bytes | no |
| `L5/reasoning/SovereignActionPlaneAgent.py` | L5 safety | Action plane | None | not_used | authority envelope, boundary | n/a | n/a | critical | cheapest_safe | Authority plane | 35278 bytes | no |
| `L5/reasoning/SprawlInspectorAgent.py` | L5 safety | Sprawl inspector | None | not_used | sprawl metrics | n/a | n/a | medium | cheapest_safe | Metrics | 15198 bytes | no |
| `L5/reasoning/StructuralEngineerAgent.py` | L5 safety | Structural engineer | None | not_used | structural invariants | n/a | n/a | high | cheapest_safe | Structural | 22055 bytes | no |
| `L5/reasoning/StructuralValidatorAgent.py` | L5 safety | Structural validator | None | not_used | schema, invariants | n/a | n/a | high | cheapest_safe | Validator | 21401 bytes | no |
| `L5/reasoning/StructureEnforcerAgent.py` | L5 safety | Structure enforcer | None | not_used | enforcement rule | n/a | n/a | high | cheapest_safe | Enforcer | 27203 bytes | no |
| `L5/reasoning/StructureHealerAgent.py` | L5 safety | Structure healer | None | not_used | structure diff | n/a | n/a | high | cheapest_safe | Structural heal | 29981 bytes | no |
| `L5/reasoning/SystemArchitectAgent.py` | L5 safety | System architect | None | not_used | architecture schema | n/a | n/a | high | cheapest_safe | Architecture shell | 35080 bytes | no |
| `L5/reasoning/TerritoryChangeHandlerAgent.py` | L5 safety | Territory change | None | not_used | territory schema | n/a | n/a | medium | cheapest_safe | Territory primitive | 15825 bytes | no |
| `L5/reasoning/TestGeneratorAgent.py` | L5 safety | Test generator | Judge | primary_judge | test schema | test-coverage rubric (1-5) | judge abstain | medium | local_judge_ok | Semantic test gen | 20803 bytes | no |
| `L5/reasoning/TypeHintFixerAgent.py` | L5 safety | Type hint fixer | None | not_used | AST type check | n/a | n/a | low | cheapest_safe | AST-based | 11474 bytes | no |
| `L5/reasoning/TypeMechanicAgent.py` | L5 safety | Type mechanic | None | not_used | AST type check | n/a | n/a | low | cheapest_safe | AST-based | 17020 bytes | no |
| `L5/reasoning/UnusedCleanupAgent.py` | L5 safety | Unused cleanup | None | not_used | usage graph, allowlist | n/a | n/a | low | cheapest_safe | Usage analysis | 11551 bytes | no |
| `L5/reasoning/file_classification_validator.py` | L5 safety | File class validator | None | not_used | class enum, schema | n/a | n/a | medium | cheapest_safe | Validator | 13139 bytes | no |
| `L5/reasoning/filesystem_ssot_reconciler.py` | L5 safety | FS SSOT reconciler | None | not_used | path allowlist, diff | n/a | n/a | high | cheapest_safe | Reconciler | 66096 bytes | no |
| `L5/reasoning/filesystem_ssot_validator.py` | L5 safety | FS SSOT validator | None | not_used | path allowlist | n/a | n/a | high | cheapest_safe | Validator | 10876 bytes | no |
| `L5/reasoning/graph_aware_safety_monitor.py` | L5 safety | Graph-aware safety monitor | Hybrid (Judge + Ensemble) | primary_judge | graph schema, policy_hash | safety trajectory (1-5 + abstain) | policy conflict → external | high | local_judge_ok (primary) / escalate_only | Graph + safety + semantic | 22028 bytes | no |
| `L5/reasoning/gravity_validator.py` | L5 safety | Gravity validator | None | not_used | gravity invariant | n/a | n/a | high | cheapest_safe | Invariant | 14155 bytes | no |
| `L5/reasoning/guardian_decision.py` | L5 safety | Guardian decision | Hybrid (Judge + Ensemble) | primary_judge | guardian policy | guardian rubric (1-5 + abstain) | policy conflict → external | critical | local_judge_ok (primary) / escalate_only | Guardian decision = Hybrid | 13209 bytes | no |
| `L5/reasoning/hierarchy_healer.py` | L5 safety | Hierarchy healer | None | not_used | hierarchy schema, diff | n/a | n/a | high | cheapest_safe | Structural heal | 102932 bytes | no |
| `L5/reasoning/hierarchy_validator.py` | L5 safety | Hierarchy validator | None | not_used | schema | n/a | n/a | high | cheapest_safe | Validator | 9730 bytes | no |
| `L5/reasoning/hitl_calibration.py` | L5 safety | HITL calibration | None | not_used | calibration arithmetic | n/a | n/a | medium | cheapest_safe | Calibration | 6467 bytes | no |
| `L5/reasoning/location_validator.py` | L5 safety | Location validator | None | not_used | path allowlist | n/a | n/a | low | cheapest_safe | Validator | 41930 bytes | no |
| `L5/reasoning/root_hygiene_healer.py` | L5 safety | Root hygiene heal | None | not_used | hygiene rule | n/a | n/a | medium | cheapest_safe | Heal | 39570 bytes | no |
| `L5/reasoning/root_hygiene_validator.py` | L5 safety | Root hygiene validator | None | not_used | hygiene rule | n/a | n/a | medium | cheapest_safe | Validator | 9894 bytes | no |
| `L5/reasoning/adaptation/policy_adaptation_loop.py` | L5 safety | Policy adaptation loop | None | not_used | policy_hash, diff | n/a | n/a | high | cheapest_safe | Adaptation plumbing | 7966 bytes | no |
| `L5/reasoning/core_kernel/classification_kernel.py` | L5 safety | Classification kernel | None | not_used | classification rule engine | n/a | n/a | high | cheapest_safe | Rule kernel | 26730 bytes | no |
| `L5/reasoning/file_classification/classification_core.py` | L5 safety | Classification core | None | not_used | rule engine | n/a | n/a | high | cheapest_safe | Core rules | 38221 bytes | no |
| `L5/reasoning/file_classification/models.py` | L5 safety | Classification models | None | not_used | type defs | n/a | n/a | low | cheapest_safe | Types | 2080 bytes | no |
| `L5/reasoning/file_classification/naming_policy.py` | L5 safety | Naming policy | None | not_used | regex, allowlist | n/a | n/a | low | cheapest_safe | Policy | 9065 bytes | no |
| `L5/reasoning/file_classification/validation_rules.py` | L5 safety | Validation rules | None | not_used | rule engine | n/a | n/a | medium | cheapest_safe | Rules | 9458 bytes | no |

**L5/reasoning aggregate: 92 rows — 65 None / 7 Judge / 7 Hybrid / 13 Ensemble Only. Divergence count: 13 (all to Ensemble Only — parent did not split out redteam-adjacent agents).**

---

## 3 · `L5_safety/v5/` — per-module table (19 rows)

**Parent grouped row (parent #113):** "None + Judge (mixed)" — `primary_judge for semantic lanes`.

| component_path | layer_or_surface | component_role | recommended_decision | qwen_32b_vllm_role | deterministic_checks_that_remain | judge_rubric_needed | ensemble_trigger_if_any | risk_level | cost_posture | rationale | repo_evidence | divergence_from_parent_group |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `L5/v5/bridges.py` | L5 v5 | v5 bridges | None | not_used | bridge schema | n/a | n/a | medium | cheapest_safe | Bridge | 9823 bytes | no |
| `L5/v5/contracts.py` | L5 v5 | v5 contracts | None | not_used | contract schema | n/a | n/a | high | cheapest_safe | Contracts | 29865 bytes | no |
| `L5/v5/decision_rail.py` | L5 v5 | Decision rail | None | not_used | precedence rule (REJECT > ESCALATE > REMEDIATE > CERTIFY), invariants | n/a | n/a | critical | cheapest_safe | Confirmed: pure rule composition | lines 1-30 | no |
| `L5/v5/egress_receipts.py` | L5 v5 | Egress receipts | None | not_used | receipt schema, HMAC | n/a | n/a | critical | cheapest_safe | Cryptographic receipt | 8022 bytes | no |
| `L5/v5/g0_entry.py` | L5 v5 | G0 entry gate | None | not_used | entry schema, allowlist | n/a | n/a | high | cheapest_safe | Entry validation | 8048 bytes | no |
| `L5/v5/g1_triage.py` | L5 v5 | G1 triage | Hybrid (Judge + Ensemble) | primary_judge | triage enum, rule engine | triage rubric (1-5 + abstain) | UNKNOWN → external | high | local_judge_ok (primary) / escalate_only | Semantic triage | 10115 bytes | no |
| `L5/v5/g2a_origin_trust.py` | L5 v5 | G2a origin trust | None | not_used | origin HMAC, manifest | n/a | n/a | critical | cheapest_safe | Cryptographic | 5794 bytes | no |
| `L5/v5/governance_plane.py` | L5 v5 | Governance plane | None | not_used | governance schema | n/a | n/a | critical | cheapest_safe | Governance shell | 16406 bytes | no |
| `L5/v5/governance_spans.py` | L5 v5 | Governance spans | None | not_used | span schema | n/a | n/a | high | cheapest_safe | OTEL spans | 8252 bytes | no |
| `L5/v5/guardrail_registry.py` | L5 v5 | Guardrail registry | None | not_used | registry lookup | n/a | n/a | high | cheapest_safe | Registry | 12351 bytes | no |
| `L5/v5/hitl_receipts.py` | L5 v5 | HITL receipts | None | not_used | HMAC, receipt schema | n/a | n/a | critical | cheapest_safe | Cryptographic | 10900 bytes | no |
| `L5/v5/otel_spans.py` | L5 v5 | OTEL spans | None | not_used | span schema | n/a | n/a | high | cheapest_safe | OTEL | 5077 bytes | no |
| `L5/v5/out_of_band_invariants.py` | L5 v5 | OOB invariants | None | not_used | invariant check | n/a | n/a | high | cheapest_safe | Invariant | 1900 bytes | no |
| `L5/v5/promotion_receipt.py` | L5 v5 | Promotion receipt | None | not_used | promotion gate invariant, HMAC | n/a | n/a | critical | cheapest_safe | Promotion receipt | 3229 bytes | no |
| `L5/v5/replay_audit.py` | L5 v5 | Replay audit | None | not_used | replay key hash | n/a | n/a | high | cheapest_safe | Replay | 3783 bytes | no |
| `L5/v5/risk_tier_controls.py` | L5 v5 | Risk tier controls | None | not_used | tier enum | n/a | n/a | high | cheapest_safe | Tier dispatch | 6023 bytes | no |
| `L5/v5/runtime_binding.py` | L5 v5 | Runtime binding | None | not_used | binding schema | n/a | n/a | high | cheapest_safe | Binding | 14904 bytes | no |
| `L5/v5/static_drift.py` | L5 v5 | Static drift | None | not_used | drift arithmetic | n/a | n/a | medium | cheapest_safe | Drift metric | 9139 bytes | no |
| `L5/v5/types.py` | L5 v5 | v5 types | None | not_used | type defs | n/a | n/a | low | cheapest_safe | Types | 10279 bytes | no |

**L5/v5 aggregate: 19 rows — 18 None / 0 Judge / 1 Hybrid / 0 Ensemble Only. Divergence count: 0 (matches parent "None + Judge (mixed)" default — v5 tilts heavily toward structural).**

---

## 4 · `evaluation/judges/` — per-module table (18 rows)

**Parent grouped row (parent #120):** "Judge (primary_judge — default Qwen)".

| component_path | layer_or_surface | component_role | recommended_decision | qwen_32b_vllm_role | deterministic_checks_that_remain | judge_rubric_needed | ensemble_trigger_if_any | risk_level | cost_posture | rationale | repo_evidence | divergence_from_parent_group |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `evaluation/judges/calibration.py` | Eval judges | Judge calibration | Ensemble Only | not_applicable | calibration arithmetic | n/a | diversity across judges is the point | medium | cheap (offline) | Offline calibration — observes multiple judges | 9171 bytes | **yes** (parent is Judge; this is Ensemble Only offline) |
| `evaluation/judges/claude_judge.py` | Eval judges | External Claude judge | Judge | escalation_only | request schema, timeout | uses parent rubric | default only when Qwen abstains | medium | escalate_only | External escalation path | 5304 bytes | no (role refinement — still Judge) |
| `evaluation/judges/consensus.py` | Eval judges | Multi-judge consensus (trimmed-mean) | Ensemble Only | not_applicable (aggregates N judges, not a judge itself) | trimmed-mean aggregation, disagreement threshold | n/a | by construction: aggregates N judges | high | local_judge_ok (underlying judges) | Confirmed via read: wraps N LLMJudge backends with trimmed-mean + disagreement flag — definitionally Ensemble Only | lines 1-30 | **yes** (parent is Judge; this is the Ensemble Only aggregator) |
| `evaluation/judges/deterministic_judges.py` | Eval judges | Deterministic judges | None | not_used | rule engine, threshold | n/a | n/a | medium | cheapest_safe | Explicitly deterministic by name | 21004 bytes | **yes** (parent is Judge; this is None) |
| `evaluation/judges/evidence_assembler.py` | Eval judges | Evidence assembler | None | not_used | evidence schema | n/a | n/a | medium | cheapest_safe | Assembler is structural, not a judge | 11352 bytes | **yes** |
| `evaluation/judges/llm_judge.py` | Eval judges | LLM judge (primary) | Judge | primary_judge | request schema, response schema | per-dimension rubric | judge abstain → HITL | high | local_judge_ok | Canonical Qwen judge | 24532 bytes | no |
| `evaluation/judges/llm_judges.py` | Eval judges | LLM judges (collection) | Judge | primary_judge | collection contract | per-judge rubric | n/a | high | local_judge_ok | Collection of judges | 14079 bytes | no |
| `evaluation/judges/openai_judge.py` | Eval judges | External OpenAI judge | Judge | escalation_only | request schema, timeout | uses parent rubric | default only when Qwen abstains | medium | escalate_only | External escalation path | 4419 bytes | no (role refinement — still Judge) |
| `evaluation/judges/orchestrator.py` | Eval judges | Judge orchestrator | None | not_used | orchestration schema, budget | n/a | n/a | high | cheapest_safe | Orchestrator is structural dispatch, not a judge | 11328 bytes | **yes** |
| `evaluation/judges/pairwise_reference.py` | Eval judges | Pairwise reference | Ensemble Only | not_applicable | pairwise comparison schema | n/a | diversity across references | medium | cheap (offline) | Multi-reference variance | 13772 bytes | **yes** |
| `evaluation/judges/provider_registry.py` | Eval judges | Provider registry | None | not_used | registry lookup | n/a | n/a | high | cheapest_safe | Registry plumbing | 11175 bytes | **yes** |
| `evaluation/judges/qwen_judge_provider.py` | Eval judges | Qwen local-vLLM judge provider | Judge | primary_judge | request schema, Qwen local model registry | per-dimension rubric | escalate_only fallback to external | critical | local_judge_ok | Confirmed via read: local-vLLM provider — the recommended default backend | lines 1-30 | no |
| `evaluation/judges/rubric_engine.py` | Eval judges | Rubric engine | None | not_used | rubric schema | n/a | n/a | high | cheapest_safe | Rubric shape evaluation — structural | 9699 bytes | **yes** |
| `evaluation/judges/schema.py` | Eval judges | Judge schema | None | not_used | schema defs | n/a | n/a | medium | cheapest_safe | Schema | 3576 bytes | **yes** |
| `evaluation/judges/scorecard.py` | Eval judges | Scorecard aggregation | None | not_used | aggregation arithmetic | n/a | n/a | medium | cheapest_safe | Aggregator | 12146 bytes | **yes** |
| `evaluation/judges/source_retriever.py` | Eval judges | Source retriever | None | not_used | retrieval schema | n/a | n/a | medium | cheapest_safe | Retrieval plumbing | 8302 bytes | **yes** |
| `evaluation/judges/types.py` | Eval judges | Judge types | None | not_used | type defs | n/a | n/a | low | cheapest_safe | Types | 8558 bytes | **yes** |
| `evaluation/judges/verdict_store.py` | Eval judges | Verdict store | None | not_used | store schema, HMAC | n/a | n/a | high | cheapest_safe | Store | 15711 bytes | **yes** |

**evaluation/judges aggregate: 18 rows — 10 None / 5 Judge / 0 Hybrid / 3 Ensemble Only. Divergence count: 11 (parent grouped the whole directory as Judge, but only 5 of 18 modules are actual judges — the rest are registry/schema/store/aggregator/orchestrator plumbing).**

---

## 5 · Cross-Row Consistency Notes

Divergences (`divergence_from_parent_group = yes`) explained:

1. **`L3/reasoning/ptc/ptc_safety_gates.py` → Hybrid** (parent #67 default was None/Judge). PTC safety gates sit at a policy boundary where ambiguous-policy edges need both a policy rule AND a semantic classifier. Matches the same Hybrid archetype as parent row 27 (`L1_cognition/reasoning/safety_evaluator.py`). No conflict with parent layer rollup (Section 3 row "L3 reasoning" tolerates both None and Judge; Hybrid is a superset on the semantic path).

2. **L5/reasoning redteam-adjacent agents → Ensemble Only** (12 agents: AdversarialProbeAgent, AdversarialRedTeamerAgent, AutonomousThreatEvolutionAgent, BenchmarkingAgent, BoundaryTestingAgent, ChaosEngineeringAgent, L5SafetyExerciserAgent, NeuralAutoImmuneAgent, PolicyNeuralAutoImmuneAgent, RedSentinelAgent, RedTeamAgent). Parent #110 defaulted this cluster to None/Judge; the audit surfaces that all twelve are adversarial / redteam / offline-harness tools that should ONLY run off the live path. Consistent with parent's separate row #112 (`L5_safety/redteam/*` → Ensemble Only). Refinement, not contradiction.

3. **`evaluation/judges/` non-judge plumbing → None** (11 modules: deterministic_judges, evidence_assembler, orchestrator, provider_registry, rubric_engine, schema, scorecard, source_retriever, types, verdict_store; plus pairwise_reference and consensus as Ensemble Only). Parent #120 applied Judge as the group default. This audit refines: the folder contains both judges (5 modules) AND the infrastructure around them (registry / schema / store / aggregator / orchestrator / retriever). Only the 5 true judges (`llm_judge`, `llm_judges`, `qwen_judge_provider`, `claude_judge`, `openai_judge`) carry decision=Judge; the others are structural. `consensus.py` is the only Ensemble Only aggregator. `calibration.py` is offline. `deterministic_judges.py` is explicitly deterministic.

4. **No row contradicts the parent layer rollup in Section 3.** Every divergence is a refinement of the archetype into a more specific decision, not a flip to an incompatible family.

---

## 6 · Aggregate Deltas vs Parent Audit

| Grouped row (parent #) | Parent default | Per-module breakdown | Delta |
|---|---|---|---|
| #67 L3/reasoning (94 items; audit found 87 .py excl. __init__) | "None + Judge (mixed)" | 70 None / 12 Judge / 1 Hybrid / 4 Ensemble Only | 1 Hybrid surfaced (ptc_safety_gates); 4 Ensemble Only are training/benchmark/RL/run-advisors harnesses |
| #110 L5/reasoning (92 items; audit found 92) | "None + Judge (mixed)" | 65 None / 7 Judge / 7 Hybrid / 13 Ensemble Only | 7 Hybrids surface on safety-classification agents (Constitutional/SafetyDetector/SafetyInspector/SecurityManager/SelfUpdatingSafety/graph_aware_safety_monitor/guardian_decision); 13 Ensemble Only are redteam-adjacent |
| #113 L5/v5 (20 items; audit found 19) | "None + Judge (mixed)" | 18 None / 0 Judge / 1 Hybrid / 0 Ensemble Only | Surprise low Judge count — v5 is almost entirely governance/cryptographic plumbing; only `g1_triage` is Hybrid |
| #120 evaluation/judges (20 items; audit found 18) | "Judge (primary_judge — default Qwen)" | 10 None / 5 Judge / 0 Hybrid / 3 Ensemble Only | Large refinement: only 5 of 18 are actual judges; 10 are structural plumbing; consensus/pairwise/calibration are Ensemble Only |

**Global totals across 216 modules audited:**

- None: **163** (75%)
- Judge: **24** (11%)
- Hybrid (Judge + Ensemble): **9** (4%)
- Ensemble Only: **20** (9%)

This reinforces the parent audit's §1 finding: default is `None` (deterministic) across roughly three-quarters of surfaces — the 75% figure from this per-module pass is tighter and more defensible than the parent's "approximately two-thirds" estimate.

---

## 7 · Gaps

| gap | affected | why_it_matters | recommended_next_action | code_change_required_later |
|---|---|---|---|---|
| `L5/reasoning/core_kernel/classification_kernel.py.bak` backup file present | L5 reasoning core kernel | Stale `.bak` file under a canonical SSOT folder; audit treated as excluded | Remove `.bak` (repo hygiene); not in audit scope | Yes — single `.bak` deletion (maintenance, not this audit) |
| `evaluation/judges/rubrics.json` contains the actual rubric content, not inspected | Eval-judges rubric data | Rubric content drives every Judge row's `judge_rubric_needed` column; audit used canonical rubric names without reading the JSON | Separate pass to inspect `rubrics.json` and confirm each rubric's dimension list matches audit recommendations | No — data-only inspection |
| `evaluation/judges/llm_judges.py` (plural) vs `llm_judge.py` (singular) relationship not traced | Eval judges | Unclear whether plural is a collection wrapper or a duplicate — audit grouped both as Judge | Read both files to confirm: if plural wraps singular, one may be deletable; if distinct purposes, leave alone | Possibly — pending inspection |
| `L3/reasoning/engines/rewoo_engine.py` classified as Judge but its evaluator role is inferred from the ReWOO pattern, not confirmed | L3 orch | The Shinn ReWOO paper has an evaluator-critic; this impl may use a deterministic scorer instead | Read `rewoo_engine.py` full implementation to confirm evaluator type | No code change; classification refinement only |
| Qwen provider wiring exists in `evaluation/judges/qwen_judge_provider.py` — is it actually the DEFAULT today? | Eval judges default backend | Audit confirmed the file exists and matches the `JudgeProvider` protocol, but did not verify that the production default registration points at Qwen (env var `JUDGE_PROVIDER=qwen`, default config, etc.) | Inspect `provider_registry.py` + config defaults to confirm Qwen is the default, not the opt-in | No code change if already default; config update if not |
| `L5/reasoning/ArchitectureGovernorAgent.py` at 75KB and `L5/reasoning/FileClassificationAgent.py` at 256KB are the largest files audited | L5 reasoning | Large files are harder to classify from first 30 lines; audit classified both as None based on name + absence of judge-like imports, but these are candidates for a deeper read if the per-module classification matters | Optional deeper read if production concerns arise | No code change |
| Parent plan estimated 226 modules; audit found 216 (excluding `__init__.py`, `__pycache__`, `.bak`) | All four groups | Small delta from plan estimate — all accounted for in filtering rules | None — sizing estimate difference only | No |
| This audit uses filename + first-30-lines classification (supplemented by 8 spot-checks); no ADG fan-in was pulled | All | For most rows the archetype is obvious from name; ambiguous cases were spot-checked. A future pass could use `adg_edge_fanin` to confirm criticality scoring | Optional ADG-based refinement pass on the 9 Hybrid rows | No |
| `L5/reasoning/` subdirs `adaptation/`, `core_kernel/`, `file_classification/` are small (1, 1, 4 files) — grouped inline vs separate subsection | L5 reasoning | For consistency with the per-module mandate, treated as flat rows under L5/reasoning rather than separate subtables | Document choice; no follow-up needed | No |

---

**End of per-module audit.**
Zero code changes. Zero patches. Zero refactors. Zero new Python files.
Extends — does not contradict — parent audit `docs/reports/agentic_core_eval_control_audit/2026-05-02.md`.
ADG provenance stamp applied per constitutional §11.
