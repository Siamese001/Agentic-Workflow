(comment
  ;; File: Combined_Agentic_Pipeline_v9_7.clj
  ;; Version: 9.7 (P0-Enhancements: Safety, ToT-Strategy, Dynamic-Prompt)
  ;; This file merges the agentic capability assessment (summary tables)
  ;; with the detailed pipeline flow diagrams, reflecting v9.7 P0 upgrades.

  ;; --------------------------------------------------------------------
  ;; SECTION 1: AGENTIC CAPABILITY ASSESSMENT (PIVOTED SCORES) [v9.7]
  ;; --------------------------------------------------------------------
  ;;
  ;; UPDATE: Scores re-calculated for v9.7.
  ;; StrategyStack & PromptStack scores are now high due to P0 upgrades (ToT & Dynamic Engineering).
  ;; A new SafetyGuardStack has been added as a foundational, parallel component.
  ;;
  ;; Indicators:
  ;; * Score is directly enabled by The_LangGraph_App (orchestration, replanning, HIL).
  ;; ** Score is directly enabled by the MetaLearningLoop (long-term learning, log files).
  ;;
  ;; 1: DraftingStack covers Headline, Exec Summary, Unify Intro, IBM Intro, EY, TraderSense, early career narratives.
  ;; 2: BulletStack only covers bullet point generation for Unify, IBM, and Strategic/Tech Competencies.
+---------------------------------+-----------------------------------------------------------+----------+-------------+---------------+---------+------------------+---------------+-------------+------------------+
| Agentic Dimension               | Function                                                  | RAGStack | BulletStack | DraftingStack | QAStack | MetaLearningLoop | StrategyStack | PromptStack | SafetyGuardStack |
+---------------------------------+-----------------------------------------------------------+----------+-------------+---------------+---------+------------------+---------------+-------------+------------------+
| Multi-Agent Collaboration (20%) | How well agents communicate and critique each other.      | 95       | 90          | 98            | 95      | 95*              | 90            | 80          | 95*              |
| Agentic Orchestration (25%)     | How the system dynamically plans and routes tasks.        | 95*      | 90*         | 98*           | 95*     | 90*              | 95*           | 85*         | 95*              |
| Emergent Behavior (10%)         | Novel behaviors that emerge from complex feedback loops.  | 95       | 80          | 98            | 95      | 80*              | 80            | 70          | 85               |
| Reflexive Autonomy (30%)        | The system's ability to observe and modify itself.        | 98       | 90*         | 100*          | 95*     | 100**            | 80*           | 70*         | 90*              |
| Environmental Coupling (15%)    | How the system reads, writes, and acts on its env.        | 98       | 80          | 95*           | 95**    | 100**            | 70            | 30          | 100**            |
+---------------------------------+-----------------------------------------------------------+----------+-------------+---------------+---------+------------------+---------------+-------------+------------------+
| Overall Score                   | N/A                                                       | 96       | 88          | 98            | 95      | 92**             | 85            | 72          | 93               |
+---------------------------------+-----------------------------------------------------------+----------+-------------+---------------+---------+------------------+---------------+-------------+------------------+
)

