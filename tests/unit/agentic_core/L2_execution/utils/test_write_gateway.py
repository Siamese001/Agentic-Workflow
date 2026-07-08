"""Targeted gap-closure tests for write_gateway atomic-write hardening.

Covers:
- _atomic_write_bytes happy path: content survives temp→final rename
- _atomic_write_bytes idempotent on overwrite: content is replaced
- WriteSizeCapError and WriteAmplificationError constructors (correct module + args)
- write_json uses atomic write: output is valid JSON with correct content
"""

from __future__ import annotations

import json

import pytest

_WRITE_GATEWAY = pytest.importorskip(
    "agentic_core.L2_execution.utils.write_gateway",
    reason="Write-gateway tests require agentic_core runtime modules",
)

WriteAmplificationError = _WRITE_GATEWAY.WriteAmplificationError
WriteSizeCapError = _WRITE_GATEWAY.WriteSizeCapError
_atomic_write_bytes = _WRITE_GATEWAY._atomic_write_bytes
_path_exists = _WRITE_GATEWAY._path_exists
_read_text = _WRITE_GATEWAY._read_text
write_json = _WRITE_GATEWAY.write_json
write_text = _WRITE_GATEWAY.write_text


def test_atomic_write_bytes_creates_file(tmp_path) -> None:
    target = tmp_path / "output.bin"
    _atomic_write_bytes(target, b"hello bytes")
    assert target.exists()
    assert target.read_bytes() == b"hello bytes"


def test_atomic_write_bytes_overwrites_existing(tmp_path) -> None:
    target = tmp_path / "output.bin"
    _atomic_write_bytes(target, b"first")
    _atomic_write_bytes(target, b"second")
    assert target.read_bytes() == b"second"


def test_atomic_write_bytes_no_temp_file_left(tmp_path) -> None:
    target = tmp_path / "output.bin"
    _atomic_write_bytes(target, b"data")
    tmp_files = [f for f in tmp_path.iterdir() if f.suffix == ".tmp"]
    assert tmp_files == [], f"Stale .tmp files after atomic write: {tmp_files}"


def test_atomic_write_bytes_uses_short_temp_prefix_for_windows_path_budget(tmp_path, monkeypatch) -> None:
    target = tmp_path / "component_scorecards.csv"
    observed: dict[str, str] = {}
    real_mkstemp = _WRITE_GATEWAY.tempfile.mkstemp

    def spy_mkstemp(*, dir: str, suffix: str, prefix: str) -> tuple[int, str]:
        observed["prefix"] = prefix
        return real_mkstemp(dir=dir, suffix=suffix, prefix=prefix)

    monkeypatch.setattr(_WRITE_GATEWAY.tempfile, "mkstemp", spy_mkstemp)
    _atomic_write_bytes(target, b"scorecards")

    assert target.read_bytes() == b"scorecards"
    assert observed["prefix"] == ".wg_"
    assert len(observed["prefix"]) < len(f".{target.stem}_")


def test_write_text_handles_windows_extended_final_path(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("AGENTIC_ALLOW_MUTATION_FOR_TESTS", "1")
    target_dir = tmp_path
    target_name = "l6_microstep_future_run_proposals.json"
    while len(str((target_dir / target_name).resolve())) < 270:
        target_dir = target_dir / "deep_path_segment_1234567890"
    target = target_dir / target_name

    write_text(target, '{"ok": true}\n', encoding="utf-8")

    assert _path_exists(target)
    assert json.loads(_read_text(target, encoding="utf-8"))["ok"] is True


def test_write_size_cap_error_carries_fields(tmp_path) -> None:
    p = tmp_path / "f.txt"
    err = WriteSizeCapError(p, proposed_bytes=20_000_000, max_bytes=10_485_760)
    assert err.proposed_bytes == 20_000_000
    assert err.max_bytes == 10_485_760
    assert "WRITE_SIZE_CAP_EXCEEDED" in str(err)


def test_write_amplification_error_carries_fields(tmp_path) -> None:
    p = tmp_path / "f.txt"
    err = WriteAmplificationError(p, original_bytes=100, proposed_bytes=500, growth_ratio=5.0)
    assert err.growth_ratio == 5.0
    assert "WRITE_AMPLIFICATION_DETECTED" in str(err)


def test_write_json_atomic_round_trip(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("AGENTIC_ALLOW_MUTATION_FOR_TESTS", "1")
    target = tmp_path / "result.json"
    write_json(target, {"key": "value", "num": 42})
    data = json.loads(target.read_text(encoding="utf-8"))
    assert data["key"] == "value"
    assert data["num"] == 42
