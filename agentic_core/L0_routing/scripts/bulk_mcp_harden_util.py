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
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)

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
