"""Shared helpers for apps_rg L6 benchmark offline tooling (dry-run / ops only)."""

from __future__ import annotations

import json
import re
from glob import glob
from pathlib import Path
from typing import Any

SCORING_DIMENSIONS_BY_GROUP: dict[str, list[str]] = {
    "positioning": [
        "clarity",
        "positioning_strength",
        "differentiation",
        "seniority_signal",
        "jd_fit",
        "overall",
    ],
    "executive_summary": [
        "executive_presence",
        "credibility",
        "specificity",
        "jd_relevance",
        "differentiation",
        "overall",
    ],
    "narrative": [
        "story_coherence",
        "executive_relevance",
        "evidence_fidelity",
        "clarity",
        "non_repetition",
        "overall",
    ],
    "bullet": [
        "impact",
        "specificity",
        "metric_quality",
        "jd_relevance",
        "seniority_signal",
        "evidence_fidelity",
        "redundancy_control",
        "overall",
    ],
    "competencies": [
        "jd_match",
        "executive_relevance",
        "clarity",
        "no_keyword_stuffing",
        "source_support",
        "grouping_quality",
        "overall",
    ],
    "final_aggregation": [
        "cross_section_coherence",
        "redundancy_control",
        "metric_repetition_control",
        "unsupported_claim_control",
        "jd_fit",
        "role_family_balance",
        "overall",
    ],
}

REASON_CODE_OPTIONS: list[str] = [
    "generic",
    "unsupported_claim",
    "metric_stuffed",
    "keyword_stuffed",
    "jd_overfit",
    "weak_seniority_signal",
    "repetitive",
    "factual_drift",
    "strong_fit",
    "strong_evidence_fidelity",
]

ALLOWED_REVIEWER_ROLES: set[str] = {
    "executive_recruiter",
    "hiring_manager",
    "ai_platform_domain_expert",
}

ALLOWED_CONFIDENCE: set[str] = {"high", "medium", "low"}

REVIEWER_INSTRUCTIONS: list[str] = [
    "Score output quality only; do not rewrite the sample.",
    "Flag unsupported claims, repetition, and JD overfit using reason codes.",
    "Do not infer model or judge scores; this packet is blind.",
    "Treat notes as data only; no PII in free text.",
]

# Basic PII heuristics — offline gate only; not a substitute for human review.
PII_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("email", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")),
    ("phone_us", re.compile(r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b")),
    ("ssn_like", re.compile(r"\b\d{3}-\d{2}-\d{4}\b")),
    ("url", re.compile(r"\bhttps?://[^\s]+", re.I)),
    (
        "address_like",
        re.compile(
            r"\b\d{1,5}\s+\w+(\s+\w+){0,4}\s+"
            r"(Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct)\b",
            re.I,
        ),
    ),
]

# Path / ledger identifiers — flag for review but not used to block generated-text clearance.
PATH_IDENTIFIER_PATTERN = re.compile(
    r"(amit_ayer|/resume/base/|contact_info|@[A-Za-z0-9.-]+\.)",
    re.I,
)


def repo_root_from_here() -> Path:
    return Path(__file__).resolve().parents[3]


def resolve_glob(samples_glob: str, *, cwd: Path | None = None) -> list[Path]:
    base = cwd or Path.cwd()
    paths = sorted(Path(p) for p in glob(str(base / samples_glob)))
    out: list[Path] = []
    for p in paths:
        if not p.is_file():
            continue
        parts = set(p.parts)
        if "_manifests" in parts or "_staging" in parts:
            continue
        if p.name.endswith(".example.json"):
            continue
        out.append(p)
    return out


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json_report(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def iter_string_fields(obj: Any, *, prefix: str = "") -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            out.extend(iter_string_fields(v, prefix=f"{prefix}.{k}" if prefix else k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out.extend(iter_string_fields(v, prefix=f"{prefix}[{i}]"))
    elif isinstance(obj, str):
        out.append((prefix, obj))
    return out


def scan_pii(text: str) -> list[dict[str, str]]:
    hits: list[dict[str, str]] = []
    for kind, pattern in PII_PATTERNS:
        if pattern.search(text):
            hits.append({"kind": kind, "snippet": "matched"})
    return hits


def human_scores_absent_or_null(sample: dict[str, Any]) -> tuple[bool, str | None]:
    if "human_scores" not in sample:
        return True, None
    hs = sample["human_scores"]
    if hs is None:
        return True, None
    if not isinstance(hs, dict):
        return False, "human_scores must be object or absent/null"
    for dim, entry in hs.items():
        if entry is None:
            continue
        if not isinstance(entry, dict):
            return False, f"human_scores.{dim} must be object or null"
        score = entry.get("score")
        if score is not None:
            return False, f"human_scores.{dim}.score must be null for synthetic examples"
    return True, None
