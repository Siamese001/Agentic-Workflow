# apps_rg AIG E2E Failure Remediation (Hardened)

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: IN_PROGRESS
CURRENT_WAVE: W4
LAST_COMPLETED_WAVE: W3
LAST_UPDATED: 2026-06-08

Plan ID: `apps-rg-aig-e2e-remediation-e4b7c1`
Status: Not Started
Created: 2026-06-07
Hardened: 2026-06-07 — independent code + RCA-artifact verification pass (6 parallel verifiers). See `## Verification Provenance`.
Implementation branch: the active per-chat branch (branch-per-chat cuts a fresh `chat/<stamp>` from `main` each session). `apps_rg_e2e` is **not** required — the original E2E-01 assumption was stale. Keep unrelated dirty files unstaged.
Scope boundary: **apps_rg only.** No `agentic_core` edits, no other `apps_*`. Any generic-core residue is captured under `## Out Of Scope` / `## Deferred Follow-ups`, never implemented here.
Notion: https://app.notion.com/p/37827693f55c819d8ca1d5e8fee2941d

> **Execution status (2026-06-08) — UNPAUSED; Qwen-removal landed.** W0, W1, W3 are on
> `main` (`c7b1cdacdb` / `b6682b5dec` / `c66fc476d7`). The concurrent **Qwen-removal refactor
> merged** (PR #256: `ffc5391ee9` stage 1 + `15c8dcbd05` stage 2 → merge `cb2235f915`);
> `apps_rg/runtime/providers/qwen_vllm_provider.py` is **deleted** and external Claude is the
> sole generator (the seam is now `section_generation.py`).
>
> **W2 is reduced — E2E-02 (Qwen request-identity leakage) is RESOLVED BY DELETION** (no Qwen
> provider exists to mislabel). W2 residuals only: **E2E-03** (7 section lanes still call bare
> `load_dotenv()` rather than `bootstrap_apps_rg_env()` from `apps_rg/runtime/env_bootstrap.py`)
> and **E2E-04** (embedding fail-closed guard already exists in
> `apps_rg/runtime/chroma_precomputed_collection.py`; only a regression test is owed). These
> residuals are folded into W7 verification.
>
> Continuation runs on isolated worktree `aig-e2e-continue` (branch off `origin/main`
> `cb2235f915`) to avoid the multi-agent worktree collisions that paused this. Remaining order:
> **W4 → W5 → W6 → W7.**

## Context

Situation: AIG VP Global Head of Agentic AI end-to-end testing was run against:

- JD: `apps_rg/config/targeting/aig_vp_global_head_agentic_ai_jd.txt`
- Briefing: `apps_rg/config/targeting/aig_vp_global_head_agentic_ai_briefing.md`

Complication: Input validation passes and provider credentials are present, but the product run cannot certify. A 2026-06-07 verification pass against the actual code and RCA artifacts re-anchored every failure and corrected several root causes. The corrected picture: the integrated full run is killed early by a **ChromaDB use-after-close exception (E2E-11)** plus a **dispatch-status bucketing/poisoning defect (E2E-05)** that together mask the per-lane content failures; the per-lane failures themselves are a mix of a one-line crash (E2E-06), an artifact-fidelity mislabel (E2E-02), a competencies bundle **data gap** (E2E-07), and bullet-pool **selector** empty-output (E2E-09/E2E-10) that the artifacts mislabel as "provider blocked." Two items the original plan scoped are already shipped (E2E-03 env bootstrap ~80%, E2E-04 apps_rg embedding fail-closed) and two are refuted as written (E2E-08, E2E-14). Provider target is unchanged: `external_claude` / `claude-sonnet-4-6` is the apps_rg E2E target; Qwen/vLLM is diagnostic-only and must not appear in default E2E receipts.

Question: What must be fixed so the AIG JD plus briefing can run through all 11 apps_rg lanes with live providers, model-backed judges, and product-eligible X3 artifacts — without lowering deterministic gates and without touching shared core?

Answer: Fix in **causal order, not symptom order**. First unblock the integrated run (Chroma client lifecycle + dispatch isolation + truthful instrumentation) so a clean full-run signal exists. Then correct provider-receipt fidelity. Then the per-lane content fixes against a clean signal: executive-summary crash, competencies bundle/term data gap, bullet-lane selector containment, and InsurTech/EY proof slices. Close with a full AIG E2E run and a single reconciled root X3 closeout.

## Verification Provenance

This plan was hardened on 2026-06-07 by verifying each original RCA claim against the live code and the RCA artifacts under `artifacts/apps_rg/e2e_aig_apps_rg_e2e_20260607/`. What changed versus the first draft:

- **De-scoped (already shipped):** E2E-03 env bootstrap is ~80% landed in commit `b986071d16` (`apps_rg/runtime/env_bootstrap.py` wired into CLI, provider readiness, judge readiness, LLM clients). E2E-04 apps_rg embedding already fails closed and resolved local `BAAI/bge-m3` in the AIG run (`chroma_default_ef_used:false`). Both become **verify-only regression guards**.
- **Corrected root cause:** E2E-02 leakage is confined to `provider_request.json` (preflight already emits `NOT_APPLICABLE`). E2E-07 is a competency-bundle **data gap** (`llmops_reliability` orphan), not a finalizer bug, and the bundle fix alone clears only 2 of 4 X2 gates. E2E-09/E2E-10 are bullet-pool **selector `fallback_empty`** (the provider succeeded — `REAL_LLM`); the `BLOCKED` / `"provider blocked"` strings are stale/false labels.
- **Reframed (premise corrected):** E2E-08 — the AIG run actually shows **8 selections, `pass:true`**; the selector reads selection-stage artifacts by design, so the proposed repoint is dropped. E2E-14 — `X3A` is **DENY**, not success; the root already fails closed, so this becomes a vocabulary-reconciliation + exit-code task.
- **Non-viable option removed:** E2E-11 "remove the Rust path" — ChromaDB is the required dense-retrieval lane; removal is not viable. Fix is client-lifecycle.
- **Re-estimated:** W6 (role-episode proof) is net-new resume-sourced fact authoring + 2 bundle files + ~2 planners; 8k → ~12k, split into data and code phases.
- **Reordered:** the integrated unblock (E2E-11 + E2E-05) and truthful instrumentation move to the front because they gate observation of everything else.

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| W0 | W0.P1-W0.P3 | Evidence harness + truthful instrumentation (summarizer, traceback persistence, fixtures) | 4k | Current RCA artifacts remain available | DONE | Summarizer + fixtures cover all observed blockers; tracebacks persisted per lane |
| W1 | W1.P1-W1.P3 | **Unblock integrated dispatch**: ChromaDB client lifecycle (E2E-11) + three-state lane classification & per-lane exception isolation (E2E-05) | 8k | Chroma dense retrieval is required, not removable | DONE | Integrated run no longer dies on `RustBindingsAPI.bindings`; one lane failure cannot poison independent lanes; executed-X3_BLOCK ≠ never-attempted |
| W2 | W2.P1-W2.P4 | Provider-receipt fidelity (E2E-02) + env-bootstrap residual & embedding verify-only (E2E-03, E2E-04) | 6k | Provider selection remains external Claude default; preflight already correct | TODO | `provider_request.json` names the selected provider; `provider_request==provider_response` invariant test; apps_rg embedding fail-closed guard green |
| W3 | W3.P1-W3.P2 | Executive-summary crash (E2E-06) | 2k | Token-budget policy retained | DONE | No `UnboundLocalError`; `executive_summary` reaches provider + X1D artifacts |
| W4 | W4.P1-W4.P4 | Competencies bundle/term data gap + X1D guard (E2E-07, E2E-08 reframed) | 9k | JD/briefing stay targeting-only | TODO | `competencies` zero X2 failures; every taxonomy category carries lineage; X1D empty-selection guarded (no repoint) |
| W5 | W5.P1-W5.P3 | Bullet-lane selector containment (E2E-09, E2E-10) — containment-only | 6k | Bullet gate thresholds remain authoritative | TODO | Empty-selection fails once pre-X2 with the true reason; no false `provider blocked` label; no X2 cascade from an empty dict |
| W6 | W6.P1-W6.P4 | InsurTech/EY role-episode proof slices (E2E-12) — data + code | 12k | Real resume-sourced facts can be authored; facts are not inventable | TODO | `insurtech_*`/`ey_*` no longer hit `REQUIRED_PROOF_ABSENT`; lanes write full artifact set |
| W7 | W7.P1-W7.P4 | Full AIG E2E + root X3 reconciliation (E2E-14 reframed) | 6k | W1-W6 gates pass first | TODO | All 11 lanes attempt; zero `missing_lanes`; one X3 vocabulary at root; exit code unambiguous |

## Evidence

RCA artifacts under `artifacts/apps_rg/e2e_aig_apps_rg_e2e_20260607/` (verified 2026-06-07; corrected attributions noted):

| Probe | Artifact | Result (corrected) |
|---|---|---|
| Input dry run | `.../dryrun` | PASS input and embedding pre-dispatch |
| Full product run | `.../full_default` | FAIL: only `competencies` finalized. Killer = `ibm_bullets` ChromaDB `RustBindingsAPI.bindings` exception (E2E-11) cascading via `prior_abort`; `competencies` was executed-X3_BLOCK but mislabeled `LANE_DISPATCH_EXIT_ERROR` (E2E-05) |
| Executive summary, all judges | `.../section_executive_summary_external_all_judges` | FAIL before generation: `resolve_scratch_max_output_tokens` UnboundLocalError at `executive_summary_lane.py:1730`. No traceback file was captured (W0 fixes this) |
| Competencies, qwen_vllm | `.../section_competencies_qwen` | REAL_LLM, X2 BLOCK on 4 gates (generic-category <3 terms ×5, `llmops_reliability` missing lineage, `retrieval_context` family). **X1D actually reports 8 selections, `pass:true`** (refutes E2E-08 as written) |
| Unify bullets, external Claude | `.../section_unify_bullets_external` | **Provider succeeded (REAL_LLM)**; selector `fallback_empty` (0 paths ≥ 0.72) → empty dict cascades 15 X2 failures. `BLOCKED:` label is empty/misleading (E2E-09) |
| IBM bullets, external Claude | `.../section_ibm_bullets_external` | **Provider succeeded (REAL_LLM, valid JSON)**; same selector `fallback_empty`; `"provider blocked"` is a stale/false `parse_error` default (E2E-10) |
| InsurTech bullets, external Claude | `.../section_insurtech_bullets_external` | `REQUIRED_PROOF_ABSENT`: graph-skills allocation produced an empty slice (`section_graph_skills_proof_pool.py:410`). In the full run this lane was `PRE_RUN_BLOCKED` by the upstream IBM crash, so the proof gap is only observable standalone (E2E-12) |
| Judge transport probe | `.../judge_transport_probe` | OpenAI/Anthropic/Gemini all model-backed; no credential/transport blocker (E2E-13) |

## Execution Target And Provider Policy

Decision (unchanged):

- Production AIG E2E target provider: `external_claude`.
- Target generation model: `claude-sonnet-4-6`, sourced from `ANTHROPIC_MODEL` or provider profile resolution.
- Product E2E preflight treats Qwen/vLLM as `NOT_APPLICABLE` when `external_claude` is selected. **Already implemented** — `apps_rg/runtime/pre_dispatch_preflight.py:149-151`; verified `NOT_APPLICABLE` in the AIG preflight receipts.
- Product E2E artifacts must not show Qwen model/base URL in request, response, preflight, or provider-call receipts for Claude-selected lanes. **Residual leak is `provider_request.json` only** (E2E-02 / W2).
- Qwen/vLLM status: legacy diagnostic/dev-only explicit provider. Not part of the AIG E2E acceptance path.

Enforcement:

- `APPS_RG_MODULAR_LANE_PROVIDER=external_claude` is the default for AIG E2E.
- `--provider qwen_vllm` may remain accepted only for explicit local comparison tests, labeled `diagnostic_non_product_default`.
- Any Qwen metadata in an external-Claude `provider_request.json` / `provider_response.json` / pre-dispatch receipt / `section_provider_calls.json` is a failure. The new `provider_request==provider_response` invariant (W2) makes this deterministic.

Definition of running:

- Dry-run validates AIG inputs.
- Full run executes all 11 lanes, not just artifact collection.
- Every lane has one of: `X3_ALLOW`, accepted product-review state with a single actionable blocker, or pre-X2 upstream block with exact missing proof/config.
- The target happy path is `external_claude` through generation and model-backed X1D judges, with no default Qwen dependency.
- `integrated_lane_evidence_status.json` reports zero `missing_lanes`.

## Hardened RCA Inventory

Verdict legend: **VERIFIED** (claim + fix correct) · **NARROWED** (real but smaller than stated) · **DONE** (already shipped → verify-only) · **MISDIAGNOSED→corrected** (symptom real, cause/locus corrected) · **REFUTED→reframed** (premise wrong).

| ID | Item | Verdict | Corrected root cause + anchor | Fix (bounded, apps_rg-only) | Verification |
|---|---|---|---|---|---|
| E2E-01 | Branch/surface ambiguity | NARROWED | Branch-per-chat cuts a fresh `chat/<stamp>`; `apps_rg_e2e` is not in play | Implement on the active chat branch; keep unrelated dirty files unstaged | `git status --short --branch` clean before edits |
| E2E-02 | Qwen leakage into Claude path | NARROWED | `build_qwen_request()` hardcodes `provider_requested="qwen_vllm"` (`qwen_vllm_provider.py:230-241`); 7 lanes call it before routing and write `provider_request.json`. Preflight already correct (`pre_dispatch_preflight.py:149-151`). Precedent fix exists at `executive_summary_lane.py:2010-2018` | Provider-neutral request builder driven by selected profile; thread `provider_requested/url/model` from the selected provider. De-scope preflight | External-Claude `provider_request.json` names Claude; `provider_request==provider_response` invariant test passes |
| E2E-03 | `.env`/provider readiness | DONE (residual) | Canonical bootstrap shipped in `b986071d16` (`env_bootstrap.py` wired into CLI `__main__.py:717-719`, provider `external_provider.py:75,168`, judges `executive_summary_x1d.py:285`, clients `_llm_client.py:66,214`). Residual: 7 lane modules still bare `load_dotenv()` (e.g. `unify_bullets_lane.py:40`) | Route the 7 lane modules' bare `load_dotenv()` through `bootstrap_apps_rg_env()`; otherwise verify-only | Provider readiness passes with keys only in root `.env`; injected empty env still fails closed |
| E2E-04 | Embedding fail-closed | DONE (verify-only) | apps_rg resolver already correct: `embedding_settings.py` maps slug→`BAAI/bge-m3`, `_resolve_local_bge_path` honors `APPS_RG_EMBEDDING_MODEL_PATH`, fail-closed branches + `ForbidChromaDefaultEmbeddingFunction`. AIG run: `chroma_default_ef_used:false`, `source:local`. The generic default-EF fallback in `agentic_core/.../gptcache_client.py:120-126` is **out of scope** | Add an apps_rg regression guard asserting fail-closed (no default EF, local BGE). No code change to the resolver | Product-strict embedding test proves no default-EF fallback for apps_rg |
| E2E-05 | Full run: 1 executed / 10 missing | VERIFIED | Two conflations: product-bar bucketing stamps executed-X3_BLOCK `competencies` as `LANE_DISPATCH_EXIT_ERROR` (`modular_resume_generation.py:182-243`, `:216-217`; `product_output_policy.py:75-119`); and the IBM crash poisons 7 lanes via `should_skip_remaining_waves` (`managed_section_lane_dispatcher.py:18-28`). Packaging already distinguishes EXECUTED vs NOT_RUN (`integrated_lane_evidence_packaging.py`) | Emit `EXECUTED_X3_BLOCK` / `PRE_RUN_BLOCKED` / `MISSING_NOT_ATTEMPTED` from the product-bar layer; isolate per-lane exceptions so independent lanes still run | Failed full run reports every attempted lane with precise status; no false missing-lane classification |
| E2E-06 | Executive summary UnboundLocalError | VERIFIED | Use at `executive_summary_lane.py:1730` precedes the function-local import at `:1870-1872` inside `run_executive_summary_execution` (def `:1611`); symbol owned by `executive_summary_context_limits.py:101`. No circular-import risk | Delete the local import block; add module-scope `from ...executive_summary_context_limits import resolve_scratch_max_output_tokens` | Symtable/bytecode guard asserts the symbol is not function-local; lane reaches provider + X1D artifacts |
| E2E-07 | Competencies X2 block | MISDIAGNOSED→corrected | **Data gap, not finalizer code**: category_id `llmops_reliability` is absent from every bundle's `target_taxonomy_category_ids` in `competency_capability_bundles.json` (the `ccb_llmops_reliability` bundle targets the wrong ids). Stamp skips it (`competency_capability_evidence.py:245-262`). Gate threshold `GENERIC_CATEGORY_MIN_GRAPH_TERMS=3` (`competencies_quality_x2.py:76`). Bundle fix alone clears only 2/4 gates | (1) Add `llmops_reliability` to the bundle's targets; (2) term-fill ≥3 graph-backed terms per generic category; (3) cover `retrieval_context` family; (4) add a coverage invariant: every taxonomy category_id ∈ ≥1 bundle | AIG competencies zero X2 failures; all 8 categories carry `competency_bundle_id`/`capability_family`/`graph_skill_node_ids` |
| E2E-08 | Competencies X1D "0 selections" | REFUTED→reframed | AIG run shows **8 selections, `pass:true`** (`x1d_llm_judge_outputs.json`). Selector `competencies_pool_x1d_judge_rows` (`employment_bullet_pool.py:249,269-281`) reads selection-stage artifacts **by design**; `competencies_section_output.json` is a later stage — repoint would break stage separation | Do **not** repoint. Add an empty-selection guard (`employment_bullet_pool.py:277-286`) that emits a BLOCKED/diagnostic row instead of a silent 0. Confirm whether the external-Claude competencies section reproduces "0" (not inspected this run) | X1D never silently scores 0 on empty selection; external-Claude section checked |
| E2E-09 | Unify bullets reach X2 blocked/empty | MISDIAGNOSED→corrected | **Provider succeeded (`REAL_LLM`)**; selector returns `fallback_empty` (0 paths ≥ 0.72) → empty dict shaped at `unify_bullets_lane.py:819`, mislabeled `BLOCKED:` at `:1149`. Shared seam: `bullet_lane_generation.py` (`_generate_employment_bullet_lane:74`) | Pre-X2 empty-selection guard in the shared helper → single deterministic block with reason `selector_returned_no_candidates_above_threshold`; fix the empty `BLOCKED` label. **Containment-only** | Empty selection fails once pre-X2; no 15-failure cascade; reason names the selector |
| E2E-10 | IBM bullets reach X2 blocked | MISDIAGNOSED→corrected | Same selector `fallback_empty`; `"provider blocked"` is a stale default (`ibm_bullets_lane.py:966-968`) contradicted by a valid `provider_response.json` | Share the W5 empty-selection guard; stop emitting `"provider blocked"` when `runtime_generation_status==REAL_LLM` (artifact-honesty) | IBM fails once pre-X2 with the true reason; no false `provider blocked` |
| E2E-11 | Integrated IBM Chroma exception | VERIFIED (option corrected) | `RustBindingsAPI` is **ChromaDB 1.5.5's class (not in-repo)**; `del self.bindings` on stop (`chromadb/api/rust.py:131`) → use-after-close when a closed/`atexit`-torn `PersistentClient` is reused across lanes (`tools/retrieval/vector_store.py:213-244`). Caught at `section_lane_executor.py:93`. **Dense retrieval is required — "remove Rust path" is not viable** | Detect dead/closed client and rebuild lazily; scope client lifetime per integrated run (don't bind teardown to `atexit` for a shared client); emit a structured trace naming the ChromaDB origin | Integrated IBM no longer throws `RustBindingsAPI.bindings`; one Chroma teardown cannot zero out 10 lanes |
| E2E-12 | InsurTech/EY proof absent | VERIFIED (under-scoped) | 4 lanes registered (`role_episode_lane.py:75-112`) with PA templates + contracts present, but empty-slice `ValueError` at `section_graph_skills_proof_pool.py:410`: ledger has **0 genuine InsurTech and 0 genuine EY-employer facts** (`candidate_fact_ledger.py:18-20`); no `insurtech_/ey_role_episode_bundles.json`; EY hints `audit`/`regulatory` false-positive on generic facts; `company_lane` empty on all rows | Author HIGH-confidence InsurTech/EY facts (resume-sourced) + 2 bundle files (mirror `ibm_/unify_role_episode_bundles.json`); add ~2 dedicated planners; tighten EY hints; populate `company_lane`. Split data (P1) / code (P2). ~12k | All 4 lanes write `selected_fact_plan.json`, FEC, provider req/resp, X1D, X2, X3; empty-slice error names required fact families |
| E2E-13 | Judges are content failures | VERIFIED | All three judges model-backed; failures are rubric/content, not transport | Keep judge transport probe separate; tune rubrics only after content is product-shaped | Judge matrix model-backed; content failures cite candidate-specific reasons |
| E2E-14 | Root X3/product status confusing | REFUTED→reframed | `X3A` = **DENY** (`disposition.py:18-20`), excluded from `_SUCCESS_X3` (`canonical_dispatch.py:31`); root already fails closed (`outcome_authorized:false`). Real issue: three X3 vocabularies (lane `X3_BLOCK` `executive_summary_x3.py`; root `X3A–E` `disposition.py`; `whole_run_exit.py:16-19` hybrid) + `process_exit_code:0` override (`shell_exit_overridden_for_inspection`) | Single root closeout mapping lane↔root codes + per-required-lane attempted/executed/X3/authorized; assert vocabulary equivalence; non-zero exit on X3_BLOCK outside explicit inspection mode | Root closeout uses one vocabulary; exit code matches disposition |

