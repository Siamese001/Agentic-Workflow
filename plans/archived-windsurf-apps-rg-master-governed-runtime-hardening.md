---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\apps-rg-master-governed-runtime-hardening.md'
original_relative_path: 'apps-rg-master-governed-runtime-hardening.md'
source_sha256: 024b80d7122733db7a6a40151239b953527c225e0dd40b7e3bb85f1703fa3058
recovered_status: LOST_RECOVERED
last_commit: '59da21e70c5'
last_commit_date: '2026-05-13 12:21:45 -0400'
created_date: '2026-05-13'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: apps-rg-master-governed-runtime-hardening
plan_type: governance
touches_agentic_core: false
touches_governance_ci: true
touches_windsurf_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# apps_rg Master Governed Runtime Hardening — Zero-Loss Portfolio Consolidation

Collapse 8 overlapping apps_rg plans into one sequenced master implementation plan with clear phase ownership, no conflicting scope, and preserved valid detail from all sources. Separates apps_rg-local implementation from generic core-enabling work under Author-Gate.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: TODO
CURRENT_WAVE: W0
LAST_COMPLETED_WAVE: NONE
LAST_UPDATED: 2026-05-13

---

## Executive Recommendation

**This Master Plan is the orchestration plan for the portfolio. It owns apps_rg-local sequencing and references Author-Gated generic core-enabling tracks. It does not itself authorize or implement core changes.**

These 8 plans must not be executed literally as separate tracks. They overlap, conflict on sequencing, and duplicate governance concerns. Execute instead as:

1. **This Master Plan** — Orchestration plan with apps_rg-local sequencing and core-enabling references
2. **Core L5 Certification Packet Producer Plan** — Generic core-enabling work Phase 4A (Author-Gated)
3. **Existing Core G29 Promotion Proof Plan** — Generic L6/promotion/L4 namespace parser Phase 4B (Author-Gated)
4. **Reference-Only Source Plans** — 8 source plans updated with consolidation banners

### Track Split

| Track | Phases | Description |
|-------|--------|-------------|
| apps_rg-local | 0, 1, 2, 3, 6, 7, 8, 9, 10, 11, 12, 13 | apps_rg-owned implementation |
| Author-Gated core-enabling | 4A, 4B | Separate Author-Gated plans only |
| Phase 5 status | AUTHOR-GATED CORE-ENABLING OR NO-OP | Inspect before execution; if fields exist, Phase 5 is verification only |

**Key Portfolio Conclusions:**
- Direct semantic cache write removal is P0 (reachable UWG bypass)
- Missing L5CertificationPacket is a governed-release blocker but belongs in generic core
- `l6_shadow_learning.py` must be deleted/quarantined unless live caller proof exists
- Structured resume must not repair L6 code; only verify canonical Exit→RuntimeExhaustBundle handoff
- `fact_vectors` is product-quality foundation, not a safety blocker for L4/L5 closure
- Company research stays in `apps_research` or authoritative briefing, never direct apps_rg C0
- HITL governance deferred unless human modification/re-entry is in scope
- LLM judges and benchmark calibration deferred until deterministic checks exist

---

## Resume Shipping Critical Path

**Purpose:**
Accelerate the work needed to generate and send high-quality resumes before completing the full governed-production hardening sequence.

**Important distinction:**
apps_rg may be used for local/dev resume generation after this lane passes. It must not be called L5-governed or production-governed until the governed-production blockers are closed.

**Fast-track phases:**

**S0 — Fast Runtime Path Inventory**
- Source: Structured W0A, Master Phase 0 subset
- Scope:
  - Identify exactly one active generation path
  - Confirm dispatch -> bindings -> U0/L1/L0/C0/PA/L2/Exit
  - Confirm quarantined/legacy paths are not active
  - Capture current generated output artifact
- Exit gate:
  - exactly one active generation path proven
  - no active imports from quarantined paths

**S1 — Structured Resume Schema and Ingestion**
- Source: Structured W1/W3
- Scope:
  - source_resume_v2_structured.json
  - normalized section IDs
  - narrative vs bullets separation
  - verbatim fields for education, certifications, early career
  - backward-compatible flat text fallback
- Exit gate:
  - source resume parses into headline, exec_summary, Unify, IBM, InsurTech, EY, early_career, competencies, education, certifications

**S2 — Section-by-Section Treatment Matrix**
- Source: Structured section processing design
- Scope:
  - headline heavy
  - exec summary heavy
  - Unify narrative verbatim
  - Unify bullets 1-3 heavy, 4-5 moderate, 6 light
  - IBM narrative verbatim
  - IBM bullets 1-2 moderate, 3-5 light
  - InsurTech bullets moderate
  - EY bullets light
  - early career verbatim
  - competencies JD-ranked 2-4 word noun phrases
  - education/certifications verbatim
- Exit gate:
  - every section has treatment policy, rewrite budget, and preservation rule
  - no generic fallthrough rewrite

**S3 — PA Tiered Prompt Patching**
- Source: Structured W2
- Scope:
  - provider-neutral prompt structure
  - exact source-span first
  - JD alignment field
  - rewritten bullet field
  - blocked_items field
  - INSUFFICIENT_SOURCE_SUPPORT status
  - anti-invention rules: no new metrics, clients, tools, domains, scope, titles, impacts without source support
- Exit gate:
  - each rewritten bullet has source_span, jd_alignment, rewritten_bullet, blocked_items, status

**S4 — U0 Structured Resume Support**
- Source: Structured W3
- Scope:
  - detect structured resume input
  - preserve flat text fallback
  - pass structured sections into PA
  - preserve base resume + JD + briefing inputs
- Exit gate:
  - same CLI runs with structured JSON and legacy flat input

**S5 — Runtime Executive Summary Display Fix**
- Source: Structured W4
- Scope:
  - display live path as U0 -> L1 -> L0 -> C0 -> PA -> L2 -> Exit
  - display L6 only as post-runtime
  - display writeback as inert unless UWG receipt exists
- Exit gate:
  - no output claims L6 is in live generation path
  - no output claims cache writes are durable without UWG

**S6 — Deterministic Resume Exit Checks**
- Source: Structured W6/G21/G22 subset
- Scope:
  - headline one-line check
  - exec summary shape check
  - bullet count checks
  - verbatim hash checks for education/certs/early career
  - unsupported claim/status checks
  - UNKNOWN never PASS
- Exit gate:
  - resume is structurally sendable
  - unsupported sections block automatic acceptance

**S7 — Minimum C0 Safety**
- Source: C0 Phase 9 subset
- Scope:
  - C0 dispatch proof when grounding_required=true
  - FEC completeness check
  - authoritative briefing freshness/authority
  - weak support never promoted to PASS
  - no company research lane inside apps_rg C0
