# Agentic Workflow — Deterministic AI Control Plane

## Overview

This repository provides a **production-grade agentic AI control plane** that transforms AI systems from probabilistic black boxes into **deterministic, auditable, and governable software systems**.

> **Core Principle:** AI systems should behave like reliable software systems, not probabilistic experiments.

Most enterprise AI systems fail for three reasons:

* Non-reproducible behavior
* Lack of auditability
* Uncontrolled execution and state mutation

This platform solves these at the system level, enabling **safe, scalable, enterprise AI deployment**.

---

## System Guarantees (What You Actually Get)

```text
DETERMINISM        → Same input produces the same output
REPLAYABILITY      → Any execution can be reconstructed exactly
NO HIDDEN ENTROPY  → No time or randomness drift
CONTROLLED MUTATION→ No state changes outside governed pathways
FULL PROVENANCE    → Every decision tied to exact state + policy
EXECUTION ISOLATION→ All actions occur in sandboxed environments
GOVERNANCE FIRST   → Nothing executes without policy validation
LAYERED SCALING    → Clean separation enables safe system growth
```

These are not features.
These are **enforced system invariants**.

---

## Architecture & Layered Design (L0–L6)

```
User / API Request
        ↓
┌─────────────────────────────────────────────────────────────────────┐
│  L1: Cognition — Librarian                                            │
│  Bounded LLM reasoning → execution plan                                 │
└────────────────────────────┬──────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────────┐
│  L0: Routing — Dispatcher                                             │
│  Route authority: cache → RAG → action → fallback                       │
└────────────┬─────────────────┬─────────────────────────────┬────────────┘
             ↓                 ↓                             ↓
    ┌────────────────┐ ┌──────────────┐          ┌──────────────────────┐
    │ R1: Cache Hit    │ │ R3: Agentic  │          │ R4/R5: Action/       │
    │ (short-circuit)  │ │ RAG → C0       │          │ Fallback             │
    └────────┬───────┘ └───────┬──────┘          └──────────┬───────────┘
             ↓                 ↓                             ↓
    [RETURN] │          ┌──────────────┐              ┌──────────────────────┐
             └─────────►│ L4: State    │              │ L3: Orchestrator     │
                        │ (Archivist)  │              │ (Sec Head) [opt]     │
                        └───────┬──────┘              └──────────┬───────────┘
                                │                               ↓
                        ┌───────┴──────┐              ┌──────────────────────┐
                        │ C0: Context  │              │ L2: Execution        │
                        │ Engine       │              │ (Execution Staff)    │
                        └──────────────┘              └──────────┬───────────┘
                                                                  ↓
                        ┌──────────────────────────────────────────────────────┐
                        │ L5: Governance — Safety Officer (cross-cutting)      │
                        │ Policy enforcement at all control points               │
                        └───────────────────────┬───────────────────────────────┘
                                                ↓
                        ┌──────────────────────────────────────────────────────┐
                        │ L6: Observability — Observer (shadow evaluation)     │
                        │ Replay, telemetry, future-run learning               │
                        └──────────────────────────────────────────────────────┘
```

**Primary Runtime Path:** L1 → L0 → [opt L3] → L2 | L0 routing invokes C0 context assembly

**State Mutation Path:** L2 output → [L5 validation] → UWG → L4 (sole write authority)

---

## Key Differentiators (What Makes This Different)

### 1. Deterministic Execution (System-Level, Not Model-Level)

Determinism is enforced across:

* orchestration
* execution
* state transitions

The LLM is bounded, but **the system is deterministic**.

**Result:** predictable, testable AI behavior.

---

### 2. Deterministic Replay Engine

Every execution produces:

* full execution trace
* determinism digest
* replay key

```text
Live Run → Trace → Digest → Replay → Hash Match = Verified
```

**Result:**

* Exact incident reconstruction
* CI/CD validation for AI
* Regression detection

---

### 3. Zero Hidden Entropy (Critical Guarantee)

The system eliminates all uncontrolled variability:

* no wall clock (`now()` removed)
* seeded randomness
* controlled model parameters
* fixed execution ordering

**Result:**
No “it worked yesterday but not today” failures.

---

### 4. Controlled Mutation via Universal Write Gateway (UWG)

All state changes must pass through a **single governed interface**.

```text
ANY STATE CHANGE
        ↓
Universal Write Gateway
        ↓
Validated + Signed + Recorded
```

* No direct DB writes
* No silent mutations
* No bypass paths

**Result:**
Total state integrity and auditability.

---

