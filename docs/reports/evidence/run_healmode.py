"""Wave 3: True heal-mode run — no --validate, no --dry-run."""

import json
import os
import sys
import traceback

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
os.chdir(os.path.join(os.path.dirname(__file__), "..", ".."))
os.environ["AGENTIC_ALLOW_MUTATION_FOR_TESTS"] = "1"

out = os.path.join("docs", "evidence", "healmode_run_output.txt")
log = open(out, "w", encoding="utf-8")
log.write("INVOCATION: _legacy_main(args=['--domains'])\n")
log.write("DRY_RUN=False, VALIDATE=False\n")
log.write("AGENTIC_ALLOW_MUTATION_FOR_TESTS=1\n")
log.write("---\n")
log.flush()

from agentic_core.L0_routing.scripts.execute_ssot import _legacy_main

ec = "OK"
code = 0
exec_err = ""

try:
    _legacy_main(["--domains"])
except SystemExit as e:
    code = e.code if e.code is not None else 0
    if code != 0:
        ec = f"EXIT_{code}"
except Exception:
    ec = "FAIL"
    exec_err = traceback.format_exc()

log.write(f"EXIT: {ec} code={code}\n")
if exec_err:
    log.write(exec_err + "\n")

rsp = "runtime_state.json"
if os.path.exists(rsp):
    try:
        d = json.load(open(rsp, encoding="utf-8"))
        log.write(f"runtime_state.json: PARSE_OK keys={list(d.keys())[:10]}\n")
    except Exception as e2:
        log.write(f"runtime_state.json: PARSE_FAIL: {e2}\n")
else:
    log.write("runtime_state.json: NOT_FOUND\n")

log.close()
print(f"DONE — output written to {out}")
