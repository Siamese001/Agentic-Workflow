# MCP Server Standardization Analysis

## All 12 MCP Servers — Health Verified (2026-04-13)

| # | Server | Type | Pattern | Status |
|---|--------|------|---------|--------|
| 1 | adg_sqlite | Python | FastMCP + `@mcp.tool()` + `mcp.run()` | **Working** |
| 2 | memory | Python | FastMCP + `@mcp.tool()` + `mcp.run()` | **Working** |
| 3 | redis | Python | FastMCP + `@mcp.tool()` + `mcp.run()` | **Working** |
| 4 | otel_mcp | Python | FastMCP + `@mcp.tool()` + `mcp.run()` | **Working** (after stdin fix) |
| 5 | vector_db | Python | FastMCP + `@mcp.tool()` + `mcp.run()` | **Working** (rewritten from low-level API) |
| 6 | enhanced_http | Python | Low-level Server + `anyio.run()` | **Working** (candidate for migration) |
| 7 | pytest_mcp | Python | Low-level Server + `anyio.run()` | **Working** (candidate for migration) |
| 8 | filesystem | Node.js | npm package | External — no changes needed |
| 9 | GitKraken | Binary | gk.exe | External — no changes needed |
| 10 | task_manager | Node.js | npx package | External — no changes needed |
| 11 | deepwiki | HTTP | Remote URL | External — no changes needed |
| 12 | notion | Node.js | npx package | External — no changes needed |

## Shared Modules Created

### `tools/mcp/mcp_bootstrap.py` — Standardized Server Initialization
Replaces 15-30 lines of duplicated boilerplate per server:
- Repo-root `sys.path` bootstrap (idempotent)
- `logging.basicConfig(stream=sys.stderr, force=True)` — never stdout
- `TOKENIZERS_PARALLELISM=false`, `PYTHONUNBUFFERED=1` env safety
- FastMCP import with clear error message
- `create_mcp_server(name, instructions)` factory
- `run_server(mcp)` standardized entry point

### `tools/mcp/mcp_subprocess.py` — MCP-Safe Subprocess Execution
Replaces repeated subprocess.run boilerplate that caused MCP hangs:
- Forces `stdin=DEVNULL` (never inherit parent stdin)
- Forces `stdout=PIPE, stderr=PIPE` (never pollute JSON-RPC)
- Requires `timeout=` (constitutional §14)
- Root cause: GitHub modelcontextprotocol/python-sdk#671

### `tools/mcp/mcp_deferred_loader.py` — Lazy Resource Loading
Replaces ad-hoc ThreadPoolExecutor patterns:
- `DeferredLoader(name, factory, timeout=N)` — load once, cache forever
- Thread-safe (concurrent.futures), never blocks asyncio event loop
- `.get()` returns None on failure, `.require()` raises helpful error
- Used by: vector_db (embedding model), otel_mcp (gRPC tracer), future servers

## Duplicated Patterns Found Across 7 Python Servers

| Pattern | Files with duplication | Shared module |
|---------|----------------------|---------------|
| `sys.path.insert(0, repo_root)` | All 7 | `mcp_bootstrap.REPO_ROOT` |
| `logging.basicConfig(stream=sys.stderr)` | All 7 | `mcp_bootstrap` (auto) |
| `from mcp.server.fastmcp import FastMCP` + try/except | 5 of 7 | `mcp_bootstrap.create_mcp_server()` |
| `mcp.run(transport="stdio")` | 5 of 7 | `mcp_bootstrap.run_server()` |
| `os.environ["TOKENIZERS_PARALLELISM"]` | 2 of 7 | `mcp_bootstrap` (auto) |
| `subprocess.run(..., stdin=DEVNULL, stdout=PIPE, stderr=PIPE)` | 2 of 7 | `mcp_subprocess.safe_run()` |
| `ThreadPoolExecutor + future.result(timeout=N)` | 3 of 7 | `mcp_deferred_loader.DeferredLoader` |
| Low-level `Server` + manual `call_tool` dispatch | 2 of 7 | **Eliminate — migrate to FastMCP** |

## Migration Priority

### Already migrated
- **vector_db** — rewritten from low-level to FastMCP + shared modules

### Should migrate (working but non-standard)
- **enhanced_http** — uses low-level `Server` + `anyio.run()`, 990 lines
- **pytest_mcp** — uses low-level `Server` + `anyio.run()`, 700 lines

### Already standard (use bootstrap when convenient)
- **adg_sqlite** — already FastMCP, logs to file instead of stderr
- **memory** — already FastMCP, clean pattern
- **redis** — already FastMCP, clean pattern
- **otel_mcp** — already FastMCP, subprocess calls fixed

## Anti-Patterns That Caused Failures

| Anti-Pattern | Effect | Fix |
|-------------|--------|-----|
| Low-level `Server` API with manual `call_tool` dispatch | Verbose, error-prone | Use `FastMCP` + `@mcp.tool()` |
| `anyio.run(main)` entry point | Works but inconsistent | Use `mcp.run(transport="stdio")` |
| `asyncio.ensure_future()` for background tasks | Mixing asyncio with anyio runtime | Use `DeferredLoader` (sync, threaded) |
| `asyncio.Lock` for model loading | Blocks event loop during load | Use `DeferredLoader` (thread-safe) |
| `subprocess.run(capture_output=True)` in stdio server | Deadlocks on Windows — child inherits stdin | Use `mcp_subprocess.safe_run()` |
| `logging.basicConfig()` without `stream=sys.stderr` | May default to stdout, corrupts JSON-RPC | Use `mcp_bootstrap` |
| Module-level heavy imports (sentence_transformers) | Blocks MCP handshake (3.8s+) | Use `DeferredLoader` |
