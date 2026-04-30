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
| `APP_OVERLAY_STATIC_EVIDENCE`   | App imports the canonical contracts its declared routes require. **STATIC** evidence only — runtime trace is what proves the contracts are actually used. |
| `APP_STANDALONE_FORBIDDEN`      | App claims a domain runtime AND imports zero canonical contracts AND zero spine import edges.                    |
| `PARTIAL_SPINE_STATIC_ONLY`     | App imports infrastructure (UWG, ledger, BGE) but does not satisfy the contract requirements its routes claim. |
| `UNKNOWN_NEEDS_RUNTIME_TRACE`   | Static evidence is ambiguous. Needs runtime trace (OTEL spans / ledger rows) to classify. |

> **Rename note (W7)**: the historical bucket name `APP_OVERLAY_VALID`
> is preserved as a legacy alias in the scanner's emoji map for one
> release cycle so existing CI gates that grep on the old name keep
> working. New gates MUST read the canonical `runtime_mode` field with
> the new bucket name. The rename reflects the truth that a static
> import edge is not delegation evidence — it's only **static
> evidence** of intent to delegate; runtime trace (OTel spans hitting
> the contract surfaces) is what proves the contract is actually used.

The scanner does NOT penalize core-only paths. The scanner does NOT
require `apps_*` for generic core capabilities. The scanner ONLY flags
`apps_*` packages that claim a domain runtime without the matching
authority-handoff evidence.

---

## Route-typed contract requirement matrix

A single canonical contract import is too weak a signal: an app that
claims to serve grounded reads needs `RetrievalPlan` +
`FinalEvidenceContract`, not `PromptEnvelope`. The scanner therefore
requires apps to declare WHICH route types they support, then verifies
the contracts that those routes need.

The canonical mapping (single source of truth in
`tools/analysis/apps_spine_coverage.py::ROUTE_TYPE_CONTRACT_REQUIREMENTS`):

| Route type            | Required contracts                                                                                                                       |
|-----------------------|------------------------------------------------------------------------------------------------------------------------------------------|
| `R1_cache`            | `ValidatedRequest`                                                                                                                        |
| `R2_grounded_read`    | `ValidatedRequest`, `L1PlanContract`, `RouteContract`, `RetrievalPlan`, `FinalEvidenceContract`, `CompiledPromptArtifact`, `SealedArtifact`, `ExitReviewPacket` |
| `R3_action`           | `ValidatedRequest`, `L1PlanContract`, `RouteContract`, `CompiledPromptArtifact`, `SealedArtifact`, `ExitReviewPacket`, `CommitRequest`     |
| `R4_workflow`         | `ValidatedRequest`, `L1PlanContract`, `RouteContract`, `CompiledPromptArtifact`, `SealedArtifact`, `ExitReviewPacket`, `CommitRequest`     |
| `R5_fallback`         | `ValidatedRequest`                                                                                                                        |
| `domain_synthesis`    | `CompiledPromptArtifact`, `SealedArtifact`, `ExitReviewPacket`                                                                            |
| `durable_write`       | `CommitRequest`                                                                                                                           |
| `learning_writeback`  | `RuntimeExhaustBundle`                                                                                                                    |
| `build_time_compiler` | (none) — apps_qna shape; produces a context pack the operator pastes into an external agent. The spine is not in the runtime path of the pasted answer. **Must be explicitly declared in the manifest** to qualify; the scanner does not assume. |

An app declares its routes via `apps_<name>/spine_manifest.yaml`:

```yaml
schema_version: 1
app: apps_<name>
claimed_routes:
  - type: R2_grounded_read
    description: "What this route does in your domain."
  - type: durable_write
    description: "Why this app needs L4 admission."
```

When the manifest is present, the scanner unions the per-route
requirements and checks that the app imports every contract in the
resulting set. Missing contracts → `PARTIAL_SPINE_STATIC_ONLY` (with
the missing contracts listed in `manifest_missing_contracts`). All
present → `APP_OVERLAY_STATIC_EVIDENCE`.

When the manifest is **absent**, the scanner falls back to the legacy
any-canonical-contract-counts heuristic so existing apps don't regress
at rollout. Apps SHOULD declare a manifest; until they do, the
classification is approximate and the evidence string mentions "declare
a manifest to enable route-typed validation".

---

## Route-Shape Taxonomy for `apps_*`

The route-shape taxonomy is the **canonical vocabulary** apps use to
declare what they actually do. It is the public contract of the
manifest's `claimed_routes[].type` field. Six shapes:

