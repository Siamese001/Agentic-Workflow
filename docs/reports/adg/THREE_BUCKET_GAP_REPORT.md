# ADG Three-Bucket Gap Report

- **Generated**: 2026-05-25T00:00:20.186376+00:00
- **Snapshot**: `adg_indexed_05242026_1939.sqlite`
- **Runtime view present**: True
- **Runtime-attested edges**: 3,865
- **Runtime proof status**: `attested`
- **Total edges classified**: 550,343
- **Health score** (triplet-attested fraction): **0.0%**


## Defect distribution

| Severity | Class | Edges | % | Description |
|---|---|---:|---:|---|
| — | **TRIPLET_ATTESTED** | 0 | 0.0% | Edge present in all three graphs — fully proven. NOT a defect. |
| P2 | **REGISTRY_DRIFT** | 309 | 0.06% | Used in code AND observed at runtime, but not declared in any registry. Undocumented coupling / accidental API. |
| P3 | **DEAD_PATH** | 311 | 0.06% | Wired in code AND declared in registry, but never traced at runtime. Untested code path or vestigial policy. |
| P3 | **UNOBSERVED_CODE** | 549,696 | 99.88% | Static-only — orphan import, dead code, or never-traced path. |
| P5 | **DYNAMIC_DISPATCH** | 0 | 0.0% | No static link, but declared + verified at runtime. Plugin / DI / lazy import — usually fine. |
| P1 | **SHADOW_CHANNEL** | 0 | 0.0% | Runtime-only undeclared edge — monkey-patch, side-effect coupling, hidden import. SECURITY-CRITICAL. |
| P4 | **CONFIG_BLOAT** | 27 | 0.0% | Declared in registry but never used in code or runtime. Dead policy / config drift. |

## Static-only vs runtime-required

**Static-only** (answerable without OTEL traces — pure registry-vs-static set diff): `REGISTRY_DRIFT`, `CONFIG_BLOAT`

**Requires runtime traces** (need OTEL span evidence to classify correctly): `TRIPLET_ATTESTED`, `DEAD_PATH`, `DYNAMIC_DISPATCH`, `SHADOW_CHANNEL`, `UNOBSERVED_CODE`

## Top samples per class

### REGISTRY_DRIFT  (severity P2)

| src | dst | relation |
|---|---|---|
| `<id=48>` | `<id=70783>` | `reads_from` |
| `<id=117>` | `<id=20420>` | `writes_to` |
| `<id=123>` | `<id=77533>` | `exports` |
| `<id=137>` | `<id=27653>` | `exports` |
| `<id=150>` | `<id=77105>` | `reads_from` |
| `<id=183>` | `<id=18586>` | `unused_import` |
| `<id=197>` | `<id=71648>` | `imports` |
| `<id=205>` | `<id=37792>` | `imports` |
| `<id=212>` | `<id=37820>` | `imports` |
| `<id=224>` | `<id=71648>` | `imports` |

### DEAD_PATH  (severity P3)

| src | dst | relation |
|---|---|---|
| `<id=170>` | `<id=176126>` | `references_mcp_server` |
| `<id=198>` | `<id=176126>` | `references_mcp_server` |
| `<id=254>` | `<id=176126>` | `references_mcp_server` |
| `<id=273>` | `<id=176125>` | `references_mcp_server` |
| `<id=336>` | `<id=176126>` | `references_mcp_server` |
| `<id=345>` | `<id=176125>` | `references_mcp_server` |
| `<id=354>` | `<id=176126>` | `references_mcp_server` |
| `<id=365>` | `<id=176126>` | `references_mcp_server` |
| `<id=381>` | `<id=176125>` | `references_mcp_server` |
| `<id=402>` | `<id=176126>` | `references_mcp_server` |

### UNOBSERVED_CODE  (severity P3)

| src | dst | relation |
|---|---|---|
| `<id=8>` | `<id=4>` | `belongs_to_layer` |
| `<id=8>` | `<id=14896>` | `implements` |
| `<id=8>` | `<id=18362>` | `reads_from` |
| `<id=8>` | `<id=20740>` | `reads_from` |
| `<id=8>` | `<id=27886>` | `exports` |
| `<id=8>` | `<id=27886>` | `reads_from` |
| `<id=8>` | `<id=27898>` | `exports` |
| `<id=8>` | `<id=27898>` | `reads_from` |
| `<id=8>` | `<id=28312>` | `covers` |
| `<id=8>` | `<id=28313>` | `imports` |

### CONFIG_BLOAT  (severity P4)

| src | dst | relation |
|---|---|---|
| `<id=176121>` | `<id=176122>` | `MCP_SERVER_DECLARED` |
| `<id=176121>` | `<id=176123>` | `MCP_SERVER_DECLARED` |
| `<id=176121>` | `<id=176124>` | `MCP_SERVER_DECLARED` |
| `<id=176121>` | `<id=176125>` | `MCP_SERVER_DECLARED` |
| `<id=176121>` | `<id=176126>` | `MCP_SERVER_DECLARED` |
| `<id=176121>` | `<id=176127>` | `MCP_SERVER_DECLARED` |
| `<id=176121>` | `<id=176128>` | `MCP_SERVER_DECLARED` |
| `<id=176121>` | `<id=176129>` | `MCP_SERVER_DECLARED` |
| `<id=176121>` | `<id=176130>` | `MCP_SERVER_DECLARED` |
| `<id=176121>` | `<id=176131>` | `MCP_SERVER_DECLARED` |

