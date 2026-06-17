# ADR-100: Spine Envelope Pattern for Apps Product Modes

**Status**: ACCEPTED
**Date**: 2026-05-07
**Phase**: P2, P3 (deferred-scope-spine-refinement-5e3d1b)
**Deciders**: Codex + user Author-Gate
**ADG Snapshot**: `artifacts/adg/adg_indexed_20260507.sqlite`

---

## Context (SCQA)

- **Situation**: `apps_qna` and `apps_research` both had cert modes
  (`--apps-e2e-live`) using `governed_run` with full spine emission,
  but their product modes ran outside the spine — no U0 intake, no
  L0 routing, no L2 receipt, no Exit eval, no L7 HowTrace.

- **Complication**: The spine diagram showed these apps as spine-connected,
  but the normal product path was only partially connected. This created
  a gap between architectural intent and runtime behavior.

- **Question**: How should apps product modes be wired into the spine
  without disrupting existing functionality?

- **Answer**: Wrap the existing product-mode entry point in `governed_run`
  using a shared `EmissionConfig` factory, with real execution replacing
  the cert-mode no-op.

---

## Decision

Adopt the "spine envelope" pattern for all apps product modes:

1. Extract a shared `_build_emission_config()` factory from the existing
   cert-mode config.
2. Add a `_run_product_<app>()` function that wraps the real execution
   path in `governed_run`.
3. Refactor `_run_live_cert()` to use the shared config.
4. Update `main()` to route product mode through the spine; cert mode
   and auxiliary subcommands remain unchanged.

Applied to:
- `apps_qna/__main__.py` (P2, commit `2c99705`)
- `apps_research/__main__.py` (P3, commit `984534a`)

---

## Consequences

### Positive
- All apps product modes produce full spine receipts (U0/L1/L0/L2/Exit/L6/L7).
- Spine diagram accurately reflects runtime behavior for all apps.
- Shared `EmissionConfig` eliminates duplication between cert and product modes.
- Pattern is reusable for future apps.

### Negative
- Product mode startup incurs ~100ms overhead for spine receipt initialization.
- `governed_run` context manager adds a layer of indirection.

### Neutral
- Cert mode behavior unchanged.
- Auxiliary subcommands (lint, route, init, etc.) remain outside the spine.

---

## Alternatives Considered

1. **Modify apps internals to call spine components directly**: Would require
   refactoring every app's internal pipeline. Rejected — too invasive.
2. **Keep cert mode only, document the gap**: Perpetuates the diagram/reality
   mismatch. Rejected.
3. **Create a separate spine entrypoint per app**: Would fragment the codebase.
   Rejected — the envelope pattern keeps changes minimal and localized.

---

## References

- Plan P2: `.claude/plans/p2-apps-qna-product-spine-b3e8d2.md`
- Plan P3: `.claude/plans/p3-apps-research-spine-envelope-c4e9f3.md`
- Commits: `2c99705`, `984534a`
- Parent: `deferred-scope-spine-refinement-5e3d1b`
