---
plan_id: exec-summary-s5-bridge-hardening-acc0f0
plan_type: enhancement
touches_agentic_core: false
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
parent_plan: exec-summary-brown-gap-hardening-b9e4c1
evidence_run: exec_summary_20260527_074803
---

# Executive Summary — S5 Derivatives Inventory + Stock Bridge Hardening

Close the two X2 blockers surfaced by Brown & Brown SVP run [`exec_summary_20260527_074803`](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260527_074803): `x2_exec_summary_s5_no_derivatives_inventory` caused by C0 non-capsule path exposing `fact_quant_hpc_003.claim_text` verbatim (contains "derivatives pricing"), and `x2_exec_summary_stock_bridge_max_two` caused by the composition plan emitting no per-sentence S4 opener directive, allowing the LLM to stack three consecutive stock bridges.

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: In Progress
CURRENT_WAVE: W1
LAST_COMPLETED_WAVE: W0
LAST_UPDATED: 2026-05-27

PLAN_CREATED: slug=exec-summary-s5-bridge-hardening-acc0f0 path=.claude/plans/exec-summary-s5-bridge-hardening-acc0f0.md status=In Progress

---

## Context (SCQA)

- **Situation** — Executive-summary lane (SVP strategy lane, Qwen scratch) runs the `format_selected_facts_for_c0` path by default (evidence capsule not active). That path dumps each selected fact's `claim_text` raw into the C0 SELECTED_FACT_PLAN block. `fact_quant_hpc_003.claim_text` contains the phrase "derivatives pricing, capital modeling, and portfolio stress analytics" — which triggers the `_S5_DERIVATIVES_INVENTORY_RE` gate. The composition plan (`format_composition_plan_for_pa`) provides brushstroke roles and `s5_metric_binding` but emits no per-sentence opener prescription for S2–S4, allowing the LLM to stack three consecutive stock bridges.
- **Complication** — W2.3 of plan `exec-summary-brown-gap-hardening-b9e4c1` added `preferred_display_framing` for `fact_quant_hpc_003` but only wired it to the evidence capsule path (`use_capsule=True`). The default non-capsule path was never patched. The stock bridge gate was added in W2.1 (fires correctly) but the composition block has never included an S4 non-stock opener directive.
- **Question** — How do we ensure (a) `fact_quant_hpc_003` never exposes "derivatives pricing" through any C0 path, and (b) the model receives a per-sentence directive that forces variety at S4 when S2 and S3 already consume two stock bridge slots?
- **Answer** — (W1) Add `FACT_C0_DISPLAY_OVERRIDES` in `executive_summary_synthesis_contract.py` and apply it unconditionally in `format_selected_facts_for_c0`. (W2) Emit `s4_opener_directive` in `format_composition_plan_for_pa` for SVP strategy lanes with ≥3 S2–S4 brushstrokes. (W3) Persist `preferred_c0_display_text` on the graph node for `fact_quant_hpc_003` so future ledger reads also carry the safe framing. (W4) Unit test all three seams.

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|------|-----------|-------|-------------|--------|------------------|
| W0 | W0.1 | Plan disk + Notion registration | ~5K | ✅ DONE | Plan file on disk; Plans DB row |
| W1 | W1.1–W1.2 | C0 framing override (non-capsule path) | ~20K | 🔄 IN PROGRESS | `format_selected_facts_for_c0` never emits "derivatives pricing" for `fact_quant_hpc_003` |
| W2 | W2.1 | Composition plan S4 opener directive | ~10K | ⬜ PENDING | `format_composition_plan_for_pa` emits `s4_opener_directive` for SVP lane ≥3 brushstrokes |
| W3 | W3.1 | Graph-ledger `preferred_c0_display_text` field | ~8K | ⬜ PENDING | `fact_quant_hpc_003` node carries `preferred_c0_display_text`; `format_selected_facts_for_c0` reads it first |
| W4 | W4.1 | Unit tests (3 new) | ~12K | ⬜ PENDING | All 3 new tests pass |
| W5 | W5.1 | Brown SVP proof re-run | ~25K | ⬜ PENDING | Both gates PASS; exit 0 |

### Phase Progress

| Phase | Title | Files | Status |
|-------|-------|-------|--------|
| W0.1 | Register plan (disk + Notion) | `.claude/plans/`, Notion Plans | ✅ DONE |
| W1.1 | `FACT_C0_DISPLAY_OVERRIDES` constant in synthesis_contract | `executive_summary_synthesis_contract.py` | 🔄 IN PROGRESS |
| W1.2 | Apply override in `format_selected_facts_for_c0` | `executive_summary_pa.py` | 🔄 IN PROGRESS |
| W2.1 | `s4_opener_directive` in `format_composition_plan_for_pa` | `executive_summary_composition.py` | ⬜ PENDING |
| W3.1 | `preferred_c0_display_text` on `fact_quant_hpc_003` node | `master_skills_arsenal_ledger.json` | ⬜ PENDING |
| W4.1 | Unit tests | `tests/unit/apps_rg/test_executive_summary_w4_s5_bridge_hardening.py` | ⬜ PENDING |
| W5.1 | Brown SVP proof re-run + gate PASS verify | CLI + artifacts | ⬜ PENDING |

---

## Wave 0 — Plan registration

WAVE_ID: W0
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED

**Acceptance**
- [x] [`.claude/plans/exec-summary-s5-bridge-hardening-acc0f0.md`](exec-summary-s5-bridge-hardening-acc0f0.md) on disk.
- [ ] Notion Plans row: `Status=In Progress` — pending Notion registration in same response.

---

## Wave 1 — C0 framing override

WAVE_ID: W1
WAVE_STATUS: IN PROGRESS
AUTHORIZATION_STATUS: NOT_REQUIRED

