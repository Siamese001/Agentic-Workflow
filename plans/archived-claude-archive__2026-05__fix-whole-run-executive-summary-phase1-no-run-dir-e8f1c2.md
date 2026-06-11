---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\fix-whole-run-executive-summary-phase1-no-run-dir-e8f1c2.md'
original_relative_path: '_archive\\2026-05\\fix-whole-run-executive-summary-phase1-no-run-dir-e8f1c2.md'
source_sha256: 2932eb62b06bf59f10f33764879ff376a6aca8a12d94eb08e262825677fa035c
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: fix-whole-run-executive-summary-phase1-no-run-dir-e8f1c2
plan_type: refactor
touches_agentic_core: false
touches_governance_ci: false
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# Fix whole-run executive_summary PHASE1_NO_RUN_DIR

Canonical whole-run (`python -m apps_rg`) must materialize `executive_summary` under `modular_r4/sections/executive_summary/real/<run_id>/` with resolvable `latest_*_run.json` pointers — same contract as section mode and competencies whole-run lane.

> **plan_id discipline**: `fix-whole-run-executive-summary-phase1-no-run-dir-e8f1c2`

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: COMPLETED
CURRENT_WAVE: W5
LAST_COMPLETED_WAVE: W5
LAST_UPDATED: 2026-05-20

---

## Context (SCQA)

- **Situation** — Section-mode `python -m apps_rg --section executive_summary` exits 0 and writes `native_c03_final_evidence.json` under `artifacts/apps_rg/runtime_proofs/executive_summary/`. Competencies whole-run lane materializes under `cli_*/modular_r4/sections/competencies/`. Whole-run `cli_c61c8be7fc9c` failed with `fatal_lane_recipe_policy:executive_summary:PHASE1_NO_RUN_DIR` while `phase1_lane_inventory` showed `executive_summary: ok|missing_pointer`.
- **Complication** — Phase1 dispatch reported success for executive_summary but `resolve_latest_lane_run_dir` found no pointer under integrated `modular_r4/sections/executive_summary/` (directory absent). Product proof gate BLOCKED (`outcome_authorized=false`, X3A). Section-only proof cannot upgrade product certification.
- **Question** — How do we align whole-run Phase1 executive_summary materialization with section-mode and competencies whole-run without expanding C0.3 to other lanes or restoring shadow runners?
- **Answer** — Narrow seam fix on briefing/JD threading, `MODULAR_R4_SECTIONS_ROOT` pointer finalization, and pre-run failure surfacing; prove with targeted unit tests plus canonical whole-run re-run.

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | W1.1–W1.2 | Investigation: section vs whole-run seam map | ~12K | Failed run artifacts on disk | ✅ DONE | Seam comparison doc in closeout |
| W2 | W2.1 | Failed-run artifact inspection (`cli_c61c8be7fc9c`) | ~8K | Run dir retained | ✅ DONE | Root cause classified with evidence |
| W3 | W3.1–W3.2 | Smallest fix + targeted pytest | ~15K | No native C0.3 schema change | ✅ DONE | Unit/contract tests green |
| W4 | W4.1–W4.2 | Runtime proof matrix | ~25K | Provider available for live run | ✅ DONE | Section PASS; whole-run exec dir + artifacts |
| W5 | W5.1 | Disk + Notion closeout, git sync | ~5K | NOTION_TOKEN set | ✅ DONE | Plan Completed in Notion; receipt on disk |

### Phase Progress

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W1.1 | Section vs whole-run entrypoint diff | `__main__.py`, `modular_resume_generation.py`, `canonical_dispatch.py` | Inline JD/brief vs file paths | ~6K | ✅ DONE |
| W1.2 | Pointer / run_dir discovery | `modular_lane_adapter.py`, `runtime_proof_layout.py` | `PHASE1_NO_RUN_DIR` vs dispatch `ok` | ~6K | ✅ DONE |
| W2.1 | Failed-run forensics | `artifacts/apps_rg/runs/cli_c61c8be7fc9c/**` | Empty `sections/executive_summary` | ~8K | ✅ DONE |
| W3.1 | Briefing inline vs path-like guard | `canonical_dispatch.py`, `briefing_resolution.py` | Slashes in inline briefing | ~8K | ✅ DONE |
| W3.2 | Integrated pre-run failure + tests | `integrated_lane_evidence_packaging.py`, `tests/unit/apps_rg/test_integrated_executive_summary_materialization_w8c.py` | Missing pointer masking | ~7K | ✅ DONE |
| W4.1 | Section-mode regression | `python -m apps_rg --section executive_summary` | Must stay PASS | ~10K | ✅ DONE |
| W4.2 | Canonical whole-run + product gate | `integrated_product_proof_gate.py` | No product PASS without validator | ~15K | ✅ DONE |
| W5.1 | Closeout + git | plan, receipt, Notion Plans row | — | ~5K | ✅ DONE |

---

## Out Of Scope

