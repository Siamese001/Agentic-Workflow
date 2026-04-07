---
description: RCA workflow for ADG SQLite (mcp1), Redis (mcp10), Sequential Thinking (mcp7), PyTest (mcp11), and OTel (mcp9) MCP failures
---

# MCP Failure RCA & Auto-Fix Workflow

Invoke with `/mcp-failure-rca`. Automatically diagnoses and fixes ADG MCP and Redis MCP failures, then resumes the original prompt. **Grep is NEVER a fallback** — MCP must be restored.

---

## STEP 0: Triage — identify which MCP is down

Call `adg_health` MCP tool. If it returns an error, ADG MCP is down → go to STEP 1.
Call `mcp12_redis_health` MCP tool. If it returns an error, Redis is down → go to STEP 3.
Call `mcp11_discover_tests` with path=`tests`. If it errors → go to STEP 7.
If all healthy → nothing to fix, return to original prompt.

---

## STEP 1: RCA the ADG MCP failure

The most common causes in priority order:

**A) Missing method in SQLiteBackend** (current known bug: `_init_graph_store`)
// turbo
```
python -c "from tools.adg.core.sqlite_backend import SQLiteBackend; b = SQLiteBackend(); print('OK')"
```
If `AttributeError: ... has no attribute '_init_graph_store'` → go to STEP 2A.
If `RuntimeError: No ADG SQLite file found` → go to STEP 2B.
If import error → go to STEP 2C.

**B) Check MCP server log for root cause**
// turbo
```
python -c "import os; p=os.path.expanduser('~/adg_mcp_server.log'); lines=open(p).readlines()[-30:]; print(''.join(lines))"
```

---

## STEP 2A: Fix missing method in SQLiteBackend

The method `_init_graph_store` was called but not defined. Add the stub:

Edit `tools/adg/core/sqlite_backend.py` — add after `__init__`:
```python
def _init_graph_store(self) -> None:
    """Initialize optional SQLiteGraphStore. Currently a no-op stub."""
    self._graph_store = None
```

Then clear stale bytecode:
// turbo
```
python -c "import pathlib; [p.unlink() for p in pathlib.Path('tools/adg/core/__pycache__').glob('sqlite_backend*.pyc')]"
```

Verify fix:
// turbo
```
python -c "from tools.adg.core.sqlite_backend import SQLiteBackend; b = SQLiteBackend(); print('FIXED')"
```

Then restart the MCP server by asking Windsurf to reload MCP connections (Cmd/Ctrl+Shift+P → "Reload MCP"). Re-run `adg_health` — if ok, return to original prompt.

---

## STEP 2B: Fix — no ADG SQLite file found

ADG artifacts are missing. Regenerate:
```
python tools/generate_full_adg.py
```
Wait for completion, then re-verify with STEP 1 command.

---

## STEP 2C: Fix import error in ADG MCP

Check what the import error is from the server log (STEP 1B). Common causes:
- Missing dependency: `pip install <package>`
- Broken module path: check `tools/adg/core/__init__.py` exports

---

## STEP 2D: Fix — Pydantic validation crash (ADGNode/ADGEdge id is int, not str)

Symptom: `adg_nodes_by_layer`, `adg_nodes_by_file`, `adg_node` all return:
```
{"status": "error", "message": "1 validation error for ADGNode\nid\n  Input should be a valid string [type=string_type, input_value=1, input_type=int]"}
```

Root cause: SQLite stores `id` as INTEGER PRIMARY KEY. `ADGNode.id` is typed `str`. Missing coercion in `sqlite_backend.py`.

Fix: verify `_row_to_node` and `_row_to_edge` static methods exist in `tools/adg/core/sqlite_backend.py`:
// turbo
```
python -c "
from tools.adg.core.sqlite_backend import SQLiteBackend
import glob, pathlib
dbs = sorted(glob.glob('artifacts/adg/adg_indexed_*.sqlite'))
b = SQLiteBackend(pathlib.Path(dbs[-1]))
nodes = b.get_nodes_by_layer('L0', 2)
print('id types:', [type(n.id).__name__ for n in nodes])
"
```
Expected: `id types: ['str', 'str']`

If failing, the `_row_to_node`/`_row_to_edge` helpers are missing — re-apply fix from `tools/adg/core/sqlite_backend.py` lines 71-85.

Then clear bytecode and restart MCP:
// turbo
```
python -c "import pathlib; [p.unlink() for p in pathlib.Path('tools/adg/core/__pycache__').glob('*.pyc')]"
```
Restart the ADG MCP server in Windsurf (Ctrl+Shift+P → Reload MCP).

---

## STEP 3: RCA Redis MCP failure

// turbo
```
python -c "import redis; r=redis.Redis(); print(r.ping())"
```

- `True` → Redis is up, MCP config is broken → check `.windsurf/mcp_config.json` redis entry
- `ConnectionRefusedError` → Redis server is down → go to STEP 4

---

## STEP 4: Fix — Redis server down

// turbo
```
python tools/adg/redis_health_check.py --auto-start
```

