"""Common helpers for the per-axis validate_* runners (99.8 commands #4-#7)."""

from __future__ import annotations

import argparse
from pathlib import Path

from ..proof.bundle import read_bundle


def parse_args(description: str, argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--proof-bundle", required=True, help="Existing proof bundle directory.")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero on any failure.")
    return parser.parse_args(argv)


def load_bundle(path_str: str) -> dict:
    path = Path(path_str)
    if not (path / "bundle.json").exists():
        raise SystemExit(f"[ERROR] no bundle.json under {path}")
    return read_bundle(path)