(comment
  ;; ---------------------------------------------------
  ;; SECTION 2: AGENT DEFINITIONS TABLE (v9.7)
  ;; ---------------------------------------------------

+-------------+-----------------------+-----------------------------+------------------------------+---------------------------------+--------+-----------+-----------------------+--------------------+--------------------+-------------------------+
| Step        | Purpose               | Component                   | Agent Name                   | Intelligence Required (0-100) | ReAct? | Company   | Intelligence Tier     | Internal API Calls | External API Calls | Model Name              |
+-------------+-----------------------+-----------------------------+------------------------------+---------------------------------+--------+-----------+-----------------------+--------------------+--------------------+-------------------------+
| 0. Safety   | "Is it safe?"         | PII Scrubber (v9.6)         | PIISanitizerAgent            | 5 (Low)                         | N      | N/A       | N/A (Python)          | 1 (scrubs state)   | 0                  | N/A (Python)            |
| (Parallel)  |                       | Constitutional Guardrail    | ConstitutionalAgent          | 90 (Expert)                     | Y      | Anthropic | Tier 1 (Flagship)     | 0                  | 5 (1 per step)     | Claude 4.1 Opus         |
|             |                       | Safety Red Team             | SafetyRedTeamAgent           | 95 (Expert)                     | Y      | Anthropic | Tier 1 (Flagship)     | 0                  | 2 (Probing)        | Claude 4.1 Opus         |
+-------------+-----------------------+-----------------------------+------------------------------+---------------------------------+--------+-----------+-----------------------+--------------------+--------------------+-------------------------+
| 1. Strategy | "What's the plan?"    | ToT Strategy Generator      | StrategyGeneratorAgent (ToT) | 90 (Expert)                     | N      | Google    | Tier 1 (Flagship)     | 0                  | 3 (Branches)       | Gemini 2.5 Pro          |
| (v9.7 ToT)  |                       | ToT Strategy Critique       | StrategyCritiqueAgent (x3)   | 85 (Very High)                  | N      | Google    | Tier 2 (Workhorse)    | 0                  | 3 (Parallel)       | Gemini 2.5 Flash        |
|             |                       | ToT Strategy Selector       | StrategySelectorAgent        | 80 (Very High)                  | N      | Google    | Tier 2 (Workhorse)    | 0                  | 1 (Selects best)   | Gemini 2.5 Flash        |
+-------------+-----------------------+-----------------------------+------------------------------+---------------------------------+--------+-----------+-----------------------+--------------------+--------------------+-------------------------+
| 2. RAG      | "What are the facts?" | RAG_QueryGen                | RAG_QueryGeneratorAgent      | 75 (High)                       | N      | Google    | Tier 1 (Flagship)     | 0                  | 1                  | Gemini 2.5 Pro          |
|             |                       | QueryAdversaryAgent         | QueryAdversaryAgent          | 70 (High)                       | N      | Google    | Tier 2 (Workhorse)    | 0                  | 1                  | Gemini 2.5 Flash        |
|             |                       | RAG_SearchAgent (ReAct)     | RAG_SearchAgent (Brain)      | 95 (Expert)                     | Y      | Google    | Tier 1 (Flagship)     | 0                  | 5 (Thought+Critique)| Gemini 2.5 Pro          |
|             |                       | RAG_Tool_1 (Tool)           | _tool_master_resume_search   | 0 (Low)                         | N      | N/A       | N/A (Python)          | 1 (to resume)      | 0                  | N/A (Python)            |
|             |                       | RAG_Tool_2 (Tool)           | _tool_graph_search           | 0 (Low)                         | N      | N/A       | N/A (Python)          | 1 (to graph db)    | 0                  | N/A (Python)            |
|             |                       | RAG_Critique                | RAG_CritiqueAgent            | 85 (Very High)                  | N      | Anthropic | Tier 1 (Flagship)     | 0                  | 1                  | Claude 4.1 Opus         |
+-------------+-----------------------+-----------------------------+------------------------------+---------------------------------+--------+-----------+-----------------------+--------------------+--------------------+-------------------------+
| 3. Drafting | "Write the story."    | Dynamic Prompt Engineer     | DynamicPromptEngineerAgent   | 85 (Expert)                     | N      | Google    | Tier 2 (Workhorse)    | 1 (assembles state)| 1                  | Gemini 2.5 Flash        |
|             |                       | Bullet Stack (v8)           | ProvenanceRouterAgent        | 80 (Very High)                  | N      | N/A       | N/A (Python Router)   | 3 (calls experts)  | 0                  | N/A (Python)            |
|             |                       |                             | CustomizedBulletDrafter      | 70 (High)                       | N      | Google    | Tier 1 (Flagship)     | 0                  | 1                  | Gemini 2.5 Pro          |
|             |                       |                             | SyntheticBulletDrafter       | 85 (Very High)                  | N      | Google    | Tier 1 (Flagship)     | 0                  | 1                  | Gemini 2.5 Pro          |
|             |                       |                             | SyntheticFactCheckAgent      | 70 (High)                       | N      | Google    | Tier 2 (Workhorse)    | 0                  | 1                  | Gemini 2.5 Flash        |
|             |                       | Bullet Critique (v9)        | BulletCritiqueAgent          | 80 (Very High)                  | N      | Google    | Tier 2 (Workhorse)    | 0                  | 1                  | Gemini 2.5 Flash        |
|             |                       | Drafting Stack (v8)         | DraftingConductorAgent       | 90 (Expert)                     | Y      | Google    | Tier 1 (Flagship)     | 0                  | 1 (Plan) + 3 (Exec)| Gemini 2.5 Flash        |
|             |                       | (Expert)                    | Strategist (Gemini)          | 95 (Expert)                     | N      | Google    | Tier 1 (Flagship)     | 0                  | 1                  | Gemini 2.5 Pro          |
|             |                       | (Expert)                    | RedTeam (Claude)             | 95 (Expert)                     | N      | Anthropic | Tier 1 (Flagship)     | 0                  | 1                  | Claude 4.1 Opus         |
|             |                       | (Expert)                    | Refiner (GPT-5)              | 100 (Expert)                    | N      | OpenAI    | Tier 1 (Flagship)     | 0                  | 1                  | GPT-5                   |
|             |                       | (Expert)                    | MetricsSpecialistAgent       | 75 (High)                       | N      | Google    | Tier 2 (Workhorse)    | 0                  | 1                  | Gemini 2.5 Flash        |
|             |                       | SC Paths                    | WorkflowRePlannerAgent       | 90 (Expert)                     | Y      | Anthropic | Tier 1 (Flagship)     | 0                  | 1                  | Claude 4.1 Opus         |
+-------------+-----------------------+-----------------------------+------------------------------+---------------------------------+--------+-----------+-----------------------+--------------------+--------------------+-------------------------+
| 4. QA       | "Is it correct?"      | QA Stack (v8)               | QAConductorAgent             | 90 (Expert)                     | Y      | Google    | Tier 1 (Flagship)     | 0                  | 1 (Plan) + 5 (Exec)| Gemini 2.5 Flash        |
|             |                       | QAPlanCritiqueAgent         | QAPlanCritiqueAgent          | 70 (High)                       | N      | Google    | Tier 2 (Workhorse)    | 0                  | 1                  | Gemini 2.5 Flash        |
|             |                       | (Expert)                    | ClaimValidatorAgent          | 75 (High)                       | N      | Google    | Tier 2 (Workhorse)    | 0                  | 1                  | Gemini 2.5 Flash        |
|             |                       | (Expert)                    | AdversarialReviewerAgent     | 95 (Expert)                     | N      | Anthropic | Tier 1 (Flagship)     | 0                  | 1                  | Claude 4.1 Opus         |
|             |                       | (Expert)                    | MissedOpportunityAgent       | 80 (Very High)                  | N      | Google    | Tier 2 (Workhorse)    | 0                  | 1                  | Gemini 2.5 Flash        |
|             |                       | (Expert)                    | BiasScrubberAgent            | 60 (Medium)                     | N      | Google    | Tier 2 (Workhorse)    | 0                  | 1                  | Gemini 2.5 Flash        |
|             |                       | Atomic QA Swarm (Logic)     | AtomicQASwarmLogic           | 5 (Low)                         | N      | N/A       | N/A (Python)          | 2 (1 per check)    | 0                  | N/A (Python)            |
+-------------+-----------------------+-----------------------------+------------------------------+---------------------------------+--------+-----------+-----------------------+--------------------+--------------------+-------------------------+
| 5. HIL      | "Is it approved?"     | HIL Pause (LangGraph)       | human_review_pause           | N/A (Human)                     | N/A    | N/A       | N/A (Human)           | 1 (to console)     | 0                  | N/A (Human)             |
|             |                       | HIL Learning                | PreferenceCaptureAgent       | 60 (Medium)                     | N      | Google    | Tier 2 (Workhorse)    | 1 (diffs state)    | 1                  | Gemini 2.5 Flash        |
+-------------+-----------------------+-----------------------------+------------------------------+---------------------------------+--------+-----------+-----------------------+--------------------+--------------------+-------------------------+
| 6. Meta-Learning | "How do we improve?" | MetaLearningGraph | LogReaderAgent               | 0 (Low)                         | N      | N/A       | N/A (Python)          | 2 (reads logs)     | 0                  | N/A (Python)            |
|             |                       |                             | PatternFinderAgent (LLM)     | 75 (High)                       | N      | Google    | Tier 2 (Workhorse)    | 0                  | 1                  | Gemini 2.5 Flash        |
|             |                       |                             | HypothesisGeneratorAgent     | 80 (Very High)                  | N      | Google    | Tier 2 (Workhorse)    | 0                  | 1                  | Gemini 2.5 Flash        |
|             |                       |                             | ProposalDrafterAgent         | 70 (High)                       | N      | Google    | Tier 2 (Workhorse)    | 0                  | 1                  | Gemini 2.5 Flash        |
|             |                       |                             | ProposalCritiqueAgent        | 85 (Very High)                  | N      | Google    | Tier 2 (Workhorse)    | 0                  | 1                  | Gemini 2.5 Flash        |
|             |                       |                             | MetaPlannerAgent (Python)    | 5 (Low)                         | N      | N/A       | N/A (Python)          | 1 (writes proposal)| 0                  | N/A (Python)            |
+-------------+-----------------------+-----------------------------+------------------------------+---------------------------------+--------+-----------+-----------------------+--------------------+--------------------+-------------------------+
| Total       |                       |                             |                              |                                 |        |           |                       | 17 Calls           | 41 Calls           |                         |
+-------------+-----------------------+-----------------------------+------------------------------+---------------------------------+--------+-----------+-----------------------+--------------------+--------------------+-------------------------+
)

