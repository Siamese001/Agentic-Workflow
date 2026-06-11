---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\apps-rg-pa-w10-5-section-signal-hardening-c4f2a1.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\apps-rg-pa-w10-5-section-signal-hardening-c4f2a1.md'
source_sha256: 3f7ca6c3473a04651f7f00634a668c72c2a3eeef81bce16421e118901981a618
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: apps-rg-pa-w10-5-section-signal-hardening-c4f2a1
plan_type: refactor
touches_agentic_core: false
touches_governance_ci: false
touches_windsurf_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# apps_rg PA W10.5 — Section Signal Hardening

Add machine-readable section contracts, structured examples, a quality rubric, a unify template, and in-template self-check/evidence-tier signals to the apps_rg Prompt Assembly layer — closing the 20 gaps identified in the W10.5 gap analysis before W11 runtime binding opens.

> **plan_id discipline**: markers use `plan=apps-rg-pa-w10-5-section-signal-hardening-c4f2a1`

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: TODO
CURRENT_WAVE: W0
LAST_COMPLETED_WAVE: NONE
LAST_UPDATED: 2026-05-14

---

## Context (SCQA)

- **Situation** — W1–W10 delivered a governance-grade PA compiler, 8 templates, profiles, contracts, and 249 passing tests. The authority model, slot ordering, security fencing, and fail-closed compiler are solid.
- **Complication** — The W10.5 gap analysis (`artifacts/gap_reports/apps_rg_pa_w10_5_section_signal_gap_report_2026_05_14.md`) identified 20 gaps in prompt signal fidelity: missing section contracts, absent examples directories, no rubric, no unify template, and prompts lacking self-check blocks, evidence tiers, and gap-marking enforcement. Without these, the PA produces governance-compliant but signal-weak prompts that cannot reliably drive high-fidelity resume output.
- **Question** — How do we harden the apps_rg PA section signals to a standard where W11 runtime binding will produce high-fidelity resumes end-to-end?
- **Answer** — Add `section_contracts/`, `examples/`, and `rubrics/` YAML directories; create a `unify_v1` E4 template; update all 8 existing templates with self-check blocks, evidence tiers, and gap-marking; fix the BOM token budget; and cover everything with ~66 new tests — all without touching `agentic_core` or introducing runtime wiring.

---

## Gap Analysis Source

**Gap report:** `artifacts/gap_reports/apps_rg_pa_w10_5_section_signal_gap_report_2026_05_14.md`  
**Baseline tests:** 249 passing (76 governance + 173 W6–W10)

| Gap ID | Severity | Description |
|---|---|---|
| G-01 | BLOCKER | `section_contracts/` directory missing |
| G-02 | BLOCKER | Executive summary examples missing |
| G-03 | BLOCKER | Unify examples missing |
| G-04 | HIGH | Competencies examples missing |
| G-05 | BLOCKER | `rubrics/` directory missing |
| G-06 | HIGH | No `lead_with_seniority` enforcement in exec summary |
| G-07 | HIGH | Proof-point source not constrained to `candidate_facts` |
| G-08 | HIGH | No line-limit self-check in exec summary |
| G-09 | BLOCKER | No unify template exists |
| G-10 | HIGH | No contradiction-removal instruction |
| G-11 | HIGH | No gap-marking in competencies |
| G-12 | MEDIUM | Cluster ordering advisory-only, not enforced |
| G-13 | HIGH | No MUST_USE/SUPPORTING/GAP/FORBIDDEN evidence tiers |
| G-14 | HIGH | No section-specific evidence pre-selection block |
| G-15 | HIGH | No SELF_CHECK block in any E3 template |
| G-16 | MEDIUM | Many-shot negatives insufficient in E0 |
| G-17 | MEDIUM | No `<instruction_hierarchy>` XML tag in S0 |
| G-18 | HIGH | Self-check not anchored to rubric |
| G-19 | BLOCKER | `max_response_tokens: 200` in BOM — catastrophically undersized |
| G-20 | LOW | Docs/receipt not updated post-W10.5 |

---

## Status Tables

### Wave Progress

