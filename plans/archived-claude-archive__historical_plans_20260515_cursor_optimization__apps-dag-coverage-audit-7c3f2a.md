---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\apps-dag-coverage-audit-7c3f2a.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\apps-dag-coverage-audit-7c3f2a.md'
source_sha256: b075aec5a5f4e9733db60782e6b3eac03f4d13c3071b36b7eb72d890c3215e82
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# apps_* DAG Coverage, Optimization & Hop-Gating Audit

**Type**: Audit (read-only, tables only — no code, no edits, no implementation).
**Scope**: All `apps_*` domain producers + `apps_shared` chassis.
**Constraint anchors**: ADR-079 (L2 graph-layer consumption), ADR-080 (Phase D design), constitutional §22 (graph-layer primary), shared substrate `apps_shared.orchestration.HopPipelineExecutor`.
**Mode**: `analyze` only. Output is exclusively the seven required tables.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | P1.1 | Inventory `apps_*` directories, hop_pipeline registries, route specs, integration adapters | ~3k | All apps land hop topology in `apps_<name>/config/hop_pipeline.py` or are registry-less | DONE | Every `apps_*` has a row in Table 1 |
| W2 | P2.1 | Apply DAG-required test (≥2 bounded steps + ordered deps / fan-in / gate / HITL / staged validation) per app | ~2k | Definition from user prompt is authoritative | DONE | Each app gets a binary DAG-required verdict with defense (Table 2) |
| W3 | P3.1 | Per-hop gating recommendation (None / Judge / Ensemble / Hybrid) + defense + alternatives rejection | ~5k | Hop names + I/O contracts taken verbatim from `_STAGE_SPECS` blocks | DONE | Every hop in every existing or recommended DAG appears in Table 3 |
| W4 | P4.1 | Optimization findings per DAG (layer ownership, hop fusion, missing gates, observability) | ~2k | Severity P0 = architecture violation; P1 = correctness gap; P2 = duplication; P3 = polish | DONE | Each existing DAG has ≥1 row in Table 4 OR explicit "no findings" row |
| W5 | P5.1 | Shared chassis opportunities + missing-evidence register + final recommendation | ~2k | `apps_shared.orchestration` is the chassis SSOT | DONE | Tables 5–7 complete |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| P1.1 | Inventory pass | `apps_*/config/hop_pipeline.py` (×7), `apps_qna/builder/*`, `apps_qna/router/*`, `apps_shared/orchestration/hop_pipeline.py` | apps_qna and apps_underwriting_ai diverge from the other six in shape | ~3k | DONE |
| P2.1 | DAG-required test | Same as P1.1 | Decision boundary is "≥2 bounded L2 steps with ≥1 dependency-graph property" | ~2k | DONE |
| P3.1 | Per-hop gating | Hop specs from each `_STAGE_SPECS` | Judge-vs-Ensemble-vs-Hybrid line is rubric-driven; Hybrid reserved for high-stakes durable artifacts | ~5k | DONE |
| P4.1 | Optimization | Existing DAG locations | apps_lic 9-stage and apps_rg 7-stage are largest blast-radius targets | ~2k | DONE |
| P5.1 | Chassis + recs | `apps_shared/orchestration/`, `apps_shared/enforcement/` | Cross-app retrieval / judge / gate hops are duplicated and belong in chassis | ~2k | DONE |

## Gap Register

| Gap | Detail |
|-----|--------|
| L0 RouteContract per-app mapping | Constraint §3 references `RouteContract.execution_form = MANAGED_WORKFLOW` but no per-app routing decision file was located in `agentic_core/L0_routing/`. Scored as NOT FOUND in Table 6. |
| L3 step contract for these DAGs | The existing substrate is `apps_shared.orchestration.HopPipelineExecutor`. No `L3StepContract` adapter found wiring substrate runs to `agentic_core/L3_orchestration/`. Scored in Tables 4 + 6. |
| UWG write-path on each terminal hop | Substrate executor has no UWG hook surface. Scored in Tables 4 + 6. |

---

## Table 1 — apps_* DAG coverage summary

