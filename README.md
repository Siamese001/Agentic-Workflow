# Agentic Workflow — Deterministic AI Control Plane

> **A governed runtime around the agent — not another agent framework.**
> Route contracts, verified context, bounded execution, runtime gates, controlled writes, replay, and shadow learning. Built as the reference design for enterprise-grade agentic systems.

**Author:** [Amit Ayer](https://github.com/Siamese001) — SVP-level Agentic Engineer. Platform architecture for governed enterprise AI.

---

## Point of View

Most of the public discourse around "agents" in 2025–2026 has been about **frameworks, prompts, and demos**. That framing is the reason enterprise AI projects stall the moment they meet a regulated runtime boundary.

The thesis this repository argues — and demonstrates in code — is the opposite:

> **The agent is not the product. The governed runtime around the agent is the product.**

An agent that works in a notebook does not clear a real control boundary. Production AI in regulated environments fails on five predictable edges, every time:

1. **No route authority** — the model decides what to do next, instead of a typed, contract-bound dispatcher.
2. **No context guarantees** — retrieval quietly routes and executes, instead of grounding against canonical state.
3. **No exit evaluation** — outputs commit without a current-run disposition (allow / deny / reroute / escalate).
4. **No write controls** — state mutates through any code path that can reach a database.
5. **No replay** — incidents cannot be reconstructed, so nothing can be audited, regressed, or learned from safely.

This repository is a working proof that every one of those five failure modes is solvable as a **system engineering problem**, not a prompt-engineering problem. It is the engineering substrate behind the positioning: **AI that behaves like software, not experiments.**

---

## What this repo demonstrates (and why it matters at the SVP-Engineering level)

- **Determinism as a system invariant.** The LLM is probabilistic; the system around it is deterministic. Same input, same output, same digest.
- **Governance on the runtime path.** L5 is a cross-cutting policy plane with veto authority at every stage — not a PDF and not a post-hoc review.
- **A single door for state mutation.** Every durable write passes through the Universal Write Gateway (UWG). No side doors, no silent mutations, no bypasses.
- **Full replay.** Every run emits a determinism digest and a replay key. Any past run can be reconstructed exactly — the thing most "agentic" systems cannot do on day one of an incident review.
- **Shadow learning, never live drift.** The system learns from completed runs and promotes changes through approved paths. It does not mutate behavior mid-flight.
- **AST Dependency Graph (ADG) as the source of truth for the codebase itself.** ~264K nodes, ~929K edges, SQLite-backed, queryable. Refactoring, blast radius, and hotspot analysis are structural — not guesswork.

These are the controls an enterprise AI platform owner is accountable for. This repo is a reference implementation of that accountability.

---

## Public positioning index

- [`docs/THOUGHT_LEADERSHIP_INDEX.md`](docs/THOUGHT_LEADERSHIP_INDEX.md) — themes this repository argues for publicly
- [`docs/EXECUTIVE_OVERVIEW.md`](docs/EXECUTIVE_OVERVIEW.md) — bottom-line positioning for CTO / SVP Engineering readers
- [`docs/RECRUITER_GUIDE.md`](docs/RECRUITER_GUIDE.md) — plain-English explanation for hiring and leadership audiences

> **Note.** This repository is a **public proof asset and reference design**, not a confidential client implementation. Client-specific work is kept private; what is published here is the architecture and the reasoning behind it.

---

## Start here

| Audience | Start with | Why |
|----------|------------|-----|
| Recruiter or hiring manager | [`docs/RECRUITER_GUIDE.md`](docs/RECRUITER_GUIDE.md) | Plain-English explanation of what this repo demonstrates and the roles it supports. |
| CTO / SVP Engineering | [`docs/EXECUTIVE_OVERVIEW.md`](docs/EXECUTIVE_OVERVIEW.md) | Bottom-line positioning, runtime control model, and platform-leadership signal. |
| AI platform engineer | [`docs/RUNTIME_CONTROL_PLANE.md`](docs/RUNTIME_CONTROL_PLANE.md) | Technical narrative of the control plane: layers, separation of duties, write model, replay. |
| Governance / risk / compliance leader | [`docs/RUNTIME_CONTROL_PLANE.md`](docs/RUNTIME_CONTROL_PLANE.md) + [`docs/EXECUTIVE_OVERVIEW.md`](docs/EXECUTIVE_OVERVIEW.md) | Read-broad/write-strict model, UWG single-door commit, replay and audit evidence. |
| Deep technical reviewer | [`docs/architecture/REVIEWER_GUIDE.md`](docs/architecture/REVIEWER_GUIDE.md) and the rest of this README | Executive walkthrough plus the full architecture, proof pack, and ADRs. |

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

This is not another agent framework. It is a **deterministic AI control plane** — the engineering substrate for reproducibility, auditability, and safe autonomous execution in regulated environments.

- **For platform leaders:** the reference architecture for what "governed agentic AI" actually looks like when it has to clear an enterprise control boundary.
- **For engineers:** a working implementation of route authority, verified context, bounded execution, exit evaluation, write control, replay, and shadow learning.
- **For the field:** a counter-argument to the prevailing "bigger model + more tools = agent" framing.

**AI that behaves like software, not experiments.**

— [Amit Ayer](https://github.com/Siamese001), SVP-level Agentic Engineer

---

## Governed Architecture Proof Pack

Five apps governed. Two formal exceptions. One release gate.

```bash
python ops_scripts/ci/run_architecture_proof.py   # S1 + S2 + S3  (~17s, exit 0 = green)
```

| Suite | Validates |
|---|---|
| S1 — Conformance Gate | Registry + imports: CONF01-08 + EXCF01-08 (36 checks) |
| S2 — Exception Framework | All 7 apps behavioral: penta E2E + eval/uw exception controls |
| S3 — Regression Check | Evidence governance regression baseline (RC01-12) |

**Reviewer journey:**

1. `docs/architecture/REVIEWER_GUIDE.md` — executive walkthrough + engineer quickstart
2. `docs/architecture/architecture-proof-pack.md` — proof command map + gap maps
3. `python ops_scripts/ci/run_architecture_proof.py` — run the proofs yourself
4. `docs/architecture/ROLLOUT_CLOSEOUT.md` — final status + known-gap register

---

## Documentation

* **Reviewer Guide:** `docs/architecture/REVIEWER_GUIDE.md` — Start here for architecture review
* **Architecture Proof Pack:** `docs/architecture/architecture-proof-pack.md` — Proof command map, runtime loop, app registry
* **Rollout Closeout:** `docs/architecture/ROLLOUT_CLOSEOUT.md` — Final status, command matrix, known gaps
* **Release Readiness:** `docs/architecture/RELEASE_READINESS.md` — Cleanup log, tracked gap register
* **Governed-App Contract:** `docs/architecture/governed-app-contract.md` — `GovernedAppRunner` + `FormalExceptionEntry` schema
* **Full Process Map (v28):** `docs/reference/agentic_process_mapping_v28.md` — Complete ASCII runtime flow with L0-L6 personas
* **Architecture ADRs:** `docs/architecture/adr/` — Architectural decision records
* **Standards:** `docs/STANDARDS.md` — Code and design standards

---

*Last updated: April 2026 — maintained by [Amit Ayer](https://github.com/Siamese001).*
