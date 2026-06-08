# apps_rg AIG E2E Failure Remediation

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: TODO
CURRENT_WAVE: W0
LAST_COMPLETED_WAVE: none
LAST_UPDATED: 2026-06-07

Plan ID: `apps-rg-aig-e2e-remediation-e4b7c1`
Status: Not Started
Created: 2026-06-07
Branch observed during RCA: `chat/adg-redis-ssot-b9f4c2`
Notion: https://app.notion.com/p/37827693f55c819d8ca1d5e8fee2941d

## Context

Situation: AIG VP Global Head of Agentic AI end-to-end testing was run against:

- JD: `apps_rg/config/targeting/aig_vp_global_head_agentic_ai_jd.txt`
- Briefing: `apps_rg/config/targeting/aig_vp_global_head_agentic_ai_briefing.md`

Complication: Input validation passes and provider credentials are present, but the product run cannot certify. Failures span deterministic section gates, section orchestration, stale provider/preflight metadata, an executive-summary code crash, role-episode proof absence, and integrated dispatch resource exceptions. The provider target must also be clarified: `external_claude` / `claude-sonnet-4-6` is the apps_rg E2E target. Qwen/vLLM may exist only as an explicit diagnostic/dev provider if retained; it must not participate in default E2E, product preflight, or external-Claude receipts.

Question: What must be fixed so AIG JD plus briefing can run through all apps_rg lanes with live providers, model-backed judges, and product-eligible X3 artifacts?

Answer: Fix the section blockers in dependency order: make diagnostics truthful, decontaminate Qwen-era default metadata from Claude E2E paths, fix early crashes and provider/embedding bootstrap, repair competencies graph projection, repair bullet lane blocked outputs, supply InsurTech/EY proof slices, then rerun the full AIG E2E with judge matrix verification.

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| W0 | W0.P1-W0.P3 | Preserve AIG RCA evidence and create regression harness | 4k | Current RCA artifacts remain available | TODO | AIG fixtures and artifact summarizer cover all observed blockers |
| W1 | W1.P1-W1.P4 | Runtime bootstrap, provider metadata, embedding, and integrated diagnostics | 8k | Provider selection remains external Claude default | TODO | External Claude lanes no longer emit Qwen request/preflight metadata; Chroma/Rust exceptions include actionable traces |
| W2 | W2.P1-W2.P3 | Executive summary lane crash and judge-panel reachability | 5k | Current token budget policy is retained | TODO | `executive_summary` reaches generation and X1D judges with AIG inputs |
| W3 | W3.P1-W3.P4 | Competencies graph projection and X2/X1D alignment | 10k | JD/briefing stay targeting-only | TODO | `competencies` X3_ALLOW or explicit non-certifying judge-only review with zero X2 failures |
| W4 | W4.P1-W4.P4 | Unify/IBM bullet lanes and provider-blocked output semantics | 10k | Bullet gate thresholds remain authoritative | TODO | `unify_bullets` and `ibm_bullets` produce product-shaped outputs or fail before X2 with precise upstream blocker |
| W5 | W5.P1-W5.P3 | InsurTech/EY proof slices and role-episode lanes | 8k | Proof inventory can be extended from existing ledgers | TODO | `insurtech_*` and `ey_*` no longer stop at `REQUIRED_PROOF_ABSENT` for AIG |
| W6 | W6.P1-W6.P4 | Full AIG E2E certification run | 6k | W1-W5 gates pass first | TODO | Full `python -m apps_rg` executes all 11 lanes; root and section X3 outcomes are product-auditable |

## Evidence

Artifacts generated during RCA:

