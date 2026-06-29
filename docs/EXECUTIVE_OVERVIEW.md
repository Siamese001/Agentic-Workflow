# Executive Overview

## Bottom line

The agent is not the product. The **governed runtime around the agent** is the product.

This repository is a working proof of a deterministic AI control plane: route contracts, verified context, bounded execution, runtime gates, controlled write paths, replayability, and shadow learning — the engineering substrate that lets enterprise AI move out of demos and into production.

## Why this matters

Most enterprise AI initiatives stall at the same point: a model demo works, but the surrounding system has no route authority, no context guarantees, no exit evaluation, no write controls, and no replay. The result is non-reproducible behavior, unauditable decisions, and uncontrolled state mutation — three failure modes incompatible with regulated environments and SVP-Engineering accountability.

A governed runtime addresses these as **system invariants**, not features layered on after the fact.

## What the system demonstrates

- **Route authority** — runtime paths are dispatched through contract-bound routers (cache, RAG, action, fallback). Routing is a typed decision, not a prompt.
- **Verified context (C0)** — retrieved context is grounded against canonical state before it ever reaches the model. Retrieval cannot route or execute.
- **Prompt assembly as an engineering control** — prompts are assembled from verified components, not concatenated strings.
- **Bounded execution (L2)** — tool use is schema-driven, sandboxed, and contract-enforced. No hallucinated tool calls, no uncontrolled side effects.
- **Runtime exit gates** — live packets, steps, and write proposals are evaluated for a current-run disposition (allow / deny / reroute / escalate) before commit.
- **Universal Write Gateway (UWG)** — the intended durable write admission path, backed by bypass-risk checks in ADG and CI.
- **Replayability** — replayable paths produce determinism digests and replay keys so incidents can be reconstructed from recorded evidence and validated in CI/CD.
- **Shadow learning (L6)** — the system learns only from completed runs and proposes future-run improvements through approved promotion paths. No live drift.

## Runtime control model

```
L1 reasons → L0 routes → C0 grounds → L2 executes → Exit clears → UWG commits → L4 stores
                                                                       ↓
                                                          L6 observes (shadow)
```

- **L5** is the cross-cutting policy plane. It certifies authority, registry, origin trust, capability, sandbox, egress, HITL, replay, and audit evidence.
- **Runtime gates** decide whether *this* live packet, step, tool call, output, or write proposal may proceed *now*.
- **Exit Evaluation** emits a current-run disposition.
- **UWG** is the only durable write admission path.
- **L4** stores durable state.
- **L6** learns only from completed runs.

The cheat rule: **L2 proposes → Exit clears → UWG commits → L4 stores.**

## Platform leadership signal

This repository is intended to be read as evidence of platform-level thinking:

- AI as a **system engineering discipline**, not a model-tuning exercise.
- Governance as a **first-class runtime layer**, not a policy document.
- Determinism, replay, and write control treated as **enforced invariants**, not aspirations.
- Separation of duties between routing, context, execution, evaluation, write admission, durable state, and observation.
- A clear distinction between **current-run control** and **future-run learning** — the failure mode that breaks most "self-improving" agentic systems.

## What this is not

- Not a model. Not a fine-tune.
- Not a chat wrapper or a prompt library.
- Not a confidential client implementation. Client-specific deployments are kept private.
- Not a finished product. It is a **public proof asset** — a reference design for governed enterprise agentic systems.

## Suggested reading path

1. **README.md** — system guarantees, layered design, key differentiators
2. **docs/RUNTIME_CONTROL_PLANE.md** — the technical narrative for the control plane
3. **docs/architecture/REVIEWER_GUIDE.md** — executive walkthrough + engineer quickstart
4. **docs/architecture/architecture-proof-pack.md** — proof command map
5. **docs/THOUGHT_LEADERSHIP_INDEX.md** — themes this repo argues for publicly

For non-technical readers, start at **docs/RECRUITER_GUIDE.md**.
