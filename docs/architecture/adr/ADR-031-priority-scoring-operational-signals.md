# ADR-031: Priority Scoring v2 — Operational Signals

- **Status**: Accepted
- **Decision Date**: 2026-04-23
- **Deciders**: Cascade (on USER directive "execute and implement and test")
- **Supersedes**: v1 behavior of `tools/priority/deferred_scope_scorer.py` (structurally compatible — v1 inputs preserved)
- **Related**:
  - `.windsurf/rules/deferred-scope-capture.md`
  - `.windsurf/rules/adg-canonical-invariants.md` §6 (layer multipliers)
  - ADR-023 runtime-HITL-exit-control (for the runtime vs author-gate terminology)
  - Anthropic "Building Effective Agents", "Demystifying evals for AI agents"
  - OpenAI "Evaluation best practices"
  - EDDOps (arxiv 2411.13768) — evaluation-driven development of LLM agents

## Context

The v1 deferred-scope priority scorer scored items strictly from **static ADG features**:

```
impact_v1 = coverage_gap_pct × layer_multiplier × (1 + log10(1 + fan_in)) × surface_boost
```

This is architecturally correct but operationally blind. Two empirical problems surfaced on 2026-04-23:

1. **Fan-in=0 collapse**: 4 out of 4 open deferred items (SC-1 audit→enforce, OTel runtime-ADG ingest, ADG coverage hardening, `repo_adg_graph` retirement) scored P3 — identical band despite wildly different operational severity. Log-of-zero fan-in collapses structural weight.
2. **No operational-severity signal**: a regression that fires on every request is indistinguishable from an unfinished capability that fires never.

Industry research (both labs) converged on a richer model. Anthropic's *"Demystifying evals for AI agents"* emphasizes **trajectory quality** + **regression-vs-capability** separation. OpenAI's *"Evaluation best practices"* names **production traffic fidelity** as the prioritization anchor. Anthropic's *"Building Effective Agents"* counter-principle: **add complexity only when it demonstrably improves outcomes** — backlog items that add agentic surface area should be penalized, not promoted.

## Decision

Extend `tools/priority/deferred_scope_scorer.py` with **five optional operational signals**, each defaulting to a **neutral multiplier of 1.0** so pre-ADR-031 callers are byte-identical:

```
impact_v2 =
    coverage_gap_pct
  × layer_multiplier                              # v1 — ADG §23 structural criticality
  × (1 + log10(1 + fan_in))                       # v1 — ADG blast radius
  × surface_boost                                  # v1 — ADG 5-surface
  × (1 + log10(1 + prod_invocations))              # NEW — production frequency (OTel)
  × (1 + trajectory_defect_rate)                   # NEW — OTel-observed failure rate [0,1]
  × reversibility_boost                            # NEW — write=1.5, action=1.3, read=1.0
  × item_class_multiplier                          # NEW — regression=1.5, capability=1.0
  × complexity_penalty                             # NEW — 0.8 if adds agentic surface
```

Band thresholds (P1..P5) are **unchanged**.

### The 5 new signals — rationale + source

| Signal | Range | Source | Justification |
|---|---|---|---|
| `prod_invocations` | int ≥ 0, log-scaled | `otel_mcp.spans_by_agent` (30-day rolling) | OpenAI: "production traffic fidelity" is the primary prioritization anchor |
| `trajectory_defect_rate` | float in [0,1] | `otel_mcp.anomalies` + healing-chain failure rate | Anthropic: trajectory evaluation beats outcome-only |
| `reversibility` | `"write"/"action"/"read"` | inferred from `semantic_edge=writes_to` / `emits_side_effect` | ADG canonical invariants §3 — Write surface > State > Execution > Read |
| `item_class` | `"regression"/"capability"` | `SC/AP Violation Backlog` membership | Anthropic: regression vs capability deserve separate priority curves |
| `adds_complexity` | bool | plan metadata | Anthropic "Building Effective Agents": new tool/orchestrator/exemption → 0.8× penalty |

### Back-compat invariant (pinned by tests)

For any v1 input tuple `(layer, fan_in, surface, coverage_gap_pct)`, calling `score_deferred_scope` with those four arguments and **no others** returns an impact score and band bit-identical to v1. Validated by `tests/unit/tools/priority/test_deferred_scope_scorer_v2.py::TestBackCompat` (5 parametrized cases + neutral-defaults check).

