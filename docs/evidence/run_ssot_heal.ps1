# UTF-8 safe SSOT heal runner — no Tee file-lock races
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$env:AGENTIC_ALLOW_MUTATION_FOR_TESTS = "1"
$env:AGENTIC_BYPASS_LONGPATHS_CHECK = "1"
$env:PYTHONUTF8 = "1"

$logPath      = "docs/evidence/ssot_heal_run_output.txt"
$stateCopy    = "docs/evidence/runtime_state.run.json"
$runnerScript = "docs/evidence/_ssot_heal_runner_tmp.py"

# Write the Python runner to a temp file (avoids heredoc quoting issues)
@'
import os, sys, json, traceback

sys.path.insert(0, ".")
os.environ.setdefault("AGENTIC_ALLOW_MUTATION_FOR_TESTS", "1")
os.environ.setdefault("AGENTIC_BYPASS_LONGPATHS_CHECK", "1")

print("=== SSOT HEAL MODE RUN ===")
print("AGENTIC_ALLOW_MUTATION_FOR_TESTS=1")
print("AGENTIC_BYPASS_LONGPATHS_CHECK=1")
print("PYTHONUTF8=1")
print("---------------------------")

from agentic_core.L0_routing.scripts.execute_ssot import _legacy_main

exit_code = 0
try:
    _legacy_main(["--domains"])
except SystemExit as e:
    exit_code = e.code or 0
except Exception:
    exit_code = -1
    traceback.print_exc()

print(f"\nEXIT_CODE={exit_code}")

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
'@ | Out-File -FilePath $runnerScript -Encoding utf8

# Run Python — stdout+stderr both redirected to log file (no Tee, no file-lock race)
python $runnerScript *>&1 | Out-File -FilePath $logPath -Encoding utf8

# Copy runtime_state.json if it exists
if (Test-Path "runtime_state.json") {
    Copy-Item "runtime_state.json" -Destination $stateCopy -Force
    Write-Host "runtime_state.run.json: COPIED"
} else {
    Write-Host "runtime_state.json: NOT_FOUND"
}

# Clean up temp runner
Remove-Item $runnerScript -Force -ErrorAction SilentlyContinue

Write-Host "--- Tail of $logPath ---"
Get-Content $logPath | Select-Object -Last 15
