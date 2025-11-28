# Agentic Architecture Design v9.8

## SECTION 1: AGENTIC CAPABILITY ASSESSMENT (TRANSPOSED) [v9.8.2]

**UPDATE:** This table is transposed. Stacks are rows.
Scores for v9.8 reflect P0, P1, and P2 enhancements.
The Overall Score is a composite grade based on the 5 agentic dimensions (see footnote below).

**Legend:**
- HL/HI = High-Leverage / High-Intel ("Smart Brains")
- LL/LI = Low-Leverage / Low-Intel ("Efficient Tools")
- HL/LI = High-Leverage / Low-Intel ("Dumb Brains" - Flaw)
- LL/HI = Low-Leverage / High-Intel ("Overqualified" - Flaw)

| Stack | Function (Abbrv.) | Score | HL/HI (LLM) | LL/LI (Py) | HL/LI (Flaw) | LL/HI (Flaw) | Total | Gaps (Abbrv.) |
|:------|:------------------|------:|------------:|-----------:|-------------:|-------------:|------:|:--------------|
| RAGStack | Critique & Collaboration | 98 | 6 | 3 | 0 | 0 | 9 | Gap: Needs to read `feedback_log.jsonl` for dynamic agent selection. |
| BulletStack | Critique & Collaboration | 88 | 4 | 0 | 1 | 0 | 5 | Flaw: "Dumb Brain" Python router (`ProvenanceRouterAgent`) must be upgraded. |
| DraftingStack | Critique & Collaboration | 99** | 7 | 0 | 0 | 0 | 7 | Gap: Needs to read `feedback_log.jsonl` for dynamic agent selection. |
| QAStack | Critique & Collaboration | 98** | 13 | 1 | 0 | 0 | 14 | Gap: Needs to read `feedback_log.jsonl` for dynamic agent selection. |
| MetaLearningLoop | Observe & Modify Self | 92** | 4 | 2 | 0 | 0 | 6 | Gap: Needs "hot-reloading" of `proposed_rules.jsonl` without human deploy. |
| StrategyStack | Dynamic Planning & Routing | 85 | 4 | 0 | 0 | 0 | 4 | Gap: Needs to read `feedback_log.jsonl` to inform ToT branch selection. |
| PromptStack | Dynamic Planning & Routing | 72 | 1 | 0 | 0 | 0 | 1 | Gap: Needs to read `feedback_log.jsonl` to inform prompt generation. |
| SafetyGuardStack | Observe & Modify Self | 93 | 2 | 1 | 0 | 0 | 3 | Gap: Needs to read `proposed_rules.jsonl` to update its constitution. |
| DynamicToolingStack | Read, Write & Act on Env | 98* | 2 | 1 | 0 | 0 | 3 | Gap: Needs to read `feedback_log.jsonl` for dynamic tool selection. |
| HIL_InteractionStack | Read, Write & Act on Env | 96* | 3 | 1 | 0 | 0 | 4 | Gap: Deeper Human-Computer Interaction / collaborative reasoning. |

---

## FOOTNOTE: 5 AGENTIC DIMENSIONS (DEFINITIONS)

The "Overall Score" is a weighted composite based on these 5 dimensions:

1. **Multi-Agent Collaboration (20%)**: How well agents communicate and critique each other's work.
2. **Agentic Orchestration (25%)**: How the system dynamically plans, routes, and re-plans tasks.
3. **Emergent Behavior (10%)**: Novel behaviors that emerge from complex, multi-step feedback loops.
4. **Reflexive Autonomy (30%)**: The system's ability to observe, reason about, and modify itself (meta-learning).
5. **Environmental Coupling (15%)**: How the system reads, writes, and acts on its environment (files, APIs, tools, user).

### INDICATOR DEFINITIONS:
- `*` Score is directly enabled by The_LangGraph_App (orchestration, replanning, HIL).
- `**` Score is directly enabled by the MetaLearningLoop (long-term learning, log files).

---

## SECTION 2: DETAILED PIPELINE FLOW (v9.8)

