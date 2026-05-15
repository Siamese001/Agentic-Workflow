# G2b — MCP as Transport

Every MCP server configured in `.windsurf/mcp_config.json`, classified by ingress/egress role and network actor.

**ADG snapshot**: `artifacts/adg/adg_indexed_04172026_0611.sqlite` (04172026_0611).
**Config source**: `.windsurf/mcp_config.json` (12 servers).

## 1. Transport taxonomy

| Transport type | Meaning |
|---|---|
| `stdio-loopback` | Windsurf launches a subprocess; Windsurf ↔ subprocess JSON-RPC over stdio. No network from the repo. |
| `stdio-loopback + external-egress` | stdio to subprocess; subprocess itself makes external HTTP to a third-party service. |
| `https-external` | Windsurf ↔ remote MCP URL directly. No subprocess in the repo. |
| `binary-subprocess` | Windsurf launches an external binary (not repo python). |

## 2. Per-server records

### MCP-01 — `adg_sqlite`

- **Transport**: stdio-loopback
- **Subprocess**: `python -u -m tools.adg.mcp.server`
- **Repo entry point**: `tools/adg/mcp/server.py`
- **External egress from the subprocess**: **none** (reads local SQLite, Redis cache at `localhost:6379`)
- **Env keys injected by Windsurf**: `ADG_DIR`, `ADG_REDIS_URL`, `PYTHONPATH`, `PYTHONUNBUFFERED`
- **Ingress**: Cursor Agent tool calls → stdio → ADG query
- **Egress**: loopback (adg sqlite file + redis localhost)
- **Auth**: none (stdio + localhost Redis, unauthenticated)
- **Classification**: pure loopback

### MCP-02 — `memory`

- **Transport**: stdio-loopback
- **Subprocess**: `python -u tools/memory/adg_memory_server.py`
- **Repo entry point**: `tools/memory/adg_memory_server.py`
- **External egress**: **none** (SQLite + local Redis)
- **Env keys injected**: `ADG_REDIS_URL`, `MEMORY_DB`, `PYTHONPATH`, `PYTHONUNBUFFERED`
- **Env keys read from repo code**: `MEMORY_DB`, `ADG_REDIS_URL`
- **Auth**: none
- **Classification**: pure loopback

### MCP-03 — `vector_db`

- **Transport**: stdio-loopback
- **Subprocess**: `python -u tools/mcp/vector_db_server.py`
- **Repo entry point**: `tools/mcp/vector_db_server.py`
- **External egress**: **conditional** — if `VECTOR_DB_ALLOW_MODEL_DOWNLOAD=1` the subprocess may fetch from HuggingFace Hub (see EGRESS-HF-HUB-01). Default `0` → offline.
- **Env keys injected**: 20+ keys under `VECTOR_DB_*` namespace + `HF_HUB_OFFLINE=1`, `TOKENIZERS_PARALLELISM=false`
- **Auth**: none
- **Classification**: loopback by default; conditional external egress when model download enabled

### MCP-04 — `otel_mcp`

- **Transport**: stdio-loopback
- **Subprocess**: `python -u tools/otel/otel_mcp_server.py`
- **Repo entry point**: `tools/otel/otel_mcp_server.py`
- **External egress**: **none** — server reads local runtime-ADG trace artefacts; forwarding to an OTel collector is done by `apps_shared/utils/open_telemetry_tracing_adapter_util.py`, NOT by this MCP server
- **Auth**: none
- **Classification**: pure loopback

### MCP-05 — `redis`

- **Transport**: stdio-loopback
- **Subprocess**: `python -u tools/mcp/redis_mcp_server.py`
- **Repo entry point**: `tools/mcp/redis_mcp_server.py`
- **External egress**: **local Redis only** (`localhost:6379` default). Recorded as part of EGRESS-REDIS-01 bucket.
- **Env keys injected**: `REDIS_DB`, `REDIS_HOST`, `REDIS_PORT`, `REDIS_TIMEOUT`, `PYTHONPATH`, `PYTHONUNBUFFERED`
- **Auth**: none (localhost), `REDIS_PASSWORD` optional
- **Classification**: loopback + localhost-Redis egress

