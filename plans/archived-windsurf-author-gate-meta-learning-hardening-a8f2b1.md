---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\author-gate-meta-learning-hardening-a8f2b1.md'
original_relative_path: 'author-gate-meta-learning-hardening-a8f2b1.md'
source_sha256: fef843ba2086552169da2778166ccbde952177f6b0464728d1ad7aae683aefde
recovered_status: SURVIVED_IN_CURRENT
last_commit: '153652b9eb3'
last_commit_date: '2026-06-07 06:37:48 -0400'
created_date: '2026-04-24'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Author-Gate Meta-Learning Hardening — End-to-End

- **Plan ID**: `author-gate-meta-learning-hardening-a8f2b1`
- **Tier**: T3 (multiple scripts + hooks + CI gate + schema, single logical subsystem)
- **Owner**: Cursor Agent
- **Created**: 2026-04-24
- **Status**: Active
- **Parent**: follow-up from `author-gate-meta-learning-outcome-wiring-c3e1f7`

## Problem (audit, 2026-04-24 03:45 UTC)

| # | Hole | Metric | Impact |
|---|------|--------|--------|
| 1 | Structured-reasoning fields optional | `user_goal` 24%, `rationale` 24%, `principle` 8%, `confidence_*` 8%, `latency_ms` 5%, `task_id` 0% | Reasoning context lost |
| 2 | `decision_scope` sparse | 32% any scope, 8% `file_path`, 26% `layer` | Binder + injection filtering starved |
| 3 | Orphan executed | 25/37 (68%); 23 unreachable SHAs | Outcome data destroyed by git history mutation |
| 4 | `tests_passed=1` | 0 rows ever | Classifier can't see green test signal |
| 5 | **Injection not wired** | `pre_author_gate.py` does not call lookup skill | Precedent stored but never used |
| 6 | Promotion cadence | Manual only | Precedent decays silently |
| 7 | Exit criteria JSON | No column, no validator | Success criteria unchecked |
| 8 | Coverage CI gate | None | Ledger can rot without alarm |
| 9 | Hash-chain verify | Written but not verified at read | Tamper-invisible |
| 10 | `task_id` linkage | 0/38 | No plan/Notion cross-ref |

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|------|-----------|-------|-------------|--------|------------------|
| **W1** | W1.1–W1.3 | Capture grammar + required-field audit + scope auto-emit | 6000 | Todo | Every new DECISION_CAPTURED marker rejects w/ clear error if any required field missing; decision_scope row auto-written from marker area + cwd |
| **W2** | W2.1–W2.2 | Injection: pre_author_gate auto-consults lookup + attaches PRECEDENT block | 5000 | Todo | Next Author-Gate packet shows precedent inline when ledger has matches |
| **W3** | W3.1–W3.3 | Binding resilience: capture-time scope inference, tests_passed wiring via pytest post-hook, immediate direct-bind | 5000 | Todo | Orphan rate for new decisions drops to <10% within 3 commits of execution |
| **W4** | W4.1–W4.2 | Coverage CI gate + scheduled promotion hook | 4000 | Todo | CI fails if outcome_bind_rate<80% or no promotion run in 14d |
| **W5** | W5.1–W5.2 | Exit criteria JSON schema + verifier + hash-chain verify on read | 4000 | Todo | Every decision has exit_criteria JSON; lookup_refactor_decisions verifies hash chain before returning |

Token budget: 🟢 GREEN (~24k total, spread across 5 independently revertible commits).

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W1.1 | Marker grammar validator | `.windsurf/scripts/post_cascade_author_gate_capture.py`; new `.windsurf/scripts/author_gate_marker_validator.py` | DECISION_CAPTURED marker today tolerates missing fields silently | 2500 | Todo |
| W1.2 | Required-field audit + stats | `.windsurf/scripts/author_gate_ledger_integrity.py` (extend); new CLI `python -m .windsurf.scripts.audit_ledger_coverage` | No visibility into capture completeness | 1500 | Todo |
| W1.3 | Scope auto-emit from marker | `.windsurf/scripts/post_cascade_author_gate_capture.py` | repo_area is captured but never written to decision_scope.file_path | 2000 | Todo |
| W2.1 | Precedent lookup in pre_author_gate | `.windsurf/scripts/pre_author_gate.py`; reads `lookup_refactor_decisions.py` | Lookup skill never called → precedent unused | 3000 | Todo |
| W2.2 | PRECEDENT block in packet header | `.windsurf/rules/author-gate-enforcement.md`; `pre_author_gate.py` writes `AUTHOR_GATE_PRECEDENT` sidecar | Packet shape doesn't include precedent surface | 2000 | Todo |
| W3.1 | Capture-time scope inference | `.windsurf/scripts/post_cascade_author_gate_capture.py` | When marker has `repo_area=X` and X is a real path, emit `decision_scope(file_path=X, layer=infer)` | 2000 | Todo |
| W3.2 | tests_passed signal | new pytest post-plugin in `tests/conftest.py` writing exit outcome into `artifacts/windsurf/last_test_signal.json`; binder reads on next bind | tests_passed=0 always | 2000 | Todo |
| W3.3 | Immediate direct-bind at capture | `post_cascade_author_gate_capture.py` calls `_bind_from_current_head()` inline when `outcome=executed` AND commit_sha is HEAD | Binder runs only on push, loses data to rebases | 1000 | Todo |
| W4.1 | Coverage CI gate | new `ops_scripts/ci/check_ledger_coverage.py`; wire into `.pre-commit-config.yaml` | Ledger rot is silent | 2500 | Todo |
| W4.2 | Scheduled promotion hook | `.git/hooks/post-commit` extension invoking `promote_author_gate_patterns.py` every 10 commits | Manual only | 1500 | Todo |
| W5.1 | Exit criteria JSON | Schema in `.windsurf/schemas/exit_criteria.schema.json`; new column `decisions.exit_criteria_json` (nullable, backfill null); validator | Notion Success Criteria is free text | 2500 | Todo |
| W5.2 | Hash-chain verification on read | `.windsurf/skills/refactor-decision-memory/lookup_refactor_decisions.py` re-verifies chain on returned matches | No runtime tamper detection | 1500 | Todo |

## Execution Order

**W1 + W2 this session (loop closure, highest leverage).** W3–W5 deferred via DEFERRED_SCOPE markers (auto-posted to Notion backlog by post-cascade hook).

## Exit Criteria (plan-level)

- [ ] Capture grammar validator rejects every malformed marker
- [ ] Every new decision has ALL v2 fields populated (audit script ≥95% in next 10 decisions)
- [ ] `pre_author_gate.py` attaches PRECEDENT block to every packet when lookup returns ≥1 match
- [ ] End-to-end regression test: seed ledger → surface Author-Gate → packet contains precedent section
- [ ] Notion Wave/Phase row transitions In Progress → Done

## Reversibility

All five waves are script/hook/schema edits. Revert = single `git revert` per wave. No destructive SQL; new `exit_criteria_json` column is nullable.
