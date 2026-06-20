---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\section-product-shape-alignment-b4e7a1.md'
original_relative_path: '_archive\\2026-05\\section-product-shape-alignment-b4e7a1.md'
source_sha256: 8ccd1f6d282fcdf229281d3210972940db19d18a2944d0cc445be9f1cbd40d44
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: section-product-shape-alignment-b4e7a1
plan_type: governance
touches_agentic_core: false
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# Section Product Shape — SSOT Authority Hardening

**North star:** [`section_product_shape_ssot.py`](apps_rg/runtime/sections/section_product_shape_ssot.py) is the **executable** product-shape authority. Every live seam (PA compile `PRODUCT_SHAPE`, X2, X1D judge rubrics, graph-only fallback, lane regen, modular RG export, JSON schema, contract tests) must **import or derive** bounds from SSOT — never copy magic numbers locally.

> **plan_id discipline:** `section-product-shape-alignment-b4e7a1` ↔ file stem ↔ markers `plan=section-product-shape-alignment-b4e7a1`

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: COMPLETE
CURRENT_WAVE: —
LAST_COMPLETED_WAVE: W5
LAST_UPDATED: 2026-05-23 (closeout — W1–W5 implemented; contract tests PASS)

NOTION_PAGE_ID: 36927693-f55c-81d4-b968-c2e8fcf06d15
NOTION_PLAN_URL: https://www.notion.so/section-product-shape-alignment-b4e7a1-36927693f55c81d4b968c2e8fcf06d15

PLAN_CREATED: slug=section-product-shape-alignment-b4e7a1 path=.cursor/plans/section-product-shape-alignment-b4e7a1.md status=Completed notion_page=36927693-f55c-81d4-b968-c2e8fcf06d15

WAVE_COMPLETE: plan=section-product-shape-alignment-b4e7a1 wave=1 note="parity harness, export bounds, judge, graph-only — unit+smoke"
WAVE_COMPLETE: plan=section-product-shape-alignment-b4e7a1 wave=2 note="IBM word budget X2, schema SDR, negative tests — unit"
WAVE_COMPLETE: plan=section-product-shape-alignment-b4e7a1 wave=3 note="E0/registry/regen/unify template — unit+grep"
WAVE_COMPLETE: plan=section-product-shape-alignment-b4e7a1 wave=4 note="legacy quarantine, lane_registry, retire x2_unify_max_heavy_3 — static+unit"
WAVE_COMPLETE: plan=section-product-shape-alignment-b4e7a1 wave=5 note="assert_zero_drift OK; product-shape pytest bundle 78 passed"
PLAN_COMPLETE: plan=section-product-shape-alignment-b4e7a1 note="PASS per acceptance standard (contract+smoke; canonical runtime not claimed)"

---

## Context (SCQA)

- **Situation** — SSOT already centralizes lane shapes and feeds [`section_prompt_drift_audit.py`](apps_rg/runtime/sections/section_prompt_drift_audit.py) + compile-time `PRODUCT_SHAPE` blocks. Executive summary X2 is **exactly 6 sentences / max 140 words** (imported into SSOT from `executive_summary_x2`).
- **Complication** — Seams still **duplicate or contradict** SSOT: export rejects `wc > 60`, judge rubric allows 4 sentences, graph-only caps at 5, IBM narrative lacks word-budget X2 gate, E0 examples teach 4 sentences, unify template allows HEAVY≤3. These are **authority failures**, not cosmetic string drift.
- **Question** — How do we make SSOT the single executable authority end-to-end?
- **Answer** — Build a **parity harness + negative-control contract tests first**, then fix P0 choke points (export + graph-only + judge) in W1, IBM/schema in W2, prompt teaching in W3, legacy quarantine in W4, canonical closeout in W5.

---

## Architecture Invariants (non-negotiable)

