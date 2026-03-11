PYTEST TEST SYSTEM
(Indented to show hierarchy + relationships)

REPOSITORY
│
│ Analogy: Hospital building
│
└── pytest
    │
    │ Analogy: Head doctor coordinating all patient exams
    │
    │ Responsibilities
    │ • discovers tests
    │ • runs tests
    │ • collects results
    │ • reports failures
    │
    └── Test Files
        │
        │ Example: test_math.py
        │
        │ Analogy: Medical procedure sheets
        │
        └── Test Functions
            │
            │ Example
            │ def test_add():
            │
            │ Analogy: A specific medical exam
            │
            └── Code Execution
                │
                │ result = add(2,3)
                │
                │ Analogy: Performing the exam
                │
                └── Assertions
                    │
                    │ Example
                    │ assert result == 5
                    │
                    │ Analogy: Diagnostic rule
                    │ "expected medical result must match measurement"
                    │
                    ├── TRUE
                    │     │
                    │     └── PASS
                    │         Analogy: patient exam normal
                    │
                    └── FALSE
                          │
                          └── FAIL
                              Analogy: diagnosis mismatch


EXECUTION FLOW

pytest
  └── discovers test files
        └── runs test functions
              └── executes code
                    └── evaluates assertions
                          ├── true  → PASS
                          └── false → FAIL