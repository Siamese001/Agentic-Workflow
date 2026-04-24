# Wave C0 W3.2 — vLLM Qwen Live-Rerun Resume Notes (2026-04-24)

**Plan:** `.windsurf/plans/c0-context-assembly-best-practices-b7c3a1.md`
**Phase:** W3.2 — live-Qwen rerun of the smoke A/B for ADR-045 promotion-grade contextualization signal
**Session status:** **BLOCKED — HF Hub rate limited the AWQ download at ~7.9 GB of 9.98 GB**

## Why this phase is partially done

Wave E closed with a real smoke signal (`+21.2` pts Recall@20 from `late_chunked`; `+15.4` pts from `contextualized` with heuristic fallback). The remaining scope is a clean 4-cell A/B where the `contextualized` and `both` cells use **real Qwen-written context** instead of the heuristic fallback. That requires a running Qwen vLLM server.

## What was discovered and fixed this session

### 1. DNS fix (PERMANENT) — `~/llm-stack/docker-compose.yml`

Docker container `vllm` was crash-looping on `Temporary failure in name resolution` for `huggingface.co` even though the 28 GB HF cache was mounted. vLLM tries to validate `config.json` online before using cache.

**Applied**: Added `HF_HUB_OFFLINE=1` and `TRANSFORMERS_OFFLINE=1` to the `vllm` service environment block. Backup at `~/llm-stack/docker-compose.yml.bak`.

### 2. VRAM config tightened — `~/llm-stack/.env`

**Changed**: `VLLM_GPU_MEMORY_UTILIZATION=0.92` → `0.85` because the prior value failed startup:

```
ValueError: Free memory on device cuda:0 (28.42/31.84 GiB) on startup is less than
desired GPU memory utilization (0.92, 29.29 GiB).
```

Even at 0.85, Qwen2.5-14B bf16 (27.57 GiB weights) does not reliably fit because Windows desktop apps (NVIDIA compositor, browser GPU, etc.) consistently hold ~3.4 GiB of the 32 GiB total. `0.85 × 31.84 = 27.06 GiB` target, but need ~28 GiB for weights + minimal KV — fails during KV cache allocation.

### 3. Root-cause confirmation: 14B bf16 does not fit alongside Windows

The ADR-045 amendment already specifies `Qwen/Qwen2.5-14B-Instruct-AWQ` (4-bit AWQ quantization, ~9.98 GB weights) — that's the durable answer for a 32 GiB GPU shared with a Windows desktop.

## AWQ download — partial cache preserved

**Location:** `~/llm-stack/hf-cache/hub/models--Qwen--Qwen2.5-14B-Instruct-AWQ/`

**State at session end:**
- Complete blobs: 10 of 13 (config.json, generation_config.json, merges.txt, tokenizer.json, tokenizer_config.json, vocab.json, README.md, LICENSE, .gitattributes, model.safetensors.index.json)
- **Incomplete blobs**: 3 weight shards, frozen at 2,023,056,736 / 2,147,483,648 / 2,348,810,240 bytes
- **Total on disk**: ~7.9 GB of 9.98 GB (metadata from `model.safetensors.index.json.metadata.total_size`)
- **Download rate**: 25 MB/s initial → 1 MB/s → 0 MB/s over 30 minutes = HF Hub anonymous-tier rate limit

## Resume procedure (next session)

### Option A: Set an HF token (fastest)

1. Get a free token at `huggingface.co/settings/tokens` (read-only scope is enough).
2. Add to `~/llm-stack/.env`:
   ```
   HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```
3. Re-run:
   ```bash
   cd ~/llm-stack
   docker run --rm \
     -e HF_TOKEN="$HF_TOKEN" \
     -v "$(pwd)/hf-cache:/root/.cache/huggingface" \
     --entrypoint /usr/bin/python3 \
     vllm/vllm-openai:latest \
     -c 'from huggingface_hub import snapshot_download; p = snapshot_download("Qwen/Qwen2.5-14B-Instruct-AWQ", cache_dir="/root/.cache/huggingface/hub"); print("DONE", p)'
   ```
   `huggingface_hub` uses HTTP Range requests, so it will resume the 3 incomplete blobs from their current offsets — not re-fetch the 7.9 GB already cached.

### Option B: Retry from a fresh IP / different time-of-day

The anonymous rate limit typically clears within 2–6 hours. Same command without `HF_TOKEN`, just re-run.

## After the download completes

### 1. Switch vLLM to AWQ

Edit `~/llm-stack/.env`:

```
VLLM_MODEL=Qwen/Qwen2.5-14B-Instruct-AWQ
VLLM_GPU_MEMORY_UTILIZATION=0.60   # AWQ weights are ~9.98 GB; 0.60 × 32 = 19.2 GiB is plenty
VLLM_MAX_MODEL_LEN=4096            # now that we have VRAM headroom
VLLM_MAX_NUM_BATCHED_TOKENS=4096
VLLM_MAX_NUM_SEQS=8
```

Then:
```bash
cd ~/llm-stack
docker compose up -d --force-recreate vllm
```

Wait ~90 seconds, verify from Windows:
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/v1/models" -UseBasicParsing
```

Expect `HTTP 200` with `Qwen/Qwen2.5-14B-Instruct-AWQ` in the body.

### 2. Re-run the 4-cell smoke A/B

The Python gateway (`tools/ingestion/qwen_context_gateway.py`) already resolves `Qwen/Qwen2.5-14B-Instruct-AWQ` as its default model ID from the L0 model registry — no code change needed.

```powershell
# Delete stale collections that used heuristic fallback
# (chroma persistent path from the ingest config)
python tools/ingestion/_delete_chroma_collections.py smoke_contextualized smoke_both

# Re-ingest with live Qwen
python -m tools.ingestion.ingest_code agentic_core/knowledge/retrieval/ `
  --collection smoke_contextualized --contextualize
python -m tools.ingestion.ingest_code agentic_core/knowledge/retrieval/ `
  --collection smoke_both --contextualize --late-chunking

# Re-run harness
python tools/eval/retrieval_abcd_harness.py `
  --manifest artifacts/retrieval_baseline/smoke_calibration_manifest.json `
  --k 20 --rerank none `
  --out artifacts/retrieval_baseline/smoke_abcd_result_live_qwen.json
```

### 3. Expected outcome

If live-Qwen context is adding real signal (vs the heuristic fallback that retained raw chunk text), we expect:
- `contextualized` cell: R@20 around 0.95 (up from 0.942 with heuristic)
- `both` cell: may finally separate from `contextualized` and hit ~1.000 (compounded benefit of LLM context + late chunking single-pass encoding)

If no separation emerges, that's itself a meaningful finding — the heuristic is already capturing most of the signal for this corpus, and ADR-045's LLM-contextualization tax may not be justified at this corpus size.

## Files this session touched

| File | Change |
|---|---|
| `~/llm-stack/docker-compose.yml` | Added `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1` (permanent). Backup at `.bak`. |
| `~/llm-stack/.env` | `VLLM_GPU_MEMORY_UTILIZATION` 0.92 → 0.85 |
| `~/llm-stack/hf-cache/hub/models--Qwen--Qwen2.5-14B-Instruct-AWQ/` | Partial cache, ~7.9 GB |

No repo code changes beyond this doc.
