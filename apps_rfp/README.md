# apps_rfp — AI Proposal / RFP Generator

Generates complete AI platform proposals from a client problem statement. Demonstrates commercialization capability, solutioning discipline, and **enterprise proposal rigor with quality gates** — not free-form generation.

## Design Patterns at Work

- **Industry-Driven Defaults** — supported industries (`financial_services`, `healthcare`, `technology`, `government`) seed regulatory flags and architecture posture. The proposal inherits compliance context structurally, not by prompt.
- **ProposalAssemblyEngine + Section Contract** — the engine assembles a fixed-shape proposal: sections + roadmap + risk matrix + assumptions. Sections are typed, not free-text.
- **Quality Gates Before Emission** — `ProposalGateValidator` blocks emission when any of: required sections missing, empty section bodies, roadmap < 3 phases without Governance phase, empty risk matrix, unlabeled assumptions.
- **Final Evidence Contract (FEC)** — `apps_rfp/cert/fec_producer.py` populates the FEC with `rfp_sections_cited` as the retrieval-source key. Forward-compat: when C0 retrieval wires in, `grounded` flips to `True` automatically with no entry-point code change.
- **Exit Hook Adopted** — `apps_rfp/__main__.py` invokes `maybe_invoke_exit_eval` per `cert_route_registry.yaml` so per-app evaluator results gate the commit path.

## Quick Start

```bash
# Generate proposal for a technology company
python -m apps_rfp --brief "We need to automate document review with AI" --industry technology

# Financial services with sovereign architecture
python -m apps_rfp --brief "Compliance workflow automation" --industry financial_services --posture sovereign

# Dry run — plan but don't emit
python -m apps_rfp --brief-file input/client_brief.md --dry-run
```

## Pipeline

```
Problem Statement
    → ProposalAssemblyEngine (sections + roadmap + risk matrix + assumptions)
    → ProposalGateValidator (6 hard gates)
    → maybe_invoke_exit_eval (AppSpecificEvaluator + HITL routing)
    → FEC populate (cert/fec_producer)
    → Artifact Emission + RunSummary
```

## Supported Industries

| Industry             | Regulatory Flags          | Architecture Default |
|----------------------|---------------------------|----------------------|
| `financial_services` | SOX, GDPR, MiFID II       | sovereign            |
| `healthcare`         | HIPAA, FDA 21 CFR         | hybrid               |
| `technology`         | —                         | cloud-first          |
| `government`         | FedRAMP, FISMA, ITAR      | sovereign            |

## Quality Gates

- All 6 required sections present — **BLOCK** if any missing
- No empty section bodies — **BLOCK**
- Roadmap must have ≥ 3 phases including Governance — **BLOCK**
- Risk matrix non-empty — **BLOCK**
- All assumptions explicitly labeled — **BLOCK**
- Exit-eval verdict ≠ `deny` — **BLOCK**

## Artifacts

All artifacts written to `rfp/` by default:

- `proposal_<industry>_<trace_id[:8]>.md` — full structured proposal
- `proposal_manifest_<trace_id[:8]>.json` — section manifest + metadata
- `run_summary_<trace_id[:8]>.json` — provenance + gate results

## Folder Structure

```
apps_rfp/
├── config/                  # sections, industries, roadmap, gates
│   ├── domain_contract/
│   ├── specs/
│   └── cert_route_registry.yaml
├── engines/                 # ProposalAssemblyEngine, judges/, hop_proposal_assembly_engine
├── reasoning/               # RfpOrchestrator (multi-stage pipeline)
├── cert/                    # FEC producer + cert init
├── integrations/            # execution_adapter, governed_rfp_run
├── scripts/                 # run_rfp.py CLI
├── types/                   # rfp_types.py (frozen dataclasses, enums)
├── validators/              # ProposalGateValidator
├── __init__.py
└── __main__.py
```

## Companion Docs

- `RUNBOOK.md` — on-call decision tree
- `SLO.md` — performance budgets
- `SVP_ENGINEERING_REVIEW.md` — architectural review
