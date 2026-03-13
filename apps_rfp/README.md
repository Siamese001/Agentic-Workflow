# apps_rfp — AI Proposal / RFP Generator

Generates complete AI platform proposals from a client problem statement.
Demonstrates commercialization capability, solutioning discipline, and enterprise proposal rigor.

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
Problem Statement → ProposalAssemblyEngine (sections + roadmap + risk matrix + assumptions)
                 → ProposalGateValidator → Artifact Emission → RunSummary
```

## Supported Industries

| Industry            | Regulatory Flags         | Architecture Default |
|---------------------|--------------------------|----------------------|
| `financial_services`| SOX, GDPR, MiFID II      | sovereign            |
| `healthcare`        | HIPAA, FDA 21 CFR        | hybrid               |
| `technology`        | —                        | cloud-first          |
| `government`        | FedRAMP, FISMA, ITAR     | sovereign            |

## Artifacts

All artifacts written to `rfp/` by default:

- `proposal_<industry>_<trace_id[:8]>.md` — full structured proposal
- `proposal_manifest_<trace_id[:8]>.json` — section manifest + metadata
- `run_summary_<trace_id[:8]>.json` — provenance + gate results

## Quality Gates

- All 6 required sections present — BLOCK if any missing
- No empty section bodies — BLOCK
- Roadmap must have ≥ 3 phases including Governance — BLOCK
- Risk matrix non-empty — BLOCK
- All assumptions explicitly labeled

## Folder Structure

```
apps_rfp/
├── config/           # Pydantic config: sections, industries, roadmap, gates
├── engines/          # ProposalAssemblyEngine
├── reasoning/        # RfpOrchestrator (multi-stage pipeline)
├── scripts/          # run_rfp.py CLI
├── types/            # rfp_types.py (frozen dataclasses, enums)
├── utils/
├── validators/       # ProposalGateValidator
├── __init__.py
└── __main__.py
```
