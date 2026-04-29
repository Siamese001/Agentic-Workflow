# ADG Three-Bucket Gap Report

- **Generated**: 2026-04-29T20:03:48.555128+00:00
- **Snapshot**: `adg_indexed_04292026_1513.sqlite`
- **Runtime view present**: True
- **Runtime-attested edges**: 127
- **Total edges classified**: 400,462
- **Health score** (triplet-attested fraction): **0.0%**


## Defect distribution

| Severity | Class | Edges | % | Description |
|---|---|---:|---:|---|
| — | **TRIPLET_ATTESTED** | 0 | 0.0% | Edge present in all three graphs — fully proven. NOT a defect. |
| P2 | **REGISTRY_DRIFT** | 127 | 0.03% | Used in code AND observed at runtime, but not declared in any registry. Undocumented coupling / accidental API. |
| P3 | **DEAD_PATH** | 0 | 0.0% | Wired in code AND declared in registry, but never traced at runtime. Untested code path or vestigial policy. |
| P3 | **UNOBSERVED_CODE** | 400,302 | 99.96% | Static-only — orphan import, dead code, or never-traced path. |
| P5 | **DYNAMIC_DISPATCH** | 0 | 0.0% | No static link, but declared + verified at runtime. Plugin / DI / lazy import — usually fine. |
| P1 | **SHADOW_CHANNEL** | 0 | 0.0% | Runtime-only undeclared edge — monkey-patch, side-effect coupling, hidden import. SECURITY-CRITICAL. |
| P4 | **CONFIG_BLOAT** | 33 | 0.01% | Declared in registry but never used in code or runtime. Dead policy / config drift. |

## Static-only vs runtime-required

**Static-only** (answerable without OTEL traces — pure registry-vs-static set diff): `REGISTRY_DRIFT`, `CONFIG_BLOAT`

**Requires runtime traces** (need OTEL span evidence to classify correctly): `TRIPLET_ATTESTED`, `DEAD_PATH`, `DYNAMIC_DISPATCH`, `SHADOW_CHANNEL`, `UNOBSERVED_CODE`

## Top samples per class

### REGISTRY_DRIFT  (severity P2)

| src | dst | relation |
|---|---|---|
| `<id=21>` | `<id=65332>` | `reads_from` |
| `<id=66>` | `<id=51600>` | `applies` |
| `<id=162>` | `<id=53455>` | `reads_from` |
| `<id=253>` | `<id=14156>` | `reads_from` |
| `<id=320>` | `<id=56682>` | `reads_from` |
| `<id=340>` | `<id=51903>` | `reads_from` |
| `<id=376>` | `<id=55734>` | `imports` |
| `<id=399>` | `<id=29574>` | `imports` |
| `<id=590>` | `<id=29478>` | `imports` |
| `<id=678>` | `<id=21379>` | `writes_to` |

### UNOBSERVED_CODE  (severity P3)

| src | dst | relation |
|---|---|---|
| `<id=4>` | `<id=13249>` | `reads_from` |
| `<id=4>` | `<id=14012>` | `reads_from` |
| `<id=4>` | `<id=15825>` | `exports` |
| `<id=4>` | `<id=15825>` | `reads_from` |
| `<id=4>` | `<id=21061>` | `imports` |
| `<id=4>` | `<id=43981>` | `unused_import` |
| `<id=4>` | `<id=49386>` | `reads_from` |
| `<id=4>` | `<id=51600>` | `applies` |
| `<id=4>` | `<id=51605>` | `imports` |
| `<id=4>` | `<id=51616>` | `imports` |

### CONFIG_BLOAT  (severity P4)

| src | dst | relation |
|---|---|---|
| `<id=117117>` | `<id=117118>` | `MCP_SERVER_DECLARED` |
| `<id=117117>` | `<id=117119>` | `MCP_SERVER_DECLARED` |
| `<id=117117>` | `<id=117120>` | `MCP_SERVER_DECLARED` |
| `<id=117117>` | `<id=117121>` | `MCP_SERVER_DECLARED` |
| `<id=117117>` | `<id=117122>` | `MCP_SERVER_DECLARED` |
| `<id=117117>` | `<id=117123>` | `MCP_SERVER_DECLARED` |
| `<id=117117>` | `<id=117124>` | `MCP_SERVER_DECLARED` |
| `<id=117117>` | `<id=117125>` | `MCP_SERVER_DECLARED` |
| `<id=117117>` | `<id=117126>` | `MCP_SERVER_DECLARED` |
| `<id=117117>` | `<id=117127>` | `MCP_SERVER_DECLARED` |

