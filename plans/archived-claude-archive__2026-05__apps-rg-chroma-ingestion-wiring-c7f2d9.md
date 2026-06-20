---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\apps-rg-chroma-ingestion-wiring-c7f2d9.md'
original_relative_path: '_archive\\2026-05\\apps-rg-chroma-ingestion-wiring-c7f2d9.md'
source_sha256: 1fb173f41a1f7dfa44fd14f28a9371d701855a37801284dac8b4fe45eb5eedf2
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: apps-rg-chroma-ingestion-wiring-c7f2d9
plan_type: infra
touches_agentic_core: false
touches_governance_ci: true
touches_windsurf_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# apps_rg ChromaDB Ingestion and C0 Retrieval Wiring

Wire apps_rg C0 retrieval from file-only to ChromaDB-backed semantic search by ingesting the 7 missing resume-relevant corpora and connecting `c0_binding.py` to `ChromaResearchStore`.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: DONE
CURRENT_WAVE: W5
CURRENT_WAVE_STATUS: DONE
LAST_COMPLETED_WAVE: W5
W1_STATUS: DONE
W2_STATUS: DONE
W2_1_STATUS: DONE
W2_2_STATUS: DONE
W2_3_STATUS: DONE
W2_4_STATUS: DONE
W3_STATUS: DONE (COLLISION_REPAIR_REQUIRED — see w3_repair_receipt.json)
W3_1_STATUS: DONE (chunks: 182)
W3_2_STATUS: DONE (chunks: 967)
W3_3_STATUS: DONE (chunks: 644)
W4_STATUS: DONE (35/35 tests passing — see w4_c0_binding_receipt.json)
W4_1_STATUS: DONE (Chroma opt-in, chromadb_path param, CHROMA_PERSIST_DIR env)
W4_2_STATUS: DONE (citation_map, source_lineage_map, freshness_receipts, support_status, excluded_evidence_refs)
W4_3_STATUS: DONE (EMBEDDING_ENABLED guard, C0EvidenceGapError)
W5_STATUS: DONE (11/11 probes PASS, 9/9 CI checks OK, gap report READY — see w5_probe_ci_receipt.json)
CHROMA_COUNT_LAST_VERIFIED: 13281
EXECUTE_FLAG_USED: true
LAST_UPDATED: 2026-05-13

---

## Context (SCQA)

- **Situation** — apps_rg pipeline is fully operational (W6 complete, Qwen 32B AWQ, exit_status='success'). Chroma `process_docs` collection has 9,138 agentic_core-owned vectors. The non-mutating gap audit (`artifacts/apps_rg/retrieval/`) confirmed the current state with directly-observed evidence.
- **Complication** — The C0 binding (`apps_rg/runtime/bindings/c0_binding.py`) is file-based only: it reads JD + resume from `app_payload` but never queries ChromaDB. Zero apps_rg-owned vectors exist. All 8 required metadata fields (`source_id`, `source_class`, `authority_class`, `freshness`, `citation_anchor`, `chunk_digest`, `app`, `ACL`) are absent from the current `process_docs` schema. Seven of eight resume-relevant source corpora are missing entirely. `c0_binding.py` leaves the 5 optional tuple fields on `FinalEvidenceContract` at their safe-default empty values (`citation_map`, `source_lineage_map`, `freshness_receipts`, `support_status=UNKNOWN`, `excluded_evidence_refs`).
- **Question** — How do we ingest the missing apps_rg corpora, add the required metadata fields, and wire C0 retrieval to ChromaDB so that resume generation is grounded in cited, metadata-scoped evidence?
- **Answer** — Build a chunker script, ingest the 7 corpora in priority order, populate the 5 FEC optional tuple fields from Chroma metadata in `apps_rg/runtime/bindings/c0_binding.py`, and wire it to `ChromaResearchStore` with `source_class` filters. No `agentic_core` schema changes required — all 5 fields already exist in `agentic_core/runtime/contracts/final_evidence_contract.py` with safe defaults.