### Illustration — SC-1 audit→enforce promotion

With `layer=L_TOOLS, fan_in=3, surface=Security, coverage_gap_pct=60.0`:

| Signal mix | Impact | Band |
|---|---|---|
| **v1 (no operational signals)** | 144.19 | **P3** |
| Just 5 prod invocations + 2% defect rate | ~231 | **P2** ← promoted |
| Heavy: 5000 invocations + 5% defect + `action` path + `regression` class | ~1387 | **P1** ← severe |

The scorer rewards operationally severe items even when structural fan-in is low — exactly the gap that produced the original 4-item P3 collapse.

## Consequences

### Positive

- Priority bands reflect **both** architectural risk (ADG) and operational risk (OTel). Matches published lab practice.
- Zero breaking change: existing hooks, markers, and CLI callers that don't pass new args behave identically.
- New signals are CLI-addressable (`--prod-invocations`, `--trajectory-defect-rate`, `--reversibility`, `--item-class`, `--adds-complexity`) so manual reviewers can rescore a marker without code changes.
- `ScoreResult` gains five new fields for transparency in logs and audit trails.

### Negative / Trade-offs

- The scorer now has **9 inputs** vs 4. More to validate per call, more to document.
- Operational signals must be **sourced from OTel** to be accurate. ADR-031 wires **layer A** (marker grammar + hook passthrough) so any `DEFERRED_SCOPE:` marker can carry v2 fields and the hook forwards them to the scorer. ADR-031 **does not** wire **layer B** (automatic OTel → marker enrichment); that is a genuine follow-up because it requires a plan-slug → agent-class resolver and a query fabric against `otel_mcp`.
- Band thresholds remain calibrated for v1 magnitudes. Heavy operational signals can push items from P3 → P1 in a single hop (see SC-1 heavy case). Monitor for over-promotion on real data; re-calibrate thresholds in a future ADR if the P1 cohort balloons.
- Complexity penalty (`adds_complexity=True` → 0.8×) is advisory — `adds_complexity` is self-reported by the marker author. Enforcement gate could be added later (e.g. auto-set to True when the plan introduces a new MCP or tool registration).

### Deferred / Not in scope

- Automatic sourcing of `prod_invocations` from `otel_mcp.spans_by_agent`.
- Automatic sourcing of `trajectory_defect_rate` from `otel_mcp.anomalies`.
- Automatic inference of `reversibility` from ADG semantic edges.
- Reconciliation of the `[Pn]` prefix in Notion Phase Title when a row is rescored post-hoc.

### Completed in this ADR (layer A)

- Marker grammar (`.windsurf/rules/deferred-scope-capture.md`) documents the 5 optional v2 fields.
- Hook parser (`.windsurf/scripts/post_cascade_deferred_scope_capture.py`) parses optional keys and forwards them to `score_deferred_scope`.
- Test: `tests/unit/windsurf/scripts/test_deferred_scope_capture_v2_passthrough.py` proves passthrough + fail-open on unknown values.

Each of these is a single-file follow-up tracked as its own DEFERRED_SCOPE item in the next execution wave.

## Implementation references

| File | Change |
|---|---|
| `tools/priority/deferred_scope_scorer.py` | Added 5 optional kwargs + 5 ScoreResult fields + 5 CLI flags; formula extended; v1 parity preserved |
| `tests/unit/tools/priority/test_deferred_scope_scorer_v2.py` | New — 26 tests across 7 classes |
| `.windsurf/rules/deferred-scope-capture.md` | Marker grammar extended with 5 optional v2 fields table |
| `.windsurf/scripts/post_cascade_deferred_scope_capture.py` | Hook parses optional v2 keys and forwards to scorer |
| `tests/unit/windsurf/scripts/test_deferred_scope_capture_v2_passthrough.py` | New — 5 tests proving end-to-end passthrough |

## Verification

```
python -m pytest tests/unit/tools/priority/test_deferred_scope_scorer_v2.py -q -n 0
# → 26 passed, 1 warning in 0.14s
```

All back-compat, signal-behavior, worked-example, and dataclass-shape tests green. CLI smoke (v1 inputs only) produces identical pre-ADR-031 output plus neutral defaults in the v2 fields.
