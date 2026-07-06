# ADG Three-Bucket Gap Report

- **Generated**: 2026-07-06T03:27:11.389058+00:00
- **Snapshot**: `adg_indexed_07052026_2301.sqlite`
- **Runtime view present**: True
- **Runtime-attested edges**: 3,867
- **Runtime proof status**: `attested`
- **Total edges classified**: 568,880
- **Health score** (triplet-attested fraction): **0.0%**


## Defect distribution

| Severity | Class | Edges | % | Description |
|---|---|---:|---:|---|
| — | **TRIPLET_ATTESTED** | 0 | 0.0% | Edge present in all three graphs — fully proven. NOT a defect. |
| P2 | **REGISTRY_DRIFT** | 277 | 0.05% | Used in code AND observed at runtime, but not declared in any registry. Undocumented coupling / accidental API. |
| P3 | **DEAD_PATH** | 276 | 0.05% | Wired in code AND declared in registry, but never traced at runtime. Untested code path or vestigial policy. |
| P3 | **UNOBSERVED_CODE** | 568,305 | 99.9% | Static-only — orphan import, dead code, or never-traced path. |
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
| `<id=77>` | `<id=28019>` | `exports` |
| `<id=90>` | `<id=83427>` | `reads_from` |
| `<id=124>` | `<id=18752>` | `unused_import` |
| `<id=138>` | `<id=77822>` | `imports` |
| `<id=146>` | `<id=38910>` | `imports` |
| `<id=153>` | `<id=38938>` | `imports` |
| `<id=165>` | `<id=77822>` | `imports` |
| `<id=239>` | `<id=38849>` | `imports` |
| `<id=239>` | `<id=38903>` | `imports` |
| `<id=242>` | `<id=95306>` | `implements` |

### DEAD_PATH  (severity P3)

| src | dst | relation |
|---|---|---|
| `<id=27>` | `<id=188347>` | `references_mcp_server` |
| `<id=27>` | `<id=188348>` | `references_mcp_server` |
| `<id=27>` | `<id=188351>` | `references_mcp_server` |
| `<id=27>` | `<id=188352>` | `references_mcp_server` |
| `<id=28>` | `<id=188348>` | `references_mcp_server` |
| `<id=31>` | `<id=188347>` | `references_mcp_server` |
| `<id=31>` | `<id=188348>` | `references_mcp_server` |
| `<id=31>` | `<id=188351>` | `references_mcp_server` |
| `<id=31>` | `<id=188352>` | `references_mcp_server` |
| `<id=32>` | `<id=188347>` | `references_mcp_server` |

### UNOBSERVED_CODE  (severity P3)

| src | dst | relation |
|---|---|---|
| `<id=7>` | `<id=15085>` | `implements` |
| `<id=7>` | `<id=18536>` | `reads_from` |
| `<id=7>` | `<id=20867>` | `reads_from` |
| `<id=7>` | `<id=28245>` | `exports` |
| `<id=7>` | `<id=28245>` | `reads_from` |
| `<id=7>` | `<id=28256>` | `exports` |
| `<id=7>` | `<id=28256>` | `reads_from` |
| `<id=7>` | `<id=28684>` | `covers` |
| `<id=7>` | `<id=28685>` | `imports` |
| `<id=7>` | `<id=55855>` | `unused_import` |

### CONFIG_BLOAT  (severity P4)

| src | dst | relation |
|---|---|---|
| `<id=188346>` | `<id=188347>` | `MCP_SERVER_DECLARED` |
| `<id=188346>` | `<id=188348>` | `MCP_SERVER_DECLARED` |
| `<id=188346>` | `<id=188349>` | `MCP_SERVER_DECLARED` |
| `<id=188346>` | `<id=188350>` | `MCP_SERVER_DECLARED` |
| `<id=188346>` | `<id=188351>` | `MCP_SERVER_DECLARED` |
| `<id=188346>` | `<id=188352>` | `MCP_SERVER_DECLARED` |
| `<id=188346>` | `<id=188353>` | `MCP_SERVER_DECLARED` |
| `<id=188346>` | `<id=188354>` | `MCP_SERVER_DECLARED` |
| `<id=188346>` | `<id=188355>` | `MCP_SERVER_DECLARED` |
| `<id=188356>` | `<id=188357>` | `AGENT_SPEC_DECLARED` |

