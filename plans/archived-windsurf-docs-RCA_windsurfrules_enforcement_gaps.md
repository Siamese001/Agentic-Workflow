---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\RCA_windsurfrules_enforcement_gaps.md'
original_relative_path: 'RCA_windsurfrules_enforcement_gaps.md'
source_sha256: 96d73d1df40eb4338fb5aa9bae70203be0cd9ea949993dfecc4cb2575b4dd69f
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-09'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# RCA: Why .windsurfrules Is Not Followed 100% Every Turn in Cascade

**Date:** 2026-03-09
**Severity:** CRITICAL - Constitutional Enforcement Gap
**Status:** ACTIVE INVESTIGATION

## Executive Summary

`.windsurfrules` contains 438 lines of constitutional rules with `trigger: always_on`, yet Cascade does not enforce these rules with 100% reliability every turn. This RCA identifies the architectural gaps between rule declaration and runtime enforcement.

## Root Cause Analysis

### 1. **Cascade Is Not a Repository-Native Enforcement System**

**Issue:** Cascade is an external AI assistant that receives `.windsurfrules` as **context injection**, not as **executable constraints**.

**Evidence:**
- `.windsurfrules` is located at `c:\Git\Agentic-Workflow\.windsurf\rules\.windsurfrules`
- The file has `trigger: always_on` frontmatter (lines 1-3)
- Cascade receives this as part of `<user_rules>` in system prompt
- **BUT**: Cascade processes rules as **guidance**, not as **hard constraints**

**Problem:**
```
Rule Declaration (SSOT) ≠ Runtime Enforcement (Cascade)
```

Cascade's architecture:
1. Receives rules as text in system prompt
2. Uses LLM reasoning to interpret rules
3. **No formal verification** that rules are followed
4. **No runtime enforcement layer** that blocks violations
5. **No post-action validation** that checks compliance

### 2. **LLM Non-Determinism vs. Deterministic Rule Requirements**

**Issue:** `.windsurfrules` demands deterministic behavior (§3.3, §1.3, §1.7), but Cascade is an LLM with inherent non-determinism.

**Evidence from `.windsurfrules`:**
```
§1.3 Deterministic tests only
§1.7 Deterministic decision surfaces
§3.3 Deterministic analysis
- Code analysis MUST use AST detailed parsing by default.
- Regex or grep for structural logic is FORBIDDEN unless explicitly stated by user.
- No randomness in deterministic surfaces.
```

**Problem:**
- LLM token sampling is probabilistic
- Different turns may interpret same rule differently
- Context window limitations may truncate rules
- Attention mechanisms may not weight all rules equally

**Architectural Mismatch:**
```
Deterministic Rules → Non-Deterministic Executor = Probabilistic Compliance
```

### 3. **No Pre-Action or Post-Action Validation Gates**

**Issue:** Cascade lacks enforcement checkpoints that validate rule compliance before/after actions.

**What's Missing:**
- **Pre-action gate:** No validation that proposed action complies with rules
- **Post-action gate:** No verification that completed action followed rules
- **Rollback mechanism:** No automatic revert when violation detected

**Evidence:**
- Repository has L5 safety enforcement (`agentic_core/L5_safety/enforcement/`)
- Repository has validators (`agentic_core/L5_safety/validators/`)
- **BUT**: These are Python modules for repository code, not Cascade action validators

**Gap:**
```
.windsurfrules (438 lines) → Cascade Actions → No Validation Layer
```

### 4. **Context Window Prioritization**

**Issue:** Cascade receives massive context (workspace layout, memories, MCP servers, IDE metadata) that may dilute rule attention.

**Evidence from system prompt structure:**
1. Tool definitions (100+ tools)
2. Communication style guidelines
3. MCP server descriptions (12 servers)
4. Workspace layout (full directory tree)
5. User rules (`.windsurfrules` + `plan-location.md`)
6. Retrieved memories
7. IDE metadata
8. User request

**Problem:**
- Rules compete with other context for attention
- Later context (user request) may override earlier context (rules)
- Token budget limits may truncate rules in long conversations

### 5. **Rule Specificity vs. Execution Complexity**

