# Apps Portfolio Overview

## Why These Apps Exist

This repository contains an enterprise-grade agentic AI platform (`agentic_core`) with
six architectural layers, constitutional enforcement hooks, policy hash validation,
static analysis for determinism, and multi-hop orchestration.

The four apps in this directory answer a question that architecture docs alone cannot:

> **Can this platform actually deliver?**

Each app is a concrete demonstration. Not a demo. Not a prototype. Each one:
- Takes real inputs
- Runs a deterministic, auditable pipeline
- Enforces explicit quality gates with no silent fallback
- Produces polished, provenance-carrying artifacts
- Supports dry-run mode, JSON output, and CI integration

Together they form a portfolio of applied platform capability — showing that the
platform can be used to build production-grade applications across four distinct problem domains.

---

## How They Strengthen the Repository

| Without These Apps | With These Apps                                    |
|--------------------|----------------------------------------------------|
| Architecture docs  | Architecture + running, testable applications      |
| Governance theory  | Governance enforcement demonstrated in `apps_eval` |
| Platform patterns  | Patterns applied to real workflows (exec, rfp, research) |
| Code depth         | Code depth + output quality + business relevance  |

A reviewer opening this repository now sees:
1. **Platform infrastructure** (agentic_core L0–L6)
2. **App workloads** (4 apps, each showcasing a different value dimension)
3. **Evaluation harness** (apps_eval benchmarks the entire stack)
4. **Documentation** (PRODUCT_SPEC, TECHNICAL_SPEC, OUTPUT_CONTRACTS, CLI_SPEC, TEST_STRATEGY per app)

---

## App Summary

### `apps_exec` — Executive Brief Generator

**What it does:** Translates the repo's architecture documentation into persona-targeted
executive briefs for recruiters, CTOs, SVP engineers, and board audiences.

**Why it exists:** Demonstrates platform-to-strategy translation capability.
An AI platform that cannot explain itself to non-engineers has limited commercial reach.

**Artifacts produced:**
- `exec_brief_<audience>_<trace>.md` — formatted brief with evidence anchors
- `run_summary_<trace>.json` — provenance, quality score, gate violations

**Reviewer persona impressed:** Recruiters, hiring managers, SVP Engineering reviewers

---

### `apps_rfp` — AI Proposal / RFP Generator

**What it does:** Generates complete AI platform proposals from a client problem statement —
including executive narrative, future-state architecture, 5-phase roadmap, risk matrix,
and commercial value case. Industry-aware: financial services, healthcare, government, technology.

**Why it exists:** Demonstrates commercialization maturity. Shows that the platform owner
can build systems that generate revenue-facing artifacts, not just infrastructure.

**Artifacts produced:**
- `proposal_<industry>_<trace>.md` — full structured proposal
- `proposal_manifest_<trace>.json` — section manifest, roadmap, risks, assumptions
- `run_summary_<trace>.json` — provenance + gate results

**Reviewer persona impressed:** CTOs, Heads of AI, pre-sales and solutions leads reviewing
the candidate's enterprise solutioning ability

---

### `apps_research` — Autonomous Research Engine

**What it does:** Generates structured research artifacts from a topic and mode.
Five modes: `brief`, `comparison`, `trend`, `position`, `thought_leadership`.
Every claim is labeled with its epistemic type (`direct_evidence`, `interpretation`,
`analyst_inference`, `assumption`). Every artifact ships with a machine-readable source register.

**Why it exists:** Demonstrates synthesis and thought leadership capability.
Shows the platform can produce institutional knowledge artifacts, not just execute pipelines.

**Artifacts produced:**
- `research_<mode>_<trace>.md` — structured research artifact with labeled claims
- `source_register_<trace>.json` — full source register with claim types and confidence
- `run_summary_<trace>.json` — provenance + quality score

**Reviewer persona impressed:** AI research leads, Heads of AI Strategy, technical reviewers
evaluating depth of synthesis

---

### `apps_eval` — Evaluation Lab

**What it does:** Benchmarks `agentic_core` and app workloads against deterministic scenarios.
Computes a weighted scorecard across 5 dimensions (correctness, determinism, governance,
latency, output richness). Detects regressions against a stored baseline. Exit code 2 on
regression (distinct from exit code 1 for gate failure) — CI-ready.

**Why it exists:** Demonstrates engineering rigor. Proves that the platform owner measures
quality, tracks it over time, and can gate on it. Most AI repos have no evaluation harness.

**Artifacts produced:**
- `eval_report_<trace>.md` — full report with scorecard + suite results + regression table
- `scorecard_<trace>.csv` — machine-readable, CI-consumable
- `eval_manifest_<trace>.json` — lightweight manifest
- `run_summary_<trace>.json` — provenance + overall score + gate violations

**Reviewer persona impressed:** CTOs, SVP Engineering, AI Platform leads, and any technical
reviewer who cares about whether quality is measured, not just assumed

---

## Reviewer Persona Map

