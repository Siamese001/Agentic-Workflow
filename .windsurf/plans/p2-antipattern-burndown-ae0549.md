# P2 HIGH-Severity Antipattern Burndown Plan

Wave-based plan to classify and reduce 3,924 HIGH-severity antipattern locations from ADG snapshot `04062026_2106`, using ADG-first triage, with **classify-only** discipline (no bulk auto-fix, no test suite destabilization).

---

## Context

| Item | Value |
|------|-------|
| **ADG Snapshot** | `04062026_2106` (86,351 nodes, 625,325 edges) |
| **Total antipattern edges** | 7,057 |
| **Scope** | HIGH-severity only: `silent_exception_swallow`, `broad_exception_catch`, `log_and_swallow`, `return_none_swallow` |
| **Estimated locations** | ~3,924 |
| **P2 Rule** | Classify-only — `can_fix()` always returns `(False, "P2 requires human classification")` |
| **Hard-fail gate** | `_check_p2_antipatterns()` in `tools/generate/generate_full_adg.py` now exits non-zero on any HIGH antipattern |
| **Blocker** | Cannot regenerate a clean ADG until count reaches 0 (or ratchet threshold is set) |

---

## Wave Summary

| Wave | Focus | Est. Locations | Status |
|------|-------|---------------|--------|
| **W0** | ADG query: get per-category counts and file distribution | 0 code changes | DONE — 4,553 rows |
| **W1** | Establish ratchet baseline + P2 classify rule | Infrastructure | **Done** (2026-04-22) |
| **W2** | Burn `return_none_swallow` — safest, mechanical pattern | **303** | Pending |
| **W3** | Burn `log_and_swallow` — log-only exception bodies | **739** | Pending |
| **W4** | Burn `silent_exception_swallow` — add re-raise/metadata | **530** | Pending |
| **W5** | Burn `broad_exception_catch` — largest, most complex | **2,981** | Pending |
| **W6** | Regenerate ADG, verify gate passes, update ratchet | Verification | Pending |

---

## Wave 0 — ADG Triage Query (Read-Only)

**Goal:** Establish exact counts per category and per layer before touching any file.

**Actions:**
1. Run `tools/evidence/_query_antipatterns.py` against `adg_indexed_04062026_2106.sqlite`
2. Extend query to group by `edge_kind` AND `source_file` layer prefix — produces per-layer breakdown
3. Export CSV: `artifacts/adg_analysis/p2_high_severity_inventory.csv`
4. Identify top-20 files by antipattern density (fan-out hotspot intersection)

**Acceptance:** CSV exists with columns `[source_file, line_no, edge_kind, layer]`. Counts sum to ~3,924.

---

## Wave 1 — Infrastructure: Ratchet + Classify Rule

**Goal:** Prevent regression and wire the classify rule the repair orchestrator plan (02c1fc) specified but left incomplete.

**Actions:**
1. **P2 ratchet** — Update `artifacts/adg/p2_ratchet.json` (file already exists):
   - Set `high_severity_ceiling` to current count (~3,924)
   - Gate in `_check_p2_antipatterns()` blocks if count EXCEEDS ceiling
   - Ceiling is lowered after each wave completes
2. **`fix_p2_antipatterns.py` rule** — Wire the classify-only rule missing from `tools/adg/repair/rules/` (GAP-3 from plan 02c1fc):
   - `match()`: `issue_type IN ('silent_exception_swallow', 'broad_exception_catch', 'log_and_swallow', 'return_none_swallow')`
   - `can_fix()`: always `(False, "P2 requires human classification")`
   - `apply_fix()`: returns structured classification report (file, line, type, hint)
   - Register in `tools/adg/repair/rules/__init__.py`
3. **`get_p2_antipatterns()` in `sqlite_analyzer.py`** — Add the missing HIGH-severity query (GAP-3)
4. **Tests** — `test_p2_rule_always_block_fix()` + `test_sqlite_analyzer_p2_antipatterns()`

**Acceptance:** `python tools/adg/adg_repair.py --latest --dry-run` prints P2 count >= 1.

### W1 Completion Evidence (2026-04-22)

All W1 infrastructure is live on disk and wired:

- `artifacts/adg/p2_ratchet.json` — schema is `{"exception_swallow_ceiling": N}`; current ceiling=0.
- `tools/adg/repair/rules/fix_p2_antipatterns.py` — `FixP2AntipatternsRule` registered in `tools/adg/repair/rules/__init__.py`; `can_fix()` always returns `(False, "P2 antipatterns require human classification and review")`.
- `tools/adg/repair/sqlite_analyzer.py::get_p2_antipatterns()` — HIGH-severity query present; feeds deficiencies into repair orchestrator.
- `tools/generate/validation/gates.py::_check_p2_ratchet()` — wired into `tools/generate/generate_full_adg.py` at line 576; counts `violations WHERE severity='MEDIUM' AND category='antipattern'`; fails ADG generation on regression above ceiling; auto-lowers ceiling when count drops.

**Taxonomy correction (IMPORTANT for W2-W5):** The plan's wave counts (530/739/2981/303) were drafted against ADG snapshot `04062026_2106` with an older antipattern classification. Current snapshot `04222026_1218` uses a new taxonomy where severity is `P0`/`P1`/`P2`/`P3`/`LOW`/`CRITICAL` and category codes are `AP-NN`/`SC-NN`. The raw `edges` table still exposes legacy `edge_kind` labels; counts from that source are:

