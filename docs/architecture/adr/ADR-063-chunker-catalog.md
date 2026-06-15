# ADR-063 — Chunker Catalog: Per-Source Strategies + Parent-Document Lineage

**Status**: Accepted (implemented; catalog seed landed)
**Date**: 2026-04-24
**Deciders**: Agentic-Workflow maintainers
**Impact Layers**: `tools/ingestion/`, `tools/generate/ingestion/`, `agentic_core/knowledge/canonical/chunk_manifest.py`, `agentic_core/knowledge/retrieval/parent_child_hydrator.py`
**Plan**: `.windsurf/plans/chromadb-best-in-class-agentic-embeddings-c4a1f8.md` W6.1
**Relates-to**: ADR-045 (contextual retrieval), ADR-055 (provenance), ADR-056 (multi-head), ADR-059 (embedding-cosine semantic chunking)

**Current-state note (2026-06-15):** `tools/ingestion/chunker_catalog.py` now provides the source-kind registry, markdown header lineage, Python thin-symbol recovery, pytest-node extraction, and trace causal-window grouping seed. Existing manifest lineage and parent-child hydration primitives remain compatible with the catalog metadata.

---

## Context

Today's chunking surface is single-strategy-per-source and lossy:

| Source | Today's chunker | Documented loss |
|---|---|---|
| Python code | AST chunker (`ingest_code.py`) | Skips zero-arg functions, method-less classes, module-level constants. ~10–15 % of ADG nodes per sibling plan `e9aa09` §2.4. |
| Markdown docs | Token-window chunker (`ingest_docs.py`) | No header-aware splitting; no H1/H2 lineage in metadata; AGENTS.md / `.windsurf/rules/*` not ingested at all. |
| Tests | (mostly absent — tools/ingestion has no `ingest_tests.py` for code-style coverage) | Missing entirely from `repo_tests_guardrails`. |
| Traces (JSONL) | Per-line chunker | No causal-window grouping (parent span + children); per-line embeddings lose flow. |
| RCA / incidents | Token-window | No event-window grouping; no link to the underlying ADR / Wave row. |

ADR-059 added embedding-cosine semantic chunking as a generic option (LangChain SemanticChunker / LlamaIndex SemanticSplitterNodeParser parity). It is a chunker, not a **catalog**. The repo needs a catalog so each source uses the strategy that fits its structure.

Three additional 2024-2025 patterns are not yet exercised:

- **Parent-document / small-to-big**: index small chunks for retrieval precision but return the parent document (or a wider window) at fetch time.
- **Sentence-window**: index single sentences but expand to ±N sentences before reranking.
- **Causal-window for traces**: group spans by trace_id + parent_span_id so retrieved evidence preserves flow.

Without the catalog, every new source faces a one-off design decision on chunking strategy.

## Decision

Adopt a **chunker catalog** keyed by source kind, with one canonical strategy per source plus an optional secondary, all wired through a single `ChunkingEngine.register_chunker()` hook (the hook from ADR-059).

### Normative Requirements

1. **Catalog table**:

   | Source kind | Primary chunker | Secondary (opt-in) | Granularity |
   |---|---|---|---|
   | `code/python` | `AstThinChunker` (new — extends current AST chunker) | `EmbeddingSemanticChunker` (ADR-059) | function/class/constant; thin chunks for zero-arg/empty cases |
   | `code/non-python` | `TreeSitterChunker` (new — opt-in once tree-sitter binding is on the dep allowlist) | `EmbeddingSemanticChunker` | symbol-level |
   | `docs/markdown` | `MarkdownHeaderChunker` (new) | `EmbeddingSemanticChunker` | section bounded by headers; lineage in metadata |
   | `docs/rules-and-plans` | `MarkdownHeaderChunker` | — | same as docs/markdown but ingest-source `.windsurf/rules/*` and `.windsurf/plans/*` |
   | `tests/python` | `PytestNodeChunker` (new) | `AstThinChunker` | one chunk per test function with class context |
   | `traces/jsonl` | `CausalWindowChunker` (new) | — | trace_id + parent span tree, max N children per chunk |
   | `incidents-rca/markdown` | `MarkdownHeaderChunker` | — | section-bounded; `linked_adr_id` and `wave_phase_id` extracted to metadata |

2. **AstThinChunker** — extends today's AST chunker (`ingest_code.py`) so that:
   - Zero-arg functions emit a `thin_chunk` with parent class context (signature + docstring + class.__doc__).
   - Method-less classes emit a `thin_chunk` with module context (path + class signature + docstring).
   - Module-level constants whose name is `ALL_CAPS` emit a one-line chunk with leading 50-token module preamble.
   Closes the documented 10–15 % node-loss gap.

3. **MarkdownHeaderChunker** — splits at H1/H2/H3 boundaries. Each chunk's metadata carries `header_lineage: list[str]` (e.g. `["ADR-063", "Decision", "Normative Requirements"]`). Stable lineage enables: (a) parent-document hydration, (b) self-query metadata filters that say "only chunks under §Decision".

4. **CausalWindowChunker** — for OTEL trace JSONL: groups by `trace_id`, builds a span tree, chunks emit:
   - One chunk per non-leaf span containing its event + ≤ 5 nearest children's events.
   - One leaf-aggregate chunk per trace summarizing all leaves.
   - Metadata carries `trace_id`, `parent_span_id`, `agent_class`. Joins natively with `mcp7_otel_spans_by_agent`.

5. **PytestNodeChunker** — visits each `test_*` / `Test*` collection node, emits one chunk per test function with:
   - Test function source.
   - Enclosing class docstring + class fixtures.
   - Module-level fixtures referenced by name.
   Hooks into `pytest_mcp.discover_tests` for the discovery pass; no fresh AST walk.