| Probe | Artifact | Result |
|---|---|---|
| Input dry run | `artifacts/apps_rg/e2e_aig_apps_rg_e2e_20260607/dryrun` | PASS input and embedding pre-dispatch |
| Full product run | `artifacts/apps_rg/e2e_aig_apps_rg_e2e_20260607/full_default` | FAIL, only `competencies` finalized; 10 lanes not run |
| Executive summary, all judges | `artifacts/apps_rg/e2e_aig_apps_rg_e2e_20260607/section_executive_summary_external_all_judges` | FAIL before generation: `resolve_scratch_max_output_tokens` UnboundLocalError |
| Competencies, qwen_vllm | `artifacts/apps_rg/e2e_aig_apps_rg_e2e_20260607/section_competencies_qwen` | REAL_LLM, X1D Anthropic PASS, X2 BLOCK |
| Unify bullets, external Claude | `artifacts/apps_rg/e2e_aig_apps_rg_e2e_20260607/section_unify_bullets_external` | REAL_LLM but blocked/empty output; X2 and X1D BLOCK |
| IBM bullets, external Claude | `artifacts/apps_rg/e2e_aig_apps_rg_e2e_20260607/section_ibm_bullets_external` | REAL_LLM but `provider blocked`; X2 and X1D BLOCK |
| InsurTech bullets, external Claude | `artifacts/apps_rg/e2e_aig_apps_rg_e2e_20260607/section_insurtech_bullets_external` | `REQUIRED_PROOF_ABSENT`; retries stopped |
| Judge transport probe | `artifacts/apps_rg/e2e_aig_apps_rg_e2e_20260607/judge_transport_probe` | OpenAI, Anthropic, Gemini all model-backed; no credential/model-not-found transport blocker |

## Execution Target And Provider Policy

Decision:

- Production AIG E2E target provider: `external_claude`.
- Target generation model: `claude-sonnet-4-6`, sourced from `ANTHROPIC_MODEL` or provider profile resolution.
- Product E2E preflight must treat Qwen/vLLM as `NOT_APPLICABLE` whenever `external_claude` is selected.
- Product E2E artifacts must not show Qwen model/base URL in request, response, preflight, or provider-call receipts for Claude-selected lanes.
- Qwen/vLLM status: legacy diagnostic/dev-only explicit provider unless a later plan intentionally removes it. It is not part of the AIG E2E acceptance path.

Enforcement:

- `APPS_RG_MODULAR_LANE_PROVIDER=external_claude` is the default for AIG E2E.
- `--provider qwen_vllm` may remain accepted only for explicit local comparison tests and must be labeled `diagnostic_non_product_default`.
- Any Qwen health/model check during an external-Claude lane is a failure unless recorded as `NOT_APPLICABLE`.
- Any Qwen metadata in an external-Claude `provider_request.json`, `provider_response.json`, pre-dispatch receipt, or `section_provider_calls.json` is a failure.

Definition of running:

- Dry-run validates AIG inputs.
- Full run executes all 11 lanes, not just artifact collection.
- Every lane has one of: `X3_ALLOW`, accepted product-review state with a single actionable blocker, or pre-X2 upstream block with exact missing proof/config.
- The target happy path is `external_claude` through generation and model-backed X1D judges, with no default Qwen dependency.
- `integrated_lane_evidence_status.json` reports zero `missing_lanes`.

## RCA Summary

