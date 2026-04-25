"""Bootstrap ``BaselineRegistry`` from historical OTEL trace records.

Usage:
    python tools/runtime_gates/bootstrap_baselines.py \
        --source path/to/traces.jsonl \
        --target artifacts/runtime_gates/baselines.json \
        [--alpha 0.2] [--task-class-key task_class] [--dry-run]

Source formats:
- ``.json``  — list of trace records, or dict with ``records`` key.
- ``.jsonl`` — one JSON record per line.
- directory — recursively load every ``.json`` and ``.jsonl`` file.

A trace record is a dict with at minimum ``task_class`` and one or more of
the metrics tracked by ``BaselineRegistry`` (``tokens``, ``cost_usd``,
``latency_ms``, ``tool_count``, ``retry_count``). Unknown fields are ignored.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from collections.abc import Iterable, Iterator
from pathlib import Path
from typing import Any

from agentic_core.L5_safety.runtime_gates.baseline_registry import (
    DEFAULT_ALPHA,
    TRACKED_METRICS,
    BaselineRegistry,
)

logger = logging.getLogger("runtime_gates.bootstrap")


def _iter_records_from_file(path: Path) -> Iterator[dict[str, Any]]:
    """Yield records from a single ``.json`` or ``.jsonl`` file."""
    suffix = path.suffix.lower()
    if suffix == ".jsonl":
        with path.open("r", encoding="utf-8") as fh:
            for line_no, line in enumerate(fh, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError as exc:
                    logger.warning("skipping malformed jsonl %s:%d: %s", path, line_no, exc)
                    continue
                if isinstance(record, dict):
                    yield record
        return
    if suffix == ".json":
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            logger.warning("skipping malformed json %s: %s", path, exc)
            return
        if isinstance(payload, list):
            for record in payload:
                if isinstance(record, dict):
                    yield record
            return
        if isinstance(payload, dict):
            records = payload.get("records") or payload.get("traces")
            if isinstance(records, list):
                for record in records:
                    if isinstance(record, dict):
                        yield record
                return
            # Treat the dict itself as a single record.
            yield payload
        return
    logger.debug("ignoring unsupported file %s", path)


def iter_records(source: Path) -> Iterator[dict[str, Any]]:
    """Yield records from a file or directory of files."""
    if source.is_dir():
        files = sorted(p for p in source.rglob("*") if p.suffix.lower() in {".json", ".jsonl"})
        for f in files:
            yield from _iter_records_from_file(f)
    else:
        yield from _iter_records_from_file(source)


def _record_observation(
    record: dict[str, Any],
    task_class_key: str,
) -> tuple[str, dict[str, float]] | None:
    """Extract (task_class, observation_dict) from a record. Returns None if invalid."""
    task_class = record.get(task_class_key) or record.get("task_class")
    if not task_class or not isinstance(task_class, str):
        return None
    observation: dict[str, float] = {}
    for metric in TRACKED_METRICS:
        if metric in record:
            try:
                observation[metric] = float(record[metric])
            except (TypeError, ValueError):
                continue
    if not observation:
        return None
    return task_class, observation


def bootstrap(
    source: Path,
    target: Path,
    *,
    alpha: float = DEFAULT_ALPHA,
    task_class_key: str = "task_class",
    dry_run: bool = False,
) -> dict[str, Any]:
    """Run the bootstrap. Returns a stats dict suitable for logging.

    When ``dry_run`` is True, the registry is built in-memory and never
    persisted; the stats dict still reflects what would have been written.
    """
    registry_path: Path | None = None if dry_run else target
    registry = BaselineRegistry(path=registry_path, alpha=alpha)

    seen_records = 0
    accepted = 0
    skipped = 0
    per_class_counts: dict[str, int] = {}
    for record in iter_records(source):
        seen_records += 1
        extracted = _record_observation(record, task_class_key)
        if extracted is None:
            skipped += 1
            continue
        task_class, observation = extracted
        registry.update(task_class, observation)
        accepted += 1
        per_class_counts[task_class] = per_class_counts.get(task_class, 0) + 1

    stats = {
        "source": str(source),
        "target": str(target),
        "alpha": alpha,
        "dry_run": dry_run,
        "records_seen": seen_records,
        "records_accepted": accepted,
        "records_skipped": skipped,
        "task_classes": sorted(per_class_counts),
        "samples_per_class": per_class_counts,
        "tracked_metrics": list(TRACKED_METRICS),
    }
    return stats


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        required=True,
        type=Path,
        help="path to a .json/.jsonl file or a directory of such files",
    )
    parser.add_argument(
        "--target",
        required=True,
        type=Path,
        help="destination JSON file for the BaselineRegistry persistence",
    )
    parser.add_argument(
        "--alpha",
        type=float,
        default=DEFAULT_ALPHA,
        help=f"EMA alpha for the registry (default {DEFAULT_ALPHA})",
    )
    parser.add_argument(
        "--task-class-key",
        default="task_class",
        help="dict key holding the task-class label in each record",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="do not persist; print stats only",
    )
    parser.add_argument("--verbose", action="store_true", help="DEBUG logging")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    parser = _build_arg_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    if not args.source.exists():
        logger.error("source not found: %s", args.source)
        return 2
    stats = bootstrap(
        source=args.source,
        target=args.target,
        alpha=args.alpha,
        task_class_key=args.task_class_key,
        dry_run=args.dry_run,
    )
    print(json.dumps(stats, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
