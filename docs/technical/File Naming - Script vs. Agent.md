REPOSITORY
│                                                          ANALOGY
│                                                          Library System
│
├────────────────────────────────────────────────────────────────────────────
│ CASE 1 — NO AGENT (JUST SCRIPTS)
│
│ Files contain procedural logic only.
│
├─ hierarchy_validator.py        │ ANALOGY: Librarian manually checking shelves
│
├─ hierarchy_healer.py           │ ANALOGY: Librarian manually re-shelving books
│
└─ run_hierarchy_fix.py          │ ANALOGY: Front desk telling librarian to fix shelves
│
│
│ CODE STRUCTURE
│
├─ hierarchy_validator.py
│     │
│     └── validate_structure()
│         │ ANALOGY: librarian scans shelves for misplaced books
│
├─ hierarchy_healer.py
│     │
│     └── heal_hierarchy()
│         │ ANALOGY: librarian re-shelves misplaced books
│
└─ run_hierarchy_fix.py
      │
      └── main()
          │ ANALOGY: front desk receives complaint and calls librarian



├────────────────────────────────────────────────────────────────────────────
│ CASE 2 — AGENT ARCHITECTURE
│
│ Files contain agent classes and orchestration adapters.
│
├─ hierarchy_validator_agent.py     │ ANALOGY: Inspection Librarian
│
├─ hierarchy_healer_agent.py        │ ANALOGY: Repair Librarian
│
└─ hierarchy_agent_healer.py        │ ANALOGY: Front desk routing desk
│
│
│ CODE STRUCTURE
│
├─ hierarchy_validator_agent.py
│     │
│     └── class HierarchyValidatorAgent
│            └── validate_structure()
│            │ ANALOGY: inspection librarian audits shelves
│
├─ hierarchy_healer_agent.py
│     │
│     └── class HierarchyHealerAgent
│            └── heal_hierarchy()
│            │ ANALOGY: repair librarian fixes shelving
│
└─ hierarchy_agent_healer.py
      │
      └── heal_hierarchy_violations()
             │ ANALOGY: front desk opens repair ticket and calls repair librarian



├────────────────────────────────────────────────────────────────────────────
│ KEY DIFFERENCE
│
│ SCRIPT SYSTEM
│
│ validate() → heal()
│
│ ANALOGY
│ One librarian does everything manually
│
│
│ AGENT SYSTEM
│
│ ValidatorAgent → HealerAgent → Adapter
│
│ ANALOGY
│ Specialized librarians coordinated by a front desk
│
