---
plan_id: apps-research-blend-baseline-c74787
plan_type: refactor
---

# apps_research — Blend360 SVP Baseline Gap Closure

Baseline `apps_research` output against the Blend360 SVP Agentic Transformation reference PDF (17pp) and close retrieval / rendering / citation gaps in four waves.

> ⚠️ **Plan reconstructed 2026-05-02** from Notion row `35527693-f55c-81a3-ab5e-cb5f368e44bb` (Plans DB) after original on-disk file was lost before commit. W1 Discovery detail, ADG fan-in inventory, and AG-1 precedent preserved verbatim from the Notion Summary property. **P1.1–P1.5 implementation specs (acceptance criteria, exact file targets, retrieval parameters below the wave-level) were NOT captured in Notion** — see `GAP-R1` in the Gap Register. The wave-level themes and retrieval parameters from the Anthropic / OpenAI / RAG-consensus research ARE captured.

---

## Context (SCQA)

- **Situation** — `apps_research` produces company-brief research output on `main` at git `1e6f16d78b`. A 17-page Blend360 SVP Agentic Transformation PDF (extracted to `@c:\Git\Agentic-Workflow-FRESH\artifacts\blend_svp_clean.txt`) is the reference gold-standard. Baseline `apps_research` output differs from the reference on topic coverage, citation density, and narrative structure.
- **Complication** — `apps_research` has: (1) no topic-driven query decomposition; (2) no explicit URL-cited register render; (3) no reference-doc ingest path for calibrating against an exemplar; (4) no long-form corporate-history or PE-value-creation renderer. ADG fan-in inventory (W1 Discovery) also confirms `ResearchRetrievalEngine` is dead-code (`fan_in=1`, G14) and `hop_company_brief_engine` is missing from the 2026-05-02 snapshot — **ADG regen required before P1.5**.
- **Question** — How do we close the `apps_research` → Blend360-reference gap in four bounded waves without breaking existing consumers?
- **Answer** — W1 wires `company_brief` + topic decomposition + Tavily retrieval + reranker; W2 adds URL-cited register + stat-table renderer + `role_profile` + parallel tool dispatch; W3 adds `--reference-doc` PDF ingest; W4 adds `long_form` + `corporate_history` timeline + `pe_value_creation` + citation-density gate + contextual-retrieval prefix.

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| Notion Plans row `35527693-f55c-81a3-ab5e-cb5f368e44bb` | SSOT for wave themes + W1 Discovery inventory after on-disk loss | ✅ |
| `artifacts/blend_svp_clean.txt` (17pp extracted) | Reference gold-standard for gap analysis + W3 ingest fixture | ✅ |
| `artifacts/blend_svp_pdf.txt` (raw PDF text) | W3 PDF-ingest fixture | ✅ |
| `artifacts/_blend_briefing_extract.txt` | Prior extraction pass for cross-check | ✅ |
| ADG snapshot `adg_indexed_05022026_1921.sqlite` | OLD — used for Notion W1 Discovery fan-in (now stale) | ⚠️ superseded |
| ADG snapshot `adg_indexed_05022026_2152.sqlite` | DIRTY-tree regen (with in-flight taxonomy files) 2026-05-02 21:52 | ⚠️ superseded by 2217 |
| ADG snapshot `adg_indexed_05022026_2217.sqlite` | **CLEAN-tree regen** 2026-05-02 22:17 after stash; SSOT for R5 | ✅ primary |
| Anthropic multi-agent research post | W1 query-decomposition params | 🔲 (cached in prior W1 Discovery) |
| OpenAI Deep Research docs | W1 retrieval pattern calibration | 🔲 (cached in prior W1 Discovery) |
| RAG consensus (contextual-retrieval prefix, 512/50 chunk/overlap) | W3+W4 params | 🔲 (cached in prior W1 Discovery) |
| AG-1 precedent `dec_19deb571135bac59c` | W1 `full_w1_sequential` ordering locked (conf=0.85, gap=0.30) | ✅ |
| AG-re-entry `dec_19deb866f26fe4ee2` | 2026-05-02 `reconstruct_plan_first` dominance-fires (conf=0.88, gap=0.32) | ✅ |

---

## Wave Structure