- Explicitly defer:
  - fact_vectors
  - ingest pipeline
  - BM25
  - LLM free-text claim verification
- Exit gate:
  - grounding-required route cannot bypass C0
  - stale/unauthorized briefing cannot become PASS
  - weak support stays WEAK

**S8 — Manual Section Review Harness**
- Source: new operational shipping layer
- Scope:
  - produce section review artifact with generated text, source support, issues, approve/edit/retry
  - support headline, exec_summary, competencies, and each role section
- Exit gate:
  - human can approve or reject each section before sending
  - review artifact is saved with generated resume

**S9 — Resume-Shipping Cache Safety**
- Source: Master Phase 1 minimum subset
- Scope:
  - either replace direct semantic cache write with inert proposal-only OR hard-disable semantic cache writes in resume-shipping mode
- Exit gate:
  - resume-shipping mode does not mutate semantic cache

### Lane Requirements Table

| Lane | Required before sending resumes? | Required before governed production? |
|------|--------------------------------|--------------------------------------|
| Resume Shipping Critical Path S0-S9 | Yes | Not sufficient |
| Full L5CertificationPacket producer | No | Yes |
| Core G29 / promotion proof | No | Yes |
| Full UWG/L4 proposal lifecycle | No, except cache disabled/proposal-only | Yes |
| fact_vectors | No | Later product-quality foundation |
| L6 shadow learning | No | Later future-run learning |
| LLM judges/benchmarks | No | Later calibration hardening |
| HITL governance | No unless human edits re-enter runtime | Yes if human re-entry is enabled |

### Master Sequence Note (Updated)

- The original Phase 0-13 sequence remains the governed-production track.
- The Resume Shipping Critical Path may execute before the full governed-production sequence.
- Phase S9 must ensure no semantic cache durable mutation occurs during resume-shipping runs.
- Do not market or label output as L5-governed until Phase 4A, Phase 8, and final governance gates are complete.

---

## Proposed Master Sequence

