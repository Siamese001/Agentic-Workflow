"""REQ-019/177/354: signature verification MUST precede any state mutation."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from agentic_core.L2_execution.UniversalWriteGateway import UniversalWriteGateway
from system_learning.engines.l4_version_store import L4VersionStore


@pytest.mark.governance
def test_uwg_verifies_signature_before_write() -> None:
    """UWG.write MUST call _verify_signature before touching store; bad sig = store untouched."""
    uwg = UniversalWriteGateway()
    mock_store = MagicMock()

    with patch.object(uwg, "_verify_signature", return_value=False) as mock_verify:
        with pytest.raises(PermissionError, match="REQ-019"):
            uwg.write(payload=b"sensitive_data", signature="invalid_sig", store=mock_store)
        mock_verify.assert_called_once_with("invalid_sig")
        mock_store.write.assert_not_called()


@pytest.mark.governance
def test_uwg_write_succeeds_with_valid_signature() -> None:
    """UWG.write MUST delegate to store.write when signature is valid."""
    uwg = UniversalWriteGateway()
    mock_store = MagicMock()

    with patch.object(uwg, "_verify_signature", return_value=True):
        uwg.write(payload=b"safe_payload", signature="good_sig", store=mock_store)
    mock_store.write.assert_called_once_with(b"safe_payload")


@pytest.mark.governance
def test_uwg_empty_signature_is_invalid() -> None:
    """UWG._verify_signature stub MUST treat empty string as invalid."""
    uwg = UniversalWriteGateway()
    assert uwg._verify_signature("") is False


@pytest.mark.governance
def test_version_store_verifies_before_commit() -> None:
    """L4VersionStore.commit MUST verify HMAC before state mutation; failure leaves store clean."""
    vs = L4VersionStore()
    mock_pkg = MagicMock()
    mock_ptr = MagicMock()

    with patch.object(vs, "_verify_package_hmac", return_value=False) as mock_verify:
        with pytest.raises(PermissionError, match="REQ-019"):
            vs.commit(package=mock_pkg, version_pointer=mock_ptr)
        mock_verify.assert_called_once_with(mock_pkg, mock_ptr)

    assert len(vs.list_versions()) == 0


@pytest.mark.governance
def test_version_store_commit_passes_with_valid_hmac() -> None:
    """L4VersionStore.commit MUST NOT raise when _verify_package_hmac returns True."""
    vs = L4VersionStore()
    mock_pkg = MagicMock()
    mock_ptr = MagicMock()

    with patch.object(vs, "_verify_package_hmac", return_value=True):
        vs.commit(package=mock_pkg, version_pointer=mock_ptr)


@pytest.mark.governance
def test_signature_check_ordering_uwg() -> None:
    """Verify that _verify_signature is checked BEFORE write side-effect (call order)."""
    call_order: list[str] = []

    uwg = UniversalWriteGateway()
    original_verify = uwg._verify_signature

    def tracking_verify(sig: str) -> bool:
        call_order.append("verify")
        return original_verify(sig)

    class TrackingStore:
        def write(self, data: bytes) -> None:
            call_order.append("write")

    with patch.object(uwg, "_verify_signature", side_effect=tracking_verify):
        uwg.write(payload=b"ordered_data", signature="nonempty", store=TrackingStore())

    assert call_order == ["verify", "write"], f"Expected verify before write, got: {call_order}"
