---
plan_id: briefing-jd-c0-enhancements-ee0b1d
plan_type: refactor
touches_agentic_core: false
touches_governance_ci: false
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# Briefing / JD → C0.3 Enhancements (F1–F6)

Six targeted improvements to the briefing and JD data-flow path in apps_rg, from
U0 ingress through C0.3 graph targeting and cross-section X2 coherence.

> **plan_id discipline**: markers use `plan=briefing-jd-c0-enhancements-ee0b1d`.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: COMPLETED
CURRENT_WAVE: W4
LAST_COMPLETED_WAVE: W4
LAST_UPDATED: 2026-05-27

---

## Context (SCQA)

- **Situation** — `apps_rg` resolves the JD and briefing from U0 → `jd_resolution.py` /
  `briefing_resolution.py` → `ModularLaneTargeting` → C0 retrieval → C0.3 graph ref policy
  → Prompt Assembly. The spine is functional and the contract `jd_used_as_proof=False` /
  `briefing_used_as_proof=False` is enforced.

- **Complication** — Six gaps were identified during a structural audit:  (F1) the
  briefing's company-specific signals never reach C0.3 pillar ranking; (F2) DEFAULT_SSOT
  JD fallback is invisible at U0; (F3) `briefing_hash` is hardcoded `""` in section
  evidence traces; (F4) C0.3 targeting degradation fires silently with no gate; (F5) the
  C0.1 JD excerpt is naively truncated at 240 chars; (F6) sections compute graph targeting
  independently with no cross-section coherence check.

- **Question** — How do we close these six gaps without weakening the existing proof-authority
  contracts?

- **Answer** — Four waves of additive changes: (W1) four low-effort plumbing fixes, (W2)
  briefing supplement into C0.3 pillar hints, (W3) cross-section pillar coherence X2 gate,
  (W4) test suite clean + commit + GitHub sync.

---

## Status Tables

### Wave Progress

| Wave | Focus | Status | Tests Added | Files Changed |
|------|-------|--------|-------------|---------------|
| W1 | Low-effort plumbing: F2 jd_targeting_mode, F3 briefing_hash, F4 degradation gate, F5 excerpt | ✅ DONE | 11 | 5 |
| W2 | F1 briefing targeting supplement into C0.3 pillar hints | ✅ DONE | 7 | 1 |
| W3 | F6 cross-section pillar coherence X2 gate | ✅ DONE | 10 | 1 |
| W4 | Full test run + commit + GitHub push + plan/Notion closeout | ✅ DONE | — | — |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W1.1 | F2 — jd_targeting_mode in U0 query_spec + jd_resolution WARNING | ✅ DONE |
| W1.2 | F3 — briefing_hash wired in _build_section_evidence_trace() | ✅ DONE |
| W1.3 | F4 — TARGETING_DEGRADED gate verdict in resolve_role_family_projection() | ✅ DONE |
| W1.4 | F5 — smarter jd_text_excerpt in build_c01_retrieval_plan() | ✅ DONE |
| W2.1 | F1 — extract_briefing_targeting_supplement() + augment pillar hints | ✅ DONE |
| W2.2 | F1 — unit tests for briefing supplement path | ✅ DONE |
| W3.1 | F6 — check_cross_section_pillar_coherence() in cross_section_x2.py | ✅ DONE |
| W3.2 | F6 — unit tests for coherence gate | ✅ DONE |
| W4.1 | Run full test suite, assert zero regressions | ✅ DONE |
| W4.2 | Commit + push to GitHub + Notion/plan closeout | ✅ DONE |

---

## Out Of Scope

- Changing `jd_used_as_proof` or `briefing_used_as_proof` from False to True
- Any agentic_core modifications
- Modifying `apps_rg/config/default_jd_targeting.txt` or `default_targeting_briefing.txt`
- LLM prompt template changes
- F6 coherence gate blocking generation (WARN only, never hard-stop)

---

## Wave 1 — Low-Effort Plumbing Fixes

WAVE_ID: W1
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

**Authorization**: NOT_REQUIRED — all changes are additive, no proof authority altered.

