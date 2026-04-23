"""Tests for ops_scripts/ci/check_prompt_packet_contract.py CI gate."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import pytest

from tools.adg.prompt_assembly.contracts import PromptEnvelope

_ROOT = Path(__file__).resolve().parents[3]
_GATE_PATH = _ROOT / "ops_scripts" / "ci" / "check_prompt_packet_contract.py"


def _load_gate_module():
    spec = importlib.util.spec_from_file_location("check_prompt_packet_contract_test_loaded", _GATE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def gate():
    return _load_gate_module()


def _clean_packet_dict() -> dict[str, Any]:
    env = PromptEnvelope(
        packet_type="test",
        system_block="mode",
        policy_block="Rules:\n1. cite sources\n2. abstain if weak",
        task_block="Summarize.",
        must_use_evidence=[{"source_artifact": "s", "content": "body"}],
        output_schema={"fields": ["answer"]},
        replay_metadata={"replay_key": "rk"},
    )
    return env.to_dict()


def test_gate_passes_on_clean_packet(tmp_path: Path, gate, capsys: pytest.CaptureFixture[str]) -> None:
    pkt = tmp_path / "clean.json"
    pkt.write_text(json.dumps(_clean_packet_dict()), encoding="utf-8")
    rc = gate.main([str(pkt)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "1 packet(s) passed" in out


def test_gate_fails_closed_on_bad_packet(tmp_path: Path, gate, capsys: pytest.CaptureFixture[str]) -> None:
    bad = _clean_packet_dict()
    bad["task_block"] = "no numbered directive"
    bad["policy_block"] = ""
    pkt = tmp_path / "bad.json"
    pkt.write_text(json.dumps(bad), encoding="utf-8")
    rc = gate.main([str(pkt)])
    assert rc == 1
    err = capsys.readouterr().err
    assert "PA.2a" in err
    assert "missing_grounding_directive" in err


def test_gate_returns_2_on_invalid_json(tmp_path: Path, gate, capsys: pytest.CaptureFixture[str]) -> None:
    pkt = tmp_path / "bad.json"
    pkt.write_text("{not-json", encoding="utf-8")
    rc = gate.main([str(pkt)])
    assert rc == 2
    err = capsys.readouterr().err
    assert "invalid JSON" in err


def test_gate_returns_2_when_json_is_not_object(
    tmp_path: Path, gate, capsys: pytest.CaptureFixture[str]
) -> None:
    pkt = tmp_path / "list.json"
    pkt.write_text(json.dumps([1, 2, 3]), encoding="utf-8")
    rc = gate.main([str(pkt)])
    assert rc == 2


def test_gate_scans_directory_recursively(tmp_path: Path, gate) -> None:
    subdir = tmp_path / "nested"
    subdir.mkdir()
    (subdir / "a.json").write_text(json.dumps(_clean_packet_dict()), encoding="utf-8")
    (subdir / "b.json").write_text(json.dumps(_clean_packet_dict()), encoding="utf-8")
    rc = gate.main([str(tmp_path)])
    assert rc == 0


def test_gate_aggregates_multiple_bad_packets(
    tmp_path: Path, gate, capsys: pytest.CaptureFixture[str]
) -> None:
    for i, broken_key in enumerate(("task_block", "policy_block")):
        data = _clean_packet_dict()
        data[broken_key] = "no directive"
        data["policy_block" if broken_key == "task_block" else "task_block"] = "x"
        (tmp_path / f"bad_{i}.json").write_text(json.dumps(data), encoding="utf-8")
    rc = gate.main([str(tmp_path)])
    assert rc == 1
    err = capsys.readouterr().err
    assert "2 C5 PA contract violation" in err or "violation(s) across 2" in err


def test_gate_ok_when_no_packets_found(tmp_path: Path, gate, capsys: pytest.CaptureFixture[str]) -> None:
    rc = gate.main([str(tmp_path)])
    assert rc == 0
    assert "no prompt packets to lint" in capsys.readouterr().out


def test_gate_warns_on_missing_path(tmp_path: Path, gate, capsys: pytest.CaptureFixture[str]) -> None:
    rc = gate.main([str(tmp_path / "does-not-exist.json")])
    assert rc == 0  # no packets collected → clean
    err = capsys.readouterr().err
    assert "skipping missing path" in err
