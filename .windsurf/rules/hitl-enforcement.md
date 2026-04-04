# HITL (Human-In-The-Loop) Enforcement Rule

**Trigger**: always_on
**Layer**: Windsurf (AI-time behavioral)
**Type**: Behavioural
**Priority**: Constitutional

---

## §HITL-0: Core Principle

**HITL (Human-In-The-Loop) means Cascade MUST present you with options to choose from rather than just proceeding with significant actions.**

When facing a decision point with multiple valid approaches, Cascade MUST:
1. **STOP before taking action**
2. **Present 2-4 concrete options** with trade-offs
3. **Wait for explicit user selection**
4. **Execute only the chosen option**

### §HITL-0.1: Continuous Execution Mandate

**Cascade MUST execute continuously without stopping UNLESS a genuine HITL decision point is reached.**

**FORBIDDEN BEHAVIORS**:
- ❌ Stopping after every tool call to "check in"
- ❌ Asking permission for deterministic actions
- ❌ Presenting options when there's only one correct path
- ❌ Breaking work into artificial "phases" to ask for approval
- ❌ Stopping to summarize progress when work is incomplete

**REQUIRED BEHAVIORS**:
- ✅ Execute all deterministic steps continuously
- ✅ Chain tool calls without interruption when path is clear
- ✅ Only stop when multiple valid approaches exist
- ✅ Present clickable options via `ask_user_question` tool
- ✅ Include pros/cons/recommendation in option descriptions

**CLICKABLE CASCADE OPTIONS FORMAT**:
When HITL is required, use `ask_user_question` tool with:
- **Question**: Clear decision point description
- **Options** (2-4): Each with label + description including:
  - What the option does
  - **Pros**: Benefits/advantages
  - **Cons**: Drawbacks/risks
  - **Recommendation**: ⭐ marker if this is the recommended choice
- **allowMultiple**: false (single selection required)

**EXAMPLE**:
```
ask_user_question(
  question="Wave 2 getattr migration found only 11 patterns. How should we proceed?",
  options=[
    {
      label: "Investigate ADG detection patterns",
      description: "Analyze what patterns ADG actually detects vs what AST tool catches. Pros: Root cause understanding, better tool. Cons: Takes time, delays other waves. ⭐ RECOMMENDED"
    },
    {
      label: "Continue to Wave 3 (clock)",
      description: "Defer getattr work, proceed with clock elimination. Pros: Immediate progress on clearer target. Cons: Leaves 2,966 getattr sites unaddressed."
    },
    {
      label: "Manual getattr review",
      description: "Sample 20 getattr sites and fix manually. Pros: Quick validation. Cons: Doesn't scale, no automation."
    }
  ],
  allowMultiple=false
)
```

---

## §HITL-1: Mandatory HITL Decision Points

### 1.1 Code Architecture Decisions

**TRIGGER**: When multiple architectural approaches are viable

**REQUIRED PROMPT (STAR Format)**:

> **SITUATION**: Facing architectural choice for `<task>` with multiple valid approaches.
>
> **TASK**: Select the optimal approach aligned with SVP Engineering priorities.
>
> **OPTIONS**:
>
> **Option A**: `<approach>`
>   - **Pros**: `<benefits>`
>   - **Cons**: `<drawbacks>`
>
> **Option B**: `<approach>`
>   - **Pros**: `<benefits>`
>   - **Cons**: `<drawbacks>`
>
> **Option C**: `<approach>` (if applicable)
>   - **Pros**: `<benefits>`
>   - **Cons**: `<drawbacks>`
>
> **⭐ RECOMMENDED**: Option `<X>` — Aligns with SVP priority `<(a) operational simplicity | (b) dependency hygiene | (c) archival discipline | (d) documentation | (e) zero-regression validation>`.
>
> **RESULT**: Execute chosen approach with full test coverage.
>
> Which approach should I use? (A/B/C)

**EXAMPLES**:
- Choosing between inheritance vs composition
- Deciding layer placement (L0-L6) for new module
- Selecting between factory pattern vs direct instantiation
- Choosing test strategy (unit vs integration vs both)

### 1.2 Refactoring Scope

**TRIGGER**: When refactoring could affect multiple files or modules

**REQUIRED PROMPT (STAR Format)**:

