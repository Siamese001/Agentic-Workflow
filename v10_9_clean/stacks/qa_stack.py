"""Deterministic evidence fusion helpers."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List


def fuse_results(list_of_sources: Iterable[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    merged: List[Dict[str, Any]] = []
    for source in list_of_sources:
        for item in source:
            merged.append(dict(item))

    return sorted(merged, key=lambda r: (r.get("query", ""), r.get("rank", 0)))

