---
plan_id: semantic-cache-fingerprint-proof-c9f1a3
plan_type: audit
touches_agentic_core: false
touches_governance_ci: false
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# Semantic cache fingerprint proof (optional)

**Parent closeout:** `.cursor/plans/p4.2_apps-rg-l6-shadow-learning-hardening-7e4c2f.md` (2026-05-15)  
**Purpose:** When a stakeholder needs to claim semantic-cache payloads or index segments are **byte-stable** across a bounded operation, produce **measured** fingerprints (hash, segment IDs, snapshot manifest) rather than narrative proof.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1  
PLAN_STATUS: COMPLETE
CURRENT_WAVE: W2
LAST_COMPLETED_WAVE: W2
LAST_UPDATED: 2026-05-25
NOTION_STATUS: Completed
PLAN_COMPLETED: 2026-05-25
CLOSEOUT_RECEIPT: docs/reports/plans/waiting_plans_execution_receipt_20260525.md
PROOF_COMMAND: python tools/cache/capture_semantic_cache_fingerprint.py --label closeout
NOTION_PAGE_ID: 36127693-f55c-81ce-a640-d26133b431de
NOTION_RECONCILED: 2026-05-25
TRIPLECHECK: valid optional — fingerprint receipt DoD open
WAITING_FOR: Optional audit request; W1–W2 not started

---

## Context (SCQA)

- **Situation** — Resume-shipping phases removed/neutralized direct semantic-cache writes; some claims still need reproducibility evidence.
- **Complication** — “Unchanged” without a hash is non-falsifiable.
- **Question** — What artifact captures cache fingerprint before/after?
- **Answer** — Define namespace + collection IDs, dump canonical serialized view or provider-specific stats, SHA-256, store under `artifacts/` with UTC timestamp in receipt.

---

## Status Tables

### Wave Progress

| Wave | Focus | Status | Tests Added | Files Changed |
|------|-------|--------|-------------|---------------|
| W1 | Decide fingerprint granularity (collection vs embedding vs record) | 🔲 TODO | — | — |
| W2 | Script or pytest that emits `artifacts/...fingerprint.json` | 🔲 TODO | — | tools/ or tests |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W1.1 | Document what “unchanged” means (which store, which namespace) | 🔲 TODO |
| W2.1 | Implement capture + comparison | 🔲 TODO |
| W2.2 | Add receipt markdown under `artifacts/governance/` | 🔲 TODO |

---

## Definition of Done

DoD-1: Fingerprint capture command documented and reproducible  
- Evidence: README section or plan “Execution Details” with exact command  
- Status: TODO  

DoD-2: Before/after hashes recorded for the claimed operation  
- Evidence: JSON under `artifacts/` checked into repo or CI-uploaded per policy  
- Status: TODO  

DoD-3: No false claim of global cache immutability — scope string names the collection/namespace only  
- Evidence: receipt lists limits  
- Status: TODO  

DoD-4: No `*_BYPASS`  
- Evidence: env transcript  
- Status: TODO  

DoD-5: Optional — wire as advisory CI gate only if operator requests automated regression  
- Evidence: gate registration note or explicit “manual evidence only”  
- Status: TODO  

---

## Out Of Scope

- Re-enabling live semantic-cache writes on resume-shipping hot path (conflicts with S0.5 guard unless master plan authorizes).
- Cross-machine absolute byte identity for nondeterministic embeddings unless seed + model pinned.
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
