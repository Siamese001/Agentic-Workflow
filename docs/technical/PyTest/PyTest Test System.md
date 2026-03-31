PYTEST TEST SYSTEM
(Indented to show hierarchy + relationships)

REPOSITORY
│
│ Analogy: Library building
│
└── pytest
    │
    │ Analogy: Head librarian coordinating all book inspections
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
        │ Analogy: Library shelves containing books to inspect
        │
        └── Test Functions
            │
            │ Example
            │ def test_add():
            │
            │ Analogy: A librarian inspecting one specific book
            │
            └── Code Execution
                │
                │ result = add(2,3)
                │
                │ Analogy: The librarian reads the book and compares it to records
                │
                └── Assertions
                    │
                    │ Example
                    │ assert result == 5
                    │
                    │ Analogy: Catalog verification rule
                    │ "book contents must match the official catalog record"
                    │
                    ├── TRUE
                    │     │
                    │     └── PASS
                    │         Analogy: book matches catalog perfectly
                    │
                    └── FALSE
                          │
                          └── FAIL
                              Analogy: book record does not match catalog


EXECUTION FLOW

pytest
  └── discovers test files
        └── runs test functions
              └── executes code
                    └── evaluates assertions
                          ├── true  → PASS
                          └── false → FAIL