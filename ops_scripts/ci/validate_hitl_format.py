"""
HITL Format CI Validator — checks ask_user_question blocks in docs/rule files.

validate_file(path) returns a list of (location, violation_type) tuples.

Violation types:
  BANNED_OLD_FORMAT        — **Pros**: / **Cons**: / inline Pros: / Cons: patterns
  MISSING_CONFIDENCE_SCORE — option label missing [0.NN HIGH|MEDIUM|LOW]
  MISSING_DECISION_THESIS  — option description missing decision_thesis:
  MISSING_STAR_MARKER      — HIGH-confidence option (score >= 0.85) missing ⭐
  LOW_CONFIDENCE_SURFACED  — option with score < 0.72 surfaced in options block

Exit codes (when run as __main__):
    0 — no violations
    1 — violations found

Usage:
    python ops_scripts/ci/validate_hitl_format.py <file> [<file> ...]
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    from tqdm import tqdm
except ImportError:
    sys.exit("[FATAL] tqdm not installed — run: pip install tqdm")

_ROOT = Path(__file__).resolve().parents[2]

# Patterns that are banned regardless of context
_BANNED_PATTERNS = [
    r"\*\*Pros\*\*:",
    r"\*\*Cons\*\*:",
    r"\bPros:\s",
    r"\bCons:\s",
]

# Confidence score in option label: [0.NN HIGH|MEDIUM|LOW]
_CONFIDENCE_RE = re.compile(r"\[(\d+\.\d+)\s+(HIGH|MEDIUM|LOW)\]")

_HIGH_CONFIDENCE_THRESHOLD = 0.85
_SURFACE_THRESHOLD = 0.72


def _read_text(path: Path) -> tuple[str | None, str | None]:
    try:
        return path.read_text(encoding="utf-8"), None
    except (OSError, UnicodeDecodeError) as exc:
        return None, f"{type(exc).__name__}: {exc}"


def validate_file(path: Path) -> list[tuple[str, str]]:
    """Return list of (location, violation_type) tuples for HITL format issues in *path*."""
    text, read_error = _read_text(path)
    if read_error is not None or text is None:
        return [("file", f"FILE_READ_ERROR: {read_error}")]

    violations: list[tuple[str, str]] = []

    # 1. Global banned patterns (whole file, line by line)
    for i, line in enumerate(text.splitlines(), 1):
        for pattern in _BANNED_PATTERNS:
            if re.search(pattern, line):
                violations.append((f"line {i}", "BANNED_OLD_FORMAT"))
                break

    # 2. Per-option checks within ask_user_question blocks
    for ask_match in tqdm(
        list(re.finditer(r"ask_user_question\(", text)),
        desc="Scanning ask_user_question blocks",
        disable=True,
    ):
        block_start = ask_match.start()
        after_ask = text[block_start:]

        opts_match = re.search(r"options=\[", after_ask)
        if not opts_match:
            continue
        opts_start = block_start + opts_match.end()
        opts_text = text[opts_start:]

        label_matches = list(re.finditer(r'label:\s*"([^"]*)"', opts_text))
        desc_matches = list(re.finditer(r'description:\s*"([^"]*)"', opts_text))

        for idx, lm in tqdm(list(enumerate(label_matches)), desc="Validating options", disable=True):
            label_val = lm.group(1)
            desc_val = desc_matches[idx].group(1) if idx < len(desc_matches) else ""
            abs_pos = opts_start + lm.start()
            line_no = text[:abs_pos].count("\n") + 1
            loc = f"line {line_no}"

            score_match = _CONFIDENCE_RE.search(label_val)
            if not score_match:
                violations.append((loc, "MISSING_CONFIDENCE_SCORE"))
                continue

            score = float(score_match.group(1))

            if score >= _HIGH_CONFIDENCE_THRESHOLD and "\u2b50" not in label_val:
                violations.append((loc, "MISSING_STAR_MARKER"))

            if score < _SURFACE_THRESHOLD:
                violations.append((loc, "LOW_CONFIDENCE_SURFACED"))

            if "decision_thesis:" not in desc_val:
                violations.append((loc, "MISSING_DECISION_THESIS"))

    return violations


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def _run(paths: list[Path]) -> int:
    if not paths:
        print("[SKIP] validate_hitl_format: no files provided")
        return 0

    exit_code = 0
    for path in paths:
        if not path.exists():
            print(f"[MISSING_FILE] {path}", file=sys.stderr)
            exit_code = 1
            continue
        for loc, vtype in validate_file(path):
            print(f"[{vtype}] {path}:{loc}", file=sys.stderr)
            exit_code = 1
    return exit_code


if __name__ == "__main__":
    _paths = [Path(p) for p in sys.argv[1:]] if len(sys.argv) > 1 else []
    sys.exit(_run(_paths))