| apps_* | domain purpose | observed route/workflow shape | DAG required? | DAG found? | DAG location | optimized? | verdict | evidence |
|--------|----------------|-------------------------------|---------------|------------|--------------|------------|---------|----------|
| apps_eval | Evaluation lab — scenario runs, scorecards, judge verdicts, regression detection | 6 ordered stages with retrieval → run → score → judge → regress → HITL-quality | YES | YES | `apps_eval/config/hop_pipeline.py` (`REGISTRY`, 6 stages) + `apps_eval/reasoning/EvalOrchestrator.py` (imperative primary) | PARTIAL | DAG present but dual-path (substrate is "additive", imperative remains primary) | `apps_eval/config/hop_pipeline.py:26-81` declares 6 `HopStageSpec`; docstring confirms imperative is primary |
| apps_exec | Executive brief generator — ingest → retrieve prior → extract capability → assemble brief | 4 ordered stages, fan-in at assembly | YES | YES | `apps_exec/config/hop_pipeline.py` (`REGISTRY`, 4 stages) | PARTIAL | DAG present, additive only — `BaseExecEngine` runtime remains primary | `apps_exec/config/hop_pipeline.py:19-61`; docstring "additive" |
| apps_lic | LinkedIn outreach campaign — profile analysis → research → grounding → routing → generation → validation → gate → QA → integration | 9 ordered stages with explicit gate at stage 7 | YES | YES | `apps_lic/config/hop_pipeline.py` (`REGISTRY`, 9 stages) + `apps_lic/integrations/governed_lic_run.py` outer chain | PARTIAL | DAG present + gate stage present; substrate is SSOT per Author-Gate 2026-05-01 | `apps_lic/config/hop_pipeline.py:29-117`; gate flag at stage 7 (`gate=True`) |
| apps_qna | Q&A pack lifecycle — pack build, route selection, paste-set composition, promotion | NOT a multi-step generation DAG; lifecycle of pack artifacts (build, lint, self-eval, promotion) routed by `paste_bandit` / `route_bandit` | NO | N/A | NOT FOUND — no `apps_qna/config/hop_pipeline.py`; `apps_qna/builder/card_pack_builder.py` + `apps_qna/router/*.py` are the surface | N/A | Correctly DAG-less; this is a registry-and-bandit surface, not a managed workflow | `apps_qna/builder/card_pack_builder.py`, `apps_qna/router/{paste_bandit,route_bandit,semantic_router,promotion_gates}.py` (no hop_pipeline.py present) |
| apps_research | Autonomous research — retrieve prior research → company brief → assemble final artifact | 3 ordered stages, fan-in at assembly | YES | YES | `apps_research/config/hop_pipeline.py` (`REGISTRY`, 3 stages) | PARTIAL | DAG present, additive only — imperative `BaseResearchEngine` primary | `apps_research/config/hop_pipeline.py:22-49`; docstring "additive" |
| apps_rfp | RFP / proposal generator — ingest RFP → retrieve similar prior proposals → assemble proposal | 3 ordered stages, fan-in at assembly | YES | YES | `apps_rfp/config/hop_pipeline.py` (`REGISTRY`, 3 stages) | PARTIAL | DAG present, additive only — `BaseRfpEngine` primary | `apps_rfp/config/hop_pipeline.py:19-46`; docstring "additive" |
| apps_rg | Resume generation — clerk extraction → enrichment → generation → fact-check → diversity gate → optimizer → diagnostics | 7 ordered stages with explicit gate at stage 5 | YES | YES | `apps_rg/config/hop_pipeline.py` (`REGISTRY`, 7 stages) + `apps_rg/reasoning/RgResumeOrchestrator.py` 606-line imperative path remains primary | PARTIAL | DAG present + gate stage present; substrate additive | `apps_rg/config/hop_pipeline.py:32-96`; gate flag at stage 5 (`gate=True`) |
| apps_underwriting_ai | Underwriting decision pipeline — initialize evidence → reconcile docs → derive features → collect evidence → assemble decision | 5 ordered stages, fan-in at decision packet | YES | YES | `apps_underwriting_ai/config/hop_pipeline.py` (`REGISTRY`, 5 stages) | PARTIAL | DAG present, additive only — `UnderwritingEngine.run()` primary | `apps_underwriting_ai/config/hop_pipeline.py:22-72` |
| apps_shared | Chassis — `HopPipelineExecutor`, `HopRegistry`, `HopStageSpec`, app guardian registry | NOT an app — chassis substrate consumed by all apps | N/A (chassis) | N/A (chassis) | `apps_shared/orchestration/hop_pipeline.py` (substrate, not a DAG) | N/A | Correctly DAG-less; chassis only | `apps_shared/orchestration/hop_pipeline.py:121-262` (HopStageSpec/HopRegistry/HopPipelineExecutor) |

## Table 2 — DAG requirement defense

