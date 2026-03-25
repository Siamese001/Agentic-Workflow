╔════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                  ARCHITECTURE DECISION: SCRIPT vs. AGENT                                   ║
╠═════════════════════════════════════════════╦══════════════════════════════════════════════════════════════╣
║                   SCRIPT                    ║                         AGENT CLASS                          ║
╟─────────────────────────────────────────────╫──────────────────────────────────────────────────────────────╢
║ CONCEPT     One-shot procedural step        ║ Reusable object with encapsulated logic & state              ║
║ METAPHOR    Closing checklist / glue        ║ Reference librarian / subject matter expert                  ║
║ LIFECYCLE   Runs, completes, exits          ║ Instantiated, called repeatedly, reused across flows         ║
╟─────────────────────────────────────────────╫──────────────────────────────────────────────────────────────╢
║ PURPOSE     Orchestrate tasks               ║ Own a specific domain responsibility                         ║
║ ROLE        Execute batch, CLI, CI/CD       ║ Classify, validate, heal, enforce policy                     ║
╟─────────────────────────────────────────────╫──────────────────────────────────────────────────────────────╢
║ STRUCTURE   Functions (snake_case.py)       ║ Class + methods (PascalCaseAgent.py)                         ║
║ STATE       Stateless across runs           ║ Stateful (tracks items, violations, stats, deduplication)    ║
║ FLOW MODEL  Linear sequence (A → B → Exit)  ║ Iterative (Inspect → Decide → Apply → Track → Return)        ║
║ ERRORS      Fail step → stop / exit > 0     ║ Detect → record / heal / continue / escalate                 ║
╟─────────────────────────────────────────────╫──────────────────────────────────────────────────────────────╢
║ INVOCATION  `python script.py`              ║ `agent = FileAgent(); agent.validate()`                      ║
║ REUSABILITY Low (One entrypoint)            ║ High (Imported by scripts, orchestrators, validators)        ║
╟─────────────────────────────────────────────╫──────────────────────────────────────────────────────────────╢
║ DIRS        ops_scripts/, tools/, scripts/  ║ reasoning/, validators/, enforcement/                        ║
║ EXAMPLES    generate_full_adg.py            ║ FileClassificationAgent.py, HierarchyValidatorAgent.py       ║
╚═════════════════════════════════════════════╩══════════════════════════════════════════════════════════════╝

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ ✦ SHARPEST DISTINCTION                                                                                     │
│   SCRIPT coordinates work.                                                                                 │
│   AGENT performs governed reasoning about work.                                                            │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ ✦ IMPORTANT CLARIFICATION                                                                                  │
│   "Agent" in this codebase does NOT mean LLM-powered or autonomous. It is a deterministic class with       │
│   encapsulated logic, stable method contracts, instance state, and repeatable outputs.                     │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

DECISION TREE
=============

      [ START: NEW COMPONENT ]
                 │
                 ▼
    1. REUSABILITY: Will other modules ─────────── YES ───────────┐
       import and reuse this logic?                               │
                 │                                                │
                NO                                                │
                 │                                                │
                 ▼                                                │
    2. STATE: Does it need instance ────────────── YES ───────────┤
       state across many items?                                   │
                 │                                                │
                NO                                                │
                 │                                                │
                 ▼                                                │
    3. LOGIC: Is it enforcing rules ────────────── YES ───────────┤
       rather than just sequencing?                               │
                 │                                                │
                NO                                                │
                 │                                                ▼
                 ▼                                       ┏━━━━━━━━━━━━━━━━━━━┓
        ┏━━━━━━━━━━━━━━━━━━┓                             ┃    AGENT CLASS    ┃
        ┃      SCRIPT      ┃                             ┗━━━━━━━━━━━━━━━━━━━┛
        ┗━━━━━━━━━━━━━━━━━━┛                             (reasoning/ dir)
        (ops_scripts/ dir)                               (PascalCase.py)
        (snake_case.py)
