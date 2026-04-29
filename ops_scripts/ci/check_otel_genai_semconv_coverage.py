#!/usr/bin/env python3
"""Gate G-OTEL-GENAI-SEMCONV-COVERAGE — assert agent/workflow/tool spans align with semconv.

ADG consumer mode: ``inventory`` — this gate scans the filesystem for
emitter alignment; it does not consume ADG views.

Per ADR-074 (Runtime Bucket as OTEL View) and the 2026-04-29 user pivot,
the runtime bucket is a view over the OTel span sink. For that view to
remain interoperable with any OTel backend (Jaeger/Tempo/SigNoz/Anthropic/
OpenAI Traces), our spans MUST follow the OpenTelemetry GenAI SIG semantic
conventions:

    https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-agent-spans/

This gate scans Python files under the production roots that look like
they emit agent/workflow/tool spans (heuristic: file matches a producer
pattern OR contains a ``start_as_current_span``/``trace_span`` call) and
checks each one for alignment markers from
``agentic_core.L6_observability.semconv.gen_ai.ALIGNMENT_MARKERS``.

Tier: B (advisory). Threshold defaults to **80%** of detected emitters
must be aligned. Below 80%, reports the gap; above 80%, passes. Strict
mode (env var ``GENAI_SEMCONV_STRICT=1`` or ``--strict``) flips below-
threshold to exit 1.

Plan: ``.windsurf/plans/three-bucket-otel-view-5db409.md`` (W4.P4.2).

USAGE
=====

::

    python ops_scripts/ci/check_otel_genai_semconv_coverage.py
    python ops_scripts/ci/check_otel_genai_semconv_coverage.py --threshold 90
    python ops_scripts/ci/check_otel_genai_semconv_coverage.py --strict

Bypass: ``GENAI_SEMCONV_BYPASS=1``.
"""

from __future__ import annotations

# This gate scans filesystem source text; it does not query ADG views.
__adg_consumer_mode__ = "inventory"

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Final

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agentic_core.L6_observability.semconv.gen_ai import (  # noqa: E402
    ALIGNMENT_MARKERS,
)

REPORT_PATH: Final[Path] = (
    REPO_ROOT / "docs" / "reports" / "adg" / "otel_genai_semconv_gate_report.json"
)

# Production roots to scan.
SCAN_ROOTS: Final[tuple[str, ...]] = (
    "agentic_core",
    "system_learning",
    "tools/otel",
)

# Emitter-detection signature: a file is an "agent/workflow/tool span emitter"
# if it contains any of these tokens (rough heuristic).
EMITTER_SIGNATURES: Final[tuple[re.Pattern[str], ...]] = (
    re.compile(r"\bstart_as_current_span\b"),
    re.compile(r"\btracer\.start_span\b"),
    re.compile(r"\btrace_span\b"),
    re.compile(r"\bemit_span_to_runtime_adg\b"),
    re.compile(r"\bemit_spans_to_runtime_adg\b"),
    re.compile(r"\b_forward_to_runtime_adg\b"),
    re.compile(r"\bsl_span_with_ingest\b"),
)

# Emitter-detection paths: files matching these patterns are emitter-like
# regardless of content (helps include emitter modules whose span call lives
# in an imported helper).
EMITTER_PATH_PATTERNS: Final[tuple[re.Pattern[str], ...]] = (
    re.compile(r"runtime_span_emitter"),
    re.compile(r"otel_runtime_ingest"),
    re.compile(r"heal_router_otel"),
    re.compile(r"consensus_otel"),
    re.compile(r"_tracing\.py$"),
)

# Files explicitly excluded — schema, tests, generated code.
EXCLUDE_PATH_PATTERNS: Final[tuple[re.Pattern[str], ...]] = (
    re.compile(r"[/\\]semconv[/\\]"),  # the semconv module itself defines, doesn't emit
    re.compile(r"[/\\]tests[/\\]"),
    re.compile(r"[/\\]archives[/\\]"),
    re.compile(r"[/\\]_archived"),
    re.compile(r"[/\\]\.windsurf[/\\]"),
)


@dataclass
class FileResult:
    rel_path: str
    is_emitter: bool
    is_aligned: bool
    matched_marker: str = ""
    reason_emitter: str = ""


