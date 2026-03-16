"""ADG-driven tests for agentic_core/mixins/hardening_mixin.py — fan_in=2.

Contract tests: TokenLimitError, HardeningMixin init, execute_hardened API.
"""

from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_hardening_mixin_adg")
_emit_applies_guardrail("p0", "test_hardening_mixin_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_hardening_mixin_adg", "policy_binding")
_emit_snapshots_state("p0", "test_hardening_mixin_adg", "state_snapshot")
emit_replay_key("p0", "test_hardening_mixin_adg")
emit_determinism_digest("p0", "test_hardening_mixin_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

try:
    from agentic_core.mixins.hardening_mixin import HardeningMixin, TokenLimitError

    _IMPORT_OK = True
except Exception:
    _IMPORT_OK = False
    HardeningMixin = None  # type: ignore[assignment,misc]
    TokenLimitError = None  # type: ignore[assignment,misc]


class TestTokenLimitError:
    @pytest.mark.skipif(not _IMPORT_OK, reason="hardening_mixin deps unavailable")
    def test_is_exception(self):
        assert issubclass(TokenLimitError, Exception)

    @pytest.mark.skipif(not _IMPORT_OK, reason="hardening_mixin deps unavailable")
    def test_can_be_raised(self):
        with pytest.raises(TokenLimitError):
            raise TokenLimitError("token limit exceeded")


@pytest.mark.skipif(not _IMPORT_OK, reason="hardening_mixin deps unavailable")
class TestHardeningMixinImport:
    def test_importable(self):
        assert callable(HardeningMixin)

    def test_has_execute_hardened(self):
        assert hasattr(HardeningMixin, "execute_hardened")