| edge_kind (legacy) | 2026-04-22 count |
|--------------------|-----------------:|
| log_and_swallow | 701 |
| broad_exception_catch | 648 |
| silent_exception_swallow | 339 |
| return_none_swallow | 297 |
| **HIGH-severity subtotal** | **1,985** |

W2-W5 should be replanned against the new taxonomy before execution. Tracking row in Wave/Phase Convergence DB will be re-scored after W2 plan is drafted.

---

## Wave 2 — `return_none_swallow` (~600 locations)

**Pattern:** `except Exception: return None` / `return {}` / `return []` — mechanical, low-risk.

**Fix strategy:** Replace with structured error return `{"error": str(e), ...}` or re-raise.

**Approach:**
- ADG query: `SELECT source_file, line_no FROM edges WHERE relation_type='antipattern' AND edge_kind='return_none_swallow'`
- Group by layer — fix L_TOOLS and L_OPS first (lowest blast radius), then L_APP, then `agentic_core/`
- Verify: scoped `pytest` on affected files only (T2 discipline — no full suite per wave)

**Acceptance:** `return_none_swallow` count = 0. Ratchet ceiling lowered by ~600.

---

## Wave 3 — `log_and_swallow` (~800 locations)

**Pattern:** `except Exception: logger.error(...)` with no re-raise — log then silently continue.

**Fix strategy:** Add `raise` after log, OR convert to structured error return.

**Approach:**
- ADG query for `log_and_swallow` edges with `source_file`
- Triage: if caller handles `None` return — structured return; otherwise — re-raise
- Priority order: L_TOOLS -> L_OPS -> L_APP -> `agentic_core/` (L5 last, highest blast radius)
- Run scoped tests after each ~100-location batch

**Acceptance:** `log_and_swallow` count = 0. Ratchet ceiling lowered by ~800.

---

## Wave 4 — `broad_exception_catch` (~900 locations)

**Pattern:** `except Exception:` that doesn't swallow — catches broadly but may do something.

**Fix strategy:** Narrow exception type where clear, or add re-raise.

**Approach:**
- ADG query for `broad_exception_catch` edges
- Sub-classify via AST: does body re-raise? does it propagate? does it swallow?
  - Re-raises: add `# guardian: allow-broad-exception -- <specific justification>` (Author-Gate gate required per §8)
  - Silent: escalate to `silent_exception_swallow` treatment in Wave 5
- Each guardian exemption requires Author-Gate approval (constitutional §8)

**Acceptance:** `broad_exception_catch` count = 0 or remaining instances have approved guardian exemptions. Ratchet ceiling lowered.

---

## Wave 5 — `silent_exception_swallow` (~1,624 locations)

**Pattern:** `except Exception: pass` — no logging, no re-raise, no error propagation.

**Fix strategy:** Most complex — requires understanding caller contract.

**Approach:**
- ADG query for `silent_exception_swallow` edges, grouped by module layer and fan-in
- Triage sub-categories:
  - **Cleanup swallowers** (`__del__`, `__exit__`, teardown): guardian exemption with justification
  - **Best-effort operations** (cache miss, optional enrichment): convert to warn-and-continue
  - **True silent failures**: add structured error metadata return or re-raise
- Author-Gate gate before any guardian exemption (§8)
- Maximum 50 files per sub-wave to keep scope verifiable

**Acceptance:** `silent_exception_swallow` count = 0 or all remaining have approved guardian exemptions. Ratchet ceiling lowered.

---

## Wave 6 — Verification and ADG Regeneration

**Goal:** Clean ADG generation with P2 gate passing.

**Actions:**
1. Close MCP ADG connections to release SQLite locks
2. `python tools/generate/generate_full_adg.py` — must complete without P2 hard-fail
3. Verify new snapshot: antipattern HIGH count = 0 (or <= approved guardian-exempt ceiling)
4. Run full test suite: `pytest tests/` — zero regressions
5. Update `artifacts/adg/p2_ratchet.json` ceiling to final approved count

**Acceptance:** ADG generation exits 0. Full test suite passes. Ratchet ceiling = approved final count.

---

## Rules

- **Classify-only** — P2 rule MUST NOT write code changes autonomously
- **Author-Gate before guardian exemptions** — §8 requires explicit approval before any `# guardian: allow-*` comment
- **Scoped tests only per wave** — no full-suite run until Wave 6
- **Ratchet enforced** — ceiling decreases after each wave; count above ceiling blocks ADG
- **ADG-first** — every wave starts with an ADG SQL query before touching files
- **No bulk exemptions** — each guardian comment needs specific, non-generic justification per §8

---

## Success Criteria

- [ ] W0: `p2_high_severity_inventory.csv` exists with ~3,924 rows
- [ ] W1: `fix_p2_antipatterns.py` rule registered; `adg_repair.py --dry-run` shows P2 count
- [ ] W2-W5: Each HIGH category count = 0 (or approved guardian-exempt remainder)
- [ ] W6: ADG generation exits 0; full test suite passes; ratchet ceiling = approved final count
