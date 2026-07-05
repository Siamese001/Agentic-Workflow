# ADG Three-Bucket Gap Report

> ⚠ **DIAGNOSTIC ONLY — RUNTIME-THIN (runtime_proof_status=view_present_zero_attested)**. This report was produced without runtime attestation; do NOT treat as certification-clean. Re-run with `--require-runtime-proof` in CI once OTel attestation is wired.

- **Generated**: 2026-07-05T03:18:02.882779+00:00
- **Snapshot**: `adg_indexed_07042026_2305.sqlite`
- **Runtime view present**: True
- **Runtime-attested edges**: 0
- **Runtime proof status**: `view_present_zero_attested`
- **Total edges classified**: 567,825
- **Health score** (triplet-attested fraction): **0.0%**

> **Caveat**: `v_runtime_proof` exists but contains zero attested edges. The runtime bucket is empty — populate the OTel `runtime_adg_store` (e.g., run pytest with OTel exporters) and regenerate the snapshot to surface `TRIPLET_ATTESTED`, `SHADOW_CHANNEL`, and `DYNAMIC_DISPATCH` rows.


## Defect distribution

| Severity | Class | Edges | % | Description |
|---|---|---:|---:|---|
| — | **TRIPLET_ATTESTED** | 0 | 0.0% | Edge present in all three graphs — fully proven. NOT a defect. |
| P2 | **REGISTRY_DRIFT** | 0 | 0.0% | Used in code AND observed at runtime, but not declared in any registry. Undocumented coupling / accidental API. |
| P3 | **DEAD_PATH** | 253 | 0.04% | Wired in code AND declared in registry, but never traced at runtime. Untested code path or vestigial policy. |
| P3 | **UNOBSERVED_CODE** | 567,550 | 99.95% | Static-only — orphan import, dead code, or never-traced path. |
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
| `<id=27>` | `<id=187955>` | `references_mcp_server` |
| `<id=27>` | `<id=187956>` | `references_mcp_server` |
| `<id=27>` | `<id=187959>` | `references_mcp_server` |
| `<id=27>` | `<id=187960>` | `references_mcp_server` |
| `<id=28>` | `<id=187956>` | `references_mcp_server` |
| `<id=31>` | `<id=187955>` | `references_mcp_server` |
| `<id=31>` | `<id=187956>` | `references_mcp_server` |
| `<id=31>` | `<id=187959>` | `references_mcp_server` |
| `<id=31>` | `<id=187960>` | `references_mcp_server` |
| `<id=32>` | `<id=187955>` | `references_mcp_server` |

### UNOBSERVED_CODE  (severity P3)

| src | dst | relation |
|---|---|---|
| `<id=7>` | `<id=15058>` | `implements` |
| `<id=7>` | `<id=18508>` | `reads_from` |
| `<id=7>` | `<id=20838>` | `reads_from` |
| `<id=7>` | `<id=28216>` | `exports` |
| `<id=7>` | `<id=28216>` | `reads_from` |
| `<id=7>` | `<id=28227>` | `exports` |
| `<id=7>` | `<id=28227>` | `reads_from` |
| `<id=7>` | `<id=28653>` | `covers` |
| `<id=7>` | `<id=28654>` | `imports` |
| `<id=7>` | `<id=55809>` | `unused_import` |

### CONFIG_BLOAT  (severity P4)

| src | dst | relation |
|---|---|---|
| `<id=187954>` | `<id=187955>` | `MCP_SERVER_DECLARED` |
| `<id=187954>` | `<id=187956>` | `MCP_SERVER_DECLARED` |
| `<id=187954>` | `<id=187957>` | `MCP_SERVER_DECLARED` |
| `<id=187954>` | `<id=187958>` | `MCP_SERVER_DECLARED` |
| `<id=187954>` | `<id=187959>` | `MCP_SERVER_DECLARED` |
| `<id=187954>` | `<id=187960>` | `MCP_SERVER_DECLARED` |
| `<id=187954>` | `<id=187961>` | `MCP_SERVER_DECLARED` |
| `<id=187954>` | `<id=187962>` | `MCP_SERVER_DECLARED` |
| `<id=187954>` | `<id=187963>` | `MCP_SERVER_DECLARED` |
| `<id=187964>` | `<id=187965>` | `AGENT_SPEC_DECLARED` |

