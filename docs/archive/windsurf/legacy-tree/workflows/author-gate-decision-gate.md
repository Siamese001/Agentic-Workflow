---
description: Present options to user before proceeding with significant decisions
---

> **Cursor Agent workflow note:** This workflow is a reusable procedural lane, not always-on policy. Use it to hold staged retrieval, evidence gathering, execution order, and verification steps that would otherwise overload rules. For deep research, separate retrieval, quote extraction, synthesis, and final verification into distinct phases.

## Author-Gate (Human-In-The-Loop) Decision Gate

Use this workflow BEFORE making any significant decision with multiple valid approaches.

### When to Invoke

**MANDATORY TRIGGERS**:
- Multiple architectural approaches are viable
- Refactoring affects >3 files or crosses layer boundaries
- Adding new external dependencies
- Deleting production files (especially *Agent.py)
- Modifying governance/policy configuration
- Introducing anti-patterns (see `/antipattern-author-gate`)
- Test failures with multiple valid repair classes
- Error handling strategy has trade-offs
- Performance optimization involves complexity increase
- ADG regeneration timing is ambiguous

**BYPASS ALLOWED**:
- Trivial changes (typos, formatting, whitespace)
- Deterministic fixes (syntax errors, single correct solution)
- Explicit user directive ("just do X" with no ambiguity)
- Emergency rollback / auto-fixable violations

---

### Step 1 — Identify Decision Point

Ask: Are there 2+ valid approaches with different trade-offs and unclear user preference? If YES to all → invoke Author-Gate.

### Step 2 — Analyze Options

For each approach (2-4 options, never more): **What** (concrete action), **Impact** (files, scope, risk), **Trade-offs** (pros/cons), **Effort** (complexity).

### Step 3 — Present Options via Canonical Author-Gate Pipeline (STOP HERE)

**REQUIRED**: Use the canonical Author-Gate pipeline — do NOT present options as prose or blockquotes. Per `author-gate-enforcement.md`: *"Surface 1–N options via canonical Author-Gate emitter — ALL analysis INSIDE description field, never in chat prose."*

For governance-class decisions (refactoring scope, architecture choice, anti-pattern introduction, dependency adds), use the canonical pipeline:

```python
from .windsurf.skills.author_gate_packet_builder import emit_packet

# Build and emit AUTHOR_GATE_PACKET (canonical path)
packet = emit_packet.build_author_gate_packet(
    decision_type="<type>",
    question="<decision question>",
    options=[
        {
            "id": "A",
            "label": "Option A — <approach>",
            "description": "<impact, trade-offs, risk>",
            "confidence": 0.85,
            "tradeoff": "<what is traded off>",
        },
        {
            "id": "B", 
            "label": "Option B — <approach>",
            "description": "<impact, trade-offs, risk>",
            "confidence": 0.72,
            "tradeoff": "<what is traded off>",
        },
    ],
    recommended_id="A",  # ⭐ marks this option
)

# Emit AUTHOR_GATE_PACKET (canonical path only)
print("AUTHOR_GATE_PACKET: " + json.dumps(packet))

# Present to user via ask_user_question
ask_user_question(
    question=packet["question"],  # Includes confidence prefix [confidence=X.XX]
    options=packet["options"],     # Includes ⭐ on recommended, trade-off segment
    allowMultiple=False,
)
```

**Authority boundary**: AUTHOR_GATE_PACKET is reserved for canonical AG pipeline only. For non-governance branch resolution, use `tools.decisions.build_enriched_choice_question()` (emits ASK_USER_QUESTION_PACKET).

**CRITICAL**: STOP after the tool call. Do NOT proceed with any option until the user responds.

### Step 4 — Wait for User Selection

User MUST explicitly select A/B/C/D. **FORBIDDEN**: assuming "best" option, proceeding with default, implementing multiple options, guessing from ambiguous response. If unclear → restate and ask again.

### Step 5 — Confirm and Execute

> Proceeding with Option `<X>`: `<brief description>`

Execute ONLY the chosen option.

### Step 6 — Record Decision

```markdown
## AUTHOR_GATE_DECISION_RECORD
**Decision Point**: <description>
**Options Presented**: A, B, C
**User Selection**: <A|B|C>
**Rationale**: <user's stated reason, if any>
**Executed Action**: <what was done>
```

---

### Anti-Patterns

- ❌ "I think Option A is best. Should I proceed?" → presents bias
- ❌ "I'll do Option A unless you object." → assumes default
- ❌ "What would you like me to do?" → no concrete options
- ✅ "Option A: <action> — <trade-offs>. Option B: <action> — <trade-offs>. Which?"

### Reference

- Rule: `.windsurf/rules/author-gate-enforcement.md`
- Canonical pipeline: `.windsurf/skills/author-gate-packet-builder/emit_packet.py` (AUTHOR_GATE_PACKET)
- Enriched choices (non-governance): `tools.decisions.enriched_choice_builder` (ASK_USER_QUESTION_PACKET)
- Related workflows: `/antipattern-author-gate`, `/adg-repair-loop`
