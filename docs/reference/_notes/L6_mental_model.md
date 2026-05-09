# L6 Mental Model — Observability + System Learning

> **Doctrine:** L6 is **one layer with two physical surfaces**. `agentic_core/L6_observability/` is the *passive* surface (exhaust capture). `system_learning/` is the *active* surface (learn from exhaust). The latter sits at repo root without an `L6_` prefix — that's a known doctrinal/code-layout drift tracked by plan `l6-folder-rename-doctrinal-alignment-a8c4e2` (Deprioritized).

## Top-level shape

```
L6 (one layer, two surfaces)
│
├── 1. OBSERVABILITY  ─ passive ─  agentic_core/L6_observability/
│   ├── runtime_trace/      OTEL spans, trace correlation, runtime ADG hand-off
│   ├── semconv/            semantic-convention vocabulary for span attributes
│   ├── execution/          exec-side tracing (tool calls, agent dispatch)
│   ├── reasoning/          reasoning-side tracing (planner / cognition spans)
│   ├── shadow_eval/        observe-only eval hooks (no policy effect)
│   ├── enforcement/        anti-bypass monitors, agent_monitor.py
│   ├── types/              span / event / decision-event schemas
│   └── utils/              shared helpers
│
└── 2. SYSTEM LEARNING ─ active ─  system_learning/   (root — no L6_ prefix yet)
    │
    ├── 06.1 Exhaust Ingest & Normalization
    │   ├── adapters/             intake adapters (healing-outcome, exemplar-seeder, ...)
    │   ├── ports/                inbound contracts (typed boundaries for ingest)
    │   ├── buses/                bus_p, meta-learning bus, prompt-outcome bus
    │   ├── raw/                  unprocessed exhaust landing zone
    │   ├── runtime_adg/          runtime ADG ingest from OTEL
    │   ├── adg/                  static ADG references for cross-correlation
    │   └── telemetry/            ingest-side metrics
    │
    ├── 06.2 Observer Law / Surface Isolation / Eval Readiness
    │   ├── invariants/           layer-isolation invariants (cannot affect runtime)
    │   ├── enforcement/          observer-law enforcement (no write-back to L0..L5)
    │   ├── constraints/          eval-readiness preconditions
    │   ├── policy/               read-only policy projection
    │   └── validators/           structural validators on ingested events
    │
    ├── 06.3 Outcome Trajectory Governance & Eval
    │   ├── engines/              pattern-analysis, optimization-proposal, drift, ... (~60 engines)
    │   ├── rubrics/              trajectory rubrics + grading criteria
    │   ├── correlation/          cross-trace correlation (cause-effect linking)
    │   └── fingerprinting/       trajectory fingerprints for dedup + clustering
    │
    ├── 06.4 Human Calibration & Eval Record Seal
    │   ├── golden/               human-labeled golden set
    │   ├── provenance/           sealed evidence chain (immutable)
    │   └── memory/ (read side)   eval-record retrieval
    │
    ├── 06.5 Signal Fusion, RCA, Pattern Synthesis
    │   ├── meta_learning/        cross-signal fusion + pattern extraction
    │   ├── embedding/            vector representations of incidents / prompts / mutations
    │   ├── ml_integration/       ML-model boundary
    │   ├── confidence/           confidence scoring on synthesized patterns
    │   └── arbitration/          conflict resolution between competing signals
    │
    ├── 06.6 Proposal Drafting & Admission Gate
    │   ├── pipelines/            meta-learning pipeline (proposal authoring)
    │   ├── output/               admission-gate output staging
    │   └── engines/optimization_proposal_engine.py + retrieval_profile_proposal_manager.py
    │
    ├── 06.7 Gauntlet → Approval → UWG Promotion → Future Run
    │   ├── engines/approval_gauntlet_engine.py
    │   ├── scripts/meta_learning_operator.py    operator entrypoint
    │   ├── state/                gauntlet run-state
    │   └── runtime_hitl_consumer.py             HITL approval consumption
    │
    ├── 06.8 Observability KPIs / Tests / Anti-Bypass
    │   ├── monitoring/           KPI emitters
    │   └── snapshots/            point-in-time eval snapshots for regression
    │
    └── 06.9 Memory Promotion Interface
        ├── memory/ (write side)  promote-to-long-term-memory writers
        └── stores/               persistence backends (sqlite, vector, blob)
```

## Cross-cutting modules (not chapter-specific)

| Path | Role |
|---|---|
| `system_learning/__init__.py` | Public surface — entrypoints for L0..L5 to read L6 outputs (read-only). |
| `system_learning/_tracing.py` | Internal tracing helpers for system-learning code paths. |
| `system_learning/v6_contract_map.py` | v6 contract surface map; couples to `agentic_core/L3_orchestration/exit_eval/v6/`. |
| `system_learning/config/` | Static config (rubric paths, embedding model IDs, store URIs). |
| `system_learning/runtime/` | Runtime helpers shared across stages. |
| `system_learning/types/` | Cross-stage data contracts (Pydantic / TypedDict shapes). |
| `system_learning/logs/` | Local log staging (gitignored). |

## Why `system_learning/` is doctrinally L6

