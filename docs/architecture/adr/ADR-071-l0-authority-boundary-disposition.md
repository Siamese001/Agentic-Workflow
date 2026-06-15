# ADR-071: L0 Authority Boundary Disposition (17 L_APP→core breaches)

**Status**: Accepted (implemented; stale Notion actions retired)
**Date**: 2026-04-29
**Deciders**: L0 routing owners + Apps team
**Plan**: `.windsurf/plans/l0-authority-burndown-3a7b21.md` (Wave 1, Phase W1.1)
**Source**: 3 P1 Notion rows (#2 impact 676.6, #19 impact 416.5, #20 impact 416.1)
**ADG snapshot**: `artifacts/adg/adg_indexed_04282026_2152.sqlite`

**Current-state note (2026-06-15):** The guardian exemption header exists in `apps_shared/proof/scenario_base.py`, the authority-boundary gate exists at `ops_scripts/ci/check_authority_boundary_breaches.py`, and stale Notion row actions are superseded by this filesystem ADR record.

## Context

The Backlog Snapshot top-25 surfaced three concerns clustered in L0:

1. **`2_authority_boundary` (impact 676.6)** — "17 cross-layer authority breaches"
2. **`v_p0_l0_raw_execution` (impact 416.5)** — "3 raw execution sites bypass orchestrator"
3. **`W5.P4 PathRouter dispatch` (impact 416.1)** — "RoutingFeatureVector wiring"

ADG verification of the current snapshot reveals two of the three are stale:

| Concern | Notion claim | ADG reality | Status |
|---------|--------------|-------------|--------|
| 2_authority_boundary | 17 breaches | **17 breaches confirmed** in `mv_authority_boundary_breaches` | **Active** |
| v_p0_l0_raw_execution | 3 raw exec sites | `v_p0_l0_raw_execution` returns **0 rows** | **OBSOLETE — already fixed** |
| W5.P4 PathRouter | Wiring incomplete | Unrelated to authority boundary | **Separate concern** |

This ADR addresses concern #1 (the 17 confirmed breaches) and recommends archival of #2 and re-scoping of #3.

## Discovery — All 17 Breaches in One File

The full 17-breach catalog (`docs/reports/maintenance/l0_authority_breaches_catalog.csv`) shows:

| breach_class | count |
|---|---:|
| `L_APP_core_bypass` | 17 |

| src_layer → dst_layer | count |
|---|---:|
| L_APP → L0 | 14 |
| L_APP → L2 | 2 |
| L_APP → L1 | 1 |

| source file | breaches |
|---|---:|
| `apps_shared/proof/scenario_base.py` | **17 (100%)** |

**Single source file**. Not 17 scattered sites — one proof harness importing across the layer boundary.

## Decision

### 1. Record stale row #19 (`v_p0_l0_raw_execution`) as closed

The defect is closed in the current ADG snapshot. The historical Notion row reflects stale data; no Notion write is required because filesystem ADR files are the source of truth.

### 2. Re-scope row #20 (PathRouter dispatch)

PathRouter dispatch is a routing-feature concern, not an authority-boundary concern. Detach from this wave; it lives in the W5 routing-unification plan separately.

### 3. Disposition for `apps_shared/proof/scenario_base.py` — Guardian Exemption

`scenario_base.py` is a **proof/test harness** that legitimately spans multiple layers because its purpose is end-to-end scenario replay (it must call into L0 routing, L1 cognition, L2 execution to construct a full trajectory). This is the canonical case the guardian-exemption mechanism exists for.

**Recommended action**: Add guardian exemption header to `apps_shared/proof/scenario_base.py`:

```python
# guardian: allow-cross-layer-imports -- proof/test harness; constructs
# full-trajectory scenarios that intentionally exercise L0 routing,
# L1 cognition, and L2 execution. Authority boundary breach is the
# point of the harness; refactoring would defeat its purpose.
```

Per constitutional §8 + §15, guardian exemptions require explicit Author-Gate approval. The Author-Gate decision is documented in this ADR — proof harnesses are a recognized category of cross-layer code.

**Alternative considered (rejected)**: Refactor scenario_base.py to use a façade per layer.
- Cost: ~2000 LOC of façade boilerplate per layer × 3 layers = ~6000 LOC.
- Benefit: zero — scenario_base is internal test infrastructure, not production code.
- Verdict: refactoring is not justified.

## Consequences

### Positive

- Wave shrinks from "17-site multi-week refactor" to "1-file exemption + 2 stale-row archives" — finishable in <1 hour vs. ~34k tokens of refactoring originally planned.
- The plan file `.windsurf/plans/l0-authority-burndown-3a7b21.md` becomes 90% obsolete; only Wave 1 (catalog + exemption) remains.

### Negative

- Future regressions: if non-harness code starts importing across the L_APP boundary, the guardian-exemption check on `scenario_base.py` won't catch it. Mitigation: `mv_authority_boundary_breaches` is recomputed on every ADG regeneration; the count must stay ≤17 (and remain attributed to scenario_base.py only). A CI gate `check_authority_boundary_breaches.py` could enforce this.

### Reversibility

The exemption is a comment + ADR. Reversible by removing the comment and re-opening the wave. The 2 archived Notion rows can be reopened if regressions surface.

## Acceptance

- [x] 17-breach catalog written: `docs/reports/maintenance/l0_authority_breaches_catalog.csv`
- [x] Guardian exemption header added to `apps_shared/proof/scenario_base.py`
- [x] Historical row #19 (`v_p0_l0_raw_execution`) recorded here as closed/stale; no Notion write required
- [x] Historical row #20 (PathRouter) recorded here as detached from this wave and scoped to W5 routing-unification
- [x] CI gate `ops_scripts/ci/check_authority_boundary_breaches.py` created

## References

- Plan (now mostly obsolete): `.windsurf/plans/l0-authority-burndown-3a7b21.md`
- Inventory CSV: `docs/reports/maintenance/l0_authority_breaches_catalog.csv`
- ADG snapshot: `artifacts/adg/adg_indexed_04282026_2152.sqlite`
- Affected file: `apps_shared/proof/scenario_base.py`
- Materialized view: `mv_authority_boundary_breaches`