> **SITUATION**: Refactoring `<target>` can be scoped at multiple levels with varying risk.
>
> **TASK**: Select scope balancing risk, time, and SVP operational simplicity priority.
>
> **OPTIONS**:
>
> **Option A**: Minimal — `<files>`
>   - **Pros**: Lowest risk, fast validation, minimal blast radius
>   - **Cons**: May leave related technical debt, requires follow-up
>
> **Option B**: Moderate — `<files>`
>   - **Pros**: Comprehensive within module/layer, addresses related issues
>   - **Cons**: Higher risk, longer validation time, potential for regression
>
> **Option C**: Comprehensive — `<files>`
>   - **Pros**: Complete elimination of pattern, future-proof
>   - **Cons**: Maximum risk, extended validation period, may touch unrelated systems
>
> **⭐ RECOMMENDED**: Option A (Minimal) — SVP priority: operational simplicity through incremental, low-risk changes with full test validation at each step.
>
> **RESULT**: Execute scoped refactoring with zero-regression validation.
>
> Which scope should I target? (A/B/C)

**EXAMPLES**:
- Renaming widely-used function
- Moving module between layers
- Consolidating duplicate code
- Changing interface signatures

### 1.3 Anti-Pattern Introduction

**TRIGGER**: Before introducing any anti-pattern instance

**REQUIRED PROMPT (STAR Format)**:

> **SITUATION**: This change will introduce `<N>` new `<category>` instance(s) in `<file>`, which the anti-pattern scanner will flag.
>
> **TASK**: Select approach that balances immediate need against architectural integrity.
>
> **OPTIONS**:
>
> **Option A**: Narrow the exception type
>   - **Pros**: No guardian comment needed, proper exception handling, passes scanner
>   - **Cons**: Requires understanding the specific error types that may occur
>
> **Option B**: Add `# guardian: allow-<category>`
>   - **Pros**: Quick exemption, unblocks immediate work
>   - **Cons**: Technical debt, requires HITL approval, tracked in ratchet ceiling, may hide real issues
>
> **Option C**: Restructure to avoid the pattern entirely
>   - **Pros**: Cleanest solution, aligns with SVP dependency hygiene priority
>   - **Cons**: May require significant redesign, longer implementation time
>
> **Option D**: Proceed as-is and accept the ratchet increase
>   - **Pros**: No code changes needed, preserves current approach
>   - **Cons**: Violates architectural standards, increases anti-pattern debt, may block CI
>
> **⭐ RECOMMENDED**: Option A (Narrow the exception type) — SVP priority: dependency hygiene through proper exception handling without introducing exemptions.
>
> **RESULT**: Implement chosen approach with appropriate validation.
>
> Which approach? (A/B/C/D)

**EXAMPLES**:
- New `except Exception` block
- New `os.path.*` call
- String path concatenation
- Silent exception swallower

### 1.4 Test Modification Strategy

**TRIGGER**: When test failures could be fixed multiple ways

**REQUIRED PROMPT (STAR Format)**:

> **SITUATION**: Test `<nodeid>` is failing. Multiple repair classes are applicable.
>
> **TASK**: Select repair class aligned with root cause and SVP zero-regression priority.
>
> **OPTIONS**:
>
> **Option A**: `production_bug_fix`
>   - **Description**: `<description>`
>   - **Pros**: Addresses root cause, improves system quality, prevents recurrence
>   - **Cons**: Requires deeper analysis, may have broader impact
>
> **Option B**: `stale_reference_fix`
>   - **Description**: `<description>`
>   - **Pros**: Quick fix, aligns with current architecture
>   - **Cons**: Doesn't validate if symbol/path change was intentional
>
> **Option C**: `broken_test_fix` (semantic equivalence preserved)
>   - **Description**: `<description>`
>   - **Pros**: Maintains test intent while updating for changes
>   - **Cons**: Risk of weakening test coverage if not careful
>
> **Option D**: `policy_regression_fix`
>   - **Description**: `<description>`
>   - **Pros**: Corrects governance/policy drift
>   - **Cons**: May change intended behavior, requires policy review
>
> **⭐ RECOMMENDED**: Option A (production_bug_fix) — SVP priority: zero-regression validation through addressing root causes rather than symptom patching.
>
> **RESULT**: Apply selected repair class with full test validation.
>
> Which repair class should I apply? (A/B/C/D)

**EXAMPLES**:
- Assertion mismatch (fix code vs fix test)
- Import path changed (update reference vs restore old path)
- Expected error type changed
- Threshold/policy drift

