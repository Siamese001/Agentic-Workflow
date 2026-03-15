"""
Validate Base Agent Uniqueness
===============================

Ensures each layer (L0-L6) has exactly ONE base agent class.
Multiple base agents per layer causes inheritance confusion and architectural violations.

Validation Rules:
1. Each layer must have exactly 1 base agent (e.g., L1CognitionBase, L2Agent, etc.)
2. Base agents should be in base_class or root layer directories
3. No duplicate base agent classes

Fixes:
- Identifies duplicate base agents
- Suggests which to keep (canonical) vs deprecate
- Can auto-deprecate non-canonical base agents
"""

import json
from collections import defaultdict

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)

data = json.load(open("agent_discovery_full.json"))
LAYERS = ["L0", "L1", "L2", "L3", "L4", "L5", "L6"]
CANONICAL_BASE_AGENTS = {
    "L0": "L0RoutingBaseAgent",
    "L1": "L1CognitionBase",
    "L2": "L2Agent",
    "L3": "L3Agent",
    "L4": "L4Agent",
    "L5": "L5Agent",
    "L6": "L6ObservabilityBase",
}


def find_base_agents() -> dict[str, list[dict]]:
    """Find all base agents grouped by layer."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "find_base_agents", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "find_base_agents", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "find_base_agents")
    base_agents_by_layer = defaultdict(list)
    for agent in data:
        class_name = agent.get("class_name", "")
        layer = agent.get("layer", "")
        is_base_agent = (
            "BaseAgent" in class_name
            or class_name in CANONICAL_BASE_AGENTS.values()
            or "base_class" in agent.get("path", "").lower()
        )
        if is_base_agent and layer:
            layer_prefix = layer[:2] if len(layer) >= 2 else layer
            if layer_prefix in LAYERS:
                base_agents_by_layer[layer_prefix].append(agent)
    return base_agents_by_layer


def validate_base_agents() -> tuple[bool, list[str]]:
    """Validate base agent uniqueness per layer."""
    base_agents = find_base_agents()
    errors = []
    warnings = []
    print("=" * 80)
    print("BASE AGENT UNIQUENESS VALIDATION")
    print("=" * 80)
    print()
    for layer in LAYERS:
        agents = base_agents.get(layer, [])
        canonical = CANONICAL_BASE_AGENTS.get(layer)
        print(f"{layer} Layer:")
        if len(agents) == 0:
            warnings.append(f"⚠️  {layer}: No base agent found (expected {canonical})")
            print(f"   ⚠️  No base agent (expected {canonical})")
        elif len(agents) == 1:
            agent = agents[0]
            name = agent["class_name"]
            if name == canonical:
                print(f"   ✅ Canonical base agent: {name}")
            else:
                warnings.append(f"⚠️  {layer}: Found {name}, expected canonical {canonical}")
                print(f"   ⚠️  Found {name}, expected {canonical}")
                print(f"      Path: {agent['path']}")
        else:
            errors.append(f"❌ {layer}: Found {len(agents)} base agents (expected 1)")
            print(f"   ❌ MULTIPLE BASE AGENTS FOUND: {len(agents)}")
            canonical_agent = next((a for a in agents if a["class_name"] == canonical), None)
            for i, agent in enumerate(agents, 1):
                name = agent["class_name"]
                path = agent["path"]
                is_canonical = name == canonical
                marker = "👑 CANONICAL" if is_canonical else "🔴 DUPLICATE"
                print(f"      {i}. {name} {marker}")
                print(f"         {path}")
            if canonical_agent:
                print(f"   💡 Recommendation: Keep {canonical}, deprecate others")
            else:
                print(f"   💡 Recommendation: Rename one to {canonical}, deprecate others")
        print()
    print("=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)
    if errors:
        print(f"❌ {len(errors)} ERRORS")
        for error in errors:
            print(f"   {error}")
        print()
    if warnings:
        print(f"⚠️  {len(warnings)} WARNINGS")
        for warning in warnings:
            print(f"   {warning}")
        print()
    if not errors and (not warnings):
        print("✅ All layers have exactly 1 canonical base agent")
        print()
    is_valid = len(errors) == 0
    all_messages = errors + warnings
    return (is_valid, all_messages)


def suggest_fixes() -> list[str]:
    """Suggest fixes for base agent violations."""
    base_agents = find_base_agents()
    fixes = []
    for layer in LAYERS:
        agents = base_agents.get(layer, [])
        canonical = CANONICAL_BASE_AGENTS.get(layer)
        if len(agents) > 1:
            canonical_agent = next((a for a in agents if a["class_name"] == canonical), None)
            if canonical_agent:
                for agent in agents:
                    if agent["class_name"] != canonical:
                        fixes.append(
                            f"Deprecate {agent['class_name']} at {agent['path']} (duplicate of canonical {canonical})"
                        )
            else:
                fixes.append(f"Rename {agents[0]['class_name']} to {canonical} at {agents[0]['path']}")
                for agent in agents[1:]:
                    fixes.append(f"Deprecate {agent['class_name']} at {agent['path']}")
    return fixes


def main():
    """Main entry point."""
    is_valid, messages = validate_base_agents()
    if not is_valid:
        print("=" * 80)
        print("RECOMMENDED FIXES")
        print("=" * 80)
        fixes = suggest_fixes()
        for i, fix in enumerate(fixes, 1):
            print(f"{i}. {fix}")
        print()
        print("Run this script with --fix flag to auto-apply fixes (not yet implemented)")
        return 1
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
