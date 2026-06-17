# ADR-051: SC-1 Structural Block Remediation — Phased Closure Strategy

- **Status**: Accepted (with Amendment 2026-04-24)
- **Date**: 2026-04-24
- **Amended**: 2026-04-24 (scope revised — see Amendment section)
- **Deciders**: Agentic-Workflow core (harness + architecture)
- **Impact Layers**: L3, L_APP (narrowed — see Amendment)
- **Supersedes**: —
- **Superseded by**: —
- **Related**: ADR-049 (L5 v4 governance plane), `.claude/rules/adg-canonical-invariants.md`

## Amendment — 2026-04-24

**Scope revised from 54 to 3 violations.** After W7.1-P0 classification
(`tools/debug/_sc1_subtype_classifier.py` + `docs/reports/sc1_subtype_triage_20260424.md`),
the actual SC-1 P0 set in the current ADG snapshot is:

| # | Module | Layer | Subtype | Pattern |
|---|---|:---:|:---:|---|
| 1 | `agentic_core/L3_orchestration/exit_control/ledger_integrity.py:222` | L3 | 1 | `self._path.parent.mkdir(parents=True, exist_ok=True)` |
| 2 | `agentic_core/L3_orchestration/exit_control/runtime_hitl_ledger.py:122` | L3 | 1 | same |
| 3 | `apps_shared/integrations/runtime_hitl_integration.py:207` | L_APP | 1 | same |

All three are **identical pattern** — SQLite-ledger `__init__` calling
`self._path.parent.mkdir(...)` before `sqlite3.connect(...)`. The previous
"54 violations" figure was drawn from a stale probe. The actual gate state
(via P-view `v_p0_write_bypass_uwg`) has only 3 rows.

**Revised Impact Layers**: L3 + L_APP only (not the original broad L0–L5).

**Revised remediation** (supersedes the original 5-wave structure below):

| Wave | Action | Effort |
|---|---|---|
| W7.1-P0 (DONE) | Classifier + triage report | ~2h |
| W7.1-P1 | Replace mkdir with `agentic_core.L2_execution.utils.write_gateway.ensure_dir` across 3 files | ~1h |
| W7.1-P2 (OBSOLETE) | Boundary-bypass fixes | — |
| W7.1-P3 (OBSOLETE) | Exemption register | — |
| W7.1-P4 | Regenerate ADG, confirm `v_p0_write_bypass_uwg` returns 0 rows | ~30min |

**Total effort: ~3.5h** (vs. original 30–45h estimate).

The original 5-wave structure below is preserved for ADR audit integrity but
is OBSOLETE as of this amendment. See companion plan
`.claude/plans/sc1-structural-block-closure-f9e3b1.md` for the collapsed
execution path.

## Context

**SC-1** is the structural-conformance rule checked by the ADG validation gate
`v_structural_conformance` (materialized view in `artifacts/adg/adg_indexed_*.sqlite`).
It combines two violation classes:

1. **Layer gravity violations** — an import that runs "upward" against the
   ordered layer stack (`L0` < `L1` < `L2` < `L3` < `L4` < `L5` < `L6`). A
   higher layer importing a lower one is fine; the reverse violates gravity.
2. **Import cycles** — any SCC (strongly-connected component) involving two or
   more modules in the production graph.

Both are promoted to `Enforcement.BLOCK` (gate severity P0) since 2026-04-23 per
`ops_scripts/ci/adg_gates/unified_registry.py`. As of the latest ADG snapshot,
**54 SC-1 violations remain** — these predate the BLOCK promotion and are
grandfathered in the ratchet baseline, not re-detected as new defects.

The violations cluster around three architectural seams that warrant separate
subtype analysis:

| Subtype | Pattern | Expected count |
|---|---|---:|
| **Direct mutation bypass** | Higher layer reaches down to mutate an `L4` cache/state object directly instead of going through the UWG/exit-control seam. | ~15–20 |
| **Boundary bypass** | Cross-boundary imports that sidestep the canonical adapter / registry (e.g., `L2` reaching `L0` routing internals). | ~10–15 |
| **Ingress shortcut** | A runner/driver imports a cross-layer symbol that should flow through a governance plane checkpoint (policy / exit-control / attestation). | ~8–12 |
| **Exit-control skip** | A production path bypasses `L5` exit-control despite emitting a side-effect the safety plane is supposed to gate. | ~8–12 |

Exact counts per subtype will be produced by Wave W7.1 Phase P0 (classification
pass — see companion plan). The classification informs whether each violation
is a **true bypass** (must fix) or a **legitimate structural exemption**
(register with a guardian token + justification).

## Decision

Remediate SC-1 as a **dedicated multi-phase plan** with its own Author-Gate at
each phase boundary, NOT as a bulk batch fix. The plan follows the ADG
canonical-invariant doctrine (`.claude/rules/adg-canonical-invariants.md`)
for hotspot analysis and the §22 graph-layer evidence requirement for refactor
plans.

### Phase Structure

