"""P1 hotspot basename coverage — ExitDispositionReceipt (Exit X3 receipt)."""
import pytest

from agentic_core.runtime.exit.exit_disposition import (
    ExitDispositionReceipt,
    X3D_ALLOW_FINISH,
)


def test_exit_disposition_receipt_single_x3_code() -> None:
    rec = ExitDispositionReceipt(
        request_id="r1",
        run_id="run1",
        trace_root="t1",
        app_id="apps_rg",
        task_class="resume_generation",
        x3_code=X3D_ALLOW_FINISH,
    )
    assert rec.allows_finish

    with pytest.raises(ValueError, match="invalid x3_code"):
        ExitDispositionReceipt(x3_code="NOT_A_CODE")
