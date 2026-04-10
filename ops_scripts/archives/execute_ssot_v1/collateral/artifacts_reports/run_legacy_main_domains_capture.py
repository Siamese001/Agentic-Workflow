#!/usr/bin/env python3
"""Deterministic heal-mode runner — Wave 3 containment script.

Sets AGENTIC_ALLOW_MUTATION_FOR_TESTS=1, imports _legacy_main in-process,
runs with ['--domains'] (no --validate, no --dry-run), and writes a
concise run log to docs/evidence/healmode_run_output.txt.

Usage:
    python docs/evidence/run_legacy_main_domains_capture.py
"""

from __future__ import annotations

import json
import os
import sys
import traceback
from pathlib import Path

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
os.chdir(REPO_ROOT)
sys.path.insert(0, str(REPO_ROOT))

os.environ["AGENTIC_ALLOW_MUTATION_FOR_TESTS"] = "1"

OUT_PATH = REPO_ROOT / "docs" / "evidence" / "healmode_run_output.txt"
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

log = open(OUT_PATH, "w", encoding="utf-8")


def _log(msg: str) -> None:
    log.write(msg + "\n")
    log.flush()


_log(f"REPO_ROOT: {REPO_ROOT}")
_log("INVOCATION: _legacy_main(args=['--domains'])")
_log("DRY_RUN=False, VALIDATE=False")
_log("AGENTIC_ALLOW_MUTATION_FOR_TESTS=1")
_log("---")

# Import after env setup
from ops_scripts.dev_tools.L0_routing_scripts.execute_ssot import _legacy_main  # noqa: E402

exit_status = "OK"
exit_code = 0
exc_text = ""

try:
    _legacy_main(["--domains"])
except SystemExit as e:    # guardian: SystemExit should be handled with specific context
    exit_code = e.code if e.code is not None else 0
    if exit_code != 0:
        exit_status = f"EXIT_{exit_code}"
except (ValueError, TypeError, RuntimeError) as e:
    # TODO: Handle specific exception properly
    raise  # Re-raise after logging/handling
    exit_status = "EXCEPTION"
    exc_text = traceback.format_exc()

_log(f"EXIT_STATUS: {exit_status}")
_log(f"EXIT_CODE: {exit_code}")
if exc_text:
    _log("TRACEBACK:")
    _log(exc_text)

# Check runtime_state.json
rsp = REPO_ROOT / "runtime_state.json"
if rsp.exists():
    try:
        data = json.loads(rsp.read_text(encoding="utf-8"))
        keys = list(data.keys())[:10]
        _log(f"runtime_state.json: PARSE_OK keys={keys}")
    except Exception as e2:
        # TODO: Handle specific exception properly
        raise  # Re-raise after logging/handling
        _log(f"runtime_state.json: PARSE_FAIL: {e2}")
else:
    _log("runtime_state.json: NOT_FOUND")

log.close()
print(f"DONE — log written to {OUT_PATH}")
