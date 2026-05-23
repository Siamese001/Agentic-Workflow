# Windows Smart App Control and apps_rg (BGE / PyTorch)

## Symptom

```text
ImportError: DLL load failed while importing _C: An Application Control policy has blocked this file.
```

Code Integrity log (`Microsoft-Windows-CodeIntegrity/Operational`, event **3077**) shows
`torch\_C.cp312-win_amd64.pyd` blocked for **Enterprise signing level** (Smart App Control /
Verified & Reputable policy).

This is **not** classic WDAC admin policy; it is **Smart App Control** on Windows 11+.

## Fixes (pick one)

### A — WSL runner (recommended, no SAC change)

Isolated Linux venv on WSL ext4 (`~/.cache/awf-venv-wsl`), repo stays on `/mnt/c/...`:

```powershell
# First time only (downloads deps; several minutes):
wsl -e bash -lc "sed -i 's/\r$//' /mnt/c/Git/Agentic-Workflow-FRESH/tools/apps_rg/wsl_bootstrap.sh && bash /mnt/c/Git/Agentic-Workflow-FRESH/tools/apps_rg/wsl_bootstrap.sh"

# Run section CLI:
.\tools\apps_rg\Invoke-AppsRgSectionWsl.ps1 --section executive_summary `
  --target-company "Brown & Brown" `
  --target-role "SVP IT Strategy & Innovation" `
  --jd apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt `
  --manual-brief apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md
```

Requires `local-qwen-vllm` running (`docker start local-qwen-vllm`). WSL reaches `http://localhost:8000/v1`.

### B — Disable Smart App Control (admin + reboot)

```powershell
# Status
.\ops_scripts\windows\smart_app_control_apps_rg.ps1 -Action Status

# UI
.\ops_scripts\windows\smart_app_control_apps_rg.ps1 -Action OpenSettings

# Registry (elevated; reboot after)
.\ops_scripts\windows\smart_app_control_apps_rg.ps1 -Action DisableDev
```

After reboot, verify:

```powershell
python -c "import torch; print(torch.__version__)"
```

### C — Keep SAC on; do not share `.venv` with WSL

WSL bootstrap uses `UV_PROJECT_ENVIRONMENT=~/.cache/awf-venv-wsl` so it does **not** replace the
Windows `.venv` under the repo.

## Related

- [qwen-vllm-topology.md](../architecture/qwen-vllm-topology.md)
- `apps_rg/runtime/embedding_settings.py` — BGE load path
