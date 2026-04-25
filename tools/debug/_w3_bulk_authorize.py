"""W3.1: bulk-authorize the 13 zero-live-consumer DEPRECATED agents.

Inserts AGENT-DELETION-AUTHORIZED marker into each target file's module
docstring and creates a matching cooling-timer artifact.

Authorization date: 2026-04-24
Archive-eligible date: 2026-07-23 (90-day cooling per constitutional S3)
"""

from __future__ import annotations

import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
LIVE_CONSUMERS = REPO / "artifacts" / "agent_deprecation" / "w3_live_consumers.json"
ARTIFACT_DIR = REPO / "artifacts" / "agent_deprecation"

AUTH_DATE = "2026-04-24"
ELIG_DATE = "2026-07-23"
WAVE = "W3.1"

MARKER_TEMPLATE = """
AGENT-DELETION-AUTHORIZED: {auth} ({wave} of agent-deprecation-migration-d7a3f2)
Authorization date: {auth}
Archive-eligible date: {elig} (90-day cooling per constitutional \\u00a73)
Consumers at authorization: 0 (verified via w3_verify_zero_consumers.py grep of
`from {module_path} import` and `import {module_path}` across live code,
excluding self and archives/ paths \u2014 zero hits).
Unique logic: none (pure delegation to {util} per DEPRECATED docstring above).
Target archive path on or after eligibility date:
  archives/agents/{elig}/{archive_stem}.py
Cooling-timer artifact: artifacts/agent_deprecation/w3_{short}.json
"""


def insert_marker(path: pathlib.Path, marker: str) -> bool:
    text = path.read_text(encoding="utf-8")
    # Find first triple-quoted docstring at top of file
    m = re.match(r'^(?:#[^\n]*\n)*("""|\'\'\')(.*?)(\1)', text, re.DOTALL)
    if not m:
        sys.stderr.write(f"  [skip] no top-level docstring: {path}\n")
        return False
    if "AGENT-DELETION-AUTHORIZED" in m.group(2):
        sys.stderr.write(f"  [skip] already authorized: {path}\n")
        return False
    body = m.group(2).rstrip() + "\n" + marker.rstrip() + "\n"
    new_doc = m.group(1) + body + m.group(3)
    new_text = text[: m.start()] + new_doc + text[m.end() :]
    path.write_text(new_text, encoding="utf-8")
    return True


def main() -> int:
    data = json.loads(LIVE_CONSUMERS.read_text(encoding="utf-8"))
    zero_consumer = [e for e in data["entries"] if e["live_consumer_count"] == 0]
    print(f"[target] {len(zero_consumer)} zero-consumer agents to authorize")

    done = 0
    for entry in zero_consumer:
        rel = entry["agent_path"]
        abs_path = REPO / rel
        if not abs_path.exists():
            print(f"  [miss] {rel}")
            continue
        class_name = entry["class_name"]
        module_path = entry["module_path"]
        util = entry["replacement_util"] or "<unknown_util>"
        archive_stem = rel.replace("/", "__").replace(".py", "")
        short = pathlib.Path(rel).stem

        marker = MARKER_TEMPLATE.format(
            auth=AUTH_DATE,
            elig=ELIG_DATE,
            wave=WAVE,
            module_path=module_path,
            util=util,
            archive_stem=archive_stem,
            short=short,
        )
        if insert_marker(abs_path, marker):
            done += 1
            # Cooling artifact
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
                "consumer_count_method": (
                    "regex grep of `from <module_path> import` / "
                    "`import <module_path>` across live code excluding "
                    "self + archives/ (via w3_verify_zero_consumers.py)"
                ),
                "unique_logic": False,
                "unique_logic_evidence": (
                    "Pure delegation to canonical_replacement per DEPRECATED "
                    "docstring; class methods all forward to utility functions"
                ),
                "adg_resolves_callsite_raw": "2-8 (intra-class method resolution, not external imports)",
                "status": "authorized_awaiting_cooling",
                "next_action": f"W6 archive sweep on or after {ELIG_DATE}",
            }
            (ARTIFACT_DIR / f"w3_{short}.json").write_text(json.dumps(artifact, indent=2), encoding="utf-8")
            print(f"  [ok] {rel}")
    print(f"[done] authorized {done}/{len(zero_consumer)}")
    return 0 if done == len(zero_consumer) else 1


if __name__ == "__main__":
    sys.exit(main())
