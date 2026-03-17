# Agentic Workflow — Deterministic Multi-Agent AI Platform

## Overview
This repository provides a production-grade agentic AI platform that enforces deterministic execution, embedded governance, and full-system observability, enabling enterprises to move from AI experimentation to reliable, auditable, and scalable AI systems.

> **Core Principle:** AI systems should behave like reliable software systems, not probabilistic experiments.

Most enterprise AI implementations today face three core issues: **non-reproducible behavior, limited observability, and weak governance.** This platform addresses these directly by treating AI as a systems engineering problem rather than just a modeling problem, ensuring reproducibility, traceability, and continuous improvement across all agent interactions.

---

## Architecture & Layered Design (L0–L6)

The system enforces a strict separation of responsibilities across layers to ensure scalability, determinism, and operational clarity.

```
User / API Request
        ↓
┌─────────────────────────────────────────┐
│  L0: Routing                            │
│  (Intent Classification & Workload)     │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────┐    ┌──────────────────┐
│  L1: Cognition          │◄───│  L4: State       │
│  (Bounded LLM)          │    │  (ADG, Memory)   │
└──────────┬──────────────┘    └────────┬─────────┘
           ↓                            │
┌─────────────────────────┐             │
│  L2: Execution          │             │
│  (PTC Tool Calling)     │             │
└──────────┬──────────────┘             │
           ↓                            │
┌─────────────────────────┐    ┌────────┴─────────┐
│  L3: Orchestration      │───→│  L5: Safety      │
│  (Multi-Agent)          │    │  (Guardrails)    │
└──────────┬──────────────┘    └────────┬─────────┘
           ↓                            ↓
┌──────────────────────────────────────────────────┐
│  L6: Observability                               │
│  (Tracing & Determinism Digests)                 │
└──────────────────────────────────────────────────┘
```

* **L0 Routing:** Deterministic routing across model tiers and workflows.
* **L1 Cognition:** Controlled LLM interaction with bounded stochasticity.
* **L2 Execution:** Programmatic Tool Calling (PTC) with schema enforcement.
* **L3 Orchestration:** Multi-agent coordination and workflow management.
* **L4 State:** Agentic Dependency Graph (ADG), memory, and checkpointing.
* **L5 Safety:** Guardrails, policy enforcement, and HITL triggers.
* **L6 Observability:** Execution tracing, determinism validation, and metrics.

---

## Key Differentiators

### 1. Deterministic Replay (System-Level Determinism)
Determinism is enforced at the system layer, not the model layer. Determinism is enforced across orchestration, tool execution, and state transitions, while the LLM layer remains probabilistic but bounded and controlled.

```
Live Execution          Traces & Digests          Graph Storage
┌──────────────┐              →              ┌─────────────────┐
│ L1-L3        │                             │ SQLite (ADG)    │
│ Activity     │                             │ ~69K Nodes      │
└──────┬───────┘                             │ ~500K Edges     │
       ↑                                     └────────┬────────┘
       │                                              │
       │ State Hydration              Query / Fetch  │
       │                                              ↓
┌──────┴────────┐      Hash Match      ┌──────────────────────┐
│ Replay Engine │◄─────────────────────│ CI/CD / Debug        │
└───────────────┘                      └──────────────────────┘
```

* Execution traces recorded across all layers.
* Determinism digests validate execution consistency.
* Replay engine re-executes workflows against captured state.
* Controlled LLM parameters (temperature, seeds, caching boundaries).
* **Result:** Audit-ready execution, reproducible workflows, and CI/CD validation for AI systems.

### 2. Agentic Dependency Graph (ADG)
A fully indexed, queryable graph representing system behavior.

* **~69K nodes** and **~500K+ edges** observed in production-scale ADG snapshots.
* Edge types: `calls`, `reads_from`, `writes_to`, `emits_determinism_digest`.
* SQLite-backed for deterministic state inspection and replay.
* **Result:** End-to-end observability and instant root cause analysis across complex agent workflows.

### 3. Built-In Governance & Safety
Governance is embedded directly into execution flows.