**Issue:** Some rules are highly specific (e.g., "PowerShell invocation is forbidden" §2.1), but Cascade must translate these into complex multi-step actions.

**Example Violation Pattern:**
- **Rule:** "All plans MUST reside in `docs/reports/plans/`" (§8)
- **Cascade Behavior:** May save to `.windsurf/plans/` due to IDE system guidance
- **Root Cause:** IDE system guidance conflicts with user rules

**Evidence:**
- `RCA_windsurf_plans_violation.md` documents this exact violation
- System planning guidance instructed: `C:\Users\amita\.windsurf\plans\`
- User rule requires: `docs/reports/plans/`
- **Conflict Resolution:** Cascade chose system guidance over user rule

**Architectural Gap:**
```
System Guidance (IDE) vs. User Rules (.windsurfrules) = Undefined Precedence
```

### 6. **No Automated Rule Compliance Testing**

**Issue:** Repository has extensive test infrastructure (pytest, evidence contracts, CI gates), but **no tests that verify Cascade follows .windsurfrules**.

**Evidence:**
- `tests/` directory has 16+ subdirectories
- CI workflows in `.github/workflows/` (17 YAML files)
- **BUT**: No test suite that validates Cascade action compliance

**What's Missing:**
```python
def test_cascade_follows_plan_location_rule():
    """Verify Cascade saves plans to docs/reports/plans/."""
    # Simulate Cascade creating a plan
    # Assert plan path matches DOCS_REPORTS_PLANS constant
    # Fail if plan saved to .windsurf/plans/ or external path
```

### 7. **Memory System May Contradict Rules**

**Issue:** Cascade has access to retrieved memories that may conflict with current rules.

**Evidence:**
- System-retrieved memory states: "ALL plans MUST be saved to `docs/reports/plans/`"
- This memory is **correct** and aligns with rules
- **BUT**: If stale/incorrect memories exist, they could override rules

**Risk:**
```
Stale Memory (outdated rule) > Current Rule (.windsurfrules) = Violation
```

## Impact Assessment

### Observed Violations

1. **Plan Location Violations** (§8)
   - Plans saved to `C:\Users\amita\.windsurf\plans\` instead of `docs/reports/plans/`
   - Documented in `RCA_windsurf_plans_violation.md`

2. **PowerShell Usage** (§2.1)
   - Rule: "PowerShell invocation is forbidden"
   - Repository has `powershell_ban.py` scanner to detect violations
   - Implies violations occurred that necessitated scanner creation

3. **Test Skipping** (§1.12)
   - Rule: "Zero-tolerance for test skipping"
   - Repository has pytest integrity skill (`pytest-integrity/`)
   - Implies test deselection issues occurred

### Severity Classification

| Rule Category | Severity | Enforcement Gap |
|--------------|----------|-----------------|
| Testing & Evidence (§1) | CRITICAL | No pre-action test validation |
| Evidence Contract (§2) | HIGH | No evidence format validation |
| Scope & Determinism (§3) | HIGH | No scope contamination detection |
| Architecture Locks (§4) | CRITICAL | No layer violation prevention |
| CI & Contract Gates (§5) | MEDIUM | CI runs post-commit, not pre-action |
| Execution Modality (§6) | MEDIUM | No phase boundary enforcement |
| Acceptance Discipline (§7) | HIGH | No acceptance criteria validation |
| Artifact Location (§8) | CRITICAL | No path validation before write |

## Remediation Recommendations

### Immediate Actions

#### 1. **Create Pre-Action Validation Layer**

Add validation before Cascade writes files:

```python
# agentic_core/L5_safety/enforcement/cascade_action_validator.py

def validate_file_write(target_path: Path) -> ValidationResult:
    """Validate file write complies with .windsurfrules §8."""
    # Check against DOCS_REPORTS_PLANS constant
    # Check against PROJECT_ROOT_WHITELIST
    # Block writes outside sovereign territories
    pass
```

#### 2. **Enhance User Rules with Enforcement Hooks**

Modify `.windsurfrules` to include validation references:

```markdown
## §8. ARTIFACT LOCATION