| Phase | Source Plan Waves | Dependency | Scope | Why Now | Files Likely Touched | Exit Gate | Stop Condition |
|-------|-------------------|------------|-------|---------|---------------------|-----------|----------------|
| **0** | All W0/W0A baselines | None | Unified baseline receipt, import graph, direct-write scan, L6 caller proof, core diff proof, runtime path inventory | Foundation for all downstream phases | `artifacts/governance/apps_rg_master_w0_baseline_receipt.json`, `artifacts/ci/direct_semantic_cache_write.json`, `artifacts/ci/apps_rg_runtime_path_inventory.json` | W0 baseline receipt exists | Active import from quarantined paths |
| **1** | L4 W1, L6 W1, L5 GAP-002 | Phase 0 | Remove direct semantic cache writes, replace with inert `SectionCacheWriteProposal`, surface through Exit only | P0 UWG bypass blocker | `apps_rg/runtime/section_agentic_pipeline.py`, `apps_rg/runtime/schemas/__init__.py`, `apps_rg/runtime/bindings/exit_binding.py`, `ops_scripts/ci/check_no_direct_semantic_cache_write.py`, `tests/governance/test_apps_rg_uwg_cache_write_sovereignty.py` | `check_no_direct_semantic_cache_write.py` passes | Any runtime imports cache writer directly |
| **2** | L4 W2, L6 W2, Structured W10 | Phase 1 | Delete/quarantine app-local L6 runtime, rename spans to section observation, prove zero importers | Duplicate L6 surface removal | `apps_rg/runtime/l6_shadow_learning.py`, `apps_rg/_quarantine/`, `apps_rg/runtime/schemas/__init__.py`, `apps_rg/runtime/section_agentic_pipeline.py`, `ops_scripts/ci/check_no_apps_rg_runtime_l6_engine.py`, `tests/governance/test_apps_rg_l6_surface_ownership.py` | Zero importers proven | Any L6/Shadow/Producer engine remains active |
| **3** | L4 W3/W5/W6, Structured W8.3 | Phase 2 | L4 namespace manifest, durable write allowlists, Exit proposal-only path, Chroma readonly guard, filesystem write CI | Write boundary lockdown | `apps_rg/config/l4_namespace_manifest.yaml`, `apps_rg/config/l4_namespace_manifest.schema.json`, `apps_rg/runtime/bindings/exit_binding.py`, `ops_scripts/ci/check_apps_rg_l4_write_boundary.py`, `ops_scripts/ci/check_apps_rg_chroma_readonly.py`, `ops_scripts/ci/check_apps_rg_exit_no_direct_writes.py`, `tests/_apps_contract/test_apps_rg_l4_namespace_manifest.py` | All CI gates pass | Exit writes files directly or Chroma mutations occur |
| **4A** | L5 GAP-001/GAP-003 | Phase 0 + Author-Gate PASS; can run in parallel with Phases 1–3 | Generic `L5CertificationPacket` producer, child certifier aggregation, shared `l5_governance_context_digest`, generic egress receipt producer/interface | Core-enabling work (Author-Gated) | `agentic_core/L5_safety/certification/l5_packet_producer.py`, `agentic_core/L5_safety/certification/egress_certifier.py`, `agentic_core/L5_safety/contracts/*`, `tests/unit/agentic_core/L5_safety/*` | Core receipt with Author-Gate PASS | Producer contains apps_rg literals |
| **4B** | Core G29 W1-W3; apps_rg L6 W4/W5 are reference-only/downstream verification | Phase 0 + Author-Gate PASS; can run in parallel with Phases 1–3 | PromotionGauntlet.GATE_ID, L6GauntletResult.gate_id, FutureRunPromotionRequest proof fields, generic L4 namespace parser | Core-enabling work (Author-Gated) | `agentic_core/L6_learning/promotion_gauntlet.py`, `agentic_core/L6_learning/__init__.py`, `agentic_core/L4_state/contracts/l4_namespace_contract.py`, `tests/unit/agentic_core/L6_learning/test_promotion_gauntlet.py` | Core receipt with Author-Gate PASS | Parser has app-specific literals |
| **5** | L1 W1-W4, L0 P1.3/P5.1 core parts | AUTHOR-GATED CORE-ENABLING OR NO-OP; inspect whether generic L1/L0 contract fields already exist before execution | Generic L1/L0 contract field enablement OR verification only if fields exist | Contract foundation | `agentic_core/runtime/contracts/l1_plan_contract.py`, `agentic_core/runtime/contracts/route_contract.py`, `agentic_core/runtime/contracts/route_gate_receipt.py` | Contract tests pass | Contract fields contain app-specific enums |
| **6** | L1 W2-W5 apps-local | Phase 5 | U0 emits L1 planning profile ref/digest, L1 validates digest fail-closed, advisory work-shape hints | apps_rg L1 wiring | `apps_rg/runtime/u0/payload_synthesizer.py`, `apps_rg/runtime/bindings/l1_binding.py`, `apps_rg/profiles/rg_planning_profile.yaml`, `tests/_apps_contract/test_apps_rg_l1_profile_wiring.py`, `tests/_apps_contract/test_apps_rg_l1_work_shape.py`, `tests/_apps_contract/test_apps_rg_l1_non_authority.py` | All L1 tests pass | Missing profile silently passes |
| **7** | L0 W1-W6 apps-local | Phase 5 | Canonical route profile path, fail-closed loader, route_family/execution_form/allowed_next_stage, typed gate receipts, cache bypass | apps_rg L0 wiring | `apps_rg/runtime/bindings/l0_binding.py`, `apps_rg/config/domain_contract/route_profiles.yaml`, `apps_rg/runtime/bindings/pa_binding.py`, `tests/_apps_contract/test_l0_gate_verdicts.py`, `tests/_apps_contract/test_l0_execution_form.py`, `tests/_apps_contract/test_l0_cache_bypass.py`, `tests/_apps_contract/test_l0_canonical_profile_path.py` | All L0 tests pass | L0 manufactures PASS from missing facts |
| **8** | L5 GAP-001/GAP-003 app wiring | Phase 4A/6/7 | Wire apps_rg U0/L1/L0/C0/PA/L2/Exit to L5 packet refs, add egress receipts around ProviderGateway | L5 integration | `apps_rg/runtime/bindings/u0_binding.py`, `apps_rg/runtime/bindings/l1_binding.py`, `apps_rg/runtime/bindings/l0_binding.py`, `apps_rg/runtime/bindings/c0_binding.py`, `apps_rg/runtime/bindings/pa_binding.py`, `apps_rg/runtime/bindings/l2_binding.py`, `apps_rg/runtime/bindings/exit_binding.py`, `apps_rg/config/domain_contract/l5_governance_profile.yaml`, `tests/_apps_contract/test_apps_rg_l5_certification_packet.py`, `tests/_apps_contract/test_apps_rg_l2_egress_receipts.py` | L5 packet + egress receipts present | Provider call lacks EgressCertificationReceipt |
| **9** | C0 W1/G2/G3/G4 min safety | Phase 8 | C0 dispatch proof, FEC completeness, briefing authority/freshness, weak support never promoted | C0 minimum safety | `apps_rg/runtime/bindings/c0_binding.py`, `apps_rg/config/domain_contract/runtime_gate_profile.resume_generation.v1.json`, `apps_rg/config/domain_contract/research_delegation_profile.yaml`, `tests/_apps_contract/test_apps_rg_c0_dispatch.py`, `tests/_apps_contract/test_apps_rg_c0_briefing_bypass.py`, `tests/_apps_contract/test_apps_rg_fec_completeness.py` | All C0 tests pass | C0 bypasses when grounding_required=True |
| **10** | Structured W0A-W6 | Phase 9 | Structured resume schema, U0 structured input, PA tiered prompts, Exit G21/G22 gates | Product quality | `apps_rg/runtime/schemas/source_resume_v2_structured.json`, `apps_rg/runtime/u0/payload_synthesizer.py`, `apps_rg/runtime/bindings/pa_binding.py`, `apps_rg/runtime/bindings/u0_binding.py`, `apps_rg/runtime/bindings/exit_binding.py`, `tests/_apps_contract/test_source_resume_schema_v2.py`, `tests/_apps_contract/test_exit_binding_structured_output.py`, `tests/_apps_contract/test_apps_rg_pa_tiered_prompt.py`, `tests/_apps_contract/test_apps_rg_exit_g21_g22.py` | Schema + quality gates pass | Narrative intros rewritten instead of verbatim |
| **11** | C0 W2-W6, Structured W7 | Phase 10 | fact_vectors schema, ingest pipeline, collection routing, section retrieval, deterministic claim verification | Product foundation | `apps_rg/config/domain_contract/fact_vectors_schema.yaml`, `apps_rg/tools/fact_vector_ingest.py`, `apps_rg/config/domain_contract/section_retrieval_profile.yaml`, `tests/_apps_contract/test_fact_vectors_collection_separate_from_process_docs.py`, `tests/_apps_contract/test_section_retrieval_bounded_by_profile.py`, `tests/_apps_contract/test_metadata_filter_retrieves_exact_employer_name.py`, `tests/_apps_contract/test_claim_verification_flags_ungrounded_employer.py` | Section retrieval + claim verification pass | candidate_profile mixed into process_docs |
| **12** | L6 W3-W6 apps-local, Core G29 outputs | Phase 10/4B | Exit to canonical RuntimeExhaustBundle, ObserverLaw tests, future-run-only promotion | L6 handoff | `apps_rg/runtime/bindings/exit_binding.py`, `tests/governance/test_apps_rg_l6_handoff_contract.py`, `tests/runtime/test_l6_observer_law_prohibitions.py`, `tests/governance/test_l6_promotion_uwg_required.py` | ObserverLaw + promotion tests pass | L6 emits X3 or writes cache/L4 |
| **13** | All CI/99 closeouts | Phase 12 | Register gates, run smoke, run contract gates, produce non-contamination proof, 99 proof bundle | Closeout | `ops_scripts/ci/run_contract_gates.py`, `artifacts/governance/apps_rg_master_closeout_receipt.json`, `artifacts/governance/apps_rg_99_proof_bundle.json` | All gates pass, 99 proof produced | Any UNKNOWN treated as PASS |

---

## Dependency Graph

