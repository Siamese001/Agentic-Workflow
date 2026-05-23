# ADG Three-Bucket Gap Report

- **Generated**: 2026-05-23T23:07:18.180613+00:00
- **Snapshot**: `adg_indexed_05232026_1851.sqlite`
- **Runtime view present**: True
- **Runtime-attested edges**: 3,410
- **Runtime proof status**: `attested`
- **Total edges classified**: 546,982
- **Health score** (triplet-attested fraction): **0.0%**


## Defect distribution

| Severity | Class | Edges | % | Description |
|---|---|---:|---:|---|
| — | **TRIPLET_ATTESTED** | 0 | 0.0% | Edge present in all three graphs — fully proven. NOT a defect. |
| P2 | **REGISTRY_DRIFT** | 0 | 0.0% | Used in code AND observed at runtime, but not declared in any registry. Undocumented coupling / accidental API. |
| P3 | **DEAD_PATH** | 0 | 0.0% | Wired in code AND declared in registry, but never traced at runtime. Untested code path or vestigial policy. |
| P3 | **UNOBSERVED_CODE** | 546,982 | 100.0% | Static-only — orphan import, dead code, or never-traced path. |
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
| `<id=8>` | `<id=4>` | `belongs_to_layer` |
| `<id=8>` | `<id=14965>` | `implements` |
| `<id=8>` | `<id=18411>` | `reads_from` |
| `<id=8>` | `<id=20785>` | `reads_from` |
| `<id=8>` | `<id=27925>` | `exports` |
| `<id=8>` | `<id=27925>` | `reads_from` |
| `<id=8>` | `<id=27937>` | `exports` |
| `<id=8>` | `<id=27937>` | `reads_from` |
| `<id=8>` | `<id=28349>` | `covers` |
| `<id=8>` | `<id=28350>` | `imports` |

