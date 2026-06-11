---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\antipattern-reclassify-e5a569.md'
original_relative_path: '_archive\\2026-05\\antipattern-reclassify-e5a569.md'
source_sha256: 4cb828b729d3c9635661dc99bba6ed174de441f8e415a04703713d3542423bc2
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Anti-Pattern Reclassification: ADG as Primary Hardening Gate

Reclassify P3/P4 antipatterns to P2/P1 where warranted, wire them into the ADG RepairRoute + blocking chain, and fix the terminal P1-P4 defect table to read counts directly from the ADG violations table in SQLite rather than the routing summary (which only covers `violates`/`dynamic_exec` edges).

---

## Problem Statement

Two compounding bugs make the current system blind:

1. **Severity SQL is `edge_kind`-blind** — classifies by `symbol LIKE 'except:Exception%'` only; all other exception types default to LOW regardless of pattern or layer.
2. **`_print_defect_table` reads from `routing_summary`** which is populated by `route_violations()` → `_RELATION_TO_ROUTE`. Since `antipattern` relation_type is absent from that dict, **P3/P4 counts in the terminal table are always 0** from antipatterns. The table is lying.

Result: 4,151+ real violations are invisible in the terminal output and unreported.

---

## Current State (directly observed from ADG SQLite)

| Edge Kind | Total | Current Severity | Correct Severity |
|---|---|---|---|
| `broad_exception_catch` | 2,924 | 185 MEDIUM, 2,739 LOW | HIGH in L0/L2/L3/L5; MEDIUM elsewhere |
| `log_and_swallow` | 741 | 32 MEDIUM, 709 LOW | HIGH in L0/L2/L3/L5; MEDIUM elsewhere |
| `silent_exception_swallow` | 538 | 45 MEDIUM, 493 LOW | HIGH in L0/L2/L3/L5; MEDIUM elsewhere |
| `return_none_swallow` | 313 | 45 MEDIUM, 268 LOW | HIGH in L0/L2/L3/L5; MEDIUM elsewhere |
| `retry_without_backoff` | 162 | ALL LOW | **Keep LOW** — false positives (`symbol=for_retry` variable names) |
| `blocking_call_in_async` | 15 | ALL LOW | **Keep LOW** — false positives (`dict.get()`, test tooling only) |
| `global_state_mutation` | 5 | ALL LOW | **Keep LOW** — false positives (lazy singleton caches) |

---

## Files Touched (5 total)

| # | File | Change |
|---|---|---|
| 1 | `agentic_core/adg/artifact/multi_writer.py` | Fix severity SQL |
| 2 | `agentic_core/adg/artifact/ArtifactPaths.py` | Same severity SQL (duplicate writer path) |
| 3 | `agentic_core/adg/analysis/RepairRoute.py` | Add 4 antipattern `edge_kind`s to `_RELATION_TO_ROUTE` |
| 4 | `tools/generate/generate_full_adg.py` | Fix defect table + extend `violation_edges` filter + add `_check_p2_defects()` |
| 5 | Test files (2) | Cover new severity branches + routing entries |

---

## Wave 1 — Severity SQL Fix (files 1 & 2, identical change)

Replace the `symbol LIKE 'except:Exception%'` filter with `edge_kind IN (...)`:

```sql
CASE
    -- Exception handling antipatterns in critical layers → HIGH (P2)
    WHEN relation_type = 'antipattern'
     AND edge_kind IN ('broad_exception_catch','silent_exception_swallow',
                       'log_and_swallow','return_none_swallow')
     AND (   source_file LIKE 'agentic_core/L0_routing/%'
          OR source_file LIKE 'agentic_core/L5_safety/%'
          OR source_file LIKE 'agentic_core/L2_execution/%'
          OR source_file LIKE 'agentic_core/L3_orchestration/%'
     ) THEN 'HIGH'

    -- Exception handling antipatterns in non-critical layers → MEDIUM (P3)
    WHEN relation_type = 'antipattern'
     AND edge_kind IN ('broad_exception_catch','silent_exception_swallow',
                       'log_and_swallow','return_none_swallow')
    THEN 'MEDIUM'

    -- All other antipatterns → LOW (P4) — covers false-positive-prone kinds
    WHEN relation_type = 'antipattern' THEN 'LOW'
    ELSE 'MEDIUM'
END
```