**App/core boundary (DIRECTLY OBSERVED)**:
- `FinalEvidenceContract` canonical definition: `agentic_core/runtime/contracts/final_evidence_contract.py` — all 5 fields present as optional tuple fields with empty defaults. **No core schema changes needed.**
- `citation_map: tuple[tuple[str, str], ...]` — maps `evidence_id → citation_anchor`. Type is tuple-of-2-tuples, NOT `List[CitationInfo]` (that type lives in the package-driven grounding path only).
- `support_status` sentinel vocabulary (enforced by `support_status_is_passing()`): `PASS`, `PARTIAL`, `WEAK`, `EMPTY`, `BLOCKED`, `CONFLICTED`, `UNKNOWN`, `NOT_APPLICABLE`. `UNKNOWN` is NOT a passing value.
- `l5_certification_ref` is validated in `__post_init__` — apps_rg C0 binding **must** pass `"c0-apps-rg-resume-generation-app-payload-b3a449"` or construction raises `ValueError`.
- W4 scope: apps_rg-side population of existing fields only. All edits stay in `apps_rg/runtime/bindings/c0_binding.py`.

---

## Gap Register (from audit artifacts/apps_rg/retrieval/)

**GAP-1: No apps_rg-owned ChromaDB collection / zero vectors**
- `process_docs` has 9,138 docs; all agentic_core-owned; no `source_class`, `app`, or `ACL` field
- Impact: C0 retrieval cannot return resume-relevant evidence; `FinalEvidenceContract` is file-only

**GAP-2: Chunker script missing**
- `tools/ingestion/chunk_apps_rg_corpus.py` does not exist
- Impact: Cannot convert PDF/DOCX/YAML/JSON source files to `.jsonl` required by `chroma_ingest_pipeline.py`

**GAP-3: All 8 required metadata fields absent from process_docs**
- `source_id`, `source_class`, `authority_class`, `freshness`, `citation_anchor`, `chunk_digest`, `app`, `ACL`
- Impact: Metadata filter queries (`where={"source_class": "candidate_profile"}`) return zero results

**GAP-4: 7 of 8 resume-relevant source corpora missing**
- `candidate_profile`, `project_evidence`, `approved_examples`, `rubrics`, `governance_docs` (filtered), `receipts`, `prior_outputs`
- Impact: Probe queries PQ-009/PQ-010 return zero results; no grounded evidence for resume bullets

**GAP-5: FinalEvidenceContract 5 optional fields unpopulated by apps_rg C0 binding**
- Fields exist in `agentic_core/runtime/contracts/final_evidence_contract.py` with safe empty defaults; `apps_rg/runtime/bindings/c0_binding.py` does not populate them from Chroma metadata
- Types: `citation_map: tuple[tuple[str,str],...]`, `source_lineage_map: tuple[tuple[str,str],...]`, `freshness_receipts: tuple[str,...]`, `support_status: str = STATUS_UNKNOWN`, `excluded_evidence_refs: tuple[str,...]`
- `l5_certification_ref` must be `"c0-apps-rg-resume-generation-app-payload-b3a449"` (validated in `__post_init__`)
- Impact: Downstream prompt assembly cannot cite evidence sources; `support_status` stays `UNKNOWN` (not a passing value)

**GAP-6: BM25 reranker not wired for apps_rg**
- `ResearchC0Adapter` hybrid path (ChromaDB + BM25) exists for `apps_research` but apps_rg C0 binding bypasses it
- Impact: Retrieval is dense-only; no keyword fallback for exact-match queries

**GAP-7: EMBEDDING_ENABLED guard not validated pre-flight**
- No pre-flight check confirms `EMBEDDING_ENABLED=true` before retrieval is attempted
- Impact: Silent failure if embedding model unavailable

---

## Wave Overview

**Waves**: 5 total (W1–W5)
**Total Estimate**: ~40K tokens
**Current**: W0 (pre-flight)

**Wave Manifest**:
- **W1** — Chunker script + dry-run validation | ~8K tokens | Checkpoint A | STATUS: DONE ✅
- **W2** — Corpus ingestion (waves 1–4: governance, candidate_profile, project_evidence, approved_examples) | ~12K tokens | Checkpoint B | STATUS: TODO
- **W3** — Corpus ingestion (waves 5–7: rubrics, receipts, prior_outputs) | ~6K tokens | Checkpoint C | STATUS: TODO
- **W4** — C0 binding extension: ChromaResearchStore wiring + FEC field expansion | ~10K tokens | Checkpoint D | STATUS: TODO
- **W5** — Probe pack execution + gap report update + CI gate | ~4K tokens | Checkpoint E | STATUS: TODO

