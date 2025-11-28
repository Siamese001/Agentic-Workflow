#!/usr/bin/env python3
"""Concatenate repository code into consolidated text bundles.

The script walks tracked text files in the repository and writes them into a
handful of consolidated parts for easier upload to ChatGPT. Files are grouped
sequentially based on their line counts so that the total set fits into at most
``max_parts`` outputs.
"""

from __future__ import annotations

import argparse
import math
import os
from pathlib import Path
from typing import Iterable, List

ROOT = Path(__file__).resolve().parent.parent


def is_text_file(path: Path) -> bool:
    """Return True when the file appears to be text, False for binary files."""
    try:
        with path.open("rb") as fh:
            chunk = fh.read(2048)
            return b"\0" not in chunk
    except OSError:
        return False


def iter_repo_files() -> Iterable[Path]:
    """Yield repo-tracked files under the root directory."""
    stream = os.popen("git ls-files")
    for line in stream:
        rel = line.strip()
        if not rel:
            continue
        path = ROOT / rel
        if not path.exists():
            continue
        if rel.startswith("consolidated/"):
            # Skip previously generated bundles.
            continue
        if path.is_dir():
            continue
        if not is_text_file(path):
            continue
        yield path


def compute_chunk_size(paths: Iterable[Path], max_parts: int) -> int:
    """Compute a chunk size (lines per part) to stay within max_parts."""
    total_lines = 0
    for path in paths:
        with path.open("r", encoding="utf-8", errors="replace") as fh:
            total_lines += sum(1 for _ in fh)
    return max(1, math.ceil(total_lines / max_parts))


def group_files(paths: List[Path], chunk_size: int, max_parts: int) -> List[List[Path]]:
    """Group paths into parts so that total lines per part stay near chunk_size."""
    parts: List[List[Path]] = [[]]
    current_lines = 0
    for path in paths:
        with path.open("r", encoding="utf-8", errors="replace") as fh:
            line_count = sum(1 for _ in fh)
        if current_lines + line_count > chunk_size and len(parts) < max_parts:
            parts.append([])
            current_lines = 0
        parts[-1].append(path)
        current_lines += line_count
    return parts


def write_parts(parts: List[List[Path]], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for index, group in enumerate(parts, start=1):
        target = output_dir / f"part_{index:02d}.txt"
        with target.open("w", encoding="utf-8", errors="replace") as out:
            for path in group:
                rel_path = path.relative_to(ROOT)
                out.write(f"==== {rel_path} ====" + "\n")
                with path.open("r", encoding="utf-8", errors="replace") as fh:
                    content = fh.read()
                if content and not content.endswith("\n"):
                    content += "\n"
                out.write(content)
                out.write("\n")
        print(f"Wrote {target}")


def build_parts(max_parts: int, output_dir: Path) -> None:
    tracked_files = sorted(iter_repo_files())
    if not tracked_files:
        raise SystemExit("No tracked text files found.")

    chunk_size = compute_chunk_size(tracked_files, max_parts)
    parts = group_files(tracked_files, chunk_size, max_parts)
    write_parts(parts, output_dir)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--max-parts",
        type=int,
        default=20,
        help="Maximum number of consolidated files to generate (default: 20)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("consolidated"),
        help="Directory for the consolidated files (default: ./consolidated)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    build_parts(max_parts=args.max_parts, output_dir=args.output_dir)
