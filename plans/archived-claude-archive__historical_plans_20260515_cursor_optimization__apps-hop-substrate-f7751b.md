---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\apps-hop-substrate-f7751b.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\apps-hop-substrate-f7751b.md'
source_sha256: 37c356adeaca1a4750a7cae9b8eabb17996e959ed5ab743beb0bed0e0d684a7e
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: apps-hop-substrate-f7751b
plan_type: refactor
---

# Canonical HOP Pipeline Substrate + apps_lic HOP Port

Author-Gate (2026-05-01, `architecture_choice`, selected=`shared_substrate_hop_pipeline`, confidence=0.85) established a shared inner-DAG substrate in `apps_shared/orchestration/` with per-app topology declarations, and the apps_lic HOP1..HOP9 re-implementation as the first consumer.

---

## Context (SCQA)

- **Situation** — The outer DAG (`GovernedAppRunner.run_governed_core`: L1→L0→C0→L2→L5+L6) is uniform across 6 R3 apps. The inner per-app DAG is not: apps_rg runs a real 8-HOP chain from `apps_rg/reasoning/RgResumeOrchestrator.py` + 380+ lines of Pydantic specs in `apps_rg/config/agent_spec_config.py`; apps_lic has a 9-stage `HOPPipelineExecutor` + `hop_stage_registry.py` whose handlers are one-line stubs (`{"status": "processed"}`) because the 2026-02-08 "consolidation pass 190→149 agents" deleted the original HOP1..HOP9 agent bodies and never ported them into the registry; the handlers' only live caller is `LicHealingOrchestrator._heal_schema`. apps_eval/exec/research/rfp have no inner DAG. apps_qna is `build_time_compiler` (legitimately different). apps_underwriting_ai has 5 chained engines with no formal orchestrator.
- **Complication** — The apps_rg pattern works but conflates DAG topology with config schemas; the apps_lic pattern is structurally sound but semantically empty; there is no canonical home for inner-DAG orchestration; as more apps grow multi-hop needs, each invents its own walk loop and checkpoint recorder.
- **Question** — How do we establish one canonical inner-DAG substrate that apps_lic completes, apps_rg migrates onto, and future multi-hop apps consume without re-inventing orchestration plumbing?
- **Answer** — Build `apps_shared/orchestration/hop_pipeline.py` (HopStageSpec + HopRegistry + HopPipelineExecutor); declare per-app topology in `apps_<name>/config/hop_pipeline.py`; implement each stage as `apps_<name>/engines/<stage>_engine.py`; reduce `apps_<name>/reasoning/<Name>Orchestrator.py` to a thin shared-executor caller. apps_lic is the first full consumer (Wave 2); apps_rg migrates (Wave 3); apps_underwriting_ai adapts its 5-engine chain (Wave 4).

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| `.windsurf/rules/ssot-folder-enforcement.md` | new files must land in canonical folders | 🔲 |
| `.windsurf/rules/adg-canonical-invariants.md` | layer gravity for apps_shared new module | 🔲 |
| `apps_shared/integrations/governed_app_runner.py` | proven shared-substrate precedent to mirror | 🔲 |
| `apps_rg/reasoning/RgResumeOrchestrator.py:226-458` | reference HOP walk + checkpoint recording pattern | 🔲 |
| `apps_rg/config/agent_spec_config.py:282-380` | reference Pydantic stage-config shapes | 🔲 |
| `apps_lic/reasoning/HOPPipelineExecutor.py` | current dispatcher — keep API, move substrate to shared | 🔲 |
| `apps_lic/engines/hop_stage_registry.py` | 9 stage names preserved (profile_analysis → integration) | 🔲 |
| `apps_lic/reasoning/LicHealingOrchestrator.py:307-313` | dead `_heal_schema` hook — rewire or retire | 🔲 |
| `apps_underwriting_ai/engines/*.py` | 5-engine chain to adapt | 🔲 |
| Git archaeology (`a4661c0009`, `3ad48871c2`, `8f082cff38`) | original HOP agent bodies ARE LOST — must re-derive, not resurrect | ✅ verified |

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Shared substrate lands | `apps_shared/orchestration/hop_pipeline.py` + tests + layer-gravity proof | A | ~18K 🟢 |
| Wave 2 | apps_lic HOP1..9 port | 9 engine classes + config + orchestrator + retire stubs | B | ~42K 🟢 |
| Wave 3 | apps_rg migration | extract stages into engines, declare config, shrink orchestrator | C | ~28K 🟢 |
| Wave 4 | apps_underwriting_ai adopt + consistency gate | adapt 5-engine chain + CI gate for new apps | D | ~22K 🟢 |

