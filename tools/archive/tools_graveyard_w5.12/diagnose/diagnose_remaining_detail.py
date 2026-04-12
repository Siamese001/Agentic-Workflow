"""Get detailed info about each remaining error: test file, source file, line, error."""

import os
import re
import subprocess

ROOT = r"C:\Git\Agentic-Workflow"
unit_dir = os.path.join(ROOT, "tests", "unit")

for sd in sorted(os.listdir(unit_dir)):
    sdp = os.path.join(unit_dir, sd)
    if not os.path.isdir(sdp) or sd.startswith("_"):
        continue

    r = subprocess.run(
        ["python", "-m", "pytest", f"tests/unit/{sd}", "--co", "--tb=short", "-p", "no:logging", "-q"],
        capture_output=True,
        text=True,
        cwd=ROOT,
        timeout=60,
    )
    out = re.sub(r"\x1b\[[0-9;]*m", "", r.stdout)
    lines = out.split("\n")

    i = 0
    while i < len(lines):
        if "ERROR collecting" in lines[i]:
            test_file = (
                lines[i].split("ERROR collecting ")[-1].split(" ")[0]
                if "ERROR collecting" in lines[i]
                else ""
            )
            src_file = ""
            src_line = ""
            err_msg = ""
            for j in range(i + 1, min(i + 30, len(lines))):
                s = lines[j].strip()
                m = re.match(r"((?:agentic_core|apps_\w+|system_learning)[/\\].+\.py):(\d+)", s)
                if m:
                    src_file = m.group(1).replace("\\", "/")
                    src_line = m.group(2)
                if s.startswith("E   ") and len(s) > 6:
                    msg = s[4:].strip()
                    if not msg.startswith("File "):
                        err_msg = msg
                        break

            if err_msg:
                print(f"TEST: {test_file}")
                print(f"  SRC: {src_file}:{src_line}")
                print(f"  ERR: {err_msg[:150]}")
                print()
        i += 1
