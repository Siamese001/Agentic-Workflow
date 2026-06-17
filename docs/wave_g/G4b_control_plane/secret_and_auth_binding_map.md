# G4b — Secret and Auth Binding Map

ADG snapshot: `artifacts/adg/adg_indexed_04172026_0611.sqlite` (04172026_0611).

Only key names are listed. No secret values are shown.

## 1. Secret classes

- **External-provider secrets**: API keys/passwords for egress providers.
- **Internal-governance secrets**: signing/verifier tokens used for runtime authority and gateway integrity.
- **MCP subprocess secrets**: keys injected only into MCP subprocesses.

## 2. External-provider secret bindings

| Key | Primary consumer modules | Egress/provider binding | Pipeline touchpoints |
|---|---|---|---|
| `OPENAI_API_KEY` | `infrastructure/sdks_mcps/__init__.py`, `apps_shared/types/model_router_types.py`, `agentic_core/L2_execution/reasoning/EmbeddingSovereignAgent.py` | EGRESS-OPENAI-01 | `PIPE-INFERENCE-LLM`, `PIPE-EMBEDDING` |
| `ANTHROPIC_API_KEY` | `infrastructure/sdks_mcps/__init__.py`, `apps_shared/types/model_router_types.py` | EGRESS-ANTHROPIC-01 | `PIPE-INFERENCE-LLM` |
| `GOOGLE_API_KEY` | `infrastructure/sdks_mcps/__init__.py`, `apps_shared/utils/providers_google_genai_client_util.py`, `apps_lic/tools/GoogleSearchClient.py` | EGRESS-GEMINI-01 + EGRESS-GOOGLE-CSE-01 | `PIPE-INFERENCE-LLM`, `PIPE-APP-REQUEST` |
| `GEMINI_API_KEY` | same Gemini client surfaces | EGRESS-GEMINI-01 | `PIPE-INFERENCE-LLM` |
| `GOOGLE_CSE_ID` | `apps_lic/tools/GoogleSearchClient.py` | EGRESS-GOOGLE-CSE-01 | `PIPE-APP-REQUEST` |
| `NEO4J_USERNAME`, `NEO4J_PASSWORD` | `agentic_core/L4_state/enforcement/neo4j_store.py` | EGRESS-NEO4J-01 | `PIPE-APP-REQUEST` |
| `REDIS_PASSWORD` | `agentic_core/cache/redis_cache_client.py`, `apps_shared/utils/resource_manager_types_util.py` | EGRESS-REDIS-01 | `PIPE-APP-REQUEST`, `PIPE-HEALING` |
| `PINECONE_INDEX_NAME` | `apps_shared/utils/etl_pipeline_util.py` | EGRESS-PINECONE-STUB-01 (declared-not-wired) | none runtime-critical |

## 3. Internal-governance secret bindings

| Key | Reader | Use | Risk |
|---|---|---|---|
| `LLM_GATEWAY_SECRET` | `agentic_core/L2_execution/enforcement/SovereignLLMGateway.py` | Gateway signing secret (fallback random secret when absent) | high — cross-process consistency risk if unset |
| `AGENTIC_AUTHORITY_SECRET` | `agentic_core/runtime/engine/execution_bound_token.py` | Execution-bound token signing; fail-closed when missing | critical |
| `RG_VALIDATION_SECRET` | `apps_rg/validators/validation_gate_validator.py` | APP-RG validation signature path | high |

## 4. MCP-injected secrets (not repo in-process reads)

| Key | MCP server | Notes |
|---|---|---|
| `NOTION_TOKEN` | notion MCP (`npx @notionhq/notion-mcp-server`) | injected via `.mcp.json`; not read by repo runtime Python |
| `GITKRAKEN_GK_PATH` | GitKraken MCP command interpolation | executable path token, not provider API secret |

## 5. Auth-binding + control-plane coupling

| Secret key | Coupled control knobs |
|---|---|
| `OPENAI_API_KEY` | `OPENAI_MODEL` |
| `ANTHROPIC_API_KEY` | `ANTHROPIC_MODEL` |
| `GOOGLE_API_KEY`/`GEMINI_API_KEY` | `GEMINI_MODEL`, `GEMINI_PRO_MODEL` |
| `REDIS_PASSWORD` | `REDIS_HOST`, `REDIS_PORT`, `REDIS_DB`, `REDIS_URL`, `ADG_REDIS_URL` |
| `NEO4J_USERNAME`/`NEO4J_PASSWORD` | `NEO4J_URI` |
| `LLM_GATEWAY_SECRET` | `EGRESS_GUARD_DISABLED` (policy bypass context) |
| `AGENTIC_AUTHORITY_SECRET` | `DISABLE_RUNTIME_MUTATION_GUARD` (governance hardening posture) |

## 6. Secret hygiene observations

1. Several provider keys have no in-code fallback (expected for secrets) and must be supplied by environment.
2. `LLM_GATEWAY_SECRET` has a runtime fallback to random bytes when unset; this avoids startup failure but weakens deterministic signature continuity across restarts.
3. `AGENTIC_AUTHORITY_SECRET` is stricter: module documentation states fail-closed behavior when absent.
4. Pinecone remains a declared-only stub in G2b/G4b; key presence does not imply active egress.

## 7. Practical policy for G5/G6 hand-off

- Keep secret injection externalized (`.env` / OS env / MCP env blocks).
- Add rotation and presence checks for critical keys (`AGENTIC_AUTHORITY_SECRET`, provider API keys, Redis auth where enabled).
- Treat any run with critical secret missing (except intentionally fallback-tolerant `LLM_GATEWAY_SECRET`) as failed preflight.
