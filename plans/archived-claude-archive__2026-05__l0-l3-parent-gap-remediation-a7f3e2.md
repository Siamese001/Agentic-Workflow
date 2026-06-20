---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\l0-l3-parent-gap-remediation-a7f3e2.md'
original_relative_path: '_archive\\2026-05\\l0-l3-parent-gap-remediation-a7f3e2.md'
source_sha256: e844a365d89011d13cf867fd06aeb3e8862c223f81925eb8c87056fcfbe453f8
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: l0-l3-parent-gap-remediation-a7f3e2
plan_type: platform_core_change
touches_agentic_core: true
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: true
author_gate_receipt_ref: ""
dod_exempt: false
---

# L0 / L3 Parent Gap Remediation (03 Switching_L3)

Close gaps between repo runtime and parent SSOT [03_L0_Route_Decision_Switching_L3.md](../docs/reference/03_L0_Route_Decision/03_L0_Route_Decision_Switching_L3.md). Evidence: [03_l0_l3_parent_gap_analysis_20260523.md](../docs/reports/l0_l3/03_l0_l3_parent_gap_analysis_20260523.md). **Notion:** https://www.notion.so/36927693f55c812e9828ccb5031897fd

> **plan_id discipline**: `plan=l0-l3-parent-gap-remediation-a7f3e2`

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: COMPLETE
CURRENT_WAVE: W3
LAST_COMPLETED_WAVE: W3
LAST_UPDATED: 2026-05-25
NOTION_STATUS: Completed
PLAN_COMPLETED: 2026-05-25
CLOSEOUT_RECEIPT: docs/reports/plans/waiting_plans_execution_receipt_20260525.md
DEFERRED_SCOPE: W4 OTEL/replay integrated proof
PROOF_GATE: ops_scripts/ci/check_l0_parent_invariants.py
W0_SSOT: docs/reports/l0_l3/execution_form_ssot_decision_20260525.md
NOTION_PAGE_ID: 36927693-f55c-812e-9828-ccb5031897fd
NOTION_RECONCILED: 2026-05-25
TRIPLECHECK: valid backlog — l3_binding + §7 validators not shipped
WAITING_FOR: Author-Gate for touches_agentic_core; W0 execution_form SSOT
PLAN_CREATED: slug=l0-l3-parent-gap-remediation-a7f3e2 path=.cursor/plans/l0-l3-parent-gap-remediation-a7f3e2.md status=Waiting

---

## Context (SCQA)

- **Situation** — Parent doc defines 12 invariants, evidence fields, OTEL spans, and 13 release-gate validators. Core has W6 `RouteContract`, v15 types, `ManagedWorkflowRunner`, L3 doctrine contracts, and apps_lic `l3_binding`. Gap analysis (2026-05-23) shows **DOC_ONLY** release gates and vocabulary drift.
- **Complication** — Three execution_form vocabularies (parent snake_case, v15 enum, W6 strings); W6 contract missing digest/HMAC/policy fields; apps_rg has L0 but no L3 binding; validators named in doctrine but not in CI.
- **Question** — How do we bring the repo to parent §10 PASS without breaking apps_rg spine or duplicating apps_lic patterns?
- **Answer** — **Vocabulary cutover first → W6/v15 evidence uplift → validator pack → apps_rg L3 binding → integrated OTEL/replay proof**, reusing apps_lic as the binding template.

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W0 | W0.1 | Inventory lock + vocabulary decision | ~8K | v15 cutover plan stays authoritative for enums | 🔲 TODO | Gap analysis + plan registered; Author-Gate on execution_form SSOT if parent text not updated |
| W1 | W1.1–W1.3 | W6 RouteContract evidence fields + apps_rg L0 emit | ~25K | `touches_agentic_core` receipt | 🔲 TODO | apps_rg route receipt includes digest + signature; tests pass |
| W2 | W2.1–W2.2 | §7 validator pack (L0 cluster) | ~30K | Depends W0 vocabulary | 🔲 TODO | `l0_*_validator` scripts exist; `run_contract_gates` green |
| W3 | W3.1–W3.3 | L3 validators + apps_rg `l3_binding` | ~35K | apps_lic binding as template | 🔲 TODO | `l3_orchestrate_apps_rg`; eligibility NC tests |
| W4 | W4.1–W4.2 | OTEL spans + replay proof on integrated path | ~20K | Provider available for smoke | 🔲 TODO | Receipt with span list + byte-identical fixture |

### Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W0.1 | Lock gap SSOT + vocab | gap doc, parent doc pointer, v15 plan link | Parent vs v15 enum mismatch | ~8K | 🔲 TODO |
| W1.1 | Route evidence fields on W6 | `route_contract.py`, serializers | Missing route_digest, policy_hash | ~10K | 🔲 TODO |
| W1.2 | apps_rg L0 emit uplift | `apps_rg/runtime/bindings/l0_binding.py` | Empty signature | ~8K | 🔲 TODO |
| W1.3 | Contract tests | `tests/_apps_contract/` | Regression on L1 advisory | ~7K | 🔲 TODO |
| W2.1 | L0 validators | `ops_scripts/ci/check_l0_parent_invariants.py` (new) | 8 named validators | ~18K | 🔲 TODO |
| W2.2 | NC tests L0 | `tests/governance/l0_parent/` (new) | NC-L0-* critical rows | ~12K | 🔲 TODO |
| W3.1 | L3 validators | same CI module / sibling | 5 named validators | ~15K | 🔲 TODO |
| W3.2 | apps_rg l3_binding | `apps_rg/runtime/bindings/l3_binding.py` (new) | No L3 on product path | ~12K | 🔲 TODO |
| W3.3 | Wire dispatch | integrated spine entry | Hidden expansion risk | ~8K | 🔲 TODO |
| W4.1 | OTEL seam | L0/L3 binding otel hooks | NO_SPANS_EMITTED in 10C | ~12K | 🔲 TODO |
| W4.2 | Replay receipt | `artifacts/apps_rg/plans/` | byte_identical proof | ~8K | 🔲 TODO |

---

## Gap Register (prioritized)

| Gap ID | P | Summary | Wave |
|--------|---|---------|------|
| GAP-L03-VOCAB-1 | P0 | execution_form vocabulary: parent §4 vs v15 vs W6 | W0 |
| GAP-L03-EVID-1 | P0 | W6 RouteContract missing parent §5 fields | W1 |
| GAP-L03-FIELD-1 | P1 | `hmac_sig` vs `signature` naming | W1 |
| GAP-L03-VAL-1 | P0 | All §7 validators missing from CI | W2–W3 |
| GAP-AR-L03-1 | P1 | apps_rg no l3_binding | W3 |
| GAP-L03-OTEL-1 | P2 | Prod path lacks l0.*/l3.* spans | W4 |
| GAP-AC-L03-1 | P2 | L0 tree hosts c0_retrieval (side-effect boundary) | W2 (anti-cheat) |

---

## Out Of Scope

- Full conversion of child files 03.1–03.9 REQ tables (parent §12 deferred)
- Rewriting `agentic_core/L0_routing/c0_retrieval/` tree (separate ADG migration)
- Section CLI path A parity (tracked under apps-rg spine plans)
- Notion backlog item creation per gap (optional post-W4)

---

## Wave 0 — Vocabulary and inventory lock

WAVE_ID: W0

**W0.1** — Confirm execution_form SSOT: either amend parent doc to v15 three-form model or map parent seven-form → v15 aspects in interpreter. Coordinate with [l0-routing-v15-only-cutover-c9e2f1](l0-routing-v15-only-cutover-c9e2f1.md). **Author-Gate** if parent markdown must change.

**Exit:** Decision recorded in gap analysis §Recommended remediation; no W1 edits until closed.

---

## Wave 1 — RouteContract evidence uplift

WAVE_ID: W1

**W1.1** — Extend W6 `RouteContract` (or v15 bridge) with `route_digest`, `policy_hash`, `blueprint_hash`, `content_hash` per §5; keep backward-compatible defaults.

**W1.2** — `l0_route_apps_rg`: compute digest + HMAC using v15 helper or shared util; populate `signature` / alias `hmac_sig` in JSON receipts.

