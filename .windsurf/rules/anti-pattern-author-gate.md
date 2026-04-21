---
trigger: model_decision
description: Use this rule before introducing any new anti-pattern instance (bare except, shell=True, subprocess without timeout, or similar) to enforce the Author-Gate approval gate.
---

> **Cascade always-on discipline:** Keep this file lean and invariant-focused. Put durable boundaries, routing cues, and non-negotiable standards here. Move long procedures, examples, templates, and execution playbooks into skills or workflows.
>
> **Cascade retrieval discipline:** When this rule affects research or synthesis, prefer local-first retrieval, exact or structural matches before broad semantic search, and evidence or quote extraction before final synthesis on high-risk tasks.
>
> **Cascade enforcement split:** Advisory guidance lives here, but deterministic blocking, fail-closed checks, and audit capture belong in hooks and scripts rather than prompt prose.

# Anti-Pattern Author-Gate Gate

## Constitutional Rule

**ALL new anti-pattern violations MUST receive explicit Human-In-The-Loop (Author-Gate) approval before commit.**

## Scope

This rule applies to:
- `magic_configuration` - Hard-coded configuration values
- `silent_swallower` - Exception handlers that suppress errors without logging
- `global_mutation` - Global state modifications
- `direct_prompt_compilation` - Direct prompt string construction
- `config_with_logic` - Configuration files containing business logic
- `path_fragility` - Hard-coded file paths

## Enforcement Protocol

### 1. Pre-Commit Detection
The ADG burndown gate (`T3a: ADG Anti-Pattern Burndown Ratchet`) automatically detects new anti-pattern violations during pre-commit hooks.

### 2. Author-Gate Approval Required
When new violations are detected:
1. **STOP** - Do not bypass or override the gate
2. **DOCUMENT** - Explain why the anti-pattern is necessary
3. **REQUEST** - Explicitly ask the user for approval
4. **JUSTIFY** - Provide alternatives considered and why they were rejected

### 3. Guardian Comments
After Author-Gate approval is granted, add guardian comments to whitelist the violation:

```python
# guardian: allow-magic_configuration
# guardian: allow-silent-swallow
# guardian: allow-global-mutation
```

**Format Requirements:**
- Use hyphens, not underscores: `allow-silent-swallow` NOT `allow-silent_swallower`
- Place at module level (after docstring, before imports)
- One comment per pattern type

### 4. Commit Message Documentation
Include in commit message:
```
Author-Gate-APPROVED: <count> new anti-pattern violations
- <file>: <pattern> (<count>) - <justification>
```

## Forbidden Actions

1. **NEVER** add guardian comments without explicit user approval
2. **NEVER** bypass the ADG burndown gate by:
   - Modifying the ratchet ceiling
   - Disabling the pre-commit hook
   - Committing with `--no-verify`
3. **NEVER** use generic justifications like "needed for functionality"

## Approval Protocol - Cascade Interactive Prompt (STAR Format)

When the ADG burndown gate detects new anti-pattern violations, Cascade MUST use the `ask_user_question` tool to present an interactive approval prompt with pros/cons for each option and a ⭐ recommendation.

### Implementation

```python
ask_user_question(
    question="ADG Burndown Gate detected {count} new anti-pattern violations. Review options and select approach?",
    options=[
        {
            "label": "Approve All",
            "description": "Accept all {count} violations and add guardian comments. Pros: Unblocks immediate work, fast resolution. Cons: Increases technical debt, may hide real issues. ⭐ RECOMMENDED if violations are unavoidable and well-documented."
        },
        {
            "label": "Reject All",
            "description": "Revert changes - no anti-patterns allowed. Pros: Maintains code quality, zero new debt. Cons: Work blocked until alternative implementation found. ⭐ RECOMMENDED if alternatives exist."
        },
        {
            "label": "Review Details",
            "description": "Show detailed breakdown before deciding. Pros: Informed decision with full context. Cons: Takes additional time. ⭐ RECOMMENDED for first-time or complex violations."
        },
        {
            "label": "Approve Selectively",
            "description": "Choose which violations to accept. Pros: Balanced approach, only necessary violations approved. Cons: Requires careful review of each violation."
        }
    ],
    allowMultiple=False
)
```

### Response Handling

**If "Approve All":**
1. Add guardian comments to all affected files
2. Commit with `Author-Gate-APPROVED:` prefix in commit message
3. Document violations in commit body

**If "Reject All":**
1. `git reset --hard HEAD` to revert all changes
2. Inform user that changes were reverted
3. Suggest alternative implementation approaches

**If "Review Details":**
1. Present detailed breakdown of each violation:
   - File path
   - Pattern type and count
   - Code snippets showing violations
   - Technical justification
   - Alternatives considered
   - Mitigation strategies
2. After review, present "Approve All" / "Reject All" options again

**If "Approve Selectively":**
1. Present each file as a separate toggle option
2. User selects which files to approve
3. Revert unapproved files
4. Add guardian comments only to approved files
5. Commit approved changes

### Detailed Breakdown Format

When "Review Details" is selected, present:

```
## Anti-Pattern Violations - Detailed Review

**File:** {file_path}
**Pattern:** {pattern_type} ({count} occurrences)

**Why needed:**
{technical_justification}

**Code example:**
```python
{code_snippet}
```

**Alternatives considered:**
1. {alternative_1} → Rejected: {reason}
2. {alternative_2} → Rejected: {reason}

**Mitigation:**
{how_risk_is_reduced}

---
```

### Forbidden Actions

1. **NEVER** present approval as plain text "yes/no" question
2. **NEVER** assume approval without interactive prompt
3. **NEVER** add guardian comments before user selects "Approve"
4. **NEVER** commit with `--no-verify` to bypass the gate

## Rationale

Anti-patterns create technical debt and maintenance burden. Author-Gate approval ensures:
1. **Conscious decisions** - No accidental anti-patterns slip through
2. **Documentation** - Justifications are recorded
3. **Accountability** - Clear ownership of technical debt
4. **Ratchet discipline** - Ceiling only decreases, never increases

## Integration Points

- `.pre-commit-config.yaml` - T3a hook enforces ratchet
- `ops_scripts/ci/_adg_burndown_gate.py` - Gate implementation
- `.windsurf/rules/constitutional.md` - Constitutional authority
- This file - Procedural enforcement

## See Also

- `docs/architecture/ADG_BURNDOWN_DISCIPLINE.md` - Full burndown strategy
- `.windsurf/rules/constitutional.md` - Constitutional rules
