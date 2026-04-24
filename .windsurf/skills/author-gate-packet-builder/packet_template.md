# Author-Gate Decision Packet Template — Didactic Option Shape

This template is loaded by Cascade when `emit_packet.py` is constructing an
`ask_user_question` packet for a **developer-loop / harness** decision point.

Terminology note (do NOT conflate):
- **Author-Gate Decision** = this template. Developer-loop / harness-side
  (Fowler: "human in the loop" at the code-gen level). Fires when Cascade
  is about to write code and a trigger in `author_gate_triggers.yaml` matches.
- **Runtime Author-Gate** = v30 step [5] ESCALATE branch. Production agent escalates
  a live request to a human approver. Covered by `ADR-023` and the sibling
  plan `runtime-hitl-exit-control-c4e7b3.md`. **NOT** what this template serves.

Every field here has a role in producing a surfaced decision that both
**forces a real choice** and **teaches the user why**.

## Header Packet (above the options)

The header MUST start with the marker line so `post_cascade_author_gate_capture.py`
can detect the packet type unambiguously:

```
AUTHOR-GATE DECISION — <decision_type_human_readable>
⭐ Recommended: <winning option id>
Why it wins: <one case-specific sentence — never generic>
Principle at stake: <layer gravity | fail-closed | zero-loss refactor | SSOT | reversibility | ...>
What the ADG shows: <fan_in=N, fan_out=M, layer=L?, blast_radius_files=K>
Historical precedent: <strong|suggestive|none> — <matched_decision_id or "no precedent">
What you're optimizing for: <goal verb>
What you're trading off: <precise cost, not generic>
What would flip this decision: <concrete condition>
Counts: N candidates | M surfaced | X low-confidence | Y non-distinct
```

## Gold-Star Marking (recommended option)

The recommended option (highest `confidence_score` among surfaced candidates)
MUST be visually distinguished:

- `ask_user_question` option **label**: prefix with `⭐ Recommended — ` then the title.
  - Example: `⭐ Recommended — Minimal scope (extract SovereignBaseAgent only)`
- `ask_user_question` option **description**: first line is `[RECOMMENDED ⭐ confidence=0.88]`
  followed by the AG-10 fields on subsequent lines.
- Non-recommended surfaced options: plain label, description starts with
  `[confidence=0.NN]` (no star).
- Suppressed options (below threshold / dominance-fired / non-distinct) are NOT
  surfaced to `ask_user_question` but ARE retained in the emitted packet for audit.

Rationale: the star is a fast-parse visual affordance — users can pick the
recommended path at a glance without re-reading the header. It also makes
"did I override the recommendation?" a measurable event (`override_vs_recommendation`).

## Per-Option Shape (AG-10 fields)

Every option MUST supply these 10 fields. `emit_packet.py` validates presence
before writing the packet; missing fields → schema error.

| # | Field | Contract |
|---|-------|----------|
| 1 | `thesis` | Short actionable description. Leads with a verb. |
| 2 | `value_to_goal` | How this advances the user's stated goal. |
| 3 | `key_tradeoffs` | Array of "Gains X but increases Y because Z" sentences — at least 2. |
| 4 | `execution_impact` | Scope (files, test surface, hook/config churn). |
| 5 | `risk_profile` | Reversibility, blast radius, guardrail exposure. |
| 6 | `time_to_value` | When the option delivers observable value. |
| 7 | `confidence_score` | 0.00–1.00. ≥0.72 to surface; ≥0.85 with 0.12 gap = dominance. |
| 8 | `principle_at_stake` | The architectural principle this honors or violates. Pick one: `layer gravity`, `fail-closed`, `zero-loss refactor`, `SSOT`, `reversibility`, `ADR precedent`, `compliance`, `simplicity over cleverness`. |
| 9 | `what_youd_miss_if_skipped` | What insight/safety would be lost by skipping Author-Gate here. Specific, not abstract. |
| 10 | `what_would_change_the_recommendation` | One concrete condition under which a different option wins. |

### Didactic field authoring rules

**`principle_at_stake`** — the enforceable word, not a paragraph. If nothing fits the canonical list above, state "none — pure tactical choice" (then consider: is this really Author-Gate?).

**`what_youd_miss_if_skipped`** — answers "if the agent just did this without asking, what would the user lose?" Examples:
- ✅ "You'd miss that `SovereignBaseAgent` has 47 callers — reversibility is not 1 commit."
- ❌ "Better context." (generic — rejected)

**`what_would_change_the_recommendation`** — forcing the model to articulate the flip condition sharpens scoring. Examples:
- ✅ "If blast_radius crosses L5 safety plane, fail-closed dominates and `comprehensive` wins."
- ✅ "If precedent ledger has ≥3 `strong` matches for `comprehensive`, promotion-to-pattern applies and Author-Gate can be skipped."
- ❌ "If the user prefers differently." (non-falsifiable — rejected)

## Example — Fully-Populated Option

```json
{
  "id": "minimal",
  "surfaced": true,
  "confidence_score": 0.88,
  "suppression_reason": null,
  "thesis": "Extract SovereignBaseAgent into L2_execution/base.py; defer 4 sibling classes to a follow-up wave.",
  "value_to_goal": "Unblocks the pending L2 refactor without fan-out through 47 caller sites.",
  "key_tradeoffs": [
    "Gains reversibility (single commit revert works) but increases L4 sibling drift because those classes remain in the old location.",
    "Gains rapid feedback (1 wave, 2 days) but increases total plan duration because follow-up waves are needed.",
    "Gains precedent alignment (2026-04-10 decision succeeded with this pattern) but increases Author-Gate ceremony because each sibling gets its own packet."
  ],
  "execution_impact": "3 files touched, 2 test files affected, no hook/config change.",
  "risk_profile": "Low — layer gravity preserved, guardrails not invoked, ADG fan_out=3.",
  "time_to_value": "~2 days; observable after first commit lands.",
  "principle_at_stake": "reversibility",
  "what_youd_miss_if_skipped": "You'd miss that SovereignBaseAgent is imported by 47 callers; a bad extract = 47-file fan-out.",
  "what_would_change_the_recommendation": "If blast_radius fan_in crosses L5 safety, fail-closed dominates and `comprehensive` wins."
}
```

## Suppression

Options below `surface_threshold` (0.72) are still EMITTED in the packet but
with `surfaced: false` and a `suppression_reason` — this preserves audit
transparency. Cascade MUST NOT drop low-confidence options silently.

```json
{
  "id": "big_bang",
  "surfaced": false,
  "confidence_score": 0.41,
  "suppression_reason": "below_surface_threshold",
  "thesis": "Extract all 5 siblings in one commit.",
  "confidence_score_rationale": "Ratio of blast_radius to test_coverage is 14:1 — regression risk too high."
}
```

## Routing Rules (applied by emit_packet.py)

| Condition | Behavior |
|-----------|----------|
| All candidates < 0.72 | Emit `LOW_CONFIDENCE_AMBIGUITY` marker; route to clarify/replan/abstain. Do not surface options. |
| Top ≥ 0.85 AND gap to next ≥ 0.12 | Dominance fires — surface only the top option; others carried as `surfaced: false, suppression_reason: dominance_fired`. |
| Otherwise | Surface up to 4 options above threshold, sorted by confidence DESC. |
| Two options differ only cosmetically | Collapse into one; the other gets `suppression_reason: non_distinct`. |
