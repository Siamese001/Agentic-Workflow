"""Hardening tests for ``tools/eval/ragbench_loader.py``.

The download path requires network + ``datasets`` and is exercised only
manually. These tests cover the offline contract: ``load_local`` and the
``check`` subcommand, plus a smoke test of the import-failure error
message for ``download_techqa``.
"""

from __future__ import annotations

import builtins
import json
from pathlib import Path

import pytest

from tools.eval.ragbench_loader import (
    _Row,
    _main,
    download_techqa,
    load_local,
)


def _write_fixture(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r))
            f.write("\n")


class TestLoadLocal:
    def test_round_trip(self, tmp_path: Path):
        fixture = tmp_path / "x.jsonl"
        _write_fixture(
            fixture,
            [
                {
                    "query_id": "q1",
                    "query": "what",
                    "relevant_passage_ids": ["p1"],
                    "passages": [{"id": "p1", "text": "answer"}],
                },
                {
                    "query_id": "q2",
                    "query": "how",
                    "relevant_passage_ids": ["p2", "p3"],
                    "passages": [
                        {"id": "p2", "text": "first"},
                        {"id": "p3", "text": "second"},
                    ],
                },
            ],
        )
        rows = load_local(fixture)
        assert len(rows) == 2
        assert rows[0].query_id == "q1"
        assert rows[1].relevant_passage_ids == ["p2", "p3"]
        assert all(isinstance(r, _Row) for r in rows)

    def test_skips_blank_lines(self, tmp_path: Path):
        fixture = tmp_path / "y.jsonl"
        with fixture.open("w", encoding="utf-8") as f:
            f.write("\n")
            f.write(
                json.dumps(
                    {
                        "query_id": "q1",
                        "query": "x",
                        "relevant_passage_ids": ["p1"],
                        "passages": [{"id": "p1", "text": "y"}],
                    }
                )
            )
            f.write("\n\n")
        rows = load_local(fixture)
        assert len(rows) == 1


class TestDownloadFailureMessage:
    def test_missing_datasets_raises_runtime_error(self, monkeypatch, tmp_path: Path):
        real_import = builtins.__import__

        def fail_datasets(name, *args, **kwargs):
            if name == "datasets":
                raise ImportError("simulated absence")
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", fail_datasets)
        with pytest.raises(RuntimeError, match="datasets"):
            download_techqa(tmp_path / "out.jsonl", n=1)


class TestCLI:
    def test_check_subcommand_validates(self, tmp_path: Path, capsys):
        fixture = tmp_path / "ok.jsonl"
        _write_fixture(
            fixture,
            [
                {
                    "query_id": "q1",
                    "query": "x",
                    "relevant_passage_ids": ["p1"],
                    "passages": [{"id": "p1", "text": "y"}],
                }
            ],
        )
        rc = _main(["check", "--path", str(fixture)])
        assert rc == 0
        captured = capsys.readouterr()
        assert "Loaded 1 rows" in captured.out

    def test_check_subcommand_flags_missing_gold(self, tmp_path: Path):
        fixture = tmp_path / "bad.jsonl"
        _write_fixture(
            fixture,
            [
                {
                    "query_id": "q1",
                    "query": "x",
                    "relevant_passage_ids": [],
                    "passages": [{"id": "p1", "text": "y"}],
                }
            ],
        )
        rc = _main(["check", "--path", str(fixture)])
        assert rc == 1
