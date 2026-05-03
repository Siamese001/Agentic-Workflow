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
| W1 | Topic-driven query decomposition + Tavily retrieval + reranker + wire `company_brief` mode | `apps_research/engines/company_brief_engine.py`, `apps_research/hop_pipeline.py`, retrieval wiring | W1 Discovery ✅, Impl 🔲 | ~26k 🟢 |
| W2 | URL-cited register + stat-table renderer + `role_profile` mode + parallel tool dispatch | `apps_research/outputs/*renderer.py`, new `role_profile` engine, parallel dispatch in orchestrator | 🔲 | ~22k 🟢 |
| W3 | `--reference-doc` PDF ingest (512-token chunks / 50 overlap) | new PDF ingest adapter, CLI flag, chunking primitive | 🔲 | ~10k 🟢 |
| W4 | `long_form` + `corporate_history` timeline + `pe_value_creation` + citation-density gate + contextual-retrieval prefix | new render modes, density-gate CI, contextual-retrieval prefix on all queries | 🔲 | ~26k 🟢 |

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
| P1.1 | Topic-driven query decomposition primitive | `apps_research/engines/query_decomposer.py` (new); `apps_research/config/agent_spec_config.py` | PP-1 no decomposition; GAP-R2 Anthropic-post params | ~5k | 🔲 TODO |
| P1.2 | Tavily retrieval adapter | new `apps_research/integrations/tavily_retrieval.py`; env `TAVILY_API_KEY`; MCP serialization compliance (§25) | PP-2 no external retrieval beyond local | ~5k | 🔲 TODO |
| P1.3 | Reranker wiring | reuse existing reranker from `apps_qna/router/reranker.py` via `apps_shared/` or new adapter | PP-3 relevance drift | ~4k | 🔲 TODO |
| P1.4 | Wire `company_brief` mode end-to-end | `apps_research/engines/company_brief_engine.py`, `apps_research/hop_pipeline.py` | fan_in=4 but mode not default-routable | ~6k | 🔲 TODO |
| P1.5 | ~~Prune G14 dead-code `ResearchRetrievalEngine`~~ — **DOWNGRADED to INVESTIGATION** | `apps_research/engines/research_retrieval_engine.py` | G14 verdict invalidated by GAP-R5 (14 `resolves_callsite` + 8 `emits_side_effect` in fresh snapshot); needs semantic-edge blast-radius analysis post-taxonomy-land | ~8k | 🔲 TODO — ⚠️ BLOCKED on GAP-R4 + GAP-R5 |
| P2.1 | URL-cited source register renderer | `apps_research/outputs/source_register_renderer.py` (new) | PP-4 no URL-level provenance | ~6k | 🔲 TODO |
| P2.2 | Stat-table renderer | `apps_research/outputs/stat_table_renderer.py` (new) | PP-5 no structured stat surface | ~5k | 🔲 TODO |
| P2.3 | `role_profile` mode | new engine + hop_pipeline entry | PP-6 no role-scoped output | ~6k | 🔲 TODO |
| P2.4 | Parallel tool dispatch in orchestrator | `apps_research/integrations/execution_adapter.py` | PP-7 sequential latency | ~5k | 🔲 TODO |
| P3.1 | `--reference-doc` CLI flag + PDF ingest adapter | `scripts/` or `apps_research/integrations/` (SSOT per §31) | PP-8 no exemplar-calibration path | ~6k | 🔲 TODO |
| P3.2 | 512-token chunk / 50 overlap chunker | reuse `apps_qna` chunker if present, else new | PP-9 chunk-size mismatch | ~4k | 🔲 TODO |
| P4.1 | `long_form` render mode | new output engine | PP-10 brief-only output | ~6k | 🔲 TODO |
| P4.2 | `corporate_history` timeline renderer | new output engine | PP-11 no temporal surface | ~6k | 🔲 TODO |
| P4.3 | `pe_value_creation` renderer | new output engine | PP-12 no PE-specific lens | ~6k | 🔲 TODO |
| P4.4 | Citation-density CI gate | new `ops_scripts/ci/check_research_citation_density.py` | PP-13 no density floor enforced | ~4k | 🔲 TODO |
| P4.5 | Contextual-retrieval prefix on all queries | all retrieval call sites | PP-14 no prefix → context drift | ~4k | 🔲 TODO |

**Status legend**: 🔲 TODO · 🔄 IN PROGRESS · ✅ DONE · ❌ BLOCKED

---

## Gap Register

