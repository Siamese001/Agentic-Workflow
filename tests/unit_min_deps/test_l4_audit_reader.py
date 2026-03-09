"""Unit tests for system_learning.engines.l4_audit_reader.

Covers:
  - Valid read returns expected bytes
  - Window invalid => ValueError
  - AuditStore protocol has no write methods
  - Authority guard is called (assert_read_only_audit_access invoked)
"""

from unittest.mock import MagicMock, patch

import pytest

from system_learning.enforcement.authority_invariants import AuthorityViolation
from system_learning.engines.l4_audit_reader import AuditStore, pull_audit_data

pytestmark = pytest.mark.unit_min_deps


# =============================================================================
# Fake in-memory AuditStore for tests
# =============================================================================


class FakeAuditStore:
    """Pure in-memory fake implementing AuditStore protocol."""

    def __init__(self, data: bytes = b"") -> None:
        self._data = data

    def read_audit_slice(self, window_start_utc: int, window_end_utc: int) -> bytes:
        return self._data


# =============================================================================
# Protocol conformance
# =============================================================================


class TestAuditStoreProtocol:
    def test_fake_store_satisfies_protocol(self):
        store = FakeAuditStore(b"test")
        assert isinstance(store, AuditStore)

    def test_protocol_has_no_write_methods(self):
        """AuditStore protocol must not expose any write/delete/mutate methods."""
        forbidden = {
            "write_audit_slice",
            "append_audit_slice",
            "delete_audit_slice",
            "mutate_audit",
            "overwrite_audit",
            "patch_audit",
        }
        protocol_attrs = set(dir(AuditStore))
        intersection = forbidden & protocol_attrs
        assert not intersection, f"AuditStore protocol exposes forbidden write methods: {intersection}"

    def test_fake_store_has_no_write_methods(self):
        """FakeAuditStore must not expose write methods."""
        store = FakeAuditStore()
        forbidden = {
            "write_audit_slice",
            "append_audit_slice",
            "delete_audit_slice",
        }
        store_attrs = set(dir(store))
        intersection = forbidden & store_attrs
        assert not intersection, f"FakeAuditStore exposes forbidden write methods: {intersection}"


# =============================================================================
# pull_audit_data — valid reads
# =============================================================================


class TestPullAuditDataValid:
    def test_returns_expected_bytes(self):
        expected = b"audit-data-slice"
        store = FakeAuditStore(expected)
        result = pull_audit_data(store, 1_700_000_000, 1_700_003_600)
        assert result == expected

    def test_returns_empty_bytes_when_store_empty(self):
        store = FakeAuditStore(b"")
        result = pull_audit_data(store, 1_700_000_000, 1_700_003_600)
        assert result == b""

    def test_returns_bytes_unmodified(self):
        """pull_audit_data must not mutate the returned bytes."""
        raw = b"\x00\x01\x02\x03\xff\xfe"
        store = FakeAuditStore(raw)
        result = pull_audit_data(store, 1_700_000_000, 1_700_003_600)
        assert result == raw
        assert result is not None

    def test_delegates_window_to_store(self):
        """pull_audit_data must pass window parameters to store unchanged."""
        mock_store = MagicMock(spec=FakeAuditStore)
        mock_store.read_audit_slice.return_value = b"data"
        pull_audit_data(mock_store, 1_700_000_000, 1_700_003_600)
        mock_store.read_audit_slice.assert_called_once_with(1_700_000_000, 1_700_003_600)
        assert True  # no-exception contract


# =============================================================================
# pull_audit_data — invalid window
# =============================================================================


class TestPullAuditDataInvalidWindow:
    def test_start_equal_to_end_raises(self):
        store = FakeAuditStore(b"data")
        with pytest.raises(ValueError, match="INVALID_AUDIT_WINDOW"):
            pull_audit_data(store, 1_700_000_000, 1_700_000_000)

    def test_start_greater_than_end_raises(self):
        store = FakeAuditStore(b"data")
        with pytest.raises(ValueError, match="INVALID_AUDIT_WINDOW"):
            pull_audit_data(store, 1_700_003_600, 1_700_000_000)

    def test_store_not_called_on_invalid_window(self):
        mock_store = MagicMock(spec=FakeAuditStore)
        with pytest.raises(ValueError):
            pull_audit_data(mock_store, 1_700_003_600, 1_700_000_000)
        mock_store.read_audit_slice.assert_not_called()


# =============================================================================
# Authority guard integration
# =============================================================================


class TestAuthorityGuardIntegration:
    def test_assert_read_only_audit_access_is_called(self):
        """pull_audit_data must invoke assert_read_only_audit_access."""
        store = FakeAuditStore(b"data")
        with patch("system_learning.engines.l4_audit_reader.assert_read_only_audit_access") as mock_guard:
            pull_audit_data(store, 1_700_000_000, 1_700_003_600)
        mock_guard.assert_called_once()
        assert True  # no-exception contract

    def test_assert_zero_execution_authority_is_called(self):
        """pull_audit_data must invoke assert_zero_execution_authority."""
        store = FakeAuditStore(b"data")
        with patch("system_learning.engines.l4_audit_reader.assert_zero_execution_authority") as mock_guard:
            pull_audit_data(store, 1_700_000_000, 1_700_003_600)
        mock_guard.assert_called_once()
        assert True  # no-exception contract

    def test_authority_context_has_read_mode(self):
        """The AuthorityContext passed to guards must have mode='READ'."""
        store = FakeAuditStore(b"data")
        captured_ctx = []

        def capture(ctx):
            captured_ctx.append(ctx)

        with patch(
            "system_learning.engines.l4_audit_reader.assert_read_only_audit_access",
            side_effect=capture,
        ):
            pull_audit_data(store, 1_700_000_000, 1_700_003_600)

        assert len(captured_ctx) == 1
        assert captured_ctx[0].mode == "READ"

    def test_authority_context_targets_l4_audit(self):
        """The AuthorityContext must target 'l4_audit'."""
        store = FakeAuditStore(b"data")
        captured_ctx = []

        def capture(ctx):
            captured_ctx.append(ctx)

        with patch(
            "system_learning.engines.l4_audit_reader.assert_read_only_audit_access",
            side_effect=capture,
        ):
            pull_audit_data(store, 1_700_000_000, 1_700_003_600)

        assert "audit" in captured_ctx[0].target.lower()

    def test_authority_violation_propagates(self):
        """If a guard raises AuthorityViolation, it must propagate to caller."""
        store = FakeAuditStore(b"data")
        with patch(
            "system_learning.engines.l4_audit_reader.assert_zero_execution_authority",
            side_effect=AuthorityViolation("TEST_VIOLATION"),
        ):
            with pytest.raises(AuthorityViolation, match="TEST_VIOLATION"):
                pull_audit_data(store, 1_700_000_000, 1_700_003_600)
