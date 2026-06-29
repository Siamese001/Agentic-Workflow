# ADG Three-Bucket Gap Report

- **Generated**: 2026-06-29T11:19:44.777265+00:00
- **Snapshot**: `adg_indexed_06292026_0701.sqlite`
- **Runtime view present**: True
- **Runtime-attested edges**: 3,867
- **Runtime proof status**: `attested`
- **Total edges classified**: 565,527
- **Health score** (triplet-attested fraction): **0.0%**


## Defect distribution

| Severity | Class | Edges | % | Description |
|---|---|---:|---:|---|
| — | **TRIPLET_ATTESTED** | 0 | 0.0% | Edge present in all three graphs — fully proven. NOT a defect. |
| P2 | **REGISTRY_DRIFT** | 277 | 0.05% | Used in code AND observed at runtime, but not declared in any registry. Undocumented coupling / accidental API. |
| P3 | **DEAD_PATH** | 259 | 0.05% | Wired in code AND declared in registry, but never traced at runtime. Untested code path or vestigial policy. |
| P3 | **UNOBSERVED_CODE** | 564,969 | 99.9% | Static-only — orphan import, dead code, or never-traced path. |
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
| `<id=75>` | `<id=27874>` | `exports` |
| `<id=88>` | `<id=82867>` | `reads_from` |
| `<id=122>` | `<id=18615>` | `unused_import` |
| `<id=136>` | `<id=77275>` | `imports` |
| `<id=144>` | `<id=38733>` | `imports` |
| `<id=151>` | `<id=38761>` | `imports` |
| `<id=163>` | `<id=77275>` | `imports` |
| `<id=237>` | `<id=38672>` | `imports` |
| `<id=237>` | `<id=38726>` | `imports` |
| `<id=240>` | `<id=94692>` | `implements` |

### DEAD_PATH  (severity P3)

| src | dst | relation |
|---|---|---|
| `<id=28>` | `<id=186992>` | `references_mcp_server` |
| `<id=31>` | `<id=186991>` | `references_mcp_server` |
| `<id=31>` | `<id=186992>` | `references_mcp_server` |
| `<id=31>` | `<id=186995>` | `references_mcp_server` |
| `<id=31>` | `<id=186996>` | `references_mcp_server` |
| `<id=36>` | `<id=186991>` | `references_mcp_server` |
| `<id=36>` | `<id=186993>` | `references_mcp_server` |
| `<id=36>` | `<id=186997>` | `references_mcp_server` |
| `<id=36>` | `<id=186998>` | `references_mcp_server` |
| `<id=37>` | `<id=186992>` | `references_mcp_server` |

### UNOBSERVED_CODE  (severity P3)

| src | dst | relation |
|---|---|---|
| `<id=8>` | `<id=14959>` | `implements` |
| `<id=8>` | `<id=18399>` | `reads_from` |
| `<id=8>` | `<id=20726>` | `reads_from` |
| `<id=8>` | `<id=28100>` | `exports` |
| `<id=8>` | `<id=28100>` | `reads_from` |
| `<id=8>` | `<id=28111>` | `exports` |
| `<id=8>` | `<id=28111>` | `reads_from` |
| `<id=8>` | `<id=28536>` | `covers` |
| `<id=8>` | `<id=28537>` | `imports` |
| `<id=8>` | `<id=55659>` | `unused_import` |

### CONFIG_BLOAT  (severity P4)

| src | dst | relation |
|---|---|---|
| `<id=186990>` | `<id=186991>` | `MCP_SERVER_DECLARED` |
| `<id=186990>` | `<id=186992>` | `MCP_SERVER_DECLARED` |
| `<id=186990>` | `<id=186993>` | `MCP_SERVER_DECLARED` |
| `<id=186990>` | `<id=186994>` | `MCP_SERVER_DECLARED` |
| `<id=186990>` | `<id=186995>` | `MCP_SERVER_DECLARED` |
| `<id=186990>` | `<id=186996>` | `MCP_SERVER_DECLARED` |
| `<id=186990>` | `<id=186997>` | `MCP_SERVER_DECLARED` |
| `<id=186990>` | `<id=186998>` | `MCP_SERVER_DECLARED` |
| `<id=186990>` | `<id=186999>` | `MCP_SERVER_DECLARED` |
| `<id=187000>` | `<id=187001>` | `AGENT_SPEC_DECLARED` |

