You are right, that response was truncated. My apologies.

Here is the complete and final file, `agentic_design_v10_3.md`, in its entirety.

-----

# Agentic Architecture Design v10.3

**VERSION 10.3: INSTRUCTIONAL INJECTION & HYBRID RAG**

### Key v10.3 Changes:

This is a destructive overwrite based on `Instructional_Injection_Enhanced_v4.md`. All v10.2 features are preserved, but the system's core is now hardened with new validation and resilience patterns.

1.  **[HYBRID] 🚀 Hybrid RAG (Row 1):** The v10.2 RAG agent is **deleted**. The new `RAG_SearchAgent` is a non-ReAct pipeline that executes a **Hybrid RAG** strategy. It runs `ChromaDBSearchTool` (vector) and the new `BM25SearchTool` (keyword) in parallel, merges their results, and reranks the superior, combined context.
2.  **[VAL] 🛡️ Pydantic Validation (All Rows):** All 30+ LLM output contracts are now defined by Pydantic models in `core_v10_3.py`. All agents and tools use the injected `ResponseValidator` to parse and validate 100% of LLM outputs, eliminating fragile `.get()` logic.
3.  **[RESIL] 🔄 Node Retries (Orchestration):** All 11 primary LangGraph nodes (e.g., `run_tot_strategy`, `run_rag_stack`) are now decorated with `@exponential_backoff_retry`, making the graph resilient to transient API or validation errors.
4.  **[RESIL] 🔌 Tool Circuit Breakers (Rows 3 & 4):** The `ReActConductorAgent` and `QAConductorAgent` now wrap all 15+ tool calls in a `CircuitBreaker`. If a specific tool (e.g., `validate_claims`) fails 3 consecutive times, the breaker for *that tool* opens, making the ReAct loop resilient to cascading failures.
5.  **[BUDGET] ✂️ Context Budgeting (Row 4):** The `QAConductorAgent` no longer naively injects full documents. It now uses the `ContextBudgetManager` to prune large contexts (like `master_resume`) *before* passing them to tools, preventing token limit errors.
6.  **[DI] 🏠 Prompt Centralization (All Rows):** All 30+ hardcoded prompts are **eradicated** from agents and tools. All agents now call `self.prompt_manager.get_template()` to retrieve instructions from a central `PromptTemplateManager` in `core_v10_3`.
7.  **[DI] 💡 Few-Shot Injection (Rows 3 & 4):** The new `PromptTemplateManager` injects 1-2 high-quality, few-shot examples into all 15 specialist tool prompts, mandating reliable JSON output.
8.  **[DI] ✍️ Style Injection (Rows 3 & 7):** `PromptEngineerAgent` and `DraftingRefinerTool` now inject a `style_guide` variable into their prompts to control linguistic output.
9.  **[DI] 📦 True Dependency Injection (Core):** All global `CONFIG` singletons are **deleted**. `main.py` and `run_batch.py` now act as true Composition Roots, instantiating all 10+ core services (Validator, PromptManager, etc.) and injecting them into the `WorkflowContext`.

-----

## SECTION 1: AGENTIC CAPABILITY ASSESSMENT (TRANSPOSED) [v10.3]

**UPDATE:** Scores reflect v10.3's Hybrid RAG, Pydantic Validation, and system-wide Resilience Patterns.

**Legend:**

  * `[HYBRID]` = v10.3 Hybrid RAG (Vector + Keyword)
  * `[VAL]` = v10.3 Pydantic Schema Validation
  * `[RESIL]` = v10.3 Resilience Pattern (Retry or Circuit Breaker)
  * `[BUDGET]` = v10.3 Context Budget Management
  * `[DI]` = v10.3 True Dependency Injection / Centralized Service
  * `♾️` = Preserved v10.1 Feedback-Aware / Hot-Reloading

