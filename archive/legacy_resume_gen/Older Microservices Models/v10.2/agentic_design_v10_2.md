Here is the updated Agentic Architecture Design, overwritten to version 10.2 based on the provided code files.

The primary changes from v10.1 to v10.2 are the **replacement of the mock TF-IDF RAG search with a persistent ChromaDB vector store** for true semantic search, the addition of a **per-job ingest-and-cleanup data lifecycle**, and the **injection of the `chromadb_client`** into the `WorkflowContext` to support this new capability.

All v10.1 feedback-awareness and hot-reloading features have been preserved.

-----

# Agentic Architecture Design v10.2

**VERSION 10.2: SEMANTIC RAG & DATA ISOLATION**

### Key v10.2 Changes:

1.  **[VEC] 🤖 ChromaDB Semantic RAG (ROW 1):** The `RAGStack` has been fundamentally upgraded. The previous TF-IDF-based `GraphSearchTool` is **deleted** and replaced by the new `ChromaDBSearchTool`. This tool provides true semantic vector search capabilities using a persistent ChromaDB instance.
2.  **[VEC] 📥 Ingest-then-Search (ROW 1):** The `RAG_SearchAgent` (ReAct Conductor) has been modified. Its *first action* is now to call `_ingest_resume_to_chroma_async`. This function chunks the `master_resume` and ingests the bullets into the ChromaDB collection *specifically for this job*.
3.  **[VEC] 🏷️ Per-Job Data Isolation (ROW 1):** During ingestion, all resume documents are tagged with the unique `workflow_id`. The `ChromaDBSearchTool` then performs all queries using a `where={"workflow_id": "..."}` filter, guaranteeing that RAG results are isolated to the current job and do not leak data between concurrent runs.
4.  **[VEC] 🧹 ChromaDB Cleanup (PIPELINE):** The `main_v10_2.py` and `run_batch_v10_2.py` runners are updated. After a workflow successfully completes, a new cleanup step is executed: `collection.delete(where={"workflow_id": "..."})`. This removes all temporary job data from the vector store.
5.  **[VEC] 💉 Dependency Injection (CONTEXT):** The `WorkflowContext` in `core_v10_2.py` has been updated. It now accepts the `chromadb_client` in its constructor and injects it into all agents, adhering to the established DI pattern.
6.  **♾️ PRESERVED (v10.1):** All v10.1 features (Feedback-Aware Agents, `FeedbackLogReader`, Dynamic Constitution, `ProposedRulesLoader`, and Hot-Reloading) are preserved and fully functional.
7.  **⚡ PRESERVED (v10.0):** All v10.0 performance features (Async clients, Caching, Parallel Critique) are preserved.
8.  **🔒 PRESERVED (v9.9):** All v9.9 security hardening (local Presidio PII and local regex bias detection) is preserved.

-----

## SECTION 1: AGENTIC CAPABILITY ASSESSMENT (TRANSPOSED) [v10.2]

**UPDATE:** Scores reflect v10.2's robust ChromaDB RAG (Row 1) on top of v10.1's feedback-driven adaptation (All Rows).

**Legend:**

  * HL/HI = High-Leverage / High-Intel ("Smart Brains")
  * LL/LI = Low-Leverage / Low-Intel ("Efficient Tools")
  * HL/LI = High-Leverage / Low-Intel ("Dumb Brains" - Flaw)
  * LL/HI = Low-Leverage / High-Intel ("Overqualified" - Flaw)
  * `♾️` = Enhanced in v10.1 (Feedback-Aware / Hot-Reloading)
  * `[VEC]` = Enhanced in v10.2 (ChromaDB Semantic RAG)

