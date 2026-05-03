"""Production-log mining skeleton — harvest eval samples from live runs.

Plan: `.windsurf/plans/apps-eval-harness-residual-a2d9c7.md` W3.P1.

Purpose
-------
Skeleton pipeline that reads production log streams (OTEL-derived JSONL),
applies a PII-redaction hook, and emits weekly eval-sample JSONL bundles
at `artifacts/eval_samples/<app>/<yyyy-ww>.jsonl` for later promotion
into `apps_eval/fixtures/dev/`.

This is a **skeleton** — the PII redactor is a stub that returns input
unchanged. Operators MUST wire a real redactor before the pipeline
runs against real traffic. A loud warning is logged at startup if the
redactor is still the stub.

Authority
---------
READ-ONLY. Writes only to `artifacts/eval_samples/`. Never mutates
production logs or app state.

Usage
-----
    python ops_scripts/calibration/production_log_miner.py \
        --input path/to/production.jsonl \
        --app apps_qna \
        --out artifacts/eval_samples/apps_qna/2026-W18.jsonl \
        --max-samples 500
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Mapping, Optional

Logger = logging.getLogger(__name__)

PiiRedactor = Callable[[Mapping[str, object]], Mapping[str, object]]


def _stub_pii_redactor(row: Mapping[str, object]) -> Mapping[str, object]:
    """PII-redactor stub. OPERATORS MUST REPLACE before real-traffic use."""
    return row


_REDACTOR: PiiRedactor = _stub_pii_redactor
_REDACTOR_IS_STUB: bool = True


def set_redactor(redactor: PiiRedactor) -> None:
    """Register the real redactor. Clears the stub warning."""
    global _REDACTOR, _REDACTOR_IS_STUB
    if not callable(redactor):
        raise TypeError("redactor must be callable")
    _REDACTOR = redactor
    _REDACTOR_IS_STUB = False


def is_stub_redactor() -> bool:
    return _REDACTOR_IS_STUB


@dataclass(frozen=True)
class MinerConfig:
    input_path: Path
    app_id: str
    out_path: Path
    max_samples: int = 500


def _iter_jsonl(path: Path) -> Iterable[Mapping[str, object]]:
    with path.open("r", encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as exc:
                Logger.warning("skipping malformed line %d in %s: %s", line_no, path, exc)


def _filter_for_app(row: Mapping[str, object], app_id: str) -> bool:
    return str(row.get("app_id", "")).strip() == app_id


def mine(config: MinerConfig) -> int:
    """Run the pipeline. Returns count of rows written."""
    if _REDACTOR_IS_STUB:
        Logger.warning(
            "[production_log_miner] PII REDACTOR IS STUB — do not run against real traffic "
            "without calling set_redactor() first"
        )
    config.out_path.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    with config.out_path.open("w", encoding="utf-8") as out:
        for row in _iter_jsonl(config.input_path):
            if not _filter_for_app(row, config.app_id):
                continue
            redacted = _REDACTOR(row)
            out.write(json.dumps(redacted, ensure_ascii=False, sort_keys=True) + "\n")
            written += 1
            if written >= config.max_samples:
                break
    Logger.info(
        "[production_log_miner] wrote %d samples for app_id=%s -> %s",
        written,
        config.app_id,
        config.out_path,
    )
    return written


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Mine production logs into eval samples")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--app", required=True, dest="app_id")
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--max-samples", type=int, default=500)
    parser.add_argument(
        "--force-stub",
        action="store_true",
        help="Allow running with the stub PII redactor (dev/testing only)",
    )
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    args = _build_parser().parse_args(argv)
    if _REDACTOR_IS_STUB and not args.force_stub:
        Logger.error(
            "PII redactor is the stub. Refusing to run without --force-stub. "
            "Wire a real redactor via set_redactor() first."
        )
        return 2
    cfg = MinerConfig(
        input_path=args.input,
        app_id=args.app_id,
        out_path=args.out,
        max_samples=args.max_samples,
    )
    count = mine(cfg)
    print(f"wrote {count} samples -> {cfg.out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