### 5. Full Provenance (Policy + State Binding)

Every action is tied to:

* exact system state
* exact policy version (`policy_hash`)
* full input/output trace

**Result:**
Every decision is explainable, reproducible, and attributable.

---

### 6. Execution Sandbox (L2 Isolation)

All tool execution occurs in a **sealed environment**:

* no side effects outside sandbox
* no uncontrolled external calls
* schema-validated tool usage

**Result:**
Safe, predictable, and contained execution.

---

### 7. Governance as a First-Class System Layer (L5)

Nothing executes without passing:

* pre-execution guardrails
* mutation boundary checks (C0)
* post-execution validation

HITL is embedded into flows, not bolted on.

**Result:**
Enterprise-grade compliance and safety by default.

---

### 8. Agentic Dependency Graph (ADG)

A fully queryable system graph representing:

* execution flow
* state dependencies
* tool interactions
* ~264K nodes
* ~929K edges
* SQLite-backed for deterministic inspection

**Result:**
Instant root cause analysis and full system observability.

---

### 9. Programmatic Tool Calling (PTC)

Tool usage is:

* schema-driven
* contract-enforced
* non-ambiguous

```text
LLM Intent → Schema Validation → Execution
```

**Result:**
Zero hallucinated tool calls.

---

### 10. Meta-Learning Without Runtime Instability

System learns via:

* execution traces
* embeddings
* pattern detection

But:

* no mid-execution mutation
* no live drift

**Result:**
Continuous improvement without breaking active runs.

---

### 11. Semantic Cache + Redis L1 Gate

* Redis = fast retrieval layer
* SQLite (ADG) = canonical truth

**Result:**
Performance without compromising determinism.

---

## System Mental Model

```text
WHY IT MATTERS
→ Deterministic AI systems you can trust

HOW IT WORKS
→ Layered control plane (L0–L6)

WHY IT IS PROVABLE
→ Replay + digests + controlled state
```

---

## Architecture Deep Dive — L0 to L6

The system operates through **six distinct architectural layers**, each with a single accountability and clear authority boundaries.

### Layer Personas & Responsibilities

| Layer | Persona | Core Function | Authority |
|-------|---------|---------------|-----------|
| **L0** | Dispatcher | Route authority — determines execution path (cache, RAG, action, fallback) | Routing decisions only |
| **L1** | Librarian | Reasoning loop — formulates execution plans and dispatches to routing | Plan formulation |
| **L2** | Execution Staff | Tool and action execution — interfaces with external systems | Sandboxed execution only |
| **L3** | Orchestrator | Multi-step coordination — manages complex L2 execution chains | Optional; when complexity requires |
| **L4** | Archivist | Authoritative state — durable writes via UWG only | Read-broad, write-strict |
| **L5** | Safety Officer | Cross-cutting policy plane — enforces guardrails across all runtime/exit points | Veto authority everywhere |
| **L6** | Observer | Shadow evaluation — monitors telemetry for future-run system learning | Read-only, no runtime mutation |

### Primary Runtime Flow

```
User/API Request
      ↓
┌─────────────────────────────────────────────────────────┐
│ [1] REQUEST INTAKE                                      │
│     Ingress validation (optional pre-layer envelope)    │
└─────────────────────────────────────────────────────────┘
      ↓
┌─────────────────────────────────────────────────────────┐
│ [2] L1 REASONING (Librarian)                           │
│     Formulates execution plan                          │
│     ↓ dispatches to L0                                  │
└─────────────────────────────────────────────────────────┘
      ↓
┌─────────────────────────────────────────────────────────┐
│ [3] L0 ROUTING (Dispatcher)                            │
│     D1: Exact cache hit? → R1A short-circuit            │
│     D2: Semantic cache valid? → R1B short-circuit       │
│     D3: Need grounded context? → R3 Agentic RAG → C0    │
│     D4: Need external action? → R4 Action / R5 Fallback │
└─────────────────────────────────────────────────────────┘
      ↓
┌─────────────────────────────────────────────────────────┐
│ C0 CONTEXT ENGINE (Ref Desk)                             │
│     Retrieves and grounds only — never routes/executes │
│     Reads from L4 State / returns evidence to Prompt    │
│     Assembly → dispatches to [4]                        │
└─────────────────────────────────────────────────────────┘
      ↓
┌─────────────────────────────────────────────────────────┐
│ [4] RUNTIME DISPATCH                                   │
│     Simple execution → direct to L2                   │
│     Multi-step required → L3 Orchestrator → L2        │
└─────────────────────────────────────────────────────────┘
      ↓
┌─────────────────────────────────────────────────────────┐
│ [5] LIVE POST-L2 CONTROL                               │
│     Live Evaluation Spine: policy, schema, trajectory │
│     EXIT SPINE: allow / deny / reroute / escalate     │
│     COMMIT → UWG → L4 (only state mutation path)      │
└─────────────────────────────────────────────────────────┘
      ↓
┌─────────────────────────────────────────────────────────┐
│ [6] SHADOW EVALUATION + LEARNING                       │
│     Never current-run mutation                         │
│     Future-run influence via telemetry, regression      │
│     testing, and approved rollout paths                 │
└─────────────────────────────────────────────────────────┘
```