---

## Wave 1 — Chunker Script + Dry-Run Validation

WAVE_ID: W1
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

> ✅ **NON-MUTATING** — W1 writes no vectors to ChromaDB. `--execute` flag MUST NOT appear in any W1 command.

**Phases**:
- **W1.1** — Build `tools/ingestion/chunk_apps_rg_corpus.py` — converts PDF/DOCX/YAML/JSON to `.jsonl` with all 8 required metadata fields | ~5K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W1.2** — Dry-run validate all 7 `.jsonl` files against `chroma_ingest_pipeline.py` (no `--execute`) | ~3K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance (hardened)**:
- `chunk_apps_rg_corpus.py` emits every chunk with `id`, `text`, and all 8 metadata fields; any chunk missing a field raises `ChunkValidationError` and halts (fail-closed, not fail-soft)
- Chunker runs self-validation pass before writing: duplicate `id` values → error; empty `text` → error; `source_class` not in `SOURCE_CLASS_VOCAB` → error; `ACL` not in `{"apps_rg:private", "apps_rg:shared"}` → error
- `candidate_profile` chunks additionally require a PII scrub receipt file at `artifacts/apps_rg/retrieval/pii_scrub_receipts/candidate_profile.json` before dry-run validates them; absence → error
- `python tools/ingestion/chroma_ingest_pipeline.py --input <file> --chromadb-path data/cache/chromadb` (no `--execute`) exits 0 for each `.jsonl`; output confirms `0 vectors written`
- No ChromaDB writes performed — verified by pre/post collection count equality

**Blockers resolved in W1**:
- PII scrub receipt created: `artifacts/apps_rg/retrieval/pii_scrub_receipts/candidate_profile.json` ✅
- Approval gate for `approved_examples` — human sign-off still required before W2.4; absence blocks W2.4 only

**W1 Evidence**:

Receipt: `artifacts/apps_rg/retrieval/ingestion_receipts/w1_dry_run_receipt.json`

| Corpus | JSONL path | Chunks | Validation | Dry-run exit |
|---|---|---|---|---|
| `governance_docs` | `ingestion_input/governance_docs.jsonl` | 363 | PASS | 0 |
| `rubrics` | `ingestion_input/rubrics.jsonl` | 86 | PASS | 0 |
| `receipts` | `ingestion_input/receipts.jsonl` | 967 | PASS | 0 |
| `approved_examples` | `ingestion_input/approved_examples.jsonl` | 153 | PASS | 0 |
| `prior_outputs` | `ingestion_input/prior_outputs.jsonl` | 644 | PASS | 0 |
| `project_evidence` | `ingestion_input/project_evidence.jsonl` | 554 | PASS | 0 |
| `candidate_profile` | `ingestion_input/candidate_profile.jsonl` | 1280 | PASS | 0 |

**Non-mutation proof**: `process_docs` count before = 9138; after all dry-runs = 9138. `--execute` never issued.

**Duplicate id fix**: Initial run hit a duplicate id error on chunk 12 (two rule files shared identical opening text). Fixed by incorporating `source_id` (file path + index) into the id hash — `sha256(f"{source_id}\x00{text[:200]}")`. All 7 corpora passed validation after fix.

---

## Wave 2 — Priority Corpus Ingestion (Critical + High)

WAVE_ID: W2
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: COMPLETE (all 4 phases executed 2026-05-12)
CHECKPOINT: B
PARTIAL_INGESTION_RECEIPT: artifacts/apps_rg/retrieval/ingestion_receipts/w2_partial_ingestion_receipt.json
W2_4_RECEIPT: artifacts/apps_rg/retrieval/ingestion_receipts/w2_approved_examples_ingestion_receipt.json

