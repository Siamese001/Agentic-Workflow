# Recruiter and Hiring Manager Guide

A non-technical guide to what this repository demonstrates and which roles it supports.

## What this repo shows

This repository is a public proof asset for **enterprise agentic AI platform leadership**. It demonstrates how to build the governed runtime *around* an AI agent — the engineering substrate that makes AI usable in regulated, audited, production environments.

In one sentence:

> A deterministic AI control plane for governed enterprise agents: route contracts, verified context, bounded execution, runtime gates, controlled writes, replay, and shadow learning.

The repository is intentionally a reference design, not a client implementation. Confidential work is kept private.

## Roles this supports

This work is most relevant for senior platform and AI leadership roles, including:

- **SVP Engineering**
- **VP Engineering**
- **Head of AI Engineering**
- **AI Platform Engineering leader**
- **Chief AI Officer**
- **Agentic AI platform leader**
- **Enterprise AI runtime governance leader**

It also speaks to Director-level platform, MLOps, and AI infrastructure roles where the candidate is expected to argue for and build production-grade AI systems.

## Why this matters for SVP Engineering and AI Platform roles

At senior platform levels, the question is no longer *"can you ship a model?"* It is:

- Can you make AI behave like reliable software?
- Can you make decisions auditable and reproducible?
- Can you bound autonomous execution without killing capability?
- Can you separate live runtime control from learning, so the system improves without drifting?
- Can you stand in front of risk, compliance, and the board with this architecture?

The repository is structured to answer those questions directly, with executable proofs (the architecture proof pack) backing the narrative.

## What to look at first

Pick one path:

| If you have | Read |
|-------------|------|
| 60 seconds | The top of `README.md` and `docs/EXECUTIVE_OVERVIEW.md` |
| 5 minutes | `docs/EXECUTIVE_OVERVIEW.md` + `docs/RUNTIME_CONTROL_PLANE.md` |
| 15 minutes | The above plus `docs/architecture/REVIEWER_GUIDE.md` |
| Deep review | `docs/architecture/architecture-proof-pack.md` and run the proof pack locally |

## Plain-English glossary

- **Runtime control plane** — the system that sits around an AI agent and decides what is allowed to happen, in what order, with what evidence. The "operating system" for governed AI.
- **Route contract** — a typed agreement about how a request is dispatched (e.g. cache, retrieval, action). Routing is a decision the system makes, not a prompt the model writes.
- **Context engineering** — the discipline of getting the *right* information in front of the model, verified against canonical state, in a structured form. Different from generic RAG.
- **Prompt assembly** — building prompts from verified components under an engineering contract, instead of concatenating strings.
- **Bounded execution** — the agent can only call tools that are schema-validated, sandboxed, and policy-allowed. No surprise side effects.
- **Exit Evaluation** — the moment a live run is checked against policy, schema, and trajectory before any output or write is allowed to proceed.
- **Universal Write Gate (UWG)** — the single, mandatory door that any state change must pass through. There is no other write path.
- **Replayability** — the ability to take any past execution and re-run it deterministically to reconstruct the exact behavior, used for incident review and CI/CD.
- **Shadow learning** — the system learns from completed runs in the background and proposes improvements for *future* runs. It never mutates an in-flight run.
- **Governed autonomy** — the agent is allowed to act, but only inside boundaries the platform enforces. Autonomy with accountability.

## Signals to take away

- **Platform thinking, not model tinkering.** The repository is about runtime architecture, not prompt tuning.
- **Determinism and replay as defaults.** AI behavior is treated like ordinary software behavior — testable, reproducible, auditable.
- **Governance on the runtime path, not bolted on.** Policy enforcement is structurally embedded.
- **Clear separation of current-run control vs future-run learning.** This is the failure mode that breaks most "self-improving" agent stacks.
- **Public proof asset.** Confidential client work is not in this repo. What is here is the reference design and the reasoning behind it.
