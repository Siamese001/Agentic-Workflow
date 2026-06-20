---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\one-canonical-spine-e8b4a1.md'
original_relative_path: '_archive\\2026-05\\one-canonical-spine-e8b4a1.md'
source_sha256: 997f0f08f2565e7f33ef9174fb7b564aca779fa787b2f95de13c4c06dcc9c140
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: one-canonical-spine-e8b4a1
plan_type: governance
touches_agentic_core: false
touches_governance_ci: false
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# One Canonical Spine — Section CLI Hardening (apps_rg)

Collapse `python -m apps_rg --section <lane>` onto one product-visible spine chain: **U0 → L1 → L0 → (section FEC bridge) → PA → L2 → Exit → optional UWG → L4 → L6**, without a parallel C0/GraphRAG path or raw proof_pool direct-to-PA authority.

> **plan_id discipline**: `one-canonical-spine-e8b4a1` matches filename stem.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: SUPERSEDED
CURRENT_WAVE: W9
LAST_COMPLETED_WAVE: W9
LAST_UPDATED: 2026-05-23
SUPERSEDED_BY: apps-rg-spine-only-unification-d8f4a2
SUPERSESSION_REASON: Bridge/FEC/lane-body second pipeline retained; replaced by spine-only unification (no bridges).
TARGETED_ONE_SPINE_PROOF: PASS
FINAL_ONE_SPINE_STATUS: CLOSED
FULL_APPS_CONTRACT_SUITE_CERTIFIED: false

---

## Context (SCQA)

- **Situation** — Section lanes used proof_pool / SRFS / augmented skills graph directly; PA consumed `proof_pool_metadata`; no front-spine contracts before proof_pool; executive_summary was the only lane with live FEC-bridge proof.
- **Complication** — Two execution shapes (section CLI vs R4 integrated), misnamed C0.3/FEC artifacts, and product-visible runs that could compile without RouteContract or FEC bridge.
- **Question** — How do we harden all section lanes behind one spine-shaped contract chain without migrating to full agentic_core C0 or weakening X2/X3?
- **Answer** — apps_rg-local front spine (U0/L1/L0), section_fec_bridge (non-canonical C0.5), PA kill switches, runtime artifact proof per lane; agentic_core untouched.

---

## Canonical Law

```
U0 → L1 → L0 → C0 → PA → L2 → Exit → optional UWG → L4 → L6
```

**Section lane interpretation (not full spine C0):**

| Stage | Section implementation |
|-------|-------------------------|
| U0/L1/L0 | `section_front_spine_bridge` → ValidatedRequest, L1PlanContract, RouteContract |
| C0 | `section_graph_binding_shim` + proof_pool_resolver (not spine dense/traverse) |
| C0.5 FEC | `section_fec_bridge` → `final_evidence_contract_bridge.json` |
| PA | Section PA compile via FEC `pa_proof_authority_metadata` |
| L2/Exit/L6 | Existing section lane outputs (unchanged scope) |

---