> ⛔ **AUTHORIZATION_REQUIRED + MUTATION BOUNDARY** — Wave 2 executes `--execute` flag on `chroma_ingest_pipeline.py`. Permanently writes vectors to ChromaDB. User must issue explicit approval in chat before any phase runs.
>
> **Hard preflight guard**: Before any `--execute` invocation, run `python tools/ingestion/chroma_ingest_pipeline.py --preflight-check --input <file>`. This must exit 0 and confirm `OPERATOR_APPROVAL_CONFIRMED=true` in env or fail with `MutationNotAuthorizedError`. Cursor Agent MUST NOT issue `--execute` without user's explicit same-turn approval.

**Phases**:
- **W2.1** — Ingest `governance_docs` corpus | PHASE_STATUS: DONE | PHASE_COMPLETE: YES | chunks: 363
- **W2.2** — Ingest `candidate_profile` corpus; **PII receipt verified** | PHASE_STATUS: DONE | PHASE_COMPLETE: YES | chunks: 1280
- **W2.3** — Ingest `project_evidence` corpus | PHASE_STATUS: DONE | PHASE_COMPLETE: YES | chunks: 554
- **W2.4** — Ingest `approved_examples` corpus; **approval receipt present** | PHASE_STATUS: DONE | PHASE_COMPLETE: YES | chunks: 153

**Acceptance**:
- Pre-ingestion count recorded and written to `artifacts/apps_rg/retrieval/ingestion_receipts/w2_pre_count.txt`
- Post-ingestion count increased by expected chunk range per corpus
- Metadata sample on ingested chunks confirms all 8 required fields present
- `source_class` filter query returns non-zero results for each ingested corpus
- W2.2 blocked until `artifacts/apps_rg/retrieval/pii_scrub_receipts/candidate_profile.json` exists ✅ (present)
- W2.4 blocked until human approval receipt at `artifacts/apps_rg/retrieval/approval_receipts/approved_examples.json` exists ⛔ (ABSENT — template at `approval_receipts/approved_examples.TEMPLATE.json`)

**W2 Readiness Packaging** (completed 2026-05-12 — no mutation, no --execute):

Approval packet: `artifacts/apps_rg/retrieval/ingestion_receipts/w2_approval_packet.json`
Preflight checklist: `artifacts/apps_rg/retrieval/ingestion_receipts/w2_preflight_checklist.md`
Approval receipt template: `artifacts/apps_rg/retrieval/approval_receipts/approved_examples.TEMPLATE.json`

| Phase | Corpus | Chunks | Status | Blocker |
|---|---|---|---|---|
| W2.1 | `governance_docs` | 363 | READY | none |
| W2.2 | `candidate_profile` | 1280 | READY | none (PII receipt ✅) |
| W2.3 | `project_evidence` | 554 | READY | none |
| W2.4 | `approved_examples` | 153 | BLOCKED_PENDING_APPROVAL_RECEIPT | `approval_receipts/approved_examples.json` absent |

**Gate before any --execute**: `OPERATOR_APPROVAL_CONFIRMED=1` env var must be set. Chroma pre-count = 9138. Expected post-count (W2.1+W2.2+W2.3 only): 11335. With W2.4: 11488.

**Rollback**: filesystem backup of `data/cache/chromadb/` before any --execute step:
```
xcopy /E /I data\cache\chromadb data\cache\chromadb_w2_pre_backup
```

---

## Wave 3 — Supporting Corpus Ingestion (Medium + Low)

WAVE_ID: W3
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: COMPLETE
CHECKPOINT: C
REPAIR_REQUIRED: YES — chunk_id collision; see incident + repair receipts
REPAIR_RECEIPT: artifacts/apps_rg/retrieval/ingestion_receipts/w3_repair_receipt.json
INCIDENT_RECEIPT: artifacts/apps_rg/retrieval/ingestion_receipts/w3_collision_incident_receipt.json
BACKUP: data/cache/chromadb_backup_20260512_165024

**Phases**:
- **W3.1** — Ingest `rubrics` corpus | PHASE_STATUS: DONE | PHASE_COMPLETE: YES | chunks: 182 (expanded from 86 — 6 new .json config files added since W1)
- **W3.2** — Ingest `receipts` corpus | PHASE_STATUS: DONE | PHASE_COMPLETE: YES | chunks: 967
- **W3.3** — Ingest `prior_outputs` corpus with `invalid_for_normative_use=True` | PHASE_STATUS: DONE | PHASE_COMPLETE: YES | chunks: 644

