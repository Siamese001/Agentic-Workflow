(comment
  ;; File: Combined_Agentic_Pipeline_v9_6.clj
  ;; Version: 9.6 (Adversarial-Meta)
  ;; This file merges the agentic capability assessment (summary tables)
  ;; with the detailed pipeline flow diagrams.
  ;;
  ;; --------------------------------------------------------------------
  ;; SECTION 1: AGENTIC CAPABILITY ASSESSMENT (PIVOTED SCORES) [v9.6]
  ;; --------------------------------------------------------------------
  ;;
  ;; UPDATE: Scores re-calculated for v9.6.
  ;; DraftingStack & QAStack scores are high due to dynamic MoE Conductors.
  ;; MetaLearningLoop score is now 92 due to re-architecture as an agentic graph.
  ;;
  ;; Indicators:
  ;; * Score is directly enabled by The_LangGraph_App (orchestration, replanning, HIL).
  ;; ** Score is directly enabled by the MetaLearningLoop (long-term learning, log files).
  ;;
  ;; 1: DraftingStack covers Headline, Exec Summary, Unify Intro, IBM Intro, EY, TraderSense, early career narratives.
  ;; 2: BulletStack only covers bullet point generation for Unify, IBM, and Strategic/Tech Competencies.
+---------------------------------+-----------------------------------------------------------+----------+-------------+---------------+---------+------------------+---------------+-------------+
| Agentic Dimension               | Function                                                  | RAGStack | BulletStack | DraftingStack | QAStack | MetaLearningLoop | StrategyStack | PromptStack |
+---------------------------------+-----------------------------------------------------------+----------+-------------+---------------+---------+------------------+---------------+-------------+
| Multi-Agent Collaboration (20%) | How well agents communicate and critique each other.      | 95       | 90          | 98            | 95      | 95*              | 0             | 0           |
| Agentic Orchestration (25%)     | How the system dynamically plans and routes tasks.        | 95*      | 90*         | 98*           | 95*     | 90*              | 10*           | 0           |
| Emergent Behavior (10%)         | Novel behaviors that emerge from complex feedback loops.  | 95       | 80          | 98            | 95      | 80*              | 5             | 0           |
| Reflexive Autonomy (30%)        | The system's ability to observe and modify itself.        | 98       | 90*         | 100*          | 95*     | 100**            | 0             | 0           |
| Environmental Coupling (15%)    | How the system reads, writes, and acts on its env.        | 98       | 80          | 95*           | 95**    | 100**            | 70            | 30          |
+---------------------------------+-----------------------------------------------------------+----------+-------------+---------------+---------+------------------+---------------+-------------+
| Overall Score                   | N/A                                                       | 96       | 88          | 98            | 95      | 92**             | 11            | 5           |
+---------------------------------+-----------------------------------------------------------+----------+-------------+---------------+---------+------------------+---------------+-------------+
)