## Wave Summary

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | W1.1 | Inventory two paths, terminology | ~15K | ADG optional | ✅ DONE | `one_spine_section_path_inventory.json` |
| W2 | W2.1 | Guardrails, binding shim metadata | ~20K | No agentic_core | ✅ DONE | `test_one_spine_section_guardrails.py` PASS |
| W3 | W3.1 | Front spine before proof_pool | ~25K | exec_summary CLI inputs | ✅ DONE | `one_spine_front_bridge_w3_redo.json` PASS |
| W4 | W4.1 | FEC bridge → PA (executive_summary) | ~30K | qwen_vllm available | ✅ DONE | `one_spine_c0_fec_bridge_w4.json` PASS |
| W5A | W5A.1 | FEC bridge all section lanes | ~40K | Live runtime per lane | ✅ DONE | `one_spine_fec_bridge_w5a_all_lanes.json` PASS |
| W5B | W5B.1 | L2 spine receipts all lanes | ~25K | qwen_vllm | ✅ DONE | `one_spine_l2_receipts_w5b_all_lanes.json` PASS |
| W6 | W6.1 | Exit disposition receipts | ~25K | — | ✅ DONE | `one_spine_exit_receipts_w6_all_lanes.json` PASS |
| W7 | W7.1 | RuntimeExhaustBundle + L6 handoff | ~25K | — | ✅ DONE | `one_spine_runtime_exhaust_w7_all_lanes.json` PASS |
| W8 | W8.1 | Certification + proof eligibility | ~30K | — | ✅ DONE | `one_spine_certification_w8_all_lanes.json` PASS |
| W9 | W9.1 | Master closeout + no-two-path + triage | ~20K | — | ✅ DONE | `one_spine_master_closeout_w9.json` PARTIAL/CLOSED |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W1.1 | Path inventory | `one_spine_inventory.py`, reports | Two-path confusion | ~15K | ✅ DONE |
| W2.1 | Guardrails + shim labels | `section_spine_terminology.py`, `c03_graphrag_bound.py` | False C0 claims | ~20K | ✅ DONE |
| W3.1 | Front spine bridge | `section_front_spine_bridge.py`, `proof_pool_resolver.py` | proof_pool without U0/L1/L0 | ~25K | ✅ DONE |
| W4.1 | FEC bridge exec summary | `section_fec_bridge.py`, `executive_summary_*` | Raw proof_pool to PA | ~30K | ✅ DONE |
| W5A.1 | FEC all lanes | All `*_lane.py`, `*_pa.py`, `input_authority_prompt_block.py` | Lane parity | ~40K | ✅ DONE |
| W5B.1 | L2 spine receipts | section_l2_* | L2 without spine packet | ~25K | ✅ DONE |
| W6.1 | Exit disposition | section_exit_* | section x3 as authority | ~25K | ✅ DONE |
| W7.1 | Runtime exhaust + L6 | section_runtime_exhaust_* | L6 before exhaust | ~25K | ✅ DONE |
| W8.1 | Certification receipts | section_one_spine_certification | false certification | ~30K | ✅ DONE |
| W9.1 | Plan closeout | emit_one_spine_master_closeout_w9 | two-path + suite triage | ~20K | ✅ DONE |

---

## Wave Progress

| Wave | Focus | Status | Tests Added | Files Changed |
|------|-------|--------|-------------|---------------|
| W1 | Inventory | ✅ DONE | contract inventory tests | inventory + closeout |
| W2 | Guardrails | ✅ DONE | 7 guardrail tests | terminology, c03 shim |
| W3 | Front spine | ✅ DONE | 9 w3 tests | front bridge, resolver |
| W4 | FEC exec summary | ✅ DONE | 10 w4 tests | fec bridge, exec PA |
| W5A | FEC all lanes | ✅ DONE | 13 w5a tests | 7 lanes wired |
| W5B | L2 receipts | ✅ DONE | 13 w5b tests | l2 spine all lanes |
| W6 | Exit receipts | ✅ DONE | 13 w6 tests | exit disposition |
| W7 | Runtime exhaust | ✅ DONE | 13 w7 tests | exhaust + L6 handoff |
| W8 | Certification | ✅ DONE | 12 w8 tests | certification triple |
| W9 | Closeout | ✅ DONE | 4 w9 tests | master + no-two-path + triage |

---

## Out Of Scope

- Full agentic_core C0.2 dense retrieval or C0.3 governed graph traverse
- Canonical C0.5 FinalEvidenceContract from spine C0
- Product certification / release signoff
- Removing `python -m apps_rg --section <lane>`
- Weakening X2/X3 gates or fixtures to force PASS

---

## Wave 1 — Inventory (COMPLETE)

WAVE_ID: W1
WAVE_STATUS: DONE
WAVE_COMPLETE: YES

**Deliverables:**
- [one_spine_section_path_inventory.md](docs/reports/apps_rg/one_spine_section_path_inventory.md)
- [one_spine_guardrail_closeout.json](docs/reports/apps_rg/one_spine_guardrail_closeout.json)

---

## Wave 2 — Guardrails (COMPLETE)

WAVE_ID: W2
WAVE_STATUS: DONE
WAVE_COMPLETE: YES

**Deliverables:**
- `apps_rg/runtime/section_spine_terminology.py`
- `apps_rg/runtime/one_spine_inventory.py`
- `tests/unit/apps_rg/test_one_spine_section_guardrails.py`

---

## Wave 3 — Front Spine Bridge (COMPLETE)

WAVE_ID: W3
WAVE_STATUS: DONE
WAVE_COMPLETE: YES

**Runtime proof:** executive_summary with ValidatedRequest, L1PlanContract, RouteContract before proof_pool.

