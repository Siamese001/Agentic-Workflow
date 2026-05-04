# vLLM + apps_rg Auto-Launch Setup

Complete automation for running apps_rg with local Qwen-32B vLLM — no manual Docker Desktop, no manual commands.

---

## Quick Start (One-Time Setup)

### 1. Enable systemd in WSL (Required for autostart)

In **WSL Ubuntu**:
```bash
sudo cp /mnt/c/Git/Agentic-Workflow-FRESH/tools/vllm/wsl.conf.example /etc/wsl.conf
# Edit to set your username: sudo nano /etc/wsl.conf
```

In **Windows PowerShell (Admin)**:
```powershell
wsl --shutdown
# Wait 10s, then reopen WSL - systemd is now enabled
```

### 2. Install vLLM systemd service

In **WSL Ubuntu**:
```bash
# Create venv and download model (one-time)
python3.12 -m venv ~/.vllm_env
~/.vllm_env/bin/pip install vllm huggingface_hub hf_transfer
bash /mnt/c/Git/Agentic-Workflow-FRESH/tools/vllm/download_qwen_32b_awq.sh

# Install systemd service
mkdir -p ~/.config/systemd/user
cp /mnt/c/Git/Agentic-Workflow-FRESH/tools/vllm/vllm.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now vllm.service
```

Verify:
```bash
systemctl --user status vllm
bash /mnt/c/Git/Agentic-Workflow-FRESH/tools/vllm/check_vllm.sh
```

### 3. Run apps_rg with auto-launcher (Windows PowerShell)

```powershell
# From repo root
cd C:\Git\Agentic-Workflow-FRESH

# With arguments
.\tools\vllm\launch_apps_rg.ps1 --target-role "Senior ML Engineer" --target-company "Google"

# Interactive mode (prompts for inputs)
.\tools\vllm\launch_apps_rg.ps1
```

---

## How It Works

### Three-Layer Defense

| Layer | Component | What It Does |
|-------|-----------|--------------|
| **1** | `vllm.service` (systemd) | Autostarts vLLM when WSL boots; auto-restarts on crash |
| **2** | `launch_apps_rg.ps1` | Windows-side: ensures WSL running → starts vLLM if stopped → waits for health |
| **3** | `VLLM_WAIT_FOR_READY` | apps_rg internal: blocks until vLLM healthy before first inference |

### Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `VLLM_WAIT_FOR_READY` | `0` (off) | Seconds to wait for vLLM before falling back to Anthropic |
| `VLLM_HEALTH_PROBE_TIMEOUT` | `1.5` | Health check timeout (seconds) |
| `VLLM_HEALTH_PROBE_TTL_SECONDS` | `5` | Cache TTL for health probes |

---

## Troubleshooting

### vLLM won't start
```bash
# In WSL
journalctl --user -u vllm.service -f    # Watch logs
systemctl --user restart vllm.service   # Hard restart
```

### vLLM starts but apps_rg falls back to Anthropic
```powershell
# In PowerShell - check if localhost:8000 is reachable from Windows
Invoke-RestMethod -Uri "http://localhost:8000/v1/models" -TimeoutSec 5
# Should return JSON with model list
```

If Windows can't reach WSL localhost:
```powershell
# Use WSL IP instead
$wslIp = (wsl hostname -I).Split()[0]
$env:VLLM_BASE_URL = "http://${wslIp}:8000/v1"
```

### Slow first start (model loading)
Normal — 32B AWQ takes ~30-60s to load on first boot. Subsequent calls are fast. The launcher waits up to 5 minutes by default.

---

## Architecture

```
Windows PowerShell
  └─ launch_apps_rg.ps1
       ├─ Checks WSL status → starts if needed
       ├─ Checks vLLM health at localhost:8000/v1/models
       ├─ Waits up to 5 min for vLLM (with progress logging)
       └─ Runs: python -m apps_rg [args]

WSL2 Ubuntu (systemd enabled)
  └─ vllm.service (user unit)
       ├─ ExecStart: start_vllm_server_32b.sh
       ├─ Restart: on-failure (every 10s)
       └─ Logs: journalctl --user -u vllm

apps_rg narrative pipeline
  └─ _llm_client.py
       ├─ VLLM_WAIT_FOR_READY=60 → blocks until healthy
       ├─ Generates via Qwen-32B (fast, free)
       └─ Falls back to Anthropic only if vLLM fails
```

---

## Files Modified/Created

| File | Change |
|------|--------|
| `tools/vllm/vllm.service` | Now points to 32B script + FRESH repo path |
| `tools/vllm/launch_apps_rg.ps1` | **NEW** — Windows launcher with health wait |
| `tools/vllm/wsl.conf.example` | **NEW** — systemd enable template |
| `apps_rg/integrations/hops/_llm_client.py` | Added `VLLM_WAIT_FOR_READY` retry logic |
| `apps_rg/__main__.py` | Added interactive prompts for missing args |
| `apps_rg/scripts/candidate_profile.yaml` | **NEW** — auto-generated from master_resume.json |
| `tools/rg/build_candidate_profile_from_master.py` | **NEW** — profile builder utility |
