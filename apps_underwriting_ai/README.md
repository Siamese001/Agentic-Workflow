# apps_underwriting_ai — AI Underwriting Decision Pipeline

A 5-stage HOP pipeline that emits a structured underwriting decision packet from an applicant's request + supporting documents. **Zero-authority surface over `agentic_core`** — the app composes the runtime; it does not decide policy.

> **Maturity status (2026-05-02):** wired skeleton. The 5 pipeline stages and all canonical surfaces (engines / integrations / outputs / config / docs) are in place and run end-to-end. Real underwriting domain logic — actuarial scoring, regulatory checks, risk-tier mapping — is **out of scope** for this skeleton and lives behind well-defined seams. See `SVP_ENGINEERING_REVIEW.md` for the seam map.

## Focused production-grade slice: Submitted-Document Evidence Sufficiency Gate

> **Honesty note:** production-*grade* / client-*style*, built and tested against
> **synthetic** documents. No real customer deployment, no real PII, no real binding
> credit/insurance decision.

**What it does.** A deterministic gate (`UnderwritingC0Adapter`) that sits between intake
and decision/rationale assembly. It inspects submitted documents, checks required/optional
evidence coverage, extracts fields from submitted documents only (including falsy values like
`0`), assigns a deterministic, value-aware evidence ID to each field, computes an explainable
support score, detects contradictions (two cross-document rules + one intra-document
`CREDIT_REPORT` rule), and emits an immutable `FinalEvidenceContract`
(`PASS / WEAK_WITH_CAVEATS / FAIL`). `PASS` requires all required document classes present,
all required fields extracted, no contradictions, and `support_score >= 0.80`. Downstream
rationale generation must consume that contract; the LLM owns prose only and cannot change the
verdict or invent evidence — a **deterministic** citation allowlist (not a second LLM judge)
in the firewall rejects any rationale citing an evidence ID absent from the contract. The
`evidence_contract_id` is value-aware, so changing any submitted value changes the ID. It
fails closed on malformed/non-list input and never touches the open web.

**Run the focused demo / tests.**

```bash
# The anchor test suite for this slice (PASS, missing-required, contradictions,
# malformed input, determinism, no-open-web, no-inferred-fields, firewall guard):
python -m pytest tests/apps_underwriting_ai/test_c0_evidence_sufficiency_gate.py -v

# Pre-existing governance coverage for the same gate + firewall:
python -m pytest tests/governance/test_apps_underwriting_ai_c0.py tests/governance/test_apps_underwriting_ai_llm_firewall.py -v
```

Instantiate the gate directly from Python:

```python
from apps_underwriting_ai.integrations.underwriting_c0_adapter import UnderwritingC0Adapter

fec = UnderwritingC0Adapter().run(
    submitted_documents=[
        {"document_class": "BANK_STATEMENT", "average_monthly_balance": 8500.0, "account_tenure_months": 36},
        {"document_class": "TAX_RETURN", "annual_gross_income": 95000.0, "tax_year": 2025},
        {"document_class": "CREDIT_REPORT", "credit_score": 740, "derogatory_mark_count": 0},
    ],
    demo_policy_hash="sha256-demo-policy-standard-v1-aabbcc",
)
print(fec.c0_state, fec.support_score, fec.evidence_ids)
```

**Where the code lives.** Gate + `FinalEvidenceContract`: `integrations/underwriting_c0_adapter.py` ·
firewall: `integrations/underwriting_llm_firewall.py` · fixtures: `fixtures/c0_*_documents.yaml`.

**Where the case study lives.** `docs/EVIDENCE_SUFFICIENCY_GATE_CASE_STUDY.md` — interview-ready
write-up (business problem, data contract, scoring, contradiction rules, failure modes,
production controls, 90-second + 5-minute talk track, 15 Q&A pairs).

## Design Patterns at Work

- **Imperative + Declarative Twin Drivers** — the **same** 5-stage pipeline ships in two forms: an imperative `UnderwritingEngine.run(request)` for direct use, and a declarative `UnderwritingHopOrchestrator.run(context)` over the shared `HopPipelineExecutor` with replay support. They are interchangeable; tests prove parity.
- **Frozen Dataclass Contracts** — `types/underwriting_types.py` is `@dataclass(frozen=True)` end-to-end. `UnderwritingRequest`, `DecisionPacket`, evidence + feature shapes are immutable, hashable, and reproducible.
- **Evidence Register + Decision Packet Assembler** — `EvidenceRegisterEngine` accumulates evidence with provenance; `DecisionPacketAssembler` projects the register into `verdict / rationale / evidence_refs / feature_summary` — separating evidence accumulation from decision projection.
- **Rubric Output Mapper** — `engines/rubric_output_mapper.py:map_decision_to_dim_scores` projects a `DecisionPacket` into 5-dim `output.dim_scores` consumed by the v6 Exit `AppSpecificEvaluator`. The mapper is the seam between domain and harness.
- **Cert + Exit Hook Adopted** — `__main__.py` imports `apps_underwriting_ai.cert` (registers FEC producer side-effect) and invokes `maybe_invoke_exit_eval` per `cert_route_registry.yaml`. Parser-provenance source ladder feeds `retrieval_sources`.
- **HOP-Substrate Adapters** — `engines/hop_*.py` bridge the imperative engines to the declarative HOP topology. One source of truth (the registry); two ways to walk it.
- **Holdout Schema** — `holdout/holdout_schema.yaml` defines the structured release-gate eval set. Read by release-gate CI only.

