---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\apps_rg_agentic_spine_refactor_plan.md'
original_relative_path: 'apps_rg_agentic_spine_refactor_plan.md'
source_sha256: 4df97c3119a99b5dc1b3f804eb6ae378f65fa77b3abf0b61de9d883be712c160
recovered_status: SURVIVED_IN_CURRENT
last_commit: '315fd11926d'
last_commit_date: '2026-05-06 06:26:53 -0400'
created_date: '2026-05-04'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# apps_rg Agentic Spine Refactor Plan

## 1. Executive Summary

**Target**: apps_rg remains `R4_SINGLE_ACTION` with an **L2-owned deterministic HOP pipeline**, preloaded context (JD + master resume + company brief from disk), no C0 runtime retrieval, no L3 DAG, no runtime HITL, and optional semantic cache commit only through Exit → CommitRequest → UWG → L4.

**Scope**: Bring `apps_rg/AGENTIC_SPINE.md` and runtime implementation into full alignment with the canonical agentic core spine documented in `docs/reference/04_L2_Execute/` and `docs/reference/05_Exit_Evaluation_and_Control/`. Preserve all domain behavior — on-demand résumé generation, preloaded inputs, deterministic HOP pipeline, JSON/narrative/DOCX outputs, out-of-band candidate review, no ATS submission, no LinkedIn writes, no hidden live research.

**Key corrections** (16 items from the task specification):
1. Rename "Inner DAG" → "L2-owned deterministic HOP pipeline"
2. Preserve L3 bypass
3. Add R1A exact cache before R1B
4. Strengthen R1B cache key
5. Resolve L4 durable-write contradiction (enable optional Exit → UWG path)
6. Fix Prompt Assembly posture (APP_LOCAL_PA_COMPATIBLE for HOP 3)
7. Remove hidden Tavily/live research from runtime
8. Fix Exit disposition ownership (HOPs emit sealed packets, not X3)
9. Remove EXIT_PARTIAL — map to canonical X3D/X3E + terminal_class
10. Fix HITL posture consistency
11. Fix Runtime Authority (sandbox write + model egress, not "none")
12. Clarify FEC semantics (local evidence contract, not C0 FEC)
13. Map HOPs to L2 E1–E5
14. Update cross-app integration boundaries
15. Add 18+ tests
16. Define proof / acceptance criteria

---

## 2. Current Findings

### Already Aligned

| Item | Evidence |
|------|----------|
| Route type R4_SINGLE_ACTION | `spine_manifest.yaml` line 28 |
| L3 bypass | `spine_manifest.yaml` expected_l3_path=BYPASSED |
| No C0 vector retrieval | JD/resume/brief loaded from disk paths |
| R1B semantic cache with policy/blueprint validation | `cache/r1b_adapter.py` lines 130–147 |
| R5 briefing prerequisite gate | `__main__.py` lines 530–591 |
| Exit V6 integration via `_maybe_run_exit_hook` | `__main__.py` line 627 |
| 7-stage HOP pipeline topology | `config/hop_pipeline.py` |
| L1 JDPlan semantic extraction (pure, no LLM) | `L1_cognition/jd_planner.py` |
| Post-pipeline narrative pass + DOCX export | `__main__.py` lines 829–914 |
| FEC producer with source ladders | `cert/fec_producer.py` |
| Governed run context wrapping | `__main__.py` line 508 `governed_run(cfg)` |

### Misaligned

| # | Issue | Location | Severity |
|---|-------|----------|----------|
| F1 | "Inner DAG" terminology — calls HOP pipeline an "Inner DAG" while L3=BYPASSED | `AGENTIC_SPINE.md` section header | Medium — terminology drift |
| F2 | No R1A exact cache — only R1B exists | `__main__.py` lines 511–528; `AGENTIC_SPINE.md` | High — missing canonical route path |
| F3 | R1B cache key too thin — `ResumeGenerationIntent.to_cache_key_dict()` missing jd_text_hash, master_resume_hash, company_brief_hash, output_schema_hash, prompt_template_hash, model_lane_hash, freshness_class, cache_schema_version | `cache/r1b_adapter.py`, `types/intent_payload.py`, `utils/intent_builder.py` | High — cache could return stale/incompatible output |
| F4 | L4 contradiction — "Output Chunking + R1B Commit via UWG" in spine flow vs "No L4 durable state writes" / "No CommitRequest" in Non-Goals | `AGENTIC_SPINE.md` flow diagram vs Non-Goals section | High — contradictory |
| F5 | Prompt Assembly = False — HOP 3 calls Qwen/Anthropic without prompt manifest, hash, policy binding, replay metadata | `AGENTIC_SPINE.md` characteristics table; `reasoning/RgResumeOrchestrator.py` | High — invisible prompt construction |
| F6 | Hidden Tavily supplement inside runtime — `--auto-research-tavily` flag calls `tavily_supplement.supplement_company_brief()` from within `narrative_pass.py` via `company_research_loader._try_tavily_supplement()` | `integrations/company_research_loader.py` lines 54–56, 71, 79–81, 152–161 | High — violates "no C0/live retrieval" |
| F7 | Hidden `--auto-research-internal` invokes `CompanyBriefEngine` (apps_research import) inside runtime | `integrations/company_research_loader.py` lines 131–149 | High — hidden cross-app execution |
| F8 | HOP failure language implies direct X3 emission — "HOP failure → Exit → X3" | `AGENTIC_SPINE.md` exit disposition mapping | Medium — ownership violation |
| F9 | EXIT_PARTIAL not a canonical X3 enum — repo uses X3A/X3B/X3C/X3D/X3E only | `__main__.py` line 619 `_compute_x3()` returns EXIT_PARTIAL; `05.5_Exit_Aggregation_and_X3_Disposition.md` lines 187–215 | High — non-canonical disposition |
| F10 | HITL inconsistency — "HITL Posture = False" but code has `HUMAN_REVIEW` status path at `__main__.py` lines 637–672 and `AGENTIC_SPINE.md` mentions HUMAN_REVIEW | `AGENTIC_SPINE.md` + `__main__.py` | Medium |
| F11 | Runtime Authority = "none" — but writes local artifacts and calls model provider | `AGENTIC_SPINE.md` characteristics table | Medium — underspecified |
| F12 | FEC says grounded=false but can become grounded dynamically — confusing semantics when inputs are preloaded (not C0 retrieved) | `cert/fec_producer.py` lines 58–72 | Low — semantic clarity |
| F13 | HOPs not mapped to L2 E1–E5 phases | `AGENTIC_SPINE.md` flow diagram | Medium — missing canonical alignment |
| F14 | No prompt_bom, prompt_hash, replay_key, token budget receipt, security airlock for untrusted JD/brief text | Various engines under `reasoning/` | High — no prompt provenance |

