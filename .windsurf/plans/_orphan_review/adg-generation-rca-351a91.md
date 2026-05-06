# ADG Generation Failure — RCA & Fix Plan

Single-line fix: change `parents[1]` to `parents[2]` in `tools/generate/generate_full_adg.py` line 47.

---

## Root Cause

**File:** `tools/generate/generate_full_adg.py:47`

```python
ROOT = Path(__file__).resolve().parents[1]   # BUG: resolves to tools/
```

The script was **moved** from `tools/` → `tools/generate/` at some point (confirmed by the backup at `tools/adg_backups/generate_full_adg_backup_20260324_190130.py` which used the same `parents[1]` when the file lived one level shallower).

**Path resolution with current file location:**

| Expression | Resolves To |
|---|---|
| `parents[0]` | `C:\Git\Agentic-Workflow\tools\generate` |
| `parents[1]` | `C:\Git\Agentic-Workflow\tools` ← **WRONG (current)** |
| `parents[2]` | `C:\Git\Agentic-Workflow` ← **CORRECT repo root** |

## Failure Chain (Two Cascading Bugs)

### Bug 1 — Zero Files Scanned
```
ROOT = C:\Git\Agentic-Workflow\tools\
ADGStaticScanner(repo_root=ROOT)  →  scans tools/ subtree only
Result: 0 Python files match expected agentic_core/apps_*/system_learning layout
Output: "ADG FATAL: zero files parsed — scan aborted"
```

### Bug 2 — Redis Ingest Path Double-Nesting
```
ingest_script = ROOT / "tools" / "adg" / "adg_redis_ingest.py"
              = C:\Git\Agentic-Workflow\tools\tools\adg\adg_redis_ingest.py  ← DOES NOT EXIST
Actual path  = C:\Git\Agentic-Workflow\tools\adg\adg_redis_ingest.py
Output: RuntimeError: Redis ingest script not found: ...tools\tools\adg\adg_redis_ingest.py
```

## Fix

**File:** `C:\Git\Agentic-Workflow\tools\generate\generate_full_adg.py`  
**Line 47** — change `parents[1]` → `parents[2]`

```python
# BEFORE (wrong)
ROOT = Path(__file__).resolve().parents[1]

# AFTER (correct)
ROOT = Path(__file__).resolve().parents[2]
```

This single change fixes both bugs:
- Bug 1: Scanner now receives correct repo root → scans all Python files
- Bug 2: `ROOT / "tools" / "adg" / "adg_redis_ingest.py"` resolves correctly

## Verification

After fix, run:
```
python tools/generate/generate_full_adg.py --full
```

Expected:
- `[ADG] Modules: <N>` — non-zero (previously 6,000+)
- `[ADG] Edges: <N>` — non-zero (previously 692,000+)
- `[ADG] Redis ingest complete` — no RuntimeError

## Impact

- No other files need changes
- No downstream code affected (ROOT is local to this script)
- Fix is backward compatible

## Wave Summary

| Wave | Phase | Focus | Est. Tokens | Status | Success Criteria |
|------|-------|-------|-------------|--------|-----------------|
| 1 | P1 | Fix `parents[1]` → `parents[2]` in line 47 | 5K 🟢 | Pending | ADG generates with non-zero modules/edges |
| 1 | P2 | Verify full ADG generation succeeds | 5K 🟢 | Pending | All evidence floors pass, Redis hot |