| \# | Stack | Function | Collab (20%) | Orch (25%) | Emer (10%) | Auto (30%) | Env (15%) | Overall Score | HL/HI (LLM) | LL/LI (Py) | Total | v10.3 Enhancements |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| 1 | **RAGStack** | Ingests resume, runs **Hybrid RAG** (parallel Vector + Keyword), merges, and reranks. | 20 | 25 | 10 | 30 | 15 | **100** | 4 | 5 | 9 | Async, Cached, `[HYBRID]`, `[VAL]`, `♾️` |
| 2 | BulletStack | Generates/refines bullets in parallel using feedback-aware, validated critique strategies. | 20 | 25 | 10 | 30 | 15 | **100** | 5 | 0 | 5 | Parallel Async, `[VAL]`, `[DI]` (Prompts), `♾️` |
| 3 | DraftingStack | Orchestrates expert agents via ReAct, now with **tool circuit breakers** and **Pydantic validation**. | 20 | 25 | 10 | 30 | 15 | **100** | 7 | 0 | 7 | Async ReAct, `[RESIL]`, `[VAL]`, `[DI]`, `♾️` |
| 4 | QAStack | Runs a swarm of validators with **tool circuit breakers**, **Pydantic validation**, and **context budgeting**. | 20 | 25 | 10 | 30 | 15 | **100** | 13 | 1 | 14 | Async Pool, `[RESIL]`, `[VAL]`, `[BUDGET]`, `[DI]`, `♾️` |
| 5 | MetaLearningLoop | Observes logs to find patterns and propose hot-reloadable rule changes. | 20 | 25 | 10 | 30 | 15 | **100** | 4 | 2 | 6 | Async, Cached, `[VAL]`, `[DI]` (Prompts), `♾️` |
| 6 | StrategyStack | Uses feedback-aware, **Pydantic-validated** Tree-of-Thoughts (ToT) to select strategy. | 15 | 25 | 10 | 30 | 15 | **95** | 4 | 0 | 4 | Async ToT, `[VAL]`, `[DI]` (Prompts), `♾️` |
| 7 | PromptStack | Generates dynamic, **Pydantic-validated** prompts using insights from feedback logs. | 15 | 20 | 10 | 25 | 15 | **85** | 1 | 0 | 1 | Async, Cached, `[VAL]`, `[DI]` (Style), `♾️` |
| 8 | SafetyGuardStack | Provides local-only PII/bias checks using a dynamically hot-reloaded rule constitution. | 20 | 25 | 10 | 30 | 15 | **100** | 0 | 3 | 3 | Local (v9.9), `[DI]` (Prompts), `♾️` |
| 9 | DynamicToolingStack | Selects/executes tools based on feedback logs. (Now part of core resilience). | 20 | 25 | 10 | 30 | 15 | **100** | 2 | 1 | 3 | Async, `[DI]` (Core), `♾️` |
| 10 | HIL\_InteractionStack | Proactively detects ambiguity (now **Pydantic-validated**) to pause workflow. | 20 | 25 | 10 | 28 | 15 | **98** | 3 | 1 | 4 | `[VAL]`, `[DI]` (Prompts) |

**v10.3 System-Wide Upgrades (Gap Closure):**

  * **Hybrid RAG (`[HYBRID]`):** RAGStack upgraded from pure vector to Hybrid (Vector + Keyword) search, closing the retrieval quality gap.
  * **Pydantic Validation (`[VAL]`):** All LLM-based stacks now validate 100% of outputs, closing the reliability and parsing gap.
  * **Resilience Patterns (`[RESIL]`):** The entire orchestration graph is now resilient to transient errors via `@exponential_backoff_retry`, and ReAct loops are resilient to tool failures via `CircuitBreaker`s.
  * **Dependency Injection (`[DI]`):** All global singletons are gone. The system is now a true DI application, closing the architecture/testing gap.
  * **Context Budgeting (`[BUDGET]`):** The QAStack is now protected from token limit errors, closing a critical performance gap.

-----

## SECTION 2: DETAILED PIPELINE FLOW (v10.3)