### MCP-06 — `pytest_mcp`

- **Transport**: stdio-loopback
- **Subprocess**: `python -u tools/mcp/pytest_server.py`
- **External egress**: **none** (runs pytest in a subprocess; no network)
- **Auth**: none
- **Classification**: pure loopback

### MCP-07 — `enhanced_http`

- **Transport**: stdio-loopback **+ external-egress**
- **Subprocess**: `python -u tools/mcp/enhanced_http_server.py` (FastMCP + register_http_tools)
- **Repo entry point**: `tools/mcp/enhanced_http_server.py` → `tools/mcp/http_mcp/tools.py`
- **External egress**: **yes, by design.** This is the MCP that Cursor Agent uses to make programmatic HTTP calls to arbitrary URLs (per constitutional MCP Authority rule: "enhanced_http is the sole authority for ALL programmatic HTTP calls").
- **HTTP client**: `aiohttp` (see `tools/mcp/http_mcp/client.py`)
- **Retry posture** (per tool signatures): `retries: int = 3` default, `timeout: int = 30` default, `verify_ssl: bool = True`, `follow_redirects: bool = True`.
- **Auth passthrough**: accepts `auth` argument in tool calls; no persistent credential storage. User / Cursor Agent supplies credentials per request.
- **Env keys read**: several `HTTP_*` constants via `tools/mcp/http_mcp/constants.py::env_truthy`.
- **Classification**: ingress from Cursor Agent, egress to arbitrary URLs. **This is the only code path by which Cursor Agent is SUPPOSED to make HTTP calls; all repo-internal services should use canonical gateways (SovereignLLMGateway, EmbeddingSovereignAgent).**

### MCP-08 — `filesystem`

- **Transport**: binary-subprocess (Node)
- **Launcher**: `node .windsurf/scripts/filesystem_mcp_launcher.js <AGENTIC_REPO_ROOT>`
- **Server**: `@modelcontextprotocol/server-filesystem` (installed globally via npm)
- **External egress**: **none** (pure local FS)
- **Auth**: scope-locked to repo root (per `_comment` in mcp_config.json)
- **Classification**: pure loopback (local FS only)

### MCP-09 — `notion`

- **Transport**: stdio-loopback **+ external-egress**
- **Subprocess**: `cmd /c npx -y @notionhq/notion-mcp-server` (Node)
- **External egress**: **yes** — Node subprocess makes HTTPS calls to `api.notion.com`
- **Env keys injected**: `NOTION_TOKEN` (bearer token propagated from OS env)
- **Auth**: `token_bearer_env` (NOTION_TOKEN)
- **Classification**: stdio-loopback from Windsurf's perspective; external-egress from the subprocess. Treated as loopback in `egress_points.yaml` because the Node subprocess is the network actor (egress invisible to repo Python code).

### MCP-10 — `task_manager`

- **Transport**: stdio-loopback
- **Subprocess**: `cmd /c npx -y @blizzy/mcp-task-manager stdio`
- **External egress**: **none** (task state is in subprocess memory)
- **Auth**: none
- **Classification**: pure loopback

### MCP-11 — `GitKraken`

- **Transport**: binary-subprocess
- **Binary**: `${env:GITKRAKEN_GK_PATH} mcp --host=windsurf --source=gitlens --scheme=windsurf`
- **External egress**: **conditional** — GitKraken binary may contact GitHub / GitLab / Azure / Bitbucket APIs for PR / issue operations. Credentials managed inside GitKraken, not via repo env vars.
- **Auth**: managed by GitKraken binary; not visible to repo
- **Classification**: binary-subprocess with opaque external egress. Out-of-scope for env-key catalogue.

### MCP-12 — `deepwiki`

- **Transport**: **https-external**
- **URL**: `https://mcp.deepwiki.com/mcp`
- **External egress**: **yes** — Windsurf connects directly to the remote MCP endpoint. No repo subprocess involved.
- **Auth**: none (per config; may be unauthenticated service)
- **Classification**: external. Recorded as `EGRESS-MCP-DEEPWIKI-01` in `egress_points.yaml`.

## 3. Summary matrix

