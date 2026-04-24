"""Shared territory and report-placement rules for maintenance helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath
from agentic_core.L0_routing.config.path_constants import DOCS_REPORTS_DIR


@dataclass(frozen=True, slots=True)
class TerritoryRule:
    prefix: str
    label: str
    protected: bool = False


TERRITORY_RULES: tuple[TerritoryRule, ...] = (
    TerritoryRule("agentic_core/", "core", protected=True),
    TerritoryRule("apps_lic/", "app"),
    TerritoryRule("apps_rg/", "app"),
    TerritoryRule("apps_shared/", "shared"),
    TerritoryRule(DOCS_REPORTS_DIR + "/", "reports"),
    TerritoryRule("tests/", "tests"),
    TerritoryRule("ops_scripts/", "ops"),
)

REPORT_SUBDIR_HINTS: dict[str, str] = {
    "audit": "audit",
    "gap": "audit",
    "assessment": "assessments",
    "plan": "plans",
    "status": "status",
    "report": "misc",
}


def normalize_relative_path(path: str) -> str:
    return PurePosixPath(path.replace("\\", "/")).as_posix().lstrip("./")


def classify_territory(path: str) -> str:
    normalized = normalize_relative_path(path)
    for rule in TERRITORY_RULES:
        if normalized.startswith(rule.prefix):
            return rule.label
    return "unknown"


def is_protected_territory(path: str) -> bool:
    normalized = normalize_relative_path(path)
    return any(rule.protected and normalized.startswith(rule.prefix) for rule in TERRITORY_RULES)


def suggest_report_subdir(filename: str) -> str:
    lowered = filename.lower()
    for token, subdir in REPORT_SUBDIR_HINTS.items():
        if token in lowered:
            return subdir
    return "misc"
