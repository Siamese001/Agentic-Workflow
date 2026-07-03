#!/usr/bin/env python3
"""pre_user_prompt_adg_ssot_gate.py — ADG SQLite/MCP green-light for T2/T3 prompts.

Lean Claude Code ``UserPromptSubmit`` gate enforcing constitutional §13 with the
corrected SSOT semantics from plan ``adg-redis-hotcache-enforcement-b9f4c2``:

  - **ADG SQLite snapshot is the SSOT.** If no readable canonical
    ``artifacts/adg/adg_indexed_*.sqlite`` snapshot exists, a T2/T3 prompt is
    **BLOCKED** (exit 2): the agent cannot do reliable graph work without the
    source of truth.
  - **ADG Redis is a non-authoritative hot cache.** A cold/absent Redis hot cache
    is advisory only and **never blocks** — SQLite serves every query directly
    (constitutional §28 SQLite-direct fallback).
  - **ADG MCP transport must be open for ordinary T2/T3 work.** A live process or
    readable SQLite snapshot is not enough to prove the active Codex stdio route
    is callable. T2/T3 prompts block unless the supervisor reports an open
    transport, except explicit ADG transport recovery/RCA prompts.

This reuses ``classify_tier`` / ``check_adg_health_red`` / ``check_redis_*`` from
``pre_prompt_classifier.py`` so the probe logic has a single source of truth. It
deliberately does NOT inject the structured-reasoning mandate or MCP routing
traces — that is the classifier's concern, out of scope for this green-light gate.

Payload: reads the ``UserPromptSubmit`` JSON from stdin. Accepts both the Claude
Code shape (``{"prompt": "..."}``) and the legacy ``{"tool_info": {...}}`` shape.

Exit codes: 0 for T0/T1 and healthy T2/T3; 2 to block a T2/T3 prompt when the
SQLite SSOT or ADG MCP transport is unavailable.

Bypass: ``ADG_SSOT_GATE_BYPASS=1``.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any
from pathlib import Path

_GOV_DIR = Path(__file__).resolve().parent
if str(_GOV_DIR) not in sys.path:
    sys.path.insert(0, str(_GOV_DIR))
_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

_ADG_RECOVERY_TERMS = (
    "transport",
    "closed",
    "callability",
    "callable",
    "proof",
    "rca",
    "recover",
    "recovery",
    "reconnect",
    "restart",
    "reattach",
    "supervisor",
    "health",
    "unavailable",
    "failure",
    "failed",
    "broken",
    "repair",
    "restore",
)


def _read_payload(raw: str) -> dict[str, Any]:
    """Parse the hook payload; return an empty dict for invalid/non-object input."""
    try:
        payload = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _read_prompt(raw: str) -> str:
    """Extract the prompt text from either payload shape; '' if absent/invalid."""
    payload = _read_payload(raw)
    tool_info = payload.get("tool_info", payload)
    if not isinstance(tool_info, dict):
        return ""
    return tool_info.get("user_prompt") or tool_info.get("prompt") or ""


def _read_session_id(raw: str) -> str:
    """Extract the Codex session id when the hook payload provides one."""
    payload = _read_payload(raw)
    tool_info = payload.get("tool_info", payload)
    for source in (payload, tool_info):
        if isinstance(source, dict):
            value = source.get("session_id") or source.get("sessionId")
            if isinstance(value, str) and value.strip():
                return value.strip()
    return ""


def _is_adg_transport_recovery_prompt(prompt: str) -> bool:
    """Allow the work needed to repair ADG itself when the transport is closed."""
    text = prompt.lower()
    return "adg" in text and any(term in text for term in _ADG_RECOVERY_TERMS)


def _check_adg_transport_open(session_id: str = "") -> tuple[bool, str, dict[str, Any]]:
    """Probe the out-of-band supervisor for active-session ADG MCP callability."""
    try:
        from tools.adg.mcp import supervisor

        result = supervisor.transport_status(session_id=session_id or None)
    except Exception as exc:  # noqa: BLE001
        # guardian: allow-broad-exception -- probe errors block ordinary T2/T3 but
        # must not crash the hook host or prevent explicit ADG recovery prompts.
        return False, "probe_error", {"error": f"{type(exc).__name__}: {exc}"}
    status = str(result.get("status") or "unknown")
    return bool(result.get("open")), status, result


def _transport_detail(result: dict[str, Any]) -> str:
    callable_proof = result.get("callable_proof") if isinstance(result, dict) else None
    proof_required = ""
    if isinstance(callable_proof, dict):
        proof_required = str(callable_proof.get("proof_required") or "")
    heartbeat_pids = result.get("heartbeat_authoritative_pids") if isinstance(result, dict) else None
    proof_source = ""
    if isinstance(callable_proof, dict):
        proof_source = str(callable_proof.get("selected_source") or "none")
    pieces = []
    if heartbeat_pids:
        pieces.append(f"heartbeat_pids={heartbeat_pids}")
    if proof_source:
        pieces.append(f"proof_source={proof_source}")
    if proof_required:
        pieces.append(proof_required)
    if not pieces and isinstance(result, dict) and result.get("error"):
        pieces.append(str(result.get("error")))
    return " ".join(pieces)


def main() -> int:
    if os.getenv("ADG_SSOT_GATE_BYPASS") == "1":
        return 0
    try:
        if sys.stdin.isatty():
            return 0  # standalone-invocation guard: never hang waiting on a TTY
    except (ValueError, OSError):
        pass
    raw = sys.stdin.read()
    if not raw.strip():
        return 0

    prompt = _read_prompt(raw)
    if not prompt:
        return 0
    session_id = _read_session_id(raw)

    try:
        import pre_prompt_classifier as ppc
    except ImportError:
        return 0  # fail-open: probe logic unavailable, do not block

    tier = ppc.classify_tier(prompt)
    if tier not in ("T2", "T3"):
        return 0  # T0/T1 never gated

    try:
        sqlite_red = ppc.check_adg_health_red(ppc.repo_root)
    except Exception:  # noqa: BLE001
        # guardian: allow-broad-except -- gate fail-soft contract (never block on probe error)
        return 0

    if sqlite_red:
        print(
            f"[adg_ssot_gate] BLOCKED: {tier} prompt — ADG SQLite SSOT is unavailable "
            "(no readable artifacts/adg/adg_indexed_*.sqlite snapshot). Regenerate with "
            "`python tools/generate/generate_full_adg.py`, then retry (constitutional §13).",
            file=sys.stderr,
        )
        return 2

    transport_open, transport_status, transport_result = _check_adg_transport_open(session_id)
    if not transport_open:
        detail = _transport_detail(transport_result)
        if _is_adg_transport_recovery_prompt(prompt):
            print(
                f"[adg_ssot_gate] {tier}: ADG SQLite SSOT green; ADG MCP transport "
                f"is {transport_status}, but this looks like ADG transport recovery/RCA. "
                "Allowing recovery path only.",
                file=sys.stderr,
            )
        else:
            print(
                f"[adg_ssot_gate] BLOCKED: {tier} prompt — ADG MCP transport is "
                f"{transport_status}; active-session callability proof is required "
                f"before ordinary T2/T3 work. {detail}",
                file=sys.stderr,
            )
            return 2

    # SQLite SSOT green — surface advisory Redis hot-cache status (never blocks).
    try:
        if ppc.check_redis_up() and ppc.check_redis_adg_hot():
            print(
                f"[adg_ssot_gate] {tier}: ADG SQLite SSOT green; Redis hot cache warm.",
                file=sys.stderr,
            )
        else:
            print(
                f"[adg_ssot_gate] {tier}: ADG SQLite SSOT green; Redis hot cache cold/absent "
                "(advisory — not blocking). Warm it: python tools/adg/adg_redis_ingest.py --force",
                file=sys.stderr,
            )
    except Exception:  # noqa: BLE001
        # guardian: allow-broad-except -- advisory Redis status only, never fatal
        pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