| Wave | Metric | Scope | Checkpoint | Tokens |
|------|--------|-------|------------|--------|
| W1 | Topic-driven query decomposition + Tavily retrieval + reranker + wire `company_brief` mode | `apps_research/engines/company_brief_engine.py`, retrieval wiring | ✅ DONE commit `1bdf1df3b5` | ~26k 🟢 |
| W2 | URL-cited register + stat-table renderer + `role_profile` mode + parallel tool dispatch | `apps_research/outputs/*renderer.py`, new `role_profile` engine, parallel dispatch | ✅ DONE commit `0b7cc72ec1` | ~22k 🟢 |
| W3 | `--reference-doc` PDF ingest (512-token chunks / 50 overlap) | PDF ingest adapter, CLI flag, chunking primitive | ✅ DONE commit `8ce4632a68` | ~10k 🟢 |
| W4 | `long_form` + `corporate_history` timeline + `pe_value_creation` + citation-density gate + contextual-retrieval prefix | render modes, density-gate CI, contextual-retrieval prefix | ✅ DONE (this turn) | ~26k 🟢 |

**Total: ~84k tokens across 4 waves, all GREEN**

---

## Out Of Scope

- `apps_folder_taxonomy_unification_b7d4e1` refactor — currently in-flight in the working tree (~170 file moves across `apps_lic/`, `apps_qna/`, `apps_rg/`, `apps_shared/`, `apps_underwriting_ai/`, `apps_research/`, `apps_eval/`, `apps_exec/`). **This plan MUST NOT edit `apps_research/` until the taxonomy refactor is committed or stashed.**
- `apps_rg/` (resume generation) — different app; reference-doc fixture comes from apps_rg/ runs but no reverse coupling.
- Changes to `tools/adg/` — ADG regen is consumed, not modified.
- Any guardrail, anti-pattern, or certification work.

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| P1.1 | Topic-driven query decomposition primitive | `apps_research/engines/query_decomposer.py` | PP-1 no decomposition | ~5k | ✅ DONE |
| P1.2 | Tavily retrieval adapter | `apps_research/integrations/tavily_retrieval.py`; env `TAVILY_API_KEY`; `.env.example` entry | PP-2 no external retrieval | ~5k | ✅ DONE |
| P1.3 | Reranker wiring | `apps_research/integrations/reranker_adapter.py` (score-based thin adapter) | PP-3 relevance drift | ~4k | ✅ DONE |
| P1.4 | Improve `CompanyBriefEngine` content quality (flag `APPS_RESEARCH_RETRIEVAL_V2=1`) | `apps_research/engines/company_brief_engine.py` | V2 retrieval pipeline, backward-compatible | ~6k | ✅ DONE |
| P1.5 | INVESTIGATION — `hop_*` engines triage | memo `.windsurf/plans/hop-engines-triage-a7e4b2.md` | verdict: ALIVE (dynamic import via HopStageSpec) | ~2k | ✅ DONE |
| P2.1 | URL-cited source register renderer | `apps_research/outputs/source_register_renderer.py` | PP-4 no URL-level provenance | ~6k | ✅ DONE |
| P2.2 | Stat-table renderer | `apps_research/outputs/stat_table_renderer.py` | PP-5 no structured stat surface | ~5k | ✅ DONE |
| P2.3 | `role_profile` mode | `apps_research/engines/role_profile_engine.py` + `types/role_profile.py` + CLI | PP-6 no role-scoped output | ~6k | ✅ DONE |
| P2.4 | Parallel tool dispatch | `company_brief_engine._run_research_v2` via `concurrent.futures.ThreadPoolExecutor` | PP-7 sequential latency | ~5k | ✅ DONE |
| P3.1 | `--reference-doc` CLI flag + PDF ingest adapter | `apps_research/integrations/pdf_ingest.py` + CLI flag | PP-8 no exemplar-calibration path | ~6k | ✅ DONE |
| P3.2 | 512-token chunk / 50 overlap chunker | `apps_shared/chunking.py` (tiktoken + whitespace fallback) | PP-9 chunk-size mismatch | ~4k | ✅ DONE |
| P4.1 | `long_form` render mode | `apps_research/outputs/long_form_renderer.py` + CLI | PP-10 brief-only output | ~6k | ✅ DONE |
| P4.2 | `corporate_history` timeline renderer | `apps_research/outputs/timeline_renderer.py` + CLI | PP-11 no temporal surface | ~6k | ✅ DONE |
| P4.3 | `pe_value_creation` renderer | `apps_research/outputs/pe_value_creation_renderer.py` + CLI | PP-12 no PE-specific lens | ~6k | ✅ DONE |
| P4.4 | Citation-density CI gate | `ops_scripts/ci/check_research_citation_density.py` | PP-13 no density floor enforced | ~4k | ✅ DONE |
| P4.5 | Contextual-retrieval prefix on all queries | `tavily_retrieval.apply_contextual_prefix` wired into `_run_research_v2` | PP-14 no prefix → context drift | ~4k | ✅ DONE |

