"""P1 hotspot basename coverage — X3Disposition (Exit terminal contract)."""
import pytest

from tests._core_contract._spine_u0_exit_fixtures import L5_CERT


def test_x3_disposition_requires_l5_cert() -> None:
    from agentic_core.runtime.contracts.x3_disposition import X3Disposition

    d = X3Disposition(
        request_id="r1",
        run_id="run1",
        app_id="apps_rg",
        trace_id="t1",
        exit_status="success",
        l5_certification_ref=L5_CERT,
    )
    assert d.l5_certification_ref == L5_CERT

    with pytest.raises(ValueError, match="l5_certification_ref"):
        X3Disposition(
            request_id="r1",
            run_id="run1",
            app_id="apps_rg",
            trace_id="t1",
            exit_status="success",
            l5_certification_ref="",
        )
