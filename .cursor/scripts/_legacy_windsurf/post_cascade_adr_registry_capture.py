#!/usr/bin/env python3
"""post_cascade_adr_registry_capture.py — Windsurf post_cascade_response hook.

**REPURPOSED 2026-05-11 (plan notion-integration-consistency-audit-b2c4d8 W2):**
The Notion ADR Registry was archived 2026-05-02 as part of the Notion
consolidation commit (b11200e833). Filesystem is now the SSOT for ADRs.
This hook no longer writes to Notion; it logs detected ADR paths to the
filesystem JSONL only, providing an audit trail without dead-DB writes.

Original purpose: auto-post new ADR markdown files to the Notion ADR Registry.
Current purpose: detect ADR file references in Cascade responses, parse
metadata, and log to ``artifacts/windsurf/adr_registry_capture.jsonl``
(filesystem-only).

Detection
---------
Scan the response payload for ``docs/architecture/adr/ADR-<N>-<slug>.md``
(both forward and back slashes accepted; case-insensitive). For each unique
path:

  1. Verify the file exists on disk.
  2. Parse the ADR markdown header for: ADR ID, Title, Status, Decision Date,
     Deciders, Impact Layers (e.g. ``L1, L4``), and a Summary derived from the
     first paragraph under "Context".
  3. Log ``kind: adr_filesystem_only`` to JSONL — no Notion write.

Behavior (ADVISORY — always exits 0)
------------------------------------
- ADR file found → logged ``adr_filesystem_only``.
- File missing on disk → logged ``file_missing``, skipped.
- Parse failure → logged ``parse_error``, skipped.

Escape hatch: ADR_REGISTRY_CAPTURE_BYPASS=1
Fail policy: OPEN — any error → exit 0 silently.
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
CAPTURE_LOG = REPO_ROOT / "artifacts" / "windsurf" / "adr_registry_capture.jsonl"

# ADR Registry was archived 2026-05-02. No Notion imports needed.

# Hard cap on response payload bytes scanned for ADR paths. Defends against
# pathological inputs (logs, captured stdout, etc.) that would otherwise drag
# the hook into a multi-second regex run.
MAX_RESPONSE_BYTES = 512 * 1024  # 512 KB

# Hard cap on ADR file size before we'll parse it. Real ADRs are < 50 KB; a
# multi-MB file under the ADR directory is almost certainly not an ADR.
MAX_ADR_FILE_BYTES = 256 * 1024  # 256 KB

# Recognized ADR statuses in the Notion select column.
ALLOWED_STATUSES = {"Proposed", "Accepted", "Deprecated", "Superseded", "Rejected"}
DEFAULT_STATUS = "Proposed"

# Recognized impact-layer multi_select values. Includes the L_<NAMESPACE>
# values observed in the live ADR Registry (L_SHARED, L_TOOLS, L_APP, L_OPS,
# L_INFRA) so a path like ``apps_shared/...`` can map to ``L_SHARED``.
ALLOWED_LAYERS = {
    "L0",
    "L1",
    "L2",
    "L3",
    "L4",
    "L5",
    "L6",
    "L_SHARED",
    "L_TOOLS",
    "L_APP",
    "L_OPS",
    "L_INFRA",
}

# Path wiring for the shared payload extractor used by sibling hooks.
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))


# ---------------------------------------------------------------------------
# Path detection
# ---------------------------------------------------------------------------

# Match docs/architecture/adr/ADR-<digits>-<slug>.md with either separator.
# Numeric form only: alternate naming (e.g. ADR-PROMPT-ASSEMBLY-001) is
# logged as ``unsupported_naming`` and skipped — those rows already exist in
# Notion under a separate convention and the auto-poster declines to invent
# rules for them.
_ADR_PATH_RE = re.compile(
    r"docs[/\\]architecture[/\\]adr[/\\](ADR-\d+(?:-[A-Za-z0-9_\-]+)?\.md)",
    re.IGNORECASE,
)

# Detector for non-numeric ADR variants (telemetry-only).
_ADR_VARIANT_RE = re.compile(
    r"docs[/\\]architecture[/\\]adr[/\\](ADR-[A-Z][A-Z0-9_\-]*\.md)",
    re.IGNORECASE,
)

# ADR id token: "ADR-055" anywhere in title, filename, or first lines.
_ADR_ID_RE = re.compile(r"\bADR-(\d+)\b", re.IGNORECASE)

# Path tokens that, when present in the matched path, mean we should NOT
# auto-post even if the file exists. Defends against historical or archived
# ADR copies being picked up.
_PATH_EXCLUSIONS = ("archives/", "archives\\", "_smoke_", "/_archive/", "\\_archive\\")


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _append_log(record: dict[str, Any]) -> None:
    try:
        CAPTURE_LOG.parent.mkdir(parents=True, exist_ok=True)
        with CAPTURE_LOG.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError as exc:
        print(f"[adr_registry_capture] log write failed: {exc}", file=sys.stderr)


def _read_stdin_response() -> str:
    try:
        payload = sys.stdin.read()
    except (OSError, UnicodeDecodeError):
        return ""
    try:
        from _post_cascade_payload import extract_response_text  # noqa: PLC0415

        return extract_response_text(payload)
    except ImportError:
        try:
            obj = json.loads(payload)
            if isinstance(obj, dict):
                info = obj.get("tool_info") or {}
                return str(info.get("response") or obj.get("response") or payload)
        except (json.JSONDecodeError, ValueError):
            pass
        return payload


def _find_adr_filenames(response: str) -> tuple[list[str], list[str]]:
    """Return (numeric_filenames, unsupported_variants) found in the response.

    De-duplicates while preserving first-seen order. Excludes paths under
    ``archives/`` and similar quarantine prefixes.
    """

    numeric: dict[str, None] = {}
    variants: dict[str, None] = {}

    def _context_excluded(span_start: int) -> bool:
        # Inspect up to 64 chars preceding the match to detect exclusion
        # prefixes like ``archives/`` or ``_smoke_`` that sit OUTSIDE the
        # matched ``docs/architecture/adr/...`` span itself.
        head = response[max(0, span_start - 64) : span_start]
        return any(tok in head for tok in _PATH_EXCLUSIONS)

    for match in _ADR_PATH_RE.finditer(response):
        if _context_excluded(match.start()):
            continue
        numeric.setdefault(match.group(1), None)

    # Variants: only count a file once, and don't double-count if the same
    # filename also matched the numeric pattern (it can't, but defensively).
    for match in _ADR_VARIANT_RE.finditer(response):
        if _context_excluded(match.start()):
            continue
        filename = match.group(1)
        # Skip if the filename starts with ADR-<digits> (already in numeric).
        if re.match(r"ADR-\d+", filename, re.IGNORECASE):
            continue
        variants.setdefault(filename, None)

    return list(numeric.keys()), list(variants.keys())


# ---------------------------------------------------------------------------
# ADR markdown parsing
# ---------------------------------------------------------------------------


def _parse_header_field(text: str, label: str) -> str:
    """Extract a ``**Label**: value`` line from the ADR header block.

    Stops at first newline so multi-line fields (rare) only return the head.
    """

    pattern = re.compile(
        rf"^\s*\*\*{re.escape(label)}\*\*\s*:\s*(.+?)\s*$",
        re.IGNORECASE | re.MULTILINE,
    )
    match = pattern.search(text)
    if not match:
        return ""
    # Strip surrounding markdown emphasis on the value (e.g. "*Proposed*").
    value = match.group(1).strip()
    value = re.sub(r"^[*_`]+|[*_`]+$", "", value).strip()
    return value


def _normalize_status(raw: str) -> str:
    """Map a raw Status field to one of ALLOWED_STATUSES.

    Falls back to DEFAULT_STATUS so a typo never breaks the post. Splits on
    whitespace/parens because authors sometimes write "Proposed (rescoped 2026-04-23)".
    """

    if not raw:
        return DEFAULT_STATUS
    head = re.split(r"[\s()]+", raw.strip(), maxsplit=1)[0].strip().capitalize()
    if head in ALLOWED_STATUSES:
        return head
    # Some files use "Draft" — coerce to Proposed.
    if head.lower() in {"draft", "wip"}:
        return "Proposed"
    return DEFAULT_STATUS


def _parse_decision_date(raw: str) -> str:
    """Return YYYY-MM-DD or empty string. Tolerates parenthetical amendments."""

    if not raw:
        return ""
    match = re.search(r"\d{4}-\d{2}-\d{2}", raw)
    return match.group(0) if match else ""


def _parse_impact_layers(raw: str) -> list[str]:
    """Extract layer tokens from a free-form Impact Layers field.

    Recognizes:
    - Bare numeric tokens: ``L0`` ... ``L6``
    - Path-prefix numeric: ``agentic_core/L1_cognition/...`` (extracts ``L1``)
    - Namespace tokens: ``L_SHARED``, ``L_TOOLS``, ``L_APP``, ``L_OPS``,
      ``L_INFRA`` — both bare and path-prefix forms.

    Order is preserved for first-seen-wins; duplicates suppressed.
    """

    if not raw:
        return []
    layers: list[str] = []

    # Numeric layer tokens (bare or path-prefix).
    for match in re.finditer(r"\bL([0-6])(?:[_\s,()/\\.]|$)", raw):
        token = f"L{match.group(1)}"
        if token in ALLOWED_LAYERS and token not in layers:
            layers.append(token)

    # Namespace layer tokens (L_<UPPER>).
    for match in re.finditer(r"\bL_([A-Z]+)\b", raw):
        token = f"L_{match.group(1)}"
        if token in ALLOWED_LAYERS and token not in layers:
            layers.append(token)

    return layers


def _parse_deciders(raw: str) -> str:
    """Trim and bound deciders string. Empty string OK (Notion accepts blank)."""

    if not raw:
        return "Agentic-Workflow maintainers"
    # Cap at 200 chars so a verbose "Deciders" line doesn't blow the property.
    return raw.strip()[:200]


def _parse_title(text: str, fallback: str) -> str:
    """Pull the first H1 ``# ADR-NNN — Title`` and return just the Title part.

    Handles all common author separators between the ADR id and title: em-dash
    (—), en-dash (–), hyphen (-), colon (:), and combinations. Falls back to
    the raw H1 line when the prefix doesn't match.
    """

    match = re.search(r"^\s*#\s+(.+?)\s*$", text, re.MULTILINE)
    if not match:
        return fallback
    line = match.group(1).strip()
    # Accept em-dash, en-dash, hyphen, colon, and runs thereof.
    cleaned = re.sub(
        r"^ADR-\d+\s*[\u2014\u2013\-:]+\s*",
        "",
        line,
        flags=re.IGNORECASE,
    ).strip()
    return cleaned or line


def _parse_summary(text: str) -> str:
    """Return a one-paragraph Summary harvested from the Context section.

    Falls back to the first non-header paragraph after the header block.
    Capped at 1800 chars to fit Notion rich_text without truncation by the API.
    """

    # Prefer the first paragraph under "## Context".
    ctx_match = re.search(
        r"^##\s+Context\s*$\n+(.+?)(?=\n##\s|\Z)",
        text,
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )
    if ctx_match:
        block = ctx_match.group(1).strip()
        # Take only the first paragraph (split on blank line).
        paragraph = re.split(r"\n\s*\n", block, maxsplit=1)[0].strip()
        if paragraph:
            return _flatten_md(paragraph)[:1800]

    # Fallback: first paragraph after the metadata block (separator ``---``).
    after_meta = re.split(r"^---\s*$", text, maxsplit=1, flags=re.MULTILINE)
    body = after_meta[1] if len(after_meta) > 1 else text
    for paragraph in re.split(r"\n\s*\n", body):
        clean = paragraph.strip()
        if clean and not clean.startswith("#") and not clean.startswith("*"):
            return _flatten_md(clean)[:1800]
    return ""


def _flatten_md(text: str) -> str:
    """Reduce common markdown to plain prose for the Notion Summary cell."""

    # Strip bold/italic/inline-code markers but preserve the inner text.
    text = re.sub(r"`{1,3}([^`]+)`{1,3}", r"\1", text)
    text = re.sub(r"\*{1,2}([^*]+)\*{1,2}", r"\1", text)
    text = re.sub(r"_{1,2}([^_]+)_{1,2}", r"\1", text)
    # Collapse internal whitespace.
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _parse_adr_file(path: Path) -> dict[str, Any] | None:
    """Read and parse an ADR markdown file.

    Returns None on read failure, file too large, or missing ADR ID.
    """

    try:
        size = path.stat().st_size
    except OSError:
        return None
    if size > MAX_ADR_FILE_BYTES:
        return None

    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None

    filename = path.name
    id_match = _ADR_ID_RE.search(filename) or _ADR_ID_RE.search(text[:400])
    if not id_match:
        return None
    adr_id = f"ADR-{int(id_match.group(1)):03d}"

    # Header fields live in the lines immediately after the H1.
    header_block = text[: text.find("\n## ")] if "\n## " in text else text[:1500]

    return {
        "adr_id": adr_id,
        "filename": filename,
        "title": _parse_title(text, fallback=adr_id),
        "status": _normalize_status(_parse_header_field(header_block, "Status")),
        "decision_date": _parse_decision_date(_parse_header_field(header_block, "Date")),
        "deciders": _parse_deciders(_parse_header_field(header_block, "Deciders")),
        "impact_layers": _parse_impact_layers(_parse_header_field(header_block, "Impact Layers")),
        "summary": _parse_summary(text),
    }


# ---------------------------------------------------------------------------
# Main flow
# ---------------------------------------------------------------------------

def _process_filename(filename: str) -> dict[str, Any]:
    """Parse ADR file and return a filesystem-only log record.

    ADR Registry archived 2026-05-02; no Notion write is performed.
    """
    path = REPO_ROOT / "docs" / "architecture" / "adr" / filename
    if not path.is_file():
        return {
            "timestamp": _utc_now_iso(),
            "kind": "file_missing",
            "filename": filename,
            "resolved_path": str(path),
        }

    adr = _parse_adr_file(path)
    if adr is None:
        return {
            "timestamp": _utc_now_iso(),
            "kind": "parse_error",
            "filename": filename,
        }

    return {
        "timestamp": _utc_now_iso(),
        "kind": "adr_filesystem_only",
        "adr": adr,
        "note": "ADR Registry archived 2026-05-02; filesystem SSOT only",
    }


def main() -> int:
    if os.environ.get("ADR_REGISTRY_CAPTURE_BYPASS") == "1":
        _append_log(
            {
                "timestamp": _utc_now_iso(),
                "kind": "bypass",
                "reason": "ADR_REGISTRY_CAPTURE_BYPASS=1",
            }
        )
        return 0

    if sys.stdin.isatty():
        print(
            "[adr_registry_capture] no stdin payload (TTY detected) — exiting 0. "
            "This script is a post_cascade_response hook.",
            file=sys.stderr,
        )
        return 0

    response = _read_stdin_response()
    if not response:
        return 0
    # Bound the regex scan budget. Truncating preserves head-of-response
    # signal because the ADR paths are typically near the top in tool-call
    # arguments / write summaries, not buried in trailing logs.
    if len(response) > MAX_RESPONSE_BYTES:
        response = response[:MAX_RESPONSE_BYTES]
    if "docs/architecture/adr/ADR-" not in response.replace("\\", "/"):
        return 0

    filenames, variants = _find_adr_filenames(response)
    # Log unsupported-naming variants for telemetry.
    for variant in variants:
        _append_log(
            {
                "timestamp": _utc_now_iso(),
                "kind": "unsupported_naming",
                "filename": variant,
                "reason": "non-numeric ADR id; filesystem logger only supports ADR-<digits>",
            }
        )
    if not filenames:
        return 0

    summary: dict[str, int] = {}
    for filename in filenames:
        record = _process_filename(filename)
        _append_log(record)
        kind = record.get("kind", "unknown")
        summary[kind] = summary.get(kind, 0) + 1

    if summary or variants:
        summary_str = ", ".join(f"{k}={v}" for k, v in sorted(summary.items()))
        if variants:
            summary_str = f"{summary_str}, unsupported_naming={len(variants)}".lstrip(", ")
        print(
            f"[adr_registry_capture] adrs={len(filenames)} {summary_str} "
            f"-> log: {CAPTURE_LOG.relative_to(REPO_ROOT)}",
            file=sys.stderr,
        )

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"[adr_registry_capture] fail-open on exception: {exc}", file=sys.stderr)
        sys.exit(0)