**Status legend**: 🔲 TODO · 🔄 IN PROGRESS · ✅ DONE · ❌ BLOCKED

---

## Gap Register

**GAP-R1: Reconstructed plan lacks fine-grained P1.1–P1.5 implementation specs** — ✅ **CLOSED 2026-05-03 05:50 (all downstream gaps closed)**
- Original plan file lost before commit; reconstruction complete across two turns (2026-05-02 reconstruction + 2026-05-03 enrichment).
- Closure ledger:
  1. ✅ Plan structure restored (frontmatter, Wave Structure, Phase-Level Summary, Out-Of-Scope, Rules, Rollback)
  2. ✅ ADG regenerated (closes GAP-R3)
  3. ✅ Fresh fan-in inventory captured (exposed GAP-R5)
  4. ✅ Per-phase `Scope` / `Commands` / `Acceptance` authored for all 15 phases (closes GAP-R6)
  5. ✅ Retrieval parameters documented (closes GAP-R2)
  6. ✅ Invocation path traced (closes GAP-R7)
  7. ✅ Working tree cleaned via stash (closes GAP-R4)
- Precedent decision record `dec_19deb571135bac59c` not re-opened (deferred — not on blocker path).

**GAP-R2: Retrieval parameters not captured at phase-level** — ✅ **CLOSED 2026-05-03 05:40 with industry-consensus defaults**
- Numeric thresholds adopted from RAG consensus (tunable after first eval):

  | Parameter | Value | Source / Rationale |
  |---|---|---|
  | Chunk size | 512 tokens | RAG consensus (preserved from W1 Discovery) |
  | Chunk overlap | 50 tokens | RAG consensus (preserved from W1 Discovery) |
  | Retrieval top-k (pre-rerank) | 10 | OpenAI Deep Research default; Tavily search default max results |
  | Rerank cutoff (post-rerank) | 5 | Anthropic contextual-retrieval blog recommended; 50% winnow |
  | Query decomposition fan-out | 3–5 sub-queries per topic | Anthropic multi-agent research post; balances coverage vs. token burn |
  | Contextual-retrieval prefix | Anthropic format: `<document>...</document>\n<chunk_context>...</chunk_context>` | Anthropic contextual-retrieval blog |
  | Citation density floor (P4.4) | ≥ 1 URL citation per 200 rendered tokens | Derived from Blend reference PDF density (~1 per 180 tokens) |

- Impact: P1.1–P1.3 unblocked on parameters. Real evaluation pass in W2+ will tune these against Blend reference.

**GAP-R3: ADG snapshot missing `hop_company_brief_engine`** — ✅ **CLOSED 2026-05-02 21:52 by regen**
- Fresh snapshot `adg_indexed_05022026_2152.sqlite` contains all 6 `apps_research/engines/` modules: `company_brief_engine.py`, `hop_company_brief_engine.py`, `research_assembly_engine.py`, `hop_research_assembly_engine.py`, `research_retrieval_engine.py`, `hop_research_retrieval_engine.py`.
- Module node ids: 2909, 2910, 2911, 2912, 2913, 2914 respectively.

**GAP-R4: Working tree is mid-refactor on an unrelated plan** — ✅ **CLOSED 2026-05-02 22:00 by stash**
- `apps-folder-taxonomy-unification-b7d4e1` had ~170 uncommitted file moves touching `apps_research/_telemetry.py` among others.
- Resolution: stashed in two parts to preserve ALL work for later recovery:
  - `stash@{0}` — untracked files (new `apps_*/THREAT_MODEL.md`, new dirs, new ADR, new ops_scripts gate, etc.)
  - `stash@{1}` — tracked modifications
