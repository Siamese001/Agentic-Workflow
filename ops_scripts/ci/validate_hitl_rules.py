"""
HITL Rules CI Validator — checks the HITL rule corpus for correct schema sections.

Three validators:
  validate_yaml_config_section  — §HITL-9 threshold config (yaml-fenced OR plaintext)
  validate_option_shape_section — §HITL-10 option shape fields (bold-markdown-tolerant)
  validate_no_hardcoded_2to4    — forbidden 2-4 count patterns + required pipeline
                                    patterns (corpus-wide)

CORPUS MODE (default when >1 file provided):
    §HITL-9 / §HITL-10 section checks run per-file (the section must live
    somewhere in a single canonical file). Pipeline-pattern checks run
    across the union of file contents — the patterns may appear in any
    file of the HITL rule corpus. This matches the post-consolidation
    layout where enforcement.md holds pipeline patterns and
    decision-points.md holds the §HITL-9 / §HITL-10 sections.

Exit codes (when run as __main__):
    0 — all checks passed
    1 — violations found

Usage:
    python ops_scripts/ci/validate_hitl_rules.py <file> [<file> ...]
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]

# ---------------------------------------------------------------------------
# §HITL-9 threshold config validator
# ---------------------------------------------------------------------------

# Required thresholds. Accepted in either yaml-fenced blocks OR plaintext
# ``key: value`` presentation. ``allow_single_option_hitl: true`` was dropped
# during the 2026-Q1 HITL rule consolidation and is NO LONGER required.
_HITL9_REQUIRED_KEYS = [
    "surface_threshold: 0.72",
    "dominance_score_threshold: 0.85",
    "dominance_delta: 0.12",
]


def _read_text(path: Path) -> tuple[str | None, str | None]:
    try:
        return path.read_text(encoding="utf-8"), None
    except (OSError, UnicodeDecodeError) as exc:
        return None, f"{type(exc).__name__}: {exc}"


def validate_yaml_config_section(path: Path) -> list[str]:
    """Return list of error strings for §HITL-9 threshold-config issues in *path*.

    When the file does not contain a §HITL-9 section at all, the file is
    treated as a non-§HITL-9-carrier and no errors are reported. This
    supports the post-consolidation layout where only one file in the
    corpus carries the canonical §HITL-9 section. Use
    :func:`validate_corpus_has_section` separately to ensure the corpus
    contains the section somewhere.
    """
    text, read_error = _read_text(path)
    errors: list[str] = []
    if read_error is not None or text is None:
        errors.append(f"file read failed: {read_error}")
        return errors

    if "\u00a7HITL-9" not in text:
        return errors  # non-carrier; corpus-level check is the source of truth

    match = re.search(r"##\s+\u00a7HITL-9[^\n]*\n(.*?)(?=\n##\s|\Z)", text, re.DOTALL)
    section = match.group(1) if match else text

    # Accept either yaml-fenced block OR plaintext key:value presentation.
    # Required keys must appear somewhere in the section either way.
    for key in _HITL9_REQUIRED_KEYS:
        if key not in section:
            errors.append(f"Required key missing from \u00a7HITL-9 section: {key}")

    return errors


# ---------------------------------------------------------------------------
# §HITL-10 option shape section validator
# ---------------------------------------------------------------------------

_HITL10_REQUIRED_FIELDS = [
    "decision_thesis:",
    "value_to_goal:",
    "key_tradeoffs:",
    "execution_impact:",
    "risk_profile:",
    "time_to_value:",
]


def _strip_markdown_bold(text: str) -> str:
    """Remove ``**...**`` bold markers so field-name matching is format-agnostic.

    Both ``**decision_thesis**:`` and ``decision_thesis:`` should satisfy a
    search for the literal ``decision_thesis:``. The rule corpus uses bold
    markdown for readability; the validator strips it before matching.
    """
    return re.sub(r"\*\*([^*]+)\*\*", r"\1", text)


def validate_option_shape_section(path: Path) -> list[str]:
    """Return list of error strings for §HITL-10 option shape issues in *path*.

    As with §HITL-9, files lacking a §HITL-10 section are treated as
    non-carriers and produce no errors here; corpus-level presence is
    verified separately by :func:`validate_corpus_has_section`.
    """
    text, read_error = _read_text(path)
    errors: list[str] = []
    if read_error is not None or text is None:
        errors.append(f"file read failed: {read_error}")
        return errors

    if "\u00a7HITL-10" not in text:
        return errors  # non-carrier; corpus-level check is the source of truth

    match = re.search(r"##\s+\u00a7HITL-10[^\n]*\n(.*?)(?=\n##\s|\Z)", text, re.DOTALL)
    section = match.group(1) if match else text

    # Strip markdown bold so ``**field**:`` also matches.
    section_plain = _strip_markdown_bold(section)

    for field in _HITL10_REQUIRED_FIELDS:
        if field not in section_plain:
            errors.append(f"Required field missing from \u00a7HITL-10 section: {field}")

    return errors


# ---------------------------------------------------------------------------
# Hardcoded 2-4 count pattern validator
# ---------------------------------------------------------------------------

_FORBIDDEN_PATTERNS: list[tuple[str, str]] = [
    ("Present 2-4 concrete options", "Present 2-4 concrete options"),
    (r"Options \(2-4\)", r"Options \(2-4\)"),
]

# Required pipeline patterns. Each entry is a list of *accepted* literal
# spellings; any one of them satisfies that row. This allows yaml-style
# (``surface_threshold: 0.72``) and python-style (``surface_threshold = 0.72``)
# to both count.
_REQUIRED_PATTERNS: list[tuple[list[str], str]] = [
    (["surface_threshold = 0.72", "surface_threshold: 0.72"], "surface_threshold = 0.72"),
    (["dominance rule"], "dominance rule"),
    (["Surface 1\u2013N options", "Surface 1-N options"], "Surface 1\u2013N options"),
    (["LOW_CONFIDENCE_AMBIGUITY"], "LOW_CONFIDENCE_AMBIGUITY"),
]


def validate_no_hardcoded_2to4(path: Path, corpus_text: str | None = None) -> list[str]:
    """Return list of error strings for forbidden / missing patterns.

    Forbidden patterns are checked per-file (any single file introducing
    the old 2-4 phrasing is a violation).

    Required patterns are checked against ``corpus_text`` when supplied —
    the union of all HITL rule file contents. When ``corpus_text`` is
    ``None`` (single-file legacy mode), the checks fall back to per-file
    matching for backward compatibility.
    """
    text, read_error = _read_text(path)
    errors: list[str] = []
    if read_error is not None or text is None:
        errors.append(f"file read failed: {read_error}")
        return errors

    for regex, label in _FORBIDDEN_PATTERNS:
        if re.search(regex, text):
            errors.append(f"Forbidden pattern found: {label}")

    haystack = corpus_text if corpus_text is not None else text
    for accepted, label in _REQUIRED_PATTERNS:
        if not any(spelling in haystack for spelling in accepted):
            errors.append(f"Required pattern missing: {label}")

    return errors


# ---------------------------------------------------------------------------
# Corpus-level presence check — at least one file must carry each section
# ---------------------------------------------------------------------------


def validate_corpus_has_section(paths: list[Path], section_marker: str) -> list[str]:
    """Ensure at least one file in the corpus contains ``section_marker``.

    Used for §HITL-9 and §HITL-10, which live in exactly one canonical
    file (``author-gate-decision-points.md``) after the 2026-Q1 consolidation.
    """
    for p in paths:
        text, _err = _read_text(p)
        if text and section_marker in text:
            return []
    return [f"No file in corpus contains section marker {section_marker!r}"]


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def _run(paths: list[Path]) -> int:
    if not paths:
        print("[SKIP] validate_hitl_rules: no files provided")
        return 0

    # Filter to existing files and build the corpus text for cross-file checks.
    existing: list[Path] = []
    exit_code = 0
    corpus_parts: list[str] = []
    for p in paths:
        if not p.exists():
            print(f"[MISSING_FILE] {p}", file=sys.stderr)
            exit_code = 1
            continue
        existing.append(p)
        text, read_err = _read_text(p)
        if text is not None:
            corpus_parts.append(text)
        elif read_err is not None:
            print(f"[READ_ERROR] {p}: {read_err}", file=sys.stderr)
            exit_code = 1

    if not existing:
        return exit_code

    corpus_text = "\n".join(corpus_parts)

    # Corpus-level presence checks — at least one file must carry §HITL-9 and §HITL-10.
    for marker in ("\u00a7HITL-9", "\u00a7HITL-10"):
        for e in validate_corpus_has_section(existing, marker):
            print(f"[corpus] {e}", file=sys.stderr)
            exit_code = 1

    # Per-file checks. Section validators are no-ops for non-carriers;
    # the hardcoded-2to4 validator uses the corpus for required-pattern lookup.
    for path in existing:
        for fn_name, fn in (
            ("validate_yaml_config_section", validate_yaml_config_section),
            ("validate_option_shape_section", validate_option_shape_section),
        ):
            for e in fn(path):
                print(f"[{fn_name}] {path}: {e}", file=sys.stderr)
                exit_code = 1
        for e in validate_no_hardcoded_2to4(path, corpus_text=corpus_text):
            print(f"[validate_no_hardcoded_2to4] {path}: {e}", file=sys.stderr)
            exit_code = 1

    return exit_code


if __name__ == "__main__":
    _paths = [Path(p) for p in sys.argv[1:]] if len(sys.argv) > 1 else []
    sys.exit(_run(_paths))