6. **Parent-document hydration** — `agentic_core/knowledge/retrieval/parent_child_hydrator.py` is already present in the canonical retrieval module's `__init__.py` exports. ADR-063 wires its hooks:
   - Each chunk's metadata carries `parent_id` (already set by `MarkdownHeaderChunker` and `AstThinChunker`).
   - `HybridRecallStage` after rerank invokes the hydrator with `mode="parent"|"sentence_window"|"none"` per `RetrievalPlan.hydration_mode`.
   - Default `mode` per source: code → `none` (chunk is self-contained); docs → `parent` (return the H2 section); traces → `parent` (return the full causal window).

7. **Catalog wiring** — `tools/ingestion/chunker_catalog.py` (new) holds the source-kind → chunker mapping and the registry call:

   ```python
   ChunkingEngine.register_chunker("code/python", AstThinChunker)
   ChunkingEngine.register_chunker("docs/markdown", MarkdownHeaderChunker)
   ...
   ```

   Every ingest entry point resolves its chunker via `chunker_catalog.resolve(source_kind)`. Direct instantiation is rejected by CI gate `check_chunker_catalog_use.py`.

8. **Manifest schema** — `ChunkManifest` already has `situated_context` (ADR-045). ADR-063 adds (additive):
   - `chunker_name: str`        (e.g. `"ast_thin/v1"`, `"markdown_header/v1"`)
   - `parent_id: str | None`    (for hydration)
   - `header_lineage: list[str] | None` (markdown only)
   - `trace_id: str | None`     (traces only)
   - `chunk_kind: Literal["primary", "thin", "aggregate"]`
   Pre-existing manifest payloads read cleanly with these as None / default.

### Non-Goals

- Re-ingesting the entire corpus immediately. Catalog applies to **new** ingests; backfill is a separate plan that piggybacks on the next full ADR-055-driven reindex.
- Adding `tree-sitter` as a hard dependency. `TreeSitterChunker` is opt-in and lazy-imports.
- Re-architecting `ingest_code.py` away from its `--contextualize` shape. ADR-045 owns that shape; this ADR slots a different chunker behind it.

## Consequences

**Positive**
- Closes the 10–15 % node-loss gap from `e9aa09` §2.4.
- AGENTS.md / `.windsurf/rules` / `.windsurf/plans` become first-class retrieval targets.
- Parent-document hydration is finally backed by a real `parent_id` graph.
- Trace retrieval no longer fragments causality; one chunk = one branch of a trace.
- Operators can A/B chunkers per source via the catalog without touching ingest scripts.

**Negative / costs**
- Five new chunker classes; modest test surface.
- Backfill of manifest schema fields is additive but requires a one-shot reindex per corpus to populate `parent_id`/`header_lineage` on old rows. Coordinated with ADR-055 reindex.
- `CausalWindowChunker` requires a one-time scan of the trace JSONL to build the parent map; bounded.

**Risks**
- **R1 — `AstThinChunker` thin chunks dilute precision** if too many empty-shell symbols flood the index. Mitigation: thin chunks emit only when `docstring or has_decorator or len(signature) > 0`; pure no-op symbols are still skipped. W5.1 acceptance gate compares Recall@20 vs Precision@20 per source.
- **R2 — Markdown header lineage explodes for deep nesting**. Mitigation: cap lineage at 4 levels; deeper headers fold into the parent.
- **R3 — Tree-sitter dependency surface.** Mitigation: opt-in only; never imported in default ingest path.

## Validation

- `pytest tests/unit/tools/ingestion/test_chunker_catalog.py` — registry lookup, missing-source-kind fallback to `EmbeddingSemanticChunker` with telemetry.
- `pytest tests/unit/tools/ingestion/test_ast_thin_chunker.py` — zero-arg/method-less recovery.
- `pytest tests/unit/tools/ingestion/test_markdown_header_chunker.py` — lineage extraction; 4-level cap.
- `pytest tests/integration/test_parent_document_hydration.py` — end-to-end retrieve-then-hydrate yields parent section.
- W5.1 acceptance gate: per-source Recall@20 ≥ pre-catalog baseline + 3 % (no regression on any source).

Rollback: `CHUNKER_CATALOG_DISABLE=1` env knob falls back to the existing single-strategy chunkers per source.

## Alternatives Considered

1. **Apply `EmbeddingSemanticChunker` to everything.** ADR-059 anticipates this; it's the universal-fallback. But generic semantic chunking under-performs on code (where AST boundaries are gold) and traces (where causality, not similarity, is the cohesion signal). Rejected as the primary.
2. **Stay single-strategy per source.** Concedes documented coverage gaps and parent-document hydration. Rejected.
3. **Use LlamaIndex / LangChain node parsers wholesale.** Heavy dep; we own only the part we need.

## References

- ADR-059 (embedding-cosine semantic chunking — the registry hook)
- ADR-045 (contextual retrieval — interacts with thin chunks via situated_context)
- LlamaIndex `SentenceWindowNodeParser`, `HierarchicalNodeParser` (2024)
- LangChain `MarkdownHeaderTextSplitter`, `RecursiveJsonSplitter` (2024)
- In-repo: `agentic_core/knowledge/retrieval/parent_child_hydrator.py`, `agentic_core/knowledge/canonical/chunk_manifest.py`
- Sibling plan: `chromadb-bge-retrieval-hardening-e9aa09` §2.4
- Parent plan: `.windsurf/plans/chromadb-best-in-class-agentic-embeddings-c4a1f8.md`
