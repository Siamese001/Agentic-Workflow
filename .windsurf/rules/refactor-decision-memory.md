---
trigger: model_decision
description: Before opening a Author-Gate packet for any refactor-class decision, consult the refactor-decision-memory skill to surface historical precedent and bias or enrich the Author-Gate packet accordingly.
---

> **Cascade always-on discipline:** Keep this file lean and invariant-focused. Put durable boundaries, routing cues, and non-negotiable standards here. Move long procedures, examples, templates, and execution playbooks into skills or workflows.
>
> **Cascade retrieval discipline:** When this rule affects research or synthesis, prefer local-first retrieval, exact or structural matches before broad semantic search, and evidence or quote extraction before final synthesis on high-risk tasks.
>
> **Cascade enforcement split:** Advisory guidance lives here, but deterministic blocking, fail-closed checks, and audit capture belong in hooks and scripts rather than prompt prose.

# Refactor Decision Memory — Pre-Author-Gate Precedent Check

## Scope

This rule fires **before** Author-Gate for these decision classes (defined in `author-gate-enforcement.md` §HITL-1):

- Architecture choice (§1.1)
- Refactoring scope (§1.2)
- Anti-pattern resolution (§1.3)
- Test modification strategy (§1.4)
- Dependency addition (§1.5)
- File/module deletion (§1.6)
- Error handling strategy (§1.8)

This rule does **not** replace `author-gate-enforcement.md`. That file remains the policy SSOT for:
when Author-Gate fires, scoring, filtering, dominance, and explicit selection requirements.
This rule adds a precedent-lookup layer **under** that policy.

## Pre-Author-Gate Protocol

**Before assembling any Author-Gate packet for a refactor-class decision:**

1. Invoke the `refactor-decision-memory` skill
2. Run the lookup:
   ```bash
   echo '{"decision_type":"<type>","normalized_intent":"<1–2 sentences>","repo_area":"<path>","limit":5}' \
     | python .windsurf/skills/refactor-decision-memory/lookup_refactor_decisions.py
   ```
3. Route on `verdict`:

| Verdict | Action |
|---------|--------|
| `strong` | Reuse or heavily bias toward the matched precedent. State `"Historical precedent recommends: …"` in the Author-Gate question packet. If `promote_to_pattern=true` and no regression, the dominance rule from `author-gate-enforcement.md` may fire — surface a single option. |
| `suggestive` | Include a precedent summary in the Author-Gate framing: `"Prior decision (YYYY-MM-DD): …"` in the question packet header before the standard options. |
| `none` | Proceed with standard Author-Gate per `author-gate-enforcement.md`. No precedent bias. |

## Capture

After a refactor decision is resolved, the `post_cascade_response` hook captures the decision
**if and only if** Cascade emitted a `DECISION_CAPTURED:` marker in the response, as required
by `author-gate-enforcement.md` step 9. Without that emission the hook finds nothing to capture.

Capture is **advisory** — missed captures are acceptable. The ledger grows over time.

## Promotion

To promote a resolved decision to `promote_to_pattern=1` (elevates it to `strong` precedent):

```sql
UPDATE decision_outcomes
SET promote_to_pattern = 1
WHERE decision_id = '<id>'
  AND tests_passed = 1
  AND regression_found = 0
  AND rollback_required = 0;
```

Criteria: repeated successful pattern, no rollback, no newer contradictory precedent,
same constraint class, validated by tests.

## Policy SSOT Reference

All scoring, filtering, dominance, and option-shape rules live in:

- `author-gate-enforcement.md` — core pipeline (always_on)
- `author-gate-decision-points.md` — full doctrine (model_decision, §HITL-1 through §HITL-11)

This rule governs **only** the precedent lookup layer — not the decision policy itself.
