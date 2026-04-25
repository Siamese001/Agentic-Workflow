---
trigger: model_decision
description: Apply when advising on local LLM model size, quantization, VRAM budgeting, or vLLM/llama.cpp configuration on the local RTX 5090 + WSL2 + Docker stack. Corrects the common framing error of treating Windows desktop overhead as a major VRAM cost.
---

# Local LLM Runtime — WSL2/Docker, not Windows

> ⛔ When reasoning about VRAM budgets or model-size feasibility for the local
> Qwen vLLM stack, frame the runtime as **WSL2 + Docker with CUDA passthrough**.
> Do NOT reason from a "Windows desktop overhead" baseline.

## Hardware (this workstation)

| Item | Value |
|------|-------|
| GPU | NVIDIA RTX 5090 (Blackwell, SM_120) |
| Total VRAM | 32,607 MiB |
| Driver path | Windows WDDM → WSL2 CUDA passthrough → Docker `--gpus all` → vLLM container |
| Windows desktop compositor overhead | ~1–2 GB (small, varies with foreground apps) |
| Practical usable VRAM for vLLM | ~29–30 GB |

## Model VRAM footprint (AWQ 4-bit, 8K context, vLLM v0.11 V1 engine)

| Model | Weights | KV cache (8K) | Framework | Total | Verdict on this rig |
|-------|---------|---------------|-----------|-------|---------------------|
| Qwen2.5-7B-AWQ | ~5 GB | ~1.5 GB | ~2 GB | ~8.5 GB | ✅ comfortable |
| Qwen2.5-14B-AWQ | ~10 GB | ~3 GB | ~2 GB | ~15 GB | ✅ comfortable |
| **Qwen2.5-32B-AWQ** | ~20 GB | ~5 GB | ~2 GB | **~27 GB** | ✅ **feasible** with `gpu_memory_utilization=0.85`, `max_model_len ≤ 8192` |
| Qwen2.5-72B-AWQ | ~42 GB | — | — | ≥42 GB | ❌ won't fit |

## Forbidden framings

- ❌ "32B will OOM because of Windows overhead" — wrong: WSL2 has near-direct CUDA access; Windows process tree is **not** the container's allocator.
- ❌ Citing "~3.4 GB Windows desktop overhead" as a reason to downsize.
- ❌ Treating the host Windows process state as a constraint on the WSL2 Docker container's CUDA memory.

## Required framings

- ✅ Quote VRAM math from the **container CUDA allocator** vantage point.
- ✅ When `nvidia-smi` (run from WSL or Windows) shows X MiB used, treat that as the floor; remainder is available to vLLM.
- ✅ For model-size selection on this rig: 32B is the **canonical production choice** (fits at `gpu_memory_utilization=0.92`, `max_model_len=16384`), 72B is out.

## Stack location (canonical — Stack A)

**All model weights live on the WSL2 ext4 VHDX, NOT on Windows `C:\`.**

```
/home/amita/                       # WSL2 Ubuntu-24.04 user home, /dev/sdd ext4
├── models/Qwen2.5-32B-Instruct-AWQ/    # ✅ canonical model dir (~19 GB, 5 safetensors shards)
├── .vllm_env/                          # ✅ Python venv with vllm 0.16.0
└── .config/systemd/user/vllm.service   # ✅ user-mode systemd unit (calls Stack A launcher)
```

**Repo-side launcher** (Windows-side `C:\Git\Agentic-Workflow\tools\vllm\`, accessed via `/mnt/c`):
- `start_vllm_server_32b.sh` — canonical launcher (gpu_util 0.92, max_model_len 16384, AWQ)
- `vllm.service` — systemd unit (deployed to `~/.config/systemd/user/`)
- `check_vllm.sh` — health probe

Active runtime flags (Stack A):
```
--model /home/amita/models/Qwen2.5-32B-Instruct-AWQ
--served-model-name Qwen/Qwen2.5-32B-Instruct-AWQ
--host 0.0.0.0 --port 8000
--quantization awq --dtype float16
--gpu-memory-utilization 0.92
--max-model-len 16384
--max-num-seqs 24
--disable-log-requests
```

> **Never put model weights on `/mnt/c/...`** — Windows NTFS access through 9P over the WSL relay is ~10× slower than native ext4 and breaks fastpath mmap. The 9.4 GB AWQ model loads in ~30 s from ext4 VHDX vs minutes from `/mnt/c`.

## Retired stack (deleted 2026-04-24)

`~/llm-stack/` — Docker compose attempt with `vllm/vllm-openai:v0.11.0`, separate hf-cache. Retired in favor of Stack A. Caused config-drift confusion. Do not resurrect without retiring Stack A first.

## Known operational quirks (don't re-discover these)

1. **vLLM `latest` (v0.15.x) has a pydantic JSON-parse bug** in `VllmConfig` validator on Blackwell. Pin `v0.11.0`.
2. **vLLM v0.11 requires V1 engine** — `assert envs.VLLM_USE_V1` fires on V0. Always set `VLLM_USE_V1=1`.
3. **vLLM v0.11 positional `model_tag` ≠ `--model`** — the positional arg is decorative; you MUST pass `--model` explicitly or it loads `Qwen3-0.6B` (the default).
4. **Memory profiling can race during init** — "Initial free memory > current free memory" assertion. Workaround: just retry; succeeds on second attempt.
5. **HF Hub free-tier rate limits per token** — large multi-shard downloads (>10 GB / 8h window) get throttled to ~100 KB/s. Use community GGUF mirrors as a fallback CDN path when needed.
6. **WSL2 bind-mount + hf_transfer mmap is broken** — hf_transfer pre-allocates a sparse file and then buffers writes in memory rather than landing on the bind-mounted disk. Symptom: `du -h` stays at 4.2 MB while `NetIO` shows GB-scale throughput. Workaround: use plain `requests` with explicit per-chunk `flush()`+`fsync()`, OR download to container overlay-fs first then `cp` to bind-mount.

## References

- Research report: `docs/reports/retrieval_baseline/rtx5090_vllm_qwen_optimization_research_20260424.md`
- AWQ resume notes: `docs/reports/retrieval_baseline/c0_w3_2_vllm_awq_resume_notes_20260424.md`
- ADR-045 (contextualization backend): `docs/architecture/adr/ADR-045-contextual-retrieval.md`
