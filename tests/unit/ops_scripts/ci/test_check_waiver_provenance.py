"""Tests for ops_scripts/ci/check_waiver_provenance.py (W6)."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

import pytest

from ops_scripts.ci import check_waiver_provenance as mod


NOW = datetime(2026, 4, 23, 12, 0, tzinfo=timezone.utc)


# ---- validate_entry ----------------------------------------------------


def _valid_entry(**overrides):
    base = {
        "gate": "G_REACH_l0_reachability",
        "scope": "agentic_core/foo.py",
        "reason": "Legit dynamic dispatch",
        "owner": "amit@workflow.local",
        "expires_on": "2026-07-31",
        "plan": "plan-slug-a1b2c3.md",
    }
    base.update(overrides)
    return base


def test_validate_entry_complete_passes() -> None:
    with mock.patch.object(
        mod, "_provenance_path_exists", return_value=True
    ):
        assert mod.validate_entry(_valid_entry(), now=NOW) == []


def test_missing_required_field(tmp_path: Path) -> None:
    entry = _valid_entry()
    del entry["reason"]
    problems = mod.validate_entry(entry, now=NOW)
    assert any("reason" in p for p in problems)


def test_missing_provenance() -> None:
    entry = _valid_entry()
    del entry["plan"]
    problems = mod.validate_entry(entry, now=NOW)
    assert any("provenance" in p for p in problems)


def test_bad_date_format() -> None:
    entry = _valid_entry(expires_on="July 2026")
    with mock.patch.object(
        mod, "_provenance_path_exists", return_value=True
    ):
        problems = mod.validate_entry(entry, now=NOW)
    assert any("YYYY-MM-DD" in p for p in problems)


def test_adr_file_must_exist() -> None:
    entry = _valid_entry()
    del entry["plan"]
    entry["adr"] = "ADR-999-missing.md"
    with mock.patch.object(
        mod, "_provenance_path_exists", return_value=False
    ):
        problems = mod.validate_entry(entry, now=NOW)
    assert any("adr provenance" in p for p in problems)


def test_plan_file_must_exist() -> None:
    entry = _valid_entry(plan="nonexistent-plan.md")
    with mock.patch.object(
        mod, "_provenance_path_exists", return_value=False
    ):
        problems = mod.validate_entry(entry, now=NOW)
    assert any("plan provenance" in p for p in problems)


def test_empty_string_field_is_missing() -> None:
    problems = mod.validate_entry(
        _valid_entry(reason="   "), now=NOW
    )
    assert any("reason" in p for p in problems)


# ---- _load_waivers -----------------------------------------------------


def test_load_waivers_missing_file(tmp_path: Path) -> None:
    assert mod._load_waivers(tmp_path / "absent.yaml") == []


def test_load_waivers_empty(tmp_path: Path) -> None:
    p = tmp_path / "w.yaml"
    p.write_text("waivers: []\n", encoding="utf-8")
    assert mod._load_waivers(p) == []


def test_load_waivers_malformed(tmp_path: Path) -> None:
    p = tmp_path / "w.yaml"
    p.write_text("{[ invalid yaml }}", encoding="utf-8")
    assert mod._load_waivers(p) == []


def test_load_waivers_filters_non_dict(tmp_path: Path) -> None:
    p = tmp_path / "w.yaml"
    p.write_text(
        "waivers:\n"
        "  - gate: X\n"
        "    scope: Y\n"
        "  - this-is-a-string\n",
        encoding="utf-8",
    )
    got = mod._load_waivers(p)
    assert len(got) == 1


# ---- _provenance_path_exists ------------------------------------------


def test_provenance_exact_path_match(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(mod, "REPO_ROOT", tmp_path)
    (tmp_path / "docs" / "architecture" / "adr").mkdir(parents=True)
    adr = tmp_path / "docs" / "architecture" / "adr" / "ADR-001-foo.md"
    adr.write_text("adr", encoding="utf-8")
    assert mod._provenance_path_exists(
        "docs/architecture/adr/ADR-001-foo.md", mod.ADR_GLOB
    )
    assert not mod._provenance_path_exists(
        "docs/architecture/adr/ADR-999.md", mod.ADR_GLOB
    )


def test_provenance_basename_match(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(mod, "REPO_ROOT", tmp_path)
    plan_dir = tmp_path / ".windsurf" / "plans"
    plan_dir.mkdir(parents=True)
    (plan_dir / "my-plan-abc123.md").write_text("x", encoding="utf-8")
    assert mod._provenance_path_exists(
        "my-plan-abc123.md", mod.PLAN_GLOB
    )
    # Partial/fuzzy match should also hit via fnmatch
    assert mod._provenance_path_exists("my-plan", mod.PLAN_GLOB)


# ---- Gate integration ---------------------------------------------------


def test_gate_returns_empty_on_empty_waivers(
    tmp_path: Path, monkeypatch
) -> None:
    waiver_file = tmp_path / "w.yaml"
    waiver_file.write_text("waivers: []\n", encoding="utf-8")
    monkeypatch.setattr(mod, "WAIVER_FILE", waiver_file)
    gate = mod.WaiverProvenanceGate.__new__(mod.WaiverProvenanceGate)
    gate.snapshot = tmp_path / "dummy.sqlite"
    gate.waivers = {}
    violations = gate.run(None)
    assert violations == []


def test_gate_flags_malformed_waiver(
    tmp_path: Path, monkeypatch
) -> None:
    waiver_file = tmp_path / "w.yaml"
    waiver_file.write_text(
        "waivers:\n"
        "  - gate: G_REACH_l0_reachability\n"
        "    scope: some/file.py\n"
        "    reason: missing provenance\n"
        "    owner: amit\n"
        "    expires_on: 2026-07-31\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(mod, "WAIVER_FILE", waiver_file)
    gate = mod.WaiverProvenanceGate.__new__(mod.WaiverProvenanceGate)
    gate.snapshot = tmp_path / "dummy.sqlite"
    gate.waivers = {}
    violations = gate.run(None)
    assert len(violations) == 1
    assert "provenance" in violations[0].detail