## Critical Path To Running

1. **Unblock the integrated run first.** Fix the ChromaDB client lifecycle (E2E-11) and dispatch bucketing/isolation (E2E-05) so one exception cannot poison the run and executed-but-blocked lanes are not reported as missing. Add traceback persistence + three-state classification so every failed lane is legible.
2. **Make receipts truthful.** Drive `provider_request.json` from the selected provider (E2E-02); finish the env-bootstrap residual and assert the apps_rg embedding fail-closed guard (E2E-03/04 verify-only).
3. **Fix the executive-summary crash** (E2E-06) — a one-line shadow that blocks a required lane before providers/judges.
4. **Fix deterministic competencies** (E2E-07) before judge calibration — a bundle data gap plus term-fill and capability-family coverage; reframe X1D (E2E-08) to an empty-selection guard only.
5. **Contain bullet-lane selector empty-output** (E2E-09/E2E-10) so an empty selection fails once with the true reason instead of cascading 15 X2 failures under a false `provider blocked` label.
6. **Populate InsurTech/EY proof slices** (E2E-12) — resume-sourced facts + bundles + planners.
7. **Run targeted section probes, then full AIG E2E, then the judge matrix**, and reconcile the root X3 vocabulary + exit code (E2E-14).
8. Close only when every required lane has an auditable X3 or a single accepted product-review blocker.

