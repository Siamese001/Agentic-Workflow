---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\notion-backlog-human-scoring-e7a941.md'
original_relative_path: 'notion-backlog-human-scoring-e7a941.md'
source_sha256: aab50fa4351d275be51b0593ba73f1de9f8bb8752105c55437e43fbedbcf9cea
recovered_status: SURVIVED_IN_CURRENT
last_commit: '153652b9eb3'
last_commit_date: '2026-06-07 06:37:48 -0400'
created_date: '2026-04-24'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: notion-backlog-human-scoring-e7a941
plan_type: tracker
---

# Notion Backlog — Human Scoring of 63 UNSCORED Rows

Human-driven scoring pass for the 63 Wave/Phase Convergence rows that no automated pass could score (no `[Pn]` in title, no `Files In Scope`, no path-like tokens in Blocking Items). Output: worksheet filled by human → applier script PATCHes Notion.

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| `artifacts/notion/human_scoring_worksheet.md` | Pre-populated row list for human | ✅ generated |
| `artifacts/notion/human_scoring_worksheet.json` | Machine-readable worksheet (applier consumes this) | ✅ generated |
| `artifacts/notion/_pending_rescore.json` | Original rescore dry-run (shows unscorable reasons) | ✅ exists |
| `.windsurf/rules/constitutional.md` §24 | Priority scoring formula | ✅ |
| `.windsurf/rules/deferred-scope-capture.md` | Band thresholds SSOT | ✅ |
| `tools/priority/deferred_scope_scorer.py` | Formula reference (same thresholds) | ✅ |

---

## Wave Structure

| Wave | Metric | Scope | Checkpoint | Tokens |
|---|---|---|---|---|
| Wave 1 | Score 4 graph-edge rows (W9/W11/W12/W13) | W9, W11, W12, W13 | A | ~2K 🟢 |
| Wave 2 | Score 22 governance rows (W1.x / W2.x / W2-P1.x) | governance category | B | ~5K 🟢 |
| Wave 3 | Score 8 baseline-burndown rows (GAP/W1-P0/W3-P2/W4-P3) | baseline-burndown | C | ~3K 🟢 |
| Wave 4 | Score 22 singleton rows (H/B/EQ/ENH/misc) | singleton category | D | ~5K 🟢 |
| Wave 5 | Apply filled worksheet to Notion | applier script | E | ~2K 🟢 |

**Total: ~17K tokens across 5 waves, all GREEN.**

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| 1.1 | Score W9 (OTel→ADG edge) | worksheet.json | PP-1.1 | ~0.5K | 🔲 TODO |
| 1.2 | Score W11 (watchdog + secret telemetry) | worksheet.json | PP-1.2 | ~0.5K | 🔲 TODO |
| 1.3 | Score W12 (HITL decision log edges) | worksheet.json | PP-1.3 | ~0.5K | 🔲 TODO |
| 1.4 | Score W13 (profiler-derived calls) | worksheet.json | PP-1.4 | ~0.5K | 🔲 TODO |
| 2.1 | Score W1 pre/post gates (1.1–1.8) | worksheet.json | PP-2.1 | ~2K | 🔲 TODO |
| 2.2 | Score W2 rules/policy/MCP (2.1/2.4/2.7) | worksheet.json | PP-2.2 | ~1K | 🔲 TODO |
| 2.3 | Score W2-P1 exception wiring (2.1–2.5) | worksheet.json | PP-2.3 | ~1K | 🔲 TODO |
| 2.4 | Score W3-P2 baseline rows | worksheet.json | PP-2.4 | ~1K | 🔲 TODO |
| 3.1 | Score W1-P0 gate precision rows | worksheet.json | PP-3.1 | ~1K | 🔲 TODO |
| 3.2 | Score GAP-A/B rows (ssot-sweep residuals) | worksheet.json | PP-3.2 | ~1K | 🔲 TODO |
| 3.3 | Score W4-P3 test-harness baseline | worksheet.json | PP-3.3 | ~1K | 🔲 TODO |
| 4.1 | Score ENH1–ENH6 (LLM/prompt enhancements) | worksheet.json | PP-4.1 | ~2K | 🔲 TODO |
| 4.2 | Score H3/H6–H10 remainder (closure packages) | worksheet.json | PP-4.2 | ~1K | 🔲 TODO |
| 4.3 | Score B1–B5 (capture pipeline) | worksheet.json | PP-4.3 | ~1K | 🔲 TODO |
| 4.4 | Score EQ-8b/EQ-11b/EQ-12b/EQ-15/EQ-16 | worksheet.json | PP-4.4 | ~1K | 🔲 TODO |
| 4.5 | Score misc singletons (W0/W4/W1-W5/RT3/M/S/etc) | worksheet.json | PP-4.5 | ~1K | 🔲 TODO |
| 5.1 | Run applier script over filled worksheet | tools/debug/_apply_human_scoring.py | PP-5.1 | ~2K | 🔲 TODO |

---

## Gap Register

