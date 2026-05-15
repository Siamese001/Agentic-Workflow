---
plan_id: apps-qna-bootstrap-c4f2a8
plan_type: infra
---

# apps_qna — Interview Q&A Card-Pack Builder Bootstrap

Bootstrap a new `apps_qna` module that generates parameterized, ChatGPT-5.5-Thinking-ready interview-prep card packs from (company, role, JD, interviewer profile(s), my-experience) — generalizing the Drew Clements / Dentsu pattern into a reusable builder + linter, fed by `apps_research`, `apps_rg`, and `apps_exec` outputs.

---

## Context (SCQA)

- **Situation** — A working interview-prep card pack exists for the Drew Clements / Dentsu interview at `C:\Users\amita\Documents\Dentsu\Drew Clements - 4.29.2026\` (18 numbered cards: Runtime Root → Routing Manifest → Live Mode & Release Gates → 8 primary-route specialist cards → STAR Bank → RCA → Cross-Exam → Drew Lens → Dentsu Overlay). The pattern is validated; the cards run cleanly inside a ChatGPT 5.5-Thinking project as the system-prompt context budget. The repo has `apps_research`, `apps_rg`, and `apps_exec` whose outputs (research briefs, STAR proofs, executive framing) are the natural feeders.
- **Complication** — The Drew pack is hand-authored. Every new interview (different interviewer, different company, different JD) requires re-doing 18 cards by hand. There is no programmatic builder, no card-set linter (route purity, ≤2 specialist cards, max-context rule), and no typed adapter from `apps_research` / `apps_rg` / `apps_exec` outputs into card-source inputs.
- **Question** — How do we build an `apps_qna` module that generates a Drew-Clements-equivalent card pack for any interview, parameterized by interviewer(s), company, JD, my experience, and deep research, with the routing manifest's invariants enforced by a static linter?
- **Answer** — Ship a builder + linter + template library: parameterized Jinja card templates, a builder CLI that accepts typed inputs and emits a numbered card directory, and a router/linter that validates the emitted pack obeys the routing manifest (one primary route per question class, ≤2 specialist cards, max-context rule, route purity check). No runtime agent, no API call, no UWG/L5 integration in v1 — cards ARE the deliverable, manually pasted into ChatGPT 5.5-Thinking.

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| `.windsurf/rules/plan-location.md` | plan SSOT path + format invariants | ✅ |
| `.windsurf/rules/author-gate-enforcement.md` | architecture decision captured | ✅ |
| `apps_research/` (README, __main__, structure) | apps_* contract template | ✅ |
| `C:\Users\amita\Documents\Dentsu\Drew Clements - 4.29.2026\01_ROUTING_MANIFEST.md` | routing pattern source | ✅ |
| `C:\Users\amita\Documents\Dentsu\Drew Clements - 4.29.2026\00_RUNTIME_ROOT.md` | runtime root pattern source | ✅ |
| Remaining 16 Drew cards (02-17) | template surface for generalization | 🔲 (read in Wave 1) |
| `apps_rg/`, `apps_exec/` structure | adapter contract design | 🔲 (read in Wave 4) |

---

## Wave Structure

| Wave | Metric | Scope | Checkpoint | Tokens |
|------|--------|-------|------------|---------|
| Wave 1 | Skeleton + types + 18-card template library generalized | apps_qna scaffold; templates/ directory; types/ | A | ~14K ✅ |
| Wave 2 | Builder CLI generates a card pack from typed inputs | builder/, scripts/run_qna.py, __main__.py, integration with one input fixture | B | ~12K ✅ |
| Wave 3 | Router/linter enforces routing-manifest invariants | router/, validators/, route_purity_check, max_context_check | C | ~8K ✅ |
| Wave 4 | Adapters wire `apps_research` / `apps_rg` / `apps_exec` outputs into card sources | integrations/research_adapter.py, rg_adapter.py, exec_adapter.py | D | ~10K 🟢 |
| Wave 5 | Drew Clements e2e canary: regenerate the existing 18-card pack from typed inputs and diff against the hand-authored source | tests/test_drew_canary.py, fixtures/drew_clements/ | E | ~8K 🟢 |

**Total: ~52K tokens across 5 waves, all GREEN**

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| 1.1 | ✅ apps_qna scaffold + apps_* contract docs | `apps_qna/{__init__.py, __main__.py, README.md, RUNBOOK.md, SLO.md, TECHNICAL_SPEC.md, TEST_STRATEGY.md, SVP_ENGINEERING_REVIEW.md}` | New app — must satisfy apps_* contract | ~4K | 🔲 TODO |
| 1.2 | ✅ Types: pydantic v2 frozen models for Interview / Interviewer / Company / Role / JDSection / ExperiencePoint / Story / RCAStory / ResearchInputs / BuildMetadata / CardPackManifest | `apps_qna/types/qna_types.py` | Frozen pydantic models, exhaustive | ~3K | ✅ DONE |
| 1.3 | ✅ Read 00/01/02 Drew cards; authored generalized templates from validated routing manifest pattern; extract template variables; author 12-15 generalized Jinja templates | `apps_qna/templates/{00_runtime_root.md.j2, 01_routing_manifest.md.j2, 02_live_mode.md.j2, 03_executive_lens.md.j2, 04_company_overlay.md.j2, 05_architecture_core.md.j2, 06_data_platform.md.j2, 07_measurement.md.j2, 08_governance.md.j2, 09_semantic.md.j2, 10_ds_to_platform.md.j2, 11_global_engineering.md.j2, 12_productization.md.j2, 13_executive_fit.md.j2, 14_star_bank.md.j2, 15_rca.md.j2, 16_cross_exam.md.j2, 17_questions_for_them.md.j2}` | Templates must stay interview-agnostic | ~7K | 🔲 TODO |
| 2.1 | ✅ Config: `QnaBuildConfig` (pydantic), `RouteRegistry` (route triggers + answer shapes from routing manifest) | `apps_qna/config/{__init__.py, build_config.py, route_registry.py, route_registry.yaml}` | YAML SSOT for the 9 routes; consumed by both builder and router | ~3K | 🔲 TODO |
| 2.2 | ✅ Builder: `CardPackBuilder` orchestrates template render → numbered file emit | `apps_qna/builder/{__init__.py, card_pack_builder.py, jinja_env.py}` | Filename convention `<NN>_<SLUG>.md` numbered 00..17 | ~3K | 🔲 TODO |
| 2.3 | ✅ CLI: `python -m apps_qna --interview <slug> --company <name> --role <title> --jd <path> --interviewers <yaml>` | `apps_qna/scripts/run_qna.py`, `apps_qna/__main__.py` | argparse, dry-run, output dir override | ~2K | 🔲 TODO |
| 2.4 | ✅ First end-to-end smoke: synthetic mini-input → 4-card output | `apps_qna/tests/test_smoke_minimal.py`, `apps_qna/tests/fixtures/synthetic_mini.yaml` | Proves the spine works before Drew canary | ~4K | 🔲 TODO |
| 3.1 | ✅ Router/linter primitives: parse a card pack directory, extract front-matter, build route map | `apps_qna/router/{__init__.py, pack_loader.py}` | Reads emitted packs back as structured objects | ~2K | 🔲 TODO |
| 3.2 | ✅ Validators: route purity, ≤2 specialist cards, max-context rule, all-routes-covered, no-orphan-card | `apps_qna/validators/{__init__.py, route_purity.py, context_budget.py, route_coverage.py}` | Errors map 1:1 to routing-manifest §"Hard rule", §"Max context rule", §"Route purity check" | ~3K | 🔲 TODO |
| 3.3 | ✅ `python -m apps_qna lint <pack-dir>` subcommand wired through real validator runner | `apps_qna/scripts/lint_pack.py` | Exit non-zero on any violation | ~1K | 🔲 TODO |
| 3.4 | ✅ Tests: 6 negative tests (one per LINT-1..6) + 6 positive tests + integration runner test — 19/19 green | `apps_qna/tests/test_validators.py`, `apps_qna/tests/fixtures/invalid_packs/*` | Each validator gets its own red-then-green proof | ~2K | 🔲 TODO |
| 4.1 | `apps_research` adapter: maps research-brief sections → CompanyBackground / RoleAreasOfFocus card sources | `apps_qna/integrations/research_adapter.py` | Reads `reports/research/research_<mode>_<trace>.md` + `source_register_<trace>.json` | ~3K | 🔲 TODO |
| 4.2 | `apps_rg` adapter: maps achievements + STAR proofs → ExperiencePoint / StoryBank card sources | `apps_qna/integrations/rg_adapter.py` | Reads existing apps_rg artifacts | ~3K | 🔲 TODO |
| 4.3 | `apps_exec` adapter: maps executive-brief framing → ExecutiveFit card source | `apps_qna/integrations/exec_adapter.py` | Reads `reports/executive/exec_brief_*.md` | ~2K | 🔲 TODO |
| 4.4 | Adapter integration tests against real fixtures from each source app | `apps_qna/tests/test_adapters.py` | Uses checked-in fixtures, no live runs | ~2K | 🔲 TODO |
| 5.1 | Drew Clements canary fixture: encode the inputs that produced the existing 18 cards | `apps_qna/tests/fixtures/drew_clements/{interview.yaml, company.yaml, role.yaml, interviewers.yaml, experience.yaml, research_brief.md}` | Reverse-engineered from the 18 hand-authored cards | ~4K | 🔲 TODO |
| 5.2 | E2E test: regenerate 18-card pack from canary inputs; diff against hand-authored source; assert structural equivalence (route triggers, card numbering, section presence) — not byte-identical | `apps_qna/tests/test_drew_canary.py` | Diff is structural, not literal — Jinja output will differ in punctuation | ~3K | 🔲 TODO |
| 5.3 | Update apps_qna README with Drew canary as the worked example | `apps_qna/README.md` (extend) | Demonstrates the "from inputs to ChatGPT-paste-ready pack" flow | ~1K | 🔲 TODO |

**Status legend**: 🔲 TODO · 🔄 IN PROGRESS · ✅ DONE · ❌ BLOCKED

---

## Gap Register

**GAP-1: 16 Drew cards still unread**
- Only 00 (Runtime Root) and 01 (Routing Manifest) have been read in this session.
- Phase 1.3 must read the remaining 16 (02-17) before authoring templates, or templates will miss surface area.

**GAP-2: Existing apps_research / apps_rg / apps_exec output schemas not yet inventoried**
- Adapter design in Wave 4 depends on the actual artifact shapes these apps produce today.
- Phases 4.1-4.3 each open with a 5-minute schema read of one real artifact from `reports/`.

**GAP-3: ChatGPT 5.5-Thinking project context-paste mechanics not yet codified**
- Cards are designed to be pasted into a ChatGPT Project as instruction-set context.
- The exact paste order, project-instructions field length limit, and any custom-instruction split is operational knowledge that should land in `RUNBOOK.md`.

**GAP-4: Multi-interviewer support shape**
- User mentioned "multiple interviewers in some cases".
- Card 03 (Drew Lens) is currently per-interviewer. Multi-interviewer mode needs either (a) one Lens card per interviewer or (b) a unified Panel Lens. Decision deferred to Phase 1.3 once all 18 templates are read.

---

## Execution Plan

### Phase 1.1 — Scaffold + apps_* contract docs
**Scope**: Create `apps_qna/` directory with the apps_* required document set (README, RUNBOOK, SLO, TECHNICAL_SPEC, TEST_STRATEGY, SVP_ENGINEERING_REVIEW), `__init__.py`, `__main__.py` stub.

**Acceptance**: `python -c "import apps_qna"` succeeds. `python -m apps_qna --help` prints. All six required docs exist with substantive content (no placeholder TODOs).

### Phase 1.2 — Types
**Scope**: Pydantic v2 frozen models for all interview-prep entities. Exhaustive — every input field that a card might reference must have a typed home.

**Acceptance**: `python -m apps_qna.types --print-schemas` emits JSON schemas. mypy --strict clean.

### Phase 1.3 — Template library
**Scope**: Read remaining 16 Drew cards. Extract every interview-specific value (company name, interviewer name/title/lens, JD-specific terminology, my-experience-specific names) and replace with Jinja variable. Author one template per Drew card.

**Acceptance**: `apps_qna/templates/` contains 18 `.md.j2` files. Each renders cleanly under `jinja2.Environment(undefined=StrictUndefined)`.

### Phase 2.1 — Config + RouteRegistry
**Scope**: YAML SSOT for the 9 routes from `01_ROUTING_MANIFEST.md` (Executive Fit, STAR, RCA, Architecture, Governance, DS-to-Platform, Productization, DGS, Cross-Exam). Each route declares: triggers, answer-shape, required-cards, optional-specialist-cards.

**Acceptance**: Route registry round-trips YAML ↔ pydantic. Triggers, shapes, and load-lists match `01_ROUTING_MANIFEST.md` line-for-line.

### Phase 2.2 — CardPackBuilder
**Scope**: `CardPackBuilder.build(config: QnaBuildConfig) -> Path` — renders all templates, writes numbered files to output dir.

**Acceptance**: Smoke fixture (Phase 2.4) produces a 4-card pack in `<output>/test_smoke/`.

### Phase 2.3 — CLI
**Scope**: argparse-based entrypoint mirroring apps_research's CLI shape.

**Acceptance**: `python -m apps_qna --interview drew-clements --company dentsu --role 'VP Decisioning' --jd <path> --interviewers <yaml> --dry-run` prints the planned card list without writing.

### Phase 2.4 — Smoke
**Scope**: Synthetic minimal fixture (1 interviewer, 3 sentences of company background, a 5-line JD, 2 experience points). Render 4 cards. Assert exit 0 + 4 files emitted.

**Acceptance**: `pytest apps_qna/tests/test_smoke_minimal.py` green.

### Phase 3.1-3.4 — Router/linter
**Scope**: Static analyzer over an emitted pack. Validates route purity (no card collapses multiple route types), context budget (no answer would load >3 cards), route coverage (all 9 routes have at least one card).

**Acceptance**: 6 negative fixtures each fail their target validator with a precise error message; 1 positive fixture passes all.

### Phase 4.1-4.4 — Adapters
**Scope**: Three thin adapter modules. Each reads one apps_* artifact type and emits the typed card-source object.

**Acceptance**: For each adapter, a real artifact from `reports/` round-trips into card source without loss of structured fields.

### Phase 5.1-5.3 — Drew canary
**Scope**: Encode the inputs that produced the existing 18 hand-authored Drew cards as YAML fixtures. Run the builder. Diff structurally. Document the result in README.

**Acceptance**: All 18 generated cards exist with correct numbering and section headers; route registry triggers/loads match the hand-authored `01_ROUTING_MANIFEST.md` line-for-line.

---

## Rules

- No editing of the `C:\Users\amita\Documents\Dentsu\Drew Clements - 4.29.2026\` source files. They are read-only reference.
- No programmatic ChatGPT API call in v1. Cards are pasted manually.
- No UWG / L5 / Author-Gate runtime integration. This is a builder + linter, not a runtime agent.
- Every template must render under `StrictUndefined` — no silent missing-variable fallbacks.
- All generated card filenames are `<NN>_<UPPER_SLUG>.md`, zero-padded, matching the Drew pack convention.
- The router/linter is the SSOT for routing-manifest invariants. If the routing manifest evolves, the linter changes first, then the templates.

---

## Success Criteria

- [ ] `apps_qna` module exists, importable, with all six apps_* contract docs.
- [ ] 18 templates render cleanly from typed inputs.
- [ ] CLI builds a card pack from `--company / --role / --jd / --interviewers` inputs.
- [ ] Linter catches all 6 known invariant violations on negative fixtures.
- [ ] Three adapters consume real artifacts from `apps_research`, `apps_rg`, `apps_exec`.
- [ ] Drew Clements canary regenerates a structurally-equivalent 18-card pack from typed inputs.
- [ ] `pytest apps_qna/` green.

---

## Implementation Commands

```bash
# Wave 1
python -m apps_qna --help

# Wave 2 smoke
python -m apps_qna --interview synthetic-mini --company acme --role "Director of AI" \
  --jd apps_qna/tests/fixtures/synthetic_mini/jd.md \
  --interviewers apps_qna/tests/fixtures/synthetic_mini/interviewers.yaml \
  --output reports/qna/synthetic-mini

# Wave 3 lint
python -m apps_qna lint reports/qna/synthetic-mini

# Wave 5 Drew canary
pytest apps_qna/tests/test_drew_canary.py -v
```

---

## Rollback Strategy

If things go wrong:
1. `apps_qna` is a brand-new module — rollback is `rm -rf apps_qna && git checkout -- .windsurf/plans/apps-qna-bootstrap-c4f2a8.md`.
2. No existing apps_* are modified by this plan; integration adapters in Wave 4 are read-only against existing apps' artifacts.
3. No CI gates added; if a wave fails, halt at the wave boundary, fix-or-revert, do not proceed to the next wave.

---

## Acceptance Criteria

| Metric | Target | Verification |
|---|---|---|
| Templates render | 18/18 under StrictUndefined | `pytest apps_qna/tests/test_templates_render.py` |
| Linter coverage | 6/6 invariants enforced | `pytest apps_qna/tests/test_validators.py` |
| Adapter fidelity | 3/3 round-trip real artifacts | `pytest apps_qna/tests/test_adapters.py` |
| Drew canary | 18 cards, structurally equivalent | `pytest apps_qna/tests/test_drew_canary.py` |
| Module importable | `python -c "import apps_qna"` exit 0 | manual |

---

## Inputs From Other apps_*

| Source app | Artifact | Card source (becomes input to template) |
|---|---|---|
| `apps_research` | `reports/research/research_<mode>_<trace>.md` + `source_register_<trace>.json` | `CompanyBackground`, `RoleAreasOfFocus`, `IndustryTrends` (drives 04_company_overlay, 13_executive_fit) |
| `apps_research` | `reports/research/research_brief_<trace>.md` (interviewer-focused mode) | `InterviewerLens` (drives 03_executive_lens) |
| `apps_rg` | resume + STAR proofs from `reports/rg/` | `ExperiencePoint[]`, `StoryBank` (drives 14_star_bank, 16_cross_exam) |
| `apps_exec` | `reports/executive/exec_brief_<id>.md` | `ExecutiveFit` framing (drives 13_executive_fit) |
| User-provided | JD markdown / PDF text | `JDSections[]` (drives 04_company_overlay scoped sections) |
| User-provided | Interviewer profile YAML (name, title, public-statements, technical-depth, hot-buttons) | `Interviewer[]` (drives 03_executive_lens — one per interviewer for multi-interviewer mode) |

---

## Cascade Alignment Checks

- Plan saved at SSOT: `.windsurf/plans/apps-qna-bootstrap-c4f2a8.md`.
- plan_type=infra → §22 ADG graph-layer-evidence gate is correctly skipped (no refactor; new module bootstrap).
- Author-Gate emitted with confidence=0.88, gap=0.10, principle=runtime cards are the deliverable not the engine, precedent=none.
- Folder naming `apps_qna` (snake_case) enforced — `&` shell-hostility documented inline.
- All five waves stay inside the apps_qna module; no cross-cutting changes to agentic_core, ops_scripts, or other apps_*.