| ID | Invariant |
|----|-----------|
| INV-1 | **No independent shape constants** in runtime/export/judge/tests when SSOT (or its imported X2/rigor sources) already defines them. |
| INV-2 | Seams that cannot import SSOT directly must use a **documented generated snapshot** or a **parity test** proving equivalence to SSOT. |
| INV-3 | **Modular RG export** is a P0 product choke point: lane-valid shape must not be rejected or **silently narrowed** at assembly. |
| INV-4 | **Graph-only fallback** is product runtime, not repair prose: same 6-sentence / 140-word bounds; must pass the **same** X2 sentence-count and word-budget gates as the normal lane. |
| INV-5 | **X1D judges** must never authorize a shape X2 would reject (judges ⊆ X2 hardness). |
| INV-6 | **Do not weaken** X2/X3 gates or skip gates to pass. |
| INV-7 | **Do not edit** `agentic_core`. |
| INV-8 | **Do not change** product shape counts (6 sentences, 2/3/1 unify distribution, etc.) — only align enforcement. |
| INV-9 | **No docs-only or grep-only PASS** for release eligibility; classify proof tier explicitly. |
| INV-10 | **Mocks/fixtures/Phase0 synthetics** are not canonical runtime proof. |

---

## SSOT Import Contract

### Must import from `section_product_shape_ssot` (or re-exported symbols it imports)

| Seam | Required SSOT-derived symbols / APIs |
|------|--------------------------------------|
| `modular_rg_output_builder.py` | `EXEC_SUMMARY_MIN/MAX_SENTENCES`, `EXEC_SUMMARY_MAX_WORDS`; `MIN_CATEGORY_COUNT`, `MAX_CATEGORY_COUNT` |
| `executive_summary_judge_packet.py` | `shape_summary`, `bounds_gate_ids`, sentence/word caps via SSOT imports |
| `exec_summary_graph_only_quality.py` | Same sentence/word caps; target sentence count = `EXEC_SUMMARY_MIN_SENTENCES` |
| Lane regen strings (`*_lane_runtime.py`) | `section_product_shape(section_id).shape_summary` or format helpers |
| `input_authority_prompt_block.py` | Already uses SSOT for `PRODUCT_SHAPE` — extend parity tests only |
| New: `section_product_shape_export_bounds.py` (W1.0) | Thin SSOT module exposing **export** limits derived from X2 caps (no duplicate literals) |

### Cannot import SSOT directly

| Seam | Required mitigation |
|------|---------------------|
| `rg_output_schema.json` | W2 **Schema Decision Record** + `test_schema_export_bounds_match_ssot` |
| PA YAML templates | `audit_all_generated_lanes()` + forbidden/required patterns from `SectionProductShape` |
| E0 YAML examples | W3 contract test: compiled prompt must not contain retired 4–5 patterns from live E0 |

### New harness (W1.0 — deliver before other W1 code)

1. **`section_product_shape_parity.py`** — introspect SSOT vs: judge packet strings, export bounds, graph-only builder caps, `lane_registry` critical gates, schema maxLength fields (via test fixture map).
2. **`tests/_apps_contract/test_product_shape_ssot_parity.py`** — fails when SSOT `shape_summary` / `bounds_gate_ids` disagree with any registered seam snapshot.
3. **`tests/_apps_contract/test_product_shape_negative_controls.py`** — intentional fail-if-drift cases (see matrix below).

Extend SSOT in W1.0/W2.0 only when adding **new** export-bound helpers or registering `x2_ibm_narrative_word_budget` in `ibm_narrative.bounds_gate_ids` (mirror unify).

---

## Execution Order (authoritative)

| Wave | Focus | P0? |
|------|-------|-----|
| **W1** | SSOT parity harness + exec judge + graph-only + **modular RG export choke point** | Yes |
| **W2** | IBM narrative X2 gate + schema/export parity decisions | Yes |
| **W3** | Prompt teaching: E0, registry, competencies regen, unify template (SSOT-derived) | P1 |
| **W4** | Legacy quarantine/retirement + lane_registry + docs cleanup | P2 |
| **W5** | Final drift audit + canonical CLI smoke + closeout receipt | Required |

