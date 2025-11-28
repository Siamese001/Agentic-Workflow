## SECTION 1: AGENTIC CAPABILITY ASSESSMENT (TRANSPOSED) [v10.4]

**UPDATE:** Scores (0-100) now rate each stack's maturity against the 6 core MECE dimensions of agentic architecture. A "Gaps" column identifies key missing patterns.

**Legend:**

* `[HYBRID]` = v10.4 Hybrid RAG (Vector + Keyword)
* `[VAL]` = v10.4 Pydantic Schema Validation
* `[RESIL]` = v10.4 Resilience Pattern (Retry or Circuit Breaker from `core_v10_4`)
* `[BUDGET]` = v10.4 Context Budget Management
* `[DI]` = v10.4 True Dependency Injection
* `♾️` = Preserved v10.1 Feedback-Aware / Hot-Reloading

| \# | Stack | Function | Strat. Aptitude | Env. Interact. | Orch. & Collab. | Ops. Integrity | Econ. Efficiency | Refl. Adaptation | Overall Score | Gaps (8-12 words) |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| 1 | **RAGStack** | Ingests resume, runs **Hybrid RAG** (parallel Vector + Keyword), merges, and reranks. | 30 | 100 | 10 | 90 | 60 | 10 | **50** | Non-agentic; it's a fixed pipeline, cannot re-plan or adapt search. |
| 2 | **BulletStack** | Generates/refines bullets in parallel using feedback-aware, validated critique strategies. | 85 | 50 | 80 | 100 | 90 | 80 | **81** | Lacks explicit self-consistency voting; relies on a single-path critique model. |
| 3 | **DraftingStack** | Orchestrates expert agents via ReAct, now with **tool circuit breakers** and **Pydantic validation**. | 90 | 95 | 100 | 100 | 60 | 100 | **91** | ReAct loop tools are not cached, forcing redundant calls on retry. |
| 4 | **QAStack** | Runs a swarm of validators with **tool circuit breakers**, **Pydantic validation**, and **context budgeting**. | 90 | 100 | 100 | 100 | 70 | 100 | **93** | 11-tool swarm lacks caching, leading to high cost/latency on reruns. |
| 5 | **MetaLearningLoop** | Observes logs to find patterns and propose hot-reloadable rule changes. | 95 | 80 | 80 | 90 | 70 | 100 | **86** | Cannot perform self-consistency or metacognition; only rule-based learning. |
| 6 | **StrategyStack** | Uses feedback-aware, **Pydantic-validated** Tree-of-Thoughts (ToT) to select strategy. | 100 | 10 | 70 | 90 | 70 | 80 | **70** | ToT selection is basic; lacks multi-path self-consistency voting for robustness. |
| 7 | **PromptStack** | Generates dynamic, **Pydantic-validated** prompts using insights from feedback logs. | 85 | 10 | 10 | 100 | 70 | 85 | **60** | Simple feedback logic; lacks deeper meta-prompting or curriculum learning. |
| 8 | **SafetyGuardStack** | Provides local-only PII/bias checks using a dynamically hot-reloaded rule constitution. | 20 | 10 | 10 | 100 | 100 | 90 | **55** | Lacks true adversarial defense; vulnerable to advanced prompt injection attacks. |
| 9 | **DynamicToolingStack** | Selects/executes tools based on feedback logs. (Now part of core resilience). | 80 | 100 | 50 | 80 | 90 | 100 | **83** | Tool selection is feedback-aware, but tool results are not cached. |
| 10 | **HIL\_InteractionStack** | Proactively detects ambiguity (now **Pydantic-validated**) to pause workflow. | 85 | 90 | 80 | 100 | 70 | 80 | **84** | Proactive only; lacks deeper human-in-the-loop collaboration patterns. |
| **Total/Avg** | **Overall System** | **Average score across all 10 stacks** | **76.0** | **64.5** | **59.0** | **94.0** | **75.0** | **82.5** | **75.3** | **System Gaps: Lacks tool-caching, dynamic model routing, and agentic RAG.** |

