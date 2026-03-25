---
description: Present options to user before proceeding with significant decisions
---

## HITL (Human-In-The-Loop) Decision Gate

Use this workflow BEFORE making any significant decision with multiple valid approaches.

### When to Invoke

**MANDATORY TRIGGERS**:
- Multiple architectural approaches are viable
- Refactoring affects >3 files or crosses layer boundaries
- Adding new external dependencies
- Deleting production files (especially *Agent.py)
- Modifying governance/policy configuration
- Introducing anti-patterns (see `/antipattern-hitl-gate`)
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

Ask: Are there 2+ valid approaches with different trade-offs and unclear user preference? If YES to all → invoke HITL.

### Step 2 — Analyze Options

For each approach (2-4 options, never more): **What** (concrete action), **Impact** (files, scope, risk), **Trade-offs** (pros/cons), **Effort** (complexity).

### Step 3 — Present Options (STOP HERE)

**REQUIRED FORMAT**:

> I've identified N approaches for `<task>`:
>
> **Option A**: `<approach>` — Impact: `<what changes>` — Trade-offs: `<pros/cons>`
>
> **Option B**: `<approach>` — Impact: `<what changes>` — Trade-offs: `<pros/cons>`
>
> Which approach should I use?

**CRITICAL**: STOP after presenting. Do NOT proceed with any option.

### Step 4 — Wait for User Selection

User MUST explicitly select A/B/C/D. **FORBIDDEN**: assuming "best" option, proceeding with default, implementing multiple options, guessing from ambiguous response. If unclear → restate and ask again.

### Step 5 — Confirm and Execute

> Proceeding with Option `<X>`: `<brief description>`

Execute ONLY the chosen option.

### Step 6 — Record Decision

```markdown
## HITL_DECISION_RECORD
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

- Rule: `.windsurf/rules/hitl-enforcement.md`
- Related: `/antipattern-hitl-gate`, `/adg-repair-loop`
