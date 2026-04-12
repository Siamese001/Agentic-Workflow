"""Test guardian exemption logic."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
source_file = "ops_scripts/dev_tools/l0_scripts/start_runtime_api_util.py"
line_no = 71

src_path = ROOT / source_file
print(f"ROOT: {ROOT}")
print(f"Source file: {source_file}")
print(f"Resolved path: {src_path}")
print(f"Exists: {src_path.exists()}")

if src_path.exists():
    lines = src_path.read_text(encoding="utf-8", errors="ignore").splitlines()
    print(f"Total lines: {len(lines)}")
    check_lines = lines[max(0, line_no - 2) : line_no]
    print(f"Checking lines {max(0, line_no - 2)}-{line_no}:")
    for i, ln in enumerate(check_lines, start=max(0, line_no - 2) + 1):
        print(f"  Line {i}: {ln}")
    exempted = any("guardian: allow-layer-violation" in ln for ln in check_lines)
    print(f"Exempted: {exempted}")
