---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\04_apps-rg-c0-architecture-analysis-f3d8b2.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\04_apps-rg-c0-architecture-analysis-f3d8b2.md'
source_sha256: 114e97568d9c7bce484df876e096df8bf1a4ab1ba2701df861d1df633f4cd62e
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
slug: apps-rg-c0-architecture-analysis-f3d8b2
status: Completed
plan_type: audit
dod_exempt: false
created_at: "2026-05-13"
updated_at: "2026-05-14"
---

**PLAN STATUS: ALL WAVES COMPLETED — W7 CLOSEOUT WITH ADVISORY**

- W1-W5: Core C0 retrieval with gate verdicts, metadata filtering, bounded section retrieval ✅
- W6: Observability span emission to FEC.otel_span_refs for L6 consumption ✅
- W7: Boundary CI gate with PASS_WITH_ADVISORY classification ✅

**Final Status:** 145 tests passing, 111 boundary findings classified (0 C0-specific blockers), advisory closeout complete.

> [!IMPORTANT]
> PORTFOLIO_STATUS: CONSOLIDATED_UNDER_MASTER
> MASTER_PLAN_REF: .windsurf/plans/01_apps-rg-master-governed-runtime-hardening.md
> DISPOSITION: MERGED_INTO_MASTER_SPLIT_BY_PRIORITY
> SUPERSEDED_BY_PHASES: Phase 9 and Phase 11
> RETAINED_SCOPE:
> - narrow hybrid C0
> - current C0 safety and FEC completeness
> - authoritative briefing gate
> - fact_vectors schema and candidate-fact retrieval
> - deterministic claim verification
> MOVED_SCOPE:
> - minimum safety moves to Phase 9
> - fact_vectors and section retrieval move to Phase 11
> DEFERRED_SCOPE:
> - BM25/sparse retrieval unless separately justified
> - LLM free-text claim verification
> CONFLICTS_RESOLVED:
> - company research remains apps_research or authoritative briefing, not apps_rg C0
> - fact_vectors is Phase 11 product-quality foundation, not a blocker for Phase 1-3 L4/L5 safety closure

## Portfolio Consolidation Notes
This plan has been merged into the master consolidation with work split by priority:
- Phase 9: Minimum C0 safety (FEC completeness, briefing gates)
- Phase 11: Product-quality foundation (fact_vectors, section retrieval, claim verification)

**Resume Shipping Critical Path:**
- Minimum C0 safety (Phase 9 subset) is part of the Resume Shipping Critical Path (Master Plan S7).
- fact_vectors remains post-shipping product-quality foundation (Phase 11).

---

# apps_rg C0 Architecture Analysis and Implementation Plan (Hardened)

## RECOMMENDATION: HYBRID (Narrowed)

**Defense:** apps_rg already has a functioning C0 path. `apps_rg/runtime/bindings/c0_binding.py` fires on every run where `route.grounding_required=True`, retrieves JD + resume + master_resume, and optionally queries a `process_docs` Chroma collection. The question is not whether to open C0 — it is open today — but whether the current scope is sufficient and how to extend it safely.

**Narrowed scope of the Hybrid recommendation:**
- Direct apps_rg C0 is authorised **only** for: candidate-owned facts, JD/resume grounding, per-section evidence support, and claim verification.
- Company research remains apps_research via L3 (when `auto_research_internal=True`) or a supplied authoritative briefing (when `manual_brief_path` is present and passes freshness/authority checks).
- **No parallel company-research retrieval path is to be built inside apps_rg C0.** The existing `process_docs` Chroma collection contains `approved_examples`, `rubrics`, `governance_docs`, and `receipts` — none of these are company-research. The only two source classes that address candidate facts are `candidate_profile` and `project_evidence`. Those are the only Chroma lanes C0 should execute for resume generation.
- apps_research-through-L3 handles broad company context. Direct apps_rg C0 handles narrow candidate-fact retrieval. These two concerns must not overlap.

---

## §1 — Investigation Findings (Analysis-Only Mode)

### 1.1 Current apps_rg Runtime Flow

