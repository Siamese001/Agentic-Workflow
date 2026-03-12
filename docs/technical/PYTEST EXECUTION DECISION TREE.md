PYTEST EXECUTION DECISION TREE (LIBRARIAN / BOOK ANALOGY)
=========================================================

pytest start
(the librarian begins the daily library inspection)

    │
    ▼
collect test files
(the librarian gathers all books that must be inspected)

    │
    ▼
collect test functions
(each inspection checklist inside each book is identified)

    │
    ▼
for each test
(the librarian picks up one book to inspect)

    │
    ▼
check environment / dependencies
(the librarian checks if required reference books or catalogs exist)

    │
    ├── dependency missing
    │       │
    │       ▼
    │     SKIPPED
    │     (required reference book is missing so inspection cannot be done)
    │
    ├── skip marker condition true
    │       │
    │       ▼
    │     SKIPPED
    │     (this book is marked "do not inspect under current conditions")
    │
    ▼
run setup / fixtures
(the librarian prepares the inspection desk and opens the book)

    │
    ├── setup crash
    │       │
    │       ▼
    │     ERROR
    │     (the book cannot even be opened because it is damaged)
    │
    ▼
execute test body
(the librarian reads the contents of the book)

    │
    ├── pytest.skip() triggered
    │       │
    │       ▼
    │     SKIPPED
    │     (the librarian stops inspection because a rule says it should not continue)
    │
    ├── unexpected exception
    │       │
    │       ▼
    │     ERROR
    │     (pages are corrupted or unreadable during inspection)
    │
    ▼
evaluate assertions
(the librarian checks the book against the official catalog checklist)

    │
    ├── assertion failed
    │       │
    │       ▼
    │     FAIL
    │     (the book does not match the catalog record)
    │
    └── assertion passed
            │
            ▼
          PASS
          (the book matches the catalog perfectly)