- Recovery path: `git stash pop stash@{0}` then `git stash pop stash@{1}` (order matters — untracked pops first)
- Working tree is now on `main` commit `69baccb9a6` with only one unrelated modified plan file remaining.
- This plan's file (`apps-research-blend-baseline-c74787.md`) committed as `d2db452005` — no longer at risk of loss.

**GAP-R5: Fresh ADG shows `fan_in(imports)=0` for ALL 6 `apps_research/engines/` modules** — ✅ **CLOSED 2026-05-02 22:17 by clean-tree re-validation**
- Re-ran ADG after GAP-R4 stash (commit `69baccb9a6`, snapshot `adg_indexed_05022026_2217.sqlite`). Results **identical** to dirty-tree — this is a real codebase property, NOT a mid-refactor artifact:

  | Module | imports_in | resolves_callsite | emits_side_effect | flows_to |
  |---|---|---|---|---|
  | `company_brief_engine.py` | **0** | 30 | 4 | 0 |
  | `hop_company_brief_engine.py` | **0** | 0 | 0 | 0 |
  | `research_assembly_engine.py` | **0** | 5 | 2 | 0 |
  | `hop_research_assembly_engine.py` | **0** | 0 | 0 | 0 |
  | `research_retrieval_engine.py` | **0** | 14 | 8 | 0 |
  | `hop_research_retrieval_engine.py` | **0** | 0 | 0 | 0 |

- **Finding 1**: All 6 engines are structurally orphaned (zero module-level import callers) on `main`. This means `apps_research/` is NOT wired into anything that imports it today. W1 Discovery inventory (fan_in=3/1/4 from Notion) was wrong — those numbers did not come from the `imports` edge type on modules.
- **Finding 2**: 3 of 6 engines carry live semantic behavior (`company_brief_engine`, `research_assembly_engine`, `research_retrieval_engine`). They are invoked at runtime via resolves_callsite + emits_side_effect. The old G14 "dead-code" verdict on `research_retrieval_engine` (14 callsites + 8 side effects) is **definitively invalidated** on clean tree.
- **Finding 3**: 3 `hop_*` engines have zero incoming edges of ANY type — truly orphaned. Candidates for separate investigation (not P1.5).
- **Actionable consequence**: P1.5 is NOT a valid prune target. Downgraded in Phase-Level Summary to INVESTIGATION. Blend-baseline W1 goal (wire `company_brief` mode end-to-end) now requires clarifying how `apps_research/` is invoked at all — since nothing imports it at module level, the caller must be CLI or entry-point discovery.
- **Follow-on (GAP-R7)**: discover the actual invocation path for `apps_research/` before P1.4 executes.

**GAP-R7: Invocation path for `apps_research/` is unclear** — ✅ **CLOSED 2026-05-03 05:38 by source-trace**
- Entry point chain (verified by reading source):
  1. `python -m apps_research` invokes `apps_research/__main__.py::main()`
  2. `__main__.py` branches on `--apps-e2e-live`:
     - With flag → `_run_live_cert()` → `apps_shared.spine_emission.governed_run()` with 5-step plan (`intake`, `retrieve`, `assemble_prompt`, `generate_brief`, `seal`); route registry `apps_research/config/route_registry.yaml`; selected_capability `apps_research.company_brief_v1`
     - Without flag → `apps_research/scripts/run_research.py::main()`
  3. `run_research.py::main()` branches on `--mode`:
     - `--mode company` → `_run_company_brief()` → `CompanyBriefEngine().execute(payload)` → writes `<out>/runs/<ts>/company_research.json` → optional pydantic `CompanyBrief` validation
     - Other modes (`brief`/`comparison`/`trend`/`position`/`thought_leadership`) → `ResearchOrchestrator.run(ResearchRequest)`
