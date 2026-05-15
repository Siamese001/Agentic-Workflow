---
plan_id: wire-sqlite-decision-ledger-e8f3a2
plan_type: infra
---

# Wire On-Disk SQLite Decision Ledger as True SSOT (Notion → Mirror)

Make `.windsurf/state/refactor_decisions/refactor_decision_ledger.sqlite` the canonical Author-Gate decision ledger; demote Notion HITL Decision Ledger to a read-only mirror synced from SQLite; close all three currently-broken capture paths.

---

## Context (SCQA)

- **Situation** — Three capture paths exist for Author-Gate decisions: (1) Windsurf `post_cascade_response` hook `post_cascade_author_gate_capture.py` writes a 27-column row to SQLite `decisions` table, (2) `tools/capture/append_marker.py` writes thin `DECISION_CAPTURED:` lines to `artifacts/capture/markers.jsonl`, (3) Cursor Agent manually posts full rows to Notion HITL Decision Ledger via `mcp7_API-post-page`. The on-disk SQLite has rich schema (incl. `prev_hash`/`row_hash`/`signature` for tamper-evident chaining) but **0 rows**. Notion has full-rationale rows (latest 2026-05-02). JSONL has 14 thin markers.
- **Complication** — The `post_cascade_author_gate_capture.py` hook is firing but receiving truncated stdin (`text_len=30..47` chars per `author_gate_capture.log`), so detection always returns `marker=False` and SQLite stays empty. Meanwhile `append_marker.py` writes JSONL but never SQLite. Notion is the only durable record but is human-driven (Cursor Agent manually posts), creating a single point of failure: skip the manual post → decision is lost.
- **Question** — How do we make on-disk SQLite the canonical, automated, tamper-evident SSOT while keeping Notion as a human-readable mirror?
- **Answer** — (a) Diagnose and fix the truncated-stdin issue OR route around it by having `append_marker.py` ALSO insert a SQLite row, (b) build a one-way `tools/notion/sync_decision_ledger.py` that mirrors SQLite → Notion, (c) backfill existing JSONL + Notion rows into SQLite, (d) make Notion read-only (sync overwrites manual edits), (e) update constitutional §30 to reference SQLite as canonical.

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| `.windsurf/scripts/post_cascade_author_gate_capture.py` | Existing hook implementation; understand current SQLite write logic | ✅ |
| `.windsurf/state/refactor_decisions/refactor_decision_ledger.sqlite` | Schema (27-col `decisions`, `decision_scope`, `decision_outcomes`, `decisions_fts`) | ✅ |
| `.windsurf/state/refactor_decisions/author_gate_capture.log` | Confirms hook fires but stdin is 30-47 chars | ✅ |
| `tools/capture/append_marker.py` | JSONL writer; current marker format | 🔲 to read in Phase 1.1 |
| `artifacts/capture/markers.jsonl` | 14 existing markers for backfill | ✅ |
| `.windsurf/hooks.json` | `post_cascade_response` chain definition; understand stdin contract | 🔲 to read in Phase 1.1 |
| Notion HITL Decision Ledger (data_source `5b60fdde-...`) | Existing rows for backfill | ✅ |
| `.windsurf/rules/author-gate-enforcement.md` | Marker format spec | 🔲 to read in Phase 4.3 |
| `constitutional.md §30` | Currently references "DECISION_CAPTURED:" + `tools/capture/append_marker.py` as canonical capture | 🔲 to update in Phase 4.3 |

---

## Wave Structure

| Wave | Metric | Scope | Checkpoint | Tokens |
|---|---|---|---|---|
| Wave 1 | Stdin-truncation root cause OR routing decision | Diagnose hook stdin issue; pick fix-hook vs route-via-marker path | A | 6K 🟢 |
| Wave 2 | SQLite write path live | `append_marker.py` (and/or fixed hook) inserts full row into `decisions` + `decision_scope` + `decisions_fts` | B | 12K 🟢 |
| Wave 3 | Notion sync job | `tools/notion/sync_decision_ledger.py` mirrors SQLite → Notion (one-way) | C | 10K 🟢 |
| Wave 4 | Backfill + governance | Backfill 14 JSONL + Notion rows into SQLite; update constitutional §30; add CI gate | D | 8K 🟢 |

**Total: ~36K tokens across 4 waves, all GREEN**

---

## Out Of Scope