**Removed:** old W5/W6 split — export is **inside W1**, not a later wave.

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Status | Success Criteria |
|------|-----------|-------|--------|------------------|
| W1 | W1.0–W1.5 | Parity harness, export, judge, graph-only, negative tests | ✅ DONE | Export/graph-only/judge aligned to SSOT; contract tests PASS |
| W2 | W2.0–W2.3 | IBM word budget X2, schema SDR, export truncate policy | ✅ DONE | `x2_ibm_narrative_word_budget` live; schema parity test PASS |
| W3 | W3.1–W3.4 | E0/registry/regen/unify template via SSOT | ✅ DONE | E0 gold 6 sentences; unify HEAVY==2; registry SSOT-derived |
| W4 | W4.1–W4.3 | Legacy quarantine, `x2_unify_max_heavy_3`, registry | ✅ DONE | Quarantine banners; `x2_unify_max_heavy_3` retired from live emission |
| W5 | W5.1 | Drift audit + closeout receipt | ✅ DONE | `assert_zero_drift()` OK; receipt below |

### Phase Progress

| Phase | Title | Key files | Status |
|-------|-------|-----------|--------|
| W1.0 | SSOT parity harness | `section_product_shape_parity.py`, `test_product_shape_ssot_parity.py`, `test_product_shape_negative_controls.py` | ✅ DONE |
| W1.1 | Export bounds from SSOT | `modular_rg_output_builder.py`, `section_product_shape_export_bounds.py` | ✅ DONE |
| W1.2 | Exec judge ⊆ X2 | `executive_summary_judge_packet.py`, `test_lane_judge_x2_ssot_alignment.py` | ✅ DONE |
| W1.3 | Graph-only product runtime | `exec_summary_graph_only_quality.py`, `section_authority_repairs.py` | ✅ DONE |
| W1.4 | Export contract tests | `test_modular_rg_output_builder.py` (product-shape cases) | ✅ DONE |
| W1.5 | Graph-only smoke + X2 | `test_exec_summary_graph_only_product_shape.py` | ✅ DONE |
| W2.0 | IBM SSOT + X2 gate | `section_product_shape_ssot.py`, `ibm_narrative_x2.py` | ✅ DONE |
| W2.1 | IBM regen + template asserts | `ibm_narrative_lane_runtime.py`, `ibm_position_narrative_v1.yaml` | ✅ DONE |
| W2.2 | Schema Decision Record | `rg_output_schema.json`, `test_schema_export_bounds_match_ssot.py` | ✅ DONE |
| W2.3 | IBM negative tests | `test_ibm_narrative_word_budget_x2.py` | ✅ DONE |
| W3.1 | E0 six-sentence examples | `executive_summary_examples.yaml` | ✅ DONE |
| W3.2 | Registry + compiled prompt | `prompt_registry.yaml`, drift tests | ✅ DONE |
| W3.3 | Competencies regen + taxonomy | `competencies_lane_runtime.py`, `executive_capability_taxonomy.yaml` | ✅ DONE |
| W3.4 | Unify template distribution | `unify_bullet_tailor_v1.yaml` | ✅ DONE |
| W4.1 | Lane registry ↔ SSOT | `lane_registry.py`, exception record in plan | ✅ DONE |
| W4.2 | Legacy quarantine | `strategic_tailor_v2.yaml`, `modular_resume_generation.py` | ✅ DONE |
| W4.3 | Retire/document `x2_unify_max_heavy_3` | `unify_bullets_x2.py`, SSOT `RETIRED_*` | ✅ DONE |
| W5.1 | Closeout | drift audit CLI, receipt block | ✅ DONE |

---

## Edge Case Register (mapped to hardened waves)

