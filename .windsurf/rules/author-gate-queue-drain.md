---
trigger: always_on
---

# Author-Gate Queue Drain (§35)

> ⛔ After ANY wave/phase completion marker, Cursor Agent MUST emit the next pending `AUTHOR_GATE_PACKET:` from `.windsurf/state/author_gate_queue/<plan-slug>.jsonl` in the same or immediately-following response. Queue drains to empty or explicit user stop.

## Invariant

Trigger tokens: `WAVE_COMPLETE:`, `PHASE_COMPLETE:`, `wave_execution_state.py complete`, or a Wave Structure row flipping to `✅ DONE`.

When triggered AND `_author_gate_queue.list_plans_with_pending()` is non-empty → response MUST contain `AUTHOR_GATE_PACKET:` (or legacy `HITL_PACKET:`) for the head-of-queue packet from the just-completed plan.

## SSOT

- **State**: `.windsurf/state/author_gate_queue/<slug>.jsonl` (append-only, survives restart).
- **Helper**: `.windsurf/scripts/_author_gate_queue.py` — `enqueue`, `next_packet`, `mark_answered`, `pending_count`, `list_plans_with_pending`.
- **Row**: `{id, title, depends_on, status, recommended_option, score, gap, enqueued_at, answered_at, chosen}`.

## Plan-Time Seeding

Plans foreseeing AG decisions MUST emit marker lines — prose alone is forbidden:

```
AG_QUEUE_SEED: plan=<slug> id=<packet_id> depends_on=<id1,id2> title=<short>
```

Capture hook `post_cascade_ag_queue_seed_capture.py` writes markers to queue JSONL. Pre-commit gate `check_ag_queue_seed_markers.py` blocks plan commits where prose count > marker count (quoted examples excluded).

## Drain Order

`next_packet(slug)` returns eligible head: `status=pending` AND all `depends_on` answered (or absent). Ties: score desc, then enqueue order.

## Stop Conditions

Queue empty · user says stop/pause/wait · `AG_QUEUE_DRAIN_BYPASS=1`.

## Forbidden

- ❌ Wave/phase complete without emitting next packet.
- ❌ Manually clearing queue state to bypass drain.
- ❌ Plan prose naming future AG decisions without matching marker.
- ❌ Answering a packet without `DECISION_CAPTURED:` (§30) + `mark_answered`.

## Enforcement

This rule + `_author_gate_queue.py` (SSOT helper) + `pre_user_prompt_ag_queue_surface.py` (emits `AG_QUEUE_PENDING:`) + `post_cascade_ag_queue_drain_audit.py` (violations) + `post_cascade_ag_queue_seed_capture.py` (marker → queue) + `check_ag_queue_seed_markers.py` (T7t pre-commit) + `check_ag_queue_drain_freshness.py` (weekly drift). §6, §24, §30, §35.