```
+------------------------------------------------------------------------------------------------------------+
| 🚀 v10.3 ASYNC BATCH HARNESS (True DI Root) [DI]                           |
| (Processes jobs with CONTROLLED CONCURRENCY using asyncio.Semaphore)                                       |
|                                                                                                            |
|  (Input) 1. 📂 `batch_queue/` (Contains [job_1.json], [job_2.json], ... [job_N.json])                      |
|                                                                                                            |
| | (Initialize ALL SHARED SERVICES ⚡[DI])                                                                |
| |  (config, redis_client, chromadb_client, prompt_manager, validator, budget_manager, ...)           |
| |                 v                                                                                       |
| |  +--------------------------------------------------------------------------------------------------+    |
| |  | ⚡ **Async Batch Executor with Semaphore** (asyncio.gather)                      |
| |  | (Max concurrent: `max_concurrent_llm_calls` from config)                                          |
| |  |                                                                                                  |    |
| |  | +------------------+ +------------------+ +------------------+ +------------------+               |    |
| |  | | [Async Job 1]    | | [Async Job 2]    | | [Async Job 3]    | | ... [Async Job N]| (Up to 10   |    |
| |  | | (Job-Specific Ctx)| | (Job-Specific Ctx)| | (Job-Specific Ctx)| | (Job-Specific Ctx)| concurrent) |    |
| |  | | (Shared Services)| | (Shared Services)| | (Shared Services)| | (Shared Services)|             |    |
| |  | | await workflow() | | await workflow() | | await workflow() | | await workflow() |             |    |
| |  | +------------------+ +------------------+ +------------------+ +------------------+               |    |
| |  |         |                  |                  |                  |                          |    |
| |  | `-----------------(asyncio.gather with semaphore)-----------------'                          |    |
| |  |                                      v                                                        |
| |  |   2. (finally) Write all results to `batch_summary_v10_3.csv` (Output 1) 📈|
| |  |   3. (finally) Move all job files to `batch_complete/` (Output 2) 🗂️                            |
| |  |   4. (finally) 🧹 **ChromaDB Cleanup (v10.3)**: `collection.delete(where={"workflow_id": ...})` |
| |  |   5. (finally) Log cache stats: "Cache hit rate: 45%" ⚡                     |
| |  +--------------------------------------------------------------------------------------------------+    |
|                                                                                                            |
|                 | (After batch completes)                                                                  |
|                 v                                                                                          |
|  +--------------------------------------------------------------------------------------------------+    |
|  | 🤖 **Automated Async Meta-Learning Trigger** ⚡♾️ [VAL] [DI]           |
|  | (Batch runner *automatically* calls `await run_meta_learning(config)`)                 |
|  +--------------------------------------------------------------------------------------------------+    |
|                                                                                                            |
+------------------------------------------------------------------------------------------------------------+

+ - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -+
|
| ♾️ v10.3 ASYNC AGENTIC META-LEARNING GRAPH ⚡♾️ [VAL]                       |
| (Triggered by `run_batch_v10_3.py` after batch is complete)                  |
| (Uses its own WorkflowContext injected with PromptManager, Validator, etc.)  |
|                                                                                                            |
| 1. `await run_meta_learning(config)` runs (which is a LangGraph app):       |
|    +---------------------------+ (Reads) -> +-------------------------+                                   |
|    | 🤖 **LogReaderAgent** (Python) |            | 📄 `feedback_log.jsonl` |                                   |
|    +---------------------------+            | 📄 `preference_log.jsonl` |                                   |
|                 | (Sends logs)       +-------------------------+                                   |
|                 v                                                                                        |
|    +---------------------------+                                                                         |
|    | 🤖 **AsyncPatternFinderAgent** (Gemini 2.5 Pro / T1) ⚡ (Async + cached + validated [VAL])         |
|    +---------------------------+                                                                         |
|                 | (Sends patterns)                                                                     |
|                 v                                                                                        |
|    +--------------------------------+                                                                    |
|    | 🤖 **AsyncHypothesisGeneratorAgent** (Gemini 2.5 Pro / T1) ⚡ (Async + cached + validated [VAL])  |
|    +--------------------------------+                                                                    |
|                 | (Sends 1 hypothesis)                                                                 |
|                 v                                                                                        |
|    +---------------------------+                                                                         |
|    | 🤖 **AsyncProposalDrafterAgent** (Gemini 2.5 Flash / T2) ⚡ (Async + cached + validated [VAL])      |
|    +---------------------------+                                                                         |
|                 | (Sends proposal)                                                                     |
|                 v                                                                                        |
|    +-----------------------------+                                                                     |
|    | 🤖 **AsyncProposalCritiqueAgent** (Gemini 2.5 Flash / T2) ⚡ (Async + cached + validated [VAL])    |
|    +-----------------------------+                                                                     |
|                 | (Critique Passed?)                                                                   |
|    +------------+--------------+                                                                       |
|    | (No)                      | (Yes)                                                                |
|    v (Loop to Hypothesis)      v                                                                       |
|    (Or loop to Drafter)        +----------------------------------+ (Writes to) -> +---------------------------+ |
|                              | 🤖 **HotReloadRuleManager** ♾️     |              | 📄 `proposed_rules.jsonl` | |
|                              | (Auto-approves high-confidence rules) |              | (File is hot-reloaded)    | |
|                              +----------------------------------+              +---------------------------+ |
+------------------------------------------------------------------------------------------------------------+

                                        |
  v (Each `await workflow.run()` call from async batch executor)