---

## Wave 2 — RepairRoute Wiring (file 3)

Add to `_RELATION_TO_ROUTE` (keyed by `edge_kind`, matched via the existing fallback in `route_violations()`):

```python
"broad_exception_catch":    ("ManualReview", "governance", "high",   "Broad exception catch: hides bugs and error propagation failures"),
"silent_exception_swallow": ("ManualReview", "governance", "high",   "Silent exception swallow: suppresses failures without signalling callers"),
"log_and_swallow":          ("ManualReview", "governance", "high",   "Log-and-swallow: logs but does not re-raise; callers see false success"),
"return_none_swallow":      ("ManualReview", "governance", "high",   "Return-None-swallow: caller cannot distinguish error from valid None"),
```

---

## Wave 3 — Terminal Table + Enforcement Fix (file 4)

### Fix 1: `violation_edges` filter — include critical-layer antipatterns

```python
violation_edges = [
    e for e in result.edges
    if e.relation_type in ("violates", "dynamic_exec", "invokes_provider")
    or (
        e.relation_type == "antipattern"
        and e.edge_kind in {
            "broad_exception_catch", "silent_exception_swallow",
            "log_and_swallow", "return_none_swallow",
        }
        and any(
            e.source_file.startswith(p)
            for p in ("agentic_core/L0_routing/", "agentic_core/L5_safety/",
                      "agentic_core/L2_execution/", "agentic_core/L3_orchestration/")
        )
    )
]
```

### Fix 2: `_print_defect_table` — read from SQLite violations table

The terminal table currently reads from `routing_summary["by_severity"]` which misses all antipatterns. Fix: after SQLite is written, query the violations table directly for the printed counts. Signature change:

```python
def _print_defect_table(
    routing_summary: dict,
    semantic_warnings: list[str] | None = None,
    sqlite_path: Path | None = None,   # NEW
) -> None:
```

Logic: if `sqlite_path` is provided, query `SELECT severity, COUNT(*) FROM violations GROUP BY severity` and use those counts. `routing_summary` counts (layer violations, dynamic_exec, etc.) are **added on top** — they are not in the violations table.

Terminal output becomes:

```
[ADG] Defect Summary (from ADG edges):
+-----+-------------------------------+--------+
| P#  | Description                   | Count  |
+-----+-------------------------------+--------+
| P1  | CRITICAL - layer violations   |      0 |
| P2  | HIGH - exception antipatterns |    307 |
| P3  | MEDIUM - code quality         |   4151 |
| P4  | LOW - semantic/style          |    240 |
+-----+-------------------------------+--------+
| TOT | TOTAL                         |   4698 |
+-----+-------------------------------+--------+
```

### Fix 3: Add `_check_p2_defects()` — non-blocking, prints count

```python
def _check_p2_defects(sqlite_path: Path) -> int:
    """Return count of HIGH antipatterns in critical layers (non-blocking, for reporting)."""
```

Called after `_check_p1_defects()`. Does **not** call `sys.exit(1)` — P2 is tracking-only per constitutional table.

---

## Wave 4 — Tests (file 5)

| Test | What it verifies |
|---|---|
| `test_multi_writer.py` | `broad_exception_catch` in L0 → HIGH; in `apps_rg` → MEDIUM; `retry_without_backoff` → LOW |
| `test_repair_route.py` | All 4 antipattern edge_kinds appear in `_RELATION_TO_ROUTE`; route_violations returns routes for them |
| `test_generate_full_adg.py` (if exists) | `_print_defect_table` with sqlite_path reads from violations table |

---

## What Does NOT Change