**GAP-R1: Reconstructed plan lacks fine-grained P1.1–P1.5 implementation specs** — 🟡 **PARTIALLY CLOSED 2026-05-02 21:55**
- Original plan file lost before commit (never in git; created-then-deleted). Notion Summary field preserved wave-level themes + W1 Discovery inventory + retrieval-parameter research sources, but did NOT preserve per-phase acceptance criteria, exact file targets below the engine level, or the precise `full_w1_sequential` ordering rationale.
- Closure progress in this enrichment turn:
  1. ✅ Plan structure restored (frontmatter, Wave Structure, Phase-Level Summary, Out-Of-Scope, Rules, Rollback)
  2. ✅ ADG regenerated (closes GAP-R3 — all 6 engines present)
  3. ✅ Fresh fan-in inventory captured (exposes GAP-R5)
  4. 🔲 Per-phase `Commands` / `Acceptance` sections — tracked as **GAP-R6** (follow-on)
  5. 🔲 Precedent decision record `dec_19deb571135bac59c` not re-opened (deferred — not on blocker path)

**GAP-R2: Retrieval parameters not captured at phase-level**
- Anthropic multi-agent research post params, OpenAI Deep Research docs, and RAG consensus (chunk=512, overlap=50, contextual-retrieval prefix) are cited as sources but the specific numeric thresholds (top-k, rerank cutoff, query-decomposition fan-out) are not recorded.
- Impact: P1.1–P1.3 require either re-derivation from sources or precedent decision lookup before execution.

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

**GAP-R7: Invocation path for `apps_research/` is unclear** — 🔴 **NEW (discovered closing R5)**
- Zero module-import callers for ALL 6 engines means `apps_research/` is invoked via CLI, `__main__`, entry-point discovery, or dynamic import — NOT via `import apps_research.engines.X`.
- Before P1.4 wires `company_brief` end-to-end, we need to identify how users currently invoke `apps_research/` so the wiring happens at the right layer.
- Candidate inspection targets: `apps_research/scripts/run_research.py`, `apps_research/__main__.py` if exists, any `pyproject.toml` entry points, any CLI adapters in `apps_research/integrations/`.

**GAP-R6: P1.1–P4.5 acceptance criteria still missing** — 🔴 **FOLLOW-ON FROM GAP-R1**
- Closing GAP-R1 in this enrichment turn required only the high-level phase shape (captured). Per-phase Commands / Acceptance / test-paths still need authoring before any phase can execute. This is a known planning debt; not a blocker for documentation but is a blocker for code execution.

---

## Execution Plan

### Wave 1 — Retrieval + `company_brief` wiring

**Precondition**: taxonomy refactor committed OR stashed; ADG regenerated; GAP-R1/R2/R3 closed per reconstruction turn.

**Phase ordering**: `full_w1_sequential` (P1.1 → P1.2 → P1.3 → P1.4 → P1.5) per AG-1 precedent `dec_19deb571135bac59c` (conf=0.85, gap=0.30, 2026-05-02).

**Acceptance**: `company_brief` mode produces output on Blend360 reference query with Tavily-sourced URL citations ≥ baseline citation count; `ResearchRetrievalEngine` deleted; ADG violations count for `apps_research/` does not increase.

### Wave 2 — Rendering + `role_profile` + parallelism

**Precondition**: W1 committed.

**Acceptance**: URL-cited register + stat-table appear in `company_brief` output; `role_profile` mode callable end-to-end; parallel dispatch measurably reduces wall-clock on multi-query runs.

### Wave 3 — `--reference-doc` ingest

**Precondition**: W2 committed.

**Acceptance**: `python -m apps_research --reference-doc artifacts/blend_svp_clean.txt --mode company_brief --company Blend360` runs end-to-end; chunking produces 512-token chunks with 50-token overlap.

### Wave 4 — Long-form + density gate + contextual-retrieval

**Precondition**: W3 committed.

**Acceptance**: `long_form` / `corporate_history` / `pe_value_creation` modes callable; citation-density CI gate blocks PRs below floor; contextual-retrieval prefix applied to all retrieval call sites.

---

## Rules

- No `apps_research/` edits while `apps-folder-taxonomy-unification-b7d4e1` has uncommitted moves in the working tree.
- Every phase emits `DECISION_CAPTURED:` markers per constitutional §30 before completion.
- No edits until GAP-R1/R2/R3 are closed in a separate reconstruction turn.
- ADG regeneration mandatory before P1.5.
- Tavily calls honor MCP serialization (§25) — one remote MCP per response.
- Each phase landed as its own commit; no multi-phase commits.

---

## Success Criteria

- [ ] Plan enrichment turn closes GAP-R1/R2/R3 (acceptance criteria per phase, retrieval params, ADG regen)
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
