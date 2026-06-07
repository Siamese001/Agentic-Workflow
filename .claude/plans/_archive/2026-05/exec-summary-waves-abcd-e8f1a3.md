---
plan_id: exec-summary-waves-abcd-e8f1a3
plan_type: refactor
touches_agentic_core: false
touches_governance_ci: false
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# Executive Summary — Waves A–D Remediation (Display + Repair + Regen + Infra)

**North star:** Fix root-cause executive-summary quality defects (Basel corruption, metric duplication, over-aggressive graph-only rewrite) and tighten repair/mutator order without weakening X2/X3 gates.

**Sibling plans:**
- [section-product-shape-alignment-b4e7a1.md](section-product-shape-alignment-b4e7a1.md) — 6-sentence SSOT (COMPLETE)
- [c03-skills-graph-exec-summary-f9a2c4.md](c03-skills-graph-exec-summary-f9a2c4.md) — C0.3 graph enhancements (Not Started)
- [apps-rg-proof-pool-c0-ssot-a7f3e2.md](apps-rg-proof-pool-c0-ssot-a7f3e2.md) — pool/FEC SSOT (In Progress)

**Live proof artifact:** [exec_summary_20260523_213853](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260523_213853)

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: COMPLETE
CURRENT_WAVE: —
LAST_COMPLETED_WAVE: D
LAST_UPDATED: 2026-05-23
NOTION_STATUS: Completed
NOTION_PAGE_ID: 36927693-f55c-8154-9135-e3691666916e
NOTION_PLANS_ROW: page_id=36927693-f55c-8154-9135-e3691666916e
DISK_SSOT: .cursor/plans/exec-summary-waves-abcd-e8f1a3.md

PLAN_COMPLETE: plan=exec-summary-waves-abcd-e8f1a3 note="Waves A–D implemented; Brown CLI X2 PASS; X3_REVIEW (2/3 judges)"
WAVE_COMPLETE: plan=exec-summary-waves-abcd-e8f1a3 wave=A note="splitter PUA tokens; X2 integrity gates; graph-only dedup"
WAVE_COMPLETE: plan=exec-summary-waves-abcd-e8f1a3 wave=B note="opener-only repair; composition-before-graph-repair; voice join"
WAVE_COMPLETE: plan=exec-summary-waves-abcd-e8f1a3 wave=C note="composition-aware rebuild; strategic closer; judge regen opt-in"
WAVE_COMPLETE: plan=exec-summary-waves-abcd-e8f1a3 wave=D note="APPS_RG_VLLM_AUTO_START; topology doc"

---

## Context

Brown & Brown run `exec_summary_20260523_211407` exposed three root causes:

| RC | Root cause | Symptom |
|----|------------|---------|
| RC-1 | U+001F abbrev tokens consumed by `\s` / `strip()` in `split_sentences` | `B3\x1f` instead of `Basel III` |
| RC-2 | Graph-only pad loop ignored `covered_bases` | Duplicate 8→28 metric in S2 + S6 |
| RC-3 | Full graph-only rewrite on `mechanical_opener_stack` alone | Stacked template prose; judge soft-fail |

Waves A–D address RC-1–RC-3 plus infra ergonomics (vLLM container down on first CLI attempt).

---

## Execution flow (implemented)

```text
A[Wave A: splitter + X2 integrity + graph-only dedup]
  → B[Wave B: repair policy + mutator order]
  → C[Wave C: composition-aware rebuild + optional X1D regen]
  → D[Wave D: infra auto-start doc/opt-in]
  → V[Verify: Brown CLI + contract tests]
```

---

## Wave A — Display integrity + graph-only dedup ✅

| ID | Deliverable | Files |
|----|-------------|-------|
| A.1 | PUA abbrev sentinels (`\ue000…\ue001`); ASCII-only sentence boundary split | [executive_summary_sentence_utils.py](apps_rg/runtime/validators/executive_summary_sentence_utils.py) |
| A.2 | `x2_exec_summary_display_roundtrip_integrity` | [executive_summary_x2.py](apps_rg/runtime/validators/executive_summary_x2.py) |
| A.3 | `x2_exec_summary_cross_sentence_metric_dedup` | [executive_summary_x2.py](apps_rg/runtime/validators/executive_summary_x2.py) |
| A.4 | Pad loop honors `covered_bases` | [exec_summary_graph_only_quality.py](apps_rg/runtime/sections/exec_summary_graph_only_quality.py) |
| A.5 | SSOT gate registration | [section_product_shape_ssot.py](apps_rg/runtime/sections/section_product_shape_ssot.py) |
| A.6 | Quant background min word band | [exec_summary_graph_only_quality.py](apps_rg/runtime/sections/exec_summary_graph_only_quality.py) |

---

## Wave B — Repair policy + mutator order ✅

