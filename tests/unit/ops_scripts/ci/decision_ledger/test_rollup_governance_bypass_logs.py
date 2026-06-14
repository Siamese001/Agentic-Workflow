"""Unit tests for rollup_governance_bypass_logs (W4.2)."""

import importlib.util
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[5]
MOD_PATH = REPO_ROOT / "ops_scripts" / "ci" / "decision_ledger" / "rollup_governance_bypass_logs.py"


def _load():
    name = "rollup_governance_bypass_logs_tested"
    spec = importlib.util.spec_from_file_location(name, MOD_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def test_rollup_counts_lines(tmp_path: Path, monkeypatch):
    _m = _load()
    art = tmp_path / "artifacts" / "governance"
    art.mkdir(parents=True)
    log = art / "foo_bypass.jsonl"
    log.write_text(
        '{"reason": "test_a"}\n{"reason": "test_a"}\nnot json\n',
        encoding="utf-8",
    )

    monkeypatch.setattr(_m, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(
        _m,
        "ARTIFACT_ROOTS",
        (
            tmp_path / "artifacts" / "governance",
            tmp_path / "artifacts" / "governance",
            tmp_path / "artifacts" / "ci",
        ),
    )
    out = tmp_path / "out.json"
    monkeypatch.setattr(_m, "OUT_JSON", out)

    assert _m.main() == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["total_bypass_lines"] == 3
    assert data["files_scanned"] == 1
    assert any("test_a" in k for k in data["by_file"][0]["top_reasons"])
