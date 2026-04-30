# apps_qna — Interview Q&A Card-Pack Builder

Generates parameterized, ChatGPT-5.5-Thinking-ready interview-prep card packs
from (company, role, JD, interviewer profile(s), my-experience), generalizing
the Drew Clements / Dentsu pattern (validated 2026-04-29) into a reusable
builder + linter.

## What this is

`apps_qna` is a **builder + linter**, not a runtime agent.

- **Cards are the deliverable.** They are markdown files designed to be pasted
  into a ChatGPT 5.5-Thinking *Project* as the project-instruction context
  budget.
- **No API call.** v1 has no programmatic ChatGPT integration.
- **No runtime governance.** No UWG, no L5 gates, no Author-Gate at runtime.
  Card validity is enforced offline by a static linter.

## Quick Start

```bash
# Generate a pack from typed inputs
python -m apps_qna \
  --interview drew-clements \
  --company dentsu \
  --role "VP Decisioning Engineering" \
  --jd path/to/jd.md \
  --interviewers path/to/drew_clements.yaml \
  --experience path/to/my_experience.yaml \
  --research-from reports/research/research_brief_<trace>.md \
  --output reports/qna/drew-clements

# Lint an emitted pack against the routing-manifest invariants
python -m apps_qna lint reports/qna/drew-clements

# Dry run (print plan, write nothing)
python -m apps_qna --interview drew-clements --company dentsu --dry-run
```

## Card Pack Anatomy (18 cards)

The pack mirrors the validated Drew Clements layout. Each card is a small,
focused markdown file with a routing-manifest-defined role.

| # | Card | Role |
|---|---|---|
| 00 | Runtime Root | Always-on: live answer spine, posture, length defaults |
| 01 | Routing Manifest | Always-on: 9 primary routes, triggers, answer shapes |
| 02 | Live Mode and Release Gates | Always-on: q-prefix gate, release checks |
| 03 | Interviewer Lens | Per-interviewer profile (one card per interviewer for panels) |
| 04 | Company Decisioning Overlay | Company-specific anchors and vocabulary |
| 05 | Agentic Architecture Core | Route 4 (Architecture) primary card |
| 06 | Data Platform Stack | Route 4/6 specialist (Databricks/Foundry/Unity etc.) |
| 07 | Measurement Intelligence | Route 6 specialist (MMM/incrementality/forecasting) |
| 08 | Guardian Agents and Safe Actions | Route 5 (Governance) primary card |
| 09 | Semantic Grounding and Text-to-SQL | Route 5 specialist |
| 10 | DS to Platform / MLOps | Route 6 (DS-to-Platform) primary card |
| 11 | Global Engineering Model | Route 8 (DGS) primary card |
| 12 | Productization and ROI | Route 7 (Product/ROI) primary card |
| 13 | Executive Fit and Positioning | Route 1 (Exec Fit) primary card |
| 14 | STAR Story Bank and Proof Router | Route 2 (STAR) primary card |
| 15 | Failure RCA and Recovery | Route 3 (RCA) primary card |
| 16 | Cross-Exam Technical Depth | Route 9 (Cross-Exam) primary card |
| 17 | Questions and 90-Day Plan | Closing: questions Amit asks them |

## Inputs from other apps_*

| Source app | Artifact | Card source produced |
|---|---|---|
| `apps_research` | research brief + source register | `CompanyBackground`, `RoleAreasOfFocus`, `IndustryTrends`, `InterviewerLens` |
| `apps_rg` | resume + STAR proofs | `ExperiencePoint[]`, `StoryBank` |
| `apps_exec` | executive brief | `ExecutiveFit` framing |
| User YAML | interviewer profile | `Interviewer[]` |
| User markdown | JD | `JDSections[]` |

## Folder Structure

```
apps_qna/
├── __init__.py
├── __main__.py              # python -m apps_qna entrypoint
├── README.md                # this file
├── RUNBOOK.md               # paste-into-ChatGPT operational guide
├── SLO.md                   # service-level objectives
├── TECHNICAL_SPEC.md        # types + builder + linter contract
├── TEST_STRATEGY.md         # 18-template render + 6-invariant linter coverage
├── SVP_ENGINEERING_REVIEW.md
├── config/                  # QnaBuildConfig + RouteRegistry SSOT
├── types/                   # pydantic models
├── templates/               # 18 .md.j2 templates
├── builder/                 # CardPackBuilder
├── router/                  # pack loader + linter
├── validators/              # 6 invariant checks
├── integrations/            # adapters for apps_research / apps_rg / apps_exec
├── scripts/                 # CLI entrypoints
└── tests/                   # pytest suite + fixtures
```

## See also

- `RUNBOOK.md` — how to paste a pack into ChatGPT 5.5-Thinking
- `TECHNICAL_SPEC.md` — types, builder contract, linter invariants
- `.windsurf/plans/apps-qna-bootstrap-c4f2a8.md` — bootstrap plan (5 waves)
