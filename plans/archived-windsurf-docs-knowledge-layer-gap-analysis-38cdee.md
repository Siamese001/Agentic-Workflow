---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\knowledge-layer-gap-analysis-38cdee.md'
original_relative_path: 'knowledge-layer-gap-analysis-38cdee.md'
source_sha256: 8f685400bea1068d980c3c700faf28355899262d5c2adf20d644f3a8a6eb1c78
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-17'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Knowledge Layer Gap Analysis & Implementation Plan

Comprehensive gap analysis of `agentic_core/knowledge/` vs LCD+ best practices, with prioritized fixes, file diffs, and test plans.

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Current State Summary

**Files**: 13 `.py` files across 6 subfolders
**Subfolders**: `document_loaders/`, `engine/`, `healing/`, `reasoning/`, `research_cache/`, `static_index/`
**Tests**: 8 mirror-only tests (import + `__file__` + public attrs) — zero behavioral coverage

---

## Gap Inventory

### G1 — LCD+ Skeleton Non-Compliance (P0)

The LCD+ canonical skeleton requires: `config/`, `types/`, `reasoning/`, `enforcement/`, `validators/`, `utils/`. The `engines.md` workflow explicitly lists `domains/knowledge/` as in-scope for LCD+ migration (step 9).

| Required Folder | Status | Action |
|---|---|---|
| `config/` | **MISSING** | Create — absorb loader configs |
| `types/` | **MISSING** | Create — absorb `source_document_types.py`, static index types |
| `reasoning/` | EXISTS | Keep — already has `SovereignRAGManagerAgent.py` |
| `enforcement/` | **MISSING** | Create (can start empty) |
| `validators/` | **MISSING** | Create (can start empty) |
| `utils/` | **MISSING** | Create — absorb `cache_store_util.py` |