+------------------------------------------------------------------------------------------------------------+
| 🧠 v10.3 FULL ASYNC LANGGRAPH ORCHESTRATION ⚡[RESIL] [VAL] [HYBRID] [DI]        |
| (v10.3: Hybrid RAG, Pydantic Validation, Node Retries, Tool Circuit Breakers, True DI)                     |
|                                                                                                            |
| +---------------------------------------------------------------------------------------------------------+  |
| | 📦 **v10.3 Async LangGraph State Flow** ⚡♾️ [RESIL]                                                     |
| +---------------------------------------------------------------------------------------------------------+  |
| |                                                                                                         |  +----------------------------------+
| | 0. 🧼 **await run_sanitize_pii()** [@retry] (LOCAL Presidio 🔒) |  | 🛡️ **PARALLEL SAFETYGUARDSTACK ♾️** (LOCAL Regex 🔒) |
| |    | (v9.9 security preserved)                                   |  | (Reads dynamic constitution     |
| |    v                                                                                                    |  |  from `proposed_rules.jsonl`) |
| | 1. 🧭 **await run_tot_strategy()** [@retry] (Gemini 2.5 Pro / T1) ⚡♾️ [VAL]                          |  +----------------------------------+
| |    | (Async ToT, cached, feedback-aware, Pydantic validated)     |  +----------------------------------+
| |    | (Writes `StrategyPlan` model to 📋 ModularState)             |  | 💰 **COSTTRACKER (Injected)** [DI] ⚡ |
| |    v                                                                                                    |  +----------------------------------+
| | 2. 🧐 **await run_detect_ambiguity()** [@retry] (Gemini 2.5 Flash / T2) [VAL]                       |  +----------------------------------+
| |    | **AMBIGUITY DETECTED?** |  | 💾 **CACHEMANAGER (Injected)** [DI] ⚡ |
| |    +--------------------------+ (No)                                                                   |  | (Redis-backed LLM cache)|
| |    | (Yes)                     v                                                                       |  +----------------------------------+
| |    '----(Go to Step 8: HIL)   3. 🔍 **await run_rag_stack()** [@retry] (Hybrid Pipeline) ⚡♾️ [HYBRID]    |  +----------------------------------+
| |                              | (Parallel ChromaDB + BM25, merge, rerank)           |  | ♾️ **FEEDBACKLOGREADER (Injected)** [DI] |
| |                              | (Writes `rag_search_results` to 📋 State)                             |  +----------------------------------+
| |                              v                                                                        |  +----------------------------------+
| | 4. ✒️ **await run_generate_bullets()** [@retry] (Mixed T1/T2) ⚡♾️ [VAL]                             |  | ♾️ **PROPOSEDRULESLOADER (Injected)** [DI] |
| |    | (Async, cached, feedback-aware, fact-check validated)      |  +----------------------------------+
| |    | (Writes `generated_bullets` to 📋 State)                                                        |  +----------------------------------+
| |    v                                                                                                    |  | [DI] **PROMPTMANAGER (Injected)** |
| | 5. 🧐 **await run_critique_bullets()** [@retry] (Gemini 2.5 Flash / T2) ⚡ [VAL]                     |  +----------------------------------+
| |    | (Uses `asyncio.gather` for PARALLEL, validated critique)  |  +----------------------------------+
| |    v                                                                                                    |  | [DI] **RESPONSEVALIDATOR (Injected)** |
| |   | **BULLETS PASSED?** [Retry: {bullet_retries}/2]                                                     |  +----------------------------------+
| +-------------------------------------------------+                                                       |  +----------------------------------+
| |    | (Yes)                                    | (No)                                                  |  | [DI] **CONTEXTBUDGETMANAGER (Injected)** |
| +-------------------------------------------------+                                                       |  +----------------------------------+
| |    v                                            v                                                       |
| | 6. ✍️ **await run_drafting()** [@retry] (P1 Conductor) ⚡♾️ [RESIL] [VAL]                          | [ 🔄 **Local Retry: Bullets** ] |
| |    | (ReAct loop with tool-level Circuit Breakers)         | (If bullet_retries < 2, +1 retry)                     |
| |    | (Writes `final_draft` to 📋 State)         '----(Go to Step 4: Bullet Stack)                       |
| |    v                                            '----(Go to 🚨 Global RePlanner)                        |
| | 7. 🛡️ **await run_qa_validation()** [@retry] (P1 Conductor) ⚡♾️ [RESIL] [VAL] [BUDGET]              |
| |    | (ReAct loop w/ Circuit Breakers + Context Budgeting) |
| |    v                                                                                                    |
| |   | **QA PASSED?** [Retry: {qa_retries}/1]                                                              |
| +-------------------------------------------------+                                                       |
| |    | (Yes)                                    | (No)                                                  |
| +-------------------------------------------------+                                                       |
| |    v                                            v                                                       |
| | 8. 🗣️ **await run_feedback_router()** [@retry] (HIL/P1) (Gemini 2.5 Flash / T2) [VAL]             | [ 🔄 **Local Retry: Drafting** ] |
| |    | (Routes HIL feedback, Pydantic validated)                 | (If qa_retries < 1, +1 retry)                         |
| |    v                                            '----(Go to Step 6: Run Drafting)                       |
| | 9. ⏸️ **HIL Pause** (Awaits Human Input) (Human)                                                     | (If qa_retries >= 1)                                  |
| |    v                                            v                                                       |
| | 10. 🗺️ **(Node 8 moved here)** (Feedback Router)                                                   | [ 🚨 **Call Global RePlanner** ] |
| |    | (Logs feedback to `feedback_log.jsonl`) ♾️                                    |
| |    | **ROUTE FEEDBACK?** |                                                                    |
| |    +--------------------------+ (Drafting/Bullets/Strategy)                                            |
| |    | (End)                     v                                                                       |
| |    '----(Go to 🚨 Global RePlanner or 1, 4, 6)   [ ✅ **GOAL MET** ] (End)                            |
| |                                                                                                       |
| +---------------------------------------------------------------------------------------------------------+
+------------------------------------------------------------------------------------------------------------+

                                        |
  | (Graph calls the Strategy (ToT) Node)
                                        v

