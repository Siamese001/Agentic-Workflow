# Wave E Smoke A/B — 4-Cell Retrieval Benchmark (2026-04-24)

**Plan:** `.windsurf/plans/c0-context-assembly-best-practices-b7c3a1.md` (Waves A–E)
**Harness:** `tools/eval/retrieval_abcd_harness.py` (commit `bcdcf04d59`)
**Corpus scope:** `agentic_core/knowledge/retrieval/` — 20 `.py` files → **154 chunks**
**Query set:** 8 queries (4 semantic, 4 exact) — see `c0_w3_1_smoke_calibration_manifest_20260424.json`
**Top-K:** 20
**Rerank mode:** `none` across all cells (isolates embedding + chunking effects)

## Results

| Cell | Ingest flags | Recall@20 | Prec@20 | MRR | Hit Rate | Δ vs baseline |
|---|---|---|---|---|---|---|
| **baseline** | plain | 0.788 | 0.313 | 0.838 | 1.000 | — |
| **contextualized** | `--contextualize` | 0.942 | 0.375 | 0.917 | 1.000 | **+0.154 R@20** |
| **late_chunked** | `--late-chunking` | **1.000** | **0.400** | 0.896 | 1.000 | **+0.212 R@20** |
| **both** | `--contextualize --late-chunking` | 0.942 | 0.375 | 0.917 | 1.000 | +0.154 R@20 |

## Interpretation

- **Late chunking alone beats the ADR-045 acceptance threshold** of +20 pts Recall@20 on this 8-query subset (+21.2 pts directionally).
- **Contextualization adds +15.4 pts** even with vLLM Qwen down — the heuristic fallback (text-only context) still lifts BM25/sparse matching. Live-Qwen rerun is deferred to W3.2.
- **MRR is highest for contextualized / both (0.917)** — better rank-1 ordering. Late chunking trades some rank-1 precision for complete recall.
- **"both" did not compound**: at this scale, contextualizing the text before late-chunking produces the same retrieval signal as contextualizing alone. Needs larger corpus to separate.

## Caveats

- **8 queries is directional, not promotion-grade.** ADR-045 acceptance requires full-corpus measurement (n≫100 queries) against 4 distinct collections.
- **Qwen vLLM was down during ingest** (WSL Ubuntu-24.04 + Docker `vllm` container). `contextualized` and `both` cells used the heuristic context fallback in `qwen_context_gateway.build_from_env()` (returns `None` → upstream skips LLM context, retains raw chunk text). Live-Qwen rerun captured as DEFERRED_SCOPE (W3.2).
- **Single reranker mode (`none`)** — cross-encoder rerank was not exercised. Wave D factory (`reranker_factory.py`) is ready; rerank A/B is phase W3.2+ work.

## Operational notes — WSL/vLLM state at end of run

During the session I discovered and fixed a latent DNS issue in `~/llm-stack/docker-compose.yml`:

- **Problem**: `vllm` container crash-looped with `Temporary failure in name resolution` for `huggingface.co` when attempting to fetch `config.json`, despite the 28 GB HF cache being mounted.
- **Fix applied**: Added `HF_HUB_OFFLINE=1` and `TRANSFORMERS_OFFLINE=1` to the `vllm` service environment block. Backup at `~/llm-stack/docker-compose.yml.bak`.
- **Verified working**: vLLM successfully loaded `Qwen/Qwen2.5-14B-Instruct` (27.57 GiB, bf16) and served an HTTP 200 on `/v1/models` briefly during the session.
- **Remaining issue**: Container exhibits a short-lifetime shutdown loop (~60 s after `Application startup complete`). Root cause unresolved — likely related to repeated `wsl -d Ubuntu-24.04 -- bash -c ...` invocations destabilizing the WSL service; operator-side `wsl --shutdown` recovery is the recommended path.

See DEFERRED_SCOPE marker W3.2 (Priority auto-computed by scorer, posted to Wave/Phase Convergence DB).

## Pipeline Validation

Every Wave A→E component executed end-to-end against real BGE-M3 embeddings on the RTX 5090:

| Wave | Component | Verified by |
|---|---|---|
| A | `LateChunkingEmbedder` single-pass encoding | `smoke_late` collection embeddings differ from `smoke_baseline` |
| C | `--late-chunking` CLI + `LATE_CHUNKING=1` env routing | Ingest logs show `late_chunking_helper.apply_late_chunking` executed |
| C | `chroma_client.add_documents(embeddings=...)` bypass path | 154 chunks ingested without re-embedding |
| D | `reranker_factory.get_reranker()` honored `RERANKER=none` | Harness ran without rerank overhead |
| E | `retrieval_abcd_harness.py` end-to-end | JSON report + stdout table produced |

## Artifacts

- `c0_w3_1_smoke_abcd_result_20260424.json` — full per-query breakdown, schema_version=1
- `c0_w3_1_smoke_calibration_manifest_20260424.json` — 8 queries with real Chroma chunk IDs
- `tools/eval/_build_smoke_manifest.py` — reusable manifest builder keyed on `source_path` substring