## Quick Start

```bash
# Demo run (deterministic synthetic request, no inputs required)
python -m apps_underwriting_ai --demo

# Run against a YAML request file
python -m apps_underwriting_ai --request input/request.yaml --artifact-dir underwriting_artifacts/
```

## Pipeline

```
UnderwritingRequest
    → 1. initialize_evidence       (EvidenceRegisterEngine.initialize)
    → 2. reconcile_documents       (DocumentReconciliationEngine.reconcile)
    → 3. derive_features           (FeatureDerivationEngine.derive_features)
    → 4. collect_evidence          (EvidenceRegisterEngine.collect_*_evidence)
    → 5. assemble_decision         (DecisionPacketAssembler.assemble)
    → DecisionPacket (verdict, rationale, evidence_refs, feature_summary)
    → rubric_output_mapper → output.dim_scores
    → maybe_invoke_exit_eval (AppSpecificEvaluator + HITL routing)
    → FEC populate (cert/fec_producer)
    → enterprise_underwriting_renderer → disk emission
```

Two equivalent drivers walk this pipeline:

- **Imperative:** `apps_underwriting_ai.engines.UnderwritingEngine.run(request)` — direct, sequential.
- **Declarative:** `apps_underwriting_ai.reasoning.UnderwritingHopOrchestrator.run(context)` — uses shared `HopPipelineExecutor`, supports replay.

## Decision Verdicts

| Verdict | Meaning |
|---|---|
| `APPROVE` | Evidence sufficient, features derived, no unresolved documents |
| `DECLINE` | (Reserved — real verdict logic TBD) |
| `REFER` | Unresolved document reconciliations require manual review |
| `INSUFFICIENT_EVIDENCE` | No evidence registered AND no features derived |

## Folder Structure

```
apps_underwriting_ai/
├── config/
│   ├── agent_spec_config.py             # Pydantic config + spec loader
│   ├── domain_contract/                 # 15 domain-contract YAML configs (active)
│   ├── hop_pipeline.py                  # 5-stage HOP topology (REGISTRY)
│   ├── cert_route_registry.yaml         # exit-eval invocation flag
│   └── specs/agent_spec.underwriting.v1.0.0.yaml
├── engines/
│   ├── base_underwriting_engine.py
│   ├── underwriting_engine.py           # Imperative driver
│   ├── evidence_register_engine.py      # Stage 1 + 4
│   ├── document_reconciliation_engine.py # Stage 2
│   ├── feature_derivation_engine.py     # Stage 3
│   ├── decision_packet_assembler.py     # Stage 5
│   ├── rubric_output_mapper.py          # DecisionPacket → dim_scores
│   ├── hop_*.py                         # 5 HOP-substrate adapters
│   └── judges/                          # per-rubric LLM judge stubs
├── integrations/
│   ├── execution_adapter.py             # Runtime handoff
│   ├── governed_underwriting_run.py     # Convenience entrypoint
│   ├── underwriting_ingress_runner.py   # File-based ingress
│   ├── observability_adapter.py         # Structured event emission
│   └── spine_handoff.py                 # Spine envelope packaging
├── outputs/
│   ├── decision_renderer.py             # JSON / Markdown
│   └── enterprise_underwriting_renderer.py  # Disk emission
├── reasoning/
│   └── UnderwritingHopOrchestrator.py   # Declarative driver
├── cert/                                # FEC producer + cert init
├── parsers/                             # document parsers (active seam)
├── holdout/                             # release-gate eval schema
├── validators/                          # decision validators
├── tests/                               # in-app tests
├── types/underwriting_types.py          # Frozen dataclass contracts
├── __init__.py
├── __main__.py                          # CLI entrypoint
└── AGENTIC_SPINE.md
```

## Companion Docs

- `AGENTIC_SPINE.md` — spine alignment + route claim
- `RUNBOOK.md` — on-call decision tree
- `SLO.md` — service level objectives
- `SVP_ENGINEERING_REVIEW.md` — architectural review + seam map for real-domain layering
- `THREAT_MODEL.md` — external-input threat surface (request YAML, document parsers)
- `holdout/holdout_schema.yaml` — release-gate eval schema