**Collision Repair Summary** (2026-05-12):
- Root cause: `_id_for_chunk` formula missing `source_class` in SHA256 hash → cross-corpus ID collisions
- Fix: patched `tools/ingestion/chunk_apps_rg_corpus.py::_id_for_chunk` to include `source_class`
- Stale records deleted: 491 prior_outputs chunks with old-hash IDs (backup proof confirmed)
- Post-repair process_docs count: **13281** (9138 pre-W3 baseline + 2143 W2 + 182 rubrics + 967 receipts + 644 prior_outputs - 491 stale prior_outputs = 13281 net)
- Zero cross-corpus ID collisions confirmed in dry-run validation

**Acceptance** ✅:
- All 7 source classes represented in `process_docs` with `source_class` metadata filter ✅
- `prior_outputs` chunks: all 644 have `invalid_for_normative_use=True` ✅
- Final process_docs count: 13281 ✅
- W2 data (governance_docs=363, candidate_profile=1280, project_evidence=554, approved_examples=153, receipts=967) preserved intact ✅

---

## Wave 4 — C0 Binding Extension + FEC Field Population

WAVE_ID: W4
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: D
RECEIPT: artifacts/apps_rg/retrieval/ingestion_receipts/w4_c0_binding_receipt.json

> ✅ **NON-MUTATING** — W4 edits only `apps_rg/runtime/bindings/c0_binding.py`. No `agentic_core` files are modified. `FinalEvidenceContract` schema is unchanged — all 5 fields already exist with safe empty defaults in `agentic_core/runtime/contracts/final_evidence_contract.py`.

**Phases**:
- **W4.1** — Wire `ChromaResearchStore` into `apps_rg/runtime/bindings/c0_binding.py`; Chroma path is opt-in via `CHROMA_PERSIST_DIR` env var or explicit `chromadb_path` argument; file fallback is the default safe path | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W4.2** — Populate FEC tuple fields from Chroma metadata in `c0_binding.py` using canonical types from `final_evidence_contract.py` | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W4.3** — Add `EMBEDDING_ENABLED` pre-flight check to Chroma retrieval path only (not file fallback path) | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance (hardened)**:

*W4.1 — Chroma opt-in + file fallback*:
- Chroma retrieval is activated only when `CHROMA_PERSIST_DIR` env var is set OR `chromadb_path` arg is explicitly passed; neither set → file-only path, no error
- When Chroma is activated but unavailable (connection error), C0 binding logs a warning and falls back to file-only path; it does NOT raise
- File-only path (default) is completely unchanged and continues to pass existing tests

*W4.2 — FEC field population with correct types (DIRECTLY OBSERVED from `final_evidence_contract.py`)*:
- `citation_map: tuple[tuple[str, str], ...]` — each entry is `(evidence_id, citation_anchor)` from chunk metadata; chunks missing `citation_anchor` are excluded from citation_map and added to `excluded_evidence_refs`
- `source_lineage_map: tuple[tuple[str, str], ...]` — each entry is `(evidence_id, source_id)` from chunk metadata
- `freshness_receipts: tuple[str, ...]` — each entry is the `freshness` ISO8601 field from chunk metadata
- `support_status: str` — computed from evidence sufficiency (not left at `STATUS_UNKNOWN`); must use sentinel vocabulary: `PASS`, `PARTIAL`, `WEAK`, `EMPTY`, `BLOCKED`, `CONFLICTED`, `UNKNOWN`, `NOT_APPLICABLE`
- `excluded_evidence_refs: tuple[str, ...]` — chunks with `invalid_for_normative_use=True` are placed here, never in `evidence_items`
- `l5_certification_ref` must be `"c0-apps-rg-resume-generation-app-payload-b3a449"` (required by `__post_init__` validation — wrong value raises `ValueError`)

