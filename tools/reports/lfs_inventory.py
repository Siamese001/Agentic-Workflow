#!/usr/bin/env python3
"""Generate a local Git LFS inventory report.

Read-only diagnostic for GitHub LFS billing investigations. It does not mutate
history, refs, LFS tracking, or remote objects. It shells out to:

    git lfs ls-files --all --size

and writes deterministic inventory files under artifacts/reports/lfs_inventory/
by default.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

LFS_LINE_RE = re.compile(
    r"^(?P<oid>[0-9a-fA-F]+)\s+"
    r"(?P<attrs>\S+)\s+"
    r"(?P<path>.*?)\s+"
    r"\((?P<size>[0-9]+(?:\.[0-9]+)?)\s*(?P<unit>B|KB|MB|GB|TB)\)\s*$"
)
UNIT_BYTES = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3, "TB": 1024**4}

RISK_BUCKETS: tuple[tuple[str, str], ...] = (
    ("06_data", "06_data/"),
    ("semantic_cache", "semantic_cache/"),
    ("artifacts_adg", "artifacts/adg/"),
    ("legacy_adg_archives", "artifacts/_legacy_adg_archives/"),
    ("adg_clean", "artifacts/adg_clean/"),
    ("test_enforcement_artifacts", "artifacts/reports/test_enforcement/"),
    ("data_cache", "data/cache/"),
    ("data_processed", "data/processed/"),
    ("data_snapshots", "data/snapshots/"),
)
RISK_EXTENSIONS = {".sqlite", ".db", ".zip", ".gz", ".pkl", ".pb", ".embedding", ".ast"}


@dataclass(frozen=True)
class LfsEntry:
    oid: str
    attrs: str
    path: str
    size_bytes: int
    size_display: str
    bucket: str
    extension: str


def run_git_lfs() -> str:
    cmd = ["git", "lfs", "ls-files", "--all", "--size"]
    try:
        result = subprocess.run(
            cmd,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except FileNotFoundError as exc:
        raise SystemExit("git is not installed or not available on PATH") from exc

    if result.returncode != 0:
        raise SystemExit(
            "git lfs inventory command failed. Ensure git-lfs is installed and run "
            "from the repository root.\n\n"
            f"Command: {' '.join(cmd)}\n"
            f"stderr:\n{result.stderr.strip()}"
        )
    return result.stdout


def parse_size(value: str, unit: str) -> int:
    return int(float(value) * UNIT_BYTES[unit])


def classify_bucket(path: str) -> str:
    normalized = path.replace("\\", "/")
    for bucket, marker in RISK_BUCKETS:
        if marker in normalized or normalized.startswith(marker):
            return bucket
    suffix = Path(normalized).suffix.lower()
    if suffix in RISK_EXTENSIONS:
        return f"ext:{suffix}"
    return "other"


def parse_lfs_lines(raw: str) -> list[LfsEntry]:
    entries: list[LfsEntry] = []
    skipped: list[str] = []
    for line in raw.splitlines():
        if not line.strip():
            continue
        match = LFS_LINE_RE.match(line)
        if not match:
            skipped.append(line)
            continue
        size_bytes = parse_size(match.group("size"), match.group("unit"))
        path = match.group("path")
        entries.append(
            LfsEntry(
                oid=match.group("oid"),
                attrs=match.group("attrs"),
                path=path,
                size_bytes=size_bytes,
                size_display=f"{match.group('size')} {match.group('unit')}",
                bucket=classify_bucket(path),
                extension=Path(path).suffix.lower(),
            )
        )
    if skipped:
        raise SystemExit(
            "Could not parse one or more git-lfs output lines. Examples:\n"
            + "\n".join(skipped[:10])
        )
    return entries


def summarize(entries: Iterable[LfsEntry]) -> dict[str, object]:
    rows = list(entries)
    total_bytes = sum(row.size_bytes for row in rows)
    by_bucket: dict[str, dict[str, int]] = {}
    by_extension: dict[str, dict[str, int]] = {}

    for row in rows:
        bucket = by_bucket.setdefault(row.bucket, {"count": 0, "bytes": 0})
        bucket["count"] += 1
        bucket["bytes"] += row.size_bytes

        ext_key = row.extension or "<none>"
        ext = by_extension.setdefault(ext_key, {"count": 0, "bytes": 0})
        ext["count"] += 1
        ext["bytes"] += row.size_bytes

    largest = sorted(rows, key=lambda item: item.size_bytes, reverse=True)[:50]
    return {
        "total_files": len(rows),
        "total_bytes": total_bytes,
        "total_human": human_bytes(total_bytes),
        "by_bucket": sort_summary(by_bucket),
        "by_extension": sort_summary(by_extension),
        "largest_files": [asdict(row) for row in largest],
    }


def sort_summary(data: dict[str, dict[str, int]]) -> list[dict[str, object]]:
    return [
        {
            "name": name,
            "count": values["count"],
            "bytes": values["bytes"],
            "human": human_bytes(values["bytes"]),
        }
        for name, values in sorted(data.items(), key=lambda item: item[1]["bytes"], reverse=True)
    ]


def human_bytes(num_bytes: int) -> str:
    value = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if value < 1024 or unit == "TB":
            return f"{value:.2f} {unit}"
        value /= 1024
    return f"{num_bytes} B"


def write_reports(entries: list[LfsEntry], out_dir: Path) -> dict[str, str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    sorted_entries = sorted(entries, key=lambda item: item.size_bytes, reverse=True)
    summary = summarize(sorted_entries)

    csv_path = out_dir / "lfs_inventory.csv"
    json_path = out_dir / "lfs_inventory_summary.json"
    md_path = out_dir / "lfs_inventory_summary.md"

    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["size_bytes", "size_display", "bucket", "extension", "path", "oid", "attrs"],
        )
        writer.writeheader()
        for row in sorted_entries:
            writer.writerow(asdict(row))

    json_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(render_markdown(summary), encoding="utf-8")
    return {"csv": str(csv_path), "json": str(json_path), "markdown": str(md_path)}


def render_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Git LFS Inventory Summary",
        "",
        f"Total LFS files: {summary['total_files']}",
        f"Total LFS size: {summary['total_human']} ({summary['total_bytes']} bytes)",
        "",
        "## By risk bucket",
        "",
        "| Bucket | Files | Size | Bytes |",
        "| --- | ---: | ---: | ---: |",
    ]
    for row in summary["by_bucket"]:  # type: ignore[index]
        lines.append(f"| {row['name']} | {row['count']} | {row['human']} | {row['bytes']} |")

    lines.extend([
        "",
        "## By extension",
        "",
        "| Extension | Files | Size | Bytes |",
        "| --- | ---: | ---: | ---: |",
    ])
    for row in summary["by_extension"]:  # type: ignore[index]
        lines.append(f"| {row['name']} | {row['count']} | {row['human']} | {row['bytes']} |")

    lines.extend([
        "",
        "## Largest files",
        "",
        "| Size | Bucket | Path |",
        "| ---: | --- | --- |",
    ])
    for row in summary["largest_files"]:  # type: ignore[index]
        lines.append(f"| {human_bytes(row['size_bytes'])} | {row['bucket']} | `{row['path']}` |")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a read-only Git LFS inventory report")
    parser.add_argument(
        "--out",
        default="artifacts/reports/lfs_inventory",
        help="Directory for generated reports. Default: artifacts/reports/lfs_inventory",
    )
    parser.add_argument("--json", action="store_true", help="Print summary JSON to stdout")
    args = parser.parse_args(argv)

    entries = parse_lfs_lines(run_git_lfs())
    summary = summarize(entries)
    paths = write_reports(entries, Path(args.out))

    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(f"LFS files: {summary['total_files']}")
        print(f"LFS size: {summary['total_human']} ({summary['total_bytes']} bytes)")
        print("Reports written:")
        for label, path in paths.items():
            print(f"  {label}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