```text
                         ┌──────────────────────────────┐
                         │ Phase 0 Unified Baseline      │
                         │ import graph + CI + receipts  │
                         └──────────────┬───────────────┘
                                        │
                 ┌──────────────────────┼────────────────────────┐
                 │                      │                        │
                 ▼                      ▼                        ▼
   ┌────────────────────────┐  ┌─────────────────────┐  ┌─────────────────────────┐
   │ Phase 1 P0 Cache Bypass │  │ Phase 4A Core L5    │  │ Phase 4B Core G29/L4    │
   │ remove direct writes    │  │ packet + egress     │  │ namespace + promotion   │
   └────────────┬───────────┘  │ Author-Gated        │  │ Author-Gated           │
                │              └──────────┬──────────┘  └──────────┬──────────────┘
                ▼                         │                        │
   ┌────────────────────────┐             │                        │
   │ Phase 2 L6 duplicate    │             │                        │
   │ delete/quarantine       │             │                        │
   └────────────┬───────────┘             │                        │
                ▼                         │                        │
   ┌────────────────────────┐             │                        │
   │ Phase 3 L4 write guards │◄────────────┘                        │
   │ manifest + CI           │                                      │
   └────────────┬───────────┘                                      │
                │                                                  │
                ▼                                                  │
   ┌────────────────────────┐                                      │
   │ Phase 5 Generic L1/L0   │                                      │
   │ contract fields         │                                      │
   └────────────┬───────────┘                                      │
                ▼                                                  │
   ┌────────────────────────┐                                      │
   │ Phase 6 L1 app wiring   │                                      │
   │ profile digest + hints  │                                      │
   └────────────┬───────────┘                                      │
                ▼                                                  │
   ┌────────────────────────┐                                      │
   │ Phase 7 L0 route wiring │                                      │
   │ typed gates + route     │                                      │
   └──────┬─────────┬───────┘                                      │
          │         │                                              │
          ▼         ▼                                              │
┌────────────────┐ ┌────────────────────────┐                      │
│ Phase 8 L5 app  │ │ Phase 9 C0 min safety  │                      │
│ cert wiring     │ │ FEC + brief gates      │                      │
└──────┬──────────┘ └──────────┬─────────────┘                      │
       │                       ▼                                    │
       │          ┌──────────────────────────┐                      │
       │          │ Phase 10 Structured       │                      │
       │          │ resume + PA + Exit gates  │                      │
       │          └──────────┬───────────────┘                      │
       │                     ▼                                      │
       │          ┌──────────────────────────┐                      │
       │          │ Phase 11 C0 fact_vectors  │                      │
       │          │ section retrieval claims  │                      │
       │          └──────────┬───────────────┘                      │
       │                     │                                      │
       └─────────────────────┼──────────────────────────────────────┘
                             ▼
              ┌──────────────────────────────┐
              │ Phase 12 L6 canonical exhaust │
              │ ObserverLaw + future promote  │
              └──────────────┬───────────────┘
                             ▼
              ┌──────────────────────────────┐
              │ Phase 13 CI / 99 closeout     │
              └──────────────────────────────┘
```

**Note:** Phase 4A and Phase 4B are parallel Author-Gated core-enabling tracks after Phase 0. They are not blocked by apps_rg-local Phases 1–3. Phase 8 depends on Phase 4A. Phase 12 depends on Phase 4B.

---

## Overlap and Redundancy Inventory

| # | Overlap Area | Source Plans | Consolidation |
|---|--------------|--------------|---------------|
| 1 | Direct semantic cache write removal | L4 W1, L6 W1, L5 GAP-002, Structured W8.3 | Master Phase 1 owns implementation. Use strongest tests from L6 W1 and provenance schema from L4 W1. |
| 2 | App-local L6 duplicate runtime surface | L4 W2, L6 W2, Structured W10 | Master Phase 2 owns deletion/quarantine. Structured W10 rewritten as canonical L6 handoff verification only. |
| 3 | G29 and promotion proof fields | L6 W4/W5, Core G29 plan | Core G29 plan owns all core edits. L6 W4/W5 become reference-only/downstream tests. |
| 4 | L4 namespace manifest/parser | L4 W3, Core G29 W2 | apps_rg manifest is local; generic parser is Core G29. Keep split. |
| 5 | Runtime path inventory | Structured W0A, L4 W0, L6 W0/W2 | Master Phase 0 owns one import graph and one classification artifact. |
| 6 | Core boundary CI | Structured W5, L1 W4, L0 W6, L4 W6 | One consolidated `check_apps_rg_core_boundary.py` plus targeted tests. |
| 7 | L1 work-shape and L0 work-shape/task-shape | L1, L0 | L1 emits advisory hints only; L0 owns route selection. |
| 8 | Route/provider model refs | L0 W5, L5 egress GAP-003, PA structured prompts | RouteContract provider ref → PA consumes ref → L2 ProviderGateway emits egress receipt. |
| 9 | C0 evidence trust | C0 plan, Structured W7, L5 replay/profile gaps | Minimum C0 safety in Phase 9; fact_vectors in Phase 11. |
| 10 | Exit G21/G22 and judge inventory | Structured W6/W9, L6 learning | Deterministic G21/G22 first; LLM judges and benchmark calibration deferred. |
| 11 | HITL governance | L5 GAP-004, structured human review | Deferred unless human modification/re-entry is in release scope. |
| 12 | C0 company research | C0 plan, apps_research delegation | Hard ban inside apps_rg C0. Company research remains apps_research or authoritative briefing. |
| 13 | fact_vectors priority | C0, structured resume | Product-quality foundation after structured schema, not a safety blocker. |

---

## Consolidated Implementation Runbook

### Phase 0 — Unified Baseline

**Validation Commands (Plan-Only Scope):**
```bash
# Verify all 8 source plans have consolidation banners (strict: only CONSOLIDATED_UNDER_MASTER in PORTFOLIO_STATUS)
rg "PORTFOLIO_STATUS: CONSOLIDATED_UNDER_MASTER" .windsurf/plans/apps-rg-*.md .windsurf/plans/core-l6-g29-promotion-proof-hardening-d9e3b2.md

# Verify dispositions are specific and correct
rg "DISPOSITION: (ACTIVE_SEPARATE_CORE_PLAN|MERGED_INTO_MASTER|MERGED_INTO_MASTER_WITH_CORE_SPLIT|MERGED_INTO_MASTER_SPLIT_BY_PRIORITY|MERGED_INTO_MASTER_WITH_CONFLICT_RESOLUTION|GAP_REPORT_REFERENCE|SUPERSEDED_REFERENCE_ONLY)" .windsurf/plans/apps-rg-*.md .windsurf/plans/core-l6-g29-promotion-proof-hardening-d9e3b2.md

# Verify only plan files changed
git diff --name-only | rg -v "^\.windsurf/plans/" && exit 1 || true
```

**Stop Condition:**
- Any source plan missing the consolidation banner blocks closeout

**Commands to execute:**
```bash
# Baseline contract gates
python ops_scripts/ci/run_contract_gates.py

# Direct semantic cache write scan
python ops_scripts/ci/check_no_direct_semantic_cache_write.py

# Test collection baseline
python -m pytest --collect-only -q

# Import graph verification
rg "agentic_core.L0_routing.apps_rg_l0_binding|agentic_core.L1_cognition.apps_rg_l1_binding" . --include="*.py"

# L6 shadow learning surface scan
rg "l6_shadow_learning|write_section_to_semantic_cache|APPS_RG_CACHE_WRITE_ENABLED" apps_rg agentic_core --include="*.py"
```

**Artifacts produced:**
- `artifacts/governance/apps_rg_master_w0_baseline_receipt.json`
- `artifacts/ci/direct_semantic_cache_write.json`
- `artifacts/ci/apps_rg_runtime_path_inventory.json`

**Stop conditions:**
- Active import from quarantined paths found
- `section_agentic_pipeline.py` not actually active despite L5 reachability proof
- Any core source edit attempted before Author-Gate

