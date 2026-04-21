# ADR-024: Cross-Band Re-Severity for Write-Plane & Safety-Surface Antipatterns

**Status**: ACCEPTED (Part A executing; Part B deferred until post-W5 per Author-Gate decision 2026-04-21)
**Date**: 2026-04-21
**Phase**: P2 Burndown Wave — `p2-burndown-wave-9e4c17`
**Deciders**: SVP Engineering (Cascade) + User (Human Approver)
**Related Plan**: `.windsurf/plans/p2-burndown-wave-9e4c17.md`

---

## Context

The P2 burndown wave (session 2026-04-21) reduced P2 net from 60 → 12 (-80%) via targeted
narrow-catch + guardian-token fixes across 48 files (W1 + W3-batch-1..4). During that work,
the ADG surface analysis revealed that **severity bands are assigned by pattern kind, not by
the architectural surface the pattern intersects.** Two P3 flags on `agentic_core/L5_safety/`
can be more dangerous than 30 P2 flags on `apps_*/reasoning/`, because:

- A swallowed failure on an L5 guardrail = no safety.
- A swallowed failure on an L4 write-plane = silent state corruption.
- A swallowed failure on an L0 routing chokepoint = lost execution.

Per constitutional §23 / `adg-canonical-invariants.md` §3, the **5 ADG Surfaces**
(Execution / Write / Security / State / Observability) are risk boundaries. The current
severity assignment in `agentic_core.adg.severity_bands` does not weight by surface.

Per `adg-canonical-invariants.md` §6, **Layer Criticality Multipliers** are canonical
doctrine:

| Layer | Multiplier | Rationale |
|-------|-----------|-----------|
| L0 routing | ×2.0 | Poisoned routing = all downstream lies |
| L5 safety | ×2.0 | Swallowed controls = no safety |
| L3 orchestration | ×1.75 | Chain failure hiding |
| L4 state | ×1.75 | Silent inconsistency |
| L1/L2 | ×1.0 | Standard |
| L6 observability | ×0.75 | Less structural risk |

Severity bands today **ignore these multipliers**. That is drift from the doctrinal floor.

---

## Decision

**Adopt a two-part remediation** that preserves SSOT while bringing severity into alignment
with surface/layer criticality.

### Part A — Annotation pass (no band manifest changes yet)

1. **Identify** all antipattern occurrences on the 5 ADG Surfaces (Execution / Write /
   Security / State / Observability) AND on L0/L5 layers (×2.0 multiplier).
2. **Require** a guardian token + specific `-- <justification>` at every such site where
   the pattern is preserved by design (e.g. first-write fallback, optional telemetry).
3. **Refactor** every site where the pattern is NOT by design (drop `logger.error` before
   `raise` on non-audit paths; narrow broad catches; split partial-side-effect try bodies).

### Part B — Severity-band manifest update (ADR-gated promotion)

Promote the following pattern × surface/layer combinations to higher bands:

| From → To | Pattern | Scope (surface + layer filter) | Est. net count |
|-----------|---------|--------------------------------|---------------:|
| **P2 → P1** | `partial_side_effects` | Write surface, any prod layer | 2 |
| **P2 → P1** | `default_fallback_masking` | Write surface, L3/L4 prod | 7 |
| **P2 → P1** | `retry_without_backoff` | Execution surface, prod | 4 |
| **P3 → P2** | `global_state_mutation` | L0 or L5 critical-path (fan_in ≥100) | ~30 |
| **P3 → P2** | `broad_exception_catch` | L5 safety/validators | ~25 |
| **P3 → P1** | `silent_exception_swallow` + `log_and_swallow` | L0 or L5 | ~15 |

Total post-promotion shift: **~83 items moved up; no changes to L1/L2/L6 or to
non-critical-path occurrences**.

---

## Rationale

- **SVP priority: alignment with existing doctrine** — multipliers already exist in
  `adg-canonical-invariants.md` §6; this ADR applies them instead of inventing new rules.
- **Zero new antipattern introduction** — promotions are re-classification of *existing*
  items, not new code. Constitutional §8 (Author-Gate for new antipatterns) does not apply.
- **Part A is a strictly-additive annotation pass** — touches only `# guardian:` comments
  and (for non-by-design cases) the catch body. No behavior change.
- **Part B is a single-commit manifest change** — pairs the `severity_bands.py` update
  with the `gates.py` ratchet ceiling update so CI never sees a regression.
- **Does not block the primary burndown** — this ADR is for the ~83 promotion candidates,
  not the 12 remaining P2 tail; those can be burned down without re-severity.

---

## Non-Goals

- Does NOT introduce new pattern *kinds* to the detector (`agentic_core.adg.extraction.visitors.core`).
- Does NOT change the Column-5 precise-exception-handling policy (constitutional §15).
- Does NOT touch guardian-exemption semantics (constitutional §8 / `approval-exception-policy.md`).
- Does NOT split the SC-1 structural-conformance P0 wall (separate plan track — see plan §12).

---

## Implementation Plan

### Step 1 — Manifest update (single commit)

File: `agentic_core/adg/severity_bands.py`

Add a `SURFACE_OVERRIDE` table applied after the base band lookup:

```python
SURFACE_OVERRIDE: dict[tuple[str, str], str] = {
    # (pattern_kind, layer_or_surface_marker) → elevated_band
    ("partial_side_effects", "write"): "HIGH",       # P2 → P1
    ("default_fallback_masking", "write"): "HIGH",   # P2 → P1
    ("retry_without_backoff", "prod"): "HIGH",       # P2 → P1
    ("global_state_mutation", "L0_critical"): "MEDIUM",  # P3 → P2
    ("global_state_mutation", "L5_critical"): "MEDIUM",  # P3 → P2
    ("broad_exception_catch", "L5"): "MEDIUM",           # P3 → P2
    ("silent_exception_swallow", "L0"): "HIGH",          # P3 → P1
    ("silent_exception_swallow", "L5"): "HIGH",          # P3 → P1
    ("log_and_swallow", "L0"): "HIGH",                   # P3 → P1
    ("log_and_swallow", "L5"): "HIGH",                   # P3 → P1
}
```

