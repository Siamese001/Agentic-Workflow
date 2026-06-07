# Author-Gate Decision Packet Template — Didactic Option Shape

> ⚠️ **GENERATED FILE** — Do not hand-edit. Regenerate with
> `python tools/author_gate/render_template.py`. The reference below is
> derived from `.claude/schemas/author_gate_packet.schema.json` (canonical
> SSOT per plan `author-gate-ssot-consolidation-b7c3e1`).

This template is loaded by Claude Code when `emit_packet.py` is constructing an
`ask_user_question` packet for a **developer-loop / harness** decision point.

Terminology note (do NOT conflate):
- **Author-Gate Decision** = this template. Developer-loop / harness-side.
  Fires when Claude Code is about to write code and a trigger in
  `author_gate_triggers.yaml` matches.
- **Runtime Author-Gate** = v30 step [5] ESCALATE branch. Production agent
  escalates a live request to a human approver. Covered by `ADR-023`.

## Header Packet (above the options)

```
AUTHOR-GATE DECISION — <decision_type_human_readable>
⭐ Recommended: <winning option id>            (only when routing.rule_applied == "dominance_fires")
Why it wins: <one case-specific sentence>
Principle at stake: <layer gravity | fail-closed | zero-loss refactor | SSOT | reversibility | ...>
What the ADG shows: <fan_in=N, fan_out=M, layer=L?, blast_radius_files=K>
Historical precedent: <strong|suggestive|none> — <matched_decision_id or "no precedent">
What you're optimizing for: <goal verb>
What you're trading off: <precise cost, not generic>
What would flip this decision: <concrete condition>
Counts: N candidates | M surfaced | X low-confidence | Y non-distinct
```

## Gold-Star Marking

The ⭐ Recommended label fires **iff `routing.rule_applied == "dominance_fires"`**
(top confidence ≥ 0.85 AND gap to next ≥ 0.12). Every surfaced option carries
`[confidence=0.NN]` prefix; only the dominant winner adds `[RECOMMENDED ⭐]`.

## Per-Packet Schema (auto-generated)

### Top-level fields

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `branch` | `string | null` |  | — |
| `calibrator_version` | `string | null` |  | — |
| `candidates` | `array` | ✅ | — |
| `commit_sha` | `string | null` |  | pattern `^([a-f0-9]{7,40})?$` |
| `confidence_dominance_gap` | `number | null` |  | range [0, 1] |
| `confidence_top` | `number | null` |  | range [0, 1] |
| `context_fingerprint` | `context_fingerprint` |  | — |
| `created_at` | `string` | ✅ | — |
| `decision_id` | `string` | ✅ | pattern `^dec_[a-z0-9]{6,}$`; Stable id; emit_packet.py mints as dec_<hex>. |
| `decision_type` | `string` | ✅ | enum: 'architecture_choice', 'refactor_scope', 'anti_pattern', 'dependency_addition', 'test_strategy', 'deletion_strategy', 'error_handling', 'certification_claim', 'unknown' |
| `normalized_intent` | `string | null` |  | — |
| `override_vs_recommendation` | `boolean | integer | null` |  | — |
| `policy_snapshot` | `string | null` |  | pattern `^(author-gate@[0-9a-f]+|unknown)?$` |
| `precedent` | `precedent` |  | — |
| `principle_at_stake` | `string | null` |  | — |
| `reason_code_palette` | `array | null` |  | — |
| `recommended_option_id` | `string | null` |  | — |
| `request_summary` | `string | null` |  | — |
| `routing` | `routing` | ✅ | — |
| `selected_option_id` | `string | null` |  | — |
| `selection_latency_ms` | `integer | null` |  | range [0, ∞] |
| `selection_rationale` | `string | null` |  | — |
| `status` | `string` | ✅ | enum: 'surfaced', 'executed', 'rolled_back', 'failed' |
| `user_goal` | `string | null` |  | — |

### Candidate (one per option in `candidates[]`)

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `blast_radius` | `object | null` |  | — |
| `confidence_score` | `number` | ✅ | range [0, 1] |
| `execution_impact` | `string | null` |  | — |
| `id` | `string` | ✅ | — |
| `is_recommended` | `boolean | null` |  | — |
| `key_tradeoffs` | `array | null` |  | — |
| `principle_at_stake` | `string | null` |  | — |
| `raw_score` | `number | null` |  | — |
| `reason_codes` | `array | null` |  | — |
| `risk_profile` | `string | null` |  | — |
| `signal_weights` | `object | null` |  | — |
| `signals` | `object | null` |  | — |
| `suppression_reason` | `string | null` |  | enum: 'below_surface_threshold', 'non_distinct', 'dominance_fired', None |
| `surface_description_prefix` | `string | null` |  | — |
| `surface_label` | `string | null` |  | — |
| `surfaced` | `boolean | null` |  | — |
| `thesis` | `string | null` |  | — |
| `time_to_value` | `string | null` |  | — |
| `value_to_goal` | `string | null` |  | — |
| `what_would_flip` | `string | array | null` |  | — |
| `what_youd_miss` | `string | null` |  | — |

### Routing object (`routing`)

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `dominance_delta_observed` | `number | null` |  | — |
| `rule_applied` | `string` | ✅ | pattern `^(dominance_fires|low_confidence_ambiguity|surface_top_[0-9]+|empty|tie_break|manual_override|filter_passes)$`; Routing verdict. Star-count contract: dominance_fires => 1 star; otherwise 0 stars. |
| `surface_threshold` | `number | null` |  | — |
| `top_score` | `number | null` |  | — |

### Precedent object (`precedent`)

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `match_count` | `integer | null` |  | — |
| `matched_ids` | `array` |  | — |
| `summary` | `string | null` |  | — |
| `verdict` | `string` |  | enum: 'none', 'strong', 'suggestive' |

### Context Fingerprint (`context_fingerprint`)

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `adg_snapshot` | `string | null` |  | — |
| `blast_radius` | `object | null` |  | — |
| `branch` | `string | null` |  | — |
| `files_in_scope` | `array` |  | — |
| `fp` | `string | null` |  | pattern `^[0-9a-f]+$` |
| `git_sha` | `string | null` |  | — |

## Routing Rules

| Condition | `routing.rule_applied` | UI behavior |
|-----------|------------------------|-------------|
| All candidates < 0.72 | `low_confidence_ambiguity` | No options surfaced; route to clarify/replan |
| Top ≥ 0.85 AND gap ≥ 0.12 | `dominance_fires` | Surface only top; ⭐ on it |
| Otherwise | `surface_top_<N>` | Surface up to 4 above threshold; no star |

## Suppression Reasons

Suppressed options are still EMITTED in `candidates[]` with `surfaced: false`
for audit transparency; only filtered from the user-facing prompt.

## References

- Canonical schema: `.claude/schemas/author_gate_packet.schema.json`
- Skill: `.claude/skills/author-gate-packet-builder/SKILL.md`
- Renderer skill: `.claude/skills/author-gate-ui-renderer/SKILL.md`
- Constitutional §6, §30
- Plan: `.claude/plans/author-gate-ssot-consolidation-b7c3e1.md`