### Phase 1 — Remove Direct Cache Writes

**Commands:**
```bash
# Gate verification (must pass at end)
python ops_scripts/ci/check_no_direct_semantic_cache_write.py

# Test verification
pytest tests/governance/test_apps_rg_uwg_cache_write_sovereignty.py -v

# Dry-run verification
python -m apps_rg --dry-run
```

**Stop conditions:**
- Any runtime imports `apps_rg.cache.r1b_semantic.write_section_to_semantic_cache`
- Any dry-run writes under `artifacts/apps_rg/semantic_cache/`
- Proposal is mutable or missing `PENDING_UWG` status

### Phase 2 — Delete/Quarantine L6 Duplicate

**Commands:**
```bash
# Gate verification
python ops_scripts/ci/check_no_apps_rg_runtime_l6_engine.py

# Test verification
pytest tests/governance/test_apps_rg_l6_surface_ownership.py -v

# Import scan
rg "L6-SHADOW|l6_shadow_learning|produce_l6_shadow_learning" apps_rg --include="*.py"
```

**Stop conditions:**
- Any runtime importer exists
- Any L6/Shadow/Producer engine remains under active apps_rg runtime
- Structured W10 attempts to repair app-local L6 instead of deleting/quarantining

### Phase 3 — L4 Write Guards

**Commands:**
```bash
# Manifest tests
pytest tests/_apps_contract/test_apps_rg_l4_namespace_manifest.py -v

# Write boundary gates
python ops_scripts/ci/check_apps_rg_l4_write_boundary.py
python ops_scripts/ci/check_apps_rg_chroma_readonly.py
python ops_scripts/ci/check_apps_rg_exit_no_direct_writes.py
```

**Stop conditions:**
- Exit writes files directly
- Chroma mutations occur in runtime path
- Manifest is embedded in core instead of apps_rg config
- Durable artifact writes bypass X3C/UWG

### Phase 4A — Core L5 Packet Producer (Author-Gated)

**Author-Gate required before any core edits.**

**Commands:**
```bash
# Core receipt capture
python tools/capture/core_addition_receipt.py --plan core-l5-certification-packet-producer

# Unit tests
pytest tests/unit/agentic_core/L5_safety/ -v

# Boundary verification
python ops_scripts/ci/check_agentic_core_app_agnostic.py
```

**Stop conditions:**
- No Author-Gate PASS receipt
- Producer contains `apps_rg` literals
- L5 emits GateVerdict, X3, or durable commit
- Child certifiers do not share one governance context digest

### Phase 4B — Core G29/L4 Parser (Author-Gated)

**Author-Gate required before any core edits.**

**Commands:**
```bash
# Core receipt capture
python tools/capture/core_addition_receipt.py --plan core-l6-g29-promotion-proof-hardening

# Unit tests
pytest tests/unit/agentic_core/L6_learning/ -v
pytest tests/unit/agentic_core/L4_state/contracts/ -v

# Boundary verification
rg "apps_rg" agentic_core/L4_state/contracts/ && exit 1 || true
```

**Stop conditions:**
- Author-Gate missing
- Parser has app-specific literals
- Promotion request can pass gauntlet without eval/RCA/audit proof refs
- G29 is not present or not populated

### Phase 5 — AUTHOR-GATED CORE-ENABLING OR NO-OP

**Rule:** Before Phase 5, inspect whether the generic L1/L0 contract fields already exist. If they exist, Phase 5 is verification only. If absent, create or use a separate Author-Gated core contract-enablement plan. Do not implement Phase 5 inside the apps_rg master plan.

**Stop Condition:**
- Any attempt to edit `agentic_core/runtime/contracts/*` from the master plan without separate Author-Gated core plan stops execution

**Commands:**
```bash
pytest tests/unit/agentic_core/runtime/contracts/ -v
python ops_scripts/ci/check_agentic_core_app_agnostic.py
```

**Stop conditions:**
- Core contract fields contain resume-specific enum values
- L1 contract gains route authority fields
- RouteContract gets raw provider/model constants instead of refs

### Phase 6 — L1 App Wiring

**Commands:**
```bash
pytest tests/_apps_contract/test_apps_rg_l1_profile_wiring.py -v
pytest tests/_apps_contract/test_apps_rg_l1_work_shape.py -v
pytest tests/_apps_contract/test_apps_rg_l1_non_authority.py -v
```

**Stop conditions:**
- Missing planning profile silently passes
- Digest mismatch does not fail
- L1 route hints use concrete RouteContract enum values
- L1 imports C0/PA/provider code

### Phase 7 — L0 Route Wiring

**Commands:**
```bash
pytest tests/_apps_contract/test_l0_canonical_profile_path.py -v
pytest tests/_apps_contract/test_l0_execution_form.py -v
pytest tests/_apps_contract/test_l0_gate_verdicts.py -v
pytest tests/_apps_contract/test_l0_cache_bypass.py -v
```

**Stop conditions:**
- L0 manufactures PASS from missing facts
- `apps_rg/profiles/rg_route_profile.yaml` is referenced
- `execution_form` is empty
- Personalized drafts allow R1A/R1B semantic cache reuse
- PA hardcodes provider/model instead of consuming ref

### Phase 8 — L5 App Wiring

**Commands:**
```bash
pytest tests/_apps_contract/test_apps_rg_l5_certification_packet.py -v
pytest tests/_apps_contract/test_apps_rg_l2_egress_receipts.py -v
python ops_scripts/ci/check_apps_rg_l5_cert_refs.py
```

**Stop conditions:**
- Layer bindings still emit only isolated hardcoded cert strings
- ProviderGateway call lacks EgressCertificationReceipt
- L5_NOT_CERTIFIED directly emits GateVerdict or X3

### Phase 9 — C0 Minimum Safety

**Commands:**
```bash
pytest tests/_apps_contract/test_apps_rg_c0_dispatch.py -v
pytest tests/_apps_contract/test_apps_rg_c0_briefing_bypass.py -v
pytest tests/_apps_contract/test_apps_rg_fec_completeness.py -v
```

**Stop conditions:**
- C0 bypasses when grounding_required=True
- Stale or unauthorized brief silently passes
- Empty FEC fields are treated as PASS instead of WEAK/UNKNOWN
- apps_rg C0 attempts company research

### Phase 10 — Structured Resume

**Commands:**
```bash
pytest tests/_apps_contract/test_source_resume_schema_v2.py -v
pytest tests/_apps_contract/test_exit_binding_structured_output.py -v
pytest tests/_apps_contract/test_apps_rg_pa_tiered_prompt.py -v
pytest tests/_apps_contract/test_apps_rg_exit_g21_g22.py -v
python -m apps_rg --dry-run
```

