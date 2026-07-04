# ADG Three-Bucket Gap Report

- **Generated**: 2026-07-04T03:21:08.062443+00:00
- **Snapshot**: `adg_indexed_07032026_2302.sqlite`
- **Runtime view present**: True
- **Runtime-attested edges**: 3,867
- **Runtime proof status**: `attested`
- **Total edges classified**: 567,522
- **Health score** (triplet-attested fraction): **0.0%**


## Defect distribution

| Severity | Class | Edges | % | Description |
|---|---|---:|---:|---|
| — | **TRIPLET_ATTESTED** | 0 | 0.0% | Edge present in all three graphs — fully proven. NOT a defect. |
| P2 | **REGISTRY_DRIFT** | 277 | 0.05% | Used in code AND observed at runtime, but not declared in any registry. Undocumented coupling / accidental API. |
| P3 | **DEAD_PATH** | 272 | 0.05% | Wired in code AND declared in registry, but never traced at runtime. Untested code path or vestigial policy. |
| P3 | **UNOBSERVED_CODE** | 566,951 | 99.9% | Static-only — orphan import, dead code, or never-traced path. |
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
| `<id=78>` | `<id=27985>` | `exports` |
| `<id=91>` | `<id=83215>` | `reads_from` |
| `<id=125>` | `<id=18719>` | `unused_import` |
| `<id=139>` | `<id=77615>` | `imports` |
| `<id=147>` | `<id=38853>` | `imports` |
| `<id=154>` | `<id=38881>` | `imports` |
| `<id=166>` | `<id=77615>` | `imports` |
| `<id=240>` | `<id=38792>` | `imports` |
| `<id=240>` | `<id=38846>` | `imports` |
| `<id=243>` | `<id=95067>` | `implements` |

### DEAD_PATH  (severity P3)

| src | dst | relation |
|---|---|---|
| `<id=28>` | `<id=187781>` | `references_mcp_server` |
| `<id=28>` | `<id=187782>` | `references_mcp_server` |
| `<id=28>` | `<id=187785>` | `references_mcp_server` |
| `<id=28>` | `<id=187786>` | `references_mcp_server` |
| `<id=29>` | `<id=187782>` | `references_mcp_server` |
| `<id=32>` | `<id=187781>` | `references_mcp_server` |
| `<id=32>` | `<id=187782>` | `references_mcp_server` |
| `<id=32>` | `<id=187785>` | `references_mcp_server` |
| `<id=32>` | `<id=187786>` | `references_mcp_server` |
| `<id=33>` | `<id=187781>` | `references_mcp_server` |

### UNOBSERVED_CODE  (severity P3)

| src | dst | relation |
|---|---|---|
| `<id=8>` | `<id=15056>` | `implements` |
| `<id=8>` | `<id=18503>` | `reads_from` |
| `<id=8>` | `<id=20833>` | `reads_from` |
| `<id=8>` | `<id=28211>` | `exports` |
| `<id=8>` | `<id=28211>` | `reads_from` |
| `<id=8>` | `<id=28222>` | `exports` |
| `<id=8>` | `<id=28222>` | `reads_from` |
| `<id=8>` | `<id=28648>` | `covers` |
| `<id=8>` | `<id=28649>` | `imports` |
| `<id=8>` | `<id=55785>` | `unused_import` |

### CONFIG_BLOAT  (severity P4)

| src | dst | relation |
|---|---|---|
| `<id=187780>` | `<id=187781>` | `MCP_SERVER_DECLARED` |
| `<id=187780>` | `<id=187782>` | `MCP_SERVER_DECLARED` |
| `<id=187780>` | `<id=187783>` | `MCP_SERVER_DECLARED` |
| `<id=187780>` | `<id=187784>` | `MCP_SERVER_DECLARED` |
| `<id=187780>` | `<id=187785>` | `MCP_SERVER_DECLARED` |
| `<id=187780>` | `<id=187786>` | `MCP_SERVER_DECLARED` |
| `<id=187780>` | `<id=187787>` | `MCP_SERVER_DECLARED` |
| `<id=187780>` | `<id=187788>` | `MCP_SERVER_DECLARED` |
| `<id=187780>` | `<id=187789>` | `MCP_SERVER_DECLARED` |
| `<id=187790>` | `<id=187791>` | `AGENT_SPEC_DECLARED` |