| Wave | Focus | Status | Tests Added | Files Changed |
|------|-------|--------|-------------|---------------|
| W10.5.0 | Baseline lock — confirm 249 tests, record in receipt | 🔲 TODO | — | — |
| W10.5.1 | Section contracts (exec_summary, unify, competencies) | 🔲 TODO | — | — |
| W10.5.2 | Examples (exec_summary, unify, competencies) | 🔲 TODO | — | — |
| W10.5.3 | Rubrics (6-dimension quality rubric) | 🔲 TODO | — | — |
| W10.5.4 | Template updates (SELF_CHECK, evidence tiers, gap-marking, hierarchy tag) | 🔲 TODO | — | — |
| W10.5.5 | Unify template + BOM fix | 🔲 TODO | — | — |
| W10.5.6 | Tests (~66 new + full regression) | 🔲 TODO | — | — |
| W10.5.7 | Docs + receipt update | 🔲 TODO | — | — |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W10.5.0.1 | Run 249-test baseline, record counts | 🔲 TODO |
| W10.5.1.1 | executive_summary_contract.yaml | 🔲 TODO |
| W10.5.1.2 | unify_contract.yaml | 🔲 TODO |
| W10.5.1.3 | competencies_contract.yaml | 🔲 TODO |
| W10.5.1.4 | prompt_registry.yaml contract refs | 🔲 TODO |
| W10.5.2.1 | executive_summary_examples.yaml | 🔲 TODO |
| W10.5.2.2 | unify_examples.yaml | 🔲 TODO |
| W10.5.2.3 | competencies_examples.yaml | 🔲 TODO |
| W10.5.3.1 | section_quality_rubrics.yaml (6 dims) | 🔲 TODO |
| W10.5.4.1 | strategic_tailor_v1 + generate_scratch_v1 updates | 🔲 TODO |
| W10.5.4.2 | tailor_existing_v1 + enhance_current_v1 updates | 🔲 TODO |
| W10.5.4.3 | E4 template S0 hierarchy tag | 🔲 TODO |
| W10.5.5.1 | unify_v1.yaml template | 🔲 TODO |
| W10.5.5.2 | BOM max_response_tokens fix (200 → 1800) | 🔲 TODO |
| W10.5.5.3 | prompt_registry.yaml + prompt_bom.yaml unify entry | 🔲 TODO |
| W10.5.6.1 | test_w10_5_section_contracts.py (~12 tests) | 🔲 TODO |
| W10.5.6.2 | test_w10_5_examples.py (~15 tests) | 🔲 TODO |
| W10.5.6.3 | test_w10_5_rubrics.py (~9 tests) | 🔲 TODO |
| W10.5.6.4 | test_w10_5_template_refs.py (~18 tests) | 🔲 TODO |
| W10.5.6.5 | test_w10_5_unify_template.py (~12 tests) | 🔲 TODO |
| W10.5.6.6 | Full regression rerun (249 baseline) | 🔲 TODO |
| W10.5.7.1 | docs/guides/apps_rg_pa_prompt_contract.md update | 🔲 TODO |
| W10.5.7.2 | artifacts/apps_rg/pa_prompt_contract_receipt.json update | 🔲 TODO |

---

## Out Of Scope

- No `agentic_core` edits of any kind
- No runtime wiring (W11 boundary respected — runtime binding is a separate future plan)
- No model/provider calls
- No C0 live retrieval
- No L2 execution
- No Exit evaluation
- No L4/UWG writes
- PA remains packet builder only throughout this plan
- No changes to existing test files (add new tests only; never weaken W6–W10 tests)

---

## Wave W10.5.0 — Baseline Lock

WAVE_ID: W10.5.0
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

**Authorization**: NOT_REQUIRED — read-only baseline capture, no source changes.

**Phases**:
- **W10.5.0.1** — Run full 249-test baseline; verify counts; update receipt with W10.5 section | ~1K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- `test_apps_rg_pa_governance.py` → 76 passed (matches W10 baseline)
- W6–W10 combined → 173 passed (matches W10 baseline)
- Receipt updated with `W10.5_baseline` section recording exact counts

---

## Wave W10.5.1 — Section Contracts

WAVE_ID: W10.5.1
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: B

**Authorization**: NOT_REQUIRED — new YAML files in apps_rg-owned directory, no shared surface.

**Phases**:
- **W10.5.1.1** — `apps_rg/prompt_assembly/section_contracts/executive_summary_contract.yaml` | ~3K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W10.5.1.2** — `apps_rg/prompt_assembly/section_contracts/unify_contract.yaml` | ~2K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W10.5.1.3** — `apps_rg/prompt_assembly/section_contracts/competencies_contract.yaml` | ~2K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W10.5.1.4** — Add `section_contract_refs` to `prompt_registry.yaml` entries | ~1K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Closes gaps:** G-01

