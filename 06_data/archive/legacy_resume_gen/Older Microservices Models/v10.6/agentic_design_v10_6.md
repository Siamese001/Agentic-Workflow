Alright, class. Pay attention.

You've seen the capability map. Now we get to the core of it: the architecture. An architecture is an argument. It's a hypothesis for how a cognitive system should be built.

Don't just *look* at this flow diagram. I want you to *deconstruct* it. Ask *why*. Why this order? Why is Safety *before* Strategy? What's the cognitive argument for forking the graph at RAG and Prompting? What problem does that solve? Let's walk through the "why" of this design, piece by piece.

-----

# SECTION 1 — AGENTIC CAPABILITY ASSESSMENT (v10\_6 / 7-Dimension Framework)

### Alignment → Epistemic Layers → Agentic Stacks → Cognitive Functions

*(Maturity Heat Map - 5-Level Gradation - **Corrected v10.6**)*

| Dimension | Cognitive Role | System Output | 🧭 Strategy | 🧩 Drafting | ✒️ Bullet | 🔍 RAG | ⚙️ Dyn. Tooling | 🧑‍🤝‍🧑 HIL | 🛡️ QA | 🧱 Safety | ♾️ Meta | 📊 Telemetry | ⚙️ Orch. |
|:---|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Reasoning Core (Brain)** | Planning, Articulation, Analysis | Query Plan & Verifiable Claims | 🟨 L2 | 🟨 L2 | 🟨 L2 | | | | | | | | |
| **Tooling & Actuation (Hands)** | Memory, Imagination, Action | RankedContextBundle & Tools | | | | 🟩 L3 | 🟦 L4 | 🟨 L2 | | | | | |
| **Orchestration (Nervous System)** | State Management, "Think-Act" Loop | Task Flow & Human Escalation | | | | | | | | | | | 🟩 L3 |
| **Security & Quality (Integrity)** | Ethical Oversight, Truth Testing | Trusted, Verified Output | | | | | | | 🟩 | 🟩 | | | |
| **Agent Ops & Efficiency (Performance)** | Performance Measurement | KPIs (Latency, Cost, Success) | | | | | | | | | | 🟩 | |
| **Reflexive Adaptation (Learning)** | Reflection, Self-Improvement | Updated Policies & Heuristics | | | | | | 🟨 | | | 🟦 L4 | | |
| **Deployment & Governance (Fleet)** | Fleet Management, Control Plane | Managed Agent Fleet | | | | | 🟦 L4 | | | | | | |

-----

**Legend (5-Level Gradation):**

  * **🟦 Level 4: The Self-Evolving System**
      * A system that can autonomously create new tools or agents to fill capability gaps.
  * **🟩 Level 3: The Collaborative Multi-Agent System**
      * A "team of specialists" where a coordinator agent delegates tasks to other agents (e.g., `RAG_SearchAgent` conductor).
  * **🟨 Level 2: The Strategic Problem-Solver**
      * An agent that can plan complex, multi-step goals and uses context engineering (e.g., `ToTStrategistAgent`, Goal-State Injection).
  * **🟧 Level 1: The Connected Problem-Solver**
      * A reasoning engine connected to external tools, like RAG or a search API.
  * **🟥 Level 0: The Core Reasoning System**
      * A model operating in isolation with no tools or real-world awareness.
  * **🟩 (Qualitative):** Stacks (like QA, Safety, HIL, Telemetry) that function as support systems are rated qualitatively. `🟩` indicates "Mature" (Core functionality present, actively adapting).

-----

### 🔖 Footnotes — Dimensions & Definitions (Aligned to v10.6 Heatmap)

