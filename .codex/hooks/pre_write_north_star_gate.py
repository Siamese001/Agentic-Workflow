"""North-Star Relevance Gate (PreToolUse on Edit|Write|MultiEdit).

The MISSING 'relevance' primitive (RCA 2026-06-15). Every other PreToolUse gate checks FORM
(branch, plan-format, retrieval budgets, file routing); NONE checks whether the edit advances the
north star (apps_rg 11/11 E2E). So off-target meta-work — building/deleting governance machinery
while lanes are unfinished — was never intercepted, and the lone relevance judgment was delegated to
the model itself (the governed actor = structurally self-bypassable, same defect as 0/317 PRs
self-merged).

This gate makes the north star the centerpiece of the edit decision. When an edit targets a KNOWN
off-north-star surface AND lanes < lanes_total, it BLOCKS (exit 2) and instructs the model to put
the decision to the operator via the native ``AskUserQuestion`` tool — with the disciplined "Park
it" option pre-marked RECOMMENDED at a confidence EARNED from the operator's own recent base-rate,
and the off-target option clearly labelled dopamine-seeking at the inverse (low) confidence.

Why a block-and-instruct (not a direct tool call): a PreToolUse hook returns an exit code, it
cannot itself render ``AskUserQuestion``. So it blocks and hands the model the exact option shape.

Choices the operator gets (rendered by the model per .codex/skills/ask-user-question-recommendation):
  1. "Park it (Recommended)" desc begins [RECOMMENDED ⭐ confidence=<earned>]
  2. "Do it now" desc begins [confidence=<inverse>]
  3. "Park + promote at review" desc begins [confidence=0.50]
Each description includes Pros: and Cons:, and the recommended one includes Flips if.

Auto-disables when lanes_passing >= lanes_total (after ship; no nagging). Always-exempt: PARKING_LOT.md
(capture must never be blocked), the gate's own state, and the harness's ~/.codex scratch.
Fail-soft: any internal error or missing/garbled state exits 0 (never blocks unrelated work).
Bypass: NORTH_STAR_GATE_BYPASS=1, or mode NORTH_STAR_GATE_ENFORCE=warn|off.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

_BYPASS_ENV = "NORTH_STAR_GATE_BYPASS"
_MODE_ENV = "NORTH_STAR_GATE_ENFORCE"  # ask (default) | warn | off
_STATE_REL = "config/north_star_state.json"
REPO_ROOT = Path(__file__).resolve().parents[2]

# Edits that ADVANCE the north star — always allowed (apps_rg + apps_lic + apps_eval + apps_underwriting_ai; see config/north_star_state.json goals[]).
_NORTH_PREFIXES = (
    "apps_rg/", "apps_lic/", "apps_eval/", "apps_underwriting_ai/",
    "tests/unit/apps_rg", "tests/apps_rg",
    "tests/unit/apps_lic", "tests/apps_lic",
    "tests/unit/apps_eval", "tests/apps_eval",
    "tests/unit/apps_underwriting_ai", "tests/apps_underwriting_ai",
)
# KNOWN displacement surfaces — intercept while lanes are unfinished. Deliberately conservative:
# core/spine work, app config, READMEs, and neutral paths are NOT intercepted (avoid over-blocking).
_OFF_STAR_PREFIXES = (
    ".codex/rules", ".codex/hooks", ".codex/governance", ".codex/skills",
    ".codex/agents", ".codex/settings", ".codex/plans", ".codex/commands",
    "plans/", "ops_scripts/ci", "ops_scripts/calibration", "ops_scripts/maintenance",
    "docs/reports/governance", ".github/",
)
# Capture + the gate's own infra must never be blocked.
_EXEMPT_SUBSTR = ("parking_lot.md", "north_star_state.json", "pre_write_north_star_gate.py")


def _repo_rel(file_path: str) -> str:
    p = file_path.replace("\\", "/")
    if p.startswith("./"):
        p = p[2:]
    root = REPO_ROOT.as_posix().rstrip("/") + "/"
    if p.startswith(root):
        p = p[len(root):]
    # strip any leading absolute prefix up to a known repo segment
    for seg in ("apps_rg/", "apps_eval/", "apps_underwriting_ai/", "tests/", ".codex/", "plans/", "ops_scripts/", "docs/", ".github/", "config/"):
        i = p.find(seg)
        if i > 0:
            p = p[i:]
            break
    return p


def _load_state(state_path: Path | None = None) -> dict:
    try:
        sp = state_path or (REPO_ROOT / _STATE_REL)
        return json.loads(sp.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _confidence(state: dict) -> tuple[float, float]:
    """Return (park_confidence, dopamine_confidence) EARNED from the recent base-rate."""
    pct = state.get("recent_north_star_pct", 20)
    try:
        pct = max(0.0, min(100.0, float(pct)))
    except (TypeError, ValueError):
        pct = 20.0
    dopamine = round(pct / 100.0, 2)
    park = round(1.0 - dopamine, 2)
    # floor the recommendation so it always reads as a confident default
    park = max(park, 0.70)
    return park, dopamine


def _classify(rel: str) -> str:
    low = rel.lower()
    if any(s in low for s in _EXEMPT_SUBSTR):
        return "exempt"
    if low.startswith(_NORTH_PREFIXES) or any(low.startswith(p) for p in _NORTH_PREFIXES):
        return "north"
    if any(low.startswith(p) for p in _OFF_STAR_PREFIXES):
        return "off_star"
    return "neutral"


def _instruction(rel: str, state: dict) -> str:
    passing = state.get("lanes_passing", 0)
    total = state.get("lanes_total", 11)
    pct = state.get("recent_north_star_pct", 20)
    park, dop = _confidence(state)
    return (
        f"NORTH-STAR GATE: this edit targets `{rel}` — an off-north-star surface while lanes are "
        f"{passing}/{total}.\n"
        "The north star is the centerpiece of this decision. Do NOT silently proceed. Put it to the "
        "operator now via the native AskUserQuestion tool, recommended option FIRST, using exactly "
        "this shape (per .codex/skills/ask-user-question-recommendation):\n\n"
        "  Q: \"This write is off the 11/11 apps_rg E2E north star. Park it or do it now?\"\n"
        f"  1. \"Park it (Recommended)\"  desc: \"[RECOMMENDED ⭐ confidence={park:.2f}] "
        "Pros: captures the idea without derailing lane work. Cons: delays this governance edit. "
        f"Flips if the edit directly unblocks the failing lane today. Earned from your base-rate: only {pct}% "
        f"of recent commits were north-star, so ~{int(park*100)}% of off-target work historically did not "
        "advance the goal.\"\n"
        f"  2. \"Do it now\"  desc: \"[confidence={dop:.2f}] Pros: handles the meta-work immediately. "
        "Cons: continues off-north-star work while lanes are incomplete.\"\n"
        "  3. \"Park + promote at weekly review\"  desc: \"[confidence=0.50] Pros: preserves the idea "
        "and creates a review point. Cons: adds a later triage step.\"\n\n"
        "On choice 1 or 3: append a one-line `[P]` entry to PARKING_LOT.md and ABANDON this edit.\n"
        f"On choice 2: retry the edit with {_BYPASS_ENV}=1 in the environment.\n"
        f"(Gate auto-disables at {total}/{total}. Suppress: {_MODE_ENV}=warn|off or {_BYPASS_ENV}=1.)\n"
        "Reminder: deterministic workflow first, one live product path over many control planes, "
        "and the live trace matters more than adjacent artifacts."
    )


def evaluate(data: dict, state: dict | None = None, env: dict | None = None) -> tuple[int, str]:
    """Pure decision function. Returns (exit_code, reason). exit 2 = block + instruct."""
    env = env if env is not None else os.environ
    if str(env.get(_BYPASS_ENV, "")).strip().lower() in ("1", "true", "yes"):
        return 0, ""
    mode = str(env.get(_MODE_ENV, "ask")).strip().lower() or "ask"
    if mode == "off":
        return 0, ""
    if str(data.get("tool_name", "")) not in ("Edit", "Write", "MultiEdit"):
        return 0, ""
    tool_input = data.get("tool_input") or {}
    file_path = str(tool_input.get("file_path") or "").strip()
    if not file_path:
        return 0, ""
    # harness scratch under ~/.codex is never a repo edit
    try:
        home_claude = (Path.home() / ".codex").resolve()
        fp = Path(file_path).expanduser().resolve()
        if fp == home_claude or home_claude in fp.parents:
            return 0, ""
    except (OSError, ValueError, RuntimeError):
        pass
    state = state if state is not None else _load_state()
    if not state or not state.get("enabled", True):
        return 0, ""
    passing = state.get("lanes_passing", 0)
    total = state.get("lanes_total", 11)
    try:
        if int(passing) >= int(total):
            return 0, ""  # shipped — gate auto-disabled
    except (TypeError, ValueError):
        return 0, ""
    rel = _repo_rel(file_path)
    if _classify(rel) != "off_star":
        return 0, ""
    reason = _instruction(rel, state)
    if mode == "warn":
        return 0, "WARN: " + reason
    return 2, reason


def main() -> int:
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
        code, reason = evaluate(data)
        if reason:
            print(reason, file=sys.stderr)
        return code
    except Exception:  # guardian: allow-broad-exception -- hook fail-soft contract
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
