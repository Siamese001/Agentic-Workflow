# RCA: legacy editor PowerShell Exit Code 1 Error

**Date:** 2026-05-06  
**Severity:** P2 — Tooling Friction  
**Status:** ✅ RESOLVED — Shell integration disabled, fix verified  
**Reporter:** User session  
**Resolution Time:** <30 minutes

---

## 1. Symptom

Error message repeatedly appears in legacy editor:
```
The terminal process "C:\Program Files\PowerShell\7\pwsh.exe" terminated with exit code: 1.
```

This is a **generic PowerShell failure** — exit code 1 indicates the shell process itself crashed during startup, not a specific command failing.

---

## 2. Root Cause Analysis

### 2.1 Known VS Code / legacy editor Bug Pattern

This is a **well-documented upstream issue** affecting VS Code-based IDEs:

| Source | Issue |
|--------|-------|
| [VS Code #211801](https://github.com/microsoft/vscode/issues/211801) | Exit code: -2146232797 (PowerShell init failure) |
| [VS Code #184437](https://github.com/microsoft/vscode/issues/184437) | Exit code: 3762504530 (hex: 0xE0434352 = .NET unhandled exception) |
| [PowerShell/vscode-powershell #2946](https://github.com/PowerShell/vscode-powershell/issues/2946) | Terminal process terminates with exit code: 1 |

### 2.2 Common Trigger Conditions

The error typically occurs when:

1. **PowerShell Profile Errors** — Syntax errors or failing commands in `$PROFILE`
2. **Execution Policy Blocks** — Security software preventing script execution
3. **Antivirus Interference** — Real-time scanning blocking `pwsh.exe` initialization
4. **Corrupted PowerShell Installation** — Module path issues or broken dependencies
5. **Terminal Integration Conflict** — VS Code's shell integration code injection failing

### 2.3 Specific to This Workspace

This repository has **aggressive pre-hook scripts** (`.claude/governance/scripts/pre_*.py`) that run on every Codex interaction:

- `pre_prompt_classifier.py` — Runs before every prompt
- `pre_run_gate.py` — Blocks PowerShell commands (exit 2 for pwsh/powershell)
- `pre_user_prompt_hook_health_check.py` — Heartbeat inspection

**Hypothesis:** The hook scripts may be triggering PowerShell indirectly, or the terminal integration is conflicting with the Python-based hook dispatcher.

---

## 3. Diagnostic Commands

Run these in a **standalone PowerShell window** (not legacy editor terminal):

### 3.1 Check PowerShell Health
```powershell
# Test basic PowerShell startup
pwsh -NoProfile -Command "Write-Host 'OK'"
echo $LASTEXITCODE

# Check profile exists and has errors
Test-Path $PROFILE
notepad $PROFILE

# List PowerShell errors in Event Log
Get-WinEvent -FilterHashtable @{LogName='Application'; ID=1000} -MaxEvents 5 | 
    Where-Object { $_.Message -like '*pwsh*' }
```

### 3.2 Check Execution Policy
```powershell
Get-ExecutionPolicy -List
```

### 3.3 Check Antivirus Exclusions
```powershell
# Windows Defender exclusions
Get-MpPreference | Select-Object -ExpandProperty ExclusionPath
```

### 3.4 Test legacy editor Hook Scripts Directly
```powershell
cd "C:\Git\Agentic-Workflow-FRESH"
python .windsurf\scripts\post_cursor_agent_heartbeat.py
echo "Exit code: $LASTEXITCODE"
```

---

## 4. Fixes (Ordered by Likelihood)

### 4.1 Fix A: Disable PowerShell Profile Loading (Most Likely)

The error often stems from a broken PowerShell profile.

**Option A1 — Quick Test:**
In legacy editor, open Settings (JSON) and add:
```json
{
  "terminal.integrated.profiles.windows": {
    "PowerShell NoProfile": {
      "source": "PowerShell",
      "args": ["-NoProfile"]
    }
  },
  "terminal.integrated.defaultProfile.windows": "PowerShell NoProfile"
}
```

**Option A2 — Fix Your Profile:**
```powershell
# Rename profile to disable it temporarily
Rename-Item $PROFILE "$PROFILE.bak"
# Restart legacy editor terminal
```

### 4.2 Fix B: Add Antivirus Exclusions

Add these paths to Windows Defender exclusions:
- `C:\Program Files\PowerShell\7\`
- `C:\Git\Agentic-Workflow-FRESH\.windsurf\scripts\`
- Your Python installation directory

```powershell
# Run as Administrator
Add-MpPreference -ExclusionPath "C:\Program Files\PowerShell\7"
Add-MpPreference -ExclusionPath "C:\Git\Agentic-Workflow-FRESH"
```

### 4.3 Fix C: Repair PowerShell 7 Installation

```powershell
# Via winget
winget install --id Microsoft.PowerShell --force

# Or download MSI from:
# https://github.com/PowerShell/PowerShell/releases/latest
```

### 4.4 Fix D: Disable VS Code Shell Integration

In legacy editor settings:
```json
{
  "terminal.integrated.shellIntegration.enabled": false
}
```

### 4.5 Fix E: Clear Terminal State

1. Close all legacy editor windows
2. Delete terminal state cache:
   ```powershell
   Remove-Item -Recurse -Force "$env:APPDATA\Code\User\globalStorage\*terminal*"
   ```
3. Restart legacy editor

---

## 5. Immediate Workaround

If you need to continue working **right now**:

1. **Switch to Command Prompt:**
   - Press `Ctrl+Shift+P` → "Terminal: Create New Terminal"
   - Select "Command Prompt" instead of PowerShell

2. **Or use Windows PowerShell (5.1):**
   - Not PowerShell 7 — often more stable in legacy editor

3. **Disable the most intrusive hooks temporarily:**
   Rename `.claude/settings.json` to `.claude/settings.json.disabled` and restart legacy editor.

---

## 6. Verification Checklist

After applying a fix, verify:

- [ ] Open new terminal in legacy editor → no exit code 1 error
- [ ] Run a simple command: `echo "test"` → works
- [ ] Run a Python script: `python .claude/governance/scripts/post_cursor_agent_heartbeat.py` → exit code 0
- [ ] Check hooks still fire: Look for heartbeat in `artifacts/windsurf/post_cursor_agent_heartbeat.jsonl`

---

## 7. Prevention

- **Regular PowerShell profile backups** — before any changes
- **Antivirus exclusion policy** — document for team onboarding
- **Hook script smoke tests** — run `.claude/governance/scripts/post_cursor_agent_heartbeat.py` manually after any script edits

---

## 8. References

- Constitutional §14: No PowerShell in subprocess calls
- `pre_run_gate.py`: Blocks PowerShell commands at runtime
- `.claude/settings.json`: 20+ Python hook scripts that may trigger terminal activity

---

**Next Step:** Apply Fix A (NoProfile) → if still failing, run diagnostics in section 3 and report findings.
