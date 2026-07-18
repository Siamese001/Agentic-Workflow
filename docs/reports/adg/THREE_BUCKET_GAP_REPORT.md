# ADG Three-Bucket Gap Report

> ⚠ **DIAGNOSTIC ONLY — RUNTIME-THIN (runtime_proof_status=view_present_zero_attested)**. This report was produced without runtime attestation; do NOT treat as certification-clean. Re-run with `--require-runtime-proof` in CI once OTel attestation is wired.

- **Generated**: 2026-07-14T04:44:07.432251+00:00
- **Snapshot**: `adg_indexed_07142026_0023.sqlite`
- **Runtime view present**: True
- **Runtime-attested edges**: 0
- **Runtime proof status**: `view_present_zero_attested`
- **Total edges classified**: 517,213
- **Health score** (triplet-attested fraction): **0.0%**

> **Caveat**: `v_runtime_proof` exists but contains zero attested edges. The runtime bucket is empty — populate the OTel `runtime_adg_store` (e.g., run pytest with OTel exporters) and regenerate the snapshot to surface `TRIPLET_ATTESTED`, `SHADOW_CHANNEL`, and `DYNAMIC_DISPATCH` rows.


## Defect distribution

| Severity | Class | Edges | % | Description |
|---|---|---:|---:|---|
| — | **TRIPLET_ATTESTED** | 0 | 0.0% | Edge present in all three graphs — fully proven. NOT a defect. |
| P2 | **REGISTRY_DRIFT** | 0 | 0.0% | Used in code AND observed at runtime, but not declared in any registry. Undocumented coupling / accidental API. |
| P3 | **DEAD_PATH** | 267 | 0.05% | Wired in code AND declared in registry, but never traced at runtime. Untested code path or vestigial policy. |
| P3 | **UNOBSERVED_CODE** | 516,924 | 99.94% | Static-only — orphan import, dead code, or never-traced path. |
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
| `<id=19>` | `<id=191429>` | `references_mcp_server` |
| `<id=19>` | `<id=191430>` | `references_mcp_server` |
| `<id=19>` | `<id=191431>` | `references_mcp_server` |
| `<id=19>` | `<id=191432>` | `references_mcp_server` |
| `<id=19>` | `<id=191433>` | `references_mcp_server` |
| `<id=19>` | `<id=191434>` | `references_mcp_server` |
| `<id=19>` | `<id=191435>` | `references_mcp_server` |
| `<id=19>` | `<id=191436>` | `references_mcp_server` |
| `<id=19>` | `<id=191437>` | `references_mcp_server` |
| `<id=29>` | `<id=191429>` | `references_mcp_server` |

### UNOBSERVED_CODE  (severity P3)

| src | dst | relation |
|---|---|---|
| `<id=8>` | `<id=15305>` | `implements` |
| `<id=8>` | `<id=18788>` | `reads_from` |
| `<id=8>` | `<id=21160>` | `reads_from` |
| `<id=8>` | `<id=28557>` | `exports` |
| `<id=8>` | `<id=28557>` | `reads_from` |
| `<id=8>` | `<id=28568>` | `exports` |
| `<id=8>` | `<id=28568>` | `reads_from` |
| `<id=8>` | `<id=29001>` | `covers` |
| `<id=8>` | `<id=29002>` | `imports` |
| `<id=8>` | `<id=56327>` | `unused_import` |

### CONFIG_BLOAT  (severity P4)

| src | dst | relation |
|---|---|---|
| `<id=191428>` | `<id=191429>` | `MCP_SERVER_DECLARED` |
| `<id=191428>` | `<id=191430>` | `MCP_SERVER_DECLARED` |
| `<id=191428>` | `<id=191431>` | `MCP_SERVER_DECLARED` |
| `<id=191428>` | `<id=191432>` | `MCP_SERVER_DECLARED` |
| `<id=191428>` | `<id=191433>` | `MCP_SERVER_DECLARED` |
| `<id=191428>` | `<id=191434>` | `MCP_SERVER_DECLARED` |
| `<id=191428>` | `<id=191435>` | `MCP_SERVER_DECLARED` |
| `<id=191428>` | `<id=191436>` | `MCP_SERVER_DECLARED` |
| `<id=191428>` | `<id=191437>` | `MCP_SERVER_DECLARED` |
| `<id=191438>` | `<id=191439>` | `AGENT_SPEC_DECLARED` |

