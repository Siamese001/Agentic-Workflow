# Family Seed Registry — Wave E1

**Authority:** Chat 1 / integration lead, E1-Setup run.
**Status:** Reserved (not yet `DRAFT` as a schema Family record — E1a publishes the `families.yaml` proposal).
**ID format:** `F<NN>` per `id_conventions.md`. Regex `^F[0-9]{2}$`.

This registry is the **sole authoritative list of minted Family IDs** for this run. Any other lane or document that claims a Family ID not listed here is invalid.

---

## Minted Families (F01..F12)

### F01 — Request Intake + Envelope Check
**Owning layer:** L0 (boundary) / L5 (policy) — definitive owner to be confirmed by E1c.
**Intent:** Every inbound request MUST be admitted only after envelope validation (shape, auth, policy preconditions) before any downstream reasoning, routing, or execution is attempted.

### F02 — L1 Reasoning + Plan Generation
**Owning layer:** L1
**Intent:** L1 is the sole authority that decomposes an admitted request into a plan. No other layer MAY produce plans; other layers consume L1's plan output.

### F03 — L0 Route Decision + Switching
**Owning layer:** L0
**Intent:** L0 is the sole route authority. It selects the downstream capability or chain that will serve a plan step. No other layer MAY choose routes.

### F04 — C0 Context Assembly + Grounding
**Owning layer:** C0 (cross-cutting context layer) — confirm in E1c scope review.
**Intent:** Context required by L1, L2, and L3 MUST be assembled through C0's grounding path, so that reasoning and execution operate on a consistent, attributable context set.

### F05 — L3 Orchestration
**Owning layer:** L3
**Intent:** L3 orchestrates multi-step execution of a plan, coordinating L2 task executions and handling intra-plan sequencing. L3 does not generate plans (L1) and does not choose routes (L0).

### F06 — L2 Task Execution
**Owning layer:** L2
**Intent:** L2 executes individual tasks dispatched by L3 against the route decided by L0. L2 does not plan, does not route, and does not mutate durable state except through the Universal Write Gate (F09).

### F07 — L2 Heal / Retry / Recovery
**Owning layer:** L2
**Intent:** Failed L2 task executions MUST be routed through a bounded heal/retry/recovery path. Unrecoverable failures MUST surface to L3 for re-planning and MUST NOT silently mutate state.

### F08 — Runtime Exit Control + Evaluation Spine
**Owning layer:** L5 (policy) with L3 (orchestration) cooperation.
**Intent:** Runtime termination and result acceptance flow through a single evaluation spine that applies exit policy, records outcome, and signals the write gate. Ad-hoc exit paths are forbidden.

### F09 — Universal Write Gate
**Owning layer:** L4 (durable state) with L5 (policy) authority.
**Intent:** The Universal Write Gate is the sole durable write path. All mutations to authoritative state MUST pass through it; no layer may bypass.

### F10 — L4 Durable Archive / State Authority
**Owning layer:** L4
**Intent:** L4 is the authoritative durable state. Reads and writes of canonical state are served by L4; writes only via F09. Other layers MUST NOT hold private durable state that shadows L4.

### F11 — L5 Policy / Safety Authority
**Owning layer:** L5
**Intent:** L5 is the cross-cutting policy and safety authority. Its policies bind L0 routing, L2 execution, F09 write gating, and F08 exit control. L5 does not execute tasks and does not mutate state directly.

### F12 — L6 Observability + Future-Run Learning
**Owning layer:** L6
**Intent:** L6 observes the current run and feeds learning into **future** runs. L6 MUST NOT influence current-run decisions, route choices, or state mutations.

---

## Confirmation Notes for Downstream Lanes

- **E1a (family spine)** MUST publish `families.yaml` whose entries match these IDs, titles, and intents verbatim unless a HITL revision is approved.
- **E1b (atoms)** MUST use exactly these Family IDs as `family_id`. No `F13+` unless integration lead revises this registry.
- **E1c (authority scope)** MUST confirm or refine the `owning_layer` choices marked above with "confirm in E1c scope review".
- **E1d (interactions)** MUST treat every edge between a layer boundary concern and the Write Gate, Policy, or Observability layer as an explicit `InteractionEdge` record.

---

## Registry Closure

No further Family IDs are minted in this E1-Setup run. The next integer available to the integration lead in a **future run** would be `F13`. Lanes that reach the end of E1 believing new families are needed MUST log `proposed_new_family` in their README and defer to HITL.
