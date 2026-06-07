---
trigger: model_decision
description: Apply when introducing any deferred scope item (descoping work from a wave/phase, capturing future-work items, or any "we'll handle X later" decision). Demoted from always_on 2026-05-01 per Anthropic two-tier compliance.
---

# Deferred Scope Capture — Invariant-Only Stub

> ⛔ **Every deferred scope item MUST be captured to Notion with a computed priority within the same response that introduces it.** Self-reported "added to backlog" prose without a `DEFERRED_SCOPE:` marker is a constitutional violation (§24).

## Invariant

`DEFERRED_SCOPE:` marker is mandatory. Priority P1..P5 is **computed deterministically** by `tools/priority/deferred_scope_scorer.py` — never hand-assigned.

## Marker grammar (minimum)

```
DEFERRED_SCOPE: plan=<plan-slug> wave=<wave_id> phase=<phase_id> layer=<L0..L6|L_*> fan_in=<N> surface=<Execution|Write|Security|State|Observability|None> coverage_gap_pct=<N.N> est_tokens=<N> reason=<short>
```

Optional v2 operational signals (ADR-031): `prod_invocations`, `trajectory_defect_rate`, `reversibility`, `item_class`, `adds_complexity`. Omitting = neutral 1.0 multiplier.

## Priority formula (SSOT)

`tools/priority/deferred_scope_scorer.py` — do not duplicate elsewhere.

```
impact = coverage_gap_pct × layer_multiplier × (1 + log10(1 + fan_in)) × surface_boost
```

Bands: P1 ≥ 300 · P2 ≥ 150 · P3 ≥ 75 · P4 ≥ 30 · P5 < 30.

## Five failure modes the rule prevents (2026-04-22 RCA)

1. Prose-only deferred mention → nothing written
2. Notion row without matching plan file (orphan)
3. Memory entity with wrong `entityType="general"` → auto-purged
4. Duplicate rows from subsequent sessions
5. Sentinel plan-file names instead of real plans

## Where the procedural detail lives

| Concern | Location |
|---|---|
| Full marker contract (all fields, examples, auto-fill table) | (this rule was SSOT — full text preserved in git history at HEAD~1) |
| Deterministic capture + auto-post | `.windsurf/scripts/post_cascade_deferred_scope_capture.py` |
| Priority scorer SSOT | `tools/priority/deferred_scope_scorer.py` |
| Pre-commit gate | `ops_scripts/ci/check_deferred_scope_markers.py` |
| Session-start recovery | `.windsurf/scripts/pre_user_prompt_deferred_scope_recovery.py` |
| Memory pattern (cross-session recall) | `ProceduralPattern:DeferredScopeCaptureProtocol` in memory MCP |
| Bypass | `DEFERRED_SCOPE_CAPTURE_BYPASS=1` |

## Forbidden patterns

- Prose-only deferred mention without marker
- Hand-assigned `[Pn]` priority
- Sentinel plan name (e.g. `(infrastructure — no dedicated plan file...)`)
- Memory entity without protected `entityType` (auto-purge trap)

## Constitutional cross-reference

§24 (Deferred-scope capture mandatory). Sibling rule `.windsurf/rules/next-step-capture.md` covers `NEXT_STEP:` markers (P2..P5; voluntary follow-ups).