| # | Server | Transport | Subprocess actor | External egress? | Egress target |
|---|---|---|---|---|---|
| 01 | adg_sqlite | stdio-loopback | python | no | — |
| 02 | memory | stdio-loopback | python | no | — |
| 03 | vector_db | stdio-loopback | python | conditional | HF Hub (gated) |
| 04 | otel_mcp | stdio-loopback | python | no | — |
| 05 | redis | stdio-loopback | python | yes (localhost) | Redis localhost |
| 06 | pytest_mcp | stdio-loopback | python | no | — |
| 07 | enhanced_http | stdio-loopback + egress | python | **yes (any URL)** | arbitrary (by-design) |
| 08 | filesystem | binary-subprocess | node | no | — |
| 09 | notion | stdio-loopback + egress | node/npx | yes | api.notion.com |
| 10 | task_manager | stdio-loopback | node/npx | no | — |
| 11 | GitKraken | binary-subprocess | gk.exe | conditional | GitHub/GitLab/Azure/Bitbucket |
| 12 | deepwiki | https-external | (remote) | yes | mcp.deepwiki.com |

## 4. Key findings

- **Repo Python code has no MCP-ingress path**. MCPs exist only to let Cursor Agent (Windsurf IDE) call into the repo's tools. The repo never acts as a client of its own MCP servers at runtime.
- **11 of 12 MCP servers are locally-launched** by Windsurf: **9 via stdio-loopback** (`adg_sqlite`, `memory`, `vector_db`, `otel_mcp`, `redis`, `pytest_mcp`, `enhanced_http`, `notion`, `task_manager`) and **2 via binary-subprocess** (`filesystem` Node launcher, `GitKraken` gk.exe). Network actors are the subprocesses themselves, not repo Python.
- **2 servers have by-design external egress from their subprocesses** (`enhanced_http`, `notion`). Both are sanctioned transport surfaces — `enhanced_http` is the constitutional sole-authority for programmatic HTTP (per MCP Authority rule); `notion` is a cooperative PM integration. Neither is part of the repo's LLM inference or embedding pipelines.
- **`deepwiki` is the only pure-external MCP** (no subprocess; Windsurf ↔ remote URL). Repo code does not reference it.
- **`GitKraken` binary-subprocess** has opaque credentials and opaque egress to git-hosting providers. Out of scope for repo env-key catalogue; G4b may record as a side-channel integration surface.

## 5. MCP loopback vs real external egress — disambiguation

The catalogue in `egress_points.yaml` intentionally splits:

| egress_points.yaml ID | Subsumes |
|---|---|
| `EGRESS-MCP-DEEPWIKI-01` | MCP-12 only (true external MCP URL) |
| `EGRESS-MCP-LOOPBACK-BUCKET` | MCP-01 through MCP-11 as a bucket. Individual MCP-internal network egress is tracked upstream (vector_db → HF Hub, redis MCP → local Redis, notion → api.notion.com, GitKraken → git hosts) in their respective provider records or, where the egress is opaque to the repo (GitKraken), flagged here for transparency. |

## 6. Retry / rate-limit posture for MCP transports

| Server | Retry (subprocess side) | Rate limit observed |
|---|---|---|
| enhanced_http | `retries: int = 3` default per tool call | no |
| notion | npx / `@notionhq/notion-mcp-server` internals | unknown |
| GitKraken | binary internal | unknown |
| adg_sqlite / memory / otel_mcp / pytest_mcp / redis / task_manager / filesystem / vector_db | none needed (loopback) | n/a |
| deepwiki (external) | MCP client default | unknown |

## 7. Hand-off

- G3 should represent `enhanced_http` as an explicit named egress pipeline ("Cursor Agent HTTP passthrough") to avoid confusion with SovereignLLMGateway.
- G4b should record MCP-injected env keys (`VECTOR_DB_*`, `REDIS_*`, `ADG_REDIS_URL`, `MEMORY_DB`, `NOTION_TOKEN`) as `mcp_runtime_env` class, distinct from repo-runtime env.
- G7 traceability: map `enhanced_http` tool surface to v1.4 atom space — no current atom explicitly scopes "IDE programmatic HTTP"; B7 candidate deferred.
