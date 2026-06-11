---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\skills-graph-hardening-gap-closure-53576c.md'
original_relative_path: 'skills-graph-hardening-gap-closure-53576c.md'
source_sha256: 947286615c659eeaa5b469f48b0ddea2776695a8a452287119e93cf019f0b86e
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: skills-graph-hardening-gap-closure-53576c
plan_type: refactor
touches_agentic_core: false
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# Skills Graph Hardening & Gap Closure

Close the feedback loop between `apps_rg` resume runs and `master_skills_arsenal_ledger.json` by building automated gap detection, enforcing per-section fact-to-skill ratio floors as CI gates, triaging 56 DRAFT skills, and hardening JD→graph node link coverage and utilization scorer wiring.

> **plan_id discipline**: markers use `plan=skills-graph-hardening-gap-closure-53576c`

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: TODO
CURRENT_WAVE: W0
LAST_COMPLETED_WAVE: NONE
LAST_UPDATED: 2026-05-27

---

## Context (SCQA)

- **Situation** — The `apps_rg` pipeline selects skills from `master_skills_arsenal_ledger.json` (236 nodes, 1 400 edges, 162 skill rows) and passes facts to the LLM as grounding evidence. Each run produces `graph_selection_rationale.json` (GSR) and `native_c03_final_evidence.json` (C03) artifacts that report selection counts and admitted facts. The Brown & Brown SVP IT Strategy run was the most recent full-run exercise of this pipeline.
- **Complication** — Six hardening gaps were identified from that run:
  1. No automated signal connects a resume run back to the graph when a skill is needed but missing — gap detection is entirely manual.
  2. No CI gate enforces a minimum `allowed_fact_count / selected_skill_count` ratio per section; funnel collapse (20 skills → 7 facts) is undetected.
  3. 56 DRAFT skills in the graph have empty `fact_id_links` — they cannot surface in resume output.
  4. JD keyword → graph node link coverage is untested; `jd_only_or_empty_fact_id_links` failures are invisible until post-run inspection.
  5. The utilization scorer (`score_graph_skills_utilization`) is isolated — its output does not feed a hard gate.
  6. C0.3 dynamic graph traversal is `BLOCKED` (D16 plan), so the graph acts as a static pre-filter rather than a live context injector.
- **Question** — How do we close the loop so that skills discovered as missing during a run are captured, triaged, and promoted into the graph — and that degradation in graph grounding is caught by CI before runs reach the LLM?
- **Answer** — Build a post-run gap detector script, enforce section-specific ratio floors as contract gates, triage DRAFT skills with human confirmation, and harden JD→node and scorer wiring in four sequential waves.

---

## Status Tables

> Placement: required at top, before Wave detail sections.

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|-----------------|
| W1 | W1.1–W1.2 | Post-run gap detector script | ~18K | Artifact schema stable (GSR + C03) | 🔲 TODO | `detect_graph_skill_gaps.py` produces `candidate_skill_gap_report.json`; pytest passes |
| W2 | W2.1–W2.2 | Per-section ratio floor CI gates | ~14K | Section list from prior run (7 sections) | 🔲 TODO | Contract gate passes on healthy runs; fails on injected regression |
| W3 | W3.1–W3.2 | DRAFT skill triage + activation | ~20K | Human confirms eligible DRAFTs | 🔲 TODO | ≥10 DRAFT→ACTIVE_CONFIRMED promotions; graph SQLite rematerialized |
| W4 | W4.1–W4.3 | JD→node coverage + scorer gate + D16 scoping | ~16K | D16 may split to separate plan | 🔲 TODO | JD coverage contract test green; scorer gate wired; D16 scoped |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W1.1 | Build `detect_graph_skill_gaps.py` | 🔲 TODO |
| W1.2 | Unit tests for gap detector | 🔲 TODO |
| W2.1 | Implement ratio floor constants + section map | 🔲 TODO |
| W2.2 | Contract gate `test_graph_fact_skill_ratio_floors.py` | 🔲 TODO |
| W3.1 | DRAFT skill triage — fact-link + human confirm | 🔲 TODO |
| W3.2 | Reharden + rematerialize SQLite + smoke run | 🔲 TODO |
| W4.1 | JD keyword → graph node coverage contract test | 🔲 TODO |
| W4.2 | Utilization scorer hard gate wiring | 🔲 TODO |
| W4.3 | D16 C0.3 unblock — scope + author-gate | 🔲 TODO |

