PYTEST EXECUTION LIFECYCLE (THE LIBRARIAN'S DAILY INSPECTION)
=============================================================

[START] pytest
(The librarian begins the daily library inspection)
  │
  ▼
[COLLECT] Test Files & Functions
(The librarian gathers all books and identifies their inspection checklists)
  │
  ├─ Check Environment & Dependencies (Are reference catalogs available?)
  │  ├─ Dependency missing ──────▶ [SKIPPED] (Cannot inspect without references)
  │  └─ Skip marker condition ───▶ [SKIPPED] (Marked: "Do not inspect currently")
  │
  ▼ SUCCESS: Found & Valid
  │
[SETUP] Run Fixtures
(The librarian prepares the desk and attempts to open the book)
  │
  ├─ Setup crash / exception ────▶ [ERROR] (Book's cover is glued shut; cannot start)
  │
  ▼ SUCCESS: Setup complete
  │
[EXECUTE] Run Test Body
(The librarian reads the contents of the book)
  │
  ├─ pytest.skip() triggered ────▶ [SKIPPED] (A rule inside says to stop reading)
  │
  ├─ Unexpected exception ───────▶ [FAIL] (Pages are corrupted or unreadable)
  │
  ▼ SUCCESS: Execution finishes
  │
[EVALUATE] Assertions
(The librarian checks the book's contents against the official catalog)
  │
  ├─ Assertion failed ───────────▶ [FAIL] (The book contains the wrong information)
  │
  ▼ SUCCESS: Assertion passed
  │
[PASS] (The book matches the catalog perfectly)