+------------------------------------------------------------------------------------------------------------+
| 🧭 v10.3 STEP 1: STRATEGY (Validated ToT) ⚡♾️ [VAL] [DI]                                                  |
| (v10.3: All prompts from PromptManager, all outputs Pydantic validated)                                    |
|                                                                                                            |
|    +--------------------------------------------------------------------------------------------------+    |
|    | 📋 **MainGraphState** (Modular Composition) ⚡                                                     |
|    | - strategy: StrategyState (Contains `StrategyPlan` Pydantic model)                             |
|    +--------------------------------------------------------------------------------------------------+    |
|       ^                                                                   ^                            |
|       | (Writes *final* `StrategyPlan` model)                           | (Reads feedback)           |
|       |                                                                   |                            |
|    [ 📄 **JD** ] -> [ 🤖 **AsyncToTStrategistAgent** (Gemini 2.5 Pro / T1) ⚡♾️ [VAL] ] -- [ ♾️ **FeedbackLogReader** ] |
|                 | (Async, cached, prioritizes branches, validates output w/ `StrategyPlan` model) |
|   +-------------+----------------+-----------------+                                                    |
|   | (Strategy A)                   | (Strategy B)                    | (Strategy C)                   |
|   v                                v                               v                              |
| [ 🤖 **StrategyCritique** (Gemini 2.5 Flash / T2) [VAL] ] [ 🤖 **StrategyCritique** (Gemini 2.5 Flash / T2) [VAL] ] [ 🤖 **StrategyCritique** (Gemini 2.5 Flash / T2) [VAL] ] |
| (Async: "Critique A")          (Async: "Critique B")         (Async: "Critique C")         |
|   +-------------+----------------+-----------------+                                                    |
|                 | (Gathers 3 strategies + 3 critiques)                                                 |
|                 v                                                                                      |
|    [ 🤖 **StrategySelectorAgent** (Gemini 2.5 Flash / T2) [VAL] ] (Selects single best one)             |
|                 | (Async call with caching, validated)                                                 |
|                 v (Checks for vagueness)                                                               |
|    [ 🧐 **AmbiguityDetectorAgent (P1)** (Gemini 2.5 Flash / T2) [VAL] ] --(Yes)--> (Route to HIL Stack)  |
|                                                                                                            |
+------------------------------------------------------------------------------------------------------------+

                                        |
  | (Graph calls `run_rag_stack` node)
                                        v

