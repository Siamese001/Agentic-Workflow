# Briefing — Local Qwen vLLM Docker boot (Cursor / Windows)

> **Date:** 2026-05-26  
> **Audience:** Operator (future Cursor sessions)  
> **Full runbook:** [local_qwen_docker_boot.md](local_qwen_docker_boot.md)  
> **Compose SSOT:** [docker-compose.qwen.yml](../../docker-compose.qwen.yml)

---

## Why this briefing exists

The `local-qwen-vllm` container was **turning off or needing manual restarts** because:

1. **`RestartPolicy=no`** on hand-created containers — no auto-recovery after crash/reboot.
2. **64 MiB `/dev/shm`** (Docker default) — too small for vLLM workers; instability under load.
3. **Empty `/models/qwen` mount** when `docker compose` ran from **PowerShell only** — WSL paths do not bind correctly; vLLM then re-downloaded ~20 GB from Hugging Face Hub (slow, rate-limited, looks “stuck”).
4. **`diagnose()` → `vllm_container_down`** while container status was `Up` — model still loading; `/v1/models` not ready yet (not a dead container).

**Fix pattern:** bind local WSL weights, 16 GiB shm, `unless-stopped`, boot **from WSL**, verify mount before trusting HTTP.

---

## One-page boot procedure

### 0. Prerequisites (once)

```powershell
docker info
wsl -e test -f /home/amita/models/Qwen2.5-32B-Instruct-AWQ/config.json && echo OK
```

Weights live on WSL ext4: `~/models/Qwen2.5-32B-Instruct-AWQ` (~19 GB). Do **not** rely on in-container Hub download for daily use.

### 1. Boot (canonical)

```powershell
wsl bash /mnt/c/Git/Agentic-Workflow-FRESH/ops_scripts/apps_rg/boot_local_qwen_vllm.sh
```

Equivalent:

```powershell
wsl -e bash -lc 'cd /mnt/c/Git/Agentic-Workflow-FRESH && docker compose -f docker-compose.qwen.yml up -d qwen-vllm'
```

**Recreate** after image/args/mount changes:

```powershell
wsl -e bash -lc 'cd /mnt/c/Git/Agentic-Workflow-FRESH && docker compose -f docker-compose.qwen.yml up -d --force-recreate qwen-vllm'
```

### 2. Verify mount (fail-closed)

```powershell
docker exec local-qwen-vllm test -f /models/qwen/config.json && echo mount_ok
```

If this fails → empty bind; re-boot via **WSL** (step 1), not PowerShell-only compose.

### 3. Verify API (model loaded)

```powershell
curl -fsS http://localhost:8000/v1/models
```

Expect `"id":"Qwen/Qwen2.5-32B-Instruct-AWQ"`, `"max_model_len":24576`.  
Cold load from local disk: **~2–4 minutes**. Empty curl reply = still loading.

### 4. Repo diagnostic

```powershell
cd C:\Git\Agentic-Workflow-FRESH
python -c "from agentic_core.L2_execution.healers.qwen_strict_diagnostic import diagnose; d=diagnose(); print(d.status, d.message)"
```

Expect: `ok Qwen vLLM healthy ...`

### 5. Stability check

```powershell
docker inspect local-qwen-vllm --format "Restart={{.HostConfig.RestartPolicy.Name}} Shm={{.HostConfig.ShmSize}}"
```

Expect: `Restart=unless-stopped`, `Shm=17179869184` (16 GiB).

---

## Apps_rg full runtime fix

Starts vLLM (step 1) **and** validates WSL Python venv + BGE:

```powershell
.\ops_scripts\apps_rg\Fix-AppsRgWslRuntime.ps1
```

Set before live runs:

```powershell
$env:VLLM_MAX_MODEL_LEN = "24576"
```

---

## Daily commands

| Action | Command |
|--------|---------|
| Start existing | `docker start local-qwen-vllm` |
| Stop | `docker stop local-qwen-vllm` |
| Logs | `docker logs local-qwen-vllm --tail 50 -f` |

---

## Troubleshooting quick reference

| Symptom | Cause | Action |
|---------|--------|--------|
| `Invalid repository ID: '/models/qwen'` | Empty bind mount | Boot via WSL (step 1); verify mount |
| Container `Up` but curl fails | Model loading | Wait 2–4 min; `docker logs` until `Application startup complete` |
| `vllm_container_down` in Python | Same — not ready yet | Do not restart loop; wait for step 3 |
| Slow boot every time | HF re-download | Fix mount; optional `HF_TOKEN` in `.env` for hub updates only |
| Crashes under load | Old 64 MiB shm / OOM | Recreate with compose (`shm_size: 16gb`, `gpu-memory-utilization: 0.88`) |

**Avoid:** `APPS_RG_QWEN_VLLM_DOCKER_RESTART=always` on every run — full model reload each time.

---

## Compose settings (reference)

| Item | Value |
|------|--------|
| Container | `local-qwen-vllm` |
| Image | `vllm/vllm-openai:latest` (no v0.11 pull required) |
| Model | `/models/qwen` ← `/home/amita/models/Qwen2.5-32B-Instruct-AWQ` |
| Context | `max-model-len=24576` |
| Quant / attention | `awq_marlin`, `TRITON_ATTN` |
| GPU util | `0.88` |
| shm | `16gb` |
| restart | `unless-stopped` |
| Endpoint | `http://localhost:8000/v1` |

Override weights path: `QWEN_MODEL_HOST_PATH` in `.env` or shell (see [.env.example](../../.env.example)).

---

## Related docs

- [local_qwen_docker_boot.md](local_qwen_docker_boot.md) — expanded runbook  
- [qwen-vllm-topology.md](../architecture/qwen-vllm-topology.md) — architecture + apps_rg env tables  
- [.cursor/rules/local-llm-wsl2-gpu.mdc](../../.cursor/rules/local-llm-wsl2-gpu.mdc) — VRAM / Blackwell quirks for agents  
