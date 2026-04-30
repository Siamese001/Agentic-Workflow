# App Overlay vs. Core-Only Runtime

> **Status**: Architecture invariant. Co-canonical with
> `_notes/agentic_system_process_map_exec.md`. Updated 2026-04-30.

This document defines the three runtime-mode classifications every
request and every `apps_*` package MUST fit into. The classifications
are mutually exclusive and collectively exhaustive (MECE). The scanner
at `tools/analysis/apps_spine_coverage.py` enforces them at audit time.

---

## TL;DR

```
apps_* is optional.
agentic_core is not.
apps_* depends on agentic_core.
agentic_core must not depend on apps_*.
```

A request that does NOT need domain-specific schemas, rubrics, prompts,
tools, or memory surfaces should run **CORE_ONLY** through
`agentic_core`. A request that DOES need domain specifics runs as an
**APP_OVERLAY** that enriches packets and **delegates authority back to
the spine-owned contracts**. An `apps_*` package that runs a
**standalone mini-runtime** without delegating to spine contracts is
**FORBIDDEN**.

---

## A. CORE_ONLY  ✅ valid

```
[ user request ] -> [ agentic_core spine ] -> [ output ]
```

Use when:
- Generic grounded Q&A over the canonical KB
- Generic action execution governed by the canonical L0 routes
- Repo audits, replay/golden-path proof, runtime gates
- Cache lookup, prompt assembly, registry lookup
- Any other capability already provided by the spine

Authority chain (always one direction):

```
INTAKE U0  →  L1 (L1PlanContract)
            →  L0 (RouteContract)
            →  C0 (FinalEvidenceContract)         [if grounded]
            →  PA (CompiledPromptArtifact)        [if model exec]
            →  L2 (SealedArtifact)                [bounded execution]
            →  Exit (ExitReviewPacket)            [final disposition]
            →  L4 / UWG (CommitRequest)           [if durable write]
            →  L6 (RuntimeExhaustBundle)          [post-run only]
```

No `apps_*` participation is needed for a CORE_ONLY route.

---

## B. APP_OVERLAY  ✅ valid

```
[ user request ] -> [ apps_* overlay ] -> [ agentic_core spine ] -> [ output ]
```

