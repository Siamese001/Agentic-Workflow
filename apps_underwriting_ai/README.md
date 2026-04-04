# Apps Underwriting AI

A production-grade commercial credit underwriting decision-support domain app built as a zero-authority surface over `agentic_core`.

## Overview

`apps_underwriting_ai` is an enterprise commercial credit underwriting accelerator that packages business workflow, domain schemas, feature derivation, reasoning, validation, and artifact generation while delegating sovereign concerns (routing, governance, execution, evaluation, replay, meta-learning, persistence) to `agentic_core`.

### What It Does

Given a credit request package, this app determines whether to:
- **APPROVE** - Request meets all policy criteria
- **APPROVE_WITH_CONDITIONS** - Acceptable with mitigants
- **COUNTER_OFFER** - Acceptable only with revised terms
- **PEND_FOR_INFORMATION** - Decision pending additional data
- **DECLINE** - Request does not meet criteria
- **ESCALATE_TO_HUMAN** - Requires human underwriter review

### Domain Coverage

- **Structured Input Ingestion**: JSON, CSV, XLSX mapping to canonical schema
- **Document Processing**: PDF financials, bank statements, appraisals, aging schedules
- **Feature Derivation**: DSCR, leverage, liquidity, collateral coverage, credit scores
- **Risk Reasoning**: Strengths, risks, open questions, hypothesis generation
- **Policy Validation**: Compliance, authority limits, forbidden feature checking
- **Decision Assembly**: Conditions, covenants, counter-offers, escalation logic
- **Artifact Generation**: Decision memos, audit trails, evidence registers

## Architecture

### Zero-Authority Domain App

`apps_underwriting_ai` is explicitly NOT:
- ❌ A replacement for L0 routing
- ❌ A replacement for L5 safety/governance
- ❌ A replacement for L2 execution authority
- ❌ A replacement for L4 persistence authority
- ❌ A replacement for Evaluation Spine

`apps_underwriting_ai` IS:
- ✅ A domain-specific intent producer
- ✅ A typed schema provider
- ✅ A feature derivation engine
- ✅ A business logic validator
- ✅ An artifact packager
- ✅ A core integration layer

### Integration Handoff

```
┌─────────────────────────┐     ┌─────────────────────────┐
│  apps_underwriting_ai   │────▶│      agentic_core      │
│                         │     │                         │
│  - Domain Request       │     │  - L0 Routing           │
│  - Risk Features        │     │  - L5 Governance        │
│  - Recommendation       │     │  - L2 Execution         │
│  - Evidence Register    │     │  - L4 Persistence       │
│  - Audit Trail          │     │  - L6 Observability     │
└─────────────────────────┘     └─────────────────────────┘
```

## Installation

```bash
# Requires Python 3.10+
pip install pydantic pyyaml

# Optional for document parsing
pip install openpyxl  # For XLSX ingestion
```

## Quick Start

```python
from apps_underwriting_ai import UnderwritingEngine, UnderwritingRequest

# Load request from JSON/dict
request_data = {...}  # Your underwriting request
request = UnderwritingRequest(**request_data)

# Run underwriting workflow
engine = UnderwritingEngine()
result = engine.run(request)

# Access outputs
print(f"Decision: {result.decision}")
print(f"Confidence: {result.confidence_score:.0%}")
print(f"Memo: {result.decision_memo}")
```

## Input Contracts

### UnderwritingRequest

Primary request structure containing:
- **Borrower Profile**: Entity info, ownership, industry
- **Financial Package**: Periods, calculated metrics
- **Collateral Package**: Type, value, LTV
- **Credit Package**: Scores, derogatories
- **Banking Package**: Deposits, NSFs
- **Document Package**: Document references
- **Policy Context**: Thresholds, restrictions
- **Decision Constraints**: SLA, authority limits

See `examples/sample_underwriting_request.json` for full example.

## Output Contracts

### DecisionMemo

Human-readable underwriting recommendation with:
- Recommended decision
- Conditions precedent
- Ongoing covenants
- Key strengths and risks
- Policy exceptions
- Evidence register

### DecisionPacket

Machine-readable output for downstream systems:
- Decision state
- Recommended structure
- Pricing adjustments
- Exception flags
- Confidence score

### AuditTrace

Compliance and replay record:
- Derived features snapshot
- Evidence references
- Validators executed
- Human review triggers

## Configuration

Policy and thresholds defined in `config/`:

- `underwriting_required_docs.yaml` - Document requirements by product
- `underwriting_thresholds.yaml` - DSCR, leverage, FICO thresholds
- `covenant_templates.yaml` - Standard covenants by risk profile
- `policy_exception_rules.yaml` - Exception approval requirements
- `product_rules.yaml` - Product-specific rules
- `prohibited_features.yaml` - Forbidden attributes
- `industry_risk_weights.yaml` - NAICS-based risk scores

## Testing

```bash
# Run all tests
python -m pytest apps_underwriting_ai/tests/

# Run specific test file
python -m pytest apps_underwriting_ai/tests/test_underwriting_engine.py
```

## Project Structure

```
apps_underwriting_ai/
├── types/              # Pydantic domain models
├── ingestion/          # JSON/CSV/XLSX mappers, document ingestion
├── engines/           # Reconciliation, feature derivation, decision assembly
├── reasoning/         # Hypothesis building, interpreters, recommenders
├── validators/        # Compliance, forbidden features, authority, contradictions
├── parsers/           # Financial statement, debt schedule, aging parsers
├── integrations/      # Core, retrieval, policy, observability adapters
├── outputs/           # Memo, packet, audit renderers
├── config/            # YAML policy and threshold configurations
├── examples/          # Sample request and decision payloads
└── tests/             # Unit and scenario tests
```

## Key Design Principles

1. **Deterministic Logic**: All underwriting rules are explicit and inspectable
2. **Evidence-Based**: Every claim is linked to source documentation or metrics
3. **Policy-Compliant**: Built-in checks for thresholds, restrictions, exceptions
4. **Fair and Explainable**: Forbidden feature checking ensures compliance with fair lending
5. **Audit-Ready**: Complete trace of features, validators, and decision rationale

## Limitations

- Document parsing relies on external OCR/extraction services (not included)
- Industry risk weights require periodic recalibration
- Counter-party and concentration analysis requires supplemental data feeds
- Real-time market signals are placeholder integrations

## License

Enterprise - See LICENSE file

## Support

For questions or issues, contact the agentic_core team.