* C0 informational boundary prevents unsafe state mutation.
* Guardrails enforced pre and post execution.
* HITL triggered dynamically based on risk thresholds.
* Policy enforcement tied to execution graph state.
* **Result:** Enterprise-grade safety and compliance without sacrificing velocity.

### 4. Programmatic Tool Calling (PTC)
Tool usage is deterministic and contract-driven.

```
┌──────────────────────┐
│  L1: Cognition       │
│  (JSON Intent)       │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│  Contract Schema     │──(Fail)──→ Error / Self-Correction
│  Validator           │
└──────────┬───────────┘
           ↓ (Pass)
┌──────────────────────┐
│  L2: Tool Execution  │
└──────────────────────┘
```

* Explicit tool schemas and invocation contracts.
* No free-form or inferred tool selection.
* Execution routed through controlled interfaces.
* **Result:** Eliminates hallucinated tool calls and ensures reliable automation.

### 5. Meta-Learning Feedback Loop
The system improves continuously through execution feedback.

```
┌─────────────────────┐         ┌──────────────────────┐
│ ADG Execution Trace │────────→│ Text Embedding Model │
└─────────────────────┘         └──────────┬───────────┘
                                           ↓
┌─────────────────────┐         ┌──────────────────────┐
│ L0 / L3 Future      │◄────────│ Vector Store (FAISS) │
│ Routing             │         └──────────────────────┘
└─────────────────────┘
```

* Execution traces → embeddings → retrieval signals.
* Pattern detection across runs.
* Healing agents adjust future execution paths.
* **Result:** Reduced failure recurrence and compounding system intelligence.

### 6. Semantic Cache + Redis L1 Retrieval Gate
Efficient retrieval and cost optimization layer.

```
┌─────────────────┐         ┌──────────────────┐
│ Incoming Query  │────────→│ Redis L1 Cache   │──(Hit)──→ Fast Return
└─────────────────┘         └────────┬─────────┘
                                     │
                                   (Miss)
                                     ↓
                            ┌─────────────────┐
                            │ L1 Cognition    │
                            │ (LLM)           │
                            └─────────────────┘
```

* Redis-based hot cache for low-latency access.
* Embedding similarity for semantic cache hits.
* Deterministic validation of cached responses.
* **Result:** Lower latency and significant reduction in LLM cost footprint.

### 7. Human-in-the-Loop (HITL) as a System Primitive
Human oversight is embedded, not external.

* Triggered by policy and risk scoring.
* Integrated into orchestration flows.
* Fully traceable within ADG.
* **Result:** Increased trust, auditability, and controlled deployment of critical workflows.

---

## Enterprise Impact

| Capability | Enterprise Outcome |
| :--- | :--- |
| **Deterministic Replay** | Audit-ready AI systems with CI/CD compatibility |
| **ADG Observability** | 10x faster debugging and precise root cause analysis |
| **Embedded Governance** | Reduced compliance risk and safe data boundaries |
| **Programmatic Tool Calling**| Reliable automation with zero tool hallucination |
| **Meta-Learning System** | Continuous improvement and reduced failure recurrence |
| **Semantic Cache** | Lower latency and reduced infrastructure cost |

---

## Tech Stack

* **Languages:** Python (core orchestration, agents, tooling)
* **Execution Layer:** Custom agentic orchestration framework (L0–L3 separation)
* **State & Graph:** SQLite (ADG), JSON graph snapshots
* **Caching Layer:** Redis (L1 semantic cache, retrieval gating)
* **Embeddings:** OpenAI (`text-embedding-3-large`), BGE (local embedding models)
* **Vector Store:** FAISS (semantic retrieval layer)
* **LLM Routing:** Multi-model routing (OpenAI, local vLLM inference)
* **Infrastructure:** Local-first with containerized services (Redis, supporting services)

---

## Quickstart

# Clone the repository
git clone https://github.com/Siamese001/Agentic-Workflow.git
cd Agentic-Workflow

# Create environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start Redis (L1 cache)
docker-compose up -d redis

# Run a deterministic workflow
python main.py --workflow sample_agentic_run

# Validate replay determinism
python replay.py --run_id <execution_id>
