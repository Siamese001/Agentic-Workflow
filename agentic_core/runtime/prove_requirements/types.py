"""Dataclasses for the requirements proof system."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True)
class SourceFileEntry:
    """One row of source_manifest.json."""

    source_folder: str  # absolute path to the canonical source folder
    path: str  # absolute path to the file
    relative_path: str  # repo-relative POSIX path
    sha256: str  # 64-char lowercase hex
    line_count: int  # number of newlines + 1 (or actual line count)
    mtime: str  # ISO-8601 UTC
    ingested: bool


@dataclass(frozen=True)
class RequirementRecord:
    """One row of requirements_index.json."""

    req_id: str
    source_folder: str
    source_path: str
    relative_path: str
    line_start: int
    line_end: int
    source_text: str
    requirement_type: str
    owning_layer: str
    normalized_requirement: str
    verification_needed: Tuple[str, ...]
    status: str = "UNMAPPED"
    matched_markers: Tuple[str, ...] = field(default_factory=tuple)
