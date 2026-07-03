# ADG Three-Bucket Gap Report

- **Generated**: 2026-07-03T03:21:30.692427+00:00
- **Snapshot**: `adg_indexed_07022026_2303.sqlite`
- **Runtime view present**: True
- **Runtime-attested edges**: 3,867
- **Runtime proof status**: `attested`
- **Total edges classified**: 566,834
- **Health score** (triplet-attested fraction): **0.0%**


## Defect distribution

| Severity | Class | Edges | % | Description |
|---|---|---:|---:|---|
| — | **TRIPLET_ATTESTED** | 0 | 0.0% | Edge present in all three graphs — fully proven. NOT a defect. |
| P2 | **REGISTRY_DRIFT** | 277 | 0.05% | Used in code AND observed at runtime, but not declared in any registry. Undocumented coupling / accidental API. |
| P3 | **DEAD_PATH** | 261 | 0.05% | Wired in code AND declared in registry, but never traced at runtime. Untested code path or vestigial policy. |
| P3 | **UNOBSERVED_CODE** | 566,274 | 99.9% | Static-only — orphan import, dead code, or never-traced path. |
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
| `<id=77>` | `<id=27947>` | `exports` |
| `<id=90>` | `<id=83086>` | `reads_from` |
| `<id=124>` | `<id=18684>` | `unused_import` |
| `<id=138>` | `<id=77488>` | `imports` |
| `<id=146>` | `<id=38813>` | `imports` |
| `<id=153>` | `<id=38841>` | `imports` |
| `<id=165>` | `<id=77488>` | `imports` |
| `<id=239>` | `<id=38752>` | `imports` |
| `<id=239>` | `<id=38806>` | `imports` |
| `<id=242>` | `<id=94928>` | `implements` |

### DEAD_PATH  (severity P3)

| src | dst | relation |
|---|---|---|
| `<id=28>` | `<id=187498>` | `references_mcp_server` |
| `<id=31>` | `<id=187497>` | `references_mcp_server` |
| `<id=31>` | `<id=187498>` | `references_mcp_server` |
| `<id=31>` | `<id=187501>` | `references_mcp_server` |
| `<id=31>` | `<id=187502>` | `references_mcp_server` |
| `<id=32>` | `<id=187498>` | `references_mcp_server` |
| `<id=37>` | `<id=187497>` | `references_mcp_server` |
| `<id=37>` | `<id=187499>` | `references_mcp_server` |
| `<id=37>` | `<id=187503>` | `references_mcp_server` |
| `<id=37>` | `<id=187504>` | `references_mcp_server` |

### UNOBSERVED_CODE  (severity P3)

| src | dst | relation |
|---|---|---|
| `<id=8>` | `<id=15021>` | `implements` |
| `<id=8>` | `<id=18468>` | `reads_from` |
| `<id=8>` | `<id=20798>` | `reads_from` |
| `<id=8>` | `<id=28173>` | `exports` |
| `<id=8>` | `<id=28173>` | `reads_from` |
| `<id=8>` | `<id=28184>` | `exports` |
| `<id=8>` | `<id=28184>` | `reads_from` |
| `<id=8>` | `<id=28610>` | `covers` |
| `<id=8>` | `<id=28611>` | `imports` |
| `<id=8>` | `<id=55745>` | `unused_import` |

### CONFIG_BLOAT  (severity P4)

| src | dst | relation |
|---|---|---|
| `<id=187496>` | `<id=187497>` | `MCP_SERVER_DECLARED` |
| `<id=187496>` | `<id=187498>` | `MCP_SERVER_DECLARED` |
| `<id=187496>` | `<id=187499>` | `MCP_SERVER_DECLARED` |
| `<id=187496>` | `<id=187500>` | `MCP_SERVER_DECLARED` |
| `<id=187496>` | `<id=187501>` | `MCP_SERVER_DECLARED` |
| `<id=187496>` | `<id=187502>` | `MCP_SERVER_DECLARED` |
| `<id=187496>` | `<id=187503>` | `MCP_SERVER_DECLARED` |
| `<id=187496>` | `<id=187504>` | `MCP_SERVER_DECLARED` |
| `<id=187496>` | `<id=187505>` | `MCP_SERVER_DECLARED` |
| `<id=187506>` | `<id=187507>` | `AGENT_SPEC_DECLARED` |