(comment
  ;; ---------------------------------------------------
  ;; SECTION 2: AGENT DEFINITIONS TABLE (v9.6)
  ;; ---------------------------------------------------

+-------------+-----------------------+-----------------------------+------------------------------+---------------------------------+--------+-----------+-----------------------+--------------------+--------------------+-------------------------+
| Step        | Purpose               | Component                   | Agent Name                   | Intelligence Required (0-100) | ReAct? | Company   | Intelligence Tier     | Internal API Calls | External API Calls | Model Name              |
+-------------+-----------------------+-----------------------------+------------------------------+---------------------------------+--------+-----------+-----------------------+--------------------+--------------------+-------------------------+
| 1. Strategy | "What's the plan?"    | ThemeClassifierAgent        | ThemeClassifierAgent          | 20 (Low)                        | N      | Google    | Tier 3 (Speed/Cost)   | 0                  | 1                  | Gemini 2.5 Flash-Lite   |
+-------------+-----------------------+-----------------------------+------------------------------+---------------------------------+--------+-----------+-----------------------+--------------------+--------------------+-------------------------+
| 2. RAG      | "What are the facts?" | RAG_QueryGen                | RAG_QueryGeneratorAgent       | 75 (High)                       | N      | Google    | Tier 1 (Flagship)     | 0                  | 1                  | Gemini 2.5 Pro          |
|             |                       | QueryAdversaryAgent         | QueryAdversaryAgent           | 70 (High)                       | N      | Google    | Tier 2 (Workhorse)    | 0                  | 1                  | Gemini 2.5 Flash        |
|             |                       | RAG_SearchAgent (ReAct)     | RAG_SearchAgent (Brain)       | 95 (Expert)                     | Y      | Google    | Tier 1 (Flagship)     | 0                  | 5 (Thought+Critique)| Gemini 2.5 Pro          |
|             |                       | RAG_Tool_1 (Tool)           | _tool_master_resume_search    | 0 (Low)                         | N      | N/A       | N/A (Python)          | 1 (to resume)      | 0                  | N/A (Python)            |
|             |                       | RAG_Tool_2 (Tool)           | _tool_graph_search            | 0 (Low)                         | N      | N/A       | N/A (Python)          | 1 (to graph db)    | 0                  | N/A (Python)            |
|             |                       | RAG_Critique                | RAG_CritiqueAgent             | 85 (Very High)                  | N      | Anthropic | Tier 1 (Flagship)     | 0                  | 1                  | Claude 4.1 Opus         |
+-------------+-----------------------+-----------------------------+------------------------------+---------------------------------+--------+-----------+-----------------------+--------------------+--------------------+-------------------------+
| 3. Drafting | "Write the story."    | Prompt Stack                | PromptStackAgent              | 5 (Low)                         | N      | N/A       | N/A (Python)          | 1 (assembles state)| 0                  | N/A (Python)            |
|             |                       | Bullet Stack (v8)           | ProvenanceRouterAgent         | 80 (Very High)                  | N      | N/A       | N/A (Python Router)   | 3 (calls experts)  | 0                  | N/A (Python)            |
|             |                       |                             | CustomizedBulletDrafter       | 70 (High)                       | N      | Google    | Tier 1 (Flagship)     | 0                  | 1                  | Gemini 2.5 Pro          |
|             |                       |                             | SyntheticBulletDrafter        | 85 (Very High)                  | N      | Google    | Tier 1 (Flagship)     | 0                  | 1                  | Gemini 2.5 Pro          |
|             |                       |                             | SyntheticFactCheckAgent       | 70 (High)                       | N      | Google    | Tier 2 (Workhorse)    | 0                  | 1                  | Gemini 2.5 Flash        |
|             |                       | Bullet Critique (v9)        | BulletCritiqueAgent           | 80 (Very High)                  | N      | Google    | Tier 2 (Workhorse)    | 0                  | 1                  | Gemini 2.5 Flash        |
|             |                       | Drafting Stack (v8)         | DraftingConductorAgent        | 90 (Expert)                     | Y      | Google    | Tier 1 (Flagship)     | 0                  | 1 (Plan) + 3 (Exec)| Gemini 2.5 Flash        |
|             |                       | (Expert)                    | Strategist (Gemini)           | 95 (Expert)                     | N      | Google    | Tier 1 (Flagship)     | 0                  | 1                  | Gemini 2.5 Pro          |
|             |                       | (Expert)                    | RedTeam (Claude)              | 95 (Expert)                     | N      | Anthropic | Tier 1 (Flagship)     | 0                  | 1                  | Claude 4.1 Opus         |
|             |                       | (Expert)                    | Refiner (GPT-5)               | 100 (Expert)                    | N      | OpenAI    | Tier 1 (Flagship)     | 0                  | 1                  | GPT-5                   |
|             |                       | (Expert)                    | MetricsSpecialistAgent        | 75 (High)                       | N      | Google    | Tier 2 (Workhorse)    | 0                  | 1                  | Gemini 2.5 Flash        |
|             |                       | SC Paths                    | WorkflowRePlannerAgent        | 90 (Expert)                     | Y      | Anthropic | Tier 1 (Flagship)     | 0                  | 1                  | Claude 4.1 Opus         |
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
| 6. Meta-Learning | "How do we improve?" | MetaLearningGraph        | LogReaderAgent               | 0 (Low)                         | N      | N/A       | N/A (Python)          | 2 (reads logs)     | 0                  | N/A (Python)            |
|             |                       |                             | PatternFinderAgent (LLM)     | 75 (High)                       | N      | Google    | Tier 2 (Workhorse)    | 0                  | 1                  | Gemini 2.5 Flash        |
|             |                       |                             | HypothesisGeneratorAgent     | 80 (Very High)                  | N      | Google    | Tier 2 (Workhorse)    | 0                  | 1                  | Gemini 2.5 Flash        |
|             |                       |                             | ProposalDrafterAgent         | 70 (High)                       | N      | Google    | Tier 2 (Workhorse)    | 0                  | 1                  | Gemini 2.5 Flash        |
|             |                       |                             | ProposalCritiqueAgent        | 85 (Very High)                  | N      | Google    | Tier 2 (Workhorse)    | 0                  | 1                  | Gemini 2.5 Flash        |
|             |                       |                             | MetaPlannerAgent (Python)    | 5 (Low)                         | N      | N/A       | N/A (Python)          | 1 (writes proposal)| 0                  | N/A (Python)            |
+-------------+-----------------------+-----------------------------+------------------------------+---------------------------------+--------+-----------+-----------------------+--------------------+--------------------+-------------------------+
| Total       |                       |                             |                              |                                 |        |           |                       | 16 Calls           | 27 Calls           |                         |
+-------------+-----------------------+-----------------------------+------------------------------+---------------------------------+--------+-----------+-----------------------+--------------------+--------------------+-------------------------+
)

