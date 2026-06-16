"""The base/master resume must be IDENTITY-ONLY — the graph is the sole fact source.

Standing rule: `apps_shared/data/master_resume*.json` may hold only identity fields
(name, location, job/company, position/title, years/dates, education, credentials,
LinkedIn, GitHub, phone, email). It must carry NO claims, achievements, narrative
summaries, skills, or metric tokens — those come exclusively from the apps_rg
augmented_skills_graph. This gate fails if a fact/claim/metric is re-introduced.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA = REPO_ROOT / "apps_shared" / "data"
RESUME_FILES = ["master_resume.json", "master_resume_svp.json"]

# Forbidden fact-bearing keys (the things the graph is SSOT for).
FORBIDDEN_KEYS = frozenset(
    {
        "executive_summary",
        "bullet_pool",
        "context",
        "engineering_and_platform_competencies",
        "competencies",
        "skills",
        "achievements",
        "summary",
    }
)
# Metric tokens: $amounts, percentages, magnitudes (k/m/b). Years (4-digit) and
# credential years are allowed; these patterns deliberately do not match them.
_METRIC_RE = re.compile(r"\$\s?\d|\d+(?:\.\d+)?\s?%|\b\d+(?:\.\d+)?\s?(?:m|mm|k|b|bn)\b", re.IGNORECASE)


def _iter_files():
    for name in RESUME_FILES:
        path = DATA / name
        if path.exists():
            yield path


def _all_strings(obj):
    if isinstance(obj, dict):
        for key, value in obj.items():
            yield ("key", str(key))
            yield from _all_strings(value)
    elif isinstance(obj, list):
        for item in obj:
            yield from _all_strings(item)
    elif isinstance(obj, str):
        yield ("value", obj)


@pytest.mark.parametrize("path", list(_iter_files()), ids=lambda p: p.name)
def test_no_forbidden_fact_keys(path: Path) -> None:
    doc = json.loads(path.read_text(encoding="utf-8"))
    found = {k for kind, k in _all_strings(doc) if kind == "key" and k in FORBIDDEN_KEYS}
    assert not found, f"{path.name} re-introduced fact-bearing key(s): {found}"


@pytest.mark.parametrize("path", list(_iter_files()), ids=lambda p: p.name)
def test_no_metric_tokens(path: Path) -> None:
    doc = json.loads(path.read_text(encoding="utf-8"))
    # The _policy note intentionally mentions example tokens — skip that field.
    doc.pop("_policy", None)
    offenders = [
        v for kind, v in _all_strings(doc) if kind == "value" and _METRIC_RE.search(v)
    ]
    assert not offenders, f"{path.name} carries metric token(s) (graph is SSOT): {offenders}"


@pytest.mark.parametrize("path", list(_iter_files()), ids=lambda p: p.name)
def test_envelope_fact_cache_absent(path: Path) -> None:
    # The derived experience-library envelope (a fact cache) must not be regenerated.
    assert not (DATA / "master_resume.envelope.json").exists(), (
        "master_resume.envelope.json (derived fact cache) must stay removed"
    )


def test_identity_fields_preserved() -> None:
    doc = json.loads((DATA / "master_resume.json").read_text(encoding="utf-8"))
    assert doc["owner"]["name"]
    assert doc["owner"]["contact"]["email"]
    assert doc["education"]
    assert doc["certifications_and_credentials"]
    for role in doc["professional_experience"]:
        assert role["company"] and role["title"] and role["dates"]