| ID | Symptom | SSOT authority fix | Wave |
|----|---------|-------------------|------|
| EC-01 | Export `wc > 60` vs X2 ≤140 | Import `EXEC_SUMMARY_MAX_WORDS` in export bounds | W1.1 |
| EC-02 | `competencies[:6]` silent drop | Import `MAX_CATEGORY_COUNT` | W1.1 |
| EC-03 | Unify HEAVY≤3 in template | `UNIFY_DEFAULT_DISTRIBUTION` in YAML asserts | W3.4 |
| EC-04 | `x2_unify_max_heavy_3` looser | Retire or quarantine; not distribution authority | W4.3 |
| EC-05 | E0 ~4 sentences | Rewrite to 6 or remove from live PA | W3.1 |
| EC-06–08 | Judge 4-sentence / 4–5 test | Judge derives from SSOT; parity test | W1.2 |
| EC-07 | Graph-only max 5 | `EXEC_SUMMARY_MIN_SENTENCES` target + X2 run | W1.3 |
| EC-09 | Drift test asserts 4–5 | Negative control + SSOT patterns | W1.0 / W3.2 |
| EC-10–11 | IBM no word gate; `count('.')>=1` | Add gate to SSOT + X2; `== 1` assert | W2.0–W2.1 |
| EC-12–13 | Schema 240/800 vs X2 | Schema SDR + parity test | W2.2 |
| EC-14–15 | Regen eight / taxonomy 7 | SSOT `shape_summary` in regen | W3.3 |
| EC-16 | prompt_registry 4–5 | SSOT-derived catalog string | W3.2 |
| EC-17 | lane_registry ⊂ bounds | Parity harness + exception record | W4.1 |
| EC-18 | strategic_tailor_v2 | Quarantine banner | W4.2 |
| EC-19 | Stale receipts | Historical-only section | W4.2 |
| EC-21 | Bullet 250 silent truncate | Visible failure/warning in export | W2.2 |
| EC-23 | Phase0 synthetics | `SMOKE_ONLY` marker; forbidden as product proof | W4.2 |

---

## Wave 1 — SSOT Parity Harness + P0 Choke Points (export, judge, graph-only)

WAVE_ID: W1
WAVE_STATUS: TODO
CHECKPOINT: A

### W1.0 — Parity harness (first code)

- Add [`section_product_shape_parity.py`](apps_rg/runtime/sections/section_product_shape_parity.py): register seam snapshots (export max words, export max categories, judge rubric substrings, graph-only max sentences, `lane_registry` critical gate sets).
- Add [`tests/_apps_contract/test_product_shape_ssot_parity.py`](tests/_apps_contract/test_product_shape_ssot_parity.py): **fails** when SSOT `bounds_gate_ids` / numeric caps disagree with any registered seam.
- Add [`tests/_apps_contract/test_product_shape_negative_controls.py`](tests/_apps_contract/test_product_shape_negative_controls.py): see **Negative-Control Matrix** (below).
- Add [`tests/_apps_contract/test_lane_judge_x2_ssot_alignment.py`](tests/_apps_contract/test_lane_judge_x2_ssot_alignment.py): for `executive_summary`, `unify_narrative`, `ibm_narrative`, `competencies`, `headline`, `unify_bullets` — every judge criterion that mentions shape must be **at least as strict** as SSOT `shape_summary` + deterministic X2 bounds (no "4 sentences is valid", no 4–5 band).

### W1.1 — Modular RG export (P0 choke point)

- Add [`section_product_shape_export_bounds.py`](apps_rg/runtime/sections/section_product_shape_export_bounds.py) re-exporting SSOT caps for assembly (exec words/chars/sentences; competencies category cap; optional bullet truncate policy hook).
- Refactor [`modular_rg_output_builder.py`](apps_rg/l2_recipe/modular_rg_output_builder.py):
  - Replace hardcoded `wc > 60` / `len > 500` with SSOT-derived `EXEC_SUMMARY_MAX_WORDS` (+ char cap derived from SSOT, not guessed).
  - Replace `competencies[:6]` with `[:MAX_CATEGORY_COUNT]`.
  - On unavoidable truncate (bullets 250): emit **visible** `export_shape_warning` / failure receipt field — **no silent mutation** (INV-3).