| Area | Finding | Root Cause Hypothesis | Remedy |
|---|---|---|---|
| Ingress | AIG JD and briefing pass dry-run and pre-dispatch | Inputs are valid | Keep fixtures pinned for regression |
| Full dispatch | Full run records 1 executed lane and 10 missing lanes | Integrated run treats X3_BLOCK lanes as missing/success-pointer absent and lets early exceptions poison later lanes | Record failed-but-executed lane pointers, isolate per-lane exceptions, and continue audit collection |
| Provider metadata | Actual generation used `external_claude` / `claude-sonnet-4-6`, but request/preflight receipts still show Qwen fields | Section request receipt and some preflight paths remain Qwen-shaped | Make provider metadata come from `ProviderResult`/selected provider, not Qwen defaults |
| Embedding/Chroma | Product-strict embedding prints fallback and full run gets `data/cache/chromadb` exception in Unify path | Chroma embedding function resolves invalid `sentence-transformers/bge-m3-v1` instead of local BGE path; resource exceptions lack trace | Use configured local BGE path, fail closed when mandatory embedding is unavailable, add trace artifact |
| Executive summary | `resolve_scratch_max_output_tokens` UnboundLocalError before generation | Function-local import after earlier use shadows the global name | Move import above first use or module-level; add regression test |
| Competencies | External Claude and Qwen both X2_BLOCK | Final projection emits generic categories with only 2 graph-backed terms, and `LLMOps & Reliability` loses bundle/graph lineage | Preserve bundle/graph ids for every category and emit at least 3 graph-backed terms for generic categories |
| Competencies X1D | Gemini graph-pool selector reports 0 selected categories despite 8 generated categories | Judge adapter evaluates the wrong merge shape or pre-finalization shape | Align X1D graph-pool packet with canonical `competencies_section_output.json` |
| Unify bullets | External Claude lane returns blocked/empty output but still cascades through many X2 failures | Provider-blocked/empty output is represented as a product-shaped candidate too late | Fail before X2 on provider-blocked output, or repair/retry before exit gates |
| IBM bullets | Standalone lane returns `provider blocked`; integrated run also saw `RustBindingsAPI.bindings` | IBM lane has both provider-blocked product shape failure and integrated resource-state exception | Add provider-blocked pre-X2 handling; fix Rust bindings call/adapter state in integrated dispatch |
| Role episode lanes | InsurTech/EY stop at `REQUIRED_PROOF_ABSENT` | Proof slices/product generators for new lanes are not complete | Add AIG/insurance carrier role-episode proof slices and generators |
| Judges | OpenAI `gpt-5.5`, Anthropic `claude-sonnet-4-6`, Gemini `gemini-3.1-pro-preview` all execute model-backed | Judge transport is available; failing judge rows are content/rubric outcomes, not credentials | Keep judge transport probe; fix content/gates before judge calibration |

## Detailed RCA Inventory

