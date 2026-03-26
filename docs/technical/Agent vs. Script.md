=========================================================================================================================================================================
ARCHITECTURE DECISION: SCRIPT vs. AGENT (INTEGRATING LIBRARIAN PERSONA SYSTEM)
=========================================================================================================================================================================

┌───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ ✦ SHARPEST DISTINCTION                                                                                                                                                │
│   SCRIPT coordinates work (The Maintenance Crew / Closing Checklist).                                                                                                 │
│   AGENT performs governed reasoning about work (The Trained Reference Librarian).                                                                                     │
├───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ ✦ IMPORTANT CLARIFICATION                                                                                                                                             │
│   "Agent" in this codebase does NOT mean LLM-powered or autonomous. It is a deterministic class with encapsulated logic, stable method contracts, instance state,     │
│   and repeatable outputs.                                                                                                                                             │
└───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

=========================================================================================================================================================================
COMPARISON MATRIX
=========================================================================================================================================================================

FEATURE               SCRIPT                                                         AGENT CLASS
-------------------   ------------------------------------------------------------   ----------------------------------------------------------------------------------
CONCEPT               One-shot procedural step                                       Reusable object with encapsulated logic & state
METAPHOR              Maintenance crew script / closing checklist                    Trained librarian role / subject matter expert
LIFECYCLE             Runs, completes, exits                                         Instantiated, called repeatedly, reused across flows
PURPOSE               Orchestrate tasks                                              Own a specific domain responsibility
ROLE                  Execute batch, CLI, CI/CD                                      Classify, validate, heal, enforce policy
STRUCTURE             Procedural functions (snake_case)                              Class with methods (PascalCase)
STATE                 Stateless across runs (no memory of previous run)              Stateful (tracks items, violations, stats, deduplication)
FLOW MODEL            Linear sequence (Start → Scan → Process → Write → Exit)        Iterative (Instantiate → for each: Classify/Validate/Heal → Return)
DECISION LOGIC        Fixed procedure ("do steps 1-5 in order")                      Encapsulated business logic ("assess request, apply rule/policy")
DETERMINISM           Always deterministic (Same input → same output)                Can be deterministic (catalog rules) OR adaptive (research synthesis)
REUSABILITY           Low (Standalone executable, one entrypoint)                    High (Imported by scripts, orchestrators, validators)
ERROR BEHAVIOR        Fail step → stop / exit > 0 (clerk stops, no authority)        Detect → log/heal/continue/escalate (librarian notes misfiled book, continues)
INVOCATION            `python script.py`                                             `agent = Agent(); agent.validate()`
DIRS                  ops_scripts/, tools/, scripts/                                 reasoning/, validators/, enforcement/
FILE NAMING           {verb}_{noun}.py (e.g., generate_full_adg.py)                  {Purpose}Agent.py (e.g., FileClassificationAgent.py)
CODEBASE EXAMPLES     tools/generate_full_adg.py, ci/agent_validation.py             reasoning/FileClassificationAgent.py, validators/HierarchyValidatorAgent.py

=========================================================================================================================================================================
DECISION TREE: WHEN TO CREATE WHICH?
=========================================================================================================================================================================

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
        (snake_case.py)                                  (Reusable logic)
        (One-off automation)                             (Stateful healing)
        (CI/CD pipeline step)                            (Rule enforcement)

=========================================================================================================================================================================
KEY INSIGHT: AGENTS CAN BE DETERMINISTIC
=========================================================================================================================================================================

The term "Agent" DOES NOT require:                      The term "Agent" DOES require:
✗ LLM reasoning                                         ✓ Encapsulation (business logic in a class)
✗ Feedback loops                                        ✓ Responsibility (single, well-defined purpose)
✗ Multi-strategy selection                              ✓ Reusability (imported and used across contexts)
✗ Adaptive behavior                                     ✓ Interface contract (standard methods)
✗ Goal-seeking autonomy                                 ✓ Statefulness (maintains instance variables)

Most agents in this codebase are DETERMINISTIC (AST analysis, Regex, Rule engine). This is CORRECT and PREFERABLE for reproducibility, performance, and testability.

=========================================================================================================================================================================
ENFORCEMENT RULES (Via FileClassificationAgent)
=========================================================================================================================================================================

1. AGENT SUFFIX WINS SUBFOLDER: Any file containing "class *Agent:" MUST reside in reasoning/ subfolder. Split files if needed.
2. SCRIPTS PURITY: scripts/ may contain CLI entrypoints and one-off scripts ONLY. FORBIDDEN: PascalCase filenames, Agent classes, test_*.py files.
3. LOCATION DISCIPLINE:
   - Agents: agentic_core/L{N}/reasoning/ or apps_{domain}/reasoning/
   - Scripts: ops_scripts/, tools/, or app-level scripts/
   - Tests: tests/ hierarchy matching production structure.
=========================================================================================================================================================================