**W1.3** — Tests: deterministic digest replay (mirror apps_lic); forbid dual route emission per request in binding tests.

---

## Wave 2 — L0 validator pack

WAVE_ID: W2

**W2.1** — New CI module implementing: `l0_one_route_validator`, `l0_route_digest_validator`, `l0_execution_form_validator`, `l0_hmac_validator`, `l0_cache_terminal_validator`, `l0_handoff_validator`, `l0_no_reroute_mid_run_validator`, `l0_no_side_effect_validator` (AST/import scan for L0→C0/PA/L2 calls in binding paths).

**W2.2** — Negative controls: `NC-L0-DUAL-ROUTE-001`, `NC-L0-RETRIEVE-LEAK-001`, `NC-L0-REROUTE-MID-001` pytest fixtures.

Register in `ops_scripts/ci/run_contract_gates.py`.

---

## Wave 3 — L3 binding and validators

WAVE_ID: W3

**W3.1** — L3 validators: `l3_eligibility_validator`, `l3_dag_validator`, `l3_step_ledger_validator`, `l3_completion_validator`, `l3_l2_handoff_validator`.

**W3.2** — Add `apps_rg/runtime/bindings/l3_binding.py` modeled on [apps_lic/runtime/bindings/l3_binding.py](../apps_lic/runtime/bindings/l3_binding.py): emit `L3RuntimeOrchestrationReceipt` + `L3StepContract` only when `execution_form` is managed workflow.

**W3.3** — Wire into integrated spine after L0 route; fail-closed when `l3_required` without binding.

**NC:** `NC-L3-HIDDEN-EXPANSION-001` test — single_action route must not emit L3 spans/contracts.

---

## Wave 4 — OTEL and replay proof

WAVE_ID: W4

**W4.1** — Emit parent §6 spans on integrated apps_rg run (minimal: `l0.route_decision`, `l3.eligibility_check` when applicable).

**W4.2** — Run e2e proof fixture or apps_rg smoke; write receipt `artifacts/apps_rg/plans/l0_l3_parent_proof_receipt.json` with contract hashes and span manifest.

---

## Definition of Done

| # | Criterion | Verification |
|---|-----------|--------------|
| D1 | Gap analysis on disk linked from plan | File exists at `docs/reports/l0_l3/03_l0_l3_parent_gap_analysis_20260523.md` |
| D2 | Plan registered in Notion Plans DB | `create_plan_in_notion` ok |
| D3 | W6/apps_rg route emits `route_digest` + non-empty `signature` | pytest contract tests |
| D4 | All 13 §7 validators registered in CI | `run_contract_gates` lists gates |
| D5 | apps_rg `l3_binding` + NC-L3-HIDDEN-EXPANSION test | pytest apps_contract |
| D6 | Smoke: `python -m pytest tests/_apps_contract/test_apps_rg_l1_route_authority_advisory.py -q --no-header` exits 0 | command output |
| D7 | W4 receipt with OTEL span names + replay hash | artifact path |

### Verification vs deferral

| Item | Status |
|------|--------|
| Static gap analysis | **Done** (2026-05-23) |
| Validator implementation | **Deferred** W2–W3 |
| Live OTEL proof | **Deferred** W4 |
| Child 03.1–03.9 REQ conversion | **Out of scope** |

---

## Dependencies

- [l0-routing-v15-only-cutover-c9e2f1](l0-routing-v15-only-cutover-c9e2f1.md) — vocabulary authority
- [apps-rg-spine-only-unification-d8f4a2](apps-rg-spine-only-unification-d8f4a2.md) — integrated path target
- apps_lic AG-8 L3 binding — implementation template

---

## Review checklist (for human reviewer)

1. Agree execution_form SSOT: parent doc amendment vs v15-only?
2. Accept W6 field additions vs v15-only emit path?
3. Prioritize apps_rg L3 binding before or after v15 cutover?
4. Confirm `agentic_core` edit receipt path for W1–W3
5. Sign off on DOC_ONLY → CI PASS promotion criteria per validator
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