**GAP-1**: graph-edge rows (W9/W11/W12/W13) lack ADR justification; scoring requires deciding whether the new edge type is high-priority (ADG completeness) or low-priority (nice-to-have) — depends on downstream plan dependencies.

**GAP-2**: governance rows (W1.1–1.8, W2.x, W2-P1.x) are 2-week-old; many may already be landed (hooks exist, rules exist). Human should audit each before scoring — if landed, mark `DESCOPE` instead of assigning a band.

**GAP-3**: baseline-burndown rows reference counts (153 env flags, 142 legacy leaks, 1051 uncovered modules) that may have changed since the rows were created. Human should spot-check counts before scoring.

**GAP-4**: singleton rows have `[Pn]` band HINTS in titles for some (H/B/EQ/ENH series) — but these were already extracted in Wave D of the prior residual-cleanup plan. The 22 singletons in this worksheet are the ones that had NO extractable band.

**GAP-5**: some rows are action items ("Run tests", "Post-W4 resnapshot", "Final verification") not file-work — these should be marked `DESCOPE` or `SKIP` since P-band scoring doesn't apply to actions.

---

## Execution Plan

### Waves 1–4: Human Fills Worksheet (no Cursor Agent work)

**Deliverable**: `artifacts/notion/human_scoring_worksheet.json` populated with one of these values per row:

| BAND value | Meaning | Notion action |
|---|---|---|
| `P1`/`P2`/`P3`/`P4`/`P5` | Assign this priority band | PATCH P-Band select |
| `DESCOPE` | Row is obsolete/landed/duplicate | PATCH Status=Descoped |
| `SKIP` | Leave as UNSCORED (row needs more info first) | No PATCH; note added |
| (empty) | Not yet reviewed | No PATCH |

Optional columns (row gets richer metadata if filled):

| Column | Effect |
|---|---|
| `LAYER` | PATCH Layer select |
| `FILES` | PATCH Files In Scope rich_text (enables future auto-scoring) |
| `NOTES` | Append to Blocking Items |

**Scoring cheat-sheet** (constitutional §24):
```
impact = coverage_gap_pct × layer_multiplier × (1 + log10(1 + fan_in)) × surface_boost
layer_multiplier:  L0=2.0, L5=2.0, L3=1.75, L4=1.75, L1=1.0, L2=1.0, L6=0.75
surface_boost:     Security=1.5, Write=1.4, Execution=1.3, State=1.2, Observability=1.1, None=1.0
Bands: P1 ≥300, P2 ≥150, P3 ≥75, P4 ≥30, P5 <30
```

### Wave 5: Cursor Agent Applies Worksheet

**Script**: `tools/debug/_apply_human_scoring.py`
- Loads filled `human_scoring_worksheet.json`
- For each row with non-empty `BAND`:
  - If `DESCOPE` → PATCH Status=Descoped + note
  - If `SKIP` → no-op (keeps UNSCORED)
  - Else → PATCH P-Band=<band>, optionally Layer + Files In Scope + Blocking Items
- Logs every op to `artifacts/notion/_writeback_receipts.jsonl` (op=`PATCH-human-scored`)

---

## Rules

- Cursor Agent never assigns a BAND value — that's the human's job. This plan exists because automated scoring was exhausted.
- Applier script MUST be idempotent — re-running on an already-scored row patches the same values (detects no-op via current state).
- No MCP calls — direct Notion REST (consistent with prior waves).
- Receipts append-only; never truncate.

---

## Success Criteria

- [ ] Worksheet generated with all 63 rows categorized
- [ ] Plan registered in Plans DB
- [ ] 5 wave summary rows posted to Wave/Phase Convergence (one per wave, Status=Todo until human fills worksheet)
- [ ] Applier script exists and is tested on at least 3 pilot rows before bulk run
- [ ] After human fills worksheet, applier PATCHes all non-empty rows
- [ ] Post-apply, UNSCORED count drops from 63 toward 0 (aspirational; some rows may stay SKIP)

---

## Implementation Commands

```bash
# Already done (setup)
python tools/debug/_build_scoring_worksheet.py

# Human step (manual, this turn or later session):
# Edit artifacts/notion/human_scoring_worksheet.json and fill in BAND column for each row.

# Apply when ready (any future session):
python tools/debug/_apply_human_scoring.py
```

---

## Rollback Strategy

1. Receipts log records prior P-Band/Status for every PATCH — restore by re-PATCH from receipt values.
2. Human can re-edit worksheet and re-run applier; applier is idempotent.
3. If a whole category was miscategorized, delete those receipts entries and re-run just that subset.

---

## Acceptance Criteria

| Metric | Target | Verification |
|---|---|---|
| Worksheet row count | 63 | `jq length artifacts/notion/human_scoring_worksheet.json` |
| Plan in Plans DB | exists | Query Plans DB for slug=notion-backlog-human-scoring-e7a941 |
| Wave summary rows | 5 | Query Wave/Phase Convergence for Wave ID=HUMAN-SCORING |
| Applier idempotent | yes | Re-run and confirm zero new receipts |
| Final UNSCORED count | ≤63 (strictly decreases) | Query Wave/Phase Convergence for P-Band=UNSCORED |
