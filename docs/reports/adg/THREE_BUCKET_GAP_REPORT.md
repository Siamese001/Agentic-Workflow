# ADG Three-Bucket Gap Report

- **Generated**: 2026-07-02T03:24:47.825511+00:00
- **Snapshot**: `adg_indexed_07012026_2302.sqlite`
- **Runtime view present**: True
- **Runtime-attested edges**: 3,867
- **Runtime proof status**: `attested`
- **Total edges classified**: 566,304
- **Health score** (triplet-attested fraction): **0.0%**


## Defect distribution

| Severity | Class | Edges | % | Description |
|---|---|---:|---:|---|
| — | **TRIPLET_ATTESTED** | 0 | 0.0% | Edge present in all three graphs — fully proven. NOT a defect. |
| P2 | **REGISTRY_DRIFT** | 277 | 0.05% | Used in code AND observed at runtime, but not declared in any registry. Undocumented coupling / accidental API. |
| P3 | **DEAD_PATH** | 261 | 0.05% | Wired in code AND declared in registry, but never traced at runtime. Untested code path or vestigial policy. |
| P3 | **UNOBSERVED_CODE** | 565,744 | 99.9% | Static-only — orphan import, dead code, or never-traced path. |
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
| `<id=77>` | `<id=27944>` | `exports` |
| `<id=90>` | `<id=82995>` | `reads_from` |
| `<id=124>` | `<id=18681>` | `unused_import` |
| `<id=138>` | `<id=77400>` | `imports` |
| `<id=146>` | `<id=38810>` | `imports` |
| `<id=153>` | `<id=38838>` | `imports` |
| `<id=165>` | `<id=77400>` | `imports` |
| `<id=239>` | `<id=38749>` | `imports` |
| `<id=239>` | `<id=38803>` | `imports` |
| `<id=242>` | `<id=94832>` | `implements` |

### DEAD_PATH  (severity P3)

| src | dst | relation |
|---|---|---|
| `<id=28>` | `<id=187293>` | `references_mcp_server` |
| `<id=31>` | `<id=187292>` | `references_mcp_server` |
| `<id=31>` | `<id=187293>` | `references_mcp_server` |
| `<id=31>` | `<id=187296>` | `references_mcp_server` |
| `<id=31>` | `<id=187297>` | `references_mcp_server` |
| `<id=32>` | `<id=187293>` | `references_mcp_server` |
| `<id=37>` | `<id=187292>` | `references_mcp_server` |
| `<id=37>` | `<id=187294>` | `references_mcp_server` |
| `<id=37>` | `<id=187298>` | `references_mcp_server` |
| `<id=37>` | `<id=187299>` | `references_mcp_server` |

### UNOBSERVED_CODE  (severity P3)

| src | dst | relation |
|---|---|---|
| `<id=8>` | `<id=15018>` | `implements` |
| `<id=8>` | `<id=18465>` | `reads_from` |
| `<id=8>` | `<id=20795>` | `reads_from` |
| `<id=8>` | `<id=28170>` | `exports` |
| `<id=8>` | `<id=28170>` | `reads_from` |
| `<id=8>` | `<id=28181>` | `exports` |
| `<id=8>` | `<id=28181>` | `reads_from` |
| `<id=8>` | `<id=28607>` | `covers` |
| `<id=8>` | `<id=28608>` | `imports` |
| `<id=8>` | `<id=55742>` | `unused_import` |

### CONFIG_BLOAT  (severity P4)

| src | dst | relation |
|---|---|---|
| `<id=187291>` | `<id=187292>` | `MCP_SERVER_DECLARED` |
| `<id=187291>` | `<id=187293>` | `MCP_SERVER_DECLARED` |
| `<id=187291>` | `<id=187294>` | `MCP_SERVER_DECLARED` |
| `<id=187291>` | `<id=187295>` | `MCP_SERVER_DECLARED` |
| `<id=187291>` | `<id=187296>` | `MCP_SERVER_DECLARED` |
| `<id=187291>` | `<id=187297>` | `MCP_SERVER_DECLARED` |
| `<id=187291>` | `<id=187298>` | `MCP_SERVER_DECLARED` |
| `<id=187291>` | `<id=187299>` | `MCP_SERVER_DECLARED` |
| `<id=187291>` | `<id=187300>` | `MCP_SERVER_DECLARED` |
| `<id=187301>` | `<id=187302>` | `AGENT_SPEC_DECLARED` |