+------------------------------------------------------------------------------------------------------------+
| 🔍 v10.3 STEP 2: ASYNC HYBRID RAG STACK (Parallel) ⚡[HYBRID] [VAL] [Score: 100]                             |
| (v10.3: Replaced ReAct loop with a superior parallel Hybrid RAG pipeline)                                  |
|                                                                                                            |
| 1. [ 🤖 **RAG_SearchAgent (Conductor)** [96] (Python Pipeline) ] ⚡♾️ [HYBRID]                               |
|    | (Async, cached, feedback-aware selection)                                                             |
|    `--(Reads)--> [ ♾️ **FeedbackLogReader** ] (Selects best sub-agents/tools)                                 |
|                                                                                                            |
|    **STEP A: INGEST (Per-Job)** |
|    | (Calls `_ingest_resume_to_chroma_async()`)                                                            |
|    `--(Writes)--> [ 🗄️ **ChromaDB Collection** (Tags docs with `workflow_id`) ]                             |
|                                                                                                            |
|    **STEP B: PARALLEL SEARCH (`asyncio.gather`)** |
|    |                                                                                                      |
|    +--> [ 🔎 **ChromaDBSearchTool (Vector)** ⚡ ] --(Reads)--> [ 🗄️ **ChromaDB** ]                            |
|    |                                                                                                      |
|    +--> [ ⌨️ **BM25SearchTool (Keyword)** ⚡ ] --(Reads)--> [ 📄 **In-Memory Corpus** ]                       |
|    |                                                                                                      |
|    **STEP C: MERGE** |
|    |                                                                                                      |
|    `--> [ 🧬 **Merge & Deduplicate (Python)** ] (Combines Vector + Keyword results)                          |
|    |                                                                                                      |
|    **STEP D: RERANK** |
|    |                                                                                                      |
|    `--> [ 🧐 **AsyncRAG_ReRankerAgent** [80] (Gemini 2.5 Flash / T2) ⚡♾️ [VAL] ]                           |
|        | (Async call with caching, Pydantic validated)                                                    |
|        v                                                                                                  |
|   [ 📜 **Final Reranked List** ] (Writes `experience_bullets` to 📋 State)                                   |
|                                                                                                            |
+------------------------------------------------------------------------------------------------------------+

                                        |
  | (Graph calls `run_bullet_stack` node)
                                        v

