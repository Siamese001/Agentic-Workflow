# ADG Three-Bucket Gap Report

- **Generated**: 2026-07-12T02:28:40.757301+00:00
- **Snapshot**: `adg_indexed_07112026_2208.sqlite`
- **Runtime view present**: True
- **Runtime-attested edges**: 3,867
- **Runtime proof status**: `attested`
- **Total edges classified**: 511,538
- **Health score** (triplet-attested fraction): **0.0%**


## Defect distribution

| Severity | Class | Edges | % | Description |
|---|---|---:|---:|---|
| — | **TRIPLET_ATTESTED** | 0 | 0.0% | Edge present in all three graphs — fully proven. NOT a defect. |
| P2 | **REGISTRY_DRIFT** | 256 | 0.05% | Used in code AND observed at runtime, but not declared in any registry. Undocumented coupling / accidental API. |
| P3 | **DEAD_PATH** | 275 | 0.05% | Wired in code AND declared in registry, but never traced at runtime. Untested code path or vestigial policy. |
| P3 | **UNOBSERVED_CODE** | 510,985 | 99.89% | Static-only — orphan import, dead code, or never-traced path. |
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
| `<id=77>` | `<id=28120>` | `exports` |
| `<id=90>` | `<id=83970>` | `reads_from` |
| `<id=124>` | `<id=18849>` | `unused_import` |
| `<id=138>` | `<id=78349>` | `imports` |
| `<id=165>` | `<id=78349>` | `imports` |
| `<id=242>` | `<id=95908>` | `implements` |
| `<id=282>` | `<id=95908>` | `reads_from` |
| `<id=356>` | `<id=187919>` | `imports` |
| `<id=366>` | `<id=95908>` | `reads_from` |
| `<id=401>` | `<id=12881>` | `reads_from` |

### DEAD_PATH  (severity P3)

| src | dst | relation |
|---|---|---|
| `<id=27>` | `<id=189556>` | `references_mcp_server` |
| `<id=27>` | `<id=189557>` | `references_mcp_server` |
| `<id=27>` | `<id=189560>` | `references_mcp_server` |
| `<id=27>` | `<id=189561>` | `references_mcp_server` |
| `<id=28>` | `<id=189557>` | `references_mcp_server` |
| `<id=31>` | `<id=189556>` | `references_mcp_server` |
| `<id=31>` | `<id=189557>` | `references_mcp_server` |
| `<id=31>` | `<id=189560>` | `references_mcp_server` |
| `<id=31>` | `<id=189561>` | `references_mcp_server` |
| `<id=32>` | `<id=189557>` | `references_mcp_server` |

### UNOBSERVED_CODE  (severity P3)

| src | dst | relation |
|---|---|---|
| `<id=7>` | `<id=15171>` | `implements` |
| `<id=7>` | `<id=18633>` | `reads_from` |
| `<id=7>` | `<id=20971>` | `reads_from` |
| `<id=7>` | `<id=28346>` | `exports` |
| `<id=7>` | `<id=28346>` | `reads_from` |
| `<id=7>` | `<id=28357>` | `exports` |
| `<id=7>` | `<id=28357>` | `reads_from` |
| `<id=7>` | `<id=28785>` | `covers` |
| `<id=7>` | `<id=28786>` | `imports` |
| `<id=7>` | `<id=55967>` | `unused_import` |

### CONFIG_BLOAT  (severity P4)

| src | dst | relation |
|---|---|---|
| `<id=189555>` | `<id=189556>` | `MCP_SERVER_DECLARED` |
| `<id=189555>` | `<id=189557>` | `MCP_SERVER_DECLARED` |
| `<id=189555>` | `<id=189558>` | `MCP_SERVER_DECLARED` |
| `<id=189555>` | `<id=189559>` | `MCP_SERVER_DECLARED` |
| `<id=189555>` | `<id=189560>` | `MCP_SERVER_DECLARED` |
| `<id=189555>` | `<id=189561>` | `MCP_SERVER_DECLARED` |
| `<id=189555>` | `<id=189562>` | `MCP_SERVER_DECLARED` |
| `<id=189555>` | `<id=189563>` | `MCP_SERVER_DECLARED` |
| `<id=189555>` | `<id=189564>` | `MCP_SERVER_DECLARED` |
| `<id=189565>` | `<id=189566>` | `AGENT_SPEC_DECLARED` |

