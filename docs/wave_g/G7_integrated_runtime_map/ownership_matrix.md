# G7 — Ownership Matrix

wave: G7
adg_snapshot: artifacts/adg/adg_indexed_04182026_0814.sqlite
adg_snapshot_timestamp: "04182026_0814"

## Ownership classes

- **repo-managed**: runtime behavior controlled primarily by code/config under this repository.
- **operator-managed**: lifecycle/trust/SLA controlled externally (service ops, accounts, endpoint availability).
- **external-tool-owned**: behavior managed by third-party tool process or endpoint beyond repo control.
- **mixed-control**: repo logic and operator/external lifecycle both materially determine behavior.

## Matrix

| surface_cluster | class | primary owner | secondary owner | rationale | requires_wave_h_formalization |
|---|---|---|---|---|---|
| App runtimes (`apps_eval/exec/lic/research/rfp/rg`) | repo-managed | app owners + core owners | operator (runtime env) | Entrypoints and core execution logic are in-repo; operator only supplies env/runtime host | no |
| Core runtime libraries (`agentic_core/*`) | repo-managed | core architecture owners | app owners | Layer logic, routing, orchestration, execution all in-repo | no |
| ADG generation and sqlite snapshots | repo-managed | ADG/tooling owners | operator (schedule) | Generator and schema are in-repo; execution scheduling may be operator/CI triggered | no |
| Redis daemon lifecycle | operator-managed | runtime operator | repo cache/ADG clients | Daemon uptime, persistence, and host policy are external to repo code | no |
| Redis client usage (`redis_*`, ADG cache, coordination) | mixed-control | repo owners | runtime operator | Key semantics and usage in repo; availability and persistence policy operator-controlled | yes |
| Memory MCP + sqlite canonical store | mixed-control | memory/tooling owners | runtime operator | Server logic in-repo; effective canonical file path depends on environment and deployment | yes |
| Vector DB MCP + embedded Chroma | mixed-control | retrieval/vector owners | runtime operator | In-repo service logic with operator-controlled model/download/cache posture | yes |
| OTel MCP + runtime ADG ingest | mixed-control | observability owners | operator (collector endpoint) | In-repo telemetry tooling but external collector endpoint policy may apply | yes |
| MCP python stdio servers (adg, memory, vector, otel, redis, pytest, enhanced_http) | repo-managed | MCP/tooling owners | operator (IDE process env) | Server implementations are in-repo, launched through IDE MCP runtime | no |
| MCP Node/binary launchers (`filesystem`, `task_manager`, `notion`, `GitKraken`) | external-tool-owned | external tool vendors + operator | repo operator | Lifecycle/contracts partly or fully outside repo Python control | yes |
| DeepWiki MCP endpoint | external-tool-owned | deepwiki service owner + operator | repo operator | Pure external endpoint with no local subprocess control | yes |
| Provider egress endpoints (OpenAI/Anthropic/Gemini/etc.) | operator-managed | operator/account owner | repo gateway owners | Credentialing/SLA/network path external; repo controls invocation logic only | yes |
| Exit-control and write-gate policy plane | mixed-control | L5/L2 policy owners | operator (critical bypass toggles) | Enforcement logic in-repo but critical bypass toggles change practical trust posture | yes |
| Compatibility startup shims/facades | repo-managed | app owners | architecture owner | Implemented in-repo; marked special-case not canonical topology | yes |

## Explicit ownership-boundary residuals

| residual_or_issue | current boundary status | impact | owner | wave_h_blocking |
|---|---|---|---|---|
| `B7-G6-05` repo-managed vs operator-managed formalization | partially explicit, not fully normalized per-surface | map trust ambiguity in mixed-control zones | G7/G8 runtime map owner | yes |
| G5 dual-plane runtime ambiguity (MCP subprocess vs in-process) | explicit but accepted | operational reasoning complexity | tooling + architecture owners | no |
| opaque restart semantics (GitKraken, DeepWiki, some external surfaces) | accepted external ambiguity | affects operability predictability, not core map correctness | operator + external tool owner | no |
| `MEMORY_DB` canonical-state ambiguity | unresolved | ownership of authoritative memory state unclear | memory owner + config owner | yes |
| Redis posture ambiguity (TTL/eviction/dev-scale assumptions) | explicit residual | impacts reliability/trust assumptions | infra operator + cache owners | no |
| provider/model selector default-layering ambiguity | explicit residual | may change route predictability under env changes | provider/runtime owners | no |

## Requirement-specific labels

### Repo-managed surfaces

- App and core runtime logic, ADG tooling, python MCP servers, G-wave artifacts.

### Operator-managed surfaces

- Redis daemon/service lifecycle, external provider accounts/endpoints, ambient network policy.

### External-tool-owned surfaces

- DeepWiki endpoint, GitKraken bridge behaviors, Notion/Task Manager/filesystem launcher toolchain contracts.

### Mixed-control surfaces

- Memory lifecycle, vector retrieval/embedding posture, OTel path, egress guard and governance override posture.
