# ADG Three-Bucket Gap Report

- **Generated**: 2026-06-23T06:13:12.509477+00:00
- **Snapshot**: `adg_indexed_06232026_0201.sqlite`
- **Runtime view present**: True
- **Runtime-attested edges**: 3,867
- **Runtime proof status**: `attested`
- **Total edges classified**: 561,892
- **Health score** (triplet-attested fraction): **0.0%**


## Defect distribution

| Severity | Class | Edges | % | Description |
|---|---|---:|---:|---|
| — | **TRIPLET_ATTESTED** | 0 | 0.0% | Edge present in all three graphs — fully proven. NOT a defect. |
| P2 | **REGISTRY_DRIFT** | 277 | 0.05% | Used in code AND observed at runtime, but not declared in any registry. Undocumented coupling / accidental API. |
| P3 | **DEAD_PATH** | 258 | 0.05% | Wired in code AND declared in registry, but never traced at runtime. Untested code path or vestigial policy. |
| P3 | **UNOBSERVED_CODE** | 561,335 | 99.9% | Static-only — orphan import, dead code, or never-traced path. |
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
| `<id=75>` | `<id=27776>` | `exports` |
| `<id=88>` | `<id=82091>` | `reads_from` |
| `<id=122>` | `<id=18523>` | `unused_import` |
| `<id=136>` | `<id=76516>` | `imports` |
| `<id=144>` | `<id=38625>` | `imports` |
| `<id=151>` | `<id=38653>` | `imports` |
| `<id=163>` | `<id=76516>` | `imports` |
| `<id=237>` | `<id=38564>` | `imports` |
| `<id=237>` | `<id=38618>` | `imports` |
| `<id=240>` | `<id=93852>` | `implements` |

### DEAD_PATH  (severity P3)

| src | dst | relation |
|---|---|---|
| `<id=28>` | `<id=185432>` | `references_mcp_server` |
| `<id=31>` | `<id=185431>` | `references_mcp_server` |
| `<id=31>` | `<id=185432>` | `references_mcp_server` |
| `<id=31>` | `<id=185435>` | `references_mcp_server` |
| `<id=31>` | `<id=185436>` | `references_mcp_server` |
| `<id=36>` | `<id=185431>` | `references_mcp_server` |
| `<id=36>` | `<id=185433>` | `references_mcp_server` |
| `<id=36>` | `<id=185437>` | `references_mcp_server` |
| `<id=36>` | `<id=185438>` | `references_mcp_server` |
| `<id=37>` | `<id=185432>` | `references_mcp_server` |

### UNOBSERVED_CODE  (severity P3)

| src | dst | relation |
|---|---|---|
| `<id=8>` | `<id=14875>` | `implements` |
| `<id=8>` | `<id=18307>` | `reads_from` |
| `<id=8>` | `<id=20632>` | `reads_from` |
| `<id=8>` | `<id=28003>` | `exports` |
| `<id=8>` | `<id=28003>` | `reads_from` |
| `<id=8>` | `<id=28014>` | `exports` |
| `<id=8>` | `<id=28014>` | `reads_from` |
| `<id=8>` | `<id=28440>` | `covers` |
| `<id=8>` | `<id=28441>` | `imports` |
| `<id=8>` | `<id=55557>` | `unused_import` |

### CONFIG_BLOAT  (severity P4)

| src | dst | relation |
|---|---|---|
| `<id=185430>` | `<id=185431>` | `MCP_SERVER_DECLARED` |
| `<id=185430>` | `<id=185432>` | `MCP_SERVER_DECLARED` |
| `<id=185430>` | `<id=185433>` | `MCP_SERVER_DECLARED` |
| `<id=185430>` | `<id=185434>` | `MCP_SERVER_DECLARED` |
| `<id=185430>` | `<id=185435>` | `MCP_SERVER_DECLARED` |
| `<id=185430>` | `<id=185436>` | `MCP_SERVER_DECLARED` |
| `<id=185430>` | `<id=185437>` | `MCP_SERVER_DECLARED` |
| `<id=185430>` | `<id=185438>` | `MCP_SERVER_DECLARED` |
| `<id=185430>` | `<id=185439>` | `MCP_SERVER_DECLARED` |
| `<id=185440>` | `<id=185441>` | `AGENT_SPEC_DECLARED` |

