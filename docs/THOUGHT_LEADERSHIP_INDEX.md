# Thought Leadership Index

A public index connecting this repository to the broader argument it makes about how enterprise agentic AI should be built.

## Core thesis

> **Enterprise agentic AI needs a runtime control plane.**

The model is bounded; the system is deterministic. AI moves into production when it stops being a probabilistic experiment and starts behaving like governed software — with route contracts, verified context, bounded execution, runtime gates, controlled writes, replay, and shadow learning.

This repository is the working reference. The themes below are the public argument around it.

## Published or planned artifacts

- **GitHub: `Agentic-Workflow`** — this repository, the public proof asset. Reference design, runnable proofs, layered architecture (L0–L6).
- **Executive Overview** — `docs/EXECUTIVE_OVERVIEW.md`
- **Recruiter & Hiring Manager Guide** — `docs/RECRUITER_GUIDE.md`
- **Runtime Control Plane** — `docs/RUNTIME_CONTROL_PLANE.md`
- **Reviewer Guide** — `docs/architecture/REVIEWER_GUIDE.md`
- **Architecture Proof Pack** — `docs/architecture/architecture-proof-pack.md`
- **LinkedIn long-form essays** — planned series, see below.

## Suggested article series

A reading order for a long-form series on this thesis:

1. **The agent is not the product. The runtime is.** — why enterprise AI fails at the system boundary, not the model.
2. **Deterministic agentic AI: making AI behave like software.** — replay, digests, no hidden entropy.
3. **Lowest viable agency.** — give the agent the smallest amount of autonomy that still solves the problem; prove it; expand only with evidence.
4. **Runtime governance vs static AI policy.** — why policy documents do not survive contact with a live agent, and what runtime gates do instead.
5. **C0 context engineering.** — retrieval as a typed, verified, contract-bound operation, not a string concatenation.
6. **Prompt assembly as an engineering control.** — the prompt is a build artifact, not a creative writing exercise.
7. **Exit Evaluation and the LLM-as-judge problem.** — where evaluation belongs in the runtime, and how to keep judges from drifting into authority.
8. **Universal Write Gate.** — the single-door pattern for state mutation in agentic systems.
9. **Replayable AI execution.** — incident review and CI/CD for AI, applied like ordinary software engineering.
10. **Shadow learning for future-run improvement.** — separating live runtime control from learning, so the system improves without drifting in flight.

## LinkedIn Featured assets

Recommended pinned items on the LinkedIn profile:

- Link to the GitHub repository.
- Link to `docs/EXECUTIVE_OVERVIEW.md`.
- Link to `docs/RUNTIME_CONTROL_PLANE.md`.
- The lead essay from the series above, once published.

Avoid pinning narrow technical artifacts on LinkedIn; pin the *positioning*, then let the repository carry the depth.

## GitHub reading path

For a reviewer arriving from LinkedIn or a search:

1. `README.md` — system guarantees, layered design, key differentiators.
2. `docs/EXECUTIVE_OVERVIEW.md` — what the system demonstrates, in plain terms.
3. `docs/RUNTIME_CONTROL_PLANE.md` — the architecture narrative.
4. `docs/architecture/REVIEWER_GUIDE.md` — executive walkthrough + engineer quickstart.
5. `docs/architecture/architecture-proof-pack.md` — proof command map.
6. `docs/architecture/ROLLOUT_CLOSEOUT.md` — final status and known-gap register.

## Topics Amit is publicly exploring

- Enterprise agentic AI needs a runtime control plane
- Deterministic agentic AI systems
- Lowest viable agency
- Runtime governance vs static AI policy
- C0 context engineering
- Prompt assembly as an engineering control
- Exit Evaluation and LLM-as-judge placement
- Universal Write Gate
- Replayable AI execution
- Shadow learning for future-run improvement

These are the public threads. The repository is the evidence.
