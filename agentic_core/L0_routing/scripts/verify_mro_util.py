"""
MRO Verification Script

Verifies the Method Resolution Order (MRO) for complex agents after
the infrastructure_mixin consolidation.

Opportunity #4: Mixin Inheritance Complexity - Phase 4 Verification
"""

import sys
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "verify_mro_util")
emit_determinism_digest("p0", "verify_mro_util")

_emit_dispatches_healing_run("p1", "verify_mro_util", "L0")
_emit_routes_through("p1", "verify_mro_util", "L0")
_emit_escalates_to_human("p1", "verify_mro_util", "L0")
_emit_reads_policy_state("p1", "verify_mro_util", "L0")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
# guardian: allow-global-mutation
sys.path.insert(0, str(PROJECT_ROOT))


def print_mro(agent_class, agent_name: str):
    """Print the MRO for an agent class."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "print_mro", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "print_mro", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "print_mro")
    print(f"\n{'=' * 80}")
    print(f"MRO for {agent_name}")
    print(f"{'=' * 80}")
    mro = agent_class.__mro__
    for i, cls in enumerate(mro):
        indent = "  " * i
        print(f"{indent}{i}. {cls.__module__}.{cls.__name__}")
    print(f"\nTotal classes in MRO: {len(mro)}")
    has_infra = any("infrastructure_mixin" in cls.__name__ for cls in mro)
    has_healer = any("HealerMixin" in cls.__name__ for cls in mro)
    has_mcp = any("MCPHardened" in cls.__name__ for cls in mro)
    has_testing = any("SubatomicTesting" in cls.__name__ for cls in mro)
    print("\nInfrastructure Components:")
    print(f"  infrastructure_mixin: {('✅' if has_infra else '❌')}")
    print(f"  HealerMixin: {('✅' if has_healer else '❌')}")
    print(f"  MCPHardenedMixin: {('✅' if has_mcp else '❌')}")
    print(f"  SubatomicTestingMixin: {('✅' if has_testing else '❌')}")
    return {
        "has_infra": has_infra,
        "has_healer": has_healer,
        "has_mcp": has_mcp,
        "has_testing": has_testing,
        "mro_length": len(mro),
    }


def verify_sovereign_base_agent():
    """Verify SovereignBaseAgent MRO."""
    try:
        from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

        return print_mro(SovereignBaseAgent, "SovereignBaseAgent")
    except ImportError as e:
        print(f"❌ Failed to import SovereignBaseAgent: {e}")
        return None


def verify_meta_learning_agent():
    """Verify MetaLearningAgent MRO (complex case)."""
    try:
        from agentic_core.L0_routing.seams.observability_seam import load_meta_learning_agent

        MetaLearningAgent = load_meta_learning_agent()
        return print_mro(MetaLearningAgent, "MetaLearningAgent")
    except ImportError as e:
        print(f"❌ Failed to import MetaLearningAgent: {e}")
        return None


def verify_location_validator_agent():
    """Verify LocationValidatorAgent MRO."""
    try:
        from agentic_core.L0_routing.seams.safety_reasoning_seam import load_location_validator_agent

        LocationValidatorAgent = load_location_validator_agent()
        return print_mro(LocationValidatorAgent, "LocationValidatorAgent")
    except ImportError as e:
        print(f"❌ Failed to import LocationValidatorAgent: {e}")
        return None


def verify_hierarchy_agent():
    """Verify HierarchyAgent MRO via subprocess."""
    try:
        from agentic_core.L0_routing.utils.subprocess_runner_util import invoke_hierarchy_agent

        result = invoke_hierarchy_agent(action="verify_mro")
        if result.get("success"):
            mro = result.get("mro", [])
            print(f"\n{'=' * 80}")
            print("MRO for HierarchyAgent (via subprocess)")
            print(f"{'=' * 80}")
            for i, cls_name in enumerate(mro):
                indent = "  " * i
                print(f"{indent}{i}. {cls_name}")
            print(f"\nTotal classes in MRO: {len(mro)}")
            has_infra = any("infrastructure_mixin" in cls for cls in mro)
            has_healer = any("HealerMixin" in cls for cls in mro)
            has_mcp = any("MCPHardened" in cls for cls in mro)
            has_testing = any("SubatomicTesting" in cls for cls in mro)
            print("\nInfrastructure Components:")
            print(f"  infrastructure_mixin: {('✅' if has_infra else '❌')}")
            print(f"  HealerMixin: {('✅' if has_healer else '❌')}")
            print(f"  MCPHardenedMixin: {('✅' if has_mcp else '❌')}")
            print(f"  SubatomicTestingMixin: {('✅' if has_testing else '❌')}")
            return {
                "has_infra": has_infra,
                "has_healer": has_healer,
                "has_mcp": has_mcp,
                "has_testing": has_testing,
                "mro_length": len(mro),
            }
        else:
            print(f"❌ Failed to verify HierarchyAgent MRO: {result.get('error')}")
            return None
    except Exception as e:
        print(f"❌ Failed to verify HierarchyAgent: {e}")
        return None


def main():
    """Run MRO verification for multiple agents."""
    print("=" * 80)
    print("MRO VERIFICATION - Opportunity #4: Mixin Inheritance Complexity")
    print("=" * 80)
    results = {}
    print("\n[Test 1] SovereignBaseAgent (Root)")
    results["sovereign"] = verify_sovereign_base_agent()
    print("\n[Test 2] MetaLearningAgent (Complex Case)")
    results["meta_learning"] = verify_meta_learning_agent()
    print("\n[Test 3] LocationValidatorAgent (L5 Agent)")
    results["location_validator"] = verify_location_validator_agent()
    print("\n[Test 4] HierarchyAgent (L5 Agent)")
    results["hierarchy"] = verify_hierarchy_agent()
    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    success_count = sum(1 for r in results.values() if r is not None and r.get("has_infra"))
    total_count = len(results)
    print(f"\nAgents with infrastructure_mixin: {success_count}/{total_count}")
    for agent_name, result in results.items():
        if result is None:
            print(f"  ❌ {agent_name}: Failed to import")
        elif result.get("has_infra"):
            print(f"  ✅ {agent_name}: infrastructure_mixin present (MRO length: {result['mro_length']})")
        else:
            print(f"  ⚠️  {agent_name}: infrastructure_mixin missing (MRO length: {result['mro_length']})")
    if success_count == total_count:
        print("\n✅ ALL AGENTS VERIFIED: infrastructure_mixin consolidation successful")
        return 0
    else:
        print(f"\n❌ VERIFICATION FAILED: {total_count - success_count} agents missing infrastructure_mixin")
        return 1


if __name__ == "__main__":
    sys.exit(main())