**`executive_summary_contract.yaml` required fields:**
- `lead_with_seniority: required`
- `proof_points: {min: 1, max: 2, source: candidate_facts_only}`
- `max_lines: 4`
- `max_words: 60`
- `forbidden_openers: [list from rg_prompt_profile.yaml]`
- `forbidden_unsupported_adjectives: [proven, accomplished, seasoned, dynamic, results-driven]`
- `self_check_required: true`
- `citation_required: true`

**`unify_contract.yaml` required fields:**
- `no_new_claims: required`
- `harmonize_sections: [summary, experience, projects, competencies, skills]`
- `remove_contradictions: required`
- `contradiction_types: [date_overlap, title_inflation, metric_inconsistency, scope_inflation]`
- `summary_claims_must_appear_in_experience: required`
- `no_filler_for_removed_content: required`

**`competencies_contract.yaml` required fields:**
- `evidence_required: candidate_facts_only`
- `jd_gap_marking: required`
- `gap_marker_format: "[Gap: {jd_skill} — no supporting evidence]"`
- `cluster_ordering: jd_priority`
- `forbidden: [jd_only_skills_unlabeled, keyword_stuffing, unsupported_trendy_terms]`
- `self_check_required: true`

**Acceptance**:
- All 3 contract YAML files parse without error
- `prompt_registry.yaml` has `section_contract_ref` field in each E3 entry
- `section_contracts/` directory exists with 3 files

---

## Wave W10.5.2 — Examples

WAVE_ID: W10.5.2
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: C

**Phases**:
- **W10.5.2.1** — `apps_rg/prompt_assembly/examples/executive_summary_examples.yaml` | ~4K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W10.5.2.2** — `apps_rg/prompt_assembly/examples/unify_examples.yaml` | ~4K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W10.5.2.3** — `apps_rg/prompt_assembly/examples/competencies_examples.yaml` | ~3K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Closes gaps:** G-02, G-03, G-04, G-16

**Example file schema per entry:**
```yaml
- id: exec_summary_pos_001
  category: positive   # positive | negative | repair
  section: executive_summary
  seniority_band: EXECUTIVE
  before: null   # null for positive; string for repair/negative
  after: |
    Technology executive with 18+ years leading enterprise AI transformations.
    Reduced cloud spend $2.1M (2023) [source: fact_003]. Delivered 40% ops
    efficiency gain via ML pipeline modernization [source: fact_007].
  citation_preserved: true
  annotation: "Leads with seniority identity; 2 proof points from candidate_facts; no generic openers"
```

**Minimum counts per file:**
- ≥2 `category: positive` entries
- ≥2 `category: negative` entries (with `annotation` explaining the violation)
- ≥1 `category: repair` entry (before/after showing correction)

**Anonymization requirements:**
- No real employer names
- No real personal names
- No `@` email patterns
- No phone number patterns

**Acceptance**:
- All 3 example YAMLs parse without error
- Each file has ≥2 positive, ≥2 negative, ≥1 repair entries
- No PII in any entry

---

## Wave W10.5.3 — Rubrics

WAVE_ID: W10.5.3
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: D

**Phases**:
- **W10.5.3.1** — `apps_rg/prompt_assembly/rubrics/section_quality_rubrics.yaml` with 6 scoring dimensions | ~3K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Closes gaps:** G-05, G-18

**Required 6 dimensions (each with weight, description, pass_gate per section):**

| Dimension | Definition |
|---|---|
| `evidence_support` | Fraction of claims backed by `candidate_facts` citations |
| `target_relevance` | Fraction of included content mapped to JD requirements |
| `specificity` | Absence of vague descriptors; presence of concrete metrics |
| `non_generic_language` | Absence of forbidden phrases/openers from `rg_prompt_profile.yaml` |
| `section_consistency` | Claims consistent across sections (summary↔experience↔skills) |
| `citation_preservation` | Fraction of `[source: X]` IDs preserved from C0 |

**Per-section pass gates:**
- `executive_summary`: `evidence_support ≥ 0.9`, `non_generic_language ≥ 0.95`, `specificity ≥ 0.8`
- `experience`: `evidence_support ≥ 0.95`, `citation_preservation ≥ 0.9`
- `competencies`: `evidence_support = 1.0`, `target_relevance ≥ 0.7`

**Weights must sum to 1.0 per section.**

**Acceptance**:
- YAML parses without error
- All 6 dimensions present
- Each dimension has `weight`, `description`, `pass_gate`
- Weights sum to 1.0 per section

---

## Wave W10.5.4 — Template Updates

