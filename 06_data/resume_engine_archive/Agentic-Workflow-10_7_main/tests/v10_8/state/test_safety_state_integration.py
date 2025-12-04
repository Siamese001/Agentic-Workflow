import pathlib
from models import MainGraphState

def test_safety_fields_merge():
    base = MainGraphState()
    patch = {
        "safety_report": {"is_safe": True, "findings": []},
        "policy_decision": {"allowed": True, "reason": None},
        "constitutional_review": {"passed": True, "violations": []},
    }

    # simulate adapter logic
    from state_adapter_stack import StateAdapterStack
    adapter = StateAdapterStack(context=None, debug_mode=False)

    new_state = adapter.apply_patch(base, patch)

    assert new_state.safety_report == patch["safety_report"]
    assert new_state.policy_decision == patch["policy_decision"]
    assert new_state.constitutional_review == patch["constitutional_review"]