| apps_* | why DAG is required or not required | managed workflow criteria met | single-step/terminal risk | final DAG requirement decision |
|--------|--------------------------------------|-------------------------------|---------------------------|--------------------------------|
| apps_eval | 6 bounded steps with ordered deps (retrieval feeds runner, scorecard feeds judge + regression, all feed HITL quality); staged validation; multi-artifact merge before Exit | ordered deps; fan-in at HITL-quality; staged validation; multiple artifacts merged | LOW — workflow is genuinely multi-stage | REQUIRED |
| apps_exec | 4 bounded steps with ordered deps; ingestion + retrieval + extraction must merge at assembly (fan-in) | ordered deps; fan-in at assembly; evidence gathering before generation | LOW | REQUIRED |
| apps_lic | 9 bounded steps with explicit gate at stage 7 (gate_decision); proposed durable mutation at stage 9 (integration); evidence gathering before generation | ordered deps; gate; staged validation; durable mutation after generation | NEGLIGIBLE | REQUIRED |
| apps_qna | Surface is "build pack at offline time, route at request time, score promotion at calibration time" — these are separate trigger contexts, not one managed workflow. Pack build is a build-time pipeline (not L3 runtime); route selection is single-shot bandit call; promotion is a calibration job | NONE met for runtime path | HIGH if forced into L3 — single-step bandit lookup MUST NOT be wrapped as MANAGED_WORKFLOW per constraint §4 | NOT REQUIRED |
| apps_research | 3 bounded steps; retrieval feeds brief feeds assembly (ordered deps + fan-in) | ordered deps; evidence gathering before generation; fan-in | LOW | REQUIRED |
| apps_rfp | 3 bounded steps; ingestion feeds retrieval feeds assembly | ordered deps; evidence gathering before generation; fan-in | LOW | REQUIRED |
| apps_rg | 7 bounded steps with diversity gate at stage 5; multi-section merge at optimizer; staged validation via fact-check + gate + diagnostics | ordered deps; gate; staged validation; multi-artifact merge | NEGLIGIBLE | REQUIRED |
| apps_underwriting_ai | 5 bounded steps; reconciliation + features + evidence merge at decision packet (fan-in); proposed durable mutation at terminal stage | ordered deps; fan-in; staged validation; durable mutation after generation | NEGLIGIBLE | REQUIRED |
| apps_shared | Not a domain app | N/A | N/A — chassis, not a route | NOT APPLICABLE |

## Table 3 — Per-hop gating recommendation

