"""Aggregate Anthropic prompt-cache receipts across an apps_rg suite artifact tree.

The summary is an observability artifact. It never changes X2/X1D/X3 outcomes and
never writes durable L4 state. Self-consistency lane summaries are preferred over
their last-writer-wins per-call receipt so every in-memory path receipt is counted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

SUITE_SUMMARY_SCHEMA = "apps_rg_anthropic_cache_suite_summary_v1"
DEFAULT_SUITE_SUMMARY_FILENAME = "anthropic_cache_suite_summary.json"

_STANDALONE_RECEIPT_GLOBS: tuple[str, ...] = (
    "**/provider_cache_receipt*.json",
    "**/bullet_pool_selector_cache_receipt*.json",
    "**/x1d_*anthropic_judge_cache_receipt*.json",
    "**/anthropic_cache_live_probe_receipt*.json",
)

_NUMERIC_TOTAL_FIELDS: tuple[str, ...] = (
    "input_tokens",
    "output_tokens",
    "cache_creation_input_tokens",
    "cache_creation_5m_input_tokens",
    "cache_creation_1h_input_tokens",
    "cache_read_input_tokens",
    "estimated_uncached_input_tokens",
    "estimated_cached_input_tokens",
    "estimated_input_token_savings",
    "estimated_input_cost_without_cache_usd",
    "estimated_input_cost_with_cache_usd",
    "estimated_input_cost_savings_usd",
)


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return loaded if isinstance(loaded, dict) else None


def _number(value: Any) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def _receipt_identity(receipt: Mapping[str, Any], source: str) -> str:
    payload = {
        "source": source,
        "provider": receipt.get("provider"),
        "model": receipt.get("model"),
        "section_id": receipt.get("section_id"),
        "run_id": receipt.get("run_id"),
        "input_payload_hash": receipt.get("input_payload_hash"),
        "effective_cached_prefix_hash": receipt.get("effective_cached_prefix_hash"),
        "cache_creation_input_tokens": receipt.get("cache_creation_input_tokens"),
        "cache_read_input_tokens": receipt.get("cache_read_input_tokens"),
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()[:24]


def _normalize_receipt(receipt: Mapping[str, Any], *, source: str) -> dict[str, Any]:
    out = dict(receipt)
    out["receipt_source"] = source
    out["receipt_id"] = _receipt_identity(out, source)
    return out


def discover_cache_receipts(root: Path | str) -> list[dict[str, Any]]:
    """Discover de-duplicated leaf cache receipts under ``root``.

    A ``lane_cache_summary.json`` contains every self-consistency path receipt,
    while ``provider_cache_receipt.json`` in that same directory contains only
    the last completed path. The lane summary therefore wins for that directory.
    """
    suite_root = Path(root).resolve()
    lane_summary_dirs: set[Path] = set()
    receipts: list[dict[str, Any]] = []

    for path in sorted(suite_root.glob("**/lane_cache_summary.json")):
        doc = _read_json(path)
        if not doc:
            continue
        nested = doc.get("receipts")
        if not isinstance(nested, list):
            continue
        lane_summary_dirs.add(path.parent.resolve())
        for index, receipt in enumerate(nested):
            if not isinstance(receipt, Mapping):
                continue
            source = f"{path.relative_to(suite_root).as_posix()}#receipt[{index}]"
            receipts.append(_normalize_receipt(receipt, source=source))

    seen_paths: set[Path] = set()
    for pattern in _STANDALONE_RECEIPT_GLOBS:
        for path in sorted(suite_root.glob(pattern)):
            resolved = path.resolve()
            if resolved in seen_paths:
                continue
            seen_paths.add(resolved)
            if path.name in {DEFAULT_SUITE_SUMMARY_FILENAME, "lane_cache_summary.json"}:
                continue
            if path.name.startswith("provider_cache_receipt") and path.parent.resolve() in lane_summary_dirs:
                continue
            doc = _read_json(path)
            if not doc:
                continue
            source = path.relative_to(suite_root).as_posix()
            receipts.append(_normalize_receipt(doc, source=source))

    unique: dict[str, dict[str, Any]] = {}
    for receipt in receipts:
        unique.setdefault(str(receipt["receipt_id"]), receipt)
    return list(unique.values())


def _group_summary(receipts: Sequence[Mapping[str, Any]], group_key: str) -> dict[str, Any]:
    grouped: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for receipt in receipts:
        key = str(receipt.get(group_key) or "unknown")
        grouped[key].append(receipt)
    out: dict[str, Any] = {}
    for key, rows in sorted(grouped.items()):
        out[key] = {
            "receipt_count": len(rows),
            "cache_creation_input_tokens": int(sum(_number(row.get("cache_creation_input_tokens")) for row in rows)),
            "cache_read_input_tokens": int(sum(_number(row.get("cache_read_input_tokens")) for row in rows)),
            "estimated_input_token_savings": round(
                sum(_number(row.get("estimated_input_token_savings")) for row in rows), 3
            ),
            "estimated_input_cost_savings_usd": round(
                sum(_number(row.get("estimated_input_cost_savings_usd")) for row in rows), 8
            ),
        }
    return out


def build_suite_cache_summary(
    receipts: Iterable[Mapping[str, Any]],
    *,
    suite_root: str = "",
) -> dict[str, Any]:
    rows = [dict(receipt) for receipt in receipts if isinstance(receipt, Mapping)]
    totals = {field: round(sum(_number(row.get(field)) for row in rows), 8) for field in _NUMERIC_TOTAL_FIELDS}
    creation = totals["cache_creation_input_tokens"]
    reads = totals["cache_read_input_tokens"]
    cache_ops = creation + reads
    live_rows = [
        row
        for row in rows
        if str(row.get("provider") or "") in {"external_claude", "anthropic_claude"}
        and row.get("input_tokens") is not None
    ]
    read_rows = [row for row in live_rows if _number(row.get("cache_read_input_tokens")) > 0]
    enabled_rows = [row for row in rows if bool(row.get("cache_enabled"))]
    warnings: list[dict[str, Any]] = []

    prefix_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        prefix = str(row.get("effective_cached_prefix_hash") or row.get("stable_prefix_hash") or "")
        if prefix:
            prefix_groups[prefix].append(row)
    for prefix, group in prefix_groups.items():
        if len(group) < 3:
            continue
        group_creation = sum(_number(row.get("cache_creation_input_tokens")) for row in group)
        group_reads = sum(_number(row.get("cache_read_input_tokens")) for row in group)
        if group_creation > 0 and group_reads == 0:
            warnings.append(
                {
                    "warning": "cache_miss_repeated_prefix_warning",
                    "effective_cached_prefix_hash": prefix,
                    "repeated_count": len(group),
                    "cache_creation_input_tokens": int(group_creation),
                    "cache_read_input_tokens": int(group_reads),
                }
            )

    return {
        "schema": SUITE_SUMMARY_SCHEMA,
        "suite_root": suite_root,
        "receipt_count": len(rows),
        "cache_enabled_receipt_count": len(enabled_rows),
        "live_anthropic_receipt_count": len(live_rows),
        "cache_read_receipt_count": len(read_rows),
        "cache_creation_input_tokens": int(creation),
        "cache_read_input_tokens": int(reads),
        "cache_hit_ratio": round(reads / cache_ops, 6) if cache_ops else None,
        "cache_hit_ratio_definition": (
            "sum(cache_read_input_tokens)/(sum(cache_creation_input_tokens)+sum(cache_read_input_tokens))"
        ),
        "estimated_uncached_input_tokens": int(round(totals["estimated_uncached_input_tokens"])),
        "estimated_cached_input_tokens": int(round(totals["estimated_cached_input_tokens"])),
        "estimated_input_token_savings": round(totals["estimated_input_token_savings"], 3),
        "estimated_input_cost_without_cache_usd": round(
            totals["estimated_input_cost_without_cache_usd"], 8
        ),
        "estimated_input_cost_with_cache_usd": round(
            totals["estimated_input_cost_with_cache_usd"], 8
        ),
        "estimated_input_cost_savings_usd": round(
            totals["estimated_input_cost_savings_usd"], 8
        ),
        "by_section": _group_summary(rows, "section_id"),
        "by_model": _group_summary(rows, "model"),
        "warnings": warnings,
        "receipts": rows,
    }


def write_suite_cache_summary(
    root: Path | str,
    *,
    output_path: Path | str | None = None,
) -> dict[str, Any]:
    suite_root = Path(root).resolve()
    receipts = discover_cache_receipts(suite_root)
    summary = build_suite_cache_summary(receipts, suite_root=suite_root.as_posix())
    output = Path(output_path).resolve() if output_path is not None else suite_root / DEFAULT_SUITE_SUMMARY_FILENAME
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    summary["output_path"] = output.as_posix()
    return summary


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", help="Suite or whole-run artifact root")
    parser.add_argument("--output", default="", help="Output JSON path")
    parser.add_argument(
        "--require-live-cache-read",
        action="store_true",
        help="Exit nonzero unless at least one live Anthropic receipt has cache-read tokens",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    summary = write_suite_cache_summary(args.root, output_path=args.output or None)
    print(json.dumps({key: value for key, value in summary.items() if key != "receipts"}, indent=2))
    if args.require_live_cache_read and int(summary.get("cache_read_input_tokens") or 0) <= 0:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
