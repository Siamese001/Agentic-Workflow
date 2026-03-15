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
- Emergency rollback
- Auto-fixable violations (ruff, trailing whitespace)

---

### Step 1 — Identify Decision Point

Before proceeding with any action, ask:
1. Are there 2+ valid approaches?
2. Do approaches have different trade-offs?
3. Is user preference unclear?

If YES to all three → invoke HITL.

---

### Step 2 — Analyze Options

For each viable approach, document:
- **What**: Concrete action Cascade will take
- **Impact**: Files affected, scope, risk level
- **Trade-offs**: Pros and cons
- **Effort**: Estimated complexity

Aim for 2-4 options. More than 4 = analysis paralysis.

---

### Step 3 — Present Options (STOP HERE)

**REQUIRED FORMAT**:

> I've identified N approaches for `<task>`:
>
> **Option A**: `<approach>`
> - Impact: `<what changes>`
> - Trade-offs: `<pros/cons>`
>
> **Option B**: `<approach>`
> - Impact: `<what changes>`
> - Trade-offs: `<pros/cons>`
>
> **Option C**: `<approach>`
> - Impact: `<what changes>`
> - Trade-offs: `<pros/cons>`
>
> Which approach should I use?

**CRITICAL**: STOP after presenting options. Do NOT proceed with any option.

---

### Step 4 — Wait for User Selection

User MUST explicitly select:
- "A" or "Option A" or "Use approach A"
- "B" or "Option B" or "Use approach B"
- "C" or "Option C" or "Use approach C"

**FORBIDDEN**:
- Assuming user wants "best" option
- Proceeding with default
- Implementing multiple options
- Guessing intent from ambiguous response

If user response is unclear → restate options and ask for explicit A/B/C selection.

---

### Step 5 — Confirm and Execute

Once user selects, confirm:

> Proceeding with Option `<X>`: `<brief description>`

Then execute ONLY the chosen option.

---

### Step 6 — Record Decision

Add to evidence file or commit message:

```markdown
## HITL_DECISION_RECORD

**Decision Point**: <description>
**Options Presented**: A, B, C
**User Selection**: <A|B|C>
**Rationale**: <user's stated reason, if any>
**Executed Action**: <what was done>
```

---

## Common Decision Templates

### Template: Architecture Choice

> I've identified N approaches for `<feature>`:
>
> **Option A**: Inheritance-based — extend `<BaseClass>`
> - Impact: Single file change, tight coupling to base
> - Trade-offs: Simple, but harder to test in isolation
>
> **Option B**: Composition-based — inject `<Dependency>`
> - Impact: 2 files (interface + impl), loose coupling
> - Trade-offs: More flexible, but additional abstraction
>
> **Option C**: Mixin-based — add `<Mixin>` to existing class
> - Impact: Modify existing class + new mixin file
> - Trade-offs: Reusable, but multiple inheritance complexity
>
> Which approach?

---

### Template: Refactoring Scope

> This refactoring can be scoped as:
>
> **Option A**: Minimal — `<3 files>`
> - Impact: Fix immediate issue only
> - Trade-offs: Fast, low risk, but leaves technical debt
>
> **Option B**: Moderate — `<8 files>`
> - Impact: Fix issue + related duplicates
> - Trade-offs: Balanced risk/reward, 2x effort
>
> **Option C**: Comprehensive — `<20+ files>`
> - Impact: Full consolidation across codebase
> - Trade-offs: Eliminates debt, but high risk, 5x effort
>
> Which scope?

---

### Template: Test Repair Strategy

> Test `<nodeid>` is failing. Possible fixes:
>
> **Option A**: Fix production code — `<bug description>`
> - Repair class: `production_bug_fix`
> - Impact: `<affected modules>`
>
> **Option B**: Update stale reference — `<old_path>` → `<new_path>`
> - Repair class: `stale_reference_fix`
> - Impact: Test file only
>
> **Option C**: Fix broken test assertion — `<what's wrong>`
> - Repair class: `broken_test_fix` (semantic equivalence preserved)
> - Impact: Test file only
>
> **Option D**: Restore policy contract — `<policy drift>`
> - Repair class: `policy_regression_fix`
> - Impact: Governance config + production code
>
> Which repair class?

