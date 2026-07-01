# ADG Three-Bucket Gap Report

- **Generated**: 2026-07-01T08:40:23.520547+00:00
- **Snapshot**: `adg_indexed_07012026_0418.sqlite`
- **Runtime view present**: True
- **Runtime-attested edges**: 3,867
- **Runtime proof status**: `attested`
- **Total edges classified**: 565,683
- **Health score** (triplet-attested fraction): **0.0%**


## Defect distribution

| Severity | Class | Edges | % | Description |
|---|---|---:|---:|---|
| — | **TRIPLET_ATTESTED** | 0 | 0.0% | Edge present in all three graphs — fully proven. NOT a defect. |
| P2 | **REGISTRY_DRIFT** | 277 | 0.05% | Used in code AND observed at runtime, but not declared in any registry. Undocumented coupling / accidental API. |
| P3 | **DEAD_PATH** | 259 | 0.05% | Wired in code AND declared in registry, but never traced at runtime. Untested code path or vestigial policy. |
| P3 | **UNOBSERVED_CODE** | 565,125 | 99.9% | Static-only — orphan import, dead code, or never-traced path. |
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
| `<id=75>` | `<id=27892>` | `exports` |
| `<id=88>` | `<id=82904>` | `reads_from` |
| `<id=122>` | `<id=18633>` | `unused_import` |
| `<id=136>` | `<id=77312>` | `imports` |
| `<id=144>` | `<id=38751>` | `imports` |
| `<id=151>` | `<id=38779>` | `imports` |
| `<id=163>` | `<id=77312>` | `imports` |
| `<id=237>` | `<id=38690>` | `imports` |
| `<id=237>` | `<id=38744>` | `imports` |
| `<id=240>` | `<id=94733>` | `implements` |

### DEAD_PATH  (severity P3)

| src | dst | relation |
|---|---|---|
| `<id=28>` | `<id=187069>` | `references_mcp_server` |
| `<id=31>` | `<id=187068>` | `references_mcp_server` |
| `<id=31>` | `<id=187069>` | `references_mcp_server` |
| `<id=31>` | `<id=187072>` | `references_mcp_server` |
| `<id=31>` | `<id=187073>` | `references_mcp_server` |
| `<id=36>` | `<id=187068>` | `references_mcp_server` |
| `<id=36>` | `<id=187070>` | `references_mcp_server` |
| `<id=36>` | `<id=187074>` | `references_mcp_server` |
| `<id=36>` | `<id=187075>` | `references_mcp_server` |
| `<id=37>` | `<id=187069>` | `references_mcp_server` |

### UNOBSERVED_CODE  (severity P3)

| src | dst | relation |
|---|---|---|
| `<id=8>` | `<id=14970>` | `implements` |
| `<id=8>` | `<id=18417>` | `reads_from` |
| `<id=8>` | `<id=20744>` | `reads_from` |
| `<id=8>` | `<id=28118>` | `exports` |
| `<id=8>` | `<id=28118>` | `reads_from` |
| `<id=8>` | `<id=28129>` | `exports` |
| `<id=8>` | `<id=28129>` | `reads_from` |
| `<id=8>` | `<id=28555>` | `covers` |
| `<id=8>` | `<id=28556>` | `imports` |
| `<id=8>` | `<id=55682>` | `unused_import` |

### CONFIG_BLOAT  (severity P4)

| src | dst | relation |
|---|---|---|
| `<id=187067>` | `<id=187068>` | `MCP_SERVER_DECLARED` |
| `<id=187067>` | `<id=187069>` | `MCP_SERVER_DECLARED` |
| `<id=187067>` | `<id=187070>` | `MCP_SERVER_DECLARED` |
| `<id=187067>` | `<id=187071>` | `MCP_SERVER_DECLARED` |
| `<id=187067>` | `<id=187072>` | `MCP_SERVER_DECLARED` |
| `<id=187067>` | `<id=187073>` | `MCP_SERVER_DECLARED` |
| `<id=187067>` | `<id=187074>` | `MCP_SERVER_DECLARED` |
| `<id=187067>` | `<id=187075>` | `MCP_SERVER_DECLARED` |
| `<id=187067>` | `<id=187076>` | `MCP_SERVER_DECLARED` |
| `<id=187077>` | `<id=187078>` | `AGENT_SPEC_DECLARED` |