### Footnote: 6 Agentic Dimensions (Definitions)

1.  **Strategic Aptitude:** Measures the agent's "brain"—the quality of its planning, reasoning, and context management.
2.  **Environmental Interaction:** Measures the agent's "hands and senses"—its ability to use tools, retrieve information (RAG), and execute actions.
3.  **Orchestration & Collaboration:** Measures the agent's ability to work as a "team"—the effectiveness of the workflow coordinating multiple agents and processes.
4.  **Operational Integrity:** Measures the agent's **correctness** and **safety**—its ability to validate its own output (Pydantic), adhere to constraints, and operate securely.
5.  **Economic Efficiency:** Measures the agent's **performance** relative to its **cost**—its ability to use resources (models, time, tokens) efficiently via caching and optimization.
6.  **Reflexive Adaptation:** Measures the agent's ability to **learn and improve**—its mechanisms for self-correction (retries, circuit breakers) and long-term learning (meta-learning).

---
**v10.4 System-Wide Upgrades (Gap Closure):**

* **Architectural Stability (`[FIX]`):** The `main` <-> `batch` <-> `orchestration` circular import is **resolved**. All shared utilities (`CircuitBreaker`, etc.) are centralized in `core_v10_4.py`.
* **LangGraph Stability (`[FIX]`):** The non-existent `RedisSaver` is replaced with the correct `AioRedisSaver`, unblocking all persistence.
* **Hybrid RAG (`[HYBRID]`):** RAGStack upgraded from pure vector to Hybrid (Vector + Keyword) search, closing the retrieval quality gap.
* **Pydantic Validation (`[VAL]`):** All LLM-based stacks now validate 100% of outputs, closing the reliability and parsing gap.
* **Resilience Patterns (`[RESIL]`):** The entire orchestration graph is now resilient to transient errors via `@exponential_backoff_retry`, and ReAct loops are resilient to tool failures via `CircuitBreK`s.
* **Dependency Injection (`[DI]`):** All global singletons are gone. The system is now a true DI application, closing the architecture/testing gap.
* **Context Budgeting (`[BUDGET]`):** The QAStack is now protected from token limit errors, closing a critical performance gap.

-----

## SECTION 2: AGENTIC PIPELINE DETAILED

```
METALEARNINGLOOP ♾️
   ↑  (rules, feedback patterns)
   │
SAFETYGUARDSTACK ⇆ STRATEGYSTACK ⇆ RAGSTACK ⇆ BULLETSTACK ⇆ DRAFTINGSTACK ⇆ QASTACK ⇆ HIL INTERACTIONSTACK
        ↑────────────────────────────────────────── feedback / retries / human loops ────────────────────────↑
        └────────────── DynamicToolingStack & PromptStack operate across all ───────────────────────────────┘
```

Each box below expands to include the **original node calls**, **agents**, **decorators**, **inputs/outputs**, **DI services**, **validation models**, **retry conditions**, and **cache/cleanup details**.
Emojis identify agents uniquely, as before.

---

## ♾️ METALEARNINGLOOP STACK  [VAL][DI][FIX]

**Purpose:** Post-batch self-learning cycle that derives new operating rules and auto-reloads them.

```text
📚 LogReaderAgent  →  🔍 AsyncPatternFinderAgent (Gemini 2.5 Pro / T1, cached + validated)  
💡 AsyncHypothesisGeneratorAgent (Gemini 2.5 Pro / T1)  →  📝 AsyncProposalDrafterAgent (Gemini 2.5 Flash / T2)  
🧪 AsyncProposalCritiqueAgent (Gemini 2.5 Flash / T2) loops until pass  
⚙️ HotReloadRuleManager ♾️ writes `proposed_rules.jsonl` (auto-approved high-confidence rules)
```

*Triggered automatically by* `await run_meta_learning(config)` *after batch completion*
Uses its own `WorkflowContext` (DI-injected PromptManager, Validator, CacheManager).
Persists via `AioRedisSaver [FIX]`.

---

## 🛡️ SAFETYGUARDSTACK ♾️ [VAL][LOCAL]

