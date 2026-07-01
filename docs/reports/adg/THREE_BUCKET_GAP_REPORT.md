# ADG Three-Bucket Gap Report

> ⚠ **DIAGNOSTIC ONLY — RUNTIME-THIN (runtime_proof_status=view_present_zero_attested)**. This report was produced without runtime attestation; do NOT treat as certification-clean. Re-run with `--require-runtime-proof` in CI once OTel attestation is wired.

- **Generated**: 2026-07-01T09:07:16.146357+00:00
- **Snapshot**: `adg_indexed_07012026_0451.sqlite`
- **Runtime view present**: True
- **Runtime-attested edges**: 0
- **Runtime proof status**: `view_present_zero_attested`
- **Total edges classified**: 565,627
- **Health score** (triplet-attested fraction): **0.0%**

> **Caveat**: `v_runtime_proof` exists but contains zero attested edges. The runtime bucket is empty — populate the OTel `runtime_adg_store` (e.g., run pytest with OTel exporters) and regenerate the snapshot to surface `TRIPLET_ATTESTED`, `SHADOW_CHANNEL`, and `DYNAMIC_DISPATCH` rows.


## Defect distribution

| Severity | Class | Edges | % | Description |
|---|---|---:|---:|---|
| — | **TRIPLET_ATTESTED** | 0 | 0.0% | Edge present in all three graphs — fully proven. NOT a defect. |
| P2 | **REGISTRY_DRIFT** | 0 | 0.0% | Used in code AND observed at runtime, but not declared in any registry. Undocumented coupling / accidental API. |
| P3 | **DEAD_PATH** | 239 | 0.04% | Wired in code AND declared in registry, but never traced at runtime. Untested code path or vestigial policy. |
| P3 | **UNOBSERVED_CODE** | 565,366 | 99.95% | Static-only — orphan import, dead code, or never-traced path. |
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
| `<id=28>` | `<id=187064>` | `references_mcp_server` |
| `<id=31>` | `<id=187063>` | `references_mcp_server` |
| `<id=31>` | `<id=187064>` | `references_mcp_server` |
| `<id=31>` | `<id=187067>` | `references_mcp_server` |
| `<id=31>` | `<id=187068>` | `references_mcp_server` |
| `<id=36>` | `<id=187063>` | `references_mcp_server` |
| `<id=36>` | `<id=187065>` | `references_mcp_server` |
| `<id=36>` | `<id=187069>` | `references_mcp_server` |
| `<id=36>` | `<id=187070>` | `references_mcp_server` |
| `<id=37>` | `<id=187064>` | `references_mcp_server` |

### UNOBSERVED_CODE  (severity P3)

| src | dst | relation |
|---|---|---|
| `<id=8>` | `<id=14967>` | `implements` |
| `<id=8>` | `<id=18413>` | `reads_from` |
| `<id=8>` | `<id=20740>` | `reads_from` |
| `<id=8>` | `<id=28114>` | `exports` |
| `<id=8>` | `<id=28114>` | `reads_from` |
| `<id=8>` | `<id=28125>` | `exports` |
| `<id=8>` | `<id=28125>` | `reads_from` |
| `<id=8>` | `<id=28551>` | `covers` |
| `<id=8>` | `<id=28552>` | `imports` |
| `<id=8>` | `<id=55686>` | `unused_import` |

### CONFIG_BLOAT  (severity P4)

| src | dst | relation |
|---|---|---|
| `<id=187062>` | `<id=187063>` | `MCP_SERVER_DECLARED` |
| `<id=187062>` | `<id=187064>` | `MCP_SERVER_DECLARED` |
| `<id=187062>` | `<id=187065>` | `MCP_SERVER_DECLARED` |
| `<id=187062>` | `<id=187066>` | `MCP_SERVER_DECLARED` |
| `<id=187062>` | `<id=187067>` | `MCP_SERVER_DECLARED` |
| `<id=187062>` | `<id=187068>` | `MCP_SERVER_DECLARED` |
| `<id=187062>` | `<id=187069>` | `MCP_SERVER_DECLARED` |
| `<id=187062>` | `<id=187070>` | `MCP_SERVER_DECLARED` |
| `<id=187062>` | `<id=187071>` | `MCP_SERVER_DECLARED` |
| `<id=187072>` | `<id=187073>` | `AGENT_SPEC_DECLARED` |

