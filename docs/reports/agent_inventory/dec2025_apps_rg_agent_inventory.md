# December 2025 apps_rg Agent Inventory

## 1. HISTORICAL_COMMIT_SOURCE

- **commit_sha**: `5b443166b24379ba09c843ed59474c0800e26f4e`
- **commit_date**: 2025-12-31T21:52:33-05:00
- **branch/tag**: none
- **selection**: git log --before=2026-01-01T00:00:00 -1 (last commit in calendar Dec 2025). No Dec 2025 tags matched *2025*/*dec*/*apps_rg*. Read-only worktree: c:/Git/apps_rg_dec2025_review.
- **confidence**: HIGH
- **worktree**: `c:/Git/apps_rg_dec2025_review`
- **apps_rg files**: 112 total, 104 Python

## 2. DEC2025_AGENT_INVENTORY

**DEC2025_AGENT_COUNT**: 33 primary symbols (autonomous swarm + engine surface)

| Path | Symbol | Archetype | Models | Roles | Receipts | Current equivalent | Recommendation | Risks |
|------|--------|-----------|--------|-------|----------|-------------------|----------------|-------|
| `apps_rg/engines/resume_engine/debug_resume_test.py` | debug_resume_test | DEMO_OR_SMOKE_AGENT | - | test_mock | no | tests/unit/apps_rg/, tests.helpers.offline_lane_orchestration | KEEP_AS_TEST_FIXTURE | MOCK_AS_PRODUCT_PROOF |
| `apps_rg/engines/resume_engine/test_resume_logic_mock.py` | test_resume_logic_mock | DEMO_OR_SMOKE_AGENT | - | test_mock | no | tests/unit/apps_rg/, tests.helpers.offline_lane_orchestration | KEEP_AS_TEST_FIXTURE | MOCK_AS_PRODUCT_PROOF |
| `apps_rg/engines/resume_engine/dispatch_resume_tools.py` | DispatchResumeTools | DISPATCH_OR_ROUTER_AGENT | - | route | no | apps_rg/runtime/orchestration/canonical_dispatch.py | REPLACED_BY_CANONICAL_RUNTIME | - |
| `apps_rg/engines/resume_engine/autonomous/gitops.py` | ConversationalRepair | HEALER_OR_RECOVERY_AGENT | google_gemini | heal,model_call,orchestrate,validate | no | apps_rg/runtime/sections/*_repair_policy.py, section_repair_ledger.py (E | SUPERSEDED_BY_E2_E4 | DIRECT_MODEL_BYPASS,PROVIDER_SUBSTITUTION_RISK,ROUTE_AUTHORITY_DRIFT,SAME_AUTHORITY_HEALING_VIOLATION |
| `apps_rg/engines/resume_engine/autonomous/healing.py` | HealingOrchestrator | HEALER_OR_RECOVERY_AGENT | - | agent_execute,heal,judge,orchestrate,plan,route | no | apps_rg/runtime/sections/*_repair_policy.py, section_repair_ledger.py (E | SUPERSEDED_BY_E2_E4 | EVIDENCE_AUTHORITY_DRIFT,EXIT_X3_BYPASS,PROMPT_AUTHORITY_DRIFT,ROUTE_AUTHORITY_DRIFT |
| `apps_rg/engines/resume_engine/autonomous/healing.py` | SignalRouter | HEALER_OR_RECOVERY_AGENT | - | agent_execute,heal,judge,orchestrate,plan,route | no | apps_rg/runtime/sections/*_repair_policy.py, section_repair_ledger.py (E | SUPERSEDED_BY_E2_E4 | EVIDENCE_AUTHORITY_DRIFT,EXIT_X3_BYPASS,PROMPT_AUTHORITY_DRIFT,ROUTE_AUTHORITY_DRIFT |
| `apps_rg/engines/resume_engine/autonomous/healing.py` | AgentFactory | HEALER_OR_RECOVERY_AGENT | - | agent_execute,heal,judge,orchestrate,plan,route | no | apps_rg/runtime/sections/*_repair_policy.py, section_repair_ledger.py (E | SUPERSEDED_BY_E2_E4 | EVIDENCE_AUTHORITY_DRIFT,EXIT_X3_BYPASS,PROMPT_AUTHORITY_DRIFT,ROUTE_AUTHORITY_DRIFT |
| `apps_rg/engines/resume_engine/autonomous/agents.py` | ReflectionAgent | JUDGE_OR_EVALUATOR_AGENT | - | agent_execute,judge,plan,validate | no | apps_rg/runtime/judges/*, APPS_RG_*_JUDGE_MODEL_* | SUPERSEDED_BY_X2_X3 | EXIT_X3_BYPASS,PROMPT_AUTHORITY_DRIFT |
| `apps_rg/engines/resume_engine/autonomous/agents.py` | StrategicPlanner | PLANNER_AGENT | - | agent_execute,judge,plan,validate | no | apps_rg/l2_recipe/modular_resume_generation.py, domain_contract targetin | REPLACED_BY_CANONICAL_RUNTIME | EXIT_X3_BYPASS,PROMPT_AUTHORITY_DRIFT |
| `apps_rg/engines/resume_engine/resume_planner.py` | RGPlanner | PLANNER_AGENT | - | plan,validate | no | apps_rg/l2_recipe/modular_resume_generation.py, domain_contract targetin | REPLACED_BY_CANONICAL_RUNTIME | - |
| `apps_rg/engines/resume_engine/autonomous/gitops.py` | Phase4Orchestrator | RESUME_ORCHESTRATOR_AGENT | google_gemini | heal,model_call,orchestrate,validate | no | apps_rg/runtime/orchestration/canonical_dispatch.py, python -m apps_rg | REPLACED_BY_CANONICAL_RUNTIME | DIRECT_MODEL_BYPASS,PROVIDER_SUBSTITUTION_RISK,ROUTE_AUTHORITY_DRIFT,SAME_AUTHORITY_HEALING_VIOLATION |
| `apps_rg/engines/resume_engine/autonomous/governance.py` | Phase7Orchestrator | RESUME_ORCHESTRATOR_AGENT | - | heal,judge,orchestrate,validate | no | apps_rg/runtime/orchestration/canonical_dispatch.py, python -m apps_rg | REPLACED_BY_CANONICAL_RUNTIME | EXIT_X3_BYPASS,PROMPT_AUTHORITY_DRIFT,ROUTE_AUTHORITY_DRIFT |
| `apps_rg/engines/resume_engine/autonomous/intelligence.py` | UnifiedOrchestrator | RESUME_ORCHESTRATOR_AGENT | - | judge,orchestrate,validate | no | apps_rg/runtime/orchestration/canonical_dispatch.py, python -m apps_rg | REPLACED_BY_CANONICAL_RUNTIME | ROUTE_AUTHORITY_DRIFT |
| `apps_rg/engines/resume_engine/autonomous/intelligence.py` | Phase6Orchestrator | RESUME_ORCHESTRATOR_AGENT | - | judge,orchestrate,validate | no | apps_rg/runtime/orchestration/canonical_dispatch.py, python -m apps_rg | REPLACED_BY_CANONICAL_RUNTIME | ROUTE_AUTHORITY_DRIFT |
| `apps_rg/engines/resume_engine/orchestrate_resume.py` | ResumeOrchestrator | RESUME_ORCHESTRATOR_AGENT | - | judge,orchestrate,validate | no | apps_rg/runtime/orchestration/canonical_dispatch.py, python -m apps_rg | REPLACED_BY_CANONICAL_RUNTIME | ROUTE_AUTHORITY_DRIFT |
| `apps_rg/engines/resume_engine/autonomous/resume_base.py` | ResumeAgent | SECTION_GENERATOR_AGENT | google_gemini | agent_execute,model_call,validate | no | apps_rg/runtime/sections/*_lane.py + qwen_vllm_provider | SUPERSEDED_BY_SECTION_LANE | DIRECT_MODEL_BYPASS,EVIDENCE_AUTHORITY_DRIFT,EXIT_X3_BYPASS,PROVIDER_SUBSTITUTION_RISK |
| `apps_rg/engines/resume_engine/execute_resume_generation.py` | execute_resume_generation | SECTION_GENERATOR_AGENT | - | validate | no | apps_rg/runtime/sections/*_lane.py + qwen_vllm_provider | SUPERSEDED_BY_SECTION_LANE | DIRECT_MODEL_BYPASS |
| `apps_rg/engines/resume_engine/resume_generator.py` | ResumeGenerator | SECTION_GENERATOR_AGENT | google_gemini | model_call,test_mock,validate | no | apps_rg/runtime/sections/*_lane.py + qwen_vllm_provider | SUPERSEDED_BY_SECTION_LANE | DIRECT_MODEL_BYPASS,PROVIDER_SUBSTITUTION_RISK |
| `apps_rg/engines/resume_engine/autonomous/agents.py` | TemplateOptimizer | UNKNOWN | - | agent_execute,judge,plan,validate | no | NEEDS_DECISION | NEEDS_DECISION | EXIT_X3_BYPASS,PROMPT_AUTHORITY_DRIFT |
| `apps_rg/engines/resume_engine/autonomous/context.py` | ResumeEngineContext | UNKNOWN | google_gemini | heal,judge,model_call,validate | no | NEEDS_DECISION | NEEDS_DECISION | EVIDENCE_AUTHORITY_DRIFT,EXIT_X3_BYPASS,PROVIDER_SUBSTITUTION_RISK,UWG_L4_BYPASS |
| `apps_rg/engines/resume_engine/autonomous/context.py` | BudgetManager | UNKNOWN | google_gemini | heal,judge,model_call,validate | no | NEEDS_DECISION | NEEDS_DECISION | EVIDENCE_AUTHORITY_DRIFT,EXIT_X3_BYPASS,PROVIDER_SUBSTITUTION_RISK,UWG_L4_BYPASS |
| `apps_rg/engines/resume_engine/autonomous/gitops.py` | GitOpsManager | UNKNOWN | google_gemini | heal,model_call,orchestrate,validate | no | NEEDS_DECISION | NEEDS_DECISION | DIRECT_MODEL_BYPASS,PROVIDER_SUBSTITUTION_RISK,ROUTE_AUTHORITY_DRIFT,SAME_AUTHORITY_HEALING_VIOLATION |
| `apps_rg/engines/resume_engine/autonomous/governance.py` | PredictiveBudgetManager | UNKNOWN | - | heal,judge,orchestrate,validate | no | NEEDS_DECISION | NEEDS_DECISION | EXIT_X3_BYPASS,PROMPT_AUTHORITY_DRIFT,ROUTE_AUTHORITY_DRIFT |
| `apps_rg/engines/resume_engine/autonomous/learning.py` | ResumeLearningAgent | UNKNOWN | - | agent_execute,validate | no | NEEDS_DECISION | NEEDS_DECISION | - |
| `apps_rg/engines/resume_engine/autonomous/proactive.py` | ProactiveAgent | UNKNOWN | - | agent_execute,judge,validate | no | NEEDS_DECISION | NEEDS_DECISION | EVIDENCE_AUTHORITY_DRIFT,EXIT_X3_BYPASS |
| `apps_rg/engines/resume_engine/resume_engine.py` | resume_engine | UNKNOWN | google_gemini,openai,anthropic | judge,model_call,validate | no | NEEDS_DECISION | NEEDS_DECISION | PROVIDER_SUBSTITUTION_RISK |
| `apps_rg/engines/resume_engine/create_test_resume.py` | create_test_resume | UTILITY_SCRIPT | - | judge,test_mock | no | ops_scripts/apps_rg/, historical reference | HISTORICAL_REFERENCE_ONLY | MOCK_AS_PRODUCT_PROOF |
| `apps_rg/engines/resume_engine/autonomous/agents.py` | ContentQualityAgent | VALIDATOR_AGENT | - | agent_execute,judge,plan,validate | no | apps_rg/runtime/validators/*_x2.py | SUPERSEDED_BY_X2_X3 | EXIT_X3_BYPASS,PROMPT_AUTHORITY_DRIFT |
| `apps_rg/engines/resume_engine/autonomous/agents.py` | FactCheckAgent | VALIDATOR_AGENT | - | agent_execute,judge,plan,validate | no | apps_rg/runtime/validators/*_x2.py | SUPERSEDED_BY_X2_X3 | EXIT_X3_BYPASS,PROMPT_AUTHORITY_DRIFT |
| `apps_rg/engines/resume_engine/autonomous/agents.py` | BrandComplianceAgent | VALIDATOR_AGENT | - | agent_execute,judge,plan,validate | no | apps_rg/runtime/validators/*_x2.py | SUPERSEDED_BY_X2_X3 | EXIT_X3_BYPASS,PROMPT_AUTHORITY_DRIFT |
| `apps_rg/engines/resume_engine/autonomous/agents.py` | SectionBalanceAgent | VALIDATOR_AGENT | - | agent_execute,judge,plan,validate | no | apps_rg/runtime/validators/*_x2.py | SUPERSEDED_BY_X2_X3 | EXIT_X3_BYPASS,PROMPT_AUTHORITY_DRIFT |
| `apps_rg/engines/resume_engine/autonomous/agents.py` | ATSCompatibilityAgent | VALIDATOR_AGENT | - | agent_execute,judge,plan,validate | no | apps_rg/runtime/validators/*_x2.py | SUPERSEDED_BY_X2_X3 | EXIT_X3_BYPASS,PROMPT_AUTHORITY_DRIFT |
| `apps_rg/engines/resume_engine/autonomous/agents.py` | TestPilot | VALIDATOR_AGENT | - | agent_execute,judge,plan,validate | no | apps_rg/runtime/validators/*_x2.py | SUPERSEDED_BY_X2_X3 | EXIT_X3_BYPASS,PROMPT_AUTHORITY_DRIFT |

## 3. OLD_AGENT_ARCHETYPE_MAP

- **UNKNOWN**: 8
- **VALIDATOR_AGENT**: 6
- **RESUME_ORCHESTRATOR_AGENT**: 5
- **HEALER_OR_RECOVERY_AGENT**: 4
- **SECTION_GENERATOR_AGENT**: 3
- **PLANNER_AGENT**: 2
- **DEMO_OR_SMOKE_AGENT**: 2
- **JUDGE_OR_EVALUATOR_AGENT**: 1
- **DISPATCH_OR_ROUTER_AGENT**: 1
- **UTILITY_SCRIPT**: 1

## 4. RISK_ASSESSMENT_AGAINST_CURRENT_SPINE

See per-row `risks` in JSON. Dominant classes if old agents were reactivated:
- **ROUTE_AUTHORITY_DRIFT** — `UnifiedOrchestrator`, `HealingOrchestrator`, `ResumeOrchestrator` route multi-hop flows without spine E1–E5 packets.
- **DIRECT_MODEL_BYPASS** — `ResumeAgent.call_llm` / `resume_generator` call Gemini directly.
- **SAME_AUTHORITY_HEALING_VIOLATION** — `HealingOrchestrator` re-runs validator agents cross-signal without bounded E4 scope.
- **EXIT_X3_BYPASS** — agents record pass/fail on shared context, not Exit→single X3.
- **MOCK_AS_PRODUCT_PROOF** — `test_resume_logic_mock`, `debug_resume_test`, `create_test_resume`.

## 5–6. CURRENT_EQUIVALENT / KEEP_OR_ARCHIVE

Encoded per inventory row (`current_equivalent`, `recommendation`). Default for autonomous subtree: **HISTORICAL_REFERENCE_ONLY** / **DO_NOT_RESTORE**.

## 7. LESSONS_LEARNED

December 2025 `apps_rg` experimented with a **ResumeAgent swarm**: shared `ResumeEngineContext`, signal-driven healing cycles, and embedded Gemini calls. That accelerated iteration but **merged plan, route, execute, heal, judge, and model access** inside the app without L2 packet boundaries, Exit, or UWG.

The governed model delegates durable authority to the spine; product proof is `python -m apps_rg` + section lanes + X2/X3 + pinned judges — not autonomous orchestrators or mocks.

## EXPLICIT_NON_CLAIMS

- Historical grep/worktree inventory does not prove current runtime reachability.
- Old mock/smoke/demo paths are not product proof.
- No code was restored, deleted, or migrated in this review.