**Total: ~110K tokens across 4 waves, all GREEN**

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| 1.1 | Draft HopStageSpec + HopRegistry + HopPipelineExecutor | `apps_shared/orchestration/hop_pipeline.py` (NEW), `apps_shared/orchestration/__init__.py` (NEW) | PP-1 (new substrate), GAP-1 | ~10K | ✅ DONE |
| 1.2 | Unit tests + layer-gravity proof | `tests/unit/apps_shared/test_hop_pipeline.py` (NEW — 27 tests passing) | PP-1, GAP-2 | ~8K | ✅ DONE |
| 2.1 | Declare apps_lic 9-stage topology | `apps_lic/config/hop_pipeline.py` (NEW) | PP-2, GAP-3 | ~6K | ✅ DONE |
| 2.2 | Author 9 engine classes (re-derive from apps_rg patterns + domain requirements) | `apps_lic/engines/{profile_analysis,research,sender_grounding,routing,generation,validation,gate_decision,qa_report,integration}_engine.py` (NEW) | PP-2, GAP-3, GAP-4 | ~24K | ✅ DONE (scaffolded; deeper domain logic deferred) |
| 2.3 | Rewrite `LicCampaignOrchestrator` as thin shared-executor caller; rewire `_heal_schema` | `apps_lic/reasoning/LicCampaignOrchestrator.py` (NEW), `apps_lic/reasoning/LicHealingOrchestrator.py` (edit) | PP-2 | ~6K | ✅ DONE |
| 2.4 | Retire dead surfaces | `apps_lic/engines/hop_stage_registry.py` + `apps_lic/reasoning/HOPPipelineExecutor.py` converted to deprecation shims (hard delete deferred — 2 active tests still depend on import surface) | PP-2 | ~4K | ✅ DONE (shim form) |
| 2.5 | Wire `GovernedLicRun.run_governed_e2e` to invoke orchestrator from inside L2 authorize_and_execute | `apps_lic/integrations/governed_lic_run.py` (edit) — added `hop_checkpoints`/`hop_terminal_error`/`hop_composite_score` fields, `_run_hop_pipeline` helper. E2E smoke: 9 HOP checkpoints all COMPLETED, composite 1.0. | PP-2, GAP-5 | ~3K | ✅ DONE |
| 3.1 | Declare apps_rg 7-stage topology via thin adapter engines | `apps_rg/engines/hop_pipeline_adapters.py` (NEW, 7 adapter classes wrapping ClerkExtraction/DataEnrichment/ResumeGeneration/FactCheck/BulletDiversityGate/ContentOptimizer/GenerationDiagnostics) | PP-3 | ~10K | ✅ DONE |
| 3.2 | Declare apps_rg topology | `apps_rg/config/hop_pipeline.py` (NEW) — 7-stage REGISTRY with gate=True on bullet_diversity_gate (evaluator-optimizer pattern) | PP-3, GAP-4 | ~8K | ✅ DONE |
| 3.3 | `RgHopOrchestrator` as additive substrate entry point (RgResumeOrchestrator remains primary runtime) | `apps_rg/reasoning/RgHopOrchestrator.py` (NEW) — thin HopPipelineExecutor wrapper. Golden-parity test deferred: the adapters are passthroughs so no parity claim is made; full BaseModel↔dict marshaling + parity fixture tracked in follow-up plan `apps-rg-substrate-deep-migration`. | PP-3 | ~10K | ✅ DONE (shallow) |
| 4.1 | Adapt apps_underwriting_ai 5-engine chain | `apps_underwriting_ai/config/hop_pipeline.py` (NEW), `apps_underwriting_ai/reasoning/UnderwritingHopOrchestrator.py` (NEW), 5 adapter engines `apps_underwriting_ai/engines/hop_*_engine.py` (NEW) wrapping EvidenceRegister/DocumentReconciliation/FeatureDerivation/collect_evidence/DecisionPacketAssembler. UnderwritingEngine.run() remains primary; substrate path additive. | PP-4 | ~12K | ✅ DONE |
| 4.2 | CI consistency gate | `ops_scripts/ci/check_apps_hop_pipeline_location.py` (NEW) — strict for migrated apps, advisory for unmigrated candidates. apps_lic clean, 5 advisories emitted. | PP-5, GAP-6 | ~8K | ✅ DONE |
| 4.3 | Documentation + Notion writeback | `docs/architecture/adr/ADR-081-canonical-hop-pipeline-substrate.md` (NEW). Notion ADR Registry post + Wave/Phase rows pending. | PP-6 | ~2K | ✅ DONE (ADR); Notion posts deferred |

