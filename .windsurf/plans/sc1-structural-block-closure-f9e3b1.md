---
plan_type: refactor
---

# SC-1 Structural Block Closure — Phased Remediation Plan

- **Plan ID**: `sc1-structural-block-closure-f9e3b1`
- **Parent**: Wave W7.1 (deferred-scope backlog)
- **ADR**: `docs/architecture/adr/ADR-051-sc1-structural-block-remediation.md`
- **Status**: AMENDED 2026-04-24 — P0 Done, P1 In Progress; P2/P3 obsolete per scope revision
- **Owner**: Agentic-Workflow core
- **Start date**: 2026-04-24
- **Target completion**: 2026-05-22 (4 weeks, elapsed)

## Intent

Close the SC-1 structural-conformance violations tracked by the ADG P-view
`v_p0_write_bypass_uwg` (gate severity P0 BLOCK since 2026-04-23).

**Amendment 2026-04-24**: W7.1-P0 classifier run (commit `c096c68439`)
revealed only **3 actual violations**, not 54 as originally estimated. All 3
are the identical pattern — SQLite-ledger `__init__` calling
`self._path.parent.mkdir(...)`. Execution collapses from 5 waves to 2:

| Wave | Status |
|---|---|
| W7.1-P0 | ✅ DONE — classifier + triage report authored |
| W7.1-P1 | In Progress — replace mkdir with `ensure_dir` across 3 files |
| W7.1-P2 | OBSOLETE — no boundary bypass sites remain |
| W7.1-P3 | OBSOLETE — no exemptions needed (3 sites all have clean fix) |
| W7.1-P4 | Todo — regenerate ADG, confirm 0 rows |

The original 5-wave structure below is preserved for audit integrity but is
OBSOLETE. See `docs/architecture/adr/ADR-051-sc1-structural-block-remediation.md`
Amendment section. See `.windsurf/plans/w7-p1-adr-tooling-followup-b5c9e2.md`
for the active P1 execution.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---:|---|---|---|
| **W1** | P0 | Sub-classify 54 violations by subtype | 3,000 | ADG snapshot is current; `v_structural_conformance` query reachable | Todo | Report in `docs/reports/sc1_subtype_triage_<date>.md` with per-violation disposition (true-bypass vs legitimate-exemption) and subtype tallies |
| **W2** | P1 | Fix subtype 1 (direct mutation bypass, ~15–20 sites) | 8,000 | UWG/exit-control seam is stable; tests exist for gated paths | Blocked on W1 | L5 mutations route through canonical seam; target tests pass; ADG SC-1 count drops by ~15–20 |
| **W3** | P2 | Fix subtypes 2+3 (boundary bypass + ingress shortcut, ~18–27 sites) | 9,000 | Adapter/registry interfaces stable | Blocked on W2 | Cross-layer imports route through adapters/registry; ADG SC-1 count drops by ~18–27 additional |
| **W4** | P3 | Register legitimate exemptions (~0–12 sites) | 3,500 | Exemptions genuinely architectural (not rationalizations) | Blocked on W3 | `config/sc1_structural_exemptions.yaml` populated; each entry has guardian token + expiry + ADR-051 reference |
| **W5** | P4 | Validation + close | 1,500 | ADG regen succeeds | Blocked on W4 | ADG SC-1 count = 0 OR matches exemption set; Wave/Phase row marked Done |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---:|---|
| P0 | Sub-classify violations by subtype | Read-only — queries `v_structural_conformance` + reads violation source sites | `v_structural_conformance` schema may vary between ADG snapshots; classifier heuristics need calibration against a few exemplars | 3,000 | Todo |
| P1 | Fix direct mutation bypass (~15–20 modules) | L4 state modules + L2/L3/L5 callers that currently bypass the UWG | Every fix must preserve runtime semantics; exit-control may refuse writes that previously succeeded; tests need new mocks | 8,000 | Blocked on P0 |
| P2 | Fix boundary bypass + ingress shortcuts (~18–27 modules) | Cross-layer import sites in `apps_*`, `agentic_core/L0..L3` | Some "bypasses" may be legacy adapters that got inlined; need to decide adapter vs delete vs keep inline with exemption | 9,000 | Blocked on P1 |
| P3 | Register legitimate exemptions (~0–12 modules) | New file `config/sc1_structural_exemptions.yaml`; guardian tokens added to source | Risk of rationalizing true bypasses as "legitimate"; each exemption MUST pass Author-Gate with specific justification per constitutional §8 | 3,500 | Blocked on P2 |
| P4 | Validation + close | ADG regen + Wave/Phase row update + Notion writeback | ADG regen failures unrelated to SC-1 may block closure; need to isolate this plan's contribution | 1,500 | Blocked on P3 |

## ADG_HOTSPOT_REPORT

Hotspot ranking will be produced in P0 by joining `v_structural_conformance`
against `mv_hotspot_centrality` + `mv_graph_critical_path_blast_radius`. The
report structure:

| Rank | Module | Layer | Fan-in | Impact | Archetype | Surface | Subtype |
|---:|---|---|---:|---:|---|---|---|

Columns:
- **Layer**: L0..L6 (drives the multiplier — L5/L0 ×2.0, L3/L4 ×1.75).
- **Archetype**: one of `CENTRAL_DEPENDENCY`, `ORCHESTRATOR`, `STATE_NODE`,
  `SAFETY_GATEKEEPER` per canonical invariants §5.