| Stage | Location | Observed State |
|---|---|---|
| U0 ingress | `agentic_core/runtime/entry/u0_apps_rg_binding.py` | Validates `AppsRgIngressPayload`, produces `ValidatedRequest` with `app_payload.jd_payload` + `app_payload.resume_payload`. Reflection receipt emitted. |
| L1 planning | `agentic_core/L1_cognition/apps_rg_l1_binding.py` | Produces `PackageDrivenL1Plan`; reads `route_profiles.yaml` via generic interpreter. `grounding_required=True` when `evidence_grounded_generation` route family fires. |
| L0 routing | `agentic_core/L0_routing/apps_rg_l0_binding.py` | Selects `evidence_grounded_generation` (default) → `R3_SIMPLE_GROUNDED_READ` via `route_evaluation_order` in `route_profiles.yaml`. Route `apps_rg.resume_generation_managed_v1` is `registered_not_active`; legacy `apps_rg.resume_generation_v1` is `deprecated`. |
| C0 grounding | `apps_rg/runtime/bindings/c0_binding.py` | **ACTIVE TODAY.** Fires when `route.grounding_required=True`. Retrieves JD text + resume + master resume (file-only default). Opt-in Chroma via `CHROMA_PERSIST_DIR` env var → queries `process_docs` collection across 6 `source_class` values. Emits `FinalEvidenceContract`. |
| PA prompt assembly | `apps_rg/prompt_assembly/` | 8-slot model (S0/I0/C0/U0/D0/E0/Y0/R0). `compiled_artifact_required_for` 5 model steps. FEC evidence enters C0 slot as data only. |
| L2 generation | `agentic_core/L2_execution/apps_rg_l2_binding.py` | HOP pipeline (intake → extract → score → assemble → narrative → DOCX). |
| Exit/X1/X3 | `agentic_core/runtime/exit/apps_rg_exit_binding.py` | X3 disposition. `invoke_exit_eval: true` in `cert_route_registry.yaml`. AppSpecificEvaluator runs 8-dim rubric. |
| apps_research delegation | `apps_rg/config/domain_contract/research_delegation_profile.yaml` | Config-driven delegation to `apps_research` via L3. `manual_brief_path` bypasses research delegation when briefing supplied. |
| ChromaDB / vector store | `apps_rg/runtime/bindings/c0_binding.py` W4 | `process_docs` collection, 6 source classes (`candidate_profile`, `project_evidence`, `approved_examples`, `rubrics`, `governance_docs`, `receipts`), BAAI/bge-m3 embeddings, metadata filter `app=apps_rg`. |
| `fact_vectors` | grep: no matches | **`fact_vectors` does not exist in the codebase.** No YAML, JSON, Python, or plan file references it. The "prior Notion plan" described in the prompt request has no materialized artifact on disk. |

### 1.2 Direct C0 Integration Today

| Item | Status |
|---|---|
| `RouteContract.grounding_required=True` | **YES** — `route_profiles.yaml` line 7: `grounding_required: true` |
| `GroundingRouteContract` fields | **PARTIAL** — `route_profiles.yaml` declares `R3_SIMPLE_GROUNDED_READ` condition but no `GroundingRouteContract` type is explicitly bound; uses `RouteContract.grounding_required` flag |
| `FinalEvidenceContract` consumed by PA | **YES** — C0 emits FEC; PA ingests via C0 slot. Schema version `AG-2.b3a449.W4`. |
| C0 evidence slot in PA | **YES** — 8-slot model, C0 slot is `S0/I0/C0/U0/D0/E0/Y0/R0` third slot |
| C0 runtime gates G08/G09/G13/G17/G23/G24 | **DECLARED** in `runtime_gate_profile.resume_generation.v1.json` C0 stage. Wiring proof unverified by OTel (no runtime traces). |
| C0 telemetry, receipts, audit refs | **PARTIAL** — `evidence_digest` computed; `l5_certification_ref` set; OTel span wiring not confirmed |
| Tests proving no C0 bypass when `grounding_required=True` | **GAP** — `c0_binding.py` raises `ValueError` if called with `grounding_required=False`, but no CI test asserts the dispatch chain enforces this at runtime |
| Section-level evidence retrieval | **ABSENT** — C0 retrieves at request level, not section level. No per-section query. |
| Claim verification / contradiction detection | **ABSENT** — No implementation. No test. No config. |
| Exact metadata filter / sparse retrieval | **ABSENT** — Only dense (BAAI/bge-m3 cosine) retrieval today. No Chroma `where`-clause metadata filter path and no keyword/BM25 implementation. |
| `fact_vectors` collection / schema | **ABSENT** — Zero references anywhere in the repo. |

### 1.3 Three Operating Model Comparison

#### Model A — Keep Current (supplied briefing or apps_research via L3)

| Dimension | Assessment |
|---|---|
| Quality lift | None new. JD + resume + master_resume grounding already occurs. Chroma is opt-in and unused in practice (no `fact_vectors`). |
| Latency / token cost | Lowest. No additional retrieval. |
| Governance complexity | Lowest. Single path. |
| Replayability | Good. File-based evidence is deterministic. |
| Duplicate retrieval risk | Low. |
| Stale/weak evidence risk | Medium. Briefing freshness not gated. |
| agentic_core purity | Fully preserved. |
| apps_rg declarative-only | Yes. |
| `fact_vectors` value | Zero — they don't exist. |
| L6 shadow learning | Not connected to retrieval outcomes. |

