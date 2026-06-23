# PRODUCT SPEC — apps_research: Autonomous Research Engine

## Product Intent

`apps_research` generates structured research artifacts from a topic and a mode.
It demonstrates autonomous synthesis capability — the ability to take a topic,
select the appropriate artifact type, assemble evidence-grounded content, and
produce a publication-quality output with explicit claim-type labeling.

The app proves that the platform owner can build systems that produce thought leadership,
not just infrastructure — and that those systems are transparent about what is evidence,
what is interpretation, and what is analyst inference.

---

## Primary Users

| User Persona         | Goal                                                            | Success Signal                                  |
|----------------------|-----------------------------------------------------------------|-------------------------------------------------|
| **AI Platform Lead** | Quickly synthesize the state of a topic for internal briefing  | Brief ready for distribution in < 30 seconds   |
| **Solutions Team**   | Generate a framework comparison for a client conversation      | Structured comparison matrix with recommendation|
| **Thought Leader**   | Draft a position memo or LinkedIn post grounded in evidence    | Post-quality content with labeled claim types  |
| **Portfolio Reviewer**| See evidence of research and synthesis capability             | Labeled sources, structured claims, modes       |

---

## Core User Stories

1. **As an AI platform lead,** I want to get a 3-section brief on a topic so I can share it
   with stakeholders without researching it from scratch.
2. **As a solutions team member,** I want to compare agentic frameworks side-by-side on
   governance, determinism, and enterprise readiness.
3. **As a thought leader,** I want a draft position memo with a clear statement, supporting
   evidence, and counterarguments labeled by claim type.
4. **As a portfolio reviewer,** I want every claim in every artifact to be labeled with its
   epistemic type so I can judge confidence levels.

---

## Artifact Modes

| Mode                | Description                                          | Required Sections                                   |
|---------------------|------------------------------------------------------|-----------------------------------------------------|
| `brief`             | Topic brief for internal use                         | executive_summary, key_findings, strategic_implications |
| `comparison`        | Framework/vendor comparison with matrix              | comparison_overview, comparison_matrix, recommendation |
| `trend`             | Trend scan with signal analysis                      | trend_overview, signal_analysis, horizon_implications |
| `position`          | Position memo for external publication               | position_statement, supporting_evidence, counterarguments, conclusion |
| `thought_leadership`| LinkedIn/blog-style post with hook and CTA           | hook, insight, evidence, call_to_action             |

---

## Inputs

| Input          | Type           | Required | Description                                          |
|----------------|----------------|----------|------------------------------------------------------|
| `--topic`      | str            | Yes      | Research topic or question                           |
| `--mode`       | Enum           | No       | Artifact mode (default: `brief`)                     |
| `--audience`   | Enum           | No       | `technical`, `executive`, `market-facing`            |
| `--compare`    | List[str]      | No       | Comparison subjects (for `comparison` mode)          |
| `--horizon`    | str            | No       | Time horizon (e.g. "12 months") for `trend` mode     |
| `--out`        | Path           | No       | Output directory (default: `artifacts/apps_research/`) |
| `--dry-run`    | Flag           | No       | Plan; do not emit artifacts                          |

**Rejected inputs:**
- Empty topic string rejected at parse time.
- `--compare` with no subjects in `comparison` mode: falls back to default framework list.

---

## Outputs

| Artifact                                    | Format | Description                                  |
|---------------------------------------------|--------|----------------------------------------------|
| `research_<mode>_<trace_id[:8]>.md`         | Markdown | Structured research artifact with labeled claims |
| `source_register_<trace_id[:8]>.json`       | JSON   | Full source register with claim types + confidence |
| `run_summary_<trace_id[:8]>.json`           | JSON   | Provenance, quality score, gate results      |

---

## Source Register Contract

Every artifact includes a source register entry for every claim. Fields:

| Field        | Type    | Description                              |
|--------------|---------|------------------------------------------|
| `source_id`  | str     | Unique source reference (SRC-NNN)        |
| `title`      | str     | Source description                       |
| `claim_type` | Enum    | `direct_evidence` / `interpretation` / `analyst_inference` / `assumption` |
| `confidence` | float   | 0.0–1.0 confidence score                 |
| `summary`    | str     | What this source supports                |
| `section_id` | str     | Which artifact section cites this source |

---

## Deterministic vs. Model-Driven Boundary

| Stage              | Deterministic? | Notes                                              |
|--------------------|----------------|----------------------------------------------------|
| Source register    | Yes            | Built from repo-internal evidence + analyst labels |
| Section assembly   | Yes            | Templates per mode with claim-type labels          |
| Comparison matrix  | Yes            | Lookup from known framework profiles               |
| Gate validation    | Yes            | Presence + threshold checks                        |
| Artifact emission  | Yes            | File writes + JSON serialization                   |

No LLM calls. All synthesis is deterministic and auditable.

---

## Quality Gates

| Gate ID                    | Threshold          | Action on Fail |
|----------------------------|--------------------|----------------|
| `RES_NO_SOURCE_REGISTER`   | ≥ 1 source         | BLOCK          |
| `RES_MISSING_SECTION`      | All required present| BLOCK         |
| `RES_EMPTY_SECTION`        | body != ""         | BLOCK          |

---

## Testable Acceptance Criteria

1. `--topic "governance" --mode brief --dry-run` returns `DRY_RUN` with 3 sections.
2. `--mode comparison --compare "LangGraph,AutoGen"` produces comparison matrix with ≥ 2 rows.
3. Every section body contains a claim type label (`[DIRECT_EVIDENCE]`, `[INTERPRETATION]`, etc.).
4. `source_register.json` contains all required fields for every entry.
5. `--mode thought_leadership` produces sections: `hook`, `insight`, `evidence`, `call_to_action`.
