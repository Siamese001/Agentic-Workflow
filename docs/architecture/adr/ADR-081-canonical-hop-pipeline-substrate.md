# ADR-081: Canonical HOP Pipeline Substrate for apps_* Inner DAGs

| Field | Value |
|---|---|
| Status | Accepted |
| Decision Date | 2026-05-01 |
| Deciders | Author-Gate (architecture_choice), confidence=0.85 |
| Impact Layers | L_APP (apps_shared, apps_lic, apps_rg, apps_underwriting_ai, apps_research, apps_rfp, apps_exec, apps_eval) |
| Plan | `.windsurf/plans/apps-hop-substrate-f7751b.md` |
| Supersedes | (none) |
| Superseded By | (none) |

## Context

The outer DAG that every R3-shaped app shares (`L1 plan → L0 route → C0 retrieve → L2 authorize_and_execute → L5+L6 evaluate_and_emit`) is owned by the `GovernedAppRunner` substrate in `apps_shared/integrations/governed_app_runner.py`. The inner per-app DAGs that run inside the L2 step were not uniform:

- **apps_rg** — real 8-HOP chain; topology mixed into `apps_rg/config/agent_spec_config.py` (380+ lines of Pydantic specs alongside DAG topology); walk implemented in `apps_rg/reasoning/RgResumeOrchestrator.py`.
- **apps_lic** — structurally declared 9-stage pipeline (`HOPPipelineExecutor` + `hop_stage_registry.py`) whose handlers were one-line stubs returning `{"status": "processed"}`. The 2026-02-08 consolidation pass (190 → 149 agents) deleted the original HOP1..HOP9 agent bodies and never ported them into the new registry. Git archaeology confirms the bodies are unrecoverable; by commit `a4661c0009` all HOP agents were already deprecation shims.
- **apps_exec / apps_research / apps_rfp / apps_eval** — no inner DAG; single-step L2 calls through engines.
- **apps_qna** — `build_time_compiler` route shape; legitimately no runtime DAG.
- **apps_underwriting_ai** — 5-engine chain with no formal orchestrator.

