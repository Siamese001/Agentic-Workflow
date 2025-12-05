# ================================================
# PHASE 0.5 — SEMANTIC CACHE REBUILD TEST SUITE
# ================================================

## 0.5.1 — PYTHON COMPONENT EXTRACTION TESTS

### TEST CASE 0.5-PY-01 — Extract classes, functions, constants
Input file:
```python
class Planner:
    def plan(self): pass

def helper(): pass

CONFIG = {"mode": "test"}
```
Expected:
- Components:
  - class::Planner
  - func::helper
  - assign::CONFIG
- All components have valid span_start/span_end.
- Components do not overlap.
- Bucket inference populated.
Pass criteria:
- `<hash>.semantic.json` contains exactly 3 components.

---

### TEST CASE 0.5-PY-02 — Syntax error fallback
Input file with syntax error:
```python
def broken(
    print("x")
```
Expected:
- AST parse fails → fallback to blob component.
- Semantic JSON contains exactly 1 component.
- Component spans entire file.

---

### TEST CASE 0.5-PY-03 — Multi-class file
Input:
```python
class A: ...
class B: ...
```
Expected:
- Two class components.
- Graph includes `co_defined` edge between A and B.

---

## 0.5.2 — NON-PYTHON EXTRACTION TESTS

### TEST CASE 0.5-NP-01 — JSON configuration
Input: `config.json`
Expected:
- One component, `kind: config`.
- Span covers full file.
- Bucket = 05_config.

---

### TEST CASE 0.5-NP-02 — Markdown file
Expected:
- One component (`kind: document`).
- Span covers whole file.
- Included in semantic cache.

---

## 0.5.3 — ARTIFACT GENERATION TESTS

### TEST CASE 0.5-ART-01 — Required artifacts exist
For file hash **H**, verify all:
- `ast/H.ast`
- `golden/H.golden.json`
- `embeddings/H.embedding`
- `integrity/H.integrity.json`
- `meta/H.meta.json`
- `semantic/H.semantic.json`
Pass: None missing.

---

### TEST CASE 0.5-ART-02 — Deterministic ordering
Run Phase 0.5 twice with no changes.
Expected:
- `component_graph.json` identical.
- All semantic files identical.
- No diff in `.semantic_cache/`.

---

## 0.5.4 — POINTER TESTS

### TEST CASE 0.5-PTR-01 — Pointer validity
Verify for each pointer JSON:
- Correct component hash.
- Valid component_id.
- Correct canonical_root + canonical_relative.
Pass if all fields resolve.

---

### TEST CASE 0.5-PTR-02 — Invalid pointer detection
Manually corrupt a pointer.
Expected:
- Phase05Validator fails key `K11`.

---

# END OF PHASE 0.5 TEST SUITE
