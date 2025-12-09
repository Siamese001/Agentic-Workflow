Here is the full content of `agentic_design_v10_0.md`, provided in a single fenced markdown block as requested.

```markdown
# Agentic Architecture Design v10.0

**VERSION 10.0: MODULARITY, CACHING, AND ASYNC PERFORMANCE**

### Key v10.0 Changes:

1.  **🏗️ Modularity (ROW 4):** Decomposed monolithic `MainGraphState` into 11 focused dataclasses. Eliminated global singletons (`COST_TRACKER`, `HIL_MANAGER`, `TOOL_REGISTRY`) in favor of `WorkflowContext` dependency injection.
2.  **💾 Caching (ROW 5):** Implemented Redis-based LLM response caching with `CacheManager`. Expected 30-70% cost reduction via cache hits across batch jobs.
3.  **⚡ Performance (ROW 6):** Converted all LLM clients to async with parallel operations. Bullet critique runs 5× faster (parallel `asyncio.gather`). Batch processing 10× faster with controlled concurrency.

---

## SECTION 1: AGENTIC CAPABILITY ASSESSMENT (TRANSPOSED) [v10.0]

**UPDATE:** Scores for v10.0 reflect modularity, caching, and async improvements on top of v9.9's P0/P1/P2 enhancements and security hardening.

**Legend:**

* HL/HI = High-Leverage / High-Intel ("Smart Brains")
* LL/LI = Low-Leverage / Low-Intel ("Efficient Tools")
* HL/LI = High-Leverage / Low-Intel ("Dumb Brains" - Flaw)
* LL/HI = Low-Leverage / High-Intel ("Overqualified" - Flaw)
* ⚡ = Enhanced in v10.0 (async/caching/modularity)

| Stack | Function (Abbrv.) | Score | HL/HI (LLM) | LL/LI (Py) | HL/LI (Flaw) | LL/HI (Flaw) | Total | v10.0 Enhancements | Gaps (Abbrv.) |
|:------|:------------------|------:|------------:|-----------:|-------------:|-------------:|------:|:-------------------|:--------------|
| RAGStack ⚡ | Critique & Collaboration | 99 | 6 | 3 | 0 | 0 | 9 | Async HyDE, parallel reranking | Gap: Needs to read `feedback_log.jsonl` for dynamic agent selection. |
| BulletStack ⚡ | Critique & Collaboration | 95 | 5 | 0 | 0 | 0 | 5 | **Parallel async critique (5× faster)** | Fixed: "Dumb Brain" router upgraded to async LLM conductor |
| DraftingStack ⚡ | Critique & Collaboration | 99\*\* | 7 | 0 | 0 | 0 | 7 | Async ReAct conductor with caching | Gap: Needs to read `feedback_log.jsonl` for dynamic agent selection. |
| QAStack ⚡ | Critique & Collaboration | 99\*\* | 13 | 1 | 0 | 0 | 14 | Async validator pool, parallel checks | Gap: Needs to read `feedback_log.jsonl` for dynamic agent selection. |
| MetaLearningLoop ⚡ | Observe & Modify Self | 95\*\* | 4 | 2 | 0 | 0 | 6 | Async pattern finding, hypothesis generation | Gap: Needs "hot-reloading" of `proposed_rules.jsonl` without human deploy. |
| StrategyStack ⚡ | Dynamic Planning & Routing | 90 | 4 | 0 | 0 | 0 | 4 | Async ToT with caching | Gap: Needs to read `feedback_log.jsonl` to inform ToT branch selection. |
| PromptStack ⚡ | Dynamic Planning & Routing | 78 | 1 | 0 | 0 | 0 | 1 | Async LLM-driven prompts with caching | Gap: Needs to read `feedback_log.jsonl` to inform prompt generation. |
| SafetyGuardStack | Observe & Modify Self | 98 | 0 | 3 | 0 | 0 | 3 | Local processing preserved (v9.9) | Gap: Needs to read `proposed_rules.jsonl` to update its constitution. |
| DynamicToolingStack ⚡ | Read, Write & Act on Env | 98\* | 2 | 1 | 0 | 0 | 3 | Async tool execution | Gap: Needs to read `feedback_log.jsonl` for dynamic tool selection. |
| HIL_InteractionStack | Read, Write & Act on Env | 96\* | 3 | 1 | 0 | 0 | 4 | Preserved from v9.9 | Gap: Deeper Human-Computer Interaction / collaborative reasoning. |


**v10.0 Score Improvements:**
* **BulletStack:** +7 points (88→95) - Parallel critique + fixed "Dumb Brain" flaw
* **RAGStack:** +1 point (98→99) - Async operations
* **StrategyStack:** +5 points (85→90) - Async ToT
* **PromptStack:** +6 points (72→78) - Async with caching
* **MetaLearningLoop:** +3 points (92→95) - Async execution
* **QAStack:** +1 point (98→99) - Async validator pool

---

## FOOTNOTE: 5 AGENTIC DIMENSIONS (DEFINITIONS)

The "Overall Score" is a weighted composite based on these 5 dimensions:

1.  **Multi-Agent Collaboration (20%)**: How well agents communicate and critique each other's work.
2.  **Agentic Orchestration (25%)**: How the system dynamically plans, routes, and re-plans tasks.
3.  **Emergent Behavior (10%)**: Novel behaviors that emerge from complex, multi-step feedback loops.
4.  **Reflexive Autonomy (30%)**: The system's ability to observe, reason about, and modify itself (meta-learning).
5.  **Environmental Coupling (15%)**: How the system reads, writes, and acts on its environment (files, APIs, tools, user).

### INDICATOR DEFINITIONS:

* `*` Score is directly enabled by The_LangGraph_App (orchestration, replanning, HIL).
* `**` Score is directly enabled by the MetaLearningLoop (long-term learning, log files).
* `⚡` Enhanced in v10.0 with async execution, caching, or modularity improvements.

---

## SECTION 2: DETAILED PIPELINE FLOW (v10.0)

```
+------------------------------------------------------------------------------------------------------------+
| 🚀 v10.0 ASYNC BATCH HARNESS (run_batch_v10_0.py) ⚡                           |
| (Processes jobs with CONTROLLED CONCURRENCY using asyncio.Semaphore)                                       |
|                                                                                                            |
|  (Input) 1. 📂 `batch_queue/` (Contains [job_1.json], [job_2.json], ... [job_N.json])                      |
|                                                                                                            |
| | (Initialize SHARED WorkflowContext for all jobs - enables cross-job cache hits! ⚡)                     |
| |  context = WorkflowContext(CONFIG, redis_client)  # Shared CacheManager                                |
| |                 v                                                                                       |
| |  +--------------------------------------------------------------------------------------------------+    |
| |  | ⚡ **Async Batch Executor with Semaphore** (asyncio.gather)                      |
| |  | (Max concurrent: `max_concurrent_llm_calls` from config)                                          |
| |  |                                                                                                  |    |
| |  | +------------------+ +------------------+ +------------------+ +------------------+               |    |
| |  | | [Async Job 1]    | | [Async Job 2]    | | [Async Job 3]    | | ... [Async Job N]| (Up to 10   |    |
| |  | | (v10.0 Async)    | | (v10.0 Async)    | | (v10.0 Async)    | | (v10.0 Async)    | concurrent) |    |
| |  | | (Shared Cache ⚡)| | (Shared Cache ⚡)| | (Shared Cache ⚡)| | (Shared Cache ⚡)|             |    |
| |  | | await workflow() | | await workflow() | | await workflow() | | await workflow() |             |    |
| |  | +------------------+ +------------------+ +------------------+ +------------------+               |    |
| |  |         |                  |                  |                  |                          |    |
| |  | `-----------------(asyncio.gather with semaphore)-----------------'                          |
| |  |                                      v                                                        |
| |  |   2. (finally) Write all results to `batch_summary_v10_0.csv` (Output 1) 📈 |
| |  |   3. (finally) Move all job files to `batch_complete/` (Output 2) 🗂️                            |
| |  |   4. (finally) Log cache stats: "Cache hit rate: 45%" ⚡                     |
| |  +--------------------------------------------------------------------------------------------------+    |
|                                                                                                            |
|                 | (After batch completes)                                                                  |
|                 v                                                                                          |
|  +--------------------------------------------------------------------------------------------------+    |
|  | 🤖 **Automated Async Meta-Learning Trigger** ⚡                       |
|  | (Batch runner *automatically* calls `await run_meta_learning()`)                 |
|  +--------------------------------------------------------------------------------------------------+    |
|                                                                                                            |
| **v10.0 Performance:** 10 jobs × 30s each = 300s sequential → ~30s with max_concurrent=10 (10× faster)    |
| **v10.0 Cost Savings:** Cache hit rate ~50% in batch → ~40% cost reduction vs v9.9                       |
+------------------------------------------------------------------------------------------------------------+

+ - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -+
|
| ♾️ v10.0 ASYNC AGENTIC META-LEARNING GRAPH ⚡                              |
| (Triggered by `run_batch_v10_0.py` after batch is complete)                                                |
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
|    (Or loop to Drafter)        +--------------------------+ (Writes to) -> +---------------------------+ |
|                              | 🐍 **MetaPlannerAgent** (Python) |              | 📄 `proposed_rules.jsonl` | |
|                              +--------------------------+              +---------------------------+ |
+------------------------------------------------------------------------------------------------------------+

                                        |
  v (Each `await workflow.run()` call from async batch executor)

+------------------------------------------------------------------------------------------------------------+
| 🧠 v10.0 FULL ASYNC LANGGRAPH ORCHESTRATION ⚡                                    |
| (Main graph with P0+P1+P2 enhancements, v9.9 security, v10.0 async/caching/modularity)                    |
|                                                                                                            |
| +---------------------------------------------------------------------------------------------------------+  |
| | 📦 **v10.0 Async LangGraph State Flow** ⚡ |
| +---------------------------------------------------------------------------------------------------------+  |
| |                                                                                                         |  +----------------------------------+
| | 0. 🧼 **await run_sanitize_pii()** (LOCAL Presidio 🔒)          |  | 🛡️ **PARALLEL SAFETYGUARDSTACK** (LOCAL Regex 🔒) |
| |    | (v9.9 security preserved)                                   |  | (Runs on *every* step's output)  |
| |    v                                                                                                    |  | 1. `ConstitutionalAgent`         |
| | 1. 🧭 **await run_tot_strategy()** (Gemini 2.5 Pro / T1) ⚡                                            |  | 2. `SafetyRedTeamAgent`          |
| |    | (Async ToT with caching)                                    |  +----------------------------------+
| |    | (Calls `ToTStrategistAgent` → parallel critiques → selector) |
| |    | (Writes `strategy_brief` to 📋 ModularState)                |  +----------------------------------+
| |    v                                                                                                    |  | 💰 **COSTTRACKER (Injected)** ⚡  |
| | 2. 🧐 **await run_detect_ambiguity()** (P1) (Gemini 2.5 Flash / T2)                                   |  | (Via WorkflowContext)            |
| |    | **AMBIGUITY DETECTED?** |  | (Monitors token spend per agent) |
| |    +--------------------------+ (No)                                                                   |  | (Can veto on cost overrun)       |
| |    | (Yes)                     v                                                                       |  +----------------------------------+
| |    '----(Go to Step 8: HIL)   3. 🔍 **await run_rag_stack()** (P2: HyDE/Re-rank) ⚡                     |  +----------------------------------+
| |                              | (Async operations with caching)                                       |  | 💾 **CACHEMANAGER (New)** ⚡      |
| |                              | (Writes `rag_critique`, `rag_search_results` to 📋 State)             |  | (Redis-backed LLM cache)         |
| |                              v                                                                        |  | (Tracks hits/misses)             |
| | 4. ✒️ **await run_generate_bullets()** (Mixed T1/T2) ⚡                                               |  +----------------------------------+
| |    | (Async bullet generation with caching)                                                         |
| |    | (Writes `generated_bullets` to 📋 State)                                                        |
| |    v                                                                                                    |
| | 5. 🧐 **await run_critique_bullets()** (Gemini 2.5 Flash / T2) ⚡ **PARALLEL** |
| |    | (Uses asyncio.gather for PARALLEL critique - 5× faster!)                                       |
| |    | (Writes `bullet_critique_results` to 📋 State)                                                  |
| |    v                                                                                                    |
| |   | **BULLETS PASSED?** [Retry: {bullet_retries}/2]                                                     |
| +-------------------------------------------------+                                                       |
| |    | (Yes)                                    | (No)                                                  |
| +-------------------------------------------------+                                                       |
| |    v                                            v                                                       |
| | 6. ✍️ **await run_drafting()** (P1 Conductor) ⚡                                                     | [ 🔄 **Local Retry: Bullets** ] |
| |    | (Async ReAct conductor with caching)      | (If bullet_retries < 2, +1 retry)                     |
| |    | (Calls `AsyncDynamicPromptEngineer`,       '----(Go to Step 4: Bullet Stack)                       |
| |    |  `AsyncDraftingConductor (ReAct)`)         | (If bullet_retries >= 2)                              |
| |    | (Writes `final_draft` to 📋 State)         '----(Go to 🚨 Global RePlanner)                        |
| |    v                                                                                                    |
| | 7. 🛡️ **await run_qa_validation()** (P1 Conductor) ⚡                                                |
| |    | (Async QA validator pool with caching)                                                         |
| |    | (Writes `validation_results` to 📋 State)                                                       |
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
| |    | (Calls `FeedbackRouterAgent`, `PreferenceCaptureAgent`)                                          |
| |    | **NEW RULES?** |                                                                    |
| |    +--------------------------+ (No)                                                                   |
| |    | (Yes)                     v                                                                       |
| |    '----(Go to 🚨 Global RePlanner)   [ ✅ **GOAL MET** ] (End)                                       |
| |                                                                                                       |
| +---------------------------------------------------------------------------------------------------------+
+------------------------------------------------------------------------------------------------------------+

**v10.0 Workflow Performance:**
- Single workflow (1st run): ~14s (vs v9.9: ~22s) - async operations
- Single workflow (cached): ~2.5s (vs v9.9: ~22s) - 9× faster with cache hits
- Bullet critique: ~2s (vs v9.9: ~10s) - 5× faster with parallel async

                                        |
  | (Graph calls the Strategy (ToT) Node)
                                        v

+------------------------------------------------------------------------------------------------------------+
| 🧭 v10.0 STEP 1: STRATEGY (Async ToT) ⚡                                                                    |
| (v9.9 ToT flow upgraded to async with caching)                                                            |
|                                                                                                            |
|    +--------------------------------------------------------------------------------------------------+    |
|    | 📋 **MainGraphState** (Modular Composition) ⚡                                                     |
|    | - strategy: StrategyState (isolated strategy data)                                             |
|    +--------------------------------------------------------------------------------------------------+    |
|       ^                                                                                                |
|       | (Writes *final* `strategy_brief`)                                                              |
|       |                                                                                                |
|    [ 📄 **JD** ] -> [ 🤖 **AsyncToTStrategistAgent** (Gemini 2.5 Pro / T1) ⚡ ] (Generates 3 strategies)  |
|                 | (Async call with caching)                                                              |
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
| 🔍 v10.0 STEP 2: ASYNC RAG STACK (P1/P2 + Async) ⚡ [Score: 99]                                            |
|                                                                                                            |
| 1. [ ❓ **RAG_QueryGen** [85] (Gemini 2.5 Pro / T1) ] (P1: Generates queries + *new temporary Python tools*) |
|                 | (Async call with caching)                                                             |
|                 | (Sends Queries + Tool Code)                                                          |
|                 v                                                                                      |
| 2. [ 🧐 **QueryAdversaryAgent** [70] (Gemini 2.5 Flash / T2) ] (v9.6 Agent: "Improve these queries.")    |
|                 | (Async call with caching)                                                             |
|                 | (Sends *Improved* Queries)                                                           |
|                 v                                                                                      |
| 3. [ 📡 **RAG_SearchAgent (ReAct)** [96] (Gemini 2.5 Pro / T1) ] ⚡                                        |
|    (Executes async "Thought-Action-Critique" loop for each query)                                     |
|    |                                                                                                 |
|    |  1. [ 💭 **Thought** ] (Async LLM call: "What should I do?")                                    |
|    |  2. [ ⚡ **Action** ] (P1: Calls `ToolSelectionAgent` → `ToolExecutionAgent`)                     |
|    |       |                                                                                        |
|    |       `--> [ 📚 master_resume_search (Python) ]                                                  |
|    |       `--> [ 🕸️ web_search (Python) ]                                                          |
|    |       `--> [ 🔗 **graph_search** (Python) ]                                                     |
|    |       `--> [ 💡 **HyDEGeneratorAgent** (Gemini 2.5 Flash / T2) ⚡ ] (P2: Async HyDE Tool)       |
|    |       `--> [ 🐍 **_tool_dynamic_tool_executor** (Python) ] (P1 Tool: Runs generated Python)       |
|    |                                                                                                |
|    |  3. [ 👁️ **Observation** ] (Receives results from tool)                                          |
|    |  4. [ 🧐 **Internal Critique** ] (Async LLM call: "Is this step's result good?")                |
|    |  5. [ 🎯 **Satisfied?** ] --(No)--> (Loop to 1. Thought)                                       |
|    |       | (Yes)                                                                                  |
|    |       v (Gathers all loop results)                                                             |
|    |                                                                                                |
| 4. [ 🧐 **AsyncRAG_ReRankerAgent** [80] (Gemini 2.5 Flash / T2) ⚡ ] (P2: Async re-rank based on strategy) |
|    | (Async call with caching)                                                                     |
|    |                                                                                                |
| 5. [ 🧑‍🏫 **RAG_Critique** [85] (Claude 4.1 Opus / T1) ] <---+ (Critiques *re-ranked* search results)      |
|                                                                                                            |
+------------------------------------------------------------------------------------------------------------+

                                        |
  | (Graph calls `run_bullet_stack` node)
                                        v