**Stop conditions:**
- Narrative intro sentences are rewritten when they should be copied verbatim
- Education/certifications/early career are not hash-preserved
- Prompt asks for unsupported metrics/tools/clients/domains
- W10 tries to repair `l6_shadow_learning.py`

### Phase 11 — C0 fact_vectors

**Commands:**
```bash
pytest tests/_apps_contract/test_fact_vectors_collection_separate_from_process_docs.py -v
pytest tests/_apps_contract/test_section_retrieval_bounded_by_profile.py -v
pytest tests/_apps_contract/test_metadata_filter_retrieves_exact_employer_name.py -v
pytest tests/_apps_contract/test_claim_verification_flags_ungrounded_employer.py -v
```

**Stop conditions:**
- candidate_profile or project_evidence remains mixed into process_docs
- Section names leak into agentic_core
- Metadata filter and dense score are conflated
- Free-text LLM claim verification is added before deterministic structured claim checks

### Phase 12 — L6 Canonical Handoff

**Commands:**
```bash
pytest tests/governance/test_apps_rg_l6_handoff_contract.py -v
pytest tests/runtime/test_l6_observer_law_prohibitions.py -v
pytest tests/governance/test_l6_promotion_uwg_required.py -v
python ops_scripts/ci/check_g29_firewall.py
```

**Stop conditions:**
- L6 emits X3
- L6 writes cache, vector store, or L4
- L6 reroutes, reexecutes, or mutates current run
- Promotion request bypasses UWG or activates before future run start

### Phase 13 — Final CI and 99 Proof

**Commands:**
```bash
python ops_scripts/ci/run_contract_gates.py
python ops_scripts/ci/check_apps_rg_core_boundary.py
python ops_scripts/ci/check_no_direct_semantic_cache_write.py
python ops_scripts/ci/check_no_apps_rg_runtime_l6_engine.py
python -m pytest tests/_apps_contract/ -v
python -m pytest tests/governance/ -v
python -m pytest tests/unit/agentic_core/ -v
python -m apps_rg --dry-run
```

**Stop conditions:**
- Any direct durable write remains
- Any UNKNOWN is treated as PASS
- agentic_core gained app literals outside approved legacy shims
- L5 packet absent from governed run proof
- Egress receipt missing when provider used
- 99 proof lacks replay/audit refs

---

## Final Consolidation Recommendation

1. **Execute by lane**:
   - Resume Shipping Critical Path S0-S9 may run first for local/dev sendable resume generation.
   - S0.5 must complete before any full end-to-end resume-generation smoke run or sendable resume artifact.
   - Governed-production Phase 0-13 remains the full production hardening track and must complete before calling apps_rg L5-governed or production-governed.
   - Phase 0-13 sequencing applies to governed-production closeout, not to the accelerated resume-shipping lane.
2. **Author-Gate all core work** — Phases 4A and 4B require explicit core addition authorization
3. **Preserve source plans as reference** — All 8 source plans updated with consolidation banners
4. **No duplicate L6 surfaces** — `l6_shadow_learning.py` must be deleted/quarantined
5. **No direct cache writes** — All writes UWG-mediated via inert proposals
6. **Generic core work separate** — L5 packet producer and G29 promotion belong in core

---

## Per-Source-Plan Disposition Table

| # | Source Plan | Disposition | Master Phases | Retained Scope | Moved Scope | Deferred Scope |
|---|-------------|-------------|---------------|----------------|-------------|----------------|
| 1 | apps-rg-l4-boundary-hardening-c8f2a1.md | MERGED_INTO_MASTER | 0, 1, 2, 3, 13 | apps_rg-local L4 boundary, namespace manifest, CI gates | Generic L4 parser to Core G29 | None |
| 2 | core-l6-g29-promotion-proof-hardening-d9e3b2.md | ACTIVE_SEPARATE_CORE_PLAN | 4B, 12 | Core G29, promotion proof, L4 parser | apps_rg L6 handoff tests to Phase 12 | None |
| 3 | apps-rg-l5-governance-gap-report-hardened-f8c2e1.md | GAP_REPORT_REFERENCE | 4A, 8, 13 | GAP-001/002/003 evidence, HITL as future | L5 producer to Core L5 plan, wiring to Phase 8 | HITL governance |
| 4 | apps-rg-l6-shadow-learning-hardening-7e4c2f.md | MERGED_INTO_MASTER_WITH_CORE_SPLIT | 0, 1, 2, 12, 13 | Delete/quarantine L6, canonical handoff, ObserverLaw | G29/promotion proof to Core G29 plan | LLM judge calibration |
| 5 | apps-rg-c0-architecture-analysis-f3d8b2.md | MERGED_INTO_MASTER_SPLIT_BY_PRIORITY | 9, 11 | Narrow C0, FEC, fact_vectors | Min safety to Phase 9, fact_vectors to Phase 11 | BM25/sparse, LLM claim verification |
| 6 | apps-rg-structured-resume-refactor-f8c2a1.md | MERGED_INTO_MASTER_WITH_CONFLICT_RESOLUTION | 0, 10, 11, 12 | Structured schema, tiered bullets, G21/G22 | Path inventory to Phase 0, L6 handoff to Phase 12 | LLM judges, benchmark calibration |
| 7 | apps-rg-l0-critical-gaps-remediation-a3f8e1.md | MERGED_INTO_MASTER_WITH_CORE_SPLIT | 5, 7 | Canonical route profile, typed gates, cache bypass | Generic RouteContract to Phase 5, apps wiring to Phase 7 | Terminal RET hardening |
| 8 | apps-rg-l1-contract-wiring-3e7f92.md | MERGED_INTO_MASTER_WITH_CORE_SPLIT | 5, 6 | Deterministic L1, profile refs, work-shape hints | Generic L1PlanContract to Phase 5, apps wiring to Phase 6 | L1 Qwen/vLLM invocation |

---

## Stop Conditions and CI Gates Per Phase

See per-phase runbook above for detailed stop conditions. Summary of key CI gates:

| Gate | Enforces | Phases |
|------|----------|--------|
| `check_no_direct_semantic_cache_write.py` | No direct cache writes | 1, 13 |
| `check_no_apps_rg_runtime_l6_engine.py` | No duplicate L6 surface | 2, 13 |
| `check_apps_rg_l4_write_boundary.py` | L4 manifest compliance | 3, 13 |
| `check_apps_rg_chroma_readonly.py` | Chroma readonly in runtime | 3, 13 |
| `check_apps_rg_exit_no_direct_writes.py` | Exit proposal-only | 3, 13 |
| `check_agentic_core_app_agnostic.py` | No app literals in core | 4A, 4B, 5 |
| `check_apps_rg_core_boundary.py` | Boundary compliance | 13 |
| `run_contract_gates.py` | All gates pass | 0, 13 |

---

