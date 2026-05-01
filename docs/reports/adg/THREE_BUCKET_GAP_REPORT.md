# ADG Three-Bucket Gap Report

- **Generated**: 2026-04-30T23:34:37.413432+00:00
- **Snapshot**: `adg_indexed_04302026_1933.sqlite`
- **Runtime view present**: True
- **Runtime-attested edges**: 0
- **Total edges classified**: 424,921
- **Health score** (triplet-attested fraction): **0.0%**

> **Caveat**: `v_runtime_proof` exists but contains zero attested edges. The runtime bucket is empty — populate the OTel `runtime_adg_store` (e.g., run pytest with OTel exporters) and regenerate the snapshot to surface `TRIPLET_ATTESTED`, `SHADOW_CHANNEL`, and `DYNAMIC_DISPATCH` rows.


## Defect distribution

| Severity | Class | Edges | % | Description |
|---|---|---:|---:|---|
| — | **TRIPLET_ATTESTED** | 0 | 0.0% | Edge present in all three graphs — fully proven. NOT a defect. |
| P2 | **REGISTRY_DRIFT** | 0 | 0.0% | Used in code AND observed at runtime, but not declared in any registry. Undocumented coupling / accidental API. |
| P3 | **DEAD_PATH** | 0 | 0.0% | Wired in code AND declared in registry, but never traced at runtime. Untested code path or vestigial policy. |
| P3 | **UNOBSERVED_CODE** | 424,921 | 100.0% | Static-only — orphan import, dead code, or never-traced path. |
| P5 | **DYNAMIC_DISPATCH** | 0 | 0.0% | No static link, but declared + verified at runtime. Plugin / DI / lazy import — usually fine. |
| P1 | **SHADOW_CHANNEL** | 0 | 0.0% | Runtime-only undeclared edge — monkey-patch, side-effect coupling, hidden import. SECURITY-CRITICAL. |
| P4 | **CONFIG_BLOAT** | 0 | 0.0% | Declared in registry but never used in code or runtime. Dead policy / config drift. |

## Static-only vs runtime-required

**Static-only** (answerable without OTEL traces — pure registry-vs-static set diff): `REGISTRY_DRIFT`, `CONFIG_BLOAT`

**Requires runtime traces** (need OTEL span evidence to classify correctly): `TRIPLET_ATTESTED`, `DEAD_PATH`, `DYNAMIC_DISPATCH`, `SHADOW_CHANNEL`, `UNOBSERVED_CODE`

## Top samples per class

### UNOBSERVED_CODE  (severity P3)

| src | dst | relation |
|---|---|---|
| `<id=5>` | `<id=1>` | `belongs_to_layer` |
| `<id=5>` | `<id=13826>` | `reads_from` |
| `<id=5>` | `<id=14600>` | `reads_from` |
| `<id=5>` | `<id=16447>` | `exports` |
| `<id=5>` | `<id=16447>` | `reads_from` |
| `<id=5>` | `<id=21910>` | `imports` |
| `<id=5>` | `<id=45006>` | `unused_import` |
| `<id=5>` | `<id=51230>` | `reads_from` |
| `<id=5>` | `<id=53517>` | `applies` |
| `<id=5>` | `<id=53522>` | `imports` |

