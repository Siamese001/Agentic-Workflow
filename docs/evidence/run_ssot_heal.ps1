# SSOT heal runner — .NET Process-based, unbuffered, 10min timeout, input() blocked
# No Tee-Object, no pipe chains, incremental streaming to file

[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$env:AGENTIC_ALLOW_MUTATION_FOR_TESTS = "1"
$env:AGENTIC_BYPASS_LONGPATHS_CHECK = "1"
$env:AGENTIC_DENY_SOURCE_MUTATION = "1"
$env:PYTHONUTF8 = "1"

$logPath      = "docs/evidence/ssot_heal_run_output.txt"
$stateCopy    = "docs/evidence/runtime_state.run.json"
$runnerScript = "docs/evidence/_ssot_heal_runner_tmp.py"
$ssotFile     = "agentic_core/L0_routing/scripts/execute_ssot.py"
$timeoutSec   = 600  # 10 minutes

# Delete prior outputs
Remove-Item $logPath -Force -ErrorAction SilentlyContinue
Remove-Item $stateCopy -Force -ErrorAction SilentlyContinue

# ============================================================================
# PRE-FLIGHT: Restore SSOT entrypoint
# ============================================================================
Write-Host "[PRE-FLIGHT] Restoring $ssotFile from HEAD..."
git restore --source=HEAD -- $ssotFile 2>&1 | Out-Null

# ============================================================================
# Generate temp runner with input() blocked
# ============================================================================
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
print("AGENTIC_ALLOW_MUTATION_FOR_TESTS=1")
print("AGENTIC_BYPASS_LONGPATHS_CHECK=1")
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

# ============================================================================
# Execute with timeout using Start-Process + job
# ============================================================================
Write-Host "[RUN] Starting python with ${timeoutSec}s timeout..."

$job = Start-Job -ScriptBlock {
    param($script, $log)
    Set-Location $using:PWD
    $env:PYTHONUTF8 = "1"
    $env:AGENTIC_ALLOW_MUTATION_FOR_TESTS = "1"
    $env:AGENTIC_BYPASS_LONGPATHS_CHECK = "1"
    python -u $script 2>&1 | Out-File -FilePath $log -Encoding utf8
    $LASTEXITCODE
} -ArgumentList $runnerScript, $logPath

$completed = Wait-Job -Job $job -Timeout $timeoutSec

if ($null -eq $completed) {
    Write-Host "[TIMEOUT] Process exceeded ${timeoutSec}s, killing..."
    Stop-Job -Job $job
    Remove-Job -Job $job -Force
    "`n=== TIMEOUT ===`nProcess killed after ${timeoutSec} seconds" | Out-File -FilePath $logPath -Append -Encoding utf8
    $exitCode = -1
} else {
    $exitCode = Receive-Job -Job $job
    Remove-Job -Job $job
    if ($null -eq $exitCode) { $exitCode = 0 }
}

Write-Host "[RUN] Python exit code: $exitCode"

# Copy runtime_state.json if it exists
if (Test-Path "runtime_state.json") {
    Copy-Item "runtime_state.json" -Destination $stateCopy -Force
    Write-Host "runtime_state.run.json: COPIED"
} else {
    Write-Host "runtime_state.json: NOT_FOUND"
}

# Clean up temp runner
Remove-Item $runnerScript -Force -ErrorAction SilentlyContinue

# ============================================================================
# POST-FLIGHT: Restore tracked corruption
# ============================================================================
Write-Host "[POST-FLIGHT] Restoring tracked files to HEAD..."
git restore --source=HEAD -- agentic_core/ 2>&1 | Out-Null

Write-Host "--- Tail of $logPath ---"
Get-Content $logPath -ErrorAction SilentlyContinue | Select-Object -Last 40

exit $exitCode
