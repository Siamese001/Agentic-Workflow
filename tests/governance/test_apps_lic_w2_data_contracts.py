"""apps_lic calibration-holdout W2 — data contract sentinel tests.

Plan: docs/archive/windsurf/legacy-tree/plans/apps-lic-calibration-holdout-e8f1c4.md W2
Covers DS4-P1 (OutreachTouchRecord / OutreachHistory) and
DS5-P1 (MutualConnectionItem / ConnectionDataSet).

Tests verify:
  - Contracts importable from apps_shared.contracts (package __init__).
  - Contracts importable from canonical module paths.
  - Immutability (frozen dataclass).
  - Field validation.
  - Helper methods (from_list, as_engine_list, properties).
  - Engine imports from contracts (not ad-hoc definitions).
  - Engine behaviour unchanged after contract wiring.
"""

from __future__ import annotations

import pytest


# ===========================================================================
# DS4-P1: OutreachTouchRecord / OutreachHistory
# ===========================================================================

class TestOutreachTouchRecordContract:
    def test_importable_from_package(self):
        from apps_shared.contracts import OutreachTouchRecord
        assert OutreachTouchRecord is not None

    def test_importable_from_module(self):
        from apps_shared.contracts.outreach_history_contract import OutreachTouchRecord
        assert OutreachTouchRecord is not None

    def test_is_frozen(self):
        from apps_shared.contracts import OutreachTouchRecord
        r = OutreachTouchRecord(touch_number=1)
        with pytest.raises((AttributeError, TypeError)):
            r.touch_number = 99  # type: ignore[misc]

    def test_required_fields(self):
        from apps_shared.contracts import OutreachTouchRecord
        r = OutreachTouchRecord(touch_number=1)
        assert r.touch_number == 1
        assert r.sent_at_iso == ""
        assert r.channel == ""
        assert r.response_received is False
        assert r.response_at_iso == ""
        assert r.message_subject == ""

    def test_all_fields_set(self):
        from apps_shared.contracts import OutreachTouchRecord
        r = OutreachTouchRecord(
            touch_number=2,
            sent_at_iso="2026-05-01T10:00:00Z",
            channel="email",
            response_received=True,
            response_at_iso="2026-05-02T09:00:00Z",
            message_subject="Following up",
        )
        assert r.touch_number == 2
        assert r.channel == "email"
        assert r.response_received is True

    def test_invalid_touch_number_raises(self):
        from apps_shared.contracts import OutreachTouchRecord
        with pytest.raises(ValueError, match="touch_number must be"):
            OutreachTouchRecord(touch_number=0)

    def test_contract_version_present(self):
        from apps_shared.contracts.outreach_history_contract import CONTRACT_VERSION, CONTRACT_NAME
        assert CONTRACT_VERSION == "1.0"
        assert "outreach_history" in CONTRACT_NAME


class TestOutreachHistory:
    def test_importable(self):
        from apps_shared.contracts import OutreachHistory
        assert OutreachHistory is not None

    def test_from_list(self):
        from apps_shared.contracts import OutreachTouchRecord, OutreachHistory
        records = [OutreachTouchRecord(touch_number=i) for i in range(1, 4)]
        history = OutreachHistory.from_list(records, recipient_id="abc123")
        assert history.touch_count == 3
        assert history.recipient_id == "abc123"

    def test_as_engine_list(self):
        from apps_shared.contracts import OutreachTouchRecord, OutreachHistory
        records = [OutreachTouchRecord(touch_number=1)]
        history = OutreachHistory.from_list(records)
        result = history.as_engine_list()
        assert isinstance(result, list)
        assert len(result) == 1

    def test_last_response_received_true(self):
        from apps_shared.contracts import OutreachTouchRecord, OutreachHistory
        records = [
            OutreachTouchRecord(touch_number=1, response_received=False),
            OutreachTouchRecord(touch_number=2, response_received=True),
        ]
        history = OutreachHistory.from_list(records)
        assert history.last_response_received is True

    def test_last_response_received_false(self):
        from apps_shared.contracts import OutreachTouchRecord, OutreachHistory
        records = [OutreachTouchRecord(touch_number=1)]
        history = OutreachHistory.from_list(records)
        assert history.last_response_received is False

    def test_is_frozen(self):
        from apps_shared.contracts import OutreachHistory
        h = OutreachHistory(touches=(), recipient_id="x")
        with pytest.raises((AttributeError, TypeError)):
            h.recipient_id = "y"  # type: ignore[misc]

    def test_touch_count_zero_for_empty(self):
        from apps_shared.contracts import OutreachHistory
        h = OutreachHistory.from_list([])
        assert h.touch_count == 0


