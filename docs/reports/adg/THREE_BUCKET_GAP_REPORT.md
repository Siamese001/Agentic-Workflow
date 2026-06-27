# ADG Three-Bucket Gap Report

- **Generated**: 2026-06-27T09:10:56.722054+00:00
- **Snapshot**: `adg_indexed_06272026_0458.sqlite`
- **Runtime view present**: True
- **Runtime-attested edges**: 3,867
- **Runtime proof status**: `attested`
- **Total edges classified**: 563,667
- **Health score** (triplet-attested fraction): **0.0%**


## Defect distribution

| Severity | Class | Edges | % | Description |
|---|---|---:|---:|---|
| — | **TRIPLET_ATTESTED** | 0 | 0.0% | Edge present in all three graphs — fully proven. NOT a defect. |
| P2 | **REGISTRY_DRIFT** | 277 | 0.05% | Used in code AND observed at runtime, but not declared in any registry. Undocumented coupling / accidental API. |
| P3 | **DEAD_PATH** | 259 | 0.05% | Wired in code AND declared in registry, but never traced at runtime. Untested code path or vestigial policy. |
| P3 | **UNOBSERVED_CODE** | 563,109 | 99.9% | Static-only — orphan import, dead code, or never-traced path. |
| P5 | **DYNAMIC_DISPATCH** | 0 | 0.0% | No static link, but declared + verified at runtime. Plugin / DI / lazy import — usually fine. |
| P1 | **SHADOW_CHANNEL** | 0 | 0.0% | Runtime-only undeclared edge — monkey-patch, side-effect coupling, hidden import. SECURITY-CRITICAL. |
| P4 | **CONFIG_BLOAT** | 22 | 0.0% | Declared in registry but never used in code or runtime. Dead policy / config drift. |

## Static-only vs runtime-required

**Static-only** (answerable without OTEL traces — pure registry-vs-static set diff): `REGISTRY_DRIFT`, `CONFIG_BLOAT`

**Requires runtime traces** (need OTEL span evidence to classify correctly): `TRIPLET_ATTESTED`, `DEAD_PATH`, `DYNAMIC_DISPATCH`, `SHADOW_CHANNEL`, `UNOBSERVED_CODE`

## Top samples per class

### REGISTRY_DRIFT  (severity P2)

| src | dst | relation |
|---|---|---|
| `<id=75>` | `<id=27817>` | `exports` |
| `<id=88>` | `<id=82457>` | `reads_from` |
| `<id=122>` | `<id=18567>` | `unused_import` |
| `<id=136>` | `<id=76874>` | `imports` |
| `<id=144>` | `<id=38658>` | `imports` |
| `<id=151>` | `<id=38686>` | `imports` |
| `<id=163>` | `<id=76874>` | `imports` |
| `<id=237>` | `<id=38597>` | `imports` |
| `<id=237>` | `<id=38651>` | `imports` |
| `<id=240>` | `<id=94240>` | `implements` |

### DEAD_PATH  (severity P3)

| src | dst | relation |
|---|---|---|
| `<id=28>` | `<id=186235>` | `references_mcp_server` |
| `<id=31>` | `<id=186234>` | `references_mcp_server` |
| `<id=31>` | `<id=186235>` | `references_mcp_server` |
| `<id=31>` | `<id=186238>` | `references_mcp_server` |
| `<id=31>` | `<id=186239>` | `references_mcp_server` |
| `<id=36>` | `<id=186234>` | `references_mcp_server` |
| `<id=36>` | `<id=186236>` | `references_mcp_server` |
| `<id=36>` | `<id=186240>` | `references_mcp_server` |
| `<id=36>` | `<id=186241>` | `references_mcp_server` |
| `<id=37>` | `<id=186235>` | `references_mcp_server` |

### UNOBSERVED_CODE  (severity P3)

| src | dst | relation |
|---|---|---|
| `<id=8>` | `<id=14916>` | `implements` |
| `<id=8>` | `<id=18351>` | `reads_from` |
| `<id=8>` | `<id=20675>` | `reads_from` |
| `<id=8>` | `<id=28043>` | `exports` |
| `<id=8>` | `<id=28043>` | `reads_from` |
| `<id=8>` | `<id=28054>` | `exports` |
| `<id=8>` | `<id=28054>` | `reads_from` |
| `<id=8>` | `<id=28479>` | `covers` |
| `<id=8>` | `<id=28480>` | `imports` |
| `<id=8>` | `<id=55590>` | `unused_import` |

### CONFIG_BLOAT  (severity P4)

| src | dst | relation |
|---|---|---|
| `<id=186233>` | `<id=186234>` | `MCP_SERVER_DECLARED` |
| `<id=186233>` | `<id=186235>` | `MCP_SERVER_DECLARED` |
| `<id=186233>` | `<id=186236>` | `MCP_SERVER_DECLARED` |
| `<id=186233>` | `<id=186237>` | `MCP_SERVER_DECLARED` |
| `<id=186233>` | `<id=186238>` | `MCP_SERVER_DECLARED` |
| `<id=186233>` | `<id=186239>` | `MCP_SERVER_DECLARED` |
| `<id=186233>` | `<id=186240>` | `MCP_SERVER_DECLARED` |
| `<id=186233>` | `<id=186241>` | `MCP_SERVER_DECLARED` |
| `<id=186233>` | `<id=186242>` | `MCP_SERVER_DECLARED` |
| `<id=186243>` | `<id=186244>` | `AGENT_SPEC_DECLARED` |

