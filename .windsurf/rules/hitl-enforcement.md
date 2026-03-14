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

---

## §HITL-1: Mandatory HITL Decision Points

### 1.1 Code Architecture Decisions

**TRIGGER**: When multiple architectural approaches are viable

**REQUIRED PROMPT**:
> I've identified N approaches for `<task>`:
> 
> **Option A**: `<approach>` — `<trade-offs>`  
> **Option B**: `<approach>` — `<trade-offs>`  
> **Option C**: `<approach>` — `<trade-offs>`  
> 
> Which approach should I use?

**EXAMPLES**:
- Choosing between inheritance vs composition
- Deciding layer placement (L0-L6) for new module
- Selecting between factory pattern vs direct instantiation
- Choosing test strategy (unit vs integration vs both)

### 1.2 Refactoring Scope

**TRIGGER**: When refactoring could affect multiple files or modules

**REQUIRED PROMPT**:
> This refactoring can be scoped in N ways:
> 
> **Option A**: Minimal — `<files>` — `<risk level>`  
> **Option B**: Moderate — `<files>` — `<risk level>`  
> **Option C**: Comprehensive — `<files>` — `<risk level>`  
> 
> Which scope should I target?

**EXAMPLES**:
- Renaming widely-used function
- Moving module between layers
- Consolidating duplicate code
- Changing interface signatures

### 1.3 Anti-Pattern Introduction

**TRIGGER**: Before introducing any anti-pattern instance

**REQUIRED PROMPT** (per existing `/antipattern-hitl-gate`):
> This change will introduce N new `<category>` instance(s) in `<file>`.
> 
> **Option A**: Narrow the exception type — no guardian comment needed  
> **Option B**: Add `# guardian: allow-<category>` — exempt from blocking  
> **Option C**: Restructure to avoid the pattern entirely  
> **Option D**: Proceed as-is and accept the ratchet increase  
> 
> Which approach?

**EXAMPLES**:
- New `except Exception` block
- New `os.path.*` call
- String path concatenation
- Silent exception swallower

### 1.4 Test Modification Strategy

**TRIGGER**: When test failures could be fixed multiple ways

**REQUIRED PROMPT**:
> Test `<nodeid>` is failing. I've identified N potential fixes:
> 
> **Option A**: `<production_bug_fix>` — `<description>`  
> **Option B**: `<stale_reference_fix>` — `<description>`  
> **Option C**: `<broken_test_fix>` — `<description>` (semantic equivalence preserved)  
> **Option D**: `<policy_regression_fix>` — `<description>`  
> 
> Which repair class should I apply?

**EXAMPLES**:
- Assertion mismatch (fix code vs fix test)
- Import path changed (update reference vs restore old path)
- Expected error type changed
- Threshold/policy drift

### 1.5 Dependency Addition

**TRIGGER**: Before adding new external dependencies

**REQUIRED PROMPT**:
> To implement `<feature>`, I can:
> 
> **Option A**: Add dependency `<package>` — `<pros/cons>`  
> **Option B**: Implement in-house — `<pros/cons>`  
> **Option C**: Use existing `<alternative>` — `<pros/cons>`  
> 
> Which approach?

**EXAMPLES**:
- New PyPI package
- New system dependency
- New MCP server
- New external API

### 1.6 File/Module Deletion

**TRIGGER**: Before deleting any production file

**REQUIRED PROMPT**:
> File `<path>` can be handled as:
> 
> **Option A**: Delete immediately — `<references>` migrated, `<deprecation_period>` elapsed  
> **Option B**: Deprecate first — add deprecation warning, set 90-day timer  
> **Option C**: Keep as shim — redirect to `<replacement>`, document in shim registry  
> **Option D**: Cancel deletion — `<reason>`  
> 
> Which approach?

**EXAMPLES**:
- Agent deletion (§1.6 requirements)
- Utility module consolidation
- Dead code removal
- Test file cleanup

### 1.7 Configuration Changes

**TRIGGER**: Before modifying governance/policy configuration

**REQUIRED PROMPT**:
> Configuration `<config_file>` can be updated as:
> 
> **Option A**: `<change>` — affects `<scope>`  
> **Option B**: `<change>` — affects `<scope>`  
> **Option C**: Keep current — `<reason>`  
> 
> Which option?

**EXAMPLES**:
- Confidence thresholds
- Retry limits
- Timeout values
- Layer boundary rules

### 1.8 Error Handling Strategy

**TRIGGER**: When implementing error handling with multiple valid approaches

**REQUIRED PROMPT**:
> Error `<error_type>` can be handled as:
> 
> **Option A**: Fail-closed — raise immediately, no fallback  
> **Option B**: Fail-open with logging — log + continue with degraded behavior  
> **Option C**: Retry with backoff — `<retry_config>`  
> **Option D**: Escalate to user — prompt for manual intervention  
> 
> Which strategy?

**EXAMPLES**:
- External API failures
- Missing configuration
- Invalid user input
- Resource exhaustion

### 1.9 Performance Optimization Trade-offs

**TRIGGER**: When optimization involves correctness/complexity trade-offs

**REQUIRED PROMPT**:
> Performance can be improved via:
> 
> **Option A**: `<optimization>` — `<speedup>`, `<complexity_increase>`  
> **Option B**: `<optimization>` — `<speedup>`, `<complexity_increase>`  
> **Option C**: Keep current — prioritize simplicity  
> 
> Which approach?

**EXAMPLES**:
- Caching strategies
- Batch processing
- Parallel execution
- Index optimization

### 1.10 ADG Regeneration Timing

**TRIGGER**: After code changes that may affect ADG

**REQUIRED PROMPT**:
> ADG may be stale after these changes. I can:
> 
> **Option A**: Regenerate now — blocks current work for ~30s  
> **Option B**: Defer to end of session — faster now, risk of stale analysis  
> **Option C**: Skip — changes don't affect dependency graph  
> 
> Which timing?

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
