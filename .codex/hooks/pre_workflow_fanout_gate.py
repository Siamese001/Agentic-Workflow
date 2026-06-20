"""Agent/Workflow fan-out restraint gate (PreToolUse on the Workflow tool).

User directive (2026-06-13): "ensure there are not agents spun up taking millions of
tokens only when they need to — this goes for all efforts, especially ultracode, where I
see most of the agents spun up."

Multiple workflows / agents are welcome — parallel fan-out is a tool, not a cost to
minimise, and agent COUNT is NOT what this hook gates. The single anti-pattern it guards is
**re-running discovery a plan (or prior results) already provides**: a fan-out whose work is
purely discovery/inventory with no plan-execution or output intent. This hook inspects an
INLINE Workflow script and, when it reads as that pure-rediscovery shape (discovery-dominant
AND zero execution/output intent — at ANY agent count), surfaces a confirmation so redundant
re-discovery does not run silently.

Decoupled from count by design — these pass untouched at any scale:
  * verification / adversarial / judge-panel / regression workflows (justification signals)
  * migration / per-item / worktree / implement workflows
  * plan-execution / output-producing fan-out (execution signals) — even if it also discovers
  * large parallel-implementation fan-out (many agents, no discovery dominance)
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
# ── Execution / plan-output intent (the fan-out EXECUTES, it does not re-discover) ──
# ANY of these present means the work is not pure re-discovery, so the gate never fires —
# however many agents the script spins up. This is the escape valve that keeps multiple
# workflows/agents friction-free while still catching discovery a plan already provides.
_EXECUTION_TOKENS = (
    "the plan", "per the plan", "from the plan", "follow the plan",
    "plan provides", "plan already", "already mapped", "already know",
    "already understood", "produce", "generate", "output", "deliver",
    "emit", "render", "assemble", "write the", "apply the", "build the",
    "implement", "patch each", "fix each", "refactor",
)


def _distinct_hits(text_lc: str, tokens: tuple[str, ...]) -> list[str]:
    return [t for t in tokens if t in text_lc]


def assess_fanout(script: str) -> dict:
    """Pure, testable assessment of a Workflow script's fan-out shape.

    The trigger is **decoupled from agent COUNT** — multiple workflows/agents never fire on
    scale alone. It fires only on the **pure-rediscovery** shape: discovery/inventory
    dominates (≥2 distinct discovery signals, outweighing justification) AND there is *no*
    plan-execution or output intent in the script. That is precisely the work a plan (or
    prior results) should already provide. ``high_scale`` is still computed for
    telemetry/context, but it is NOT a trigger condition.
    """
    s = script or ""
    s_lc = s.lower()

    agent_calls = len(_AGENT_CALL_RE.findall(s))
    has_parallel = bool(_PARALLEL_RE.search(s))
    has_pipeline = bool(_PIPELINE_RE.search(s))
    has_fleet_loop = bool(_FLEET_LOOP_RE.search(s))

    # Informational only — high agent count never triggers the gate by itself.
    high_scale = (
        agent_calls >= 4
        or has_fleet_loop
        or ((has_parallel or has_pipeline) and agent_calls >= 2)
    )

    discovery = _distinct_hits(s_lc, _DISCOVERY_TOKENS)
    justification = _distinct_hits(s_lc, _JUSTIFICATION_TOKENS)
    execution = _distinct_hits(s_lc, _EXECUTION_TOKENS)

    # Pure re-discovery: discovery dominates AND nothing in the script says it will execute a
    # plan or produce an output. A fan-out that also executes/produces — at ANY agent count —
    # is real work, not rediscovery, and passes untouched.
    triggered = (
        len(discovery) >= 2
        and len(discovery) > len(justification)
        and len(execution) == 0
    )

    return {
        "agent_calls": agent_calls,
        "has_parallel": has_parallel,
        "has_pipeline": has_pipeline,
        "has_fleet_loop": has_fleet_loop,
        "high_scale": high_scale,
        "discovery_signals": discovery,
        "justification_signals": justification,
        "execution_signals": execution,
        "triggered": triggered,
    }


def build_reason(assessment: dict, workflow_name: str) -> str:
    disc = ", ".join(assessment["discovery_signals"][:6]) or "—"
    name = f" '{workflow_name}'" if workflow_name else ""
    return (
        f"[fanout-restraint] Workflow{name} reads as pure re-discovery — discovery/inventory "
        f"dominant (signals: {disc}) with no plan-execution or output intent in the script. "
        "Multiple workflows/agents are fine and agent count is not gated here; the only "
        "restraint is not re-running discovery a plan (or prior results) already provides. If a "
        "plan already covers this, execute it and produce the outputs instead of re-mapping. If "
        "this is genuine first-time discovery no plan covers, confirm/proceed. Effort tier "
        "(max/ultracode/ultra) raises rigor, not agent count. "
        "Doctrine: .codex/rules/agent-fanout-restraint.md  ·  Bypass: FANOUT_RESTRAINT_BYPASS=1."
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
            "execution_signals": assessment["execution_signals"],
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
