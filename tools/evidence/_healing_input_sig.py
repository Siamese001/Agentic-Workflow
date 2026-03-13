"""Check HealingInput signature, RoutingInputs signature, and REPO_ROOT depth."""
import inspect
from pathlib import Path


def test_healing_input_sig():
    from agentic_core.L2_execution.healers.healing_tier_types import HealingInput
    sig = inspect.signature(HealingInput)
    print(f"\nHealingInput params: {list(sig.parameters.keys())}")
    for name, p in sig.parameters.items():
        print(f"  {name}: default={p.default!r}")


def test_routing_inputs():
    try:
        from agentic_core.L0_routing.scripts._ssot_types import RoutingInputs
        sig = inspect.signature(RoutingInputs)
        print(f"\nRoutingInputs params: {list(sig.parameters.keys())}")
    except ImportError as e:
        print(f"\nRoutingInputs not found: {e}")

    # Try compute_routing_decision
    try:
        from agentic_core.L0_routing.scripts._ssot_routing import compute_routing_decision
        sig2 = inspect.signature(compute_routing_decision)
        print(f"\ncompute_routing_decision params: {list(sig2.parameters.keys())}")
    except ImportError as e:
        print(f"\ncompute_routing_decision not found: {e}")


def test_repo_root():
    this_file = Path(__file__).resolve()
    print(f"\nThis file: {this_file}")
    for i in range(8):
        print(f"  parents[{i}] = {this_file.parents[i]}")

    # Where test file would be
    test_file = Path(r"C:\Git\Agentic-Workflow\tests\unit\agentic_core\L2_execution\healers\test_confidence_routing_consolidation.py")
    print(f"\nTest file: {test_file}")
    for i in range(8):
        print(f"  parents[{i}] = {test_file.parents[i]}")