@dataclass
class GateResult:
    gate: str = "G-OTEL-GENAI-SEMCONV-COVERAGE"
    tier: str = "B"
    timestamp: str = ""
    threshold_pct: float = 80.0
    strict_mode: bool = False
    files_scanned: int = 0
    emitters_detected: int = 0
    emitters_aligned: int = 0
    emitters_unaligned: int = 0
    coverage_pct: float = 0.0
    status: str = "ok"
    unaligned_files: list[str] = field(default_factory=list)


def _excluded(path: Path) -> bool:
    p = str(path).replace("\\", "/")
    return any(rx.search(p) for rx in EXCLUDE_PATH_PATTERNS)


def _is_emitter_by_path(rel_path: str) -> str:
    for rx in EMITTER_PATH_PATTERNS:
        if rx.search(rel_path):
            return rx.pattern
    return ""


def _is_emitter_by_content(text: str) -> str:
    for rx in EMITTER_SIGNATURES:
        if rx.search(text):
            return rx.pattern
    return ""


def _is_aligned(text: str) -> tuple[bool, str]:
    for marker in ALIGNMENT_MARKERS:
        if marker in text:
            return True, marker
    return False, ""


def _scan(root: Path) -> list[FileResult]:
    results: list[FileResult] = []
    for py in root.rglob("*.py"):
        if _excluded(py):
            continue
        rel = str(py.relative_to(REPO_ROOT)).replace("\\", "/")
        try:
            text = py.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        path_match = _is_emitter_by_path(rel)
        content_match = _is_emitter_by_content(text)
        is_emitter = bool(path_match or content_match)
        if not is_emitter:
            continue

        is_aligned, marker = _is_aligned(text)
        results.append(
            FileResult(
                rel_path=rel,
                is_emitter=True,
                is_aligned=is_aligned,
                matched_marker=marker,
                reason_emitter=path_match or content_match,
            )
        )
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--threshold",
        type=float,
        default=80.0,
        help="Required alignment percentage (default 80.0)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Force strict mode (override GENAI_SEMCONV_STRICT env)",
    )
    args = parser.parse_args(argv)

    if os.environ.get("GENAI_SEMCONV_BYPASS") == "1":
        print("[otel_genai_semconv] bypass active (GENAI_SEMCONV_BYPASS=1)")
        return 0

    strict = args.strict or os.environ.get("GENAI_SEMCONV_STRICT") == "1"

    all_results: list[FileResult] = []
    for root_name in SCAN_ROOTS:
        root = REPO_ROOT / root_name
        if not root.exists():
            continue
        all_results.extend(_scan(root))

    detected = [r for r in all_results if r.is_emitter]
    aligned = [r for r in detected if r.is_aligned]
    unaligned = [r for r in detected if not r.is_aligned]
    total = len(detected)
    coverage_pct = (100.0 * len(aligned) / total) if total else 100.0

    result = GateResult(
        timestamp=datetime.now(timezone.utc).isoformat(),
        threshold_pct=args.threshold,
        strict_mode=strict,
        files_scanned=len(all_results),
        emitters_detected=total,
        emitters_aligned=len(aligned),
        emitters_unaligned=len(unaligned),
        coverage_pct=round(coverage_pct, 2),
        status="ok" if coverage_pct >= args.threshold else "below_threshold",
        unaligned_files=sorted(r.rel_path for r in unaligned),
    )

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        json.dumps(asdict(result), indent=2, default=str), encoding="utf-8"
    )

    print(
        f"[otel_genai_semconv] emitters={total} aligned={len(aligned)} "
        f"unaligned={len(unaligned)} coverage={coverage_pct:.1f}% "
        f"threshold={args.threshold:.1f}% strict={strict}"
    )
    if unaligned:
        print(f"[otel_genai_semconv] details written to {REPORT_PATH}")
        for r in unaligned[:10]:
            print(f"  - {r.rel_path} ({r.reason_emitter})")
        if len(unaligned) > 10:
            print(f"  ... +{len(unaligned) - 10} more")

    if coverage_pct >= args.threshold:
        return 0
    return 1 if strict else 0


if __name__ == "__main__":
    sys.exit(main())