All plans, evidence, and reports MUST reside in:

`docs/reports/plans/`

**Enforcement:** `agentic_core.L5_safety.utils.validate_path_ssot_util.validate_path`
**Validator:** Pre-commit hook + Cascade action gate
```

#### 3. **Add Post-Action Compliance Audit**

Create skill that audits Cascade actions:

```bash
# .windsurf/skills/rule-compliance-audit/

## Audit Cascade Action Compliance

After each Cascade turn:
1. Check git diff for new files
2. Validate paths against PROJECT_ROOT_WHITELIST
3. Scan for PowerShell usage in new evidence files
4. Verify test count matches collection count
```

### Long-Term Solutions

#### 1. **Formal Rule Specification Language**

Replace prose rules with machine-readable constraints:

```yaml
# .windsurf/rules/constraints.yaml
constraints:
  - id: PLAN_LOCATION
    type: path_constraint
    rule: "plans MUST match pattern: docs/reports/plans/*.md"
    validator: agentic_core.L5_safety.utils.validate_path_ssot_util
    severity: CRITICAL
    auto_block: true
```

#### 2. **Cascade Action Wrapper**

Intercept all Cascade tool calls with validation layer:

```python
def cascade_tool_wrapper(tool_name: str, **kwargs):
    """Wrap Cascade tool calls with rule validation."""
    # Pre-action validation
    validate_against_windsurfrules(tool_name, kwargs)

    # Execute action
    result = execute_tool(tool_name, **kwargs)

    # Post-action validation
    verify_compliance(tool_name, result)

    return result
```

#### 3. **Rule Compliance Dashboard**

Track Cascade rule compliance over time:

```
docs/reports/telemetry/cascade_compliance.json
{
  "total_turns": 1000,
  "rule_violations": 23,
  "compliance_rate": 0.977,
  "violations_by_rule": {
    "§8_ARTIFACT_LOCATION": 15,
    "§2.1_POWERSHELL_BAN": 5,
    "§1.12_TEST_SKIPPING": 3
  }
}
```

## Prevention Measures

### 1. **Rule Priority Declaration**

Add precedence hierarchy to `.windsurfrules`:

```markdown
# RULE PRECEDENCE

When conflicts arise:
1. .windsurfrules (this file) = HIGHEST AUTHORITY
2. plan-location.md (supplementary rules)
3. System guidance (IDE, Cascade defaults)
4. Retrieved memories (if not contradictory)

User rules ALWAYS override system guidance.
```

### 2. **Cascade Self-Audit Prompt**

Add to system prompt:

```
Before executing any action:
1. Review relevant .windsurfrules sections
2. Verify action complies with all applicable rules
3. If conflict detected, STOP and ask user for clarification
4. Document rule compliance in action explanation
```

### 3. **Automated Rule Regression Tests**

```python
# tests/cascade_compliance/test_windsurfrules_compliance.py

def test_plan_location_rule_compliance():
    """Verify all plans in git history are in docs/reports/plans/."""
    plans = find_all_markdown_files_with_plan_in_name()
    for plan in plans:
        assert plan.is_relative_to(DOCS_REPORTS_PLANS)

def test_no_powershell_in_evidence():
    """Verify no PowerShell usage in evidence files."""
    violations = scan_repository_for_powershell(PROJECT_ROOT)
    assert len(violations) == 0
