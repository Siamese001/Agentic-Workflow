"""W3.2: authorize CostGovernorAgent + GravityStateAgent (now zero-consumer
after removing their entries from the dead compat re-export shims).
"""

from __future__ import annotations

import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
MAP = REPO / "artifacts" / "agent_deprecation" / "w3_live_consumers.json"
ARTIFACT_DIR = REPO / "artifacts" / "agent_deprecation"

AUTH_DATE = "2026-04-24"
ELIG_DATE = "2026-07-23"
WAVE = "W3.2"

TARGETS = {
    "CostGovernorAgent": (
        "agentic_core/L5_safety/reasoning/CostGovernorAgent.py",
        "agentic_core.L5_safety.reasoning.CostGovernorAgent",
        "agentic_core.L5_safety.utils.cost_governor_util",
        "Only consumer was agentic_core/_compat/core/l5_safety_aliases.py "
        "(dead compat shim with zero importers). W3.2 edit removed the "
        "CostGovernorAgent entry from that shim. Remaining live consumer "
        "count: 0.",
    ),
    "GravityStateAgent": (
        "agentic_core/L3_orchestration/reasoning/GravityStateAgent.py",
        "agentic_core.L3_orchestration.reasoning.GravityStateAgent",
        "agentic_core.L3_orchestration.utils.gravity_state_util",
        "Only consumer was agentic_core/interfaces/state_agents.py (dead "
        "interface re-export with zero importers). W3.2 edit removed the "
        "GravityStateAgent entry + docstring note pointing callers at the "
        "gravity_state_util. Remaining live consumer count: 0.",
    ),
}

MARKER_TEMPLATE = """
AGENT-DELETION-AUTHORIZED: {auth} ({wave} of agent-deprecation-migration-d7a3f2)
Authorization date: {auth}
Archive-eligible date: {elig} (90-day cooling per constitutional \\u00a73)
Consumers at authorization: 0 ({evidence})
Unique logic: none (pure delegation to {util} per DEPRECATED docstring above).
Target archive path on or after eligibility date:
  archives/agents/{elig}/{archive_stem}.py
Cooling-timer artifact: artifacts/agent_deprecation/w3_{short}.json
"""


def insert_marker(path: pathlib.Path, marker: str) -> bool:
    text = path.read_text(encoding="utf-8")
    m = re.match(r'^(?:#[^\n]*\n)*("""|\'\'\')(.*?)(\1)', text, re.DOTALL)
    if not m:
        print(f"  [skip] no docstring: {path}", file=sys.stderr)
        return False
    if "AGENT-DELETION-AUTHORIZED" in m.group(2):
        print(f"  [skip] already authorized: {path}", file=sys.stderr)
        return False
    body = m.group(2).rstrip() + "\n" + marker.rstrip() + "\n"
    new_doc = m.group(1) + body + m.group(3)
    new_text = text[: m.start()] + new_doc + text[m.end() :]
    path.write_text(new_text, encoding="utf-8")
    return True


def main() -> int:
    done = 0
    for class_name, (rel, module_path, util, evidence) in TARGETS.items():
        abs_path = REPO / rel
        if not abs_path.exists():
            print(f"  [miss] {rel}")
            continue
        archive_stem = rel.replace("/", "__").replace(".py", "")
        short = pathlib.Path(rel).stem
        marker = MARKER_TEMPLATE.format(
            auth=AUTH_DATE,
            elig=ELIG_DATE,
            wave=WAVE,
            util=util,
            evidence=evidence,
            archive_stem=archive_stem,
            short=short,
        )
        if insert_marker(abs_path, marker):
            done += 1
            artifact = {
                "agent_name": class_name,
                "class_name": class_name,
                "file_path": rel,
                "category": "deprecated-delegating-shim",
                "canonical_replacement": util,
                "authorization_date": AUTH_DATE,
                "authorization_wave": WAVE,
                "authorization_plan": "agent-deprecation-migration-d7a3f2",
                "cooling_days": 90,
                "archive_eligible_date": ELIG_DATE,
                "archive_target_path": f"archives/agents/{ELIG_DATE}/{archive_stem}.py",
                "consumer_count_at_authorization": 0,
                "consumer_count_method": "regex grep after removing entries from dead compat shim",
                "consumer_count_evidence": evidence,
                "unique_logic": False,
                "unique_logic_evidence": (
                    "Pure delegation to canonical_replacement per DEPRECATED "
                    "docstring; class methods forward to utility functions"
                ),
                "status": "authorized_awaiting_cooling",
                "next_action": f"W6 archive sweep on or after {ELIG_DATE}",
            }
            (ARTIFACT_DIR / f"w3_{short}.json").write_text(json.dumps(artifact, indent=2), encoding="utf-8")
            print(f"  [ok] {rel}")
    print(f"[done] authorized {done}/{len(TARGETS)}")
    return 0 if done == len(TARGETS) else 1


if __name__ == "__main__":
    sys.exit(main())