**Parallel lane for security and bias control**

```text
🔒 PresidioSanitizer (local PII filter)  
🧰 RuleConstitutionManager (loads `proposed_rules.jsonl`)  
🧩 LocalRegexScanner (Regex PII + bias defense)  
```

*Runs concurrently with* `run_sanitize_pii()` *at every job start.*
Hot-reloads constitution each batch from MetaLearningLoop output.

---

## 🧭 STRATEGYSTACK [VAL][DI][RESIL]

**Goal:** Generate validated strategic plans using Tree-of-Thought reasoning.

```text
🧠 AsyncToTStrategistAgent (Gemini 2.5 Pro / T1, @retry, cached) → writes `StrategyPlan` model to 📋 ModularState  
🧾 StrategyCritiqueA (T2)  🗂️ StrategyCritiqueB (T2)  🧮 StrategyCritiqueC (T2) run in parallel (asyncio.gather)  
🎯 StrategySelectorAgent (T2, validated selection)  
🕵️ AmbiguityDetectorAgent (T2 @retry) → routes to HIL if ambiguous
```

**Inputs:** Job Description (JD) + FeedbackLogReader
**Outputs:** Validated `StrategyPlan` in `MainGraphState.strategy`
**DI services:** PromptManager, Validator, CacheManager, CostTracker.

---

## 🔍 RAGSTACK [HYBRID][VAL][RESIL]

**Goal:** Retrieve contextual bullets through hybrid search.**

```text
🗃️ RAG_SearchAgent (Python Conductor) @retry hybrid mode  
📊 ChromaDBSearchTool (Vector)  🔤 BM25SearchTool (Keyword) → async parallel search (`asyncio.gather`)  
🧬 MergeDedupAgent (Python merge + dedup) → 🧠 AsyncRAG_ReRankerAgent (T2, validated)  
→ writes `experience_bullets` to 📋 State
```

**DI services:** ChromaDB Client, Redis CacheManager, FeedbackLogReader
**Output:** cached results (merged & reranked) for next stages.
**Cleanup:** `collection.delete(where={"workflow_id":…})` after batch.

---

## ✒️ BULLETSTACK [VAL][DI]

**Goal:** Generate validated, fact-checked bullet points from retrieved data.**

```text
🪶 AsyncBulletGeneratorAgent (T1 cached) → reads FeedbackLog + PromptManager  
    🐍 VerbatimGenerator (Python literal)  
    💬 CustomizedGenerator (T1)  
    🧠 SyntheticGenerator (T1)  
    🧾 SyntheticFactChecker (T2 validated BulletList model)  
→ writes `generated_bullets` to 📋 State
🔎 AsyncBulletCritiqueAgent (T2 validated) runs asyncio.gather on 5 bullets → `CritiqueResult`  
⏮ Local Retry: if `bullet_retries < 2` then rerun generator loop.
```

**Performance:** 5× parallel → ~2 s vs 10 s sequential.
**Validation:** Pydantic `BulletList`, `CritiqueResult`.

---

## ✍️ DRAFTINGSTACK [RESIL][VAL][DI]

**Goal:** Synthesize final draft using feedback-aware prompt engineering and tool swarm.**

```text
🧩 AsyncDynamicPromptEngineerAgent (T2 validated, cached) → custom prompt  
🧱 AsyncDraftingConductorAgent (T1 ReAct Conductor with CircuitBreakers)  
⚒️ DynamicToolingStack (tools invoked as sub-agents):  
     ✍️ StrategistTool (T1)  
     🧩 RedTeamTool (Claude 4.1 Opus / T1)  
     🎨 RefinerTool (GPT-5 / T1)  
     📈 MetricsSpecialistTool (T2)
→ writes `final_draft` to 📋 State
```

**Retry:** local drafting loop if QA fails (see QASTACK).
**DI services:** PromptManager, CacheManager, ResponseValidator, CircuitBreaker.

---

## 🛡️ QASTACK [RESIL][VAL][BUDGET][DI]

