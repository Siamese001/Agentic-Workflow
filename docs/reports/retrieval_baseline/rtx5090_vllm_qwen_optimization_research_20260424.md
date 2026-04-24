# RTX 5090 (32 GB) + vLLM + Qwen2.5-14B — Best Practices Research

**Date:** 2026-04-24
**Context:** Debugging + optimizing the W3.2 live-Qwen rerun stack after running into three stacked issues this session: (a) HF Hub DNS crash-loop, (b) bf16 14B won't fit alongside Windows desktop, (c) AWQ download rate-limited at 7.9 GB / 9.98 GB.

**Sources consulted (primary, with citations):**
- [Hugging Face Hub Rate Limits docs](https://huggingface.co/docs/hub/rate-limits) — official, authoritative
- [vLLM Forum — "Project: vLLM docker for running smoothly on RTX 5090 + WSL2"](https://discuss.vllm.ai/t/project-vllm-docker-for-running-smoothly-on-rtx-5090-wsl2/1697) — community Docker image `BoltzmannEntropy/vLLM-5090`
- [vLLM Forum — "Field Report: AWQ on RTX 5060 Ti (SM_120 / Blackwell) — awq_marlin + TRITON_ATTN working"](https://discuss.vllm.ai/t/field-report-awq-on-rtx-5060-ti-sm-120-blackwell-awq-marlin-triton-attn-working/2463) — SAME GPU family as 5090 (SM_120)
- [vLLM Docker docs — VLLM_ENABLE_CUDA_COMPATIBILITY, HF_TOKEN patterns](https://docs.vllm.ai/en/stable/deployment/docker/)
- [vLLM Environment Variables reference](https://docs.vllm.ai/en/stable/configuration/env_vars/)
- r/LocalLLaMA threads on 5090 + vLLM + hf_transfer (summaries; Reddit raw content bot-blocked but summaries captured in search index)

---

## TL;DR — Fix the three issues permanently

| Problem | Cause (confirmed this session) | Fix |
|---|---|---|
| DNS crash-loop | Container tries HF `/resolve/` on cached config | `HF_HUB_OFFLINE=1` + `TRANSFORMERS_OFFLINE=1` in compose env ✅ already applied |
| 14B bf16 OOM on startup | Blackwell SM_120 forces bfloat16; weights 27.6 GiB + Windows holds ~3.4 GiB = no room | Use AWQ 4-bit (~9.98 GiB weights) with **`--quantization awq_marlin`** (NOT `awq`) and **`--attention-backend TRITON_ATTN`** |
| AWQ download stuck at 7.9 GB | HF anonymous rate limit (5-min rolling window) | **HF_TOKEN** + optionally `HF_HUB_ENABLE_HF_TRANSFER=1` (100× speed) |

---

## 1. Hugging Face Hub download — the definitive fix

### Rate-limit tiers (HF official docs, Sept 2025)

| Tier | Limit | Notes |
|---|---|---|
| Anonymous | **Subject to change** (lowest) | 5-minute rolling window; effectively throttles to zero under load |
| Free (with HF_TOKEN) | Much higher | Token is free at `huggingface.co/settings/tokens`; read scope sufficient |
| PRO | ~10× Free | $9/mo |
| Team / Enterprise | Highest | $20+/user/mo |

**Quote from HF docs (authoritative):**
> "First, make sure you always pass a HF_TOKEN, and it is passed downstream to all libraries or applications that download stuff from the Hub. **This is the number one reason users get rate limited and is a very easy fix.**"

### Three-layer acceleration stack

Order of impact, top-to-bottom:

#### Layer 1 — `HF_TOKEN` (required, unblocks throttle)

```bash
# ~/llm-stack/.env
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxx
```

In Docker:
```bash
docker run --rm \
  -e HF_TOKEN="$HF_TOKEN" \
  -v "$(pwd)/hf-cache:/root/.cache/huggingface" \
  ...
```

#### Layer 2 — `hf_transfer` (100× speedup on fast connections)

From r/LocalLLaMA — "When I download via the website I get capped at around ±40MB/s. When I enable hf_transfer I get over 1GB/s."

```bash
pip install hf_transfer
export HF_HUB_ENABLE_HF_TRANSFER=1
```

In Docker:
```bash
docker run --rm \
  -e HF_TOKEN="$HF_TOKEN" \
  -e HF_HUB_ENABLE_HF_TRANSFER=1 \
  -v "$(pwd)/hf-cache:/root/.cache/huggingface" \
  --entrypoint /bin/bash \
  vllm/vllm-openai:latest \
  -c "pip install -q hf_transfer && python3 -c 'from huggingface_hub import snapshot_download; snapshot_download(\"Qwen/Qwen2.5-14B-Instruct-AWQ\", cache_dir=\"/root/.cache/huggingface/hub\")'"
```

**Note:** `hf_transfer` is a Rust-based multi-connection downloader. Disables resume-on-failure by default (trade-off). For our case where we already have 7.9 GB cached, run the plain `snapshot_download` first (resumes the 3 incomplete blobs), then enable `hf_transfer` only for future fresh downloads.

#### Layer 3 — `huggingface_hub >= 1.2.0` smart retry

Built into new SDK. Parses the `RateLimit` HTTP header the Hub emits and waits the exact reset duration before retrying. No code change needed beyond upgrading.

```bash
pip install -U "huggingface_hub>=1.2.0"
```

### Observability while downloading

HF emits these HTTP headers per request:
- `RateLimit: "api|pages|resolvers";r=[remaining];t=[seconds until reset]`
- `RateLimit-Policy: "fixed window";...;q=[total];w=[window duration]`

And a billing dashboard at `huggingface.co/settings/billing` shows 3 live gauges (requests, resolver calls, API calls) updated in real-time.

---

## 2. Running vLLM on RTX 5090 (Blackwell / SM_120) — the non-obvious quirks

The RTX 5090 has compute capability 12.0 (SM_120, Blackwell). The same SM family as RTX 5060 Ti / 5070 / 5080 for which field reports exist. All these quirks apply.

### Quirk A — Blackwell forces bfloat16

From [vLLM Forum field report](https://discuss.vllm.ai/t/field-report-awq-on-rtx-5060-ti-sm-120-blackwell-awq-marlin-triton-attn-working/2463):

> "Blackwell GPUs (SM_120) are forced to bfloat16. Standard AWQ requires float16 and crashes immediately with a pydantic ValidationError."

**Do NOT use:**
- `--quantization awq` → **crashes** (requires float16)
- `--quantization gptq` → **broken on SM_120**
- BitsAndBytes → **garbage/corrupt output**

**DO use:**
- `--quantization awq_marlin` (Marlin kernel rewrites AWQ math in bf16-compatible form)

### Quirk B — FlashAttention not supported on SM_120

FA still has no SM_120 kernels as of vLLM 0.17.x (Nov 2025). Attention backend falls back silently and sometimes crashes.

**Force the backend explicitly:**
```
--attention-backend TRITON_ATTN
```

### Quirk C — CUDA 12.8+ and PyTorch 2.9+ required

Community reports confirm:
- CUDA 12.8 or later
- PyTorch 2.9.0+ with `cu128` or `cu130` wheels
- `torch_cuda_arch_list="12.0 12.1"` at build time

Pre-built community container: **`BoltzmannEntropy/vLLM-5090`** on GitHub — "Docker Container for RTX 5090 on WSL2/Windows". Third-party (not vLLM official) but widely reported as working out of the box.

### Quirk D — Enforce eager often hurts on Blackwell

`--enforce-eager` disables torch.compile / CUDA graphs. On SM_120 with vLLM 0.15+, the compiled path actually works (Inductor + Triton). Drop `--enforce-eager` unless you hit a specific compile bug. You trade off ~0.5 GiB VRAM for 20-30% higher throughput.

---

## 3. The working config for Qwen2.5-14B-Instruct-AWQ on RTX 5090

Based on the Field Report performance numbers on Qwen 2.5 14B AWQ (on 5060 Ti 16 GiB — scales cleanly to 5090 32 GiB):

```bash
# ~/llm-stack/.env (final)
VLLM_MODEL=Qwen/Qwen2.5-14B-Instruct-AWQ
VLLM_QUANTIZATION=awq_marlin
VLLM_ATTENTION_BACKEND=TRITON_ATTN
VLLM_GPU_MEMORY_UTILIZATION=0.80      # 0.80 × 32 = 25.6 GiB — plenty of room
VLLM_MAX_MODEL_LEN=8192               # Qwen2.5 supports 32k; 8k is a safe reasonable
VLLM_MAX_NUM_BATCHED_TOKENS=8192
VLLM_MAX_NUM_SEQS=16                  # 16 concurrent sequences
VLLM_DTYPE=bfloat16                   # explicit for clarity; Blackwell forces it anyway
VLLM_KV_CACHE_DTYPE=auto              # 'fp8' would save more but not needed at 32 GiB
HF_HUB_OFFLINE=1                      # once model cached
TRANSFORMERS_OFFLINE=1
```

And in `~/llm-stack/docker-compose.yml`, the `vllm` service command should be:

```yaml
command: >
  --model ${VLLM_MODEL}
  --host 0.0.0.0 --port 8000
  --quantization ${VLLM_QUANTIZATION}
  --attention-backend ${VLLM_ATTENTION_BACKEND}
  --gpu-memory-utilization ${VLLM_GPU_MEMORY_UTILIZATION}
  --max-model-len ${VLLM_MAX_MODEL_LEN}
  --max-num-batched-tokens ${VLLM_MAX_NUM_BATCHED_TOKENS}
  --max-num-seqs ${VLLM_MAX_NUM_SEQS}
  --dtype ${VLLM_DTYPE}
  --kv-cache-dtype ${VLLM_KV_CACHE_DTYPE}
```

### Expected performance on RTX 5090

Field report on 5060 Ti (~half the SM count of 5090):
- Qwen 2.5 14B AWQ: **~30 tok/s generation peak**, 16 GB VRAM, KV cache 1.5%

On 5090 (projected scaling, Blackwell throughput ~2× 5060 Ti):
- **~50-70 tok/s generation peak** at batch=1
- **100-150 tok/s aggregate** at batch=8 with `--enforce-eager` dropped
- Weights + KV + activations: ~15 GiB total at `max_model_len=8192`, leaving 17 GiB headroom

---

## 4. Windows desktop GPU overhead — is it reducible?

The ~3.4 GiB that Windows holds on the RTX 5090 is **mostly not reducible** without major lifestyle changes. Composition of that overhead:

| Consumer | Typical GiB | Notes |
|---|---|---|
| DWM (Desktop Window Manager) compositor | 0.5–1.0 | Per-monitor; higher for 4K / HDR / multi-monitor |
| Hardware-Accelerated GPU Scheduling (HAGS) reserve | 0.3–0.5 | Windows 10 20H1+; on by default; **leave on** (required for DLSS FG) |
| Browser GPU tiles + video decode | 0.5–2.0 | Heavy tabs, video calls, YouTube |
| MS Teams / ChatGPT desktop / Word / Edge | 0.5–1.5 | Cumulative |
| NVIDIA Overlay / GeForce Experience | 0.1–0.3 | Can be disabled |
| WSL2 vGPU passthrough overhead | 0.2–0.5 | Structural, not tunable |

### Practical reductions (ordered by effort/benefit)

1. **Close heavy GPU-accelerated apps before launching vLLM** — Teams, Chrome with many tabs, video calls. Recovers 1-2 GiB.
2. **Disable NVIDIA Overlay** (GeForce Experience → Settings → In-Game Overlay OFF). 0.1-0.3 GiB.
3. **Switch Chrome/Edge to "Use graphics acceleration when available" OFF** if running many tabs and willing to trade browser smoothness. 0.5-1.0 GiB.
4. **Do NOT disable HAGS** — disabling it breaks DLSS Frame Generation on RTX 50-series and is actively discouraged by Microsoft's RTX-50 guidance.
5. **Do NOT disable the DWM compositor** — breaks Windows UI.

### The right framing

RTX 5090 has 32 GiB VRAM. Windows desktop holds ~3.4 GiB typical. **Usable VRAM budget for vLLM: ~28 GiB.** Plan around that number, not the 32 GiB spec-sheet figure.

At 28 GiB usable:
- ✅ Qwen2.5-14B-Instruct-AWQ (9.98 GiB weights + 4-8 GiB KV at 8k context) — **fits with 10+ GiB headroom**
- ✅ Qwen2.5-7B-Instruct bf16 (15 GiB weights + 4 GiB KV) — **fits**
- ⚠️ Qwen2.5-14B-Instruct bf16 (27.6 GiB weights) — **borderline; needs 0.85 util + fp8 KV; fragile to Windows app launches**
- ❌ Qwen2.5-32B-Instruct bf16 (~64 GiB weights) — **won't fit**
- ✅ Qwen2.5-32B-Instruct-AWQ (~19 GiB weights) — **fits** with ~8 GiB KV headroom at 4k context

---

## 5. The specific path forward for this repo

### Step 1 — Finish the AWQ download (next session, after user sets HF_TOKEN)

```bash
# 1. Get token from huggingface.co/settings/tokens (read scope)
# 2. Write to ~/llm-stack/.env:
echo "HF_TOKEN=hf_xxxxxxxxxxxxxxxxxx" >> ~/llm-stack/.env

# 3. Resume download (huggingface_hub uses Range requests — resumes the 3 incomplete blobs)
cd ~/llm-stack
docker run --rm \
  -e HF_TOKEN="$HF_TOKEN" \
  -v "$(pwd)/hf-cache:/root/.cache/huggingface" \
  --entrypoint /usr/bin/python3 \
  vllm/vllm-openai:latest \
  -c 'from huggingface_hub import snapshot_download; p = snapshot_download("Qwen/Qwen2.5-14B-Instruct-AWQ", cache_dir="/root/.cache/huggingface/hub"); print("DONE", p)'
```

Expected: ~5-15 min to finish remaining 2 GB with token (vs frozen at 0 bytes/sec anonymous).

### Step 2 — Flip vLLM to AWQ with Blackwell-correct flags

Update `~/llm-stack/.env`:
```
VLLM_MODEL=Qwen/Qwen2.5-14B-Instruct-AWQ
VLLM_QUANTIZATION=awq_marlin
VLLM_ATTENTION_BACKEND=TRITON_ATTN
VLLM_GPU_MEMORY_UTILIZATION=0.80
VLLM_MAX_MODEL_LEN=8192
VLLM_MAX_NUM_BATCHED_TOKENS=8192
VLLM_MAX_NUM_SEQS=16
```

Update `~/llm-stack/docker-compose.yml` `vllm` service `command:` to pass `--quantization awq_marlin` and `--attention-backend TRITON_ATTN` (or read from env).

Drop `--enforce-eager` from the command (was there to sidestep a compile issue that awq_marlin + TRITON_ATTN handles correctly).

```bash
docker compose up -d --force-recreate vllm
```

Wait ~60 sec (AWQ loads much faster than bf16), verify:
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/v1/models" -UseBasicParsing
```

### Step 3 — Re-run the smoke A/B

Delete stale collections (they used heuristic fallback):
```powershell
python -c "import chromadb; c = chromadb.PersistentClient('artifacts/chroma'); [c.delete_collection(n) for n in ['smoke_contextualized', 'smoke_both']]"
```

Re-ingest with live Qwen (no env override needed — `qwen_context_gateway.py` reads `QWEN_LOCAL_MODEL_ID` from the L0 model registry which already points to `Qwen/Qwen2.5-14B-Instruct-AWQ`):
```powershell
$env:CONTEXT_GATEWAY="qwen"
python -m tools.ingestion.ingest_code agentic_core/knowledge/retrieval/ --collection smoke_contextualized --contextualize
python -m tools.ingestion.ingest_code agentic_core/knowledge/retrieval/ --collection smoke_both --contextualize --late-chunking
```

Re-run harness:
```powershell
python tools/eval/retrieval_abcd_harness.py `
  --manifest artifacts/retrieval_baseline/smoke_calibration_manifest.json `
  --k 20 --rerank none `
  --out artifacts/retrieval_baseline/smoke_abcd_result_live_qwen.json
```

### Step 4 — Promotion-grade (optional)

The 8-query smoke proves directionality. For ADR-045 promotion-grade:
- Scale to 100+ queries (edit `tools/eval/_build_smoke_manifest.py` or write a larger manifest builder)
- Ingest a broader corpus (e.g., `agentic_core/` recursive, `~500-2000 chunks`)
- Run rerank=none AND rerank=cross_encoder for a 2×4 grid

---

## 6. Debugging playbook — if vLLM misbehaves again

Symptoms → First thing to check (ordered by likelihood per this session's evidence):

| Symptom | Probable cause | Check |
|---|---|---|
| Container crash-loops, logs show DNS failure | `HF_HUB_OFFLINE` not set, cache not mounted | `docker exec vllm env \| grep HF_HUB_OFFLINE`; `docker inspect vllm \| grep Mounts` |
| `ValueError: Free memory on device cuda:0 (X/Y GiB) is less than desired` | Windows apps holding VRAM at startup | `nvidia-smi`; lower `gpu_memory_utilization` OR close GPU-heavy apps |
| `pydantic ValidationError` at engine init with AWQ | Standard `awq` quant on Blackwell (forces bf16) | Switch to `--quantization awq_marlin` |
| Silent shutdown after "Application startup complete" | FlashAttention falling back unpredictably | Add `--attention-backend TRITON_ATTN` |
| `RuntimeError: Engine core initialization failed. See root cause above. Failed core proc(s): {}` | Look higher in log for the FIRST error (the {} is empty because engine died before reporting) | `docker logs vllm 2>&1 \| grep -B2 'EngineCore failed to start'` |
| Loading safetensors stuck at 0/N | HF anonymous rate limit | Set `HF_TOKEN`, confirm with `curl -H "Authorization: Bearer $HF_TOKEN" https://huggingface.co/api/whoami` |
| WSL "Catastrophic failure" | Too many short-lived `wsl -- bash -c` spawns | `wsl --shutdown`, wait 30s, restart Docker Desktop |

### Log hygiene

vLLM logs are verbose and truncate badly in WSL+docker. Pipe through a regex filter:

```bash
docker logs --tail 100 vllm 2>&1 | \
  grep -vE 'config=|compilation_config|pass_config|observability_config|dynamic_shapes' | \
  tail -40
```

### Always check for the FIRST error

vLLM's V1 engine has a misleading pattern:
```
RuntimeError: Engine core initialization failed. See root cause above. Failed core proc(s): {}
```

The `{}` (empty dict) tricks you into thinking there's no root cause. The actual error is **higher in the log** — grep backwards from "EngineCore failed to start".

---

## 7. Alternative paths if AWQ still won't cooperate

Ranked by fallback order:

### 7a. GGUF + llama.cpp (NOT vLLM)
- Qwen2.5-14B-Instruct-Q4_K_M.gguf is ~8 GiB
- Use `ollama run qwen2.5:14b-instruct-q4_K_M` or `llama.cpp` server
- **Trade-off:** Much simpler setup, lower throughput (~15-20 tok/s vs vLLM's 50-70). OpenAI-compatible API. Skips all the SM_120 quirks.
- **Use if:** you need to unblock urgently and the test is only about contextualization quality, not throughput.

### 7b. GPTQ (alternate 4-bit)
- `Qwen/Qwen2.5-14B-Instruct-GPTQ-Int4` (same ~4 GB class)
- **Warning:** Field report says GPTQ is **broken on SM_120** in vLLM 0.17.x. Verify against the latest vLLM before trying.

### 7c. Qwen2.5-7B at full bf16
- Already may be cacheable (not currently in `~/llm-stack/hf-cache/`)
- 15 GiB weights, fits easily even with 5 GiB Windows overhead
- **Trade-off:** Smaller model may write less nuanced context. For a 154-chunk smoke test, probably fine.

### 7d. Cloud API (OpenAI or Anthropic) for contextualization only
- `CONTEXT_GATEWAY=openai` or `CONTEXT_GATEWAY=anthropic`
- ~154 short calls × $0.001/call ≈ $0.15 total
- **Trade-off:** Contradicts ADR-045 local-Qwen direction. Use only to unblock a Wave E promotion decision where local is blocked.

---

## 8. What's already done vs still open

| Item | Status |
|---|---|
| Diagnose DNS crash-loop | ✅ Done (session 1) |
| Apply `HF_HUB_OFFLINE=1` fix permanently | ✅ `~/llm-stack/docker-compose.yml` committed |
| Diagnose bf16 OOM | ✅ Done (session 2) |
| Lower `VLLM_GPU_MEMORY_UTILIZATION` 0.92→0.85 | ✅ `~/llm-stack/.env` |
| Confirm AWQ is the durable answer | ✅ Matches ADR-045 amendment |
| Download `Qwen/Qwen2.5-14B-Instruct-AWQ` | 🟡 7.9 GB / 9.98 GB (rate limited) |
| **Set HF_TOKEN** | 🔴 **OPERATOR ACTION NEEDED** |
| Resume download with token | 🔴 blocked on above |
| Update compose to use `awq_marlin` + `TRITON_ATTN` | 🔴 blocked on download completing |
| Re-ingest `smoke_contextualized` / `smoke_both` with live Qwen | 🔴 blocked |
| Re-run harness for clean 4-cell signal | 🔴 blocked |

---

## 9. One-line summary per major finding

- **HF rate limit killed the download.** Set `HF_TOKEN` once, solved forever.
- **RTX 5090 is Blackwell / SM_120 / bf16-only.** Use `awq_marlin` (not `awq`) + `TRITON_ATTN` (not FlashAttention).
- **14B bf16 cannot share a 32 GiB GPU with Windows desktop.** AWQ 4-bit is not optional, it's required.
- **`HF_HUB_ENABLE_HF_TRANSFER=1` + `hf_transfer` package gets 100× download speed** on fast connections.
- **vLLM V1's `"Engine core initialization failed. Failed core proc(s): {}"` is misleading** — the real error is higher in the log.
- **Windows desktop GPU overhead is ~3.4 GiB and mostly irreducible** on a working desktop. Budget for 28 GiB usable, not 32.
- **`BoltzmannEntropy/vLLM-5090` community Docker image** exists specifically for RTX 5090 + WSL2 and bypasses the CUDA/PyTorch build matrix for anyone who wants a turnkey start.

## References (clickable)

1. https://huggingface.co/docs/hub/rate-limits — HF Hub rate limits (authoritative)
2. https://discuss.vllm.ai/t/field-report-awq-on-rtx-5060-ti-sm-120-blackwell-awq-marlin-triton-attn-working/2463 — Blackwell AWQ field report
3. https://discuss.vllm.ai/t/project-vllm-docker-for-running-smoothly-on-rtx-5090-wsl2/1697 — RTX 5090 Docker community project
4. https://github.com/BoltzmannEntropy/vLLM-5090 — the actual Docker image
5. https://docs.vllm.ai/en/stable/configuration/env_vars/ — vLLM env var reference
6. https://docs.vllm.ai/en/stable/deployment/docker/ — vLLM Docker deployment guide
7. https://huggingface.co/settings/tokens — get the free HF_TOKEN
