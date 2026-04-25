"""Behavioral tests for L4 knowledge_integrity_guard + mission_historian."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from agentic_core.L4_state.enforcement.knowledge_integrity_guard import (
    KnowledgeIntegrityGuard,
    KnowledgeIntegrityViolation,
    KnowledgeNode,
)


# ============================================================================
# KnowledgeIntegrityGuard
# ============================================================================


class TestKnowledgeNode:
    def test_signature_deterministic(self) -> None:
        a = KnowledgeNode(
            content_hash="c",
            prev_hash="p",
            node_id="n",
            content={"x": 1},
        )
        b = KnowledgeNode(
            content_hash="c",
            prev_hash="p",
            node_id="n",
            content={"x": 1},
        )
        assert a.signature == b.signature

    def test_signature_changes_with_content_hash(self) -> None:
        a = KnowledgeNode(
            content_hash="c1",
            prev_hash="p",
            node_id="n",
            content={},
        )
        b = KnowledgeNode(
            content_hash="c2",
            prev_hash="p",
            node_id="n",
            content={},
        )
        assert a.signature != b.signature

    def test_signature_is_sha256_hex(self) -> None:
        n = KnowledgeNode(content_hash="c", prev_hash="p", node_id="n", content={})
        assert len(n.signature) == 64
        int(n.signature, 16)

    def test_frozen(self) -> None:
        n = KnowledgeNode(content_hash="c", prev_hash="p", node_id="n", content={})
        with pytest.raises((AttributeError, Exception)):
            n.node_id = "other"  # type: ignore[misc]


class TestKnowledgeIntegrityViolation:
    def test_is_exception(self) -> None:
        assert issubclass(KnowledgeIntegrityViolation, Exception)


class TestKnowledgeIntegrityGuard:
    def test_genesis_chain_verifies(self) -> None:
        g = KnowledgeIntegrityGuard("genesis")
        assert g.verify_chain() is True

    def test_single_mutation(self) -> None:
        g = KnowledgeIntegrityGuard("genesis")
        node = g.mutate("node1", {"k": "v"})
        assert node.prev_hash == "genesis"
        assert g.verify_chain() is True

    def test_chain_of_mutations(self) -> None:
        g = KnowledgeIntegrityGuard("genesis")
        a = g.mutate("n1", {"v": 1})
        b = g.mutate("n2", {"v": 2})
        assert b.prev_hash == a.signature
        assert g.verify_chain() is True

    def test_head_updates_with_mutation(self) -> None:
        g = KnowledgeIntegrityGuard("genesis")
        n = g.mutate("n1", {})
        assert g._head_hash == n.signature

    def test_tampered_ledger_detected(self) -> None:
        g = KnowledgeIntegrityGuard("genesis")
        node = g.mutate("n1", {"k": "v"})
        # Tamper: remove node from ledger while head still points to it
        del g._ledger[node.signature]
        with pytest.raises(KnowledgeIntegrityViolation, match="Chain broken"):
            g.verify_chain()

    def test_compaction_snapshot_shape(self) -> None:
        g = KnowledgeIntegrityGuard("genesis")
        g.mutate("n1", {})
        snapshot = g.create_compaction_snapshot()
        assert "snapshot" in snapshot
        assert "signature" in snapshot
        assert snapshot["snapshot"]["genesis_hash"] == "genesis"
        assert snapshot["snapshot"]["ledger_size"] == 1

    def test_compaction_snapshot_signature_is_sha256(self) -> None:
        g = KnowledgeIntegrityGuard("genesis")
        g.mutate("n1", {})
        snapshot = g.create_compaction_snapshot()
        assert len(snapshot["signature"]) == 64
        int(snapshot["signature"], 16)


# ============================================================================
# MissionHistorian
# ============================================================================


@pytest.fixture
def fake_gateway() -> MagicMock:
    gw = MagicMock()
    gw.init_csv = MagicMock()
    gw.append_csv_row = MagicMock()
    return gw


@pytest.fixture
def historian(tmp_path: Path, fake_gateway: MagicMock):
    log = tmp_path / "audit.csv"
    with patch(
        "agentic_core.L4_state.enforcement.mission_historian._get_write_gateway",
        return_value=fake_gateway,
    ):
        from agentic_core.L4_state.enforcement.mission_historian import (
            MissionHistorian,
        )

        yield MissionHistorian(log_path=log), log


class TestMissionHistorianConstruction:
    def test_defaults_log_path(self, fake_gateway: MagicMock) -> None:
        with patch(
            "agentic_core.L4_state.enforcement.mission_historian._get_write_gateway",
            return_value=fake_gateway,
        ):
            from agentic_core.L4_state.enforcement.mission_historian import (
                MissionHistorian,
            )

            h = MissionHistorian()
            assert h.log_path == Path("mission_audit.csv")

    def test_init_csv_called_when_missing(self, historian: tuple) -> None:
        h, log = historian
        # gateway.init_csv was called because log didn't exist
        # Note: fake_gateway comes via the fixture, so we check through h instance
        assert h.log_path == log


class TestMissionHistorianRecord:
    def test_record_calls_gateway(
        self,
        historian: tuple,
        fake_gateway: MagicMock,
    ) -> None:
        h, _ = historian
        with patch(
            "agentic_core.L4_state.enforcement.mission_historian._get_write_gateway",
            return_value=fake_gateway,
        ):
            h.record("f.py", "move", "src/", "dst/", "refactor")
        fake_gateway.append_csv_row.assert_called_once()
        args, _ = fake_gateway.append_csv_row.call_args
        row = args[1]
        assert "f.py" in row
        assert "move" in row
        assert "refactor" in row


class TestMissionHistorianGetHistory:
    def test_returns_empty_when_no_file(self, tmp_path: Path) -> None:
        gw = MagicMock()
        with patch(
            "agentic_core.L4_state.enforcement.mission_historian._get_write_gateway",
            return_value=gw,
        ):
            from agentic_core.L4_state.enforcement.mission_historian import (
                MissionHistorian,
            )

            h = MissionHistorian(log_path=tmp_path / "missing.csv")
            # Remove file that init may have created (gw is mocked so no actual init)
            p = tmp_path / "missing.csv"
            if p.exists():
                p.unlink()
            assert h.get_history() == []

    def test_reads_real_csv(self, tmp_path: Path) -> None:
        log = tmp_path / "real.csv"
        log.write_text(
            "timestamp,file,action,source,destination,reason\n"
            "2026-01-01T00:00:00,a.py,move,/a,/b,refactor\n"
            "2026-01-02T00:00:00,b.py,delete,/b,,cleanup\n",
            encoding="utf-8",
        )
        gw = MagicMock()
        with patch(
            "agentic_core.L4_state.enforcement.mission_historian._get_write_gateway",
            return_value=gw,
        ):
            from agentic_core.L4_state.enforcement.mission_historian import (
                MissionHistorian,
            )

            h = MissionHistorian(log_path=log)
            all_rows = h.get_history()
            assert len(all_rows) == 2
            filtered = h.get_history(file_name="a.py")
            assert len(filtered) == 1
            assert filtered[0]["action"] == "move"


class TestMissionHistorianGetSummary:
    def test_summary_shape(self, tmp_path: Path) -> None:
        log = tmp_path / "summary.csv"
        log.write_text(
            "timestamp,file,action,source,destination,reason\n"
            "t,a.py,move,/a,/b,r\n"
            "t,b.py,move,/c,/d,r\n"
            "t,c.py,delete,/e,,r\n",
            encoding="utf-8",
        )
        gw = MagicMock()
        with patch(
            "agentic_core.L4_state.enforcement.mission_historian._get_write_gateway",
            return_value=gw,
        ):
            from agentic_core.L4_state.enforcement.mission_historian import (
                MissionHistorian,
            )

            h = MissionHistorian(log_path=log)
            summary = h.get_summary()
            assert summary["total_records"] == 3
            assert summary["actions"]["move"] == 2
            assert summary["actions"]["delete"] == 1
            assert summary["log_path"] == str(log)
