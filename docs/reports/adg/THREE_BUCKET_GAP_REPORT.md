# ADG Three-Bucket Gap Report

- **Generated**: 2026-04-29T22:37:03.183367+00:00
- **Snapshot**: `adg_indexed_04292026_1606.sqlite`
- **Runtime view present**: True
- **Runtime-attested edges**: 3,073
- **Total edges classified**: 400,890
- **Health score** (triplet-attested fraction): **0.06%**


## Defect distribution

| Severity | Class | Edges | % | Description |
|---|---|---:|---:|---|
| — | **TRIPLET_ATTESTED** | 248 | 0.06% | Edge present in all three graphs — fully proven. NOT a defect. |
| P2 | **REGISTRY_DRIFT** | 2,825 | 0.7% | Used in code AND observed at runtime, but not declared in any registry. Undocumented coupling / accidental API. |
| P3 | **DEAD_PATH** | 0 | 0.0% | Wired in code AND declared in registry, but never traced at runtime. Untested code path or vestigial policy. |
| P3 | **UNOBSERVED_CODE** | 397,784 | 99.23% | Static-only — orphan import, dead code, or never-traced path. |
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
| `<id=4>` | `<id=43988>` | `unused_import` |
| `<id=13>` | `<id=117132>` | `antipattern` |
| `<id=18>` | `<id=20802>` | `reads_from` |
| `<id=21>` | `<id=57058>` | `imports` |
| `<id=21>` | `<id=57269>` | `reads_from` |
| `<id=21>` | `<id=65340>` | `reads_from` |
| `<id=32>` | `<id=56689>` | `reads_from` |
| `<id=37>` | `<id=65340>` | `reads_from` |
| `<id=38>` | `<id=65340>` | `reads_from` |
| `<id=39>` | `<id=51910>` | `reads_from` |

### UNOBSERVED_CODE  (severity P3)

| src | dst | relation |
|---|---|---|
| `<id=4>` | `<id=13251>` | `reads_from` |
| `<id=4>` | `<id=14014>` | `reads_from` |
| `<id=4>` | `<id=15827>` | `exports` |
| `<id=4>` | `<id=15827>` | `reads_from` |
| `<id=4>` | `<id=21068>` | `imports` |
| `<id=4>` | `<id=49393>` | `reads_from` |
| `<id=4>` | `<id=51607>` | `applies` |
| `<id=4>` | `<id=51612>` | `imports` |
| `<id=4>` | `<id=51623>` | `imports` |
| `<id=4>` | `<id=51628>` | `imports` |

### CONFIG_BLOAT  (severity P4)

| src | dst | relation |
|---|---|---|
| `<id=117161>` | `<id=117162>` | `MCP_SERVER_DECLARED` |
| `<id=117161>` | `<id=117163>` | `MCP_SERVER_DECLARED` |
| `<id=117161>` | `<id=117164>` | `MCP_SERVER_DECLARED` |
| `<id=117161>` | `<id=117165>` | `MCP_SERVER_DECLARED` |
| `<id=117161>` | `<id=117166>` | `MCP_SERVER_DECLARED` |
| `<id=117161>` | `<id=117167>` | `MCP_SERVER_DECLARED` |
| `<id=117161>` | `<id=117168>` | `MCP_SERVER_DECLARED` |
| `<id=117161>` | `<id=117169>` | `MCP_SERVER_DECLARED` |
| `<id=117161>` | `<id=117170>` | `MCP_SERVER_DECLARED` |
| `<id=117161>` | `<id=117171>` | `MCP_SERVER_DECLARED` |