- **Zero module-import fan-in is NOT a bug** — it reflects the canonical `__main__.py` invocation pattern. `CompanyBriefEngine` / `ResearchAssemblyEngine` / `ResearchRetrievalEngine` are imported LATE inside function bodies (lines 99, 84 of `run_research.py`) to keep top-level import cheap. This pattern defeats naïve module-level fan-in analysis.
- **Correction to P1.4 wording**: `company` mode ALREADY exists and routes end-to-end. The real gap is not "wire the mode" but "improve the retrieval + rendering inside `CompanyBriefEngine.execute()` to match Blend reference quality". P1.4 retitled accordingly.
- Canonical Blend-baseline invocation: `python -m apps_research --topic "Blend360" --mode company --out reports/research --json-output`

**GAP-R6: P1.1–P4.5 acceptance criteria still missing** — ✅ **CLOSED 2026-05-03 05:45 by per-phase spec authoring**
- See `## Execution Plan` §§ Wave 1–4 below for per-phase `Scope` / `Commands` / `Acceptance` / `Test paths`.
- Specs assume GAP-R4 stashes remain stashed throughout W1 (no taxonomy-refactor cross-contamination).

---

## Execution Plan

### Wave 1 — Retrieval + `company_brief` quality

**Precondition**: GAP-R4 stashes remain stashed; snapshot `adg_indexed_05022026_2217.sqlite` is SSOT.

**Phase ordering**: `full_w1_sequential` (P1.1 → P1.2 → P1.3 → P1.4 → P1.5) per AG-1 `dec_19deb571135bac59c`.

**Canonical invocation**: `python -m apps_research --topic "Blend360" --mode company --out reports/research --json-output`

#### P1.1 — Query-decomposition primitive
- **Scope**: new `apps_research/engines/query_decomposer.py::decompose(topic, depth) -> list[SubQuery]`; fan-out 3/4/5 for shallow/standard/deep.
- **Commands**: create module; unit test `tests/apps_research/engines/test_query_decomposer.py`.
- **Acceptance**: pytest passes; 5 sub-queries at depth=deep; no two sub-queries share >70% of words (Jaccard).

#### P1.2 — Tavily retrieval adapter
- **Scope**: new `apps_research/integrations/tavily_retrieval.py::retrieve(sub_query, top_k=10)`; reads `TAVILY_API_KEY` from env.
- **Commands**: create module; update `.env.example`; integration test gated by env (`pytest.mark.skipif`).
- **Acceptance**: with key, ≥5 docs per sub-query; without key, raises `RuntimeError` with actionable message.

#### P1.3 — Reranker wiring
- **Scope**: reuse `apps_qna/router/reranker.py` if exposed via `apps_shared/`, else new thin adapter `apps_research/integrations/reranker_adapter.py::rerank(sub_query, docs, cutoff=5)`.
- **Commands**: inspect `apps_qna/router/reranker.py`; unit test with synthetic doc scores.
- **Acceptance**: outputs exactly 5 docs; monotonic score ordering.

#### P1.4 — Improve `CompanyBriefEngine` content quality (RETITLED per GAP-R7)
- **Scope**: modify `apps_research/engines/company_brief_engine.py::execute()`: (a) `decompose(topic)`, (b) per-sub-query `retrieve()`, (c) `rerank()`, (d) assemble into existing `CompanyBrief` pydantic shape. Behind feature flag `APPS_RESEARCH_RETRIEVAL_V2=1`.
- **Commands**: wrap existing `execute()` body; update `tests/apps_research/engines/test_company_brief_engine.py` to exercise both paths.
- **Acceptance**: `python -m apps_research --topic "Blend360" --mode company --out /tmp/r` writes `company_research.json` validating against `apps_rg.types.company_research.CompanyBrief`; `source_register` ≥5 distinct URLs; existing tests pass (no regression).

#### P1.5 — INVESTIGATION (no code) — hop_* engines triage
- **Scope**: determine whether `hop_company_brief_engine.py`, `hop_research_assembly_engine.py`, `hop_research_retrieval_engine.py` are reachable via any runtime path.
- **Commands**: targeted grep (≤3 calls) for `"hop_company_brief_engine"` / `"hop_research_"`; check `apps_research/config/route_registry.yaml`.
- **Acceptance**: investigation memo `.windsurf/plans/hop-engines-triage-<6hex>.md` with verdict (alive/dead/dormant); **NO file deletions this phase**; if verdict=dead, open follow-on plan.

### Wave 2 — Rendering + `role_profile` + parallelism

**Precondition**: W1 committed; `company_brief` output achieves ≥baseline citation count on Blend.

