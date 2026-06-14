"""Unit tests for agentic_core.runtime.gates.gate_profile_resolver.

Wave 6.1 (P2 untested-module coverage) — declarative gate-profile loader.
Generic core: fails closed (GateProfileError) on missing/malformed profiles.
Covers GateProfile dataclass defaults, resolve() happy path, required-key
validation, runtime-gate merge precedence (exit profile wins on conflict),
and the two GateProfileError fail-closed branches. Uses real temp JSON files.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agentic_core.runtime.gates.gate_profile_resolver import (
    GateProfile,
    GateProfileError,
    GateProfileResolver,
)


def _write(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


_MINIMAL_EXIT = {
    "exit_profile_id": "ep-1",
    "app_id": "apps_demo",
    "task_class": "generation",
    "version": "1.0",
    "required_exit_gates": ["X1A", "X1B"],
    "conditional_exit_gates": ["X1C"],
    "gate_definitions": {"X1A": {"severity": "hard_fail"}},
    "conditional_gate_triggers": {"X1C": {"when": "always"}},
}


class TestGateProfileDataclass:
    def test_defaults(self) -> None:
        gp = GateProfile()
        assert gp.profile_id == ""
        assert gp.required_exit_gates == ()
        assert gp.gate_definitions == {}
        assert gp.runtime_gate_profile == {}

    def test_mutable_not_frozen(self) -> None:
        gp = GateProfile()
        gp.profile_id = "x"  # frozen=False — assignment allowed
        assert gp.profile_id == "x"


class TestResolveHappyPath:
    def test_resolve_populates_fields(self, tmp_path: Path) -> None:
        _write(tmp_path / "exit.json", _MINIMAL_EXIT)
        gp = GateProfileResolver(tmp_path).resolve("exit.json")
        assert gp.profile_id == "ep-1"
        assert gp.app_id == "apps_demo"
        assert gp.task_class == "generation"
        assert gp.version == "1.0"
        assert gp.required_exit_gates == ("X1A", "X1B")
        assert gp.conditional_exit_gates == ("X1C",)
        assert gp.gate_definitions == {"X1A": {"severity": "hard_fail"}}
        assert gp.conditional_gate_triggers == {"X1C": {"when": "always"}}
        assert gp.raw_exit_profile == _MINIMAL_EXIT

    def test_resolve_without_runtime_profile_empty_runtime(self, tmp_path: Path) -> None:
        _write(tmp_path / "exit.json", _MINIMAL_EXIT)
        gp = GateProfileResolver(tmp_path).resolve("exit.json")
        assert gp.runtime_gate_profile == {}
        assert gp.raw_runtime_profile == {}


class TestRuntimeMerge:
    def test_runtime_adds_new_gate(self, tmp_path: Path) -> None:
        _write(tmp_path / "exit.json", _MINIMAL_EXIT)
        _write(tmp_path / "rt.json", {"gate_rules": {"G21": {"severity": "warn"}}})
        gp = GateProfileResolver(tmp_path).resolve("exit.json", "rt.json")
        assert gp.gate_definitions["G21"] == {"severity": "warn"}
        assert "X1A" in gp.gate_definitions

    def test_exit_profile_wins_on_conflict(self, tmp_path: Path) -> None:
        _write(tmp_path / "exit.json", _MINIMAL_EXIT)
        # Runtime supplies X1A with different severity + an extra field.
        _write(
            tmp_path / "rt.json",
            {"gate_rules": {"X1A": {"severity": "warn", "extra": "added"}}},
        )
        gp = GateProfileResolver(tmp_path).resolve("exit.json", "rt.json")
        # Exit value wins for the conflicting key, runtime-only field is merged in.
        assert gp.gate_definitions["X1A"]["severity"] == "hard_fail"
        assert gp.gate_definitions["X1A"]["extra"] == "added"


class TestFailClosed:
    def test_missing_file_raises(self, tmp_path: Path) -> None:
        with pytest.raises(GateProfileError, match="not found"):
            GateProfileResolver(tmp_path).resolve("nope.json")

    def test_malformed_json_raises(self, tmp_path: Path) -> None:
        (tmp_path / "bad.json").write_text("{not valid json", encoding="utf-8")
        with pytest.raises(GateProfileError, match="malformed JSON"):
            GateProfileResolver(tmp_path).resolve("bad.json")

    def test_missing_required_key_raises(self, tmp_path: Path) -> None:
        _write(tmp_path / "partial.json", {"required_exit_gates": ["X1A"]})
        with pytest.raises(GateProfileError, match="gate_definitions"):
            GateProfileResolver(tmp_path).resolve("partial.json")

    def test_missing_runtime_file_raises(self, tmp_path: Path) -> None:
        _write(tmp_path / "exit.json", _MINIMAL_EXIT)
        with pytest.raises(GateProfileError, match="not found"):
            GateProfileResolver(tmp_path).resolve("exit.json", "missing_rt.json")