WAVE_ID: W10.5.4
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: E

**Phases**:
- **W10.5.4.1** — Update `strategic_tailor_v1.yaml` + `generate_scratch_v1.yaml` (largest changes) | ~8K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W10.5.4.2** — Update `tailor_existing_v1.yaml` + `enhance_current_v1.yaml` (smaller changes) | ~4K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W10.5.4.3** — Add `<instruction_hierarchy>` tag to S0 of all 4 E4 templates | ~2K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Closes gaps:** G-06, G-07, G-08, G-11, G-12, G-13, G-14, G-15, G-16, G-17, G-18

**Changes per E3 template (W10.5.4.1 and W10.5.4.2):**

1. **S0** — Wrap authority hierarchy section in `<instruction_hierarchy>` XML tag (G-17)

2. **I0 — Executive Summary section** (strategic_tailor_v1 + generate_scratch_v1 only):
   - Add `LEAD_CLAUSE: required — open with seniority/operating identity as first clause` (G-06)
   - Add `PROOF_POINT_SOURCE: candidate_facts only — do NOT use company_brief or jd_requirements as proof` (G-07)
   - Add `SELF_CHECK: verify ≤4 lines AND ≤60 words AND no generic openers AND ≥1 proof point from candidate_facts before finalizing` (G-08)

3. **I0 — Skills/Competencies section** (all E3 templates):
   - Add `GAP_MARKING_REQUIRED: for any JD skill with no candidate_facts match, output "[Gap: {skill} — no supporting evidence]"` (G-11)
   - Promote `cluster_ordering` from Y0 advisory to I0 enforcement: `CLUSTER_ORDER: jd_priority — reorder skill categories so highest-JD-weight categories appear first` (G-12)

4. **I0 — Evidence tier block** (all E3 templates, all sections):
   - Add `EVIDENCE_TIER_SELECTION` block before each section:
     ```
     MUST_USE: candidate_facts entries with alignment_map.status=DIRECT
     SUPPORTING: candidate_facts entries with alignment_map.status=IMPLIED
     GAP: jd_requirements with alignment_map.status=GAP (mark gaps, do not fill)
     FORBIDDEN: jd_requirements — never use as proof of candidate capability
     ```
   (G-13, G-14)

5. **I0 — SELF_CHECK_BEFORE_OUTPUT block** (all E3 templates):
   - Add after all section instructions:
     ```
     SELF_CHECK_BEFORE_OUTPUT:
       ref: apps_rg/prompt_assembly/rubrics/section_quality_rubrics.yaml
       verify:
         - evidence_support ≥ 0.9 for executive_summary
         - no generic openers (forbidden phrases list)
         - no JD-only skills without gap marker
         - all [source: X] IDs preserved from C0 input
         - ≤4 lines / ≤60 words for executive_summary
     ```
   (G-15, G-18)

6. **E0** — Add reference to `examples/*.yaml` file for the section type (G-16)

**Changes per E4 template (W10.5.4.3):**
- S0: wrap hierarchy prose in `<instruction_hierarchy>` XML tag only (G-17)
- No other changes to E4 templates

**Acceptance**:
- All 8 templates still parse as valid YAML
- `strategic_tailor_v1.yaml` I0 contains: `SELF_CHECK`, `GAP_MARKING_REQUIRED`, `EVIDENCE_TIER_SELECTION`, `LEAD_CLAUSE`, `PROOF_POINT_SOURCE`
- All 4 E3 templates contain `SELF_CHECK_BEFORE_OUTPUT`
- All 8 templates S0 contains `<instruction_hierarchy>`
- W6–W10 tests still pass (249 baseline)

---

## Wave W10.5.5 — Unify Template + BOM Fix

WAVE_ID: W10.5.5
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: F

**Phases**:
- **W10.5.5.1** — Create `apps_rg/prompt_assembly/templates/unify_v1.yaml` | ~5K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W10.5.5.2** — Fix `prompt_bom.yaml` `max_response_tokens: 200` → `1800` | ~1K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W10.5.5.3** — Add `unify_v1` entry to `prompt_registry.yaml` + `prompt_bom.yaml` template_registry_refs | ~1K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Closes gaps:** G-09, G-10, G-19

**`unify_v1.yaml` specification:**

```yaml
template_id: unify_v1
version: "1.0"
allowed_stage: E4_HEAL
description: Harmonize multi-section resume — remove contradictions, ensure cross-section consistency, add no new claims
```

