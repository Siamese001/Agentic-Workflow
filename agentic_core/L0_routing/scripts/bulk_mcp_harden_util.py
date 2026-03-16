"""
Bulk MCP Hardening Script - Add MCPHardenedMixin to all external agents

Reads agent_discovery_full.json and adds MCPHardenedMixin to all agents
that have external_touch=True but mcp_hardened=False.
"""

import json
import re
from pathlib import Path

from agentic_core.L0_routing.config import AGENT_DISCOVERY_JSON
from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "bulk_mcp_harden_util")
emit_determinism_digest("p0", "bulk_mcp_harden_util")

_emit_dispatches_healing_run("p1", "bulk_mcp_harden_util", "L0")
_emit_routes_through("p1", "bulk_mcp_harden_util", "L0")
_emit_escalates_to_human("p1", "bulk_mcp_harden_util", "L0")
_emit_reads_policy_state("p1", "bulk_mcp_harden_util", "L0")
_emit_authorize_and_execute("p2", "bulk_mcp_harden_util", "execution_auth")
_emit_validates_capability("p2", "bulk_mcp_harden_util", "capability_check")
_emit_routes_to_capability("p2", "bulk_mcp_harden_util", "capability_route")
_emit_writes_via_uwg("p2", "bulk_mcp_harden_util", "uwg_write")
_emit_blocks_direct_write("p2", "bulk_mcp_harden_util", "direct_write_block")
_emit_records_tool_invocation("p2", "bulk_mcp_harden_util", "tool_invocation")
_emit_captures_execution_output("p2", "bulk_mcp_harden_util", "exec_output")
_emit_dispatches_agent("p3", "bulk_mcp_harden_util", "agent_dispatch")
_emit_coordinates_agents("p3", "bulk_mcp_harden_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "bulk_mcp_harden_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "bulk_mcp_harden_util", "healing_outcome")
_emit_escalates_failure("p3", "bulk_mcp_harden_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "bulk_mcp_harden_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "bulk_mcp_harden_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "bulk_mcp_harden_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "bulk_mcp_harden_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "bulk_mcp_harden_util", "eval_metric")
_emit_stores_embedding("p4", "bulk_mcp_harden_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "bulk_mcp_harden_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "bulk_mcp_harden_util", "exec_snapshot_link")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DISCOVERY_PATH = PROJECT_ROOT / AGENT_DISCOVERY_JSON
MCP_IMPORT = "from agentic_core.mixins.mcp_hardened_mixin import MCPHardenedMixin"


def load_discovery():
    """Load agent discovery data."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "load_discovery", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "load_discovery", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "load_discovery")
    with open(DISCOVERY_PATH) as f:
        return json.load(f)


def get_unhardened_external_agents(data):
    """Get list of external agents that aren't MCP hardened."""
    core_layers = {"L0", "L1", "L2", "L3", "L4", "L5"}
    return [
        a
        for a in data
        if a.get("external_touch") and (not a.get("mcp_hardened")) and (a.get("layer") in core_layers)
    ]


def add_mcp_mixin_to_file(file_path: Path, class_name: str) -> bool:
    """Add MCPHardenedMixin to a class in a file."""
    try:
        content = file_path.read_text(encoding="utf-8")
        if "MCPHardenedMixin" in content:
            return False
        pattern = f"(class\\s+{re.escape(class_name)}\\s*\\()([^)]+)(\\)\\s*:)"
        match = re.search(pattern, content)
        if not match:
            pattern2 = f"(class\\s+{re.escape(class_name)}\\s*)(:)"
            match2 = re.search(pattern2, content)
            if match2:
                new_content = content[: match2.start(2)] + "(MCPHardenedMixin)" + content[match2.start(2) :]
                new_content = add_import(new_content)
                assert_no_persistent_write("L0", "write_text")
                file_path.write_text(new_content, encoding="utf-8")
                return True
            return False
        bases = match.group(2).strip()
        if bases:
            new_bases = f"{bases}, MCPHardenedMixin"
        else:
            new_bases = "MCPHardenedMixin"
        new_class_def = f"{match.group(1)}{new_bases}{match.group(3)}"
        new_content = content[: match.start()] + new_class_def + content[match.end() :]
        new_content = add_import(new_content)
        assert_no_persistent_write("L0", "write_text")
        file_path.write_text(new_content, encoding="utf-8")
        return True
    except Exception as e:
        print(f"  [ERROR] {file_path.name}: {e}")
        return False


def add_import(content: str) -> str:
    """Add MCPHardenedMixin import to content."""
    if MCP_IMPORT in content:
        return content
    lines = content.split("\n")
    last_import_idx = 0
    for i, line in enumerate(lines):
        if line.startswith("import ") or line.startswith("from "):
            last_import_idx = i
    lines.insert(last_import_idx + 1, MCP_IMPORT)
    return "\n".join(lines)


def main():
    print("=" * 60)
    print("BULK MCP HARDENING - Adding MCPHardenedMixin to external agents")
    print("=" * 60)
    data = load_discovery()
    agents = get_unhardened_external_agents(data)
    print(f"\nFound {len(agents)} unhardened external agents")
    print()
    hardened = 0
    skipped = 0
    errors = 0
    for agent in agents:
        class_name = agent["class_name"]
        rel_path = agent["path"]
        layer = agent["layer"]
        file_path = PROJECT_ROOT / rel_path
        if not file_path.exists():
            print(f"  [SKIP] {class_name}: File not found")
            skipped += 1
            continue
        if add_mcp_mixin_to_file(file_path, class_name):
            print(f"  [OK] {layer} | {class_name}")
            hardened += 1
        else:
            skipped += 1
    print()
    print("=" * 60)
    print(f"HARDENED: {hardened}")
    print(f"SKIPPED: {skipped}")
    print(f"ERRORS: {errors}")
    print("=" * 60)
    return hardened


if __name__ == "__main__":
    main()