### W1.2 — Executive summary judge ⊆ X2

- Rubric strings built from SSOT imports / `shape_summary` — remove "4 sentences is valid" and all 4–5 language.
- Fix [`test_executive_summary_judge_packet_srfs_rubric.py`](tests/_apps_contract/test_executive_summary_judge_packet_srfs_rubric.py) to assert SSOT-aligned rubric.

### W1.3 — Graph-only fallback = product runtime

- Target exactly `EXEC_SUMMARY_MIN_SENTENCES` (6); remove 4–5 docstrings and `>= 5` caps.
- After build, run **`check_exec_summary_sentence_count_6`** and **`x2_exec_summary_paragraph_max_words`** (or `run_x2_gates` subset) on representative fact pool — same validators as normal lane.
- Representative smoke: enough facts to produce **exactly 6** sentences.

### W1.4 — Export contract tests

- [`test_modular_rg_export_product_shape.py`](tests/unit/apps_rg/test_modular_rg_export_product_shape.py):
  - 6-sentence exec summary with **word_count 61–140** passes lane X2 mocks + **modular merge** (no `executive_summary_out_of_rg_bounds`).
  - 8-category competencies survive export (count == 8).
  - Assert export does not slice below `MIN_CATEGORY_COUNT` or above `MAX_CATEGORY_COUNT`.

### W1.5 — Graph-only smoke tests

- Unit test: graph-only output sentence count == 6 and X2 sentence + word gates PASS.

**W1 minimum commands:**
```bash
rg "4–5 dense|4-5|4 sentences is valid|wc > 60|competencies\[:6\]" apps_rg/l2_recipe/modular_rg_output_builder.py apps_rg/runtime/judges apps_rg/runtime/sections/exec_summary_graph_only_quality.py -n
python -m pytest tests/_apps_contract/test_product_shape_ssot_parity.py tests/_apps_contract/test_product_shape_negative_controls.py tests/unit/apps_rg/test_modular_rg_export_product_shape.py tests/unit/apps_rg/test_exec_summary_graph_only_product_shape.py -q -o addopts=
python -c "from apps_rg.runtime.sections.exec_summary_graph_only_quality import build_graph_only_executive_summary_from_facts; from apps_rg.runtime.validators.executive_summary_x2 import check_exec_summary_sentence_count_6; ..."
python -c "# modular RG export: 6 sentences, wc=100 -> merge success"
git diff --name-only
git diff -- agentic_core
```

---

## Wave 2 — IBM Narrative X2 Contract + Schema/Export Parity

WAVE_ID: W2
WAVE_STATUS: TODO
CHECKPOINT: B

### W2.0 — True X2 contract (mirror unify)

- Implement `x2_ibm_narrative_word_budget`: exactly **1** sentence, `<= NARRATIVE_MAX_WORDS` (58), `<= NARRATIVE_MAX_CHARS` (360) — constants from SSOT imports only.
- Register in `section_product_shape_ssot._ibm_narrative_shape().bounds_gate_ids` alongside `x2_ibm_narrative_exactly_one_sentence`.
- Add to `lane_registry` **critical_gates** unless recorded in **Registry Exception Record** with test proving intentional omission.

### W2.1 — IBM regen + template

- Regen strings: import SSOT `NARRATIVE_MAX_WORDS` / `NARRATIVE_MAX_CHARS` — no literal 58/360 copies outside SSOT chain.
- [`ibm_position_narrative_v1.yaml`](apps_rg/prompt_assembly/templates/ibm_position_narrative_v1.yaml): `count('.') == 1` (parity with unify).

### W2.2 — Schema Decision Record (SDR)

Encode decisions in plan + test — **no silent looseness**:

| Field | Current schema | X2 / SSOT | Decision (pick one per row in implementation) |
|-------|----------------|-----------|-----------------------------------------------|
| `headline_line.maxLength` | 240 | `x2_headline_executive_length` ≤140 | **Tighten to 140** OR keep 240 with test proving X2 always stricter and export never emits >140 |
| `role_narrative.maxLength` | 800 | 360 chars | **Tighten to 360** OR export test: narratives >360 fail before schema validation |
| Bullet text | truncate 250 | lane quality | **Fail/warn** on truncate — record in export receipt |

- Add `HEADLINE_MAX_CHARS = 140` to SSOT (import from `headline_x2` constant) in W2.2 if tightening.
- [`test_schema_export_bounds_match_ssot.py`](tests/_apps_contract/test_schema_export_bounds_match_ssot.py).

### W2.3 — IBM negative tests

- Fail X2 when: >58 words, >360 chars, >1 sentence (period count / gate).

**W2 minimum commands:**
```bash
python -m pytest tests/unit/apps_rg/test_ibm_narrative_word_budget_x2.py tests/_apps_contract/test_schema_export_bounds_match_ssot.py -q -o addopts=
rg "x2_ibm_narrative_word_budget|count\('\.'\) >= 1" apps_rg -n
```

---

## Wave 3 — Prompt Teaching Cleanup (SSOT-derived, not local strings)

WAVE_ID: W3
WAVE_STATUS: TODO
CHECKPOINT: C

### W3.1 — E0 examples (model-behavior risk)

- **Rewrite** [`executive_summary_examples.yaml`](apps_rg/prompt_assembly/examples/executive_summary_examples.yaml) gold/variants to **exactly 6 sentences** OR **remove** examples from live PA compile path.
- **Forbidden:** relying only on "do not mimic example count" while keeping 4-sentence gold in live E0.
- Test: compiled prompt grep — no retired `4-5` / `4 sentences` from live E0 payload.

### W3.2 — Registry + drift tests

- `prompt_registry.yaml` descriptions generated from or reviewed against `section_product_shape(section_id).shape_summary`.
- Replace `test_section_prompt_product_shape_drift` `4-5` regex with SSOT `required_any_text_patterns` for exec summary.

### W3.3 — Competencies

- Regen uses `MIN_CATEGORY_COUNT`–`MAX_CATEGORY_COUNT` from SSOT import chain.
- Taxonomy `default_category_count` must not imply fixed 7 or 8 outside band.

### W3.4 — Unify bullets

- Template asserts: `HEAVY == UNIFY_DEFAULT_DISTRIBUTION['HEAVY']` (2) — not `<= 3`.
- Self-check and post-output asserts use SSOT distribution dict.

---

## Wave 4 — Legacy Quarantine + Registry

WAVE_ID: W4
WAVE_STATUS: TODO
CHECKPOINT: D

### W4.1 — Lane registry parity

- `lane_registry.critical_gates` must equal SSOT `bounds_gate_ids` per lane **or** appear in **Registry Exception Record** (table in plan Gap Register) with justification + test.

### W4.2 — Non-product shape sources

- [`strategic_tailor_v2.yaml`](apps_rg/prompt_assembly/templates/strategic_tailor_v2.yaml): banner `NON_PRODUCT_PLANNING_ONLY — do not use for live lane shape; see section_product_shape_ssot`.
- [`modular_resume_generation.py`](apps_rg/l2_recipe/modular_resume_generation.py): `PHASE0_SMOKE_ONLY` — forbidden as product-shape proof (INV-10).

### W4.3 — `x2_unify_max_heavy_3`

- **Retire** from live `run_x2_gates` output **or** move to `RETIRED_*` with comment: non-authoritative upper bound; **distribution correctness = `x2_unify_rewrite_distribution_valid` only**.

---

## Wave 5 — Final Drift Audit + Closeout Receipt

WAVE_ID: W5
WAVE_STATUS: TODO
CHECKPOINT: E

### W5.1