### Contradictions

1. **L4 write**: Spine flow says "Output Chunking + R1B Commit" → Non-Goals says "No L4 durable state writes" / "No CommitRequest"
2. **HITL**: Spine says "HITL Posture = False" → Code has HUMAN_REVIEW path marking EXIT_PARTIAL
3. **Research**: Non-Goals says "no C0 vector retrieval / preloaded disk inputs only" → Cross-App section says "apps_research (Tavily) Live company data" → `company_research_loader.py` has `--auto-research-tavily` and `--auto-research-internal` flags

---

## 3. Canonical Target Architecture

```
USER (CLI: python -m apps_rg --target-company <co> --jd <path> ...)
 │
 v
U0 INTAKE
 │  raw input capture, arg parse, file existence
 │
 v
L1 PLAN
 │  JDPlan extraction (jd_planner.py)
 │  seniority_band, role_family, ats_keywords, max_pages
 │  Pure deterministic — no LLM, no network
 │
 v
L0 ROUTE DECISION
 │
 ├── R1A Exact Cache? ──hit──► [RET] sealed artifact ref → Exit X3D
 │     (SHA256 of jd+resume+brief+policy+blueprint+schema)
 │
 ├── R1B Semantic Cache? ──hit──► [RET] cached chunks + lineage → Exit X3D
 │     (full 14-field compatibility key)
 │
 ├── R5 Briefing Prerequisite ──fail──► sealed_failure_packet → Exit X3E
 │     (brief missing / stale / invalid)
 │
 └── R4_SINGLE_ACTION ──────────────────────────────────────────────┐
                                                                     │
 L2 BOUNDED EXECUTION PACKET                                        │
 │                                                                   │
 ├── E1 PREP                                                        │
 │   • Load JD, master resume, company brief from disk              │
 │   • Compute content hashes (jd, resume, brief)                   │
 │   • Freeze run directory (artifacts/apps_rg/runs/<ts>/)          │
 │   • Bind policy/blueprint/registry/model lane                    │
 │   • Create replay_key + idempotency_key                          │
 │   • Create artifact manifest shell                               │
 │   • Build prompt_bom for HOP 3                                   │
 │                                                                   │
 ├── E2 VALID                                                       │
 │   • Validate JD JSON schema                                      │
 │   • Validate company brief freshness + schema                    │
 │   • Validate no hidden research path (Tavily/internal disabled)  │
 │   • Validate prompt/model authority                              │
 │   • Validate output schema                                       │
 │   • Validate sandbox write location                              │
 │   • Validate cache compatibility rules                           │
 │                                                                   │
 ├── E3 EXEC (L2-owned deterministic HOP pipeline)                  │
 │   • HOP 1 clerk_extraction                                       │
 │   • HOP 2 data_enrichment (preloaded inputs only)                │
 │   • HOP 3 resume_generation (governed prompt packet)             │
 │   • HOP 4 fact_check                                             │
 │   • HOP 5 bullet_diversity_gate                                  │
 │   • HOP 6 content_optimizer                                      │
 │   • HOP 7 generation_diagnostics                                 │
 │   • Narrative pass (preloaded brief only)                        │
 │   • DOCX export                                                  │
 │                                                                   │
 ├── E4 HEAL (same-authority local repair only)                     │
 │   • Retry model timeout (same provider lane, within budget)      │
 │   • Retry JSON/schema/template/DOCX formatting defects           │
 │   • NOT allowed: research, human input, route change, L4 write   │
 │                                                                   │
 └── E5 SEAL                                                        │
     • Seal generated_resume.json                                    │
     • Seal narrative_resume.json (if produced)                      │
     • Seal DOCX (if produced)                                       │
     • Seal run_report.json, diagnostics, claim-to-source map        │
     • Seal prompt_bom + replay metadata                             │
     • terminal_class: SUCCESS | DEGRADED_SUCCESS | FAILURE          │
     • Optional cache_commit_candidate (inert until Exit)            │
                                                                     │
 EXIT                                                                │
 │  X1 checkout checks                                              │
 │  X2 aggregation                                                  │
 │  Exactly one X3 disposition:                                     │
 │    X3A_DENY_REROUTE — hard failure, no usable output             │
 │    X3C_COMMIT_REQUEST_TO_UWG — if cache commit enabled + passed  │
 │    X3D_ALLOW_FINISH — success or degraded success                │
 │    X3E_SAFE_ABSTAIN_CLARIFY — brief missing, fabrication, etc.   │
 │    (X3B not used — no runtime HITL)                              │
 │                                                                   │
 ├── Optional CommitRequest → UWG → L4 (cache commit only)          │
 │                                                                   │
 └── L6 (after run completion only — evaluation + future-run learning)
```