| \# | Stack | Function | Collab (20%) | Orch (25%) | Emer (10%) | Auto (30%) | Env (15%) | Overall Score | HL/HI (LLM) | LL/LI (Py) | HL/LI (Flaw) | LL/HI (Flaw) | Total | v10.2 Enhancements | Gaps (Abbrv.) |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| 1 | **RAGStack** `[VEC]` | Ingests resume chunks into ChromaDB, then performs semantic ReAct search filtered by `workflow_id`. | 20 | 25 | 10 | 30 | 15 | 100 | 6 | 3 | 0 | 0 | 9 | Async, Cached, **ChromaDB Semantic Search [VEC]**, **Feedback-Aware Selection** `♾️` | [GAP CLOSED] |
| 2 | BulletStack `♾️` | Generates and refines resume bullets in parallel using feedback-aware critique strategies. | 20 | 25 | 10 | 28 | 15 | 98 | 5 | 0 | 0 | 0 | 5 | Parallel Async, **Feedback-Aware Strategy** `♾️` | [GAP CLOSED] |
| 3 | DraftingStack `♾️` | Orchestrates expert agents via an async ReAct conductor for final draft generation. | 20 | 25 | 10 | 30 | 15 | 100\*\* | 7 | 0 | 0 | 0 | 7 | Async ReAct, **Feedback-Aware Selection** `♾️` | [GAP CLOSED] |
| 4 | QAStack `♾️` | Runs a parallel swarm of async, feedback-selected validators and bias checkers. | 20 | 25 | 10 | 30 | 15 | 100\*\* | 13 | 1 | 0 | 0 | 14 | Async Pool, **Feedback-Aware Selection** `♾️` | [GAP CLOSED] |
| 5 | MetaLearningLoop `♾️` | Observes system feedback logs to find patterns and propose hot-reloadable rule changes. | 20 | 25 | 10 | 30 | 15 | 100\*\* | 4 | 2 | 0 | 0 | 6 | Async, Cached, **Hot-Reload Output** `♾️` | [GAP CLOSED] |
| 6 | StrategyStack `♾️` | Uses feedback-aware Tree-of-Thoughts (ToT) to generate and select the optimal strategy. | 15 | 25 | 10 | 30 | 15 | 95 | 4 | 0 | 0 | 0 | 4 | Async ToT, **Feedback-Aware Branching** `♾️` | [GAP CLOSED] |
| 7 | PromptStack `♾️` | Generates dynamic, context-specific prompts using insights from historical feedback logs. | 15 | 20 | 10 | 25 | 15 | 85 | 1 | 0 | 0 | 0 | 1 | Async, Cached, **Feedback-Aware Gen** `♾️` | [GAP CLOSED] |
| 8 | SafetyGuardStack `♾️` | Provides local-only PII/bias checks using a dynamically hot-reloaded rule constitution. | 20 | 25 | 10 | 30 | 15 | 100 | 0 | 3 | 0 | 0 | 3 | Local (v9.9), **Dynamic Constitution** `♾️` | [GAP CLOSED] |
| 9 | DynamicToolingStack `♾️` | Selects and executes the best tools for a task based on feedback logs. | 20 | 25 | 10 | 30 | 15 | 100\* | 2 | 1 | 0 | 0 | 3 | Async, **Feedback-Aware Selection** `♾️` | [GAP CLOSED] |
| 10 | HIL\_InteractionStack | Proactively detects ambiguity to pause the workflow and request human clarification. | 20 | 25 | 10 | 26 | 15 | 96\* | 3 | 1 | 0 | 0 | 4 | Preserved (v9.9) | Gap: Deeper Human-Computer Interaction |

**v10.2 Score Improvements (Gap Closure):**

  * **RAGStack:** Score (100) preserved from v10.1, but implementation is now a robust semantic search via ChromaDB, replacing v10.1's simulated TF-IDF.
  * **MetaLearningLoop:** +5 points (95→100) - Gap closed by implementing hot-reloading of rules. (v10.1)
  * **SafetyGuardStack:** +2 points (98→100) - Gap closed by dynamically reading `proposed_rules.jsonl`. (v10.1)
  * **All other stacks:** Gaps closed by integrating `FeedbackLogReader` for dynamic, performance-based agent/strategy selection. (v10.1)

-----

## FOOTNOTE: 5 AGENTIC DIMENSIONS (DEFINITIONS)

The "Overall Score" is a weighted composite based on these 5 dimensions:

1.  **Multi-Agent Collaboration (20%)**: How well agents communicate and critique each other's work.
2.  **Agentic Orchestration (25%)**: How the system dynamically plans, routes, and re-plans tasks.
3.  **Emergent Behavior (10%)**: Novel behaviors that emerge from complex, multi-step feedback loops.
4.  **Reflexive Autonomy (30%)**: The system's ability to observe, reason about, and modify itself (meta-learning).
5.  **Environmental Coupling (15%)**: How the system reads, writes, and acts on its environment (files, APIs, tools, user).