```bash
rg "4–5 dense|4-5|4 sentences is valid|count\('\.'\) >= 1|HEAVY <= 3|max_HEAVY: 3|wc > 60|competencies\[:6\]" apps_rg tests docs -n
python -c "from apps_rg.runtime.sections.section_prompt_drift_audit import audit_all_generated_lanes; ..."
python -m pytest tests/_apps_contract/test_product_shape_ssot_parity.py tests/_apps_contract/test_product_shape_negative_controls.py tests/_apps_contract/test_lane_judge_x2_ssot_alignment.py tests/unit/apps_rg/test_modular_rg_export_product_shape.py -q -o addopts=
git diff --name-only
git diff -- agentic_core
```

Emit **Closeout Receipt** block (template below). `PLAN_COMPLETE` only when acceptance standard met.

---

## Negative-Control Test Matrix

Tests in `test_product_shape_negative_controls.py` (and lane-specific files) must **fail CI** if:

| Control | Failure trigger |
|---------|-----------------|
| NC-01 | Live exec summary prompt/judge/E0 contains `4-5`, `4–5`, or `4 sentences is valid` |
| NC-02 | Graph-only builder produces `< EXEC_SUMMARY_MIN_SENTENCES` sentences |
| NC-03 | Modular export rejects exec summary with `word_count` in 61..`EXEC_SUMMARY_MAX_WORDS` and 6 sentences |
| NC-04 | Export drops category 7 or 8 when input has 8 valid categories |
| NC-05 | Unify template self-check accepts `HEAVY=3` as valid distribution |
| NC-06 | IBM narrative X2 run lacks `x2_ibm_narrative_word_budget` gate emission |
| NC-07 | `lane_registry` missing SSOT `bounds_gate_ids` entry without exception record row |
| NC-08 | Judge rubric mentions looser sentence band than SSOT for any of the six shape lanes |
| NC-09 | `strategic_tailor_v2` used in live compile path without quarantine guard (grep-based guard test) |

---

## Proof Classification (required in closeout)

| Class | Allowed for | Examples |
|-------|-------------|----------|
| **Static / grep** | Drift discovery only | `rg` for 4–5 patterns |
| **Unit contract** | SSOT parity, negative controls, export merge, IBM X2 | pytest files above |
| **Smoke `python -c`** | Seam verification after unit coverage | graph-only 6 sentences + X2 |
| **Canonical runtime** | Release eligibility | Full lane run with real provider — **out of scope** unless user requests; plan PASS = contract + smoke only |

**Explicit non-claims in closeout:** mock judges, Phase0 synthetics, fixture-only lane runs, grep-clean without pytest PASS.

---

## Closeout Receipt

```text
STATUS: PASS
PLAN_ID: section-product-shape-alignment-b4e7a1
SCOPE_MATCH: yes — SSOT authority across PA/X2/judge/graph-only/export/schema/tests
SCOPE_DRIFT: none beyond listed seams
FILES_CHANGED:
- [section_product_shape_ssot.py](apps_rg/runtime/sections/section_product_shape_ssot.py)
- [section_product_shape_export_bounds.py](apps_rg/runtime/sections/section_product_shape_export_bounds.py)
- [section_product_shape_parity.py](apps_rg/runtime/sections/section_product_shape_parity.py)
- [modular_rg_output_builder.py](apps_rg/l2_recipe/modular_rg_output_builder.py)
- [executive_summary_judge_packet.py](apps_rg/runtime/judges/executive_summary_judge_packet.py)
- [exec_summary_graph_only_quality.py](apps_rg/runtime/sections/exec_summary_graph_only_quality.py)
- [ibm_narrative_x2.py](apps_rg/runtime/validators/ibm_narrative_x2.py)
- [unify_bullets_x2.py](apps_rg/runtime/validators/unify_bullets_x2.py)
- [lane_registry.py](apps_rg/runtime/rigor/lane_registry.py)
- [rg_output_schema.json](apps_rg/rg_output_schema.json)
- tests/_apps_contract/test_product_shape_*.py (+ lane/export/IBM/graph-only tests)
COMMANDS_RUN:
- python -c "from apps_rg.runtime.sections.section_prompt_drift_audit import assert_zero_drift; assert_zero_drift()" -> exit 0
- PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest tests/_apps_contract/test_product_shape_ssot_parity.py tests/_apps_contract/test_product_shape_negative_controls.py tests/_apps_contract/test_lane_judge_x2_ssot_alignment.py tests/_apps_contract/test_schema_export_bounds_match_ssot.py tests/_apps_contract/test_product_shape_edge_cases.py -o addopts= -> 78 passed
TESTS_GATES:
- product-shape contract bundle -> pass
- graph-only product-shape smoke -> pass
FORBIDDEN_FILES_TOUCHED:
- agentic_core: none
PROOF_CLASSIFICATION:
- static: drift audit assert_zero_drift
- unit contract: 78 pytest (product-shape parity/negative/edge/schema/judge alignment)
- smoke: graph-only 6 sentences + X2 sentence/word gates
- canonical runtime: not claimed (Brown & Brown live lane out of scope)
EXPLICIT_NON_CLAIMS:
- full Windows pytest collection (WinError 1920), mock judges, Phase0 synthetics, canonical live provider lane
NEXT_BLOCKER:
- none for plan PASS tier
```

