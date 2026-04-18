# G2b — Provider / Gateway / Egress / Auth Boundary Map

## 1. Sub-wave ID, title, one-line purpose

**G2b** — *Provider / Gateway / Egress / Auth Boundary Map*. Enumerate every external-facing boundary (provider SDK wrappers, gateway clients, MCP loopback transports, auth/env-key consumers, retry posture) and produce a canonical egress catalogue with hard SSOT coordinates.

## 2. Inputs

- **ADG snapshot (frozen)**: `artifacts/adg/adg_indexed_04172026_0611.sqlite` (04172026_0611; 83,319 nodes / 638,815 edges; `adg_health` = healthy, `graph_projection.stale=false`). Same snapshot as G1/G1b/G2.
- **G0 planning**: `runtime_scope_map.md`, `repo_surface_inventory.md`, `output_contracts.md` (egress-point schema §"Egress point schema (G2b)"), `wave_g_execution_plan.md`, `dependency_and_risk_register.md`.
- **G1**: `component_inventory.yaml` (2014 `agentic_core/` modules), `cross_cutting_classification.md`.
- **G1b**: `app_inventory.yaml` (8 apps), `app_to_core_bindings.md`, `adapter_patterns.md`.
- **G2**: `import_edge_matrix.md` (bridge candidate `cache/redis_cache_client.py` fan_in=fan_out=70), `canonical_request_walk.md`, `boundary_violations.md` (dynamic-wiring sites).
- **Wave F v1.4 canonical**: `docs/wave_e/99_integration_v14/canonical/*` (used only for citation; not mutated).
- **Repo evidence scan** (ADG-first + literal env-key scan; constitutionally allowed for literal matches):
  - 269 `os.getenv` / `os.environ` reads across 154 unique env keys in `agentic_core/`, `apps_*/`, `infrastructure/`, `tools/`.
  - HTTP-library import scan: `requests` (4), `aiohttp` (4), `openai` (2), `anthropic` (2), `google.generativeai` (3), `neo4j` (1), `chromadb` (39), `redis` (19).
  - MCP server catalogue: `.windsurf/mcp_config.json` (12 servers).

## 3. Outputs

- `README.md` — this index.
- `provider_inventory.md` — per-provider wrappers, selection surfaces, consumer modules.
- `egress_points.yaml` — canonical egress-point catalogue conforming to G0 schema.
- `env_key_consumer_map.md` — all 154 env keys mapped to consumer modules (names only; no values).
- `mcp_as_transport.md` — MCP servers classified as loopback vs external, with ingress/egress semantics.

## 4. Stop condition

Met.

- Every egress point catalogued: **12** entries in `egress_points.yaml` (6 external, 3 localhost/internal, 3 MCP-transport buckets), each record carries all 10 required schema fields.
- Every `os.getenv` / `os.environ[...]` read mapped to consumer modules: 269 reads / 154 unique keys across 4 repo roots. Full table in `env_key_consumer_map.md`.
- MCP loopback documented in `mcp_as_transport.md` — 9 stdio-loopback servers + 1 HTTPS external (`deepwiki`) + 1 binary subprocess (`GitKraken`) + 1 ingress-perspective FastMCP (`enhanced_http` both ingresses tool calls from Windsurf AND egresses HTTP from the repo).
- Real external egress distinguished from MCP loopback transport and local-only stubs (see §5 of `provider_inventory.md` for the canonical matrix).
- G2 findings consumed explicitly:
  - **Gateway/interface live subset** (G2 `seam_usage_report.md` §2): `agentic_core/interfaces/gateway.py` is ingress-side (Kong/Envoy/Custom tracing header injection per `agentic_core/gateway/api_gateway_integration.py`), **not a provider egress wrapper** — fully disambiguated in `provider_inventory.md` §6.
  - **Cache/Redis bridge chokepoint** (G2 `boundary_violations.md` §Bridge candidates): `agentic_core/cache/redis_cache_client.py` at fan_in=fan_out=70 is the single largest external-dependency bridge — recorded as `EGRESS-REDIS-01` in `egress_points.yaml`.
  - **App→L3 `qwen_vllm` imports** (G2 unexpected edges, 30 edges / 6 apps): localhost vLLM inference server is the egress target — recorded as `EGRESS-QWEN-VLLM-LOCAL-01`. Per `hardened_vllm_client.py`, posture has full retry + circuit breaker.
  - **App→L4 `vllm_routing_predicates` imports** (22 edges / 5 apps): these are **config predicates, not egress** — classified as configuration coupling in `provider_inventory.md` §7. Not a new egress point; noted as B7-G2b-01.
  - **Dynamic-wiring sites that affect provider selection** (G2 §Class 3): 3 app-side `importlib.import_module` call-sites in `apps_eval/integrations/governed_eval_exception.py`, `apps_research/__main__.py`, `apps_underwriting_ai/integrations/governed_uw_exception.py` — recorded as dynamic-provider-selection surfaces in `provider_inventory.md` §8.
- **No secret values exposed** — only env-key names appear anywhere in G2b artefacts. Verified by spot-scan of every YAML / MD file.
- **Retry posture reported honestly**: known for SovereignLLMGateway, model_router_types, hardened_vllm_client, hardened_gemini_executor_types, enhanced_http MCP, GoogleSearchClient. **Unknown** for Neo4j store and raw Redis client (recorded as `unknown`, not fabricated).
- **Provider selection is dynamic** for the multi-provider router (`MultiProviderRouterAgent` moved to `agentic_core/L5_safety/guardrails/multi_provider_router_agent.py` per `infrastructure/sdks_mcps/__init__.py` migration note; runtime selection by `apps_shared/types/model_router_types.py` `ModelRouter` class). Decision surface recorded explicitly.

