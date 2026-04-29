# ADG Three-Bucket Gap Report

- **Generated**: 2026-04-29T17:03:20.695361+00:00
- **Snapshot**: `adg_indexed_04292026_0825.sqlite`
- **Runtime view present**: False
- **Runtime-attested edges**: 0
- **Total edges classified**: 399,637
- **Health score** (triplet-attested fraction): **0.0%**

> **Caveat**: This snapshot predates the W1 `v_runtime_proof` schema addition OR no OTel traces have been emitted yet. The runtime bucket is treated as empty, so all edges fall into static-only classes (`UNOBSERVED_CODE` / `REGISTRY_DRIFT` / `CONFIG_BLOAT`). To produce the full triplet matrix, regenerate the ADG snapshot via `python tools/generate/generate_full_adg.py` against a runtime store with attested OTel spans.


## Defect distribution

| Severity | Class | Edges | % | Description |
|---|---|---:|---:|---|
| — | **TRIPLET_ATTESTED** | 0 | 0.0% | Edge present in all three graphs — fully proven. NOT a defect. |
| P2 | **REGISTRY_DRIFT** | 0 | 0.0% | Used in code AND observed at runtime, but not declared in any registry. Undocumented coupling / accidental API. |
| P3 | **DEAD_PATH** | 0 | 0.0% | Wired in code AND declared in registry, but never traced at runtime. Untested code path or vestigial policy. |
| P3 | **UNOBSERVED_CODE** | 399,637 | 100.0% | Static-only — orphan import, dead code, or never-traced path. |
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
| `<id=4>` | `<id=13233>` | `reads_from` |
| `<id=4>` | `<id=13996>` | `reads_from` |
| `<id=4>` | `<id=15808>` | `exports` |
| `<id=4>` | `<id=15808>` | `reads_from` |
| `<id=4>` | `<id=21000>` | `imports` |

