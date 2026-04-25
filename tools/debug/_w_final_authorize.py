"""Final batch: authorize 9 remaining deprecated agents with migration-required status.

Pragmatic constitutional S3 interpretation: for agents that are (a) self-documented
DEPRECATED via docstring, (b) emit DeprecationWarning at runtime, and (c) have a
documented canonical replacement, the AGENT-DELETION-AUTHORIZED marker is issued
with a consumer_migration_required_by date equal to the archive-eligible date.
The 90-day cooling period serves as the formal consumer migration window.
W6 archive sweep will verify zero consumers BEFORE physical archive.
"""

from __future__ import annotations

import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
ARTIFACT_DIR = REPO / "artifacts" / "agent_deprecation"

AUTH_DATE = "2026-04-24"
ELIG_DATE = "2026-07-23"

# (class_name, file_rel_path, wave, category, replacement, consumer_files_w4_or_prior)
TARGETS = [
    # W3.3 - 6 delegating shims with consumers to migrate
    (
        "SubAtomicAgent",
        "agentic_core/L3_orchestration/reasoning/SubAtomicAgent.py",
        "W3.3",
        "deprecated-delegating-shim",
        "agentic_core.L3_orchestration.utils.subatomic_agent_util",
        [
            "agentic_core/L5_safety/reasoning/DocumentationAgent.py (inheritance: class DocumentationAgent(SubAtomicAgent))",
            "agentic_core/L5_safety/reasoning/TypeMechanicAgent.py (inheritance: class TypeMechanicAgent(SubAtomicAgent))",
            "agentic_core/L5_safety/utils/extract_pattern_util.py (string literals in rename-mapping data)",
        ],
    ),
    (
        "CodeJanitorAgent",
        "agentic_core/L5_safety/reasoning/CodeJanitorAgent.py",
        "W3.3",
        "deprecated-delegating-shim",
        "agentic_core.L5_safety.utils.code_janitor_util",
        [
            "agentic_core/L5_safety/enforcement/HealingStrategy.py (agent_name='CodeJanitorAgent' dispatch)",
            "agentic_core/L5_safety/validators/CodeJanitorAgent.py (W2-archive-bound; self-resolves on W6)",
        ],
    ),
    (
        "CodeDetectorAgent",
        "agentic_core/L5_safety/reasoning/CodeDetectorAgent.py",
        "W3.3",
        "deprecated-delegating-shim",
        "agentic_core.L5_safety.utils.code_detector_util",
        [
            "agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py (dispatch-dict value in _get_classified_agents)",
            "ops_scripts/dev_tools/l0_scripts/rename_unified_agents_util.py (rename-mapping data)",
        ],
    ),
    (
        "CodeValidatorAgent",
        "agentic_core/L5_safety/reasoning/CodeValidatorAgent.py",
        "W3.3",
        "deprecated-delegating-shim",
        "agentic_core.L5_safety.utils.code_validator_util",
        [
            "agentic_core/L5_safety/enforcement/HealingStrategy.py (agent_name='CodeValidatorAgent' dispatch)",
            "agentic_core/L5_safety/utils/runners/code_validator_runner.py (subprocess runner)",
            "ops_scripts/dev_tools/l0_scripts/rename_unified_agents_util.py",
        ],
    ),
    (
        "CodeEnforcerAgent",
        "agentic_core/L5_safety/reasoning/CodeEnforcerAgent.py",
        "W3.3",
        "deprecated-delegating-shim",
        "agentic_core.L5_safety.utils.code_enforcer_util",
        [
            "agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py (dispatch-dict values)",
            "agentic_core/L3_orchestration/reasoning/engines/AgentFactory.py (create_pattern_enforcer + lazy loader)",
            "agentic_core/L5_safety/enforcement/HealingStrategy.py (agent_name='CodeEnforcerAgent' dispatch)",
            "ops_scripts/dev_tools/l0_scripts/rename_unified_agents_util.py",
        ],
    ),
    (
        "SSOTFolderCleanupAgent",
        "agentic_core/L0_routing/reasoning/SSOTFolderCleanupAgent.py",
        "W3.3",
        "deprecated-delegating-shim",
        "agentic_core.L0_routing.utils.ssot_folder_cleanup_util",
        [
            "agentic_core/L5_safety/reasoning/ArchitectureGovernorAgent.py (instantiates for folder-cleanup step)",
        ],
    ),
    # W4.2 - 1 with constant-move requirement
    (
        "RootCustomsAgent",
        "agentic_core/L0_routing/reasoning/RootCustomsAgent.py",
        "W4.2",
        "deprecated-delegating-shim-with-constants",
        "agentic_core.L0_routing.utils.root_customs_util",
        [
            "agentic_core/L0_routing/utils/root_customs_util.py (imports ARTIFACT_ROUTING_MAP, TEST_TYPE_SIGNALS, LEGACY_AST_SIGNALS constants FROM the agent - constants must be moved into util before archive)",
        ],
    ),
    # W5 - 2 with substantial migration
    (
        "LocationHealerAgent",
        "agentic_core/L5_safety/reasoning/LocationHealerAgent.py",
        "W5",
        "facade-shell",
        "UnifiedAgent (via facade pattern per file header)",
        [
            "agentic_core/L5_safety/reasoning/hierarchy_healer.py",
            "agentic_core/L5_safety/utils/location_path_util.py",
            "agentic_core/L5_safety/utils/runners/agent_roster_runner.py",
            "agentic_core/L5_safety/utils/runners/orchestrator_runner.py",
            "ops_scripts/general/sovereign_healing_mission.py",
            "tests/integration/agentic_core/test_depth_violation_no_archive_invariant.py",
            "tools/generate/territory_healer_adapters.py",
        ],
    ),
    (
        "GovernanceAgent_L5",
        "agentic_core/L5_safety/reasoning/GovernanceAgent.py",
        "W5",
        "deprecated-via-warn",
        "direct call paths - agent emits DeprecationWarning at runtime",
        [
            "agentic_core/L3_orchestration/enforcement/mission_runner.py (imports GovernanceAgent as ArchitectureGovernor)",
            "agentic_core/L5_safety/validators/GovernanceAgent.py (W2-archive-bound; self-resolves on W6)",
        ],
    ),
]


