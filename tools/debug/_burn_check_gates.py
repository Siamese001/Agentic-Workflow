"""Run P0 runner + P1/P2 ratchet checks against latest snapshot."""

import subprocess
import sys
from pathlib import Path

snap = sorted(Path("artifacts/adg").glob("adg_indexed_*.sqlite"), key=lambda x: x.stat().st_mtime)[-1]
print(f"snap: {snap.name}\n")

# P0 runner
print("=== P0 two-pass runner ===")
r = subprocess.run(
    [sys.executable, "-m", "ops_scripts.ci.adg_gates.p0_runner", "--sqlite", str(snap)],
    capture_output=True,
    text=True,
    timeout=120,
    check=False,
)
print(f"exit={r.returncode}")
for line in r.stdout.splitlines()[-15:]:
    print(f"  stdout: {line}")
for line in r.stderr.splitlines()[-5:]:
    print(f"  stderr: {line}")
print()

# P1/P2 ratchet via direct function call
print("=== Ratchet checks ===")
sys.path.insert(0, str(Path.cwd()))
from tools.generate.validation import _check_p1_ratchet, _check_p2_ratchet  # noqa: E402

try:
    _check_p2_ratchet(sqlite_path=snap)
    print("  P2 ratchet: OK")
except SystemExit as e:
    print(f"  P2 ratchet: exit={e.code}")
try:
    _check_p1_ratchet(sqlite_path=snap)
    print("  P1 ratchet: OK")
except SystemExit as e:
    print(f"  P1 ratchet: exit={e.code}")
