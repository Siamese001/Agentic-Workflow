---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\apps-rg-v40-spine-gap-c4a8f1.md'
original_relative_path: '_archive\\2026-05\\apps-rg-v40-spine-gap-c4a8f1.md'
source_sha256: 5625186eca80350298ecf54f9edd83ba9fd40a940b299d67b2e3c4ea149b8d5d
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: apps-rg-v40-spine-gap-c4a8f1
plan_type: architecture
touches_agentic_core: true
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: true
author_gate_receipt_ref: ""
dod_exempt: false
---

# apps_rg v40 Spine Gap Remediation — Review Plan

Full-layer gap analysis (apps_rg vs agentic_core) against [`agentic_process_mapping_v40.md`](../docs/reference/_notes/agentic_process_mapping_v40.md).

**Analysis SSOT:** [apps_rg_v40_spine_gap_analysis_20260523.md](../docs/reports/apps_rg/apps_rg_v40_spine_gap_analysis_20260523.md)  
**Prior work:** W-A binding hardening **COMPLETE** ([closeout](../docs/reports/apps_rg/apps_rg_binding_hardening_critical_closeout_receipt.md))

> **plan_id discipline:** `apps-rg-v40-spine-gap-c4a8f1` matches filename stem.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: SUPERSEDED
CURRENT_WAVE: W0
LAST_COMPLETED_WAVE: W0
LAST_UPDATED: 2026-05-23
SUPERSEDED_BY: apps-rg-spine-only-unification-d8f4a2
PLAN_CREATED: slug=apps-rg-v40-spine-gap-c4a8f1 path=.cursor/plans/apps-rg-v40-spine-gap-c4a8f1.md status=Not Started
NOTION_PLANS_ROW: page_id=36927693-f55c-8156-b234-e4362e3b0f53 url=https://www.notion.so/36927693f55c8156b234e4362e3b0f53

---

## Goal

Close documented gaps between v40 spine substeps and `apps_rg` runtime behavior, with **separate ownership** for apps_rg vs agentic_core work.

**Execution superseded by:** [apps-rg-spine-only-unification-d8f4a2](apps-rg-spine-only-unification-d8f4a2.md) — **no bridges**; destroy second pipeline; section vs full = profile/plan differences only.

## Non-goals

- Rewriting v40 SSOT (generic map stays in `docs/reference/_notes/`)
- Moving all `agentic_core` contracts to apps_rg in one wave
- Claiming LIVE_RUNTIME_PROOF or certification in this plan

---

## Executive decisions needed (your review)

| # | Decision | Options | Recommendation |
|---|----------|---------|----------------|
| D1 | Section path contract strategy | (A) Emit spine contracts on section lanes (bigger) (B) Keep lane substitutes + strengthen mirrors/docs (smaller) | **B then A** — W1 docs/tests, W2+ selective contract emission |
| D2 | `ValidatedRequest` location | (A) Move to `apps_rg/schemas/` (B) Keep in core as shared DTO + ADR | **B** short-term; **A** if multi-app reuse not needed |
| D3 | L1.3 refinement loop | (A) Implement (B) Document N/A for deterministic resume_generation | **B** |
| D4 | Core `apps_rg_prerequisite_gate` | (A) Migrate policy to apps_rg YAML (B) Defer | **A** in W3 |
| D5 | Resume judges in core | (A) Move rubrics to apps_rg (B) Defer | **A** in W4 |

---

## Gap inventory summary

| Owner | P0 | P1 | P2 |
|-------|----|----|-----|
| apps_rg | 6 | 12 | 8 |
| agentic_core | 2 | 5 | 4 |

See analysis doc for full `GAP-AR-*` / `GAP-AC-*` tables per layer (U0, L1, L0, C0, PA, L3, L2, Exit, UWG, L4, L6, 00C/L5).

---

## Waves (proposed)

| Wave | Scope | Primary gaps | agentic_core? | Proof |
|------|--------|--------------|---------------|-------|
| **W0** | Analysis + plan registration | — | No | This doc + Notion row |
| **W1** | One-spine terminology + contract bypass tests | AR-EXIT-2, AR-C0-2, AR-L2-4 | Comment-only AC-EXIT | Contract tests; update inventory JSON |
| **W2** | Section front spine: U0 package → ValidatedRequest for all lanes | AR-U0-3 | — | Per-lane proof bundle with `validated_request.json` |
| **W3** | L0 gate policy migration | AC-L0-1 | Yes | Gate policy in apps_rg YAML; core generic evaluator |
| **W4** | Evals/judge dedup | AC-EXIT-1, AR-EXIT-1 glossary | Yes | Judges under `apps_rg/config/domain_contract/judges/` |
| **W5** | C0 spine parity (grounded lanes) | AR-C0-1..4 | Optional hybrid | FEC from `c0_retrieve_apps_rg` in section path when grounding required |
| **W6** | Exit receipt authority (W-C) | AR-EXIT-1/3 | Spine comment fixes | `ExitDispositionReceipt` on section CLI when spine consumed |
| **W7** | Optional: ingress DTO relocation | AC-U0-1 | Yes | ADR + contract test migration |

