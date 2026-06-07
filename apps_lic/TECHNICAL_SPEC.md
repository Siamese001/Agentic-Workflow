# apps_lic — Technical Spec

## Purpose

Governed multi-hop agent application for outbound communication (lifecycle intelligence + communication). Every run emits an auditable evidence packet; every outbound message is grounded in profile/research facts with explicit citations.

## Architecture

### HOP pipeline (canonical flow)

1. **HOP1 — ProfileAnalysis**: parse/enrich target profile (CV, LinkedIn, company context)
2. **HOP2 — Research**: deep research on target + company
3. **HOP3 — SenderGrounding**: ground sender persona (facts, tone, authority)
4. **HOP4 — Routing**: `DecisionRouter` selects branch (cold/warm/introduced, industry cluster, authority tier) via `validators/policy/*.yaml` decision tables (NOT imperative conditionals)
5. **HOP5 — Authoring**: compose message(s) using grounded facts
6. **HOP6 — Scoring/QA**: rubric evaluation via `JudgeBase` subclasses
7. **HOP7 — GateDecision**: pass/fail/escalate via policy table
8. **HOP8 — Emission**: formatted output + evidence packet

### Folder layout (post-ADR-082)

```
apps_lic/
├── config/              # Agent specs, rubrics, domain contract
├── engines/             # HOP engines (HOP1..HOP8)
│   └── outreach/        # outreach-engine helpers
├── reasoning/           # Planners, HOP executor, message/profile planners
├── services/
│   ├── persistence/     # SQLite durability for in-memory engines
│   └── observability/   # Telemetry bus + outreach-learning subscribers
├── validators/          # Schema validators
│   └── policy/          # Decision tables (YAML) + DecisionRouter + JudgeBase
├── integrations/        # Governed run entrypoints + execution adapter
├── outputs/             # Renderers
├── types/               # Pydantic models
├── utils/
└── spine_manifest.yaml
```

## Contracts

- **Input**: profile + sender context + invocation mode (`ENVELOPE_FIRST` | `SPINE_FULL`)
- **Output**: `OutreachEvidencePacket` containing every HOP's inputs, outputs, citations, policy-table match, and judge scorecards
- **Persistence**: SQLite at `~/.agentic/apps_lic/runs.db` (schema versioned)

## Dependencies

- `agentic_core` spine primitives (L0 routing, L3 orchestration, L5 policy)
- `apps_shared` cross-app contracts, validators, emission helpers
- `system_learning` episodic memory (via `apps_shared.integrations.adapters.system_learning_facade`)

## Invariants

1. Every HOP emits a lifecycle-trace event; every trace is persisted.
2. `DecisionRouter` is the ONLY branching primitive for routing/policy decisions — no `if/elif` chains in engines.
3. Policy tables live in `validators/policy/*.yaml` and are versioned with the code.
4. External input (profiles, research output) is validated through `validators/` before reaching engines.

## References

- Plan: `docs/archive/windsurf/legacy-tree/plans/decision-router-policy-tables-b3a4d2.md`
- Plan: `docs/archive/windsurf/legacy-tree/plans/apps-lic-runtime-adapter-*.md`
- ADR-082 taxonomy
