# apps_rg L7 artifact ownership boundary

Decision date: 2026-06-07

This record freezes the auditability ownership boundary for the L7 overlap cleanup plan. The intent is hardening, not redesign: `agentic_core` owns canonical L7 projection and spine proof artifacts; `apps_rg` owns product, section, and refs-only audit entrypoints.

| Artifact family | Canonical owner | Allowed producer | Forbidden producers |
|---|---|---|---|
| `agentic_core_how_trace.json` | `agentic_core` | `agentic_core` integrated spine / L7 projection | `apps_rg` section lanes |
| `agentic_core_l7_route_family_coverage.json` | `agentic_core` | `agentic_core` integrated spine / L7 projection | `apps_rg` section lanes |
| `agentic_core_spine_proof.json` | `agentic_core` | `agentic_core` integrated spine | `apps_rg` section lanes |
| `integrated_runtime_artifact_manifest.json` | `agentic_core` / integrated spine | Integrated runtime entrypoint | Standalone `apps_rg` section lanes |
| `runtime_trace_snapshot.json` | `agentic_core` when emitted by integrated spine | Integrated runtime entrypoint | Standalone `apps_rg` section lanes claiming L7 authority |
| `runtime_gate_verdict_bundle.json` | `agentic_core` gate-verdict surface | Core gate-verdict producer | `apps_rg` X2 gate output writers |
| `x2_gate_outputs.json` | `apps_rg` app-domain evidence | `apps_rg` section lane | Core 00C GateVerdict producer |
| `section_runtime_proof_bundle.json` | `apps_rg` section shim | `apps_rg` section lane | 99 RuntimeProofBundle producer |
| `evidence_package_index.json` | `apps_rg` section audit entrypoint | `apps_rg` section evidence packager | Core L7 proof producer |
| `RUN_BUNDLE_INDEX.json` | Catalog/index only | `apps_rg` run bundle indexer | Any proof authority |

Operational rules:

- Section L7 binding is refs-only. It may reference verified external core L7 artifacts, but it must not copy them into a section folder as trusted local proof.
- A local file whose name is in `L7_CORE_ARTIFACTS` is trusted only when its producer component starts with `agentic_core`.
- `x2_gate_outputs.json` is app-domain evidence, never a 00C GateVerdict.
- `section_runtime_proof_bundle.json` is a section shim, never `runtime_proof_bundle.json`.
- Durable vector/cache persistence claims require governed CommitRequest, UWG commit/block, L4/read-surface evidence, and must not be inferred from section package presence.