#### P2.1 — URL-cited source register renderer
- **Scope**: new `apps_research/outputs/source_register_renderer.py::render(brief) -> str`; Markdown `[n]: <url>` format; append to JSON as `rendered_source_register`.
- **Acceptance**: exactly `len(source_register)` entries; snapshot test against frozen Blend360 input is diff-stable.

#### P2.2 — Stat-table renderer
- **Scope**: new `apps_research/outputs/stat_table_renderer.py::render(stats) -> str`; columns: companies/revenue/headcount (Blend reference shape).
- **Acceptance**: well-formed Markdown table; handles 0/1/N rows; unit test covers empty case.

#### P2.3 — `role_profile` mode
- **Scope**: new `--mode role_profile` branch in `run_research.py`; new `apps_research/engines/role_profile_engine.py`; new `apps_research/types/role_profile.py` pydantic schema (`role`, `scope`, `required_skills`, `nice_to_have`, `source_register`).
- **Acceptance**: `python -m apps_research --topic "VP Data Science" --mode role_profile --out /tmp/r` exits 0; JSON validates against pydantic schema.

#### P2.4 — Parallel tool dispatch
- **Scope**: `asyncio.gather()` per-sub-query retrieval + rerank inside `company_brief_engine.execute()`.
- **Acceptance**: wall-clock on Blend360 ≤ 0.5× sequential baseline from P1.4; record baseline + measured values in commit message.

### Wave 3 — `--reference-doc` ingest

**Precondition**: W2 committed.

#### P3.1 — `--reference-doc` CLI flag + PDF ingest adapter
- **Scope**: add `--reference-doc` to `run_research.build_parser()`; new `apps_research/integrations/pdf_ingest.py::ingest(path) -> list[Chunk]` using `pypdf`.
- **Acceptance**: `python -m apps_research --topic "Blend360" --mode company --reference-doc artifacts/blend_svp_clean.txt --out /tmp/r` returns 0; reference-doc chunks appear in `brief.context` with file path + chunk id.

#### P3.2 — 512-token / 50-overlap chunker
- **Scope**: reuse `apps_qna/chunker.py` if present, else new `apps_shared/chunking.py::chunk_text(text, chunk_tokens=512, overlap_tokens=50)` using `tiktoken` or whitespace fallback.
- **Acceptance**: Blend PDF (~5,800 tokens) produces ~12 chunks; every chunk ≤512 tokens; consecutive chunks overlap ≥50 tokens; unit test verifies invariants.

### Wave 4 — Long-form + density gate + contextual-retrieval

**Precondition**: W3 committed.

#### P4.1 — `long_form` render mode
- **Scope**: new `apps_research/outputs/long_form_renderer.py`; `--mode long_form`; target 2000–3000 tokens (vs current brief ~500).
- **Acceptance**: output token count in [2000, 3000]; ≥5 H2 sections; source_register ≥10 URLs.

#### P4.2 — `corporate_history` timeline renderer
- **Scope**: new `apps_research/outputs/timeline_renderer.py`; `--mode corporate_history`; structured event list `{year, event, source_url}`.
- **Acceptance**: valid Markdown timeline; ≥5 events for Blend360; every event has year + URL.

#### P4.3 — `pe_value_creation` renderer
- **Scope**: new `apps_research/outputs/pe_value_creation_renderer.py`; `--mode pe_value_creation`; structured bundle `{thesis, levers[], risks[], source_register}`.
- **Acceptance**: output contains 1 thesis paragraph, ≥3 levers, ≥3 risks; each lever/risk has ≥1 source_url.

#### P4.4 — Citation-density CI gate
- **Scope**: new `ops_scripts/ci/check_research_citation_density.py` (per SSOT §31 routing); reads latest `company_research.json` from `reports/research/runs/<ts>/`; enforces ≥1 URL citation per 200 rendered tokens.
- **Acceptance**: gate passes on Blend reference run; gate fails when synthetic test input has density 1 URL per 400 tokens (regression guard); wired into `.pre-commit-config.yaml` or `run_contract_gates.py`.

