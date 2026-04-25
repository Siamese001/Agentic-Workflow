# tools/vllm — Local Qwen/vLLM Server (CANONICAL)

> ⛔ **This is the canonical local-LLM stack.** Do not stand up a parallel
> Docker/compose stack. Two parallel stacks caused a full-day-of-engineering
> incident on 2026-04-24 (config drift, port fight, ~140 GB duplicated weights).
> See `.windsurf/rules/local-llm-wsl2-gpu.md` and "Retired alternatives" below.

Serves `Qwen/Qwen2.5-32B-Instruct-AWQ` via vLLM on an RTX 5090 in WSL2 Ubuntu-24.04.
OpenAI-compatible API at `http://localhost:8000/v1` consumed by all `apps_*`
orchestrators via `agentic_core.L3_orchestration.inference.qwen_vllm`.

## Architecture

```
WSL2 Ubuntu-24.04
  → ~/.vllm_env (native venv)
  → systemctl --user start vllm
  → bash tools/vllm/start_vllm_server_32b.sh
  → vllm.entrypoints.openai.api_server
  → ~/models/Qwen2.5-32B-Instruct-AWQ/
  → CUDA 12.8 → RTX 5090 (Blackwell SM_120, 32 GB VRAM)
  → :8000/v1
```

**Why native venv (not Docker)**: WSL2 bind-mounts have a sparse-write/mmap
bug with Docker that breaks `hf_transfer` and stalls model writes. Native
venv reads ext4 directly with no overlay penalty. AWQ load time: ~30 s.

## Contents

| File | Purpose |
|---|---|
| `start_vllm_server_32b.sh` | **Canonical startup** — 32B-AWQ, float16, 16k ctx, gpu_util=0.92 |
| `download_qwen_32b_awq.sh` | Pull `Qwen/Qwen2.5-32B-Instruct-AWQ` weights from HF (~20 GB) |
| `check_vllm.sh` | Health probe — exit 0 iff `/v1/models` returns a model |
| `vllm.service` | systemd user unit for WSL autostart |
| `_optimize_vhdx_diskpart.ps1` | Windows: compact ext4.vhdx after large model swaps |

## First-time setup

Run once inside WSL Ubuntu:

```bash
# 1. Create venv + install vLLM
python3.12 -m venv ~/.vllm_env
~/.vllm_env/bin/pip install vllm huggingface_hub hf_transfer

# 2. Download 32B-AWQ weights (~20 GB)
bash tools/vllm/download_qwen_32b_awq.sh

# 3. Smoke-start the server
bash tools/vllm/start_vllm_server_32b.sh
```

## Autostart on WSL boot

```bash
mkdir -p ~/.config/systemd/user
cp tools/vllm/vllm.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now vllm.service
journalctl --user -u vllm.service -f    # tail logs
```

## Environment overrides

```
VLLM_BASE_URL=http://<wsl-ip>:8000/v1
VLLM_MODEL_NAME=Qwen/Qwen2.5-32B-Instruct-AWQ
```

## Health check

```bash
bash tools/vllm/check_vllm.sh
# → OK: vLLM serving Qwen/Qwen2.5-32B-Instruct-AWQ at http://localhost:8000/v1
```

Exit code 0 = healthy, 1 = unreachable / malformed response.

## Model

- **Production**: `Qwen/Qwen2.5-32B-Instruct-AWQ` (~20 GB, 5 shards)
- **Location**: `~/models/Qwen2.5-32B-Instruct-AWQ/` (WSL2 ext4 VHDX, NOT `/mnt/c`)
- **Quantization**: AWQ 4-bit (`float16` required, not `bfloat16`)
- **Context**: 16,384 tokens (capped from 32k to fit larger weights in 32 GB VRAM)
- **GPU util**: 0.92 × VRAM (≈29.3 GiB); at idle: ~30.7 GiB used
- **Max seqs**: 24 concurrent sequences

> **OOM headroom note**: At high concurrent load, lower `GPU_UTIL=0.88` in
> `start_vllm_server_32b.sh` and `systemctl --user restart vllm`. Adds ~1.3 GB
> KV-cache headroom at ~5% throughput cost.

## VHDX disk reclaim (after large model swaps)

When deleting models or pruning Docker images, WSL2's ext4 VHDX retains
allocated blocks until explicitly compacted. Run from **elevated** PowerShell:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File C:\Git\Agentic-Workflow\tools\vllm\_optimize_vhdx_diskpart.ps1
# Stops Docker Desktop, shuts down WSL, diskpart compact, restarts Docker.
# Last run 2026-04-25: 142.85 GB → 93.93 GB (48.92 GB reclaimed).
```

## Retired alternatives (do not resurrect)

| Stack | Location | Retired | Reason |
|---|---|---|---|
| Stack B (Docker compose) | `~/llm-stack/` (deleted) | 2026-04-24 | WSL2 bind-mount + hf_transfer stalled; corrupt shard; redundant 102 GB images |
| Qwen2.5-14B-Instruct-AWQ | `~/models/` (deleted) | 2026-04-25 | Superseded by 32B; freed 9.4 GB |

See `.windsurf/rules/local-llm-wsl2-gpu.md` for full failure-mode documentation.