| Route shape | Required contracts | When to declare |
|---|---|---|
| **`build_time_compiler`** | (none) | Offline artifact builder. Produces a context pack the operator pastes into an external agent. The spine is **not** in the runtime path of the pasted answer. A `ValidatedRequest` envelope **may** be acceptable as defensive intake-validation evidence (apps_qna shape), but is **not required**. |
| **`R3_grounded_read`** | `ValidatedRequest`, `L1PlanContract`, `RouteContract`, `RetrievalPlan`, `FinalEvidenceContract`, `CompiledPromptArtifact` (or `PromptEnvelope`), `SealedArtifact`, `ExitReviewPacket` | Grounded read with retrieval + sealed answer; no durable side effect. The full R3 contract chain is required because the spine **is** in the runtime path. Examples in this codebase: `apps_research`, `apps_exec`. |
| **`R3R4_managed_workflow`** | R3 contract chain **+ `CommitRequest`** | Multi-step / workflow with downstream durable write. The R3 chain handles the read-and-synthesize half; `CommitRequest` covers the L4 admission half. Examples: `apps_lic`, `apps_rfp`. |
| **`evaluator_only`** | (none, **but exception record required**) | Evaluation surface. Routing eval through `evaluate_and_emit` (L5/L6) creates a circular evaluation-of-evaluator loop. Generic spine wrapping is structurally inappropriate here, so the empty required-contract set is justified by a **recorded exception charter**, not by absence of a runtime path. Example: `apps_eval`. |
| **`core_adjacent_utility`** | (none, **but exception record required**) | Library-style or regulated-domain protocol with its own governance. Generic spine wrapping would be **contract theater** — the app already provides equivalent guarantees via a domain-specific protocol (e.g., `CoreAdapter` + `CoreHandoffPayload`). The empty required-set is justified by the same exception-charter mechanism as `evaluator_only`. Example: `apps_underwriting_ai`. |
| **`UNKNOWN_NEEDS_RUNTIME_TRACE`** | n/a | **Classification bucket, not a route type.** Apps that cannot prove a route shape from static analysis (no domain-runtime markers, or a formal-exception route declared without the supporting exception record) land here. Future runtime-trace evidence (OTel spans, ledger rows) is required to re-classify. |

### The empty-required-set distinction (important)

`build_time_compiler`, `evaluator_only`, and `core_adjacent_utility` all
have **empty required-contract sets**, but they are **not semantically
equivalent**. The scanner treats them differently:

| Route | Empty set is justified by | Scanner bucket when honored | Scanner bucket when manifest is missing exception fields |
|---|---|---|---|
| `build_time_compiler` | The spine is not in the runtime path. The pack is consumed by an external agent. | `APP_OVERLAY_STATIC_EVIDENCE` | `APP_OVERLAY_STATIC_EVIDENCE` (manifest is self-justifying) |
| `evaluator_only` | The runtime path WOULD circularly invoke the evaluator. The exception charter is what makes the empty set defensible. | `FORMAL_EXCEPTION_STATIC_EVIDENCE` | **`UNKNOWN_NEEDS_RUNTIME_TRACE`** — formal claim cannot be verified |
| `core_adjacent_utility` | The app's domain protocol (e.g., `CoreAdapter` + `CoreHandoffPayload`) provides equivalent guarantees; generic spine wrapping would duplicate the surface without semantic gain. | `FORMAL_EXCEPTION_STATIC_EVIDENCE` | **`UNKNOWN_NEEDS_RUNTIME_TRACE`** — formal claim cannot be verified |

### `FORMAL_EXCEPTION_STATIC_EVIDENCE` bucket

Introduced in W8. Distinct from `APP_OVERLAY_STATIC_EVIDENCE` because
the empty required-set is **not** a property of the route — it's a
property of the **recorded exception charter**.

A manifest qualifies for `FORMAL_EXCEPTION_STATIC_EVIDENCE` only when
**all three** conditions hold:

1. At least one declared route is in `{evaluator_only, core_adjacent_utility}`.
2. `exception.reason_code` is non-empty (e.g., `circular_dependency`, `regulatory_domain`).
3. `exception.compensating_controls` is a non-empty list.

The scanner emoji is **📜** to visually distinguish it from
`APP_OVERLAY_STATIC_EVIDENCE` (✅) and `PARTIAL_SPINE_STATIC_ONLY` (🟠).

### Manifest shape for formal exceptions

```yaml
schema_version: 1
app: apps_<name>

claimed_routes:
  - type: evaluator_only         # or: core_adjacent_utility
    description: ...

exception:
  reason_code: circular_dependency  # or: regulatory_domain
  exception_record_class: GovernedEvalException
  exception_record_module: apps_eval.integrations.governed_eval_exception
  blocked_layers: [L0, L1, C0, L2, L5, L6]
  safe_layers: [BUS_T_telemetry, conformance_metadata]
  compensating_controls:
    - "CC-EVAL-01: ..."
    - "CC-EVAL-02: ..."
    - "CC-EVAL-03: ..."
    - "CC-EVAL-04: ..."
  review_cadence: annual
  owner: <team>

notes:
  - "no ValidatedRequest wrapper required; no app-code migration in this pass"
```

### Why apps_qna's pattern does NOT generalize

The apps_qna `build_time_compiler + ValidatedRequest envelope` shape
worked because:

- apps_qna's runtime path goes **outside** the spine (operator pastes into ChatGPT)
- A `ValidatedRequest` envelope adds **defensive intake validation** that
  the build-time invocation genuinely benefits from

For the runtime-coupled apps (apps_research, apps_exec, apps_lic,
apps_rfp), copying that pattern would understate the delegation
evidence: those apps' actual route shapes are `R3_grounded_read` or
`R3R4_managed_workflow` and need the **full R3 contract chain**, not
just `ValidatedRequest`.

For the formal-exception apps (apps_eval, apps_underwriting_ai),
copying the pattern would be **contract theater**: a `ValidatedRequest`
envelope would either duplicate an existing domain-specific intake
contract (apps_underwriting_ai's `UnderwritingRequest`) or paper over a
fundamental architectural exemption (apps_eval's circularity boundary).
The honest move is the manifest's `exception` block — no wrapper code.

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
