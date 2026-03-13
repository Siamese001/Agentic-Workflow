# Test Failure Triage Decision Tree

This decision tree provides the canonical protocol for triaging test failures. It aligns with `.windsurfrules` §2.5 repair classification taxonomy and §1.2 test quality standards.

## Decision Tree

```
TEST FAILURE
│
├─ Check 1: Should this module exist in the architecture?
│  │
│  ├─ YES → Missing module that should exist
│  │        ├─ Code: Create the module
│  │        ├─ Test: None
│  │        ├─ Repair Class: production_bug_fix
│  │        └─ Analogy: Catalog entry exists, but the book was never placed on the shelf
│  │
│  └─ NO
│     │
│     ├─ Check 2: Is the import path wrong?
│     │  │
│     │  ├─ YES → Wrong import path
│     │  │        ├─ Code: Correct the import path
│     │  │        ├─ Test: None
│     │  │        ├─ Repair Class: stale_reference_fix
│     │  │        └─ Analogy: Librarian searched the wrong aisle
│     │  │
│     │  └─ NO
│     │     │
│     │     ├─ Check 3: Is an error supposed to happen here?
│     │     │  │
│     │     │  ├─ YES → Expected error path
│     │     │  │        ├─ Code: Ensure correct error is raised
│     │     │  │        ├─ Test: Verify correct error type
│     │     │  │        ├─ Repair Class: production_bug_fix
│     │     │  │        └─ Analogy: Library system intentionally blocks access to a restricted book
│     │     │  │
│     │     │  └─ NO
│     │     │     │
│     │     │     ├─ Check 4: Is the test too strict about wording?
│     │     │     │  │
│     │     │     │  ├─ YES → Brittle error regex
│     │     │     │  │        ├─ Code: None
│     │     │     │  │        ├─ Test: Relax regex or assertion (ONLY if semantic equivalence preserved)
│     │     │     │  │        ├─ Repair Class: broken_test_fix
│     │     │     │  │        ├─ FORBIDDEN: Weakening assertion strictness or removing failure detection
│     │     │     │  │        ├─ VALID: Changing match="Value must be positive integer" to match="must be positive"
│     │     │     │  │        ├─ INVALID: Changing pytest.raises(ValueError) to pytest.raises(Exception)
│     │     │     │  │        └─ Analogy: Inspector demanding exact wording of warning sign
│     │     │     │  │
│     │     │     │  └─ NO
│     │     │     │     │
│     │     │     │     ├─ Check 5: Did the architecture contract legitimately change?
│     │     │     │     │  │
│     │     │     │     │  ├─ YES → Architecture contract changed
│     │     │     │     │  │        ├─ Code: Implement new behavior if missing
│     │     │     │     │  │        ├─ Test: Update tests to match new contract
│     │     │     │     │  │        ├─ Repair Class: policy_regression_fix (if governance) OR production_bug_fix (if logic)
│     │     │     │     │  │        └─ Analogy: Library updated catalog rules, but the inspection checklist is old
│     │     │     │     │  │
│     │     │     │     │  └─ NO → Fake module created to silence failure
│     │     │     │     │           ├─ Code: Do NOT create fake module
│     │     │     │     │           ├─ Test: Fix test expectation
│     │     │     │     │           ├─ Status: BLOCKED - Anti-pattern detected
│     │     │     │     │           └─ Analogy: Adding a fake book so the catalog check passes
```

## Repair Classification Mapping

Per `.windsurfrules` §2.5, every repair must be labeled with exactly one class:

| Check | Outcome | Repair Class |
|-------|---------|--------------|
| 1 YES | Missing module that should exist | `production_bug_fix` |
| 2 YES | Wrong import path | `stale_reference_fix` |
| 3 YES | Expected error path | `production_bug_fix` |
| 4 YES | Brittle error regex | `broken_test_fix` |
| 5 YES (governance) | Architecture contract changed | `policy_regression_fix` |
| 5 YES (logic) | Architecture contract changed | `production_bug_fix` |
| 5 NO | Fake module anti-pattern | **BLOCKED** |

## Critical Constraints

### Check 4: Brittle Error Regex

When relaxing test assertions, you MUST preserve semantic equivalence:

**ALLOWED:**
- Changing exact error message wording when the error type and meaning are unchanged
- Generalizing overly specific regex patterns that match the same semantic contract
- Example: `match="Value must be positive integer"` → `match="must be positive"`

**FORBIDDEN (per §1.2, §5.4 gate #8):**
- Weakening error type specificity: `ValueError` → `Exception`
- Removing error message matching entirely
- Changing `strict=True` to `strict=False`
- Removing assertions
- Adding `assert True` or pass-only bodies
- Broadening mocks without corresponding assertions

### Check 5 NO: Anti-Pattern Detection

If you reach this path, **STOP**. Do not create fake modules, empty implementations, or stub files to make tests pass. This violates:
- `.windsurfrules` §1.2 test quality gates
- `.windsurfrules` §1.3 test-first discipline
- `.windsurfrules` §2.5 repair classification (no valid class exists for this action)

**Correct action:** Fix the test expectation to match actual architectural reality.

## Evidence Requirements

When using this decision tree, document in evidence:
1. Which check path was followed
2. Repair class assigned
3. For Check 4: Proof that semantic equivalence is preserved
4. For Check 5 YES: Whether governance or logic contract changed
5. For Check 5 NO: Why the module should not exist (architectural justification)