---

## 4. Route and Cache Refactor

### Route Order (canonical)

```
R1A → R1B → R5 → R4_SINGLE_ACTION
```

Each of R1A, R1B, R5 is a terminal `[RET]` path into Exit. They MUST NOT go through C0, PA, L3, or L2.

### R1A Exact Cache (NEW)

- **Key**: `SHA256(jd_text + master_resume_json + company_brief_json + policy_hash + blueprint_hash + output_schema_hash + cache_schema_version)`
- **Hit behavior**: Return sealed artifact reference with full lineage. Terminal → Exit X3D.
- **Files to create/modify**: New `check_r1a_for_apps_rg()` in `cache/r1b_adapter.py` (or new `cache/r1a_adapter.py`), wire into `__main__.py` before R1B check.

### R1B Semantic Cache (STRENGTHEN)

Current key uses `ResumeGenerationIntent.to_cache_key_dict()` which likely includes candidate_profile, company, role. Must expand to:

| Field | Source | Required |
|-------|--------|----------|
| candidate_profile_hash | SHA256(master_resume_json) | ✅ |
| master_resume_hash | SHA256(master_resume_json) | ✅ |
| jd_text_hash | SHA256(jd_json) | ✅ |
| company_brief_hash | SHA256(company_brief_json) | ✅ |
| target_company | args.target_company | ✅ |
| role_title_hash | SHA256(jd_plan.target_role) | ✅ |
| seniority_band | jd_plan.seniority_band | ✅ |
| output_schema_hash | SHA256(output JSON schema) | ✅ |
| prompt_template_hash | SHA256(HOP 3 prompt template) | ✅ |
| policy_hash | from cfg | ✅ (already present) |
| blueprint_hash | from cfg | ✅ (already present) |
| model_lane_hash | SHA256(provider+model+version) | ✅ |
| freshness_class | brief.freshness_ttl_days bucket | ✅ |
| cache_schema_version | constant "2" | ✅ |

- **Files to modify**: `types/intent_payload.py` (add fields to `ResumeGenerationIntent`), `utils/intent_builder.py` (populate new fields), `cache/r1b_adapter.py` (validate all 14 fields on recall).

### R5 Briefing Prerequisite (NO CHANGE to logic, fix disposition)

Currently returns via `_emit_r5_terminal_via_exit()`. This is already close to correct. Change: the sealed packet must be `sealed_failure_packet` type and Exit must produce `X3E_SAFE_ABSTAIN_CLARIFY`, not a custom reason code.

### Cache Commit Policy (resolve contradiction)

**Preferred target**: Enable optional R1B cache commit through canonical Exit → CommitRequest → UWG → L4.

- After Exit produces X3D_ALLOW_FINISH, if `cache_commit_enabled=True` in config:
  - Exit also emits X3C_COMMIT_REQUEST_TO_UWG with the cache_commit_candidate from E5
  - UWG validates and commits to L4 semantic cache
  - If UWG rejects, X3D still stands (cache is best-effort)
- Remove Non-Goal statements: "No L4 durable state writes" / "No CommitRequest"
- Replace with: "No direct L4 writes. Optional semantic cache CommitRequest via Exit → UWG only."

---

## 5. L2 HOP Pipeline Refactor

### Terminology Fix

| Current | Target |
|---------|--------|
| "Inner DAG" | "L2-owned deterministic HOP pipeline" |
| "Inner DAG — 7 stages" | "L2 E3 — Deterministic Domain Pipeline (7 HOPs)" |

HOPs are NOT L3 DAG nodes. They execute within a single L2 bounded execution room. The HOP topology in `config/hop_pipeline.py` is a domain-level pipeline specification consumed by E3, not an L3 orchestration graph.

### HOP → E1-E5 Mapping

| L2 Phase | Current Code | HOPs Contained |
|----------|-------------|----------------|
| **E1 Prep** | `__main__.py` lines 438–500 (intake, JD copy, L1 plan) + new hash/manifest/prompt_bom code | Pre-HOP setup |
| **E2 Valid** | `__main__.py` lines 450–456 (JD exists check) + new validation gates | Pre-HOP validation |
| **E3 Exec** | `asyncio.run(_run())` at line 595 + `_run_post_pipeline()` at line 600 | HOP 1–7 + Narrative + DOCX |
| **E4 Heal** | Not currently explicit — model timeout retries are inside orchestrator | Same-authority retry budget |
| **E5 Seal** | `_maybe_mark_provenance_failure()` + `_maybe_run_exit_hook()` + `_chunk_and_commit_output()` | Seal all artifacts |

### Changes Required

- Wrap existing HOP execution in explicit `gr.span("L2.E1_prep")` / `E2_valid` / `E3_exec` / `E4_heal` / `E5_seal` spans
- Move hash computation and manifest creation to E1
- Move validation checks to E2
- Make E4 heal budget explicit (currently implicit in orchestrator retry logic)
- Consolidate sealing logic in E5

---

## 6. Prompt Assembly and Model Invocation Refactor

### Current State