## Author-Gate Split

### apps_rg-Local Work (This Master Plan)

- Phases 0–3, 5–13: All apps_rg-local changes
- L4 namespace manifest (app-owned)
- L1/L0/C0/PA/L2/Exit bindings
- U0 profile wiring
- Cache write proposals
- L6 handoff verification

### Generic Core-Enabling Work (Author-Gated Separate Plans)

- **Phase 4A** → `core-l5-certification-packet-producer-hardening.md`
  - Generic `L5CertificationPacket` producer
  - `EgressCertificationReceipt` producer/interface
  - `agentic_core/L5_safety/certification/*`
  
- **Phase 4B** → `core-l6-g29-promotion-proof-hardening-d9e3b2.md`
  - `PromotionGauntlet.GATE_ID`
  - `FutureRunPromotionRequest` proof fields
  - Generic L4 namespace parser

**Core Addition Author-Gate Required**: Any edit to `agentic_core/` must carry `CoreAdditionAuthorGateReceipt` (verdict=PASS).

---

## Files and Paths by Phase

| Phase | Files Touched |
|-------|---------------|
| 0 | `artifacts/governance/apps_rg_master_w0_baseline_receipt.json`, `artifacts/ci/direct_semantic_cache_write.json`, `artifacts/ci/apps_rg_runtime_path_inventory.json` |
| 1 | `apps_rg/runtime/section_agentic_pipeline.py`, `apps_rg/runtime/schemas/__init__.py`, `apps_rg/runtime/bindings/exit_binding.py`, `ops_scripts/ci/check_no_direct_semantic_cache_write.py`, `tests/governance/test_apps_rg_uwg_cache_write_sovereignty.py` |
| 2 | `apps_rg/runtime/l6_shadow_learning.py` → `apps_rg/_quarantine/`, `apps_rg/runtime/schemas/__init__.py`, `apps_rg/runtime/section_agentic_pipeline.py`, `ops_scripts/ci/check_no_apps_rg_runtime_l6_engine.py`, `tests/governance/test_apps_rg_l6_surface_ownership.py` |
| 3 | `apps_rg/config/l4_namespace_manifest.yaml`, `apps_rg/config/l4_namespace_manifest.schema.json`, `apps_rg/runtime/bindings/exit_binding.py`, `ops_scripts/ci/check_apps_rg_l4_write_boundary.py`, `ops_scripts/ci/check_apps_rg_chroma_readonly.py`, `ops_scripts/ci/check_apps_rg_exit_no_direct_writes.py`, `tests/_apps_contract/test_apps_rg_l4_namespace_manifest.py` |
| 4A | `agentic_core/L5_safety/certification/l5_packet_producer.py`, `agentic_core/L5_safety/certification/egress_certifier.py`, `agentic_core/L5_safety/contracts/*`, `tests/unit/agentic_core/L5_safety/*` |
| 4B | `agentic_core/L6_learning/promotion_gauntlet.py`, `agentic_core/L6_learning/__init__.py`, `agentic_core/L4_state/contracts/l4_namespace_contract.py`, `tests/unit/agentic_core/L6_learning/test_promotion_gauntlet.py` |
| 5 | `agentic_core/runtime/contracts/l1_plan_contract.py`, `agentic_core/runtime/contracts/route_contract.py`, `agentic_core/runtime/contracts/route_gate_receipt.py` |
| 6 | `apps_rg/runtime/u0/payload_synthesizer.py`, `apps_rg/runtime/bindings/l1_binding.py`, `apps_rg/profiles/rg_planning_profile.yaml`, `tests/_apps_contract/test_apps_rg_l1_*.py` |
| 7 | `apps_rg/runtime/bindings/l0_binding.py`, `apps_rg/config/domain_contract/route_profiles.yaml`, `apps_rg/runtime/bindings/pa_binding.py`, `tests/_apps_contract/test_l0_*.py` |
| 8 | `apps_rg/runtime/bindings/*_binding.py` (all 7), `apps_rg/config/domain_contract/l5_governance_profile.yaml`, `tests/_apps_contract/test_apps_rg_l5_certification_packet.py`, `tests/_apps_contract/test_apps_rg_l2_egress_receipts.py` |
| 9 | `apps_rg/runtime/bindings/c0_binding.py`, `apps_rg/config/domain_contract/runtime_gate_profile.resume_generation.v1.json`, `apps_rg/config/domain_contract/research_delegation_profile.yaml`, `tests/_apps_contract/test_apps_rg_c0_*.py` |
| 10 | `apps_rg/runtime/schemas/source_resume_v2_structured.json`, `apps_rg/runtime/u0/payload_synthesizer.py`, `apps_rg/runtime/bindings/pa_binding.py`, `apps_rg/runtime/bindings/u0_binding.py`, `apps_rg/runtime/bindings/exit_binding.py`, `tests/_apps_contract/test_source_resume_schema_v2.py`, `tests/_apps_contract/test_exit_binding_structured_output.py`, `tests/_apps_contract/test_apps_rg_pa_tiered_prompt.py`, `tests/_apps_contract/test_apps_rg_exit_g21_g22.py` |
| 11 | `apps_rg/config/domain_contract/fact_vectors_schema.yaml`, `apps_rg/tools/fact_vector_ingest.py`, `apps_rg/config/domain_contract/section_retrieval_profile.yaml`, `tests/_apps_contract/test_fact_vectors_*.py`, `tests/_apps_contract/test_section_retrieval_*.py`, `tests/_apps_contract/test_metadata_filter_*.py`, `tests/_apps_contract/test_claim_verification_*.py` |
| 12 | `apps_rg/runtime/bindings/exit_binding.py`, `tests/governance/test_apps_rg_l6_handoff_contract.py`, `tests/runtime/test_l6_observer_law_prohibitions.py`, `tests/governance/test_l6_promotion_uwg_required.py` |
| 13 | `ops_scripts/ci/run_contract_gates.py`, `artifacts/governance/apps_rg_master_closeout_receipt.json`, `artifacts/governance/apps_rg_99_proof_bundle.json` |

---

## "Do Not Implement in This Plan" List

**Explicitly Deferred to Future Plans:**

1. HITL governance (GAP-004) — only if human modification/re-entry enters release scope
2. LLM judge calibration and benchmark Spearman ≥ 0.80 — needs human-labeled holdout
3. Real LLM judge implementations for deferred dimensions — after deterministic G21/G22
4. BM25/sparse retrieval in C0 — unless separately justified
5. L1 Qwen/vLLM/API invocation — out of scope for contract wiring plan
6. Terminal RET hardening — unless R5 actively emitted
7. Production-log mining with PII redaction
8. SSOT consolidation of legacy policy/threshold YAMLs
9. Core contract field additions beyond L1/L0 enablement
10. Any attempt to repair `l6_shadow_learning.py` — must delete/quarantine only

