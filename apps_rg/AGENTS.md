# apps_rg - App Agent Contract

> `apps_rg` owns the resume-generation app surface. The active app contract lives here; the architecture and runtime details are split across `AGENTIC_SPINE.md` and `LEAN_CORE.md`.

## Scope

`apps_rg` owns app-specific prompt assembly, runtime sections, contracts, profiles, tests, and evidence artifacts under `apps_rg/`.

`agentic_core` provides generic enforcement. App-specific behavior must not be added to `agentic_core` without a migration receipt.

## Core invariants

- Graph IDs are the only claim authority.
- Runtime selection narrows evidence, but cannot add evidence.
- Whole-run caches stay separate from per-section C0 semantic payloads.
- Shared lanes such as `executive_summary`, `headline`, and `competencies` may only claim from their section-specific evidence plan.
- Locked deterministic copy stays fixed unless explicitly authorized.

## Working rules

- Build and verify section seams before broad integration.
- Keep whole-run `R1A`/`R1B` state separate from per-section payloads.
- Show exact section output, prompt/profile, provider or model status, artifact path, judge result, X2 gate result, and X3 disposition when making implementation claims.

## References

- `AGENTIC_SPINE.md`
- `LEAN_CORE.md`
- Root [`AGENTS.md`](../AGENTS.md)