**Status legend**: 🔲 TODO · 🔄 IN PROGRESS · ✅ DONE · ❌ BLOCKED

---

## Gap Register

**GAP-1: No inner-DAG shared substrate exists today.**
- `apps_shared/integrations/governed_app_runner.py` is the outer DAG substrate; there is no equivalent for inner per-app workflows. Each app is on its own.

**GAP-2: apps_lic HOP domain logic is lost.**
- Git archaeology confirms: by commit `a4661c0009` ("consolidation pass 190→149 agents") the HOP1..HOP9 agents were already shims pointing to `HOPPipelineExecutor`. The original `_process` bodies are not recoverable from git history in any practical form.
- Consequence: Wave 2 engines must be **re-derived** from the 9 stage names + apps_lic domain requirements + apps_rg patterns. They are not a resurrection.

**GAP-3: apps_lic HOP stage semantics are under-specified.**
- Stage names exist (`profile_analysis`, `research`, `sender_grounding`, `routing`, `generation`, `validation`, `gate_decision`, `qa_report`, `integration`) but the input/output contract per stage is not documented anywhere. Wave 2.1 must author this.

**GAP-4: apps_rg config file mixes schemas with DAG topology.**
- `apps_rg/config/agent_spec_config.py:282-380` contains `HOP<N>Config` Pydantic classes alongside the `AgentSpec` registry. Wave 3 separates topology (→ `config/hop_pipeline.py`) from per-stage config schemas (remain in `agent_spec_config.py` but become `inputs:`/`outputs:` of each `HopStageSpec`).

**GAP-5: `GovernedLicRun` runs the outer chain but never invokes the HOP executor.**
- `apps_lic/integrations/governed_lic_run.py:136-176` calls `run_governed_core`; the L2 `authorize_and_execute` step does not dispatch to `HOPPipelineExecutor` today. Wave 2.5 wires the new orchestrator as the L2 body.

**GAP-6: No CI enforcement that future multi-hop apps adopt the canonical pattern.**
- Without a gate, the next multi-hop app will re-invent orchestration. Wave 4.2 adds `check_apps_hop_pipeline_location.py`.

---

## Execution Plan

### Wave 1 — Shared Substrate

#### Phase 1.1 — Draft `apps_shared/orchestration/hop_pipeline.py`

**Scope**: New module. Three public classes + module tests.