### INDICATOR DEFINITIONS:

  * `*` Score is directly enabled by The\_LangGraph\_App (orchestration, replanning, HIL).
  * `**` Score is directly enabled by the MetaLearningLoop (long-term learning, log files).
  * `♾️` Enhanced in v10.1 with feedback-awareness or hot-reloading.
  * `[VEC]` Enhanced in v10.2 with ChromaDB Semantic RAG.

-----

## SECTION 2: DETAILED PIPELINE FLOW (v10.2)

```
+------------------------------------------------------------------------------------------------------------+
| 🚀 v10.2 ASYNC BATCH HARNESS (run_batch_v10_2.py) ♾️ [VEC]                   |
| (Processes jobs with CONTROLLED CONCURRENCY using asyncio.Semaphore)                                       |
|                                                                                                            |
|  (Input) 1. 📂 `batch_queue/` (Contains [job_1.json], [job_2.json], ... [job_N.json])                      |
|                                                                                                            |
| | (Initialize SHARED WorkflowContext for all jobs ⚡♾️ [VEC])                                             |
| |  context = WorkflowContext(CONFIG, redis_client, chromadb_client)  # Shared Cache, ChromaDB, etc. |
| |                 v                                                                                       |
| |  +--------------------------------------------------------------------------------------------------+    |
| |  | ⚡ **Async Batch Executor with Semaphore** (asyncio.gather)                      |
| |  | (Max concurrent: `max_concurrent_llm_calls` from config)                                          |
| |  |                                                                                                  |    |
| |  | +------------------+ +------------------+ +------------------+ +------------------+               |    |
| |  | | [Async Job 1]    | | [Async Job 2]    | | [Async Job 3]    | | ... [Async Job N]| (Up to 10   |    |
| |  | | (v10.2 Async)    | | (v10.2 Async)    | | (v10.2 Async)    | | (v10.2 Async)    | concurrent) |    |
| |  | | (Shared Cache ⚡)| | (Shared Cache ⚡)| | (Shared Cache ⚡)| | (Shared Cache ⚡)|             |    |
| |  | | await workflow() | | await workflow() | | await workflow() | | await workflow() |             |    |
| |  | +------------------+ +------------------+ +------------------+ +------------------+               |    |
| |  |         |                  |                  |                  |                          |    |
| |  | `-----------------(asyncio.gather with semaphore)-----------------'                          |
| |  |                                      v                                                        |
| |  |   2. (finally) Write all results to `batch_summary_v10_2.csv` (Output 1) 📈|
| |  |   3. (finally) Move all job files to `batch_complete/` (Output 2) 🗂️                            |
| |  |   4. (finally) 🧹 **ChromaDB Cleanup (v10.2)**: `collection.delete(where={"workflow_id": ...})` [VEC]|
| |  |   5. (finally) Log cache stats: "Cache hit rate: 45%" ⚡                     |
| |  +--------------------------------------------------------------------------------------------------+    |
|                                                                                                            |
|                 | (After batch completes)                                                                  |
|                 v                                                                                          |
|  +--------------------------------------------------------------------------------------------------+    |
|  | 🤖 **Automated Async Meta-Learning Trigger** ⚡♾️                      |
|  | (Batch runner *automatically* calls `await run_meta_learning()`)                 |
|  +--------------------------------------------------------------------------------------------------+    |
|                                                                                                            |
+------------------------------------------------------------------------------------------------------------+

+ - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -+
|
| ♾️ v10.2 ASYNC AGENTIC META-LEARNING GRAPH ⚡♾️                             |
| (Triggered by `run_batch_v10_2.py` after batch is complete)                  |
| (Uses its own WorkflowContext, also injected with chromadb_client)           |
|                                                                                                            |
| 1. `await run_meta_learning()` runs (which is a LangGraph app):              |
|    +---------------------------+ (Reads) -> +-------------------------+                                   |
|    | 🤖 **LogReaderAgent** (Python) |            | 📄 `feedback_log.jsonl` |                                   |
|    +---------------------------+            | 📄 `preference_log.jsonl` |                                   |
|                 | (Sends logs)       +-------------------------+                                   |
|                 v                                                                                        |
|    +---------------------------+                                                                         |
|    | 🤖 **AsyncPatternFinderAgent** (Gemini 2.5 Flash / T2) ⚡ (Async + cached)                         |
|    +---------------------------+                                                                         |
|                 | (Sends patterns)                                                                     |
|                 v                                                                                        |
|    +--------------------------------+                                                                    |
|    | 🤖 **AsyncHypothesisGeneratorAgent** (Gemini 2.5 Flash / T2) ⚡ (Async + cached)                  |
|    +--------------------------------+                                                                    |
|                 | (Sends 1 hypothesis)                                                                 |
|                 v                                                                                        |
|    +---------------------------+                                                                         |
|    | 🤖 **AsyncProposalDrafterAgent** (Gemini 2.5 Flash / T2) ⚡ (Async + cached)                      |
|    +---------------------------+                                                                         |
|                 | (Sends proposal)                                                                     |
|                 v                                                                                        |
|    +-----------------------------+                                                                     |
|    | 🤖 **AsyncProposalCritiqueAgent** (Gemini 2.5 Flash / T2) ⚡ (Async + cached)                    |
|    +-----------------------------+                                                                     |
|                 | (Critique Passed?)                                                                   |
|    +------------+--------------+                                                                       |
|    | (No)                      | (Yes)                                                                |
|    v (Loop to Hypothesis)      v                                                                       |
|    (Or loop to Drafter)        +----------------------------------+ (Writes to) -> +---------------------------+ |
|                              | 🤖 **HotReloadRuleManager (v10.1)** ♾️ |              | 📄 `proposed_rules.jsonl` | |
|                              | (Auto-approves high-confidence rules) |              | (File is hot-reloaded)    | |
|                              +----------------------------------+              +---------------------------+ |
+------------------------------------------------------------------------------------------------------------+

                                        |
  v (Each `await workflow.run()` call from async batch executor)