```
+------------------------------------------------------------------------------------------------------------+
| 🚀 v9.8 PARALLEL BATCH HARNESS (run_batch_v9_8.py)                                                        |
| (Processes all jobs in parallel using a ProcessPoolExecutor)                                               |
|                                                                                                            |
|  (Input) 1. 📂 `batch_queue/` (Contains [job_1.json], [job_2.json], ... [job_N.json])                      |
|                                                                                                            |
| | (Spawns `max_parallel_workers` (e.g., 8) via ProcessPoolExecutor)                                        |
| |                 v                                                                                       |
| |  +--------------------------------------------------------------------------------------------------+    |
| |  | 🌀 **Parallel Executor (`concurrent.futures`)** |    |
| |  | (Each job runs in its own `process_single_job` function)                                           |
| |  |                                                                                                  |    |
| |  | +------------------+ +------------------+ +------------------+ +------------------+               |    |
| |  | | [Run Job 1]      | | [Run Job 2]      | | [Run Job 3]      | | ... [Run Job N]  | (All run     |    |
| |  | | (v9.0 Cost Check)| | (v9.0 Cost Check)| | (v9.0 Cost Check)| | (v9.0 Cost Check)| simultaneously)|
| |  | | (try/catch)      | | (try/catch)      | | (try/catch)      | | (try/catch)      |               |    |
| |  | | `workflow.run()` | | `workflow.run()` | | `workflow.run()` | | `workflow.run()` |               |    |
| |  | +------------------+ +------------------+ +------------------+ +------------------+               |    |
| |  |         |                  |                  |                  |                          |    |
| |  | `-----------------(Collects all results when complete)-----------------'                          |
| |  |                                      v                                                        |
| |  |   2. (finally) Write all results to `batch_summary_v9_8.csv` (Output 1) 📈                     |
| |  |   3. (finally) Move all job files to `batch_complete/` (Output 2) 🗂️                            |
| |  +--------------------------------------------------------------------------------------------------+    |
|                                                                                                            |
|                 | (After batch completes)                                                                  |
|                 v                                                                                          |
|  +--------------------------------------------------------------------------------------------------+    |
|  | 🤖 **Automated Meta-Learning Trigger** |    |
|  | (Batch runner *automatically* calls `run_learning_v9_8.py`)                                        |
|  +--------------------------------------------------------------------------------------------------+    |
|                                                                                                            |
+------------------------------------------------------------------------------------------------------------+

+ - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -+
|
| ♾️ v9.8 AGENTIC META-LEARNING GRAPH (v9.6 Logic, v9.8 Model Info)                                         |
| (Triggered by `run_batch_v9_8.py` after batch is complete)                                                 |
|                                                                                                            |
| 1. `run_learning_v9_8.py` runs (which is a LangGraph app):                                                 |
|    +---------------------------+ (Reads) -> +-------------------------+                                   |
|    | 🤖 **LogReaderAgent** (Python) |            | 📄 `feedback_log.jsonl` |                                   |
|    +---------------------------+            | 📄 `preference_log.jsonl` |                                   |
|                 | (Sends logs)       +-------------------------+                                   |
|                 v                                                                                        |
|    +---------------------------+                                                                         |
|    | 🤖 **PatternFinderAgent** (Gemini 2.5 Flash / T2) | (Finds patterns)                                 |
|    +---------------------------+                                                                         |
|                 | (Sends patterns)                                                                     |
|                 v                                                                                        |
|    +--------------------------------+                                                                    |
|    | 🤖 **HypothesisGeneratorAgent** (Gemini 2.5 Flash / T2) | (Generates root causes)                    |
|    +--------------------------------+                                                                    |
|                 | (Sends 1 hypothesis)                                                                 |
|                 v                                                                                        |
|    +---------------------------+                                                                         |
|    | 🤖 **ProposalDrafterAgent** (Gemini 2.5 Flash / T2) | (Drafts JSON change)                           |
|    +---------------------------+                                                                         |
|                 | (Sends proposal)                                                                     |
|                 v                                                                                        |
|    +-----------------------------+                                                                     |
|    | 🤖 **ProposalCritiqueAgent** (Gemini 2.5 Flash / T2) | (Adversarial review)                         |
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
  v (Each `workflow.run()` call from a parallel thread)