| Phase | Purpose | Output | Gate |
|---|---|---|---|
| **P0 — Classification** | Sub-classify all 54 violations into the 4 subtypes by querying `v_structural_conformance` + reading each source site. | `docs/reports/sc1_subtype_triage_<date>.md` with per-violation disposition. | No code changes — read-only. |
| **P1 — Safety-plane fixes** | Fix subtype 1 (direct mutation bypass) first because it intersects the L5 safety-plane Surface at ×2.0 impact. Route mutations through the canonical UWG/exit-control seam. | Source edits + new/updated tests exercising the exit-control path. | Author-Gate before each module's change; regen ADG after each batch. |
| **P2 — Boundary + ingress fixes** | Fix subtypes 2 and 3. Re-route cross-layer imports through adapters or registry lookups. | Source edits + interface-contract tests. | Author-Gate per module; ADG regen. |
| **P3 — Exemption registration** | For any violation determined to be a legitimate structural exemption (e.g., test-harness seam, bootstrap loader, explicitly-documented inversion), register it with a guardian token `# guardian: allow-structural-exemption -- <specific justification tying to ADR>`. | Updated source + an entry in `config/sc1_structural_exemptions.yaml` with reason + expiry date. | Author-Gate required per constitutional §8 + §24. |
| **P4 — Validation + close** | Regenerate ADG. Confirm SC-1 count drops to zero OR matches the registered-exemption set. Update the W7.1 Wave/Phase Convergence row to Done. Archive the classification report. | Validation artifact + Notion writeback. | Automatic if P1–P3 passed. |

### Rejected Alternatives

| Alternative | Why rejected |
|---|---|
| Emergency batch-fix codemod | SC-1 violations often have historical context (intentional inversions for bootstrapping, test harnesses, compatibility shims). A codemod cannot distinguish true bypass from legitimate exemption — risk of breaking load paths is unacceptable in L5. |
| Defer until upstream L5 doctrine ADR | L5 v4 governance plane (ADR-049) already provides the policy framework. No further upstream dependency is blocking SC-1 remediation. |
| Case-by-case without a plan | Violates constitutional §19 (mode separation) — execution must be planned, not ad-hoc. |

## Consequences

### Positive

- Closes the largest remaining P1 item in the deferred-scope backlog
  (impact score ~829, L5 × Security × coverage=100%).
- Establishes a reusable pattern for future structural-conformance remediation
  (SC-5 spine completeness, SC-7 grounding contract — both already promoted
  to BLOCK with 0 current violations but may accrue over time).
- Documents legitimate structural exemptions explicitly, converting tacit
  knowledge into versioned artifacts (`config/sc1_structural_exemptions.yaml`).

### Negative / Risks

- Total wall-clock time is substantial (~30–45h across phases). P1 + P2 each
  require per-module Author-Gate cycles, which slow execution intentionally
  to maintain safety-plane integrity.
- Phase P1 touches L5 safety-plane code paths. A regression here has higher
  blast-radius than a typical L2/L3 refactor. Mitigation: every P1 change is
  gated by ADG regen + targeted test run before the next module begins.
- The `config/sc1_structural_exemptions.yaml` creates a new SSOT that must be
  kept in sync with the ADG baseline. The P4 validation phase explicitly
  includes a reconciliation step.

### Neutral

- No change to existing runtime behavior in the normal case — the plan fixes
  structural violations but leaves valid runtime semantics intact.

## Implementation Notes

### Graph-Layer Evidence (constitutional §22)

The remediation plan (`.claude/plans/sc1-structural-block-closure-f9e3b1.md`)
includes the mandatory `## ADG_GRAPH_LAYER_EVIDENCE` section citing:

- `v_structural_conformance` (the source MV — SSOT for violation set)
- `mv_graph_critical_path_blast_radius` (to rank violation remediation by
  downstream impact)
- `mv_hotspot_centrality` (to identify which of the 54 modules are
  CENTRAL_DEPENDENCY or ORCHESTRATOR hotspots)
- Semantic edges: `imports`, `writes_to`, `emits_side_effect`, `controls_flow`,
  `resolves_callsite` (each used in the subtype classifier).

### Hotspot Report (constitutional §22)

P0 output includes the ranked hotspot report with archetype + surface + layer
multipliers per the canonical invariants.

### Decision Points Requiring Author-Gate

Per `.claude/rules/author-gate-enforcement.md`, every one of the following
triggers an Author-Gate (scored options, 0.72 threshold, dominance rule):

- Any **deletion of an `*Agent.py`** encountered during remediation (constitutional §3)
- Any **guardian exemption addition** beyond the P3 budget
- Any **new anti-pattern instance** introduced while fixing an SC-1 site
- Any **cross-layer refactor exceeding 5 files** (T3 boundary)

## References

- `ops_scripts/ci/adg_gates/unified_registry.py` — `v_structural_conformance` gate spec
- `.claude/rules/adg-canonical-invariants.md` — layer multipliers, surfaces, archetypes
- `.claude/rules/adg-graph-layer-enforcement.md` — §22 plan section requirements
- ADR-049 — L5 v4 governance plane (the canonical safety-plane ADR)
- Companion plan: `.claude/plans/sc1-structural-block-closure-f9e3b1.md`