### 1.5 Dependency Addition

**TRIGGER**: Before adding new external dependencies

**REQUIRED PROMPT (STAR Format)**:

> **SITUATION**: To implement `<feature>`, external dependency or in-house solution is needed.
>
> **TASK**: Select approach aligned with SVP dependency hygiene priority.
>
> **OPTIONS**:
>
> **Option A**: Add dependency `<package>`
>   - **Pros**: Faster implementation, battle-tested, community support
>   - **Cons**: Increases dependency surface, supply chain risk, potential version conflicts
>
> **Option B**: Implement in-house
>   - **Pros**: Reduces dependencies, full control, tailored to needs, aligns with SVP dependency hygiene
>   - **Cons**: Development time, maintenance burden, must meet testing standards
>
> **Option C**: Use existing `<alternative>`
>   - **Pros**: No new dependencies, leverages known patterns
>   - **Cons**: May not fit perfectly, could require workarounds
>
> **⭐ RECOMMENDED**: Option B (Implement in-house) — SVP priority: dependency hygiene through eliminating external dependencies unless critical capability gap exists.
>
> **RESULT**: Implement chosen approach with full documentation (per SVP priority d).
>
> Which approach? (A/B/C)

**EXAMPLES**:
- New PyPI package
- New system dependency
- New MCP server
- New external API

### 1.6 File/Module Deletion

**TRIGGER**: Before deleting any production file

**REQUIRED PROMPT (STAR Format)**:
>
> **SITUATION**: File `<path>` is candidate for removal. References and deprecation status must be evaluated.
>
> **TASK**: Select disposition aligned with SVP archival priority.
>
> **OPTIONS**:
>
> **Option A**: Delete immediately
>   - **Description**: `<references>` migrated, `<deprecation_period>` elapsed
>   - **Pros**: Immediate cleanup, reduces clutter
>   - **Cons**: Irreversible, history lost, risk if references missed
>
> **Option B**: Deprecate first
>   - **Description**: Add deprecation warning, set 90-day timer
>   - **Pros**: Graceful transition, time for migration, visibility of pending removal
>   - **Cons**: Code remains active during deprecation period
>
> **Option C**: Keep as shim
>   - **Description**: Redirect to `<replacement>`, document in shim registry
>   - **Pros**: Backward compatibility preserved, clear migration path
>   - **Cons**: Maintenance burden of shim layer
>
> **Option D**: Archive instead of delete
>   - **Description**: Move to `tools/archive/`, preserve history
>   - **Pros**: History preserved, can reference later, aligns with SVP archival discipline
>   - **Cons**: Repository size slightly larger
>
> **⭐ RECOMMENDED**: Option D (Archive) — SVP priority: archival over deletion preserves history in `tools/archive/`.
>
> **RESULT**: Execute chosen disposition with appropriate validation.
>
> Which approach? (A/B/C/D)

**EXAMPLES**:
- Agent deletion (§1.6 requirements)
- Utility module consolidation
- Dead code removal
- Test file cleanup

### 1.7 Configuration Changes

**TRIGGER**: Before modifying governance/policy configuration

**REQUIRED PROMPT (STAR Format)**:
>
> **SITUATION**: Configuration `<config_file>` requires update with potential governance impact.
>
> **TASK**: Select change option balancing scope against SVP zero-regression priority.
>
> **OPTIONS**:
>
> **Option A**: `<change>` — affects `<scope>`
>   - **Pros**: `<benefits>`
>   - **Cons**: `<risks>`
>
> **Option B**: `<change>` — affects `<scope>`
>   - **Pros**: `<benefits>`
>   - **Cons**: `<risks>`
>
> **Option C**: Keep current — `<reason>`
>   - **Pros**: No risk of regression, stability maintained
>   - **Cons**: Issue persists, may accumulate technical debt
>
> **⭐ RECOMMENDED**: Option with narrowest scope that addresses root cause — SVP priority: zero-regression validation requires full test pass before any configuration commit.
>
> **RESULT**: Apply configuration change with comprehensive test validation.
>
> Which option? (A/B/C)

**EXAMPLES**:
- Confidence thresholds
- Retry limits
- Timeout values
- Layer boundary rules

### 1.8 Error Handling Strategy

**TRIGGER**: When implementing error handling with multiple valid approaches

