# ADG Three-Bucket Gap Report

- **Generated**: 2026-05-25T08:32:57.469711+00:00
- **Snapshot**: `adg_indexed_05252026_0415.sqlite`
- **Runtime view present**: True
- **Runtime-attested edges**: 3,865
- **Runtime proof status**: `attested`
- **Total edges classified**: 551,876
- **Health score** (triplet-attested fraction): **0.0%**


## Defect distribution

| Severity | Class | Edges | % | Description |
|---|---|---:|---:|---|
| — | **TRIPLET_ATTESTED** | 0 | 0.0% | Edge present in all three graphs — fully proven. NOT a defect. |
| P2 | **REGISTRY_DRIFT** | 309 | 0.06% | Used in code AND observed at runtime, but not declared in any registry. Undocumented coupling / accidental API. |
| P3 | **DEAD_PATH** | 311 | 0.06% | Wired in code AND declared in registry, but never traced at runtime. Untested code path or vestigial policy. |
| P3 | **UNOBSERVED_CODE** | 551,229 | 99.88% | Static-only — orphan import, dead code, or never-traced path. |
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
| `<id=48>` | `<id=70955>` | `reads_from` |
| `<id=117>` | `<id=20471>` | `writes_to` |
| `<id=123>` | `<id=77722>` | `exports` |
| `<id=143>` | `<id=27704>` | `exports` |
| `<id=156>` | `<id=77293>` | `reads_from` |
| `<id=189>` | `<id=18636>` | `unused_import` |
| `<id=203>` | `<id=71828>` | `imports` |
| `<id=211>` | `<id=37850>` | `imports` |
| `<id=218>` | `<id=37878>` | `imports` |
| `<id=230>` | `<id=71828>` | `imports` |

### DEAD_PATH  (severity P3)

| src | dst | relation |
|---|---|---|
| `<id=176>` | `<id=176548>` | `references_mcp_server` |
| `<id=204>` | `<id=176548>` | `references_mcp_server` |
| `<id=259>` | `<id=176548>` | `references_mcp_server` |
| `<id=277>` | `<id=176547>` | `references_mcp_server` |
| `<id=340>` | `<id=176548>` | `references_mcp_server` |
| `<id=349>` | `<id=176547>` | `references_mcp_server` |
| `<id=358>` | `<id=176548>` | `references_mcp_server` |
| `<id=369>` | `<id=176548>` | `references_mcp_server` |
| `<id=385>` | `<id=176547>` | `references_mcp_server` |
| `<id=406>` | `<id=176548>` | `references_mcp_server` |

### UNOBSERVED_CODE  (severity P3)

| src | dst | relation |
|---|---|---|
| `<id=8>` | `<id=4>` | `belongs_to_layer` |
| `<id=8>` | `<id=14943>` | `implements` |
| `<id=8>` | `<id=18412>` | `reads_from` |
| `<id=8>` | `<id=20791>` | `reads_from` |
| `<id=8>` | `<id=27937>` | `exports` |
| `<id=8>` | `<id=27937>` | `reads_from` |
| `<id=8>` | `<id=27949>` | `exports` |
| `<id=8>` | `<id=27949>` | `reads_from` |
| `<id=8>` | `<id=28364>` | `covers` |
| `<id=8>` | `<id=28365>` | `imports` |

### CONFIG_BLOAT  (severity P4)

| src | dst | relation |
|---|---|---|
| `<id=176543>` | `<id=176544>` | `MCP_SERVER_DECLARED` |
| `<id=176543>` | `<id=176545>` | `MCP_SERVER_DECLARED` |
| `<id=176543>` | `<id=176546>` | `MCP_SERVER_DECLARED` |
| `<id=176543>` | `<id=176547>` | `MCP_SERVER_DECLARED` |
| `<id=176543>` | `<id=176548>` | `MCP_SERVER_DECLARED` |
| `<id=176543>` | `<id=176549>` | `MCP_SERVER_DECLARED` |
| `<id=176543>` | `<id=176550>` | `MCP_SERVER_DECLARED` |
| `<id=176543>` | `<id=176551>` | `MCP_SERVER_DECLARED` |
| `<id=176543>` | `<id=176552>` | `MCP_SERVER_DECLARED` |
| `<id=176543>` | `<id=176553>` | `MCP_SERVER_DECLARED` |