**Verdict:** Adequate today. Insufficient as resume quality demands increase. No hallucination prevention for invented bullets.

#### Model B — Open Direct apps_rg C0 (all retrieval via direct C0)

| Dimension | Assessment |
|---|---|
| Quality lift | Potential but speculative — requires fact_vectors to exist, be populated, and prove lift over Model A. |
| Latency / token cost | High. 6 source-class queries × 5 results = 30 Chroma reads per request, BAAI/bge-m3 encoding, added prompt tokens. |
| Governance complexity | High. Requires GroundingRouteContract, per-section query design, FEC expansion, additional gate wiring. |
| Replayability | Degrades unless Chroma snapshots are persisted with run artifacts. |
| Duplicate retrieval risk | High if apps_research is also invoked. Same company/JD facts retrieved twice. |
| Stale/weak evidence risk | High — Chroma collections have no declared freshness policy or TTL for `fact_vectors`. |
| agentic_core purity | Preserved if apps_rg contributes only declarative retrieval profiles. |
| apps_rg declarative-only | Achievable. Requires new retrieval profile YAML in `domain_contract/`. |
| `fact_vectors` value | Requires build-out. Currently zero. |
| L6 shadow learning | Could connect evidence quality to judge outcomes. |

**Verdict:** Premature. fact_vectors do not exist. End-to-end Chroma retrieval for resume generation is unproven. Build the foundation first.

#### Model C — Hybrid Route Policy

| Dimension | Assessment |
|---|---|
| Quality lift | Targeted. Narrow candidate-fact retrieval (JD-to-resume fact grounding, contradiction detection, claim verification) adds measurable quality without broad retrieval overhead. |
| Latency / token cost | Moderate. Section-level queries are bounded (3–5 items per section, not 30 total). |
| Governance complexity | Medium. Requires briefing-bypass gate, section-level retrieval profile, claim verification slot in X1D. |
| Replayability | Good. Gated by replay_key; Chroma queries tied to evidence_digest. |
| Duplicate retrieval risk | Low — apps_research handles company research; C0 handles candidate-owned facts. |
| Stale/weak evidence risk | Managed — candidate_profile and project_evidence are candidate-owned, long-lived, low staleness risk. |
| agentic_core purity | Preserved — apps_rg contributes declarative section-level retrieval profiles. |
| apps_rg declarative-only | Yes — section retrieval profiles, bypass policy, and claim-check config owned by apps_rg. |
| `fact_vectors` value | Must be built. Provides incremental value once populated. |
| L6 shadow learning | Connects evidence quality dimensions to factual_grounding and no_fabrication rubric scores. |

**Verdict:** Correct path. Implement in phases. Start with gap closure (briefing-bypass gate, section retrieval profile), then build fact_vectors, then claim verification.

---

## §2 — agentic_core Purity Invariant

> ⛔ **All `agentic_core/` files in this plan are READ-ONLY by default.**  
> An `agentic_core` file may be modified only if the change is generic infrastructure with a proof it is not apps_rg-specific.
> All apps_rg behaviour — retrieval profiles, bypass logic, section queries, metadata filters, claim check config, briefing freshness policy — lives in:
> - `apps_rg/config/domain_contract/` (declarative YAML/JSON)
> - `apps_rg/runtime/bindings/` (app-owned bindings)
> - `apps_rg/tools/` (app-owned utilities)
> - `tests/_apps_contract/` (app-owned tests)
>
> **Forbidden in `agentic_core/`:** `apps_rg` literals, section names (e.g. `executive_summary`, `headline`), resume-domain concepts (e.g. `fact_vectors`, `master_resume`, `jd_payload`), briefing policy logic, or any reference to a specific resume section or candidate profile structure.
>
> If a wave requires an `agentic_core` edit, the PR description must carry: `AGENTIC_CORE_EDIT_PROOF: generic_contract_propagation | generic_exit_hook_defect — <specific defect description>`.

---

## §3 — Gap Matrix (Hardened)

