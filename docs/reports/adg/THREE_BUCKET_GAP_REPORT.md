# ADG Three-Bucket Gap Report

- **Generated**: 2026-06-22T09:51:41.396692+00:00
- **Snapshot**: `adg_indexed_06222026_0539.sqlite`
- **Runtime view present**: True
- **Runtime-attested edges**: 3,867
- **Runtime proof status**: `attested`
- **Total edges classified**: 561,386
- **Health score** (triplet-attested fraction): **0.0%**


## Defect distribution

| Severity | Class | Edges | % | Description |
|---|---|---:|---:|---|
| — | **TRIPLET_ATTESTED** | 0 | 0.0% | Edge present in all three graphs — fully proven. NOT a defect. |
| P2 | **REGISTRY_DRIFT** | 277 | 0.05% | Used in code AND observed at runtime, but not declared in any registry. Undocumented coupling / accidental API. |
| P3 | **DEAD_PATH** | 258 | 0.05% | Wired in code AND declared in registry, but never traced at runtime. Untested code path or vestigial policy. |
| P3 | **UNOBSERVED_CODE** | 560,829 | 99.9% | Static-only — orphan import, dead code, or never-traced path. |
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
| `<id=75>` | `<id=27769>` | `exports` |
| `<id=88>` | `<id=82055>` | `reads_from` |
| `<id=122>` | `<id=18516>` | `unused_import` |
| `<id=136>` | `<id=76487>` | `imports` |
| `<id=144>` | `<id=38616>` | `imports` |
| `<id=151>` | `<id=38644>` | `imports` |
| `<id=163>` | `<id=76487>` | `imports` |
| `<id=237>` | `<id=38555>` | `imports` |
| `<id=237>` | `<id=38609>` | `imports` |
| `<id=240>` | `<id=93793>` | `implements` |

### DEAD_PATH  (severity P3)

| src | dst | relation |
|---|---|---|
| `<id=28>` | `<id=185332>` | `references_mcp_server` |
| `<id=31>` | `<id=185331>` | `references_mcp_server` |
| `<id=31>` | `<id=185332>` | `references_mcp_server` |
| `<id=31>` | `<id=185335>` | `references_mcp_server` |
| `<id=31>` | `<id=185336>` | `references_mcp_server` |
| `<id=36>` | `<id=185331>` | `references_mcp_server` |
| `<id=36>` | `<id=185333>` | `references_mcp_server` |
| `<id=36>` | `<id=185337>` | `references_mcp_server` |
| `<id=36>` | `<id=185338>` | `references_mcp_server` |
| `<id=37>` | `<id=185332>` | `references_mcp_server` |

### UNOBSERVED_CODE  (severity P3)

| src | dst | relation |
|---|---|---|
| `<id=8>` | `<id=14869>` | `implements` |
| `<id=8>` | `<id=18300>` | `reads_from` |
| `<id=8>` | `<id=20625>` | `reads_from` |
| `<id=8>` | `<id=27996>` | `exports` |
| `<id=8>` | `<id=27996>` | `reads_from` |
| `<id=8>` | `<id=28007>` | `exports` |
| `<id=8>` | `<id=28007>` | `reads_from` |
| `<id=8>` | `<id=28433>` | `covers` |
| `<id=8>` | `<id=28434>` | `imports` |
| `<id=8>` | `<id=55548>` | `unused_import` |

### CONFIG_BLOAT  (severity P4)

| src | dst | relation |
|---|---|---|
| `<id=185330>` | `<id=185331>` | `MCP_SERVER_DECLARED` |
| `<id=185330>` | `<id=185332>` | `MCP_SERVER_DECLARED` |
| `<id=185330>` | `<id=185333>` | `MCP_SERVER_DECLARED` |
| `<id=185330>` | `<id=185334>` | `MCP_SERVER_DECLARED` |
| `<id=185330>` | `<id=185335>` | `MCP_SERVER_DECLARED` |
| `<id=185330>` | `<id=185336>` | `MCP_SERVER_DECLARED` |
| `<id=185330>` | `<id=185337>` | `MCP_SERVER_DECLARED` |
| `<id=185330>` | `<id=185338>` | `MCP_SERVER_DECLARED` |
| `<id=185330>` | `<id=185339>` | `MCP_SERVER_DECLARED` |
| `<id=185340>` | `<id=185341>` | `AGENT_SPEC_DECLARED` |

