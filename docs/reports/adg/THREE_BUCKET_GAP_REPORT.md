# ADG Three-Bucket Gap Report

- **Generated**: 2026-04-29T19:46:05.264242+00:00
- **Snapshot**: `adg_indexed_04292026_1513.sqlite`
- **Runtime view present**: True
- **Runtime-attested edges**: 0
- **Total edges classified**: 400,462
- **Health score** (triplet-attested fraction): **0.0%**

> **Caveat**: `v_runtime_proof` exists but contains zero attested edges. The runtime bucket is empty — populate the OTel `runtime_adg_store` (e.g., run pytest with OTel exporters) and regenerate the snapshot to surface `TRIPLET_ATTESTED`, `SHADOW_CHANNEL`, and `DYNAMIC_DISPATCH` rows.


## Defect distribution

| Severity | Class | Edges | % | Description |
|---|---|---:|---:|---|
| — | **TRIPLET_ATTESTED** | 0 | 0.0% | Edge present in all three graphs — fully proven. NOT a defect. |
| P2 | **REGISTRY_DRIFT** | 0 | 0.0% | Used in code AND observed at runtime, but not declared in any registry. Undocumented coupling / accidental API. |
| P3 | **DEAD_PATH** | 0 | 0.0% | Wired in code AND declared in registry, but never traced at runtime. Untested code path or vestigial policy. |
| P3 | **UNOBSERVED_CODE** | 400,429 | 99.99% | Static-only — orphan import, dead code, or never-traced path. |
| P5 | **DYNAMIC_DISPATCH** | 0 | 0.0% | No static link, but declared + verified at runtime. Plugin / DI / lazy import — usually fine. |
| P1 | **SHADOW_CHANNEL** | 0 | 0.0% | Runtime-only undeclared edge — monkey-patch, side-effect coupling, hidden import. SECURITY-CRITICAL. |
| P4 | **CONFIG_BLOAT** | 33 | 0.01% | Declared in registry but never used in code or runtime. Dead policy / config drift. |

## Static-only vs runtime-required

**Static-only** (answerable without OTEL traces — pure registry-vs-static set diff): `REGISTRY_DRIFT`, `CONFIG_BLOAT`

**Requires runtime traces** (need OTEL span evidence to classify correctly): `TRIPLET_ATTESTED`, `DEAD_PATH`, `DYNAMIC_DISPATCH`, `SHADOW_CHANNEL`, `UNOBSERVED_CODE`

## Top samples per class

### UNOBSERVED_CODE  (severity P3)

| src | dst | relation |
|---|---|---|
| `<id=4>` | `<id=13249>` | `reads_from` |
| `<id=4>` | `<id=14012>` | `reads_from` |
| `<id=4>` | `<id=15825>` | `exports` |
| `<id=4>` | `<id=15825>` | `reads_from` |
| `<id=4>` | `<id=21061>` | `imports` |

### CONFIG_BLOAT  (severity P4)

| src | dst | relation |
|---|---|---|
| `<id=117117>` | `<id=117118>` | `MCP_SERVER_DECLARED` |
| `<id=117117>` | `<id=117119>` | `MCP_SERVER_DECLARED` |
| `<id=117117>` | `<id=117120>` | `MCP_SERVER_DECLARED` |
| `<id=117117>` | `<id=117121>` | `MCP_SERVER_DECLARED` |
| `<id=117117>` | `<id=117122>` | `MCP_SERVER_DECLARED` |