**Hard Constraints (Never Violate):**
- No direct semantic cache writes in runtime
- No app-local L6 runtime engine (delete/quarantine only)
- No company research retrieval inside apps_rg C0
- No apps_rg literals in `agentic_core` outside legacy shims
- L6 never rescues, reroutes, mutates current run, emits X3, writes L4, or activates current-run changes
- UNKNOWN is never PASS

---

## Gap Register

**GAP-1: L5CertificationPacket Producer Missing**
- Generic core L5 packet producer does not exist
- Blocking governed release for all apps requiring L5 certification
- Resolution: Author-Gated core plan Phase 4A

**GAP-2: Direct Semantic Cache Write UWG Bypass**
- P0 reachable bypass around UWG mediation
- Resolution: Master Phase 1

**GAP-3: Egress Receipt Around ProviderGateway**
- No EgressCertificationReceipt emitted around provider calls
- Resolution: Master Phase 8 (after core L5 producer Phase 4A)

**GAP-4: L5 HITL Governance**
- Human-in-the-loop reclearance not implemented
- Resolution: Deferred unless human modification enters scope

**GAP-5: L6 Shadow Learning Dead Code**
- `l6_shadow_learning.py` creates architectural confusion
- Resolution: Master Phase 2 (delete/quarantine)

**GAP-6: L6 W4/W5 Core Edits Conflict**
- apps_rg L6 plan duplicates Core G29 work
- Resolution: Core G29 plan owns generic edits

**GAP-7: Core Boundary Scanner Consolidation**
- Multiple overlapping core boundary scan gates
- Resolution: One consolidated gate plus targeted tests

**GAP-8: C0 Company Research Temptation**
- Risk of implementing company research inside apps_rg C0
- Resolution: Hard ban enforced

**GAP-9: LLM Judge vs Deterministic Priority**
- Risk of adding LLM judges before deterministic checks
- Resolution: G21/G22 first, judges deferred

**GAP-10: fact_vectors Timing**
- Risk of treating fact_vectors as safety blocker
- Resolution: Product-quality foundation, not L4/L5 blocker

---

## Definition of Done

| DoD ID | Criterion | Verification |
|--------|-----------|--------------|
| DoD-1 | All 8 source plans updated with consolidation banners | Visual inspection of each plan file |
| DoD-2 | Master plan created with all 13 phases and runbook commands | File exists at canonical path |
| DoD-3 | Core L5 plan created if no suitable plan exists | File exists at canonical path |
| DoD-4 | Per-source-plan disposition table complete and accurate | 8 rows with correct dispositions |
| DoD-5 | Dependency graph ASCII art present and accurate | Visual inspection |
| DoD-6 | Overlap and redundancy inventory with 13 rows | Visual inspection |
| DoD-7 | Only `.windsurf/plans` files modified (plan-only scope) | `git diff --name-only` confirms |
| DoD-8 | No runtime/code implementation performed | No Python source edits outside plans |
| DoD-9 | No `agentic_core` source files modified (plan-only) | `git diff agentic_core/` empty |
| DoD-10 OPTIONAL | Notion Plans DB registration, only if required by current project plan protocol. This is not a blocker for plan-file consolidation | `API-post-page` returns 200 with page ID (if required) |

### Verification-vs-Deferral

| Item | In plan? | Deferral reason |
|------|----------|-----------------|
| Core L5 packet producer implementation | Not implemented | Author-Gated separate plan only |
| Core G29 edits implementation | Not implemented | Author-Gated separate plan only |
| Any apps_rg runtime code changes | Not implemented | Plan-only consolidation task |
| CI gate script changes | Not implemented | Plan-only consolidation task |
| Test file changes | Not implemented | Plan-only consolidation task |

---

## Plan-Only Validation Commands

Run after consolidation edits:

```bash
git diff -- .windsurf/plans
git diff --name-only
git diff --name-only | rg -v "^\.windsurf/plans/" && exit 1 || true
git diff -- agentic_core apps_rg ops_scripts tests
```

**Expected:**
- Only `.windsurf/plans/*` files changed
- No `agentic_core/` source files changed
- No `apps_rg/` source files changed
- No `ops_scripts/` files changed
- No `tests/` files changed
- Runtime implementation is untouched

## Open Verification Items

Before marking this plan complete, verify:

1. [ ] All 8 source plans contain banners with PORTFOLIO_STATUS and MASTER_PLAN_REF
2. [ ] No non-plan files changed in the consolidation commit
3. [ ] Phase 4A and 4B are separate Author-Gated plans, not implemented by master
4. [ ] Phase 5 has separate Author-Gated plan if fields are missing (or marked NO-OP)
5. [ ] Source plan W10 conflict is marked superseded in structured resume plan
6. [ ] No external registration dependency (Notion is optional per DoD-10)

## Scope Expansion Authorization

When scope is discovered during execution, follow the four-step discipline: DISCOVERED_SCOPE → AUTHORIZATION_DECISION → Plan updates → SCOPE_EXPANSION.

---

## Related Plans

| Plan | Relation |
|------|----------|
| core-l6-g29-promotion-proof-hardening-d9e3b2.md | Core-enabling work Phase 4B |
| core-l5-certification-packet-producer-hardening.md | Core-enabling work Phase 4A (new) |
| apps-rg-l4-boundary-hardening-c8f2a1.md | Merged Phase 0, 1, 2, 3, 13 |
| apps-rg-l5-governance-gap-report-hardened-f8c2e1.md | Reference Phase 4A, 8, 13 |
| apps-rg-l6-shadow-learning-hardening-7e4c2f.md | Merged Phase 0, 1, 2, 12, 13 |
| apps-rg-c0-architecture-analysis-f3d8b2.md | Merged Phase 9, 11 |
| apps-rg-structured-resume-refactor-f8c2a1.md | Merged Phase 0, 10, 11, 12 |
| apps-rg-l0-critical-gaps-remediation-a3f8e1.md | Merged Phase 5, 7 |
| apps-rg-l1-contract-wiring-3e7f92.md | Merged Phase 5, 6 |

---

## Consolidation Notes

**What This Plan Proves:**
1. 8 overlapping apps_rg plans can be consolidated without loss
2. Core-enabling work correctly separates to Author-Gated plans
3. P0 blockers (direct cache write) sequenced before product features
4. L6 surface ownership clarified (apps_rg must not duplicate core L6)
5. C0 scope bounded (no company research inside apps_rg)
6. Structured resume and fact_vectors sequenced after safety phases

**Portfolio Success Criteria:**
- Zero conflicting scope between plans
- Zero duplicated implementation ownership
- All valid detail preserved
- Clear phase-by-phase execution path
- All Author-Gate decisions captured before core edits