1. **ADG layer-resolution heuristic already tags it.** Run `mcp1_adg_nodes_by_layer(layer="L6")` — `system_learning/*` modules appear alongside `agentic_core/L6_observability/*`.
2. **No write-path back to L0..L5.** Observer-law enforcement (`system_learning/enforcement/`, `system_learning/invariants/`) hard-blocks any reverse coupling. The only path *out* of L6 back into runtime is the **UWG promotion gate** (06.7), which is itself an HITL-gated boundary, not a direct write.
3. **Doc folder.** `docs/reference/06_L6_Shadow_Evaluation_System_Learning/` (06.1–06.9) is the canonical L6 chapter set. The L6_ prefix on the doc folder confirms layer membership.

## Observability vs System Learning — the boundary

| Concern | Observability (`agentic_core/L6_observability/`) | System Learning (`system_learning/`) |
|---|---|---|
| Posture | Passive — emit and store | Active — read, fuse, propose |
| Latency | Synchronous to runtime (must not block) | Asynchronous batch / streaming |
| Failure mode | Drop spans, never block runtime | Skip cycle, never propose unsafe change |
| Promotion path | None — terminal sink for runtime exhaust | Gauntlet → UWG → L4 (06.7) |
| Output consumers | Telemetry backends, runtime ADG | Memory promotion, retrieval profile updates, prompt mutations |

## Pointers

- Full doctrinal chapters: `@c:\Git\Agentic-Workflow-FRESH\docs\reference\06_L6_Shadow_Evaluation_System_Learning`
- ADG canonical invariants (Static vs Runtime ADG distinction): `.windsurf/rules/adg-canonical-invariants.md` §8
- Promotion-gate rule: `.windsurf/rules/evaluation-promotion-gate.md`
- Folder-rename plan (Deprioritized): `.windsurf/plans/l6-folder-rename-doctrinal-alignment-a8c4e2.md`
- Non-invasive alignment plan: `.windsurf/plans/l6-doctrinal-alignment-noninvasive-b9d3f5.md`

## Alignment Status (plan `l6-doctrinal-alignment-noninvasive-b9d3f5`)

| Wave | Mechanism | Status | Notes |
|---|---|---|---|
| W1 | In-tree `__layer__ = "L6"` markers on root + 27 subpackage `__init__.py` files | ✅ Landed | 28/28 smoke tests pass. Root declares `__l6_surface__ = "active"`. Each subpackage declares `__l6_chapter__` per the chapter map above. |
| W2 | Forward-import alias `agentic_core.L6_system_learning` (re-exports `system_learning` via `sys.modules` rebind) | ✅ Landed | 31/31 smoke tests pass. Both paths first-class; `is`-comparison verified state-shared (no double-load); zero DeprecationWarning. |
| W3 | `LAYER.md` declarations on both surfaces | ✅ Landed | `system_learning/LAYER.md` (active) + `agentic_core/L6_observability/LAYER.md` (passive). |
| W4 | Observer-law CI gate `check_l6_observer_law.py` | ✅ Landed (advisory) | 8/8 unit tests pass. **2 real findings** surfaced: `system_learning/ports/{meta_outcome_bus_hook,outcome_write_back_hook}.py` import `agentic_core.L3_orchestration.healers.healing_tier_dispatcher`. Remediation deferred. Promotion to fail-closed gated on baseline clean. Bypass: `L6_OBSERVER_LAW_BYPASS=1`. |
| W5 | ADG layer-tag consistency CI gate `check_l6_layer_tag_consistency.py` | ✅ Landed (advisory) | 6/6 unit tests pass. **292 modules** under `system_learning/` are NOT tagged `layer=L6` in current snapshot — the ADG layer-resolution heuristic does not yet recognize `system_learning/*` as L6. Remediation deferred (heuristic update is the canonical fix, NOT moving the files). Bypass: `L6_LAYER_TAG_BYPASS=1`. |
| W6 | Mental-model doc updated with Alignment Status table (this section) | ✅ Landed | You are reading it. |

### Files added/modified by the plan

- `system_learning/__init__.py` — docstring + `__layer__` + `__l6_surface__`
- 27× `system_learning/<sub>/__init__.py` — `__layer__` + `__l6_chapter__`
- `system_learning/LAYER.md` — new
- `agentic_core/L6_observability/LAYER.md` — new
- `agentic_core/L6_system_learning/__init__.py` — new (forward alias)
- `tests/unit/system_learning/test_l6_layer_markers.py` — new
- `tests/unit/agentic_core/L6_system_learning/test_l6_system_learning_alias.py` — new
- `ops_scripts/ci/check_l6_observer_law.py` + tests — new (gate L6-OBS)
- `ops_scripts/ci/check_l6_layer_tag_consistency.py` + tests — new (gate L6-TAG)
- `ops_scripts/ci/run_contract_gates.py` — registered both gates as advisory
- `docs/reference/_notes/L6_mental_model.md` — this section

### Total test additions

73 tests (28 W1 + 31 W2 + 8 W4 + 6 W5). All green. Zero behavioral regressions in `system_learning` or `agentic_core/L6_observability`.