+------------------------------------------------------------------------------------------------------------+
| 🧠 v10.2 FULL ASYNC LANGGRAPH ORCHESTRATION ⚡♾️ [VEC]                           |
| (Main graph with P0+P1+P2, v9.9 security, v10.0 async/caching, v10.1 feedback/hot-reload, v10.2 ChromaDB) |
|                                                                                                            |
| +---------------------------------------------------------------------------------------------------------+  |
| | 📦 **v10.2 Async LangGraph State Flow** ⚡♾️ [VEC] |
| +---------------------------------------------------------------------------------------------------------+  |
| |                                                                                                         |  +----------------------------------+
| | 0. 🧼 **await run_sanitize_pii()** (LOCAL Presidio 🔒)          |  | 🛡️ **PARALLEL SAFETYGUARDSTACK ♾️** (LOCAL Regex 🔒) |
| |    | (v9.9 security preserved)                                   |  | (Reads dynamic constitution     |
| |    v                                                                                                    |  |  from `proposed_rules.jsonl`) |
| | 1. 🧭 **await run_tot_strategy()** (Gemini 2.5 Pro / T1) ⚡♾️                                         |  +----------------------------------+
| |    | (Async ToT, cached, feedback-aware)                         |  +----------------------------------+
| |    | (Calls `FeedbackLogReader` to select branches) |  | 💰 **COSTTRACKER (Injected)** ⚡  |
| |    | (Writes `strategy_brief` to 📋 ModularState)                |  | (Via WorkflowContext) |
| |    v                                                                                                    |  +----------------------------------+
| | 2. 🧐 **await run_detect_ambiguity()** (P1) (Gemini 2.5 Flash / T2)                                   |  +----------------------------------+
| |    | **AMBIGUITY DETECTED?** |  | 💾 **CACHEMANAGER (Injected)** ⚡ |
| |    +--------------------------+ (No)                                                                   |  | (Redis-backed LLM cache)|
| |    | (Yes)                     v                                                                       |  +----------------------------------+
| |    '----(Go to Step 8: HIL)   3. 🔍 **await run_rag_stack()** (P2: Ingest+ReAct) ⚡♾️ [VEC]           |  +----------------------------------+
| |                              | (Ingests resume to ChromaDB, runs semantic search) |  | ♾️ **FEEDBACKLOGREADER (v10.1)** |
| |                              | (Writes `rag_critique`, `rag_search_results` to 📋 State)             |  | (Reads `feedback_log.jsonl`) |
| |                              v                                                                        |  +----------------------------------+
| | 4. ✒️ **await run_generate_bullets()** (Mixed T1/T2) ⚡♾️                                            |  +----------------------------------+
| |    | (Async, cached, feedback-aware strategy)                                                     |  | ♾️ **PROPOSEDRULESLOADER (v10.1)** |
| |    | (Writes `generated_bullets` to 📋 State)                                                        |  | (Hot-reloads `proposed_rules.jsonl`) |
| |    v                                                                                                    |  +----------------------------------+
| | 5. 🧐 **await run_critique_bullets()** (Gemini 2.5 Flash / T2) ⚡ **PARALLEL** ♾️                     |  +----------------------------------+
| |    | (Uses `asyncio.gather` for PARALLEL critique - 5× faster!)                                     |  | [VEC] **CHROMADBCLIENT (New)** |
| |    | (Feedback-aware critique model selection)                         |  | (Injected ChromaDB client)     |
| |    v                                                                                                    |  +----------------------------------+
| |   | **BULLETS PASSED?** [Retry: {bullet_retries}/2]                                                     |
| +-------------------------------------------------+                                                       |
| |    | (Yes)                                    | (No)                                                  |
| +-------------------------------------------------+                                                       |
| |    v                                            v                                                       |
| | 6. ✍️ **await run_drafting()** (P1 Conductor) ⚡♾️                                                  | [ 🔄 **Local Retry: Bullets** ] |
| |    | (Async ReAct conductor, cached, feedback-aware) | (If bullet_retries < 2, +1 retry)                     |
| |    | (Writes `final_draft` to 📋 State)         '----(Go to Step 4: Bullet Stack)                       |
| |    v                                            '----(Go to 🚨 Global RePlanner)                        |
| | 7. 🛡️ **await run_qa_validation()** (P1 Conductor) ⚡♾️                                             |
| |    | (Async QA, cached, feedback-aware validator selection) |
| |    v                                                                                                    |
| |   | **QA PASSED?** [Retry: {qa_retries}/1]                                                              |
| +-------------------------------------------------+                                                       |
| |    | (Yes)                                    | (No)                                                  |
| +-------------------------------------------------+                                                       |
| |    v                                            v                                                       |
| | 8. 🗣️ **await run_hil_stack()** (P1) (Gemini 2.5 Flash / T2)                                       | [ 🔄 **Local Retry: Drafting** ] |
| |    | (Calls `SuggestionAgent`)                 | (If qa_retries < 1, +1 retry)                         |
| |    v                                            '----(Go to Step 6: Run Drafting)                       |
| | 9. ⏸️ **HIL Pause** (Awaits Human Input) (Human)                                                     | (If qa_retries >= 1)                                  |
| |    v                                            v                                                       |
| | 10. 🗺️ **await run_feedback_router()** (P1) (Gemini 2.5 Flash / T2)                                | [ 🚨 **Call Global RePlanner** ] (Claude 4.1 Opus / T1) |
| |    | (Logs feedback to `feedback_log.jsonl`) ♾️                                    |
| |    | **NEW RULES?** |                                                                    |
| |    +--------------------------+ (No)                                                                   |
| |    | (Yes)                     v                                                                       |
| |    '----(Go to 🚨 Global RePlanner)   [ ✅ **GOAL MET** ] (End)                                       |
| |                                                                                                       |
| +---------------------------------------------------------------------------------------------------------+
+------------------------------------------------------------------------------------------------------------+

                                        |
  | (Graph calls the Strategy (ToT) Node)
                                        v

