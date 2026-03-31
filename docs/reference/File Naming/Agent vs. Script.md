╔══════════════════════════════════════════════════════════════════════════════════════════════════════╗
║ ARCHITECTURE DECISION: SCRIPT vs. AGENT (INTEGRATING LIBRARIAN PERSONA SYSTEM)                       ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════╝

┌──────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ ✦ THE CORE DISTINCTION                                                                               │
│                                                                                                      │
│ SCRIPT: Coordinates work (The Maintenance Crew / Closing Checklist).                                 │
│ AGENT:  Performs governed reasoning about work (The Trained Reference Librarian).                    │
├──────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ ✦ CRITICAL CLARIFICATION                                                                             │
│                                                                                                      │
│ In this codebase, "Agent" does NOT imply LLM-powered autonomy. It defines a deterministic class      │
│ with encapsulated business logic, statefulness, repeatable outputs, and stable contracts.            │
└──────────────────────────────────────────────────────────────────────────────────────────────────────┘

┌───────────────────┬──────────────────────────────────────┬───────────────────────────────────────────┐
│ FEATURE           │ SCRIPT                               │ AGENT CLASS                               │
├───────────────────┼──────────────────────────────────────┼───────────────────────────────────────────┤
│ CONCEPT           │ One-shot procedural step             │ Encapsulated logic & state object         │
│ METAPHOR          │ Maintenance Crew / Checklist         │ Trained Librarian / Subject Expert        │
│ LIFECYCLE         │ Runs, completes, exits               │ Instantiated, reused across flows         │
│ PURPOSE           │ Orchestrate tasks                    │ Own a specific domain responsibility      │
│ ROLE              │ Execute batch, CLI, CI/CD            │ Classify, validate, heal, enforce policy  │
│ STRUCTURE         │ Procedural functions (snake_case)    │ Class with methods (PascalCase)           │
│ STATE             │ Stateless (no memory of prior runs)  │ Stateful (tracks items, errors, stats)    │
│ FLOW MODEL        │ Linear (Start → Process → Exit)      │ Iterative (Instantiate → Assess → Return) │
│ DECISION LOGIC    │ Fixed ("do steps 1-5 in order")      │ Encapsulated ("apply rule/policy")        │
│ DETERMINISM       │ Always deterministic                 │ Deterministic OR adaptive (synthesis)     │
│ REUSABILITY       │ Low (Standalone executable)          │ High (Imported by orchestrators/scripts)  │
│ ERROR BEHAVIOR    │ Fail step → stop/exit (no authority) │ Detect → log/heal/escalate/continue       │
│ INVOCATION        │ `python script.py`                   │ `agent = Agent(); agent.validate()`       │
│ DIRECTORIES       │ ops_scripts/, tools/, scripts/       │ reasoning/, validators/, enforcement/     │
│ FILE NAMING       │ {verb}_{noun}.py                     │ {Purpose}Agent.py                         │
│ CODE EXAMPLES     │ tools/generate_full_adg.py           │ FileClassificationAgent.py                │
└───────────────────┴──────────────────────────────────────┴───────────────────────────────────────────┘

╔══════════════════════════════════════════════════════════════════════════════════════════════════════╗
║ DECISION TREE: WHEN TO CREATE WHICH?                                                                 ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════╝

    [ START: NEW COMPONENT ]
               │
               ▼
  1. REUSABILITY: Will other modules import this logic? ───────── YES ──┐
               │                                                        │
               NO                                                       │
               │                                                        │
               ▼                                                        │
  2. STATE: Does it need instance state across many items? ────── YES ──┤
               │                                                        │
               NO                                                       │
               │                                                        │
               ▼                                                        │
  3. LOGIC: Is it enforcing rules, not just sequencing? ───────── YES ──┤
               │                                                        │
               NO                                                       │
               │                                                        ▼
               ▼                                              ╔═══════════════════╗
       ┌───────────────┐                                      ║    AGENT CLASS    ║
       │    SCRIPT     │                                      ╚═══════════════════╝
       └───────────────┘                                      • reasoning/ dir
       • ops_scripts/ dir                                     • PascalCase.py
       • snake_case.py                                        • Reusable logic
       • One-off automation                                   • Stateful healing
       • CI/CD pipeline step                                  • Rule enforcement

┌──────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ THE DETERMINISTIC AGENT PARADIGM                                                                     │
├─────────────────────────────────────────────┬────────────────────────────────────────────────────────┤
│ WHAT AN AGENT IS NOT REQUIRED TO BE:        │ WHAT AN AGENT ABSOLUTELY MUST BE:                      │
│                                             │                                                        │
│ ✗ LLM reasoning dependent                   │ ✓ Encapsulated (Class-bound business logic)            │
│ ✗ Self-prompting / Goal-seeking             │ ✓ Responsible (Single domain authority)                │
│ ✗ Adaptive / Autonomous                     │ ✓ Reusable (Importable across contexts)                │
│ ✗ Multi-strategy selection                  │ ✓ Contractual (Standardized interface methods)         │
│ ✗ Feedback-loop driven                      │ ✓ Stateful (Maintains instance variables)              │
├─────────────────────────────────────────────┴────────────────────────────────────────────────────────┤
│ KEY INSIGHT: Most agents in this codebase are DETERMINISTIC (AST analysis, Regex, Rule engine).      │
│ This is correct and preferable for reproducibility, high performance, and strict testability.        │
└──────────────────────────────────────────────────────────────────────────────────────────────────────┘

╔══════════════════════════════════════════════════════════════════════════════════════════════════════╗
║ ARCHITECTURE ENFORCEMENT RULES (Via FileClassificationAgent)                                         ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ 1. AGENT LOCATION REGULATION:                                                                        ║
║    Any file defining `class *Agent:` MUST reside in a `reasoning/` subfolder. Split if necessary.    ║
║                                                                                                      ║
║ 2. SCRIPT DIRECTORY PURITY:                                                                          ║
║    `scripts/` is exclusively for CLI entrypoints and procedural one-offs.                            ║
║    FORBIDDEN in `scripts/`: PascalCase filenames, Agent classes, `test_*.py`.                        ║
║                                                                                                      ║
║ 3. STRICT STRUCTURAL DISCIPLINE:                                                                     ║
║    • Agents:  `agentic_core/L{N}/reasoning/` or `apps_{domain}/reasoning/`                           ║
║    • Scripts: `ops_scripts/`, `tools/`, or app-level `scripts/`                                      ║
║    • Tests:   `tests/` hierarchy MUST strictly mirror the production folder structure.               ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════╝