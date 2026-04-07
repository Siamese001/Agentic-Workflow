# RCA: Dual Sources of Truth for P2-P4 Defect Counts

**Status:** IN PROGRESS  
**Date:** 2026-04-07  
**Severity:** MEDIUM — Governance/Operational Clarity  
**Reporter:** Cascade  

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

### 4.1 Immediate (Documentation)

- [ ] Update ADG architecture docs to clarify dual-source design
- [ ] Add inline comments in `generate_full_adg.py` explaining which table is used for which gate
- [ ] Create runbook: "Understanding P2 Counts: violations vs edges"

### 4.2 Short-term (Governance Alignment)

- [ ] Audit: Which gates use `violations` vs `edges` table
- [ ] Standardize on single source per gate type:
  - **Ratchet gates** → `edges` table (operational metrics)
  - **Violation reports** → `violations` table (governance tracking)
- [ ] Rename or namespace to clarify: `op_p2_count` vs `gov_p2_count`

### 4.3 Long-term (Consolidation)

- [ ] Evaluate merging scanners: Can anti-pattern scanner write to edges table directly?
- [ ] Or: Create unified `defects` view that unions both sources with provenance

---

## 5. Verification

Post-fix validation:
- [ ] Documentation updated with dual-source explanation
- [ ] Gate code comments reference correct table
- [ ] Dashboard shows both counts with clear labels

---

## 6. Prevention

- Add schema documentation to `artifacts/adg/*.sqlite` explaining table purposes
- Include "data lineage" comments in SQL queries showing table source
- Architectural decision: Single source of truth for each metric type

---

**Next Steps:**
1. Document current state (complete)
2. Align team on intended design (pending)
3. Implement consolidation plan (pending)
