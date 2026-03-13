REPOSITORY
│                                                  ANALOGY
│                                                  Library Building
│
├────────────────────────────────────────────────────────────────────────────────────────────
│ FILE LAYER (physical files in the repo)
├────────────────────────────────────────────────────────────────────────────────────────────
│
├─ hierarchy_validator.py        │ ANALOGY: Inspection Librarian (checks if books are shelved correctly)
│
├─ hierarchy_healer.py           │ ANALOGY: Repair Librarian (re-shelves books placed in the wrong section)
│
└─ hierarchy_agent_healer.py     │ ANALOGY: Front Desk Librarian (receives problem report and routes it to repair)



│
├────────────────────────────────────────────────────────────────────────────────────────────
│ CODE STRUCTURE (what exists inside each file)
├────────────────────────────────────────────────────────────────────────────────────────────
│
├─ hierarchy_validator.py        │ ANALOGY: Inspection Librarian
│     │
│     └── class HierarchyValidatorAgent
│            │
│            └── validate_structure()      │ checks the catalog against the shelves
│
│
├─ hierarchy_healer.py           │ ANALOGY: Repair Librarian
│     │
│     └── class HierarchyAgent
│            │
│            ├── scan_root_violations()    │ walks library aisles looking for misplaced books
│            │
│            └── heal_hierarchy()          │ re-shelves books to the correct section
│
│
└─ hierarchy_agent_healer.py     │ ANALOGY: Front Desk Librarian
      │
      └── heal_hierarchy_violations()
             (wrapper function)           │ receives incident ticket and calls repair librarian



│
├────────────────────────────────────────────────────────────────────────────────────────────
│ ARCHITECTURE ROLES (what the code means in the system)
├────────────────────────────────────────────────────────────────────────────────────────────
│
├─ HierarchyValidatorAgent       │ ANALOGY: Inspection Librarian
│
│     role: VALIDATOR
│     responsibility: detect structural violations in the repository hierarchy
│
│
├─ HierarchyAgent                │ ANALOGY: Repair Librarian
│
│     role: HEALING SERVICE
│     responsibility: correct directory / hierarchy violations
│
│
└─ heal_hierarchy_violations()   │ ANALOGY: Front Desk Librarian
│
      role: ORCHESTRATION ADAPTER
      responsibility: expose a clean callable entrypoint for healers



│
├────────────────────────────────────────────────────────────────────────────────────────────
│ RUNTIME EXECUTION FLOW
├────────────────────────────────────────────────────────────────────────────────────────────
│
│ pre_commit  →  validate  →  violation detected  →  heal
│
│
│         VALIDATION PHASE
│               │
│               ▼
│   HierarchyValidatorAgent
│   │ ANALOGY: Inspection librarian checks the shelves
│               │
│        produces violation report
│               │
│               ▼
│
│           HEAL PHASE
│               │
│               ▼
│   heal_hierarchy_violations()
│   │ ANALOGY: Front desk receives repair ticket
│               │
│               ▼
│   HierarchyAgent
│   │ ANALOGY: Repair librarian fixes the shelving
│               │
│               ▼
│        heal_hierarchy()



│
├────────────────────────────────────────────────────────────────────────────────────────────
│ TAXONOMY CLASSIFICATION
├────────────────────────────────────────────────────────────────────────────────────────────
│
│ hierarchy_validator.py        │ ANALOGY: Inspection Librarian
│
│   file_type: VALIDATOR
│   execution_phase: VALIDATE
│   capability_contract: STRUCTURE_VERIFICATION
│
│
│ hierarchy_healer.py           │ ANALOGY: Repair Librarian
│
│   file_type: SERVICE
│   execution_phase: HEAL
│   capability_contract: STRUCTURE_REPAIR
│
│
│ hierarchy_agent_healer.py     │ ANALOGY: Front Desk Librarian
│
│   file_type: ADAPTER
│   execution_phase: HEAL
│   capability_contract: ORCHESTRATION_ENTRYPOINT



│
├────────────────────────────────────────────────────────────────────────────────────────────
│ COMPLETE RELATIONSHIP
├────────────────────────────────────────────────────────────────────────────────────────────
│
│        REPOSITORY                              │ ANALOGY: Library
│             │
│             ▼
│            FILE                                │ ANALOGY: Library department
│             │
│             ▼
│           CLASS                                │ ANALOGY: Librarian role
│             │
│             ▼
│      ARCHITECTURAL ROLE                        │ ANALOGY: Job responsibility
│  (Validator / Service / Adapter)
│             │
│             ▼
│       EXECUTION PHASE                          │ ANALOGY: Library workflow stage
│ (validate → repair)
│