HOP 3 (`resume_generation`) calls Qwen vLLM / Anthropic through `RgResumeOrchestrator` without a prompt manifest, hash, or replay key. The narrative HOPs (4A–4H) also call LLM providers with no prompt provenance.

### Target: APP_LOCAL_PA_COMPATIBLE

Since apps_rg's prompt construction is deeply integrated into domain logic (multi-HOP, iterative with judges), a full canonical PA integration would be high-risk scope expansion. Instead, apps_rg MUST implement `APP_LOCAL_PA_COMPATIBLE` — a local prompt assembly contract that produces equivalent provenance artifacts.

### Required Prompt Artifacts

For every LLM invocation (HOP 3, narrative HOPs 4A–4H):

| Artifact | Description |
|----------|-------------|
| `prompt_bom` | Bill of materials: template ID, variable bindings, source refs |
| `prompt_template_hash` | SHA256 of the prompt template text |
| `prompt_policy_hash` | Hash of policy config governing model behavior |
| `compiled_prompt_packet` | The assembled prompt as-sent (or reference) |
| `provider_lane` | Provider + model + version binding |
| `output_schema_binding` | Expected output JSON schema |
| `authority_labels` | Source boundary labels (JD=untrusted, brief=preloaded, resume=user) |
| `evidence_refs` | Pointers to JD, master resume, company brief used |
| `replay_key` | Deterministic key for prompt replay |
| `token_budget_receipt` | Input/output token budget and actual usage |
| `security_airlock` | Sanitization receipt for untrusted JD and brief text |

### Implementation Approach

- Create `apps_rg/prompt_assembly/pa_local.py` with `build_prompt_bom()` and `seal_prompt_packet()`
- Wrap HOP 3 and narrative HOP invocations to capture prompt_bom before model call
- Store prompt_bom in run artifacts alongside generated_resume.json
- E5 seals prompt_bom with other artifacts

### Files to Modify

- `apps_rg/reasoning/RgResumeOrchestrator.py` — wrap LLM calls
- `apps_rg/integrations/hops/*.py` — wrap narrative HOP LLM calls
- `apps_rg/prompt_assembly/pa_local.py` — NEW
- `apps_rg/AGENTIC_SPINE.md` — change "Prompt Assembly = False" to "APP_LOCAL_PA_COMPATIBLE"

---

## 7. Briefing and Research Boundary Refactor

### Current State (VIOLATION)

`apps_rg/integrations/company_research_loader.py` supports 4 modes:
1. Manual brief from disk ✅ (canonical)
2. Cross-app via `apps_research` (`--research-via apps_research`) ❌ (executes apps_research INSIDE apps_rg runtime)
3. Internal `CompanyBriefEngine` (`--auto-research-internal`) ❌ (hidden LLM + HTTP research)
4. Tavily supplement (`--auto-research-tavily`) ❌ (live web research inside apps_rg)

### Target Rule

- **apps_rg consumes a prebuilt company brief artifact from disk ONLY.**
- If brief is missing, stale, or invalid → R5 → X3E_SAFE_ABSTAIN_CLARIFY with user action "Run apps_research first."
- apps_rg MUST NOT perform live web/Tavily/company research.
- If future cross-app automation is needed → L3 managed workflow (upstream orchestration, not hidden retrieval).

### Changes Required

| File | Change |
|------|--------|
| `integrations/company_research_loader.py` | Remove `_try_apps_research()`, `_try_internal_engine()`, `_try_tavily_supplement()` code paths. Retain only `_try_manual()`. Raise `CompanyBriefMissingError` if manual brief absent. |
| `scripts/narrative_pass.py` | Remove `--research-via`, `--auto-research-internal`, `--auto-research-tavily` CLI args. Only accept `--manual-brief`. |
| `__main__.py` | Remove `--research-via`, `--auto-research-internal`, `--auto-research-tavily` args (lines 388–403). |
| `AGENTIC_SPINE.md` | Remove cross-app "Tavily live company data" from integration table. Add "apps_rg fails closed if brief missing — run apps_research upstream." |

### Risk

- **Medium**: Users who currently rely on `--auto-research-tavily` or `--auto-research-internal` lose that convenience. Mitigation: document the apps_research → apps_rg workflow.

---

## 8. Exit Disposition Refactor

### Current State

- `__main__.py` uses `EXIT_PARTIAL` (non-canonical) via `_compute_x3()` and `_maybe_mark_provenance_failure()`
- HOP failures appear to emit X3 directly in `AGENTIC_SPINE.md` language

### Canonical X3 Enum (from 05.5)

| Code | Name | When |
|------|------|------|
| X3A | DENY_REROUTE | Hard failure, no usable output |
| X3B | ESCALATE_HITL | Freeze + human review (NOT used by apps_rg) |
| X3C | COMMIT_REQUEST_TO_UWG | Cache commit eligible |
| X3D | ALLOW_FINISH | Success or degraded success |
| X3E | SAFE_ABSTAIN_CLARIFY | Brief missing, fabrication, safe stop |

### Mapping Current → Canonical

