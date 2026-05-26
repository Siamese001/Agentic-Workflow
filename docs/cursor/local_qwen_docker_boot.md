# Cursor — Local Qwen vLLM Docker boot (operator SSOT)

> **Last updated:** 2026-05-26  
> **Briefing note (one-pager):** [briefing_local_qwen_docker_boot_20260526.md](briefing_local_qwen_docker_boot_20260526.md)  
> **Compose SSOT:** [`docker-compose.qwen.yml`](../../docker-compose.qwen.yml)  
> **Topology:** [`docs/architecture/qwen-vllm-topology.md`](../architecture/qwen-vllm-topology.md)  
> **VRAM / Blackwell quirks:** [`.cursor/rules/local-llm-wsl2-gpu.mdc`](../../.cursor/rules/local-llm-wsl2-gpu.mdc)

Use this runbook before live `qwen_vllm` / `python -m apps_rg` work in Cursor on **Windows + Docker Desktop + WSL2**.

---

## Prerequisites

| Check | Command |
|-------|---------|
| Docker Desktop running | `docker info` |
| WSL model weights (~19 GB) | `wsl -e test -f /home/amita/models/Qwen2.5-32B-Instruct-AWQ/config.json && echo OK` |
| GPU visible to Docker | `docker run --rm --gpus all nvidia/cuda:12.0.0-base-ubuntu22.04 nvidia-smi` (optional smoke) |

Override model host path (non-default install):

```bash
export QWEN_MODEL_HOST_PATH=/path/on/wsl/to/Qwen2.5-32B-Instruct-AWQ
```

---

## Boot (canonical — run Compose from WSL)

**Do not** run `docker compose -f docker-compose.qwen.yml` from PowerShell alone: a bind mount of `/home/amita/models/...` often resolves to an **empty** `/models/qwen` inside the container.

From **PowerShell** (repo on `C:\Git\Agentic-Workflow-FRESH`):

```powershell
wsl -e bash -lc 'cd /mnt/c/Git/Agentic-Workflow-FRESH && docker compose -f docker-compose.qwen.yml up -d qwen-vllm'
```

Or use the helper script (same behavior):

```powershell
wsl bash /mnt/c/Git/Agentic-Workflow-FRESH/ops_scripts/apps_rg/boot_local_qwen_vllm.sh
```

**First boot / recreate** after changing image, `max-model-len`, or mount:

```powershell
wsl -e bash -lc 'cd /mnt/c/Git/Agentic-Workflow-FRESH && docker compose -f docker-compose.qwen.yml up -d --force-recreate qwen-vllm'
```

---

## Verify (fail-closed)

### 1. Bind mount (weights on disk, not re-downloading from Hub)

```powershell
docker exec local-qwen-vllm test -f /models/qwen/config.json && echo mount_ok
```

If this fails, recreate via **WSL compose** (see Boot above). Do not rely on in-container Hugging Face download for the 32B AWQ checkpoint.

### 2. HTTP readiness (model loaded, not just port open)

```powershell
curl -fsS http://localhost:8000/v1/models
```

Expect JSON with `"id":"Qwen/Qwen2.5-32B-Instruct-AWQ"` and `"max_model_len":24576`.

Cold load from local EXT4 weights is typically **2–4 minutes**; Hub download can take **30+ minutes** without `HF_TOKEN`.

### 3. Repo diagnostic

```powershell
cd C:\Git\Agentic-Workflow-FRESH
python -c "from agentic_core.L2_execution.healers.qwen_strict_diagnostic import diagnose; d=diagnose(); print(d.status, d.message)"
```

Expect: `ok Qwen vLLM healthy ...`

### 4. Container policy (stability)

```powershell
docker inspect local-qwen-vllm --format "Restart={{.HostConfig.RestartPolicy.Name}} Shm={{.HostConfig.ShmSize}}"
```

Expect: `Restart=unless-stopped` and `Shm=17179869184` (16 GiB). Default Docker **64 MiB** `/dev/shm` causes worker crashes under load.

---

## Daily lifecycle

| Action | Command |
|--------|---------|
| Start existing container | `docker start local-qwen-vllm` |
| Stop (honored across reboot) | `docker stop local-qwen-vllm` |
| Logs | `docker logs local-qwen-vllm --tail 50 -f` |
| Full apps_rg runtime fix (vLLM + WSL venv) | `.\ops_scripts\apps_rg\Fix-AppsRgWslRuntime.ps1` |

Set `VLLM_MAX_MODEL_LEN=24576` in the shell or `.env` to match the container (see [`executive_summary_operator_guide.md`](../apps_rg/executive_summary_operator_guide.md)).

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|----------------|-----|
| `Invalid repository ID: '/models/qwen'` | Empty bind mount (compose/run from Windows without WSL path) | Boot via **WSL compose**; verify mount step above |
| `vllm_container_down` while container is `Up` | Model still loading; `/v1/models` not ready yet | Wait 2–4 min; watch `docker logs` for `Application startup complete` |
| Container exits / restart loop | OOM, bad image, or missing weights | Lower `--gpu-memory-utilization` to `0.88` (compose default); confirm mount; check `docker logs` |
| Slow boot every recreate | HF re-download (~20 GB) | Mount `~/models/Qwen2.5-32B-Instruct-AWQ`; optional `HF_TOKEN` in `.env` only for hub updates |
| Frequent manual restarts | Old container had `RestartPolicy=no` | Recreate with compose (`restart: unless-stopped`) |

**Discouraged:** `APPS_RG_QWEN_VLLM_DOCKER_RESTART=always` before every run — forces a full model reload (~minutes).

---

## What compose configures (summary)

| Setting | Value |
|---------|--------|
| Container | `local-qwen-vllm` |
| Image | `vllm/vllm-openai:v0.11.0` (pinned; see topology for digest discipline) |
| Model path | `/models/qwen` ← bind `${QWEN_MODEL_HOST_PATH:-/home/amita/models/Qwen2.5-32B-Instruct-AWQ}` |
| `max-model-len` | `24576` |
| Quantization / attention | `awq_marlin`, `TRITON_ATTN` |
| `gpu-memory-utilization` | `0.88` |
| `shm_size` | `16gb` |
| `restart` | `unless-stopped` |

Endpoint: `http://localhost:8000/v1` (`VLLM_BASE_URL`).