| ID | Failure | Observed Evidence | Root Cause | Fix | Verification |
|---|---|---|---|---|---|
| E2E-01 | Branch / execution-surface ambiguity | Plan creation and RCA observed on `chat/adg-redis-ssot-b9f4c2`; `apps_rg_e2e` exists separately | Worktree changed between branch setup and E2E execution | Before implementation, switch or recreate a clean worktree from `apps_rg_e2e`, then replay targeted probes | `git status --short --branch` shows `apps_rg_e2e`; no unrelated dirty files before code changes |
| E2E-02 | Qwen leakage into Claude path | External Claude generation used `claude-sonnet-4-6`, but some request/preflight receipts exposed Qwen fields | Request/preflight receipts are built from Qwen-era defaults instead of selected provider result | Centralize provider receipt builder; drive metadata from selected provider/result; mark Qwen checks `NOT_APPLICABLE` for Claude | External Claude section run writes no Qwen model/base URL except allowed diagnostic labels |
| E2E-03 | `.env` and provider readiness ambiguity | Shell lacked keys, `.env` had keys; provider probe worked after explicit `.env` load | Env bootstrap is not uniformly guaranteed before all provider and judge guards | Add canonical apps_rg env bootstrap before preflight/provider/judge resolution | Provider readiness test passes with keys only in `.env`; injected empty env still fails closed |
| E2E-04 | Embedding fallback despite product strictness | Logs show invalid `sentence-transformers/bge-m3-v1` fallback to default EF; integrated Unify exception references Chroma path | Chroma embedding resolver ignores local `APPS_RG_EMBEDDING_MODEL_PATH` or treats mandatory embedding failure as fallback | Resolve BGE from configured local snapshot; if mandatory embedding fails, stop before generation with trace | Product-strict embedding test proves no default EF fallback; Chroma exception includes stack trace |
| E2E-05 | Full run stops after competencies | `full_default` finalized only `competencies`; 10 lanes marked missing/pre-run blocked | Integrated dispatcher conflates X3-blocked executed lanes with missing successful lane pointers and lets early exceptions poison later status | Store latest attempted run pointer for blocked lanes; continue audit collection per lane; separate `EXECUTED_X3_BLOCK`, `PRE_RUN_BLOCKED`, and `MISSING_NOT_ATTEMPTED` | Failed full run still reports every attempted lane with precise status and no false missing-lane classification |
| E2E-06 | Executive summary UnboundLocalError | `section_executive_summary_external_all_judges` fails before generation | Function-local import shadows earlier call in `executive_summary_lane.py` | Move import to module scope or before first use; add targeted regression | Executive summary reaches provider request/response and X1D judge artifacts |
| E2E-07 | Competencies X2 block | External Claude and Qwen both fail generic-category graph term gate; `LLMOps & Reliability` missing bundle/graph ids | Deterministic finalization/projection drops lineage and emits 2-term generic categories when gate requires 3 graph-backed terms | Repair competencies finalizer to preserve category lineage and fill 3 graph-backed terms from selected graph pool | AIG competencies has zero X2 failures; lineage fields present for all 8 categories |
| E2E-08 | Competencies X1D false zero-selection | Gemini graph selector reports 0 category selections while 8 categories exist | X1D reads wrong shape or pre-finalization object instead of canonical `competencies_section_output.json` | Adapt X1D packet builder to canonical output; assert final category count and selected category mapping | X1D output reports 8 category selections and meaningful score/verdict |
| E2E-09 | Unify bullets blocked/empty output reaches X2 | `L2_UNIFY_BULLETS_OUTPUT: BLOCKED`; X2 then fails top-level keys, count, metrics, claim coverage, lineage, seniority, technical specificity | Provider-blocked or empty output is represented as a product candidate too late | Convert blocked/empty provider output into pre-X2 upstream blocker or repairable retry; enforce product JSON skeleton before X2 | Unify either produces 6 product bullets with zero structural X2 failures or emits one upstream blocker before X2 |
| E2E-10 | IBM bullets provider-blocked output reaches X2 | `IBM_BULLETS_OUTPUT: BLOCKED: provider blocked`; X2 count/key/coverage failures | Same blocked-output path as Unify, plus IBM-specific metric/ownership requirements | Share bullet-lane blocked-output handling; add IBM product-shape pre-X2 repair | IBM either produces 5 bullets with claim ledger coverage or emits one upstream blocker before X2 |
| E2E-11 | Integrated IBM Rust binding exception | Full run records `RustBindingsAPI object has no attribute bindings` for IBM and dependent lanes | Integrated resource/state path calls Rust bindings incorrectly or assumes adapter shape not present | Find call site, wrap with typed adapter capability check, emit structured trace, or remove Rust path from product E2E | Integrated IBM no longer throws raw attribute error; exception trace artifact names exact module if still blocked |
| E2E-12 | InsurTech/EY role lanes proof absent | `insurtech_bullets` stops at `REQUIRED_PROOF_ABSENT`; EY/InsurTech lanes missing in full run | New 11-lane design registered lanes without full AIG proof slices/product generators | Add role-episode proof inventory slices and PA/product generators for insurance carrier and EY lanes | All `insurtech_*` and `ey_*` write FEC, selected facts, provider output, X1D, X2, X3 |
| E2E-13 | Judge results are content failures, not transport failures | OpenAI, Anthropic, Gemini all model-backed; tiny synthetic probe failed rubric scores | Judges can run; content/gates are not ready for certification | Keep judge transport probe separate; rerun after deterministic gates pass; only tune rubrics after content is product-shaped | Judge transport matrix produces model-backed rows; final lane judge failures have candidate-specific rationale |
| E2E-14 | Root X3/product status confusing | Root X3 receipt showed `X3A` while lane status is `X3_BLOCK` and product authorization false | Artifact collection, root placeholder, and lane X3 authority are not visually separated | Make root closeout report name lane X3 authority and product authorization; block root success if any required lane not run | Final full-run status cannot say success when lane X3 is blocked or missing |

