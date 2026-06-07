# Technical Spec — apps_underwriting_ai

**Application:** apps_underwriting_ai (AI Underwriting Decision Pipeline)
**Spec Version:** 1.0.0 (skeleton stage)
**Last Updated:** 2026-05-02
**Companion docs:** `README.md` · `RUNBOOK.md` · `SLO.md` · `SVP_ENGINEERING_REVIEW.md` · `TEST_STRATEGY.md`

---

## 1. Architecture

### 1.1 Pipeline Topology

apps_underwriting_ai implements a **5-stage HOP pipeline** declared in `config/hop_pipeline.py` and driven equivalently by two orchestrators:

```
┌──────────────────────────────────────────────────────────────┐
│                   UnderwritingRequest                          │
└───────────────────┬────────────────────────────────────────┘
                    │
        ┌───────────▼────────────┐
        │  Stage 1: initialize_  │  EvidenceRegisterEngine.initialize
        │  evidence              │     → EvidenceRegister (empty)
        └───────────┬────────────┘
                    │
        ┌───────────▼────────────┐
        │  Stage 2: reconcile_   │  DocumentReconciliationEngine.reconcile
        │  documents             │     → ReconciliationResult
        └───────────┬────────────┘
                    │
        ┌───────────▼────────────┐
        │  Stage 3: derive_      │  FeatureDerivationEngine.derive_features
        │  features              │     → RiskFeatures
        └───────────┬────────────┘
                    │
        ┌───────────▼────────────┐
        │  Stage 4: collect_     │  EvidenceRegisterEngine.collect_*_evidence
        │  evidence (×5)         │     → updated EvidenceRegister
        └───────────┬────────────┘
                    │
        ┌───────────▼────────────┐
        │  Stage 5: assemble_    │  DecisionPacketAssembler.assemble
        │  decision              │     → DecisionPacket
        └───────────┬────────────┘
                    │
                    ▼
            UnderwritingResult
```

### 1.2 Two-Driver Equivalence

| Driver | Module | Style | Replay | Use case |
|---|---|---|---|---|
| `UnderwritingEngine` | `engines/underwriting_engine.py` | Imperative (sequential method calls) | ❌ | Default runtime path; matches sibling apps |
| `UnderwritingHopOrchestrator` | `reasoning/UnderwritingHopOrchestrator.py` | Declarative (HopPipelineExecutor over REGISTRY) | ✅ | Replay during incident healing; sub-pipeline composition |

Both produce semantically identical results from the same input.

### 1.3 Layer Alignment

| Layer | apps_underwriting_ai surface |
|---|---|
| **L0 Routing** | `ExecutionAdapter` integrates with the routing dispatch surface |
| **L1 Cognition** | `UnderwritingRequest` → `DecisionPacket` is the reasoning contract |
| **L2 Execution** | Stage engines enforce execution policy + invocation contract |
| **L3 Orchestration** | `UnderwritingHopOrchestrator` over `HopPipelineExecutor` |
| **L4 State** | `EvidenceRegister` append-only via `_append()`; frozen-dataclass discipline |
| **L5 Safety** | Reserved (`validators/` package — gate-violations enforcement, regulatory checks) |
| **L6 Observability** | `ObservabilityAdapter` emits `stage.start`/`stage.complete`/`decision.emitted` events |

---

## 2. Data Contracts

### 2.1 Frozen Dataclasses (`types/underwriting_types.py`)

| Type | Required Fields | Notes |
|---|---|---|
| `UnderwritingRequest` | `request_id`, `applicant_id`, `product_class` | Optional `documents` (tuple of dicts), `metadata` (dict) |
| `EvidenceRecord` | `evidence_id`, `source`, `kind` | `payload` is free-form dict |
| `EvidenceRegister` | `request_id` | `records` is an immutable tuple; mutation is via `EvidenceRegisterEngine._append()` returning a new register |
| `ReconciliationResult` | (none required) | `reconciled_count`, `unresolved_count`, `notes` tuple |
| `RiskFeatures` | (none required) | `feature_vector` (dict[str, float]), `derived_at` (str), `notes` tuple |
| `DecisionPacket` | `request_id`, `verdict` | `rationale`, `evidence_refs`, `feature_summary`, `gate_violations` |
| `UnderwritingResult` | `request_id`, `decision`, `register`, `features`, `reconciliation` | Optional `trace_id` |

### 2.2 Verdict Enum (`DecisionVerdict`)

| Value | Trigger |
|---|---|
| `APPROVE` | Evidence registered AND features derived AND zero unresolved documents |
| `DECLINE` | Reserved (real verdict logic TBD) |
| `REFER` | Any unresolved document reconciliation forces REFER |
| `INSUFFICIENT_EVIDENCE` | No evidence records AND no derived features |

The skeleton verdict heuristic lives in `engines/decision_packet_assembler.py::DecisionPacketAssembler.assemble()`. Real verdict logic replaces this method body (no other plumbing changes required).

### 2.3 Pipeline Stage Contract (`config/hop_pipeline.py`)

Every stage declares:
- `stage_id` (1-5)
- `stage_name` (snake_case)
- `engine_module` + `engine_class` (importable adapter)
- `inputs` (tuple of context keys consumed)
- `outputs` (tuple of context keys produced)
- `required` (bool)

The 5 hop adapters under `engines/hop_*_engine.py` satisfy the substrate's `execute(context, **kwargs) → dict` contract.

---

## 3. Integration Surfaces

### 3.1 Inbound

