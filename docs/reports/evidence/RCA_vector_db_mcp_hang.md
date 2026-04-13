# RCA: Vector DB MCP Server Hang

**Status**: RESOLVED  
**Date**: 2026-04-13  
**Severity**: P0 — blocks all semantic search and embedding queries  
**File**: `tools/mcp/vector_db_server.py`

---

## Symptom

The `vector_db` MCP server appeared to hang indefinitely when invoked from
Windsurf.  `list_collections` sometimes worked, but any tool requiring the
embedding model (`query_collection`, `embed_text`, `semantic_search`,
`vector_stats`) timed out or never returned.

---

## Root Causes (6 bugs, composite failure)

### Bug 1 — Module-level `sentence_transformers` import blocks MCP handshake
- **Impact**: CRITICAL — **3.8 s** blocked before `stdio_server()` could start
- `from sentence_transformers import SentenceTransformer` at module top
  imported torch, transformers, tokenizers, numpy, safetensors.
- The MCP stdio protocol requires a fast handshake.  Windsurf's client timed
  out waiting for the `initialize` response.
- **Evidence**: Timing test showed 4.375 s before MCP ready (vs 0.703 s after fix).

### Bug 2 — `print()` to stdout in KeyboardInterrupt handler
- **Impact**: HIGH — corrupts JSON-RPC protocol stream
- `print("Vector DB MCP Server stopped by user")` wrote to stdout.
- On MCP stdio transport, **stdout is exclusively for JSON-RPC messages**.
  Any other output corrupts the framing and kills the connection.
- **Ref**: [ChatForest MCP Debugging Guide](https://chatforest.com/guides/debugging-mcp-servers/)

### Bug 3 — `TOKENIZERS_PARALLELISM` spawns subprocesses inheriting stdio
- **Impact**: CRITICAL — corrupts JSON-RPC protocol stream
- HuggingFace `tokenizers` library spawns parallel processes by default.
  These child processes inherit stdin/stdout file descriptors from the parent.
  Any output from child processes corrupts the MCP protocol.
- **Ref**: [python-sdk#817](https://github.com/modelcontextprotocol/python-sdk/issues/817)

### Bug 4 — tqdm progress bars during model load saturate stderr pipe
- **Impact**: MEDIUM — blocks background thread on Windows
- `SentenceTransformer` constructor emits tqdm progress bars ("Loading
  weights: 100%|█████|") to stderr.  On Windows, anonymous pipe buffers are
  4–64 KB.  Rapid tqdm updates can fill the buffer; if Windsurf doesn't drain
  stderr fast enough, the write blocks, stalling the model load thread and
  starving the asyncio event loop.

### Bug 5 — Tool handlers block on `_model_lock` during prewarm
- **Impact**: HIGH — tools hang 10–20 s
- `_ensure_embedding_model()` acquires `self._model_lock`.  The prewarm
  coroutine holds this lock for the entire duration of the import + model
  load (~6–20 s).  Any tool call during this window blocks on the lock,
  causing the event loop to stall — no MCP messages are processed.

### Bug 6 — No graceful degradation when model not ready
- **Impact**: MEDIUM — opaque error messages
- Tools returned "Failed to load embedding model" with no indication of
  whether the model was still loading or had failed permanently.

---

## Fixes Applied

| Bug | Fix | Line(s) |
|-----|-----|---------|
| 1 | Defer `sentence_transformers` import to `_load_model()` (background thread) | L33–35, L280–296 |
| 2 | `print()` → `logger.info()` in KeyboardInterrupt handler | L1170 |
| 3 | `os.environ["TOKENIZERS_PARALLELISM"] = "false"` at module top | L55–59 |
| 4 | `os.environ["TQDM_DISABLE"] = "1"` during import/load, restored after | L287–295 |
| 5 | Replace `await _ensure_embedding_model()` in tool handlers with non-blocking `_model_ready()` check; return status message instantly | L706–711, L775–780, L903–908, L969–974 |
| 6 | Added `_model_ready()` and `_model_status_message()` methods with clear loading/failed status | L361–374 |

### Config changes
- `mcp_config.json`: `HF_HUB_OFFLINE=1`, `VECTOR_DB_MODEL_LOAD_TIMEOUT=120`

---

## Web Research Sources

| Source | Key Finding |
|--------|-------------|
| [ChatForest: Debugging MCP Servers](https://chatforest.com/guides/debugging-mcp-servers/) | "stdout is sacred" — any non-JSON-RPC output kills connection |
| [AWS MCP #1086](https://github.com/awslabs/mcp/issues/1086) | Exact same bug: SentenceTransformer model load times out MCP startup. Fix: async load + increase timeout |
| [python-sdk #817](https://github.com/modelcontextprotocol/python-sdk/issues/817) | multiprocessing/subprocess + STDIO = hang (inherited file descriptors) |
| [python-sdk #671](https://github.com/modelcontextprotocol/python-sdk/issues/671) | Tool execution hangs in stdio mode with subprocess calls |
| [SO: SentenceTransformer slow import](https://stackoverflow.com/questions/79350206/) | `from sentence_transformers import SentenceTransformer` takes 2–120 s |

---

## Verification

### Before fix
- Module-level exec: **4.375 s** → MCP handshake blocked
- Tool calls during prewarm: **blocked 10–20 s** on model lock

### After fix
- Module-level exec: **0.703 s** → MCP handshake completes immediately
- Tool calls during prewarm: **return instantly** with "model still loading" message
- Tool calls after prewarm (~10–20 s): **work normally** with full embeddings

### Best practices implemented
1. **Zero stdout output** — all logging to stderr, no print() to stdout
2. **Deferred heavy imports** — sentence_transformers, torch loaded in background thread
3. **No subprocess spawning** — `TOKENIZERS_PARALLELISM=false`
4. **Suppressed tqdm** — `TQDM_DISABLE=1` during model load
5. **Non-blocking tool handlers** — fail fast with clear message instead of blocking
6. **Background prewarm** — model loads async after MCP handshake completes
7. **`HF_HUB_OFFLINE=1`** — zero network calls during model load
8. **Configurable timeout** — `MODEL_LOAD_TIMEOUT` env var (default 120s)