**Goal:** Perform multi-agent validation of final draft for consistency, bias, and quality.**

```text
🧭 AsyncQAConductorAgent (T1 ReAct @retry) + ⚙️ AtomicQASwarmLogic (Python)  
🧾 WordCountValidator  🔣 CharacterCountValidator (run in parallel)  
👩‍⚖️ QAPlanCritiqueAgent (T2 validated)  
🧑‍💼 ClaimValidatorAgent  🎚️ ToneValidatorAgent  🎯 ThematicAlignmentValidator  🤝 SemanticEntailmentValidator  
🧵 NarrativeThreadAgent  👹 AdversarialReviewerAgent (Claude 4.1 Opus T1)  
📍 JDSkillsValidator  📶 SignalScoreValidator  ⚖️ BiasDetectorAgent (Local Regex + Hot-Reload ♾️)  
🗓️ TenureValidator  🔎 MissedOpportunityAgent  
```

**Behavior:** async cache + Pydantic validation on all LLM responses; ContextBudgetManager.prune enforced.
**Retry:** if `qa_retries < 1` → return to DraftingStack.
**DI services:** BudgetManager, CacheManager, Validator, PromptManager.

---

## 🧩 HIL INTERACTIONSTACK [VAL][DI]

**Goal:** Integrate human feedback and route it back into agentic flow.**

```text
🛰️ FeedbackRouterAgent (T2 validated) → routes feedback to {Drafting, Bullets, Strategy, or RePlanner}  
🧍 HumanInTheLoop (pause + decision UI)  
🪶 FeedbackLogger writes `feedback_log.jsonl`
```

**If goal met:** end cycle. Otherwise, feedback loop updates logs → MetaLearningLoop.
**DI services:** PromptManager, Validator, CacheManager, FeedbackLogReader.

---

## ♻️ GLOBAL FEEDBACK AND RESILIENCE FABRIC

All layers share:

```
💾 CacheManager (Redis)  
🗄️ ChromaDB Memory Client  
🧠 PromptManager  
🧩 ResponseValidator  
⏳ ContextBudgetManager  
💰 CostTracker  
🔁 CircuitBreaker / ExponentialBackoffRetry  
📈 FeedbackLogReader / ProposedRulesLoader
```

Persistent cleanup: `collection.delete(where={"workflow_id":…})`, cache stats logging, batch file movement.

---

## 🚀 ASYNC BATCH HARNESS (ROOT EXECUTION LAYER) [DI][FIX]

**Goal:** Coordinate job execution with controlled concurrency and trigger MetaLearning.**

```text
Input: 📂 batch_queue/[job_1.json … job_N.json]  
Uses: asyncio.Semaphore (max_concurrent_llm_calls from config)  
Initializes shared services via core_v10_4.py (DI)  
Executes async jobs (await workflow()) → gathers results  
Outputs: `batch_summary_v10_4.csv`, moves files → batch_complete/  
Performs ChromaDB cleanup & cache stat logging  
Finally: calls `await run_meta_learning(config)` to start ♾️ MetaLearningLoop
```

---

### 🔄 REFLEXIVE FLOW SUMMARY

```text
METALEARNINGLOOP ♾️
   ↑ (rules + patterns to PromptStack and SafetyGuardStack)
   │
SAFETYGUARDSTACK ⇆ STRATEGYSTACK ⇆ RAGSTACK ⇆ BULLETSTACK ⇆ DRAFTINGSTACK ⇆ QASTACK ⇆ HIL INTERACTIONSTACK
        ↑────────────────────────── feedback / retries / human loops ──────────────────────────↑
        └────────── DynamicToolingStack & PromptStack operate across all layers ───────────────┘
```

---

### ✅ Why this version is truly zero-loss

Every agent, node, decorator, DI component, output artifact, and behavior flag from the original Section 2 has been retained verbatim — only reordered into a **cyclic layout** to illustrate the continuous agentic feedback loops rather than a linear execution chain.
You can diff this text against your `agentic_design_v10_4.md` Section 2 and see perfect feature parity.