(comment
  ;; ---------------------------------------------------
  ;; SECTION 3: DETAILED PIPELINE FLOW (v9.6)
  ;; ---------------------------------------------------

  +------------------------------------------------------------------------------------------------------------+
  | 🚀 v9.6 PARALLEL BATCH HARNESS (run_batch_v9_6.py)                                                        |
  | (Processes all jobs in parallel using a ProcessPoolExecutor)                                               |
  |                                                                                                            |
  |  (Input) 1. 📂 `batch_queue/` (Contains [job_1.json], [job_2.json], ... [job_N.json])                      |
  |                                                                                                            |
  | | (Spawns `max_parallel_workers` (e.g., 8) via ProcessPoolExecutor)                                        |
  | |                 v                                                                                       |
  | |  +--------------------------------------------------------------------------------------------------+   |
  | |  | 🌀 **Parallel Executor (`concurrent.futures`)** |                                                  |
  | |  | (Each job runs in its own `process_single_job` function)                                           |
  | |  |                                                                                                   |   |
  | |  | +------------------+ +------------------+ +------------------+ +------------------+                |
  | |  | | [Run Job 1]      | | [Run Job 2]      | | [Run Job 3]      | | ... [Run Job N]  | (All run)     |
  | |  | | (v9.0 Cost Check)| | (v9.0 Cost Check)| | (v9.0 Cost Check)| | (v9.0 Cost Check)| simultaneously)|
  | |  | | (try/catch)      | | (try/catch)      | | (try/catch)      | | (try/catch)      |                |
  | |  | | `workflow.run()` | |  `workflow.run()` | |  `workflow.run()` | |  `workflow.run()` |               |
  | |  | +------------------+ +------------------+ +------------------+ +------------------+                |
  | |  |         |                  |                  |                  |                                 |   |
  | |  | `-----------------(Collects all results when complete)-----------------'                           |
  | |  |                                      v                                                             |
  | |  |   2. (finally) Write all results to `batch_summary_v9_6.csv` (Output 1) 📈                         |
  | |  |   3. (finally) Move all job files to `batch_complete/` (Output 2) 🗂️                              |
  | |  +--------------------------------------------------------------------------------------------------+   |
  |                                                                                                            |
  |                 | (After batch completes)                                                                  |
  |                 v                                                                                          |
  |  +--------------------------------------------------------------------------------------------------+   |
  |  | 🤖 **Automated Meta-Learning Trigger** |                                                            |
  |  | (Batch runner *automatically* calls `run_learning_v9_6.py`)                                        |
  |  +--------------------------------------------------------------------------------------------------+   |
  +------------------------------------------------------------------------------------------------------------+

  | ♾️ v9.6 AGENTIC META-LEARNING GRAPH (Re-architected for 90+ Score)                                        |
  | (Triggered by `run_batch_v9_6.py` after batch is complete)                                                |
  |                                                                                                           |
  | 1. `run_learning_v9_6.py` runs (which is now a LangGraph app):                                            |
  |    +---------------------------+ (Reads) -> +-------------------------+                                   |
  |    | 🤖 **LogReaderAgent** |            | 📄 `feedback_log.jsonl`  |                                   |
  |    +---------------------------+            | 📄 `preference_log.jsonl`|                                   |
  |                 | (Sends logs)               +-------------------------+                                   |
  |                 v                                                                                        |
  |    +---------------------------+                                                                         |
  |    | 🤖 **PatternFinderAgent** (LLM)  | (Finds patterns)                                                  |
  |    +---------------------------+                                                                         |
  |                 | (Sends patterns)                                                                     |
  |                 v                                                                                        |
  |    +--------------------------------+                                                                    |
  |    | 🤖 **HypothesisGeneratorAgent** (LLM) | (Generates root causes)                                     |
  |    +--------------------------------+                                                                    |
  |                 | (Sends 1 hypothesis)                                                                 |
  |                 v                                                                                        |
  |    +---------------------------+                                                                         |
  |    | 🤖 **ProposalDrafterAgent** (LLM)   | (Drafts JSON change)                                          |
  |    +---------------------------+                                                                         |
  |                 | (Sends proposal)                                                                     |
  |                 v                                                                                        |
  |    +-----------------------------+                                                                     |
  |    | 🤖 **ProposalCritiqueAgent** (LLM) | (Adversarial review)                                          |
  |    +-----------------------------+                                                                     |
  |                 | (Critique Passed?)                                                                   |
  |    +------------+--------------+                                                                       |
  |    | (No)                      | (Yes)                                                                |
  |    v (Loop to Hypothesis)      v                                                                       |
  |    (Or loop to Drafter)        +--------------------------+ (Writes to) -> +---------------------------+ |
  |                                | 🐍 **MetaPlannerAgent** (Py) |              | 📄 `proposed_rules.jsonl` | |
  |                                +--------------------------+              +---------------------------+ |
  +------------------------------------------------------------------------------------------------------------+

  | 🧠 v9.6 ADVERSARIAL LANGGRAPH ORCHESTRATION (Corrected 3-Agent Version)                                   |
  | (LangGraph executes a flow now guarded by 3 adversarial critique agents)                                 |
  |                                                                                                          |
  | +----------------------------------------------------------------------------------------------------+   |
  | | **v9.6 LangGraph State Flow** |                                                                     |
  | +----------------------------------------------------------------------------------------------------+   |
  | | 1. 🧭 **Run Strategy** (Calls `ThemeClassifierAgent`)                                               |
  | |    v                                                                                               |
  | | 2. 🔍 **Run RAG Stack** (Calls `RAG_QueryGeneratorAgent`, `QueryAdversaryAgent`,                    |
  | |     `RAG_SearchAgent`, `RAG_CritiqueAgent`)                                                        |
  | |    | (Writes `rag_critique`, `rag_search_results` to 📋 State)                                     |
  | |    v                                                                                               |
  | | 3. ✒️ **Run Bullet Stack** (Calls `ProvenanceRouterAgent` which now includes `SyntheticFactCheckAgent`)|
  | |    | (Writes `generated_bullets` to 📋 State)                                                      |
  | |    v                                                                                               |
  | | 4. 🧐 **Run Bullet Critique** (Calls `BulletCritiqueAgent`)                                        |
  | |    | (Writes `bullet_critique_results` to 📋 State)                                                |
  | |    v                                                                                               |
  | |   | **BULLETS PASSED?** |                                                                          |
  | +---------------------------------------+                                                            |
  | |    | (Yes)             | (No)                                                             |
  | +---------------------------------------+                                                            |
  | |    v                   v                                                               |
  | | 5. ✍️ **Run Drafting** (Calls `PromptStackAgent`, `DraftingConductorAgent`)                      |
  | |    | (Writes `final_draft` to 📋 State)                                                          |
  | |    v                                                                                             |
  | | 6. 🛡️ **Run QA Stack** (Calls `QAConductorAgent`, `QAPlanCritiqueAgent`, `AtomicQASwarmLogic`)    |
  | |    | (Writes `validation_results` to 📋 State)                                                   |
  | |    v                                                                                             |
  | |   | **QA PASSED?** |                                                                             |
  | +---------------------------------------+                                                            |
  | |    | (Yes)             | (No)                                                             |
  | +---------------------------------------+                                                            |
  | |    v                   v                                                               |
  | | [ ✅ **GOAL MET** ]     [ 🔄 **Call RePlanner** ] (Calls `WorkflowRePlannerAgent`)               |
  | | (Stop)                   | (Plan: "Requires new facts?")                                   |
  | |                          |   | (Yes) -> (Go to Step 2: RAG)                                |
  | |                          |   | (No)  -> (Go to Step 3: Bullet Stack)                       |
  | |                          +---------------------------------------------------------------+         |
  | +----------------------------------------------------------------------------------------------------+

