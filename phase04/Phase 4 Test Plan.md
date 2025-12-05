# ================================================
# PHASE 4 — CRYPTOGRAPHIC FREEZE TEST SUITE
# ================================================

## 4.1 — HASHING TESTS

### TEST CASE 4.1-HS-01 — Correct hash sensitivity (1-byte change)
Prep:
- Run Phase 4 on baseline codebase → produce freeze report `freeze_1.json`.
- Modify a single file by exactly 1 byte (e.g., add a space or newline).
- Run Phase 4 again → `freeze_2.json`.
Expected:
- Only the entry for the modified file changes:
  - `sha256` differs.
  - `size_bytes` may differ (if you added/removed bytes).
- All unaffected files retain identical hash and size entries.
Pass:
- Diff between `freeze_1.json` and `freeze_2.json` shows changes only for that file.

---

### TEST CASE 4.1-HS-02 — Deterministic re-freeze on unchanged FS
Prep:
- Run Phase 4 on a codebase → `freeze_a.json`.
- Without changing any files, run Phase 4 again → `freeze_b.json`.
Expected:
- `freeze_a.json` and `freeze_b.json` are byte-identical.
- File ordering in the report is stable (e.g., lexicographic by path).
Pass:
- `diff freeze_a.json freeze_b.json` shows no differences.

---

## 4.2 — DIRECTORY COVERAGE TESTS

### TEST CASE 4.2-CV-01 — All files included in freeze
Prep:
- Run Phase 4 on `TARGET_ROOT`.
- Separately, list all files under `TARGET_ROOT` using:
  ```bash
  find TARGET_ROOT -type f | sort
  ```
Expected:
- Every non-excluded file path under `TARGET_ROOT` appears exactly once in the freeze report.
- No extra paths in freeze that do not exist on disk.
Pass:
- Sorted list of paths from freeze report matches `find` output (after removing excluded directories).

---

## 4.3 — EXCLUSION TESTS

### TEST CASE 4.3-EX-01 — Exclude semantic cache & snapshots from freeze
Directories to exclude:
- `06_data/semantic_cache`
- `06_data/phase3_snapshots` (or equivalent snapshot root)

Prep:
- Ensure these directories exist and contain files.
- Run Phase 4.
Expected:
- No entry in the freeze report for:
  - Any file under `06_data/semantic_cache/**`
  - Any file under `06_data/phase3_snapshots/**`
- All other files under `TARGET_ROOT` still included.
Pass:
- A search over the freeze report (by path prefix) finds zero matches for excluded directories.

---

# END OF PHASE 4 TEST SUITE