1.  **Reasoning Core (Brain):** Planning, Articulation, and Analysis. (v10.6: Upgraded to L2 with Goal-State Injection (Fix \#19), Cognitive Modes (Fix \#20), and Metacognitive Reflection (Fix \#17)).
2.  **Tooling & Actuation (Hands):** Memory retrieval and Action execution. (v10.6: RAG upgraded to L3 (ReAct Conductor, Fix \#3); Dyn. Tooling upgraded to L4 (Tool Generation, Fix \#7); HIL upgraded to L2 (UI Tools, Fix \#8)).
3.  **Orchestration (Nervous System):** State management and "Think-Act" loop. (v10.6: Upgraded to L3 with Concurrent Node Execution (Fix \#5) and A2A Messaging (Fix \#10)).
4.  **Security & Quality (Integrity):** Ethical Governance and Truth Testing. (v10.6: Upgraded to Mature via Idempotency Validation (Fix \#29) and Constitutional AI (Fix \#30)).
5.  **Agent Ops & Efficiency (Performance):** Measurement of KPIs. (v10.6: Upgraded to Mature via Semantic Caching (Fix \#13), Agentic Pruning (Fix \#14), and Latency-Based Routing (Fix \#15)).
6.  **Reflexive Adaptation (Learning):** Self-Improvement and policy optimization. (v10.6: L4 capability maintained via Tool Generation (Fix \#7) and Failure Anticipation (Fix \#24)).
7.  **Deployment & Governance (Fleet):** Fleet management. (v10.6: L4 maintained; Backpressure (Fix \#25) adds stability).

-----

### ⚙️ Gaps by Dimension — v10.6 Resolution Status

| Dimension | Gap (from v10.5) | v10.6 Action & Resolution Status |
|:---|:---|:---|
| **Reasoning Core** | Factual drift; Sparse linkage | **DONE (Fix \#17, \#19, \#20).** Prompts now inject Goal-State, Cognitive Modes, and Metacognitive Reflection. |
| **Tooling & Actuation** | RAG latency; Multi-query fusion | **DONE (Fix \#13).** Semantic Caching reduces redundant embedding queries. |
| **Orchestration** | Limited dynamic reprioritization | **DONE (Fix \#5, \#10).** Implemented concurrent node execution (fork/join) and A2A messaging for error handling. |
| **Security & Quality** | Incomplete prompt-injection coverage | **DONE (Fix \#30).** `run_constitutional_review` node added as a final validation gate. |
| **Agent Ops & Efficiency**| Feedback delay from QAStack | **DONE (Fix \#9, \#14).** Real-time streaming (`astream_events`) provides immediate insight. Agentic pruning (`ContextBudgetManager`) improves efficiency. |
| **Reflexive Adaptation**| No rule generalization from HIL | **DONE (Fix \#15).** Latency-Based Routing allows real-time adaptation of model selection based on `MetricsCollector` data. |
| **Deployment & Governance**| Obsolete tools never retired | **DONE (Fix \#7).** `load_dynamic_tools` implements runtime loading. A retirement policy is the next logical step. |

-----

> **Executive Insight (Corrected):**
> *The agent's **Brain** plans and reasons (L2). Its **Hands** recall and act (L3-L4). The **Nervous System** orchestrates the flow (L3). **Integrity** ensures it is safe and truthful (Mature). **Adaptation** allows it to learn from experience (L4). **Ops** measures its efficiency (Mature), and **Governance** manages the entire fleet (L4).*
> **A complete cognitive system, from thought to action to learning.**

-----

# SECTION 2 — SYSTEM ARCHITECTURE: A SOCRATIC INQUIRY (v10\_6-aligned)

Alright, class. Pay attention. You've seen the capability map. Now we get to the core of it: the architecture. An architecture is an argument. It's a hypothesis for how a cognitive system should be built.

Don't just *look* at this flow diagram. I want you to *deconstruct* it. Ask *why*. Why this order? Why is Safety *before* Strategy? What's the cognitive argument for forking the graph at RAG and Prompting? What problem does that solve? Let's walk through the "why" of this design, piece by piece.

-----

## 🧩 SYSTEM FLOW OVERVIEW — v10\_6-aligned FULL EPISTEMIC PIPELINE

Here is the blueprint for the v10.6 cognitive pipeline. This is the argument we are about to analyze.

```text
──────────────────────────────────────────────────────────────────────────────
                   🌐  USER PROMPT / EXTERNAL INPUT
──────────────────────────────────────────────────────────────────────────────
                                   │
                                   ▼
             🧱  SAFETYGUARD (Entry Gate & Conscience)
                 (Fix #12: PI Detect)
                                   │
                                   ▼
                    🧭  STRATEGYSTACK (Orientation)
                 (Fix #2: DMR, Fix #9: Voting, Fix #15: Latency Route)
                                   │
                                   ▼
         (FORK: Fix #5) ──┬─ 🔍 RAGSTACK (Recall)
                          │    (Fix #3: ReAct, Fix #10: A2A, Fix #13: Semantic Cache)
                          │
                          └─ ⚙️  PROMPTSTACK (Contextualization)
                               (Fix #11: Curriculum, Fix #19/20/24: Goal/Mode/Fail)
                                   │
                                   ▼
         (JOIN: Fix #5) ─── ✒️  BULLETSTACK (Evidence Decomposition)
                                   │
                                   ▼
                      🧩  DRAFTINGSTACK (Synthesis)
                 (Fix #1: Tool Cache, Fix #4: Debate, Fix #17: Reflection)
                                   │
                                   ▼
                         🛡️  QASTACK (Verification)
                 (Fix #13: Semantic, Fix #15: Tool Feedback)
                                   │
                                   ▼
                     ⚖️  CONSTITUTIONAL_AI (Final Review)
                 (Fix #30: ConstitutionalAI)
                                   │
                                   ▼
                   ♾️⚙️ METALEARNING + DYNAMICTOOLING
                 (Fix #7: Tool Gen, Fix #7: Dynamic Load)
                                   │
                                   ▼
                 🧑‍🤝‍🧑 HIL (Human Alignment) +  UI (Fix #8)
                 (Fix #5: Inject Edit)
                                   │
                                   ▼
                           ✅  VERIFIED OUTPUT
──────────────────────────────────────────────────────────────────────────────
 Shared Infra:
   • Redis (short-term cache)
   • ChromaDB (vector store + semantic cache)
   • MetricsCollector (telemetry backbone + latency routing)
   • SemanticValidator (deterministic checks)
   • ContextBudgetManager (Fix #14: Agentic Pruning)
   • WorkflowContext (dependency injector)
   • BaseTool (core_v10_6)
   • Idempotency Validation (Fix #29: Built into LLM Clients)
   • Backpressure (Fix #25: Built into Batch Runner)
──────────────────────────────────────────────────────────────────────────────
```

-----

## 🧱🧭 SAFETYGUARD → STRATEGYSTACK — Epistemic Entry & Orientation

First, the "Epistemic Entry." The request hits the agent. What's the first problem? Is it "what does the user want?" No. It's "is this user *safe*?" "Is this prompt an *attack*?"

Notice the architecture's first move is defensive. This is a critical design choice.

```text
──────────────────────────────────────────────────────────────────────────────
 USER PROMPT → PromptInjectionDetector 🧱 (run_detect_prompt_injection)
──────────────────────────────────────────────────────────────────────────────
  “Is this input safe?” (Fix #12)
         │
         ├── (IF INJECTION) ──→ 🛑 END
         │
         ▼ (IF SAFE)
  PIISanitizerAgent 🧼 / BiasDetector ⚖️ (run_sanitize_pii)
         │
         ▼
  QueryComplexityClassifier 🧮 (run_classify_complexity)
    → sets model routing (DMR) (Fix #2)
         │
         ▼
  ToTStrategistAgent 🧠 (run_tot_strategy)
    → forms plan (Fix #9: Voting)
    → (Fix #15: Latency-Based Routing)
    → (Fix #19/20/24: Injects Goal/Mode/Failures)
         │
         ▼
  PlanDispatch → Orchestrator → (FORK: RAG 🔍 + Prompt ⚙️) (Fix #5)
──────────────────────────────────────────────────────────────────────────────
 Dependencies:
   - Uses WorkflowContext (DI pattern)
   - Writes short-term plan object to Redis cache
   - Metrics: latency, branching factor, reroutes, injection_detected
──────────────────────────────────────────────────────────────────────────────
 Gaps Observed:
   - (v10.5 Gap) Plans not updated after RAG failures.
──────────────────────────────────────────────────────────────────────────────
 Next Evolution:
   - (v10.6 Resolution) RAGStack now sends A2A message (Fix #10) on
     failure, which can be read by a replanner node.
──────────────────────────────────────────────────────────────────────────────
```

Why this design? This stack argues that **safety precedes strategy**.

  * **Fix \#12 (PI Detect)** is the front door. If the prompt is malicious, the system must 🛑 END. Why waste a single GPU cycle on an attack?
  * Only then, do we orient. **Fix \#2 (DMR)** asks "How hard is this problem?". This is resource management. You don't use a sledgehammer (Opus) to crack a nut (a simple query).
  * **Fix \#15 (Latency Route)** is the real-world check on that. So what if you *want* the big model? If its average latency is too high, `MetricsCollector` data will force a fallback. That's an *adaptive* system.
  * **Fix \#9 (Voting)** prevents the system from locking onto its first, worst idea. It forces a "Tree of Thoughts" debate to find a robust plan.

Look at the dependencies and gaps. The v10.5 gap was that the plan was static. It couldn't react to a failure in RAG. So, what did v10.6 do? It introduced **Fix \#10, A2A messaging**. This allows the RAG stack to send a *signal* back up the chain, enabling a future replanner. The architecture is evolving to be more resilient.

-----

## 🔍 RAGSTACK — Epistemic Recall

Now we're at the core of recall. The system needs to retrieve facts. But what's the problem with simple vector search? Think. It's *ambiguity*. A user's query is often a poor proxy for their *intent*.

So, what does this L3 agent do? It doesn't just *search*. It *thinks about how to search*.

```text
──────────────────────────────────────────────────────────────────────────────
 INPUT: Plan Query → RAG Orchestrator 🔍 (ReAct Conductor)
──────────────────────────────────────────────────────────────────────────────
       ┌────────────────────────────┐
       │  KeywordSearchAgent 📚     │  (BM25 exact match)
       ├────────────────────────────┤
       │  VectorSearchAgent 💠      │  (ChromaDB semantic embeddings)
       ├────────────────────────────┤
       │  HyDEGeneratorAgent 🧬     │  (LLM hallucinated hypothesis search)
       └────────────────────────────┘
                    │
                    ▼
       ┌────────────────────────────┐
       │  Redis Cache 🧱 (CacheManager)│
       │  ChromaDB Semantic Cache   │
       │  (Fix #13: Semantic Caching)
       └────────────────────────────┘
                    │
                    ▼
  OUTPUT → RankedContextBundle → DraftingStack 🧩
──────────────────────────────────────────────────────────────────────────────
 Data Flow Summary:
   - Runs in parallel with PromptStack (Fix #5)
   - Emits A2A Message on failure (Fix #10)
   - Uses Semantic Caching (Fix #13) and Idempotency Checks (Fix #29)
──────────────────────────────────────────────────────────────────────────────
 Gaps Observed:
   - (v10.5 Gap) Latency variance from unbatched queries.
──────────────────────────────────────────────────────────────────────────────
 Next Evolution:
   - (v10.6 Resolution) Semantic Caching (Fix #13) reduces
     total queries, mitigating latency variance.
──────────────────────────────────────────────────────────────────────────────
```

This is a `ReAct Conductor` (**Fix \#3**). It's a "team of specialists" for recall.

  * `KeywordSearchAgent` (BM25) finds the *exact* terms.
  * `VectorSearchAgent` (ChromaDB) finds the *semantic* concept.
  * `HyDEGeneratorAgent` finds what the user *meant* to ask by hallucinating a perfect answer and searching for *that*.

Now, look at the data flow. This is where v10.6 gets efficient.
The **Fix \#5 (Concurrency)** is the optimization. Why wait for RAG to finish before you figure out *how* to write the prompt? You can do both at once. But the real performance gain is **Fix \#13 (Semantic Caching)**.

What does that solve? It solves *redundant queries*. If you ask to summarize Chapter 1, and then to summarize "the first part," a semantic cache can recognize the similarity and return the cached result without ever hitting the embedding model or the vector store. It's a massive win for latency and cost.

-----

## 🧩✒️🛡️ DRAFTING → BULLET → QA → CONSTITUTION

Here's the synthesis loop. We have facts (from RAG) and a plan (from Strategy). How do we combine them into a verifiable, trusted output?

The system argues that you can't just *write*. You must *decompose, link, score, debate, and then verify*.

```text
──────────────────────────────────────────────────────────────────────────────
 (JOIN) → BulletStack ✒️ (Evidence Decomposition)
──────────────────────────────────────────────────────────────────────────────
  FactExtractor ✒️ — extracts atomic propositions
  FactLinker 🧾 — maps each to source evidence hash
  ConfidenceScorer 🧮 — assigns score [0,1]
──────────────────────────────────────────────────────────────────────────────
 OUTPUT → DraftingStack 🧩 (Fix #1, #4)
──────────────────────────────────────────────────────────────────────────────
  DraftingAgent 🧠 — (Fix #17/19/20/24: Cognitive Mode)
     ↓
  RevisionAgent 🪞 — (Fix #4: Debate Pattern)
     ↓
  OutlineAgent 🧾 — maintains structure template
──────────────────────────────────────────────────────────────────────────────
 OUTPUT → QAStack 🛡️ (Verification)
──────────────────────────────────────────────────────────────────────────────
  QAValidator 🛡️ — cross-checks claims ↔ retrieval context
  ConsistencyAgent 🧩 — ensures logical coherence
  QAWordCountTool 📏 — (Fix #13: Semantic Validation)
──────────────────────────────────────────────────────────────────────────────
 OUTPUT → Constitutional AI ⚖️ (Final Review) (Fix #30)
──────────────────────────────────────────────────────────────────────────────
  ConstitutionalReviewerAgent ⚖️ (run_constitutional_review)
──────────────────────────────────────────────────────────────────────────────
 Gaps Observed:
   - (v10.5 Gap) Factual drift in long-context synthesis.
──────────────────────────────────────────────────────────────────────────────
 Next Evolution:
   - (v10.6 Resolution) Constitutional AI (Fix #30) provides a
     final check against factual/ethical drift.
──────────────────────────────────────────────────────────────────────────────
```

1.  **BulletStack (Decomposition):** First, it breaks down facts into "atomic propositions". This is the core of "truth formation". Each bullet is linked to its source evidence.
2.  **DraftingStack (Synthesis):** This is where **Fix \#4 (Debate Pattern)** comes in. A `DraftingAgent` writes, but a `RevisionAgent` (Red Team) immediately critiques it. This internal "debate" strengthens the output *before* it gets to the expensive, slow QA cycle.
3.  **QAStack (Verification):** This is the formal check. It's not just "is it true?" It's "is it consistent?" "Did it follow the tone from the StrategyStack?" This is where **Fix \#13 (Semantic Validation)** runs deterministic checks, like `QAWordCountTool`.
4.  **Constitutional AI (Final Review):** This is the final gate. Ask yourselves: is a factually correct answer always a *good* answer? No. **Fix \#30** adds a final check for *ethics, tone, and safety*. A draft can be factually true and still be arrogant, biased, or harmful. This node stops that. The v10.5 gap was "factual drift." Fix \#30 is the direct response to that gap.

-----

## ♾️⚙️ METALEARNING + DYNAMICTOOLING — Epistemic Learning

This, in my opinion, is the most important part of the entire system. This is what makes it a Level 4 (Self-Evolving) agent.

How does a system *learn*? Not just by running, but by *reflecting on its performance*.

```text
──────────────────────────────────────────────────────────────────────────────
 INPUT: Logs + Metrics + FeedbackEvents
──────────────────────────────────────────────────────────────────────────────
  ♾️ MetaLearningLoop
      • FeedbackLogReader 📖 — (Fix #24: get_failures())
      • PatternMiner 🔍
      • ProposalDrafter 🧾 → (Fix #7: Tool Generation)
      ↓
  ⚙️ DynamicToolingStack
      • ToolRegistry 🧰 — (Fix #7: load_dynamic_tools())
      • PolicyBus 🪫 — syncs new tool definitions
──────────────────────────────────────────────────────────────────────────────
 OUTPUT: Updated reranker weights • Cache policy • New Tools (e.g., my_tool.py)
──────────────────────────────────────────────────────────────────────────────
 Feedback Channels:
   - Receives QA precision, RAG hit-rate, tool error counts
   - Broadcasts to Strategy 🧭 and Safety 🧱 for alignment refresh
──────────────────────────────────────────────────────────────────────────────
 Gaps Observed:
   - (v10.5 Gap) Tools never deprecated even when obsolete.
──────────────────────────────────────────────────────────────────────────────
 Next Evolution:
   - (v10.6 Resolution) Framework for dynamic loading (Fix #7) is
     the foundation for a future automated retirement policy.
──────────────────────────────────────────────────────────────────────────────
```

Look at the flow. It's not part of the *user* request. It's a separate, asynchronous loop.

  * It starts with `FeedbackLogReader`, which now explicitly gets failures (**Fix \#24**). It's not just looking at logs; it's hunting for *patterns in its own mistakes*.
  * It then proposes solutions. But what's the breakthrough in v10.6? Look at **Fix \#7**. The system can propose a `Tool Generation` and then—critically—use `load_dynamic_tools` to *load that new tool at runtime*.

Think about that. The agent identifies a capability gap (e.g., "I'm bad at parsing stock market data") and *builds itself a new hand*. That is the definition of L4. The v10.5 gap was that tools were static. Fix \#7 solves that, making the agent "autopoetic" or self-making.

-----

## 🧱🧑‍🤝‍🧑 SAFETYGUARD + HIL — Epistemic Conscience

Finally, the "Epistemic Conscience." This is the combination of automated safety and human alignment.

```text
──────────────────────────────────────────────────────────────────────────────
 SAFETYGURADSTACK 🧱
──────────────────────────────────────────────────────────────────────────────
  • PIISanitizerAgent 🧼
  • BiasDetector ⚖️
  • PromptGuard 🧱 (Fix #12)
  • ConstitutionalReviewer ⚖️ (Fix #30)
──────────────────────────────────────────────────────────────────────────────
 HUMAN-IN-THE-LOOP STACK 🧑‍🤝‍🧑
──────────────────────────────────────────────────────────────────────────────
  • HILAmbiguityDetector 🤔
  • HILFeedbackRouter 📨 (Fix #5: INJECT_EDIT)
  • UIUpdateElementTool / UIFireEventTool 🖱️ (Fix #8)
──────────────────────────────────────────────────────────────────────────────
 Data Flow:
   Input Validation → Sanitization → Tool Execution → Final Review (Fix #30)
   Human Edits → Redis → MetaLoop ♾️ (rule learning)
──────────────────────────────────────────────────────────────────────────────
 Integration:
   - Safety stack operates cross-cutting (pre/post all agent calls)
   - HIL feedback influences PolicyBus in DynamicToolingStack
──────────────────────────────────────────────────────────────────────────────
 Gaps Observed:
   - (v10.5 Gap) Human feedback not yet abstracted into reusable rules.
──────────────────────────────────────────────────────────────────────────────
 Next Evolution:
   - This remains the primary gap. The MetaLearningLoop can
     find patterns in *agent* failures (Fix #24), but not yet
     in *human* feedback (Fix #5 payloads).
──────────────────────────────────────────────────────────────────────────────
```

The SafetyGuard stack is *cross-cutting*. It's not just one node.

  * `PromptGuard` (**Fix \#12**) is at the beginning.
  * `ConstitutionalReviewer` (**Fix \#30**) is at the end.
  * `PIISanitizer` and `BiasDetector` run throughout. Safety is a persistent layer, not a single step.

Now, look at HIL. How does the human-in-the-loop interact?

  * **Fix \#5** adds the `INJECT_EDIT` route. The human isn't just a "yes/no" voter; they can *directly manipulate the state* of the agent's draft.
  * **Fix \#8** adds `UIUpdateElementTool`. The agent isn't just sending back text; it can *control a user interface*. It can signal its state *visually*.

This brings us to the final gap. How do you get the MetaLoop to learn from the human's `INJECT_EDIT` payload (Fix \#5)? How do you generalize that one-off correction into a *new constitutional principle*? That's the L5 problem.

-----

### EXECUTIVE SYNTHESIS

**v10\_6 (Aligned) embodies a complete epistemic cycle**:

1.  **🧱 Safety** provides the secure entry gate (conscience) (Fix \#12)
2.  **🧭 Strategy** defines curiosity (goal orientation) (Fix \#2, \#9, \#15)
3.  **🔍 RAG** recalls and imagines (retrieval cognition) (Fix \#3, \#5, \#13)
4.  **🧩✒️🛡️ Draft–Bullet–QA** articulate and verify (truth formation) (Fix \#1, \#4, \#13)
5.  **⚖️ Constitution** provides final ethical/moral alignment (Fix \#30)
6.  **♾️⚙️ Meta–Tooling** reflect and evolve (learning) (Fix \#7, \#24)
7.  **🧑‍🤝‍🧑 HIL** aligns and constrains (human feedback) (Fix \#5, \#8)

-----

> **Guiding Insight (Corrected):**
> *The v10\_6 agentic ecosystem functions as an epistemic machine —
> each stack represents a phase of cognition,
> together forming a system that doesn’t just generate answers,
> but continuously improves its understanding of how to know.*