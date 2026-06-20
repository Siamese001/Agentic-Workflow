---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\apps-qna-intake-llm-extraction-b7d4f1.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\apps-qna-intake-llm-extraction-b7d4f1.md'
source_sha256: 12096721e3e0bbfb6cf3c983cef6f3dd68dfcb439ffaea18c7c9875b283ea014
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# apps_qna Wave 2 — LLM-driven Intake Extraction

**Slug**: `apps-qna-intake-llm-extraction-b7d4f1`
**Status**: not-started (scaffold only)
**Owner**: TBD
**Created**: 2026-04-30
**Parent**: Wave 1 of `apps_qna` intake architecture (delivered as commit at session)

> ⛔ Wave 1 (typed adapters + interactive wizard, no LLM) is the prerequisite. This
> plan is invalid to execute until the typed contracts in `apps_qna/integrations/`
> are stable for ≥1 week of usage.

## Goal

Replace heuristic PDF parsing in `apps_qna/integrations/from_research_brief.py`
with an LLM-driven extraction pipeline (Anthropic Claude API). The LLM
receives the full PDF text and emits a `ResearchInputs` payload directly —
including company_brief, role_areas_of_focus, industry_trends, per-interviewer
lenses, glossary entries, and a fully-attributed source register.

## Why this is its own wave

- **Ethics surface**: LLM-extracted content needs a disclosure stance. Are
  the cards now LLM-generated rather than analyst-curated? The candidate
  reads them aloud — are those still "their words"? Wave 0 ADR required.
- **Cost / latency**: PDF → typed YAML is ~50k tokens of input. At Claude
  Sonnet pricing that's $0.15-$0.50 per pack. Build is no longer free.
- **Determinism**: Same PDF → same YAML must hold for tests. Either temp=0
  with cached responses, or fixture-record-and-replay. Both add deps.
- **API key dep**: First Anthropic API key in `apps_qna`; need secrets
  handling consistent with rest of repo.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status |
|------|-----------|-------|------------:|--------|
| 0 | 0.1 | Disclosure ADR + cost/latency budget | 3000 | Todo |
| 1 | 1.1, 1.2 | Anthropic client wrapper + prompt design | 4000 | Todo |
| 2 | 2.1 | Determinism: response caching + fixture replay | 3000 | Todo |
| 3 | 3.1 | Swap from_research_brief PDF path to LLM | 2000 | Todo |
| 4 | 4.1 | Eval harness: 10 sample briefs vs gold YAML | 3000 | Todo |

**Total est. tokens**: ~15k

## Phase-Level Summary

| Phase ID | Title | Scope | Pain Points | Est. Tokens | Status |
|----------|-------|-------|-------------|------------:|--------|
| 0.1 | Disclosure ADR | `docs/architecture/adr/ADR-NNN-llm-pdf-extraction-disclosure.md` | Reconcile candidate-voice vs LLM-extracted content; do cards need a `[LLM-EXTRACTED]` provenance flag? | 3000 | Todo |
| 1.1 | Anthropic client | `apps_qna/integrations/_llm_client.py` (small wrapper around `anthropic` lib) | Secrets handling, env var contract, retry policy | 2000 | Todo |
| 1.2 | Extraction prompt | `apps_qna/integrations/prompts/research_brief_extraction.md` | Prompt the LLM to return strict JSON matching ResearchInputs schema; pydantic validation gate | 2000 | Todo |
| 2.1 | Cache layer | `apps_qna/integrations/_llm_cache.py` (SHA256 of PDF → cached JSON) | Determinism for tests; cache eviction policy | 3000 | Todo |
| 3.1 | Adapter swap | `apps_qna/integrations/from_research_brief.py` gets `--use-llm` flag | Backwards compat with heuristic mode; no behavior change for non-LLM callers | 2000 | Todo |
| 4.1 | Eval harness | `apps_qna/tests/eval/llm_extraction_eval.py` + 10 fixture pairs | Need to hand-author 10 (PDF, gold ResearchInputs YAML) pairs | 3000 | Todo |

## Gap Register

- **G-LLM-1**: Anthropic API key handling — does this repo have a pattern? (Check `.env.example`.)
- **G-LLM-2**: Cost ceiling — should the wizard refuse to run if a single PDF would cost > $X?
- **G-LLM-3**: Disclosure UX — does the produced `interview.yaml` need an `extraction_method: llm` field that surfaces in cards 18+?
- **G-LLM-4**: Eval gold pairs require real briefings; sourcing without leaking confidential candidate info is non-trivial.

## Dependencies

- Wave 1 (typed adapters) — must be delivered and stable
- `anthropic` Python lib (new dep)
- Existing `apps_qna.types.qna_types.ResearchInputs` schema (frozen)

## Out-of-Scope (NEXT_STEP)

- Multi-LLM provider abstraction (Anthropic only for v1)
- Streaming extraction with mid-flight UX (batch only)
- Fine-tuning on the user's own briefings
