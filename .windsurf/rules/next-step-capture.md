---
trigger: model_decision
description: Apply when Cascade suggests a follow-up action — "could do later", "consider X", optional polish. Demoted from always_on 2026-05-01 per Anthropic two-tier compliance.
---

# Next-Step Capture — Invariant-Only Stub

> ⛔ **When Cascade suggests a next step, it MUST emit a `NEXT_STEP:` marker in the same response.** Prose-only "could do later" language is a constitutional violation (§24-bis): suggestions historically vanish between sessions.

## Invariant

`NEXT_STEP:` marker is mandatory for any voluntary follow-up suggestion. Sibling to constitutional §24 (DEFERRED_SCOPE) — that rule handles scoped wave deferrals; this rule handles author-suggested polish.

## Marker grammar (minimum)

```
NEXT_STEP: plan=<slug-or-NEW:slug> title=<short> priority=<P2..P5> est_tokens=<N> reason=<why>
```

`priority=P1` is FORBIDDEN here (P1 is reserved for scored DEFERRED_SCOPE items).

## Where the procedural detail lives

| Concern | Location |
|---|---|
| Full marker contract (all fields, defaults, examples) | (this rule was the SSOT — full text preserved in git history at HEAD~1) |
| Auto-capture flow | `.windsurf/scripts/post_cascade_next_step_capture.py` |
| Plan auto-scaffold | `.windsurf/scripts/_deferred_scope_plan_scaffold.py` |
| CI gate | `ops_scripts/ci/check_notion_plan_file_drift.py` |
| Bypass | `NEXT_STEP_CAPTURE_BYPASS=1` |

## Forbidden Patterns

- Prose follow-up mentions without a `NEXT_STEP:` marker
- `priority=P1` (use `DEFERRED_SCOPE:` instead)
- `priority` outside `{P2, P3, P4, P5}`
- Sentinel plan names like `(no plan)` — use `NEW:<slug>`
