# SVP Engineering Review — apps_underwriting_ai

**Application:** apps_underwriting_ai (AI Underwriting Decision Pipeline)
**Review Date:** 2026-05-02
**Status:** Skeleton complete — wired and operable; real-domain logic deliberately deferred
**Test Pass Rate:** smoke test passing (see `tests/test_smoke.py`); contract tests pending feature-complete stage

---

## What's Specifically Hard About This Domain

apps_underwriting_ai produces underwriting decisions — adjudications that determine whether an applicant gets credit, insurance, or a financial product, and at what terms. That sets a unique engineering bar:

1. **Every decision must trace to evidence.** An APPROVE with no evidence record is structurally indefensible to a regulator. The DecisionPacketAssembler enforces evidence-bound verdicts.
2. **REFER is a first-class outcome, not a fallback.** Unresolved document reconciliations should stop the pipeline cleanly and route to manual review — never silently approve.
3. **Auditability outweighs latency.** Underwriting decisions feed regulatory audit trails for years; sub-second latency is not the SLO, traceable rationale is.
4. **Domain logic is replaceable; pipeline shape is not.** The 5-stage HOP shape (initialize → reconcile → derive → collect → assemble) is the architectural commitment. Real domain logic plugs into the existing seams.

This drives the architecture: two equivalent drivers (imperative `UnderwritingEngine` + declarative `UnderwritingHopOrchestrator`) over a shared stage registry; frozen-dataclass evidence register with explicit append semantics; `DecisionVerdict` enum-bounded outputs; minimal but functional skeleton implementations of every stage so the pipeline is fully exercisable from day one.

## Skeleton Boundary (what's deliberately NOT here)

The skeleton intentionally omits:

- **Actuarial / risk-tier scoring.** `FeatureDerivationEngine` emits a deterministic skeleton vector. Real scoring plugs in here.
- **Document OCR / structured-document parsing.** `parsers/` package is reserved.
- **Regulatory compliance checks.** `validators/` package is reserved.
- **Real verdict logic.** `DecisionPacketAssembler.assemble()` uses a deterministic placeholder heuristic. Real logic replaces this method body.
- **Real evidence collection.** `EvidenceRegisterEngine.collect_*_evidence` methods append skeleton records. Real adapters replace each method body.

These are **seams**, not gaps — the skeleton is wired such that swapping any single method for feature-complete logic does not require touching the pipeline shape.

## Non-Goals (deliberately out of scope)

- **Bind-and-issue / policy issuance.** Out of scope — apps_underwriting_ai produces the decision packet; downstream systems issue policies/loans.
- **Pricing / quote generation.** Different workflow.
- **Fraud detection signals.** Reserved for a sibling app.
- **Self-improving verdict optimization.** Underwriting must be auditable — autonomous verdict optimization would invite regulatory and Goodhart-law issues.

## Alternatives Considered (and rejected)

### Alternative 1: Single monolithic `UnderwritingAgent` class
**Rejected:** monolithic agents diverge from per-stage rigor. The 5-stage HOP shape gives every concern a dedicated, replayable surface.

### Alternative 2: Implement real domain logic up front
**Rejected:** real underwriting domain logic requires actuarial sign-off, regulatory review, and SME engagement. Shipping a wired skeleton that exercises the full pipeline shape unblocks every downstream consumer (integration tests, observability wiring, spine handoff verification) without taking on premature domain-logic debt.

### Alternative 3: Heavy lifecycle-trace shim package matching apps_rfp
**Rejected:** `apps_rfp/_compat/lifecycle_trace.py` mirrors 60+ telemetry shim functions. For a skeleton, this is friction without value. apps_underwriting_ai imports lifecycle telemetry directly from `agentic_core.runtime.contracts.lifecycle_trace_contract` where needed — feature-complete stage will revisit if the shim becomes warranted.

## Architectural Differentiation From Peer Apps

apps_underwriting_ai is the only app with:
- **Two equivalent pipeline drivers** over the same stage registry (imperative + declarative)
- **Frozen-dataclass evidence register with explicit `_append()` semantics** (no in-place mutation, audit-trivial)
- **`DecisionVerdict` enum-bounded outputs** (only 4 verdicts, no string drift)

apps_underwriting_ai is the only app where **the pipeline shape is the architectural commitment** and domain logic is treated as plug-in.

## SVP Standards Compliance

### 1. Domain Contracts (frozen dataclasses)