- `HopStageSpec` (frozen Pydantic): `stage_id: int`, `stage_name: str`, `engine_module: str`, `engine_class: str`, `inputs: list[str]`, `outputs: list[str]`, `required: bool`, `gate: bool` (true for evaluator-style gates), `optional_skip_if: str | None`.
- `HopRegistry`: per-app `dict[int, HopStageSpec]` + `register(spec)`, `get(stage_id)`, `ordered()`, `validate()` (no duplicate IDs, no circular `optional_skip_if` refs).
- `HopPipelineExecutor`: takes a `HopRegistry`, walks `ordered()`, lazy-imports each engine, calls `engine.execute(context) -> dict`, records per-stage checkpoint with `status` in {`COMPLETED`, `SKIPPED`, `FAILED`, `GATED`}, integrates with `apps_shared.adapters.system_learning_facade.seal_step` (pattern from `apps_lic/reasoning/HOPPipelineExecutor.py:253`), and returns `HopRunRecord` (frozen) carrying `checkpoints: tuple[Checkpoint, ...]` + `final_context: dict` + `terminal_error: str`.

**Layer gravity**: `apps_shared/orchestration/` imports from `agentic_core.runtime.contracts.lifecycle_trace_contract` (allowed — L_APP → agentic_core), no imports from any `apps_<name>/`. Apps depend on `apps_shared`, not the reverse.

**Acceptance**: module imports cleanly; `HopRegistry.validate()` rejects dup-ID and circular-skip; executor walks a 3-stage toy registry end-to-end; layer-gravity check `check_apps_shared_no_app_imports.py` passes.

#### Phase 1.2 — Unit tests + layer-gravity proof

**Scope**: `tests/unit/apps_shared/test_hop_pipeline.py`

- Registry dup-ID rejection
- Registry ordering (stage_id ascending, tie-break deterministic)
- Executor happy path (3-stage toy)
- Executor skip behavior (`optional_skip_if` evaluated against context)
- Executor gate behavior (gate=True + failing check → status=`GATED`, subsequent stages skipped)
- Executor failure path (engine raises → status=`FAILED`, terminal_error populated, no subsequent stages run)
- `seal_step` integration (mocked adapter)

**Acceptance**: ≥12 test cases passing; `pytest tests/unit/apps_shared/test_hop_pipeline.py -v` green.

### Wave 2 — apps_lic HOP Port

#### Phase 2.1 — Declare topology

**Scope**: `apps_lic/config/hop_pipeline.py`

Author the 9-stage `HopRegistry` for apps_lic:
1. profile_analysis → reads audience/compliance; outputs profile features
2. research → reads profile features + C0 retrieval results; outputs evidence bundle
3. sender_grounding → reads campaign config; outputs sender persona
4. routing → reads profile + evidence; routes to channel-specific generation prompt
5. generation → LLM draft generation (Qwen preferred, Gemini fallback)
6. validation → fact_check + hallucination_detect on draft
7. gate_decision (gate=True) → pass/refine decision
8. qa_report → scorecard + compliance annotations
9. integration → seal final `GovernedLicE2ERunRecord`

**Acceptance**: `HopRegistry.validate()` returns clean; stage_ids are contiguous 1..9; each `HopStageSpec` references an engine that will exist after Phase 2.2.

#### Phase 2.2 — Author 9 engine classes

**Scope**: `apps_lic/engines/profile_analysis_engine.py` … `apps_lic/engines/integration_engine.py`

Re-derive from:
- The 9 stage names (documented in the current stub registry)
- apps_rg engine patterns (`clerk_extraction_engine`, `data_enrichment_engine`, `fact_check_engine`, `hallucination_detector`, `content_optimizer_engine`, `generation_diagnostics_engine`)
- apps_lic domain artifacts: `lic_models_types.py`, `archetype_indicator_config.py`, `message_body_composer.py`, `CampaignRequest`/`GovernedLicE2ERunRecord`