A surface/layer is determined by:
- **Write surface**: file_path matches `agentic_core/L4_state/` or contains
  `write_gateway`, `memory_authority`, `checkpoint`, `commit_versioned`.
- **Prod**: file is not under `tests/`, `tools/`, `ops_scripts/`, `docs/`.
- **L0_critical / L5_critical**: node fan_in ≥100 on `imports` per `mv_hotspot_centrality`.
- **L0 / L5**: file_path matches `agentic_core/L0_routing/` or `agentic_core/L5_safety/`.

### Step 2 — Migration test

File: `tests/unit/agentic_core/adg/test_severity_bands_migration.py`

- Load fixture snapshots from `artifacts/adg/adg_indexed_04212026_0433.sqlite` (pre-ADR)
  and expected post-ADR state.
- Assert: for each `SURFACE_OVERRIDE` row, the count of that `(kind, surface)` pair
  moves from the source band to the target band within ±2 count tolerance.
- Assert: no band gains items not on the override table (no silent elevations).

### Step 3 — Ratchet ceiling update

File: `tools/generate/validation/gates.py`

Update the ratchet ceilings **in the same commit** as step 1:
- P1 ceiling: current + ~48 (2 + 7 + 4 + 15 + ~20 cushion)
- P2 ceiling: current - ~48 + ~55 = net +7 (30 + 25 promoted in, 48 promoted out)
- P3 ceiling: current - ~70 (global_state, broad_catch, swallow promotions)

### Step 4 — Full ADG regen + verify

```bash
python tools/generate_full_adg.py
```

Expected: new snapshot shows the count shifts above. P0 unchanged. `infra_wiring`
pre-existing block remains (tracked in `docs/reports/plans/infra_wiring_repair_plan.md`).

### Step 5 — Targeted burndown of promoted items

Per plan `p2-burndown-wave-9e4c17.md` waves W5 (P1-promoted) and W6 (P3 critical-path).
No ADR change needed for those waves; they are execution work.

---

## Rollback

Revert the single manifest commit. `SURFACE_OVERRIDE` table becomes empty; band
assignments return to pre-ADR state. Ratchet ceilings auto-relax (they are floors on
the ledger side but gates allow lowering when counts drop).

---

## Open Questions (require user decision before moving to ACCEPTED)

1. **Are the 5 proposed surface markers (write / prod / L0_critical / L5_critical /
   L0 / L5) correct?** Alternative: use ADG node labels directly from the graph layer
   rather than file-path heuristics. Heuristic is simpler; graph labels are more
   accurate but require extraction-visitor changes.

2. **Is +48 P1 ceiling acceptable?** If CI currently enforces a tight P1 ratchet, the
   promotion bump may block existing PRs until burndown W5 completes. Alternative:
   gate the promotion behind a feature flag that defaults OFF and flips ON after W5
   completes.

3. **Should the SC-1 54-item structural-conformance block be covered here?** This ADR
   currently excludes it. Plan §12 recommends a sibling ADR/plan for SC-1; user to
   confirm.

---

## Part A Execution Findings (2026-04-21)

Scoping query against snapshot `04212026_1441` after W1+W3 burndown showed the original
~83-site estimate was **pre-W3**. Actual Part A scope on L0/L4/L5 surfaces:

| Pattern kind (promotion-candidate) | Total sites | Guardian-covered | Needed annotation |
|---|---:|---:|---:|
| `broad_exception_catch` (P2 on L5) | 13 | 13 | 0 |
| `return_none_swallow` (P2 on L0/L4/L5) | 3 | 0 | **3** |
| `partial_side_effects` | 0 | — | 0 |
| `default_fallback_masking` | 0 | — | 0 |
| `retry_without_backoff` | 0 | — | 0 |
| `silent_exception_swallow` | 0 | — | 0 |
| `log_and_swallow` | 0 | — | 0 |
| **Total Part A target kinds** | **16** | **13** | **3** |

Part A completed with **3 guardian annotations** added:
- `agentic_core/L4_state/enforcement/activation_flags.py:96` (fail-closed flags reset)
- `agentic_core/L4_state/enforcement/activation_flags.py:108` (fail-closed proof clear)
- `agentic_core/L5_safety/exit_control/hitl_policy.py:222` (optional-field float parser)

Zero behavior change. Part B estimates in the Decision section above are now STALE and
must be recomputed against a post-W5 snapshot before Part B executes. Specifically, the
`~83 items moved up` total is incorrect post-W3; the true figure is lower and should be
re-queried via `tools/debug/_adg_part_a_final_scope.py`.

Scoping diagnostics: `tools/debug/_adg_part_a_final_scope.py` (retained for Part B re-scope).

---

## References

- Plan: `.windsurf/plans/p2-burndown-wave-9e4c17.md`
- Doctrine: `.windsurf/rules/adg-canonical-invariants.md` §3 (5 Surfaces), §6 (multipliers)
- Constitutional rule §22 (graph-layer primary), §23 (surface intersections)
- Detector: `agentic_core/adg/extraction/visitors/core.py` (unchanged by this ADR)
- Severity SSOT: `agentic_core.adg.severity_bands` (changed by step 1)
- Ratchet SSOT: `tools/generate/validation/gates.py` (changed by step 3)