class TestMultiTouchSequencerUsesContract:
    def test_engine_outreach_touch_record_is_contract_type(self):
        from apps_lic.engines.multi_touch_sequencer import OutreachTouchRecord as EngineRecord
        from apps_shared.contracts import OutreachTouchRecord as ContractRecord
        assert EngineRecord is ContractRecord

    def test_engine_still_sequences_correctly(self, monkeypatch):
        monkeypatch.setenv("MULTI_TOUCH_ENABLED", "1")
        from apps_lic.engines.multi_touch_sequencer import MultiTouchSequencer, OutreachTouchRecord
        engine = MultiTouchSequencer(config={})
        history = [OutreachTouchRecord(touch_number=1)]
        result = engine.sequence(recipient_class="default", outreach_history=history)
        assert result.next_touch_number == 2
        assert result.sequencing_strategy == "nudge"

    def test_contract_outreach_history_compatible_with_engine(self, monkeypatch):
        monkeypatch.setenv("MULTI_TOUCH_ENABLED", "1")
        from apps_shared.contracts import OutreachTouchRecord, OutreachHistory
        from apps_lic.engines.multi_touch_sequencer import MultiTouchSequencer
        records = [OutreachTouchRecord(touch_number=i) for i in range(1, 3)]
        history = OutreachHistory.from_list(records)
        engine = MultiTouchSequencer(config={})
        result = engine.sequence(
            recipient_class="default",
            outreach_history=history.as_engine_list(),
        )
        assert result.prior_touch_count == 2
        assert result.next_touch_number == 3


# ===========================================================================
# DS5-P1: MutualConnectionItem / ConnectionDataSet
# ===========================================================================

class TestMutualConnectionItemContract:
    def test_importable_from_package(self):
        from apps_shared.contracts import MutualConnectionItem
        assert MutualConnectionItem is not None

    def test_importable_from_module(self):
        from apps_shared.contracts.connection_data_contract import MutualConnectionItem
        assert MutualConnectionItem is not None

    def test_is_frozen(self):
        from apps_shared.contracts import MutualConnectionItem
        item = MutualConnectionItem(name="Alice", relationship_type="colleague")
        with pytest.raises((AttributeError, TypeError)):
            item.name = "Bob"  # type: ignore[misc]

    def test_required_fields(self):
        from apps_shared.contracts import MutualConnectionItem
        item = MutualConnectionItem(name="Alice")
        assert item.name == "Alice"
        assert item.company == ""
        assert item.role == ""
        assert item.relationship_type == "unknown"
        assert item.source_label == ""

    def test_all_fields_set(self):
        from apps_shared.contracts import MutualConnectionItem
        item = MutualConnectionItem(
            name="Bob",
            company="Acme",
            role="CTO",
            relationship_type="direct",
            source_label="linkedin_api",
        )
        assert item.relationship_type == "direct"
        assert item.company == "Acme"

    def test_relationship_type_lowercased(self):
        from apps_shared.contracts import MutualConnectionItem
        item = MutualConnectionItem(name="Alice", relationship_type="COLLEAGUE")
        assert item.relationship_type == "colleague"

    def test_invalid_relationship_type_raises(self):
        from apps_shared.contracts import MutualConnectionItem
        with pytest.raises(ValueError, match="relationship_type"):
            MutualConnectionItem(name="Alice", relationship_type="boss")

    def test_empty_name_raises(self):
        from apps_shared.contracts import MutualConnectionItem
        with pytest.raises(ValueError, match="non-empty"):
            MutualConnectionItem(name="   ")

    def test_valid_relationship_types_exported(self):
        from apps_shared.contracts import VALID_RELATIONSHIP_TYPES
        assert "direct" in VALID_RELATIONSHIP_TYPES
        assert "colleague" in VALID_RELATIONSHIP_TYPES
        assert "unknown" in VALID_RELATIONSHIP_TYPES

    def test_contract_version_present(self):
        from apps_shared.contracts.connection_data_contract import CONTRACT_VERSION, CONTRACT_NAME
        assert CONTRACT_VERSION == "1.0"
        assert "connection_data" in CONTRACT_NAME


