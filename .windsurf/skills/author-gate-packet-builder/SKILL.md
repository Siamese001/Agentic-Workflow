---
name: author-gate-packet-builder
description: Emit a schema-valid Author-Gate Decision packet for harness author-gate (developer-loop) decisions. Use when an author-gate decision point is reached during code authoring (refactoring scope, architecture choice, anti-pattern, deletion, dependency add, test strategy, error handling). Not the same as runtime HITL (v30 step [5] / ADR-023). This skill consults precedent, constructs the AG-10 option shape with didactic fields + gold-star on the recommended option, and writes AUTHOR_GATE_PACKET (with HITL_PACKET legacy alias) that post_cascade_author_gate_capture consumes. Third person, deterministic, invoked before ask_user_question.
metadata:
  enforcement_layer: windsurf
  enforcement_timing: before_author_gate
  enforcement_type: behavioural
---

# Author-Gate Packet Builder

**PURPOSE:** Turn ambiguous Author-Gate decisions into schema-valid, didactic packets.

Every packet emitted by this skill:

1. Passes `ops_scripts/ci/author_gate/check_ledger_schema.py` validation
2. Carries a `context_fingerprint` matching the pending change (for gate correlation)
3. Includes 3 didactic fields per option: `principle_at_stake`, `what_youd_miss`, `what_would_flip`
4. Embeds precedent verdict from `refactor-decision-memory` skill
5. Is captured by `post_cascade_author_gate_capture.py` into the decision ledger

## When to Invoke

Invoke BEFORE `ask_user_question` whenever the decision matches any §AG-1 class:

- architecture_choice — cross-layer structural choice
- refactor_scope — scope of a refactor
- anti_pattern — introducing or resolving an anti-pattern
- deletion_strategy — removing production code
- dependency_addition — new dep or version change
- test_strategy — test modification/skip/xfail
- error_handling — new `except` block or swallow pattern

Do NOT invoke for T0/T1 edits, pure lints, or formatting-only changes.

> ⛔ **Pipeline Completion Invariant**: the emitted `AUTHOR_GATE_PACKET:` block **MUST** be followed by `ask_user_question` **in the same Cascade response**. Emitting the packet and ending the response without `ask_user_question` is a critical violation. Enforcement: `post_cascade_author_gate_pipeline_audit.py`. See plan `author-gate-ui-renderer-hardening-a7f3c2`.

## Files

- `packet_template.md` — fill-in template with AG-10 fields + didactic slots
- `emit_packet.py` — CLI that takes trigger metadata + candidates, emits `AUTHOR_GATE_PACKET:` block (with `HITL_PACKET:` legacy alias)
- `precedent_injector.py` — wrapper over `lookup_refactor_decisions.py`; adds verdict to packet

## Usage

### From a skill-aware context

```bash
echo '{
  "decision_type": "refactor_scope",
  "user_goal": "Extract L2 execution adapter into a dedicated module",
  "normalized_intent": "Split agentic_core/L2_execution/adapters.py into 3 files",
  "files_in_scope": ["agentic_core/L2_execution/adapters.py"],
  "candidates": [
    {
      "id": "minimal",
      "thesis": "Extract only SovereignBaseAgent; defer siblings",
      "confidence_score": 0.88,
      "key_tradeoffs": ["Gains reversibility, loses coverage of L4 pattern"],
      "principle_at_stake": "layer gravity",
      "what_youd_miss": "would keep L4-sibling drift unaddressed",
      "what_would_flip": "if blast_radius includes L5 safety"
    },
    {
      "id": "comprehensive",
      "thesis": "Extract all 5 siblings in one wave",
      "confidence_score": 0.61
    }
  ]
}' | python .windsurf/skills/author-gate-packet-builder/emit_packet.py
```

Output (stdout): an `AUTHOR_GATE_PACKET:` block (JSON) that `post_cascade_author_gate_capture.py` scans for. The legacy `HITL_PACKET:` alias is emitted alongside for back-compat with older scanners.

### Precedent-only lookup (without packet emit)

```bash
echo '{"decision_type": "refactor_scope", "normalized_intent": "..."}' | \
  python .windsurf/skills/author-gate-packet-builder/precedent_injector.py
```

## Output Shape (AUTHOR_GATE_PACKET block)

Emitted to stdout, fenced. Consumed by `post_cascade_author_gate_capture.py`:

```
AUTHOR_GATE_PACKET: {
  "decision_id": "dec_<ulid>",
  "decision_type": "refactor_scope",
  "user_goal": "...",
  "normalized_intent": "...",
  "principle_at_stake": "layer gravity",
  "context_fingerprint": {
    "adg_snapshot": "adg_indexed_<ts>.sqlite",
    "git_sha": "<sha>",
    "branch": "main",
    "files_in_scope": [...],
    "fp": "<16hex>"
  },
  "policy_snapshot": "author-gate@<rule_sha>",
  "candidates": [
    {
      "id": "minimal",
      "surfaced": true,
      "confidence_score": 0.88,
      "suppression_reason": null,
      "thesis": "...",
      "key_tradeoffs": [...],
      "principle_at_stake": "...",
      "what_youd_miss": "...",
      "what_would_flip": "..."
    },
    { "id": "comprehensive", "surfaced": false, "confidence_score": 0.61,
      "suppression_reason": "below_surface_threshold" }
  ],
  "routing": {
    "rule_applied": "dominance_fires",
    "surface_threshold": 0.72,
    "dominance_delta_observed": 0.27
  },
  "precedent": {
    "verdict": "suggestive",
    "matched_ids": ["dec_abc123"],
    "summary": "Prior decision (2026-04-10): minimal scope succeeded"
  },
  "status": "surfaced"
}
```

## Validation

The emitter runs every packet through `.windsurf/schemas/decision_record.schema.json` before
writing. Invalid packets are rejected with a structured error to stderr and exit 1.

## Progressive Disclosure

- `SKILL.md` (this file): when to invoke, high-level shape
- `packet_template.md`: full AG-10 option shape with didactic field semantics (Cascade reads on demand)
- `emit_packet.py`: deterministic emission + schema validation
- `precedent_injector.py`: isolated precedent lookup used by emit_packet and standalone