---

## Out of Scope

- Changing the schema of `master_skills_arsenal_ledger.json` beyond adding skill rows and fact links.
- Modifying `agentic_core` without explicit author-gate (D16 C0.3 unblock will require one if executed in W4).
- Adding new JD targeting files (Brown & Brown exec variants are already on disk).
- Automated LLM-driven skill extraction from resume text — W3 triage is human-confirmed only.

---

## Wave 1 — Post-Run Gap Detector

WAVE_ID: W1
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

**Authorization**: NOT_REQUIRED — new file in `apps_rg/fact_inventory/`, no shared surface modification.

**Phases**:
- **W1.1** — Build `detect_graph_skill_gaps.py` | ~10K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W1.2** — Unit tests for gap detector | ~8K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- `python apps_rg/fact_inventory/detect_graph_skill_gaps.py --artifact-dir <run_dir>` exits 0, produces `candidate_skill_gap_report.json`.
- Report fields: `jd_rejected_skills`, `draft_skills_matching_jd`, `uncited_fact_ids`, `suggested_fact_links`.
- All unit tests pass.

---

## Wave 2 — Per-Section Ratio Floor CI Gates

WAVE_ID: W2
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: B

**Authorization**: NOT_REQUIRED — new contract test file; no production code change.

**Phases**:
- **W2.1** — Ratio floor constants + section map | ~6K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W2.2** — Contract gate `test_graph_fact_skill_ratio_floors.py` | ~8K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Proposed floors (empirically derived from session analysis)**:

| Section | GSR floor (`allowed_fact_count / selected_skill_count`) | C03 floor (`selected_source_fact_ids / selected_skill_count`) | Rationale |
|---------|----|----|-----------|
| `executive_summary` | 0.40 | 0.25 | High-stakes; 20 skills observed, 11/7 facts — floor set to detect >50% funnel collapse |
| `competencies` | 0.35 | 0.20 | Competency bullets are breadth-first; facts are thinner per skill by design |
| `headline` | 0.50 | 0.35 | Headline is short but must be strongly grounded; low skill count makes ratio meaningful |
| `ibm_bullets` | 0.40 | 0.25 | IBM STAR bullets need proof claims; same as exec_summary |
| `ibm_narrative` | 0.45 | 0.30 | Narrative sections use fewer skills but more facts per skill |
| `unify_bullets` | 0.40 | 0.25 | Mirrors ibm_bullets pattern |
| `unify_narrative` | 0.45 | 0.30 | Mirrors ibm_narrative pattern |

**Acceptance**:
- `pytest tests/_apps_contract/test_graph_fact_skill_ratio_floors.py -v` green on a healthy run artifact.
- Same test FAILS when artifact injected with a collapsed ratio (regression proof).
- Floors stored as constants in `apps_rg/runtime/graph/ratio_floor_policy.py` — importable, not hardcoded in test.

---

## Wave 3 — DRAFT Skill Triage + Activation

WAVE_ID: W3
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: HUMAN_REQUIRED
CHECKPOINT: C

**Authorization**: HUMAN_REQUIRED — operator archive promotion requires `human_confirmed_by` on each promoted skill. No code path allows auto-promotion. Execute W3.1 output as a human-review checklist before W3.2.

**Phases**:
- **W3.1** — DRAFT skill audit + fact-link candidates report | ~12K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W3.2** — Apply promotions + reharden + rematerialize | ~8K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**W3.1 Output** — `docs/reports/apps_rg/draft_skill_triage_report_<date>.md` with:
- 56 DRAFT skills listed with `support_level`, `fact_id_links`, `pillar`
- Suggested existing candidate fact IDs that could anchor each DRAFT skill
- 3-column decision: `PROMOTE | DEFER | BLOCK` for each

