---
plan_type: refactor
---

# W6.1-Tooling Guardian Codemod — Dedicated Plan

- **Plan ID**: `w6-1-tooling-guardian-codemod-d4e8a7`
- **Parent**: `w7-p1-adr-tooling-followup-b5c9e2` (deferred W6.1)
- **Status**: Todo (production already closed per `docs/reports/w6_1_bare_guardian_inventory_20260424_v2.md`)
- **Priority**: P4 (tooling-only, no production risk)
- **Target**: Queue for unattended codemod run; do NOT block production work

## Context

The original "W6.1 BARE-guardian pass — 1696 sites L5/L0/L3" deferred-scope
figure was stale. Fresh AST scan (2026-04-24) shows:

- **All production layers (L0–L6, L_APP, L_INFRA, L_SL, other) = 100% covered.**
- **863 uncovered sites remain, all in tooling**: L_TOOLS (787) + L_OPS (76).

These are offline scripts (migration codemods, CI gate runners, debug
scanners) where broad exception handling is often legitimate. They carry
**zero production runtime risk**.

Full inventory: `@c:/Git/Agentic-Workflow/docs/reports/w6_1_bare_guardian_inventory_20260424_v2.md`

## Intent

Apply a single codemod pass to stamp guardian justifications on the 863
uncovered tooling `except Exception` / `except BaseException` handlers.
Default justification: `# guardian: allow-broad-exception -- offline tooling, reports failure`
(tune per-script as codemod runs). Any handler where the broad catch is
genuinely unsafe gets migrated to a specific exception type instead.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|---|---|---|---:|---|---|
| **W1** | P0 | Plan + Notion (this file) | 500 | In Progress | Committed + row |
| **W2** | P1 | Author codemod `tools/migration/guardian_stamp_tooling.py` | 4,000 | Todo | AST-based; dry-run + apply modes; per-file diff output |
| **W3** | P2 | Dry-run on L_OPS (76 sites) + manual review | 3,000 | Blocked on W2 | Dry-run output committed to `docs/reports/w6_1_codemod_dryrun_L_OPS.md`; hand-review for misclassification |
| **W4** | P3 | Apply L_OPS patches + regen ADG + validate | 2,500 | Blocked on W3 | L_OPS uncovered count = 0; py_compile clean |
| **W5** | P4 | Dry-run on L_TOOLS (787 sites) + manual review | 8,000 | Blocked on W4 | Dry-run output; spot-check 20 random sites |
| **W6** | P5 | Apply L_TOOLS patches + regen ADG + validate | 5,000 | Blocked on W5 | L_TOOLS uncovered count = 0; py_compile clean on all 787 files |
| **W7** | P6 | Notion sync + plan closure | 1,000 | Blocked on W6 | Phase rows Done; plan archived |

**Total token budget**: ~24,000 — GREEN (single dedicated session if codemod is solid; worst case 2 sessions).

## Phase-Level Summary

| Phase ID | Title | Scope | Pain Points | Est. Tokens | Status |
|---|---|---|---|---:|---|
| P0 | Plan + Notion | This file + Notion row | None | 500 | In Progress |
| P1 | Codemod authoring | `tools/migration/guardian_stamp_tooling.py` (new) | AST parent-chain detection for bare/broad except; line-accurate comment insertion preserving formatting | 4,000 | Todo |
| P2 | L_OPS dry-run | 76 sites in `ops_scripts/` | CI-gate scripts may need specific justification (not default) | 3,000 | Todo |
| P3 | L_OPS apply | Same 76 sites | py_compile must stay clean | 2,500 | Todo |
| P4 | L_TOOLS dry-run | 787 sites in `tools/` | Archive directories excluded; debug scripts may be throwaway | 8,000 | Todo |
| P5 | L_TOOLS apply | Same 787 sites | Large diff; needs progress bar per §16 | 5,000 | Todo |
| P6 | Notion sync + close | Plan archive | None | 1,000 | Todo |

## ADG_HOTSPOT_REPORT

Not applicable — no production hotspots remain. This plan is pure tooling
hygiene. Per `docs/reports/w6_1_bare_guardian_inventory_20260424_v2.md`,
all production layers are at 100% coverage.

## ADG_GRAPH_LAYER_EVIDENCE

Tooling-layer work does NOT trigger the constitutional §22 graph-layer
evidence requirement (that applies to T2/T3 refactoring plans affecting
production). This plan is P4 tooling hygiene.

## Rejected Alternative: Execute Now

Attempting to run W6.1 in the current session would consume 24k tokens on
low-value tooling cleanup. Given:

- Production is already closed (0 uncovered sites)
- SC-1 is closed (0 P0 rows)
- Active production work is higher-leverage

The right play is to **queue this plan for a dedicated tooling-hygiene
session** rather than interleaving it with production work.

## Success Criteria (overall)

1. Codemod tool `tools/migration/guardian_stamp_tooling.py` exists and is tested.
2. L_OPS + L_TOOLS uncovered count = 0 after apply.
3. `python tools/debug/_bare_guardian_coverage.py` shows 0 uncovered across all layers.
4. No py_compile regressions.
5. Notion row closes.

## Non-Goals

- Not touching production code (already done).
- Not migrating broad-except to specific types unless the site is demonstrably unsafe.
- Not running the codemod on `archives/`, `__pycache__/`, or `tests/` (excluded).