*W4.3 — EMBEDDING_ENABLED guard*:
- `EMBEDDING_ENABLED` check runs only on the Chroma code path; when `False` and Chroma retrieval is requested, raises `C0EvidenceGapError("EMBEDDING_ENABLED not set — Chroma retrieval unavailable")` with `action_hint`
- File-only fallback path NEVER raises `C0EvidenceGapError` for missing `EMBEDDING_ENABLED`

---

## Wave 5 — Probe Pack Execution + Gap Report Update + CI Gate

WAVE_ID: W5
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: E

**Phases**:
- **W5.1** — Run all 11 probe queries from `retrieval_probe_pack.json` against live collection | ~2K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W5.2** — Update `apps_rg_retrieval_gap_report.md` with post-ingestion verdict | ~1K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W5.3** — Register `CHECK-RG-CHROMA` CI gate at `ops_scripts/ci/check_apps_rg_chroma_readiness.py` | ~1K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- Probe PQ-001..PQ-010 each return ≥1 result with `citation_anchor` present
- Probe PQ-011 returns zero normative results
- Gap report verdict updated from `NOT_READY` to `READY` or `PARTIAL` based on evidence
- CI gate exits 0; registered in `run_contract_gates.py`

---

## Negative Controls (must hold at all times)

These are hard invariants — any test or probe result violating them is a **blocking defect**, not a warning:

1. **Empty filter → EMPTY, not PASS** — `source_class` filter query with no matching docs returns `support_status=EMPTY`; it does not fall through to a passing verdict.
2. **`invalid_for_normative_use=True` never enters MUST_USE or SUPPORTING** — chunks tagged `invalid_for_normative_use=True` MUST be routed to `excluded_evidence_refs` and `blocked_source_refs`; they must not appear in `evidence_items`.
3. **Missing `citation_anchor` blocks READY verdict** — if a chunk has no `citation_anchor` metadata field, the READY verdict for that corpus is blocked; the chunk is added to `excluded_evidence_refs`, not silently included.
4. **Missing `EMBEDDING_ENABLED` blocks Chroma retrieval** — `EMBEDDING_ENABLED` not set to `"true"` raises `C0EvidenceGapError` on the Chroma path; it never silently returns empty results.
5. **`UNKNOWN` is never PASS** — `support_status_is_passing()` (from `final_evidence_contract.py`) returns `False` for `UNKNOWN`; no downstream gate may treat `UNKNOWN` as a success.
6. **`--execute` without approval raises `MutationNotAuthorizedError`** — preflight guard in `chroma_ingest_pipeline.py` fails if `OPERATOR_APPROVAL_CONFIRMED` is not set; Cursor Agent may not bypass this.

---

## Out Of Scope

- BM25 reranker wiring for apps_rg (GAP-6) — deferred; dense retrieval sufficient for W1–W5
- Graph RAG / C0.3 live backend wiring — `CONFIG_PREPARED_ONLY` stub remains; separate plan required
- New Chroma collection (separate from `process_docs`) — reuses `process_docs` with `source_class` filter per current design
- Resume chunker fine-tuning or chunk-size optimization — hardcode reasonable defaults in W1
- JD persistent corpus — JD is ephemeral per-run; no persistent JD library per audit finding

---

## Execution Details

### W1.1 — Chunker Script

**Scope**: Build `tools/ingestion/chunk_apps_rg_corpus.py` that accepts a `--source-class` arg and a `--input-dir` arg, walks matching files, produces a `.jsonl` output file with `id`, `text`, and all 8 metadata fields.

**Validation constants** (must be enforced by chunker at write time, fail-closed):
```python
SOURCE_CLASS_VOCAB = {
    "candidate_profile", "project_evidence", "approved_examples",
    "rubrics", "governance_docs", "receipts", "prior_outputs",
}
ACL_VOCAB = {"apps_rg:private", "apps_rg:shared"}
AUTHORITY_CLASS_VOCAB = {"PRIMARY", "SUPPORTING", "REFERENCE", "UNVETTED"}
```