**Phases**
- [ ] **W1.1** — Add `FACT_C0_DISPLAY_OVERRIDES: dict[str, str]` to `executive_summary_synthesis_contract.py`. Key = `fact_id`, value = safe C0 display line. Entry for `fact_quant_hpc_003`: "FSA-chartered quantitative foundation, built through early-career capital modeling and portfolio stress analytics."
- [ ] **W1.2** — In `format_selected_facts_for_c0` (`executive_summary_pa.py`), check `FACT_C0_DISPLAY_OVERRIDES` before using `claim_text`. If override exists, emit `{fid}: {override_text} [preferred_display_framing]` instead.

**Acceptance**
- [ ] C0 output for any fact list containing `fact_quant_hpc_003` does NOT contain "derivatives pricing".
- [ ] Unit test `test_format_selected_facts_for_c0_excludes_derivatives_phrase` passes.

---

## Wave 2 — Composition plan S4 opener directive

WAVE_ID: W2
WAVE_STATUS: PENDING
AUTHORIZATION_STATUS: NOT_REQUIRED

**Phases**
- [ ] **W2.1** — In `format_composition_plan_for_pa` (`executive_summary_composition.py`), when the plan is an SVP strategy lane (`strategy_executive=True` or `dominant_arc == "B2_governed_platform_system"`) and brushstroke count ≥ 3, append: `s4_opener_directive: use non-stock opener for S4 (e.g. "In parallel," / "That operating foundation also,") — S2 and S3 consume both stock bridge slots`.

**Acceptance**
- [ ] `format_composition_plan_for_pa` output for a 4-brushstroke SVP plan contains `s4_opener_directive`.
- [ ] Unit test `test_composition_plan_s4_opener_directive_svp_lane` passes.

---

## Wave 3 — Graph-ledger preferred_c0_display_text

WAVE_ID: W3
WAVE_STATUS: PENDING
AUTHORIZATION_STATUS: NOT_REQUIRED

**Phases**
- [ ] **W3.1** — Add `"preferred_c0_display_text": "FSA-chartered quantitative foundation, built through early-career capital modeling and portfolio stress analytics."` to the `fact_quant_hpc_003` node in `master_skills_arsenal_ledger.json`. Update `format_selected_facts_for_c0` to read `fact.get("preferred_c0_display_text")` first, then fall back to `FACT_C0_DISPLAY_OVERRIDES`, then `claim_text`.

**Acceptance**
- [ ] `fact_quant_hpc_003` node in ledger has `preferred_c0_display_text`.
- [ ] `format_selected_facts_for_c0` uses graph-data-driven framing when available.

---

## Wave 4 — Unit tests

WAVE_ID: W4
WAVE_STATUS: PENDING
AUTHORIZATION_STATUS: NOT_REQUIRED

**Test file:** `tests/unit/apps_rg/test_executive_summary_w4_s5_bridge_hardening.py`

**Tests**
- [ ] `test_format_selected_facts_for_c0_excludes_derivatives_phrase` — `fact_quant_hpc_003` in selected facts → C0 output does NOT contain "derivatives pricing".
- [ ] `test_composition_plan_s4_opener_directive_svp_lane` — SVP lane, 4 brushstrokes → `s4_opener_directive` present.
- [ ] `test_stock_bridge_gate_regression_triple_stack` — exact failing text from run `074803` → gate returns `False, "stock_bridge_stack:3..."`.

**Acceptance**
- [ ] `pytest tests/unit/apps_rg/test_executive_summary_w4_s5_bridge_hardening.py -o addopts=` → 3 passed.

---

## Wave 5 — Brown SVP proof re-run

WAVE_ID: W5
WAVE_STATUS: PENDING
AUTHORIZATION_STATUS: NOT_REQUIRED

**Command**
```bash
python -m apps_rg --section executive_summary \
  --target-company "Brown & Brown" \
  --target-role "SVP IT Strategy & Innovation" \
  --jd apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt \
  --manual-brief apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md
```

**Acceptance**
- [ ] `x2_exec_summary_s5_no_derivatives_inventory` PASS
- [ ] `x2_self_check_s5_no_derivatives_inventory` PASS
- [ ] `x2_exec_summary_stock_bridge_max_two` PASS
- [ ] Exit 0 (or X3 ALLOW / certification criteria documented)

---

## RCA Reference

| Gate | Root cause | Fix wave |
|------|-----------|----------|
| `x2_exec_summary_s5_no_derivatives_inventory` | `format_selected_facts_for_c0` passes `fact_quant_hpc_003.claim_text` verbatim; W2.3 fix only wired to capsule path | W1 + W3 |
| `x2_exec_summary_stock_bridge_max_two` | `format_composition_plan_for_pa` emits no S4 opener directive; model stacks 3 stock bridges | W2 |

---

## Gap Register

**GAP-1: `format_selected_facts_for_c0` capsule-path-only framing** — **IN PROGRESS** (W1)

**GAP-2: Composition plan no per-sentence S4 opener directive** — **OPEN** (W2)

**GAP-3: Graph node lacks `preferred_c0_display_text` field** — **OPEN** (W3)

---

## Definition of Done

DoD-1: C0 output for `fact_quant_hpc_003` never contains "derivatives pricing" via any path
- Evidence: `test_format_selected_facts_for_c0_excludes_derivatives_phrase` → pass
- Status: PENDING

DoD-2: Composition plan emits `s4_opener_directive` for SVP lane ≥3 brushstrokes
- Evidence: `test_composition_plan_s4_opener_directive_svp_lane` → pass
- Status: PENDING

DoD-3: Brown SVP proof re-run passes both gates
- Evidence: run artifact + gate log
- Status: PENDING
