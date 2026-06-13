# W1.1 — Contextual Retrieval Wiring Evidence Audit

**Plan**: `chromadb-best-in-class-agentic-embeddings-c4a1f8`
**Wave/Phase**: W1.1
**Date**: 2026-04-24
**Status**: Audit complete — partial wiring confirmed; 3 residual gaps identified
**Relates-to**: ADR-045 Contextual Retrieval (Proposed, amended 2026-04-24)
**Tier**: T2 (audit, no code changes)

---

## 1. Audit Question

The original gap-plan listed **G1 — No Contextual Retrieval** as P1. Subsequent inspection found ADR-045 already exists and that key modules have shipped. This audit answers: **does the published ADR-045 contract actually run end-to-end, and where does it not?**

## 2. Modules Inspected

| Module | Role per ADR-045 | Present? | Reachable from CLI? |
|---|---|:---:|:---:|
| `tools/ingestion/contextual_chunk_builder.py` | Core builder + `_GatewayProtocol` | ✅ | ✅ |
| `tools/ingestion/qwen_context_gateway.py` | Default local-LLM backend | ✅ | ✅ (`ingest_code.py`) |
| `tools/ingestion/anthropic_context_gateway.py` | Opt-in paid backend | ✅ | ✅ (both ingest scripts) |
| `tools/ingestion/ingest_code.py::_build_context_gateway` | Backend-selection helper | ✅ | ✅ |
| `tools/ingestion/ingest_docs.py` `--contextualize` flag | CLI surface for docs | ✅ | ⚠️ Partial — see Gap A |
| `agentic_core/knowledge/canonical/chunk_manifest.py::situated_context` | Manifest schema 1.1 | Not verified in this audit | — |

## 3. Evidence Captured

### 3.1 `ingest_code.py` honors backend-selection matrix

```
tools/ingestion/ingest_code.py:57-: def _build_context_gateway() -> Any
tools/ingestion/ingest_code.py:49-54: imports anthropic + qwen build_from_env
```

Honors `CONTEXT_GATEWAY` env knob: `auto` (qwen → anthropic → heuristic), `qwen`, `anthropic`, `heuristic|off|none`. Matches ADR-045 §22 backend-selection matrix verbatim.

### 3.2 `ingest_docs.py` does NOT honor the matrix — Anthropic only

```
tools/ingestion/ingest_docs.py:44-46: only imports anthropic_context_gateway
tools/ingestion/ingest_docs.py:589:   gateway = build_anthropic_context_gateway()
```

No qwen import, no `_build_context_gateway()` helper, no `CONTEXT_GATEWAY` env handling. When `ANTHROPIC_API_KEY` is unset, `gateway is None` and `ContextualChunkBuilder` falls back to heuristic — exactly the behaviour ADR-045 §Decision item 1 promised would change. The local-LLM-default amendment (2026-04-24) did **not** propagate to `ingest_docs.py`.

### 3.3 Heuristic-fallback log-line is in place

```
tools/ingestion/ingest_docs.py:591-593: mode = "GATEWAY (Claude-generated)" if gateway else "HEURISTIC (metadata-only)"
```

Operators can now distinguish modes from logs (gap closed by `anthropic-rag-gaps-7f3c2a` P1.1).

### 3.4 ContextualChunkBuilder enforces the protocol

```
tools/ingestion/contextual_chunk_builder.py:152-154:
    if self._gateway is None:
        raise RuntimeError("ContextualChunkBuilder enabled but no gateway adapter injected")
```

Programming-error guard is correct. Heuristic path is taken when `gateway=None` is passed, not when `_enabled=True` and gateway is None at runtime.

## 4. Residual Gaps

### Gap A — `ingest_docs.py` is qwen-blind
- **Symptom:** Docs corpus only gets contextualization when an Anthropic key is set; the documented `$0` local-Qwen default does not apply.
- **Fix shape:** Mirror `ingest_code.py::_build_context_gateway()` into `ingest_docs.py` — same env knob, same chain.
- **Severity:** P2. Largest corpus by file count; without this, contextual retrieval ROI on docs is gated behind a paid API.

### Gap B — `tools/generate/ingestion/*` newer ingestors are not contextualized
- **Symptom:** Newer scripts (`ingest_symbols`, `ingest_arch_docs`, `ingest_repo_evidence`, etc. — see sibling plan `e9aa09` §2.6) have no `--contextualize` flag and no builder wiring at all.
- **Fix shape:** Either route them through the same `_build_context_gateway()` helper, or add a centralized ingest-pipeline hook that contextualizes any chunk before write regardless of script.
- **Severity:** P2. Coverage hole — half the corpus is contextualized, half is not, and a single retrieval may mix both — destabilizing rerank score distributions.

### Gap C — A/B acceptance gate not wired to CI
- **Symptom:** ADR-045 §Decision item 6 sets `Recall@20 ≥ heuristic-baseline + 20%` as the acceptance gate but the `retrieval_benchmark.py` harness is not on a schedule and has no calibration manifest at the path declared in the ADR (`config/retrieval/calibration_manifest.yaml`).
- **Fix shape:** Author the calibration manifest, freeze a 200-pair golden set, schedule nightly via pytest, write to Wave/Phase Convergence on regression. Tracked under W5.1 of the parent plan.
- **Severity:** P1. Without the gate, operators cannot tell if the wiring degrades or regresses.

## 5. Decision

ADR-045 stands. No new ADR. **Three follow-up items** carried forward:

| Item | Owner wave | Effort |
|---|---|---|
| Mirror `_build_context_gateway` into `ingest_docs.py` | W1.1-followup (small code change) | <500 LOC |
| Wire newer `tools/generate/ingestion/*` scripts through the same helper | W1.1-followup (medium) | ~2k LOC across 5-7 files |
| Author calibration manifest + schedule nightly A/B gate | W5.1 (this plan) | spec + harness wiring |

## 6. References

- ADR-045 (with 2026-04-24 amendment)
- Plan `chromadb-bge-retrieval-hardening-e9aa09` §2.6 (orchestrator coverage hole)
- Plan `c0-context-assembly-best-practices-b7c3a1` (parent of ADR-045)
- This plan: `.windsurf/plans/chromadb-best-in-class-agentic-embeddings-c4a1f8.md`