Each engine exposes `execute(context: dict) -> dict`. Lifecycle-trace emits per the apps_rg pattern.

**Acceptance**: each engine importable; each has ≥1 unit test covering happy path; `HopPipelineExecutor` walks all 9 against a fixture `CampaignRequest` without exception.

#### Phase 2.3 — `LicCampaignOrchestrator` + heal rewire

**Scope**: `apps_lic/reasoning/LicCampaignOrchestrator.py` (NEW), `apps_lic/reasoning/LicHealingOrchestrator.py` (edit)

- `LicCampaignOrchestrator.run(context) -> HopRunRecord` — thin wrapper: load `HopRegistry` from `apps_lic/config/hop_pipeline.py`, instantiate `HopPipelineExecutor`, delegate.
- `LicHealingOrchestrator._heal_schema` — rewrite to call `HopPipelineExecutor.replay_stage(registry, stage_id, context)` (new shared-substrate method) instead of `HOPPipelineExecutor(stage_id=...).execute_stage(...)`. If single-stage replay is not needed operationally, **retire** the hook entirely with a deletion Author-Gate.

**Acceptance**: `LicCampaignOrchestrator` runs end-to-end on a fixture; `LicHealingOrchestrator._heal_schema` either works on new substrate or is deleted cleanly (no orphan callers).

#### Phase 2.4 — Retire dead surfaces

**Scope**: Deletions — requires constitutional §3 (no-agent-deletion without authorization) consideration; `HOPPipelineExecutor` is in `reasoning/`, named `Agent`-adjacent. Treat as operational cleanup (not an agent in the SovereignBaseAgent sense) but run `agent-deletion-gate` workflow to confirm.

- Delete `apps_lic/engines/hop_stage_registry.py` (9 stub functions + module trace emit).
- Delete `apps_lic/reasoning/HOPPipelineExecutor.py` OR leave as a 5-line shim re-exporting `apps_shared.orchestration.hop_pipeline.HopPipelineExecutor` for one release with `DeprecationWarning`.
- Update `apps_lic/utils/hop_stage_capability_util.py` if it referenced the executor shape.

**Acceptance**: zero remaining references to `hop_stage_registry` or the old `HOPPipelineExecutor` outside the optional shim; CI green.

#### Phase 2.5 — Wire into `GovernedLicRun`

**Scope**: `apps_lic/integrations/governed_lic_run.py`

The substrate's L2 `authorize_and_execute` step needs to invoke `LicCampaignOrchestrator.run(context)` so the HOP chain is actually exercised at runtime. Minimal surgery — inject the orchestrator call inside the L2 body or via the `ROUTING_TARGET=lic_campaign_assembly` handler registered in L0.

**Acceptance**: integration test running a full `CampaignRequest` through `GovernedLicRun.run_governed_e2e` shows 9 HOP checkpoints recorded in `GovernedLicE2ERunRecord.hop_checkpoints` (add this field to the record).

### Wave 3 — apps_rg Migration

#### Phase 3.1 — Extract stages into per-stage engines

**Scope**: Promote the `_process` logic currently inline in `RgResumeOrchestrator.run()` into discrete `apps_rg/engines/hop_<stage>_engine.py` files (HOP-0 JD validation → HOP-7 QA report). Many engine files already exist (`clerk_extraction_engine.py`, `data_enrichment_engine.py`, etc.) and just need a uniform `execute(context) -> dict` entry added.

#### Phase 3.2 — Declare topology, retire HOP<N>Config bloat

**Scope**: `apps_rg/config/hop_pipeline.py` (NEW) declares the `HopRegistry`. `apps_rg/config/agent_spec_config.py` keeps `ClerkExtractionConfig`, `EnrichmentConfig`, etc. as parameter schemas referenced by `HopStageSpec.config_class` — they are no longer the source of DAG topology, only per-stage knobs.

