# apps_research — Autonomous Research Engine

Generates structured research artifacts from a topic and mode.
Demonstrates autonomous synthesis, comparative analysis, and thought leadership authoring.

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

| Mode               | Output                                          | Key Sections                               |
|--------------------|-------------------------------------------------|--------------------------------------------|
| `brief`            | Topic brief with findings + implications        | executive_summary, key_findings, strategic |
| `comparison`       | Framework comparison with matrix                | comparison_overview, matrix, recommendation|
| `trend`            | Trend scan with horizon analysis                | trend_overview, signal_analysis, horizon   |
| `position`         | Position memo with evidence + counterarguments  | position_statement, evidence, conclusion   |
| `thought_leadership`| LinkedIn/blog-style thought leadership post   | hook, insight, evidence, call_to_action    |

## Source Register

Every artifact includes a source register (`source_register_<trace_id>.json`) with:
- `source_id`, `title`, `claim_type`, `confidence`, `summary`, `section_id`

**Claim types:** `direct_evidence` | `interpretation` | `analyst_inference` | `assumption`

No claim is presented without its type label. No unsupported assertions.

## Artifacts

All artifacts written to `reports/research/` by default:

- `research_<mode>_<trace_id[:8]>.md` — structured research artifact
- `source_register_<trace_id[:8]>.json` — full source register
- `run_summary_<trace_id[:8]>.json` — provenance + gate results

## Folder Structure

```
apps_research/
├── config/           # Pydantic config: artifact modes, source register schema
├── engines/          # ResearchAssemblyEngine
├── reasoning/        # ResearchOrchestrator
├── scripts/          # run_research.py CLI
├── types/            # research_types.py
├── utils/
├── validators/       # ResearchGateValidator
├── __init__.py
└── __main__.py
```