**Required output schema** per chunk:
```json
{
  "id": "<sha256 of text[:200]>",
  "text": "<chunk text — empty string is an error>",
  "metadata": {
    "source_id": "<file_path>:<chunk_index>",
    "source_class": "<one of SOURCE_CLASS_VOCAB>",
    "authority_class": "<one of AUTHORITY_CLASS_VOCAB>",
    "freshness": "<ISO8601>",
    "citation_anchor": "<readable cite key — empty string is a warning, blocks READY verdict>",
    "chunk_digest": "<sha256 of text>",
    "app": "apps_rg",
    "ACL": "<one of ACL_VOCAB>"
  }
}
```

**Chunker self-validation rules** (all checked before writing output):
- Duplicate `id` values in output → `ChunkValidationError` (fail-closed)
- `text` is empty string → `ChunkValidationError`
- `source_class` not in `SOURCE_CLASS_VOCAB` → `ChunkValidationError`
- `ACL` not in `ACL_VOCAB` → `ChunkValidationError`
- `citation_anchor` is empty → logged as WARNING; chunk written but added to exclusion list
- `source_class=="candidate_profile"` and PII scrub receipt absent → `PIIScrubReceiptMissingError` (fail-closed)

### W1.2 — Dry-Run Validate

```powershell
# Dry-run (non-mutating) for each corpus jsonl:
python tools/ingestion/chroma_ingest_pipeline.py `
  --input artifacts/apps_rg/retrieval/ingestion_input/wave1_governance_docs.jsonl `
  --chromadb-path data/cache/chromadb
# Expect: dry-run report, 0 writes
```

### W2 — Ingestion Execute Commands (FUTURE — requires explicit user approval)

```powershell
# FUTURE EXECUTE — pre-count first:
python -c "import chromadb; c=chromadb.PersistentClient('data/cache/chromadb'); print('pre:', c.get_collection('process_docs').count())"

# Wave 1: governance_docs
python tools/ingestion/chroma_ingest_pipeline.py --input artifacts/apps_rg/retrieval/ingestion_input/wave1_governance_docs.jsonl --chromadb-path data/cache/chromadb --execute

# Wave 2: candidate_profile (PII scrub required first)
python tools/ingestion/chroma_ingest_pipeline.py --input artifacts/apps_rg/retrieval/ingestion_input/wave2_candidate_profile.jsonl --chromadb-path data/cache/chromadb --execute

# Post-count:
python -c "import chromadb; c=chromadb.PersistentClient('data/cache/chromadb'); print('post:', c.get_collection('process_docs').count())"
```

### W4.1 — C0 Binding Wiring

**Scope**: Extend `apps_rg/runtime/bindings/c0_binding.py::c0_retrieve_apps_rg()` to:
1. Accept optional `chromadb_path: str | None = None` parameter (defaults to `os.getenv("CHROMA_PERSIST_DIR")` or `None`)
2. When `chromadb_path` is `None`: run existing file-only path unchanged
3. When `chromadb_path` is set: check `EMBEDDING_ENABLED=="true"` first; if not set, raise `C0EvidenceGapError`; then instantiate `ChromaResearchStore(chromadb_path)` and call `query_similar()` with `where={"app": "apps_rg", "source_class": "candidate_profile"}` etc.
4. Route chunks with `invalid_for_normative_use=True` → `excluded_evidence_refs` + `blocked_source_refs`; never into `evidence_items`
5. Build `citation_map` as `tuple[tuple[str,str],...]` from `(evidence_id, citation_anchor)` pairs; skip chunks missing `citation_anchor` (add to `excluded_evidence_refs`)
6. Degrade gracefully on Chroma `ConnectionError` or `CollectionNotFoundError` — log warning, fall back to file-only path
7. Pass `l5_certification_ref="c0-apps-rg-resume-generation-app-payload-b3a449"` when constructing `FinalEvidenceContract`

---

## Definition of Done

DoD-1: All 7 resume-relevant source corpora ingested into `process_docs` with `source_class` metadata and all 8 required fields
- Evidence: `python -c "import chromadb; c=chromadb.PersistentClient('data/cache/chromadb'); col=c.get_collection('process_docs'); r=col.get(where={'app': 'apps_rg'}, limit=1, include=['metadatas']); print(r['metadatas'])"` returns records with all 8 fields including `citation_anchor` non-empty
- Negative control: `source_class` filter with no matching docs returns `support_status=EMPTY`
- Status: TODO