+------------------------------------------------------------------------------------------------------------+
| 🧭 v10.2 STEP 1: STRATEGY (Feedback-Aware ToT) ⚡♾️                                                        |
| (Preserved from v10.1)                                                                                     |
|                                                                                                            |
|    +--------------------------------------------------------------------------------------------------+    |
|    | 📋 **MainGraphState** (Modular Composition) ⚡                                                     |
|    | - strategy: StrategyState (isolated strategy data)                                             |
|    +--------------------------------------------------------------------------------------------------+    |
|       ^                                                                   ^                            |
|       | (Writes *final* `strategy_brief`)                                 | (Reads feedback)           |
|       |                                                                   |                            |
|    [ 📄 **JD** ] -> [ 🤖 **AsyncToTStrategistAgent** (Gemini 2.5 Pro / T1) ⚡♾️ ] -- [ ♾️ **FeedbackLogReader** ] |
|                 | (Async, cached, prioritizes branches based on feedback) |
|   +-------------+----------------+-----------------+                                                    |
|   | (Strategy A)                   | (Strategy B)                    | (Strategy C)                   |
|   v                                v                               v                              |
| [ 🤖 **StrategyCritique** (Gemini 2.5 Flash / T2) ] [ 🤖 **StrategyCritique** (Gemini 2.5 Flash / T2) ] [ 🤖 **StrategyCritique** (Gemini 2.5 Flash / T2) ] |
| (Async: "Critique A")          (Async: "Critique B")         (Async: "Critique C")         |
|   +-------------+----------------+-----------------+                                                    |
|                 | (Gathers 3 strategies + 3 critiques)                                                 |
|                 v                                                                                      |
|    [ 🤖 **StrategySelectorAgent** (Gemini 2.5 Flash / T2) ] (Selects single best one)                    |
|                 | (Async call with caching)                                                              |
|                 v (Checks for vagueness)                                                               |
|    [ 🧐 **AmbiguityDetectorAgent (P1)** (Gemini 2.5 Flash / T2) ] --(Yes)--> (Route to HIL Stack)         |
|                                                                                                            |
+------------------------------------------------------------------------------------------------------------+

                                        |
  | (Graph calls `run_rag_stack` node)
                                        v

+------------------------------------------------------------------------------------------------------------+
| 🔍 v10.2 STEP 2: ASYNC RAG STACK (ChromaDB Semantic) ⚡♾️ [VEC] [Score: 100]                               |
|                                                                                                            |
| 1. [ 🤖 **RAG_SearchAgent (Conductor)** [96] (Gemini 2.5 Pro / T1) ] ⚡♾️ [VEC]                              |
|    | (Async, cached, feedback-aware selection)                                                             |
|    `--(Reads)--> [ ♾️ **FeedbackLogReader** ] (Selects best sub-agents/tools)                                 |
|                                                                                                            |
|    **STEP A: INGEST (Per-Job)** [VEC]                                                                      |
|    | (Calls `_ingest_resume_to_chroma_async()`)                                                            |
|    `--(Writes)--> [ 🗄️ **ChromaDB Collection** (Tags docs with `workflow_id`) ]                             |
|                                                                                                            |
|    **STEP B: ReAct SEARCH LOOP (Thought-Action-Critique)** |
|    |                                                                                                      |
|    |  1. [ 💭 **Thought** ] (Async LLM call: "What should I do?")                                        |
|    |  2. [ ⚡ **Action** ] (P1: Calls tools based on thought)                                              |
|    |       |                                                                                            |
|    |       `--> [ 💡 **HyDETool** (Gemini 2.5 Flash / T2) ⚡ ] (P2: Async HyDE Tool)                       |
|    |       `--> [ 🔎 **ChromaDBSearchTool** (Python+ChromaDB) ⚡ [VEC] ]                                   |
|    |           | (Queries collection where `workflow_id` == current_id)                                   |
|    |           `--(Reads)--> [ 🗄️ **ChromaDB Collection** ]                                               |
|    |                                                                                                      |
| 2. [ 🧐 **AsyncRAG_ReRankerAgent** [80] (Gemini 2.5 Flash / T2) ⚡♾️ ] (P2: Async re-rank)                 |
|    | (Async call with caching, agent selected via feedback)                                               |
|    |                                                                                                      |
| 3. [ 🧑‍🏫 **RAG_Critique** [85] (Claude 4.1 Opus / T1) ] <---+ (Critiques *re-ranked* search results)          |
|                                                                                                            |
+------------------------------------------------------------------------------------------------------------+

                                        |
  | (Graph calls `run_bullet_stack` node)
                                        v

+------------------------------------------------------------------------------------------------------------+
| ✒️ v10.2 STEP 3: ASYNC BULLET STACK ⚡♾️ [Score: 98]                                                       |
| (Preserved from v10.1)                                                                                     |
|                                                                                                            |
|   [ 🤖 **AsyncBulletGeneratorAgent** [90] (Gemini 2.5 Pro / T1) ⚡♾️ ]                                   |
|    | (Async, cached, v10.0 fix)                                                                      |
|    `--(Reads)--> [ ♾️ **FeedbackLogReader** ] (Selects best generation strategy) |
|                 | (Executes intelligent provenance plan)                                              |
|   +-------------+----------------+-----------------+-------------------------+                           |
|   | (Step 1)                       | (Step 2)                      | (Step 3)                        | (Step 4)                |
|   v                              v                               v                               |
| [ 🐍 **Verbatim** (Python) ] [ 🤖 **Customized** (Gemini 2.5 Pro / T1) ] [ 🤖 **Synthetic** (Gemini 2.5 Pro / T1) ] [ 🤖 **SyntheticFactCheck** (Gemini 2.5 Flash / T2) ] |
| (2 Bullets)                      (3 or 2 Bullets) ⚡              (2 Bullets) ⚡                  (Filters out hallucinations) ⚡ |
|   +-------------+----------------+-----------------+-------------------------+                           |
|                 | (Gathers all *fact-checked* bullets)                                               |
|                 v                                                                                      |
|   [ 📜 **Final Bullet List** ] (Writes `generated_bullets` to 📋 State)                                    |
|                                                                                                            |
+------------------------------------------------------------------------------------------------------------+

                                        |
  | (Graph calls `run_critique_bullets` node)
                                        v

