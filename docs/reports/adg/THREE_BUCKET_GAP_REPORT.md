# ADG Three-Bucket Gap Report

> ⚠ **DIAGNOSTIC ONLY — RUNTIME-THIN (runtime_proof_status=view_present_zero_attested)**. This report was produced without runtime attestation; do NOT treat as certification-clean. Re-run with `--require-runtime-proof` in CI once OTel attestation is wired.

- **Generated**: 2026-06-13T14:47:54.918251+00:00
- **Snapshot**: `adg_indexed_06132026_1042.sqlite`
- **Runtime view present**: True
- **Runtime-attested edges**: 0
- **Runtime proof status**: `view_present_zero_attested`
- **Total edges classified**: 571,364
- **Health score** (triplet-attested fraction): **0.0%**

> **Caveat**: `v_runtime_proof` exists but contains zero attested edges. The runtime bucket is empty — populate the OTel `runtime_adg_store` (e.g., run pytest with OTel exporters) and regenerate the snapshot to surface `TRIPLET_ATTESTED`, `SHADOW_CHANNEL`, and `DYNAMIC_DISPATCH` rows.


## Defect distribution

| Severity | Class | Edges | % | Description |
|---|---|---:|---:|---|
| — | **TRIPLET_ATTESTED** | 0 | 0.0% | Edge present in all three graphs — fully proven. NOT a defect. |
| P2 | **REGISTRY_DRIFT** | 0 | 0.0% | Used in code AND observed at runtime, but not declared in any registry. Undocumented coupling / accidental API. |
| P3 | **DEAD_PATH** | 224 | 0.04% | Wired in code AND declared in registry, but never traced at runtime. Untested code path or vestigial policy. |
| P3 | **UNOBSERVED_CODE** | 571,119 | 99.96% | Static-only — orphan import, dead code, or never-traced path. |
| P5 | **DYNAMIC_DISPATCH** | 0 | 0.0% | No static link, but declared + verified at runtime. Plugin / DI / lazy import — usually fine. |
| P1 | **SHADOW_CHANNEL** | 0 | 0.0% | Runtime-only undeclared edge — monkey-patch, side-effect coupling, hidden import. SECURITY-CRITICAL. |
| P4 | **CONFIG_BLOAT** | 21 | 0.0% | Declared in registry but never used in code or runtime. Dead policy / config drift. |

## Static-only vs runtime-required

**Static-only** (answerable without OTEL traces — pure registry-vs-static set diff): `REGISTRY_DRIFT`, `CONFIG_BLOAT`

**Requires runtime traces** (need OTEL span evidence to classify correctly): `TRIPLET_ATTESTED`, `DEAD_PATH`, `DYNAMIC_DISPATCH`, `SHADOW_CHANNEL`, `UNOBSERVED_CODE`

## Top samples per class

### DEAD_PATH  (severity P3)

| src | dst | relation |
|---|---|---|
| `<id=47>` | `<id=184349>` | `references_mcp_server` |
| `<id=61>` | `<id=184351>` | `references_mcp_server` |
| `<id=65>` | `<id=184348>` | `references_mcp_server` |
| `<id=65>` | `<id=184350>` | `references_mcp_server` |
| `<id=65>` | `<id=184353>` | `references_mcp_server` |
| `<id=65>` | `<id=184354>` | `references_mcp_server` |
| `<id=67>` | `<id=184349>` | `references_mcp_server` |
| `<id=67>` | `<id=184351>` | `references_mcp_server` |
| `<id=83>` | `<id=184351>` | `references_mcp_server` |
| `<id=83>` | `<id=184353>` | `references_mcp_server` |

### UNOBSERVED_CODE  (severity P3)

| src | dst | relation |
|---|---|---|
| `<id=8>` | `<id=15482>` | `implements` |
| `<id=8>` | `<id=18998>` | `reads_from` |
| `<id=8>` | `<id=21377>` | `reads_from` |
| `<id=8>` | `<id=28542>` | `exports` |
| `<id=8>` | `<id=28542>` | `reads_from` |
| `<id=8>` | `<id=28554>` | `exports` |
| `<id=8>` | `<id=28554>` | `reads_from` |
| `<id=8>` | `<id=29005>` | `covers` |
| `<id=8>` | `<id=29006>` | `imports` |
| `<id=8>` | `<id=56517>` | `unused_import` |

### CONFIG_BLOAT  (severity P4)

| src | dst | relation |
|---|---|---|
| `<id=184347>` | `<id=184348>` | `MCP_SERVER_DECLARED` |
| `<id=184347>` | `<id=184349>` | `MCP_SERVER_DECLARED` |
| `<id=184347>` | `<id=184350>` | `MCP_SERVER_DECLARED` |
| `<id=184347>` | `<id=184351>` | `MCP_SERVER_DECLARED` |
| `<id=184347>` | `<id=184352>` | `MCP_SERVER_DECLARED` |
| `<id=184347>` | `<id=184353>` | `MCP_SERVER_DECLARED` |
| `<id=184347>` | `<id=184354>` | `MCP_SERVER_DECLARED` |
| `<id=184347>` | `<id=184355>` | `MCP_SERVER_DECLARED` |
| `<id=184356>` | `<id=184357>` | `AGENT_SPEC_DECLARED` |
| `<id=184356>` | `<id=184358>` | `AGENT_SPEC_DECLARED` |