---

## Definition of Done (acceptance standard)

**PASS is invalid** unless:

1. SSOT is the numeric and gate-id authority for all listed seams (INV-1, parity harness green).
2. No live-product 4–5 sentence or "4 sentences is valid" assertions (NC-01).
3. Graph-only produces 6 sentences and passes the same X2 sentence/word gates (NC-02, W1.5).
4. Modular export accepts 6-sentence exec summary at word_count 61–140 (NC-03).
5. Eight-category competencies survive export (NC-04).
6. IBM `x2_ibm_narrative_word_budget` live with negative tests (NC-06).
7. Schema SDR encoded and tested — no silent truncate (EC-21).
8. `git diff -- agentic_core` empty.

| DoD | Criterion | Proof class |
|-----|-----------|-------------|
| DoD-1 | Parity harness + negative controls pass | Unit contract |
| DoD-2 | Export + graph-only + judge W1 complete | Unit + smoke |
| DoD-3 | IBM + schema W2 complete | Unit contract |
| DoD-4 | E0/registry/unify W3 — no 4–5 teaching | Unit + grep |
| DoD-5 | Legacy quarantined W4 | Static + unit |
| DoD-6 | W5 closeout receipt emitted | All tiers documented |

---

## Gap Register

**GAP-1: Windows pytest collection WinError 1920** — targeted `-o addopts=`; note BLOCKED in receipt, not PASS.

**GAP-2: Headline 140-char in SSOT** — resolve in W2.2 SDR; add `HEADLINE_MAX_CHARS` to SSOT from `headline_x2`.

**GAP-3: Drift audit false positive** (`briefing_used_as_proof` only in compile block) — fix audit to read compiled PRODUCT_SHAPE or document exception in W4.1.

**GAP-4: Registry Exception Record** — table maintained in plan during W4.1 if any `bounds_gate_ids` intentionally omitted from `critical_gates`:

| lane | gate_id | reason | test |
|------|---------|--------|------|
| (empty at plan start) | | | |

**GAP-5: Canonical runtime proof** — not required for plan PASS; user may request Brown & Brown re-run separately.

---

## Out Of Scope

- `agentic_core` edits.
- Changing product shape counts.
- Weakening X2/X3.
- Docs-only proof or mock-only release eligibility.
- Notion backlog rows per wave (unless user asks).

---

## Marker Quick Reference

```
WAVE_START: plan=section-product-shape-alignment-b4e7a1 wave=<N>
WAVE_COMPLETE: plan=section-product-shape-alignment-b4e7a1 wave=<N> note="<proof classes used>"
PHASE_COMPLETE: plan=section-product-shape-alignment-b4e7a1 phase=<W1.0>
PLAN_COMPLETE: plan=section-product-shape-alignment-b4e7a1 note="<PASS|PARTIAL> per acceptance standard"
```
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