**REQUIRED PROMPT (STAR Format)**:
>
> **SITUATION**: Error `<error_type>` requires handling strategy selection.
>
> **TASK**: Select strategy aligned with SVP operational simplicity through fail-closed discipline.
>
> **OPTIONS**:
>
> **Option A**: Fail-closed
>   - **Description**: Raise immediately, no fallback
>   - **Pros**: Maximum safety, no silent failures, clear error propagation
>   - **Cons**: User-facing errors, requires upstream handling
>
> **Option B**: Fail-open with logging
>   - **Description**: Log + continue with degraded behavior
>   - **Pros**: User experience preserved, operation continues
>   - **Cons**: Risk of silent data corruption, log may be missed
>
> **Option C**: Retry with backoff
>   - **Description**: `<retry_config>`
>   - **Pros**: Transient failures resolved automatically
>   - **Cons**: Complexity, latency, may mask real issues
>
> **Option D**: Escalate to user
>   - **Description**: Prompt for manual intervention
>   - **Pros**: Human judgment applied, no automated wrong decisions
>   - **Cons**: Blocks automation, requires human availability
>
> **⭐ RECOMMENDED**: Option A (Fail-closed) — SVP priority: operational simplicity through deterministic fail-closed behavior with clear error propagation.
>
> **RESULT**: Implement chosen strategy with appropriate test coverage.
>
> Which strategy? (A/B/C/D)

**EXAMPLES**:
- External API failures
- Missing configuration
- Invalid user input
- Resource exhaustion

### 1.9 Performance Optimization Trade-offs

**TRIGGER**: When optimization involves correctness/complexity trade-offs

**REQUIRED PROMPT (STAR Format)**:
>
> **SITUATION**: Performance improvement opportunity requires balancing speed against complexity.
>
> **TASK**: Select optimization approach aligned with SVP operational simplicity priority.
>
> **OPTIONS**:
>
> **Option A**: `<optimization>`
>   - **Speedup**: `<speedup>`
>   - **Pros**: Maximum performance gain
>   - **Cons**: `<complexity_increase>`, maintenance burden, risk of bugs
>
> **Option B**: `<optimization>`
>   - **Speedup**: `<speedup>`
>   - **Pros**: Moderate gain with controlled complexity
>   - **Cons**: `<complexity_increase>`, some added complexity
>
> **Option C**: Keep current
>   - **Pros**: Prioritizes simplicity, no new failure modes
>   - **Cons**: Performance gap remains
>
> **⭐ RECOMMENDED**: Option B or C — SVP priority: operational simplicity over premature optimization unless performance is critical path.
>
> **RESULT**: Implement chosen optimization with full regression testing.
>
> Which approach? (A/B/C)

**EXAMPLES**:
- Caching strategies
- Batch processing
- Parallel execution
- Index optimization

### 1.10 ADG Regeneration Timing

**TRIGGER**: After code changes that may affect ADG

**REQUIRED PROMPT (STAR Format)**:
>
> **SITUATION**: ADG may be stale after recent changes. Regeneration timing impacts current work velocity.
>
> **TASK**: Select timing that balances immediate progress against analysis accuracy.
>
> **OPTIONS**:
>
> **Option A**: Regenerate now
>   - **Pros**: Guaranteed fresh analysis, accurate dependency graphs
>   - **Cons**: Blocks current work for ~30s, immediate delay
>
> **Option B**: Defer to end of session
>   - **Pros**: Faster immediate progress, no current interruption
>   - **Cons**: Risk of stale analysis leading to incorrect decisions
>
> **Option C**: Skip
>   - **Pros**: Maximum velocity, no regeneration time
>   - **Cons**: Analysis may be outdated, decisions based on stale graph
>
> **⭐ RECOMMENDED**: Option A (Regenerate now) — SVP priority: zero-regression validation requires accurate dependency analysis for any significant change.
>
> **RESULT**: Execute regeneration and continue with verified-fresh analysis.
>
> Which timing? (A/B/C)

**EXAMPLES**:
- After refactoring imports
- After moving files
- After adding new modules
- After test changes

---

## §HITL-2: Option Presentation Format

### 2.1 Required Elements

Every HITL prompt MUST include:
1. **Context**: Brief description of the decision point
2. **Options**: 2-4 concrete alternatives (A, B, C, D)
3. **Trade-offs**: Pros/cons or impact for each option
4. **Question**: Explicit "Which approach/option/strategy?"

### 2.2 Forbidden Patterns

