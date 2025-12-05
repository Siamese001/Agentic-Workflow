# ================================================
# PHASE 2 — SEMANTIC DIFF & PLAN GENERATION TEST SUITE
# ================================================

## 2.1 — SEMANTIC MATCHING TESTS

### TEST CASE 2.1-SM-01 — Exact hash match
Setup:
- Provide a file whose content already exists in semantic cache with identical hash **H**.
Expected:
- Diff classification: `hash_match`
- Plan MUST include:
  ```
  op: canonical_rewrite_component
  hash: H
  ```
Pass:
- Operation appears in `phase02_plan.json`.

---

### TEST CASE 2.1-SM-02 — Symbol match fallback
Input file:
```python
class Planner: ...
```
Archive contains same class but different hash.
Expected:
- Detected: `semantic_symbol_match`
- Rewrite op generated referencing original component(s).
Pass:
- Mapping lists symbol match and rewrite op present.

---

### TEST CASE 2.1-SM-03 — No semantic match
Input:
```
README.txt
```
Expected:
- Diff classification: `no_cache`
- No rewrite op for this file.
Pass:
- Operation list excludes it.

---

## 2.2 — STRUCTURAL DIFF TESTS

### TEST CASE 2.2-ST-01 — SSoT mismatch detection
Place a file in a directory NOT present in YAML SSoT.
Expected:
- Appears in `fs_only_files` list.
- Phase 2 still generates full plan successfully.
Pass:
- No blocking exceptions; file reported in mismatches.

---

## 2.3 — OPERATION GENERATION TESTS

### TEST CASE 2.3-OP-01 — Rewrite-all guarantee
For **any** matched file (hash or semantic symbol match):
Expected:
- Always emit:
  ```
  canonical_rewrite_component
  ```
Pass:
- All matched files have rewrite ops in `phase02_plan.json`.

---

### TEST CASE 2.3-OP-02 — Deterministic sort
Run Phase 2 twice with no changes.
Expected:
- Plan JSON is byte-identical.
Pass:
- `diff plan1.json plan2.json` shows no difference.

---

## 2.4 — IMPORT MAP TESTS

### TEST CASE 2.4-IMP-01 — Import detection
Input:
```python
from utils.helper import f
```
Expected:
- Plan contains import reference:
  ```
  imports: ["utils.helper"]
  ```
- Used later by Phase 3 for import rewrite.
Pass:
- Import appears in component metadata or plan entry.

---

# END OF PHASE 2 TEST SUITE
