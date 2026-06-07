# apps_qna — Interview Q&A Card-Pack Builder

Generates parameterized, ChatGPT-5.5-Thinking-ready interview-prep card packs from `(company, role, JD, interviewer profile(s), my-experience)`. Generalizes a validated interview-prep pattern (Drew Clements / Dentsu, 2026-04-29) into a reusable **builder + linter**, not a runtime agent.

## Design Patterns at Work

- **Builder + Linter, not Agent** — cards are markdown deliverables pasted into a ChatGPT 5.5-Thinking *Project*. v1 has no programmatic ChatGPT integration. Card validity is enforced **offline by a static linter**, not by runtime governance.
- **Routing Manifest** — Card 01 declares 9 primary routes. Each card carries an `<!-- card-meta -->` block (`card_type: rule | skill`, `priority`, `paste_order`, `load_strategy`) following Anthropic's RAG playbook §Rules vs Skills. Always-on rules govern *how* answers are produced; skill cards load on-demand by route.
- **Pack Promotion via Wilson CI + NamespaceBandit** — pack-lifecycle events (build / lint / self-eval / route-select / paste-set / promotion) flow through the `apps_qna_pack_lifecycle` ledger and feed W4 NamespaceBandit + Wilson-CI promotion gates per constitutional §29.
- **Deterministic Templates** — 18 `.md.j2` templates render the 22-card layout. Same inputs → same pack → same digest.
- **Self-Eval Loop** — `python -m apps_qna self-eval` diffs successive packs (cards added/removed, word-count delta, route-coverage diff). Pathology codes from `PATHOLOGY_TAXONOMY.md` close the learning loop alongside Card 22.
- **Six Linter Invariants** — every emitted pack is checked against six routing-manifest invariants (route coverage, paste-order consistency, citation-backbone integrity, metadata schema, glossary completeness, length bounds).

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

# Lint an emitted pack against the six invariants
python -m apps_qna lint reports/qna/drew-clements

# Diff a pack vs a previous run
python -m apps_qna self-eval --pack reports/qna/run-2 --previous reports/qna/run-1

# Dry run (print plan, write nothing)
python -m apps_qna --interview drew-clements --company dentsu --dry-run
```

## Card Pack Anatomy (22 cards)

The pack mirrors the validated Drew Clements layout. Each card is a small, focused markdown file with a routing-manifest-defined role.

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
| 19 | Source Register | Always-on: `[S#]` citation backbone for research claims |
| 20 | Glossary | Always-on: company- and role-specific term definitions |
| 21 | Likely Questions | Always-on: predicted-questions list grouped by route |
| 22 | Learnings and Delta Sheet | Post-rehearsal: pathology codes + delta capture |

## Card Metadata (Rules vs Skills)

```html
<!-- card-meta
card_id: 05_ARCHITECTURE_CORE
card_type: skill        # rule | skill
priority: should        # must | should | may
paste_order: 5
load_strategy: primary  # always_on | primary | specialist | post_rehearsal
-->
```

- **`rule`** cards are always-on and govern *how* answers are produced.
- **`skill`** cards are loaded by the routing manifest based on the question.
- **`paste_order`** is the recommended sequence when seeding a new ChatGPT Project — paste rules first, then skills.

## Inputs from other apps_*

| Source app | Artifact | Card source produced |
|---|---|---|
| `apps_research` | research brief + source register | `CompanyBackground`, `RoleAreasOfFocus`, `IndustryTrends`, `InterviewerLens` |
| `apps_rg` | resume + STAR proofs | `ExperiencePoint[]`, `StoryBank` |
| User YAML | interviewer profile | `Interviewer[]` |
| User markdown | JD | `JDSections[]` |

## Folder Structure

```
apps_qna/
├── builder/                 # CardPackBuilder
├── card_context/            # context budget + overlay compressor + assembler
├── cache/                   # R1A exact / R1B semantic / R5 fallback caches
├── cert/                    # FEC producer
├── config/                  # QnaBuildConfig + RouteRegistry SSOT
├── templates/               # 18 .md.j2 templates
├── router/                  # pack loader + linter
├── validators/              # 6 invariant checks
├── integrations/            # adapters for apps_research / apps_rg
├── tests/                   # pytest suite + fixtures
├── PATHOLOGY_TAXONOMY.md    # drift codes used by Card 22 and self-eval
├── RUNBOOK.md               # paste-into-ChatGPT operational guide
├── SLO.md                   # service-level objectives
├── __main__.py
└── Apps_qna_AGENTIC_SPINE.md
```

## See Also

- `RUNBOOK.md` — how to paste a pack into ChatGPT 5.5-Thinking
- `PATHOLOGY_TAXONOMY.md` — drift codes used by Card 22 and self-eval
- `SVP_ENGINEERING_REVIEW.md` — architectural review
- Plans — `docs/archive/windsurf/legacy-tree/plans/apps-qna-bootstrap-c4f2a8.md`, `apps-qna-rag-skills-alignment-7d2c4e.md`
