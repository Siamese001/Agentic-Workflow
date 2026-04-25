"""Unit tests for tools.generate.adg_graph_watchlist_builder.

Targets Wave-3 / Phase P8. Source: 3309 lines, fan_in=113 (L_TOOLS, impact 84.8).
Focused on the pure dataclasses + small helpers (_validate_sqlite_path,
_atomic_json_write) that exercise the stable contract without requiring a
full ADG SQLite.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

import pytest

from tools.generate.adg_graph_watchlist_builder import (
    GraphWatchlistItem,
    RemediationGuide,
    _atomic_json_write,
    _validate_sqlite_path,
)


class TestRemediationGuide:
    def test_minimal_fields(self) -> None:
        g = RemediationGuide(
            recommended_fix_pattern="seam-split",
            remediation_priority="high",
            gate_severity="fail",
            gate_decision="FAIL",
            operator_note="Refactor the hotspot.",
        )
        assert g.recommended_fix_pattern == "seam-split"
        assert g.remediation_priority == "high"
        assert g.dry_run_patch is None
        assert g.auto_apply_eligible is False

    def test_full_fields(self) -> None:
        g = RemediationGuide(
            recommended_fix_pattern="extract-interface",
            remediation_priority="low",
            gate_severity="warn",
            gate_decision="WARN",
            operator_note="Monitor.",
            dry_run_patch="--- a\n+++ b\n@@",
            auto_apply_eligible=True,
        )
        assert g.dry_run_patch is not None
        assert g.dry_run_patch.startswith("---")
        assert g.auto_apply_eligible is True

    def test_asdict_roundtrip(self) -> None:
        g = RemediationGuide(
            recommended_fix_pattern="x",
            remediation_priority="medium",
            gate_severity="warn",
            gate_decision="WARN",
            operator_note="n",
        )
        d = asdict(g)
        assert d["recommended_fix_pattern"] == "x"


class TestGraphWatchlistItem:
    def test_minimal_fields(self) -> None:
        item = GraphWatchlistItem(
            rank=1,
            file="agentic_core/L0_routing/x.py",
            layer="L0",
            graph_anomaly_type="reverse_hotspot",
            score=100.5,
            reverse_dep_score=80.0,
            bridge_score=20.0,
            scc_cluster_size=5,
            blast_radius=0.75,
            why_it_matters="High fan-in",
        )
        assert item.rank == 1
        assert item.remediation is None

    def test_with_remediation(self) -> None:
        guide = RemediationGuide(
            recommended_fix_pattern="x",
            remediation_priority="high",
            gate_severity="fail",
            gate_decision="FAIL",
            operator_note="n",
        )
        item = GraphWatchlistItem(
            rank=1,
            file="f",
            layer="L0",
            graph_anomaly_type="bridge",
            score=1.0,
            reverse_dep_score=1.0,
            bridge_score=1.0,
            scc_cluster_size=1,
            blast_radius=1.0,
            why_it_matters="matters",
            remediation=guide,
        )
        assert item.remediation is guide
        assert item.remediation.gate_severity == "fail"


class TestValidateSqlitePath:
    def test_accepts_existing_file(self, tmp_path: Path) -> None:
        p = tmp_path / "adg.sqlite"
        p.write_bytes(b"")
        result = _validate_sqlite_path(p)
        assert result.resolve() == p.resolve()

    def test_rejects_missing_file(self, tmp_path: Path) -> None:
        p = tmp_path / "missing.sqlite"
        with pytest.raises(FileNotFoundError, match="ADG SQLite not found"):
            _validate_sqlite_path(p)

    def test_rejects_directory(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="not a file"):
            _validate_sqlite_path(tmp_path)

    def test_expands_user_tilde(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        # Set HOME to tmp_path so ~ expands there
        monkeypatch.setenv("HOME", str(tmp_path))
        monkeypatch.setenv("USERPROFILE", str(tmp_path))
        f = tmp_path / "adg.sqlite"
        f.write_bytes(b"")
        # Pass ~/adg.sqlite and expect it to resolve to tmp_path/adg.sqlite
        result = _validate_sqlite_path(Path("~/adg.sqlite"))
        assert result.name == "adg.sqlite"


class TestAtomicJsonWrite:
    def test_writes_payload_to_file(self, tmp_path: Path) -> None:
        target = tmp_path / "out.json"
        payload = {"a": 1, "b": [2, 3]}
        _atomic_json_write(target, payload)
        assert target.exists()
        assert json.loads(target.read_text(encoding="utf-8")) == payload

    def test_creates_parent_directory(self, tmp_path: Path) -> None:
        target = tmp_path / "nested" / "deeper" / "out.json"
        _atomic_json_write(target, {"x": "y"})
        assert target.exists()

    def test_overwrites_existing(self, tmp_path: Path) -> None:
        target = tmp_path / "out.json"
        target.write_text('{"old":1}', encoding="utf-8")
        _atomic_json_write(target, {"new": 2})
        assert json.loads(target.read_text(encoding="utf-8")) == {"new": 2}

    def test_atomic_no_temp_leftover(self, tmp_path: Path) -> None:
        target = tmp_path / "out.json"
        _atomic_json_write(target, {"a": 1})
        # No .tmp file should remain in the parent directory
        tmp_leftovers = [p for p in tmp_path.iterdir() if p.name != "out.json"]
        assert tmp_leftovers == []
