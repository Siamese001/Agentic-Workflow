"""
Runtime Integrity Verifier - Phase 21

[HARDENING STEP]
Static analysis (ArchGuard) is not enough. We must prove that:
1. The refactored agents can actually be imported (No circular dependencies).
2. They can be instantiated (No missing mixin methods).
3. The tool_registry dicts are valid.

Run this to confirm the system is truly production-ready.
"""

import logging
import sys
import traceback
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_verify_runtime_integrity")
_emit_applies_guardrail("p0", "test_verify_runtime_integrity", "p0_governance")
_emit_reads_policy_state("p0", "test_verify_runtime_integrity", "policy_binding")
_emit_snapshots_state("p0", "test_verify_runtime_integrity", "state_snapshot")
emit_replay_key("p0", "test_verify_runtime_integrity")
emit_determinism_digest("p0", "test_verify_runtime_integrity")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
Logger = logging.getLogger("RuntimeVerifier")


def test_instantiation():
    print("--- STARTING RUNTIME INTEGRITY CHECK ---")
    failures = []

    # 1. Test Base Infrastructure
    try:
        print("[TEST] Initializing SovereignBaseAgent...")
        from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

        agent = SovereignBaseAgent()
        assert hasattr(agent, "llm_generate"), "Missing LLM capability"
        assert hasattr(agent, "cache_get"), "Missing Redis capability"
        print("   ✅ SovereignBaseAgent OK")
    except Exception as e:
        raise
        failures.append(f"SovereignBaseAgent: {e}")
        traceback.print_exc()

    # 2. Test Tool Registry (The Dict Refactor)
    try:
        print("[TEST] Initializing tool_registry...")
        from agentic_core.L2_execution.reasoning.registry import create_tool_registry

        registry = create_tool_registry()
        tools = registry.get_function_declarations()
        assert isinstance(tools, list), "Tools must be a list"
        assert len(tools) > 0, "No tools registered"
        assert isinstance(tools[0], dict), "Tools must be pure dicts (Architecture requirement)"
        print("   ✅ tool_registry OK (Pure Dicts confirmed)")
    except Exception as e:
        raise
        failures.append(f"tool_registry: {e}")
        traceback.print_exc()

    # 3. Test The Refactored Agents (Import Rewiring Check)
    agents_to_test = [
        ("L3_orchestration.engine.FissionManagerAgent", "FissionManagerAgent"),
        ("L5_safety.guardrails.HallucinationHunterAgent", "HallucinationHunterAgent"),
        ("L5_safety.reasoning.NeuralAutoImmuneAgent", "NeuralAutoImmuneAgent"),
        ("L0_routing.scripts.DependencyDiplomatAgent", "DependencyDiplomatAgent"),
        (
            "L1_cognition.agents.SemanticTerritoryMapperAgent",
            "SemanticTerritoryMapperAgent",
        ),
        ("L0_routing.scripts.BootstrapAgent", "BootstrapAgent"),
        ("L2_execution.L2ExecutionBase", "L2ExecutionBase"),
    ]

    for module_path, class_name in agents_to_test:
        try:
            print(f"[TEST] Loading {class_name} from {module_path}...")
            module = __import__(f"agentic_core.{module_path}", fromlist=[class_name])
            cls = getattr(module, class_name)

            if "BaseAgent" in class_name:
                cls(ctx=None)
            elif "Bootstrap" in class_name:
                cls(project_root=Path("."))
            elif "HallucinationHunter" in class_name:
                cls(ctx=None)
            else:
                cls()

            print(f"   ✅ {class_name} Instantiated")
        except ImportError as e:
            failures.append(f"IMPORT ERROR {class_name}: {e} (Likely circular dependency)")
        except AttributeError as e:
            failures.append(f"CLASS NOT FOUND {class_name}: {e}")
        except Exception as e:
            raise
            failures.append(f"RUNTIME ERROR {class_name}: {e}")

    print("-" * 30)
    if failures:
        print(f"❌ INTEGRITY CHECK FAILED with {len(failures)} errors:")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print("✅ SYSTEM INTEGRITY VERIFIED. No circular imports detected.")
        sys.exit(0)


if __name__ == "__main__":
    test_instantiation()
