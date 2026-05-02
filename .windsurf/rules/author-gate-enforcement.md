---
trigger: model_decision
description: Apply when an Author-Gate decision point is reached during code authoring (refactoring scope, architecture choice, anti-pattern, deletion, dependency add, test strategy, error handling). Distinct from runtime HITL (ADR-023). Demoted from always_on 2026-05-01 per Anthropic two-tier compliance.
---

# Author-Gate Enforcement — Invariant-Only Stub

> **Terminology**: This rule governs **Author-Gate Decisions** (developer-loop / harness-side, per ADR-023). It is NOT runtime HITL (v30 step [5] ESCALATE in `agentic_core/L5_safety/`). Historical markers (`HITL_PACKET:`) retain their legacy names but refer to Author-Gate events.

## The Pipeline (constitutional invariant — short form)

When facing an author-gate decision point:

1. **STOP** before action
2. **Generate** all plausible candidates
3. **Score** 0.00–1.00 (`confidence_score`)
4. **Filter** below `surface_threshold` (0.72 prod / 0.60 bootstrap)
5. **Dominance**: top ≥0.85 AND gap ≥0.12 → surface alone
6. **Material distinctness**: collapse cosmetic variants
7. **Surface 1–N options** via `ask_user_question` — analysis INSIDE description, not chat prose
8. **Wait** for explicit user selection
9. **Execute** chosen option; emit `DECISION_CAPTURED:` marker (refactor-class only) as **first plain-text line** of the response

## Marker grammar (refactor-class only)

```
DECISION_CAPTURED: type=<type>, repo_area=<area>, selected=<chosen>, outcome=executed[, confidence=0.NN, gap=0.NN, override=true|false, latency_ms=N, principle=<short>, precedent=<strong|suggestive|none>, exit_criteria=<short>]
```

Required: `type`, `repo_area`, `selected`, `outcome`. Plain text only, own line, top of response.

## Continuous Execution Invariant

Execute continuously WITHOUT stopping UNLESS a genuine Author-Gate decision point is reached. FORBIDDEN: stopping after tool calls, asking permission for deterministic actions, presenting options when there's one correct path.

## Bypass conditions (no Author-Gate needed)

Typos/whitespace/formatting · single correct solution (syntax/import error) · explicit unambiguous user directive · emergency rollback · auto-fixable lint.

## Silent-marker invariant (added 2026-04-27)

Every refactor-class decision MUST emit a `DECISION_CAPTURED:` marker — even when no options surfaced via `ask_user_question`. The seven trigger types are the gatekeeper: `architecture_choice`, `refactor_scope`, `anti_pattern`, `deletion_strategy`, `dependency_addition`, `test_strategy`, `error_handling`.

## Where the procedural detail lives

| Concern | Location |
|---|---|
| Full AG-10 option shape, packet construction, gold-star format, precedent injection | `.windsurf/skills/author-gate-packet-builder/SKILL.md` |
| Decision-point trigger doctrine (AG-1.1 through AG-1.11) | `.windsurf/rules/author-gate-decision-points.md` |
| SVP calibration thresholds (band-by-band) | `.windsurf/rules/author-gate-svp-calibration.md` |
| Refactor decision precedent | `.windsurf/skills/refactor-decision-memory/SKILL.md` |
| Capture hook (live) | `.windsurf/scripts/post_cascade_author_gate_capture.py` |
| Miss detector | `.windsurf/scripts/post_cascade_author_gate_miss_detector.py` |
| Hook-independent fallback | `tools/capture/append_marker.py` + `tools/capture/queue_to_ledger.py` |
| Pre-session staleness check | `tools/capture/ledger_staleness_check.py` |
| CI gate | `ops_scripts/ci/check_capture_queue_freshness.py` |
| Decision ledger SSOT | `.windsurf/state/refactor_decisions/refactor_decision_ledger.sqlite` |
| Inline-capture queue | `artifacts/capture/markers.jsonl` |
| Bypass | `AUTHOR_GATE_STALE_BYPASS=1` (queue) |

## Calibration-driven triggers

Empirical Wilson CI evidence in `docs/reports/calibration/<YYYY-Www>.md` MAY require an Author-Gate when: a band has `n ≥ 20` AND CI miss > 0.05 from nominal range, OR ≥2 bands in same ledger are mis-calibrated. Action: `decision_type=architecture_choice`. Smaller deltas auto-tune silently.

## Constitutional cross-reference

§6 (Author-Gate for ambiguous decisions). §30 (Author-Gate capture health mandatory). Sibling `.windsurf/rules/anti-pattern-author-gate.md` for the anti-pattern subcase. ADR-023 separates this from runtime HITL.
