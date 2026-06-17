#!/usr/bin/env python3
"""
post_agent_plan_evidence_gate.py — Stop-equivalent plan evidence gate (P2).

Reads the Codex response from stdin. When the response edited or created
any ``.claude/plans/*.md`` file, runs the canonical graph-layer evidence
check (``ops_scripts/ci/check_graph_layer_evidence.py``) against that plan
file immediately — closing the loop for plans that would otherwise only
be validated at commit time.

Rationale: Kumar (https://ranjankumar.in/hooks-policy-as-code-agent-enforcement)
— "Does the Stop hook verify that required output artifacts exist if the
task produces them?" — legacy editor has no Stop hook, but post_agent_response
is the closest equivalent.

Behavior:
    - If the response contains no plan-file edits → exit 0 silently.
    - If a plan file lacks ``## ADG_GRAPH_LAYER_EVIDENCE`` AND declares
      refactor intent → exit 2 (block) + log to
      ``artifacts/governance/plan_evidence_violations.jsonl``.
    - Bypass: ``PLAN_EVIDENCE_GATE_BYPASS=1``.

Fail policy: OPEN for infrastructure errors (malformed JSON, file read
failures). CLOSED for declared refactor plans missing evidence.
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

fail_policy = "closed_for_refactor_plans"

_ROOT = Path(__file__).resolve().parents[3]
_PLANS_DIR = _ROOT / "docs" / "archive" / "windsurf" / "legacy-tree" / "plans"
_LOG_PATH = _ROOT / "artifacts" / "governance" / "plan_evidence_violations.jsonl"
_BYPASS_ENV = "PLAN_EVIDENCE_GATE_BYPASS"

# Matches any plan file path mentioned in a Codex response (edit/write tool
# invocations reference them). Absolute, backslash, or forward-slash forms.
_PLAN_PATH_RE = re.compile(
    r"[\\/\.]windsurf[\\/]plans[\\/]([A-Za-z0-9_\-]+-[0-9a-f]{6})\.md",
    re.IGNORECASE,
)

# Matches the required section header.
_EVIDENCE_HEADER_RE = re.compile(r"^##\s+ADG[_ ]GRAPH[_ ]LAYER[_ ]EVIDENCE\b", re.MULTILINE)

# Matches refactor intent declarations in plan body.
_REFACTOR_INTENT_RE = re.compile(
    r"\b(refactor(?:ing)?|burn[- ]?down|hotspot|anti[- ]?pattern|wave\s+plan)\b",
    re.IGNORECASE,
)


def _extract_response_text(payload: object) -> str:
    if isinstance(payload, str):
        return payload
    if isinstance(payload, dict):
        for key in ("tool_info", "response", "text", "content"):
            val = payload.get(key)
            if isinstance(val, dict):
                for inner in ("response", "text", "content"):
                    inner_val = val.get(inner)
                    if isinstance(inner_val, str) and inner_val.strip():
                        return inner_val
            if isinstance(val, str) and val.strip():
                return val
        try:
            return json.dumps(payload)
        except (TypeError, ValueError):
            return ""
    return ""


def _find_edited_plans(response_text: str) -> list[str]:
    """Return list of unique plan slugs referenced in the response."""
    return sorted(set(_PLAN_PATH_RE.findall(response_text)))


def _plan_file_valid(plan_path: Path) -> tuple[bool, str]:
    """Return (is_valid, reason). Valid means: no refactor intent OR has evidence section."""
    try:
        content = plan_path.read_text(encoding="utf-8")
    except OSError as exc:
        return True, f"unreadable:{exc}"  # fail-open on I/O

    has_refactor_intent = bool(_REFACTOR_INTENT_RE.search(content))
    if not has_refactor_intent:
        return True, "no_refactor_intent"

    has_evidence = bool(_EVIDENCE_HEADER_RE.search(content))
    if has_evidence:
        return True, "evidence_present"

    return False, "refactor_plan_missing_evidence"


def _append_violation(record: dict) -> None:
    _LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with _LOG_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record) + "\n")


def main() -> int:
    if sys.stdin.isatty():
        return 0
    if os.environ.get(_BYPASS_ENV):
        return 0

    try:
        raw = sys.stdin.read()
    except OSError:
        return 0
    if not raw.strip():
        return 0

    try:
        payload: object = json.loads(raw)
    except json.JSONDecodeError:
        payload = raw

    text = _extract_response_text(payload)
    if not text.strip():
        return 0

    edited_plans = _find_edited_plans(text)
    if not edited_plans:
        return 0

    violations: list[dict] = []
    for slug in edited_plans:
        plan_path = _PLANS_DIR / f"{slug}.md"
        if not plan_path.exists():
            continue
        ok, reason = _plan_file_valid(plan_path)
        if not ok:
            violations.append(
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "plan_slug": slug,
                    "plan_path": str(plan_path.relative_to(_ROOT)),
                    "reason": reason,
                    "severity": "blocking",
                }
            )

    if not violations:
        return 0

    for v in violations:
        try:
            _append_violation(v)
        except OSError:
            pass  # fail-open on log write

    print(
        f"[plan_evidence_gate] BLOCKING: {len(violations)} plan file(s) edited "
        f"declare refactor intent but lack '## ADG_GRAPH_LAYER_EVIDENCE' section. "
        f"Constitutional §22. Set {_BYPASS_ENV}=1 to override. "
        f"Plans: {', '.join(v['plan_slug'] for v in violations)}",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