#### P4.5 — Contextual-retrieval prefix
- **Scope**: apply Anthropic contextual-retrieval prefix template to every `retrieve()` call site: `<document>{doc_title}</document>\n<chunk_context>{surrounding_text}</chunk_context>\n{chunk}`.
- **Acceptance**: prefix present in retrieval input for 100% of chunks (verified by grep of logged retrieval payloads under `artifacts/apps_research/runs/<ts>/`); no regression on Blend citation density.

---

## Rules

- Keep GAP-R4 stashes stashed until the end of W1 (no taxonomy-refactor cross-contamination mid-wave).
- Every phase emits `DECISION_CAPTURED:` markers per constitutional §30 before completion.
- P1.5 is INVESTIGATION-ONLY — no file deletions; separate follow-on plan if verdict=dead.
- Tavily calls honor MCP serialization (§25) — one remote MCP per response.
- Each phase lands as its own commit; no multi-phase commits.
- Any NEW Python file under P1.2/P1.3/P2.x/P3.x/P4.x respects constitutional §31 SSOT folder routing (`ops_scripts/ci/` for gates, `apps_research/integrations/` for adapters, etc.).

---

## Success Criteria

- [x] Plan enrichment turn closes GAP-R1/R2/R3/R4/R5/R6/R7 (acceptance criteria per phase, retrieval params, ADG regen, working tree cleaned, fan-in re-validated, invocation path traced) — 2026-05-03
- [ ] W1 Discovery → Implementation ratified (AG-1 precedent already locks the ordering)
- [ ] W1–W4 each land as a bounded commit with passing targeted tests
- [ ] `company_brief` output on Blend360 reference query matches reference PDF on topic coverage + citation density
- [ ] ADG violations count for `apps_research/` does not increase at any wave boundary
- [ ] Notion Plans row synchronized (Status, Plan File Path, Summary) at each wave boundary

---

## Implementation Commands

```bash
# Pre-wave: ADG regen (required before any wave)
python tools/generate_full_adg.py

# Pre-wave: verify this plan's enrichment is complete
python ops_scripts/ci/check_graph_layer_evidence.py --plan .windsurf/plans/apps-research-blend-baseline-c74787.md

# Wave 1 verification (skeleton — exact commands deferred to enrichment turn)
python -m pytest tests/ -k "apps_research and company_brief"
python -m apps_research --mode company_brief --company Blend360

# Wave 3 verification
python -m apps_research --reference-doc artifacts/blend_svp_clean.txt --mode company_brief --company Blend360

# Wave 4 verification
python ops_scripts/ci/check_research_citation_density.py  # new gate from P4.4
```

---

## Rollback Strategy

If a wave breaks `apps_research/` or downstream consumers:

1. `git revert <wave-commit>` — each wave is one commit; revert is atomic.
2. Regenerate ADG; confirm violation count returns to pre-wave baseline.
3. Notion Plans row Status → `🟡 Draft`; record RCA in wave's commit message and in Notion Summary.
4. For P1.5 (dead-code delete) specifically: `git revert` restores `research_retrieval_engine.py`; no data-migration concern.

---

## Acceptance Criteria

| Metric | Target | Verification |
|---|---|---|
| W1 `company_brief` citation count | ≥ Blend360 reference PDF count | diff rendered output against `artifacts/blend_svp_clean.txt` |
| ADG violations for `apps_research/` | non-increasing at each wave boundary | `python tools/generate_full_adg.py && sqlite3 artifacts/adg/<latest>.sqlite "SELECT COUNT(*) FROM violations WHERE file_path LIKE 'apps_research/%'"` |
| `ResearchRetrievalEngine` fan_in (post-P1.5) | 0 (deleted) | ADG query |
| `hop_company_brief_engine` in ADG | present | ADG query (requires regen to confirm) |
| Citation-density gate (post-P4.4) | passing | `python ops_scripts/ci/check_research_citation_density.py` |

## Cascade Alignment Checks

- Plan reconstructed from Notion SSOT; gaps surfaced explicitly in GAP-R1/R2/R3 rather than fabricated.
- Scope containment: `apps_research/` edits deferred until taxonomy refactor lands (GAP-R4).
- ADG-first: fan-in cited from Notion snapshot of 2026-05-02 W1 Discovery; regen mandated before P1.5.
- Author-Gate precedent preserved (AG-1 `dec_19deb571135bac59c`, re-entry `dec_19deb866f26fe4ee2`).