#### Phase 3.3 — Shrink orchestrator + parity tests

**Scope**: `RgResumeOrchestrator` collapses to `<30 lines` delegating to `HopPipelineExecutor`. Golden-output parity test: same `ResumeRequest` in → byte-identical (or normalized-JSON-identical) `GovernedRgE2ERunRecord` out, pre-migration vs post-migration.

**Acceptance**: parity test green; `apps_rg/reasoning/RgResumeOrchestrator.py` line count drops ≥400 lines; `apps_rg/config/agent_spec_config.py` drops ≥50 lines.

### Wave 4 — Consistency Gate + Underwriting Adoption

#### Phase 4.1 — apps_underwriting_ai adopt

**Scope**: The 5 engines (`document_reconciliation_engine`, `feature_derivation_engine`, `evidence_register_engine`, `decision_packet_assembler`, `underwriting_engine`) become a 5-stage `HopRegistry` at `apps_underwriting_ai/config/hop_pipeline.py`. Thin orchestrator at `apps_underwriting_ai/reasoning/UnderwritingOrchestrator.py`.

#### Phase 4.2 — CI gate: `check_apps_hop_pipeline_location.py`

**Scope**: `ops_scripts/ci/check_apps_hop_pipeline_location.py` (SSOT per `.windsurf/rules/ssot-folder-enforcement.md`).

Rules the gate enforces per `apps_*/` with an inner DAG:

1. `apps_<name>/config/hop_pipeline.py` exists and exports `REGISTRY: HopRegistry`.
2. Every `HopStageSpec.engine_module` referenced by the registry resolves to a real file under `apps_<name>/engines/`.
3. Exactly one `apps_<name>/reasoning/*Orchestrator.py` imports `apps_shared.orchestration.hop_pipeline.HopPipelineExecutor`.
4. No `apps_<name>/` file imports the old `hop_stage_registry` symbol.
5. Opt-out: apps declaring `route_type=build_time_compiler` in their spine_manifest (apps_qna) are exempt; apps declaring `route_type=R3_grounded_read` AND having ≥2 engines in `engines/` are in scope.

Wire into `.pre-commit-config.yaml` + `run_contract_gates.py`.

#### Phase 4.3 — ADR + writeback

**Scope**: `docs/architecture/adr/ADR-NNN-canonical-hop-pipeline-substrate.md` documenting the Author-Gate decision (recommended=shared_substrate, rejected=apps_rg_pattern / retire_apps_lic). Notion posts to ADR Registry + MCP Registry (if substrate changes any MCP-visible behavior).

---

## Rules

- **Layer gravity**: `apps_shared/orchestration/` imports only from `agentic_core` and stdlib — no `apps_<name>/` imports. Enforced by `check_apps_shared_no_app_imports.py`.
- **No grep for deps**: Wave 2.4 deletions consult ADG `adg_edge_fanin` on each symbol before removal (constitutional §22, §28).
- **Author-Gate for Phase 2.4 deletions**: `HOPPipelineExecutor.py` deletion runs `/agent-deletion-gate` workflow. If the class name is deemed agent-adjacent, follow 90-day deprecation (shim in Phase 2.4, hard delete in a follow-up plan).
- **SSOT folder routing**: new file locations follow `.windsurf/rules/ssot-folder-enforcement.md` (constitutional §31). CI gate auto-blocks drift.
- **Parity tests mandatory for apps_rg migration**: no silent behavior change. Golden-output test must pass pre- and post-migration.
- **Wave 2.1 under-specification risk**: if HOP stage semantics cannot be re-derived with high confidence, pause for Author-Gate (`architecture_choice`) on whether to descope apps_lic to a 4-stage minimum viable pipeline instead.

---

## Success Criteria

