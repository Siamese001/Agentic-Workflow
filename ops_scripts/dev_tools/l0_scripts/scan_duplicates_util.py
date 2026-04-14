"""Scan for duplicate files across the codebase and generate deletion review recommendations."""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

from tabulate import tabulate


def _find_project_root() -> Path:
    current = Path(__file__).resolve().parent
    for candidate in (current, *current.parents):
        if (candidate / "l0_scripts").exists() and (candidate / "L0_routing_scripts").exists():
            return candidate
    return Path(__file__).resolve().parents[1]


def _iter_files(project_root: Path, extensions: set[str]):
    for path in project_root.rglob("*"):
        if "__pycache__" in path.parts or not path.is_file():
            continue
        if not extensions or path.suffix in extensions:
            yield path


def _digest_file(path: Path) -> tuple[int, str]:
    raw = path.read_bytes()
    return len(raw), hashlib.sha256(raw).hexdigest()


def scan_duplicates(project_root: Path, extensions: set[str], min_bytes: int) -> list[dict]:
    buckets: dict[tuple[int, str], list[Path]] = {}
    for path in _iter_files(project_root, extensions):
        try:
            size, digest = _digest_file(path)
        except OSError as exc:
            print(f"[scan-duplicates] unable to read {path}: {exc}", file=sys.stderr)
            continue
        if size < min_bytes:
            continue
        buckets.setdefault((size, digest), []).append(path)

    recommendations: list[dict] = []
    for (size, _digest), paths in buckets.items():
        if len(paths) < 2:
            continue
        ordered = sorted(paths, key=lambda item: str(item.relative_to(project_root)))
        keep = ordered[0]
        delete = ordered[1:]
        recommendations.append(
            {
                "keep": str(keep.relative_to(project_root)),
                "delete": [str(path.relative_to(project_root)) for path in delete],
                "rationale": "Exact byte-for-byte duplicate; keep lexicographically first path by default.",
                "size": size * len(delete),
                "file_type": keep.suffix or "<no-ext>",
            }
        )
    return sorted(recommendations, key=lambda item: item["keep"])


def _print_report(recommendations: list[dict]) -> None:
    print("=" * 80)
    print("DUPLICATE FILE SCAN")
    print("=" * 80)
    print()
    print(f"Found {len(recommendations)} duplicate sets")
    print()
    if not recommendations:
        print("No duplicates found!")
        return
    table_data = []
    for index, rec in enumerate(recommendations, start=1):
        table_data.append(
            [
                index,
                rec["file_type"],
                f"{rec['size'] / 1024:.1f} KB",
                rec["keep"],
                "\n".join(rec["delete"]),
                rec["rationale"],
            ]
        )
    headers = ["#", "Type", "Reclaimable", "Keep", "Delete", "Rationale"]
    print(tabulate(table_data, headers=headers, tablefmt="grid", maxcolwidths=[None, None, None, 48, 48, 42]))
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total duplicate sets: {len(recommendations)}")
    print(f"Total files to delete: {sum(len(rec['delete']) for rec in recommendations)}")
    print(f"Total space to reclaim: {sum(rec['size'] for rec in recommendations) / 1024:.1f} KB")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scan for exact duplicate files")
    parser.add_argument(
        "--extensions",
        nargs="*",
        default=[".py"],
        help="File extensions to include, for example .py .md; omit for all files",
    )
    parser.add_argument("--min-bytes", type=int, default=1, help="Ignore files smaller than this size")
    args = parser.parse_args(argv)

    project_root = _find_project_root()
    extensions = {ext if ext.startswith(".") else f".{ext}" for ext in args.extensions if ext}
    recommendations = scan_duplicates(project_root, extensions, max(args.min_bytes, 0))
    _print_report(recommendations)
    return 0


if __name__ == "__main__":
    sys.exit(main())
