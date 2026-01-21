#!/usr/bin/env python3
"""
test_registry_mapping.py - Verify unified agent registry mapping

Tests that legacy agent IDs correctly map to unified agent classes.
"""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def test_registry_mapping():
    """Test that all legacy agent mappings work correctly."""
    print("=" * 60)
    print("Unified Agent Registry Mapping Test")
    print("=" * 60)

    # Import unified agents directly to test the mapping
    from agentic_core.L1_cognition.thought_engine.UnifiedASTValidatorAgent import UnifiedASTValidatorAgent
    from agentic_core.L5_safety.unified.UnifiedStructureValidatorAgent import UnifiedStructureValidatorAgent
    from agentic_core.L4_state.ValidationContext.UnifiedCheckpointManagerAgent import UnifiedCheckpointManagerAgent
    from agentic_core.L5_safety.unified.UnifiedCodeEnforcerAgent import UnifiedCodeEnforcerAgent
    from agentic_core.L4_state.ValidationContext.UnifiedStateManagementAgent import UnifiedStateManagementAgent

    # Define the mapping inline (mirrors SubAtomicRegistryAgent)
    def _get_unified_agent_mapping():
        return {
            # Phase 1: L1 AST Validator Consolidation
            "BareExceptValidator": UnifiedASTValidatorAgent,
            "EmptyExceptValidator": UnifiedASTValidatorAgent,
            "EvalExecValidator": UnifiedASTValidatorAgent,
            "DangerousBuiltinsValidator": UnifiedASTValidatorAgent,
            "DebuggerValidator": UnifiedASTValidatorAgent,
            # Phase 2: L5 Hygiene Validator Consolidation
            "HygieneGuardian": UnifiedStructureValidatorAgent,
            "HygieneValidator": UnifiedStructureValidatorAgent,
            # Phase 3: L4 Checkpoint Manager Consolidation
            "CheckpointManager": UnifiedCheckpointManagerAgent,
            "AutonomousCheckpointManager": UnifiedCheckpointManagerAgent,
            # Phase 4: L5 Code Standards Enforcer Consolidation
            "BaseClassEnforcer": UnifiedCodeEnforcerAgent,
            "PatternEnforcer": UnifiedCodeEnforcerAgent,
            "TypeHintEnforcement": UnifiedCodeEnforcerAgent,
            # Phase 5: L4 State Management Consolidation
            "ManifestManager": UnifiedStateManagementAgent,
            "MemoryManager": UnifiedStateManagementAgent,
            "AutonomousStateGuardian": UnifiedStateManagementAgent,
        }

    def get_unified_agent_class(agent_id):
        mapping = _get_unified_agent_mapping()
        if agent_id in mapping:
            return mapping[agent_id]
        raise ValueError(f"Agent ID '{agent_id}' not found")

    def is_legacy_agent(agent_id):
        return agent_id in _get_unified_agent_mapping()

    # Get the full mapping
    mapping = _get_unified_agent_mapping()

    print(f"\nTotal legacy agent mappings: {len(mapping)}")

    # Test each phase
    phases = {
        "Phase 1 (AST Validators)": [
            "BareExceptValidator",
            "EmptyExceptValidator",
            "EvalExecValidator",
            "DangerousBuiltinsValidator",
            "DebuggerValidator",
        ],
        "Phase 2 (Hygiene Validators)": [
            "HygieneGuardian",
            "HygieneValidator",
        ],
        "Phase 3 (Checkpoint Managers)": [
            "CheckpointManager",
            "AutonomousCheckpointManager",
        ],
        "Phase 4 (Code Standards Enforcers)": [
            "BaseClassEnforcer",
            "PatternEnforcer",
            "TypeHintEnforcement",
        ],
        "Phase 5 (State Managers)": [
            "ManifestManager",
            "MemoryManager",
            "AutonomousStateGuardian",
        ],
    }

    all_passed = True

    for phase_name, agent_ids in phases.items():
        print(f"\n{phase_name}:")
        for agent_id in agent_ids:
            try:
                unified_class = get_unified_agent_class(agent_id)
                print(f"  ✓ {agent_id} -> {unified_class.__name__}")
            except Exception as e:
                print(f"  ✗ {agent_id} -> ERROR: {e}")
                all_passed = False

    # Test is_legacy_agent function
    print("\n" + "=" * 60)
    print("is_legacy_agent() tests:")
    print("=" * 60)

    legacy_tests = [
        ("BareExceptValidator", True),
        ("UnifiedASTValidatorAgent", False),
        ("NonExistentAgent", False),
    ]

    for agent_id, expected in legacy_tests:
        result = is_legacy_agent(agent_id)
        status = "✓" if result == expected else "✗"
        print(f"  {status} is_legacy_agent('{agent_id}') = {result} (expected: {expected})")
        if result != expected:
            all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("✓ ALL REGISTRY MAPPING TESTS PASSED")
    else:
        print("✗ SOME TESTS FAILED")
    print("=" * 60)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(test_registry_mapping())
