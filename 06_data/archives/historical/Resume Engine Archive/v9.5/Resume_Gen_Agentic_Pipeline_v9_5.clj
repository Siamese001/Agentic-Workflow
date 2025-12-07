(comment
  ;; File: Resume Gen Agentic Pipeline v9.5.clj
  ;; Version: 9.5 (Privacy & Provenance)
  ;; This file represents the v9.0 (Agentic Loops) architecture.
  ;; It has been code-reviewed and corrected against the v9.5 Python/JSON files
  ;; to ensure all agent definitions, scores, and logic checks are accurate.

  +------------------------------------------------------------------------------------------------------------+
  | 🚀 v9.5 PARALLEL BATCH HARNESS (run_batch_v9_5.py)                                                          |
  | (Processes all jobs in parallel using a ProcessPoolExecutor)                                               |
  |                                                                                                            |
  |  (Input) 1. 📂 `batch_queue/` (Contains [job_1.json], [job_2.json], ... [job_N.json])                       |
  |                                                                                                            |
  |                 | (Spawns `max_parallel_workers` (e.g., 8) via ProcessPoolExecutor)                        |
  |                 v                                                                                          |
  |  +--------------------------------------------------------------------------------------------------+    |
  |  | 🌀 **Parallel Executor (`concurrent.futures`)** |    |
  |  |   (Each job runs in its own `process_single_job` function)                                         |    |
  |  |                                                                                                  |    |
  |  | +------------------+ +------------------+ +------------------+ +------------------+               |    |
  |  | | [Run Job 1]      | | [Run Job 2]      | | [Run Job 3]      | | ... [Run Job N]  | (All run     |    |
  |  | | (v9.0 Cost Check)| | (v9.0 Cost Check)| | (v9.0 Cost Check)| | (v9.0 Cost Check)| simultaneously)|    |
  |  | | (try/catch)      | | (try/catch)      | | (try/catch)      | | (try/catch)      |               |    |
  |  | |  `workflow.run()`| |  `workflow.run()`| |  `workflow.run()`| |  `workflow.run()`|               |    |
  |  | +------------------+ +------------------+ +------------------+ +------------------+               |    |
  |  |         |                  |                  |                  |                          |    |
  |  |         `-----------------(Collects all results when complete)-----------------'                          |    |
  |  |                                      v                                                        |    |
  |  |   2. (finally) Write all results to `batch_summary_v9_5.csv` (Output 1) 📈                     |    |
  |  |   3. (finally) Move all job files to `batch_complete/` (Output 2) 🗂️                            |    |
  |  +--------------------------------------------------------------------------------------------------+    |
  |                                                                                                            |
  |                 | (After batch completes)                                                                  |
  |                 v                                                                                          |
  |  +--------------------------------------------------------------------------------------------------+    |
  |  | 🤖 **Automated Meta-Learning Trigger** |    |
  |  |   (Batch runner *automatically* calls `run_learning_v9_0.py`)                                    |    |
  |  +--------------------------------------------------------------------------------------------------+    |
  |                                                                                                            |
  + - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -+
  | ♾️ v9.5 ASYNCHRONOUS META-LEARNING LOOP (Safer v7.5+ Logic)                                                |
  | (Triggered by `run_batch_v9_5.py` after batch is complete)                                                 |
  |                                                                                                            |
  | 1. `run_learning_v9_5.py` runs:                                                                            |
  |    +---------------------------+ (Reads failures from) -> +-------------------------+                     |
  |    | 🕵️ **PatternFinderAgent** [70]  |                       | 📄 `feedback_log.jsonl` | (Written to by 🛡️) |
  |    | (Parses `agent_name`)       | (Reads prefs from)  -> | 📄 `preference_log.jsonl` | (Written by HIL)  |
  |    | (Parses `key_changes`)      |                       +-------------------------+                     |
  |    +---------------------------+                                                                     |
  |                 | (Sends patterns to)                                                                 |
  |                 v                                                                                   |
  |    +---------------------------+ (Writes *proposals* to) -> +---------------------------+              |
  |    | 📈  **MetaPlannerAgent** [70]       |                       | 📄 `proposed_rules.jsonl` | (SAFE)       |
  |    +---------------------------+                       +---------------------------+              |
  |                 (Proposals are reviewed by human before merging into `master_config.json`)           |
  +------------------------------------------------------------------------------------------------------------+

                                        |
                                        v (Each `workflow.run()` call from a parallel thread)

  +------------------------------------------------------------------------------------------------------------+
  | 🧠 v9.0 LANGGRAPH ORCHESTRATION (Replaces v6.5 Governor)                                                     |
  | (LangGraph executes a 5-step stateful flow with dynamic recovery loops)                                    |
  |                                                                                                            |
  | 1. 🚀 **CrewOrchestrator** (Receives "Neo4j VP" goal)                                                      |
  | 2. **CrewOrchestrator** (Calls) -> 🧠 **v9.0 LangGraph State Flow** |
  |                                                                                                            |
  |  +------------------------------------------------------------------------------------------------+  |
  |  | **v9.0 LangGraph State Flow** |  |
  |  |                                                                                                |  |
  |  |   1. 🧭 **Run Strategy** (Calls `ThemeClassifierAgent`)                                          |  |
  |  |                | (Writes `strategy_brief` to 📋 State)                                        |  |
  |  |                v                                                                               |  |
  |  |   2. 🔍 **Run RAG** (Calls `v9.0 RAG Stack` agents) [Score: 96]                                  |  |
  |  |                | (Writes `rag_critique`, `rag_search_results` to 📋 State)                     |  |
  |  |                v                                                                               |  |
  |  |   3. ✒️ **Run Bullet Stack** (Calls `v9.0 ProvenanceRouterAgent`) [Score: 88] (v9) (Replaces v6.5 BulletSwarm)        |  |
  |  |                | (Writes `generated_bullets` to 📋 State)                                      |  |
  |  |                v                                                                               |  |
  |  |   4. 🧐 **Run Bullet Critique** (Calls `v9.0 BulletCritiqueAgent`)                               |  |
  |  |                | (Writes `bullet_critique_results` to 📋 State)                                |  |
  |  |                v                                                                               |  |
  |  |   | **BULLETS PASSED?** |                                                |  |
  |  |   +---------------------------------------+                                                |  |
  |  |      | (Yes)             | (No)                                                        |  |
  |  |   +---------------------------------------+                                                |  |
  |  |      v                   v                                                         |  |
  |  |   5. ✍️ **Run Drafting** (Calls `v9.0 DraftingConductorAgent`) [Score: 98]                      |  |
  |  |                | (Writes `final_draft` to 📋 State)                                            |  |
  |  |                v                                                                               |  |
  |  |   6. 🛡️ **Run QA** (Calls `v9.0 QAConductorAgent`, `AtomicQASwarmLogic`) [Score: 95]           |  |
  |  |                | (Writes `validation_results` to 📋 State)                                    |  |
  |  |                v                                                                               |  |
  |  |   +---------------------------------------+                                                |  |
  |  |   | **QA PASSED?** |                                                |  |
  |  |   +---------------------------------------+                                                |  |
  |  |      | (Yes)             | (No)                                                        |  |
  |  |      v                   v                                                         |  |
  |  |   [ ✅ **GOAL MET** ]     [ 🔄 **Call RePlanner** ] (Calls `WorkflowRePlannerAgent`)               |  |
  |  |   (Stop)                   | (Plan: "Requires new facts?")                       |  |
  |  |                            |   | (Yes) -> (Go to Step 2: RAG)                    |  |
  |  |                            |   | (No)  -> (Go to Step 3: Bullet Stack)           |  |
  |  +------------------------------------------------------------------------------------------------+  |
  +------------------------------------------------------------------------------------------------------------+

                                        |
                                        | (Graph calls `ThemeClassifierAgent`)
                                        v

  +------------------------------------------------------------------------------------------------------------+
  | 🧭 v9.0 (v7.0 Arch) STEP 1: STRATEGY (Unchanged)                                                            |
  |                                                                                                            |
  |    +--------------------------------------------------------------------------------------------------+    |
  |    |                          📋 **GraphState** (Shared State)                                         |    |
  |    +--------------------------------------------------------------------------------------------------+    |
  |       ^                                                                                                  |
  |       | (Writes `strategy_brief`)                                                                          |
  |       |                                                                                                  |
  |    [ 📄 **JD** ] -> [ 🤖 **ThemeClassifierAgent** [11] ] (Tier 3: Gemini 2.5 Flash-Lite)                  |
  |                                                                                                            |
  +------------------------------------------------------------------------------------------------------------+

                                        |
                                        | (Graph calls `run_rag_stack` node)
                                        v

  +------------------------------------------------------------------------------------------------------------+
  | 🔍 v9.0 STEP 2: RAG STACK (Agentic Upgrade) [Score: 96]                                                      |
  |                                                                                                            |
  | 1. [ ❓ **RAG_QueryGen** [75] ] (Tier 1: Gemini 2.5 Pro)                                                   |
  |                 | (Sends Queries)                                                                      |
  |                 v                                                                                      |
  | 2. [ 📡 **RAG_SearchAgent (ReAct)** [96] ] (Tier 1: Gemini 2.5 Pro)                                        |
  |    (Executes "Thought-Action-Critique" loop for each query)                                            |
  |    |                                                                                                 |
  |    |  1. [ 💭 **Thought** ] (LLM call: "What should I do?")                                           |
  |    |  2. [ ⚡ **Action** ] (LLM call: "Select a tool")                                                |
  |    |       |                                                                                        |
  |    |       `--> [ 📚 master_resume_search ] (Vector Tool)                                            |
  |    |       `--> [ 🕸️ web_search ] (External Tool)                                                   |
  |    |       `--> [ 🔗 **graph_search** ] (v9.0 Graph Tool)                                            |
  |    |       `--> [ ✍️ **write_to_graph** ] (v9.0 Graph Tool)                                          |
  |    |                                                                                                |
  |    |  3. [ 👁️ **Observation** ] (Receives results from tool)                                          |
  |    |  4. [ 🧐 **Internal Critique** ] (LLM call: "Is this step's result good?")                       |
  |    |  5. [ 🎯 **Satisfied?** ] --(No)--> (Loop to 1. Thought)                                       |
  |    |       | (Yes)                                                                                  |
  |    |       v (Gathers all loop results)                                                             |
  |    |                                                                                                |
  | 3. [ 🧑‍🏫 **RAG_Critique** [85] ] (Tier 1: Gemini 2.5 Pro) <---+ (Critiques *final* search results)         |
  |                                                                                                            |
  +------------------------------------------------------------------------------------------------------------+

                                        |
                                        | (Graph calls `run_bullet_stack` node)
                                        v

  +------------------------------------------------------------------------------------------------------------+
  | ✒️ v9.0 STEP 3: BULLET STACK (Provenance) [Score: 88] (v9) (Replaces v6.5 BulletSwarm)              |
  |                                                                                                            |
  |   [ 🤖 **ProvenanceRouterAgent** [80] (MoE Router) ] (Reads Strategy: "Unify" -> 2/3/2, "IBM" -> 2/2/2)   |
  |                 | (Executes 3-step provenance plan sequentially)                                       |
  |   +-------------+----------------+-----------------+                                                     |
  |   | (Step 1)                       | (Step 2)                      | (Step 3)                        |
  |   v                              v                               v                               |
  | [ 🐍 **Verbatim Bullets** ]        [ 🤖 **CustomizedBulletDrafter** ]    [ 🤖 **SyntheticBulletDrafter** ]   |
  | (Python similarity search)     (LLM Call: "Rewrite bullets")     (LLM Call: "Create new bullets")|
  | (2 Bullets)                      (3 or 2 Bullets)                (2 Bullets)                     |
  |   +-------------+----------------+-----------------+                                                     |
  |                 | (Gathers all bullets: e.g., 2+3+2=7)                                               |
  |                 v                                                                                      |
  |   [ 📜 **Final Bullet List** ] (Writes `generated_bullets` to 📋 State)                                    |
  |                                                                                                            |
  +------------------------------------------------------------------------------------------------------------+

                                        |
                                        | (Graph calls `run_drafting_stack` node)
                                        v

  +------------------------------------------------------------------------------------------------------------+
  | ✍️ v9.0 STEP 5: DRAFTING (MoE Conductor) [Score: 98] (Replaces v6.5 AdversarialRouter)                       |
  |                                                                                                            |
  | [ 💡 **PromptStackAgent** [5] (Python) ] (Assembles RAG context + Bullets into final prompt)              |
  |                 |                                                                                      |
  |                 v (Sends Prompt)                                                                       |
  |   +----------------------------------------------------------------------------------+   |
  |   | 🤖 **DraftingConductorAgent (MoE)** [90] (Tier 2: Gemini 2.5 Flash)              |   |
  |   | (LLM call: "Create a dynamic plan from these experts")                           |   |
  |   +----------------------------------------------------------------------------------+   |
  |                 | (Executes dynamic plan, e.g., [Strategist, MetricsSpecialist, Refiner]) |
  |                 v                                                                      |
  |   +----------------------------------------------------------------------------------+   |
  |   | 🧑‍🎨 **Pool of Drafting Experts (LLMs)** |   |
  |   |                                                                                  |   |
  |   | * [ ✍️ **Strategist (Gemini 2.5 Pro)** [95] ] (Writes initial draft)             |   |
  |   | * [ 🧐 **RedTeam (Claude 4.1 Opus)** [95] ] (Writes critique)                    |   |
  |   | * [ 🎨 **Refiner (GPT-5)** [100] ] (Writes final draft)                         |   |
  |   | * [ 📊 **MetricsSpecialist (Flash)** [75] ] (v9.0: Injects/Fixes metrics)          |   |
  |   +----------------------------------------------------------------------------------+   |
  |                 | (Final artifact from plan)                                           |
  |                 v                                                                      |
  |   [ 📜 **final_draft** ] (Writes to 📋 State)                                           |
  |                                                                                      |
  |   (v6.5 SC Paths logic is now handled by the Governor loop's RePlanner)                  |
  +------------------------------------------------------------------------------------------------------------+

                                        |
                                        v (Graph calls `run_qa_swarm` node as final validation)

  +------------------------------------------------------------------------------------------------------------+
  | 🛡️ v9.0 STEP 6: QA STACK (MoE Conductor) [Score: 95] (Code-Corrected)                                       |
  |                                                                                                            |
  |   +---------------------------------------+  +---------------------------------------+   |
  |   | 🤖 **QAConductorAgent (MoE)** [90]      |  | 📦 **AtomicQASwarmLogic** [5] (Python)  |   |
  |   | (LLM Call: "Which checks should I run?")|  | (Code-Corrected: Runs 2 Python checks)|   |
  |   |         |                             |  |         |                             |   |
  |   |         v (Dynamically selects from:) |  |         v (2 parallel checks)         |   |
  |   | **Pool of QA Experts (11 LLMs)** |  | * 🔢 WordCountValidator [15]        |   |
  |   | (Code-Corrected w/ Config Scores) |  | * 🔣 CharacterCountValidator [15]     |   |
  |   | * 🗣️ ClaimValidatorAgent (NLI) [75] |  |                                       |   |
  |   | * 🎚️ ToneValidator [55]             |  |                                       |   |
  |   | * 🎯 ThematicAlignment_Validator [80] |  |                                       |   |
  |   | * 🤝 SemanticEntailmentValidator [70] |  |                                       |   |
  |   | * 🧵 NarrativeThreadAgent [85]      |  |                                       |   |
  |   | * 👹 AdversarialReviewerAgent [95]  |  |                                       |   |
  |   | * 📍 JDSkillsValidatorAgent [65]     |  |                                       |   |
  |   | * 📶 SignalScoreValidatorAgent [70]   |  |                                       |   |
  |   | * D; BiasScrubberAgent [60]         |  |                                       |   |
  |   | * 🗓️ TenureValidatorAgent [50]      |  |                                       |   |
  |   | * 🔎 **MissedOpportunityAgent** [80] (v9.0) |  |                                 |   |
  |   +---------------------------------------+  +---------------------------------------+   |
  |                                                                                                            |
  +------------------------------------------------------------------------------------------------------------+
)