| # | Area | Observed State | Gap | Severity | Recommendation | Authoritative File (read-only unless noted) | Acceptance Test |
|---|---|---|---|---|---|---|---|
| G1 | `fact_vectors` Chroma collection | Does not exist. Zero repo references. | Schema, ingest pipeline, and metadata standard absent. `process_docs` holds rubrics and governance docs, not candidate facts. | **Critical** | Define separate `fact_vectors` collection schema; build ingest pipeline for `candidate_profile` + `project_evidence` source classes only. | New: `apps_rg/config/domain_contract/fact_vectors_schema.yaml` (MODIFY), `apps_rg/tools/fact_vector_ingest.py` (NEW) | `test_fact_vectors_collection_separate_from_process_docs` — asserts `process_docs` and `fact_vectors` are independent collections |
| G2 | Briefing-supplied bypass gate | `__main__.py` caller-convention only. C0 fires regardless when `grounding_required=True`. No freshness or authority check on supplied brief. | Authoritative brief does not suppress Chroma retrieval. Stale or unauthorized brief enters evidence bundle unchecked. | **High** | Add `G_BRIEF_BYPASS` gate: if `manual_brief_path` present AND authority class = AUTHORITATIVE AND freshness passes → skip company-research Chroma lanes ONLY; candidate-fact lanes (`candidate_profile`, `project_evidence`) MUST still execute when grounding required. Stale/unauthorized brief → `BLOCKED` or `WEAK_WITH_CAVEATS`, never silent PASS. | `apps_rg/runtime/bindings/c0_binding.py` (MODIFY), `apps_rg/config/domain_contract/runtime_gate_profile.resume_generation.v1.json` (MODIFY), `apps_rg/config/domain_contract/research_delegation_profile.yaml` (MODIFY — add `briefing_freshness_max_age_hours` + `briefing_authority_classes`) | `test_manual_brief_bypass_skips_company_chroma_only` + `test_stale_brief_produces_blocked_not_pass` |
| G3 | GroundingRouteContract contract proof | `RouteContract` has `grounding_required: bool` + all required fields (`route_replay_key`, `policy_hash`, `support_target`, `token_budget`, `retrieval_profile_ref`, `gate_verdict_refs`). No typed `GroundingRouteContract` subtype instantiated by apps_rg binding. | C0 binding receives a plain `RouteContract`. If generic engine drops a required grounding field, C0 degrades silently. Required fields `route_contract_ref`, `support_target`, `source_scope` (currently absent from `RouteContract`), `freshness_profile`, `retrieval_budget` (maps to `token_budget`), `replay_key` (`route_replay_key`), and gate refs must be verifiably present at C0 entry. | **High** | **Acceptance proof only — no agentic_core code change unless a missing field is discovered.** Add test asserting each required grounding field is non-empty on every apps_rg run. If `source_scope` or `freshness_profile` are absent, add them as generic fields in `RouteContract` (this is a generic contract propagation edit — AGENTIC_CORE_EDIT_PROOF required). | `agentic_core/L0_routing/c0_retrieval/route_contract.py` (READ-ONLY unless missing field proved), `agentic_core/runtime/contracts/route_contract.py` (READ-ONLY unless missing field proved), `apps_rg/runtime/bindings/l0_binding.py` (READ-ONLY audit) | `test_grounding_required_false_blocks_c0` + `test_route_contract_carries_required_grounding_fields` |
| G4 | FEC completeness | `FinalEvidenceContract` fields: `evidence_items`, `evidence_strata`, `citation_map`, `source_lineage_map`, `freshness_receipts`, `acl_verification_receipts`, `contradiction_report`, `support_status`, `final_evidence_digest` all exist in `final_evidence_contract.py`. `c0_binding.py` populates `citation_map` and `freshness_receipts` when Chroma active; most fields default to empty in file-only path. | File-only path produces a structurally valid but sparse FEC. `final_evidence_digest`, `contradiction_report`, and `evidence_strata` are empty on every non-Chroma run. Exit gates that require these fields may silently degrade to `UNKNOWN`. | **High** | W1 task: audit which FEC fields Exit and PA actually read. Add FEC completeness check in C0 binding: if a field required by a declared gate (G08/G09/G13) is empty, set `support_status = WEAK` with `unknown_reason`. Never default to PASS. | `apps_rg/runtime/bindings/c0_binding.py` (MODIFY), `agentic_core/runtime/contracts/final_evidence_contract.py` (READ-ONLY — already complete) | `test_apps_rg_dispatch_always_produces_fec` — asserts FEC present before PA in dispatch context |
| G5 | `fact_vectors` and `process_docs` separation | `c0_binding.py` queries `process_docs` for 6 source classes including `candidate_profile` and `project_evidence`. These should be in `fact_vectors` (candidate-owned facts), not `process_docs` (governance/rubric docs). | `fact_vectors` must be a physically separate Chroma collection. `process_docs` remains for rubrics, governance docs, approved examples. C0 must query each collection on its own path. | **Medium** | After G1 (fact_vectors schema defined): route `candidate_profile` + `project_evidence` queries to `fact_vectors`; route `rubrics` + `governance_docs` + `approved_examples` queries to `process_docs`. | `apps_rg/runtime/bindings/c0_binding.py` (MODIFY — collection routing only), `apps_rg/config/domain_contract/fact_vectors_schema.yaml` (NEW) | `test_fact_vectors_collection_separate_from_process_docs` (shared with G1) |
| G6 | Section-level evidence retrieval | Absent. C0 retrieves at request level. | No per-section queries for headline, executive summary, experience bullets, competencies. Retrieved evidence is undifferentiated — PA cannot allocate per-section budget. | **High** | Define section retrieval profile YAML. Implement opt-in section sub-query phase in C0 binding bounded by profile budget. Activate after W2 (fact_vectors exists). Section names live in the YAML file only — never hardcoded in `agentic_core/`. | New: `apps_rg/config/domain_contract/section_retrieval_profile.yaml` (NEW), `apps_rg/runtime/bindings/c0_binding.py` (MODIFY — W4 only after W2 done) | `test_section_retrieval_bounded_by_profile` |
| G7 | Exact metadata filtering | Dense retrieval only (BAAI/bge-m3 cosine). No exact-match path for employer names, certifications, dates, role names, project names, skills. | Exact employer names and certification codes score poorly in embedding space. A candidate profile chunk containing "Goldman Sachs VP, 2019" retrieves correctly only if JD also mentions Goldman Sachs. | **Medium** | Add Chroma `where` clause as a second retrieval lane for `fact_vectors` queries. Fields to filter on: `employer`, `title`, `certification`, `year`, `skill`, `project_name`, `source_class`, `app`. This is **exact metadata filtering** using Chroma's native `where` dict, not BM25. No BM25 library is introduced. `dense_score` and `metadata_score` are separate `EvidenceItem` fields — populate both. Do not conflate them. | `apps_rg/runtime/bindings/c0_binding.py` (MODIFY — W5 phase), `apps_rg/config/domain_contract/fact_vectors_schema.yaml` (NEW — declare filterable fields) | `test_metadata_filter_retrieves_exact_employer_name` |
| G8 | Claim verification in X1D | Absent. No contradiction detection. No claim-to-evidence linkage in Exit. | Generated resume claims (employers, metrics, project outcomes) are not cross-checked against FEC evidence before X3 disposition. `no_fabrication` rubric dim exists in `eval_rubrics.yaml` but receives no structured evidence input. | **Medium** | Minimal deterministic claim checker (not LLM judge): diff generated JSON employer/title/cert fields against FEC `evidence_items` source metadata. If a generated claim has no matching source in FEC, flag `support_status = WEAK`. Wire as an X1D sub-step in the Exit evaluator, feeding `no_fabrication` dim. **Feasible deterministically only for structured fields (employer, cert, date) — LLM-graded free-text verification is deferred.** | `apps_rg/config/domain_contract/eval_rubrics.yaml` (READ-ONLY audit), `agentic_core/L3_orchestration/exit_eval/v6/app_grader_registry.py` (READ-ONLY unless generic grader type gap found) | `test_claim_verification_flags_ungrounded_employer` |
| G9 | L6 shadow learning observability | `learning_profiles.yaml` is minimal. No evidence quality → judge score correlation. | L6 cannot observe that a run with `support_status=WEAK` also scored low on `factual_grounding`. | **Low** | Emit `retrieval_quality_span` from C0 binding: `evidence_count`, `support_status`, `excluded_count`, `metadata_filter_hits`, `dense_hits`. Connect span ref in FEC `otel_span_refs`. Exit pipeline reads `otel_span_refs` and includes in `tracked_metrics`. | `apps_rg/runtime/bindings/c0_binding.py` (MODIFY — W6), `agentic_core/L3_orchestration/exit_eval/v6/pipeline.py` (READ-ONLY unless generic tracked_metrics gap found) | `test_l6_retrieval_quality_span_present_in_fec_otel_refs` |
| G10 | Runtime gate G08/G09/G13/G17/G23/G24 wiring proof | Declared in `runtime_gate_profile.resume_generation.v1.json`. No OTel trace confirming they ran or were explicitly NOT_APPLICABLE with reason. | Gates could be declared but never evaluated. `UNKNOWN` gate result must never be treated as PASS. | **High** | Add test: for every gate in C0 stage of the gate profile, assert the FEC's `gate_verdict_refs` contains at least one ref, or the gate's result is `NOT_APPLICABLE` with a non-empty reason. A missing or UNKNOWN gate verdict = test failure. | `apps_rg/config/domain_contract/runtime_gate_profile.resume_generation.v1.json` (READ-ONLY), `apps_rg/runtime/bindings/c0_binding.py` (MODIFY — populate `gate_verdict_refs`), new `tests/_apps_contract/test_c0_gate_enforcement.py` | `test_unknown_or_missing_gate_not_pass` |