+------------------------------------------------------------------------------------------------------------+
| 🧐 v10.2 STEP 4: PARALLEL ASYNC BULLET CRITIQUE ⚡♾️                                                      |
| (Preserved from v10.1)                                                                                     |
|                                                                                                            |
|   [ 🤖 **AsyncBulletCritiqueAgent** [90] (Gemini 2.5 Flash / T2) ⚡♾️ ]                                   |
|    | (Receives 5 bullets to critique)                                                                 |
|    `--(Reads)--> [ ♾️ **FeedbackLogReader** ] (Selects best critique model/prompt) |
|                 v                                                                                      |
|   +--------------------------------------------------------------------------------------------------+    |
|   | async def run_async(self, bullets: List[str]):                                                  |
|   |     # Create async tasks for PARALLEL critique                                                  |
|   |     tasks = [self.critique_single_bullet(b) for b in bullets]                                   |
|   |                                                                                                  |
|   |     # Execute ALL in parallel using asyncio.gather                                              |
|   |     critiques = await asyncio.gather(*tasks, return_exceptions=True)                            |
|   |                                                                                                  |
|   |     return critiques  # All 5 critiques complete in ~2s (vs 10s sequential)                     |
|   +--------------------------------------------------------------------------------------------------+    |
|                                                                                                            |
|   **Performance:** 5 bullets × 2s each = 10s sequential (v9.9) → 2s parallel (v10.0) = **5× FASTER** |
|                                                                                                            |
+------------------------------------------------------------------------------------------------------------+

                                        |
  | (Graph calls `run_drafting_stack` node)
                                        v

+------------------------------------------------------------------------------------------------------------+
| ✍️ v10.2 STEP 5: ASYNC DRAFTING (P1 Conductor + Feedback-Aware) ⚡♾️ [Score: 100]                          |
| (Preserved from v10.1)                                                                                     |
|                                                                                                            |
| [ 🤖 **AsyncDynamicPromptEngineerAgent** [85] (Gemini 2.5 Flash / T2) ⚡♾️ ] (Async, cached, feedback-aware) |
|    | (Creates custom prompt asynchronously)                                                         |
|    `--(Reads)--> [ ♾️ **FeedbackLogReader** ] (Selects best prompt style)     |
|    v (Sends *Custom-Generated* Prompt)                                                                       |
|   +----------------------------------------------------------------------------------+   |
|   | 🤖 **AsyncDraftingConductorAgent (P1 ReAct)** [95] (Gemini 2.5 Pro / T1) ⚡♾️     |
|   | (P1: True ReAct agent. P2: Reads `feedback_log.jsonl` for dynamic agent selection) |
|   | (Executes async step-by-step "Thought-Action-Critique" loop)                       |
|   | (All LLM calls use caching for cost reduction)                                     |
|   +----------------------------------------------------------------------------------+   |
|                 | (Calls experts as tools, step-by-step)                               |
|                 v                                                                      |
|   +----------------------------------------------------------------------------------+   |
|   | 🧑‍🎨 **Pool of Async Drafting Experts (Tools)** ⚡ |   |
|   |                                                                                  |   |
|   | * [ ✍️ **Strategist** (Gemini 2.5 Pro / T1) ⚡ ]                                  |
|   | * [ 🧐 **RedTeam** (Claude 4.1 Opus / T1) ⚡ ]                                  |
|   | * [ 🎨 **Refiner** (GPT-5 / T1) ⚡ ]                                            |
|   | * [ 📊 **MetricsSpecialist** (Gemini 2.5 Flash / T2) ⚡ ]                         |
|   +----------------------------------------------------------------------------------+   |
|                 | (Final artifact from async ReAct loop)                            |
|                 v                                                                      |
|   [ 📜 **final_draft** ] (Writes to 📋 ModularState)                                    |
|                                                                                      |
+------------------------------------------------------------------------------------------------------------+

                                        |
  | (Graph calls `run_qa_swarm` node)
                                        v