+------------------------------------------------------------------------------------------------------------+
| 🧠 v9.8 FULL LANGGRAPH ORCHESTRATION (P0 + P1 + P2 Enhancements, Consolidated View)                          |
| (The main graph now includes parallel safety/cost, ToT strategy, local retries, and a full HIL stack)      |
|                                                                                                            |
| +---------------------------------------------------------------------------------------------------------+  |
| | 📦 **v9.8 LangGraph State Flow** |
| +---------------------------------------------------------------------------------------------------------+  |
| |                                                                                                         |  +----------------------------------+
| | 0. 🧼 **Run PII Scrubber** (Python)                                                                     |  | 🛡️ **PARALLEL SAFETYGUARDSTACK** (Claude 4.1 Opus / T1) |
| |    v                                                                                                    |  | (Runs on *every* step's output)  |
| | 1. 🧭 **Run Strategy (ToT)** (Gemini 2.5 Pro / T1)                                                      |  | 1. `ConstitutionalAgent`         |
| |    | (Calls `StrategyGeneratorAgent` -> 3 parallel `StrategyCritiqueAgent`s -> `StrategySelectorAgent`) |  | 2. `SafetyRedTeamAgent`          |
| |    | (Writes `strategy_brief` to 📋 State)                                                             |  +----------------------------------+
| |    v                                                                                                    |
| | 2. 🧐 **Run Ambiguity Detector** (P1) (Gemini 2.5 Flash / T2)                                         |  +----------------------------------+
| |    | **AMBIGUITY DETECTED?** |  | 💰 **PARALLEL COSTTRACKER (P2)** (Python) |
| |    +--------------------------+ (No)                                                                   |  | (Monitors token spend per agent) |
| |    | (Yes)                     v                                                                       |  | (Can veto on cost overrun)       |
| |    '----(Go to Step 8: HIL)   3. 🔍 **Run RAG Stack** (P2: HyDE/Re-rank) (Mixed T1/T2)                   |  +----------------------------------+
| |                              | (Writes `rag_critique`, `rag_search_results` to 📋 State)                |
| |                              v                                                                        |
| | 4. ✒️ **Run Bullet Stack** (Mixed T1/T2 + Python Flaw)                                                |
| |    | (Writes `generated_bullets` to 📋 State)                                                           |
| |    v                                                                                                    |
| | 5. 🧐 **Run Bullet Critique** (Gemini 2.5 Flash / T2)                                                 |
| |    | (Writes `bullet_critique_results` to 📋 State)                                                     |
| |    v                                                                                                    |
| |   | **BULLETS PASSED?** [Retry: {bullet_retries}/2]                                                     |
| +-------------------------------------------------+                                                       |
| |    | (Yes)                                    | (No)                                                  |
| +-------------------------------------------------+                                                       |
| |    v                                            v                                                       |
| | 6. ✍️ **Run Drafting** (P1 Conductor) (Mixed T1/T2)                                                  | [ 🔄 **Local Retry: Bullets** ] |
| |    | (Calls `DynamicPromptEngineerAgent`,       | (If bullet_retries < 2, +1 retry)                     |
| |    |  `DraftingConductorAgent (ReAct)`)         '----(Go to Step 4: Bullet Stack)                       |
| |    | (Writes `final_draft` to 📋 State)         | (If bullet_retries >= 2)                              |
| |    v                                            '----(Go to 🚨 Global RePlanner)                        |
| | 7. 🛡️ **Run QA Stack** (P1 Conductor) (Mixed T1/T2)                                                   |
| |    | (Writes `validation_results` to 📋 State)                                                        |
| |    v                                                                                                    |
| |   | **QA PASSED?** [Retry: {qa_retries}/1]                                                              |
| +-------------------------------------------------+                                                       |
| |    | (Yes)                                    | (No)                                                  |
| +-------------------------------------------------+                                                       |
| |    v                                            v                                                       |
| | 8. 🗣️ **Run HIL Interaction Stack** (P1) (Gemini 2.5 Flash / T2)                                    | [ 🔄 **Local Retry: Drafting** ] |
| |    | (Calls `SuggestionAgent`)                 | (If qa_retries < 1, +1 retry)                         |
| |    v                                            '----(Go to Step 6: Run Drafting)                       |
| | 9. ⏸️ **HIL Pause** (Awaits Human Input) (Human)                                                     | (If qa_retries >= 1)                                  |
| |    v                                            v                                                       |
| | 10. 🗺️ **Run Feedback Router** (P1) (Gemini 2.5 Flash / T2)                                         | [ 🚨 **Call Global RePlanner** ] (Claude 4.1 Opus / T1) |
| |    | (Calls `FeedbackRouterAgent`, `PreferenceCaptureAgent`)                                          |
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
| 🧭 v9.8 STEP 1: STRATEGY (P1 HIL Upgrade)                                                                   |
| (Adds P1 Ambiguity Detector to the v9.7 ToT flow)                                                          |
|                                                                                                            |
|    +--------------------------------------------------------------------------------------------------+    |
|    | 📋 **GraphState** (Shared State)                                                                   |
|    +--------------------------------------------------------------------------------------------------+    |
|       ^                                                                                                |
|       | (Writes *final* `strategy_brief`)                                                              |
|       |                                                                                                |
|    [ 📄 **JD** ] -> [ 🤖 **StrategyGeneratorAgent (ToT)** (Gemini 2.5 Pro / T1) ] (Generates 3 strategies)  |
|                 |                                                                                      |
|   +-------------+----------------+-----------------+                                                    |
|   | (Strategy A)                   | (Strategy B)                    | (Strategy C)                   |
|   v                                v                               v                              |
| [ 🤖 **StrategyCritique** (Gemini 2.5 Flash / T2) ] [ 🤖 **StrategyCritique** (Gemini 2.5 Flash / T2) ] [ 🤖 **StrategyCritique** (Gemini 2.5 Flash / T2) ] |
| (LLM Call: "Critique A")       (LLM Call: "Critique B")      (LLM Call: "Critique C")      |
|   +-------------+----------------+-----------------+                                                    |
|                 | (Gathers 3 strategies + 3 critiques)                                                 |
|                 v                                                                                      |
|    [ 🤖 **StrategySelectorAgent** (Gemini 2.5 Flash / T2) ] (Selects single best one)                    |
|                 |                                                                                      |
|                 v (Checks for vagueness)                                                               |
|    [ 🧐 **AmbiguityDetectorAgent (P1)** (Gemini 2.5 Flash / T2) ] --(Yes)--> (Route to HIL Stack)         |
|                                                                                                            |
+------------------------------------------------------------------------------------------------------------+

                                        |
  | (Graph calls `run_rag_stack` node)
                                        v

+------------------------------------------------------------------------------------------------------------+
| 🔍 v9.8 STEP 2: RAG STACK (P1/P2 Enhancements) [Score: 98]                                                  |
|                                                                                                            |
| 1. [ ❓ **RAG_QueryGen** [85] (Gemini 2.5 Pro / T1) ] (P1: Generates queries + *new temporary Python tools*) |
|                 | (Sends Queries + Tool Code)                                                          |
|                 v                                                                                      |
| 2. [ 🧐 **QueryAdversaryAgent** [70] (Gemini 2.5 Flash / T2) ] (v9.6 Agent: "Improve these queries.")    |
|                 | (Sends *Improved* Queries)                                                           |
|                 v                                                                                      |
| 3. [ 📡 **RAG_SearchAgent (ReAct)** [96] (Gemini 2.5 Pro / T1) ]                                           |
|    (Executes "Thought-Action-Critique" loop for each query)                                            |
|    |                                                                                                 |
|    |  1. [ 💭 **Thought** ] (LLM call: "What should I do?")                                           |
|    |  2. [ ⚡ **Action** ] (P1: Calls `ToolSelectionAgent` -> `ToolExecutionAgent`)                     |
|    |       |                                                                                        |
|    |       `--> [ 📚 master_resume_search (Python) ]                                                  |
|    |       `--> [ 🕸️ web_search (Python) ]                                                          |
|    |       `--> [ 🔗 **graph_search** (Python) ]                                                     |
|    |       `--> [ 💡 **_tool_gen_hypothetical_answer** (Gemini 2.5 Flash / T2) ] (P2 HyDE Tool)       |
|    |       `--> [ 🐍 **_tool_dynamic_tool_executor** (Python) ] (P1 Tool: Runs generated Python)       |
|    |                                                                                                |
|    |  3. [ 👁️ **Observation** ] (Receives results from tool)                                          |
|    |  4. [ 🧐 **Internal Critique** ] (LLM call: "Is this step's result good?")                       |
|    |  5. [ 🎯 **Satisfied?** ] --(No)--> (Loop to 1. Thought)                                       |
|    |       | (Yes)                                                                                  |
|    |       v (Gathers all loop results)                                                             |
|    |                                                                                                |
| 4. [ 🧐 **RAG_ReRankerAgent** [80] (Gemini 2.5 Flash / T2) ] (P2 Agent: "Re-rank based on strategy")     |
|    |                                                                                                |
| 5. [ 🧑‍🏫 **RAG_Critique** [85] (Claude 4.1 Opus / T1) ] <---+ (Critiques *re-ranked* search results)      |
|                                                                                                            |
+------------------------------------------------------------------------------------------------------------+

                                        |
  | (Graph calls `run_bullet_stack` node)
                                        v

+------------------------------------------------------------------------------------------------------------+
| ✒️ v9.8 STEP 3: BULLET STACK (v9.6 Adversarial Upgrade) [Score: 88]                                         |
| (Unchanged from v9.7 - **NOTE: This stack still contains the "Dumb Brain" v9.9 flaw**)                     |
|                                                                                                            |
|   [ 🤖 **ProvenanceRouterAgent** [80] (Python Router) ] (Flaw: High-Leverage task, Low-Intel script)      |
|                 | (Executes 4-step provenance plan sequentially)                                       |
|   +-------------+----------------+-----------------+-------------------------+                           |
|   | (Step 1)                       | (Step 2)                      | (Step 3)                        | (Step 4)                |
|   v                              v                               v                               |
| [ 🐍 **Verbatim** (Python) ] [ 🤖 **Customized** (Gemini 2.5 Pro / T1) ] [ 🤖 **Synthetic** (Gemini 2.5 Pro / T1) ] [ 🤖 **SyntheticFactCheck** (Gemini 2.5 Flash / T2) ] |
| (2 Bullets)                      (3 or 2 Bullets)                (2 Bullets)                     (Filters out hallucinations) |
|   +-------------+----------------+-----------------+-------------------------+                           |
|                 | (Gathers all *fact-checked* bullets)                                               |
|                 v                                                                                      |
|   [ 📜 **Final Bullet List** ] (Writes `generated_bullets` to 📋 State)                                    |
|                                                                                                            |
+------------------------------------------------------------------------------------------------------------+

                                        |
  | (Graph calls `run_drafting_stack` node)
                                        v

+------------------------------------------------------------------------------------------------------------+
| ✍️ v9.8 STEP 5: DRAFTING (P1 "True Conductor" Upgrade) [Score: 99]                                          |
|                                                                                                            |
| [ 🤖 **DynamicPromptEngineerAgent** [85] (Gemini 2.5 Flash / T2) ] (P0 Upgrade: Creates custom prompt)      |
|    |                                                                                                    |
|    v (Sends *Custom-Generated* Prompt)                                                                       |
|   +----------------------------------------------------------------------------------+   |
|   | 🤖 **DraftingConductorAgent (P1 ReAct)** [95] (Gemini 2.5 Pro / T1)              |
|   | (P1: True ReAct agent. P2: Reads `feedback_log.jsonl` for dynamic agent selection) |
|   | (Executes step-by-step "Thought-Action-Critique" loop using experts as tools)      |
|   +----------------------------------------------------------------------------------+   |
|                 | (Calls experts as tools, step-by-step)                               |
|                 v                                                                      |
|   +----------------------------------------------------------------------------------+   |
|   | 🧑‍🎨 **Pool of Drafting Experts (Tools)** |   |
|   |                                                                                  |   |
|   | * [ ✍️ **Strategist** (Gemini 2.5 Pro / T1) ]                                    |
|   | * [ 🧐 **RedTeam** (Claude 4.1 Opus / T1) ]                                    |
|   | * [ 🎨 **Refiner** (GPT-5 / T1) ]                                              |
|   | * [ 📊 **MetricsSpecialist** (Gemini 2.5 Flash / T2) ]                           |
|   +----------------------------------------------------------------------------------+   |
|                 | (Final artifact from ReAct loop)                                     |
|                 v                                                                      |
|   [ 📜 **final_draft** ] (Writes to 📋 State)                                           |
|                                                                                      |
+------------------------------------------------------------------------------------------------------------+

                                        |
  | (Graph calls `run_qa_swarm` node)
                                        v

+------------------------------------------------------------------------------------------------------------+
| 🛡️ v9.8 STEP 6: QA STACK (P1 "True Conductor" Upgrade) [Score: 98]                                          |
|                                                                                                            |
|   +---------------------------------------+  +---------------------------------------+   |
|   | 🤖 **QAConductorAgent (P1 ReAct)** [95] |  | 📦 **AtomicQASwarmLogic** [5] (Python)  |   |
|   | (Gemini 2.5 Pro / T1)                 |  | (Runs 2 Python checks)                |   |
|   | (P1: True ReAct agent. P2: Reads log)   |  |         |                             |   |
|   | (Executes step-by-step ReAct loop)    |  |         v (2 parallel checks)         |   |
|   |         |                             |  | * 🔢 WordCountValidator [15]        |   |
|   |         v (Calls `QAPlanCritique` first) |  | * 🔣 CharacterCountValidator [15]     |   |
|   | [ 🧐 **QAPlanCritiqueAgent** [70] (Gemini 2.5 Flash / T2) ] |  |                               |   |
|   |         |                             |  +---------------------------------------+   |
|   |         v (Calls experts as tools)    |                                              |
|   | **Pool of QA Experts (11 LLMs)** |                                              |
|   | (This is the untruncated list of tools available to the conductor)                   |
|   | * 🗣️ ClaimValidatorAgent (NLI) [75]  (Gemini 2.5 Flash / T2)                      |
|   | * 🎚️ ToneValidator [55] (Gemini 2.5 Flash / T2)                                 |
|   | * 🎯 ThematicAlignment_Validator [80] (Gemini 2.5 Flash / T2)                      |
|   | * 🤝 SemanticEntailmentValidator [70] (Gemini 2.5 Flash / T2)                      |
|   | * 🧵 NarrativeThreadAgent [85] (Gemini 2.5 Flash / T2)                          |
|   | * 👹 AdversarialReviewerAgent [95] (Claude 4.1 Opus / T1)                      |
|   | * 📍 JDSkillsValidatorAgent [65] (Gemini 2.5 Flash / T2)                         |
|   | * 📶 SignalScoreValidatorAgent [70] (Gemini 2.5 Flash / T2)                      |
|   | * ⚖️ BiasScrubberAgent [60] (Gemini 2.5 Flash / T2)                            |
|   | * 🗓️ TenureValidatorAgent [50] (Gemini 2.5 Flash / T2)                         |
|   | * 🔎 MissedOpportunityAgent [80] (v9.0) (Gemini 2.5 Flash / T2)                    |
|   +---------------------------------------+----------------------------------------------+   |
|                                                                                                            |
+------------------------------------------------------------------------------------------------------------+
```

---

## Notes

- This Markdown file uses standard table syntax that will render correctly in GitHub, GitLab, VS Code, and other Markdown viewers
- Column headers automatically align with data
- No manual spacing adjustments required
- Can be edited in any text editor with Markdown support
- Future updates: just modify table cells directly - rendering engines handle alignment