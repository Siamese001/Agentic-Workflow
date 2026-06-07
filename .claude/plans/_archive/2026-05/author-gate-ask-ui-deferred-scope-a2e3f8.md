# Author-Gate / ask_user_question UI — Deferred Scope

**Plan ID:** `author-gate-ask-ui-deferred-scope-a2e3f8`  
**Status:** Not Started  
**Tier:** T2  
**Parent:** author-gate-ask-ui-consolidated-a1e3f7  
**Created:** 2026-05-10

---

## 1. Scope Origin

This plan captures deferred scope from `author-gate-ask-ui-consolidated-a1e3f7` that was identified during rebaseline and implementation but explicitly postponed.

---

## 2. Deferred Items

### D1: Integration Test Suite

**Gap:** End-to-end integration tests for the full harmonization pipeline were identified but not implemented.

**Required:**
- `tests/integration/test_author_gate_ask_harmonization.py`
- Tests covering:
  - Full pipeline: context detection → routing → enrichment → telemetry → ledger
  - CLI stdin/stdout integration
  - Hook chain integration with actual Windsurf execution
  - Multi-option edge cases (0, 1, 5+ options)

**Effort:** ~2k tokens  
**Priority:** P2 — Not blocking core functionality

---

### D2: ADG Blast Radius Real Integration

**Gap:** `heuristic_scorer.py` uses fail-soft fallback when ADG unavailable. Real ADG integration needs implementation.

**Required:**
- Remove fallback mode in `_query_adg_blast_radius()`
- Use actual `tools.adg.core.sqlite_adg.get_blast_radius()`
- Add caching for repeated queries
- Handle edge cases: new files (not in ADG), deleted files

**Effort:** ~1.5k tokens  
**Priority:** P2 — Enhancement, heuristic default works

---

### D3: Precedent Lookup Integration

**Gap:** Heuristic scorer has placeholder precedent scoring (fixed 0.72). Real precedent lookup needed.

**Required:**
- Query `refactor_decision_ledger.sqlite` for similar past decisions
- Use `skill/refactor-decision-memory/lookup_refactor_decisions.py`
- Match on: decision_type, context similarity, files touched
- Return precedent-based confidence adjustment

**Effort:** ~2k tokens  
**Priority:** P3 — Meta-learning enhancement

---

### D4: Pre-Hook Registration in hooks.json

**Gap:** `pre_ask_user_question_gate.py` exists but not registered in Windsurf hook system.

**Required:**
- Add entry to `.cursor/hooks.json`:
  ```json
  {
    "id": "pre_ask_user_question",
    "command": "python .cursor/scripts/pre_ask_user_question_gate.py",
    "timing": "pre_user_prompt",
    "show_output": false
  }
  ```
- Validate hook runs correctly in actual Windsurf sessions
- Handle edge cases: stdin timeout, malformed input

**Effort:** ~1k tokens  
**Priority:** P1 — Required for automatic routing

---

### D5: Production Telemetry Validation

**Gap:** No production validation that telemetry packets are actually being captured.

**Required:**
- Add metrics emission to ledger operations
- Create dashboard/query for ASK_USER_QUESTION_PACKET counts
- Alert on packet absence (vacuum-closure violation)
- Weekly report: % of decisions with telemetry

**Effort:** ~1.5k tokens  
**Priority:** P2 — Observability hardening

---

### D6: Heuristic Scorer Calibration

**Gap:** Scorer weights are theoretical defaults. Empirical calibration needed.

**Required:**
- Run scorer on historical decisions with known outcomes
- Compare predicted confidence vs actual success rate
- Adjust weights to minimize prediction error
- Wilson CI bounds for confidence calibration

**Effort:** ~2k tokens  
**Priority:** P3 — Quality improvement

---

## 3. Non-Goals

- No changes to core routing logic (tested and working)
- No changes to UI invariant schema
- No changes to ledger schema (additive only)
- No breaking changes to existing API

---

## 4. Success Criteria

| # | Criterion | Priority |
|---|-----------|----------|
| D1 | Integration tests pass in CI | P2 |
| D2 | ADG integration live, no fallback mode | P2 |
| D3 | Precedent lookup returns real matches | P3 |
| D4 | Hook registered and running in production | P1 |
| D5 | Telemetry validation dashboard live | P2 |
| D6 | Scorer calibration report available | P3 |

---

## 5. Dependencies

- D2 requires: ADG snapshot healthy (already operational)
- D3 requires: refactor_decision_ledger has sufficient history
- D4 requires: Windsurf hook system available
- D5 requires: D4 complete (hook running)

---

## 6. Implementation Order

**Phase 1 (High Priority):**
- D4: Hook registration (unblocks automatic routing)

**Phase 2 (Medium Priority):**
- D1: Integration tests (validates end-to-end)
- D2: ADG real integration (improves accuracy)

**Phase 3 (Lower Priority):**
- D3: Precedent lookup (meta-learning)
- D5: Telemetry validation (observability)
- D6: Calibration (quality)

---

*Deferred from author-gate-ask-ui-consolidated-a1e3f7 implementation, 2026-05-10.*