---

## §4 — Bypass Semantics (Hardened)

### What `manual_brief_path` bypasses

`manual_brief_path` is an authoritative pre-built company research briefing. It bypasses **company-research Chroma retrieval only.**

```
manual_brief_path present AND authoritative AND fresh
  → SKIP: company_brief_kb lanes in Chroma
  → MUST STILL RUN: candidate_profile + project_evidence lanes in fact_vectors
  → MUST STILL RUN: JD evidence assembly
  → MUST STILL RUN: resume_payload evidence assembly
  → MUST STILL RUN: master_resume header protection
```

### What `manual_brief_path` does NOT bypass

| Path | Bypassed? | Reason |
|---|---|---|
| `candidate_profile` Chroma queries | **NO** | Candidate grounding is not a company-research concern |
| `project_evidence` Chroma queries | **NO** | Project evidence is candidate-owned |
| JD evidence assembly | **NO** | JD is always an input |
| master_resume header | **NO** | Always canonical |
| G08 ACL check on brief | **NO** | Brief must be tenant-scoped |
| G09 freshness check on brief | **NO** | Brief must not be expired |
| G13 support_status evaluation | **NO** | Brief quality must still be assessed |

### Brief quality outcomes

| Brief state | support_status outcome | C0 behaviour |
|---|---|---|
| Authority=AUTHORITATIVE, freshness=FRESH | Company Chroma skipped; FEC populated from brief + candidate facts | Proceed |
| Authority=AUTHORITATIVE, freshness=STALE (`briefing_freshness_max_age_hours` exceeded) | `WEAK_WITH_CAVEATS` — brief ingested but flagged stale | Proceed with caveat |
| Authority=UNKNOWN or ACL=DENIED | `BLOCKED` — brief rejected | Abort or fallback to apps_research delegation |
| Brief path present but file unreadable | `BLOCKED` — C0EvidenceGapError raised | Hard fail |

