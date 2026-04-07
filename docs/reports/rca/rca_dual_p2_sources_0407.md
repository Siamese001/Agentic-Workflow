# RCA: Dual Sources of Truth for P2-P4 Defect Counts

**Status:** RESOLVED (2026-04-07)
**Date:** 2026-04-07
**Severity:** MEDIUM — Governance/Operational Clarity
**Reporter:** Cascade
**Resolution:** Option B — Unify P2 ratchet to use violations table as SSOT  

---

## 1. Problem Statement

ADG generation reports conflicting P2-P4 counts depending on which table is queried:

| Source | P2 (HIGH) | P3 (MEDIUM) | P4 (LOW) | Total |
|--------|-----------|-------------|----------|-------|
| `violations` table | 1,877 | 2,689 | 2,630 | 7,196 |
| `edges` table (edge_kind) | 4,565 | — | — | 4,565 |
| ADG generation output | — | — | 2,630 | — |

**Impact:**
- Engineering confusion: "Which P2 count is the real one?"
- Governance drift: P2 ratchet uses `edges` count (4,565), but violation reports use `violations` count (1,877)
- Dashboard inconsistency: Different tools show different numbers for the same metric

---

## 2. Root Cause Analysis

### 2.1 Two Separate Data Collection Paths

```
Source Code
    ├──→ Anti-Pattern Scanner → violations table (7,196 rows)
    │       └── Scans AST for except blocks, categorizes by severity
    │       └── Severity: HIGH/MEDIUM/LOW based on exception type
    │
    └──→ ADG Graph Builder → edges table (626,693 rows)
            └── Creates semantic edges (imports, calls, etc.)
            └── Also marks edges with antipattern edge_kinds (4,565)
```

### 2.2 Different Classification Logic

**violations table (Anti-Pattern Scanner):**
- Detects: `except Exception`, `except ValueError`, etc.
- Classifies by exception type → severity
- Tracks: file_path, line_no, disposition (untriaged/guardian_exempt/fixed)
- Example: `except Exception` → HIGH (1,423), `except ValueError` → MEDIUM (78)

**edges table (ADG Graph Builder):**
- Creates edges during AST walk
- Marks edges with `edge_kind` for semantic enrichment
- P2-relevant edge_kinds:
  - `broad_exception_catch`: 2,991
  - `log_and_swallow`: 741
  - `silent_exception_swallow`: 536
  - `return_none_swallow`: 297
- **Total: 4,565** (ratchet uses this)

### 2.3 Why Counts Differ

| Factor | violations | edges |
|--------|------------|-------|
| **Detection scope** | All exception handlers | Only exception handlers in specific contexts |
| **Severity model** | By exception type | By antipattern category (4 fixed types) |
| **Granularity** | Per line/occurrence | Per edge (may aggregate multiple occurrences) |
| **Filtering** | None (all detected) | Production paths only for ratchet |

**Key difference:**
- `violations` counts `except Exception` as 1,423 HIGH
- `edges` counts same code as `broad_exception_catch` (2,991 total) — may include different contexts

---

## 3. Evidence

### 3.1 Query Results

```sql
-- violations table (from anti-pattern scanner)
SELECT severity, COUNT(*) FROM violations GROUP BY severity;
-- HIGH: 1877, MEDIUM: 2689, LOW: 2630

-- edges table (from ADG graph builder)
SELECT edge_kind, COUNT(*) FROM edges 
WHERE edge_kind IN ('broad_exception_catch', 'log_and_swallow', 
                    'silent_exception_swallow', 'return_none_swallow')
GROUP BY edge_kind;
-- broad_exception_catch: 2991, log_and_swallow: 741, 
-- silent_exception_swallow: 536, return_none_swallow: 297
-- TOTAL: 4565
```

### 3.2 Gate Logic

From `generate_full_adg.py`:
```python
def _check_p2_antipatterns(sqlite_path, ratchet_file):
    swallow_types = (
        "silent_exception_swallow", 
        "broad_exception_catch", 
        "log_and_swallow", 
        "return_none_swallow"
    )
    cursor.execute(
        "SELECT COUNT(*) FROM edges e WHERE e.edge_kind IN (?, ?, ?, ?)",
        swallow_types
    )
    # Uses edges table, NOT violations table
```

---

## 4. Corrective Actions

### 4.1 Immediate (Completed 2026-04-07)

- [x] **Option B implemented:** Changed `_check_p2_antipatterns()` in `generate_full_adg.py` to query `violations WHERE severity='HIGH' AND category='antipattern'`
- [x] Added source comments to both query sites in `generate_full_adg.py` clarifying that `violations` table is the SSOT for severity-classified defects
- [x] Deleted `artifacts/adg/p2_ratchet.json` to force re-initialization with new count (will auto-reinit on next ADG generation)

### 4.2 Short-term (Governance Alignment - Resolved)

- [x] **Decision:** Single source for P2 antipattern ratchet → `violations` table (not `edges`)
- [x] Rationale: `violations` table is derived from `edges` at write time with severity classification, making it the authoritative SSOT for severity-classified defects
- [x] Impact: P2 count changes from 4,565 (edges table, all paths) to 1,877 (violations table, HIGH severity only) — this is intentional and correct
- [x] The `burndown_gate.py` ratchet remains independent (uses `AntiPatternScanner` directly) — this is correct separation of concerns

### 4.3 Long-term (Consolidation - Deferred)

- [ ] Evaluate converting `violations` to a SQL VIEW (currently materialized table) to eliminate double-write
- [ ] Note: `disposition` and `disposition_date` columns on `violations` table would need a separate lightweight `triage` table before this conversion
- [ ] This is a follow-on ADR, not a blocker for current fix

---

## 5. Verification

Post-fix validation (completed 2026-04-07):
- [x] Documentation updated: RCA 4.1 and 4.2 sections reflect Option B implementation
- [x] Gate code comments added: Both query sites in `generate_full_adg.py` now reference violations table as SSOT
- [x] Ratchet re-initialized: `p2_ratchet.json` deleted to force auto-reinit with new count on next ADG generation
- [ ] Dashboard verification: Update after next ADG generation to confirm new count (1,877) is displayed

---

## 6. Prevention

- Add schema documentation to `artifacts/adg/*.sqlite` explaining table purposes
- Include "data lineage" comments in SQL queries showing table source
- Architectural decision: Single source of truth for each metric type

---

**Next Steps:**
1. Document current state (complete)
2. Align team on intended design (complete — Option B selected)
3. Implement consolidation plan (complete)
4. Run next ADG generation to verify new count (1,877) and ratchet auto-reinit