### Key Control Points

- **L5 Policy Plane** (cross-cutting): Authority over all stages [1]→[6], EXIT, and UWG
- **UWG (Universal Write Gateway)**: The sole path for any state mutation → L4
- **HITL Integration**: Embedded at exit spine, not bolted on
- **Zero Current-Run Learning**: All system learning is shadowed and promoted via approved paths only

---

## Enterprise Impact

| Capability              | Outcome                 |
| ----------------------- | ----------------------- |
| Deterministic Execution | Predictable AI behavior |
| Replay Engine           | Audit + CI/CD for AI    |
| Controlled Mutation     | No silent corruption    |
| Governance Layer        | Built-in compliance     |
| ADG Observability       | 10x faster debugging    |
| Semantic Cache          | Lower cost + latency    |
| Meta-Learning           | Continuous improvement  |

---

## Tech Stack

* Python (core orchestration)
* SQLite (deterministic state + ADG)
* Redis (L1 cache + retrieval gate)
* FAISS (vector retrieval)
* OpenAI + local LLMs (multi-model routing)
* Containerized infrastructure

---

## Quickstart

```bash
git clone https://github.com/Siamese001/Agentic-Workflow.git
cd Agentic-Workflow

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt

docker-compose up -d redis

python main.py --workflow sample_agentic_run

python replay.py --run_id <execution_id>
```

---

## Final Positioning

This is not just an AI framework.

This is a **deterministic AI control plane** that enables:

* reproducibility
* auditability
* safe autonomous execution

**AI that behaves like software, not experiments.**

---

## Governed Architecture Proof Pack

The governed runtime system — 5 fully adopted apps, 2 formal exceptions, shared substrate — is packaged into one verifiable proof surface.

**One-command release gate:**

```bash
python ops_scripts/ci/run_architecture_proof.py
```

This runs three suites in order:

| Suite | Command | What it validates |
|---|---|---|
| S1 — Conformance Gate | `ops_scripts/ci/check_governed_app_conformance.py` | Registry + imports: CONF01–CONF08 + EXCF01–EXCF08 (36 checks) |
| S2 — Exception Framework Proof | `tools/eval/retrieval_benchmark.py --exception-framework-proof` | All 7 apps behavioral: penta E2E + eval/uw exception controls |
| S3 — Regression Check | `tools/eval/retrieval_benchmark.py --regression-check` | Evidence governance regression baseline |

**Current green state:** 5 governed apps (research, exec, rfp, rg, lic) + 2 formal governed exceptions (eval, underwriting_ai) + 0 ad hoc statuses.

**Key documents:**
- **Architecture Proof Pack:** [`docs/architecture/architecture-proof-pack.md`](docs/architecture/architecture-proof-pack.md) — proof command map, gap maps, expected green state
- **Governed-App Contract:** [`docs/architecture/governed-app-contract.md`](docs/architecture/governed-app-contract.md) — `FormalExceptionEntry` schema, CONF/EXCF check definitions
- **App Registry:** [`apps_shared/integrations/app_registry.py`](apps_shared/integrations/app_registry.py) — single source of truth for all app classifications

---

## Documentation

* **Architecture Proof Pack:** `docs/architecture/architecture-proof-pack.md` — Proof command map, governed app registry, exception framework, expected green state
* **Governed-App Contract:** `docs/architecture/governed-app-contract.md` — `GovernedAppRunner` contract, `FormalExceptionEntry` schema, CONF/EXCF checks
* **Full Process Map (v28):** `docs/reference/agentic_process_mapping_v28.md` — Complete ASCII runtime flow with L0-L6 personas, decision points, and control spines
* **Architecture ADRs:** `docs/architecture/adr/` — Architectural decision records
* **Standards:** `docs/STANDARDS.md` — Code and design standards

---

*Last updated: April 2026*
