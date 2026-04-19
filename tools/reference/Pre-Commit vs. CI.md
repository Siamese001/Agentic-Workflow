DEVELOPER MACHINE → CI SERVER FLOW
==================================


edit code                    → author writes manuscript pages
   │
   ▼
git add                      → place manuscript pages into submission folder
   │
   ▼
git commit                   → author submits draft to local editor
   │
   ▼
PRE-COMMIT HOOKS             → local editorial pre-check
   │
   │ fast checks             → quick editorial inspection
   │ - lint                  → spelling rules check
   │ - formatting            → formatting guidelines check
   │ - syntax check          → grammar inspection
   │ - quick unit tests      → quick fact verification
   │
   ▼
✔ commit accepted locally    → manuscript passes local editor review
   │
   │
   │ ───────── PUSH BOUNDARY ─────────
   │        (local work finished)
   │        (manuscript sent to publisher)
   │
   ▼
git push                     → manuscript delivered to publishing house
   │
   ▼
CI PIPELINE TRIGGER          → publisher intake process starts
   │
   ▼
CI VALIDATION                → full publisher editorial review
   │
   │ heavy checks            → deep publisher validation
   │ - full pytest suite     → full manuscript review
   │ - ADG rebuild           → rebuild master catalog index
   │ - dependency graph validation → verify cross-book references
   │ - architecture validation → verify book structure standards
   │ - determinism replay tests → simulate reprint consistency
   │ - security scans        → legal / compliance review
   │
   ▼
CI RESULT                    → publisher decision
   │
   ├─ ✔ merge allowed        → book approved for printing
   │
   └─ ✖ build fails          → manuscript rejected for corrections
