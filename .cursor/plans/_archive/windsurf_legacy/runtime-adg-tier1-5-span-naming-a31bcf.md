# Plan: Runtime ADG Tier 1.5 — Span Matching & Emit-Site Gap Surfacing

**Slug**: `runtime-adg-tier1-5-span-naming-a31bcf`
**Status**: Active
**Tier**: T1 (additive, non-invasive; span_contracts.py + test + audit)
**Created**: 2026-04-23
**Parent**: `runtime-adg-tier1-trace-binding-c9b84d`

## Empirical Finding (drives this plan)

Actual corpus audit across 89 bound snapshots (post-Tier-1):

| Span name | Count | `kind` | `layer` | Signature attrs |
|---|---|---|---|---|
| `heal_router.v1.route` | 54 | `router` | `L0` | `routing.target_model`, `routing.confidence_score`, `routing.gate_applied` |
| `consensus.v1.judge` | 34 | `cognitive` | `L1` | `consensus.verdict`, `consensus.juror_count`, `consensus.threshold` |
| `test.op` | 1 | `tool` | `L2_Execu` | — |

Only **one** Tier 1 category is actually emitted today (`L0.route.select`, via `heal_router.v1.route`). Four are missing at the emit-site level: `runtime.trace_root`, `L2.step.seal`, `L2.(model|tool).invoke`, `Exit.disposition`. Broadening matchers lifts coverage from 0% → 20% **honestly**. The remaining 80% is a real architectural gap to track, not a naming problem.

## Goal

Tier 1.5 coverage should:
1. **Report the honest 20%** (L0.route.select via `heal_router.v1.route`) — match it even without the canonical name.
2. **Distinguish two failure modes**:
   - `name_mismatch` — a Tier 1 category has no matching node BY NAME, but the signature (kind/layer/attrs) is present somewhere → fix the matcher.
   - `emit_site_gap` — no matching node anywhere across the corpus by any signal → fix the runtime (i.e., add the emit site).
3. **Do not require changes to emit sites in this wave**. Tier 1.5 is purely diagnostic & matcher work. Emit-site wiring is Tier 2.

## Matcher Expansion — Signal-Based, Not Just Name

Move from "does `node.name` contain substring X" to a multi-signal match:

```
signal score for category C on node N =
    w_name  * (any name pattern matches N.name)
  + w_kind  * (N.kind ∈ expected_kinds)
  + w_layer * (N.layer ∈ expected_layers)
  + w_attrs * (any required_attr_key in N.attributes_json)
```

Node matches category C if `score >= threshold` (default 2 of 4 weighted signals). Keeps current name-based matches backward-compatible while recognizing production-like signals.

Example for `L0.route.select`:
- `name` matches any of: `route.select`, `l0.route`, `route.contract`, `router.`, `heal_router`
- `kind` ∈ {`router`, `route`}
- `layer` ∈ {`L0`}
- `attrs` include any of: `selected_route`, `routing.target_model`, `route.reason_codes`, `routing.confidence_score`

Weights: `w_name=1.0, w_kind=1.0, w_layer=1.0, w_attrs=1.0`. Threshold=2. So `heal_router.v1.route` matches because (a) `heal_router` is in name + (b) kind=router + (c) layer=L0 + (d) has `routing.target_model`. 4/4 signals → strong match.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status |
|---|---|---|---|---|
| W1 | W1.P1, W1.P2, W1.P3 | Matcher rewrite + emit-site gap helper + audit update | 5000 | Active |

## Phase-Level Summary

| Phase ID | Title | Scope | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| W1.P1 | Signal-based matcher | Rewrite `_TIER1_CONTRACTS` in `span_contracts.py` to use multi-signal matching; keep `validate_tier1_coverage()` API stable | Backward-compat of `Tier1Coverage` dataclass; existing 8 tests must still pass | 2000 | Active |
| W1.P2 | Corpus-level gap analyzer | New `validate_tier1_corpus_coverage(snapshots)` returning per-category emit-site presence across the whole corpus, not just one snapshot | Distinguish `name_mismatch` from `emit_site_gap` cleanly | 1500 | Active |
| W1.P3 | Wire into audit | Update `_runtime_adg_coverage_audit.py` to call corpus analyzer and print honest gap breakdown | Keep the audit tool fast (< 1s on 89 snapshots) | 1500 | Active |

## Success Criteria

1. `heal_router.v1.route` nodes register as `L0.route.select` in Tier 1 coverage
2. Audit reports per-category presence across the full corpus, not just samples
3. Audit distinguishes `name_mismatch` vs `emit_site_gap` vs `satisfied`
4. Tier 1 corpus coverage: was 0%, rises to expected ~20% (1 of 5 categories truly emitted today)
5. All existing Tier 1 tests still pass
6. New tests cover signal-based scoring

## Out of Scope

- Adding new emit sites (Tier 2)
- Renaming existing span emitters (would break downstream MCP consumers; matchers are cheaper)
- Attribute-level Tier 2 contracts (full 17-attr surface per span)

## Files Touched

| File | Action |
|---|---|
| `system_learning/runtime_adg/span_contracts.py` | Rewrite contracts + add corpus helper |
| `tools/debug/_runtime_adg_coverage_audit.py` | Wire in corpus helper |
| `tests/unit/system_learning/runtime_adg/test_span_contracts.py` | Extend with signal-based tests |
