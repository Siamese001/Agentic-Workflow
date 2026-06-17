# apps_research — Autonomous Research Engine

Generates structured research artifacts from a topic + mode. Demonstrates autonomous synthesis, comparative analysis, and thought-leadership authoring — with **per-claim provenance** as a first-class output, not an afterthought.

## Design Patterns at Work

- **Source Register as Output Contract** — every artifact ships a `source_register_<trace_id>.json` with `source_id`, `title`, `claim_type`, `confidence`, `summary`, `section_id`. No claim is presented without its type label. **No unsupported assertions.**
- **Claim Typing** — every claim is one of `direct_evidence` | `interpretation` | `analyst_inference` | `assumption`. The boundary between observation and inference is an explicit field, not an editorial choice.
- **Mode-Driven Pipeline** — `brief` / `comparison` / `trend` / `position` / `thought_leadership` are first-class modes with mode-specific section schemas. The orchestrator is a state machine over modes, not a free-form prompt.
- **Final Evidence Contract (FEC)** — `apps_research/cert/fec_producer.py` populates `ExitReviewPacket.final_evidence_contract` with `producer="apps_research"`, `grounded`, `retrieval_sources` (auto-flips to `True` when `c0_retrieval_sources` populates upstream), `template_ids`, `route_id`, `evidence_sufficiency`.
- **ResearchGateValidator** — quality gates fire before emission: required sections present, no empty bodies, source register matches in-text citations, claim types attached.

## Consumer Brief Customization

The default `company_brief_synthesis_v1` path still produces the full research brief. For downstream reuse, `apps_research` now emits compact consumer-specific briefs with separate templates and section contracts:

| Consumer | Template | Primary Use | Shape |
|----------|----------|-------------|-------|
| `apps_rg` | `downstream_research_substrate_v1` | Delegated downstream research substrate for app logic | Compact signal-first output, roughly 1,600 chars, no more than 14 bullets, sections: Research Summary, Key Findings, Source Attributions, Confidence Assessment, Reuse Policy |
| `apps_lic` | `apps_lic_research_substrate_v1` | Outreach drafting, recipient positioning, and proof selection | Compact machine-friendly output, roughly 1,400 chars, no more than 12 bullets, sections: Research Summary, LIC Relevance, Key Findings, Source Attributions, Confidence Assessment, Reuse Policy |
| `apps_exec` | `apps_exec_executive_brief_v1` | Executive decision framing, operating pressure, leadership map, and positioning themes | Compact executive brief, roughly 1,800 chars, no more than 12 bullets, sections: Executive Summary, Company Strategy & Operating Pressure, Leadership & Stakeholder Map, AI/Data/Platform Signals, Recent Events & Urgency, Positioning Themes, Do Not Use As Proof |

Both consumer briefs treat the JD as data, preserve only verified company facts, and block with `BLOCKED: COMPANY_NOT_IDENTIFIABLE` when the company cannot be verified.

## Quick Start

```bash
# Generate a topic brief
python -m apps_research --topic "enterprise agentic AI governance" --mode brief

# Framework comparison
python -m apps_research --topic "agentic frameworks" --mode comparison \
  --compare "LangGraph,AutoGen,CrewAI"

# Thought leadership post
python -m apps_research --topic "constitutional governance in AI" --mode thought_leadership

# Dry run
python -m apps_research --topic "determinism contracts" --mode brief --dry-run
```

## Artifact Modes

| Mode                 | Output                                          | Key Sections                                |
|----------------------|-------------------------------------------------|---------------------------------------------|
| `brief`              | Topic brief with findings + implications        | executive_summary, key_findings, strategic  |
| `comparison`         | Framework comparison with matrix                | comparison_overview, matrix, recommendation |
| `trend`              | Trend scan with horizon analysis                | trend_overview, signal_analysis, horizon    |
| `position`           | Position memo with evidence + counterarguments  | position_statement, evidence, conclusion    |
| `thought_leadership` | LinkedIn / blog-style thought-leadership post   | hook, insight, evidence, call_to_action     |

## Source Register

Every artifact includes a source register (`source_register_<trace_id>.json`) with:

```json
{
  "source_id": "S07",
  "title": "Anthropic — Programmatic Tool Calling",
  "claim_type": "direct_evidence",
  "confidence": 0.92,
  "summary": "PTC reduces tool-call hallucination by enforcing schema contracts.",
  "section_id": "key_findings"
}
```

**Claim types:** `direct_evidence` | `interpretation` | `analyst_inference` | `assumption`

## Artifacts

All artifacts written to `reports/research/` by default:

- `research_<mode>_<trace_id[:8]>.md` — structured research artifact
- `source_register_<trace_id[:8]>.json` — full source register
- `run_summary_<trace_id[:8]>.json` — provenance + gate results

## Folder Structure

```
apps_research/
├── config/                  # Pydantic config: artifact modes, source register schema
│   ├── domain_contract/
│   ├── specs/
│   ├── agent_spec_config.py
│   └── cert_route_registry.yaml
├── engines/                 # ResearchAssemblyEngine, judges/, company_brief_engine
├── reasoning/               # ResearchOrchestrator
├── cert/                    # FEC producer (apps_research) + cert init
├── L6_observability/        # observability adapters
├── scripts/                 # run_research.py CLI
├── types/                   # research_types.py
├── validators/              # ResearchGateValidator
├── __init__.py
└── __main__.py
```

## Companion Docs

- `RUNBOOK.md` — on-call decision tree
- `SLO.md` — performance budgets
- `SVP_ENGINEERING_REVIEW.md` — architectural review
- `SPINE_ALIGNMENT_REPORT.md` — spine alignment + route claim