- Tamper-detection key management (`signature` column) — keep as `null` for now; signing infra is a separate plan
- Migration of `decision_outcomes` outcome-binding logic — already wired in the existing hook, leave untouched
- Renaming the database / schema migration — schema stays as-is (27-col), only the write path changes
- Modifying constitutional rule numbers other than §30
- Editing `pre_author_gate.py`, `author_gate_marker_validator.py`, `author_gate_ledger_integrity.py` (read-only references)
- Notion → SQLite reverse sync (explicitly one-way: SQLite is canonical)
- Real-time / streaming sync (batch-only acceptable; runs on commit hook or scheduled)
- Multi-tenant decision ledger (single-operator only)

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| 1.1 | Diagnose truncated stdin | `.windsurf/hooks.json`, `post_cascade_author_gate_capture.py` (read), `author_gate_capture.log` | GAP-1 | ~3K | 🔲 TODO |
| 1.2 | Routing decision: fix hook vs route via append_marker | none — Author-Gate decision packet, choose path | GAP-1 | ~3K | 🔲 TODO |
| 2.1 | Refactor `append_marker.py` to insert full SQLite row | `tools/capture/append_marker.py`, helper from `post_cascade_author_gate_capture.py` (extract shared `_capture_from_marker` logic into a library) | GAP-2 | ~6K | 🔲 TODO |
| 2.2 | Unit tests for SQLite insert path | `tests/unit/tools/capture/test_append_marker_sqlite.py` (NEW) | GAP-2, GAP-5 | ~4K | 🔲 TODO |
| 2.3 | Smoke test end-to-end on a synthetic marker | manual or `tests/integration/test_decision_capture_e2e.py` (NEW) | GAP-2 | ~2K | 🔲 TODO |
| 3.1 | Build `tools/notion/sync_decision_ledger.py` | `tools/notion/sync_decision_ledger.py` (NEW), `tools/notion/_client.py` (use existing if present, else inline) | GAP-3 | ~6K | 🔲 TODO |
| 3.2 | Tests for sync job | `tests/unit/tools/notion/test_sync_decision_ledger.py` (NEW) | GAP-3, GAP-5 | ~4K | 🔲 TODO |
| 4.1 | Backfill 14 JSONL markers + Notion rows into SQLite | `tools/capture/backfill_to_sqlite.py` (NEW, one-shot), `artifacts/maintenance/decision_ledger_backfill.jsonl` (audit) | GAP-4 | ~3K | 🔲 TODO |
| 4.2 | CI gate: SQLite freshness | `ops_scripts/ci/check_decision_ledger_sqlite_freshness.py` (NEW) | GAP-5 | ~2K | 🔲 TODO |
| 4.3 | Constitutional §30 update + AGENTS.md HITL row | `.windsurf/rules/constitutional.md`, `AGENTS.md` | GAP-6 | ~2K | 🔲 TODO |
| 4.4 | Verification — query SQLite, compare with Notion rowcount, run pytest | none — verification | GAP-5 | ~1K | 🔲 TODO |

**Status legend**: 🔲 TODO · 🔄 IN PROGRESS · ✅ DONE · ❌ BLOCKED

---

## Gap Register

**GAP-1: Truncated stdin to post_cascade hooks**
- The Windsurf `post_cascade_response` hook chain delivers only 30-47 chars to `post_cascade_author_gate_capture.py`. Should be the full Cursor Agent response.
- May be a Windsurf hook-config issue, a buffering issue, or the hook reads the wrong field.
- Impact: SQLite `decisions` table has 0 rows despite the writer being correct.
- Resolution path forks at Phase 1.2: either fix the hook (Cursor Agent-side) or route around it (use `append_marker.py` as the SQLite writer).

**GAP-2: `append_marker.py` writes JSONL only**
- Currently only writes to `artifacts/capture/markers.jsonl`. The marker shape captures `selected`, `outcome`, `confidence`, `gap`, `principle`, `precedent` — enough to populate most SQLite columns.
- Needs to be extended to ALSO insert into SQLite, OR a new wrapper introduced.

**GAP-3: No SQLite → Notion sync**
- Notion HITL Decision Ledger has rich rows but is populated by Cursor Agent manually calling `API-post-page`. If Cursor Agent forgets, the decision is lost.
- Needs a deterministic batch sync job that reads new SQLite rows and creates/updates Notion rows.

**GAP-4: 14 existing JSONL markers + Notion rows not in SQLite**
- Backfill required so SQLite reflects the actual decision history, not just decisions captured after this plan lands.

