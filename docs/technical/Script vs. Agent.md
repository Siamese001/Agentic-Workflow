SCRIPT                                           AGENT CLASS
======                                           ===========


STRUCTURE                                        STRUCTURE
---------                                        ---------

Procedural functions                             Class with methods
snake_case naming                                PascalCase naming
generate_full_adg.py                             FileClassificationAgent.py
agent_validation.py                              HierarchyValidatorAgent.py

librarian analogy:                               librarian analogy:
maintenance crew script                          trained librarian role


LOCATION                                         LOCATION
--------                                         --------

ops_scripts/                                     reasoning/
tools/                                           validators/
scripts/                                         enforcement/

librarian analogy:                               librarian analogy:
procedure manual in the                          librarian's desk in the
operations office                                reference section


INVOCATION                                       INVOCATION
----------                                       ----------

python script.py                                 agent = Agent()
Direct CLI execution                             agent.validate()
One-off run                                      agent.heal()

librarian analogy:                               librarian analogy:
run the closing checklist                        call the reference librarian
once and exit                                    for help (reusable service)


FLOW MODEL                                       FLOW MODEL
----------                                       ----------

start                                            instantiate
  │                                                │
  ▼                                                ▼
step 1: scan files                               scan environment
  │                                                │
  ▼                                                ▼
step 2: process each                             for each item:
  │                                                │
  ▼                                                ├─ classify
step 3: write output                              ├─ validate
  │                                                ├─ detect violations
  ▼                                                └─ apply rules
end                                                │
                                                   ▼
                                                 return results

librarian analogy:                               librarian analogy:
follow printed procedure:                        trained librarian applies
1. lock doors                                    professional judgment to
2. count cash drawer                             each patron request using
3. file paperwork                                catalog rules, policies,
4. exit                                          and experience


STATE + MEMORY                                   STATE + MEMORY
--------------                                   --------------

No state between runs                            Maintains instance state
Each run is independent                          Tracks violations, stats
No memory of previous execution                  Prevents duplicate processing

librarian analogy:                               librarian analogy:
clerk follows laminated card                     librarian remembers which
with no memory of yesterday                      books were already checked


DECISION LOGIC                                   DECISION LOGIC
--------------                                   --------------

Fixed procedure                                  Encapsulated business logic
No branching logic                               Rule-based classification
Linear execution                                 Deterministic OR adaptive

librarian analogy:                               librarian analogy:
"do steps 1-5 in order"                          "assess the request, then
                                                 apply the appropriate catalog
                                                 rule, policy, or procedure"


DETERMINISM                                      DETERMINISM
-----------                                      -----------

Always deterministic                             Can be deterministic OR adaptive
Same input → same output
                                                 DETERMINISTIC AGENT:
                                                 - AST-based validation
                                                 - Regex pattern matching
                                                 - Rule engine classification
                                                 - Same input → same output

                                                 ADAPTIVE AGENT:
                                                 - LLM-powered reasoning
                                                 - Multi-strategy selection
                                                 - Feedback loops
                                                 - May vary by context

librarian analogy:                               librarian analogy:
checkout procedure never changes                 DETERMINISTIC: catalog lookup
                                                 rules (always same result)

                                                 ADAPTIVE: research question
                                                 requiring synthesis and
                                                 judgment (may vary)


REUSABILITY                                      REUSABILITY
-----------                                      -----------

Standalone executable                            Imported as module
Not imported by other code                       Called from multiple contexts
Single-purpose automation                        Reusable component

librarian analogy:                               librarian analogy:
one-time maintenance task                        librarian available for
                                                 repeated consultations


ERROR BEHAVIOR                                   ERROR BEHAVIOR
--------------                                   --------------

step fails → script stops                        violation detected → log and continue
                                                 OR
                                                 violation detected → heal and track

librarian analogy:                               librarian analogy:
if step 2 breaks, clerk stops                    if one book is misfiled,
because no authority to adapt                    note it and continue auditing
                                                 the rest of the shelf


═══════════════════════════════════════════════════════════════════════════════
CODEBASE EXAMPLES
═══════════════════════════════════════════════════════════════════════════════

SCRIPT: tools/generate_full_adg.py
--------------------------------------
- Procedural functions: generate_full_adg(), build_snapshot()
- Run via: python tools/generate_full_adg.py
- Purpose: Generate ADG artifacts once
- No class, no state between runs
- Linear execution: scan → build → write → exit