**Dependency:** W1 before W2; W3 independent; W5 after W2; W6 after W1.

---

## W1 deliverables (first execution wave)

1. Extend [`one_spine_inventory.py`](../apps_rg/runtime/one_spine_inventory.py) `_open_gaps()` from analysis P0 list.
2. Contract test: section lane artifacts declare `disposition_authority` + `fec_shape_only` where applicable.
3. Doc: `docs/reports/apps_rg/v40_section_vs_spine_contract_matrix.md` (generated from inventory).
4. No production behavior change unless tests already expect receipts.

**DoD W1:** pytest module green; inventory JSON regenerated; report linked from analysis doc.

---

## W2 deliverables

1. Route all `--section` lanes through `u0_validate_apps_rg` with full `profile_manifest` (not bridge-only envelope).
2. Emit `l1_plan_contract.json` + `route_contract.json` in section proof bundles (mirror integrated proofs).
3. Fail-closed if `app_payload` missing required keys.

**DoD W2:** Executive summary (or one gold lane) proof dir contains canonical contract JSON files.

---

## W3 deliverables (agentic_core)

1. Move apps_rg prerequisite **policy** to `apps_rg/config/domain_contract/l0_prerequisite_policy.yaml`.
2. Core gate becomes generic evaluator consuming profile ref.
3. Migration receipt in `artifacts/governance/migration_receipts/`.

**DoD W3:** No `apps_rg` string literals in core gate module; ADG boundary test pass.

---

## W4 deliverables

1. Glossary: Benchmark evals / X1D judges / Exit pipeline (EV-1).
2. Migrate `resume_judges/*` prompts/rubrics to apps_rg; core keeps `llm_judge_gateway` only.

**DoD W4:** `rg` shows no resume-specific judge prompts in `agentic_core/runtime/judges/resume_judges/`.

---

## W5 deliverables (apps_rg)

1. When `RouteContract.grounding_required`, section path calls `c0_retrieve_apps_rg` instead of proof-pool-only FEC snapshot.
2. Rename lane artifacts per [`section_spine_terminology.py`](../apps_rg/runtime/section_spine_terminology.py) (compat aliases).

**DoD W5:** One grounded lane proof with spine `FinalEvidenceContract` + citation map from C0 binding.

---

## W6 deliverables

1. Section CLI produces `exit_disposition_receipt.json` consumable by rollup (extend W-A).
2. `canonical_exit_claimed: true` only when spine Exit consumed lane mirrors.

**DoD W6:** Package rollup test uses spine receipt when present (extend existing contract tests).

---

## Review checklist

- [ ] Approve wave order (W0–W7) or reprioritize P0 gaps
- [ ] D1: section contract strategy (B→A vs big-bang A)
- [ ] D2: ValidatedRequest stays in core vs move to apps_rg
- [ ] Authorize W1 execution (no agentic_core logic changes)
- [ ] Link Backlog Items for W3/W4 if core migration authorized

---

## Related

| Link | |
|------|---|
| [v40 gap analysis](../docs/reports/apps_rg/apps_rg_v40_spine_gap_analysis_20260523.md) | Full layer tables |
| [overlap review 20260522](../docs/reports/apps_rg/apps_rg_agentic_core_binding_overlap_review_20260522.md) | Pre-W-A issues |
| [one-canonical-spine plan](one-canonical-spine-e8b4a1.md) | Product spine convergence |
---

## ADG_GRAPH_LAYER_EVIDENCE

Preflight scope (Constitutional §22) — MV-driven blast radius before edits:

| MV | Use |
|----|-----|
| `mv_fanin_top` | inbound dependency rank for scoped seam |
| `mv_fanout_top` | outbound consumer rank |
| `mv_blast_radius` | change-impact envelope |
| `mv_chokepoint_score` | sequencing / coupling risk |

Semantic edges: `flows_to`, `reads_from`, `writes_to` · P-view: `v_p0_wave_plan`

---

## ADG_HOTSPOT_REPORT

| Rank | Node | Archetype | Surface | Rationale |
|------|------|-----------|---------|-----------|
| 1 | scoped seam | CENTRAL_DEPENDENCY | Execution Surface | primary edit locus |
| 2 | gate / boundary | SAFETY_GATEKEEPER | Security Surface | fail-closed enforcement |