+------------------------------------------------------------------------------------------------------------+
| ✒️ v10.3 STEP 3: ASYNC BULLET STACK ⚡♾️ [VAL] [DI] [Score: 100]                                            |
| (v10.3: Fact-Check is now Pydantic validated, prompts from PromptManager)                                  |
|                                                                                                            |
|   [ 🤖 **AsyncBulletGeneratorAgent** [90] (Gemini 2.5 Pro / T1) ⚡♾️ [VAL] ]                            |
|    | (Async, cached, v10.0 fix, prompts from PromptManager)                                          |
|    `--(Reads)--> [ ♾️ **FeedbackLogReader** ] (Selects best generation strategy) |
|                 | (Executes intelligent provenance plan)                                              |
|   +-------------+----------------+-----------------+-------------------------+                           |
|   | (Step 1)                       | (Step 2)                      | (Step 3)                        | (Step 4)                |
|   v                              v                               v                               |
| [ 🐍 **Verbatim** (Python) ] [ 🤖 **Customized** (Gemini 2.5 Pro / T1) ] [ 🤖 **Synthetic** (Gemini 2.5 Pro / T1) ] [ 🤖 **SyntheticFactCheck** (Gemini 2.5 Flash / T2) [VAL] ] |
| (2 Bullets)                      (3 or 2 Bullets) ⚡              (2 Bullets) ⚡                  (Validates output w/ `BulletList` model) ⚡ |
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
| 🧐 v10.3 STEP 4: PARALLEL ASYNC BULLET CRITIQUE ⚡♾️ [VAL] [DI]                                            |
| (v10.3: All critiques are Pydantic validated with `CritiqueResult` model)                                  |
|                                                                                                            |
|   [ 🤖 **AsyncBulletCritiqueAgent** [90] (Gemini 2.5 Flash / T2) ⚡♾️ [VAL] ]                            |
|    | (Receives 5 bullets, prompts from PromptManager)                                                 |
|    `--(Reads)--> [ ♾️ **FeedbackLogReader** ] (Selects best critique model/prompt) |
|                 v                                                                                      |
|   +--------------------------------------------------------------------------------------------------+    |
|   | async def run_async(self, bullets: List[str]):                                                  |
|   |     tasks = [self.critique_single_bullet(b) for b in bullets]                                   |
|   |     responses = await asyncio.gather(*tasks)                                                    |
|   |     # v10.3: Validate all parallel responses                                                    |
|   |     critiques = [self.validator.validate(r['content'], CritiqueResult) for r in responses]      |
|   |     return critiques  # All 5 critiques (now Pydantic models) complete in ~2s                   |
|   +--------------------------------------------------------------------------------------------------+    |
|                                                                                                            |
|   **Performance:** 5 bullets × 2s each = 10s sequential → 2s parallel (v10.0) = **5× FASTER** |
|                                                                                                            |
+------------------------------------------------------------------------------------------------------------+

                                        |
  | (Graph calls `run_drafting_stack` node)
                                        v