| apps_* | DAG/hop | hop purpose | owning layer | input contract | output contract | recommended gating | defense | why not the other options | app-specific vs shared |
|--------|---------|-------------|--------------|----------------|-----------------|--------------------|---------|---------------------------|------------------------|
| apps_eval | evaluation_retrieval | Pull prior eval corpus, scenarios, baseline scores | L2 | `eval_request` | `retrieved_evaluations` | None | Deterministic store fetch with schema validation; no model judgment needed | Judge: nothing to score; Ensemble: deterministic, no candidate diversity gain; Hybrid: cost without benefit | Shared (retrieval substrate candidate) |
| apps_eval | scenario_runner | Execute eval scenarios against fixtures | L2 | `eval_request, retrieved_evaluations` | `scenario_results` | None | Deterministic execution + schema check on results | Judge/Ensemble: scenarios are bounded executions, not generations; Hybrid: out of scope | App-specific (scenario semantics are eval-domain) |
| apps_eval | scorecard | Compute deterministic scorecard from results | L2 | `scenario_results` | `scorecard` | None | Pure deterministic scoring against thresholds | Judge: no semantic artifact; Ensemble: deterministic; Hybrid: unwarranted | App-specific (rubric-aware) |
| apps_eval | narrative_judge | Score scenario narratives against rubric | L2 (judge engine) — Exit owns final disposition | `scenario_results, scorecard` | `judge_verdicts` | Judge | Rubric-based scoring of semantic artifact (narrative groundedness, faithfulness) | None: rubric is semantic, deterministic check insufficient; Ensemble: variance is in narrative not in judgment; Hybrid: rubric judging is stable, ensemble adds latency without robustness gain | App-specific rubric, Judge harness shared |
| apps_eval | regression_detector | Compare scorecard vs prior baselines | L2 | `scorecard` | `regression_result` | None | Deterministic delta + threshold | Judge: no narrative; Ensemble: math; Hybrid: unwarranted | Shared candidate (baseline-vs-current detector) |
| apps_eval | hitl_decision_quality | Assess HITL decision quality of past decisions in window | L2 → Exit consumes | `eval_request, scorecard, regression_result` | `hitl_quality_report` | Hybrid | Externally visible quality verdict on durable HITL ledger; multiple model classifications stabilize, then judge against rubric | None: insufficient — semantic judgment required; Judge alone: variance across edge cases warrants ensemble; Ensemble alone: needs rubric anchor for accountability | App-specific rubric, ensemble + judge harness shared |
| apps_exec | ingestion | Parse source documents into structured form | L2 | `exec_request` | `ingested_documents` | None | Deterministic parse + schema | Judge: no narrative output; Ensemble: parsing is deterministic; Hybrid: unwarranted | Shared candidate (document-ingestion adapter) |
| apps_exec | brief_retrieval | Retrieve similar prior briefs | L2 | `exec_request, ingested_documents` | `retrieved_briefs` | None | Vector + schema retrieval | Judge/Ensemble/Hybrid: deterministic retrieval | Shared (retrieval substrate) |
| apps_exec | capability_extraction | Extract capability evidence from documents | L2 | `ingested_documents` | `extracted_capabilities` | Ensemble | Extraction has high variance and ambiguity (same doc → different extractions across models); deterministic voting/selection improves robustness | None: deterministic NER misses nuance; Judge: there is no "right narrative" — there are multiple valid extractions; Hybrid: judge over extractions adds latency without rubric anchor for "correctness" | App-specific extraction schema, ensemble harness shared |
| apps_exec | brief_assembly | Assemble final exec brief from inputs | L2; Exit owns final disposition | `exec_request, ingested_documents, retrieved_briefs, extracted_capabilities` | `exec_brief` | Hybrid | Customer-facing artifact + high-variance generation; multiple drafts judged against rubric (groundedness, completeness, citation integrity) | None: insufficient for customer-facing; Judge alone: single-draft variance leaks through; Ensemble alone: no rubric anchor | App-specific rubric, harness shared |
| apps_lic | profile_analysis | Extract profile features from campaign request | L2 | `campaign_request` | `profile_features` | None | Schema-driven feature extraction | Judge/Ensemble/Hybrid: deterministic | App-specific (LinkedIn schema) |
| apps_lic | research | Gather evidence about target | L2 | `profile_features, retrieval_chunks` | `evidence_bundle` | None | Retrieval + schema | Judge: no narrative; Ensemble: deterministic; Hybrid: unwarranted | Shared (retrieval substrate) |
| apps_lic | sender_grounding | Build sender persona | L2 | `campaign_request` | `sender_persona` | None | Schema-driven from campaign request | Judge/Ensemble/Hybrid: deterministic | App-specific |
| apps_lic | routing | Choose campaign tactic + generation prompt | L2 | `profile_features, evidence_bundle, sender_persona` | `routing_decision, generation_prompt` | Ensemble | Multiple tactic candidates with selection by deterministic score; ambiguity in tactic choice rewards diversity | None: misses tactic variance; Judge: no rubric for "right tactic"; Hybrid: judge over tactic without ground truth adds cost | App-specific tactic library, selector shared |
| apps_lic | generation | Synthesize draft message | L2 | `generation_prompt, sender_persona` | `draft_message` | Hybrid | Customer-facing, externally visible artifact + high variance; ensemble candidates judged against tone/policy/safety rubric | None: insufficient; Judge alone: lacks variance hedge; Ensemble alone: lacks policy/tone enforcement | App-specific rubric, harness shared |
| apps_lic | validation | Validate draft against evidence + policy | L2 | `draft_message, evidence_bundle` | `validation_report` | Judge | Faithfulness/groundedness + policy fit on a semantic artifact | None: deterministic checks miss faithfulness; Ensemble: validation is checking, not generating; Hybrid: cost without benefit | App-specific rubric, judge harness shared |
| apps_lic | gate_decision | Threshold pass/fail on validation_report | L2 (gate flag set) | `validation_report` | `passed, gate_reason` | None | Threshold against rubric scores; deterministic | Judge/Ensemble/Hybrid: gate is a deterministic function of upstream judge | Shared (gate primitive) |
| apps_lic | qa_report | Compose QA report from validation + draft | L2 | `draft_message, validation_report, evidence_bundle` | `qa_report` | None | Deterministic report assembly | Judge/Ensemble/Hybrid: assembly only | Shared (report primitive) |
| apps_lic | integration | Propose durable mutation (campaign run record) | L2 → UWG (must not write directly) | `campaign_request, draft_message, validation_report, qa_report` | `lic_run_record_fields` | None | Deterministic mapping; UWG owns the actual write | Judge/Ensemble/Hybrid: no semantic judgment at integration boundary | Shared (UWG packet builder candidate) |
| apps_qna | N/A | No DAG required (Table 2) | N/A | N/A | N/A | N/A | DAG-less surface; gating decisions occur inside `paste_bandit.choose()` and `route_bandit.update()` (single-step bandit) | N/A | N/A |
| apps_research | research_retrieval | Retrieve prior research artifacts | L2 | `research_request` | `retrieved_research` | None | Vector + schema retrieval | Judge/Ensemble/Hybrid: deterministic | Shared (retrieval substrate) |
| apps_research | company_brief | Generate company brief from request + retrieved | L2 | `research_request, retrieved_research` | `company_brief` | Hybrid | Customer-facing semantic artifact + high variance; ensemble drafts judged against citation-integrity rubric | None: insufficient for customer-facing; Judge alone: lacks variance hedge; Ensemble alone: lacks citation-integrity anchor | App-specific rubric, harness shared |
| apps_research | research_assembly | Assemble final research artifact | L2 | `research_request, retrieved_research, company_brief` | `research_artifact` | Judge | Final artifact composition is mechanical but needs faithfulness check against retrieved corpus | None: misses faithfulness; Ensemble: composition is deterministic; Hybrid: unwarranted (composition not high-variance) | App-specific rubric, judge shared |
| apps_rfp | rfp_ingestion | Parse RFP documents | L2 | `rfp_request` | `ingested_rfp` | None | Schema-driven parse | Judge/Ensemble/Hybrid: deterministic | Shared (ingestion substrate) |
| apps_rfp | proposal_retrieval | Retrieve similar prior proposals | L2 | `rfp_request, ingested_rfp` | `retrieved_proposals` | None | Retrieval | Judge/Ensemble/Hybrid: deterministic | Shared (retrieval substrate) |
| apps_rfp | proposal_assembly | Assemble proposal | L2 | `rfp_request, ingested_rfp, retrieved_proposals` | `proposal` | Hybrid | Compliance-sensitive, customer-facing artifact + high variance; ensemble drafts judged against compliance/coverage rubric | None: insufficient for compliance; Judge alone: variance leaks; Ensemble alone: no compliance rubric | App-specific rubric, harness shared |
| apps_rg | clerk_extraction | Parse JD + master resume | L2 | `job_description, master_resume` | `hop1_extraction` | None | Schema-driven parse | Judge/Ensemble/Hybrid: deterministic | App-specific schema |
| apps_rg | data_enrichment | Normalize extracted data | L2 | `hop1_extraction` | `hop2_enrichment` | None | Deterministic normalization | Judge/Ensemble/Hybrid: deterministic | Shared (normalization primitive) |
| apps_rg | resume_generation | Synthesize tailored resume | L2 | `hop2_enrichment, master_resume, job_description` | `generated_resume` | Hybrid | Customer-facing, high-variance generation; ensemble drafts judged against ATS/rubric | None: insufficient; Judge alone: lacks variance hedge; Ensemble alone: lacks ATS/rubric anchor | App-specific rubric, harness shared |
| apps_rg | fact_check | Cross-reference generated vs master | L2 | `generated_resume, master_resume` | `fact_check_report` | Judge | Faithfulness/groundedness check on semantic artifact | None: deterministic missing nuance; Ensemble: checking not generating; Hybrid: cost without benefit | App-specific rubric, judge shared |
| apps_rg | bullet_diversity_gate | Thematic-spread gate (gate=True) | L2 (gate flag set) | `generated_resume, fact_check_report` | `passed, gate_reason` | None | Deterministic diversity score against threshold | Judge/Ensemble/Hybrid: deterministic gate | Shared (gate primitive) |
| apps_rg | content_optimizer | Keyword/action-verb refinement | L2 | `generated_resume` | `optimized_resume` | Ensemble | Multiple rewrite candidates with deterministic ATS-score selection; refinement has high variance | None: misses variance; Judge: no rubric for "best refinement"; Hybrid: judge over refinement adds cost | App-specific score, harness shared |
| apps_rg | generation_diagnostics | Final scorecard + QA report | L2 | `optimized_resume, fact_check_report` | `qa_report` | None | Deterministic report assembly | Judge/Ensemble/Hybrid: assembly only | Shared (report primitive) |
| apps_underwriting_ai | initialize_evidence | Set up evidence register | L2 | `underwriting_request` | `evidence_register` | None | Deterministic init | Judge/Ensemble/Hybrid: deterministic | App-specific |
| apps_underwriting_ai | reconcile_documents | Reconcile docs | L2 | `underwriting_request` | `reconciliation_result` | Ensemble | Document reconciliation has high ambiguity (same docs → different reconciliations); voting improves robustness | None: misses ambiguity; Judge: no narrative ground truth; Hybrid: judge over reconciliation adds cost without rubric anchor | App-specific schema, ensemble shared |
| apps_underwriting_ai | derive_features | Derive risk features | L2 | `underwriting_request, reconciliation_result` | `risk_features` | None | Deterministic feature derivation against schema | Judge/Ensemble/Hybrid: deterministic | App-specific |
| apps_underwriting_ai | collect_evidence | Collect evidence per feature | L2 | `underwriting_request, evidence_register, risk_features` | `evidence_collected` | None | Retrieval + schema | Judge/Ensemble/Hybrid: deterministic | Shared (retrieval substrate) |
| apps_underwriting_ai | assemble_decision | Assemble decision packet | L2 → UWG | `underwriting_request, evidence_register, risk_features, reconciliation_result` | `decision_packet` | Hybrid | Compliance-sensitive durable artifact + high variance in decision narrative; ensemble drafts judged against policy rubric | None: insufficient for compliance; Judge alone: variance leaks; Ensemble alone: no policy anchor | App-specific rubric, harness shared |