## Acceptance Matrix

| Checkpoint | Must Pass Before | Acceptance |
|---|---|---|
| Branch hygiene | W1 code edits | Implementation is on the active chat branch; unrelated dirty files are not staged |
| Integrated unblock | Any full run | Full run does not die on `RustBindingsAPI.bindings`; an independent lane's failure does not skip unrelated lanes |
| Lane-status truth | Final E2E | Each lane classified `EXECUTED_X3_BLOCK` / `PRE_RUN_BLOCKED` / `MISSING_NOT_ATTEMPTED`; traceback persisted on exception |
| Provider fidelity | Any AIG product run | `provider_request.json` names the selected provider; `provider_request==provider_response`; no Qwen base URL in external lanes |
| Env/embedding | Provider preflight / generation | `.env`-only credentials visible to provider + judge readiness; apps_rg embedding fail-closed guard green (no default EF) |
| Executive summary | Full run | Lane reaches provider response and X1D artifacts; no `UnboundLocalError` |
| Competencies | Bullet-dependent review | All 8 categories carry lineage; zero X2 failures; coverage invariant (every category_id ∈ ≥1 bundle) holds |
| Bullets (Unify/IBM) | Narrative/dependency lanes | Empty selection fails once pre-X2 with the true reason; no false `provider blocked`; valid candidates satisfy product shape |
| InsurTech/EY | Full run | Proof slices exist; lanes no longer stop at `REQUIRED_PROOF_ABSENT` |
| Root X3 | Final certification | One X3 vocabulary at root; exit code matches disposition; root cannot read as success while a required lane is X3_BLOCK |
| Judges | Final certification | OpenAI/Anthropic/Gemini rows model-backed or with precise transport blockers; content failures cite candidate-specific reasons |

