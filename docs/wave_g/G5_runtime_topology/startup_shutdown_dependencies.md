# G5 — Startup, Shutdown, and Dependency Ordering

wave: G5
produced_at: 2026-04-18
adg_snapshot: artifacts/adg/adg_indexed_04182026_0814.sqlite
upstream_artefacts:
  - docs/wave_g/G3_pipelines/pipeline_catalogue.yaml
  - docs/wave_g/G4_storage_infra/storage_catalogue.yaml
  - docs/wave_g/G4b_control_plane/defaults_and_reload_policy.md
  - .mcp.json

ADG snapshot timestamp used: `04182026_0814`.

## 1) Recommended startup sequence (local operator path)

1. Start/verify local Redis service (`localhost:6379`).
2. Verify ADG cache freshness (`python tools/adg/adg_redis_ingest.py --check`).
3. If stale/cold, regenerate and ingest (`python tools/generate_full_adg.py` then `python tools/adg/adg_redis_ingest.py --force`).
4. Start legacy editor MCP lifecycle (spawns local stdio/binary MCP servers from `.mcp.json`).
5. Verify core MCP health:
   - `adg_health`
   - `redis_health`
   - `readiness` (vector_db)
   - `otel_status` + `otel_server_info`
6. Launch app runtime (`python -m apps_*`) as needed.
7. Optional sidecar: `python ops_scripts/dev_tools/start_metrics_sidecar.py` for Prometheus scrape.

## 2) Startup dependency graph (high-level)

- `PROC-REDIS-LOCAL` is an upstream bridge for ADG cache, memory import, and redis MCP.
- `PROC-ADG-SNAPSHOT` must produce/point to latest `adg_indexed_<ts>.sqlite` before topology-sensitive analysis.
- `PROC-ADG-SQLITE-MCP` depends on snapshot availability; Redis optional for cache-hit acceleration.
- `PROC-VECTOR-DB-MCP` depends on Chroma path and embedding model warm/readiness state.
- App runtimes depend on `agentic_core` import path and may run ADG bootstrap checks at startup.

## 3) Shutdown order (safe)

1. Stop app runtime processes.
2. Stop optional sidecar/ancillary local daemons.
3. Stop legacy editor (terminates local MCP subprocesses).
4. Optionally keep Redis running for session continuity.

For ADG full regeneration with lock concerns:
- call `adg_close_connections`
- run generation/ingest
- call `adg_reopen_connections`

## 4) Restart patterns by surface

| Surface | Known restart mode |
|---|---|
| App runtimes (`apps_*`) | manual process restart |
| Python/Node MCP subprocesses | legacy editor restart (or process recycle via IDE) |
| ADG serving snapshot | `adg_reload` can repoint without full process restart |
| Redis local service | OS/service restart |
| Metrics sidecar | manual restart |
| DeepWiki external endpoint | unknown/operator external |
| GitKraken binary MCP | unknown/operator external |

## 5) Process-start/import-time dependencies from G4b that affect startup

- `import_time` knobs require process restart to take effect (not hot-swappable):
  - `VECTOR_DB_*` model/timeouts/cache knobs
  - core constants-based cache toggles (`USE_REDIS_CACHE`, `GRACEFUL_DEGRADATION`, etc.)
- `process_start` knobs require process/subprocess restart:
  - `MEMORY_DB`, `ADG_REDIS_URL`, `REDIS_HOST/PORT/DB`, OTEL endpoint vars
- `per_call` toggles can mutate posture immediately and are high-risk:
  - `EGRESS_GUARD_DISABLED`, `DISABLE_RUNTIME_MUTATION_GUARD`, archival auto-approve knobs

## 6) Readiness and freshness probes (required set)

- ADG: `adg_health`, `adg_status`, `adg_stale_guard.py`
- Redis: `redis_health`, hot sentinel check in `adg_redis_ingest --check`
- Vector DB: `readiness`, `vector_stats`
- OTel MCP/runtime ADG: `otel_status`, `otel_server_info`
- Dashboard aggregation: `degraded_component_flags` from dashboard aggregate snapshots

## 7) Biggest startup blockers

1. Redis unavailable or cold when ADG-dependent workflows require hot cache.
2. ADG snapshot mismatch between cache sentinel and MCP-served sqlite.
3. Vector model cold/warmup delay causing first-query latency spikes.
4. Missing MCP env injections (notably `NOTION_TOKEN` for notion MCP).
5. Import bootstrap side-effects (`apps_rg/bootstrap_runtime.py`, optional shims in `apps_exec`) masking underlying dependency misses.

## 8) Ambiguities explicitly preserved

- Exact process cleanup behavior for every legacy editor MCP child is launcher-specific and only partially codified; unknown where not directly specified.
- External endpoint downtime semantics (`deepwiki`, provider APIs) are outside repo-managed restart control.