**W3.2 Steps** (after human sign-off on W3.1):
1. Write `apply_draft_skill_promotions_<date>.py` following `apply_commercial_skills_expansion.py` pattern
2. Run `python apps_rg/fact_inventory/harden_augmented_skills_graph_ssot.py`
3. Run `python apps_rg/fact_inventory/run_materialize_augmented_skills_graph_sqlite.py`
4. Smoke-run pipeline on a short targeting config; confirm new skills appear in `graph_selection_rationale.json`

**Acceptance**:
- ≥10 DRAFT skills promoted to `ACTIVE_CONFIRMED` with `fact_id_links` non-empty.
- `graph_metadata.node_count` increases; no duplicate edges emitted.
- Pipeline smoke run exits cleanly; promoted skills appear in `selected_skill_ids`.

---

## Wave 4 — JD→Node Coverage + Scorer Gate + D16 Scoping

WAVE_ID: W4
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: AUTHOR_GATE_REQUIRED_FOR_W4.3
CHECKPOINT: D

**Authorization**: W4.1 and W4.2 — NOT_REQUIRED (new tests + wiring in `apps_rg`). W4.3 (D16 C0.3 unblock) — AUTHOR_GATE_REQUIRED if it touches `agentic_core`; emit packet before editing.

**Phases**:
- **W4.1** — JD keyword → graph node link coverage contract test | ~5K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W4.2** — Utilization scorer hard gate wiring | ~6K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W4.3** — D16 C0.3 dynamic graph traversal: scope analysis + author-gate | ~5K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**W4.1 Spec**: `test_jd_graph_node_coverage.py` reads `graph_selection_rationale.json::jd_only_admission_checks` and asserts `admitted_count / total_jd_checks >= 0.80`. Fails if JD inferred skills consistently can't resolve to graph nodes.

**W4.2 Spec**: `score_graph_skills_utilization` return value should feed a soft gate (warning) in the post-generation receipt. Add `graph_utilization_score` key to `token_budget_receipt.json` or equivalent receipt; assert non-None in contract test.

**W4.3 Spec**: Audit `R3_SIMPLE_GROUNDED_READ` vs hop-traversal route decision. If unblocking requires only `apps_rg` changes, proceed in-wave. If it requires `agentic_core` edits, emit SPLIT_TO_NEW_PLAN.

**Acceptance**:
- JD coverage contract test green on a healthy run.
- `graph_utilization_score` key present in post-generation receipt.
- D16 scoping decision documented in this plan with ACCEPTED or SPLIT_TO_NEW_PLAN marker.

---

## Execution Details

### W1.1 — Build `detect_graph_skill_gaps.py`

**Scope**: New script at `apps_rg/fact_inventory/detect_graph_skill_gaps.py`

**Inputs**:
- `graph_selection_rationale.json` — `jd_only_admission_checks`, `selected_skill_ids`
- `native_c03_final_evidence.json` — `selected_source_fact_ids`
- `master_skills_arsenal_ledger.json` — DRAFT skills, `allowed_phrases`
- Resume display text (optional) — uncited phrase detection

**Output**: `candidate_skill_gap_report.json`
```json
{
  "jd_rejected_skills": [{"skill_id": "...", "reason_code": "...", "jd_context": "..."}],
  "draft_skills_matching_jd": [{"skill_id": "...", "overlap_phrases": [...], "missing_fact_links": true}],
  "uncited_fact_ids": ["fact_xxx", "..."],
  "suggested_fact_links": [{"rejected_skill_id": "...", "candidate_fact_id": "...", "match_reason": "..."}]
}
```