## Critical Path To Running

1. Stabilize the execution surface on `apps_rg_e2e` and preserve the current RCA artifacts.
2. Fix instrumentation first so each failed lane reports the real selected provider, model, executed/missing state, exception trace, and proof blocker.
3. Remove Qwen from the default Claude E2E path and prove `external_claude` receipts are Claude-only.
4. Fix environment and embedding bootstrap before any live generation work.
5. Fix the executive-summary crash because it prevents a required lane from reaching provider or judges.
6. Fix deterministic competencies projection before judge calibration; deterministic gates define the admissible product.
7. Fix bullet-lane blocked-output semantics so provider blockers do not masquerade as malformed product candidates.
8. Populate InsurTech/EY proof slices and product generators so all 11 lanes can attempt.
9. Run targeted section probes, then full AIG E2E, then judge transport/content matrix.
10. Close only when every required lane has an auditable X3 or a single accepted product-review blocker.

## Acceptance Matrix

| Checkpoint | Must Pass Before | Acceptance |
|---|---|---|
| Branch hygiene | W1 code edits | Implementation branch is `apps_rg_e2e` or an explicit successor; unrelated dirty files are not staged |
| Env bootstrap | Provider preflight | `.env`-only credentials are visible to apps_rg provider and judge readiness |
| Provider policy | Any AIG product run | `external_claude` / `claude-sonnet-4-6` is selected; Qwen is absent or `NOT_APPLICABLE` |
| Embedding strictness | Generation | Mandatory embedding uses configured local BGE or fails before provider call with exact blocker |
| Executive summary | Full run | Lane reaches provider response and X1D artifacts |
| Competencies | Bullet dependent review | All 8 categories carry lineage and pass X2 deterministic gates |
| Unify/IBM bullets | Narrative/dependency lanes | Blocked/empty generations are repaired or stopped before X2; valid candidates satisfy product shape |
| InsurTech/EY | Full run | Proof slices exist and lanes no longer stop at `REQUIRED_PROOF_ABSENT` |
| Integrated dispatch | Final E2E | Every required lane has attempted/executed/missing truthfully classified |
| Judges | Final certification | OpenAI/Anthropic/Gemini judge rows are model-backed or have precise transport blockers; content failures cite candidate-specific reasons |

## Wave 0 - Evidence Harness

WAVE_ID: W0
WAVE_STATUS: TODO
WAVE_COMPLETE: NO

Scope:
- Add a small AIG E2E RCA summarizer that reads run artifacts and emits a compact matrix of provider, model, X1D, X2, X3, and blocker statuses.
- Add regression fixtures referencing the AIG JD and briefing paths.
- Preserve the current RCA artifact paths in a receipt.
- Capture branch provenance and selected-provider policy in the RCA receipt.
- Include `attempted`, `executed`, `x3_status`, `product_authorized`, `provider`, `model`, `blocked_reason`, and `missing_reason` fields in summarizer output.

DoD:
- `python tools/apps_rg/summarize_e2e_run.py <artifact-dir>` works for full and section runs.
- AIG fixture hashes are asserted in a unit/contract test.
- No provider calls required for W0 tests.
- Summarizer differentiates `EXECUTED_X3_BLOCK`, `PRE_RUN_BLOCKED`, and `MISSING_NOT_ATTEMPTED`.

## Wave 1 - Runtime Diagnostics And Provider Metadata

WAVE_ID: W1
WAVE_STATUS: TODO
WAVE_COMPLETE: NO