**Phases**:
- **W1.1** — F2: jd_targeting_mode in U0 + jd_resolution warning | ~3K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W1.2** — F3: briefing_hash wired in evidence trace | ~2K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W1.3** — F4: TARGETING_DEGRADED gate + logger.warning | ~2K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W1.4** — F5: smarter jd_text_excerpt | ~2K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- `u0_validate_apps_rg()` produces `query_spec["jd_targeting_mode"]` in `validated_app_payload`
- `jd_resolution.resolve_jd_for_lanes()` emits `logger.warning` when `source == JdSource.DEFAULT_SSOT`
- `SectionEvidenceTrace.briefing_hash` is non-empty when briefing_digest is available
- `resolve_role_family_projection()` returns a `TARGETING_DEGRADED` gate verdict when `targeting_degraded_explicit=True`
- `build_c01_retrieval_plan()` uses keyword-anchored excerpt for JDs > 300 chars

---

## Wave 2 — Briefing Targeting Supplement

WAVE_ID: W2
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: B

**Phases**:
- **W2.1** — extract_briefing_targeting_supplement() + merge into graph_targeting | ~4K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W2.2** — Unit tests for briefing supplement path | ~3K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- `merge_graph_targeting_jd_alignment()` accepts optional `briefing_text` kwarg
- `briefing_targeting_supplement` dict is present in `graph_targeting` block when `briefing_source == RUN_SPECIFIC`
- `briefing_used_as_proof=False` remains enforced — supplement augments pillar hints only
- Tests: supplement is empty when `briefing_text` is empty; populated when non-empty

---

## Wave 3 — Cross-Section Pillar Coherence Gate

WAVE_ID: W3
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: C

**Phases**:
- **W3.1** — check_cross_section_pillar_coherence() in cross_section_x2.py | ~4K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W3.2** — Unit tests for coherence gate | ~3K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- `check_cross_section_pillar_coherence(sections)` returns `CrossSectionGateResult`
- Jaccard similarity < 0.4 across any two primary sections → verdict WARN
- Missing pillar data → verdict UNKNOWN (never hard-fail)
- Gate never blocks generation (advisory only)
- Tests cover PASS / WARN / UNKNOWN scenarios

---

## Wave 4 — Test Suite + Commit + GitHub Sync

WAVE_ID: W4
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: D

**Phases**:
- **W4.1** — Run full pytest on apps_rg test surface | ~2K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W4.2** — git commit + push + Notion/plan closeout | ~1K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- All pre-existing tests pass; zero regressions
- Commit message references plan slug
- Notion Plans row Status = Completed
- `PLAN_COMPLETE:` marker emitted

---

## Execution Details

### W1.1 — F2: jd_targeting_mode at U0

**Scope**: `apps_rg/runtime/bindings/u0_binding.py` + `apps_rg/runtime/jd_resolution.py`

Add `jd_targeting_mode` field to `query_spec` in `u0_validate_apps_rg()`:
- `"RUN_SPECIFIC"` when `job_description_text` / `job_description_ref` / `jd_data` is non-empty
- `"DEFAULT_SSOT"` otherwise

In `jd_resolution.py`, add `logger.warning("jd targeting DEFAULT_SSOT: …")` when `source == JdSource.DEFAULT_SSOT`.

**Tests**: extend `tests/unit/apps_rg/test_u0_jd_no_io.py` + `test_jd_resolution.py`.

### W1.2 — F3: briefing_hash in evidence trace

**Scope**: `apps_rg/runtime/bindings/c0_binding.py` → `_build_section_evidence_trace()`

Add `briefing_hash` computation from `app_payload.get("briefing", {}).get("briefing_digest", "")`.
Pass through as `briefing_hash=` argument to `SectionEvidenceTrace`.

**Tests**: extend `tests/unit/apps_rg/test_u0_briefing_no_io.py` (or new `test_c0_evidence_trace.py`).

### W1.3 — F4: TARGETING_DEGRADED gate in C0.3

**Scope**: `apps_rg/runtime/c0/c03_graph_ref_policy.py` → `resolve_role_family_projection()`

When `targeting_degraded_explicit=True`, add a `targeting_degraded_gate` key to the return dict
with value `{"gate_id": "TARGETING_DEGRADED", "verdict": "WARN", "projection_source": <value>}`.
Add `logger.warning("C0.3 targeting degraded: …")`.

**Tests**: new `tests/unit/apps_rg/test_c03_graph_ref_policy_degradation.py`.

