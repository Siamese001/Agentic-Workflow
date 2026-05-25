"""W2 tests — deterministic hotspot gate linkage (no invented gates)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.adg.hotspot_gate_linkage import (
    LinkageContext,
    load_linkage_context,
    resolve_module_linkage,
)


def test_unknown_linkage_when_no_join(tmp_path: Path) -> None:
    ctx = LinkageContext()
    link = resolve_module_linkage("apps_lic/no/such/file.py", ctx)
    assert link.linkage_source == "unknown"
    assert link.linkage_confidence == "missing"
    assert link.linked_gate_ids == []


def test_accelerator_exact_match(tmp_path: Path) -> None:
    accel = tmp_path / "accel.json"
    accel.write_text(
        json.dumps(
            {
                "candidates": [
                    {
                        "file_path": "apps_lic/engines/foo.py",
                        "impacted_tests": ["tests/unit/test_foo.py"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    ctx = load_linkage_context(refactor_accelerator_path=accel, repo_root=tmp_path)
    link = resolve_module_linkage("apps_lic/engines/foo.py", ctx)
    assert link.linkage_source == "accelerator"
    assert link.linkage_confidence == "exact"
    assert link.impacted_tests_sample == ["tests/unit/test_foo.py"]


def test_queue_file_maps_gate_results(tmp_path: Path) -> None:
    queue = tmp_path / "artifacts" / "adg" / "adg_action_queue_x.json"
    queue.parent.mkdir(parents=True, exist_ok=True)
    queue.write_text(
        json.dumps(
            {
                "actions": [
                    {
                        "rank": 1,
                        "verdict_cluster": "FIX",
                        "gate_id": "10_infra_wiring",
                        "file_path": "apps_shared/integrations/governed_app_runner.py",
                        "source_id": "apps_shared/integrations/governed_app_runner.py",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    ctx = load_linkage_context(action_queue_path=queue, repo_root=tmp_path)
    link = resolve_module_linkage("apps_shared/integrations/governed_app_runner.py", ctx)
    assert link.linkage_source == "gate_results"
    assert link.linkage_confidence == "exact"
    assert link.linked_gate_ids == ["10_infra_wiring"]


def test_pview_maps_gate_id_without_markdown_grep(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """P-view consumer_file -> gate_id via P_VIEW_TO_GATE_ID only."""

    class FakeCon:
        def execute(self, sql: str, params: tuple = ()) -> "FakeCon":
            self._sql = sql
            self._params = params
            return self

        def fetchall(self) -> list[tuple]:
            if "mv_debt_concentration" in self._sql and "SELECT file" in self._sql:
                return []
            if "PRAGMA table_info(v_p0_apps_direct_infra)" in self._sql:
                return [(0, "consumer_file", "TEXT", 0, None, 0)]
            if "SELECT DISTINCT consumer_file FROM v_p0_apps_direct_infra" in self._sql:
                return [("apps_lic/integrations/bad.py",)]
            if "violations" in self._sql and "SELECT id" in self._sql:
                return []
            if "sqlite_master" in self._sql and "mv_debt" in self._sql:
                return [("mv_debt_concentration_hotspots",)]
            if "sqlite_master" in self._sql and "violations" in self._sql:
                return [("violations",)]
            return []

        def fetchone(self) -> tuple | None:
            if "sqlite_master" in self._sql and "type='view'" in self._sql:
                if self._params and self._params[0] == "v_p0_apps_direct_infra":
                    return ("v_p0_apps_direct_infra",)
                return None
            if "sqlite_master" in self._sql and "mv_debt" in self._sql:
                return ("mv_debt_concentration_hotspots",)
            if "sqlite_master" in self._sql and "violations" in self._sql:
                return ("violations",)
            rows = self.fetchall()
            return rows[0] if rows else None

    ctx = load_linkage_context(sqlite_connection=FakeCon(), repo_root=tmp_path)
    link = resolve_module_linkage("apps_lic/integrations/bad.py", ctx)
    assert link.linkage_source == "gate_results"
    assert link.linkage_confidence == "exact"
    assert "10_infra_wiring" in link.linked_gate_ids


def test_mv_debt_inferred_without_gate_invention(tmp_path: Path) -> None:
    ctx = LinkageContext(mv_debt_files={"apps_eval/core.py"})
    link = resolve_module_linkage("apps_eval/core.py", ctx)
    assert link.linkage_source == "MV"
    assert link.linkage_confidence == "inferred"
    assert link.linked_gate_ids == []
