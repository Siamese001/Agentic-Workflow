# apps_lic — Lifecycle Intelligence & Communication

A multi-hop agent application that profiles a target, researches them, grounds the result against canonical state, and authors outbound communication (email / LinkedIn) through the **canonical-dispatch spine** recorded in `apps_shared/integrations/app_registry.py`. The app is a formal governed exception to `GovernedAppRunner`, with compensating controls for the canonical `apps_lic` product path.

## Design Patterns at Work

- **HOP Pipeline Pattern** — `HopPipelineExecutor` (from `apps_shared/reasoning/orchestration/`) walks a typed multi-stage topology with replay support. Stages: profile → research → ground → author → escalate-or-emit.
- **Decision-Table Routing** — `validators/policy/` exposes decision tables consumed by `DecisionRouter`, replacing imperative classifier chains. Routing is data, not branching code.
- **Telemetry Bus + Subscribers** — `services/observability/` is a pub-sub bus with structured event subscribers. The runtime emits, observers consume — no direct logging coupling.
- **Persistence Service** — `services/persistence/` is a SQLite-backed durability layer. State changes do not bypass it; the HOP executor writes through.
- **Canonical Dispatch Governed Exception** — `python -m apps_lic` routes through `run_canonical_apps_lic_spine`; the registry records `GovernedAppRunner` / `GovernedLicRun` as blocked layers and tracks compensating controls in `GovernedLicException`.
- **Threat-Modeled Surface** — `THREAT_MODEL.md` documents the external-input surface (profile YAML, JD markdown, prompt-injection vectors).

## Quickstart

```bash
# Envelope-first mode (full HOP run)
python -m apps_lic --input-profile <path-to-profile.yaml> --mode=ENVELOPE_FIRST

# Touch-scheduled campaign mode
python -m apps_lic --input-profile <path-to-profile.yaml> --mode=CAMPAIGN
```

See `RUNBOOK.md` for operational semantics and `SLO.md` for runtime budgets.

## Architecture (post-ADR-082)

```
apps_lic/
├── L1_cognition/                    # message_planner, profile_planner (top-level per ADR-082)
├── reasoning/                       # planners, scorers, HOP pipeline executor
├── engines/                         # HOP1..HOPn agent engines (profile, research, grounding, authoring)
│   └── outreach/                    # outreach-specific engine helpers
├── validators/
│   └── policy/                      # decision tables consumed by DecisionRouter
├── services/
│   ├── persistence/                 # SQLite durability
│   └── observability/               # telemetry bus + subscribers
├── integrations/                    # governed run entrypoints + execution adapter
├── coordination/                    # HITL escalation, touch scheduler, touch-state integration
├── types/                           # Pydantic models
├── config/                          # specs, ab_variant_policy, agent_spec_config
└── spine_manifest.yaml              # spine wiring + canonical route claim
```

## HOP Pipeline (high-level)

```
ProfileRequest
  → 1. profile        (build target dossier from input YAML + canonical state)
  → 2. research       (delegated research grounded against L4 + retrieval gate)
  → 3. ground         (verify claims against canonical sources, register provenance)
  → 4. author         (compose message — email / LinkedIn — under length and tone bounds)
  → 5. exit           (HITL escalation if signals fall below configured floor; otherwise emit)
  → OutboundEnvelope (message body + metadata + provenance + decision packet)
```

## Coordination Layer

- **HITL escalation** — `coordination/hitl_escalation.py` routes uncertain decisions to a human review surface before any outbound action.
- **Touch scheduler** — `coordination/touch_scheduler.py` manages campaign cadence and prevents over-contact.
- **Touch-state integration** — `coordination/touch_state_integration.py` syncs cadence state with L4 so reschedules are durable and auditable.

## Companion Docs

- `TECHNICAL_SPEC.md` — detailed architecture
- `TEST_STRATEGY.md` — test pyramid + coverage targets
- `RUNBOOK.md` — ops runbook
- `SLO.md` — budgets and error-rate targets
- `SVP_ENGINEERING_REVIEW.md` — engineering review snapshot
- `THREAT_MODEL.md` — external-input threat surface
- `spine_manifest.yaml` — spine wiring + canonical route claim