+------------------------------------------------------------------------------------------------------------+
| 🛡️ v10.2 STEP 6: ASYNC QA STACK (P1 Conductor + Feedback-Aware + Hot-Reload) ⚡♾️ [Score: 100]              |
| (Preserved from v10.1)                                                                                     |
|                                                                                                            |
|   +---------------------------------------+  +---------------------------------------+   |
|   | 🤖 **AsyncQAConductorAgent** [95] ⚡♾️   |  | 📦 **AtomicQASwarmLogic** [5] (Python)  |   |
|   | (Gemini 2.5 Pro / T1)                 |  | (Runs 2 Python checks)                |   |
|   | (P1: True ReAct agent. P2: Reads log)   |  |         |                             |   |
|   | (Async step-by-step ReAct loop)       |  |         v (2 parallel checks)         |   |
|   | `--(Reads)--> [ ♾️ **FeedbackLogReader** ]   |  | * 🔢 WordCountValidator [15]        |   |
|   |         | (Selects best validators)   |  | * 🔣 CharacterCountValidator [15]     |   |
|   |         v (Calls `QAPlanCritique` first) |  |                               |   |
|   | [ 🧐 **QAPlanCritiqueAgent** [70] (Gemini 2.5 Flash / T2) ⚡ ] |  |                               |   |
|   |         |                             |  +---------------------------------------+   |
|   |         v (Calls experts as tools, all async!)                                           |
|   | **Pool of Async QA Experts (11 LLMs)** ⚡♾️ |                                          |
|   | (All experts use async clients with caching)                                                 |
|   | * 🗣️ ClaimValidatorAgent (NLI) [75]  (Gemini 2.5 Flash / T2) ⚡                          |
|   | * 🎚️ ToneValidator [55] (Gemini 2.5 Flash / T2) ⚡                                       |
|   | * 🎯 ThematicAlignment_Validator [80] (Gemini 2.5 Flash / T2) ⚡                          |
|   | * 🤝 SemanticEntailmentValidator [70] (Gemini 2.5 Flash / T2) ⚡                          |
|   | * 🧵 NarrativeThreadAgent [85] (Gemini 2.5 Flash / T2) ⚡                                |
|   | * 👹 AdversarialReviewerAgent [95] (Claude 4.1 Opus / T1) ⚡                            |
|   | * 📍 JDSkillsValidatorAgent [65] (Gemini 2.5 Flash / T2) ⚡                               |
|   | * 📶 SignalScoreValidatorAgent [70] (Gemini 2.5 Flash / T2) ⚡                            |
|   | * ⚖️ **BiasDetectorAgent [60] (LOCAL Regex 🔒 + Hot-Reload) ♾️** |
|   | * 🗓️ TenureValidatorAgent [50] (Gemini 2.5 Flash / T2) ⚡                               |
|   | * 🔎 MissedOpportunityAgent [80] (v9.0) (Gemini 2.5 Flash / T2) ⚡                          |
|   +---------------------------------------+----------------------------------------------+   |
|                                                                                                            |
+------------------------------------------------------------------------------------------------------------+
```