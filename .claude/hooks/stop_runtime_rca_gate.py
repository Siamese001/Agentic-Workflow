"""Runtime-RCA Stop gate (plan rca-depth-enforcement-83e392 W2).

Promotes the advisory runtime-RCA audit to a *blocking* forcing function on the single
highest-confidence, lowest-false-positive case: a refactoring turn that ships with no
Outcome frame at all (``detect()`` kind == ``missing_refactor_outcome``). On that case,
in ``block`` mode, the Stop is refused (``{"decision":"block"}`` + exit 2) so the model
re-composes with the frame. The deeper heuristics (``shallow_rca`` / ``incomplete_rca``)
stay advisory-only — a false block there would be far more annoying than useful.

Modes — ``RUNTIME_RCA_ENFORCE``:
  * ``off``   — never blocks, never warns.
  * ``warn``  — DEFAULT (shadow): logs "would block" to the receipt + stderr, allows.
  * ``block`` — refuses the Stop on ``missing_refactor_outcome``.

Escape hatches:
  * ``RUNTIME_RCA_AUDIT_BYPASS=1`` — full skip (shared with the advisory audit; scripted/batch runs).
  * Loop guard — blocks at most ``RUNTIME_RCA_GATE_MAX_BLOCKS`` (default 1) consecutive times
    per session, then allows with ``block_limit_reached`` so a model that genuinely cannot
    satisfy the frame is never trapped. The natural guard also holds: once the frame is added
    the check passes and no block fires.

Detection is NOT reimplemented here — ``detect()`` is imported from
``.claude/governance/scripts/post_agent_runtime_rca_audit.py`` so the contract stays SSOT;
this gate only adds the block decision + mode + loop guard.

Fail-open: any internal error exits 0 (never blocks unrelated work).
"""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path

from lib.claude_hook_common import allow, block, read_payload, resolve_response_text, warn, write_receipt

_REPO_ROOT = Path(__file__).resolve().parents[2]  # .claude/hooks/<this> -> repo root
_AUDIT_PATH = _REPO_ROOT / ".claude" / "governance" / "scripts" / "post_agent_runtime_rca_audit.py"
_STATE_FILE = _REPO_ROOT / "artifacts" / "governance" / "runtime_rca_gate_state.json"

# The single kind this gate is willing to BLOCK on (frame entirely absent).
_BLOCK_KIND = "missing_refactor_outcome"

_BLOCK_REASON = (
    "Refactoring turn is missing the Outcome frame. Add it before sending:\n"
    "  Did it run? <yes/no> | Verdict source: <command + exit code + verdict> | "
    "runtime provenance\n  What worked / Failure / Next\n"
    "On a FAILURE the frame's deep Layered RCA is also required (Immediate symptom -> Failing "
    "layer -> Why-chain >=2 levels -> Root cause distinct from symptom -> Evidence -> Confidence).\n"
    "SSOT: .claude/rules/001-runtime-seam-execution.md § Runtime failure ⇒ RCA mandatory; "
    "constitutional §37.\n"
    "Shadow/escape: RUNTIME_RCA_ENFORCE=warn|off, RUNTIME_RCA_AUDIT_BYPASS=1."
)


def _mode() -> str:
    raw = os.environ.get("RUNTIME_RCA_ENFORCE", "warn").strip().lower()
    return raw if raw in ("off", "warn", "block") else "warn"


def _bypass() -> bool:
    return os.environ.get("RUNTIME_RCA_AUDIT_BYPASS", "").strip().lower() in ("1", "true", "yes")


def _max_blocks() -> int:
    try:
        return max(0, int(os.environ.get("RUNTIME_RCA_GATE_MAX_BLOCKS", "1")))
    except ValueError:
        return 1


def _load_detect():
    """Import detect() from the advisory audit (SSOT). Returns None on any failure."""
    try:
        spec = importlib.util.spec_from_file_location("_runtime_rca_audit_for_gate", _AUDIT_PATH)
        if not spec or not spec.loader:
            return None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return getattr(mod, "detect", None)
    except Exception:  # guardian: allow-broad-exception -- detector import must fail open
        return None


def _read_state() -> dict:
    try:
        return json.loads(_STATE_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _write_state(state: dict) -> None:
    try:
        _STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        _STATE_FILE.write_text(json.dumps(state), encoding="utf-8")
    except OSError:
        pass


def _reset_session(session_id: str) -> None:
    if not session_id:
        return
    state = _read_state()
    if state.pop(session_id, None) is not None:
        _write_state(state)


def main() -> int:
    if _bypass():
        return allow("runtime-rca gate bypass")
    mode = _mode()
    if mode == "off":
        return allow("runtime-rca gate off")

    payload = read_payload()
    # Real Claude `Stop` payloads carry no inline response — resolve via the shared SSOT
    # (inline -> cursor text keys -> transcript recovery) so missing_refactor_outcome is
    # detected on real Stop events instead of the gate silently no-opping.
    text = resolve_response_text(payload)
    if not text.strip():
        return allow("empty stop payload")

    detect = _load_detect()
    if detect is None:
        return allow("detect() unavailable — fail open")
    try:
        _status, violations = detect(text)
    except Exception:  # guardian: allow-broad-exception -- detection failure must fail open
        return allow("detect() raised — fail open")

    session_id = str(payload.get("session_id") or "")
    blocking = any(v.get("kind") == _BLOCK_KIND for v in violations)
    if not blocking:
        # Compliant for the blocking case — clear the session's consecutive-block counter.
        _reset_session(session_id)
        return allow("no missing_refactor_outcome")

    if mode == "warn":
        write_receipt("stop_runtime_rca_gate", payload, "warn", "would_block:" + _BLOCK_KIND)
        return warn("runtime-rca gate (shadow): would block — " + _BLOCK_KIND)

    # mode == block — loop guard so the turn is never trapped.
    state = _read_state()
    count = int(state.get(session_id, 0)) if session_id else 0
    if session_id and count >= _max_blocks():
        write_receipt("stop_runtime_rca_gate", payload, "allow", "block_limit_reached")
        return allow("runtime-rca gate: block_limit_reached — not trapping the turn")

    if session_id:
        state[session_id] = count + 1
        _write_state(state)
    write_receipt("stop_runtime_rca_gate", payload, "block", _BLOCK_KIND)
    return block(_BLOCK_REASON)


if __name__ == "__main__":
    raise SystemExit(main())