## Table 4 — Optimization findings by DAG

| apps_* | DAG location | optimization issue | severity | why it matters | recommended non-code remediation |
|--------|--------------|--------------------|----------|----------------|----------------------------------|
| apps_eval | `apps_eval/config/hop_pipeline.py` | Substrate is "additive only"; primary runtime is imperative `EvalOrchestrator` — duplicate workflow definitions | P1 | Two sources of truth for the eval workflow shape; substrate cannot be trusted as the audit surface | Schedule retirement of imperative path OR mark substrate as advisory-only in docstring; do not maintain both |
| apps_eval | `apps_eval/config/hop_pipeline.py` | `narrative_judge` hop owns judge logic but constraint §9 requires Exit/Evaluation to own LLM-as-Judge — boundary blur | P0 | Risk of judge becoming orchestrator; violates §9 | Move judge invocation surface to Exit-owned harness consumed BY the hop, not authored at hop |
| apps_eval | `apps_eval/config/hop_pipeline.py` | No explicit UWG packet emission on terminal hop (`hitl_decision_quality`) | P1 | Terminal Exit-binding contract not declared in topology | Declare UWG packet expectation in spec metadata (extend `outputs` semantics) |
| apps_exec | `apps_exec/config/hop_pipeline.py` | Substrate additive-only; imperative `BaseExecEngine` primary — duplicate definitions | P1 | Same as apps_eval — SSOT drift risk | Adopt substrate as primary OR archive substrate |
| apps_exec | `apps_exec/config/hop_pipeline.py` | `capability_extraction` is fan-out from `ingested_documents` independent of `brief_retrieval` but topology lists it as serial stage 3 — missed parallelism | P2 | Latency higher than necessary; fan-in at stage 4 already accommodates parallel | Re-declare topology to allow stages 2 + 3 in parallel (no `inputs` dependency between them) |
| apps_lic | `apps_lic/config/hop_pipeline.py` | `integration` (stage 9) emits `lic_run_record_fields` but executor has no UWG hook; risk of direct write from app | P0 | Constraint §10 requires UWG as only durable write path; topology must enforce | Document UWG handoff in stage spec; require Exit to consume `lic_run_record_fields` and route through UWG |
| apps_lic | `apps_lic/config/hop_pipeline.py` | `routing` (stage 4) emits `generation_prompt` — generation prompt construction is L1 (cognition) territory leaking into L2 | P1 | Layer gravity: prompt construction belongs in L1; L2 should consume a prompt, not author one | Move prompt construction to an L1 helper consumed by `routing_engine` |
| apps_lic | `apps_lic/config/hop_pipeline.py` | `validation` + `gate_decision` + `qa_report` could overlap (all consume `validation_report`); gate at stage 7 happens after stage 6 but before stage 8 — qa_report should be conditional on gate pass | P2 | Wasted compute on QA when gate fails | Add `optional_skip_if=passed=False` to `qa_report` spec |
| apps_research | `apps_research/config/hop_pipeline.py` | Substrate additive-only — same SSOT drift concern | P1 | See apps_eval / apps_exec | Same remediation |
| apps_research | `apps_research/config/hop_pipeline.py` | No explicit citation-integrity rubric attached to `research_assembly`; judge gating is recommended but topology has no judge anchor | P1 | Judge gating cannot be enforced without rubric ref | Add `rubric_ref` to spec extension for hops marked Judge / Hybrid |
| apps_rfp | `apps_rfp/config/hop_pipeline.py` | Substrate additive-only | P1 | SSOT drift | Same remediation |
| apps_rfp | `apps_rfp/config/hop_pipeline.py` | `proposal_assembly` is the only durable-artifact hop; no Hybrid harness wiring at topology level | P1 | Hybrid recommendation cannot be enforced declaratively | Declare gating mode in spec extension |
| apps_rg | `apps_rg/config/hop_pipeline.py` | 606-line `RgResumeOrchestrator` is the primary path; substrate is additive — substrate cannot be trusted as audit surface | P0 | The 7-stage substrate may diverge silently from the imperative orchestrator | Choose one SSOT — either retire the imperative path or mark substrate as documentation-only |
| apps_rg | `apps_rg/config/hop_pipeline.py` | `bullet_diversity_gate` (stage 5) only blocks; downstream `content_optimizer` and `generation_diagnostics` cannot recover | P2 | Gate failure terminates run with no remediation hop | Add a recovery / heal hop after the gate, or make the gate softer (warn vs block) |
| apps_rg | `apps_rg/config/hop_pipeline.py` | All 7 stages route through `apps_rg.engines.hop_pipeline_adapters` (single module) — coupling risk | P3 | Adapter module is a chokepoint | Split adapters per stage or move to engines directly |
| apps_underwriting_ai | `apps_underwriting_ai/config/hop_pipeline.py` | Substrate additive-only; `UnderwritingEngine.run()` primary | P1 | SSOT drift | Same remediation |
| apps_underwriting_ai | `apps_underwriting_ai/config/hop_pipeline.py` | `assemble_decision` emits `decision_packet` but no UWG handoff declared | P0 | Constraint §10 — durable underwriting decisions must flow through UWG | Same as apps_lic: declare UWG packet expectation |
| apps_underwriting_ai | `apps_underwriting_ai/config/hop_pipeline.py` | Stages 2 + 3 (`reconcile_documents`, `derive_features`) appear serial but `derive_features` only depends on `reconciliation_result` and `underwriting_request` — no need for stage 1 to gate stage 2 | P2 | Missed parallelism between `initialize_evidence` and `reconcile_documents` | Allow stages 1 + 2 to run in parallel (no shared input) |
| apps_qna | N/A | No DAG; correctly so | — | — | None |
| apps_shared | `apps_shared/orchestration/hop_pipeline.py` | `HopPipelineExecutor` has no UWG hook surface; no L3StepContract adapter; no judge / ensemble dispatch declarations | P0 | The chassis cannot enforce constraints §6/§7/§9/§10 — substrate is mechanically correct but governance-incomplete | Extend `HopStageSpec` with `gating: None|Judge|Ensemble|Hybrid` + `uwg_handoff: bool` + `rubric_ref` fields; teach executor to dispatch accordingly |

