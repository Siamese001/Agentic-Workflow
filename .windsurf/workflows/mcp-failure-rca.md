---
description: RCA workflow for ADG SQLite (`adg_sqlite`), Redis (`redis`), PyTest (`pytest_mcp`), and OTel (`otel_mcp`) MCP failures. Sequential Thinking MCP is permanently retired — do not attempt recovery.
---

> **Cursor Agent workflow note:** This workflow is a reusable procedural lane, not always-on policy. Use it to hold staged retrieval, evidence gathering, execution order, and verification steps that would otherwise overload rules. For deep research, separate retrieval, quote extraction, synthesis, and final verification into distinct phases.

# MCP Failure RCA & Auto-Fix Workflow

Invoke with `/mcp-failure-rca`. Automatically diagnoses and fixes ADG MCP and Redis MCP failures, then resumes the original prompt. **Grep is NEVER a fallback** — MCP must be restored.

---

## STEP 0: Triage — identify which MCP is down

Call the `adg_health` tool (server: `adg_sqlite`). If it returns an error, ADG MCP is down → go to STEP 1.
Call the `redis_health` tool (server: `redis`). If it returns an error, Redis is down → go to STEP 3.
Call the `discover_tests` tool (server: `pytest_mcp`) with path=`tests`. If it errors → go to STEP 7.
If all healthy → nothing to fix, return to original prompt.

> **Load-order note:** The numeric tool prefixes Windsurf assigns (e.g. `mcp8_redis_health`) shift whenever a server is added or removed from `mcp_config.json`. Use the server names above as the stable identifiers; resolve the live prefix from the tool list visible in your session.

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

Call `adg_health` (server: `adg_sqlite`) — must return `"status": "ok"`.
Call `redis_health` (server: `redis`) — must return `"status": "ok"`.

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
| `sequentialthinking` tool (any error) | `@modelcontextprotocol/server-sequential-thinking` permanently retired — do not recover | 6 (tombstone) |
| Any npx-based MCP hangs (filesystem, memory, deepwiki, brave) | Same root cause — `npx` vs `npx.cmd` on Windows | Restart MCP in Windsurf |
| `discover_tests` errors (server: `pytest_mcp`) | pytest_server.py missing or pytest not installed | 7 |
| `otel_status` errors (server: `otel_mcp`) | otel_mcp_server.py missing or OTel collector not running | 8 |

---

## STEP 6: Sequential Thinking MCP — PERMANENTLY RETIRED

**Do not attempt to recover the Sequential Thinking MCP.** It has been permanently retired.

**Why**: stdio transport fragility on Windows, zombie node.exe processes, no reliable timeout, oversized opaque tool surface, architectural mismatch with Cursor Agent's native reasoning.

**Replacement**: Use the structured reasoning pattern instead:
- Workflow: `/structured-reasoning`
- Skill: `.windsurf/skills/structured-reasoning/SKILL.md`
- Reference: `docs/mcp/sequential-thinking-replacement.md`

**If you see `sequentialthinking` tool calls in old code or logs**: These are stale references to the retired `@modelcontextprotocol/server-sequential-thinking` package. Update them to use the SR_INTAKE + SR_PLAN pattern described in the skill.

**If zombie node.exe processes remain from old invocations:**
// turbo
```
python -c "import subprocess; r=subprocess.run(['tasklist', '/fi', 'imagename eq node.exe', '/fo', 'csv'], capture_output=True, text=True, check=False); print(r.stdout)"
```
Kill stale processes only if confirmed to be Sequential Thinking remnants:
```
python -c "import subprocess; subprocess.run(['taskkill', '/f', '/im', 'node.exe'], check=False)"
```

---

## STEP 7: Fix — PyTest MCP error

**Symptom:** `discover_tests` or `run_tests` errors from the `pytest_mcp` server.

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

**Symptom:** `otel_status` errors or returns unhealthy from the `otel_mcp` server.

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