| Component | Status | Notes |
|-----------|--------|-------|
| UnderwritingRequest | ✅ | Frozen dataclass, request_id + applicant_id + product_class + documents + metadata |
| EvidenceRegister | ✅ | Frozen, append-only via `_append()` |
| EvidenceRecord | ✅ | Frozen, evidence_id + source + kind + payload |
| ReconciliationResult | ✅ | Frozen, reconciled_count + unresolved_count + notes |
| RiskFeatures | ✅ | Frozen, feature_vector + derived_at + notes |
| DecisionPacket | ✅ | Frozen, verdict + rationale + evidence_refs + feature_summary + gate_violations |
| UnderwritingResult | ✅ | Top-level result, frozen, aggregates all stage outputs |
| DecisionVerdict | ✅ | str-enum, 4 bounded values |

### 2. Integration Adapters

| Adapter | Integration |
|---------|-------------|
| ExecutionAdapter | Runtime handoff (mirrors apps_rfp) |
| governed_underwriting_run | Convenience entrypoint with default construction |
| UnderwritingIngressRunner | YAML/JSON file-based ingress |
| ObservabilityAdapter | Structured event emission |
| SpineHandoff | Spine envelope packaging (R3_grounded_read) |

### 3. Output Renderers

| Renderer | Formats | Purpose |
|----------|---------|---------|
| DecisionRenderer | JSON, Markdown | In-memory rendering |
| EnterpriseUnderwritingRenderer | Markdown + JSON to disk | Audit-grade artifacts |

### 4. Configuration

| Config File | Purpose |
|-------------|---------|
| `config/agent_spec_config.py` | Pydantic schema + spec loader |
| `config/specs/agent_spec.underwriting.v1.0.0.yaml` | v1.0.0 agent spec |
| `config/hop_pipeline.py` | 5-stage HOP topology (REGISTRY) |
| `config/domain_contract/*.yaml` | 15 domain-contract files (input/output/eval/etc.) |

---

## Architecture Rigor

### Layer Alignment
- **L0 Routing:** ExecutionAdapter integrates with the routing surface
- **L1 Cognition:** UnderwritingRequest → DecisionPacket as reasoning contract
- **L2 Execution:** Stage engines enforce execution policy
- **L3 Orchestration:** UnderwritingHopOrchestrator over HopPipelineExecutor
- **L4 State:** EvidenceRegister append-only, frozen-dataclass discipline
- **L6 Observability:** ObservabilityAdapter emits structured events

### Key Design Principles

1. **Zero in-place evidence mutation:** the register is frozen; `_append()` returns a new register
2. **Evidence-bound verdicts:** every APPROVE traces to ≥1 evidence record
3. **REFER-on-unresolved:** unresolved reconciliations force REFER, never silently approve
4. **Two equivalent drivers:** imperative + declarative produce identical results
5. **Plug-in seams:** every stage method has a documented "real-domain replaces this body" contract

---

## Production Readiness

| Criterion | Status |
|-----------|--------|
| Type Safety | ✅ Frozen dataclasses + Pydantic config |
| Error Handling | ✅ Explicit verdicts (no silent None returns) |
| Observability | ✅ ObservabilityAdapter wired |
| Configurability | ✅ YAML configs + Pydantic loader |
| Documentation | ✅ This review + README + RUNBOOK + SLO |
| Test Coverage | 🟡 Smoke test in place; full contract tests pending feature-complete |
| Domain Logic Maturity | 🟡 Skeleton — feature-complete is a separate scope |

---

## SVP Engineering Standards Checklist

- [x] Frozen-dataclass contracts with explicit fields
- [x] Explicit verdicts (no silent None returns)
- [x] Append-only evidence register (audit-friendly)
- [x] Integration adapters for system handoff
- [x] HOP pipeline shape codified in registry
- [x] YAML configuration + Pydantic loader
- [x] Two equivalent pipeline drivers (imperative + declarative)
- [x] Bounded verdict set (DecisionVerdict enum)
- [x] Companion docs (README, RUNBOOK, SLO, SVP review)
- [x] CLI entrypoint with `--demo` smoke test
- [ ] Feature-complete domain logic (deliberately out of scope at skeleton stage)
- [ ] Full contract test suite (deliberately out of scope at skeleton stage)

---

**Approved for Skeleton-Stage Use**
*SVP Engineering Quality Certification — 2026-05-02*

Skeleton certification means: every canonical surface is wired and exercisable; the pipeline shape is the architectural commitment; real domain logic is a deferred concern with documented seams.