| Surface | Module | Use case |
|---|---|---|
| `ExecutionAdapter.execute(ExecutionRequest)` | `integrations/execution_adapter.py` | Runtime dispatch |
| `governed_underwriting_run(...)` | `integrations/governed_underwriting_run.py` | Convenience entrypoint with default construction |
| `UnderwritingIngressRunner.run_from_file(path)` | `integrations/underwriting_ingress_runner.py` | YAML/JSON file ingress |
| `python -m apps_underwriting_ai --request <path>` | `__main__.py` | CLI |
| `python -m apps_underwriting_ai --demo` | `__main__.py` | Synthetic smoke test |

### 3.2 Outbound

| Surface | Module | Use case |
|---|---|---|
| `DecisionRenderer.to_markdown(result)` | `outputs/decision_renderer.py` | Markdown output |
| `DecisionRenderer.to_json(result)` | `outputs/decision_renderer.py` | JSON output |
| `EnterpriseUnderwritingRenderer.render_to_disk(result)` | `outputs/enterprise_underwriting_renderer.py` | Audit-grade artifacts on disk |
| `SpineHandoff.package(result)` | `integrations/spine_handoff.py` | Spine-envelope packaging (R3_grounded_read) |
| `ObservabilityAdapter.emit_*` | `integrations/observability_adapter.py` | Structured event emission |

### 3.3 Spine Posture

`spine_manifest.yaml` declares `R3_grounded_read` — apps_underwriting_ai performs **no durable writes**. Pre-migration audit confirms zero matches for `CommitRequest`, `MutationIntent`, `write_gateway`, `policy_issue`, `loan_book`, etc.

Downstream consumers (policy issuance, loan booking) are responsible for any durable state changes.

---

## 4. Configuration

### 4.1 Spec File (`config/specs/agent_spec.underwriting.v1.0.0.yaml`)

```yaml
spec_version: "1.0.0"
agent_id: underwriting_decision_agent
capability_class: underwriting_decision
thresholds:
  min_evidence_records: 1
  max_unresolved_documents: 0
  require_feature_vector: true
metadata:
  app: apps_underwriting_ai
  pipeline_stages: [initialize_evidence, reconcile_documents, derive_features, collect_evidence, assemble_decision]
  spine_route: R3_grounded_read
```

Loaded via `config/agent_spec_config.py::load_spec(path) → UnderwritingAgentSpec`.

### 4.2 Domain Contract YAMLs (`config/domain_contract/*.yaml`)

15 inherited YAML files from prior scaffolding declaring app_domain_manifest, capability_profiles, eval_rubrics, fixtures, grader_roster, input_contract, negative_controls, orchestration_profiles, output_schema, prompt_profiles, retrieval_profiles, route_profiles, task_classes, threshold_profiles. Skeleton stage uses these as-is.

---

## 5. Skeleton Seams (real-domain replacement points)

The skeleton is structured so each "real-domain replaces this" surface is a single method body:

| Seam | Method to replace |
|---|---|
| Real reconciliation logic | `engines/document_reconciliation_engine.py::DocumentReconciliationEngine.reconcile` |
| Real feature derivation | `engines/feature_derivation_engine.py::FeatureDerivationEngine.derive_features` |
| Real verdict logic | `engines/decision_packet_assembler.py::DecisionPacketAssembler.assemble` |
| Real evidence collection (×5) | `engines/evidence_register_engine.py::EvidenceRegisterEngine.collect_{financial,credit,collateral,relationship,policy}_evidence` |
| Document parsers | `parsers/` (reserved package, currently empty) |
| Decision-packet validators | `validators/` (reserved package, currently empty) |

Replacing a seam requires no changes to the pipeline shape, the type contracts, or the integration adapters.

---

## 6. Error Model

| Failure | Surface | Behavior |
|---|---|---|
| Stage exception | Any stage engine raises | Pipeline halts; `ObservabilityAdapter` emits no `stage.complete` event; caller receives the exception |
| Insufficient evidence | `assemble_decision` heuristic | Verdict = `INSUFFICIENT_EVIDENCE`, decision packet still emitted |
| Unresolved reconciliation | `assemble_decision` heuristic | Verdict = `REFER` with unresolved-count rationale |
| Missing required field on inbound request | `UnderwritingIngressRunner.run_from_file` | Raises `ValueError` with the missing field name |
| Unsupported request file extension | `UnderwritingIngressRunner.run_from_file` | Raises `ValueError` |

The skeleton **never silently swallows** errors. All non-success paths surface a structured signal (verdict enum or exception).

---

## 7. Observability

`ObservabilityAdapter` emits structured events through Python's `logging` surface with `app=apps_underwriting_ai` extra. Events:

| Event | Fields |
|---|---|
| `stage.start` | `stage_name`, `request_id` |
| `stage.complete` | `stage_name`, `request_id`, `duration_ms` |
| `decision.emitted` | `request_id`, `verdict`, `evidence_count` |

Real OTEL wiring is layered on top by the `bootstrap_runtime` pattern from sibling apps when feature-complete logic lands.

---

## 8. Versioning

- **Spec version:** `1.0.0` (skeleton). Bumps when the pipeline shape, type contract, or integration surface changes incompatibly.
- **Pipeline stage IDs:** stable. New stages inserted in the middle bump the spec version.

---

## 9. References

- `config/hop_pipeline.py` — pipeline topology
- `apps_shared/orchestration/` — `HopRegistry`, `HopStageSpec`, `HopPipelineExecutor`, `Checkpoint`, `HopRunRecord`
- `agentic_core/runtime/contracts/lifecycle_trace_contract.py` — telemetry primitives
- Plan: `docs/archive/windsurf/legacy-tree/plans/apps-completeness-remediation-907fac.md` (skeleton build, completed 2026-05-02)
- Follow-up plan: `docs/archive/windsurf/legacy-tree/plans/apps-completeness-followups-287d2a.md` (this doc, contract tests, etc.)
