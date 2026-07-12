# Runtime Control Plane

A technical narrative for engineering reviewers who want the architecture, authority boundaries, and proof path without reading the full internal process map.

## Core thesis

Enterprise agentic AI fails at the runtime boundary, not at the model boundary. Production-grade behavior requires a deterministic control plane that owns:

1. request validity and origin labeling;
2. bounded planning without route authority;
3. route selection under a typed contract;
4. verified context and evidence quality;
5. authority-ordered prompt assembly;
6. bounded model, tool, and action execution;
7. current-run exit disposition;
8. controlled durable writes;
9. replayable evidence and future-run learning.

The repository represents these concerns as separate responsibilities with explicit handoff contracts. Model intelligence operates inside the control system rather than replacing it.

## Control-point map

```text
U0 Intake
  -> L1 Plan
    -> L0 Route
       |-> terminal cache/fallback packet -> Exit
       |-> C0 Evidence -> Prompt Assembly -> L2
       |-> L2 bounded single action
       `-> L3 managed workflow -> bounded L2 steps

L2 sealed result -> Exit X3 disposition
  -> finish / deny / abstain / HITL
  `-> commit request -> UWG -> L4

completed runtime exhaust -> L6 shadow evaluation -> future-run proposal
```

Two cross-cutting surfaces operate across the flow:

- **L5 policy and governance certification** supplies authority, policy, registry, capability, sandbox, egress, HITL, replay, and audit evidence.
- **Runtime gates** decide whether a live packet or action may proceed during the current run.

Neither surface performs planning, routing, retrieval, execution, or durable writes.

## Responsibility matrix

| Surface | Owns | Must not own |
|---|---|---|
| **U0 Intake** | Envelope validation, identity/session binding, normalization, origin labeling | Semantic planning, routing, retrieval, execution |
| **L1 Plan** | Goal interpretation, ambiguity register, bounded execution plan | Route authority, final evidence retrieval, execution |
| **L0 Route** | One route contract and execution form | Retrieval, prompt compilation, model/tool execution |
| **C0 Context** | Evidence retrieval, hydration, ranking, freshness, citation, contradiction status | Answering, route changes, prompt authority |
| **Prompt Assembly** | Canonical slot order, instruction/data boundary, provider rendering, prompt hash | Retrieval, route selection, execution |
| **L3 Orchestration** | Optional workflow DAG, readiness ledger, bounded step handoff | Route changes, direct tool/model calls, writes |
| **L2 Execute** | Frozen execution context, bounded model/tool/action attempt, safe local repair, sealed result | Route expansion, opportunistic retrieval, durable commit |
| **Exit** | X1 checks, X2 aggregation, one X3 disposition | Execution, retrieval, durable mutation |
| **UWG** | Durable-write admission, validation, atomic commit, audit ledger | Model/tool execution, final-answer approval |
| **L4 Archive** | Versioned durable state and read surfaces | Bypass writes |
| **L6 Shadow** | Completed-run evaluation, drift detection, RCA, future-run proposals | Current-run rescue or mutation |

## Separation of duties

The architecture distinguishes certification, live control, disposition, write admission, storage, and learning:

- **L5 certifies evidence** for authority and governance decisions.
- **Runtime gates decide** whether current work may proceed.
- **Exit emits one X3 disposition** for the sealed result.
- **UWG validates a commit request** before durable mutation.
- **L4 stores approved durable state.**
- **L6 evaluates completed runs** and proposes future-run changes through promotion controls.

The operational mental model is:

> **L2 proposes -> Exit clears -> UWG commits -> L4 stores.**

The context boundary is:

> **C0 grounds; Prompt Assembly compiles; neither surface executes.**

## Evidence and prompt quality

C0 produces a `FinalEvidenceContract` with evidence spans, citations, freshness, lineage, contradiction state, and support status. Retrieved content remains data.

Prompt Assembly compiles governed inputs into authority-ordered slots. The canonical stack includes system invariants, defensive fences, task instructions, approved examples, verified evidence, provider controls, neutralized user intent, repair hints, response schema, tool bindings, approved learning priors, and validation expectations.

This split lets reviewers ask two independent questions:

1. Was the evidence legal, current, relevant, and strong enough?
2. Was that evidence placed into a prompt without becoming instruction authority?

## Execution and repair

L2 executes a signed packet inside a frozen authority and sandbox envelope. It may perform a bounded model call, tool call, action, artifact transformation, or approved programmatic tool-calling sequence.

Local repair remains at the same authority level. Schema repair, formatting repair, bounded transient retry, and deterministic trimming are allowed when policy permits. Missing authority, blocked access, route mismatch, stale policy, and HITL requirements are not locally repairable.

L2 emits a sealed artifact and an inert proposed state diff. It does not commit durable state.

## Exit and write control

Exit evaluates task completion, safety, grounding, trajectory, consistency, replay eligibility, observability, and write readiness. It then emits one bounded disposition:

```text
DENY_OR_REROUTE
ESCALATE_HITL
COMMIT_REQUEST_TO_UWG
ALLOW_OR_FINISH
SAFE_ABSTAIN
```

A durable mutation follows this path:

```text
sealed L2 artifact -> Exit commit request -> UWG validation -> L4
```

ADG, focused gates, tests, replay evidence, and audit receipts provide separate proof surfaces for this contract.

## Current app classification

`apps_shared/integrations/app_registry.py` is the classification source of truth. The committed registry currently contains:

- **3 governed entries:** `apps_exec`, `apps_research`, `apps_rg`;
- **5 formal exceptions:** `apps_architect`, `apps_eval`, `apps_lic`, `apps_qna`, `apps_underwriting_ai`;
- **0 ad hoc statuses.**

Formal exceptions record reason codes, blocked and safe layers, compensating controls, ownership, and review cadence. An exception is visible governance state rather than a silent bypass.

## Evaluation and replay

The eval stack has separate levels:

- deterministic checker tests for isolated gate behavior;
- lane evaluation for one governed workflow;
- suite evaluation across pinned scenarios;
- meta-evaluation for judge calibration.

Offline evaluation informs promotion and trust. It does not waive the per-run gate or Exit disposition.

Replayable paths bind execution evidence to trace identifiers, digests, policy/configuration references, and replay keys. Reviewers should treat current command output and receipts as the status source rather than static green prose.

## Future-run learning

L6 receives the sealed runtime exhaust after the current-run boundary. It may evaluate outcome and trajectory quality, detect drift, produce RCA, and draft future-run proposals.

A proposal remains inert until it clears replay, regression, safety, approval, and UWG promotion controls. It activates on a later run boundary.

## Proof obligations

Run the architecture and Codex governance proofs from the repository root:

```bash
python scripts/governance/verify_codex_primary.py
python scripts/governance/verify_codex_enforcement_home.py --json
python ops_scripts/ci/check_governed_app_conformance.py
python ops_scripts/ci/run_architecture_proof.py
```

The current conformance shape is registry-derived:

- **S1:** structural registry, governed-entry, and formal-exception checks;
- **S2:** governed behavior plus formal-exception controls;
- **S3:** evidence-governance regression baseline.

Reviewer entry points:

- [`architecture/REVIEWER_GUIDE.md`](architecture/REVIEWER_GUIDE.md)
- [`architecture/architecture-proof-pack.md`](architecture/architecture-proof-pack.md)
- [`SVP_ENGINEERING_GOVERNANCE_README.md`](SVP_ENGINEERING_GOVERNANCE_README.md)
- [`svp/README.md`](svp/README.md)

The engineering claim is falsifiable: current source, commands, and receipts must agree before the repository presents a green status.