**Commands**:
```bash
python apps_rg/fact_inventory/detect_graph_skill_gaps.py \
  --artifact-dir artifacts/apps_rg/runtime_proofs/<run_id>/lanes/executive_summary \
  --output artifacts/apps_rg/runtime_proofs/<run_id>/candidate_skill_gap_report.json
```

### W1.2 — Unit Tests for Gap Detector

**Scope**: `tests/unit/apps_rg/fact_inventory/test_detect_graph_skill_gaps.py`

Tests:
- Fixture with a known-bad GSR (jd_only_or_empty_fact_id_links reason) → asserts entry in `jd_rejected_skills`
- Fixture with DRAFT skill whose `allowed_phrases` overlap JD text → asserts entry in `draft_skills_matching_jd`
- Fixture with C03 facts not in output text → asserts `uncited_fact_ids` populated
- Happy path: clean run → all lists empty or minimal

### W2.1 — Ratio Floor Constants

**Scope**: `apps_rg/runtime/graph/ratio_floor_policy.py` (new file)

```python
SECTION_GSR_FLOORS: dict[str, float] = {
    "executive_summary": 0.40,
    "competencies":      0.35,
    "headline":          0.50,
    "ibm_bullets":       0.40,
    "ibm_narrative":     0.45,
    "unify_bullets":     0.40,
    "unify_narrative":   0.45,
}

SECTION_C03_FLOORS: dict[str, float] = {
    "executive_summary": 0.25,
    "competencies":      0.20,
    "headline":          0.35,
    "ibm_bullets":       0.25,
    "ibm_narrative":     0.30,
    "unify_bullets":     0.25,
    "unify_narrative":   0.30,
}
```

### W2.2 — Contract Gate

**Scope**: `tests/_apps_contract/test_graph_fact_skill_ratio_floors.py`

Logic:
```python
from apps_rg.runtime.graph.ratio_floor_policy import SECTION_GSR_FLOORS, SECTION_C03_FLOORS

def test_gsr_ratio_floor(section_name, gsr_artifact):
    floor = SECTION_GSR_FLOORS.get(section_name, 0.25)
    ratio = gsr_artifact["allowed_fact_count"] / gsr_artifact["selected_skill_count"]
    assert ratio >= floor, f"GSR ratio {ratio:.2f} < floor {floor} for {section_name}"

def test_c03_ratio_floor(section_name, c03_artifact):
    floor = SECTION_C03_FLOORS.get(section_name, 0.20)
    ratio = len(c03_artifact["selected_source_fact_ids"]) / c03_artifact["selected_skill_count"]
    assert ratio >= floor, f"C03 ratio {ratio:.2f} < floor {floor} for {section_name}"
```

---

## Gap Register

**GAP-1: No post-run feedback loop from resume run to graph**
- Current: manual inspection of 4 JSON files required to identify missing skills
- Impact: HIGH — skills discovered by the LLM that aren't in the graph are never systematically captured
- Resolution: W1 `detect_graph_skill_gaps.py`

**GAP-2: No CI gate on fact-to-skill ratio**
- Current: funnel collapse (20 skills → 7 facts) is invisible until post-run artifact inspection
- Impact: HIGH — graph grounding can degrade without alert
- Resolution: W2 contract gates

**GAP-3: 56 DRAFT skills with empty fact_id_links**
- Current: 56 skills in graph cannot surface in resume output; many cover actuarial/risk domain
- Impact: MEDIUM — domain coverage loss for actuarial and early-career roles
- Resolution: W3 triage

**GAP-4: JD keyword → graph node link coverage untested**
- Current: `jd_only_or_empty_fact_id_links` failures visible only in GSR artifact
- Impact: MEDIUM — JD-named skills consistently failing admission = graph staleness signal
- Resolution: W4.1

**GAP-5: Utilization scorer isolated**
- Current: `score_graph_skills_utilization` runs but output does not feed a gate
- Impact: MEDIUM — model may generate claims that don't cite any selected fact; this goes undetected
- Resolution: W4.2

