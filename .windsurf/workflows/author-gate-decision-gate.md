---
description: Present options to user before proceeding with significant decisions
---

> **Cascade workflow note:** This workflow is a reusable procedural lane, not always-on policy. Use it to hold staged retrieval, evidence gathering, execution order, and verification steps that would otherwise overload rules. For deep research, separate retrieval, quote extraction, synthesis, and final verification into distinct phases.

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

### Step 3 — Present Options (STOP HERE)

**REQUIRED**: Use the `ask_user_question` tool — do NOT present options as prose or blockquotes. Per `author-gate-enforcement.md`: *"Surface 1–N options via `ask_user_question` — ALL analysis INSIDE description field, never in chat prose."*

Minimal shape for each option:
- `label`: concise option title (e.g. `Option A — <approach>`)
- `description`: impact, trade-offs, risk — everything the user needs to decide, inside this field

Set `allowMultiple: false`. Include the Author-Gate header packet in the `question` field:
```
Recommended: <option title>
Why it wins: <one sentence, case-specific>
What you are optimizing for: <actual goal>
What is being traded off: <precise cost>
Candidates evaluated: N | Surfaced: M | Suppressed (low confidence): X | Suppressed (non-distinct): Y
```

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
- Related: `/antipattern-author-gate`, `/adg-repair-loop`
