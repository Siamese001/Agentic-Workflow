# PRODUCT SPEC — apps_exec: Executive Brief Generator

## Product Intent

`apps_exec` translates an enterprise-grade agentic AI platform's technical architecture into
persona-targeted executive briefs. It produces polished, evidence-grounded documents that allow
the platform's capabilities to be communicated clearly to a recruiter, a CTO, an SVP of Engineering,
or a board-level stakeholder — each with a distinct reading priority and attention frame.

The app demonstrates that the repository owner can do more than build systems — they can translate
architecture into strategy, governance into business value, and engineering rigor into boardroom-ready narrative.

---

## Primary Users

| User Persona  | Goal                                                         | Success Signal                                      |
|---------------|--------------------------------------------------------------|-----------------------------------------------------|
| **Recruiter** | Quickly assess the candidate's technical breadth             | 1-page summary they can share with a hiring panel   |
| **CTO**       | Evaluate architectural soundness and governance maturity     | Confidence the platform is enterprise-deployable    |
| **SVP Eng**   | Assess engineering discipline and system design quality      | Visible evidence of production-grade decisions      |
| **Board**     | Understand strategic differentiation and risk posture        | ROI framing and governance assurance                |

---

## Core User Stories

1. **As a recruiter,** I want a one-page brief summarizing the candidate's AI platform skills so I can
   share it directly with the hiring team.
2. **As a CTO,** I want to see the architecture, governance model, and determinism enforcement so I can
   judge whether this is enterprise-grade or a demo.
3. **As an SVP of Engineering,** I want to see the specific engineering decisions, layer boundaries, and
   quality gates that prevent architectural drift.
4. **As a board stakeholder,** I want to understand the strategic positioning, risk posture, and
   differentiation story in plain business language.

---

## Inputs

| Input            | Type           | Required | Description                                          |
|------------------|----------------|----------|------------------------------------------------------|
| `--audience`     | Enum           | Yes      | `recruiter`, `cto`, `svp_eng`, `board`               |
| `--source-dirs`  | List[Path]     | No       | Directories to ingest documentation from             |
| `--config`       | Path           | No       | Override `config/exec_agent_specs.json`              |
| `--out`          | Path           | No       | Output directory (default: `reports/executive/`)     |
| `--dry-run`      | Flag           | No       | Plan and validate; do not emit artifacts             |
| `--trace-id`     | str            | No       | Override auto-generated trace ID for reproducibility |

**Rejected inputs:**
- Source directories containing no `.md`, `.py`, or `.txt` files are skipped with a warning.
- Files larger than 512 KB are skipped with a warning.
- Audience values outside the defined enum are rejected at parse time with a non-zero exit code.

---

## Outputs

| Artifact                                     | Format   | Description                               |
|----------------------------------------------|----------|-------------------------------------------|
| `exec_brief_<audience>_<trace_id[:8]>.md`    | Markdown | Formatted executive brief                 |
| `run_summary_<trace_id[:8]>.json`            | JSON     | Provenance, gate results, artifact paths  |

---

## Pipeline (Summary)

```
1. Ingestion        — Read and normalize source documents
2. Extraction       — Regex-based capability and evidence anchor identification
3. Assembly         — Deterministic section skeleton per persona
4. Style Gate       — Buzz-word density, evidence anchors, unsupported claims
5. Emission         — Write artifacts + run summary
```

---

## Deterministic vs. Model-Driven Boundary

| Stage              | Deterministic? | Notes                                              |
|--------------------|----------------|----------------------------------------------------|
| Ingestion          | Yes            | File reads, filtering by extension/size            |
| Capability extract | Yes            | Regex patterns against known module/doc keywords   |
| Section assembly   | Yes            | Templates with evidence injection                  |
| Style gate         | Yes            | Threshold checks — arithmetic only                 |
| Artifact emission  | Yes            | File write + JSON serialization                    |

No LLM calls. All outputs are traceable to inputs.

---

## Quality Gates

| Gate ID                   | Threshold        | Action on Fail |
|---------------------------|------------------|----------------|
| `STYLE_EMPTY_BODY`        | body != ""       | BLOCK          |
| `STYLE_UNSUPPORTED_CLAIM` | 0 absolute claims| BLOCK          |
| `STYLE_BUZZWORD_DENSITY`  | < 5% buzzwords   | BLOCK          |
| `STYLE_NO_EVIDENCE_ANCHOR`| ≥ 1 anchor       | WARN           |
| `STYLE_NO_WHY_MATTERS`    | block present    | WARN           |

---

## Failure Modes

- **No source files found:** Exit with error message listing checked paths. No silent empty brief.
- **Gate BLOCK violation:** Brief is NOT emitted. Run summary records the violations. Exit code 1.
- **Gate WARN violation:** Brief IS emitted. Run summary records the warnings. Exit code 0.
- **Config load failure:** Falls back to defaults and logs warning with path that failed.

---

## Testable Acceptance Criteria

1. Running `--audience recruiter --dry-run` returns status `DRY_RUN` with sections non-empty and `artifact_paths == []`.
2. Running `--audience cto` emits a `.md` file containing sections `architecture_overview` and `governance_model`.
3. A section with body containing "game-changer" fails `STYLE_BUZZWORD_DENSITY`.
4. A section with empty body is blocked by `STYLE_EMPTY_BODY`.
5. `run_summary.json` always contains `trace_id`, `gate_violations`, `quality_score`, and `provenance`.
