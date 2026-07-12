# ADG Three-Bucket Gap Report

- **Generated**: 2026-07-11T23:54:53.604914+00:00
- **Snapshot**: `adg_indexed_07112026_1937.sqlite`
- **Runtime view present**: True
- **Runtime-attested edges**: 3,867
- **Runtime proof status**: `attested`
- **Total edges classified**: 511,522
- **Health score** (triplet-attested fraction): **0.0%**


## Defect distribution

| Severity | Class | Edges | % | Description |
|---|---|---:|---:|---|
| — | **TRIPLET_ATTESTED** | 0 | 0.0% | Edge present in all three graphs — fully proven. NOT a defect. |
| P2 | **REGISTRY_DRIFT** | 256 | 0.05% | Used in code AND observed at runtime, but not declared in any registry. Undocumented coupling / accidental API. |
| P3 | **DEAD_PATH** | 275 | 0.05% | Wired in code AND declared in registry, but never traced at runtime. Untested code path or vestigial policy. |
| P3 | **UNOBSERVED_CODE** | 510,969 | 99.89% | Static-only — orphan import, dead code, or never-traced path. |
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
| `<id=77>` | `<id=28119>` | `exports` |
| `<id=90>` | `<id=83967>` | `reads_from` |
| `<id=124>` | `<id=18848>` | `unused_import` |
| `<id=138>` | `<id=78346>` | `imports` |
| `<id=165>` | `<id=78346>` | `imports` |
| `<id=242>` | `<id=95900>` | `implements` |
| `<id=282>` | `<id=95900>` | `reads_from` |
| `<id=356>` | `<id=187909>` | `imports` |
| `<id=366>` | `<id=95900>` | `reads_from` |
| `<id=401>` | `<id=12881>` | `reads_from` |

### DEAD_PATH  (severity P3)

| src | dst | relation |
|---|---|---|
| `<id=27>` | `<id=189544>` | `references_mcp_server` |
| `<id=27>` | `<id=189545>` | `references_mcp_server` |
| `<id=27>` | `<id=189548>` | `references_mcp_server` |
| `<id=27>` | `<id=189549>` | `references_mcp_server` |
| `<id=28>` | `<id=189545>` | `references_mcp_server` |
| `<id=31>` | `<id=189544>` | `references_mcp_server` |
| `<id=31>` | `<id=189545>` | `references_mcp_server` |
| `<id=31>` | `<id=189548>` | `references_mcp_server` |
| `<id=31>` | `<id=189549>` | `references_mcp_server` |
| `<id=32>` | `<id=189545>` | `references_mcp_server` |

### UNOBSERVED_CODE  (severity P3)

| src | dst | relation |
|---|---|---|
| `<id=7>` | `<id=15170>` | `implements` |
| `<id=7>` | `<id=18632>` | `reads_from` |
| `<id=7>` | `<id=20970>` | `reads_from` |
| `<id=7>` | `<id=28345>` | `exports` |
| `<id=7>` | `<id=28345>` | `reads_from` |
| `<id=7>` | `<id=28356>` | `exports` |
| `<id=7>` | `<id=28356>` | `reads_from` |
| `<id=7>` | `<id=28784>` | `covers` |
| `<id=7>` | `<id=28785>` | `imports` |
| `<id=7>` | `<id=55964>` | `unused_import` |

### CONFIG_BLOAT  (severity P4)

| src | dst | relation |
|---|---|---|
| `<id=189543>` | `<id=189544>` | `MCP_SERVER_DECLARED` |
| `<id=189543>` | `<id=189545>` | `MCP_SERVER_DECLARED` |
| `<id=189543>` | `<id=189546>` | `MCP_SERVER_DECLARED` |
| `<id=189543>` | `<id=189547>` | `MCP_SERVER_DECLARED` |
| `<id=189543>` | `<id=189548>` | `MCP_SERVER_DECLARED` |
| `<id=189543>` | `<id=189549>` | `MCP_SERVER_DECLARED` |
| `<id=189543>` | `<id=189550>` | `MCP_SERVER_DECLARED` |
| `<id=189543>` | `<id=189551>` | `MCP_SERVER_DECLARED` |
| `<id=189543>` | `<id=189552>` | `MCP_SERVER_DECLARED` |
| `<id=189553>` | `<id=189554>` | `AGENT_SPEC_DECLARED` |