**S0 — no-new-claims oath variant:**
- Base no-fabrication oath (same as all templates)
- Additional: `NO-NEW-CLAIMS OATH: You MUST NOT introduce any claim, fact, metric, employer, date, or technology not present in the input resume sections. Your sole function is to harmonize existing content.`

**I0 — Harmonization procedure (G-10):**
1. Summary→Experience consistency: every claim in the summary must appear in experience bullets
2. Competencies→Experience grounding: every listed competency must appear in at least one experience entry
3. Contradiction detection (referencing `contradiction_types` from `unify_contract.yaml`):
   - `date_overlap`: identify date ranges that overlap across roles — flag for resolution
   - `title_inflation`: identify title in summary stronger than title in experience — normalize to experience title
   - `metric_inconsistency`: identify same metric stated with different values across sections — preserve the more conservative value
   - `scope_inflation`: identify scope attributed in summary not supported by experience — remove from summary
4. Gap flagging: for any removed content, add to `gap_notes` in output
5. No new content added at any step

**R0 output schema — includes `harmonization_report` field**

**Acceptance**:
- `unify_v1.yaml` parses as valid YAML
- Stage is `E4_HEAL`
- S0 contains no-new-claims oath
- I0 contains all 4 contradiction-detection types
- `prompt_registry.yaml` resolves `unify_v1`
- `prompt_bom.yaml` `max_response_tokens` is 1800

---

## Wave W10.5.6 — Tests

WAVE_ID: W10.5.6
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: G

**Phases**:
- **W10.5.6.1** — `tests/_apps_contract/test_w10_5_section_contracts.py` (~12 tests) | ~3K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W10.5.6.2** — `tests/_apps_contract/test_w10_5_examples.py` (~15 tests) | ~4K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W10.5.6.3** — `tests/_apps_contract/test_w10_5_rubrics.py` (~9 tests) | ~2K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W10.5.6.4** — `tests/_apps_contract/test_w10_5_template_refs.py` (~18 tests) | ~5K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W10.5.6.5** — `tests/_apps_contract/test_w10_5_unify_template.py` (~12 tests) | ~3K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W10.5.6.6** — Full regression rerun (249 baseline must not decrease) | ~1K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Test coverage per file:**

| File | Coverage |
|---|---|
| `test_w10_5_section_contracts.py` | YAML parse, all required fields present per contract, field type/format checks |
| `test_w10_5_examples.py` | Example count per category (≥2+/≥2-/≥1 repair per file), anonymization check (no PII), `citation_preserved` field present on positive entries |
| `test_w10_5_rubrics.py` | YAML parse, all 6 dimensions present, each has `weight`+`description`+`pass_gate`, weights sum to 1.0 per section |
| `test_w10_5_template_refs.py` | SELF_CHECK in strategic_tailor/generate_scratch I0; SELF_CHECK_BEFORE_OUTPUT in all 4 E3 templates; GAP_MARKING_REQUIRED in all E3 skills sections; EVIDENCE_TIER_SELECTION in all E3 templates; `<instruction_hierarchy>` in all 8 templates S0; BOM max_response_tokens == 1800; no agentic_core imports in any new file |
| `test_w10_5_unify_template.py` | Template parse, stage=E4_HEAL, no-new-claims oath in S0, contradiction types in I0, unify_v1 in registry, template compiles via compiler |

**Acceptance**:
- All ~66 new tests pass
- `test_apps_rg_pa_governance.py` → 76 passed (no regression)
- W6–W10 → 173 passed (no regression)
- Total ≥ 315 passing

---

## Wave W10.5.7 — Docs + Receipt

WAVE_ID: W10.5.7
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: H

**Phases**:
- **W10.5.7.1** — Update `docs/guides/apps_rg_pa_prompt_contract.md` (add §14–§16 for contracts/examples/rubrics; update §11 test summary; update §13 remaining gaps) | ~3K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W10.5.7.2** — Update `artifacts/apps_rg/pa_prompt_contract_receipt.json` (add W10.5 to completed_waves, update total_tests_passed, add artifact lists) | ~2K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Closes gaps:** G-20

**Acceptance**:
- `docs/guides/apps_rg_pa_prompt_contract.md` contains `## 14.` and `## 15.` and `## 16.` sections
- Receipt JSON `completed_waves` includes `"W10.5"`
- Receipt JSON `total_tests_passed` ≥ 315
- All 20 G-* gaps listed as CLOSED in receipt

---

## Execution Details

### W10.5.0.1 — Baseline Lock
**Scope**: Run the 249-test baseline, record exact counts.

