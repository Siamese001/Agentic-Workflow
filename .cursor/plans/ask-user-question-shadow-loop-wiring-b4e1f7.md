---
slug: ask-user-question-shadow-loop-wiring-b4e1f7
status: Completed
dod_exempt: false
---

# Ask User Question — Shadow Loop Wiring (Deferred Scope)

**Origin**: Deferred from plan `ask-user-question-test-hardening-a7f2e3` (Completed 2026-05-10).

**Objective**: Wire the `ask_user_question` decision pipeline into the schema-registry LedgerConsulter framework and add a weekly calibration report for recommendation-vs-selection mismatch analysis.

## Deferred Items

### D1: LedgerConsulter Integration for ask_user_question

**What**: Register `ask_user_question` decisions as a first-class `LedgerSpec` in `tools/ledgers/schema_registry.py` so the `LedgerConsulter` class can query precedent from `ask_user_question_decisions` the same way it does for the 20+ existing ledgers.

**Why deferred**: The existing test hardening focused on verifying the build→write→read pipeline works. The LedgerConsulter integration requires a schema SQL file, a consulting skill, and wiring into the registry — a separate scope.

**Files in scope**:
- `tools/ledgers/schema_registry.py` — add `LedgerSpec(name="ask_user_question", ...)`
- `.cursor/schemas/ask_user_question_ledger.schema.sql` — formalize the CREATE TABLE + indexes
- `.cursor/skills/ledger-consulter-ask-user-question/SKILL.md` — consulting skill
- `tools/ledgers/consulter.py` — verify `LedgerConsulter.search()` works with the ask_user_question table
- Tests for the above

### D2: Weekly Calibration Report for Recommendation-vs-Selection Mismatch

**What**: Add an `ops_scripts/calibration/ask_user_question_weekly_report.py` that queries the `ask_user_question_decisions` ledger and reports:
- Total decisions in the window
- Recommendation acceptance rate (selected_index == recommended_index)
- Override rate (selected_index != recommended_index)
- Per-context breakdown
- Confidence calibration curve (binned confidence vs acceptance rate)

**Why deferred**: This is an observability/calibration concern, not a test concern. The shadow loop tests verify the data is correctly persisted; this report consumes it for human analysis.

**Files in scope**:
- `ops_scripts/calibration/ask_user_question_weekly_report.py` — the report generator
- `docs/reports/calibration/ask-user-question/<YYYY-Www>.md` — output location
- Tests for the report generator

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | P1 | LedgerSpec registration + schema SQL | ~4k | Schema registry pattern stable | ✅ DONE | LedgerSpec added, schema applied |
| W2 | P2 | Consulting skill + LedgerConsulter wiring | ~5k | consulter.py supports FTS5 | ✅ DONE | AskUserQuestionConsulter queries ask_user_question_decisions |
| W3 | P3 | Weekly calibration report | ~6k | Sufficient decision history | ✅ DONE | Report generates, acceptance/override rates computed |
| W4 | P4 | Tests + verification | ~3k | No regressions | ✅ DONE | 51 ledger + 17 weekly report tests pass |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| P1 | LedgerSpec + Schema | schema_registry.py, .schema.sql | Must match existing ledger pattern exactly | ~4k | ✅ DONE |
| P2 | Consulting Skill | SKILL.md, consulter.py | AskUserQuestionConsulter adapter added | ~5k | ✅ DONE |
| P3 | Weekly Report | ask_user_question_weekly_report.py | Binned confidence calibration curve logic | ~6k | ✅ DONE |
| P4 | Tests | tests/ | Full integration with existing test surface | ~3k | ✅ DONE |

## Definition of Done

| DoD | Criterion | Status |
|-----|-----------|--------|
| DoD-1 | `ask_user_question` registered in `LEDGER_REGISTRY` and `tools/ledgers/apply_schema.py` succeeds | ✅ DONE |
| DoD-2 | `AskUserQuestionConsulter.lookup()` returns matching precedent rows | ✅ DONE |
| DoD-3 | `python ops_scripts/calibration/ask_user_question_weekly_report.py` exits 0 and produces a Markdown report | ✅ DONE |
| DoD-4 | All new + regression tests pass (51 ledger + 17 weekly = 68 total) | ✅ DONE |
| DoD-5 | Plan + results registered in Notion | ✅ DONE |

## Non-Goals

- Implementing automated confidence adjustment based on mismatch data (that's a future ML concern)
- Changing the enriched_choice_builder behavior — this plan only adds observability
- Modifying the existing shadow loop tests — they are already hardened

## Verification vs Deferral

| Item | Verified This Plan | Deferred |
|------|-------------------|----------|
| LedgerSpec registration | W1 | — |
| Consulting skill | W2 | — |
| Weekly report | W3 | — |
| Automated confidence recalibration | — | Future: ML-driven confidence adjustment based on mismatch trends |
