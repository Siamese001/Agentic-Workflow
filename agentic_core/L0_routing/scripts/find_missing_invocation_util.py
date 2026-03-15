"""Find agents missing super().heal_repository() invocation."""

import json
import re
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

_emit_dispatches_healing_run("p1", "find_missing_invocation_util", "L0")
_emit_routes_through("p1", "find_missing_invocation_util", "L0")
_emit_escalates_to_human("p1", "find_missing_invocation_util", "L0")
_emit_reads_policy_state("p1", "find_missing_invocation_util", "L0")

_emit_records_execution_trace("p0", "evidence", "find_missing_invocation_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "find_missing_invocation_util", "p0_governance")
_emit_snapshots_state("p0", "find_missing_invocation_util", "state_snapshot")

PROJECT_ROOT = Path(__file__).parent.parent
dashboard_path = PROJECT_ROOT / REPORTS_DIR / "autonomy_dashboard.html"
content = dashboard_path.read_text(encoding="utf-8")
match = re.search("const agentDataByTerritory\\s*=\\s*(\\{.*?\\});", content, re.DOTALL)
if match:
    try:
        agent_data = json.loads(match.group(1))
        print(f"Found agentDataByTerritory with {len(agent_data)} territories")
        total_agents = 0
        invocation_yes = 0
        invocation_no = 0
        invocation_inherited = 0
        missing_invocation_agents = []
        for territory, agents in agent_data.items():
            for agent in agents:
                total_agents += 1
                inv = agent.get("invocation", "")
                name = agent.get("name", "Unknown")
                path = agent.get("path", "")
                if inv == "Yes":
                    invocation_yes += 1
                elif inv == "Inherited":
                    invocation_inherited += 1
                else:
                    invocation_no += 1
                    missing_invocation_agents.append({"name": name, "path": path, "territory": territory})
        print(f"\nTotal agents: {total_agents}")
        print(f"Invocation Yes: {invocation_yes}")
        print(f"Invocation Inherited: {invocation_inherited}")
        print(f"Invocation No/Missing: {invocation_no}")
        print(f"Invocation %: {(invocation_yes + invocation_inherited) / total_agents * 100:.1f}%")
        print(f"\n=== Agents MISSING invocation ({len(missing_invocation_agents)}) ===")
        for agent in sorted(missing_invocation_agents, key=lambda x: x["path"]):
            print(f"  {agent['path']}")
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
else:
    print("Could not find agentDataByTerritory in dashboard")
    all_invocations = re.findall('"invocation":\\s*"([^"]*)"', content)
    print(f"\nFound {len(all_invocations)} invocation values via regex")
    from collections import Counter

    print(Counter(all_invocations))
    for line in content.split("\n"):
        if '"invocation": "No (missing super)"' in line and len(line) > 10000:
            agent_pattern = '\\{"name":\\s*"([^"]+)"[^}]*"path":\\s*"([^"]+)"[^}]*"invocation":\\s*"([^"]+)"'
            matches = re.findall(agent_pattern, line)
            missing_paths = []
            for name, path, inv in matches:
                if "No" in inv or "missing" in inv:
                    missing_paths.append(path)
            print(f"\n=== Files needing super().heal_repository() ({len(missing_paths)}) ===")
            for path in sorted(set(missing_paths)):
                print(path)
            break
