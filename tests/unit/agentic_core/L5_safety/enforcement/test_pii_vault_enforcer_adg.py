"""ADG-driven tests for L5_safety/enforcement/pii_vault_enforcer.py — fan_in=1."""
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

_emit_records_execution_trace("p0", "evidence", "test_pii_vault_enforcer_adg")
_emit_applies_guardrail("p0", "test_pii_vault_enforcer_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_pii_vault_enforcer_adg", "policy_binding")
_emit_snapshots_state("p0", "test_pii_vault_enforcer_adg", "state_snapshot")
emit_replay_key("p0", "test_pii_vault_enforcer_adg")
emit_determinism_digest("p0", "test_pii_vault_enforcer_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.enforcement.pii_vault_enforcer import PiiVault


class TestPiiVault:
    def test_creates(self):
        vault = PiiVault(config={})
        assert vault is not None

    def test_tokenize_replaces_pii(self):
        vault = PiiVault(config={})
        result = vault.tokenize("trace-1", "Hello John Doe!")
        assert "John Doe" not in result
        assert "USER_ALPHA" in result

    def test_restore_recovers_pii(self):
        vault = PiiVault(config={})
        tokenized = vault.tokenize("trace-1", "Hello John Doe!")
        restored = vault.restore("trace-1", tokenized)
        assert "John Doe" in restored

    def test_clean_text_unchanged(self):
        vault = PiiVault(config={})
        result = vault.tokenize("t", "Hello world")
        assert result == "Hello world"

    def test_has_tokenize(self):
        assert hasattr(PiiVault, "tokenize")

    def test_has_restore(self):
        assert hasattr(PiiVault, "restore")