Without a canonical substrate, each app invents its own walk loop, checkpoint recording, and seal_step integration. As more apps grow multi-hop needs (evaluator-optimizer loops per Anthropic's `Building Effective Agents` guidance) the drift compounds.

## Decision

Establish `apps_shared/orchestration/hop_pipeline.py` as the canonical shared substrate for inner per-app DAGs. Every app with a multi-step inner pipeline conforms to this four-file structure:

| Path | Role |
|---|---|
| `apps_shared/orchestration/hop_pipeline.py` | Shared substrate — `HopStageSpec` (Pydantic), `HopRegistry`, `HopPipelineExecutor`, `Checkpoint`, `HopRunRecord`, `StageStatus` |
| `apps_<name>/config/hop_pipeline.py` | Per-app topology — module-level `REGISTRY: HopRegistry` built from a list of `HopStageSpec` |
| `apps_<name>/engines/<stage>_engine.py` | Per-stage business logic — one engine class per HOP exposing `execute(context) -> dict` |
| `apps_<name>/reasoning/<Name>Orchestrator.py` | Thin runner — delegates to `HopPipelineExecutor`; holds no walk plumbing |

**apps_qna** is explicitly out of scope (`build_time_compiler` route shape, no runtime DAG). **apps_eval / apps_exec / apps_research / apps_rfp** adopted the substrate additively on 2026-05-01 (Wave 5 below); their imperative `BaseXxxEngine`-rooted runtime remains primary, with the substrate path as a declarative alternative for replay and composability.

### Topology semantics

- Stages ordered by ascending `stage_id`; duplicates rejected at registration.
- `required=False` → stage failure records `FAILED` but does not halt the run.
- `gate=True` → stage output `{"passed": False, ...}` halts the run with `StageStatus.GATED` (Anthropic evaluator-optimizer surface).
- `optional_skip_if="<key>"` → stage skipped when `context[key]` is truthy at stage entry; circular self-ref rejected.
- Engine classes are lazy-imported via dotted path and cached; engines must be no-arg-constructible.
- `seal_step_provider` (optional) wraps each stage execution in a runtime-ADG span per the existing `system_learning_facade.seal_step` contract.

## Alternatives Considered

### Option A — Canonicalize on the apps_rg pattern (rejected; confidence 0.70)

Declare topology inside each app's `config/agent_spec_config.py`; require each app to implement its own orchestrator walk loop.

**Rejected because**: conflates config schemas with DAG topology (symptom already visible in apps_rg at 380+ LOC); every new app re-implements the walk loop and checkpoint recording; no shared executor to audit; does not solve the apps_lic port question.

### Option B — Retire apps_lic HOP machinery entirely (rejected; confidence 0.55)

Delete `HOPPipelineExecutor`, `hop_stage_registry`, the `LicHealingOrchestrator._heal_schema` hook; accept apps_lic as single-step `R3_grounded_read` like apps_exec.

**Rejected because**: declines the user task; leaves apps_rg as a one-off pattern; the next multi-hop app re-opens the same decision; apps_lic compliance-sensitive outreach plausibly benefits from multi-stage validation + gate even in the thin form.

## Consequences

### Positive

- **One executor surface to audit** — seal_step integration, stage lifecycle, failure propagation, and gate semantics live in one place.
- **Per-app files are smaller and topology-pure** — `apps_<name>/config/hop_pipeline.py` carries zero walk plumbing.
- **New multi-hop apps are cheap** — three files (config, engines/, thin orchestrator) and the existing substrate.
- **CI enforces drift** — `ops_scripts/ci/check_apps_hop_pipeline_location.py` validates structure per migrated app and emits advisories for unmigrated candidates.
- **Evaluator-optimizer pattern is first-class** — `gate=True` specs cleanly express the Anthropic workflow without per-app ad-hoc conditionals.

### Negative

- **Net-new module in apps_shared** — another shared surface to maintain.
- **apps_rg migration is a real refactor** — golden-parity test required to prove behavior parity. Deferred to a follow-up plan wave.
- **apps_lic stage bodies are scaffolded, not resurrected** — the pre-2026-02-08 domain logic is gone; scaffold engines must be filled in with real implementations (LLM generation, fact_check, compliance scan) as apps_lic matures.

### Neutral

- apps_qna stays on `builder/card_pack_builder.py` — `build_time_compiler` route shape is orthogonal to this substrate.
- Runtime-HITL posture (`HITL_ENABLED`) is orthogonal; the inner DAG runs independently of the outer HITL gate.

## Implementation Status (as of 2026-05-01)

| Wave | Scope | Status |
|---|---|---|
| 1 | Shared substrate + 27 unit tests | ✅ DONE |
| 2 | apps_lic full port (topology + 9 engines + orchestrator + heal rewire + deprecation shims + `GovernedLicRun` wire-up with `hop_checkpoints` field) | ✅ DONE |
| 3 | apps_rg substrate adoption — additive `RgHopOrchestrator` + 7-stage topology + 7 thin passthrough adapters. `RgResumeOrchestrator.run()` remains primary runtime. Golden-parity test + full BaseModel↔dict marshaling tracked in follow-up `apps-rg-substrate-deep-migration`. | ✅ DONE (shallow) |
| 4.1 | apps_underwriting_ai adopt — additive `UnderwritingHopOrchestrator` + 5-stage topology + 5 adapter engines wrapping existing stage methods. `UnderwritingEngine.run()` remains primary. | ✅ DONE |
| 4.2 | CI gate `check_apps_hop_pipeline_location.py` (advisory for unmigrated, strict for migrated). 3 migrated apps clean; apps_eval/apps_exec/apps_rfp remain as advisory candidates (single-step R3_grounded_read — adoption optional). | ✅ DONE |
| 4.3 | This ADR + Notion writeback | ✅ DONE |
| 5 (2026-05-01) | Four-app substrate extension — apps_research (3-stage), apps_rfp (3-stage), apps_exec (4-stage), apps_eval (6-stage). 29 NEW files: 4 configs + 16 adapters + 4 orchestrators + 4 smoke-test modules + 1 apps_eval hop_integration helper. Imperative `BaseXxxEngine` runtime unchanged; substrate path additive. L2 wiring closed: `hop_checkpoints`/`hop_terminal_error` fields + `_run_hop_pipeline()` helper added to `GovernedE2ERunRecord`/`GovernedRfpE2ERunRecord`/`GovernedExecE2ERunRecord`; apps_eval uses standalone `run_eval_hop_pipeline()` helper. GAP-1 smoke tests: 21 pass. CI gate: 7/7 migrated apps clean, 0 advisories. Plan: `.windsurf/plans/apps-hop-substrate-four-apps-b4a2c9.md`. | ✅ DONE |

## References

- Plan: `.windsurf/plans/apps-hop-substrate-f7751b.md`
- Substrate: `apps_shared/orchestration/hop_pipeline.py`
- First consumer: `apps_lic/config/hop_pipeline.py`, `apps_lic/reasoning/LicCampaignOrchestrator.py`
- Tests: `tests/unit/apps_shared/test_hop_pipeline.py`
- CI gate: `ops_scripts/ci/check_apps_hop_pipeline_location.py`
- Sibling substrate: `apps_shared/integrations/governed_app_runner.py` (outer DAG)
- Anthropic reference: [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) — workflow patterns (prompt chaining, routing, evaluator-optimizer)
- Author-Gate capture: `DECISION_CAPTURED: type=architecture_choice, repo_area=apps_shared/orchestration, selected=shared_substrate_hop_pipeline, outcome=executed, confidence=0.85, gap=0.15`