**GAP-5: No CI gate ensures SQLite is being written**
- Without a freshness check, the ledger could silently regress to "0 rows again" without anyone noticing for weeks (precedent: this is exactly what happened until today's audit).

**GAP-6: Constitutional §30 references the wrong canonical surface**
- §30 currently treats `DECISION_CAPTURED:` markers + `artifacts/capture/markers.jsonl` as the SSOT. Needs update to reference SQLite-row insertion as canonical, JSONL marker as a redundant event signal.

---

## Execution Plan

### Phase 1.1 — Diagnose truncated stdin
**Scope**: Read `.windsurf/hooks.json` to find the `post_cascade_response` chain definition. Read the entrypoint of `post_cascade_author_gate_capture.py` to see how it reads stdin. Run a one-off probe: write a tiny diagnostic hook that logs `len(sys.stdin.read())` + first 200 chars of stdin to a file; trigger it on the next response; read the log.

**Acceptance**: Either (a) stdin contract is documented and fixable in the hook, or (b) Windsurf-side limitation is confirmed and the routing-via-marker path is required.

### Phase 1.2 — Routing decision (Author-Gate)
**Scope**: Score 2 candidates: (K1) Fix hook to read full response, (K2) Route SQLite writes via `append_marker.py` instead. Apply Author-Gate per `author-gate-enforcement.md`. K2 is structurally simpler and decouples the SSOT from Windsurf-side hook quirks; K1 is more complete but depends on Windsurf cooperation.

**Acceptance**: Decision recorded in this plan + Notion HITL Decision Ledger + emitted DECISION_CAPTURED marker.

### Phase 2.1 — Refactor `append_marker.py` to insert SQLite row
**Scope**: Extract `_init_db()` + INSERT logic from `post_cascade_author_gate_capture.py` into a shared library `tools/capture/_decision_ledger_writer.py` (SSOT folder per §31 — `tools/<domain>/`). Have `append_marker.py` call the library after writing JSONL. Preserve all 27 columns; for fields the marker doesn't carry (e.g. `request_summary`, `user_goal`), insert empty strings or NULL.

**Acceptance**: Manual smoke — write a `DECISION_CAPTURED:` marker via `append_marker.py`, then `SELECT COUNT(*) FROM decisions` returns +1.

### Phase 2.2 — Unit tests for SQLite insert path
**Scope**: New test file `tests/unit/tools/capture/test_append_marker_sqlite.py`. Cover: (a) marker → SQLite row mapping, (b) idempotency (same `decision_id` inserted twice → no duplicate), (c) FTS5 sync, (d) failure mode (DB unavailable → fail-open, JSONL still written).

**Acceptance**: ≥6 tests, all pass.

### Phase 2.3 — End-to-end smoke
**Scope**: New `tests/integration/test_decision_capture_e2e.py` invokes `append_marker.py` with a realistic marker, queries SQLite, asserts row exists with expected fields.

**Acceptance**: 1 test, passes.

### Phase 3.1 — Build `tools/notion/sync_decision_ledger.py`
**Scope**: New script. Reads SQLite `decisions` rows where `created_at` > last-sync-watermark (stored in `.windsurf/state/refactor_decisions/notion_sync_watermark.txt`). For each row: query Notion HITL Decision Ledger by `decision_id` (custom property), if exists update, else create. One-way only.

**Acceptance**: Run with `--dry-run` shows N rows to sync; run with `--apply` posts N rows to Notion; re-run is idempotent (0 rows to sync).

### Phase 3.2 — Tests for sync job
**Scope**: Mock Notion API (urllib stub or requests-mock equivalent). Cover: (a) new row → POST, (b) existing row → PATCH, (c) network failure → retries, (d) idempotency.

**Acceptance**: ≥5 tests, all pass.

### Phase 4.1 — Backfill JSONL + Notion → SQLite
**Scope**: One-shot script `tools/capture/backfill_to_sqlite.py`. Reads `artifacts/capture/markers.jsonl` AND queries Notion HITL Decision Ledger AND inserts into SQLite. Audit log at `artifacts/maintenance/decision_ledger_backfill.jsonl`. Idempotent (skip if `decision_id` already present).

**Acceptance**: After running, `SELECT COUNT(*) FROM decisions` >= count of unique decisions across the two sources. Backfill log has one row per insert.

### Phase 4.2 — CI gate: SQLite freshness
**Scope**: New `ops_scripts/ci/check_decision_ledger_sqlite_freshness.py`. Detects refactor-class responses that should have produced a `DECISION_CAPTURED:` marker but produced no SQLite row in the last 24h. Wires into pre-commit `T7r` tier or similar.

**Acceptance**: Gate passes on a clean repo; gate fails on a synthetic regression (decision_id absent for a marker present in JSONL).

### Phase 4.3 — Constitutional §30 + AGENTS.md update
**Scope**: Edit `constitutional.md §30` to reference SQLite-row insertion as canonical capture; demote `DECISION_CAPTURED:` marker / JSONL to "redundant event signal". Update AGENTS.md Notion Workspace Map to flag HITL Decision Ledger as "Notion mirror — SSOT is SQLite at .windsurf/state/refactor_decisions/refactor_decision_ledger.sqlite". Verify `check_always_on_token_budget.py` still passes (constitutional.md may have grown).

**Acceptance**: §30 prose updated; AGENTS.md row updated; budget gate green.

### Phase 4.4 — Final verification
**Scope**: (a) Query SQLite: `SELECT COUNT(*) FROM decisions` ≥ Notion row count. (b) Run full pytest scope of new tests. (c) Run sync job dry-run, expect 0 deltas. (d) Run check_always_on_token_budget.py.

**Acceptance**: All four green.

---

## Rules

- All phases follow constitutional §31 SSOT folder routing (new files land in `tools/<domain>/` or `ops_scripts/ci/`)
- All subprocess calls include `timeout=` per §0/§14
- All `pytest.mark.skip` is forbidden per §1
- No `pytest` full-suite runs; scope tests with `-k` or path arg
- All file I/O uses `encoding="utf-8"`
- The SQLite write path is fail-open: if SQLite is unavailable, JSONL is still written so no decision is lost
- The Notion sync is fail-soft: a sync failure logs but does not block subsequent decisions

---

## Success Criteria

- [ ] SQLite `decisions` table receives a row for every Author-Gate decision (verified by Phase 4.4 query)
- [ ] `tools/notion/sync_decision_ledger.py` mirrors SQLite → Notion idempotently
- [ ] All 14 JSONL markers + all existing Notion rows backfilled into SQLite
- [ ] CI gate `check_decision_ledger_sqlite_freshness.py` blocks regressions
- [ ] Constitutional §30 references SQLite as canonical SSOT
- [ ] AGENTS.md Notion Workspace Map flags HITL row as "mirror"
- [ ] All new pytest passes (≥12 unit + 1 integration)
- [ ] `check_always_on_token_budget.py` green

---

## Implementation Commands

```bash
# Phase 1.1 — diagnostic
python -c "import json; print(json.load(open('.windsurf/hooks.json'))['post_cascade_response'])"

# Phase 2.x — after refactor
python -m pytest tests/unit/tools/capture/test_append_marker_sqlite.py -v
python -m pytest tests/integration/test_decision_capture_e2e.py -v

# Phase 3.1 — sync job
python tools/notion/sync_decision_ledger.py --dry-run
python tools/notion/sync_decision_ledger.py --apply

# Phase 4.1 — backfill
python tools/capture/backfill_to_sqlite.py --dry-run
python tools/capture/backfill_to_sqlite.py --apply

# Phase 4.4 — verification
python -m pytest tests/unit/tools/capture tests/unit/tools/notion tests/integration/test_decision_capture_e2e.py -v
python ops_scripts/ci/check_decision_ledger_sqlite_freshness.py
python ops_scripts/ci/check_always_on_token_budget.py
```

---

## Rollback Strategy

If things go wrong:
1. **Phase 2.x rollback** — revert `tools/capture/append_marker.py` and `tools/capture/_decision_ledger_writer.py` (delete the latter); JSONL writing is preserved unchanged so no data loss
2. **Phase 3.x rollback** — delete `tools/notion/sync_decision_ledger.py`; existing manual `API-post-page` flow still works
3. **Phase 4.1 backfill rollback** — `DELETE FROM decisions WHERE decision_id IN (<backfilled ids>)`; rows are tagged with a `created_via='backfill'` field in `selection_rationale`
4. **Phase 4.3 constitutional rollback** — git revert the AGENTS.md + constitutional.md edits; capture continues working since SQLite is still the canonical write target

Each phase is independently revertable; no irreversible operation.

---

## Acceptance Criteria

| Metric | Target | Verification |
|---|---|---|
| SQLite decisions table populated | ≥ count of distinct decisions across JSONL + Notion | `SELECT COUNT(*) FROM decisions` |
| Sync job idempotency | re-run produces 0 deltas | `python tools/notion/sync_decision_ledger.py --dry-run` |
| New tests passing | ≥12 unit + 1 integration | `python -m pytest tests/unit/tools/capture tests/unit/tools/notion tests/integration/test_decision_capture_e2e.py` |
| CI gate works | passes clean, fails on synthetic regression | run `check_decision_ledger_sqlite_freshness.py` in both states |
| Constitutional budget | still green | `python ops_scripts/ci/check_always_on_token_budget.py` |

## Cursor Agent Alignment Checks

- Reuses existing `_init_db()` and 27-col schema instead of re-defining
- Lifts shared logic into `tools/capture/_decision_ledger_writer.py` per SSOT folder discipline
- Each new file lands in canonical SSOT folder per §31
- Sync job is one-way (SQLite → Notion); no bidirectional reconciliation
- Fail-open everywhere (SQLite unavailable ≠ lose the decision)
- Phased — Wave 1 must Author-Gate-decide before any code is written
