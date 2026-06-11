---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\author-gate-meta-learning-outcome-wiring-c3e1f7.md'
original_relative_path: 'author-gate-meta-learning-outcome-wiring-c3e1f7.md'
source_sha256: 7a9bc42ca9e85938974d68c9aff099587ade08bb0e6d969c7745ec0f5421e563
recovered_status: LOST_RECOVERED
last_commit: '6477883502e'
last_commit_date: '2026-04-27 08:55:24 -0400'
created_date: '2026-04-24'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Author-Gate Meta-Learning Outcome Wiring

- **Plan ID**: `author-gate-meta-learning-outcome-wiring-c3e1f7`
- **Tier**: T2 (3 files, single layer — .windsurf/scripts + skill)
- **Owner**: Cascade
- **Created**: 2026-04-23
- **Status**: Active
- **ADG Provenance**: N/A — scripts only, no production import graph impact
- **Parent**: follow-up from `DEFERRED_SCOPE` captured during FTS5 hyphen-bug fix

## Problem

Author-Gate decisions ARE stored (38 rows in `.windsurf/state/refactor_decisions/refactor_decision_ledger.sqlite`) but the meta-learning loop is broken in three places:

1. **Binder filter mismatch** — `post_commit_outcome_binder.py::unbound_decisions()` selects `WHERE d.status = 'surfaced'`, but `post_cascade_author_gate_capture.py` writes `status='executed'` for every v2 marker where `outcome=executed`. Result: 29/38 decisions have no `decision_outcomes` row.
2. **FTS5 hyphen bug (duplicate of lookup bug)** — `promote_author_gate_patterns.py::_sanitize_fts()` keeps hyphens → `meta-learning` parsed as column filter → `OperationalError: no such column: learning` → silent zero-result sibling search.
3. **No automation** — `promote_author_gate_patterns.py` is only invoked manually; no hook, no schedule. 0 rows have `promote_to_pattern=1` so `verdict: strong` is unreachable.

Net effect: the ledger accumulates decisions but the lookup skill can only ever return `suggestive` (when FTS happens to match) or `none`. The "better inform future refactoring decisions" feedback loop is not closed.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | W1.1–W1.3 | Fix binder + FTS + wire promotion | 4000 | Ledger schema stable; git post-commit hook fires | Todo | Outcomes bound for all 29 executed rows; ≥1 promoted pattern; lookup returns `strong` for a known hyphenated intent |

Token budget: 🟢 GREEN (~4k estimated, well under 64k cap).

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W1.1 | Binder status filter fix | `.windsurf/scripts/post_commit_outcome_binder.py`, `tests/unit/ops_scripts/hooks/windsurf/test_post_commit_outcome_binder.py` (if present) | Recent capture hook writes `status='executed'`; binder only sees `surfaced` → orphan outcomes | 1200 | Todo |
| W1.2 | Promote FTS hyphen fix | `.windsurf/scripts/promote_author_gate_patterns.py` | Same FTS5 column-filter bug as lookup skill | 600 | Todo |
| W1.3 | One-shot backfill + verification | `.windsurf/scripts/post_commit_outcome_binder.py` (run with `--lookback 100`), `promote_author_gate_patterns.py` run, `_probe_outcomes.py` cleanup | Prove meta-learning loop closed end-to-end | 2200 | Todo |

## Execution Steps (W1.1 → W1.2 → W1.3)

### W1.1 — binder status filter
Edit `unbound_decisions()` SQL to `WHERE d.status IN ('surfaced', 'executed')`. Rationale: a row with `status='executed'` but no outcome row is — by definition — an orphan that needs binding; the later outcome-write is idempotent. Update the module docstring MATCH RULE.

### W1.2 — FTS5 hyphen sanitization
Change `_FTS_SAFE_RE` regex in `promote_author_gate_patterns.py` to strip hyphens to space instead of preserving them. Mirrors the fix already applied to `lookup_refactor_decisions.py::_sanitize_fts_query`.

### W1.3 — Backfill + prove loop
1. Run `python .windsurf/scripts/post_commit_outcome_binder.py --lookback 100` to bind the 29 orphans.
2. Run `python .windsurf/scripts/promote_author_gate_patterns.py` to backfill labels + promote eligible patterns.
3. Query ledger: expect `decision_outcomes` count ≥ 30, `promote_to_pattern=1` count ≥ 1.
4. Query lookup skill with a hyphenated intent that has ≥2 matching siblings — expect `verdict: strong`.

## Deferred (NOT in this plan)

- Scheduled promotion cadence (weekly cron / CI gate) — separate scope.
- Hash-chain signature verification in lookup — advisory, low priority.
- FTS logging to stderr instead of silent swallow — incremental observability, not blocking meta-learning.

## Exit Criteria

- [ ] W1.1 edit committed + test compile
- [ ] W1.2 edit committed
- [ ] W1.3 backfill proves ≥1 promotion AND ≥1 `strong` verdict on a hyphenated intent
- [ ] Notion Wave/Phase row updated to Status=Done

## Reversibility

All changes are to scripts only. Revert = single `git revert` of the W1 commits. No schema changes, no destructive SQL.
