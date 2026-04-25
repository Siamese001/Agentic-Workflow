"""Tests for the BaselineRegistry bootstrap CLI tool."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agentic_core.L5_safety.runtime_gates.baseline_registry import BaselineRegistry
from tools.runtime_gates.bootstrap_baselines import (
    bootstrap,
    iter_records,
    main,
)


def _write_jsonl(path: Path, records: list[dict]) -> None:
    path.write_text("\n".join(json.dumps(r) for r in records) + "\n", encoding="utf-8")


def _write_json(path: Path, payload) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


# ---- iter_records ----


def test_iter_records_jsonl(tmp_path: Path) -> None:
    p = tmp_path / "traces.jsonl"
    _write_jsonl(p, [{"task_class": "summarize", "tokens": 100}, {"task_class": "translate", "tokens": 200}])
    out = list(iter_records(p))
    assert len(out) == 2
    assert out[0]["task_class"] == "summarize"


def test_iter_records_json_list(tmp_path: Path) -> None:
    p = tmp_path / "traces.json"
    _write_json(p, [{"task_class": "x", "tokens": 1}, {"task_class": "y", "tokens": 2}])
    out = list(iter_records(p))
    assert len(out) == 2


def test_iter_records_json_dict_with_records_key(tmp_path: Path) -> None:
    p = tmp_path / "traces.json"
    _write_json(p, {"records": [{"task_class": "a", "tokens": 5}]})
    out = list(iter_records(p))
    assert len(out) == 1
    assert out[0]["task_class"] == "a"


def test_iter_records_directory_recursive(tmp_path: Path) -> None:
    sub = tmp_path / "sub"
    sub.mkdir()
    _write_jsonl(tmp_path / "a.jsonl", [{"task_class": "x", "tokens": 1}])
    _write_json(sub / "b.json", [{"task_class": "y", "tokens": 2}])
    out = list(iter_records(tmp_path))
    assert {r["task_class"] for r in out} == {"x", "y"}


def test_iter_records_skips_malformed_jsonl(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    p = tmp_path / "bad.jsonl"
    p.write_text('{"task_class": "ok", "tokens": 1}\n{not valid\n', encoding="utf-8")
    out = list(iter_records(p))
    assert len(out) == 1


def test_iter_records_skips_malformed_json(tmp_path: Path) -> None:
    p = tmp_path / "bad.json"
    p.write_text("{not valid", encoding="utf-8")
    out = list(iter_records(p))
    assert out == []


# ---- bootstrap ----


def test_bootstrap_persists_to_target(tmp_path: Path) -> None:
    src = tmp_path / "src.jsonl"
    _write_jsonl(
        src,
        [
            {"task_class": "summarize", "tokens": 1000, "cost_usd": 0.05},
            {"task_class": "summarize", "tokens": 1100, "cost_usd": 0.06},
            {"task_class": "translate", "tokens": 500, "latency_ms": 200},
        ],
    )
    target = tmp_path / "baselines.json"
    stats = bootstrap(source=src, target=target)
    assert stats["records_seen"] == 3
    assert stats["records_accepted"] == 3
    assert set(stats["task_classes"]) == {"summarize", "translate"}
    assert target.exists()
    # Reload through registry to verify persisted shape.
    reloaded = BaselineRegistry(path=target)
    assert reloaded.has("summarize")
    assert reloaded.has("translate")


def test_bootstrap_skips_records_without_metric(tmp_path: Path) -> None:
    src = tmp_path / "src.jsonl"
    _write_jsonl(
        src,
        [
            {"task_class": "x", "tokens": 100},
            {"task_class": "x"},  # no metric
            {"tokens": 100},  # no task_class
        ],
    )
    target = tmp_path / "out.json"
    stats = bootstrap(source=src, target=target)
    assert stats["records_seen"] == 3
    assert stats["records_accepted"] == 1
    assert stats["records_skipped"] == 2


def test_bootstrap_dry_run_does_not_persist(tmp_path: Path) -> None:
    src = tmp_path / "src.jsonl"
    _write_jsonl(src, [{"task_class": "x", "tokens": 100}])
    target = tmp_path / "would-be.json"
    stats = bootstrap(source=src, target=target, dry_run=True)
    assert stats["dry_run"] is True
    assert stats["records_accepted"] == 1
    assert not target.exists()


def test_bootstrap_custom_task_class_key(tmp_path: Path) -> None:
    src = tmp_path / "src.jsonl"
    _write_jsonl(src, [{"task_type": "x", "tokens": 100}])
    target = tmp_path / "out.json"
    stats = bootstrap(source=src, target=target, task_class_key="task_type")
    assert stats["records_accepted"] == 1


def test_bootstrap_custom_alpha(tmp_path: Path) -> None:
    src = tmp_path / "src.jsonl"
    _write_jsonl(
        src,
        [
            {"task_class": "x", "tokens": 1000},
            {"task_class": "x", "tokens": 2000},
        ],
    )
    target = tmp_path / "out.json"
    bootstrap(source=src, target=target, alpha=0.5)
    reloaded = BaselineRegistry(path=target, alpha=0.5)
    # alpha=0.5: blend(1000, 2000) = 0.5*2000 + 0.5*1000 = 1500
    assert reloaded.get("x")["tokens"] == pytest.approx(1500.0)


def test_bootstrap_unknown_metric_ignored(tmp_path: Path) -> None:
    src = tmp_path / "src.jsonl"
    _write_jsonl(src, [{"task_class": "x", "tokens": 100, "garbage": "nope"}])
    target = tmp_path / "out.json"
    stats = bootstrap(source=src, target=target)
    assert stats["records_accepted"] == 1


# ---- main / CLI ----


def test_main_dry_run_prints_stats(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    src = tmp_path / "src.jsonl"
    _write_jsonl(src, [{"task_class": "x", "tokens": 100}])
    target = tmp_path / "out.json"
    rc = main(
        [
            "--source",
            str(src),
            "--target",
            str(target),
            "--dry-run",
        ]
    )
    assert rc == 0
    captured = capsys.readouterr().out
    payload = json.loads(captured)
    assert payload["records_accepted"] == 1
    assert payload["dry_run"] is True


def test_main_missing_source_returns_2(tmp_path: Path) -> None:
    rc = main(
        [
            "--source",
            str(tmp_path / "nope.jsonl"),
            "--target",
            str(tmp_path / "out.json"),
        ]
    )
    assert rc == 2


def test_main_persists_to_target(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    src = tmp_path / "src.jsonl"
    _write_jsonl(src, [{"task_class": "summarize", "tokens": 1000}])
    target = tmp_path / "baselines.json"
    rc = main(["--source", str(src), "--target", str(target)])
    assert rc == 0
    assert target.exists()
    capsys.readouterr()  # consume