**Reports:**
- [one_spine_front_bridge_w3_redo.json](docs/reports/apps_rg/one_spine_front_bridge_w3_redo.json)
- [section_front_spine_precondition_blocked_proof.json](docs/reports/apps_rg/section_front_spine_precondition_blocked_proof.json)

**Kill switch:** `resolve_section_proof_pool` requires `SectionFrontSpineBridge` when product-visible.

---

## Wave 4 — FEC Bridge executive_summary (COMPLETE)

WAVE_ID: W4
WAVE_STATUS: DONE
WAVE_COMPLETE: YES

**Artifacts per run:**
- `final_evidence_contract_bridge.json` (`fec_bridge_mode: section_fec_bridge`)
- `c0_fec_bridge_receipt.json`
- `compiled_prompt_artifact.json` with `evidence_contract_consumed: true`, `raw_proof_pool_direct_to_pa: false`

**Report:** [one_spine_c0_fec_bridge_w4.json](docs/reports/apps_rg/one_spine_c0_fec_bridge_w4.json)

---

## Wave 5A — FEC Bridge All Lanes (COMPLETE)

WAVE_ID: W5A
WAVE_STATUS: DONE
WAVE_COMPLETE: YES

**Lanes proven (runtime):** headline, unify_bullets, unify_narrative, ibm_bullets, ibm_narrative, competencies, executive_summary (regression).

**Shared wiring:** `wire_section_fec_bridge_for_lane()`, `finalize_section_compiled_with_proof_pool()` → FEC authority.

**Report:** [one_spine_fec_bridge_w5a_all_lanes.json](docs/reports/apps_rg/one_spine_fec_bridge_w5a_all_lanes.json)

**Note:** unify_bullets / unify_narrative may X3_BLOCK on quality gates; FEC spine proof still PASS (exit 0 with `--allow-non-allow-exit-zero`).

---

## Wave 5B — L2 Spine Receipts (COMPLETE)

WAVE_ID: W5B
WAVE_STATUS: DONE
WAVE_COMPLETE: YES

**Report:** [one_spine_l2_receipts_w5b_all_lanes.json](docs/reports/apps_rg/one_spine_l2_receipts_w5b_all_lanes.json)

---

## Wave 6 — Exit Disposition Receipts (COMPLETE)

WAVE_ID: W6
WAVE_STATUS: DONE
WAVE_COMPLETE: YES

**Authority:** `exit_disposition_receipt.json` canonical; `x3_disposition.json` mirror only.

**Report:** [one_spine_exit_receipts_w6_all_lanes.json](docs/reports/apps_rg/one_spine_exit_receipts_w6_all_lanes.json)

---

## Wave 7 — RuntimeExhaust + L6 Handoff (COMPLETE)

WAVE_ID: W7
WAVE_STATUS: DONE
WAVE_COMPLETE: YES

**Report:** [one_spine_runtime_exhaust_w7_all_lanes.json](docs/reports/apps_rg/one_spine_runtime_exhaust_w7_all_lanes.json)

---

## Wave 8 — Certification Receipts (COMPLETE)

WAVE_ID: W8
WAVE_STATUS: DONE
WAVE_COMPLETE: YES

**Per lane:** `one_spine_certification_receipt.json`, `proof_eligibility_receipt.json`, `product_certification_receipt.json`

**Report:** [one_spine_certification_w8_all_lanes.json](docs/reports/apps_rg/one_spine_certification_w8_all_lanes.json)

**Note:** 6/7 lanes `ONE_SPINE_SECTION_CERTIFIED`; headline `NOT_CLAIMED` on X3_BLOCK (judge), chain still complete.

---

## Wave 9 — Master Closeout (COMPLETE)

WAVE_ID: W9
WAVE_STATUS: DONE
WAVE_COMPLETE: YES

**STATUS:** PARTIAL (overall) · **FINAL_ONE_SPINE_STATUS:** CLOSED · **TARGETED_ONE_SPINE_PROOF:** PASS

**Deliverables:**
- [one_spine_master_closeout_w9.json](docs/reports/apps_rg/one_spine_master_closeout_w9.json)
- [one_spine_no_two_path_proof_w9.json](docs/reports/apps_rg/one_spine_no_two_path_proof_w9.json)
- [one_spine_contract_suite_triage_w9.json](docs/reports/apps_rg/one_spine_contract_suite_triage_w9.json)

