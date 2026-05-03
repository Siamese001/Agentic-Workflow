"""Emit ExecutiveBriefEnvelope sidecar for apps_exec artifacts.

Plan: apps-cross-app-precursors-c94c71 Wave 3.3 (GAP-3).

Dual-write: exec_brief_*.md is untouched; a sibling
exec_brief_<trace>.envelope.json is produced.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from apps_shared.contracts.cross_app.executive_brief import (
    ExecutiveBriefEnvelope,
    ExecutiveBriefPayload,
)

_DEFAULT_EXEC_DIR = Path("reports/executive")
_BRIEF_RE = re.compile(r"^exec_brief_[\w-]+_([0-9a-f]+)\.md$")
_BULLET_RE = re.compile(r"^\s*[-*]\s+(.+?)\s*$", re.MULTILINE)
_THESIS_RE = re.compile(
    r"^##\s+(?:Thesis|Executive Summary)\s*$\n?(.*?)(?=^##\s|\Z)",
    re.MULTILINE | re.DOTALL | re.IGNORECASE,
)


def _latest_brief(exec_dir: Path) -> Path:
    if not exec_dir.is_dir():
        raise FileNotFoundError(f"Executive output directory not found: {exec_dir}")
    candidates = sorted(
        exec_dir.glob("exec_brief_*.md"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not candidates:
        raise FileNotFoundError(f"No exec_brief_*.md files in {exec_dir}")
    return candidates[0]


def _trace_id_from_name(path: Path) -> str:
    m = _BRIEF_RE.match(path.name)
    return m.group(1) if m else path.stem


def build_payload(brief_path: Path, *, max_patterns: int = 5) -> ExecutiveBriefPayload:
    text = brief_path.read_text(encoding="utf-8")
    bullets = [m.group(1).strip() for m in _BULLET_RE.finditer(text)]
    close_patterns = [
        b for b in bullets if not b.startswith("[") and len(b) <= 200
    ][:max_patterns]
    thesis_match = _THESIS_RE.search(text)
    thesis_lines: list[str] = []
    if thesis_match:
        thesis_lines = [
            ln.strip() for ln in thesis_match.group(1).splitlines() if ln.strip()
        ]
    return ExecutiveBriefPayload(
        brief_path=str(brief_path).replace("\\", "/"),
        close_patterns=close_patterns,
        thesis_lines=thesis_lines,
    )


def emit(
    *,
    brief_path: Path | None = None,
    exec_dir: Path | None = None,
    trace_id: str | None = None,
    out_path: Path | None = None,
) -> Path:
    if brief_path is None:
        exec_dir = exec_dir or _DEFAULT_EXEC_DIR
        brief_path = _latest_brief(exec_dir)
    if not brief_path.is_file():
        raise FileNotFoundError(f"Executive brief not found: {brief_path}")

    trace_id = trace_id or _trace_id_from_name(brief_path)
    payload = build_payload(brief_path)
    env = ExecutiveBriefEnvelope.emit(trace_id=trace_id, payload=payload)
    if out_path is None:
        out_path = env.default_sidecar_path(brief_path.parent)
    env.write_sidecar(out_path)
    return out_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--brief", type=Path, default=None)
    parser.add_argument("--exec-dir", type=Path, default=None)
    parser.add_argument("--trace-id", default=None)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(argv)

    written = emit(
        brief_path=args.brief,
        exec_dir=args.exec_dir,
        trace_id=args.trace_id,
        out_path=args.out,
    )
    print(f"Wrote {written}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