**Silent PASS is forbidden for stale or unauthorized briefs.**

---

## §5 — Contract Acceptance Proof (GroundingRouteContract)

The following fields must be present and non-empty on the `RouteContract` passed to `c0_retrieve_apps_rg` on every apps_rg grounded run. These are the "GroundingRouteContract" fields referenced in the plan — there is no separate type; `RouteContract` carries them all.

| Field | `RouteContract` attribute | Must be non-empty? | Enforcement |
|---|---|---|---|
| `route_contract_ref` | Derived from `route_id` + `policy_hash` | Yes | `test_route_contract_carries_required_grounding_fields` |
| `support_target` | `support_target: SupportTarget` | Yes | Declared in `SupportTarget` type |
| `source_scope` | Not yet on `RouteContract` — **GAP** | Yes (if grounding is active) | If absent: add as generic field with `AGENTIC_CORE_EDIT_PROOF` |
| `freshness_profile` | Maps to `freshness_class: FreshnessClass` | Yes | `FreshnessClass` enum |
| `retrieval_budget` | `token_budget: int` | Yes (must be > 0) | `__post_init__` check exists |
| `replay_key` | `route_replay_key: str` | Yes (must be non-empty on live runs) | Test assertion |
| `gate_refs` | `gate_verdict_refs` on FEC, not RouteContract — **OWNED BY FEC** | FEC must carry refs post-C0 | `test_unknown_or_missing_gate_not_pass` |

### FEC Required Fields (C0 Output)

The following fields must be populated (not empty/UNKNOWN with silent pass) in the `FinalEvidenceContract` emitted by `c0_retrieve_apps_rg`:

| FEC field | Required state | Failure mode if absent |
|---|---|---|
| `evidence_items` | Non-empty tuple | `support_status = EMPTY` → Exit hard-fail or HITL |
| `evidence_strata` | Non-empty when Chroma active | `UNKNOWN` — treated as non-passing |
| `citation_map` | Non-empty when Chroma active | Citation gate fails |
| `source_lineage_map` | Non-empty when Chroma active | Lineage gate fails |
| `freshness_receipts` | One per source with freshness class | G09 gate cannot be PASS |
| `acl_verification_receipts` | One per source with ACL check | G08 gate cannot be PASS |
| `contradiction_report` | Non-empty string when C0.3 graph active; empty string permitted when not active BUT `not_applicable_reason` must be set | Contradiction gate silently skips |
| `support_status` | One of `PASS / PARTIAL / WEAK / EMPTY / BLOCKED / CONFLICTED` — never `UNKNOWN` at Exit entry | Exit MUST treat UNKNOWN as fail |
| `final_evidence_digest` | Non-empty string | Provenance chain broken |
| `gate_verdict_refs` | Non-empty tuple — ≥1 ref per declared C0 gate | `test_unknown_or_missing_gate_not_pass` |

---

