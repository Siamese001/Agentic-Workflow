# December 2025 → Current apps_rg Agent Comparison

## HISTORICAL_COMMIT_SOURCE

- **SHA**: `5b443166b24379ba09c843ed59474c0800e26f4e`
- **Date**: 2025-12-31T21:52:33-05:00
- **Confidence**: **HIGH**

## Structural delta

| Dimension | Dec 2025 | Current (May 2026 HEAD) |
|-----------|----------|-------------------------|
| Entry | `resume_engine` + `autonomous/` swarm | `python -m apps_rg` → `canonical_dispatch` |
| Layout | `apps_rg/engines/resume_engine/` (~104 py) | `apps_rg/runtime/` section lanes (~560 files) |
| Generation | Gemini via `ResumeAgent.call_llm` | `qwen_vllm_provider` + section lanes |
| Validation | In-agent `record_pass` / signals | `validators/*_x2.py` deterministic gates |
| Healing | `HealingOrchestrator` multi-cycle | E4 same-authority section repair policies |
| Proof | Ad-hoc results on context | `runtime_proof_layout`, X1D/X2/X3 receipts |

## Mapping table

| Old behavior | Governed owner today | Status |
|--------------|---------------------|--------|
| ResumeAgent swarm + HealingOrchestrator | Section lanes + E4 repair + X2 gates + Exit/X3 | SUPERSEDED_BY_SECTION_LANE |
| RGPlanner K1-K8 pipeline plan | l2_recipe/modular_resume_generation + domain_contract | REPLACED_BY_CANONICAL_RUNTIME |
| Gemini GenerativeModel in ResumeAgent.call_llm | qwen_vllm_provider + APPS_RG judge pins | DO_NOT_RESTORE |
| DispatchResumeTools / Titanium RAG | C0 retrieval + apps_rg cache (r1b) | NEEDS_DECISION |
| test_resume_logic_mock.py | pytest harness (APPS_RG_TEST_HARNESS) | KEEP_AS_TEST_FIXTURE |

## TOP_10_OLD_AGENTS (material)

1. `HealingOrchestrator` — autonomous multi-cycle heal
2. `UnifiedOrchestrator` — Phase 6 intelligence routing
3. `ResumeAgent` + specialized validators — swarm execution
4. `RGPlanner` — K1–K8 pipeline planning
5. `ResumeOrchestrator` — hop workflow
6. `ConversationalRepair` — LLM gitops repair
7. `ResumeGenerator` / Gemini — direct synthesis
8. `DispatchResumeTools` — Titanium dispatch
9. `StrategicPlanner` / `ReflectionAgent` — plan/learn in-agent
10. `test_resume_logic_mock` — mock product path

## TOP_10_CURRENT_REPLACEMENTS

1. `apps_rg/__main__.py` — canonical CLI
2. `runtime/orchestration/canonical_dispatch.py`
3. `runtime/sections/*_lane.py` — modular section lanes
4. `runtime/providers/qwen_vllm_provider.py`
5. `runtime/validators/*_x2.py`
6. `runtime/judges/*` + `APPS_RG_*_JUDGE_MODEL_*`
7. `runtime/sections/*_repair_policy.py` — E4 repair
8. `runtime/runtime_proof_layout.py`
9. `l2_recipe/modular_resume_generation.py`
10. `runtime/bindings/exit_binding.py` — Exit handoff

## TOP_10_RISKS (if legacy reintroduced)

- ROUTE_AUTHORITY_DRIFT
- DIRECT_MODEL_BYPASS
- SAME_AUTHORITY_HEALING_VIOLATION
- MOCK_AS_PRODUCT_PROOF
- PROVIDER_SUBSTITUTION_RISK
- EXIT_X3_BYPASS
- EVIDENCE_AUTHORITY_DRIFT

## NEEDS_DECISION

- Whether apps_rg/reasoning/Rg* classes remain or move to quarantine
- Historical Titanium dispatch_resume_tools vs current C0 retrieval

## LESSONS_LEARNED

The old model optimized for **agent autonomy and fast local iteration**. The governed model optimizes for **bounded execution, single Exit disposition, and pinned providers**. Keep Dec 2025 artifacts as historical reference only; do not treat mocks or orchestrators as product proof.