| Current Failure Mode | Current Disposition | Target X3 | terminal_class |
|---------------------|---------------------|-----------|----------------|
| Brief missing/stale | R5 fallback → exit 1 | X3E_SAFE_ABSTAIN_CLARIFY | FAILURE |
| LLM generation timeout | SAFE_ABSTAIN | X3E_SAFE_ABSTAIN_CLARIFY | FAILURE |
| Fabrication detected | SAFE_ABSTAIN (CRITICAL) | X3E_SAFE_ABSTAIN_CLARIFY | FAILURE (severity=critical) |
| Fact-check gate fail | REROUTE / SAFE_FALLBACK | X3A_DENY_REROUTE (reentry=L2_REPAIR) if retryable, else X3E | FAILURE |
| Narrative pass failed, JSON usable | EXIT_PARTIAL | X3D_ALLOW_FINISH (degraded=true) | DEGRADED_SUCCESS |
| DOCX export failed, JSON/narrative usable | EXIT_PARTIAL | X3D_ALLOW_FINISH (degraded=true, missing=["docx"]) | DEGRADED_SUCCESS |
| Provenance failure | EXIT_PARTIAL (HUMAN_REVIEW) | X3E_SAFE_ABSTAIN_CLARIFY (severity=critical) | FAILURE |
| Full success | EXIT_OK | X3D_ALLOW_FINISH | SUCCESS |
| Full success + cache eligible | EXIT_OK + cache | X3C then X3D | SUCCESS |

### Required Sealed Packet Types

HOPs emit sealed packets to E5; Exit consumes them:

- `sealed_success_packet` — HOP pipeline completed, all gates passed
- `sealed_failure_packet` — unrecoverable HOP failure
- `sealed_violation_packet` — fabrication or provenance violation
- `sealed_degraded_packet` — partial success (narrative/DOCX missing but JSON usable)
- `sealed_cache_commit_candidate` — optional, for Exit → UWG path

### Files to Modify

- `__main__.py` — replace `_compute_x3()` EXIT_PARTIAL logic with canonical X3 packet construction
- `__main__.py` — replace `_maybe_mark_provenance_failure()` with sealed_violation_packet emission
- `AGENTIC_SPINE.md` — update all disposition language and table

---

## 9. HITL and Runtime Authority Refactor

### HITL Posture: No Runtime HITL

| Property | Value | Rationale |
|----------|-------|-----------|
| Runtime HITL | `False` | Candidate review is out-of-band |
| X3B emission | Never | No ESCALATE_HITL path |
| HUMAN_REVIEW status | Remove from runtime | Was provenance-failure signal; replace with sealed_violation_packet → X3E |

- Remove `HUMAN_REVIEW` branch from `_maybe_mark_provenance_failure()` — instead emit `sealed_violation_packet` with `severity=critical`
- Out-of-band review remains the candidate's responsibility after receiving the sealed résumé

### Runtime Authority

Replace "none" with explicit authority declarations:

| Authority | Scope | Bound |
|-----------|-------|-------|
| `FILESYSTEM_SANDBOX_WRITE` | Local artifacts under `artifacts/apps_rg/runs/<ts>/` | Sandbox only |
| `MODEL_EGRESS` | Governed model invocation (Qwen vLLM / Anthropic) through approved provider lane | Per prompt_bom |
| `OPTIONAL_UWG_CACHE_COMMIT` | Only if Exit emits CommitRequest and UWG approves | Exit-gated |
| No external irreversible action | No ATS, no LinkedIn, no direct L4, no provider SDK bypass | Hard constraint |

### Files to Modify

- `AGENTIC_SPINE.md` — update characteristics table
- `__main__.py` — remove HUMAN_REVIEW code path (lines 637–672), replace with sealed packet logic
- `spine_manifest.yaml` — add runtime_authority section (informational)

---

## 10. File-by-File Change Plan

### `apps_rg/AGENTIC_SPINE.md`

| Change | Risk | Tests |
|--------|------|-------|
| Rename "Inner DAG" → "L2-owned deterministic HOP pipeline" | Low | Visual review |
| Add R1A before R1B in flow diagram | Low | `test_apps_rg_route_order_r1a_r1b_r5_r4` |
| Strengthen R1B cache key description (14 fields) | Low | `test_apps_rg_r1b_cache_key_includes_...` |
| Fix Prompt Assembly = APP_LOCAL_PA_COMPATIBLE | Low | `test_apps_rg_prompt_manifest_emitted_...` |
| Remove Tavily/live research from Cross-App table | Low | `test_apps_rg_no_tavily_or_live_research_...` |
| Replace EXIT_PARTIAL with canonical X3 + terminal_class | Low | `test_apps_rg_exit_partial_removed_...` |
| Fix HITL to consistently "no runtime HITL" | Low | `test_apps_rg_no_runtime_hitl_...` |
| Fix Runtime Authority to sandbox+egress | Low | Visual review |
| Resolve L4 contradiction (enable optional cache commit) | Low | `test_apps_rg_cache_commit_only_via_exit_uwg_...` |
| Map HOPs to L2 E1–E5 | Low | Visual review |
| Update FEC description (local evidence contract) | Low | Visual review |

### `apps_rg/__main__.py`

| Change | Risk | Tests |
|--------|------|-------|
| Add R1A exact cache check before R1B (new function `_check_r1a_cache`) | Medium | `test_apps_rg_route_order_r1a_r1b_r5_r4` |
| Remove `--research-via`, `--auto-research-internal`, `--auto-research-tavily` args | Medium | `test_apps_rg_no_tavily_or_live_research_...` |
| Wrap execution in explicit E1/E2/E3/E4/E5 spans | Medium | Span names in traces |
| Replace `_maybe_mark_provenance_failure` HUMAN_REVIEW path with sealed_violation_packet | Medium | `test_apps_rg_no_runtime_hitl_...`, `test_apps_rg_fabrication_failure_safe_abstain_...` |
| Replace EXIT_PARTIAL in `_compute_x3()` with canonical X3D+degraded or X3E | Medium | `test_apps_rg_exit_partial_removed_...`, `test_apps_rg_docx_failure_allows_degraded_...` |
| Add hash computation in E1 prep | Low | `test_apps_rg_l2_e5_sealed_artifact_contains_required_hashes` |
| Add E5 sealing of prompt_bom and replay metadata | Medium | `test_apps_rg_replay_metadata_present` |