## §6 — When Direct apps_rg C0 Should Run

**Run C0 candidate-fact retrieval when:**
- Candidate-owned facts needed: career history, project evidence, skills, certifications
- Section-level grounding needed for executive summary, headline, or top experience bullets (after W4)
- Claim verification: check structured generated fields against known candidate facts (after W5)
- `route.grounding_required = True` (always true for `evidence_grounded_generation` route family)

**Skip Chroma company-research lanes when:**
- Authoritative, fresh briefing supplied via `manual_brief_path` — candidate-fact lanes still run
- apps_research delegated via L3 for company research — candidate-fact lanes still run
- `generation_mode` is `healing_fact_check` or `healing_unsupported_claim` → `validation_only` route family → skip all Chroma

**Never run inside apps_rg C0:**
- Company-research retrieval when brief already supplied (briefing-bypass gate blocks it)
- Graph traversal (C0.3 adapter is CONFIG_PREPARED_ONLY; `live_wiring_deferred: true`)
- Any write to L4, UWG, or durable store
- Any instruction injection (retrieved text must remain in C0 data slot only)

**Route policy table:**

| Condition | Company-research Chroma | Candidate-fact Chroma | Outcome |
|---|---|---|---|
| `manual_brief_path` + AUTHORITATIVE + fresh | SKIP (G_BRIEF_BYPASS) | RUN | FEC populated from brief + candidate facts |
| `manual_brief_path` + AUTHORITATIVE + STALE | SKIP with WEAK_WITH_CAVEATS flag | RUN | FEC support_status = WEAK |
| `manual_brief_path` + UNKNOWN authority or ACL=DENIED | BLOCKED | RUN | FEC support_status = BLOCKED for brief; candidate facts still retrieved |
| `auto_research_internal=True` → apps_research via L3 | Handled by apps_research | RUN after delegation | Company brief via SubstrateReturnPacket; candidate facts via C0 |
| No briefing, no auto-research, company research required, `CHROMA_PERSIST_DIR` set | **DO NOT RUN** — route to apps_research via L3 | RUN after apps_research delegation | apps_rg C0 never holds a company-research Chroma path; apps_research handles it; candidate facts retrieved by C0 after delegation |
| No briefing, no auto-research, company research not required, `CHROMA_PERSIST_DIR` set | **DO NOT RUN** | RUN | Proceed with JD/resume/candidate facts only |
| No briefing, no auto-research, no CHROMA_PERSIST_DIR | N/A (file-only) | N/A (file-only) | File-only path |
| `generation_mode` = `healing_fact_check` or `healing_unsupported_claim` | SKIP | SKIP | Reuse prior FEC |
| `route.grounding_required = False` | ERROR — ValueError raised | ERROR — ValueError raised | Hard fail |

---

## §7 — Wave Structure (Fixed Ordering)

| Wave | Phase IDs | Focus | Est. Tokens | Gate | Status | Success Criteria |
|---|---|---|---|---|---|---|
| W0 | P0.1 | Analysis, plan on disk, gap matrix | 8k | Analysis only, no code | **Completed** | Analysis complete; plan filed |
| W1 | P1.1–P1.3 | **Prove current C0 dispatch and FEC presence.** CI tests asserting current path is wired before any new behaviour is added. | 6k | All tests must pass before W2 starts | **Completed** | `test_apps_rg_dispatch_always_produces_fec`, `test_grounding_required_false_blocks_c0`, `test_unknown_or_missing_gate_not_pass` green |
| W2 | P2.1–P2.3 | `fact_vectors` schema + ingest pipeline. Separate collection from `process_docs`. | 10k | EMBEDDING_ENABLED + CHROMA_PERSIST_DIR env vars available | **Completed** | `test_fact_vectors_collection_separate_from_process_docs` + ≥10 chunks ingestable from sample resume |
| W3 | P3.1–P3.3 | Authoritative briefing gate (bypass when brief present + fresh). | 6k | W1 done | **Completed** | `test_briefing_bypass_gate_allows_c0` + `test_stale_briefing_blocks_with_caveat` green |
| W4 | P4.1–P4.2 | Section-level retrieval profile + bounded section sub-query in C0 binding. Requires W2 (fact_vectors exists). | 8k | W2 done; fact_vectors populated | **Completed** | `test_section_retrieval_bounded_by_profile` passes |
| W5 | P5.1–P5.2 | Exact metadata filtering (Chroma `where` clause) for `employer`, `title`, `certification`, `year`, `skill`, `project_name`, `source_class`, `app=apps_rg`. Populate `metadata_score` field on EvidenceItem. Minimal deterministic claim checker (structured fields only). | 6k | W2+W4 done | **Completed** | `test_metadata_filter_retrieves_exact_employer_name` passes; metadata filter + claim checker implemented |
| W6 | P6.1 | L6 retrieval quality span + `otel_span_refs` in FEC. Observability span emission for post-runtime L6 consumption. | 4k | OTEL collector running | **Completed** | `test_l6_retrieval_span.py` passes; span ref included in FEC.otel_span_refs |
| W7 | P7.1–P7.3 | CI gate registration + boundary gate + closeout evidence bundle + W7 advisory triage addendum. | 4k | All prior waves done | **Completed** | Boundary CI PASS_WITH_ADVISORY; 111 findings classified (0 C0-specific blockers); closeout report updated with addendum |

