"""Agent/Workflow fan-out restraint gate (PreToolUse on the Workflow tool).

User directive (2026-06-13): "ensure there are not agents spun up taking millions of
tokens only when they need to — this goes for all efforts, especially ultracode, where I
see most of the agents spun up."

Sub-agent fan-out (a Workflow that calls many ``agent()``/``parallel()``/``pipeline()``)
costs large token volumes. Effort tier (max / ultracode / ultra) raises rigor, not agent
count. This hook inspects an INLINE Workflow script and, when it reads as HIGH-SCALE *and*
discovery/inventory-dominant (the costly "re-run discovery through agents" anti-pattern),
surfaces a confirmation so an unneeded mass fan-out does not run silently.

Conservative by design — these pass untouched:
  * verification / adversarial / judge-panel / regression workflows (justification signals)
  * migration / per-item / worktree / implement workflows
  * single agents and small fan-outs
  * named-workflow calls and ``scriptPath`` re-runs (no inline script to assess)

House hook contract:
  * stdin  = PreToolUse JSON: {"tool_name": "...", "tool_input": {...}}
  * exit 0 = allow (default "ask"/"warn" modes); exit 2 = block ("block" mode)
  * fail-soft: any internal error exits 0 (never blocks legitimate work)

Modes — FANOUT_RESTRAINT_ENFORCE (default "ask"):
  ask   -> emit PreToolUse permissionDecision="ask" (user confirms the fan-out); exit 0
  warn  -> print a reminder to stderr; exit 0 (non-blocking)
  block -> print a reminder to stderr; exit 2 (model must trim or set the bypass)
Bypass — FANOUT_RESTRAINT_BYPASS=1 -> exit 0, no checks.
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LOG_FILE = REPO_ROOT / "artifacts" / "governance" / "agent_fanout_restraint.jsonl"

_TRUTHY = ("1", "true", "yes", "on")

# ── Scale signals ────────────────────────────────────────────────────────────
_AGENT_CALL_RE = re.compile(r"\bagent\s*\(")
_PARALLEL_RE = re.compile(r"\bparallel\s*\(")
_PIPELINE_RE = re.compile(r"\bpipeline\s*\(")
# budget/fleet-scaled fan-out: `while (budget…)`, `Array.from({length…})`, a `FLEET` const
_FLEET_LOOP_RE = re.compile(
    r"while\s*\([^)]*budget|Array\.from\s*\(\s*\{\s*length|\bFLEET\b", re.IGNORECASE
)

# ── Intent signals (case-insensitive substring match on the script text) ──────
_DISCOVERY_TOKENS = (
    "discover", "discovery", "inventory", "survey", "catalog", "catalogue",
    "enumerate", "reconnaissance", "recon", "map the", "map all", "map every",
    "scan the", "scan all", "explore the", "explore every", "what exists",
    "find all", "find every", "list all", "list every", "where is", "who uses",
    "what depends", "audit the", "sweep", "comb through", "understand the codebase",
    "map the codebase", "inventory of", "catalog of", "survey of",
)
_JUSTIFICATION_TOKENS = (
    "verify", "verifier", "adversarial", "refute", "skeptic", "judge", "panel",
    "cross-check", "independent", "migrate", "transform each", "per-file",
    "per-item", "worktree", "implement", "patch each", "fix each", "synthesize",
    "synthesis", "tournament", "dimension", "regression",
)


def _distinct_hits(text_lc: str, tokens: tuple[str, ...]) -> list[str]:
    return [t for t in tokens if t in text_lc]


def assess_fanout(script: str) -> dict:
    """Pure, testable assessment of a Workflow script's fan-out shape.

    Returns counts, the matched signals, and the trigger decision. The trigger is
    deliberately conservative: it requires real fan-out scale AND at least two
    discovery signals AND discovery outweighing justification signals.
    """
    s = script or ""
    s_lc = s.lower()

    agent_calls = len(_AGENT_CALL_RE.findall(s))
    has_parallel = bool(_PARALLEL_RE.search(s))
    has_pipeline = bool(_PIPELINE_RE.search(s))
    has_fleet_loop = bool(_FLEET_LOOP_RE.search(s))

    high_scale = (
        agent_calls >= 4
        or has_fleet_loop
        or ((has_parallel or has_pipeline) and agent_calls >= 2)
    )

    discovery = _distinct_hits(s_lc, _DISCOVERY_TOKENS)
    justification = _distinct_hits(s_lc, _JUSTIFICATION_TOKENS)

    triggered = high_scale and len(discovery) >= 2 and len(discovery) > len(justification)

    return {
        "agent_calls": agent_calls,
        "has_parallel": has_parallel,
        "has_pipeline": has_pipeline,
        "has_fleet_loop": has_fleet_loop,
        "high_scale": high_scale,
        "discovery_signals": discovery,
        "justification_signals": justification,
        "triggered": triggered,
    }


def build_reason(assessment: dict, workflow_name: str) -> str:
    disc = ", ".join(assessment["discovery_signals"][:6]) or "—"
    scale = (
        "budget/fleet-scaled"
        if assessment["has_fleet_loop"]
        else f"~{assessment['agent_calls']} agent call(s)"
    )
    name = f" '{workflow_name}'" if workflow_name else ""
    return (
        f"[fanout-restraint] Workflow{name} reads as high-scale ({scale}) AND "
        f"discovery/inventory-dominant (signals: {disc}). Sub-agent fan-out costs large "
        "token volumes — spin up agents only when the work genuinely needs it (independent "
        "parallel subtasks, scale beyond one context, or adversarial verification), NOT to "
        "re-run discovery an existing plan / prior results already provide. Effort tier "
        "(max/ultracode/ultra) raises rigor, not agent count. If this fan-out is needed, "
        "confirm/proceed; otherwise execute inline or from the existing plan. "
        "Doctrine: .claude/rules/agent-fanout-restraint.md  ·  Bypass: FANOUT_RESTRAINT_BYPASS=1."
    )


def _log(assessment: dict, mode: str, workflow_name: str) -> None:
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "ts_utc": datetime.now(timezone.utc).isoformat(),
            "kind": "agent_fanout_restraint",
            "mode": mode,
            "workflow_name": workflow_name,
            "agent_calls": assessment["agent_calls"],
            "high_scale": assessment["high_scale"],
            "has_fleet_loop": assessment["has_fleet_loop"],
            "discovery_signals": assessment["discovery_signals"],
            "justification_signals": assessment["justification_signals"],
        }
        with LOG_FILE.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError:
        pass


def main() -> int:
    try:
        if os.environ.get("FANOUT_RESTRAINT_BYPASS", "").strip().lower() in _TRUTHY:
            return 0

        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}

        tool_name = str(data.get("tool_name") or "")
        if tool_name and tool_name != "Workflow":
            return 0

        tool_input = data.get("tool_input") or {}
        script = tool_input.get("script")
        if not isinstance(script, str) or not script.strip():
            # named workflow or scriptPath re-run — nothing inline to assess
            return 0

        assessment = assess_fanout(script)
        if not assessment["triggered"]:
            return 0

        workflow_name = ""
        m = re.search(r"name:\s*['\"]([^'\"]+)['\"]", script)
        if m:
            workflow_name = m.group(1)

        mode = os.environ.get("FANOUT_RESTRAINT_ENFORCE", "ask").strip().lower()
        if mode not in ("ask", "warn", "block"):
            mode = "ask"

        _log(assessment, mode, workflow_name)
        reason = build_reason(assessment, workflow_name)

        if mode == "block":
            print(reason, file=sys.stderr)
            return 2
        if mode == "warn":
            print(reason, file=sys.stderr)
            return 0

        # mode == "ask" — non-blocking confirm (fail-open if the harness ignores it)
        print(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "ask",
                        "permissionDecisionReason": reason,
                    }
                }
            )
        )
        return 0

    except Exception:  # guardian: allow-broad-exception -- hook fail-soft contract
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