Scope:
- Ensure external Claude lanes never emit Qwen request model/base URL in `provider_request.json` or console preflight.
- Make `section_provider_calls.json` classify executed-but-blocked lanes separately from missing lanes.
- Persist full exception trace artifacts for integrated lane exceptions.
- Fix BGE/Chroma embedding resolution to use `APPS_RG_EMBEDDING_MODEL_PATH`; product-strict mandatory embedding must fail closed instead of silently using default EF.
- Ensure `.env` bootstrap runs before provider readiness, judge readiness, embedding config, and CLI pre-dispatch guards.
- Add a provider policy guard that marks Qwen/vLLM `NOT_APPLICABLE` in external-Claude runs and fails tests on Qwen metadata leakage.

DoD:
- External Claude pre-dispatch reports Qwen `NOT_APPLICABLE` and lane request receipts name Claude.
- Failed lanes are visible as `EXECUTED_X3_BLOCK` or `PRE_RUN_BLOCKED`, not all `MISSING_LANE_RUN`.
- Chroma/Rust integrated exceptions include stack trace, module, and remediation hint.
- Provider readiness passes when keys are present only in root `.env`.
- A metadata-leakage regression scans external-Claude artifacts and finds no Qwen model/base URL outside explicit diagnostic labels.

## Wave 2 - Executive Summary Crash

WAVE_ID: W2
WAVE_STATUS: TODO
WAVE_COMPLETE: NO

Scope:
- Fix `apps_rg/runtime/sections/executive_summary_lane.py` local import shadowing for `resolve_scratch_max_output_tokens`.
- Add a focused regression that reaches the executive-summary token budget policy with AIG runtime payload.
- Re-run executive summary with `--x1d-judges openai_chatgpt,anthropic_claude,gemini_pro`.
- Confirm OpenAI `gpt-5.5` is used only as a judge when requested, not as the Claude generation provider.

DoD:
- No UnboundLocalError.
- Provider request/response artifacts are written.
- All three judge keys are either model-backed with verdicts or blocked with precise transport reasons.
- Executive-summary X2/X3 artifacts exist even when final verdict is not ALLOW.

## Wave 3 - Competencies Graph Projection

WAVE_ID: W3
WAVE_STATUS: TODO
WAVE_COMPLETE: NO

Scope:
- Repair `finalize_competencies_v3_output` / graph projection so every emitted category carries `competency_bundle_id`, `capability_family`, and `graph_skill_node_ids`.
- For generic taxonomy labels, enforce three or more graph-backed terms before X2.
- Make competencies X1D graph-pool selector read the canonical merged output shape.
- Keep JD and briefing targeting-only; do not use them as proof.
- Add deterministic pre-X2 validator coverage for category lineage and graph-backed term counts.

DoD:
- AIG competencies with `external_claude` has zero X2 failures.
- AIG competencies with `qwen_vllm` has zero X2 failures or a provider-specific judge-only failure with no deterministic gate failure.
- `x1d_llm_judge_outputs.json` no longer reports `0 category selections` when 8 categories are emitted.
- Each of the exact 8 categories has lineage fields and at least the required graph-backed term count.

## Wave 4 - Bullet Lane Product Shape

WAVE_ID: W4
WAVE_STATUS: TODO
WAVE_COMPLETE: NO

Scope:
- For Unify/IBM, detect provider-blocked or empty generation before X2 and route through bounded retry/repair.
- Ensure bullet outputs include required top-level JSON keys, exact bullet counts, claim ledger coverage, metric ownership, role episode bundle ids, graph skill ids, and source/graph lineage.
- Fix integrated IBM `RustBindingsAPI` adapter use and integrated Unify Chroma exception.
- Share blocked-output admission logic across bullet lanes so `BLOCKED:` text cannot be passed to X2 as a product candidate.