- [ ] `apps_shared/orchestration/hop_pipeline.py` lands with ≥12 passing unit tests and clean layer-gravity proof.
- [ ] `apps_lic/config/hop_pipeline.py` declares a validated 9-stage registry.
- [ ] 9 apps_lic stage engines exist, each with ≥1 unit test and an `execute(context)` entry.
- [ ] `GovernedLicRun.run_governed_e2e` runs end-to-end with 9 HOP checkpoints in `GovernedLicE2ERunRecord`.
- [ ] `apps_lic/engines/hop_stage_registry.py` deleted; no live references.
- [ ] `apps_rg/reasoning/RgResumeOrchestrator.py` drops ≥400 lines; golden-parity test green.
- [ ] `apps_rg/config/hop_pipeline.py` declares the 8-stage registry; `agent_spec_config.py` keeps only param schemas.
- [ ] `apps_underwriting_ai/config/hop_pipeline.py` declares a 5-stage registry; thin orchestrator lands.
- [ ] `ops_scripts/ci/check_apps_hop_pipeline_location.py` wired into pre-commit + contract gates; clean on HEAD.
- [ ] ADR-NNN published; Notion ADR Registry row posted; MCP Registry unchanged (no MCP impact).
- [ ] Zero new anti-pattern violations introduced (constitutional §8 burndown).
- [ ] Zero cross-layer import violations (ADG `v_p0_apps_direct_infra`, `v_p1_mis_layered_infra` clean).

---

## Implementation Commands

```bash
# Wave 1
python -m pytest tests/unit/apps_shared/test_hop_pipeline.py -v
python ops_scripts/ci/check_apps_shared_no_app_imports.py

# Wave 2
python -m pytest tests/unit/apps_lic/engines/ -v
python -m pytest tests/integration/apps_lic/test_governed_lic_run_hop_pipeline.py -v

# Wave 3
python -m pytest tests/golden/apps_rg/test_resume_generation_parity.py -v

# Wave 4
python ops_scripts/ci/check_apps_hop_pipeline_location.py
python ops_scripts/ci/run_contract_gates.py
python tools/generate_full_adg.py  # re-scan; confirm no new violations
```

---

## Rollback Strategy

Per-wave rollback — waves are independent once merged.

1. **Wave 1 rollback**: delete `apps_shared/orchestration/` and its tests. No downstream consumers yet, so zero-impact.
2. **Wave 2 rollback**: restore `apps_lic/engines/hop_stage_registry.py` + `apps_lic/reasoning/HOPPipelineExecutor.py` from git; revert `GovernedLicRun` wire-up. apps_lic returns to current "HOP machinery present but unused" state.
3. **Wave 3 rollback**: revert `RgResumeOrchestrator.py` + `agent_spec_config.py` to the pre-migration SHA. Parity tests remain the safety net.
4. **Wave 4 rollback**: revert underwriting adoption + remove CI gate. Other waves remain.

---

## Acceptance Criteria

| Metric | Target | Verification |
|---|---|---|
| apps_lic HOP checkpoints per campaign run | 9 | integration test asserts `len(record.hop_checkpoints) == 9` |
| apps_rg output parity post-migration | byte-identical or JSON-normalized identical | golden-output test |
| `apps_rg/reasoning/RgResumeOrchestrator.py` LOC | ≤100 (down from 606) | `wc -l` |
| Shared substrate reuse | 3 apps consume `HopPipelineExecutor` | `grep_search "from apps_shared.orchestration.hop_pipeline import"` |
| New anti-pattern violations | 0 | `python tools/generate_full_adg.py` diff |
| CI gate catches drift | true | intentional failing fixture → gate fails |

## Cascade Alignment Checks

- Keep always-on rules lean; place detailed procedures in skills or workflows.
- Retrieve local or scoped evidence before synthesis.
- Prefer exact or structural matches before broad semantic expansion.
- For high-risk outputs, extract evidence or quotes before summarizing.
- Reserve deterministic enforcement for hooks or scripts, not template prose.
