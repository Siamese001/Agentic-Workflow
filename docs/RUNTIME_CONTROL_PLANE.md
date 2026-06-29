# Runtime Control Plane

A technical narrative of the architecture, written for engineering reviewers who want the model without wading through full internal process maps.

## Core thesis

Enterprise agentic AI fails at the runtime boundary, not at the model. Production-grade behavior requires a **deterministic control plane** that owns:

1. Who is allowed to route this request.
2. What context is allowed to enter the prompt.
3. How the prompt is assembled.
4. What the model is allowed to do with that prompt.
5. Whether the resulting action is allowed to proceed *now*.
6. Where, and only where, durable state may change.
7. How the system reconstructs and learns from what happened.

The repository implements those seven concerns as distinct, contract-bound layers with explicit authority boundaries. The agent is bounded; the system is deterministic.

## Control-point map

```
[1] Request intake      → ingress validation
[2] L1 Reasoning        → bounded plan formulation
[3] L0 Routing          → cache / RAG / action / fallback
        │
        └─ C0 Context   → verified retrieval, no routing, no execution
[4] Runtime dispatch    → direct L2, or L3 → L2 for multi-step
[5] Live post-L2        → Exit Evaluation → UWG → L4 commit
[6] Shadow evaluation   → telemetry, regression, future-run promotion
```

L5 is the cross-cutting policy plane and operates across runtime steps.

## Layer responsibilities

| Layer | Persona | Owns | Does not own |
|-------|---------|------|--------------|
| **L1** | Librarian | Plan formulation under bounded reasoning | Routing decisions, execution |
| **L0** | Dispatcher | Route authority — typed dispatch decision | Reasoning, retrieval, execution |
| **C0** | Reference Desk | Grounded retrieval and prompt assembly inputs | Routing, execution |
| **L2** | Execution Staff | Sandboxed tool and action execution | Routing, durable writes |
| **L3** | Orchestrator | Multi-step coordination across L2 calls (when complexity requires) | Single-step execution authority |
| **L4** | Archivist | Durable state — read-broad, write-strict | Any write that did not pass UWG |
| **L5** | Safety Officer | Policy plane: authority, registry, origin trust, capability, sandbox, egress, HITL, replay, audit evidence | Reasoning, retrieval, execution |
| **L6** | Observer | Shadow evaluation, telemetry, future-run learning | Any current-run mutation |

## Critical separation of duties

The architecture enforces strict separation between **certifying authority** and **runtime gating**, and between **current-run control** and **future-run learning**:

- **L5 certifies** — authority, policy, registry, origin trust, capability, sandbox, egress, HITL, replay, and audit evidence.
- **Runtime gates decide** — whether live packets, steps, tool calls, outputs, or write proposals may proceed *now*.
- **Exit Evaluation emits a current-run disposition** — allow, deny, reroute, or escalate.
- **UWG is the only durable write admission path.**
- **L4 stores durable state.**
- **L6 learns only from completed runs** and proposes future-run improvements through approved promotion paths. L6 cannot mutate a live run.

The cheat rule for the runtime path:

> **L2 proposes → Exit clears → UWG commits → L4 stores.**

C0 is the cheat rule for context:

> **C0 grounds; C0 does not route; C0 does not execute.**

## Evidence and context quality

C0 is the context engine, not a generic RAG layer. Its job is:

- Retrieve from canonical state (L4) under a typed query.
- Ground the retrieved evidence against the current request.
- Assemble structured inputs to prompt assembly under a contract.
- Hand off to runtime dispatch with a verifiable evidence packet.

What C0 deliberately does *not* do:

- It does not pick a route.
- It does not call tools.
- It does not mutate state.

This separation is what allows context quality to be reasoned about independently of routing or execution.

## Write-control model

Durable state changes are designed to be admitted through one path:

```
L2 output → Exit Evaluation → UWG → L4
```

Properties:

- **Single-door** — UWG is the intended durable-write admission path, with ADG/CI checks used to detect bypass risk.
- **Validated** — UWG checks schema, policy version, and authority before commit.
- **Signed and recorded** — commits bind to the policy hash, run digest, and evidence trace that produced them.
- **Auditable** — provenance is reconstructable from the commit alone.

This is what makes "no silent corruption" a system property rather than an aspiration.

## Evaluation and replay

Replayable runs produce:

- A **full execution trace** — ordered, deterministic, replayable.
- A **determinism digest** — a content hash that pins the entire run.
- A **replay key** — used to re-execute the run and verify hash match.

Operationally, this means:

- Incidents can be reconstructed from recorded evidence and replay keys.
- Regression tests can compare digests across builds.
- AI behavior gets the same CI/CD treatment as ordinary software.

Exit Evaluation is the placement point where current-run policy, schema, and trajectory checks meet. It emits the current disposition. It is *not* the same surface as L6 shadow evaluation, which does not mutate the live run.

## Future-run learning

L6 is the observer. It learns from completed runs by:

- Aggregating telemetry and execution traces.
- Detecting patterns and regressions in shadow.
- Proposing promotions (prompt, policy, rubric, config) through approved gates.
- Never writing to current-run state.

Promotions go through standard runtime gates the next time a request comes in. There is no live mutation, no in-flight drift, and no "the system updated itself mid-call" failure mode.

## Proof obligations

A deterministic control plane has to be falsifiable. The repository carries a runnable proof pack:

```bash
python ops_scripts/ci/run_architecture_proof.py
```

It validates:

- **S1 — Conformance Gate:** registry and import contracts (CONF + EXCF, 36 checks).
- **S2 — Exception Framework:** behavioral E2E across the seven apps with exception controls.
- **S3 — Regression Check:** evidence-governance regression baseline (RC01–RC12).

Reviewer entry points:

- `docs/architecture/REVIEWER_GUIDE.md` — executive walkthrough + engineer quickstart.
- `docs/architecture/architecture-proof-pack.md` — proof command map.
- `docs/architecture/ROLLOUT_CLOSEOUT.md` — final status and known-gap register.

The intent is simple: the architecture either reproduces, or it does not. Determinism is a property the system can be asked to prove on demand.