+------------------------------------------------------------------------------------------------------------+
| ✍️ v10.3 STEP 5: ASYNC DRAFTING (Conductor + Resilience) ⚡♾️ [RESIL] [VAL] [DI] [Score: 100]                |
| (v10.3: All prompts from PromptManager, all tools have Circuit Breakers and Pydantic Validation)           |
|                                                                                                            |
| [ 🤖 **AsyncDynamicPromptEngineerAgent** [85] (Gemini 2.5 Flash / T2) ⚡♾️ [VAL] ] (Async, cached, validated) |
|    | (Creates custom prompt asynchronously)                                                         |
|    `--(Reads)--> [ ♾️ **FeedbackLogReader** ] (Selects best prompt style)     |
|    v (Sends *Custom-Generated* Prompt)                                                                       |
|   +----------------------------------------------------------------------------------+   |
|   | 🤖 **AsyncDraftingConductorAgent (P1 ReAct)** [95] (Gemini 2.5 Pro / T1) ⚡♾️ [RESIL] |
|   | (P1: ReAct agent. P2: Reads feedback. P3: Tool calls wrapped in Circuit Breakers)  |
|   | (All LLM calls use caching for cost reduction)                                     |
|   +----------------------------------------------------------------------------------+   |
|                 | (Calls experts as tools, step-by-step)                               |
|                 v                                                                      |
|   +----------------------------------------------------------------------------------+   |
|   | 🧑‍🎨 **Pool of Async Drafting Experts (Tools)** ⚡ [RESIL] [VAL]                      |
|   |                                                                                  |   |
|   | * [ 🔌 **CircuitBreaker** ] -> [ ✍️ **Strategist** (Gemini 2.5 Pro / T1) ⚡ [VAL] ] |
|   | * [ 🔌 **CircuitBreaker** ] -> [ 🧐 **RedTeam** (Claude 4.1 Opus / T1) ⚡ [VAL] ] |
|   | * [ 🔌 **CircuitBreaker** ] -> [ 🎨 **Refiner** (GPT-5 / T1) ⚡ [VAL] ]             |
|   | * [ 🔌 **CircuitBreaker** ] -> [ 📊 **MetricsSpecialist** (Gemini 2.5 Flash / T2) ⚡ [VAL] ] |
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
| 🛡️ v10.3 STEP 6: ASYNC QA STACK (Resilience + Validation) ⚡♾️ [RESIL] [VAL] [BUDGET] [DI] [Score: 100]    |
| (v10.3: Circuit Breakers, Pydantic Validation, Context Budgeting, and Centralized Prompts)                 |
|                                                                                                            |
|   +---------------------------------------+  +---------------------------------------+   |
|   | 🤖 **AsyncQAConductorAgent** [95] ⚡♾️ [RESIL] [BUDGET] |  | 📦 **AtomicQASwarmLogic** [5] (Python)  |   |
|   | (Gemini 2.5 Pro / T1)                 |  | (Runs 2 Python checks)                |   |
|   | (P1: ReAct. P2: Reads feedback.)      |  |         |                             |   |
|   | (P3: Tool calls w/ Circuit Breakers)  |  |         v (2 parallel checks)         |   |
|   | (P4: Uses ContextBudgetManager.prune())|  | * 🔢 WordCountValidator [15]        |   |
|   | `--(Reads)--> [ ♾️ **FeedbackLogReader** ]   |  | * 🔣 CharacterCountValidator [15]     |   |
|   |         | (Selects best validators)   |  |                               |   |
|   |         v (Calls `QAPlanCritique` first) |  |                               |   |
|   | [ 🧐 **QAPlanCritiqueAgent** [70] (Gemini 2.5 Flash / T2) ⚡ [VAL] ] |  |                               |   |
|   |         |                             |  +---------------------------------------+   |
|   |         v (Calls experts as tools, all async!)                                           |
|   | **Pool of Async QA Experts (11 LLMs)** ⚡♾️ [RESIL] [VAL]                                  |
|   | (All experts use async clients with caching, Pydantic validation, and Circuit Breakers)    |
|   | * [ 🔌 ]->🗣️ ClaimValidatorAgent (NLI) [75]  (Gemini 2.5 Flash / T2) ⚡ [VAL]             |
|   | * [ 🔌 ]->🎚️ ToneValidator [55] (Gemini 2.5 Flash / T2) ⚡ [VAL]                            |
|   | * [ 🔌 ]->🎯 ThematicAlignment_Validator [80] (Gemini 2.5 Flash / T2) ⚡ [VAL]             |
|   | * [ 🔌 ]->🤝 SemanticEntailmentValidator [70] (Gemini 2.5 Flash / T2) ⚡ [VAL]             |
|   | * [ 🔌 ]->🧵 NarrativeThreadAgent [85] (Gemini 2.5 Flash / T2) ⚡ [VAL]                    |
|   | * [ 🔌 ]->👹 AdversarialReviewerAgent [95] (Claude 4.1 Opus / T1) ⚡ [VAL]               |
|   | * [ 🔌 ]->📍 JDSkillsValidatorAgent [65] (Gemini 2.5 Flash / T2) ⚡ [VAL]                  |
|   | * [ 🔌 ]->📶 SignalScoreValidatorAgent [70] (Gemini 2.5 Flash / T2) ⚡ [VAL]               |
|   | * [ 🔌 ]->⚖️ **BiasDetectorAgent [60] (LOCAL Regex 🔒 + Hot-Reload) ♾️ [VAL]** |
|   | * [ 🔌 ]->🗓️ TenureValidatorAgent [50] (Gemini 2.5 Flash / T2) ⚡ [VAL]                    |
|   | * [ 🔌 ]->🔎 MissedOpportunityAgent [80] (Gemini 2.5 Flash / T2) ⚡ [VAL]                   |
|   +---------------------------------------+----------------------------------------------+   |
|                                                                                                            |
+------------------------------------------------------------------------------------------------------------+
```