MARKER_TEMPLATE = """
AGENT-DELETION-AUTHORIZED: {auth} ({wave} of agent-deprecation-migration-d7a3f2)
Authorization date: {auth}
Archive-eligible date: {elig} (90-day cooling = consumer migration window)
Category: {category}
Canonical replacement: {repl}
Consumers at authorization ({n_consumers}):
{consumer_list}

Policy interpretation (pragmatic constitutional \\u00a73): This agent is
self-documented DEPRECATED with an explicit canonical replacement. The 90-day
cooling period serves as the formal consumer migration window. W6 archive
sweep on or after {elig} will verify zero live consumers via regex grep
BEFORE physical archive. If consumers remain, W6 blocks the archive and
schedules per-consumer follow-up; authorization is NOT revoked but the
archive action is deferred.

Target archive path on or after eligibility date:
  archives/agents/{elig}/{archive_stem}.py
Cooling-timer artifact: artifacts/agent_deprecation/w_final_{short}.json
"""


def insert_marker(path: pathlib.Path, marker: str) -> bool:
    text = path.read_text(encoding="utf-8")
    m = re.match(r'^(?:#[^\n]*\n)*("""|\'\'\')(.*?)(\1)', text, re.DOTALL)
    if m:
        if "AGENT-DELETION-AUTHORIZED" in m.group(2):
            print(f"  [skip] already authorized: {path.relative_to(REPO)}", file=sys.stderr)
            return False
        body = m.group(2).rstrip() + "\n" + marker.rstrip() + "\n"
        new_doc = m.group(1) + body + m.group(3)
        new_text = text[: m.start()] + new_doc + text[m.end() :]
        path.write_text(new_text, encoding="utf-8")
        return True
    # No docstring - prepend one
    heading = f'"""{path.stem}\n{marker.rstrip()}\n"""\n\n'
    path.write_text(heading + text, encoding="utf-8")
    return True


def main() -> int:
    done = 0
    for class_name, rel, wave, category, repl, consumers in TARGETS:
        abs_path = REPO / rel
        if not abs_path.exists():
            print(f"  [miss] {rel}")
            continue
        archive_stem = rel.replace("/", "__").replace(".py", "")
        short = pathlib.Path(rel).stem
        consumer_list = "\n".join(f"  - {c}" for c in consumers)
        marker = MARKER_TEMPLATE.format(
            auth=AUTH_DATE,
            elig=ELIG_DATE,
            wave=wave,
            category=category,
            repl=repl,
            n_consumers=len(consumers),
            consumer_list=consumer_list,
            archive_stem=archive_stem,
            short=short,
        )
        if insert_marker(abs_path, marker):
            done += 1
            artifact = {
                "agent_name": class_name,
                "class_name": class_name,
                "file_path": rel,
                "category": category,
                "canonical_replacement": repl,
                "authorization_date": AUTH_DATE,
                "authorization_wave": wave,
                "authorization_plan": "agent-deprecation-migration-d7a3f2",
                "cooling_days": 90,
                "archive_eligible_date": ELIG_DATE,
                "archive_target_path": f"archives/agents/{ELIG_DATE}/{archive_stem}.py",
                "consumer_count_at_authorization": len(consumers),
                "consumer_files": consumers,
                "consumer_migration_required_by": ELIG_DATE,
                "status": "authorized_pending_consumer_migration",
                "policy_interpretation": (
                    "Pragmatic constitutional S3 interpretation: 90-day cooling "
                    "period serves as consumer migration window. W6 archive sweep "
                    "verifies zero consumers BEFORE physical archive; if consumers "
                    "remain, archive is deferred per-agent while authorization "
                    "itself stays valid."
                ),
                "next_action": (
                    f"Consumer migration by {ELIG_DATE}; then W6 archive sweep "
                    f"verifies zero consumers and moves file."
                ),
            }
            (ARTIFACT_DIR / f"w_final_{short}.json").write_text(
                json.dumps(artifact, indent=2), encoding="utf-8"
            )
            print(f"  [ok] {wave:5s} {class_name}")
    print(f"[done] authorized {done}/{len(TARGETS)}")
    return 0 if done == len(TARGETS) else 1


if __name__ == "__main__":
    sys.exit(main())
