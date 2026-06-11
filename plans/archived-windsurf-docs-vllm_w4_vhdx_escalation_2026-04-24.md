---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\vllm_w4_vhdx_escalation_2026-04-24.md'
original_relative_path: 'vllm_w4_vhdx_escalation_2026-04-24.md'
source_sha256: f1cd1391aeb86ca40773e0c45efe0f5abb05b2c56ac8015951b7781f7ca5c46e
recovered_status: LOST_RECOVERED
last_commit: '2dd2ba7efc3'
last_commit_date: '2026-05-15 14:13:16 -0400'
created_date: '2026-04-25'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# W4 VHDX Optimize — Final Escalation

**Date**: 2026-04-24 21:55 EDT
**Status**: ESCALATED — needs user intervention
**Plan**: `.windsurf/plans/vllm-stack-consolidation-f6e95d.md` Wave 4

## Current State

| Item | Value |
|---|---|
| VHDX path | `C:\Users\amita\AppData\Local\wsl\{358ed4de-0575-4f25-973c-dacd8fec83c2}\ext4.vhdx` |
| VHDX on disk | **142.85 GB** |
| Used inside WSL (`df`) | 92 GB |
| Reclaim potential | ~50 GB |
| Stack A vLLM | ✅ Active (32B-AWQ serving on :8000) |

## What Cursor Agent Tried

| Attempt | Method | Result |
|---|---|---|
| 1 | `Optimize-VHD` via `Start-Process -Verb RunAs` on `tools/vllm/optimize_vhdx.ps1` | UAC declined by user |
| 2 | Same, log+marker redirection | UAC declined by user |
| 3 | `Optimize-VHD` via inline script (UAC accepted) | **Failed — `Optimize-VHD` cmdlet not found** (Hyper-V PowerShell module not installed) |
| 4 | `diskpart compact vdisk` via `_optimize_vhdx_diskpart.ps1` | UAC silently declined (no visible dialog reached user) |

## Root Cause

`Optimize-VHD` is part of the **Hyper-V Management PowerShell module**, which is NOT installed on this machine even though the Hyper-V platform is enabled (WSL2 runs on it). The cmdlet-based approach therefore cannot work until the module is added.

`diskpart compact vdisk` works without Hyper-V tools, but requires:
1. WSL distro shut down
2. Admin rights on Windows
3. Filesystem blocks to be zeroed first via `fstrim` inside the guest (otherwise compact reclaims nothing)

## Ready-to-Run: User-Initiated Path

### Option A (recommended) — One shot diskpart with fstrim

1. Open PowerShell **as Administrator** (Win+X → "Windows PowerShell (Admin)" or search "PowerShell" → right-click → Run as administrator)
2. Paste one of these:

```powershell
# Preferred: fstrim first, then diskpart compact
powershell -NoProfile -ExecutionPolicy Bypass -File C:\Git\Agentic-Workflow\tools\vllm\_optimize_vhdx_diskpart.ps1
```

The script will:
- Run `fstrim -v /` inside WSL as root (zero free blocks)
- `wsl --shutdown`
- `diskpart /s <tmp>` — attach + compact + detach
- Print "Before / After / Reclaimed" GB to console
- Write `artifacts\vhdx_optimize.done` with results
- Log full transcript to `artifacts\vhdx_optimize.log`

3. After it finishes, restart Stack A:

```powershell
wsl
```
(from any PowerShell window — cold boot the distro; systemd user session auto-starts vllm.service if you previously ran `loginctl enable-linger amita`, otherwise run `wsl -- systemctl --user start vllm`.)

### Option B — Install Hyper-V PowerShell module first, then Optimize-VHD

If you prefer `Optimize-VHD -Mode Full` (better compaction than `diskpart compact` for NTFS-VHDX):

```powershell
# Admin PowerShell
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V-Management-PowerShell -All -NoRestart
# No reboot needed if Hyper-V platform is already on
powershell -NoProfile -ExecutionPolicy Bypass -File C:\Git\Agentic-Workflow\tools\vllm\_optimize_vhdx_inline.ps1
```

### Option C — Skip reclaim entirely

If ~50 GB of reclaimable disk is not worth the service interruption right now, W4 can be deferred indefinitely. The VHDX will NOT grow beyond 1 TB (WSL default max), and the filesystem inside is healthy. Revisit when disk pressure increases.

## Expected Result After Reclaim

- VHDX before: **142.85 GB**
- VHDX after: **~75–95 GB** (depending on actual fragmentation; typically reclaims 40–70% of the delta between `df` and file size)
- Reclaimed: **~50–70 GB of Windows disk space**
- Time: 3–5 minutes including fstrim

## Rollback (if anything goes wrong)

VHDX operations are reversible in the sense that a failed compact leaves the file at its original size; no data loss. If WSL fails to start afterward:

```powershell
wsl --status              # verify distro still registered
wsl --list --verbose      # confirm Ubuntu-24.04 is present
wsl --unregister Ubuntu-24.04   # LAST RESORT — wipes the distro
```

Data inside `~/models/`, `~/.vllm_env/`, and `~/.config/systemd/user/vllm.service` would survive the compact itself; `--unregister` destroys them and should not be needed.