## Definition of Done

Plan-level DoD — all must hold before this plan is marked Completed:

| # | Definition of Done | Verification |
|---|---|---|
| 1 | **Smoke run (executable surface):** full AIG E2E completes and emits all 11 lane artifact sets | `python -m apps_rg --target-company AIG ... --artifact-dir artifacts/apps_rg/e2e_aig_verify/full` exits cleanly; `integrated_lane_evidence_status.json` has zero `missing_lanes` |
| 2 | No lane dies on `RustBindingsAPI.bindings`; one lane's failure cannot poison independent lanes (E2E-11/E2E-05) | W1 isolation test + clean full run; lanes classified `EXECUTED_X3_BLOCK`/`PRE_RUN_BLOCKED`/`MISSING_NOT_ATTEMPTED` |
| 3 | Every external-Claude `provider_request.json` names the selected provider — no Qwen leak (E2E-02) | `provider_request==provider_response` invariant test green; metadata-leakage scan clean |
| 4 | `executive_summary` reaches provider + X1D artifacts with no `UnboundLocalError` (E2E-06) | W3 symtable/bytecode guard + section run |
| 5 | `competencies` has zero X2 failures; all 8 categories carry lineage; no orphan category_id (E2E-07) | W4 run + coverage-invariant test |
| 6 | Bullet empty-selection fails once pre-X2 with the true reason; no false `provider blocked` (E2E-09/10) | W5 standalone Unify/IBM runs |
| 7 | `insurtech_*`/`ey_*` no longer return `REQUIRED_PROOF_ABSENT` (E2E-12) | W6 section runs write full artifact sets |
| 8 | Root closeout uses one X3 vocabulary; process exit code matches disposition (E2E-14) | W7 closeout artifact + exit-code assertion |
| 9 | Targeted regression slice green | `python -m pytest -q tests/unit/apps_rg tests/_apps_contract -k "apps_rg or executive_summary or competencies or bullet or x1d or provider_request or embedding"` |

