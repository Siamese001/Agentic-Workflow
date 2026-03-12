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