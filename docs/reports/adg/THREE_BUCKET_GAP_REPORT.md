# ADG Three-Bucket Gap Report

- **Generated**: 2026-06-28T03:14:44.645995+00:00
- **Snapshot**: `adg_indexed_06272026_2302.sqlite`
- **Runtime view present**: True
- **Runtime-attested edges**: 3,867
- **Runtime proof status**: `attested`
- **Total edges classified**: 564,615
- **Health score** (triplet-attested fraction): **0.0%**


## Defect distribution

| Severity | Class | Edges | % | Description |
|---|---|---:|---:|---|
| — | **TRIPLET_ATTESTED** | 0 | 0.0% | Edge present in all three graphs — fully proven. NOT a defect. |
| P2 | **REGISTRY_DRIFT** | 277 | 0.05% | Used in code AND observed at runtime, but not declared in any registry. Undocumented coupling / accidental API. |
| P3 | **DEAD_PATH** | 259 | 0.05% | Wired in code AND declared in registry, but never traced at runtime. Untested code path or vestigial policy. |
| P3 | **UNOBSERVED_CODE** | 564,057 | 99.9% | Static-only — orphan import, dead code, or never-traced path. |
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
| `<id=75>` | `<id=27846>` | `exports` |
| `<id=88>` | `<id=82689>` | `reads_from` |
| `<id=122>` | `<id=18594>` | `unused_import` |
| `<id=136>` | `<id=77098>` | `imports` |
| `<id=144>` | `<id=38704>` | `imports` |
| `<id=151>` | `<id=38732>` | `imports` |
| `<id=163>` | `<id=77098>` | `imports` |
| `<id=237>` | `<id=38643>` | `imports` |
| `<id=237>` | `<id=38697>` | `imports` |
| `<id=240>` | `<id=94483>` | `implements` |

### DEAD_PATH  (severity P3)

| src | dst | relation |
|---|---|---|
| `<id=28>` | `<id=186594>` | `references_mcp_server` |
| `<id=31>` | `<id=186593>` | `references_mcp_server` |
| `<id=31>` | `<id=186594>` | `references_mcp_server` |
| `<id=31>` | `<id=186597>` | `references_mcp_server` |
| `<id=31>` | `<id=186598>` | `references_mcp_server` |
| `<id=36>` | `<id=186593>` | `references_mcp_server` |
| `<id=36>` | `<id=186595>` | `references_mcp_server` |
| `<id=36>` | `<id=186599>` | `references_mcp_server` |
| `<id=36>` | `<id=186600>` | `references_mcp_server` |
| `<id=37>` | `<id=186594>` | `references_mcp_server` |

### UNOBSERVED_CODE  (severity P3)

| src | dst | relation |
|---|---|---|
| `<id=8>` | `<id=14938>` | `implements` |
| `<id=8>` | `<id=18378>` | `reads_from` |
| `<id=8>` | `<id=20704>` | `reads_from` |
| `<id=8>` | `<id=28072>` | `exports` |
| `<id=8>` | `<id=28072>` | `reads_from` |
| `<id=8>` | `<id=28083>` | `exports` |
| `<id=8>` | `<id=28083>` | `reads_from` |
| `<id=8>` | `<id=28508>` | `covers` |
| `<id=8>` | `<id=28509>` | `imports` |
| `<id=8>` | `<id=55651>` | `unused_import` |

### CONFIG_BLOAT  (severity P4)

| src | dst | relation |
|---|---|---|
| `<id=186592>` | `<id=186593>` | `MCP_SERVER_DECLARED` |
| `<id=186592>` | `<id=186594>` | `MCP_SERVER_DECLARED` |
| `<id=186592>` | `<id=186595>` | `MCP_SERVER_DECLARED` |
| `<id=186592>` | `<id=186596>` | `MCP_SERVER_DECLARED` |
| `<id=186592>` | `<id=186597>` | `MCP_SERVER_DECLARED` |
| `<id=186592>` | `<id=186598>` | `MCP_SERVER_DECLARED` |
| `<id=186592>` | `<id=186599>` | `MCP_SERVER_DECLARED` |
| `<id=186592>` | `<id=186600>` | `MCP_SERVER_DECLARED` |
| `<id=186592>` | `<id=186601>` | `MCP_SERVER_DECLARED` |
| `<id=186602>` | `<id=186603>` | `AGENT_SPEC_DECLARED` |