### W1.4 — F5: smarter jd_text_excerpt

**Scope**: `apps_rg/runtime/c0/c01_retrieval_plan.py` → `build_c01_retrieval_plan()`

Replace `jd_text[:240]` with `_smart_jd_excerpt(jd_text)` helper:
scan for first occurrence of `["required", "responsibilities", "you will", "qualifications", "skills"]`
(case-insensitive); start excerpt there. Fall back to `[:240]` if no marker found.
Output bounded at 300 chars.

**Tests**: extend existing c01 tests or add `test_c01_retrieval_plan.py`.

### W2.1 — F1: briefing targeting supplement

**Scope**: `apps_rg/runtime/c0/c03_graph_ref_policy.py` → `merge_graph_targeting_jd_alignment()`

Add `extract_briefing_targeting_supplement(briefing_text: str) -> list[str]` helper:
tokenize briefing_text, return known pillar-adjacent terms (AI, cloud, governance, etc.)
up to 5 terms. Gated: only when `briefing_source == "RUN_SPECIFIC"` (not DEFAULT_SSOT).

Merge returned terms into `graph_targeting["briefing_targeting_supplement"]` (list, may be empty).
Never promote to `targeting_graph_refs` directly — supplement is informational only.

### W2.2 — F1 tests

**Tests**: new `tests/unit/apps_rg/test_c03_briefing_targeting_supplement.py`.

### W3.1 — F6: cross-section pillar coherence gate

**Scope**: `apps_rg/runtime/aggregation/cross_section_x2.py`

Add `check_cross_section_pillar_coherence(sections: list[dict]) -> CrossSectionGateResult`.
- Extract `targeting_graph_refs` from each section's C0.3 graph block
- Compute pairwise Jaccard over primary sections (executive_summary, competencies, bullets/narrative)
- Verdict PASS if min similarity ≥ 0.4; WARN if < 0.4; UNKNOWN if pillar data missing

### W3.2 — F6 tests

**Tests**: new `tests/unit/apps_rg/test_cross_section_pillar_coherence.py`.

---

## Definition of Done

DoD-1: All six findings (F1–F6) implemented as described in Execution Details.
- Evidence: all changed files listed in `git diff --name-only HEAD` after W3 completion
- Status: TODO

DoD-2: No regression in existing test suite.
- Evidence: `pytest tests/unit/apps_rg/ tests/_apps_contract/ -x --tb=short` exits 0
- Status: TODO

DoD-3: New tests cover all new paths.
- Evidence: `pytest tests/unit/apps_rg/ -v --tb=short` shows ≥ 15 new test pass lines
- Status: TODO

DoD-4: `jd_used_as_proof=False` and `briefing_used_as_proof=False` remain enforced.
- Evidence: `rg "jd_used_as_proof.*True\|briefing_used_as_proof.*True" apps_rg/` returns empty
- Status: TODO

DoD-5: Plan and Notion status = Completed. Commit on main/feature branch pushed to GitHub.
- Evidence: `git log --oneline -1` shows commit with plan slug; Notion page Status=Completed
- Status: TODO

---

## Gap Register

**GAP-1**: `briefing_digest` may not be present in `app_payload["briefing"]` at the `c0_binding.py` call site — depends on whether modular lane adapter populates it.  
- Impact: medium; if absent, `briefing_hash` stays `""` gracefully — no breakage.  
- Mitigation: W1.2 reads with `.get("briefing_digest", "")` — fail-soft.

**GAP-2**: `SectionEvidenceTrace.briefing_hash` field must exist on the dataclass.  
- Impact: compile-time error if missing.  
- Mitigation: inspect dataclass definition before W1.2 edit; add field if absent.

---

## Scope Expansion Authorization

When scope is discovered during execution, emit markers in order:

```
DISCOVERED_SCOPE: plan=briefing-jd-c0-enhancements-ee0b1d wave=<N> phase=<M> gap="<what>" impact="<severity>"
AUTHORIZATION_DECISION: plan=briefing-jd-c0-enhancements-ee0b1d decision=<ACCEPTED|DEFERRED|...> authorized_by=<user|author_gate|self> decisive_reason="<why>"
SCOPE_EXPANSION: plan=briefing-jd-c0-enhancements-ee0b1d reason="<summary>" added="<waves/phases>" authorized="yes"
```