### `apps_rg/spine_manifest.yaml`

| Change | Risk | Tests |
|--------|------|-------|
| Add runtime_authority section | Low | `test_apps_rg_spine_declares_r4_single_action_l3_bypassed` |
| Add prompt_assembly = APP_LOCAL_PA_COMPATIBLE note | Low | Visual review |

### `apps_rg/config/hop_pipeline.py`

| Change | Risk | Tests |
|--------|------|-------|
| Add docstring clarifying HOPs are L2 E3 domain pipeline, not L3 DAG | Low | `test_apps_rg_hop_pipeline_not_l3_dag` |

### `apps_rg/reasoning/RgResumeOrchestrator.py`

| Change | Risk | Tests |
|--------|------|-------|
| Wrap LLM calls to capture prompt_bom | High | `test_apps_rg_prompt_manifest_emitted_...` |
| Add E4 heal budget tracking | Medium | E4 retry tests |

### `apps_rg/types/rg_flow_router_types.py`

| Change | Risk | Tests |
|--------|------|-------|
| No changes required — flow routing is domain logic within L2 E3 | None | — |

### `apps_rg/L1_cognition/jd_planner.py`

| Change | Risk | Tests |
|--------|------|-------|
| No changes required — already pure L1 semantics | None | — |

### `apps_rg/cert/fec_producer.py`

| Change | Risk | Tests |
|--------|------|-------|
| Rename to `LocalEvidenceContract` or add comment clarifying this is app-local, not C0 FEC | Low | `test_apps_rg_fec_producer` (existing) |
| Add fields: claim_to_source_map, unsupported_claims, fabricated_claims, brief_freshness_status, artifact_hashes, run_id, replay_key | Medium | New FEC field tests |

### `apps_rg/cache/r1b_adapter.py`

| Change | Risk | Tests |
|--------|------|-------|
| Add R1A exact cache function | Medium | `test_apps_rg_route_order_r1a_r1b_r5_r4` |
| Strengthen R1B recall validation to check all 14 fields | Medium | `test_apps_rg_r1b_cache_key_includes_...` |

### `apps_rg/scripts/narrative_pass.py`

| Change | Risk | Tests |
|--------|------|-------|
| Remove `--research-via`, `--auto-research-internal`, `--auto-research-tavily` args | Medium | `test_apps_rg_no_tavily_or_live_research_...` |
| Wrap narrative HOP LLM calls with prompt_bom capture | High | Prompt manifest tests |

### `apps_rg/outputs/docx_exporter.py`

| Change | Risk | Tests |
|--------|------|-------|
| No logic changes — DOCX export failure already captured | None | `test_apps_rg_docx_failure_allows_degraded_...` |

### `apps_rg/integrations/company_research_loader.py`

| Change | Risk | Tests |
|--------|------|-------|
| Remove `_try_apps_research()`, `_try_internal_engine()`, `_try_tavily_supplement()` | High | `test_apps_rg_no_tavily_or_live_research_...` |
| Retain only `_try_manual()` + `CompanyBriefMissingError` | — | `test_apps_rg_missing_brief_returns_r5_...` |

### `apps_rg/prompt_assembly/pa_local.py` (NEW)

| Change | Risk | Tests |
|--------|------|-------|
| Create APP_LOCAL_PA_COMPATIBLE prompt assembly module | Medium | `test_apps_rg_prompt_manifest_emitted_...` |

### `tests/` (multiple test files)

See §11 below.

---

## 11. Test Plan

### New Tests (under `tests/governance/` and `tests/unit/apps_rg/`)

| Test Name | Assertion |
|-----------|-----------|
| `test_apps_rg_spine_declares_r4_single_action_l3_bypassed` | spine_manifest.yaml has R4_SINGLE_ACTION and expected_l3_path=BYPASSED |
| `test_apps_rg_hop_pipeline_not_l3_dag` | hop_pipeline.py docstring or module-level constant declares L2 E3 ownership |
| `test_apps_rg_route_order_r1a_r1b_r5_r4` | __main__.py R1A check appears before R1B; R1B before R5; R5 before L2 |
| `test_apps_rg_r1b_cache_key_includes_jd_master_brief_policy_blueprint_schema` | ResumeGenerationIntent.to_cache_key_dict() contains all 14 required fields |
| `test_apps_rg_missing_brief_returns_r5_ret_safe_abstain_packet` | Missing brief → R5 → sealed_failure_packet → Exit X3E |
| `test_apps_rg_stale_brief_returns_r5_ret_safe_abstain_packet` | Stale brief → R5 → sealed_failure_packet → Exit X3E |
| `test_apps_rg_no_tavily_or_live_research_inside_runtime` | company_research_loader has no _try_tavily_supplement, no _try_apps_research, no _try_internal_engine |
| `test_apps_rg_prompt_manifest_emitted_for_model_generation` | HOP 3 execution produces prompt_bom artifact in run_dir |
| `test_apps_rg_hop_failures_seal_packets_not_x3_directly` | HOP failure path produces sealed_*_packet, not X3 directly |
| `test_apps_rg_exit_partial_removed_or_mapped_to_canonical_x3` | No EXIT_PARTIAL string in __main__.py; all dispositions are X3A–X3E |
| `test_apps_rg_no_runtime_hitl_when_hitl_false` | No X3B emission; no HUMAN_REVIEW runtime path |
| `test_apps_rg_no_direct_l4_write` | No direct SemanticCacheManager.store() outside Exit → UWG path |
| `test_apps_rg_cache_commit_only_via_exit_uwg_if_enabled` | Cache store call happens only after Exit X3C/X3D |
| `test_apps_rg_l2_e5_sealed_artifact_contains_required_hashes` | Sealed artifact includes jd_hash, resume_hash, brief_hash, prompt_hash, policy_hash, blueprint_hash |
| `test_apps_rg_docx_failure_allows_degraded_success_when_json_usable` | DOCX fail + JSON present → X3D + degraded=true + missing=["docx"] |
| `test_apps_rg_fabrication_failure_safe_abstain_no_candidate_resume` | Fabrication → X3E + no candidate-facing résumé output |
| `test_apps_rg_replay_metadata_present` | Sealed artifact includes replay_key |
| `test_apps_rg_artifacts_saved_under_sandbox_run_dir_only` | All writes go to artifacts/apps_rg/runs/<ts>/ — no writes elsewhere |

