# Test Failure Decision Tree

**Purpose**: Classify test failures into repair classes before making any code edits.

**Location**: Referenced by `.windsurf/rules/adg-repair-discipline.md` and `.windsurf/rules/.windsurfrules` §2.5

---

## The 5-Check Decision Tree

### Check 1: Should this module exist in the architecture?

**Question**: Is the failing test referencing a module that SHOULD exist per the architecture?

- **YES** → `production_bug_fix`  
  The module is required but broken. Fix the implementation.
  
- **NO** → Proceed to Check 2

**Examples**:
- Test imports `agentic_core.L2_execution.cid_registry` → should exist → `production_bug_fix`
- Test imports `legacy_module_deprecated` → should NOT exist → Check 2

---

### Check 2: Is the import path wrong?

**Question**: Is the test using a stale or incorrect import path?

- **YES** → `stale_reference_fix`  
  The symbol/path exists but the import is wrong. Correct the reference.
  
- **NO** → Proceed to Check 3

**Examples**:
- `from agentic_core.utils import X` but `X` moved to `agentic_core.shared.utils` → `stale_reference_fix`
- Import path is correct but behavior wrong → Check 3

---

### Check 3: Is an error supposed to happen here?

**Question**: Does the test expect success but the code should actually raise an error?

- **YES** → `production_bug_fix`  
  The code should raise an error but doesn't, or raises wrong error type. Ensure correct error is raised.
  
- **NO** → Proceed to Check 4

**Examples**:
- Test expects `None` return but code should raise `ValueError` for invalid input → `production_bug_fix`
- Test expects specific error message but gets generic one → `production_bug_fix`

---

### Check 4: Is the test too strict about wording?

**Question**: Is the test failing only because of string matching (error message wording, formatting) rather than semantic behavior?

- **YES** → `broken_test_fix`  
  Relax the regex/assertion while preserving semantic equivalence. **Weakening error type or removing assertions is FORBIDDEN.**
  
- **NO** → Proceed to Check 5

**Examples**:
- Test asserts `error_message == "File not found"` but actual is `"File not found: /path/to/file"` → `broken_test_fix` (relax to substring match)
- Test asserts wrong exception type → NOT a `broken_test_fix`, go back to Check 3

**CRITICAL**: Semantic equivalence MUST be preserved. You may only:
- Relax string matching (substring instead of exact)
- Update expected values to match new canonical behavior
- Adjust tolerance in numeric comparisons

You may NOT:
- Change `assert raises(ValueError)` to `assert raises(Exception)`
- Remove assertions entirely
- Broaden mocks to bypass validation

---

### Check 5: Did the architecture contract legitimately change?

**Question**: Has the intended behavior or contract changed for valid architectural reasons?

- **YES (Governance)** → `policy_regression_fix`  
  The change affects governance semantics (fail-closed vs fail-open, approval logic, thresholds, routing). Document in `## POLICY_DRIFT` section.
  
- **YES (Production Logic)** → `production_bug_fix`  
  The contract changed and code is correct. Update test expectations.
  
- **NO** → **BLOCKED**  
  Do NOT create fake modules or stub files to silence the failure. Fix the test expectation or the code.

**Examples**:
- Confidence threshold increased from 0.7 to 0.9 for security → `policy_regression_fix`
- New required field added to API contract → `production_bug_fix`
- Test expects old behavior that was intentionally changed → `production_bug_fix` (update test)

---

## Repair Class Taxonomy

| Class | When to Use | Evidence Section Required |
|-------|-------------|---------------------------|
| `production_bug_fix` | Defect in production logic | `## FAILURE_CAPTURE`, `## DEPENDENCY_GRAPH` |
| `stale_reference_fix` | Symbol/path/import no longer canonical | `## DEPENDENCY_GRAPH` with edge path |
| `broken_test_fix` | Defect inside test itself (semantic equivalence preserved) | `## FAILURE_CAPTURE` |
| `policy_regression_fix` | Governance/policy drift (fail-closed, thresholds, routing) | `## POLICY_DRIFT`, `## CONTRACT_CONFLICT` if applicable |
| `environment_contract_fix` | Subprocess, WSL, CUDA, import path, CI vs local mismatch | `## ENVIRONMENT_CONTRACT` |

---

## Forbidden Patterns

**NEVER**:
- Classify a governance bug as `production_bug_fix` (use `policy_regression_fix`)
- Patch assertion to match broken behavior
- Adjust threshold to make test pass without architectural approval
- Create fake modules or stub files to silence failures

**ALWAYS**:
- Record repair class in commit message footer: `repair_class: <class>`
- Include exact cluster ID: `Fix cluster C7A3B2: <description>`
- Write `ADG_REPAIR_LITMUS` section before any edit

---

## Quick Reference Flowchart

```
Start: Test Failing
    |
    v
Check 1: Module should exist? 
    |--YES--> production_bug_fix
    |--NO---> Check 2
    v
Check 2: Wrong import path?
    |--YES--> stale_reference_fix
    |--NO---> Check 3
    v
Check 3: Error should happen?
    |--YES--> production_bug_fix
    |--NO---> Check 4
    v
Check 4: Test too strict?
    |--YES--> broken_test_fix (preserve semantic equivalence!)
    |--NO---> Check 5
    v
Check 5: Contract changed?
    |--YES (Governance)--> policy_regression_fix
    |--YES (Logic)-----> production_bug_fix
    |--NO--------------> BLOCKED (do not fake modules)
```

---

## See Also

- `.windsurf/rules/adg-repair-discipline.md` — ADG-controlled repair loop
- `.windsurf/rules/.windsurfrules` §2.5 — Repair classification and evidence requirements
- `.windsurf/rules/hitl-enforcement.md` §1.4 — Test modification strategy HITL prompt