## 5. Risks encountered during execution

- **R-G-02 (dynamic provider selection)**: partially mitigated. `ModelRouter` in `apps_shared/types/model_router_types.py` selects provider at runtime from `TaskComplexity` + budget. Specific selection logic is data-driven; static analysis cannot fully enumerate "which provider runs for which task". Recorded the dispatch-table shape but not every branch — G3 pipeline trace should expand.
- **Pinecone referenced, not imported**: `PINECONE_INDEX_NAME` appears in `apps_shared/utils/etl_pipeline_util.py` as an env-key read, but `import pinecone` has **zero occurrences** repo-wide. Classified as a **config stub** egress (declared, not wired). Flagged as B7-G2b-02.
- **Chromadb is 39 files but NOT external egress**: ChromaDB is a local embedded vector DB (reads `data/cache/chromadb/`). Listed under local storage in G4, not here — explicitly excluded from egress_points.yaml.
- **`GOOGLE_API_KEY` has dual meaning**: 8 files read it — some for Google GenAI (Gemini), one for Google Custom Search (`apps_lic/tools/GoogleSearchClient.py`), some for validators/utilities (reading the key as a config toggle, not invoking any API). G2b splits these consumer sets explicitly in `env_key_consumer_map.md`.
- **`create_openai_client` / `create_anthropic_client` / `create_vertex_client` in `infrastructure/sdks_mcps/__init__.py` are declared as "minimal wrappers for migration"**: real production routing goes through `SovereignLLMGateway` (L2 enforcement) and `MultiProviderRouterAgent` (L5 guardrail). Records this split as "canonical gateway" vs "direct wrappers".
- **R-G-03 (grep drift)**: avoided. Dependency discovery used ADG MCP; env-key / HTTP-library enumeration uses literal-string matching only.
- **`EGRESS_GUARD_DISABLED` environment kill-switch**: `agentic_core/L2_execution/enforcement/network_egress_guard.py` has a disable toggle. Recorded as a policy-bypass switch in `env_key_consumer_map.md` with severity note.

## 6. B7 candidates surfaced

- **B7-G2b-01** — L4 `vllm_routing_predicates` used by 5 apps. This is config, not egress, but the pattern "apps reach into L4 config predicates" was flagged in G2 (unexpected edge) and propagates here as an architectural concern for gateway ownership. Deferred to G4b.
- **B7-G2b-02** — `PINECONE_INDEX_NAME` env key read but `pinecone` not imported. Either declared-but-never-wired (dead config) or pending integration. G6 to decide.
- **B7-G2b-03** — `infrastructure/sdks_mcps/__init__.py` `create_*_client` wrappers are the only place raw `openai` / `anthropic` / `google.generativeai` SDKs are imported outside `apps_shared/utils/providers_google_genai_client_util.py`. If the intended architecture is "only SovereignLLMGateway egresses to providers", these direct wrappers are a bypass. G7 to decide.
- **B7-G2b-04** — `agentic_core/gateway/api_gateway_integration.py` imports `requests` directly (for Kong / Envoy admin-API health checks). If the "sole egress seam" rule applies repo-wide, this is an exception. If ingress-side gateway admin calls are carved out, it's expected. v1.4 has no atom scoping ingress-gateway admin traffic.
- **B7-G2b-05** — Neo4j egress has unknown retry posture. `agentic_core/L4_state/enforcement/neo4j_store.py` uses the `neo4j` driver; no wrapping retry / circuit-breaker found. G6 to verify or add.
- **B7-G2b-06** — `EGRESS_GUARD_DISABLED` kill-switch exists but has no audit trail. When set, it disables `network_egress_guard.py`. No v1.4 atom covers "disabling egress guard MUST be audited". G7 owns.

## 7. Hand-off note for G3 and G4b

- **For G3 (pipelines)**: the LLM-egress pipeline is "App → ModelRouter → SovereignLLMGateway → {OpenAI | Anthropic | Vertex | Local vLLM}"; the embedding pipeline is "EmbeddingSovereignAgent → {Gemini embedding | OpenAI embedding | BAAI/bge-m3 local}"; the search pipeline is "apps_lic → GoogleSearchClient → Google Custom Search". G3 should anchor these as named pipelines with `egress_point_id` references from `egress_points.yaml`.
- **For G4b (config knobs)**: the 154-env-key inventory is the **seed set** for G4b config-knob catalogue. G4b must classify each key as `provider_config` / `runtime_tunable` / `feature_flag` / `secret` and re-home the list under G4b's schema. G2b only catalogues consumers; G4b catalogues semantics.
- **For G4 (storage)**: ChromaDB, SQLite (ADG, memory), Redis, Neo4j enumeration comes from this file's env-key scan and HTTP-library scan. Storage topology is G4's responsibility; G2b points to the consumers but does not catalogue durability or schema.
- **Gate 2 sign-off status**: G2b is **ready**. G3 and G4b may proceed in parallel.

## Summary counts

| Dimension | Value |
|---|---:|
| Egress points catalogued | 12 |
| Real external providers | 5 (OpenAI, Anthropic, Google GenAI / Vertex, Google Custom Search, HuggingFace Hub) |
| Localhost / internal egress | 4 (Qwen vLLM, Redis, Neo4j, OTel collector) |
| MCP loopback transports | 10 (stdio-loopback + 1 HTTPS external + 1 binary subprocess) |
| Total `os.getenv` / `os.environ` reads | 269 |
| Unique env-key names | 154 |
| Files reading env vars | ≈ 140 |
| Config stub (declared, not wired) | 1 (Pinecone) |
| B7 candidates surfaced | 6 |

Ready for G3 and G4b.
