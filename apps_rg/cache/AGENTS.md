# apps_rg/cache Governance Notes

## r1a_adapter.py — Tolerated Cross-Boundary Import

`apps_rg/cache/r1a_adapter.py` is imported by `agentic_core/L0_routing/apps_rg_l0_binding.py` for cache-key computation over a deterministic input surface.

Classification: TOLERATED_READ_ONLY_HELPER

Receipt:
- Plan: apps-rg-quarantine-gap-remediation-8f405c
- Wave: W3
- Finding: BR-1
- Source audit: artifacts/apps_rg/apps_rg_quarantine_u0_packet_coverage_audit.md

Allowed behavior:
- compute deterministic cache keys
- use pure standard-library hashing
- return inert strings or simple value objects
- be imported by L0 routing only for read-only cache-key derivation

Forbidden behavior:
- provider calls
- LLM/model calls
- prompt assembly
- tool execution
- contract emission
- durable writes
- UWG bypass
- L4 mutation
- imports from quarantined apps_rg modules
- dynamic imports
- network access
- filesystem mutation

Invariant:
If `r1a_adapter.py` grows beyond deterministic cache-key derivation, it must be migrated into `agentic_core` or replaced by an agentic_core-owned adapter. It must not become an apps_rg runtime authority surface.

---

## apps_rg/cert Tombstone Decision

`apps_rg/cert/` remains intentionally present as a tombstone package.

Decision: LEAVE_AS_TOMBSTONE

Reason:
- Existing files already raise RuntimeError.
- No runtime path should import or depend on this package.
- Deleting the package is cosmetic and creates git churn without reducing runtime risk.

Invariant:
`apps_rg/cert/` must remain inert. Any attempt to restore certification, FEC production, evidence contracts, or runtime authority under `apps_rg/cert/` is prohibited. Those responsibilities belong in the governed agentic_core spine.
