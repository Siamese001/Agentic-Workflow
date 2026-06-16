# Obsolete Native vLLM Autostart Setup

This file used to describe the Windsurf-era native WSL venv stack:

- `~/.vllm_env`
- `tools/vllm/vllm.service`
- `systemctl --user start vllm`
- `start_vllm_server_32b.sh`

That stack is retired. Do not recreate it. It causes config drift with the
canonical Docker vLLM server on port 8000.

Use the current local Qwen boot path instead:

```bash
cd /mnt/c/Git/Agentic-Workflow-FRESH
bash ops_scripts/apps_rg/boot_local_qwen_vllm.sh
```

Windows entrypoint:

```powershell
cd C:\Git\Agentic-Workflow-FRESH
.\ops_scripts\apps_rg\Fix-AppsRgWslRuntime.ps1
```

Canonical config:

- `docker-compose.qwen.yml`
- `QWEN_MODEL_HOST_PATH=/home/amita/models/Qwen2.5-32B-Instruct-AWQ`
- `QWEN_VLLM_MODEL=Qwen/Qwen2.5-32B-Instruct-AWQ`
- `VLLM_BASE_URL=http://localhost:8000/v1`