### Negative Controls

| Test | Asserts absence of |
|------|-------------------|
| `test_apps_rg_no_tavily_import_in_runtime` | No `tavily` import in company_research_loader at runtime |
| `test_apps_rg_no_apps_research_engine_import_in_runtime` | No `CompanyBriefEngine` import in loader |
| `test_apps_rg_no_exit_partial_string` | String "EXIT_PARTIAL" absent from __main__.py |
| `test_apps_rg_no_human_review_runtime_path` | String "HUMAN_REVIEW" absent from runtime disposition logic |

### Existing Tests to Update

| Test File | Update |
|-----------|--------|
| `tests/governance/test_apps_rg_exit_x3.py` | Update expectations: EXIT_PARTIAL → X3D+degraded or X3E |
| `tests/governance/test_apps_rg_hitl_x3b_disposition.py` | Assert X3B is never emitted |
| `tests/governance/test_apps_rg_l4_uwg.py` | Update for optional Exit → UWG cache commit path |
| `tests/_apps_contract/test_apps_rg_fec_producer.py` | Add assertions for new FEC fields |

---

## 12. Proof and Acceptance Criteria

### Success Criteria

| # | Criterion | Proof Method |
|---|-----------|-------------|
| AC1 | R4_SINGLE_ACTION route shape | `spine_manifest.yaml` + `test_apps_rg_spine_declares_r4_single_action_l3_bypassed` |
| AC2 | No L3 orchestration | `test_apps_rg_hop_pipeline_not_l3_dag` + "Inner DAG" text absent from AGENTIC_SPINE.md |
| AC3 | No C0 runtime retrieval | `test_apps_rg_no_tavily_or_live_research_inside_runtime` + grep for C0/tavily imports |
| AC4 | No hidden Tavily/live research | `test_apps_rg_no_tavily_import_in_runtime` + company_research_loader code review |
| AC5 | No direct L4 writes | `test_apps_rg_no_direct_l4_write` + grep for SemanticCacheManager.store outside Exit path |
| AC6 | Cache commit only through Exit → UWG | `test_apps_rg_cache_commit_only_via_exit_uwg_if_enabled` |
| AC7 | Sealed artifacts complete | `test_apps_rg_l2_e5_sealed_artifact_contains_required_hashes` |
| AC8 | X3 emitted only by Exit | `test_apps_rg_hop_failures_seal_packets_not_x3_directly` |
| AC9 | EXIT_PARTIAL removed | `test_apps_rg_exit_partial_removed_or_mapped_to_canonical_x3` |
| AC10 | HITL consistent | `test_apps_rg_no_runtime_hitl_when_hitl_false` |
| AC11 | Replay metadata present | `test_apps_rg_replay_metadata_present` |
| AC12 | Prompt Assembly auditable | `test_apps_rg_prompt_manifest_emitted_for_model_generation` |
| AC13 | R1A before R1B | `test_apps_rg_route_order_r1a_r1b_r5_r4` |
| AC14 | R1B cache key strengthened | `test_apps_rg_r1b_cache_key_includes_jd_master_brief_policy_blueprint_schema` |
| AC15 | AGENTIC_SPINE.md has no contradictory L4/cache non-goals | Manual review |
| AC16 | Runtime authority = sandbox write + model egress | AGENTIC_SPINE.md characteristics table review |
| AC17 | All domain behavior preserved | Existing test suite green + no HOP removal |

### Proof Commands

```bash
# Run all apps_rg governance tests
python -m pytest tests/governance/test_apps_rg_*.py -v

# Run unit tests
python -m pytest tests/unit/apps_rg/ -v

# Run apps_contract tests
python -m pytest tests/_apps_contract/test_apps_rg_*.py -v

# Grep for forbidden patterns
rg "EXIT_PARTIAL" apps_rg/ --type py
rg "HUMAN_REVIEW" apps_rg/__main__.py
rg "tavily" apps_rg/integrations/company_research_loader.py
rg "_try_apps_research\|_try_internal_engine\|_try_tavily_supplement" apps_rg/

# Verify spine manifest
python -c "import yaml; d=yaml.safe_load(open('apps_rg/spine_manifest.yaml')); assert d['claimed_routes'][0]['type']=='R4_SINGLE_ACTION'"
```