**Commands**:
```powershell
python -m pytest tests/_apps_contract/test_apps_rg_pa_governance.py --tb=no -q
python -m pytest tests/_apps_contract/test_w6_pa_compiler.py tests/_apps_contract/test_w7_pa_compiler_negative_controls.py tests/_apps_contract/test_w8_pa_templates_e4_e5.py tests/_apps_contract/test_w9_pa_integration_smoke.py tests/_apps_contract/test_w10_pa_guardrails.py --tb=no -q
```

### W10.5.6.6 — Full Regression
**Scope**: All tests after W10.5.1–W10.5.5 complete.

**Commands**:
```powershell
python -m pytest tests/_apps_contract/ --tb=short -q
```

---

## Gap Register

**GAP-1 (G-01, G-05, G-09, G-19) — Structural additions missing: section_contracts/, rubrics/, unify template, BOM budget**
- These are the 5 BLOCKERs that gate W11. Must be resolved before any runtime binding discussion.
- Impact: Without these, W11 would embed signal-weak prompts permanently into live inference.

**GAP-2 (G-02, G-03, G-04, G-16) — Examples absent or insufficient**
- Negative examples are the primary anti-hallucination calibration mechanism for Anthropic-class models.
- Impact: Executive summary and competency sections most affected — highest user-visibility sections.

**GAP-3 (G-06, G-07, G-08, G-15) — Missing in-template enforcement**
- Self-check, seniority lead, proof-point source constraint are all absent from E3 templates.
- Impact: Compliant-but-generic outputs that pass governance but fail quality.

**GAP-4 (G-13, G-14) — No evidence tiers in prompt body**
- `rg_evidence_profile.yaml` has source separation rules, but template I0 has no MUST_USE/GAP/FORBIDDEN tier labeling.
- Impact: Model treats all evidence equally; section-critical facts compete with noise.

**GAP-5 (G-11, G-12) — Competencies gap-marking and cluster ordering**
- Recruiter-facing signals missing. Gap markers give candidates and reviewers visibility into skill coverage.
- Impact: Skill lists that look complete but silently omit JD requirements.

---

## Definition of Done

DoD-1: All 20 gaps from the W10.5 gap analysis are closed (artifacts verified by test assertions)
- Evidence: `python -m pytest tests/_apps_contract/test_w10_5_*.py -q` → all pass
- Status: TODO

DoD-2: No runtime wiring introduced (PA remains packet builder only)
- Evidence: AST scan of all new files → 0 `agentic_core` imports; no L0/L1/L2/Exit/UWG references
- Status: TODO

DoD-3: ≥66 new W10.5 tests pass + 249 baseline preserved (≥315 total)
- Evidence: `python -m pytest tests/_apps_contract/ -q` shows ≥315 pass, 0 fail
- Status: TODO

DoD-4: CI gates green — no new violations introduced
- Evidence: `python ops_scripts/ci/run_contract_gates.py` exits 0 (advisory gates only)
- Status: TODO

DoD-5: Docs and receipt updated to reflect W10.5 as complete wave; all G-* gaps listed as CLOSED
- Evidence: `pa_prompt_contract_receipt.json` contains `"W10.5"` in `completed_waves`; docs has §14–§16
- Status: TODO

---

## Scope Expansion Authorization

When scope is discovered during execution, emit markers in order:

```
DISCOVERED_SCOPE: plan=apps-rg-pa-w10-5-section-signal-hardening-c4f2a1 wave=<N> phase=<M> gap="<what>" impact="<severity>"
AUTHORIZATION_DECISION: plan=apps-rg-pa-w10-5-section-signal-hardening-c4f2a1 decision=<ACCEPTED|DEFERRED|SPLIT_TO_NEW_PLAN|REJECTED> authorized_by=<user|author_gate|self> decisive_reason="<why>"
```

---

## Marker Quick Reference

```
WAVE_START: plan=apps-rg-pa-w10-5-section-signal-hardening-c4f2a1 wave=<N>
WAVE_COMPLETE: plan=apps-rg-pa-w10-5-section-signal-hardening-c4f2a1 wave=<N> note="+N tests, N files, scope=<summary>"
PHASE_COMPLETE: plan=apps-rg-pa-w10-5-section-signal-hardening-c4f2a1 phase=<W10.5.N.M>
PLAN_COMPLETE: plan=apps-rg-pa-w10-5-section-signal-hardening-c4f2a1 note="<final outcome>"
```