Verification vs Deferral:

| Item | Verified in-plan | Deferred (follow-up) |
|---|---|---|
| Integrated unblock · provider fidelity · exec-summary · competencies · bullets containment · role-episode proof · root X3 reconcile | Yes — W1–W7 | — |
| Why all bullet self-consistency paths score < 0.72 (content quality) | — | Yes — `## Deferred Follow-ups` |
| Generic L2 cache default-EF fallback (`agentic_core/.../gptcache_client.py`) | — | Yes — `## Out Of Scope` / separate core plan |

## Wave 0 - Evidence Harness & Truthful Instrumentation

WAVE_ID: W0
WAVE_STATUS: TODO
WAVE_COMPLETE: NO

Scope:
- Add `tools/apps_rg/summarize_e2e_run.py` that reads run artifacts and emits a compact matrix of provider, model, X1D, X2, X3, and blocker statuses, differentiating `EXECUTED_X3_BLOCK`, `PRE_RUN_BLOCKED`, and `MISSING_NOT_ATTEMPTED`.
- Persist exception tracebacks per lane: the section dispatch catch (`section_lane_executor.py:93`) writes a `section_exception_trace.json` (module, line, full traceback) into the lane artifact dir. (The RCA dir captured no tracebacks — this closes that gap.)
- Add regression fixtures referencing the AIG JD and briefing paths; assert fixture hashes.
- Preserve current RCA artifact paths + branch provenance + selected-provider policy in an RCA receipt.

