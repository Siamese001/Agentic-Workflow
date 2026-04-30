# apps_qna RAG/Skills Alignment

**Slug**: `apps-qna-rag-skills-alignment-7d2c4e`
**Status**: in-progress
**Owner**: Cascade
**Created**: 2026-04-30
**Parent**: `apps-qna-bootstrap-c4f2a8` (Waves 1-3 complete)

## Goal

Extend the bootstrapped `apps_qna` card-pack builder with the gaps surfaced by:
1. **Anthropic Research Briefing for Interviews** PDF (technical philosophy, alignment, agentic best practices)
2. **Claude RAG Rules and Skills** PDF (Rules vs Skills, progressive disclosure, source register, learnings loop)
3. Web research on agentic frameworks for live interview Q&A (ethics, principle-anchored STAR, real-time copilot architecture)

Scope is **prep-time only**. Real-time copilot architecture is an explicitly-deferred NEXT_STEP.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|------------:|-------------|--------|------------------|
| 0 | 0.1 | Ethics & disclosure card | 1500 | Card 18 always-on; README documents prep-vs-copilot stance | Done | Card 18 emitted, README states prep-tool stance |
| 1 | 1.1 | Rules vs Skills frontmatter + paste strategy | 2000 | YAML frontmatter prepended to every card via include | Done | Every card has `card_type` and `priority` keys |
| 2 | 2.1 | Source register card + inline-citation discipline | 2000 | Card 19 always-on; citation patterns in header | Done | Card 19 emitted; cited sources section |
| 3 | 3.1 | Glossary + Likely Questions cards | 2500 | Cards 20, 21 always-on | Done | Cards 20, 21 emitted with content |
| 4 | 4.1 | LINT-7 token budget + research map enrichment | 1500 | Per-card word cap 1500; LINT-7 added to runner | Done | LINT-7 reports per-card word count; runner integrates |
| 5 | 5.1 | Learnings card + self-eval CLI + pathology taxonomy | 2500 | Card 22 always-on; `self-eval` subcommand on CLI | Done | Card 22 emitted; `run_qna self-eval` works |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|------------:|--------|
| 0.1 | Ethics & Disclosure | `templates/18_ethics_and_disclosure.md.j2`, `builder.card_pack_builder._CARDS`, `validators.route_coverage._ALWAYS_ON_PREFIXES`, `README.md` | Distinguish prep vs real-time copilot | 1500 | Done |
| 1.1 | Card metadata frontmatter | `templates/_card_metadata.md.j2`, every numbered template, `validators.header_consistency` (extend to check frontmatter) | Rules vs Skills semantics; paste order | 2000 | Done |
| 2.1 | Source register card | `templates/19_source_register.md.j2`, `validators.route_coverage`, README §citations | Inline `[S#]` citation grammar | 2000 | Done |
| 3.1 | Glossary + Likely Questions | `templates/20_glossary.md.j2`, `templates/21_likely_questions.md.j2`, `qna_types.py` (GlossaryEntry, LikelyQuestion) | Predicted-questions seeding from JD+role+research | 2500 | Done |
| 4.1 | LINT-7 token budget | `validators/token_budget.py`, `validators/runner.py`, `04_company_overlay.md.j2` enrichment | Word-count cap (1500/card) | 1500 | Done |
| 5.1 | Learnings + self-eval CLI | `templates/22_learnings.md.j2`, `scripts/run_qna.py` (self-eval subcommand), `apps_qna/PATHOLOGY_TAXONOMY.md` | Manifest delta computation; pathology checklist | 2500 | Done |

## Gap Register

- **G1**: No ethics/disclosure card → prep-tool boundary unclear (Wave 0)
- **G2**: No Rules vs Skills classification → paste-order ambiguity (Wave 1)
- **G3**: Source register only inline in card 04 → no first-class card; no citation grammar (Wave 2)
- **G4**: No glossary or predicted-questions cards → runtime cold-start cost is high (Wave 3)
- **G5**: No token-budget linter → packs can balloon silently (Wave 4)
- **G6**: No post-rehearsal learnings loop → no self-improvement signal (Wave 5)

## Out-of-Scope (NEXT_STEP)

- Real-time copilot companion app architecture
- Audio rehearsal integration
- Per-card embedding-based retrieval router (current model is paste-time, not runtime)

## Verification

- `python -m pytest apps_qna/tests -p no:xdist -o addopts=""` → all green
- `python -m apps_qna build --interview <fixture> --output <out>` → emits 23 cards
- `python -m apps_qna lint <out>` → no errors

## Provenance

ADG Provenance: not applicable — apps_qna is a self-contained app module; no cross-layer refactoring.
