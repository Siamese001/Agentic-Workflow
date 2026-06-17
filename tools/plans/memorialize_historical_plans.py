#!/usr/bin/env python3
"""Copy historical plan material into the root plans/ folder as archived records."""

from __future__ import annotations

import csv
import hashlib
import re
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
PLANS_DIR = REPO_ROOT / "plans"
RECOVERED_ROOT = Path(r"C:\Git\windsurf-plans-recovered")
MANIFEST_PATH = PLANS_DIR / "historical-plans-memorial-manifest.csv"
MAX_FILENAME_LEN = 180


@dataclass(frozen=True)
class SourceRoot:
    key: str
    surface: str
    path: Path


SOURCE_ROOTS = [
    SourceRoot("claude", "claude_legacy_plans", REPO_ROOT / ".claude" / "plans"),
    SourceRoot("docs-reports", "docs_reports_plans", REPO_ROOT / "docs" / "reports" / "plans"),
    SourceRoot("windsurf", "recovered_windsurf_plans", RECOVERED_ROOT / "windsurf_plans"),
    SourceRoot("windsurf-docs", "recovered_docs_reports_plans", RECOVERED_ROOT / "docs_reports_plans"),
]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_part(value: str) -> str:
    value = value.replace("\\", "__").replace("/", "__")
    value = re.sub(r"[^A-Za-z0-9._-]+", "-", value)
    value = re.sub(r"-{2,}", "-", value).strip("-._")
    return value or "unnamed"


def target_name(source: SourceRoot, relative_path: Path, digest: str, occupied: set[str]) -> str:
    stem = safe_part(str(relative_path.with_suffix("")))
    suffix = relative_path.suffix.lower() or ".md"
    candidate = f"archived-{source.key}-{stem}{suffix}"
    if len(candidate) > MAX_FILENAME_LEN:
        room = MAX_FILENAME_LEN - len(f"archived-{source.key}--{digest[:12]}{suffix}")
        candidate = f"archived-{source.key}-{stem[:max(room, 20)].rstrip('-._')}-{digest[:12]}{suffix}"

    if candidate not in occupied:
        occupied.add(candidate)
        return candidate

    base = candidate[: -len(suffix)]
    for index in range(2, 10_000):
        numbered = f"{base}--dup{index}{suffix}"
        if len(numbered) > MAX_FILENAME_LEN:
            base_room = MAX_FILENAME_LEN - len(f"--dup{index}{suffix}")
            numbered = f"{base[:base_room].rstrip('-._')}--dup{index}{suffix}"
        if numbered not in occupied:
            occupied.add(numbered)
            return numbered

    raise RuntimeError(f"could not create unique target for {relative_path}")


def load_recovered_manifest() -> dict[str, dict[str, str]]:
    manifest = RECOVERED_ROOT / "manifest_enriched.csv"
    if not manifest.exists():
        return {}
    with manifest.open("r", encoding="utf-8", errors="replace", newline="") as handle:
        rows = list(csv.DictReader(handle))
    return {row.get("original_path", ""): row for row in rows}


def metadata_block(
    *,
    source: SourceRoot,
    source_path: Path,
    relative_path: Path,
    digest: str,
    recovered_status: str,
    last_commit: str,
    last_commit_date: str,
    created_date: str,
) -> str:
    original_path = str(source_path)
    return "\n".join(
        [
            "---",
            "status: Archived",
            "do_not_execute: true",
            "memorialized: true",
            f"source_surface: {source.surface}",
            f"source_key: {source.key}",
            f"original_path: {original_path!r}",
            f"original_relative_path: {str(relative_path)!r}",
            f"source_sha256: {digest}",
            f"recovered_status: {recovered_status or 'LEGACY_EXISTING'}",
            f"last_commit: {last_commit!r}",
            f"last_commit_date: {last_commit_date!r}",
            f"created_date: {created_date!r}",
            "archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis",
            "---",
            "",
            "> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.",
            "",
            "---",
            "",
        ]
    )


def main() -> int:
    PLANS_DIR.mkdir(parents=True, exist_ok=True)
    recovered_manifest = load_recovered_manifest()
    occupied = {path.name for path in PLANS_DIR.glob("*.md")}
    rows: list[dict[str, str]] = []

    for source in SOURCE_ROOTS:
        if not source.path.exists():
            rows.append(
                {
                    "source_key": source.key,
                    "source_surface": source.surface,
                    "source_path": str(source.path),
                    "target_path": "",
                    "source_sha256": "",
                    "target_sha256": "",
                    "bytes": "0",
                    "status": "SOURCE_MISSING",
                    "note": "source root does not exist",
                }
            )
            continue

        for source_path in sorted(source.path.rglob("*.md")):
            relative_path = source_path.relative_to(source.path)
            data = source_path.read_bytes()
            digest = sha256_bytes(data)

            manifest_key = str(relative_path).replace("\\", "/")
            if source.key == "windsurf":
                recovered_key = f".claude/plans/{manifest_key}"
            elif source.key == "windsurf-docs":
                recovered_key = f"docs/reports/plans/{manifest_key}"
            else:
                recovered_key = ""
            recovered_row = recovered_manifest.get(recovered_key, {})

            target = PLANS_DIR / target_name(source, relative_path, digest, occupied)
            text = data.decode("utf-8", errors="replace")
            imported = metadata_block(
                source=source,
                source_path=source_path,
                relative_path=relative_path,
                digest=digest,
                recovered_status=recovered_row.get("status", ""),
                last_commit=recovered_row.get("last_commit", ""),
                last_commit_date=recovered_row.get("last_commit_date", ""),
                created_date=recovered_row.get("created_date", ""),
            ) + text
            target.write_text(imported, encoding="utf-8", newline="\n")
            target_digest = sha256_bytes(target.read_bytes())
            rows.append(
                {
                    "source_key": source.key,
                    "source_surface": source.surface,
                    "source_path": str(source_path),
                    "target_path": str(target),
                    "source_sha256": digest,
                    "target_sha256": target_digest,
                    "bytes": str(len(data)),
                    "status": "IMPORTED_ARCHIVED",
                    "note": "",
                }
            )

    with MANIFEST_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "source_key",
                "source_surface",
                "source_path",
                "target_path",
                "source_sha256",
                "target_sha256",
                "bytes",
                "status",
                "note",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    imported = sum(1 for row in rows if row["status"] == "IMPORTED_ARCHIVED")
    missing = sum(1 for row in rows if row["status"] == "SOURCE_MISSING")
    print(f"imported={imported} missing_sources={missing} manifest={MANIFEST_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
