# apps_underwriting_ai — AI Underwriting Decision Pipeline

5-stage HOP pipeline that emits a structured underwriting decision packet from an applicant's request + supporting documents.

> **Maturity status (2026-05-02):** wired skeleton. The 5 pipeline stages and all canonical surfaces (engines / integrations / outputs / config / docs) are in place and run end-to-end. Real underwriting domain logic — actuarial scoring, regulatory checks, risk-tier mapping — is **out of scope** for this skeleton and lives behind well-defined seams. See `SVP_ENGINEERING_REVIEW.md` for the seam map.

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
│   ├── domain_contract/                 # 15 domain-contract YAML configs
│   ├── hop_pipeline.py                  # 5-stage HOP topology (REGISTRY)
│   └── specs/
│       └── agent_spec.underwriting.v1.0.0.yaml
├── engines/
│   ├── base_underwriting_engine.py
│   ├── underwriting_engine.py           # Imperative driver
│   ├── evidence_register_engine.py      # Stage 1 + 4
│   ├── document_reconciliation_engine.py # Stage 2
│   ├── feature_derivation_engine.py     # Stage 3
│   ├── decision_packet_assembler.py     # Stage 5
│   └── hop_*.py                         # 5 HOP-substrate adapters
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
├── parsers/                             # (Reserved) document parsers
├── validators/                          # (Reserved) decision validators
├── tests/                               # (Reserved) in-app tests
├── types/
│   └── underwriting_types.py            # Frozen dataclass contracts
├── __init__.py
├── __main__.py                          # CLI entrypoint
├── README.md (this file)
├── RUNBOOK.md
├── SLO.md
└── SVP_ENGINEERING_REVIEW.md
```

## Companion Docs

- `RUNBOOK.md` — on-call decision tree
- `SLO.md` — service level objectives
- `SVP_ENGINEERING_REVIEW.md` — architectural review + seam map for real-domain layering
