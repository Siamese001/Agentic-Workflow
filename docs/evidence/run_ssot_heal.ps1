# SSOT heal runner — fully synchronous, no Tee-Object, no jobs, no async
# Timeout via Start-Process + Wait-Process, redirect *>&1 to Out-File

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)

# ── Environment ──────────────────────────────────────────────────────────────
$env:PYTHONUTF8                       = "1"
$env:AGENTIC_DENY_SOURCE_MUTATION     = "1"
$env:AGENTIC_ALLOW_MUTATION_FOR_TESTS = "1"
$env:AGENTIC_BYPASS_LONGPATHS_CHECK   = "1"

$logPath      = "docs/evidence/ssot_heal_run_output.txt"
$stateCopy    = "docs/evidence/runtime_state.run.json"
$runnerScript = "docs/evidence/_ssot_heal_runner_tmp.py"
$timeoutSec   = 600  # 10 minutes

# ── Clean prior outputs ─────────────────────────────────────────────────────
Remove-Item $logPath   -Force -ErrorAction SilentlyContinue
Remove-Item $stateCopy -Force -ErrorAction SilentlyContinue

# ── Generate temp runner (input() blocked) ───────────────────────────────────
@'
import builtins
builtins.input = lambda *a, **k: (_ for _ in ()).throw(
    RuntimeError("Interactive input blocked")
)

import os, sys, json, traceback, time

sys.path.insert(0, ".")
os.environ.setdefault("AGENTIC_ALLOW_MUTATION_FOR_TESTS", "1")
os.environ.setdefault("AGENTIC_BYPASS_LONGPATHS_CHECK", "1")

start_time = time.time()

print("=== SSOT HEAL MODE RUN ===")
print("AGENTIC_DENY_SOURCE_MUTATION=1")
print("PYTHONUTF8=1")
print("input() BLOCKED")
print("---------------------------")
sys.stdout.flush()

from agentic_core.L0_routing.scripts.execute_ssot import _legacy_main

exit_code = 0
try:
    _legacy_main(["--domains"])
except SystemExit as e:
    exit_code = e.code or 0
except Exception:
    exit_code = -1
    traceback.print_exc()

elapsed = time.time() - start_time
print(f"\nEXIT_CODE={exit_code}")
print(f"RUNTIME_SECONDS={elapsed:.2f}")

if os.path.exists("runtime_state.json"):
    try:
        data = json.load(open("runtime_state.json", encoding="utf-8"))
        print("runtime_state.json: PARSE_OK")
        print(f"Top-level keys: {list(data.keys())}")
    except Exception as e:
        print("runtime_state.json: PARSE_FAIL")
        print(str(e))
else:
    print("runtime_state.json: NOT_FOUND")

sys.exit(exit_code if isinstance(exit_code, int) else 0)
'@ | Out-File -FilePath $runnerScript -Encoding utf8

# ── Baseline snapshot before run ────────────────────────────────────────────
$baseDirty = @(git status --porcelain=v1 agentic_core/ 2>$null)

# ── Synchronous execution with timeout ───────────────────────────────────────
Write-Host "[RUN] Starting python (synchronous, ${timeoutSec}s timeout)..."
$sw = [System.Diagnostics.Stopwatch]::StartNew()

$proc = Start-Process -FilePath "python" `
    -ArgumentList "-u", $runnerScript `
    -NoNewWindow -PassThru `
    -RedirectStandardOutput  "$logPath.stdout" `
    -RedirectStandardError   "$logPath.stderr"

$finished = $proc.WaitForExit($timeoutSec * 1000)
$sw.Stop()

if (-not $finished) {
    Write-Host "[TIMEOUT] Process exceeded ${timeoutSec}s - killing pid $($proc.Id)..."
    Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
    $exitCode = -1
} else {
    $exitCode = $proc.ExitCode
    if ($null -eq $exitCode) { $exitCode = 0 }
}

# ── Merge stdout + stderr into single log (no Tee-Object) ───────────────────
$mergedLines = @()
if (Test-Path "$logPath.stdout") {
    $mergedLines += Get-Content "$logPath.stdout" -Encoding utf8 -ErrorAction SilentlyContinue
}
if (Test-Path "$logPath.stderr") {
    $stderrLines = Get-Content "$logPath.stderr" -Encoding utf8 -ErrorAction SilentlyContinue
    if ($stderrLines) { $mergedLines += ""; $mergedLines += "=== STDERR ==="; $mergedLines += $stderrLines }
}
$mergedLines | Out-File -FilePath $logPath -Encoding utf8
Remove-Item "$logPath.stdout" -Force -ErrorAction SilentlyContinue
Remove-Item "$logPath.stderr" -Force -ErrorAction SilentlyContinue

$elapsedFmt = "{0:N2}" -f $sw.Elapsed.TotalSeconds
Write-Host "[RUN] Python exit code: $exitCode  (${elapsedFmt}s)"

# ── Copy runtime_state.json ─────────────────────────────────────────────────
if (Test-Path "runtime_state.json") {
    Copy-Item "runtime_state.json" -Destination $stateCopy -Force
    Write-Host "runtime_state.run.json: COPIED"
} else {
    Write-Host "runtime_state.json: NOT_FOUND"
}

# ── Clean up temp runner ────────────────────────────────────────────────────
Remove-Item $runnerScript -Force -ErrorAction SilentlyContinue

# ── POST-FLIGHT metrics ─────────────────────────────────────────────────────
$runtimeSeconds = $sw.Elapsed.TotalSeconds
$charmapCount   = (Select-String -Path $logPath -Pattern "charmap"            -ErrorAction SilentlyContinue | Measure-Object).Count
$abstractCount  = (Select-String -Path $logPath -Pattern "Create abstraction layer" -ErrorAction SilentlyContinue | Measure-Object).Count

$afterDirty  = @(git status --porcelain=v1 agentic_core/ 2>$null)
$basePaths   = $baseDirty  | ForEach-Object { $_.Substring(3).Trim() }
$afterPaths  = $afterDirty | ForEach-Object { $_.Substring(3).Trim() }
$newDirty    = @($afterPaths | Where-Object { $_ -notin $basePaths })
$newDirtyCount = $newDirty.Count

$runtimeFmt = "{0:N2}" -f $runtimeSeconds

$metricsBlock = @"

=== POST-FLIGHT METRICS ===
EXIT_CODE=$exitCode
RUNTIME_SECONDS=$runtimeFmt
CHARMAP_COUNT=$charmapCount
CREATE_ABSTRACTION_LAYER_COUNT=$abstractCount
AGENTIC_CORE_DIRTY_BEFORE=$($baseDirty.Count)
AGENTIC_CORE_DIRTY_AFTER=$($afterDirty.Count)
AGENTIC_CORE_NEW_DIRTY_FROM_RUN_COUNT=$newDirtyCount
"@
$metricsBlock | Out-File -FilePath $logPath -Append -Encoding utf8
Write-Host $metricsBlock

# ── Tail ────────────────────────────────────────────────────────────────────
Write-Host "`n--- Tail of $logPath ---"
Get-Content $logPath -ErrorAction SilentlyContinue | Select-Object -Last 30

exit $exitCode
