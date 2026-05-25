---
plan_id: 10c-proof-bundle-current-head-a8f4c2
plan_type: governance
touches_agentic_core: false
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# 10C pilot proof bundles — W4d-4 current-head refresh

**Parent closeout:** `.cursor/plans/p4.2_apps-rg-l6-shadow-learning-hardening-7e4c2f.md` (2026-05-15)  
**Purpose:** Eliminate `git_head_at_test_time` drift versus `git rev-parse HEAD` for all `CRITICAL_REQ_IDS` / pilot proof bundles checked by `check_10c_pilot_proof_evidence.py` (P4b), without weakening the gate and without hand-editing `git_head` fields.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1  
PLAN_STATUS: COMPLETE
CURRENT_WAVE: W2
LAST_COMPLETED_WAVE: W2
LAST_UPDATED: 2026-05-25
NOTION_STATUS: Completed
NOTION_PAGE_ID: 36127693-f55c-81e2-bb0a-cad26d5dc3cc
NOTION_RECONCILED: 2026-05-25
PLAN_COMPLETED: 2026-05-25
PLAN_COMPLETE: plan=10c-proof-bundle-current-head-a8f4c2 note="198 bundles regen @ HEAD; W4d-4 gate PASS"
CLOSEOUT_RECEIPT: docs/reports/plans/not_started_plans_triplecheck_receipt_20260525.md
PROOF_GATE: ops_scripts/ci/check_10c_pilot_proof_evidence.py --skip-pytest exit=0

---

## Context (SCQA)

- **Situation** — Tracked proof JSON under `artifacts/requirements/proof_bundles/` carry `git_head_at_test_time`. After `HEAD` moves, P4b rejects `EVIDENCE_PRESENT` bundles whose recorded head ≠ current `HEAD`.
- **Complication** — Manually overwriting `git_head_at_test_time` defeats tamper/bind semantics and is forbidden policy.
- **Question** — How do we refresh proof bundles so W4d-4 is green at **current** `HEAD`?
- **Answer** — Regenerate bundles via the **canonical emitter** (recompute `content_hash`, bind fresh `git rev-parse HEAD`, re-run verifier). Optionally run W4d-4 with `--skip-pytest` to match CI contract-runner parity (`run_contract_gates.py` wires `skip-pytest`), and run **without** that flag only when full P6 per-req pytest subprocess proof is explicitly required.

---

## Status Tables

### Wave Progress

| Wave | Focus | Status | Tests Added | Files Changed |
|------|-------|--------|-------------|---------------|
| W1 | Locate stale bundles + canonical regen command | 🔲 TODO | — | proof_bundles JSON |
| W2 | Verify W4d-4 standalone + optionally full contract runner | 🔲 TODO | — | artifacts reports |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W1.1 | Inventory failing req_ids / bundle paths from gate output | 🔲 TODO |
| W1.2 | Run `tools/requirements/emit_proof_bundles.py --regenerate-all` (or documented equivalent) | 🔲 TODO |
| W2.1 | `$env:PYTHONPATH=<repo>; python ops_scripts/ci/check_10c_pilot_proof_evidence.py` | 🔲 TODO |
| W2.2 | Tee full contract log after W4d-4 green | 🔲 TODO |

---

## Definition of Done

DoD-1: No stale `git_head_at_test_time` — `grep` for obsolete short SHA over `artifacts/requirements/proof_bundles/` is empty after regen  
- Evidence: `git rev-parse HEAD` matches every `EVIDENCE_PRESENT` bundle field `git_head_at_test_time`  
- Status: TODO  

DoD-2: W4d-4 checker passes at repo root  
- Evidence: `python ops_scripts/ci/check_10c_pilot_proof_evidence.py --skip-pytest` exit 0; artifacts `artifacts/requirements/10c_pilot_proof_evidence.{json,md}` updated  
- Status: TODO  

DoD-3: No bypass variables  
- Evidence: transcript shows no `*_BYPASS` for this gate suite  
- Status: TODO  

DoD-4: Optional full P6 subprocess proof  
- Evidence: run checker **without** `--skip-pytest` when policy demands per-req pytest replay; document runtime cost  
- Status: TODO  

DoD-5: If full contract rerun is required, capture exit code and first failing gate name  
- Evidence: log path e.g. `artifacts/ci_logs/contract_gates_full_after_w4d4_fix.log`  
- Status: TODO  

---

## Out Of Scope

- Downgrading W4d-4 to advisory.
- Editing `git_head_*` alone via one-off scripts (must use canonical emission / hash loop).
- Seeding “historical” bundles into the paths the **current-head** checker validates — use explicit archive dirs + checker allowlist changes only via separate governance change (not in this plan’s default path).
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