```

## Lessons Learned

1. **Context Injection ≠ Enforcement**
   - Rules in system prompt are guidance, not constraints
   - Need validation layer to convert rules into hard blocks

2. **LLM Non-Determinism Requires Deterministic Guards**
   - Cannot rely on LLM to perfectly follow rules every turn
   - Must add deterministic validation gates

3. **System Guidance Can Override User Rules**
   - IDE system guidance may conflict with user rules
   - Need explicit precedence hierarchy

4. **No Tests = No Guarantees**
   - Without compliance tests, violations go undetected
   - Need automated regression tests for rule compliance

5. **Post-Hoc Detection Is Too Late**
   - Discovering violations after commit is costly
   - Need pre-action validation to prevent violations

## References

- **Rules Source:** `c:\Git\Agentic-Workflow\.windsurf\rules\.windsurfrules`
- **Plan Location Rule:** `c:\Git\Agentic-Workflow\.windsurf\rules\plan-location.md`
- **Previous Violation:** `docs/reports/plans/RCA_windsurf_plans_violation.md`
- **SSOT Definition:** `agentic_core/L5_safety/config/structure_blueprint_config.py`
- **PowerShell Scanner:** `agentic_core/L5_safety/static_checks/powershell_ban.py`
- **Path Validator:** `agentic_core/L5_safety/utils/validate_path_ssot_util.py`

## Status

🔴 **ACTIVE** - Architectural gap identified, remediation in progress
⚠️ **ACTION REQUIRED** - Implement pre-action validation layer
📊 **TRACKING** - Monitor compliance rate across future Cascade turns

---

## Appendix: Architectural Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ Cascade AI Assistant (External)                             │
│                                                              │
│ ┌──────────────────────────────────────────────────────┐   │
│ │ System Prompt Context                                 │   │
│ │ - Tool definitions                                    │   │
│ │ - Communication guidelines                            │   │
│ │ - User rules (.windsurfrules) ← GUIDANCE ONLY        │   │
│ │ - Workspace layout                                    │   │
│ │ - Retrieved memories                                  │   │
│ │ - User request                                        │   │
│ └──────────────────────────────────────────────────────┘   │
│                          ↓                                   │
│ ┌──────────────────────────────────────────────────────┐   │
│ │ LLM Reasoning (Non-Deterministic)                     │   │
│ │ - Interprets rules probabilistically                  │   │
│ │ - May prioritize recent context over rules            │   │
│ │ - No formal verification                              │   │
│ └──────────────────────────────────────────────────────┘   │
│                          ↓                                   │
│ ┌──────────────────────────────────────────────────────┐   │
│ │ Tool Calls (write_to_file, edit, etc.)               │   │
│ │ ❌ NO PRE-ACTION VALIDATION                          │   │
│ │ ❌ NO RULE COMPLIANCE CHECK                          │   │
│ └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ Repository (c:\Git\Agentic-Workflow)                        │
│                                                              │
│ ┌──────────────────────────────────────────────────────┐   │
│ │ L5 Safety Layer (Python Modules)                      │   │
│ │ - powershell_ban.py (scanner)                         │   │
│ │ - validate_path_ssot_util.py (validator)              │   │
│ │ - structure_blueprint_config.py (SSOT)                │   │
│ │ ✅ ENFORCES RULES FOR PYTHON CODE                    │   │
│ │ ❌ DOES NOT VALIDATE CASCADE ACTIONS                 │   │
│ └──────────────────────────────────────────────────────┘   │
│                                                              │
│ ┌──────────────────────────────────────────────────────┐   │
│ │ CI/CD Gates (Post-Commit)                             │   │
│ │ - pytest                                              │   │
│ │ - evidence contract checker                           │   │
│ │ - tooling boundary checker                            │   │
│ │ ⚠️ RUNS AFTER COMMIT (TOO LATE)                      │   │
│ └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘

ENFORCEMENT GAP:
┌─────────────────────────────────────────────────────────────┐
│ .windsurfrules (438 lines, trigger: always_on)              │
│           ↓                                                  │
│ ❌ NO RUNTIME ENFORCEMENT LAYER                             │
│           ↓                                                  │
│ Cascade Actions (Probabilistic Compliance)                  │
└─────────────────────────────────────────────────────────────┘
```

## Conclusion

`.windsurfrules` is not followed 100% every turn because:

1. **Architectural Gap:** Rules are context, not constraints
2. **No Validation Layer:** No pre-action or post-action compliance checks
3. **LLM Non-Determinism:** Probabilistic reasoning cannot guarantee deterministic compliance
4. **Conflicting Guidance:** System prompts may override user rules
5. **No Compliance Testing:** No automated tests verify Cascade follows rules

**Fix:** Implement pre-action validation layer that blocks non-compliant actions before execution.

## Violation

[Describe the violation or issue that triggered this RCA]

---

## Corrective Actions

[List the corrective actions taken to resolve the issue]

---

