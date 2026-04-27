# ADG _compat Shim Retirement — Wave A

- **Plan ID**: `adg-compat-shim-retire-a1c0de`
- **Tier**: T3 (120 files, single directory, archival move)
- **ADG Snapshot**: latest `artifacts/adg/adg_indexed_*.sqlite`
- **Status**: In Progress (Wave A of dead-code / duplication shrinkage)

## Goal

Archive 120 backward-compat shim files under `agentic_core/adg/_compat/` to `archives/adg_compat/2026-04-23/`. Shims are pure re-export stubs (~330 bytes each) that dynamically import from canonical `agentic_core/adg/adapters/`, `agentic_core/adg/extraction/`, etc. Verified zero live importers (only reference is a governance test asserting non-existence).

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|------------:|-------------|--------|------------------|
| A | A.1, A.2, A.3 | Archive `agentic_core/adg/_compat/` → `archives/adg_compat/2026-04-23/` | 3,000 | Zero live importers (verified via grep); governance test asserts non-existence | 🟢 in_progress | 120 files moved; `tests/governance/test_parallel_theater_removal.py` still green; ADG regen shows node/edge drop |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|------------:|--------|
| A.1 | Verify zero importers | `agentic_core/adg/_compat/**` (120 .py) | None — already verified | 500 | done |
| A.2 | Archive move | 120 files from `agentic_core/adg/_compat/` to `archives/adg_compat/2026-04-23/` (git mv to preserve history) | Windows path length | 1,500 | pending |
| A.3 | Verify + regenerate ADG | `python tools/generate_full_adg.py`; confirm node count drop; governance test still green | ADG regen may take 5-10min | 1,000 | pending |

## Gap Register

| ID | Gap | Mitigation |
|----|-----|------------|
| G1 | Dynamic `importlib.import_module("agentic_core.adg._compat.X")` not grep-visible | Archive path (`archives/`) is import-forbidden per constitutional §12 → any residual usage breaks loudly at first invocation |
| G2 | Namespace-package behavior (no `__init__.py`) may hide transient imports | Covered by G1: archival location is non-importable |

## ADG_HOTSPOT_REPORT

All 120 files have ADG fan-in = 0 at the symbol level (verified by the scan the parent analysis produced). Archetype: **none** (pure shim, no owning behavior). Layer: `L_TOOLS` (×1.0). Impact: 0 × 1.0 = 0 — pure dead weight.

## ADG_GRAPH_LAYER_EVIDENCE

- **mv_hotspot_centrality**: no row for any `_compat/*` symbol (centrality = 0).
- **v_p3_isolated_experimental**: `agentic_core/adg/_compat/sandbox_airlock.py` listed — matches deferred Wave D scope.
- **Semantic edges**: zero `flows_to` / `resolves_callsite` edges originating from shims; only the synthetic `imports` self-reference inside each shim.
- **mv_graph_reverse_dependency_hotspots**: no `_compat/*` target appears above noise floor.

Provenance: `backend=sqlite, snapshot=adg_indexed_<latest>.sqlite`.

## Rollback

`git revert <commit>` restores the entire directory tree in place. No behavior depends on the removal (zero importers).