(comment
  ;; ---------------------------------------------------
  ;; SECTION 3: DETAILED PIPELINE FLOW (v9.7)
  ;; ---------------------------------------------------

  +------------------------------------------------------------------------------------------------------------+
  | 🚀 v9.7 PARALLEL BATCH HARNESS (run_batch_v9_7.py)                                                        |
  | (Processes all jobs in parallel using a ProcessPoolExecutor)                                     |
  |                                                                                                            |
  |  (Input) 1. 📂 `batch_queue/` (Contains [job_1.json], [job_2.json], ... [job_N.json])             |
  |                                                                                                            |
  | | (Spawns `max_parallel_workers` (e.g., 8) via ProcessPoolExecutor)                               |
  | |                 v                                                                                       |
  | |  +--------------------------------------------------------------------------------------------------+    |
  | |  | 🌀 **Parallel Executor (`concurrent.futures`)** |    |
  | |  | (Each job runs in its own `process_single_job` function)                                 |
  | |  |                                                                                                  |    |
  | |  | +------------------+ +------------------+ +------------------+ +------------------+               |
  | |  | | [Run Job 1] | | [Run Job 2] | | [Run Job 3] | | ... [Run Job N] | (All run     |    |
  | |  | | (v9.0 Cost Check) | | (v9.0 Cost Check) | | (v9.0 Cost Check) | | (v9.0 Cost Check) | simultaneously)|
  | |  | | (try/catch) | | (try/catch) | | (try/catch) | | (try/catch) |               |    |
  | |  | | `workflow.run()` | |  `workflow.run()` | |  `workflow.run()` | |  `workflow.run()` |               |    |
  | |  | +------------------+ +------------------+ +------------------+ +------------------+               |    |
  | |  |         |                  |                  |                  |                          |    |
  | |  | `-----------------(Collects all results when complete)-----------------'                 |
  | |  |                                      v                                                        |
  | |  |   2. (finally) Write all results to `batch_summary_v9_7.csv` (Output 1) 📈            |
  | |  |   3. (finally) Move all job files to `batch_complete/` (Output 2) 🗂️                   |
  | |  +--------------------------------------------------------------------------------------------------+    |
  |                                                                                                            |
  |                 | (After batch completes)                                                         |
  |                 v                                                                                          |
  |  +--------------------------------------------------------------------------------------------------+    |
  |  | 🤖 **Automated Meta-Learning Trigger** |    |
  |  | (Batch runner *automatically* calls `run_learning_v9_7.py`)                             |
  |  +--------------------------------------------------------------------------------------------------+    |
  |                                                                                                            |
  + - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -+
  |
  | ♾️ v9.7 AGENTIC META-LEARNING GRAPH (v9.6 Upgrade)                                              |
  | (Triggered by `run_batch_v9_7.py` after batch is complete)                                     |
  | (This replaces the simple v9.5 script with a full, robust agentic graph)                                   |
  |                                                                                                            |
  | 1. `run_learning_v9_7.py` runs (which is a LangGraph app):                                      |
  |    +---------------------------+ (Reads) -> +-------------------------+                                   |
  |    | 🤖 **LogReaderAgent** |            | 📄 `feedback_log.jsonl` |                                   |
  |    +---------------------------+            | 📄 `preference_log.jsonl` |                                   |
  |                 | (Sends logs)       +-------------------------+                                   |
  |                 v                                                                                        |
  |    +---------------------------+                                                                         |
  |    | 🤖 **PatternFinderAgent** (LLM) | (Finds patterns)                            |
  |    +---------------------------+                                                                         |
  |                 | (Sends patterns)                                                         |
  |                 v                                                                                        |
  |    +--------------------------------+                                                                    |
  |    | 🤖 **HypothesisGeneratorAgent** (LLM) | (Generates root causes)               |
  |    +--------------------------------+                                                                    |
  |                 | (Sends 1 hypothesis)                                                     |
  |                 v                                                                                        |
  |    +---------------------------+                                                                         |
  |    | 🤖 **ProposalDrafterAgent** (LLM) | (Drafts JSON change)                      |
  |    +---------------------------+                                                                         |
  |                 | (Sends proposal)                                                         |
  |                 v                                                                                        |
  |    +-----------------------------+                                                                     |
  |    | 🤖 **ProposalCritiqueAgent** (LLM) | (Adversarial review)                  |
  |    +-----------------------------+                                                                     |
  |                 | (Critique Passed?)                                                       |
  |    +------------+--------------+                                                                       |
  |    | (No)          | (Yes)                                                    |
  |    v (Loop to Hypothesis) v                                                                |
  |    (Or loop to Drafter) +--------------------------+ (Writes to) -> +---------------------------+ |
  |                              | 🐍 **MetaPlannerAgent** (Py) |              | 📄 `proposed_rules.jsonl` | |
  |                              +--------------------------+              +---------------------------+ |
  +------------------------------------------------------------------------------------------------------------+

                                        |
  v (Each `workflow.run()` call from a parallel thread)

  +------------------------------------------------------------------------------------------------------------+
  | 🧠 v9.7 P0-ENHANCED LANGGRAPH ORCHESTRATION (P0 Upgrades: Safety, ToT-Strategy, Dynamic-Prompt, Local-Retries) |
  | (The main graph now has a parallel SafetyGuard and local retry loops for efficiency)                         |
  |                                                                                                            |
  | +---------------------------------------------------------------------------------------------------------+  |
  | | 📦 **v9.7 LangGraph State Flow** |
  | +---------------------------------------------------------------------------------------------------------+  |
  | |                                                                                                         |
  | | 0. 🧼 **Run PII Scrubber** (Calls `PIISanitizerAgent` on `master_resume` and `job_input`)                 |  +----------------------------------+
  | |    v                                                                                                    |  | 🛡️ **PARALLEL SAFETYGUARDSTACK** |
  | | 1. 🧭 **Run Strategy (ToT)** |  | (Runs on *every* step's output)  |
  | |    | (Calls `StrategyGeneratorAgent` -> 3 parallel `StrategyCritiqueAgent`s -> `StrategySelectorAgent`) |  | 1. `ConstitutionalAgent`         |
  | |    | (Writes `strategy_brief` to 📋 State)                                                             |  | 2. `SafetyRedTeamAgent`          |
  | |    v                                                                                                    |  | (Can veto graph at any time)     |
  | | 2. 🔍 **Run RAG Stack** (Calls `RAG_QueryGen`, `QueryAdversaryAgent`, `RAG_SearchAgent`, `RAG_Critique`) |  +----------------------------------+
  | |    | (Writes `rag_critique`, `rag_search_results` to 📋 State)                              |
  | |    v                                                                                                    |
  | | 3. ✒️ **Run Bullet Stack** (Calls `ProvenanceRouterAgent` & `SyntheticFactCheckAgent`)       |
  | |    | (Writes `generated_bullets` to 📋 State)                                               |
  | |    v                                                                                                    |
  | | 4. 🧐 **Run Bullet Critique** (Calls `BulletCritiqueAgent`)                                     |
  | |    | (Writes `bullet_critique_results` to 📋 State)                                          |
  | |    v                                                                                                    |
  | |   | **BULLETS PASSED?** [Retry: {bullet_retries}/2] |                                     |
  | +-------------------------------------------------+                                                       |
  | |    | (Yes)                         | (No)                                      |
  | +-------------------------------------------------+                                                       |
  | |    v                                            v                                                       |
  | | 5. ✍️ **Run Drafting** [ 🔄 **Local Retry: Bullets** ]                         |
  | |    | (Calls `DynamicPromptEngineerAgent`,       | (If bullet_retries < 2, +1 retry)                     |
  | |    |  `DraftingConductorAgent`)     '----(Go to Step 3: Bullet Stack)                       |
  | |    | (Writes `final_draft` to 📋 State) | (If bullet_retries >= 2)                              |
  | |    v                                            '----(Go to 🚨 Global RePlanner)             |
  | | 6. 🛡️ **Run QA Stack** (Calls `QAConductor`, `QAPlanCritique`, `AtomicQASwarmLogic`)         |
  | |    | (Writes `validation_results` to 📋 State)                                            |
  | |    v                                                                                                    |
  | |   | **QA PASSED?** [Retry: {qa_retries}/1] |                                              |
  | +-------------------------------------------------+                                                       |
  | |    | (Yes)                         | (No)                                      |
  | +-------------------------------------------------+                                                       |
  | |    v                                            v                                                       |
  | | [ ✅ **GOAL MET** ] (Go to HIL/End)   [ 🔄 **Local Retry: Drafting** ]                        |
  | |                                               | (If qa_retries < 1, +1 retry)                         |
  | |                                               '----(Go to Step 5: Run Drafting)                       |
  | |                                               | (If qa_retries >= 1)                                  |
  | |                                               v                                                       |
  | |                                               [ 🚨 **Call Global RePlanner** ] (Calls `WorkflowRePlannerAgent`) |
  | |                                                  | (Plan: "Requires new facts?")            |
  | |                                                  |   | (Yes) -> (Go to Step 2: RAG)        |
  | |                                                  |   | (No)  -> (Go to Step 3: Bullet Stack) |
  | |                                                  +------------------------------------------------------+
  | +---------------------------------------------------------------------------------------------------------+
  +------------------------------------------------------------------------------------------------------------+

                                        |
  | (Graph calls the Strategy (ToT) Node)
                                        v

  +------------------------------------------------------------------------------------------------------------+
  | 🧭 v9.7 STEP 1: STRATEGY (P0 Tree-of-Thoughts Upgrade)                                                      |
  | (Replaces the simple v9.5 `ThemeClassifierAgent`)                                                |
  |                                                                                                            |
  |    +--------------------------------------------------------------------------------------------------+    |
  |    | 📋 **GraphState** (Shared State)                                                      |
  |    +--------------------------------------------------------------------------------------------------+    |
  |       ^                                                                                                |
  |       | (Writes *final* `strategy_brief`)                                                   |
  |       |                                                                                                |
  |    [ 📄 **JD** ] -> [ 🤖 **StrategyGeneratorAgent (ToT)** ] (LLM Call: "Generate 3 distinct strategies")     |
  |                 |                                                                                      |
  |   +-------------+----------------+-----------------+                                                    |
  |   | (Strategy A)                   | (Strategy B)                    | (Strategy C)                   |
  |   v                                v                               v                              |
  | [ 🤖 **StrategyCritique** ]        [ 🤖 **StrategyCritique** ]       [ 🤖 **StrategyCritique** ]      |
  | (LLM Call: "Critique A")       (LLM Call: "Critique B")      (LLM Call: "Critique C")      |
  |   +-------------+----------------+-----------------+                                                    |
  |                 | (Gathers 3 strategies + 3 critiques)                                                 |
  |                 v                                                                                      |
  |    [ 🤖 **StrategySelectorAgent** ] (LLM Call: "Review all 6 items and select the single best one")       |
  |                                                                                                            |
  +------------------------------------------------------------------------------------------------------------+

                                        |
  | (Graph calls `run_rag_stack` node)
                                        v

  +------------------------------------------------------------------------------------------------------------+
  | 🔍 v9.7 STEP 2: RAG STACK (v9.6 Adversarial Upgrade) [Score: 96]                                 |
  |                                                                                                            |
  | 1. [ ❓ **RAG_QueryGen** [75] ] (Tier 1: Gemini 2.5 Pro)                                        |
  |                 | (Sends Queries)                                                           |
  |                 v                                                                                      |
  | 2. [ 🧐 **QueryAdversaryAgent** [70] ] (v9.6 Agent: "Are these queries good? Output better ones.")         |
  |                 | (Sends *Improved* Queries)                                                           |
  |                 v                                                                                      |
  | 3. [ 📡 **RAG_SearchAgent (ReAct)** [96] ] (Tier 1: Gemini 2.5 Pro)                         |
  |    (Executes "Thought-Action-Critique" loop for each query)                                |
  |    |                                                                                                 |
  |    |  1. [ 💭 **Thought** ] (LLM call: "What should I do?")                                  |
  |    |  2. [ ⚡ **Action** ] (LLM call: "Select a tool")                                      |
  |    |       |                                                                                        |
  |    |       `--> [ 📚 master_resume_search ] (Vector Tool)                                  |
  |    |       `--> [ 🕸️ web_search ] (External Tool)                                         |
  |    |       `--> [ 🔗 **graph_search** ] (v9.0 Graph Tool)                                  |
  |    |       `--> [ ✍️ **write_to_graph** ] (v9.0 Graph Tool)                                |
  |    |                                                                                                |
  |    |  3. [ 👁️ **Observation** ] (Receives results from tool)                                |
  |    |  4. [ 🧐 **Internal Critique** ] (LLM call: "Is this step's result good?")             |
  |    |  5. [ 🎯 **Satisfied?** ] --(No)--> (Loop to 1. Thought)                               |
  |    |       | (Yes)                                                                        |
  |    |       v (Gathers all loop results)                                                   |
  |    |                                                                                                |
  | 4. [ 🧑‍🏫 **RAG_Critique** [85] ] (Tier 1: Claude 4.1 Opus) <---+ (Critiques *final* search results) |
  |                                                                                                            |
  +------------------------------------------------------------------------------------------------------------+

                                        |
  | (Graph calls `run_bullet_stack` node)
                                        v

  +------------------------------------------------------------------------------------------------------------+
  | ✒️ v9.7 STEP 3: BULLET STACK (v9.6 Adversarial Upgrade) [Score: 88]                             |
  |                                                                                                            |
  |   [ 🤖 **ProvenanceRouterAgent** [80] (MoE Router) ] (Reads Strategy: "Unify" -> 2/3/2, "IBM" -> 2/2/2) |
  |                 | (Executes 4-step provenance plan sequentially)                                   |
  |   +-------------+----------------+-----------------+-------------------------+                           |
  |   | (Step 1) | (Step 2) | (Step 3) | (Step 4)                |
  |   v         v            v         v                         |
  | [ 🐍 **Verbatim** ] [ 🤖 **Customized** ]   [ 🤖 **Synthetic** ]    [ 🤖 **SyntheticFactCheck** ] |
  | (Python)  (LLM)      (LLM)     (v9.6 Agent: "Is this plausible?") |
  | (2 Bullets) (3 or 2 Bullets) (2 Bullets)   (Filters out hallucinations) |
  |   +-------------+----------------+-----------------+-------------------------+                           |
  |                 | (Gathers all *fact-checked* bullets)                                     |
  |                 v                                                                                      |
  |   [ 📜 **Final Bullet List** ] (Writes `generated_bullets` to 📋 State)                         |
  |                                                                                                            |
  +------------------------------------------------------------------------------------------------------------+

                                        |
  | (Graph calls `run_drafting_stack` node)
                                        v

  +------------------------------------------------------------------------------------------------------------+
  | ✍️ v9.7 STEP 5: DRAFTING (P0 Dynamic Prompt Upgrade) [Score: 98]                                |
  |                                                                                                            |
  | [ 🤖 **DynamicPromptEngineerAgent** [85] (LLM-based) ] (Replaces v9.5 `PromptStackAgent`)     |
  |    | (Receives RAG context + Bullets + Strategy)                                                         |
  |    | (LLM Call: "Write the perfect, custom prompt for the drafting team based on this context")           |
  |    |                                                                                                    |
  |    v (Sends *Custom-Generated* Prompt)                                                      |
  |   +----------------------------------------------------------------------------------+   |
  |   | 🤖 **DraftingConductorAgent (MoE)** [90] (Tier 2: Gemini 2.5 Flash) |
  |   | (LLM call: "Create a dynamic plan from these experts")                 |
  |   +----------------------------------------------------------------------------------+   |
  |                 | (Executes dynamic plan, e.g., [Strategist, MetricsSpecialist, Refiner]) |
  |                 v                                                                    |
  |   +----------------------------------------------------------------------------------+   |
  |   | 🧑‍🎨 **Pool of Drafting Experts (LLMs)** |   |
  |   |                                                                                  |   |
  |   | * [ ✍️ **Strategist (Gemini 2.5 Pro)** [95] ] (Writes initial draft) |
  |   | * [ 🧐 **RedTeam (Claude 4.1 Opus)** [95] ] (Writes critique)          |
  |   | * [ 🎨 **Refiner (GPT-5)** [100] ] (Writes final draft)               |
  |   | * [ 📊 **MetricsSpecialist (Flash)** [75] ] (v9.0: Injects/Fixes metrics) |
  |   +----------------------------------------------------------------------------------+   |
  |                 | (Final artifact from plan)                               |
  |                 v                                                                    |
  |   [ 📜 **final_draft** ] (Writes to 📋 State)                             |
  |                                                                                      |
  +------------------------------------------------------------------------------------------------------------+

                                        |
  | (Graph calls `run_qa_swarm` node as final validation)
                                        v

  +------------------------------------------------------------------------------------------------------------+
  | 🛡️ v9.7 STEP 6: QA STACK (v9.6 Adversarial Upgrade) [Score: 95]                                 |
  |                                                                                                            |
  |   +---------------------------------------+  +---------------------------------------+   |
  |   | 🤖 **QAConductorAgent (MoE)** [90]  |  | 📦 **AtomicQASwarmLogic** [5] (Python) |   |
  |   | (LLM Call: "Which checks should I run?") |  | (Runs 2 Python checks)      |   |
  |   |         |                             |  |         |                   |   |
  |   |         v (Sends plan to)     |  |         v (2 parallel checks) |   |
  |   | [ 🧐 **QAPlanCritiqueAgent** [70] ]   |  | * 🔢 WordCountValidator [15]  |   |
  |   | (v9.6 Agent: "Is this plan smart?") |  | * 🔣 CharacterCountValidator [15] |   |
  |   |         |                             |  |                                       |   |
  |   |         v (Dynamically selects from:) |  +---------------------------------------+   |
  |   | **Pool of QA Experts (11 LLMs)** |                                      |
  |   | (Code-Corrected w/ Config Scores) |                                      |
  |   | * 🗣️ ClaimValidatorAgent (NLI) [75] |                                      |
  |   | * 🎚️ ToneValidator [55]             |                                      |
  |   | * 🎯 ThematicAlignment_Validator [80] |                                      |
  |   | * 🤝 SemanticEntailmentValidator [70] |                                      |
  |   | * 🧵 NarrativeThreadAgent [85]      |                                      |
  |   | * 👹 AdversarialReviewerAgent [95]  |                                      |
  |   | * 📍 JDSkillsValidatorAgent [65]     |                                      |
  |   | * 📶 SignalScoreValidatorAgent [70]   |                                      |
  |   | * ⚖️ BiasScrubberAgent [60]         |                                      |
  |   | * 🗓️ TenureValidatorAgent [50]      |                                      |
  |   | * 🔎 **MissedOpportunityAgent** [80] (v9.0) |                                |
  |   +---------------------------------------+----------------------------------------------+   |
  |                                                                                                            |
  +------------------------------------------------------------------------------------------------------------+
)