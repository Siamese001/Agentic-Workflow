
-----

### Resume Generation Pipeline (v16.32 - Merged Agentic Flow)

```
.
                              +-------------------------------------------------------------------------+
                              | 📚 "THE LIBRARIAN" (Nightly Research Agent)                             |
                              |   (RAG Agent)                                                           |
                              |                                                                         |
                              |   **WHO:** The "domain expert" agent that works offline.                |
                              |   **WHAT:** Build a persistent vector memory of high-signal company intel.|
                              |   **HOW:** Runs deep RAG (`WebSearchTool`) & embeds results via [🧠 ChromaDB].  |
                              |   **WHERE:** `rag_RES.py` (Class: `LibrarianAgent`)        |
                              +-------------------------------------------------------------------------+
                                                                 |
                                                                 v
                                             [ 🧠 agent_memory_db (ChromaDB) ]
                                 (Persistent Vector Store @ /cache/chroma_memory)
                                                                 ^
                                                                 | (READS)
+----------------------------------------------------------------+----------------------------------------------------------------+
| 🧑‍💻 "THE CLIENT" (User)                                            | 📐 "THE ARCHITECT" (Static Configuration - "The Blueprints")    |
|                                                                |                                                                |
|   (Provides the initial `job_input.json`) |   (This is NOT an agent. It is the passive data               |
|                                                                |    that all agents read to know *what* to do.)                 |
|                                                                |                                                                |
|                                                                | • `artist_specs.json` (Writer's Blueprint)  
|                                                                | • `artist_constraints.json` (Writer's Rules)
|                                                                | • `validator_rules.json` (Inspector's Rules)
|                                                                | • `prompts.json` (LLM Scripts)            
|                                                                | • `master_resume.json` (Archivist's Source) 
+------------------+---------------------------------------------+----------------------------------+-----------------------------+
                   |                                                                                 | (READS)
                   v                                                                                 v
+------------------+---------------------------------------------------------------------------------+-----------------------------+
| 👷 "THE FOREMAN" (Agent Orchestrator)                                                          |
|   (The `while` loop in `execute_workflow`)                                                                           |
|   **WHO:** The central orchestrator that manages the "Crew of Agents."                                                         |
|   **WHAT:** Execute the 8-HOP sequential workflow, manage state, and catch loops.                      |
|   **HOW:** Calls hop functions and **catches `GateDecision.HALT` to trigger loops.** |
|   **WHERE:** `workflow_RES.py` (Class: `WorkflowOrchestrator`)                                        |
+--------------------------------------------------+-----------------------------------------------------------------------------+
   |                                                 |
   +<-- (Catches [🔥 FactualFailureException] from HOP-5) <----+
   |                                                 |
   +<-- (Catches [♻️ CreativeFailure HALT] from HOP-6) <--------------------------------------------------------------------------+
                                                   |                                                                             |
                                                   v                                                                             |
+------------------+-------------------------------+-----------------------------------------------------------------------------+  |
| 🕵️‍♂️ **HOP-0: "THE RESEARCHER" Agent** |  |
|                                                                                                                              |  |
|   **WHO:** The team's intelligence analyst.                                                                                  |  |
|   **WHAT:** Analyze the JD & company to create a "Mission Brief" (`ThematicAnalysis`).                        |  |
|   **HOW:** Queries [🧠 ChromaDB] & runs 4-phase [🌐 WebSearchRAG].                                            |  |
|   **WHERE:** `rag_RES.py` (Class: `EnhancedJobDescriptionAnalyzer`)                                           |  |
|                                                                                                                              |  |
|   ➡️ **Output:** `[run_id]_HOP-0_ThematicAnalysis.json` |  |
+--------------------------------------------------+-----------------------------------------------------------------------------+  |
                                                   |                                                                             |
                                                   v                                                                             |
+------------------+-------------------------------+-----------------------------------------------------------------------------+  |
| 🗄️ **HOP-1: "THE ARCHIVIST" Agent** |  |
|                                                                                                                              |  |
|   **WHO:** The data entry clerk for the candidate's assets.                                                                    |  |
|   **WHAT:** Read `master_resume.json` and convert it into a standard internal format.                   |  |
|   **HOW:** Parses `professional_experience[].bullet_pool` into a standard `List[Dict]`.                 |  |
|   **WHERE:** `workflow_RES.py` (Class: `ClerkExtractor`)                                                |  |
|                                                                                                                              |  |
|   ➡️ **Output:** `[run_id]_HOP-1_ExtractedData.json` |  |
+--------------------------------------------------+-----------------------------------------------------------------------------+  |
                                                   |                                                                             |
                                                   v                                                                             |
+------------------+-------------------------------+-----------------------------------------------------------------------------+  |
| 🏷️ **HOP-2: "THE INDEXER" Agent** |  |
|                                                                                                                              |  |
|   **WHO:** The data enricher and cataloger.                                                                                    |  |
|   **WHAT:** Add metadata (`canonical_verbs`) and check for internal redundancy.                        |  |
|   **HOW:** Runs `DuplicateDetector` (which uses [🐍 sklearn]) for similarity checks.        |  |
|   **WHERE:** `workflow_RES.py` (Class: `DataEnricher`)                                                  |  |
|                                                                                                                              |  |
|   ➡️ **Output:** `[run_id]_HOP-2_EnrichedScaffold.json` |  |
+--------------------------------------------------+-----------------------------------------------------------------------------+  |
                                                   |                                                                             |
                                                   v (This is the start of the [♻️ Fast Loop])                                    |
+------------------+-------------------------------+-----------------------------------------------------------------------------+  |
| ✍️ **HOP-3: "THE WRITER" Agent** (Macro-ToT Generator)                                                  |  |
|                                                                                                                              |  |
|   **WHO:** The creative content generator.                                                                                   |  |
|   **WHAT:** Generate multiple creative drafts for high-stakes sections (K0, K1, K11). |  |
|   **WHERE:** `workflow_RES.py` (Class: `ArtistGenerator`)                                               |  |
|                                                                                                                              |  |
|   **HOW: (AGENTIC "ToT" GENERATE - 12 LLM Calls for K1)** |  |
|   |                                                                                                                          |  |
|   |---[ Macro-ToT Loop 1 of 3 ]---------------------------------------+                                                      |  |
|   |    |  (Config: K1_EXECUTIVE_SUMMARY_CONFIG, SC: 3) |                                                      |  |
|   |    |  -> LLM Call 1 (Candidate 1)                                |                                                      |  |
|   |    |  -> LLM Call 2 (Candidate 2)                                |                                                      |  |
|   |    |  -> LLM Call 3 (Candidate 3)                                |                                                      |  |
|   |    |  -> LLM Call 4 (Synthesis Call - Synthesizes C1,C2,C3) |                                 |  |
|   |    +--> Output: Draft 1 (String)                                |                                                      |  |
|   |---[ Macro-ToT Loop 2 of 3 ]---------------------------------------+                                                      |  |
|   |    |  (Config: K1_EXECUTIVE_SUMMARY_CONFIG, SC: 3)               |                                                      |  |
|   |    |  -> LLM Call 5-8 ...                                        |                                                      |  |
|   |    +--> Output: Draft 2 (String)                                |                                                      |  |
|   |---[ Macro-ToT Loop 3 of 3 ]---------------------------------------+                                                      |  |
|   |    |  (Config: K1_EXECUTIVE_SUMMARY_CONFIG, SC: 3)               |                                                      |  |
|   |    |  -> LLM Call 9-12 ...                                       |                                                      |  |
|   |    +--> Output: Draft 3 (String)                                |                                                      |  |
|   +----------------------------------------------------------------+                                                      |  |
|                                                                                                                              |  |
|   ➡️ **Output:** `[run_id]_HOP-3_ArtistOutput.json` (Contains `List[str]` for K0, K1, K11) |  |
+--------------------------------------------------+-----------------------------------------------------------------------------+  |
                                                   |                                                                             |
                                                   v                                                                             |
+------------------+-------------------------------+-----------------------------------------------------------------------------+  |
| 🧹 **HOP-4: "THE JANITOR" Agent** |  |
|                                                                                                                              |  |
|   **WHO:** The text sanitizer and pre-validation cleaner.                                                                      |  |
|   **WHAT:** Clean all generated text (including all 3 drafts) and lock it in the staging buffer.        |  |
|   **HOW:** Applies [⚙️ RegEx Engine] to strip markdown fences and conversational fillers.                   |  |
|   **WHERE:** `utils_RES.py` (Class: `TextSanitizer`)                                                     |  |
|                                                                                                                              |  |
|   ➡️ **Output:** `[run_id]_HOP-4_StagingBuffer.json` (Immutable Buffer, still contains 3 drafts) |  |
+--------------------------------------------------+-----------------------------------------------------------------------------+  |
                                                   |                                                                             |
                                                   v                                                                             |
+------------------+-------------------------------+-----------------------------------------------------------------------------+  |
| 🧐 **HOP-5: "THE INSPECTOR" Agent** (Macro-ToT Evaluator)                                                |  |
|                                                                                                                              |  |
|   **WHO:** The QA lead and "Generator-Evaluator" judge.                                                                        |  |
|   **WHAT:** (1) Select the single "winning" draft. (2) Validate that winner against all rules.      |  |
|   **WHERE:** `validation_RES.py` (Class: `PreFlightValidator`)                                      |  |
|                                                                                                                              |  |
|   **HOW: (AGENTIC "ToT" EVALUATE - 0 LLM Calls)** |  |
|   |                                                                                                                          |  |
|   |---[ Evaluation Step ]-------------------------------------------+                                                      |  |
|   |    |  (Tool: CodeInterpreterTool)          |                                                      |  |
|   |    |                                                            |                                                      |  |
|   |    |  -> "Scoring Competition"             |                                                      |  |
|   |    |     - Score(Draft 1)                                       |                                                      |  |
|   |    |     - Score(Draft 2)                                       |                                                      |  |
|   |    |     - Score(Draft 3)                                       |                                                      |  |
|   |    |  -> Selects 1 Winning Draft (e.g., Draft 1) |                                         |  |
|   |    +--> Output: "The single winning draft string..."            |                                                      |  |
|   +----------------------------------------------------------------+                                                      |  |
|                                                                                                                              |  |
|   ➡️ **Output 1:** `[run_id]_HOP-5_ValidationResults.json` |  |
|   ➡️ **Output 2:** *Overwrites* `[run_id]_HOP-4_StagingBuffer.json` with *only the winning drafts*. |  |
+--------------------------------------------------+-----------------------------------------------------------------------------+  |
   |                                                 ^                                                                             |
   | (This is where the [🔥 Factual Loop] triggers)   | (This is where the [♻️ Fast Loop] triggers)                                     |
   |                                                 |                                                                             |
   +-------------------------------------------------+                                                                             |
                                                   |                                                                             |
                                                   v                                                                             |
+------------------+-------------------------------+-----------------------------------------------------------------------------+  |
| 🚦 **HOP-6: "THE GATEKEEPER" Agent** |  |
|                                                                                                                              |  |
|   **WHO:** The final decision-maker.                                                                                         |  |
|   **WHAT:** Decide whether to PROCEED, HALT (creative failure), or trigger a SLOW LOOP (factual failure). |  |
|   **HOW:** Applies [⚙️ Decision Logic] (`if/else`) to `HOP-5_ValidationResults.json`. |  |
|   **WHERE:** `validation_RES.py` (Class: `GateDecisionEngine`)                                      |  |
|                                                                                                                              |  |
|      • `if FactualFailureException:` -> **[🔥 SLOW LOOP]** (Tells Foreman to re-run HOP-0)  |  |
|      • `if Critical/High Fail:` -> **[♻️ FAST LOOP]** (Tells Foreman to re-run HOP-3) |  |
|      • `else:` -> **[✅ PROCEED]** |
+--------------------------------------------------+-----------------------------------------------------------------------------+
                                                   |
                                                   v (If ✅ PROCEED)
+------------------+-------------------------------+-----------------------------------------------------------------------------+
| 🖨️ **HOP-7: "THE PUBLISHER" Agent** |
|                                                                                                                              |
|   **WHO:** The final typesetter and file generator.                                                                            |
|   **WHAT:** Render the final, winning content into all output files (MD, TXT, JSON).                                           |
|   **HOW:** Uses a [⚙️ Text Formatter] to populate `Resume.md`, etc., from the *winner-only* |
|          `HOP-4_StagingBuffer.json`. Also applies `hyphenation_rules.json`.      |
|   **WHERE:** `workflow_RES.py` (Class: `FileRenderer`)                                                  |
|                                                                                                                              |
|   ➡️ **Output:** `[run_id]_HOP-7_file_paths.json` & writes final files to `workflow_outputs/`      |
+--------------------------------------------------+-----------------------------------------------------------------------------+
                                                   |
                                                   v
+------------------+-------------------------------+-----------------------------------------------------------------------------+
| 🧾 **HOP-8: "THE AUDITOR" Agent** |
|                                                                                                                              |
|   **WHO:** The final archivist and run summarizer.                                                                             |
|   **WHAT:** Generate a comprehensive QA report summarizing the entire run, including all checks, signals, and loops.           |
|   **HOW:** Reads all state files (`HOP-0`, `HOP-4`, `HOP-5`) and formats them.                        |
|   **WHERE:** `validation_RES.py` (Class: `QAReportGenerator`)                                     |
|                                                                                                                              |
|   ➡️ **Output:** `[run_id]_HOP-8_qa_report.json` & writes `QA_Report.md` to `workflow_outputs/` |
+--------------------------------------------------+-----------------------------------------------------------------------------+
                                                   |
                                                   v
                                             [ 🏁 END ]
```