## Table 5 — Shared chassis opportunities

| reusable hop/pattern | apps_* using or needing it | should live in agentic_core/apps_shared? | reason | duplication risk | recommended owner |
|----------------------|----------------------------|-------------------------------------------|--------|------------------|-------------------|
| Vector retrieval hop | apps_eval, apps_exec, apps_lic, apps_research, apps_rfp, apps_underwriting_ai | apps_shared (or thin wrapper over agentic_core retrieval) | All six apps have a retrieval-only stage with identical contract shape | HIGH — six near-duplicate engines | `apps_shared.orchestration.retrieval` substrate |
| Document ingestion / parsing | apps_exec, apps_rfp, apps_underwriting_ai | apps_shared | Same shape: typed parse → schema → ingested_* | MEDIUM | `apps_shared.orchestration.ingestion` substrate |
| Final-artifact assembly with fan-in | apps_eval, apps_exec, apps_lic, apps_research, apps_rfp, apps_rg, apps_underwriting_ai | apps_shared (parameterized assembler) | Every DAG terminates with a fan-in assembly hop; only the schema differs | HIGH | `apps_shared.orchestration.assembly` substrate |
| Faithfulness / fact-check judge | apps_eval (`narrative_judge`), apps_lic (`validation`), apps_rg (`fact_check`) | agentic_core (Judge harness) — Exit-owned per §9 | LLM-as-Judge harness is policy boundary; rubric is per-app, harness is shared | HIGH | `agentic_core/L3_orchestration/exit_eval` |
| Ensemble dispatcher (multi-candidate generate + select) | apps_exec (`capability_extraction`), apps_lic (`routing`), apps_rg (`content_optimizer`), apps_underwriting_ai (`reconcile_documents`) | agentic_core or apps_shared | Same pattern: N candidates, deterministic selector | MEDIUM | `agentic_core/L2_execution/ensemble` |
| Hybrid (Ensemble + Judge) harness for customer-facing generation | apps_exec, apps_lic, apps_research, apps_rfp, apps_rg, apps_underwriting_ai | agentic_core | High-stakes pattern that must be auditable end-to-end | HIGH if duplicated | `agentic_core/L3_orchestration/exit_eval` (composition of judge + ensemble) |
| Threshold / pass-fail gate primitive | apps_lic (`gate_decision`), apps_rg (`bullet_diversity_gate`) | apps_shared | Deterministic threshold-against-score | LOW | `apps_shared.orchestration.gate` |
| QA report assembly | apps_lic (`qa_report`), apps_rg (`generation_diagnostics`) | apps_shared | Deterministic structured report build | LOW | `apps_shared.orchestration.report` |
| UWG packet builder for terminal hops | apps_lic (`integration`), apps_underwriting_ai (`assemble_decision`), apps_eval (`hitl_decision_quality`) | apps_shared (with UWG handoff) | Constraint §10 — single durable-write path | HIGH if absent | `apps_shared.orchestration.uwg_handoff` |
| L3StepContract adapter for substrate-driven runs | All apps with DAG | agentic_core | L3 must own step contracts per §3/§6 | HIGH — no adapter exists today | `agentic_core/L3_orchestration/reasoning` |

