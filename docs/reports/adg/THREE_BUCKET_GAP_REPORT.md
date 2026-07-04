# ADG Three-Bucket Gap Report

> ⚠ **DIAGNOSTIC ONLY — RUNTIME-THIN (runtime_proof_status=view_present_zero_attested)**. This report was produced without runtime attestation; do NOT treat as certification-clean. Re-run with `--require-runtime-proof` in CI once OTel attestation is wired.

- **Generated**: 2026-07-04T13:01:03.897643+00:00
- **Snapshot**: `adg_indexed_07042026_0851.sqlite`
- **Runtime view present**: True
- **Runtime-attested edges**: 0
- **Runtime proof status**: `view_present_zero_attested`
- **Total edges classified**: 567,488
- **Health score** (triplet-attested fraction): **0.0%**

> **Caveat**: `v_runtime_proof` exists but contains zero attested edges. The runtime bucket is empty — populate the OTel `runtime_adg_store` (e.g., run pytest with OTel exporters) and regenerate the snapshot to surface `TRIPLET_ATTESTED`, `SHADOW_CHANNEL`, and `DYNAMIC_DISPATCH` rows.


## Defect distribution

| Severity | Class | Edges | % | Description |
|---|---|---:|---:|---|
| — | **TRIPLET_ATTESTED** | 0 | 0.0% | Edge present in all three graphs — fully proven. NOT a defect. |
| P2 | **REGISTRY_DRIFT** | 0 | 0.0% | Used in code AND observed at runtime, but not declared in any registry. Undocumented coupling / accidental API. |
| P3 | **DEAD_PATH** | 252 | 0.04% | Wired in code AND declared in registry, but never traced at runtime. Untested code path or vestigial policy. |
| P3 | **UNOBSERVED_CODE** | 567,214 | 99.95% | Static-only — orphan import, dead code, or never-traced path. |
| P5 | **DYNAMIC_DISPATCH** | 0 | 0.0% | No static link, but declared + verified at runtime. Plugin / DI / lazy import — usually fine. |
| P1 | **SHADOW_CHANNEL** | 0 | 0.0% | Runtime-only undeclared edge — monkey-patch, side-effect coupling, hidden import. SECURITY-CRITICAL. |
| P4 | **CONFIG_BLOAT** | 22 | 0.0% | Declared in registry but never used in code or runtime. Dead policy / config drift. |

## Static-only vs runtime-required

**Static-only** (answerable without OTEL traces — pure registry-vs-static set diff): `REGISTRY_DRIFT`, `CONFIG_BLOAT`

**Requires runtime traces** (need OTEL span evidence to classify correctly): `TRIPLET_ATTESTED`, `DEAD_PATH`, `DYNAMIC_DISPATCH`, `SHADOW_CHANNEL`, `UNOBSERVED_CODE`

## Top samples per class

### DEAD_PATH  (severity P3)

| src | dst | relation |
|---|---|---|
| `<id=27>` | `<id=187798>` | `references_mcp_server` |
| `<id=27>` | `<id=187799>` | `references_mcp_server` |
| `<id=27>` | `<id=187802>` | `references_mcp_server` |
| `<id=27>` | `<id=187803>` | `references_mcp_server` |
| `<id=28>` | `<id=187799>` | `references_mcp_server` |
| `<id=31>` | `<id=187798>` | `references_mcp_server` |
| `<id=31>` | `<id=187799>` | `references_mcp_server` |
| `<id=31>` | `<id=187802>` | `references_mcp_server` |
| `<id=31>` | `<id=187803>` | `references_mcp_server` |
| `<id=32>` | `<id=187798>` | `references_mcp_server` |

### UNOBSERVED_CODE  (severity P3)

| src | dst | relation |
|---|---|---|
| `<id=7>` | `<id=15054>` | `implements` |
| `<id=7>` | `<id=18501>` | `reads_from` |
| `<id=7>` | `<id=20831>` | `reads_from` |
| `<id=7>` | `<id=28209>` | `exports` |
| `<id=7>` | `<id=28209>` | `reads_from` |
| `<id=7>` | `<id=28220>` | `exports` |
| `<id=7>` | `<id=28220>` | `reads_from` |
| `<id=7>` | `<id=28646>` | `covers` |
| `<id=7>` | `<id=28647>` | `imports` |
| `<id=7>` | `<id=55792>` | `unused_import` |

### CONFIG_BLOAT  (severity P4)

| src | dst | relation |
|---|---|---|
| `<id=187797>` | `<id=187798>` | `MCP_SERVER_DECLARED` |
| `<id=187797>` | `<id=187799>` | `MCP_SERVER_DECLARED` |
| `<id=187797>` | `<id=187800>` | `MCP_SERVER_DECLARED` |
| `<id=187797>` | `<id=187801>` | `MCP_SERVER_DECLARED` |
| `<id=187797>` | `<id=187802>` | `MCP_SERVER_DECLARED` |
| `<id=187797>` | `<id=187803>` | `MCP_SERVER_DECLARED` |
| `<id=187797>` | `<id=187804>` | `MCP_SERVER_DECLARED` |
| `<id=187797>` | `<id=187805>` | `MCP_SERVER_DECLARED` |
| `<id=187797>` | `<id=187806>` | `MCP_SERVER_DECLARED` |
| `<id=187807>` | `<id=187808>` | `AGENT_SPEC_DECLARED` |