If auto-start fails:
```
sc start Redis
```
Then verify: `redis-cli ping` returns `PONG`.

After Redis is up, reload ADG Redis cache:
```
python tools/adg/adg_redis_ingest.py --force
```

---

## STEP 5: Verify both MCPs healthy, resume original prompt

Call `adg_health` — must return `"status": "ok"`.
Call `mcp9_redis_health` — must return `"status": "ok"`.

Once both healthy, **return to and resume the original user prompt** that triggered this workflow. Do NOT use grep as a substitute — the original prompt must be re-executed with ADG MCP as the primary query tool.

---

## Known Failure Registry

| Error | Root Cause | Fix Step |
|---|---|---|
| `'SQLiteBackend' has no attribute '_init_graph_store'` | Method deleted during refactor, call site left | 2A |
| `RuntimeError: No ADG SQLite file found` | ADG artifacts missing or wrong dir | 2B |
| `ConnectionRefusedError` on Redis | Redis server not running | 4 |
| MCP health returns error after code change | Stale `.pyc` bytecode | Clear `__pycache__` in affected module |
| `ADGNode.id Input should be str, got int` | SQLite INTEGER PRIMARY KEY not coerced to str | 2D |
| `ADGEdge.id Input should be str, got int` | Same root cause — edge ids also int | 2D |
| `mcp7_sequentialthinking` hangs indefinitely | Windows: `npx` not resolved — must use `npx.cmd` in config | 6A |
| `mcp7_sequentialthinking` hangs indefinitely | Zombie node.exe processes from prior failed starts | 6B |
| `mcp7_sequentialthinking` returns error immediately | npx/Node.js environment broken or not installed | 6C |
| Any npx-based MCP hangs (filesystem, memory, deepwiki, brave) | Same root cause — `npx` vs `npx.cmd` on Windows | 6A |
| `mcp11_discover_tests` errors | pytest_server.py missing or pytest not installed | 7 |
| `mcp9_otel_status` errors | otel_mcp_server.py missing or OTel collector not running | 8 |

---

## STEP 6: Fix — Sequential Thinking MCP hang or error

**Symptom:** `mcp7_sequentialthinking` call hangs indefinitely or returns an error.

**A) Check Windows npx resolution (most common cause):**
// turbo
```
python -c "import subprocess; r=subprocess.run(['where', 'npx'], capture_output=True, text=True, check=False); print(r.stdout.strip())"
```
On older Windsurf versions, `npx` required `npx.cmd` on Windows. Current Windsurf resolves `npx` correctly.

Fix: ensure `config/mcp_servers.yaml` uses `command: npx` (NOT `npx.cmd`). Run sync: `python tools/adg/sync_yaml_to_global.py`. Then health check: `python ops_scripts/ci/mcp_health_check.py`.

**B) Check if the process is hung (zombie node.exe):**
// turbo
```
python -c "import subprocess; r=subprocess.run(['tasklist', '/fi', 'imagename eq node.exe', '/fo', 'csv'], capture_output=True, text=True, check=False); print(r.stdout)"
```
If multiple `node.exe` processes → kill stale ones:
```
python -c "import subprocess; subprocess.run(['taskkill', '/f', '/im', 'node.exe'], check=False)"
```

**C) Restart MCP in Windsurf:**
Ctrl+Shift+P → "Reload MCP" → verify `mcp7_sequentialthinking` responds.

**D) If MCP cannot be restored:**
Proceed WITHOUT sequential thinking for current task.
Note in response: `[ST-MCP UNAVAILABLE — proceeding without structured decomposition]`
Do NOT use grep or text search as a substitute.

---

## STEP 7: Fix — PyTest MCP error

**Symptom:** `mcp11_discover_tests` or `mcp11_run_tests` errors.

**A) Verify pytest server script exists:**
// turbo
```
python -c "import pathlib; p=pathlib.Path('tools/mcp/pytest_server.py'); print('EXISTS' if p.exists() else 'MISSING')"
```

**B) Check pytest is installed:**
// turbo
```
python -m pytest --version
```

**C) Restart MCP in Windsurf:** Ctrl+Shift+P → "Reload MCP".

---

## STEP 8: Fix — OTel MCP error

**Symptom:** `mcp9_otel_status` errors or returns unhealthy.

**A) Verify OTel server script exists:**
// turbo
```
python -c "import pathlib; p=pathlib.Path('tools/otel/otel_mcp_server.py'); print('EXISTS' if p.exists() else 'MISSING')"
```

**B) Check OTel collector connectivity:**
// turbo
```
python -c "import urllib.request; urllib.request.urlopen('http://localhost:4318/health', timeout=3)"
```
If connection refused → OTel collector is not running. This is acceptable if OTel is not in use.

**C) Restart MCP in Windsurf:** Ctrl+Shift+P → "Reload MCP".

---

## Constitutional constraint

**Grep CANNOT be used as a fallback when ANY MCP is down.** Per constitutional §2.3 fail-closed rule: stop work, fix the MCP, then resume. This workflow IS the fix path.

**This applies to ALL MCPs:** ADG SQLite, Redis, Sequential Thinking, PyTest, OTel.