DoD:
- `python tools/apps_rg/summarize_e2e_run.py <artifact-dir>` works for full and section runs.
- Summarizer differentiates `EXECUTED_X3_BLOCK`, `PRE_RUN_BLOCKED`, `MISSING_NOT_ATTEMPTED`.
- A simulated lane exception writes `section_exception_trace.json` with module + line.
- AIG fixture hashes asserted in a unit/contract test. No provider calls required for W0 tests.

## Wave 1 - Unblock Integrated Dispatch

WAVE_ID: W1
WAVE_STATUS: TODO
WAVE_COMPLETE: NO

Scope:
- **E2E-11 (ChromaDB client lifecycle):** in `tools/retrieval/vector_store.py` (client construction + atexit at `:213-244`), detect a dead/closed `PersistentClient` (missing `.bindings`) and lazily rebuild; scope client lifetime to the integrated run rather than a shared `atexit`-bound singleton. Emit a structured trace naming the ChromaDB origin if it still fails. **Do not remove the dense-retrieval path.**
- **E2E-05 (lane-status truth + isolation):** in `_phase1_materialize_lane_run_dir` (`modular_resume_generation.py:182-243`) and `product_output_policy.py:75-119`, emit `EXECUTED_X3_BLOCK` when a real run dir exists with X3_BLOCK (distinct from `LANE_DISPATCH_EXIT_ERROR` and `PRE_RUN_BLOCKED`). Decouple `should_skip_remaining_waves` (`managed_section_lane_dispatcher.py:18-28`) from independent (non-dependency) lanes so one exception cannot abort them.
- Thread the three-state classification into `integrated_lane_evidence_status.json` and `section_provider_calls.json`.

DoD:
- A full run with a deliberately-faulted lane: the faulted lane is isolated; independent lanes still execute.
- `competencies` (executed, X3_BLOCK) is classified `EXECUTED_X3_BLOCK`, not `MISSING_LANE_RUN` / `LANE_DISPATCH_EXIT_ERROR`.
- Integrated IBM no longer raises `RustBindingsAPI ... no attribute bindings`; if Chroma still fails, the trace names the exact module/line.
- Chroma/Rust integrated exceptions include stack trace, module, and remediation hint.

## Wave 2 - Provider Fidelity & Env/Embedding Guards