## §13 — Definition of Done

| DoD ID | Criterion | Verification |
|---|---|---|
| DoD-1 | Plan on disk and Notion row created (Not Started status) | This file exists; Notion row confirmed |
| DoD-2 | W1 baseline tests green before any new retrieval code merged | CI run of W1 tests exits 0 |
| DoD-3 | `fact_vectors` schema declared; collection provably separate from `process_docs` | `test_fact_vectors_collection_separate_from_process_docs` passes |
| DoD-4 | Briefing-bypass gate enforced; stale/unauthorized brief → BLOCKED/WEAK, never silent PASS | `test_stale_brief_produces_blocked_not_pass` passes |
| DoD-5 | Section retrieval bounded by profile; no unbounded Chroma queries | `test_section_retrieval_bounded_by_profile` passes |
| DoD-6 | All 11 hard CI gates from §10 green | Confirmed by `pytest tests/_apps_contract/ -v` |
| DoD-7 | No new `apps_rg` literals in `agentic_core/` | `test_no_apps_rg_literals_in_agentic_core` + `check_apps_rg_c0_boundary.py` green |
| DoD-8 | Smoke run exits 0 without modifying any `agentic_core` file | `APPS_RG_L2_FORCE_STUB=1 python -m apps_rg --dry-run ...` exits 0 |
### Verification-vs-Deferral

| Item | Verified in this plan | Deferred |
|---|---|---|
| `fact_vectors` schema + ingest | DoD-3 | Ingest from live resumes (needs real candidate data) |
| LLM-graded free-text claim verification | No — deferred | Post-W5: requires holdout set, hallucination judge |
| InsurTech / IBM / EY section profiles | No — deferred | After section retrieval pattern proven (DoD-5) |
| C0.3 graph RAG live wiring | No — deferred | Requires `AGENTIC_CORE_EDIT_PROOF` generic infra edit; activate only after G1+G6 proven |
| L6 full causal correlation pipeline | W6 span only (DoD-6) | Full causal analysis |
| apps_research delegation correctness | Existing contract tests cover this | N/A |

---

## §14 — Closeout Checklist

- [x] No new `apps_rg` / `fact_vectors` / `master_resume` / `jd_payload` / `resume_payload` / resume-section literals in `agentic_core/` (CI gate green)
- [x] All new retrieval behavior driven by YAML in `apps_rg/config/domain_contract/`; no hardcoded section names in Python
- [x] `c0_retrieve_apps_rg` raises `ValueError` if `grounding_required=False` — AND dispatch-level test confirms
- [x] FEC has non-empty `gate_verdict_refs` or each gate has explicit `NOT_APPLICABLE` with reason — no silent UNKNOWN
- [x] Manual brief: freshness + authority checked before skip; stale → BLOCKED/WEAK_WITH_CAVEATS, never silent PASS
- [x] Candidate-fact Chroma lanes not bypassed by `manual_brief_path`
- [x] Metadata filter lane uses Chroma `where` clause only — no BM25 library introduced
- [x] `metadata_score` and `dense_score` on EvidenceItem are populated separately; never conflated; no `bm25_score` field added unless BM25 is explicitly implemented
- [x] `X3DispositionReceipt` emitted exactly once per run
- [x] No C0 / PA / L2 / Exit / L6 direct durable writes (import graph checked) — **111 boundary findings all classified as pre-existing or false positive**
- [x] All 11 hard CI gates from §10 green
- [x] Smoke run exits 0 with `APPS_RG_L2_FORCE_STUB=1`
- [x] apps_research delegation tests still green (no regression to L3 handoff)

**Closeout Evidence:**
- Closeout report: `artifacts/w7_closeout/apps_rg_c0_closeout_2026_05_14.md`
- W7 Advisory Triage Addendum added with boundary CI classification
- Boundary CI Result: **PASS_WITH_ADVISORY** (22 ERRORs classified as pre-existing L2→L4 imports, 89 WARNs as false positives)
- C0-specific verification: 0 Chroma mutations, 0 L4/UWG imports, 0 L6 invocations, 0 apps_rg leakage