- `.pre-commit-config.yaml` — no changes
- `_check_p1_defects()` — P1 still blocks only on `violates` (layer boundary) edges
- `retry_without_backoff`, `blocking_call_in_async`, `global_state_mutation` — stay LOW
- Guardian exemptions — `disposition` column untouched; existing exemptions honoured
- Pre-commit hooks, tests outside the 2 test files listed — no changes

---

## Wave Summary Table

| Wave | Files | Focus | Est. Tokens | Status |
|---|---|---|---|---|
| W1 | `multi_writer.py`, `ArtifactPaths.py` | Severity SQL (identical in both) | ~200 | **Done** (2026-04-22) |
| W2 | `RepairRoute.py` | Wire 4 antipattern edge_kinds | ~100 | **Done** (2026-04-22) |
| W3 | `generate_full_adg.py` | violation_edges filter + table fix + p2 check | ~400 | **Done** (2026-04-22) |
| W4 | 2 test files | Regression coverage | ~300 | **Done** (2026-04-22) |

---

## W1-W3 Completion Evidence (2026-04-22)

Stale-source sniff-test on 2026-04-22 confirms W1, W2, W3 are already live on disk (the plan header was stale). Evidence:

### W1 — Severity SQL

Both `agentic_core/adg/artifact/multi_writer.py` and `agentic_core/adg/artifact/ArtifactPaths.py` contain a richer `edge_kind IN (...)` CASE than the plan proposal. Production-layer HIGH tier covers: `broad_exception_catch`, `silent_exception_swallow`, `log_and_swallow`, `return_none_swallow`, `unreachable_after_raise`, `exception_type_erasure`, `blocking_call_in_async`, `bare_except`. Plus CRITICAL tier for `missing_hitl_on_irreversible` and `chokepoint_bypass`, and global HIGH for `hardcoded_secret`. The legacy `symbol LIKE 'except:Exception%'` filter no longer exists.

### W2 — RepairRoute wiring

`agentic_core/adg/analysis/RepairRoute.py::_RELATION_TO_ROUTE` contains all 4 antipattern edge_kinds (`broad_exception_catch`, `silent_exception_swallow`, `log_and_swallow`, `return_none_swallow`) at lines 121-141, each routed to `("ManualReview", "governance", "high", <description>)`. `route_violations()` falls back to `edge_kind` lookup at line 160 when `relation_type` doesn't match.

### W3 — violation_edges filter + defect table

`tools/generate/generate_full_adg.py` at line 539 builds `violation_edges` including antipattern edges whose `edge_kind in _high_antipattern_kinds` AND whose `source_file` matches `_critical_layer_prefixes`. `_print_defect_table` is invoked with `sqlite_path=paths.sqlite` at line 1006; the function was M.4-extracted to `tools/generate/reporting/reports.py` and now reads counts from the violations table.

The plan's `_check_p2_defects` (non-blocking) was subsumed by the **blocking** `_check_p2_ratchet()` gate in `tools/generate/validation/gates.py::207`, wired into `generate_full_adg.py::576`. Blocking is a stronger guarantee than the plan's non-blocking proposal.

### W4 — Tests (Done)

Regression tests landed 2026-04-22:

- `tests/unit/agentic_core/adg/analysis/test_repair_route_antipatterns.py` — 7 tests covering `_RELATION_TO_ROUTE` registration (4 edge_kinds parametrized), route shape (ManualReview/governance/high), `route_violations()` edge_kind fallback, and skip-on-unknown behavior.
- `tests/unit/agentic_core/adg/artifact/test_multi_writer_severity.py` — 59 tests extracting the CASE expression from `multi_writer.py` at test time (keeps test in lockstep with production) and running it against an in-memory SQLite. Covers Tier-1 agent-safety (CRITICAL), HIGH-class in production (HIGH), HIGH-class in downgrade paths (LOW), HIGH-class outside production (MEDIUM), always-MEDIUM kinds, unknown kinds (LOW fallthrough), and violates relation (ELSE branch → MEDIUM).

Total: **66 passed, 0 failed, 0 skipped** (`pytest tests/unit/agentic_core/adg/ -q` on 2026-04-22). No guardian exemptions added; no production code touched.
