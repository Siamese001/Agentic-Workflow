# PRODUCT SPEC — apps_rfp: AI Proposal / RFP Generator

## Product Intent

`apps_rfp` generates complete, structured AI platform proposals from a client problem statement.
It demonstrates the ability to move from a client's expressed pain point to a fully-formed
proposal — with executive narrative, future-state architecture, phased roadmap, risk matrix,
and commercial value case — all grounded in the repo's platform capabilities.

The app proves commercialization maturity: the ability to take a platform and translate it
into a client-facing, revenue-generating artifact.

---

## Primary Users

| User Persona          | Goal                                                      | Success Signal                                 |
|-----------------------|-----------------------------------------------------------|------------------------------------------------|
| **Solutions Architect**| Rapidly draft a complete proposal for a client brief    | Structured proposal ready for review in <1 min |
| **Pre-Sales Engineer** | Generate a platform pitch grounded in real capabilities  | Credible architecture posture + roadmap        |
| **Practice Lead**      | Produce a compliance-aware proposal for a regulated co. | Industry-specific risk matrix and assumptions  |
| **Portfolio Reviewer** | See evidence of commercialization thinking               | Visible solutioning and value-case discipline  |

---

## Core User Stories

1. **As a solutions architect,** I want to provide a problem statement and industry, and receive a
   complete structured proposal with all required sections populated.
2. **As a practice lead,** I want industry-aware regulatory flags automatically surfaced in the
   risk matrix so no compliance consideration is missed.
3. **As a pre-sales engineer,** I want a phased roadmap that includes a governance phase,
   not just feature delivery phases.
4. **As a portfolio reviewer,** I want to see that every assumption is explicitly labeled and
   every risk has an owner and mitigation.

---

## Inputs

| Input              | Type       | Required | Description                                                  |
|--------------------|------------|----------|--------------------------------------------------------------|
| `--brief`          | str        | Yes*     | Client problem statement (inline text)                       |
| `--brief-file`     | Path       | Yes*     | Path to file containing client problem statement             |
| `--industry`       | Enum       | No       | `technology`, `financial_services`, `healthcare`, `government`|
| `--posture`        | Enum       | No       | `cloud_first`, `hybrid`, `sovereign`                         |
| `--timeline`       | int        | No       | Delivery timeline in weeks                                   |
| `--out`            | Path       | No       | Output directory (default: `rfp/`)                           |
| `--dry-run`        | Flag       | No       | Plan and validate; do not emit artifacts                     |

*One of `--brief` or `--brief-file` is required.

**Rejected inputs:**
- Empty problem statement is rejected at parse time.
- Unknown industry values fall back to `technology` with a warning.

---

## Outputs

| Artifact                                      | Format   | Description                                     |
|-----------------------------------------------|----------|-------------------------------------------------|
| `proposal_<industry>_<trace_id[:8]>.md`       | Markdown | Full structured proposal                        |
| `proposal_manifest_<trace_id[:8]>.json`       | JSON     | Section manifest, roadmap, risks, assumptions   |
| `run_summary_<trace_id[:8]>.json`             | JSON     | Provenance, gate results, artifact paths        |

---

## Pipeline (Summary)

```
1. Brief Parsing    — Extract problem statement, industry, constraints
2. Profile Loading  — Load industry regulatory flags and architecture posture
3. Assembly         — Build sections, roadmap phases, risk matrix, assumptions
4. Gate Validation  — Required sections, risk matrix presence, roadmap governance phase
5. Emission         — Write artifacts + run summary
```

---

## Deterministic vs. Model-Driven Boundary

| Stage             | Deterministic? | Notes                                                    |
|-------------------|----------------|----------------------------------------------------------|
| Brief parsing     | Yes            | String extraction, no NLP                                |
| Profile loading   | Yes            | Lookup from config                                       |
| Section assembly  | Yes            | Templates parameterized by industry/posture/problem      |
| Roadmap build     | Yes            | Fixed 5-phase structure with parameterized names/durations|
| Risk matrix       | Yes            | Lookup from industry risk register                       |
| Gate validation   | Yes            | Presence + threshold checks                              |

No LLM calls. All proposal content is derived from deterministic templates.

---

## Required Sections (always present)

1. `executive_summary` — Client-facing summary of the engagement
2. `current_state` — Honest characterization of the client's current position
3. `future_state` — Target architecture description
4. `implementation_roadmap` — 5-phase roadmap with Govern phase
5. `risk_and_governance` — Risk matrix with regulatory flags
6. `value_case` — ROI framing, efficiency gains, risk reduction

---

## Quality Gates

| Gate ID                        | Threshold            | Action on Fail |
|--------------------------------|----------------------|----------------|
| `PROP_MISSING_SECTION`         | All required present | BLOCK          |
| `PROP_EMPTY_SECTION`           | body != ""           | BLOCK          |
| `PROP_EMPTY_RISK_MATRIX`       | ≥ 1 risk item        | BLOCK          |
| `PROP_MISSING_GOVERN_PHASE`    | Govern phase present | BLOCK          |
| `PROP_MISSING_ASSUMPTIONS`     | ≥ 1 assumption       | WARN           |

---

## Testable Acceptance Criteria

1. Running `--brief "test" --dry-run` returns status `DRY_RUN` with sections non-empty.
2. Proposal for `--industry financial_services` includes SOX or GDPR in risk matrix.
3. Roadmap always has exactly 5 phases including a Governance phase.
4. All assumptions carry IDs starting with `ASM-`.
5. `run_summary.json` contains `trace_id`, `industry`, `roadmap_phases`, and `gate_violations`.