| Reviewer Persona         | Primary App to Examine | What They Will See                                    |
|--------------------------|------------------------|-------------------------------------------------------|
| **Recruiter**            | `apps_exec`            | Clean brief about the platform, tailored to their frame |
| **CTO**                  | `apps_eval`, `apps_rfp`| Governance rigor, benchmarking discipline, proposal quality |
| **SVP Engineering**      | `apps_exec`, `apps_eval`| Engineering decisions, quality gates, scorecard design |
| **Head of AI Platform**  | `apps_research`, `apps_eval`| Synthesis depth, evaluation harness, research rigor |
| **Solutions Architect**  | `apps_rfp`             | Proposal structure, industry awareness, roadmap discipline |
| **AI Researcher**        | `apps_research`        | Epistemic labeling, claim-type system, source register |
| **Hiring Panel (Senior)**| All four + agentic_core| End-to-end platform thinking: infra → apps → evaluation |

---

## Enterprise AI Platform Value Map

| Platform Value                  | Demonstrated By                                        |
|---------------------------------|--------------------------------------------------------|
| Governance as infrastructure    | `agentic_core` L0–L6 + `apps_eval` governance suite   |
| Determinism enforcement         | `apps_eval` determinism suite + static analysis layer  |
| Executive communication         | `apps_exec` — strategy translation from architecture   |
| Commercialization readiness     | `apps_rfp` — proposal generation with value cases      |
| Knowledge synthesis             | `apps_research` — labeled claims + source registers    |
| Engineering quality culture     | `apps_eval` — scorecard + regression baseline tracking |
| Auditability                    | All apps — run summaries with provenance metadata      |
| CI/CD readiness                 | All apps — JSON output + deterministic exit codes      |

---

## Global Design Rules (applied to all four apps)

These rules are non-negotiable across all apps in this portfolio:

| Rule                              | Enforcement                                                   |
|-----------------------------------|---------------------------------------------------------------|
| No silent fallback                | Gate failures stop the pipeline; violations always surfaced   |
| No fake success states            | `DRY_RUN` is not `COMPLETE`; they have different status values|
| Provenance on every output        | `run_summary.json` always written with `provenance` key       |
| Dry-run support                   | All apps support `--dry-run`; dry-run never writes files      |
| Deterministic sections explicit   | Every section tagged `is_deterministic: bool`                 |
| Explicit quality gates            | Every app has a named validator with named rule IDs           |
| Explicit failure reporting        | Exit codes, gate violation lists, error fields — never silent  |
| Testable acceptance criteria      | Every spec has 5+ concrete, assertion-level criteria          |
| Markdown + JSON + CSV outputs     | Consistent artifact format philosophy across all apps         |
| App-local schemas                 | Each app owns its Pydantic config; no cross-app config coupling|

---

## Directory Structure (all four apps)

```
apps_exec/          apps_rfp/           apps_research/      apps_eval/
├── config/         ├── config/         ├── config/         ├── config/
├── engines/        ├── engines/        ├── engines/        ├── engines/
├── reasoning/      ├── reasoning/      ├── reasoning/      ├── reasoning/
├── scripts/        ├── scripts/        ├── scripts/        ├── scripts/
├── types/          ├── types/          ├── types/          ├── types/
├── validators/     ├── validators/     ├── validators/     ├── validators/
├── utils/          ├── utils/          ├── utils/          ├── utils/
├── __init__.py     ├── __init__.py     ├── __init__.py     ├── __init__.py
├── __main__.py     ├── __main__.py     ├── __main__.py     ├── __main__.py
├── README.md       ├── README.md       ├── README.md       ├── README.md
├── PRODUCT_SPEC.md ├── PRODUCT_SPEC.md ├── PRODUCT_SPEC.md ├── PRODUCT_SPEC.md
├── TECHNICAL_SPEC  ├── TECHNICAL_SPEC  ├── TECHNICAL_SPEC  ├── TECHNICAL_SPEC
├── OUTPUT_CONTRACTS├── OUTPUT_CONTRACTS├── OUTPUT_CONTRACTS├── OUTPUT_CONTRACTS
├── CLI_SPEC.md     ├── CLI_SPEC.md     ├── CLI_SPEC.md     ├── CLI_SPEC.md
└── TEST_STRATEGY   └── TEST_STRATEGY   └── TEST_STRATEGY   └── TEST_STRATEGY
```

---

## How to Run All Four Apps (Quick Reference)

```bash
# Executive brief (dry run)
python -m apps_exec --audience cto --dry-run

# AI Proposal
python -m apps_rfp --brief "Automate compliance workflows" --industry financial_services

# Research artifact
python -m apps_research --topic "enterprise agentic AI governance" --mode comparison \
  --compare "LangGraph,AutoGen,CrewAI"

# Evaluation lab (all suites)
python -m apps_eval --all --out eval/ --json-output
```

---

*This portfolio was built to demonstrate that an AI platform repo can be more than infrastructure.
It can show executive communication, commercialization thinking, research depth, and engineering
rigor — all in one coherent, auditable, production-aligned codebase.*
