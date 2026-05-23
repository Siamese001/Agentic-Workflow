# ADR: apps_rg Spine-Only Runtime (No Second Pipeline)

**Status:** Proposed  
**Date:** 2026-05-23  
**Plan:** [apps-rg-spine-only-unification-d8f4a2.md](../.cursor/plans/apps-rg-spine-only-unification-d8f4a2.md)

## Context

`apps_rg` currently runs two product-visible architectures:

1. **Governed spine** — `c0_binding` / `pa_binding` / `l2_binding` / `ExitEvalPipeline` (integrated R4).
2. **Section lane pipeline** — proof pool, section graph binding, FEC bridges, lane PA/L2, lane X3.

The bridge-based [one-canonical-spine-e8b4a1](../.cursor/plans/one-canonical-spine-e8b4a1.md) added contracts around (2) without eliminating it.

## Decision

**One runtime only:** every `python -m apps_rg` invocation, with or without `--section`, executes:

```text
U0 → L1 → L0 → C0 → PA → L2 → Exit → (UWG → L4 if commit) → L6 after boundary
```

**Section vs full resume** differs only by:

- L1 plan shape (one work unit vs many + assembly),
- profile refs (C0/PA/Exit/judges),
- full-resume-only phases: assembly + aggregate X1D judges.

**Forbidden:** bridge modules, FEC-shaped snapshots as C0 substitutes, lane `x3_disposition.json` as disposition authority, parallel dispatch into `_*_lane_from_cli` monoliths.

## Consequences

- Delete bridge and mirror modules (see plan W3–W6).
- `canonical_dispatch` becomes a thin router to `apps_rg_spine_run`.
- Proof pool remains a **source** consumed inside `c0_binding`, not a bypass to PA.
- Full resume gains explicit assembly + coherence judges on spine Exit — not a bolt-on to the old lane path.

## Supersedes

- Bridge interpretation of `one-canonical-spine-e8b4a1` (plan marked SUPERSEDED).
- “Two paths found” as an acceptable steady state in `one_spine_inventory.py`.