AGENT: agentic_core/L5_safety/reasoning/FileClassificationAgent.py
-------------------------------------------------------------------
- Class: FileClassificationAgent
- Methods: validate_layer_alignment(), heal_repository(), classify_file()
- Imported by: ops_scripts/ci/agent_validation.py, execute_ssot.py
- Purpose: Reusable file validation and healing logic
- Maintains state: self.stats, self.processed_paths, self.violations
- Deterministic: AST parsing + regex rules (no LLM, no adaptation)


SCRIPT: ops_scripts/ci/agent_validation.py
-------------------------------------------
- Procedural functions: run_code_deduplication_check(), main()
- Run via: python ops_scripts/ci/agent_validation.py
- Purpose: CI/CD validation gate
- Instantiates agents but is itself a script
- Linear execution: import agents → run checks → exit with code


AGENT: agentic_core/L5_safety/validators/HierarchyValidatorAgent.py
--------------------------------------------------------------------
- Class: HierarchyValidatorAgent
- Methods: validate_structure(), scan_root_violations()
- Deterministic: Directory structure rules
- Reusable: Called from multiple healing workflows


═══════════════════════════════════════════════════════════════════════════════
NAMING CONVENTIONS (Enforced by FileClassificationAgent)
═══════════════════════════════════════════════════════════════════════════════

SCRIPT FILES                                     AGENT FILES
------------                                     -----------

Pattern: {verb}_{noun}.py                        Pattern: {Purpose}Agent.py
Case: snake_case                                 Case: PascalCase

Examples:                                        Examples:
  generate_full_adg.py                             FileClassificationAgent.py
  agent_validation.py                              HierarchyValidatorAgent.py
  adg_redis_ingest.py                              CodeDeduplicationAgent.py
  fix_imports.py                                   ArchitectureGovernorAgent.py

FORBIDDEN:                                       FORBIDDEN:
  ✗ PascalCase in scripts/                         ✗ snake_case for Agent classes
  ✗ GenerateAdg.py                                 ✗ file_classification_agent.py
  ✗ Agent classes in ops_scripts/                  ✗ Agent classes in ops_scripts/


═══════════════════════════════════════════════════════════════════════════════
WHEN TO CREATE WHICH?
═══════════════════════════════════════════════════════════════════════════════

Create a SCRIPT when:                            Create an AGENT CLASS when:
---------------------                            -----------------------

✓ One-off automation task                        ✓ Reusable validation logic
✓ CI/CD pipeline step                            ✓ Stateful healing process
✓ CLI tool                                       ✓ Business rule enforcement
✓ Orchestrating other components                ✓ Complex classification logic
✓ Direct execution needed                        ✓ Multiple call sites need it
✓ No state between runs                          ✓ Encapsulated responsibility

Example: "Generate ADG once" → script            Example: "Validate files" → agent
Example: "Run tests in CI" → script              Example: "Heal hierarchy" → agent
Example: "Fix imports batch" → script            Example: "Classify file types" → agent


═══════════════════════════════════════════════════════════════════════════════
KEY INSIGHT: AGENTS CAN BE DETERMINISTIC
═══════════════════════════════════════════════════════════════════════════════

The term "Agent" does NOT require:
  ✗ LLM reasoning
  ✗ Feedback loops
  ✗ Multi-strategy selection
  ✗ Adaptive behavior
  ✗ Goal-seeking autonomy

The term "Agent" DOES require:
  ✓ Encapsulation (business logic in a class)
  ✓ Responsibility (single, well-defined purpose)
  ✓ Reusability (imported and used across contexts)
  ✓ Interface contract (standard methods)
  ✓ Statefulness (maintains instance variables)

Most agents in this codebase are DETERMINISTIC:
  - AST-based analysis
  - Regex pattern matching
  - Rule engine classification
  - Policy enforcement
  - Same input → same output

This is CORRECT and often PREFERABLE for:
  - Reproducibility
  - Performance
  - Testability
  - Predictability
  - Cost efficiency


═══════════════════════════════════════════════════════════════════════════════
ENFORCEMENT
═══════════════════════════════════════════════════════════════════════════════

FileClassificationAgent enforces these rules:

AGENT SUFFIX WINS SUBFOLDER
  Any file containing "class *Agent:" MUST reside in reasoning/ subfolder
  Split files if needed: config stays in config/, Agent moves to reasoning/

SCRIPTS PURITY
  scripts/ may contain CLI entrypoints and one-off scripts ONLY
  FORBIDDEN: PascalCase filenames, Agent classes, test_*.py files

LOCATION DISCIPLINE
  Agents: agentic_core/L{N}/reasoning/ or apps_{domain}/reasoning/
  Scripts: ops_scripts/, tools/, or app-level scripts/
  Tests: tests/ hierarchy matching production structure