**Contract suite:** `full_apps_contract_suite_certified=false` — 1637 failed, 5619 passed, 87 errors; `IN_SCOPE_ONE_SPINE=0`; `UNKNOWN_NEEDS_TRIAGE=1802`.

WAVE_COMPLETE: plan=one-canonical-spine wave=9 note="master closeout; targeted proof PASS; full suite not certified"

---

## Definition of Done

| ID | Criterion | Verification | Status |
|----|-----------|--------------|--------|
| D1 | Single plan SSOT on disk | `.cursor/plans/one-canonical-spine-e8b4a1.md` exists | ✅ |
| D2 | Notion Plans row registered | Plans DB slug match + Exists On Disk | ✅ |
| D3 | W3 front spine runtime proof | `one_spine_front_bridge_w3_redo.json` status PASS | ✅ |
| D4 | W4 FEC + PA consumption proof | `one_spine_c0_fec_bridge_w4.json` status PASS | ✅ |
| D5 | W5A all lanes FEC artifacts | `one_spine_fec_bridge_w5a_all_lanes.json` status PASS | ✅ |
| D6 | Targeted one-spine tests green | W3–W9 unit — 94 passed | ✅ |
| D7 | Smoke: all 7 section lanes | W9 runtime matrix exit 0 | ✅ |
| D8 | No agentic_core edits for spine waves | `forbidden_files_touched.agentic_core=false` | ✅ |
| D9 | W5B–W8 spine receipts + certification | w5b–w8 all-lanes reports PASS | ✅ |
| D10 | W9 closeout + no-two-path | `one_spine_master_closeout_w9.json` lanes 7/7 | ✅ |
| D11 | Full apps_contract suite | NOT certified — triage logged | 🔲 |

### Verification vs Deferral

| Item | Verified now | Deferred |
|------|--------------|----------|
| FEC all lanes | W5A runtime matrix | — |
| Full apps_contract suite | W9 triage run (failed) | Suite certification |
| X3_ALLOW all lanes | — | Per-lane quality/judges |
| Canonical spine C0 | — | By design (section_fec_bridge) |
| Product certification all lanes | W8 runtime | headline X3_BLOCK |

---

## Key Modules (SSOT)

| Module | Role |
|--------|------|
| [section_front_spine_bridge.py](apps_rg/runtime/section_front_spine_bridge.py) | U0/L1/L0 before proof_pool |
| [section_fec_bridge.py](apps_rg/runtime/section_fec_bridge.py) | RouteContract + proof_pool → FEC bridge |
| [proof_pool_lane_integration.py](apps_rg/runtime/proof_pool_lane_integration.py) | Lane proof_pool + front spine |
| [input_authority_prompt_block.py](apps_rg/runtime/dispatch/input_authority_prompt_block.py) | PA INPUT_AUTHORITY via FEC |
| [section_l2_spine_receipt.py](apps_rg/runtime/section_l2_spine_receipt.py) | L2ExecutionPacket + SealedL2 |
| [section_exit_spine_receipt.py](apps_rg/runtime/section_exit_spine_receipt.py) | ExitDispositionReceipt |
| [section_runtime_exhaust_spine_receipt.py](apps_rg/runtime/section_runtime_exhaust_spine_receipt.py) | RuntimeExhaustBundle + L6 handoff |
| [section_one_spine_certification.py](apps_rg/runtime/section_one_spine_certification.py) | W8 certification triple |
| [section_one_spine_no_two_path.py](apps_rg/runtime/section_one_spine_no_two_path.py) | W9 no-two-path inspection |

---

## Explicit Non-Claims

- Not full canonical C0.2 / C0.3 / C0.5
- Not full `tests/_apps_contract` certification (`full_apps_contract_suite_certified=false`)
- Not all lanes product-certified (headline may be NOT_CLAIMED with complete chain)
- Not durable UWG/L4 write unless UWG artifacts exist
- `proof_pool_metadata` on runtime_payload remains for X2/ledger only

---

PLAN_COMPLETE: plan=one-canonical-spine-e8b4a1 note="W1-W9 complete; FINAL_ONE_SPINE_STATUS=CLOSED; targeted proof PASS; full apps_contract suite failed (1802 UNKNOWN triage); reports docs/reports/apps_rg/one_spine_*"
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
