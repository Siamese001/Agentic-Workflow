"""Deterministic section-quality report sealing and output."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from apps_rg.evals.resume_graph.reporting import canonical_digest


def report_digest(report: Mapping[str, Any]) -> str:
    """Digest a report without its self-referential digest field."""

    return canonical_digest({key: value for key, value in report.items() if key != "report_digest"})


def seal_report(report: Mapping[str, Any]) -> dict[str, Any]:
    """Return a report copy with a deterministic digest."""

    sealed = dict(report)
    sealed["report_digest"] = report_digest(sealed)
    return sealed


def report_digest_is_valid(report: Mapping[str, Any]) -> bool:
    digest = report.get("report_digest")
    return isinstance(digest, str) and digest == report_digest(report)


def write_report(report: Mapping[str, Any], path: Path, *, pretty: bool = True) -> None:
    """Write a deterministic UTF-8 JSON report to an operator-selected path."""

    payload = json.dumps(
        report,
        allow_nan=False,
        ensure_ascii=False,
        indent=2 if pretty else None,
        separators=None if pretty else (",", ":"),
        sort_keys=True,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload + "\n", encoding="utf-8")


__all__ = ["report_digest", "report_digest_is_valid", "seal_report", "write_report"]
