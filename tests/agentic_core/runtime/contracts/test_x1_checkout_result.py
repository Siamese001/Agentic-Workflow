"""P1 hotspot basename coverage — X1CheckoutResult (Exit X1 mesh)."""
from agentic_core.runtime.contracts.x1_checkout_result import X1CheckoutResult


def test_x1_checkout_default_is_not_overall_pass() -> None:
    x1 = X1CheckoutResult(request_id="r1", run_id="run1", trace_root="t1")
    assert not x1.is_overall_pass()
    assert len(x1.items()) == 10
