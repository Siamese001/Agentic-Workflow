import asyncio

from core_v10_7.constants import NodeStatus
from core_v10_7.models import NodeResult
from core_v10_7.services import SelfCorrectionManager


def test_self_correction_retry_lifecycle():
    manager = SelfCorrectionManager()
    workflow_id = "wf-1"
    assert manager.can_retry(workflow_id)
    manager.start_retry(workflow_id)
    manager.start_retry(workflow_id)
    assert not manager.can_retry(workflow_id)
    manager.finalize_retry(workflow_id)
    assert manager.can_retry(workflow_id)


def test_self_correction_apply_runs_validator():
    class DummyValidator:
        def __init__(self):
            self.called = False

        def validate(self, payload):
            self.called = True

    validator = DummyValidator()
    manager = SelfCorrectionManager(validator)
    result = NodeResult(status=NodeStatus.SUCCESS, payload={"answer": "yes"})
    final = asyncio.get_event_loop().run_until_complete(manager.apply(result))
    assert validator.called
    assert final == result