**NEVER**:
- Present only one option and ask for confirmation
- Proceed with "default" option without user choice
- Ask open-ended "what should I do?" without concrete options
- Hide trade-offs or present biased options
- Make the decision and then ask for approval

### 2.3 Option Quality Standards

Each option MUST:
- Be **actionable** — clear what Cascade will do
- Be **distinct** — meaningfully different from other options
- Include **impact** — what changes, what's affected
- Be **honest** — real trade-offs, not strawman alternatives

---

## §HITL-3: Execution Discipline

### 3.1 Wait for Selection

After presenting options:
1. **STOP** — do not proceed with any option
2. **WAIT** — user must explicitly select A, B, C, or D
3. **CONFIRM** — acknowledge selection before executing
4. **EXECUTE** — only the chosen option

### 3.2 No Assumptions

**FORBIDDEN**:
- "I'll proceed with Option A unless you object"
- "Option B seems best, so I'll do that"
- "Let me know if you want something different"
- Implementing multiple options "to give you choices"

### 3.3 Clarification Protocol

If user response is ambiguous:
1. Restate the options
2. Ask for explicit A/B/C/D selection
3. Do not guess intent

---

## §HITL-4: Bypass Conditions

HITL may be bypassed ONLY when:

1. **Trivial changes** — fixing typos, formatting, whitespace
2. **Deterministic fixes** — single correct solution (syntax errors, import errors)
3. **Explicit user directive** — user said "just do X" with no ambiguity
4. **Emergency rollback** — reverting broken commit
5. **Auto-fixable violations** — ruff, trailing whitespace, etc.

**All other cases require HITL.**

---

## §HITL-5: Evidence Requirements

When HITL is invoked, evidence file MUST include:

```markdown
## HITL_DECISION_RECORD

**Decision Point**: <description>
**Options Presented**: A, B, C, D
**User Selection**: <A|B|C|D>
**Rationale**: <user's stated reason, if provided>
**Executed Action**: <what Cascade did>
```

---

## §HITL-6: Enforcement

### 6.1 Windsurf Layer

This is a **behavioral rule** enforced during AI execution. No pre-commit hook can verify HITL compliance.

### 6.2 Audit Trail

All HITL decisions MUST be recorded in:
- Evidence files (`docs/reports/plans/`)
- Commit messages (when applicable)
- Plan updates (when scope changes)

### 6.3 Violation Consequences

Proceeding without HITL when required:
- Violates user trust
- May result in wasted work
- Requires rollback and re-execution with HITL

---

## §HITL-7: Quick Reference

| Scenario | HITL Required? | Bypass Allowed? |
|----------|----------------|-----------------|
| Multiple architectural approaches | ✅ YES | ❌ NO |
| Refactoring >3 files | ✅ YES | ❌ NO |
| Adding anti-pattern | ✅ YES | ❌ NO |
| Test failure with multiple fixes | ✅ YES | ❌ NO |
| Adding external dependency | ✅ YES | ❌ NO |
| Deleting production file | ✅ YES | ❌ NO |
| Changing governance config | ✅ YES | ❌ NO |
| Error handling strategy | ✅ YES | ❌ NO |
| Performance vs complexity | ✅ YES | ❌ NO |
| ADG regeneration timing | ✅ YES | ✅ YES (if clearly no impact) |
| Fixing typo | ❌ NO | ✅ YES |
| Auto-formatting | ❌ NO | ✅ YES |
| Syntax error fix | ❌ NO | ✅ YES (if single correct solution) |
| User said "just do X" | ❌ NO | ✅ YES (if unambiguous) |

---

## §HITL-8: Integration with Existing Rules

HITL complements but does not replace:
- **§0 DEFAULT ANALYSIS MODE** — still build ADG first, then present options
- **§1 TESTING FRAMEWORK** — still require tests, but let user choose test strategy
- **§2 ADG FRAMEWORK** — still use graph, but let user choose scope
- **§9 EXECUTION MODALITY** — still work in phases, but let user choose phase boundaries

**HITL adds**: User choice at decision points
**HITL does not remove**: Technical requirements and quality gates

---

## MAXIM

- **When in doubt, ask.** Multiple valid paths → present options.
- **Options, not permission.** Don't ask "may I?", ask "which way?"
- **Concrete, not abstract.** Show exactly what each option does.
- **Honest trade-offs.** Real pros/cons, not biased steering.
- **Wait for choice.** No defaults, no assumptions, no proceeding without selection.