**GAP-6: C0.3 dynamic graph traversal blocked (D16)**
- Current: `R3_SIMPLE_GROUNDED_READ` route means graph does 0-hop injection; 1-2 hop neighbors unused
- Impact: HIGH (long-term) — graph edge structure is wasted; richer context remains unavailable to the LLM
- Resolution: W4.3 scoping → likely SPLIT_TO_NEW_PLAN

---

## Definition of Done

DoD-1: Post-run gap detector runs without error on any prior run artifact directory.
- Evidence: `python apps_rg/fact_inventory/detect_graph_skill_gaps.py --artifact-dir <dir>` exits 0, `candidate_skill_gap_report.json` produced.
- Status: TODO

DoD-2: Ratio floor contract gates are green on a healthy run artifact and red on an injected regression.
- Evidence: `pytest tests/_apps_contract/test_graph_fact_skill_ratio_floors.py -v` — all pass; re-run with patched fixture shows failure.
- Status: TODO

DoD-3: ≥10 DRAFT skills promoted to ACTIVE_CONFIRMED with non-empty `fact_id_links`.
- Evidence: `python apps_rg/fact_inventory/harden_augmented_skills_graph_ssot.py` receipt shows `promoted ≥ 10`; `activation_status == ACTIVE_CONFIRMED` count increases.
- Status: TODO

DoD-4: Graph SQLite rematerialized and pipeline smoke-run exits clean.
- Evidence: `python -m apps_rg --target-company "Brown & Brown" ...` exits 0 on exec JD variant; promoted skills appear in `graph_selection_rationale.json::selected_skill_ids`.
- Status: TODO

DoD-5: Zero new pytest regressions across the unit + contract suite.
- Evidence: `pytest tests/unit/apps_rg tests/_apps_contract -q` — pass count ≥ baseline, 0 failures.
- Status: TODO

DoD-6: D16 C0.3 disposition documented (ACCEPTED in-plan or SPLIT_TO_NEW_PLAN).
- Evidence: `AUTHORIZATION_DECISION:` marker emitted in W4.3 execution.
- Status: TODO

DoD-7: Memory + Notion writebacks complete.
- Evidence: Memory entity `skills_graph_hardening` updated; Notion Plans DB row status = `Completed`.
- Status: TODO

---

## Verification vs Deferral

| Item | Verification required before PASS | Can be deferred? |
|------|-----------------------------------|-----------------|
| Gap detector smoke run | Yes — must run on real artifact | No |
| Ratio floor contract test (fail case) | Yes — must show red on injected regression | No |
| DRAFT skill count ≥10 | Yes — harden receipt required | No |
| C0.3 unblock execution | No — W4.3 is scoping only | Yes — D16 SPLIT acceptable |
| Scorer gate in production receipt | Soft gate (warning) acceptable for W4 | Yes — hard gate is W5 scope |

---

## Scope Expansion Authorization

When scope is discovered during execution, emit markers in order:

```
DISCOVERED_SCOPE: plan=skills-graph-hardening-gap-closure-53576c wave=<N> phase=<M> gap="<what>" impact="<severity>"
AUTHORIZATION_DECISION: plan=skills-graph-hardening-gap-closure-53576c decision=<ACCEPTED|DEFERRED|SPLIT_TO_NEW_PLAN|REJECTED> authorized_by=<user|author_gate|self> decisive_reason="<why>"
SCOPE_EXPANSION: plan=skills-graph-hardening-gap-closure-53576c reason="<summary>" added="<waves/phases>" authorized="yes"
```

---

## Marker Quick Reference

```
WAVE_START: plan=skills-graph-hardening-gap-closure-53576c wave=<N>
WAVE_COMPLETE: plan=skills-graph-hardening-gap-closure-53576c wave=<N> note="+N tests, N files, scope=<summary>"
PHASE_COMPLETE: plan=skills-graph-hardening-gap-closure-53576c phase=<W1.1>
PLAN_COMPLETE: plan=skills-graph-hardening-gap-closure-53576c note="<final outcome>"
```