**Non-LCD folders to dissolve**:
- `document_loaders/` → split across `config/`, `types/`, `engines/` (nuance)
- `engine/` → rename to canonical `engines/` (flat, no subfolders)
- `healing/` → absorb into `reasoning/` (it's a strategy agent)
- `research_cache/` → `utils/` (cache_store_util) + `config/` (cache config)
- `static_index/` → `types/` (these are static data type definitions)

### G2 — Broken Imports (P0)

`rag_orchestrator.py` imports 4 modules that **do not exist**:
- `agentic_core.knowledge.document_loaders.csv_loader` → actual: `csv_document_loader_config.py`
- `agentic_core.knowledge.document_loaders.html_loader` → **no HTML loader exists at all**
- `agentic_core.knowledge.document_loaders.pdf_loader` → actual: `pdf_document_loader_config.py`
- `agentic_core.knowledge.document_loaders.text_loader` → actual: `text_document_loader_config.py`

`SovereignRAGManagerAgent.py` also imports from non-existent `pdf_loader` and `text_loader`.

`wiki_healer.py` references undefined `config` object (bare name, never imported).

### G3 — Duplicate ResearchCache (P0)

Two separate `ResearchCache` classes exist:
1. `document_loaders/research_cache.py` — keyword-matching, simpler API (`store`/`query`/`get_all_entries`/`clear`)
2. `research_cache/cache_store_util.py` — hash-indexed, richer API (`exists`/`get`/`set`/`clear`/`get_stats`)

The `research_cache/__init__.py` exports from `cache_store_util.py`. The one in `document_loaders/` is a legacy orphan.

### G4 — Duplicate RAG Orchestrator (P1)

Two overlapping implementations:
1. `engine/rag_orchestrator.py` — `SovereignRagOrchestrator` (313 LOC, async retrieve, RRF fusion, LLM rerank)
2. `reasoning/SovereignRAGManagerAgent.py` — `SovereignRAGManager(SovereignBaseAgent)` (167 LOC, sync retrieve, naive fusion)

These must be consolidated into one canonical agent per §2 (no duplicate agents).

### G5 — Zero Behavioral Test Coverage (P1)

All 8 existing tests are `GENERATED_MIRROR_TEST` stubs — they only test `importlib.import_module()`. No behavioral tests for:
- Document loader load/parse correctness
- ResearchCache store/retrieve/clear cycle
- RRF fusion scoring
- Static index data integrity (completeness, no duplicates)
- Chunking logic

### G6 — Naming Convention Violations (P2)

| File | Issue | LCD+ Correct Name |
|---|---|---|
| `csv_document_loader_config.py` | Has `_config` suffix but is an engine, not config | `CsvDocumentLoader.py` (PascalCase, engines/) |
| `pdf_document_loader_config.py` | Same | `PdfDocumentLoader.py` |
| `text_document_loader_config.py` | Same | `TextDocumentLoader.py` |
| `source_document_types.py` | Correct suffix, wrong folder | Move to `types/` |
| `action_verbs_types.py` | Correct suffix, wrong folder | Move to `types/` |
| `skill_taxonomy_types.py` | Correct suffix, wrong folder | Move to `types/` |
| `cache_store_util.py` | Correct suffix, wrong folder | Move to `utils/` |

### G7 — Code Quality Issues (P2)

- `rag_orchestrator.py:66` — bare `except:` (no exception type)
- `rag_orchestrator.py:134,167` — `print()` instead of `logging`
- `rag_orchestrator.py:258` — redundant `import json as json_lib` (json already imported at top)
- `rag_orchestrator.py:213` — parameter `k` immediately shadowed by local `k = 60.0`
- `rag_orchestrator.py:266-280` — `get_context_for_task` calls `self.retrieve()` (async) without `await`, and loop body has dead expressions (`r["source"]`, `r["content"]` — no-ops)
- `wiki_healer.py:49,85,100,119,122` — references bare `config` object that is never imported
- `SovereignRAGManagerAgent.py:15-16` — imports from non-existent modules (will crash on import)
- `cache_store_util.py:126-127` — file handle leak: opens same file inside `with` block of same file

### G8 — Missing HTML Document Loader (P3)

The orchestrator references `HTMLDocumentLoader` but no implementation exists.

---

## Implementation Plan (Prioritized)

### Phase 1 — Fix Broken Imports & Eliminate Duplicates (P0)

**Step 1.1**: Fix document loader import paths in `rag_orchestrator.py` and `SovereignRAGManagerAgent.py`

```diff
# rag_orchestrator.py — fix import paths
- from agentic_core.knowledge.document_loaders.csv_loader import CSVDocumentLoader
- from agentic_core.knowledge.document_loaders.html_loader import HTMLDocumentLoader
- from agentic_core.knowledge.document_loaders.pdf_loader import PDFDocumentLoader
- from agentic_core.knowledge.document_loaders.text_loader import TextDocumentLoader
+ from agentic_core.knowledge.document_loaders.csv_document_loader_config import CsvDocumentLoader as CSVDocumentLoader
+ from agentic_core.knowledge.document_loaders.pdf_document_loader_config import PDFDocumentLoader
+ from agentic_core.knowledge.document_loaders.text_document_loader_config import TextDocumentLoader
```

```diff
# SovereignRAGManagerAgent.py — fix import paths
- from agentic_core.knowledge.document_loaders.pdf_loader import PDFDocumentLoader
- from agentic_core.knowledge.document_loaders.text_loader import TextDocumentLoader
+ from agentic_core.knowledge.document_loaders.pdf_document_loader_config import PDFDocumentLoader
+ from agentic_core.knowledge.document_loaders.text_document_loader_config import TextDocumentLoader
```

**Step 1.2**: Remove duplicate `document_loaders/research_cache.py` (the legacy orphan)

```diff
# DELETE: agentic_core/knowledge/document_loaders/research_cache.py
# (duplicate of research_cache/cache_store_util.py — the __init__.py already exports the canonical one)
```

**Step 1.3**: Consolidate duplicate RAG orchestrators — make `SovereignRAGManagerAgent.py` delegate to `rag_orchestrator.py`

```diff
# SovereignRAGManagerAgent.py — convert to thin delegation wrapper
- class SovereignRAGManager(SovereignBaseAgent):
-     """Orchestrates the retrieval-augmented generation pipeline."""
-     ... (full 167-line implementation)
+ class SovereignRAGManager(SovereignBaseAgent):
+     """Thin agent wrapper delegating to SovereignRagOrchestrator."""
+     def __init__(self, storage_root: Path):
+         self.logger = logging.getLogger(self.__class__.__name__)
+         self._orchestrator = SovereignRagOrchestrator(storage_root)
+         super().__init__()
+     def ingest(self, file_path: Path) -> bool:
+         return self._orchestrator.ingest(file_path)
+     def retrieve(self, query: str, top_k: int = 5) -> list[dict]:
+         # sync wrapper — orchestrator.retrieve is async
+         ...
```

**Step 1.4**: Fix `wiki_healer.py` — add missing `config` import or inject config

```diff
# wiki_healer.py — add config import
+ from agentic_core.knowledge.config.knowledge_config import KnowledgeConfig as config
```
(This requires creating the config in Phase 2.)

### Phase 2 — LCD+ Skeleton Migration (P0)

**Step 2.1**: Create LCD+ folders with `__init__.py`

```
agentic_core/knowledge/
├── config/          # NEW
├── types/           # NEW
├── reasoning/       # EXISTS
├── enforcement/     # NEW (empty initially)
├── validators/      # NEW (empty initially)
├── utils/           # NEW
├── engines/         # NEW (renamed from engine/)
```

**Step 2.2**: Move files to LCD+ targets

| Source | Target | Rename |
|---|---|---|
| `document_loaders/csv_document_loader_config.py` | `engines/CsvDocumentLoader.py` | Yes (PascalCase) |
| `document_loaders/pdf_document_loader_config.py` | `engines/PdfDocumentLoader.py` | Yes |
| `document_loaders/text_document_loader_config.py` | `engines/TextDocumentLoader.py` | Yes |
| `document_loaders/source_document_types.py` | `types/source_document_types.py` | No |
| `engine/rag_orchestrator.py` | `engines/rag_orchestrator.py` | No |
| `healing/wiki_healer.py` | `reasoning/WikiHealerAgent.py` | Yes (PascalCase Agent) |
| `research_cache/cache_store_util.py` | `utils/cache_store_util.py` | No |
| `static_index/action_verbs_types.py` | `types/action_verbs_types.py` | No |
| `static_index/skill_taxonomy_types.py` | `types/skill_taxonomy_types.py` | No |

**Step 2.3**: Create `config/knowledge_config.py`

```python
"""Knowledge layer configuration — DeepWiki, cache, ingestion settings."""
from dataclasses import dataclass

@dataclass(frozen=True)
class KnowledgeConfig:
    DEEPWIKI_HEALING_ENABLED: bool = False
    DEEPWIKI_HEALING_MAX_DAILY: int = 50
    DEEPWIKI_HEALING_BATCH_SIZE: int = 10
    DEEPWIKI_DEFAULT_REPO: str = ""
    CACHE_MAX_ENTRIES: int = 10000
    DEFAULT_CHUNK_SIZE: int = 1000
```

**Step 2.4**: Delete dissolved folders (`document_loaders/`, `engine/`, `healing/`, `research_cache/`, `static_index/`)

**Step 2.5**: Update all repo-wide imports (§1.4 closure rule) — scan entire codebase for old paths, rewrite

### Phase 3 — Code Quality Fixes (P1)

**Step 3.1**: Fix `rag_orchestrator.py` quality issues

```diff
# Line 66: bare except
-        except:
+        except Exception:

# Line 134, 167: print → logging
- print(f"Indexed {len(text_chunks)} chunks for {doc_id}")
+ Logger.info(f"Indexed {len(text_chunks)} chunks for {doc_id}")

# Line 213: shadowed parameter
- def _rrf_fusion(self, vector_list, bm25_list, k: int = 60) -> list[dict]:
-     k = 60.0
+ def _rrf_fusion(self, vector_list, bm25_list, k: float = 60.0) -> list[dict]:

# Line 258: redundant import
-            import json as json_lib
-            indices = json_lib.loads(response)
+            indices = json.loads(response)

# Lines 266-280: fix async/dead-code
- def get_context_for_task(self, Task: str, domain: str = "general") -> str:
-     retrievals = self.retrieve(Task, domain=domain)
+ async def get_context_for_task(self, task: str, domain: str = "general") -> str:
+     retrievals = await self.retrieve(task, domain=domain)
      ...
-     for r in retrievals:
-         r["source"]
-         r["content"]
+     for r in retrievals:
+         context_parts.append(f"[{r['source']}] {r['content']}")
```

**Step 3.2**: Fix `cache_store_util.py` file handle leak

```diff
# Line 126-127
-               line_num = (
-                   sum(1 for _ in open(self.cache_file, encoding="utf-8")) if self.cache_file.exists() else 0
-               )
+               line_num = len(self._index)
```

### Phase 4 — Create HTML Loader (P3)

```python
# engines/HtmlDocumentLoader.py
"""HTML Document Loader — BeautifulSoup-based HTML text extraction."""
import logging
from pathlib import Path

log = logging.getLogger(__name__)

class HtmlDocumentLoader:
    def __init__(self, file_path: Path):
        self.file_path = Path(file_path)

    def load(self) -> str:
        try:
            from bs4 import BeautifulSoup
            html = self.file_path.read_text(encoding="utf-8", errors="replace")
            soup = BeautifulSoup(html, "html.parser")
            return soup.get_text(separator="\n", strip=True)
        except ImportError:
            log.warning("beautifulsoup4 required for HTML loading")
            return ""

    @staticmethod
    def load_file(file_path: Path) -> str:
        return HtmlDocumentLoader(file_path).load()
```

---

## Test Plan

### T1 — Behavioral Tests for Document Loaders

**File**: `tests/agentic_core/knowledge/engines/test_document_loaders.py`

| Test | What it validates |
|---|---|
| `test_csv_loader_returns_records` | CSV → list[dict] with correct field names |
| `test_csv_loader_sample_respects_limit` | `load_sample(rows=3)` returns ≤3 records |
| `test_csv_loader_missing_pandas_raises` | ImportError when pandas absent |
| `test_pdf_loader_extracts_text` | PDF → non-empty string |
| `test_pdf_loader_missing_file_returns_empty` | Graceful "" on bad path |
| `test_text_loader_reads_utf8` | UTF-8 text round-trip |
| `test_html_loader_strips_tags` | HTML → clean text |

### T2 — Behavioral Tests for ResearchCache

**File**: `tests/agentic_core/knowledge/utils/test_cache_store_util.py`

| Test | What it validates |
|---|---|
| `test_cache_set_and_get_roundtrip` | `set()` then `get()` returns same data |
| `test_cache_exists_true_after_set` | `exists()` returns True after `set()` |
| `test_cache_exists_false_initially` | `exists()` returns False on empty cache |
| `test_cache_clear_removes_all` | After `clear()`, `exists()` → False |
| `test_cache_stats_counts` | `get_stats()` → correct `total_entries` |
| `test_cache_handles_corrupt_jsonl` | Malformed lines don't crash `_load_index` |

### T3 — Behavioral Tests for RRF Fusion

**File**: `tests/agentic_core/knowledge/engines/test_rag_orchestrator.py`

| Test | What it validates |
|---|---|
| `test_rrf_fusion_empty_inputs` | Empty lists → empty result |
| `test_rrf_fusion_single_source` | One list → items sorted correctly |
| `test_rrf_fusion_dual_sources_scores` | Items in both lists get boosted |
| `test_rrf_fusion_deduplicates` | Same doc_id merged, not duplicated |

### T4 — Static Index Integrity

**File**: `tests/agentic_core/knowledge/types/test_static_index_integrity.py`

| Test | What it validates |
|---|---|
| `test_action_verbs_all_categories_nonempty` | Every category has ≥5 verbs |
| `test_action_verbs_no_duplicates` | No verb appears twice across all categories |
| `test_strong_verbs_subset_of_action_verbs` | Every strong verb exists in some category |
| `test_skill_taxonomy_all_categories_nonempty` | Every skill domain has ≥5 entries |
| `test_all_skills_matches_taxonomy_flat` | `ALL_SKILLS == flattened SKILL_TAXONOMY` |

### T5 — Type Model Tests

**File**: `tests/agentic_core/knowledge/types/test_source_document_types.py`

| Test | What it validates |
|---|---|
| `test_source_document_valid_creation` | SourceDocument with valid fields |
| `test_source_document_file_type_validation` | Rejects invalid `file_type` |
| `test_knowledge_chunk_requires_doc_id` | Missing `document_id` → error |
| `test_knowledge_chunk_index_non_negative` | `chunk_index=-1` → error |

---

## Execution Order

1. **Phase 1** (P0) — Fix broken imports + eliminate duplicates → unblocks all tests
2. **Phase 2** (P0) — LCD+ skeleton migration → structural compliance
3. **Phase 3** (P1) — Code quality fixes → correctness
4. **Phase 4** (P3) — HTML loader → feature completeness
5. **Tests T1-T5** after each phase to validate

## Risk Notes

- Phase 2 file moves trigger §1.4 (Rename/Move Closure Rule) — all repo-wide imports must be updated and validated by discovery + structure verification + tests.
- The `wiki_healer.py` depends on `filesystem_mcp_client_1` and `ssot_discovery_validator` — verify those exist before moving.
- `SovereignRagOrchestrator` depends on `semantic_memory` (Gemini embedder, Pinecone, BM25) — all behind try/except, low risk.

## Gap Register

| Gap | Priority | Impact | Status |
|------|----------|--------|---------|
| [Gap 1] | High | Critical | Open |
| [Gap 2] | Medium | Moderate | In Progress |

---

## Execution Plan

1. **Phase 1**: Analysis and Planning
2. **Phase 2**: Implementation
3. **Phase 3**: Testing and Validation
4. **Phase 4**: Documentation and Cleanup

---

