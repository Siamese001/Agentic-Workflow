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
import io
import shutil
from pathlib import Path

sys.path.insert(0, ".")
os.environ.setdefault("AGENTIC_ALLOW_MUTATION_FOR_TESTS", "1")
os.environ.setdefault("AGENTIC_BYPASS_LONGPATHS_CHECK", "1")

start_time = time.time()

print("=== SSOT HEAL MODE RUN ===")
print("AGENTIC_DENY_SOURCE_MUTATION=1")
print("PYTHONUTF8=1")
print("input() BLOCKED")
print("agentic_core FS FENCE: ON")
print("---------------------------")
sys.stdout.flush()

_REPO_ROOT = os.path.abspath(".")
_AGENTIC_CORE_ROOT = os.path.abspath(os.path.join(_REPO_ROOT, "agentic_core"))

def _abspath(p) -> str:
    try:
        return os.path.abspath(os.fspath(p))
    except Exception:
        return ""

def _is_under(root: str, p: str) -> bool:
    if not p:
        return False
    try:
        rp = os.path.realpath(p)
        rr = os.path.realpath(root)
        return rp == rr or rp.startswith(rr + os.sep)
    except Exception:
        return False

def _deny(msg: str) -> None:
    raise RuntimeError(f"SOURCE_MUTATION_BLOCKED: {msg}")

def _guard_path_for_write(path) -> None:
    ap = _abspath(path)
    if _is_under(_AGENTIC_CORE_ROOT, ap):
        _deny(f"write agentic_core/{os.path.relpath(ap, _AGENTIC_CORE_ROOT)}")

def _guard_path_for_mutation(path) -> None:
    ap = _abspath(path)
    if _is_under(_AGENTIC_CORE_ROOT, ap):
        _deny(f"mutate agentic_core/{os.path.relpath(ap, _AGENTIC_CORE_ROOT)}")

def _guard_path_for_move(src, dst) -> None:
    asrc = _abspath(src)
    adst = _abspath(dst)
    if _is_under(_AGENTIC_CORE_ROOT, asrc):
        _deny(f"move-from agentic_core/{os.path.relpath(asrc, _AGENTIC_CORE_ROOT)}")
    if _is_under(_AGENTIC_CORE_ROOT, adst):
        _deny(f"move-to agentic_core/{os.path.relpath(adst, _AGENTIC_CORE_ROOT)}")

_orig_open = builtins.open
def _open_guard(file, mode="r", *a, **k):
    m = mode or "r"
    if any(ch in m for ch in ("w", "a", "x", "+")):
        _guard_path_for_write(file)
    return _orig_open(file, mode, *a, **k)
builtins.open = _open_guard
io.open = _open_guard

_orig_os_open = os.open
def _os_open_guard(path, flags, mode=0o777):
    write_flags = (
        getattr(os, "O_WRONLY", 0) | getattr(os, "O_RDWR", 0) |
        getattr(os, "O_CREAT", 0) | getattr(os, "O_TRUNC", 0) |
        getattr(os, "O_APPEND", 0)
    )
    if flags & write_flags:
        _guard_path_for_write(path)
    return _orig_os_open(path, flags, mode)
os.open = _os_open_guard

_orig_unlink = os.unlink
def _unlink_guard(path, *a, **k):
    _guard_path_for_mutation(path)
    return _orig_unlink(path, *a, **k)
os.unlink = _unlink_guard
os.remove = _unlink_guard

_orig_rename = os.rename
def _rename_guard(src, dst, *a, **k):
    _guard_path_for_move(src, dst)
    return _orig_rename(src, dst, *a, **k)
os.rename = _rename_guard

_orig_replace = os.replace
def _replace_guard(src, dst, *a, **k):
    _guard_path_for_move(src, dst)
    return _orig_replace(src, dst, *a, **k)
os.replace = _replace_guard

_orig_mkdir = os.mkdir
def _mkdir_guard(path, *a, **k):
    _guard_path_for_mutation(path)
    return _orig_mkdir(path, *a, **k)
os.mkdir = _mkdir_guard

_orig_makedirs = os.makedirs
def _makedirs_guard(name, *a, **k):
    _guard_path_for_mutation(name)
    return _orig_makedirs(name, *a, **k)
os.makedirs = _makedirs_guard

_orig_rmdir = os.rmdir
def _rmdir_guard(path, *a, **k):
    _guard_path_for_mutation(path)
    return _orig_rmdir(path, *a, **k)
os.rmdir = _rmdir_guard

_orig_shutil_move = shutil.move
def _shutil_move_guard(src, dst, *a, **k):
    _guard_path_for_move(src, dst)
    return _orig_shutil_move(src, dst, *a, **k)
shutil.move = _shutil_move_guard

_orig_copy2 = shutil.copy2
def _copy2_guard(src, dst, *a, **k):
    _guard_path_for_write(dst)
    return _orig_copy2(src, dst, *a, **k)
shutil.copy2 = _copy2_guard

_orig_copytree = shutil.copytree
def _copytree_guard(src, dst, *a, **k):
    _guard_path_for_write(dst)
    return _orig_copytree(src, dst, *a, **k)
shutil.copytree = _copytree_guard

_orig_p_open = Path.open
def _path_open_guard(self, mode="r", *a, **k):
    m = mode or "r"
    if any(ch in m for ch in ("w", "a", "x", "+")):
        _guard_path_for_write(self)
    return _orig_p_open(self, mode, *a, **k)
Path.open = _path_open_guard

_orig_write_text = Path.write_text
def _write_text_guard(self, *a, **k):
    _guard_path_for_write(self)
    return _orig_write_text(self, *a, **k)
Path.write_text = _write_text_guard

_orig_write_bytes = Path.write_bytes
def _write_bytes_guard(self, *a, **k):
    _guard_path_for_write(self)
    return _orig_write_bytes(self, *a, **k)
Path.write_bytes = _write_bytes_guard

_orig_path_unlink = Path.unlink
def _path_unlink_guard(self, *a, **k):
    _guard_path_for_mutation(self)
    return _orig_path_unlink(self, *a, **k)
Path.unlink = _path_unlink_guard

_orig_path_rename = Path.rename
def _path_rename_guard(self, target, *a, **k):
    _guard_path_for_move(self, target)
    return _orig_path_rename(self, target, *a, **k)
Path.rename = _path_rename_guard

_orig_path_replace = Path.replace
def _path_replace_guard(self, target, *a, **k):
    _guard_path_for_move(self, target)
    return _orig_path_replace(self, target, *a, **k)
Path.replace = _path_replace_guard

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