## Table 6 — Missing evidence and blockers

| apps_* | missing artifact | expected location or registry | why required | impact | blocker severity |
|--------|------------------|-------------------------------|--------------|--------|------------------|
| ALL apps with DAG | Per-app `RouteContract` declaration with `execution_form = MANAGED_WORKFLOW` | `agentic_core/L0_routing/` (no per-app file located in inventory pass) | Constraint §3 — L0 must emit a deterministic RouteContract; without it, substrate runs are not L3-gated | DAGs are runnable but not architecturally bound to L3; constraint §3 unverifiable | P0 |
| ALL apps with DAG | `L3StepContract` adapter wiring `HopPipelineExecutor` to L3 | `agentic_core/L3_orchestration/reasoning/` | Constraint §6 — L3 owns step contracts | Substrate runs without L3 binding | P0 |
| ALL apps with DAG | UWG handoff hook on terminal / gate / mutation hops | `HopPipelineExecutor` and per-app terminal stage specs | Constraint §10 — UWG-only durable writes | Risk of direct writes from L2/L3 | P0 |
| apps_eval, apps_lic, apps_rfp, apps_research, apps_rg, apps_underwriting_ai, apps_exec | Rubric reference attached to Judge / Hybrid hops | Stage spec extension + `config/rubrics/*.yaml` (apps_eval has `apps_eval/config/rubrics/`; others do not) | Constraint §9 + Judge requirement — rubric is the contract | Judge gating cannot be enforced declaratively | P1 |
| apps_eval | Confirmation that `narrative_judge` engine does not retrieve / route / write | `apps_eval/engines/hop_narrative_judge_engine.py` (NOT INSPECTED in this pass) | Constraint §9 — judge must not become orchestrator | Cannot certify boundary | P1 |
| apps_qna | Documented exemption noting no DAG required | `apps_qna/RUNBOOK.md` or registry entry | Audit requires evidence of correct DAG-less verdict | NOT FOUND — exemption is implicit, not written | P2 |
| apps_shared (chassis) | Gating-mode field (`None`/`Judge`/`Ensemble`/`Hybrid`) on `HopStageSpec` | `apps_shared/orchestration/hop_pipeline.py` `HopStageSpec` | Cannot declaratively encode gating recommendations from Table 3 | Recommendations cannot be enforced via spec | P1 |
| apps_shared (chassis) | UWG handoff field (`uwg_handoff: bool`) on `HopStageSpec` | Same | Constraint §10 enforcement at topology level | See above | P0 |
| apps_lic, apps_rg | Imperative-vs-substrate SSOT decision | `.windsurf/plans/` or `docs/architecture/adr/` | Author-Gate 2026-05-01 selected substrate as SSOT for apps_lic; apps_rg has no equivalent decision | Drift risk | P1 |

