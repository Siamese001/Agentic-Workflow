---
plan_type: audit
---

# Author-Gate Canonical Emitter RCA & Procedural Fix

> **Status:** Completed · **Tier:** T1 · **Slug:** `author-gate-canonical-emitter-rca-c7f9d1`
> **Triggered by:** W3 P3.1 + P3.2 Author-Gate invocations missing confidence prefix, tradeoff segment, and dominance star.

---

## 1. Incident Summary

During W3 Author-Gate invocations (P3.1 C0 depth thresholds, P3.2 PA compiler completeness),
`ask_user_question` options were hand-crafted with plain label/description pairs.

**Observed UI failures:**
- No `[confidence=0.NN]` prefix on any option description (UI invariant 1 violation)
- No `⭐` dominance star on recommended option (UI invariant 4 violation)
- No `· trade-off: <text>` tradeoff segment (UI invariant 4 violation)
- No `AUTHOR_GATE_PACKET:` block emitted (enforcement hook never ran; ledger never updated)

---

## 2. Root Cause

Cascade bypassed the three-step canonical pipeline:

```
refactor-decision-memory → author-gate-packet-builder (emit_packet.py) → author-gate-ui-renderer → ask_user_question
```

and instead hand-crafted option `label` + `description` strings directly into `ask_user_question`.

**Constitutional violation:** `author-gate-enforcement.md` §"Canonical-emitter invariant (2026-05-03)":
> Hand-crafting the packet from memory of the schema is FORBIDDEN.

**Enforcement gap:** `post_cascade_author_gate_ui_audit.py` invariants 1–4 log violations to
`artifacts/windsurf/author_gate_ui_violations.jsonl` **after** the response. The pre-response hook
cannot intercept `ask_user_question` arguments. This means the violation is only discovered
post-hoc — the user saw the degraded UI before the audit ran.

---

## 3. Corrective Actions

### 3.1 Immediate (this session)

- [x] RCA filed (this document)
- [x] Re-run P3.1 and P3.2 Author-Gate decisions through the canonical pipeline:
  1. `skill: refactor-decision-memory` — consult precedent ledger
  2. `skill: author-gate-packet-builder` — build JSON spec, run `emit_packet.py`
  3. `skill: author-gate-ui-renderer` — render recommendation card
  4. Pass `OPTIONS_JSON` surface_description values unchanged to `ask_user_question`

### 3.2 Procedural Fix (permanent)

**Root rule:** Before EVERY `ask_user_question` that is an Author-Gate decision:
1. MUST invoke `author-gate-packet-builder` skill
2. MUST invoke `author-gate-ui-renderer` skill
3. MUST use the `surface_description` from `OPTIONS_JSON` as the `description` field
4. NEVER hand-craft label/description pairs for Author-Gate decisions

This is already stated in `author-gate-enforcement.md` but was not followed. No code change needed —
the procedural discipline is the fix.

### 3.3 Detection Enhancement (deferred — not in scope this session)

DEFERRED_SCOPE: Pre-response guard that warns when `ask_user_question` is called in the same
response as an Author-Gate context word (e.g. "Author-Gate", "P3.", "AG:") but no
`AUTHOR_GATE_PACKET:` block is present. Difficulty: pre-response hooks cannot see tool arguments.
Alternative: post-cascade hook pattern match `ask_user_question` + guard word + missing packet.
P-band: P3. Assign to: post_cascade_author_gate_ui_audit.py extension.

---

## 4. Wave Structure

| Wave | Focus | Status |
|------|-------|--------|
| W1 | RCA + plan saved to Notion | Done |
| W2 | Re-run P3.1 + P3.2 via canonical pipeline | Done |

---

## 5. Phase-Level Summary

| Phase | Title | Scope | Est. Tokens | Status |
|-------|-------|-------|-------------|--------|
| W1.P1 | RCA document | This file | 1k | Done |
| W1.P2 | Notion plan registration | Notion Plans DB | 0.5k | Done |
| W2.P1 | Re-run P3.1 via canonical pipeline | emit_packet.py + ask_user_question | 1k | Done |
| W2.P2 | Re-run P3.2 via canonical pipeline | emit_packet.py + ask_user_question | 1k | Done |

---

## 6. References

- `author-gate-enforcement.md` §"Canonical-emitter invariant (2026-05-03)"
- `.windsurf/skills/author-gate-packet-builder/emit_packet.py`
- `.windsurf/skills/author-gate-ui-renderer/render_card.py`
- `.windsurf/scripts/post_cascade_author_gate_ui_audit.py`
- Constitutional §30 (Author-Gate capture health mandatory)