- **Surface**: one of Execution / Write / Security / State / Observability /
  none per canonical invariants §3. Subtype-1 violations typically cross the
  Write Surface + State Surface; subtype-2 crosses Execution; subtype-4
  crosses Security.
- **Subtype**: 1=direct-mutation, 2=boundary-bypass, 3=ingress-shortcut,
  4=exit-control-skip.

The P0 report will populate this table with all 54 rows ranked by impact score.

## ADG_GRAPH_LAYER_EVIDENCE

### Materialized views cited (≥3 required per constitutional §22)

1. **`v_structural_conformance`** — the canonical SC-1 SSOT. Primary source
   for the 54 violations and their subtype signatures (gravity direction +
   cycle membership).
2. **`mv_graph_critical_path_blast_radius`** — ranks each violation module by
   downstream blast radius. A violation in a module with 50+ transitive
   consumers is higher P1 than one with 2 consumers.
3. **`mv_hotspot_centrality`** — identifies which modules are
   CENTRAL_DEPENDENCY (high fan-in) vs ORCHESTRATOR (high fan-out). Subtype-1
   fixes in a CENTRAL_DEPENDENCY are higher risk and require stricter
   test coverage.
4. **`mv_dependency_cone_risk`** — surfaces whether a violation sits inside a
   larger risk cone already flagged for other reasons (antipatterns, exemption
   density). Fixing a violation inside an active risk cone often delivers
   cascade benefits.

### Semantic edges used

- `imports` — the primary edge kind SC-1 inspects.
- `writes_to` — flags subtype-1 (direct mutation) when an import is followed
  by a mutation on the imported module's state.
- `emits_side_effect` — flags subtype-4 (exit-control skip) when a production
  path emits a side-effect bypassing L5.
- `controls_flow` — flags subtype-3 (ingress shortcut) when a runner
  imports a control-flow target that should flow through a governance plane
  checkpoint.
- `resolves_callsite` — used in P2 to verify adapter/registry dispatch works
  after the fix.

### P-view cross-references

- `v_p0_apps_direct_infra` — apps importing `infrastructure/*` directly;
  intersects with subtype-2 (boundary bypass).
- `v_p0_write_bypass_uwg` — write edges that skip the UWG; intersects with
  subtype-1 (direct mutation bypass).
- `v_p1_mis_layered_infra` — misplaced infra code; informs whether a
  violation should be fixed by relocating the target module rather than
  rewiring the caller.

## Gap Register

| Gap | Impact | Mitigation |
|---|---|---|
| SC-1 subtype heuristics are not yet calibrated against real violations | P0 report quality depends on good subtype assignment | P0 spot-checks 3–5 exemplars per subtype with a human reviewer before scaling |
| Some "legitimate exemptions" may be rationalized true bypasses | Constitutional §8 violation risk | Every P3 exemption requires scored Author-Gate with specific justification; generic reasons forbidden |
| L5 safety-plane test coverage may be insufficient for P1 | Regression risk in safety-plane | Each P1 module change adds or updates at least one test exercising the gated path |
| ADG regen between phases may surface unrelated new SC-1 violations | P4 validation ambiguity | Record the starting count and only attribute this plan's credit for the delta |

## Author-Gate Checkpoints

Per constitutional §8 + `.windsurf/rules/author-gate-enforcement.md`, an
Author-Gate (scored options, 0.72 surface threshold, dominance rule) fires at:

1. **Phase boundaries** — before P1, P2, P3, P4 kickoff (4 gates total).
2. **Within P3** — before adding any entry to `sc1_structural_exemptions.yaml`.
   The `-- <justification>` must be specific and tied to ADR-051.
3. **Within P1/P2** — before any cross-layer refactor touching ≥6 files (T3
   boundary).
4. **On any `*Agent.py` deletion** encountered during remediation (constitutional §3).

## Success Criteria (plan-level)

1. `v_structural_conformance` query against the post-P4 ADG snapshot returns
   either (a) zero rows, or (b) only rows matching entries in
   `config/sc1_structural_exemptions.yaml` with active (non-expired) status.
2. `config/sc1_structural_exemptions.yaml` exists with every entry having: a
   module path, subtype, justification (≥10 words, ADR-051 reference),
   expiry date (≤180 days from creation), owner.
3. The W7.1 Wave/Phase Convergence row is marked **Done** with Actual Tokens
   populated and Blocking Items empty.
4. No new SC-1 violations detected in any ADG regen during the plan's
   execution (ratchet maintained).
5. All Author-Gate decisions taken during execution are captured in the
   Author-Gate Decision Ledger (auto-post via hook).

## Token Budget

Sum: **25,000 tokens** (~3,000 P0 + 8,000 P1 + 9,000 P2 + 3,500 P3 + 1,500 P4).
Status: 🟢 GREEN (comfortable within T3 ceiling of 30,000).

## Non-Goals

- Not addressing SC-5 (spine completeness) or SC-7 (grounding contract) —
  those have 0 current violations and are tracked separately.
- Not introducing a new structural-conformance rule class.
- Not changing the `v_structural_conformance` gate's enforcement level — it
  remains BLOCK throughout.
- Not deleting any `*Agent.py` files without independent Author-Gate
  authorization (per constitutional §3).

## Next Action

**Kickoff P0 classification** in a fresh terminal session:

```
python tools/debug/_sc1_subtype_classifier.py > docs/reports/sc1_subtype_triage_<date>.md
```

(Tool to be authored in P0. Uses `v_structural_conformance` as primary source,
joined with the `mv_*` views listed above.)