| ID | Deliverable | Files |
|----|-------------|-------|
| B.1 | Opener-only repair before full graph rewrite (`repair_kind=opener_normalize_only`) | [exec_summary_graph_only_quality.py](apps_rg/runtime/sections/exec_summary_graph_only_quality.py) |
| B.2 | Extended mechanical-opener normalization + `join_executive_summary_sentences` | [executive_summary_composition.py](apps_rg/runtime/sections/executive_summary_composition.py), [executive_summary_voice_repair.py](apps_rg/runtime/sections/executive_summary_voice_repair.py) |
| B.3 | Composition plan built **before** graph-only repair | [executive_summary_lane.py](apps_rg/runtime/sections/executive_summary_lane.py) |

---

## Wave C — Composition-aware rebuild + optional X1D regen ✅

| ID | Deliverable | Files |
|----|-------------|-------|
| C.1 | `build_graph_only_executive_summary_from_facts(..., composition_plan, target_role)` | [exec_summary_graph_only_quality.py](apps_rg/runtime/sections/exec_summary_graph_only_quality.py) |
| C.2 | Strategic closer sentence (JD-shaped, non-proof) for sentence 6 pad | [exec_summary_graph_only_quality.py](apps_rg/runtime/sections/exec_summary_graph_only_quality.py) |
| C.3 | `RELEASE_JUDGE_REGENERATION_ENABLED=True`; opt-in `APPS_RG_EXEC_SUMMARY_JUDGE_REGEN=1` | [executive_summary_repair_policy.py](apps_rg/runtime/sections/executive_summary_repair_policy.py) |

---

## Wave D — Infra auto-start ✅

| ID | Deliverable | Files |
|----|-------------|-------|
| D.1 | `APPS_RG_VLLM_AUTO_START=1` → `docker start local-qwen-vllm` on preflight | [section_cli_preflight.py](apps_rg/runtime/section_cli_preflight.py) |
| D.2 | Topology + Fix-AppsRgWslRuntime.ps1 reference | [qwen-vllm-topology.md](docs/architecture/qwen-vllm-topology.md) |

---

## Verification evidence

### Unit / contract tests

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest \
  tests/unit/apps_rg/test_executive_summary_product_shape_x2.py \
  tests/unit/apps_rg/test_exec_summary_graph_only_quality.py \
  tests/unit/apps_rg/test_section_cli_preflight.py \
  tests/_apps_contract/test_product_shape_ssot_parity.py \
  -q -o addopts=
```

**Result:** 23 passed (2026-05-23)

### Brown & Brown live CLI

```bash
python -m apps_rg --section executive_summary \
  --target-company "Brown & Brown" \
  --target-role "SVP IT Strategy & Innovation" \
  --jd apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt \
  --manual-brief apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md
```

**Artifact:** [exec_summary_20260523_213853](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260523_213853)

| Check | Before (211407) | After (213853) |
|-------|-----------------|----------------|
| Basel III display | `B3\x1f` corrupt | `Basel III` intact |
| 8→28 duplicate | S2 + S6 | Single occurrence |
| `x2_exec_summary_display_roundtrip_integrity` | n/a | PASS |
| `x2_exec_summary_cross_sentence_metric_dedup` | n/a | PASS |
| ChatGPT judge | 3.7 FAIL | **4.1 PASS** |
| Gemini / Claude | 2.0 / 2.2 | 2.0 / 2.8 |
| X3 | REVIEW | REVIEW (2/3 judges) |
| Exit code | 1 (expected) | 1 (expected) |

### Optional follow-up (out of scope)

Enable bounded judge regen for X3 ALLOW proof:

```powershell
$env:APPS_RG_EXEC_SUMMARY_JUDGE_REGEN='1'
```

---

## Definition of Done

| # | Criterion | Status |
|---|-----------|--------|
| DoD-1 | Wave A splitter roundtrip preserves `Basel III` after period boundary | ✅ |
| DoD-2 | Wave A graph-only no duplicate team-scale metric | ✅ |
| DoD-3 | Wave B opener-only path skips full rewrite when sufficient | ✅ |
| DoD-4 | Wave C strategic closer replaces duplicate pad | ✅ |
| DoD-5 | Wave D auto-start env + doc | ✅ |
| DoD-6 | Brown run X2 PASS including new gates | ✅ |
| DoD-7 | 23 unit/contract tests PASS | ✅ |

**X3 ALLOW** deferred — requires `APPS_RG_EXEC_SUMMARY_JUDGE_REGEN=1` live proof or C0.3 graph plan ([c03-skills-graph-exec-summary-f9a2c4.md](c03-skills-graph-exec-summary-f9a2c4.md)).

---

## Status table

| Wave | Focus | Status |
|------|-------|--------|
| A | Splitter + X2 integrity + dedup | ✅ DONE |
| B | Repair policy + mutator order | ✅ DONE |
| C | Composition rebuild + judge regen opt-in | ✅ DONE |
| D | vLLM auto-start | ✅ DONE |
| V | Brown CLI + tests | ✅ DONE (X3 REVIEW remains) |
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
