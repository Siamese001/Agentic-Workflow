# ADG Three-Bucket Gap Report

- **Generated**: 2026-06-24T11:18:38.474199+00:00
- **Snapshot**: `adg_indexed_06242026_0706.sqlite`
- **Runtime view present**: True
- **Runtime-attested edges**: 3,867
- **Runtime proof status**: `attested`
- **Total edges classified**: 562,435
- **Health score** (triplet-attested fraction): **0.0%**


## Defect distribution

| Severity | Class | Edges | % | Description |
|---|---|---:|---:|---|
| — | **TRIPLET_ATTESTED** | 0 | 0.0% | Edge present in all three graphs — fully proven. NOT a defect. |
| P2 | **REGISTRY_DRIFT** | 277 | 0.05% | Used in code AND observed at runtime, but not declared in any registry. Undocumented coupling / accidental API. |
| P3 | **DEAD_PATH** | 259 | 0.05% | Wired in code AND declared in registry, but never traced at runtime. Untested code path or vestigial policy. |
| P3 | **UNOBSERVED_CODE** | 561,877 | 99.9% | Static-only — orphan import, dead code, or never-traced path. |
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
| `<id=75>` | `<id=27788>` | `exports` |
| `<id=88>` | `<id=82200>` | `reads_from` |
| `<id=122>` | `<id=18538>` | `unused_import` |
| `<id=136>` | `<id=76625>` | `imports` |
| `<id=144>` | `<id=38629>` | `imports` |
| `<id=151>` | `<id=38657>` | `imports` |
| `<id=163>` | `<id=76625>` | `imports` |
| `<id=237>` | `<id=38568>` | `imports` |
| `<id=237>` | `<id=38622>` | `imports` |
| `<id=240>` | `<id=93962>` | `implements` |

### DEAD_PATH  (severity P3)

| src | dst | relation |
|---|---|---|
| `<id=28>` | `<id=185702>` | `references_mcp_server` |
| `<id=31>` | `<id=185701>` | `references_mcp_server` |
| `<id=31>` | `<id=185702>` | `references_mcp_server` |
| `<id=31>` | `<id=185705>` | `references_mcp_server` |
| `<id=31>` | `<id=185706>` | `references_mcp_server` |
| `<id=36>` | `<id=185701>` | `references_mcp_server` |
| `<id=36>` | `<id=185703>` | `references_mcp_server` |
| `<id=36>` | `<id=185707>` | `references_mcp_server` |
| `<id=36>` | `<id=185708>` | `references_mcp_server` |
| `<id=37>` | `<id=185702>` | `references_mcp_server` |

### UNOBSERVED_CODE  (severity P3)

| src | dst | relation |
|---|---|---|
| `<id=8>` | `<id=14888>` | `implements` |
| `<id=8>` | `<id=18322>` | `reads_from` |
| `<id=8>` | `<id=20646>` | `reads_from` |
| `<id=8>` | `<id=28014>` | `exports` |
| `<id=8>` | `<id=28014>` | `reads_from` |
| `<id=8>` | `<id=28025>` | `exports` |
| `<id=8>` | `<id=28025>` | `reads_from` |
| `<id=8>` | `<id=28451>` | `covers` |
| `<id=8>` | `<id=28452>` | `imports` |
| `<id=8>` | `<id=55561>` | `unused_import` |

### CONFIG_BLOAT  (severity P4)

| src | dst | relation |
|---|---|---|
| `<id=185700>` | `<id=185701>` | `MCP_SERVER_DECLARED` |
| `<id=185700>` | `<id=185702>` | `MCP_SERVER_DECLARED` |
| `<id=185700>` | `<id=185703>` | `MCP_SERVER_DECLARED` |
| `<id=185700>` | `<id=185704>` | `MCP_SERVER_DECLARED` |
| `<id=185700>` | `<id=185705>` | `MCP_SERVER_DECLARED` |
| `<id=185700>` | `<id=185706>` | `MCP_SERVER_DECLARED` |
| `<id=185700>` | `<id=185707>` | `MCP_SERVER_DECLARED` |
| `<id=185700>` | `<id=185708>` | `MCP_SERVER_DECLARED` |
| `<id=185700>` | `<id=185709>` | `MCP_SERVER_DECLARED` |
| `<id=185710>` | `<id=185711>` | `AGENT_SPEC_DECLARED` |