Use when:
- Domain-specific **schemas** (typed inputs the spine doesn't model)
- Domain-specific **rubrics** (eval criteria the spine doesn't carry)
- Domain-specific **prompt templates / cards** (output formatting,
  paste budgets, interview-prep cards)
- Domain-specific **tools** (e.g., a domain CLI subcommand)
- Domain-specific **workflow templates** (e.g., a multi-step LiC pipeline)
- Domain-specific **evidence standards** (per-domain SRC- citation rules)
- Domain-specific **memory / learning surfaces** (per-domain ledgers)

The overlay's job:
1. Receive the user request
2. Construct a **richer** `ValidatedRequest` / `L1PlanContract`
   payload than the generic spine path would
3. **Hand off to the spine** for planning / routing / retrieval /
   prompt assembly / execution / disposition / write
4. Receive the spine's typed output (`SealedArtifact`,
   `ExitReviewPacket`, ...) and apply domain-specific rendering or
   memory writeback **only after** the current-run boundary closes

The overlay MUST NOT:
- Construct its own plan without a `L1PlanContract` handoff
- Make its own routing decision without a `RouteContract` handoff
- Run its own retrieval without a `FinalEvidenceContract` handoff
- Compose its own prompt without a `CompiledPromptArtifact` handoff
- Bypass `ExitReviewPacket` for final disposition
- Write to L4 directly (must go through `CommitRequest` / UWG)
- Mutate L6 state during the current run (post-run boundary only)

If the overlay needs additional domain schemas, it adds them as
**typed addenda to** the spine contracts, not as replacements.

---

## C. FORBIDDEN_APP_STANDALONE  ❌ forbidden

```
[ user request ] -> [ apps_* local mini-runtime ] -> [ output ]
                       (no spine contract handoff)
```

Forbidden when `apps_*`:
- Performs **planning** without producing a `L1PlanContract`
- Owns **route authority** without emitting a `RouteContract`
- Owns **retrieval authority** without consuming a
  `FinalEvidenceContract`
- Owns **prompt assembly** without producing a
  `CompiledPromptArtifact` or `PromptEnvelope`
- Owns the **bounded-execution lifecycle** without a
  `SealedArtifact`
- Owns **final disposition** without an `ExitReviewPacket`
- Performs **durable writes** without a `CommitRequest` / UWG admission
- Performs **current-run learning** without crossing the L6 boundary
  via a `RuntimeExhaustBundle`

A standalone `apps_*` that does any of the above is a **shadow
runtime**. It violates the "agentic_core is the mandatory runtime
spine" invariant. The constitutional consequences:
- Bypasses §29 closed-loop router enforcement
- Bypasses §3 anti-bypass write discipline
- Bypasses §22 graph-layer evidence
- Bypasses §28 SQLite-direct fallback hierarchy

---

## ASCII diagram (canonical)

```
┌───────────────────────────────────────┐  ┌───────────────────────────────────────┐
│  ✅ VALID PATTERNS                    │  │  ❌ FORBIDDEN PATTERN                 │
├───────────────────────────────────────┤  ├───────────────────────────────────────┤
│                                       │  │                                       │
│  A. CORE_ONLY                         │  │  C. FORBIDDEN_APP_STANDALONE          │
│                                       │  │                                       │
│   ┌─────────────┐                     │  │   ┌─────────────┐                     │
│   │  user req   │                     │  │   │  user req   │                     │
│   └──────┬──────┘                     │  │   └──────┬──────┘                     │
│          ▼                            │  │          ▼                            │
│   ┌─────────────┐                     │  │   ┌─────────────┐                     │
│   │agentic_core │ (L1+L0+C0+PA+L2+    │  │   │   apps_*    │ owns plan, route,   │
│   │   SPINE     │  Exit+UWG+L6)       │  │   │ standalone  │ retrieval, prompt,  │
│   └──────┬──────┘                     │  │   │ mini-runtime│ exec, disposition,  │
│          ▼                            │  │   │             │ write, learning     │
│   ┌─────────────┐                     │  │   └──────┬──────┘                     │
│   │   output    │                     │  │          ▼                            │
│   └─────────────┘                     │  │   ┌─────────────┐                     │
│                                       │  │   │   output    │                     │
│  B. APP_OVERLAY                       │  │   └─────────────┘                     │
│                                       │  │                                       │
│   ┌─────────────┐                     │  │  Bypasses spine authority. Bypasses   │
│   │  user req   │                     │  │  §29 router enforcement, §3 anti-     │
│   └──────┬──────┘                     │  │  bypass writes, §22 graph evidence,   │
│          ▼                            │  │  §28 SQLite fallback. Treated as a    │
│   ┌─────────────┐                     │  │  shadow runtime; refused by the       │
│   │  apps_*     │  enriches packet,   │  │  spine-coverage scanner.              │
│   │  overlay    │  hands off to spine │  │                                       │
│   └──────┬──────┘                     │  │                                       │
│          ▼                            │  │                                       │
│   ┌─────────────┐                     │  │                                       │
│   │agentic_core │ owns L1/L0/C0/PA/L2/│  │                                       │
│   │   SPINE     │ Exit/UWG/L6 contracts│  │                                       │
│   └──────┬──────┘                     │  │                                       │
│          ▼                            │  │                                       │
│   ┌─────────────┐                     │  │                                       │
│   │   output    │                     │  │                                       │
│   └─────────────┘                     │  │                                       │
│                                       │  │                                       │
└───────────────────────────────────────┘  └───────────────────────────────────────┘

Canonical rule:
    apps_* is optional.
    agentic_core is not.
    apps_* depends on agentic_core.
    agentic_core must not depend on apps_*.
```

---

## MECE ownership boundaries (do not move)

| Layer       | Owns                                                            | Does not own                              |
|-------------|-----------------------------------------------------------------|-------------------------------------------|
| **L1**      | Planning. Emits `L1PlanContract`.                               | Routing, retrieval, execution.            |
| **L0**      | Deterministic route authority. Emits `RouteContract`.           | Planning, retrieval, execution.           |
| **C0**      | Retrieval + evidence contracts. Emits `FinalEvidenceContract`.  | Planning, prompt assembly, execution.     |
| **PA**      | Prompt packet construction. Emits `CompiledPromptArtifact`.     | Routing, retrieval, execution.            |
| **L3**      | Optional orchestration of multi-step DAGs.                      | Single-step execution, final disposition. |
| **L2**      | Bounded execution. Emits `SealedArtifact`.                      | Planning, routing, final disposition.     |
| **Exit**    | Final current-run disposition. Emits `ExitReviewPacket`.        | Durable writes, post-run learning.        |
| **UWG/L4**  | Durable write admission. Consumes `CommitRequest`.              | Routing, planning, current-run state.     |
| **L6**      | Completed-run evaluation + future-run learning.                 | Current-run mutation. Routing.            |
| **apps_***  | **Domain overlay specificity only.** Schemas, rubrics, prompts, tools, workflow templates, evidence standards, output formats, memory/learning surfaces. | All of the above. Apps NEVER take spine-owned authority. |

---

## How the scanner classifies (operational)

The hardened scanner at `tools/analysis/apps_spine_coverage.py` produces
one of five buckets per app:

| Bucket                          | Meaning                                                                               |
|---------------------------------|---------------------------------------------------------------------------------------|
| `CORE_ONLY_VALID`               | Not an app. (Reserved for non-`apps_*` paths the scanner audits.)                     |
| `APP_OVERLAY_VALID`             | App imports ≥1 canonical spine contract that matches the route(s) it claims to serve. |
| `APP_STANDALONE_FORBIDDEN`      | App claims a domain runtime route but imports zero spine contracts.                    |
| `PARTIAL_SPINE_STATIC_ONLY`     | App imports infrastructure (UWG, ledger, BGE) but no authority-class contracts. Static-only spine touch; runtime authority still local. |
| `UNKNOWN_NEEDS_RUNTIME_TRACE`   | Static evidence is ambiguous. Needs runtime trace (OTEL spans / ledger rows) to classify. |

The scanner does NOT penalize core-only paths. The scanner does NOT
require `apps_*` for generic core capabilities. The scanner ONLY flags
`apps_*` packages that claim a domain runtime without the matching
authority-handoff evidence.

---

## See also

- `docs/reference/_notes/agentic_system_process_map_exec.md` — canonical spine flow
- `docs/reference/02_L1_Reasoning_Plan/02.6_L1PlanContract_Handoff.md` — L1 plan handoff
- `docs/reference/03_L0_Route_Decision_and_L3_Orchestration/03.5_L0_RouteContract_Telemetry_Replay.md` — L0 route handoff
- `docs/reference/03A_C0_Context_Engine/C0.5_Final_Evidence_Contract.md` — C0 evidence handoff
- `docs/reference/03B_PA_Prompt_Assembly/PA.7_Final_Emit_Compiled_Prompt_Artifact.md` — PA prompt artifact handoff
- `docs/reference/04_L2_Execute/04.6_L2_E5_Seal_Artifact_and_Dispatch.md` — L2 sealed artifact
- `docs/reference/05_Exit_Evaluation_and_Control/05_Live_Runtime_Exit_Control_&_Evaluation.md` — Exit packet
- `docs/reference/contracts/step1/00B_L4_UWG_REQ_MATRIX.md` — UWG commit admission
- `docs/reference/06_L6_Shadow_Evaluation_System_Learning/06_Shadow_Evaluation_System_Learning.md` — L6 post-run boundary
- `tools/analysis/apps_spine_coverage.py` — the scanner that enforces this taxonomy
- `.windsurf/rules/constitutional.md` §22, §28, §29 — co-enforcement
