# ================================================
# PHASE 1 — STRUCTURAL REORGANIZATION TEST SUITE
# ================================================

## 1.1 — YAML GOVERNANCE TESTS

### TEST CASE 1.1-YAML-01 — Load SSoT successfully
Action:
- Run Phase 1 on any folder.
Expected:
- YAML loads without exception.
- Domain hierarchy populated.
- Naming rules applied.
Pass:
- `phase01_log.json` shows `yaml_load = success`.

---

### TEST CASE 1.1-YAML-02 — Protected path enforcement
Create file:
```
06_data/semantic_cache/tmp.py
```
Expected:
- Phase 1 MUST NOT move, delete, or rewrite.
- Mapping entry should include:
  - `reason = protected_path`
  - `action = skip`
Pass:
- File remains untouched.
- Appears in `phase01_mapping.json` with protected flag.

---

## 1.2 — FILENAME PREFIX ENFORCEMENT

### TEST CASE 1.2-PFX-01 — Valid RG prefix
File:
```
rg_main.py
```
Expected:
- Routed into `apps_rg/...`.
- `prefix = rg` recognized.
Pass:
- Mapping shows correct domain and routed path.

---

### TEST CASE 1.2-PFX-02 — Missing prefix fallback
File:
```
apps/main.py
```
Expected:
- Routed to:
  ```
  _unassigned/prefix_violation/main.py
  ```
- Must not appear in any RG/LIC domain.
Pass:
- Mapping contains reason: `missing_prefix`.

---

## 1.3 — DOMAIN ROUTING TESTS

### TEST CASE 1.3-ROUTE-01 — Cognitive engine routing
File:
```
planner_router.py
```
Expected:
- Domain: `01_agentic_core`
- Layer: `L3_orchestration`
- Subfolder: `routing_retry_task/`
Pass:
- Final destination path matches predicted canonical location.

---

### TEST CASE 1.3-ROUTE-02 — Blocked L/P patterns for support domains
Place file:
```
05_config/L1_cognition/test.py
```
Expected:
- Illegal L1/L2/L3/L4/L5 structure in a support domain.
- Routed to:
  ```
  _unassigned/support_violation/05_config/L1_cognition/test.py
  ```
Pass:
- Appears in `support_violation` bucket.

---

## 1.4 — COMPLETENESS & ORPHAN DETECTION

### TEST CASE 1.4-ORPH-01 — Unassigned fallback routing
File:
```
misc_notes.tmp
```
Expected:
- Sent to `_unassigned/...`
- Listed in `phase01_orphans_report.json`.
Pass:
- Orphan entry logged.

---

### TEST CASE 1.4-ORPH-02 — No file left behind
Run Phase 1 on full repo.
Expected:
- All files appear under domains `01`–`10` OR protected paths OR `_unassigned`.
- No unexpected top-level directories.
Pass:
- `phase01_post_validation.json` shows `no_orphans = true`.

---

# END OF PHASE 1 TEST SUITE
