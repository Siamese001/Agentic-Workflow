#!/usr/bin/env python3
"""Inventory ADR liveness against current enforcement surfaces.

ADRs are provenance/rationale records, not executable policy. This inventory
classifies each ADR-like file by the current repo surfaces that still bind to it
so stale Windsurf-era records can be separated from live governance anchors.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[2]

CANONICAL_ADR_DIR = REPO_ROOT / "docs" / "architecture" / "adr"
LEGACY_ADR_DIR = REPO_ROOT / "docs" / "adr"
STANDALONE_ADR_GLOB = "docs/architecture/*_adr.md"

SKIP_DIR_NAMES = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "artifacts",
    "node_modules",
}

REFERENCE_ROOTS = (
    ".codex",
    ".github",
    "agentic_core",
    "apps_eval",
    "apps_lic",
    "apps_research",
    "apps_rg",
    "apps_shared",
    "apps_underwriting_ai",
    "config",
    "docs",
    "ops_scripts",
    "scripts",
    "tests",
    "tools",
)

ACTIVE_REFERENCE_PREFIXES = (
    ".codex/rules/",
    ".codex/skills/",
    ".codex/hooks",
    ".github/workflows/",
    "agentic_core/",
    "apps_eval/",
    "apps_lic/",
    "apps_research/",
    "apps_rg/",
    "apps_shared/",
    "apps_underwriting_ai/",
    "config/",
    "ops_scripts/ci/",
    "scripts/governance/",
    "tests/",
    "tools/",
)

INACTIVE_REFERENCE_PREFIXES = (
    "tests/_archived_obsolete/",
)

SELF_REFERENCE_FILES = {
    "ops_scripts/ci/check_adr_hygiene.py",
    "ops_scripts/ci/inventory_adr_liveness.py",
    "tests/unit/ops_scripts/ci/test_adr_hygiene.py",
}

STALE_MARKERS = (
    ".windsurf",
    ".cursor",
    "windsurf",
    "cursor",
    "Notion ADR Registry",
    "ADR Registry",
    "author-gate packet",
    "author-gate",
    "Claude governance",
    "legacy Claude",
)

STATUS_RE = re.compile(r"^\s*[-*> ]*(?:\*\*)?Status(?:\*\*)?\s*:?\s*(?:\*\*)?\s*(.+?)\s*(?:\*\*)?\s*$", re.I | re.M)
ADR_NUMBER_RE = re.compile(r"\bADR[-_ ]?0*([0-9]{2,3})\b", re.I)


@dataclass(frozen=True)
class AdrRecord:
    path: str
    location: str
    number: str | None
    status: str | None
    duplicate_group_size: int
    inbound_reference_count: int
    active_reference_count: int
    active_references: list[str]
    stale_markers: list[str]
    liveness: str


def relpath(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def normalize_slashes(value: str) -> str:
    return value.replace("\\", "/")


def adr_like_files(repo_root: Path = REPO_ROOT) -> list[Path]:
    files: list[Path] = []
    canonical = repo_root / "docs" / "architecture" / "adr"
    legacy = repo_root / "docs" / "adr"
    if canonical.exists():
        files.extend(
            p
            for p in canonical.glob("*.md")
            if p.name not in {"README.md", "ADR-template.md"}
        )
    if legacy.exists():
        files.extend(legacy.rglob("*.md"))
    files.extend((repo_root / "docs" / "architecture").glob("*_adr.md"))
    return sorted(set(files), key=lambda p: relpath(p))


def extract_number(path: Path) -> str | None:
    match = ADR_NUMBER_RE.search(path.name)
    if not match:
        return None
    return f"ADR-{int(match.group(1)):03d}"


def extract_status(text: str) -> str | None:
    match = STATUS_RE.search(text[:3000])
    if not match:
        return None
    return match.group(1).strip().strip("*").strip()


def classify_location(path: Path) -> str:
    if path.is_relative_to(CANONICAL_ADR_DIR):
        return "canonical"
    if path.is_relative_to(LEGACY_ADR_DIR):
        return "legacy_docs_adr"
    return "standalone_architecture_adr"


def iter_reference_files(repo_root: Path = REPO_ROOT) -> Iterable[Path]:
    for root_name in REFERENCE_ROOTS:
        root = repo_root / root_name
        if root.is_file():
            yield root
            continue
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if any(part in SKIP_DIR_NAMES for part in path.parts):
                continue
            if path.suffix.lower() not in {".md", ".py", ".yaml", ".yml", ".json", ".toml", ".txt", ".csv", ".sql"}:
                continue
            yield path


def _reference_needles(path: Path, number: str | None) -> list[str]:
    rel = relpath(path)
    needles = {rel, path.name}
    if number:
        needles.add(number)
        needles.add(number.lower())
    return sorted(needles, key=len, reverse=True)


def find_inbound_references(paths: list[Path], repo_root: Path = REPO_ROOT) -> dict[str, list[str]]:
    needles_by_path = {relpath(path): _reference_needles(path, extract_number(path)) for path in paths}
    refs: dict[str, set[str]] = {relpath(path): set() for path in paths}

    for source in iter_reference_files(repo_root):
        source_rel = relpath(source)
        try:
            text = normalize_slashes(source.read_text(encoding="utf-8", errors="replace"))
        except OSError:
            continue
        for adr_rel, needles in needles_by_path.items():
            if source_rel == adr_rel:
                continue
            if any(needle and needle in text for needle in needles):
                refs[adr_rel].add(source_rel)

    return {key: sorted(value) for key, value in refs.items()}


def active_references(references: list[str]) -> list[str]:
    return [
        ref
        for ref in references
        if ref not in SELF_REFERENCE_FILES
        if not any(ref.startswith(prefix) for prefix in INACTIVE_REFERENCE_PREFIXES)
        if any(ref.startswith(prefix) for prefix in ACTIVE_REFERENCE_PREFIXES)
    ]


def stale_markers(text: str) -> list[str]:
    lower = text.lower()
    found: list[str] = []
    for marker in STALE_MARKERS:
        if marker.lower() in lower:
            found.append(marker)
    return found


def classify_liveness(location: str, active_count: int, stale_count: int) -> str:
    if active_count:
        return "live_bound"
    if location != "canonical":
        return "noncanonical"
    if stale_count:
        return "historical_stale_marker"
    return "unbound_review"


def build_inventory(repo_root: Path = REPO_ROOT) -> list[AdrRecord]:
    paths = adr_like_files(repo_root)
    duplicate_counts: dict[str, int] = {}
    for path in paths:
        number = extract_number(path)
        if number:
            duplicate_counts[number] = duplicate_counts.get(number, 0) + 1

    refs = find_inbound_references(paths, repo_root)
    records: list[AdrRecord] = []
    for path in paths:
        rel = relpath(path)
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            text = ""
        location = classify_location(path)
        number = extract_number(path)
        active = active_references(refs.get(rel, []))
        stale = stale_markers(text)
        records.append(
            AdrRecord(
                path=rel,
                location=location,
                number=number,
                status=extract_status(text),
                duplicate_group_size=duplicate_counts.get(number, 0) if number else 0,
                inbound_reference_count=len(refs.get(rel, [])),
                active_reference_count=len(active),
                active_references=active[:20],
                stale_markers=stale,
                liveness=classify_liveness(location, len(active), len(stale)),
            )
        )
    return records


def render_markdown(records: list[AdrRecord]) -> str:
    counts: dict[str, int] = {}
    for record in records:
        counts[record.liveness] = counts.get(record.liveness, 0) + 1

    lines = [
        "# ADR Liveness Inventory",
        "",
        "ADRs are rationale/provenance records. A record is current only when it has a live binding.",
        "",
        "## Summary",
        "",
        "| Liveness | Count |",
        "|---|---:|",
    ]
    for key in sorted(counts):
        lines.append(f"| {key} | {counts[key]} |")

    lines.extend(
        [
            "",
            "## Records",
            "",
            "| Path | Location | Number | Status | Liveness | Active refs | Stale markers |",
            "|---|---|---|---|---|---:|---|",
        ]
    )
    for record in records:
        markers = ", ".join(record.stale_markers)
        status = (record.status or "").replace("|", "\\|")
        lines.append(
            f"| `{record.path}` | {record.location} | {record.number or ''} | "
            f"{status} | {record.liveness} | {record.active_reference_count} | {markers} |"
        )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Inventory ADR liveness.")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of Markdown.")
    parser.add_argument("--output", type=Path, default=None, help="Optional output path.")
    args = parser.parse_args(argv)

    records = build_inventory(REPO_ROOT)
    if args.json:
        payload = {
            "records": [asdict(record) for record in records],
            "summary": {
                "total": len(records),
                "live_bound": sum(1 for record in records if record.liveness == "live_bound"),
                "noncanonical": sum(1 for record in records if record.liveness == "noncanonical"),
                "historical_stale_marker": sum(1 for record in records if record.liveness == "historical_stale_marker"),
                "unbound_review": sum(1 for record in records if record.liveness == "unbound_review"),
            },
        }
        output = json.dumps(payload, indent=2, sort_keys=True)
    else:
        output = render_markdown(records)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output + ("" if output.endswith("\n") else "\n"), encoding="utf-8")
    else:
        print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
