# MCP Operator Guide

## Memory MCP HTTP Route

Primary Codex route:

```bash
python -m tools.mcp.launch_memory_http_mcp
```

Configured URL:

```json
"url": "http://127.0.0.1:8766/mcp"
```

The legacy `tools/memory/adg_memory_server.py` stdio server remains a fallback
or probe target only. It is not the primary Codex route.

Verification:

```bash
python -m tools.mcp.launch_memory_http_mcp --preflight-only --json
python scripts/governance/probe_mcp_http_server.py --url http://127.0.0.1:8766/mcp --tool memory_health --json
python scripts/governance/stress_codex_mcp_transport.py --server-id memory --url http://127.0.0.1:8766/mcp --tool memory_health --count 500 --output artifacts/mcp/stress/memory_http_stress.json
```

Recovery order:

1. Run `python scripts/governance/diagnose_codex_mcp_transport.py --server memory --json`.
2. If classification is `http_service_down`, restart only the repo-managed Memory HTTP MCP service.
3. If classification is `http_protocol_unhealthy`, inspect `artifacts/mcp/memory_http_service.jsonl` and rerun the direct HTTP probe.
4. If classification is `codex_http_route_unproven`, reload/reconnect the Codex MCP client once, then call live `mcp__memory.memory_health` or `mcp__memory.mem_process_identity`.
5. Do not accept process liveness, heartbeat files, direct SQLite, port-open, curl, or tools/list as active-session callability proof. The route is green only after the PostToolUse callability ledger records fresh `route_kind=http` proof for `http://127.0.0.1:8766/mcp`.

## pytest_mcp

## Health / Verification

```bash
python tools/mcp/pytest_server.py --help   # fails fast if MCP SDK missing
python -c "import tools.mcp.pytest_server" # import smoke test
```

## Subprocess Timeouts

| Operation | Timeout |
|-----------|---------|
| `discover_tests` (collection) | 30 s |
| `run_tests` (execution) | Caller-supplied, capped at 300 s |
| `analyze_test_coverage` | 120 s |
| `pytest --version` check | 15 s |
| `coverage --version` check | 10 s |

On `TimeoutExpired`, every handler returns `isError=True` and a human-readable message. JUnit XML temp files are deleted on timeout.

## Failure Classes (pytest exit codes)

| Exit code | Meaning | `isError` |
|-----------|---------|-----------|
| 0 | All tests passed | `False` |
| 1 | Some tests failed | `False` (caller inspects output) |
| 2 | Interrupted | `True` |
| 3 | Internal pytest error | `True` |
| 4 | Usage / bad arguments | `True` |
| 5 | No tests collected | `False` (zero-count result) |

## Path Confinement

All `path` and `test_path` arguments are resolved against `REPO_ROOT` and rejected if they would escape it. Symlink traversal is blocked post-`resolve()`. Absolute paths outside the repo root are also rejected.

## Expression Injection Guard

`-k` (keywords) and `-m` (markers) values are validated against `^[\w\s\-()/\[\],'\"=!<>]+$`. Shell-dangerous characters (`;`, backtick, `$`, `|`, `&`, null byte) cause an immediate `isError=True` response without spawning a subprocess.

## CWD / REPO_ROOT Assumption

All subprocess calls set `cwd=REPO_ROOT`. `REPO_ROOT` is resolved at module import time as `Path(__file__).resolve().parent.parent.parent`. This means the server must be located at `<repo>/tools/mcp/pytest_server.py`.

## JUnit XML Temp Files

Each `run_tests` call writes a uniquely named `.pytest_results_<uuid>.xml` in `REPO_ROOT`. The file is deleted after parsing. On timeout or parse error, cleanup is attempted via `unlink()`. Leftover files (unexpected crash) are safe to delete manually.

## Known Limitations

- HTML coverage reports are written to disk and not returned inline.
- `get_test_details` does a static text scan; it does not execute the test or resolve imports.
- `MAX_OUTPUT_SIZE` is 50 000 characters; output beyond that is truncated with a notice.