DoD:
- `unify_bullets` and `ibm_bullets` standalone AIG runs produce product-shaped candidates or fail with a single upstream blocker before X2.
- Integrated dispatch no longer records raw `RustBindingsAPI.bindings` or bare Chroma path exceptions.
- Any remaining failures are content-specific and cite the missing proof/claim/metric rather than generic JSON/key cascade errors.

## Wave 5 - Role Episode Proof Slices

WAVE_ID: W5
WAVE_STATUS: TODO
WAVE_COMPLETE: NO

Scope:
- Populate insurance-carrier proof slices required by `insurtech_bullets` and `insurtech_narrative`.
- Populate EY/consulting transformation proof slices required by `ey_bullets` and `ey_narrative`.
- Wire those proof slices into section C0/FEC and PA inputs with `JD/briefing targeting only` preserved.
- Add exact diagnostics when proof is still missing so retries are not spent on upstream evidence gaps.

DoD:
- `insurtech_bullets`, `insurtech_narrative`, `ey_bullets`, and `ey_narrative` no longer return `REQUIRED_PROOF_ABSENT`.
- Role-episode lanes write `selected_fact_plan.json`, FEC, provider request/response, X1D, X2, and X3 artifacts.
- Missing-proof tests fail closed before provider generation with named required proof families.

## Wave 6 - Full AIG E2E Verification

WAVE_ID: W6
WAVE_STATUS: TODO
WAVE_COMPLETE: NO

Scope:
- Run full AIG E2E on `apps_rg_e2e`.
- Run focused section matrix for `external_claude`; run `qwen_vllm` only as an explicit diagnostic comparison if it remains supported.
- Run judge transport matrix for OpenAI, Anthropic, and Gemini.
- Generate final closeout report.
- Produce a Qwen disposition note: removed from apps_rg product path, or retained as diagnostic-only with tests proving non-default behavior.

DoD:
- Full run executes all 11 lanes.
- `integrated_lane_evidence_status.json` reports zero missing lanes.
- Root `generate_resume_step_receipt.json` has `decisive_status=PASS` or an explicitly accepted product-review state.
- All remaining non-ALLOW outcomes have a single non-ambiguous blocker and remediation note.
- Closeout artifacts show external-Claude generation path, model-backed judges, and no default Qwen dependency.

## Verification Commands

```text
python -m pytest -q tests/unit/apps_rg tests/_apps_contract -k "apps_rg or executive_summary or competencies or bullet or x1d"
python -m apps_rg --target-company AIG --target-role "VP Global Head of Agentic AI Solutions" --target-level VP --jd apps_rg/config/targeting/aig_vp_global_head_agentic_ai_jd.txt --manual-brief apps_rg/config/targeting/aig_vp_global_head_agentic_ai_briefing.md --dry-run --artifact-dir artifacts/apps_rg/e2e_aig_verify/dryrun
python -m apps_rg --target-company AIG --target-role "VP Global Head of Agentic AI Solutions" --target-level VP --jd apps_rg/config/targeting/aig_vp_global_head_agentic_ai_jd.txt --manual-brief apps_rg/config/targeting/aig_vp_global_head_agentic_ai_briefing.md --artifact-dir artifacts/apps_rg/e2e_aig_verify/full
python -m apps_rg --target-company AIG --target-role "VP Global Head of Agentic AI Solutions" --target-level VP --jd apps_rg/config/targeting/aig_vp_global_head_agentic_ai_jd.txt --manual-brief apps_rg/config/targeting/aig_vp_global_head_agentic_ai_briefing.md --section executive_summary --provider external_claude --x1d-judges openai_chatgpt,anthropic_claude,gemini_pro --artifact-dir artifacts/apps_rg/e2e_aig_verify/executive_summary_all_judges
```

## Out Of Scope

- Changing the factual authority model that keeps JD and briefing as targeting/context only.
- Lowering deterministic gates just to achieve X3_ALLOW.
- Replacing model-backed judges with mocks.
- Treating packaging or artifact collection as product certification.