class TestConnectionDataSet:
    def test_importable(self):
        from apps_shared.contracts import ConnectionDataSet
        assert ConnectionDataSet is not None

    def test_from_list(self):
        from apps_shared.contracts import MutualConnectionItem, ConnectionDataSet
        items = [
            MutualConnectionItem(name="Alice", relationship_type="direct"),
            MutualConnectionItem(name="Bob", relationship_type="colleague"),
        ]
        ds = ConnectionDataSet.from_list(items, recipient_id="r1")
        assert ds.connection_count == 2
        assert ds.recipient_id == "r1"

    def test_as_engine_list(self):
        from apps_shared.contracts import MutualConnectionItem, ConnectionDataSet
        items = [MutualConnectionItem(name="Alice")]
        ds = ConnectionDataSet.from_list(items)
        result = ds.as_engine_list()
        assert isinstance(result, list)
        assert len(result) == 1

    def test_has_direct_connection_true(self):
        from apps_shared.contracts import MutualConnectionItem, ConnectionDataSet
        items = [
            MutualConnectionItem(name="Alice", relationship_type="network"),
            MutualConnectionItem(name="Bob", relationship_type="direct"),
        ]
        ds = ConnectionDataSet.from_list(items)
        assert ds.has_direct_connection is True

    def test_has_direct_connection_false(self):
        from apps_shared.contracts import MutualConnectionItem, ConnectionDataSet
        items = [MutualConnectionItem(name="Alice", relationship_type="colleague")]
        ds = ConnectionDataSet.from_list(items)
        assert ds.has_direct_connection is False

    def test_is_frozen(self):
        from apps_shared.contracts import ConnectionDataSet
        ds = ConnectionDataSet(items=(), recipient_id="x")
        with pytest.raises((AttributeError, TypeError)):
            ds.recipient_id = "y"  # type: ignore[misc]


class TestMutualNetworkEngineUsesContract:
    def test_engine_mutual_connection_item_is_contract_type(self):
        from apps_lic.engines.mutual_network_engine import MutualConnectionItem as EngineItem
        from apps_shared.contracts import MutualConnectionItem as ContractItem
        assert EngineItem is ContractItem

    def test_engine_still_scores_correctly(self, monkeypatch):
        monkeypatch.setenv("MUTUAL_NETWORK_ENABLED", "1")
        from apps_lic.engines.mutual_network_engine import MutualNetworkEngine, MutualConnectionItem
        engine = MutualNetworkEngine(config={})
        items = [MutualConnectionItem(name="Alice", relationship_type="direct")]
        result = engine.extract(connection_items=items)
        assert result.signal_strength == "strong"
        assert result.top_connection_name == "Alice"

    def test_connection_data_set_compatible_with_engine(self, monkeypatch):
        monkeypatch.setenv("MUTUAL_NETWORK_ENABLED", "1")
        from apps_shared.contracts import MutualConnectionItem, ConnectionDataSet
        from apps_lic.engines.mutual_network_engine import MutualNetworkEngine
        items = [
            MutualConnectionItem(name="A", relationship_type="colleague"),
            MutualConnectionItem(name="B", relationship_type="alumni"),
        ]
        ds = ConnectionDataSet.from_list(items)
        engine = MutualNetworkEngine(config={})
        result = engine.extract(connection_items=ds.as_engine_list())
        assert result.connection_count == 2
        assert result.enabled is True