## Table 7 — Final recommendation

| apps_* | final DAG status | final gating posture summary | required follow-up | confidence |
|--------|------------------|------------------------------|--------------------|------------|
| apps_eval | DAG REQUIRED, present, partially optimized | Judge on narrative_judge; Hybrid on hitl_decision_quality; None elsewhere | Move judge dispatch to Exit-owned harness; declare UWG handoff on terminal hop | HIGH |
| apps_exec | DAG REQUIRED, present, partially optimized | Ensemble on capability_extraction; Hybrid on brief_assembly; None elsewhere | Re-declare stages 2+3 parallel; pick substrate-vs-imperative SSOT | HIGH |
| apps_lic | DAG REQUIRED, present, partially optimized | Ensemble on routing; Hybrid on generation; Judge on validation; None elsewhere | Declare UWG handoff at integration; move prompt construction to L1; conditional skip on qa_report | HIGH |
| apps_qna | DAG NOT REQUIRED, correctly absent | Bandit-driven gating at runtime; no DAG hops | Document exemption in apps_qna RUNBOOK so future audits do not flag false negative | HIGH |
| apps_research | DAG REQUIRED, present, partially optimized | Hybrid on company_brief; Judge on research_assembly; None on retrieval | Add rubric refs; pick substrate-vs-imperative SSOT | HIGH |
| apps_rfp | DAG REQUIRED, present, partially optimized | Hybrid on proposal_assembly; None elsewhere | Add rubric refs; pick substrate-vs-imperative SSOT | HIGH |
| apps_rg | DAG REQUIRED, present, partially optimized | Hybrid on resume_generation; Judge on fact_check; Ensemble on content_optimizer; None on gate / diagnostics | Pick substrate-vs-imperative SSOT (P0); add recovery path after diversity gate | HIGH |
| apps_underwriting_ai | DAG REQUIRED, present, partially optimized | Ensemble on reconcile_documents; Hybrid on assemble_decision; None elsewhere | Declare UWG handoff at assemble_decision; allow stages 1+2 parallel; pick SSOT | HIGH |
| apps_shared (chassis) | NOT AN APP; chassis is governance-incomplete | N/A | Extend HopStageSpec with gating + uwg_handoff + rubric_ref fields; add L3StepContract adapter; add UWG hook surface | HIGH |

---

**Audit verdict**: 7 of 8 apps_* correctly have DAGs (apps_qna correctly does not). All 7 existing DAGs are functionally present but governance-incomplete: substrate is "additive only" everywhere except apps_lic, no L0 RouteContract / L3StepContract / UWG handoff is declarable today, and gating modes (Judge/Ensemble/Hybrid/None) live in narrative form rather than topology fields. The most critical structural gaps are P0 in `apps_shared/orchestration/hop_pipeline.py` (chassis lacks gating + UWG fields) and P0 on terminal mutation hops (`apps_lic.integration`, `apps_underwriting_ai.assemble_decision`) where direct-write risk exists.
