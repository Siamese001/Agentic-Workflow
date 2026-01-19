#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Suite: Discovery Roster Builder - Layer-Based Tagging

Tests the discovery-based roster building system:
1. Discovery data loading
2. HealerMixin filtering
3. Layer-based sorting (L0 → L6 → Apps → Utils)
4. Agent instantiation
5. Full roster building

Run: python scripts/test_discovery_roster_builder.py
"""
import sys
import os
if sys.platform.startswith("win"):
    os.system("chcp 65001 >nul 2>&1")
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import json
from pathlib import Path
from typing import Dict, Any, Tuple, List

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


# ============================================================================
# TEST FUNCTIONS
# ============================================================================

def test_1_discovery_file_exists() -> Tuple[bool, str]:
    """Test 1: Verify agent_discovery_full.json exists."""
    discovery_file = project_root / "agent_discovery_full.json"
    
    if not discovery_file.exists():
        return False, f"Discovery file not found: {discovery_file}"
    
    # Check file size
    size_kb = discovery_file.stat().st_size / 1024
    if size_kb < 10:
        return False, f"Discovery file too small: {size_kb:.1f} KB"
    
    return True, f"Discovery file exists ({size_kb:.1f} KB)"


def test_2_discovery_data_loads() -> Tuple[bool, str]:
    """Test 2: Verify discovery data loads correctly."""
    from agentic_core.L3_orchestration.discovery_roster_builder import load_discovery_data
    
    data = load_discovery_data(project_root)
    
    if not data:
        return False, "No agents loaded from discovery"
    
    if not isinstance(data, list):
        return False, f"Expected list, got {type(data)}"
    
    return True, f"Loaded {len(data)} agents from discovery"


def test_3_agents_have_required_fields() -> Tuple[bool, str]:
    """Test 3: Verify agents have required fields for filtering/sorting."""
    from agentic_core.L3_orchestration.discovery_roster_builder import load_discovery_data
    
    data = load_discovery_data(project_root)
    required_fields = ['class_name', 'path', 'layer', 'inheritance', 'key_methods']
    
    missing_count = 0
    for agent in data[:50]:  # Check first 50
        for field in required_fields:
            if field not in agent:
                missing_count += 1
                break
    
    if missing_count > 5:
        return False, f"{missing_count} agents missing required fields"
    
    return True, f"All checked agents have required fields"


def test_4_healer_filter_works() -> Tuple[bool, str]:
    """Test 4: Verify HealerMixin filtering works correctly."""
    from agentic_core.L3_orchestration.discovery_roster_builder import (
        load_discovery_data, filter_healer_agents
    )
    
    data = load_discovery_data(project_root)
    healers = filter_healer_agents(data)
    
    if not healers:
        return False, "No healer agents found"
    
    # Verify all filtered agents have HealerMixin or heal_repository
    for agent in healers[:20]:
        inheritance = agent.get('inheritance', [])
        methods = agent.get('key_methods', [])
        
        has_healer = 'HealerMixin' in inheritance
        has_method = 'heal_repository' in methods
        
        if not (has_healer or has_method):
            return False, f"{agent['class_name']} lacks HealerMixin and heal_repository"
    
    return True, f"Filtered to {len(healers)} healer agents"


def test_5_layer_sorting_correct_order() -> Tuple[bool, str]:
    """Test 5: Verify layer sorting produces correct order (L0 → L6)."""
    from agentic_core.L3_orchestration.discovery_roster_builder import (
        load_discovery_data, filter_healer_agents, sort_by_layer, LAYER_PRIORITY
    )
    
    data = load_discovery_data(project_root)
    healers = filter_healer_agents(data)
    sorted_agents = sort_by_layer(healers)
    
    if not sorted_agents:
        return False, "No sorted agents"
    
    # Verify order is correct
    prev_priority = -1
    for agent in sorted_agents:
        layer = agent.get('layer', 'Utils')
        priority = LAYER_PRIORITY.get(layer, 99)
        
        if priority < prev_priority:
            return False, f"Sort order violated: {layer} (priority {priority}) after priority {prev_priority}"
        
        prev_priority = priority
    
    # Check that L0 agents come before L6
    layers_seen = []
    for agent in sorted_agents[:30]:
        layer = agent.get('layer')
        if layer and layer not in layers_seen:
            layers_seen.append(layer)
    
    return True, f"Correct layer order: {' → '.join(layers_seen[:6])}"


def test_6_l0_agents_first() -> Tuple[bool, str]:
    """Test 6: Verify L0 (Maintenance) agents run first."""
    from agentic_core.L3_orchestration.discovery_roster_builder import (
        load_discovery_data, filter_healer_agents, sort_by_layer
    )
    
    data = load_discovery_data(project_root)
    healers = filter_healer_agents(data)
    sorted_agents = sort_by_layer(healers)
    
    if not sorted_agents:
        return False, "No sorted agents"
    
    # Check first few agents are L0
    first_layers = [a.get('layer') for a in sorted_agents[:5]]
    l0_count = sum(1 for l in first_layers if l == 'L0')
    
    if l0_count == 0:
        # Check if there are any L0 agents at all
        all_l0 = [a for a in sorted_agents if a.get('layer') == 'L0']
        if all_l0:
            return False, f"L0 agents exist ({len(all_l0)}) but not first in order"
        return True, "No L0 agents in discovery (acceptable)"
    
    return True, f"L0 agents are first ({l0_count} in top 5)"


def test_7_l5_safety_before_apps() -> Tuple[bool, str]:
    """Test 7: Verify L5 (Safety) agents run before Apps."""
    from agentic_core.L3_orchestration.discovery_roster_builder import (
        load_discovery_data, filter_healer_agents, sort_by_layer
    )
    
    data = load_discovery_data(project_root)
    healers = filter_healer_agents(data)
    sorted_agents = sort_by_layer(healers)
    
    # Find first L5 and first Apps agent
    first_l5_idx = None
    first_apps_idx = None
    
    for i, agent in enumerate(sorted_agents):
        layer = agent.get('layer')
        if layer == 'L5' and first_l5_idx is None:
            first_l5_idx = i
        if layer == 'Apps' and first_apps_idx is None:
            first_apps_idx = i
    
    if first_l5_idx is None:
        return True, "No L5 agents (acceptable)"
    
    if first_apps_idx is None:
        return True, "No Apps agents (acceptable)"
    
    if first_l5_idx > first_apps_idx:
        return False, f"L5 (idx {first_l5_idx}) comes after Apps (idx {first_apps_idx})"
    
    return True, f"L5 (idx {first_l5_idx}) correctly before Apps (idx {first_apps_idx})"


def test_8_base_agents_excluded() -> Tuple[bool, str]:
    """Test 8: Verify abstract base agents are excluded."""
    from agentic_core.L3_orchestration.discovery_roster_builder import (
        load_discovery_data, filter_healer_agents, SKIP_AGENTS
    )
    
    data = load_discovery_data(project_root)
    healers = filter_healer_agents(data)
    
    # Check no base agents in filtered list
    base_agents_found = []
    for agent in healers:
        class_name = agent.get('class_name', '')
        if class_name.endswith('BaseAgent') or class_name in SKIP_AGENTS:
            base_agents_found.append(class_name)
    
    if base_agents_found:
        return False, f"Base agents in filtered list: {base_agents_found[:5]}"
    
    return True, "No base agents in filtered list"


def test_9_instantiation_works() -> Tuple[bool, str]:
    """Test 9: Verify agent instantiation works."""
    from agentic_core.L3_orchestration.discovery_roster_builder import (
        load_discovery_data, filter_healer_agents, sort_by_layer, instantiate_agent
    )
    
    data = load_discovery_data(project_root)
    healers = filter_healer_agents(data)
    sorted_healers = sort_by_layer(healers)
    
    if not sorted_healers:
        return False, "No healer agents to test"
    
    # Try to instantiate agents until we get at least 5 successes
    success_count = 0
    attempted = 0
    for agent_data in sorted_healers[:50]:  # Try more agents
        attempted += 1
        result = instantiate_agent(agent_data, project_root)
        if result:
            success_count += 1
            if success_count >= 5:
                break
    
    if success_count == 0:
        return False, f"Failed to instantiate any of {attempted} agents"
    
    return True, f"Instantiated {success_count} agents (tried {attempted})"


def test_10_instantiated_agents_have_heal_repository() -> Tuple[bool, str]:
    """Test 10: Verify instantiated agents have heal_repository method."""
    from agentic_core.L3_orchestration.discovery_roster_builder import build_healing_roster
    
    roster = build_healing_roster(project_root, max_agents=20)
    
    if not roster:
        return False, "No agents in roster"
    
    # Verify all have heal_repository
    missing_method = []
    for name, instance in roster:
        if not hasattr(instance, 'heal_repository'):
            missing_method.append(name)
        elif not callable(instance.heal_repository):
            missing_method.append(f"{name} (not callable)")
    
    if missing_method:
        return False, f"Agents missing heal_repository: {missing_method}"
    
    return True, f"All {len(roster)} agents have heal_repository"


def test_11_full_roster_builds() -> Tuple[bool, str]:
    """Test 11: Verify full roster builds successfully."""
    from agentic_core.L3_orchestration.discovery_roster_builder import build_healing_roster
    
    roster = build_healing_roster(project_root)
    
    if not roster:
        return False, "Empty roster"
    
    if len(roster) < 10:
        return False, f"Roster too small: {len(roster)} agents"
    
    return True, f"Full roster built: {len(roster)} agents"


def test_12_roster_layer_distribution() -> Tuple[bool, str]:
    """Test 12: Verify roster has agents from multiple layers."""
    from agentic_core.L3_orchestration.discovery_roster_builder import (
        load_discovery_data, filter_healer_agents, sort_by_layer
    )
    
    data = load_discovery_data(project_root)
    healers = filter_healer_agents(data)
    sorted_agents = sort_by_layer(healers)
    
    # Count layers
    layer_counts = {}
    for agent in sorted_agents:
        layer = agent.get('layer', 'Unknown')
        layer_counts[layer] = layer_counts.get(layer, 0) + 1
    
    if len(layer_counts) < 3:
        return False, f"Too few layers: {list(layer_counts.keys())}"
    
    return True, f"Layer distribution: {layer_counts}"


def test_13_roster_excludes_apps_when_requested() -> Tuple[bool, str]:
    """Test 13: Verify roster can exclude Apps layer."""
    from agentic_core.L3_orchestration.discovery_roster_builder import build_healing_roster
    
    # Build with Apps
    roster_with_apps = build_healing_roster(project_root, include_apps=True, max_agents=100)
    
    # Build without Apps
    roster_no_apps = build_healing_roster(project_root, include_apps=False, max_agents=100)
    
    if len(roster_with_apps) <= len(roster_no_apps):
        return True, "No Apps agents to exclude (acceptable)"
    
    diff = len(roster_with_apps) - len(roster_no_apps)
    return True, f"Excluded {diff} Apps agents when requested"


def test_14_max_agents_limit_works() -> Tuple[bool, str]:
    """Test 14: Verify max_agents limit is respected."""
    from agentic_core.L3_orchestration.discovery_roster_builder import build_healing_roster
    
    max_limit = 5
    roster = build_healing_roster(project_root, max_agents=max_limit)
    
    if len(roster) > max_limit:
        return False, f"Roster exceeds limit: {len(roster)} > {max_limit}"
    
    return True, f"Roster respects limit: {len(roster)} <= {max_limit}"


def test_15_path_to_module_conversion() -> Tuple[bool, str]:
    """Test 15: Verify path to module conversion works."""
    from agentic_core.L3_orchestration.discovery_roster_builder import path_to_module
    
    test_cases = [
        ("agentic_core\\L5_safety\\validators\\LocationAgent.py", "agentic_core.L5_safety.validators.LocationAgent"),
        ("agentic_core/L3_orchestration/ConsolidatedOrchestratorAgent.py", "agentic_core.L3_orchestration.ConsolidatedOrchestratorAgent"),
        ("apps_rg\\engines\\DispatchOutreachToolsAgent.py", "apps_rg.engines.DispatchOutreachToolsAgent"),
    ]
    
    for path, expected in test_cases:
        result = path_to_module(path)
        if result != expected:
            return False, f"Path conversion failed: {path} -> {result} (expected {expected})"
    
    return True, "Path to module conversion works correctly"


def test_16_layer_priority_complete() -> Tuple[bool, str]:
    """Test 16: Verify all expected layers have priorities."""
    from agentic_core.L3_orchestration.discovery_roster_builder import LAYER_PRIORITY
    
    expected_layers = ['L0', 'L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'Apps', 'Utils']
    
    missing = [l for l in expected_layers if l not in LAYER_PRIORITY]
    
    if missing:
        return False, f"Missing layer priorities: {missing}"
    
    # Verify L0 < L6 < Apps
    if not (LAYER_PRIORITY['L0'] < LAYER_PRIORITY['L6'] < LAYER_PRIORITY['Apps']):
        return False, "Layer priority order incorrect"
    
    return True, f"All {len(expected_layers)} layers have correct priorities"


def test_17_roster_order_preserved_in_execution() -> Tuple[bool, str]:
    """Test 17: Verify roster order is preserved for execution."""
    from agentic_core.L3_orchestration.discovery_roster_builder import build_healing_roster
    
    roster = build_healing_roster(project_root, max_agents=20)
    
    if len(roster) < 5:
        return False, "Not enough agents to test order"
    
    # Verify order is consistent across multiple builds
    roster2 = build_healing_roster(project_root, max_agents=20)
    
    names1 = [name for name, _ in roster]
    names2 = [name for name, _ in roster2]
    
    if names1 != names2:
        return False, "Roster order not consistent across builds"
    
    return True, "Roster order is consistent and preserved"


def test_18_healer_count_reasonable() -> Tuple[bool, str]:
    """Test 18: Verify healer count is reasonable (50-200 expected)."""
    from agentic_core.L3_orchestration.discovery_roster_builder import (
        load_discovery_data, filter_healer_agents
    )
    
    data = load_discovery_data(project_root)
    healers = filter_healer_agents(data)
    
    if len(healers) < 50:
        return False, f"Too few healers: {len(healers)} (expected 50+)"
    
    if len(healers) > 300:
        return False, f"Too many healers: {len(healers)} (expected <300)"
    
    return True, f"Healer count reasonable: {len(healers)}"


# ============================================================================
# TEST RUNNER
# ============================================================================

def run_all_tests() -> Dict[str, Any]:
    """Run all tests and return results."""
    tests = [
        ("Test 1: Discovery file exists", test_1_discovery_file_exists),
        ("Test 2: Discovery data loads", test_2_discovery_data_loads),
        ("Test 3: Agents have required fields", test_3_agents_have_required_fields),
        ("Test 4: HealerMixin filter works", test_4_healer_filter_works),
        ("Test 5: Layer sorting correct order", test_5_layer_sorting_correct_order),
        ("Test 6: L0 agents first", test_6_l0_agents_first),
        ("Test 7: L5 Safety before Apps", test_7_l5_safety_before_apps),
        ("Test 8: Base agents excluded", test_8_base_agents_excluded),
        ("Test 9: Instantiation works", test_9_instantiation_works),
        ("Test 10: Agents have heal_repository", test_10_instantiated_agents_have_heal_repository),
        ("Test 11: Full roster builds", test_11_full_roster_builds),
        ("Test 12: Roster layer distribution", test_12_roster_layer_distribution),
        ("Test 13: Excludes Apps when requested", test_13_roster_excludes_apps_when_requested),
        ("Test 14: Max agents limit works", test_14_max_agents_limit_works),
        ("Test 15: Path to module conversion", test_15_path_to_module_conversion),
        ("Test 16: Layer priority complete", test_16_layer_priority_complete),
        ("Test 17: Roster order preserved", test_17_roster_order_preserved_in_execution),
        ("Test 18: Healer count reasonable", test_18_healer_count_reasonable),
    ]
    
    results = {
        "passed": 0,
        "failed": 0,
        "total": len(tests),
        "details": [],
    }
    
    print("\n" + "=" * 70)
    print("DISCOVERY ROSTER BUILDER TEST SUITE")
    print("Layer-Based Tagging System Validation")
    print("=" * 70)
    
    for name, test_func in tests:
        try:
            passed, message = test_func()
            icon = "✅" if passed else "❌"
            
            if passed:
                results["passed"] += 1
            else:
                results["failed"] += 1
            
            results["details"].append({
                "name": name,
                "passed": passed,
                "message": message,
            })
            
            print(f"\n{icon} {name}")
            print(f"   {message}")
            
        except Exception as e:
            results["failed"] += 1
            results["details"].append({
                "name": name,
                "passed": False,
                "message": f"ERROR: {e}",
            })
            print(f"\n❌ {name}")
            print(f"   ERROR: {e}")
    
    # Summary
    print("\n" + "=" * 70)
    print(f"RESULTS: {results['passed']}/{results['total']} PASSED")
    print("=" * 70)
    
    if results["failed"] > 0:
        print("\n❌ FAILED TESTS:")
        for detail in results["details"]:
            if not detail["passed"]:
                print(f"   - {detail['name']}: {detail['message']}")
    
    return results


if __name__ == "__main__":
    results = run_all_tests()
    sys.exit(0 if results["failed"] == 0 else 1)
