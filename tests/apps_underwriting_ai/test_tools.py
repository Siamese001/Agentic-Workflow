"""W4 tools CLI + audit contract tests."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_underwriting_ai.tools.audit_spine_manifest import (
    _resolve_symbol,
    audit,
    main as audit_main,
)
from apps_underwriting_ai.tools.run_underwriting import main as run_main


# -- audit_spine_manifest ---------------------------------------------------


def test_audit_passes_on_shipped_manifest() -> None:
    report = audit()
    assert report["passed"], f"audit failed: {report}"
    # The shipped manifest claims R3_grounded_read; verify entry/exit resolve
    assert all(r["ok"] for r in report["entry_points"])
    assert all(r["ok"] for r in report["exit_points"])


def test_audit_summary_has_zero_findings() -> None:
    report = audit()
    assert report["audit_summary"]["finding_count"] == 0


def test_resolve_symbol_handles_class_method() -> None:
    ok, reason = _resolve_symbol(
        "apps_underwriting_ai.runtime.dispatch.underwriting_dispatch.run_underwriting_dispatch"
    )
    assert ok, reason


def test_resolve_symbol_fails_on_missing_attribute() -> None:
    ok, reason = _resolve_symbol(
        "apps_underwriting_ai.engines.underwriting_engine.DoesNotExist"
    )
    assert not ok
    assert "has no attribute" in reason


def test_resolve_symbol_fails_on_bogus_module() -> None:
    ok, reason = _resolve_symbol("totally.bogus.module.symbol")
    assert not ok


def test_audit_main_exits_zero_on_pass(capsys) -> None:
    rc = audit_main(["--json"])
    assert rc == 0
    out = capsys.readouterr().out
    parsed = json.loads(out)
    assert parsed["passed"] is True


def test_audit_main_bad_manifest_returns_two(tmp_path, capsys) -> None:
    rc = audit_main(["--manifest", str(tmp_path / "nope.yaml")])
    assert rc == 2


# -- run_underwriting -------------------------------------------------------


def test_run_underwriting_missing_file_returns_two(tmp_path, capsys) -> None:
    rc = run_main(["--request", str(tmp_path / "nope.yaml")])
    assert rc == 2


def test_run_underwriting_end_to_end(tmp_path, capsys) -> None:
    req = tmp_path / "req.json"
    req.write_text(
        json.dumps(
            {
                "request_id": "cli-1",
                "applicant_id": "cli-applicant",
                "product_class": "auto",
                "documents": [{"kind": "id"}],
            }
        ),
        encoding="utf-8",
    )
    rc = run_main(["--request", str(req), "--format", "json"])
    assert rc == 0
    out = capsys.readouterr().out
    parsed = json.loads(out)
    assert parsed["request_id"] == "cli-1"


def test_run_underwriting_writes_artifacts(tmp_path) -> None:
    req = tmp_path / "req.json"
    req.write_text(
        json.dumps(
            {
                "request_id": "cli-2",
                "applicant_id": "a",
                "product_class": "auto",
                "documents": [{"kind": "id"}],
            }
        ),
        encoding="utf-8",
    )
    out = tmp_path / "artifacts"
    rc = run_main(["--request", str(req), "--out", str(out)])
    assert rc == 0
    assert out.exists()
    assert any(p.suffix == ".md" for p in out.iterdir())
    assert any(p.suffix == ".json" for p in out.iterdir())