WAVE_ID: W2
WAVE_STATUS: REDUCED — E2E-02 RESOLVED BY DELETION (Qwen-removal PR #256); residuals folded into W7
WAVE_COMPLETE: N/A

> **2026-06-08 reconciliation:** the Qwen-removal refactor (PR #256) deleted
> `qwen_vllm_provider.py` and `build_qwen_request()` entirely, so **E2E-02 (the unconditional
> `qwen_vllm` request identity) can no longer occur** — there is no Qwen provider to mislabel.
> External Claude is the sole generator. The original W2 scope below is retained for provenance;
> only E2E-03 and E2E-04 residuals remain, verified in W7.

Scope (original — E2E-02 portion now MOOT):
- ~~**E2E-02:** replace the unconditional `build_qwen_request()` identity with a provider-neutral
  request builder.~~ **MOOT — provider deleted in PR #256.**
- Add a contract invariant: for every lane, `provider_request.json.provider_requested == provider_response.json.provider_requested` and no `localhost:8000` base URL in an external-Claude request. Extend `tests/_apps_contract/test_apps_rg_generation_model_env_boundary.py`.
- **E2E-03 residual:** route the 7 lane modules' bare `load_dotenv()` through `bootstrap_apps_rg_env()`; emit the `AppsRgEnvBootstrapResult` into the preflight receipt so "did `.env` load?" is observable. (Core bootstrap already shipped — verify-only.)
- **E2E-04 verify-only:** add an apps_rg regression guard asserting the embedding path stays fail-closed (no default EF; resolves local `BAAI/bge-m3`). No resolver change.

DoD:
- External-Claude `provider_request.json` names Claude; the `provider_request==provider_response` invariant test passes; a metadata-leakage scan finds no Qwen model/base URL outside explicit diagnostic labels.
- Provider readiness passes when keys are present only in root `.env`; injected empty env still fails closed.
- apps_rg embedding fail-closed guard is green (`chroma_default_ef_used:false`, local source).

## Wave 3 - Executive Summary Crash

WAVE_ID: W3
WAVE_STATUS: TODO
WAVE_COMPLETE: NO

Scope:
- Delete the function-local import block at `executive_summary_lane.py:1870-1872` and add a module-scope `from apps_rg.runtime.sections.executive_summary_context_limits import resolve_scratch_max_output_tokens` (no circular-import risk — verified). Leave the call sites at `:1730` and `:1874` unchanged.
- Add a deterministic regression: a symtable/bytecode guard asserting `resolve_scratch_max_output_tokens` is not function-local in `run_executive_summary_execution` (provider-independent, fast).
- Re-run executive summary with `--x1d-judges openai_chatgpt,anthropic_claude,gemini_pro`.

DoD:
- No `UnboundLocalError`; provider request/response artifacts written.
- All three judge keys are model-backed with verdicts or blocked with precise transport reasons.
- Executive-summary X2/X3 artifacts exist even when final verdict is not ALLOW.

## Wave 4 - Competencies Bundle/Term Data Gap

WAVE_ID: W4
WAVE_STATUS: TODO
WAVE_COMPLETE: NO

Scope:
- **E2E-07 (data):** add `llmops_reliability` to `target_taxonomy_category_ids` of the `ccb_llmops_reliability` bundle in `apps_rg/fact_inventory/competency_capability_bundles.json`.
- **E2E-07 (terms):** ensure `augment_bound_category_family_terms` (`competency_capability_evidence.py:317`) injects ≥3 graph-backed terms per generic category (gate `competencies_quality_x2.py:76`); cover the `retrieval_context_engineering` family so `x2_required_capability_families_covered` reaches 7/7.
- **Coverage invariant:** add a test asserting every category_id in `executive_capability_taxonomy.yaml` appears in ≥1 bundle's `target_taxonomy_category_ids`; make `stamp_competency_bundle_bindings` log a violation instead of silently `continue` (`competency_capability_evidence.py:255`).
- **E2E-08 (reframed):** add an empty-selection guard in `competencies_pool_x1d_judge_rows` (`employment_bullet_pool.py:277-286`) emitting a BLOCKED/diagnostic row instead of a silent 0; **do not** repoint at `competencies_section_output.json`. Check whether the external-Claude competencies section reproduces "0 selections."
- Keep JD/briefing targeting-only.

DoD:
- AIG `competencies` (`external_claude`) has zero X2 failures; `qwen_vllm` zero X2 failures or a provider-specific judge-only failure with no deterministic gate failure.
- Each of the 8 categories carries `competency_bundle_id`/`capability_family`/`graph_skill_node_ids` and ≥ the required graph-backed term count.
- The coverage invariant test passes (no orphan category_id).
- X1D never silently reports `0 category selections` on a non-empty merge; empty selection yields a diagnostic row.

## Wave 5 - Bullet Lane Selector Containment

WAVE_ID: W5
WAVE_STATUS: TODO
WAVE_COMPLETE: NO

Scope (containment-only — the deeper "why all SC paths < 0.72" content-quality dig is a `## Deferred Follow-ups` item, not implemented here):
- In the shared helper `bullet_lane_generation.py` (`_generate_employment_bullet_lane:74`), detect `selection_mode=="fallback_empty"` / `bullets_in_merged==0` **before** X2 and emit a single deterministic block with reason `selector_returned_no_candidates_above_threshold` (mirroring `upstream_evidence_block.py:159`), instead of letting the empty dict reach X2.
- Fix the misleading labels: the empty `BLOCKED:` at `unify_bullets_lane.py:1149` and the stale `"provider blocked"` default at `ibm_bullets_lane.py:966-968` (do not emit "provider blocked" when `runtime_generation_status==REAL_LLM`). Distinguish "provider blocked" from "selector empty."
- Record the sub-0.72 selector scores in the block artifact so the follow-up investigation has data.

DoD:
- `unify_bullets` and `ibm_bullets` standalone AIG runs: an empty selection fails once pre-X2 with `selector_returned_no_candidates_above_threshold`; no 15/6-failure X2 cascade from an empty dict.
- No artifact says `provider blocked` while `provider_response.json` is `REAL_LLM`.
- A valid (non-empty) selection still produces product-shaped candidates and runs X2 normally.

## Wave 6 - Role Episode Proof Slices (InsurTech/EY)

WAVE_ID: W6
WAVE_STATUS: TODO
WAVE_COMPLETE: NO

Scope (split data / code; ~12k — the largest, riskiest wave):
- **W6.P1-P2 (data, resume-sourced — facts are not inventable):** author HIGH-confidence InsurTech and EY candidate facts into `master_candidate_skills_fact_ledger_*.json`; populate `company_lane`/`company`/`domain_family` so `_ledger_rows_matching_company_hints` matches reliably (today all rows have empty `company_lane`). Author `insurtech_role_episode_bundles.json` + `ey_role_episode_bundles.json` mirroring `ibm_/unify_role_episode_bundles.json`.
- **W6.P3-P4 (code):** add dedicated graph-ranked planners for InsurTech/EY (mirror `_graph_ranked_ibm_bullets_plan`) instead of the brittle generic company-hint fallback; tighten EY hints (`audit`/`regulatory` currently false-positive — require an explicit EY/Ernst/Young employer tag); make the empty-slice error (`section_graph_skills_proof_pool.py:410`) name the required fact families.
- Keep JD/briefing targeting-only.

DoD:
- `insurtech_bullets`, `insurtech_narrative`, `ey_bullets`, `ey_narrative` no longer return `REQUIRED_PROOF_ABSENT`.
- Each writes `selected_fact_plan.json`, FEC, provider request/response, X1D, X2, X3.
- Missing-proof tests fail closed before provider generation with named required proof families.

## Wave 7 - Full AIG E2E + Root X3 Reconciliation

WAVE_ID: W7
WAVE_STATUS: TODO
WAVE_COMPLETE: NO

Scope:
- Run full AIG E2E on the active chat branch; run the focused section matrix for `external_claude` (qwen_vllm only as explicit diagnostic if retained).
- Run the judge transport matrix for OpenAI/Anthropic/Gemini.
- **E2E-14:** add a single root closeout artifact mapping lane↔root X3 codes with per-required-lane attempted/executed/X3/product-authorized; assert vocabulary equivalence across `executive_summary_x3.py` / `disposition.py` / `whole_run_exit.py`; make the process exit code non-zero on X3_BLOCK outside explicit inspection mode (`shell_exit_overridden_for_inspection`).
- Produce a Qwen disposition note: diagnostic-only, with tests proving non-default behavior.

DoD:
- Full run executes all 11 lanes; `integrated_lane_evidence_status.json` reports zero missing lanes.
- Root closeout uses one X3 vocabulary; exit code matches disposition; root cannot read as success while a required lane is X3_BLOCK.
- Root `generate_resume_step_receipt.json` has `decisive_status=PASS` or an explicitly accepted product-review state with a single non-ambiguous blocker per remaining non-ALLOW outcome.
- Closeout shows external-Claude generation path, model-backed judges, no default Qwen dependency.

## Verification Commands

```text
python -m pytest -q tests/unit/apps_rg tests/_apps_contract -k "apps_rg or executive_summary or competencies or bullet or x1d or provider_request or embedding"
python -m apps_rg --target-company AIG --target-role "VP Global Head of Agentic AI Solutions" --target-level VP --jd apps_rg/config/targeting/aig_vp_global_head_agentic_ai_jd.txt --manual-brief apps_rg/config/targeting/aig_vp_global_head_agentic_ai_briefing.md --dry-run --artifact-dir artifacts/apps_rg/e2e_aig_verify/dryrun
python -m apps_rg --target-company AIG --target-role "VP Global Head of Agentic AI Solutions" --target-level VP --jd apps_rg/config/targeting/aig_vp_global_head_agentic_ai_jd.txt --manual-brief apps_rg/config/targeting/aig_vp_global_head_agentic_ai_briefing.md --artifact-dir artifacts/apps_rg/e2e_aig_verify/full
python -m apps_rg --target-company AIG --target-role "VP Global Head of Agentic AI Solutions" --target-level VP --jd apps_rg/config/targeting/aig_vp_global_head_agentic_ai_jd.txt --manual-brief apps_rg/config/targeting/aig_vp_global_head_agentic_ai_briefing.md --section executive_summary --provider external_claude --x1d-judges openai_chatgpt,anthropic_claude,gemini_pro --artifact-dir artifacts/apps_rg/e2e_aig_verify/executive_summary_all_judges
python tools/apps_rg/summarize_e2e_run.py artifacts/apps_rg/e2e_aig_verify/full
```

## Out Of Scope

- **`agentic_core/L4_state/cache/gptcache_client.py:120-126` default-EF fallback** — generic, fleet-wide infrastructure (apps_qna + core also consume it). The apps_rg embedding path already fails closed, so this is not an AIG-E2E blocker. Touching it would require a migration receipt + profile-gating and is out of bounds for this apps_rg plan. Captured under `## Deferred Follow-ups`.
- Changing the factual authority model that keeps JD/briefing as targeting/context only.
- Lowering deterministic gates just to achieve X3_ALLOW.
- Replacing model-backed judges with mocks.
- Treating packaging or artifact collection as product certification.
- Removing the ChromaDB dense-retrieval path (required, not a diagnostic accelerator).

## Deferred Follow-ups

Captured here, not implemented in this plan (surface via `spawn_task` if/when prioritized):

- **Bullet-pool selector content quality (the < 0.72 root question):** W5 contains the cascade but does not investigate *why* every self-consistency path scores below the 0.72 gate (prompt shape, threshold calibration, or candidate quality). This is a separate content-tuning effort with unbounded scope; do not fold into the bounded remediation.
- **Generic L2 cache fail-open (`gptcache_client.py`):** if a fleet-wide "no default-EF fallback under product-strict" policy is ever desired, it belongs in a separate `agentic_core`-scoped plan with a migration receipt and a profile flag, not here.