- Native C0.3 schema changes (unless root cause proves required — not required for briefing/pointer seam)
- Expanding C0.3 binding to lanes beyond executive_summary + competencies (existing first wave only)
- Section-only proof as product / Fort Knox / L7 certification
- Restoring deleted shadow runners (`lane_batch`, `orchestrate_full_resume`, `headline_dispatch`, ops matrix scripts)
- `agentic_core` edits without explicit authorization
- Bypassing cache preflight or package/orchestrator X3 paths

---

## Wave 1 — Investigation (section vs whole-run)

WAVE_ID: W1
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

**Phases**:
- **W1.1** — Compare entrypoint, lane args, JD/brief threading, SRFS/proof pool, front_spine, native C0.3 inputs | ~6K | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W1.2** — Compare `run_dir` creation, phase1 receipt, early-return paths | ~6K | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- Documented deltas: whole-run sets `APPS_RG_WHOLE_RUN_ENVELOPE`, `MODULAR_R4_SECTIONS_ROOT`, passes inline `job_description_text` + `manual_brief` (not file paths)
- Identified `resolve_latest_lane_run_dir` as Phase1 gate after in-process dispatch

---

## Wave 2 — Failed-run artifact inspection

WAVE_ID: W2
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: B

**Phases**:
- **W2.1** — Inspect `cli_c61c8be7fc9c` manifests and modular tree | ~8K | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- Read `r4_run_manifest.json`, `generate_resume_step_receipt.json`, `phase1_lane_inventory.json`, `integrated_lane_evidence_status.json`
- Confirmed competencies native C0.3 under modular sections; executive_summary tree missing entirely

---

## Wave 3 — Smallest fix + targeted tests

WAVE_ID: W3
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: C

**Phases**:
- **W3.1** — Preserve inline briefing with `/` slashes via `_read_optional_brief` / dispatch path (not `resolve_briefing_for_lanes` path-like fail) | ~8K | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W3.2** — `emit_integrated_lane_pre_run_failure` + W8C unit tests for Phase1 materialization | ~7K | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- `test_integrated_executive_summary_materialization_w8c.py` covers inline brief, pre-run failure artifact, Phase1 modular sections root
- No native C0.3 module schema edits

---

## Wave 4 — Runtime proof matrix

WAVE_ID: W4
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: D

**Phases**:
- **W4.1** — Section executive_summary + competencies regression | ~10K | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W4.2** — Canonical whole-run Brown & Brown targeting + `integrated_product_proof_gate` | ~15K | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Commands**:
```bash
python -m apps_rg --section executive_summary --target-company "Brown & Brown" --target-role "SVP IT Strategy & Innovation" --jd apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt --manual-brief apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.txt
python -m apps_rg --target-company "Brown & Brown" --target-role "SVP IT Strategy & Innovation" --jd apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt --manual-brief apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.txt
python -m apps_rg.runtime.integrated_product_proof_gate <latest_cli_run_dir> --json
```

**Acceptance**:
- Whole-run creates `modular_r4/sections/executive_summary/real/<run_id>/` with `run_manifest.json`, `l2_output.json`, `native_c03_final_evidence.json` when route proof exists
- Product gate may remain BLOCKED until `outcome_authorized=true` — no false product PASS claim

---

## Wave 5 — Closeout (disk + Notion + git)

WAVE_ID: W5
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: E

**Phases**:
- **W5.1** — Plan SSOT, closeout receipt, Notion Plans Completed, git commit + push | ~5K | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

---

## Gap Register

**GAP-1: Product certification on whole-run**
- Integrated validator requires authorized outcome; packaging alone does not PASS product proof
- Impact: Fort Knox / L7 claims deferred until validator PASS

---

## Definition of Done

DoD-1: Root cause documented with failed-run evidence
- Evidence: [fix_whole_run_executive_summary_phase1_no_run_dir_closeout_receipt.md](docs/reports/apps_rg/fix_whole_run_executive_summary_phase1_no_run_dir_closeout_receipt.md)
- Status: DONE

DoD-2: Targeted pytest for whole-run executive_summary materialization
- Evidence: `pytest tests/unit/apps_rg/test_integrated_executive_summary_materialization_w8c.py`
- Status: DONE

DoD-3: Section-mode executive_summary still passes with Brown & Brown JD/brief files
- Evidence: `python -m apps_rg --section executive_summary` exit 0
- Status: DONE

DoD-4: Whole-run executive_summary modular run dir + native C0.3 when proof exists
- Evidence: `modular_r4/sections/executive_summary/real/<run_id>/native_c03_final_evidence.json`
- Status: DONE (post-fix canonical run; see closeout receipt for run id)

DoD-5: Competencies native C0.3 whole-run regression unchanged
- Evidence: competencies lane under same `cli_*` run retains `native_c03_final_evidence.json`
- Status: DONE

| Verification | Deferred |
|--------------|----------|
| Section + unit tests | Live whole-run Fort Knox signoff |
| Modular exec run dir | Product proof gate PASS without authorized outcome |
| Pre-run failure surfacing | Shadow runner restoration |

---

PLAN_COMPLETE: fix-whole-run-executive-summary-phase1-no-run-dir-e8f1c2
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
