---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\apps-rg-spine-deferred-harden-c8f1a2.md'
original_relative_path: '_archive\\2026-05\\apps-rg-spine-deferred-harden-c8f1a2.md'
source_sha256: e123b6a49d7bea0e438b7cf61a9edc41e63725609ab34ab7514d7c756ebe8546
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: apps-rg-spine-deferred-harden-c8f1a2
plan_type: hardening
touches_agentic_core: false
touches_governance_ci: true
touches_cursor_rules: false
parent_plan: pa-exec-flowchart-gap-f2a8c3
dod_exempt: false
---

# apps_rg spine deferred scope — harden + edge-case proof

Close **remaining partials** from [pa-exec-flowchart-gap-f2a8c3](pa-exec-flowchart-gap-f2a8c3.md) with span coverage validation, emit-site completion on harness paths, and negative/edge contract tests. **Does not** claim live LLM all-lanes, C0.3 graph RAG, or L6 promotion gauntlet.

**Parent closeout:** [pa_exec_flowchart_gap_closeout_receipt.md](../docs/reports/apps_rg/pa_exec_flowchart_gap_closeout_receipt.md)

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: COMPLETED
CURRENT_WAVE: done
LAST_COMPLETED_WAVE: W7-edge-harden
LAST_UPDATED: 2026-05-23
NOTION_STATUS: Completed
NOTION_PLAN_URL: https://www.notion.so/apps-rg-spine-deferred-harden-c8f1a2-36927693f55c813784d6d937ade72c87
DISK_SSOT: .cursor/plans/apps-rg-spine-deferred-harden-c8f1a2.md

PLAN_CREATED: slug=apps-rg-spine-deferred-harden-c8f1a2 path=.cursor/plans/apps-rg-spine-deferred-harden-c8f1a2.md status=Completed notion_page=36927693-f55c-8137-84d6-d937ade72c87
CLOSEOUT: 2026-05-23 — W1–W7 + edge-case suite 42/42 pytest (harness); receipt [apps_rg_spine_deferred_harden_closeout_receipt.md](../docs/reports/apps_rg/apps_rg_spine_deferred_harden_closeout_receipt.md)

---

## Context (SCQA)

- **Situation** — W8 + follow-up delivered one pipeline harness E2E, receipt-based span fallback, section PA core sign, L2 handoff receipt.
- **Complication** — Harness E2E only asserted PA/L2/EXIT spans; U0/L1/L0/C0/L6 emit sites incomplete on `emit_*` paths; no coverage validator; W9 `test_pa_section_contracts_w9` not in closeout gate; live OTEL/C0.3/L6 promotion still open.
- **Question** — How do we harden without widening to live provider or core spine edits?
- **Answer** — W1 span coverage SSOT + emit sites → W2 edge-case tests + E2E assert full layer order → W3 CI/doc closeout; defer live/OTEL SDK/graph/promotion.

---

## Wave Progress

| Wave | Focus | Status |
|------|-------|--------|
| W1 | Span coverage API + emit U0→L6 on product emit paths | ✅ DONE |
| W2 | Edge-case contract tests + E2E full layer assert | ✅ DONE |
| W3 | CI ratchet + closeout receipt + Notion Completed | ✅ DONE |
| W4 | OTEL dual-write metadata + span emit sites CI gate | ✅ DONE |
| W5 | C0.3 graph lane receipt (deferral proof, not full Graph RAG) | ✅ DONE |
| W6 | L6 eval-before-learn receipt + promotion blocked surface | ✅ DONE |
| W7 | Live section smoke script (BLOCKED without Chroma/provider; dry-run manifest) | ✅ DONE |
| W7-edge | Expanded edge-case hardening (29 + 9 + 4 E2E = 42 pytest) | ✅ DONE |

---

## Closeout proof (2026-05-23)

| Gate | Result |
|------|--------|
| `test_apps_rg_spine_harden_edge_cases.py` | 29 passed |
| `test_apps_rg_spine_waves_w4_w7.py` | 9 passed |
| `test_apps_rg_one_pipeline_e2e.py` | 4 passed |
| `check_apps_rg_spine_convergence_w8.py` | exit 0 |
| `check_apps_rg_spine_span_emit_sites.py` | PASS (8 rows) |

**Proof classification:** HARNESS — not live LLM all-lanes.

---

## In scope

| ID | Item | Proof |
|----|------|-------|
| H1 | `validate_spine_span_coverage` + `spine_span_coverage_receipt.json` | unit + E2E |
| H2 | Emit U0/L1/L0 in `emit_section_front_spine_receipts` | harness spans |
| H3 | Emit C0 in `emit_spine_c0_fec_artifacts` | harness spans |
| H4 | Emit L6 in exhaust spine emit | harness spans |
| H5 | Edge cases: kill switches, missing HMAC, missing exit, raw_proof_pool, FEC/L6/C0 gaps | `test_apps_rg_spine_harden_edge_cases.py` (29) |
| H6 | E2E asserts `SPINE_LAYER_ORDER` (8 layers) | `test_apps_rg_one_pipeline_e2e.py` |
| H7 | Run `test_pa_section_contracts_w9.py` in closeout | pytest PASS |

---

## Explicit deferrals (remaining after W7)

| Item | SSOT | W4–W7 delivered |
|------|------|-----------------|
| Full OTEL semconv all lanes | P1 | Dual-write bridge + emit-site gate; receipt SSOT |
| Core C0.3 Graph RAG implementation | `C0_graph_lane_deferral.md` | `c0_graph_lane_receipt.json` defers honestly |
| L6 promotion / human EvalRecord gauntlet | `L6_eval_before_learn_scope.md` | `l6_eval_before_learn_receipt.json` blocks promotion |
| Live all-lanes provider run | `live_section_spine_smoke_all_lanes.py` | BLOCKED without deps; dry-run manifest PASS |
| Full X1A..X1J per section | parent plan deferral table | unchanged |

---

## DoD

1. All H1–H7 proof rows PASS (harness; not live LLM).
2. `check_apps_rg_spine_convergence_w8.py` exit 0.
3. Plan `PLAN_STATUS: COMPLETED` + Notion **Completed**.
4. Closeout receipt under `docs/reports/apps_rg/`.

---

## Parent hygiene

- Mark `pa-exec-flowchart-gap-f2a8c3` phase W0.1 **DONE** (bridge architecture record delivered in W1–W2).
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
