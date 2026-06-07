"""Post-Cursor-Agent dispatcher — single-process replacement for the 16-script chain.

Per W4 design notes in plan rules-hooks-memories-consolidation-48b4d6.md:
- All 16 standalone post_cursor_agent_*.py scripts read sys.stdin once
- Spawning 16 python.exe processes per response costs ~3 s of overhead on Windows
- This dispatcher reads stdin once, then fans out to each script in-process

Two execution paths per registered handler:
1. **Native handler module** (Phase A) — `_post_handlers/<name>.py` exposing
   `run(parsed, repo_root)`. Handlers refactored to use the shared
   `ParsedResponse` and skip JSON re-parsing.
2. **Legacy wrapper** (Phase B) — load the existing standalone script as a
   module via `importlib.util`, redirect `sys.stdin` to a fresh
   `StringIO(parsed.raw)`, and call its `main()`. Bit-identical behavior to
   running the script as a subprocess, minus the process-spawn cost.

Activation: env `POST_CURSOR_AGENT_DISPATCHER=1`.
When unset → no-op; existing standalone scripts run unchanged via hooks.json.

Per constitutional §30 risk floor (96-hour silent capture outage precedent),
operators MUST run the dispatcher in shadow mode for ≥7 days before removing
any standalone script entry from `.cursor/hooks.json`.

Fail policy: OPEN — any handler error is logged and swallowed. One handler
must never break sibling handlers.
"""

from __future__ import annotations

import importlib.util
import io
import json
import os
import sys
import traceback
from pathlib import Path
from typing import Callable

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))

from _post_handlers import ParsedResponse  # noqa: E402
from _post_handlers import cleanup as h_cleanup  # noqa: E402
from _post_handlers import grep_budget as h_grep_budget  # noqa: E402
from _post_handlers import heartbeat as h_heartbeat  # noqa: E402
from _post_handlers import read_budget as h_read_budget  # noqa: E402
from _post_handlers import token_telemetry as h_token_telemetry  # noqa: E402

# ---------------------------------------------------------------------------
# Native handlers (Phase A — refactored to ParsedResponse contract)
# ---------------------------------------------------------------------------

NATIVE_HANDLERS: list[tuple[str, Callable[[ParsedResponse, Path], None]]] = [
    ("heartbeat", h_heartbeat.run),
    ("cleanup", h_cleanup.run),
    ("grep_budget", h_grep_budget.run),
    ("read_budget", h_read_budget.run),
    ("token_telemetry", h_token_telemetry.run),
]

# ---------------------------------------------------------------------------
# Legacy wrappers (Phase B — preserve standalone scripts; eliminate spawn cost)
#
# Order matches `.cursor/hooks.json` post_cursor_agent_response chain so the
# dispatcher's behavior is observably identical to the standalone chain.
# ---------------------------------------------------------------------------

LEGACY_SCRIPTS: list[str] = [
    # Author-Gate + ADG run in after_agent_governance_dispatch before dispatch; skip re-run here.
    "post_cursor_agent_scope_drift_detector.py",
    "post_cursor_agent_writeback_audit.py",
    "post_cursor_agent_deferred_scope_capture.py",
    "post_cursor_agent_next_step_capture.py",
    "post_cursor_agent_next_step_miss_detector.py",
    "post_cursor_agent_wave_lifecycle_capture.py",
    "post_cursor_agent_wave_completion_audit.py",
    "post_cursor_agent_mcp_preflight_audit.py",
    "post_cursor_agent_plan_evidence_gate.py",
    "post_cursor_agent_plan_wave_summary_audit.py",
    "post_cursor_agent_plan_registration_capture.py",
    "post_cursor_agent_fortknox_integrity_audit.py",
]


# ---------------------------------------------------------------------------
# Stdin parse — single pass
# ---------------------------------------------------------------------------

def _parse_stdin() -> ParsedResponse:
    try:
        raw = "" if sys.stdin.isatty() else sys.stdin.read()
    except (OSError, ValueError):
        raw = ""

    parsed = ParsedResponse(raw=raw)
    if not raw.strip():
        return parsed

    try:
        obj = json.loads(raw)
    except (ValueError, TypeError):
        parsed.response_text = raw
        return parsed

    if isinstance(obj, dict):
        parsed.json_payload = obj
        for key in ("response_text", "response", "text", "content"):
            val = obj.get(key)
            if isinstance(val, str):
                parsed.response_text = val
                break
        else:
            parsed.response_text = raw
        tools = obj.get("tool_calls")
        if isinstance(tools, list):
            parsed.tool_calls = [t for t in tools if isinstance(t, dict)]
    else:
        parsed.response_text = raw

    return parsed


# ---------------------------------------------------------------------------
# Legacy script loader — caches imported modules, redirects stdin per call
# ---------------------------------------------------------------------------

_LEGACY_MODULE_CACHE: dict[str, object] = {}


def _load_legacy_module(filename: str):
    """Import a standalone script as a module without polluting sys.modules.

    Uses a stable synthetic name keyed off the filename so the same module is
    cached across calls. Each call to `main()` is independent — the caller
    handles stdin redirection.
    """
    if filename in _LEGACY_MODULE_CACHE:
        return _LEGACY_MODULE_CACHE[filename]

    path = SCRIPTS_DIR / filename
    if not path.exists():
        raise FileNotFoundError(path)

    mod_name = "_dispatched_" + filename[: -len(".py")]
    spec = importlib.util.spec_from_file_location(mod_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"could not build spec for {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    _LEGACY_MODULE_CACHE[filename] = module
    return module


def _run_legacy(filename: str, parsed: ParsedResponse) -> None:
    """Invoke standalone script's `main()` with stdin redirected to parsed.raw."""
    module = _load_legacy_module(filename)
    main_fn = getattr(module, "main", None)
    if main_fn is None or not callable(main_fn):
        print(f"[dispatch] {filename} has no callable main()", file=sys.stderr)
        return

    saved_stdin = sys.stdin
    sys.stdin = io.StringIO(parsed.raw)
    try:
        main_fn()
    finally:
        sys.stdin = saved_stdin


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    if os.environ.get("POST_CURSOR_AGENT_DISPATCHER") != "1":
        # Disabled — standalone scripts in hooks.json own the chain.
        return 0

    parsed = _parse_stdin()

    # Native handlers first (they share the ParsedResponse and skip re-parsing).
    for name, fn in NATIVE_HANDLERS:
        try:
            fn(parsed, REPO_ROOT)
        except Exception as err:  # guardian: allow-broad-exception -- fail-soft per §30; one handler must never break siblings
            print(f"[dispatch] native handler '{name}' failed: {err}", file=sys.stderr)
            traceback.print_exc()

    # Legacy wrappers — bit-identical to running each script as a subprocess,
    # minus the process-spawn cost.
    for filename in LEGACY_SCRIPTS:
        try:
            _run_legacy(filename, parsed)
        except Exception as err:  # guardian: allow-broad-exception -- fail-soft per §30; one legacy script must never break siblings
            print(f"[dispatch] legacy script '{filename}' failed: {err}", file=sys.stderr)
            traceback.print_exc()

    return 0


if __name__ == "__main__":
    sys.exit(main())
