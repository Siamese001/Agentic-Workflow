"""Shared datatypes for generic binding validation (W2+)."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

SectionStatus = Literal["PASS", "FAIL"]


@dataclass
class SectionValidationDetail:
    """Per-section outcome from profile/ref/evidence validation."""

    section_name: str
    status: SectionStatus
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    resolved_refs: list[str] = field(default_factory=list)
    missing_refs: list[str] = field(default_factory=list)
    malformed_refs: list[str] = field(default_factory=list)
    hash_validation_results: list[str] = field(default_factory=list)
    policy_validation_results: list[str] = field(default_factory=list)


@dataclass
class MalformedRefRecord:
    """Structured malformed reference entry."""

    context: str
    detail: str
    path_hint: str | None = None


@dataclass
class ExitCompatValidationResult:
    """Outcome for Exit/X1 compatibility bundle validation (W3)."""

    status: Literal["PASS", "FAIL"]
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    contract_path: Path | None = None


@dataclass
class L6HandoffValidationResult:
    """Outcome for L6 handoff exhaust validation (W3)."""

    status: Literal["PASS", "FAIL"]
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