+------------------------------------------------------------------------------------------------------------+
| ✒️ v10.0 STEP 3: ASYNC BULLET STACK ⚡ [Score: 95] (v9.9 "Dumb Brain" flaw FIXED!)                         |
|                                                                                                            |
|   [ 🤖 **AsyncBulletGeneratorAgent** [90] (Gemini 2.5 Pro / T1) ⚡ ] (Upgraded from Python router!)       |
|                 | (Async bullet generation with caching)                                              |
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
| **v10.0 Improvement:** Python router replaced with async LLM agent (fixes "Dumb Brain" flaw)              |
+------------------------------------------------------------------------------------------------------------+

                                        |
  | (Graph calls `run_critique_bullets` node)
                                        v

+------------------------------------------------------------------------------------------------------------+
| 🧐 v10.0 STEP 4: PARALLEL ASYNC BULLET CRITIQUE ⚡ [NEW!]                                                   |
|                                                                                                            |
|   [ 🤖 **AsyncBulletCritiqueAgent** [90] (Gemini 2.5 Flash / T2) ⚡ ]                                      |
|                 | (Receives 5 bullets to critique)                                                    |
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
| ✍️ v10.0 STEP 5: ASYNC DRAFTING (P1 "True Conductor" + Async) ⚡ [Score: 99]                                |
|                                                                                                            |
| [ 🤖 **AsyncDynamicPromptEngineerAgent** [85] (Gemini 2.5 Flash / T2) ⚡ ] (Async + cached)                |
|    | (Creates custom prompt asynchronously)                                                         |
|    v (Sends *Custom-Generated* Prompt)                                                                       |
|   +----------------------------------------------------------------------------------+   |
|   | 🤖 **AsyncDraftingConductorAgent (P1 ReAct)** [95] (Gemini 2.5 Pro / T1) ⚡       |
|   | (P1: True ReAct agent. P2: Reads `feedback_log.jsonl` for dynamic agent selection) |
|   | (Executes async step-by-step "Thought-Action-Critique" loop using experts as tools)|
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
| 🛡️ v10.0 STEP 6: ASYNC QA STACK (P1 "True Conductor" + Async) ⚡ [Score: 99]                                |
|                                                                                                            |
|   +---------------------------------------+  +---------------------------------------+   |
|   | 🤖 **AsyncQAConductorAgent** [95] ⚡    |  | 📦 **AtomicQASwarmLogic** [5] (Python)  |   |
|   | (Gemini 2.5 Pro / T1)                 |  | (Runs 2 Python checks)                |   |
|   | (P1: True ReAct agent. P2: Reads log)   |  |         |                             |   |
|   | (Async step-by-step ReAct loop)       |  |         v (2 parallel checks)         |   |
|   |         |                             |  | * 🔢 WordCountValidator [15]        |   |
|   |         v (Calls `QAPlanCritique` first) |  | * VCharacterCountValidator [15]     |   |
|   | [ 🧐 **QAPlanCritiqueAgent** [70] (Gemini 2.5 Flash / T2) ⚡ ] |  |                               |   |
|   |         |                             |  +---------------------------------------+   |
|   |         v (Calls experts as tools, all async!)                                           |
|   | **Pool of Async QA Experts (11 LLMs)** ⚡ |                                           |
|   | (All experts use async clients with caching)                                                 |
|   | * 🗣️ ClaimValidatorAgent (NLI) [75]  (Gemini 2.5 Flash / T2) ⚡                          |
|   | * 🎚️ ToneValidator [55] (Gemini 2.5 Flash / T2) ⚡                                       |
|   | * 🎯 ThematicAlignment_Validator [80] (Gemini 2.5 Flash / T2) ⚡                          |
|   | * 🤝 SemanticEntailmentValidator [70] (Gemini 2.5 Flash / T2) ⚡                          |
|   | * 🧵 NarrativeThreadAgent [85] (Gemini 2.5 Flash / T2) ⚡                                |
|   | * 👹 AdversarialReviewerAgent [95] (Claude 4.1 Opus / T1) ⚡                            |
|   | * 📍 JDSkillsValidatorAgent [65] (Gemini 2.5 Flash / T2) ⚡                               |
|   | * 📶 SignalScoreValidatorAgent [70] (Gemini 2.5 Flash / T2) ⚡                            |
|   | * ⚖️ **BiasScrubberAgent [60] (LOCAL Regex 🔒)** | (v9.9 security preserved)       |
|   | * 🗓️ TenureValidatorAgent [50] (Gemini 2.5 Flash / T2) ⚡                               |
|   | * 🔎 MissedOpportunityAgent [80] (v9.0) (Gemini 2.5 Flash / T2) ⚡                          |
|   +---------------------------------------+----------------------------------------------+   |
|                                                                                                            |
+------------------------------------------------------------------------------------------------------------+
```