DoD-2: Smoke-run: apps_rg pipeline with ChromaDB wired returns FEC with `citation_map` non-empty and `support_status != UNKNOWN`
- Evidence: `python -m apps_rg --dry-run ...` exits 0 with `FinalEvidenceContract.citation_map` non-empty tuple and `support_status` in `{"PASS", "PARTIAL", "WEAK"}`
- Negative control: `EMBEDDING_ENABLED=false` → `C0EvidenceGapError` raised (not silent empty)
- Status: TODO

DoD-3: Probe pack PQ-001..PQ-010 each return ≥1 result with `citation_anchor` present; PQ-011 returns zero normative results
- Evidence: `python tools/retrieval/run_probe_pack.py --pack artifacts/apps_rg/retrieval/retrieval_probe_pack.json` shows PASS for all 11 probes
- Negative control: any probe returning UNKNOWN verdict is treated as a blocking defect
- Status: TODO

DoD-4: CI gate `check_apps_rg_chroma_readiness.py` exits 0; registered in `run_contract_gates.py`
- Evidence: `python ops_scripts/ci/check_apps_rg_chroma_readiness.py` exits 0
- Note: `touches_governance_ci=true` in frontmatter; `run_contract_gates.py` modification is in scope
- Status: TODO

DoD-5: Gap report verdict updated to READY or PARTIAL; audit receipt updated with post-ingestion counts
- Evidence: `artifacts/apps_rg/retrieval/apps_rg_retrieval_gap_report.md` verdict ≠ NOT_READY
- Negative control: verdict READY is blocked if any corpus has zero `citation_anchor`-bearing chunks
- Status: TODO

---

## Verification-vs-Deferral

| Item | Verified in this plan | Deferred |
|---|---|---|
| Corpora ingested (7 source classes) | DoD-1 | — |
| Probe pack returns cited results | DoD-3 | BM25 reranker (GAP-6) |
| FEC citation_map populated | DoD-2 | source_lineage_map deep linking |
| CI gate green | DoD-4 | Graph RAG / C0.3 wiring |
| Gap report verdict updated | DoD-5 | JD persistent corpus |

---

## Hardening Changes Applied

| # | Issue | Fix |
|---|---|---|
| H1 | `touches_governance_ci=false` contradicted W5 CI gate registration | Changed to `true`; DoD-4 note added |
| H2 | Plan implied FEC schema changes in `agentic_core` | Added DIRECTLY OBSERVED evidence: all 5 fields exist in `final_evidence_contract.py` with safe defaults; W4 is apps_rg-side population only; no core changes |
| H3 | `citation_map` described as `List[CitationInfo]` (wrong type) | Corrected to `tuple[tuple[str,str],...]` per `final_evidence_contract.py:305`; `List[CitationInfo]` is the package-driven path only |
| H4 | `l5_certification_ref` not mentioned | Added: must be `"c0-apps-rg-resume-generation-app-payload-b3a449"`; enforced by `__post_init__` |
| H5 | Mutation boundary implicit | Added explicit `--execute` preflight guard (`MutationNotAuthorizedError`); W1/W4 marked NON-MUTATING; W2/W3 marked MUTATION BOUNDARY with same-turn approval requirement |
| H6 | W1 acceptance too loose | Chunker now fail-closed on: duplicate ids, empty text, invalid `source_class`, invalid `ACL`, absent PII scrub receipt for candidate_profile |
| H7 | W4 acceptance underspecified | All 5 FEC fields specified with exact types; `EMBEDDING_ENABLED` guard fires only on Chroma path not file path; file fallback never raises |
| H8 | No negative controls | Added 6 hard invariants: empty filter → EMPTY; `invalid_for_normative_use` never in MUST_USE/SUPPORTING; missing `citation_anchor` blocks READY; missing `EMBEDDING_ENABLED` blocks Chroma; UNKNOWN is never PASS; `--execute` without approval raises |

---

## Cursor Agent Alignment Checks

- Keep always-on rules lean; place detailed procedures in skills or workflows.
- Retrieve local or scoped evidence before synthesis.
- Prefer exact or structural matches before broad semantic expansion.
- Reserve deterministic enforcement for hooks or scripts, not template prose.