---

### Template: Dependency Addition

> To implement `<feature>`, I can:
>
> **Option A**: Add `<package>` from PyPI
> - Impact: New dependency in requirements.txt
> - Trade-offs: Battle-tested, but external dependency
>
> **Option B**: Implement in-house
> - Impact: New module in `<layer>`
> - Trade-offs: Full control, but maintenance burden
>
> **Option C**: Use existing `<alternative>`
> - Impact: No new dependencies
> - Trade-offs: May not be perfect fit, requires adaptation
>
> Which approach?

---

### Template: File Deletion

> File `<path>` can be handled as:
>
> **Option A**: Delete immediately
> - Preconditions: `<N>` references migrated, 90-day deprecation elapsed
> - Impact: Permanent removal
>
> **Option B**: Deprecate first
> - Impact: Add deprecation warning, set 90-day timer
> - Trade-offs: Safe transition, but delays cleanup
>
> **Option C**: Keep as shim
> - Impact: Redirect to `<replacement>`, document in registry
> - Trade-offs: Zero breakage, but maintains legacy path
>
> **Option D**: Cancel deletion
> - Reason: `<why file is still needed>`
>
> Which approach?

---

### Template: Error Handling

> Error `<error_type>` can be handled as:
>
> **Option A**: Fail-closed — raise immediately
> - Impact: Operation blocks on error
> - Trade-offs: Safe, but may block legitimate work
>
> **Option B**: Fail-open with logging — log + continue
> - Impact: Degraded behavior on error
> - Trade-offs: Resilient, but may hide issues
>
> **Option C**: Retry with backoff — `<retry_config>`
> - Impact: Automatic recovery attempt
> - Trade-offs: Handles transient failures, but delays
>
> **Option D**: Escalate to user — prompt for intervention
> - Impact: User must decide
> - Trade-offs: Correct decision, but requires user attention
>
> Which strategy?

---

### Template: Performance Optimization

> Performance can be improved via:
>
> **Option A**: Add caching — `<cache_strategy>`
> - Impact: 10x speedup, +50 lines, memory overhead
> - Trade-offs: Fast, but cache invalidation complexity
>
> **Option B**: Batch processing — `<batch_size>`
> - Impact: 3x speedup, +20 lines, latency increase
> - Trade-offs: Efficient, but delayed results
>
> **Option C**: Keep current — prioritize simplicity
> - Impact: No change
> - Trade-offs: Maintainable, but slower
>
> Which approach?

---

## Anti-Patterns to Avoid

**DON'T**:
```
I think Option A is best. Should I proceed?
```
❌ Presents bias, asks for permission instead of choice

**DON'T**:
```
I'll do Option A unless you object.
```
❌ Assumes default, doesn't wait for selection

**DON'T**:
```
What would you like me to do?
```
❌ Open-ended, no concrete options

**DO**:
```
Option A: <concrete action> — <trade-offs>
Option B: <concrete action> — <trade-offs>
Which approach?
```
✅ Concrete options, explicit choice, no bias

---

## Integration with Other Workflows

- **`/antipattern-hitl-gate`**: Specific HITL for anti-pattern introduction
- **`/adg-repair-loop`**: Use HITL for repair class selection (§2.5)
- **`/adg-redis-refresh`**: Use HITL for regeneration timing (§HITL-1.10)

---

## Enforcement

This is a **behavioral rule** enforced during Windsurf execution.

**Reference**: `.windsurf/rules/hitl-enforcement.md`

**Violation**: Proceeding without HITL when required violates user trust and may waste effort.

**Recovery**: Rollback, present options, wait for selection, re-execute.