---

## 13. Open Questions

| # | Question | Source | Impact |
|---|----------|--------|--------|
| Q1 | Does `ResumeGenerationIntent.to_cache_key_dict()` already include some of the 14 required fields? Need to inspect `types/intent_payload.py` to determine the exact gap. | Code inspection needed | R1B key strengthening scope |
| Q2 | Does `_compute_x3()` exist as a named function or is the X3 logic implicit in `governed_run` spine receipt? If it's in `apps_shared.spine_emission`, the EXIT_PARTIAL mapping may need changes in shared code too. | `apps_shared/spine_emission/` | Scope of X3 fix |
| Q3 | Is `cache_commit_enabled` config already wired in `cert_route_registry.yaml` or does it need a new flag? | `apps_rg/config/cert_route_registry.yaml` | Cache commit config |
| Q4 | How does `apps_shared.spine_emission.governed_run` compute X3 disposition today? Does it have an EXIT_PARTIAL branch? If so, the fix may be in shared code, affecting other apps. | `apps_shared/spine_emission/` | Cross-app impact |
| Q5 | What is the exact signature of `_check_r1b_cache()` (the private function in `__main__.py`)? The existing R1B check wiring may already partially support R1A-style exact matching. | `__main__.py` lines 254–300 | R1A implementation complexity |
| Q6 | Do the narrative HOPs (4A–4H) all call LLM providers, or are some deterministic? Only LLM-calling HOPs need prompt_bom capture. | `apps_rg/integrations/hops/*.py` | Prompt Assembly scope |

---

## 14. Implementation Order

| Wave | Phase | Focus | Files | Est. Risk |
|------|-------|-------|-------|-----------|
| W1 | P1 | AGENTIC_SPINE.md terminology + L2 E1-E5 mapping + route corrections | `AGENTIC_SPINE.md` | Low |
| W1 | P2 | spine_manifest.yaml runtime authority + PA posture | `spine_manifest.yaml` | Low |
| W1 | P3 | hop_pipeline.py L2 ownership docstring | `config/hop_pipeline.py` | Low |
| W2 | P1 | R1A exact cache implementation | `cache/r1b_adapter.py` (or new `r1a_adapter.py`), `__main__.py` | Medium |
| W2 | P2 | R1B cache key strengthening | `types/intent_payload.py`, `utils/intent_builder.py`, `cache/r1b_adapter.py` | Medium |
| W3 | P1 | Research boundary: remove Tavily/internal/apps_research from loader | `integrations/company_research_loader.py` | High |
| W3 | P2 | Remove research CLI args from narrative_pass + __main__ | `scripts/narrative_pass.py`, `__main__.py` | Medium |
| W4 | P1 | Prompt Assembly: create pa_local.py, wrap HOP 3 | `prompt_assembly/pa_local.py` (NEW), `reasoning/RgResumeOrchestrator.py` | High |
| W4 | P2 | Prompt Assembly: wrap narrative HOPs | `integrations/hops/*.py` | High |
| W5 | P1 | Exit disposition: replace EXIT_PARTIAL with canonical X3 | `__main__.py` | Medium |
| W5 | P2 | Exit disposition: remove HUMAN_REVIEW path, add sealed packets | `__main__.py` | Medium |
| W5 | P3 | Exit disposition: update AGENTIC_SPINE.md table | `AGENTIC_SPINE.md` | Low |
| W6 | P1 | L4/UWG: resolve contradiction, wire optional cache commit via Exit | `__main__.py`, config | Medium |
| W6 | P2 | FEC: add fields, clarify local evidence semantics | `cert/fec_producer.py` | Low |
| W7 | P1 | E1-E5 spans: wrap __main__.py execution in explicit L2 phase spans | `__main__.py` | Medium |
| W7 | P2 | E5 seal: consolidate sealing logic, add hash + replay metadata | `__main__.py` | Medium |
| W8 | P1 | Tests: governance + unit tests (18+ new) | `tests/governance/`, `tests/unit/apps_rg/` | Low |
| W8 | P2 | Tests: update existing test expectations | `tests/governance/test_apps_rg_exit_x3.py` etc. | Low |
| W8 | P3 | Proof commands: run full test sweep, grep verification | — | Low |

### Dependency Graph

```
W1 (docs/terminology) → no deps
W2 (route/cache) → depends on W1 for terminology only
W3 (research boundary) → independent
W4 (prompt assembly) → independent
W5 (exit disposition) → depends on W3 (research removal changes failure paths)
W6 (L4/UWG/FEC) → depends on W5 (exit disposition determines commit path)
W7 (E1-E5 spans) → depends on W4 (prompt_bom captured in E1), W5 (sealed packets in E5)
W8 (tests) → depends on all previous waves
```

### Strict Rules (reiterated)

- ❌ No broad refactors
- ❌ No unrelated renames
- ❌ No implementation before plan is saved
- ❌ Do not weaken existing résumé generation behavior
- ❌ Do not remove useful HOPs
- ❌ Do not introduce L3 unless managed workflow is truly required
- ❌ Do not introduce C0 retrieval into apps_rg runtime
- ❌ Do not add runtime HITL unless explicitly required
- ❌ Do not allow direct L4 writes
- ❌ Do not let model output, cached prose, user text, JD text, or company brief text become authority
- ✅ Preserve preloaded JD/master resume/company brief behavior
- ✅ Preserve sealed artifact output
- ✅ Preserve DOCX export
- ✅ Preserve out-of-band candidate review
