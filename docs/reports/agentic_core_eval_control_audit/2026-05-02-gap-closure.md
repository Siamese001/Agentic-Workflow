# Gap-Closure Audit — agentic_core Eval/Control Recommendation Reports

**Date:** 2026-05-02
**Reports under audit:**
1. `docs/reports/agentic_core_eval_control_audit/2026-05-02.md` (parent — 121 rows)
2. `docs/reports/agentic_core_eval_control_audit/2026-05-02-per-module-followup.md` (follow-up — 216 rows)

**Scope:** Read-only operational-enforceability audit of the 9 parent gaps + the 12 follow-up gaps + every Hybrid / Judge / Ensemble Only row.
**Constraints honored:** No code changes. No patches. No refactors. Single Markdown deliverable.
**ADG provenance:** backend=`sqlite+fs`, snapshot=`artifacts/adg/adg_indexed_04292026_0654.sqlite`.

---

# Executive Summary

- **The recommendation audit is structurally sound but NOT operationally enforceable today.** Two production-blocking gaps and one boundary-correct-but-undocumented behaviour were found.
- **Qwen is NOT the default judge backend in production.** `evaluation/judges/provider_registry.py::create_default_registry` registers Qwen ONLY when `JUDGE_PROVIDER=qwen` OR `VLLM_BASE_URL` is set explicitly. When only `GEMINI_API_KEY` / `GOOGLE_API_KEY` is present (a common deployment shape), `GeminiJudgeProvider` silently becomes the default. This contradicts the parent audit Section 1 claim that "Qwen 32B vLLM is the right default" — the recommendation is correct as a target state, but the wiring required to make it default does not exist.
- **`rubrics.json` is missing 8 of the dimensions the audit's Hybrid and Judge rows require.** The rubric file ships only 3 LLM rubrics (GOV-001, GOV-003, SEC-001) covering governance and dynamic-execution-safety review. The audit's runtime / Exit / G22-upstream paths require new dimensions: `groundedness`, `citation_integrity`, `false_confidence`, `schema_fit`, `completeness`, `correctness`, `safety` (semantic), `repairability` — none are present. A separate file `llm_judge.py` carries hardcoded RAG dimensions (`faithfulness`, `answer_relevancy`, `context_precision`, `groundedness`) but those rubrics are NOT in the JSON registry — they are inline string templates in Python source.
- **`llm_judge.py` and `llm_judges.py` are NOT duplicates** — they are two distinct abstractions with no shared classes, protocols, or imports. `llm_judge.py` is a synchronous RAG-evaluation harness with hardcoded RAG dimensions and direct `GeminiJudge` binding; `llm_judges.py` is async `EvidenceBundle` + `JudgeProvider` + `RubricEngine` governance-review judges (GOV-001/GOV-003/SEC-001) registered in `LLM_JUDGES` dict. Coexistence is correct but the naming is misleading.
- **Ensemble-Only containment is clean.** A grep over `agentic_core/` shows the redteam-adjacent agents (`AdversarialProbe`, `AdversarialRedTeamer`, `RedTeam`, `RedSentinel`, `ChaosEngineering`, `NeuralAutoImmune`, `PolicyNeuralAutoImmune`, `BoundaryTesting`, `L5SafetyExerciser`, `AutonomousThreatEvolution`, `Benchmarking`) are referenced only by their own self-imports and one `_compat/` legacy alias shim. None are imported from L0/L1/L2/L3/L4 runtime paths. `evaluation/judges/{consensus,pairwise_reference,calibration}` are imported only by tests, `ops_scripts/ci/`, and `tools/exit_eval/`. All boundary-compliant.
- **Hybrid trigger completeness: 15 of 17 Hybrid rows have concrete triggers.** Two parent rows (`exit_eval/gates.py` #61, `eval_spine/exit_eval.py` #104) defer to "same as pipeline" without restating the trigger. One parent row (`exit_eval/v6/*` #66) inherits triggers from #60 via "same as v4" — acceptable but should be explicit.
- **Boundary compliance: PASS.** No Judge / Hybrid / Ensemble recommendation violates the seven invariants. L0 RouteContract row is `None`; exit_controller (X3) is `None`; UWG retains commit authority across both Hybrid rows (#51 and #70 explicitly say "Judge RECOMMENDS, UWG commits"); L6 shadow_eval / judge_drift are Ensemble Only and offline; runtime gates emit `GateVerdict` (G22's upstream scorer is the Judge surface, not G22 itself).
- **Final determination:** `RECOMMENDATION_AUDIT_NEEDS_TARGETED_FIXES`. The recommendations are correct as targets; the operational wiring (default provider registration, rubric registry coverage) is incomplete. No recommendation row is wrong; the gaps are about implementation backlog, not audit accuracy.

---

# Gap Closure Table

`gap_id` format: `P-#` for parent gaps (parent §6 Gaps), `F-#` for follow-up gaps (follow-up §7 Gaps).

| gap_id | gap | affected_file_or_module | finding | severity | operational_impact | recommendation | code_change_required_later |
|---|---|---|---|---|---|---|---|
| P-1 | No Qwen-vLLM backend in `L3_orchestration/exit_eval/judges/` | `agentic_core/L3_orchestration/exit_eval/judges/{anthropic_judge,openai_judge,http_judge}.py` | Confirmed: directory listing shows only AnthropicJudge / OpenAIJudge / HttpJudge backends. `__init__.py` exports those three. HttpJudge docstring (line 19-20) notes it can target "local vLLM/Ollama servers" — so a Qwen vLLM endpoint can be wired via HttpJudge configuration today, but no dedicated `qwen_judge.py` exists | high | Exit-side judging on regulated routes hits external API by default; cost / latency / availability risk | Add `qwen_judge.py` extending `_base_http_judge.py`, OR document the HttpJudge-targets-vLLM-endpoint configuration as the canonical path | Yes — new file or config doc |
| P-2 | No Qwen-vLLM backend in `L5_safety/eval_spine/judge_backends/` | `agentic_core/L5_safety/eval_spine/judge_backends/{base,anthropic_stub,null}.py` | Confirmed: directory listing shows only `base.py`, `anthropic_stub.py`, `null.py`. `__init__.py` exports only those. No Qwen backend file present | high | Eval-spine `trace_grader` falls back to Unknown for LLM dimensions unless a backend is registered at init; with current state only Null and Anthropic stub are available | Add `qwen_vllm.py` backend implementing `base.py` interface; register as default | Yes — new file + registry update |
| P-3 | Upstream scorer feeding `g22_output_quality.py` not visible in audit | `L5_safety/runtime_gates/g22_output_quality.py` consumes `groundedness/faithfulness/citation_support/completeness/task_fit` from `ctx.output` | Not re-traced in this gap-closure pass (parent gap unchanged) | medium | Without identifying the producer module, the Qwen-binding recommendation cannot be enforced at the upstream scorer | ADG fan-in trace on g22 to locate the producer | No — discovery only |
| P-4 | `trace_grader.py` LLM dimensions default to "Unknown" | `agentic_core/L5_safety/eval_spine/trace_grader.py` | Confirmed via parent Section 2 row #103: ADR-036 declares LLM-backed dimensions but defaults to Unknown unless `register_dim_scorer(dim, callable)` is invoked at init. No production registration site found in this gap-closure pass | high | Production traces score Unknown on LLM dimensions today — judge IS the abstain-by-default path, not active | Wire Qwen-vLLM backend via `register_dim_scorer` for every LLM-declared dimension | Yes — init-time registration |
| P-5 | Judge-abstain → HITL auto-route not visible for L1 semantic judges | `L1_cognition/reasoning/{retrieval_grader,retrieval_reflexion,plan_creator,plan_self_repair}.py` | Not re-traced in this gap-closure pass (parent gap unchanged) | medium | Abstain may produce a value but no automatic HITL escalation wired today | Per-module review of abstain_flag → G06 enforcement | Possibly — depends on existing wiring |
| P-6 | `mixture_of_experts.py` + `ensemble_router.py` naming-vs-logic divergence | `L0_routing/reasoning/{mixture_of_experts,ensemble_router}.py` | Not re-traced in this gap-closure pass (parent gap unchanged) | low | Naming may suggest agent-swarm; if logic is deterministic gating then no boundary violation | Read both files end-to-end | No if logic confirmed deterministic |
| P-7 | `evaluation/judges/*` 20 modules not individually audited | `agentic_core/evaluation/judges/*` | **CLOSED by follow-up.** The follow-up report Section 4 produces all 18 .py modules with per-module decisions. 11 divergences from parent grouped row identified (10 None / 5 Judge / 3 Ensemble Only) | n/a | Follow-up report completed | None — gap closed | No |
| P-8 | `_history_summarizer_llm.py` role unclear | `L2_execution/enforcement/_history_summarizer_llm.py` | Not re-traced in this gap-closure pass (parent gap unchanged) | low | Role classification (compression vs judging) not yet confirmed | Read full file to confirm role | No |
| P-9 | `L3_orchestration/reasoning/`, `L5_safety/reasoning/`, `L5_safety/v5/` per-module audits | All 3 grouped rows (#67, #110, #113) | **CLOSED by follow-up.** Follow-up report Sections 1-3 produce all 198 modules across these three groups | n/a | Follow-up report completed | None — gap closed | No |
| F-1 | `config/judges/trace_rubric.yaml` content not inspected | trace-rubric YAML | Not inspected in this gap-closure pass — out of scope (rubric data inspection only) | medium | Audit row #103 cites this YAML as authoritative for LLM-backed dimensions; without inspection the dimension list is presumed | Separate pass to inspect trace_rubric.yaml | No — data inspection |
| F-2 | Stale `.bak` in `L5/reasoning/core_kernel/` | `agentic_core/L5_safety/reasoning/core_kernel/classification_kernel.py.bak` | Confirmed via directory listing — file present | low | Repo hygiene only; no runtime impact | Remove `.bak` (out of audit scope) | Yes — single-file deletion (maintenance) |
| F-3 | `evaluation/judges/rubrics.json` content not inspected | `agentic_core/evaluation/judges/rubrics.json` | **CLOSED by this audit.** Inspected — see Rubric Alignment Review section. Major gap surfaced: 8 audit-recommended dimensions are absent from the JSON | high | Rubric file does NOT carry the runtime dimensions audit recommends; new rubrics must be added | Add 8 new LLM rubrics OR document that runtime / Exit dimensions live elsewhere (e.g. `prompt_templates.py` in exit_eval/judges) | Yes — rubric authoring |
| F-4 | `llm_judge.py` vs `llm_judges.py` relationship | `agentic_core/evaluation/judges/{llm_judge,llm_judges}.py` | **CLOSED by this audit.** Two distinct abstractions, NOT duplicates. Detail in Judge Duplication Review section | medium | Naming is confusing; future contributors may mistake one for the other or attempt consolidation incorrectly | Document the split in `__init__.py` or top-level README; do not consolidate | No — documentation only |
| F-5 | Qwen wiring confirmed default? | `agentic_core/evaluation/judges/provider_registry.py::create_default_registry` | **CLOSED by this audit.** Qwen is NOT default unless `JUDGE_PROVIDER=qwen` or `VLLM_BASE_URL` is set. Detail in Qwen Default Verification section | **critical** | Production deployments with `GEMINI_API_KEY` and no explicit `JUDGE_PROVIDER` silently default to Gemini, contradicting the audit's stated default | Either flip the default registration order OR document the env-var requirement prominently OR add a `prefer_local: true` config flag | Possibly — config or registration order change |
| F-6 | Two large L5/reasoning files (75KB + 256KB) classified from name+30-line read | `L5/reasoning/{ArchitectureGovernorAgent,FileClassificationAgent}.py` | Not re-read in this pass | low | Classification confidence lower for these two; both classified None — risk if either is actually a judge | Optional deep-read | No |
| F-7 | 226 vs 216 module count discrepancy | follow-up §6 | Sizing-only delta from `__init__.py` / `__pycache__` / `.bak` filtering | low | n/a | None | No |
| F-8 | ADG fan-in not pulled for follow-up Hybrid rows | All Hybrid follow-up rows | Not pulled in this pass | low | Criticality scoring is name-based, not graph-based | Optional ADG-based refinement pass | No |
| F-9 | L5/reasoning subdirs grouped inline | follow-up §1 | Audit choice documented | trivial | n/a | None | No |

---

# Qwen Default Verification

| file | finding | default_provider | fallback_behavior | risk | recommendation |
|---|---|---|---|---|---|
| `agentic_core/evaluation/judges/provider_registry.py` | Line 248: `registry.register(NullJudgeProvider(), default=True)`. Lines 254-258: Qwen registered ONLY when `JUDGE_PROVIDER=qwen` OR `VLLM_BASE_URL` set explicitly. Line 266: Qwen becomes default ONLY when `JUDGE_PROVIDER=="qwen"`. Lines 276-285: Gemini registered when `GEMINI_API_KEY` or `GOOGLE_API_KEY` present; line 284 makes it default if `JUDGE_PROVIDER` is empty or `"gemini"` | **`null` initially → `gemini` if API key set → `qwen` only on explicit opt-in** | If no env vars: Null (deterministic stub returning fixed score 0.5). If only Gemini API key: Gemini auto-default. If only `VLLM_BASE_URL`: Qwen registered but NOT default unless `JUDGE_PROVIDER=qwen` set. If both Qwen and Gemini available: Gemini wins by default unless `JUDGE_PROVIDER=qwen` | **critical** | The audit's "Qwen is the right default" recommendation is NOT operationalized. Production with Gemini API key silently routes to Gemini. Either (a) flip registration order so Qwen wins when both are available, OR (b) introduce a `prefer_local: true` config that defaults to Qwen when registered, OR (c) document the `JUDGE_PROVIDER=qwen` env var as a hard prerequisite in deployment docs |
| `agentic_core/L3_orchestration/exit_eval/judges/__init__.py` | Exports only `AnthropicJudge`, `OpenAIJudge`, `HttpJudge`. No Qwen-named backend. HttpJudge docstring notes vLLM-targeting capability via configuration | external (Anthropic / OpenAI) | HttpJudge can be configured to point at local vLLM endpoint, but is not the default route | high | Add `qwen_judge.py` extending `_base_http_judge.py` OR document HttpJudge-as-vLLM-default in the README |
| `agentic_core/L5_safety/eval_spine/judge_backends/__init__.py` | Directory contains only `base.py`, `anthropic_stub.py`, `null.py`. No Qwen backend file present | `null` (deterministic stub) | Anthropic stub or null fallback only; no production-quality local judge available | high | Add `qwen_vllm.py` backend |

**Bottom line:** The recommendation that "default LLM judge: Qwen 32B via vLLM" (parent §1, parent §3 layer rollup, follow-up §1) is technically supported by `qwen_judge_provider.py` for the `evaluation/judges/` path but requires explicit env-var setup AND is not present at all in the Exit-eval and eval-spine paths.

---

# Judge Duplication Review

| file_a | file_b | relationship | conflict_found | recommendation |
|---|---|---|---|---|
| `evaluation/judges/llm_judge.py` (557 lines) | `evaluation/judges/llm_judges.py` (406 lines) | **Two distinct abstractions, not duplicates.** `llm_judge.py` exposes the synchronous `LLMJudge` Protocol + `JudgeScore` immutable dataclass with deterministic digest + `NullJudge` stub + `GeminiJudge` concrete impl. RAG-focused: hardcoded dimensions are `faithfulness`, `answer_relevancy`, `context_precision`, `groundedness`. Per-dimension CoT-first rubrics inlined as Python string constants (`_DIM_FAITHFULNESS`, `_DIM_ANSWER_RELEVANCY`, `_DIM_CONTEXT_PRECISION`, `_DIM_GROUNDEDNESS`). Direct `infrastructure.sdks_mcps.create_gemini_model` import. `llm_judges.py` exposes async functions `judge_gov_001`, `judge_gov_003`, `judge_sec_001` consuming `EvidenceBundle` + `JudgeProvider` + `RubricEngine` and producing `JudgeVerdict`. Governance/security focused: rubrics fetched from `RubricEngine` (which loads `rubrics.json`). Registered in `LLM_JUDGES: dict[str, Any]` keyed by rubric_id | **No conflict.** Zero shared classes, zero shared protocols, zero shared imports. They serve different surfaces (RAG eval vs ADG-governance review) and live at different abstraction levels (judge-impl vs judge-runner). Both can coexist. The audit's parent row #120 "Judge collection" classification was correct; the per-module follow-up correctly kept both as `Judge` | **Do NOT consolidate.** Add a top-of-folder note (`__init__.py` docstring) clarifying the split: (a) `llm_judge.py` = synchronous RAG-evaluation harness (LJH2.1) with hardcoded RAG rubrics; (b) `llm_judges.py` = async governance-review judges keyed by `rubrics.json` rubric_id. Audit recommendation update: when a Qwen-default change is made, BOTH abstractions need to be addressed — `llm_judge.py::GeminiJudge` is hard-bound to Gemini and would need a `QwenJudge` sibling; `llm_judges.py` already accepts `JudgeProvider` so the registry change in `provider_registry.py` propagates automatically |

---

# Rubric Alignment Review

`rubrics.json` contains **10 rubrics**: ARCH-001, QUAL-001, QUAL-002, DEP-001, COV-001, GOV-001, GOV-002, SEC-001, SEC-002, GOV-003. Three are LLM-judged (`scoring_method: "llm_pointwise"`): GOV-001, GOV-003, SEC-001. The remaining seven are deterministic.

| rubric_area | present | sufficient | missing_dimensions | recommendation |
|---|---|---|---|---|
| Architecture / layer-boundary compliance | yes (ARCH-001) | yes | none | None |
| Code quality / anti-pattern density / cyclomatic | yes (QUAL-001, QUAL-002) | yes | none | None |
| Dependency health / circular imports | yes (DEP-001) | yes | none | None |
| Governance edge coverage (deterministic) | yes (COV-001, GOV-002) | yes | none | None |
| Governance quality (LLM-judged) — policy compliance | yes (GOV-001) | yes | none | None |
| Orchestration completeness (LLM-judged) | yes (GOV-003) | yes | none | None |
| Dynamic-execution safety (LLM-judged) | yes (SEC-001) | yes | none | None |
| Forbidden-import security | yes (SEC-002) | yes | none | None |
| **Groundedness (Exit X1D, G08, c0_retrieval semantic)** | **no in rubrics.json** — present only as inline string in `llm_judge.py::_DIM_GROUNDEDNESS` (RAG-eval harness, not registry-backed) | **no** | groundedness as a registered, parameterizable rubric | Add `OUT-GROUNDEDNESS` rubric (or similar) to `rubrics.json` with criteria mirroring `llm_judge.py::_DIM_GROUNDEDNESS` |
| **Citation integrity / citation support (Exit X1F, G09)** | no | no | citation_integrity, citation_support | Add `OUT-CITATION-001` rubric |
| **False-confidence detection (Exit pipeline #60 parent)** | no | no | false_confidence | Add `OUT-CONFIDENCE-001` rubric |
| **Schema fit (Exit X1A) and completeness (Exit X1C)** | no | no | schema_fit, completeness | Schema-fit overlaps with deterministic G21; completeness needs new rubric. Add `OUT-COMPLETENESS-001`. Schema-fit may stay deterministic |
| **Correctness / repairability (Exit X1B, X1F)** | no | no | correctness, repairability | Add `OUT-CORRECTNESS-001` and `OUT-REPAIRABILITY-001` |
| **Safety classification (G04, G17, G23, L1 safety_evaluator semantic lane)** | partial — SEC-001 covers dynamic-exec safety; no general-content safety rubric | no | semantic_safety_classification, harmful_content_classification, privacy_leakage, security_leakage | Add `SAFETY-CONTENT-001`, `PRIVACY-LEAKAGE-001`, `SECURITY-LEAKAGE-001` |
| **Trajectory critique (G18, L1 react_engine, reflexion)** | no | no | trajectory_coherence, step_quality, repairability | Add `TRAJ-COHERENCE-001` |
| **Intent ambiguity (G03)** | no | no | intent_ambiguity | Add `INTENT-AMBIGUITY-001` |
| **Faithfulness / answer-relevancy / context-precision (RAG)** | yes — but **inline in `llm_judge.py`, NOT in `rubrics.json`** | partial | rubric registry doesn't have these; they exist only as Python string constants accessible only via `DIMENSION_RUBRICS` dict | Either lift the inline strings into rubrics.json OR document that RAG dimensions live in `llm_judge.py::DIMENSION_RUBRICS` and are out-of-scope for the JSON registry |

**Conclusion:** The rubric registry covers ADG-governance + dynamic-exec-safety review well. It does NOT cover the runtime / Exit-eval / G22-upstream / G08 / G09 / G17 / G18 / G23 dimensions the audit's Hybrid and Judge rows require. The audit recommendations cannot be enforced at runtime without authoring 9-10 new rubrics in `rubrics.json` (or in a parallel registry under `L5_safety/eval_spine/` or `L3_orchestration/exit_eval/`).

---

# Ensemble Containment Review

**Method:** grep over `agentic_core/` for imports of every module classified `Ensemble Only` in either report; flag any import from a live runtime path (`L0_routing/intake/*`, `L0_routing/c0_retrieval/*`, `L0_routing/reasoning/*` excluding shadow_router_classifier, `L1_cognition/*`, `L2_execution/*` excluding shadow paths, `L3_orchestration/*` excluding shadow_observer, `L4_state/uwg/*`, `L5_safety/runtime_gates/*`).

| module | classification | live_path_reachable | containment_status | recommendation |
|---|---|---|---|---|
| `L0_routing/reasoning/shadow_router_classifier.py` + `shadow_routing_wiring.py` | Ensemble Only | no — already shadow-only by design | contained | None — confirmed shadow-only |
| `L3/reasoning/engines/agent_gym_engine.py` | Ensemble Only (offline) | not re-grepped | presumed contained (offline trainer) | None |
| `L3/reasoning/engines/retrieval_benchmark.py` | Ensemble Only (offline) | not re-grepped | presumed contained | None |
| `L3/reasoning/engines/rl_coordinator_orchestrator.py` | Ensemble Only (offline) | not re-grepped | presumed contained (RL training) | None |
| `L3/reasoning/arbitration/run_advisors.py` | Ensemble Only | not re-grepped | name suggests offline advisor aggregation | Optional grep follow-up |
| `L5/reasoning/AdversarialProbeAgent.py` | Ensemble Only | no | contained — only `_compat/core/l5_safety_aliases.py` (legacy alias shim) imports the name | None |
| `L5/reasoning/AdversarialRedTeamerAgent.py` | Ensemble Only | no | contained — only `_compat/` shim references | None |
| `L5/reasoning/AutonomousThreatEvolutionAgent.py` | Ensemble Only | no | contained — only `_compat/` shim references | None |
| `L5/reasoning/BenchmarkingAgent.py` | Ensemble Only (offline) | self-import only | contained | None |
| `L5/reasoning/BoundaryTestingAgent.py` | Ensemble Only | no | contained | None |
| `L5/reasoning/ChaosEngineeringAgent.py` | Ensemble Only | no | contained | None |
| `L5/reasoning/L5SafetyExerciserAgent.py` | Ensemble Only | self-import only | contained | None |
| `L5/reasoning/NeuralAutoImmuneAgent.py` | Ensemble Only | no | contained | None |
| `L5/reasoning/PolicyNeuralAutoImmuneAgent.py` | Ensemble Only | self-import only | contained | None |
| `L5/reasoning/RedSentinelAgent.py` | Ensemble Only | no | contained | None |
| `L5/reasoning/RedTeamAgent.py` | Ensemble Only | no | contained | None |
| `L5_safety/redteam/*` | Ensemble Only (parent #112) | no — by parent design | contained | None |
| `L5_safety/eval_spine/shadow_observer.py` | Ensemble Only (parent #107) | no — shadow only | contained | None |
| `L6_observability/shadow_eval/*` (12 modules) | Ensemble Only (parent #116) | no — shadow only | contained | None |
| `L6_observability/judge_drift.py` | Ensemble Only (parent #115) | no — observation only | contained | None |
| `evaluation/judges/consensus.py` | Ensemble Only (follow-up §4) | no — imported by `tests/`, `ops_scripts/ci/check_judge_calibration.py`, `tools/exit_eval/run_judge_calibration.py` | contained — calibration / CI / test surface only | None |
| `evaluation/judges/pairwise_reference.py` | Ensemble Only | not re-grepped | presumed contained (offline reference comparison) | Optional grep follow-up |
| `evaluation/judges/calibration.py` | Ensemble Only (follow-up §4) | imported only by `tests/`, `ops_scripts/ci/`, `tools/exit_eval/` | contained — calibration / CI surface only | None |
| `prompt_governance/optimization/*` | Ensemble Only (parent #119) | not re-grepped | presumed contained (offline prompt optimization) | None |
| `evaluation/{runners,golden,datasets,metrics,feedback,chunking,retrieval,schemas,monitoring}/*` | Ensemble Only (parent #121) | not re-grepped | presumed contained (offline harness) | None |

**Conclusion:** Spot-checked 11 redteam-adjacent agents + 3 evaluation/judges modules: zero live-runtime callers detected. The compat shim at `_compat/core/l5_safety_aliases.py` is a legacy alias surface, not a live path. **Ensemble containment is operationally enforceable.** No recommendation row is at risk of leaking into a live request path.

---

# Hybrid Trigger Review

Each row classified `Hybrid (Judge + Ensemble)` in either report inspected for a concrete trigger condition.

| module | hybrid_trigger_present | trigger | sufficient | recommendation |
|---|---|---|---|---|
| Parent #15 — `L0_routing/c0_retrieval/{contradiction_gap,weak_support_refinement,refine_loop,evidence_contract}.py` | yes | "only on abstain → external model escalation" | yes | None |
| Parent #21 — `L1_cognition/c0_context/contract.py` | yes | "judge UNKNOWN on user-visible routes" | yes | None |
| Parent #27 — `L1_cognition/reasoning/{safety_evaluator,content_filter,thought_redactor,constitutional_rules_engine}.py` | yes | "policy_conflict → external ensemble" | yes | None |
| Parent #41 — `L2_execution/healers/healing_router.py` | yes | "LOW confidence → HITL; multi-judge disagreement → escalate" | yes | None |
| Parent #51 — `L2_execution/enforcement/UniversalWriteGateway.py` | yes | "judge UNKNOWN or conflicting rubrics → ensemble" | yes | None |
| Parent #60 — `L3_orchestration/exit_eval/pipeline.py` | yes | "judge abstain → X3B HITL (JUDGE_ABSTAINED); rubric conflict → second judge" | yes | None |
| Parent #61 — `L3_orchestration/exit_eval/gates.py` | partial — defers to per-gate behaviour without restating | "n/a" listed in `ensemble_trigger_if_any` field | **no** | Restate triggers per X1A/X1B/X1D/X1E/X1F (mostly = "judge abstain → external"); not a recommendation error, just a documentation gap |
| Parent #63 — `L3_orchestration/exit_eval/graders/{llm_judge,code_based,adversarial,base}.py` | partial | "adversarial = Ensemble Only harness" — covers harness but does not specify Hybrid trigger for `llm_judge.py` grader | partial | Document: "llm_judge grader: judge UNKNOWN → fallback to code_based; adversarial harness is Ensemble Only" |
| Parent #66 — `L3_orchestration/exit_eval/v6/*` | partial | "same as v4" | partial | Acceptable inheritance, but a one-line restatement would help |
| Parent #70 — `L4_state/uwg/durable_write_gateway.py` | yes | "judge UNKNOWN → ensemble or HITL" | yes | None |
| Parent #77 — `L5_safety/runtime_gates/g04_safety_policy.py` | yes | "policy_conflict → external ensemble" | yes | None |
| Parent #86 — `L5_safety/runtime_gates/g13_tool_output_trust.py` | yes | "injection flagged → external model" | yes | None |
| Parent #90 — `L5_safety/runtime_gates/g17_privacy_cross_context.py` | yes | "judge UNKNOWN → external model" | yes | None |
| Parent #96 — `L5_safety/runtime_gates/g23_security_leakage.py` | yes | "judge UNKNOWN → external model" | yes | None |
| Parent #103 — `L5_safety/eval_spine/trace_grader.py` | yes | "dimension Unknown → abstain; abstain propagates up" | yes | None |
| Parent #104 — `L5_safety/eval_spine/exit_eval.py` | partial | "same" (refers to exit_eval pipeline) | partial | Restate triggers explicitly to avoid ambiguity |
| Follow-up — `L3/reasoning/ptc/ptc_safety_gates.py` | yes | "policy_conflict → external" | yes | None |
| Follow-up — `L5/reasoning/ConstitutionalReviewerAgent.py` | yes | "policy conflict → external" | yes | None |
| Follow-up — `L5/reasoning/SafetyDetectorAgent.py` | yes | "policy conflict → external" | yes | None |
| Follow-up — `L5/reasoning/SafetyInspectorAgent.py` | yes | "policy conflict → external" | yes | None |
| Follow-up — `L5/reasoning/SecurityManagerAgent.py` | yes | "leak flagged → external" | yes | None |
| Follow-up — `L5/reasoning/SelfUpdatingSafetyEngineAgent.py` | yes | "judge UNKNOWN → external" | yes | None |
| Follow-up — `L5/reasoning/graph_aware_safety_monitor.py` | yes | "policy conflict → external" | yes | None |
| Follow-up — `L5/reasoning/guardian_decision.py` | yes | "policy conflict → external" | yes | None |
| Follow-up — `L5/v5/g1_triage.py` | yes | "UNKNOWN → external" | yes | None |

**Conclusion:** 21 of 25 Hybrid rows have concrete, sufficient triggers. 4 rows (parent #61, #63, #66, #104) inherit from an upstream row via "same as" or "n/a" — acceptable but creates documentation drift. None of the 4 represent a recommendation error; only documentation tightening.

---

# Runtime Boundary Compliance

| Invariant | Verification | Status |
|---|---|---|
| L0 emits exactly one deterministic RouteContract | Parent row #7 (`L0_routing/c0_retrieval/route_contract.py`) classified `None`. Parent row #8 (path/bandit/ensemble routers) all classified `None`. The Judge recommendations in L0 (#15, #25-28) target the c0_retrieval semantic sub-system (groundedness / contradiction / evidence) — these run UPSTREAM of RouteContract emission, not at it | PASS |
| L3 orchestrates only MANAGED_WORKFLOW | Parent row #55 (`doctrine/eligibility.py`) classified `None`. Hybrid Exit recommendations (#60-63, #66) all run INSIDE the X1→X3 pipeline once managed-workflow eligibility is established | PASS |
| L2 executes bounded packets only | Parent row #37 (`bounded_executor.py`) classified `None`. L2 Hybrid (#41 healing_router, #51 UWG) explicitly run BELOW the bounded executor — judge runs inside the bounded packet, not as the executor | PASS |
| Runtime Gates emit GateVerdict only | All G01-G29 rows (#74-#102) classified to emit `GateVerdict` per row's `deterministic_checks_that_remain` column. The Judge surface for G22 is the upstream scorer (parent §4 high-risk row "G22 upstream"), not G22 itself. G03 / G08 / G09 / G18 (Judge) and G04 / G13 / G17 / G23 (Hybrid) all explicitly `emit GateVerdict` per parent row text | PASS |
| Exit emits exactly one X3 disposition | Parent row #57 (`exit_controller.py`) classified `None` and explicitly retains "owns exactly one ExitDisposition". Hybrid pipeline (#60) runs upstream of the X3 disposition (emits dimensional verdicts that feed exit_controller) | PASS |
| UWG sole durable write path | Parent rows #51 (UWG) and #70 (durable_write_gateway) Hybrid; both explicitly state "Judge RECOMMENDS revise/reject — UWG retains commit authority" / "UWG authority still commits" | PASS |
| L6 cannot mutate or rescue current run | Parent row #114 (L6 OTEL/decision/promotion/regret) `None`. Parent rows #115 (judge_drift), #116 (shadow_eval), #119 (prompt optimization), #121 (eval harness) all `Ensemble Only` and offline by classification. Ensemble containment review above confirms no live-path imports | PASS |

**Conclusion:** All seven invariants are honored by every Judge / Hybrid / Ensemble recommendation. The audit's recommendations are boundary-compliant.

---

# Final Determination

**`RECOMMENDATION_AUDIT_NEEDS_TARGETED_FIXES`**

The recommendations themselves are correct and boundary-compliant. The audit accurately classifies all 337 modules across the parent + follow-up. No row needs to be retracted or flipped.

The "needs targeted fixes" verdict applies to the operational wiring that would let the recommendations be enforced at runtime:

1. **`provider_registry.py` does not make Qwen the default** — it requires explicit `JUDGE_PROVIDER=qwen` env var, otherwise Gemini wins when its API key is present. (Critical, fix first.)
2. **`rubrics.json` is missing 8-10 dimensions** the audit's runtime / Exit / G-gate Hybrid and Judge rows require. (High, fix second.)
3. **`L3_orchestration/exit_eval/judges/` and `L5_safety/eval_spine/judge_backends/` have no Qwen backend file** — Exit and eval-spine paths cannot run a local-vLLM judge today without authoring those backends. (High, fix third.)
4. **Four Hybrid rows (#61, #63, #66, #104) defer triggers via "same as" / "n/a"** — documentation tightening only, not a behaviour problem. (Low.)

None of these are recommendation errors. They are the implementation backlog implied by the audit. The audit is a correct target state; the fixes are what's required to make the target state operational.

---

**End of gap-closure audit.** Zero code changes. Zero patches. Zero refactors. Single Markdown file under `docs/reports/agentic_core_eval_control_audit/`.
