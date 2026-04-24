"""W4.1: authorize 3 zero-consumer medium-fan-in DEPRECATED agents."""
from __future__ import annotations

import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
ARTIFACT_DIR = REPO / "artifacts" / "agent_deprecation"

AUTH_DATE = "2026-04-24"
ELIG_DATE = "2026-07-23"
WAVE = "W4.1"

TARGETS = {
    "StructureHealerAgent": (
        "agentic_core/L5_safety/reasoning/StructureHealerAgent.py",
        "UnifiedAgent with StructuralHealerStrategy (facade pattern per file header)",
        "Zero live consumers verified via regex grep of live code (self+archives excluded). File is a Facade Shell delegating to UnifiedAgent.",
    ),
    "RedSentinelAgent": (
        "agentic_core/L5_safety/reasoning/RedSentinelAgent.py",
        "agentic_core.L5_safety.reasoning directly (no util replacement - hostile-input generator is retained; this shim re-export is removed)",
        "Only live consumer was agentic_core/_compat/core/l5_safety_aliases.py (dead compat re-export with zero external importers). W4.1 edit removed the RedSentinelAgent entry from that shim.",
    ),
    "AutonomyGuardianAgent": (
        "agentic_core/L5_safety/reasoning/AutonomyGuardianAgent.py",
        "agentic_core.L5_safety.reasoning directly (real agent, this shim re-export is removed)",
        "Only live consumer was agentic_core/_compat/core/l5_safety_aliases.py (dead compat re-export with zero external importers). W4.1 edit removed the AutonomyGuardianAgent entry.",
    ),
}

MARKER_TEMPLATE = """
AGENT-DELETION-AUTHORIZED: {auth} ({wave} of agent-deprecation-migration-d7a3f2)
Authorization date: {auth}
Archive-eligible date: {elig} (90-day cooling per constitutional \\u00a73)
Consumers at authorization: 0 ({evidence})
Canonical replacement / next step: {repl}
Target archive path on or after eligibility date:
  archives/agents/{elig}/{archive_stem}.py
Cooling-timer artifact: artifacts/agent_deprecation/w4_{short}.json
"""


def insert_marker(path: pathlib.Path, marker: str) -> bool:
    text = path.read_text(encoding="utf-8")
    m = re.match(r'^(?:#[^\n]*\n)*("""|\'\'\')(.*?)(\1)', text, re.DOTALL)
    if not m:
        sys.stderr.write(f"  [skip] no docstring: {path}\n")
        return False
    if "AGENT-DELETION-AUTHORIZED" in m.group(2):
        sys.stderr.write(f"  [skip] already authorized: {path}\n")
        return False
    body = m.group(2).rstrip() + "\n" + marker.rstrip() + "\n"
    new_doc = m.group(1) + body + m.group(3)
    new_text = text[: m.start()] + new_doc + text[m.end():]
    path.write_text(new_text, encoding="utf-8")
    return True


def main() -> int:
    done = 0
    for class_name, (rel, repl, evidence) in TARGETS.items():
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
            repl=repl,
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
                "category": "deprecated-agent",
                "canonical_replacement": repl,
                "authorization_date": AUTH_DATE,
                "authorization_wave": WAVE,
                "authorization_plan": "agent-deprecation-migration-d7a3f2",
                "cooling_days": 90,
                "archive_eligible_date": ELIG_DATE,
                "archive_target_path": f"archives/agents/{ELIG_DATE}/{archive_stem}.py",
                "consumer_count_at_authorization": 0,
                "consumer_count_evidence": evidence,
                "status": "authorized_awaiting_cooling",
                "next_action": f"W6 archive sweep on or after {ELIG_DATE}",
            }
            (ARTIFACT_DIR / f"w4_{short}.json").write_text(
                json.dumps(artifact, indent=2), encoding="utf-8"
            )
            print(f"  [ok] {rel}")
    print(f"[done] authorized {done}/{len(TARGETS)}")
    return 0 if done == len(TARGETS) else 1


if __name__ == "__main__":
    sys.exit(main())
