"""Build locked-copy manifest entries from canonical base resume JSON."""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from apps_rg.runtime.resume_resolution import load_lane_base_resume_json


LOCKED_SECTION_IDS: tuple[str, ...] = (
    "insurtech",
    "ey",
    "early_career",
    "education",
    "certifications",
    "company_names",
    "titles",
    "locations",
    "dates",
)


def find_repo_root(start: Path | None = None) -> Path:
    here = (start or Path(__file__)).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "apps_rg" / "resume" / "base").exists():
            return parent
    return Path.cwd()


def sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def load_base_resume(repo: Path) -> tuple[dict[str, Any], Path, str]:
    return load_lane_base_resume_json(repo_root=repo)


def _facts(base: dict[str, Any]) -> dict[str, Any]:
    return base.get("facts", base)


def _employment(base: dict[str, Any]) -> list[dict[str, Any]]:
    return list(_facts(base).get("employment") or [])


def _find_employment(base: dict[str, Any], *, needle: str) -> dict[str, Any] | None:
    n = needle.lower()
    for emp in _employment(base):
        employer = str(emp.get("employer", "")).lower()
        if n == "insurtech" and "insurtech" in employer:
            return emp
        if n == "ey" and ("ernst" in employer or employer.startswith("ey")):
            return emp
        if n == "early_career" and "early career" in employer:
            return emp
    return None


def _employment_fact_ids(emp: dict[str, Any]) -> list[str]:
    ids = [str(emp.get("fact_id"))]
    for bullet in emp.get("bullets") or []:
        bid = bullet.get("bullet_id")
        if bid:
            ids.append(str(bid))
    return ids


@dataclass(frozen=True)
class LockedSectionEntry:
    section_id: str
    source_fact_ids: list[str]
    copied_text: str
    source_hash: str
    copied_hash: str
    byte_for_byte_match: bool
    llm_generated: bool = False
    rewrite_allowed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _section_from_canonical(
    section_id: str,
    source_value: Any,
    source_fact_ids: list[str],
) -> LockedSectionEntry:
    source_text = canonical_json(source_value)
    copied_text = source_text
    source_hash = sha256_hex(source_text)
    copied_hash = sha256_hex(copied_text)
    return LockedSectionEntry(
        section_id=section_id,
        source_fact_ids=source_fact_ids,
        copied_text=copied_text,
        source_hash=source_hash,
        copied_hash=copied_hash,
        byte_for_byte_match=source_text == copied_text,
        llm_generated=False,
        rewrite_allowed=False,
    )


def build_locked_sections(base: dict[str, Any]) -> list[LockedSectionEntry]:
    facts = _facts(base)
    employment = _employment(base)
    sections: list[LockedSectionEntry] = []

    insurtech = _find_employment(base, needle="insurtech")
    if insurtech is None:
        raise ValueError("InsurTech employment block not found in base resume.")
    sections.append(
        _section_from_canonical("insurtech", insurtech, _employment_fact_ids(insurtech))
    )

    ey = _find_employment(base, needle="ey")
    if ey is None:
        raise ValueError("EY employment block not found in base resume.")
    sections.append(_section_from_canonical("ey", ey, _employment_fact_ids(ey)))

    early = _find_employment(base, needle="early_career")
    if early is None:
        raise ValueError("Early Career employment block not found in base resume.")
    sections.append(_section_from_canonical("early_career", early, _employment_fact_ids(early)))

    education = list(facts.get("education") or [])
    edu_ids = [str(e.get("fact_id")) for e in education if e.get("fact_id")]
    sections.append(_section_from_canonical("education", education, edu_ids))

    certifications = list(facts.get("certifications") or [])
    cert_ids = [str(c.get("fact_id")) for c in certifications if c.get("fact_id")]
    sections.append(_section_from_canonical("certifications", certifications, cert_ids))

    emp_fact_ids = [str(e.get("fact_id")) for e in employment if e.get("fact_id")]
    company_names = [str(e.get("employer", "")) for e in employment]
    titles = [str(e.get("title", "")) for e in employment]
    locations = [str(e.get("location", "")) for e in employment]
    dates = [
        {
            "fact_id": e.get("fact_id"),
            "start_date": e.get("start_date"),
            "end_date": e.get("end_date"),
            "is_current": e.get("is_current"),
        }
        for e in employment
    ]

    sections.append(_section_from_canonical("company_names", company_names, emp_fact_ids))
    sections.append(_section_from_canonical("titles", titles, emp_fact_ids))
    sections.append(_section_from_canonical("locations", locations, emp_fact_ids))
    sections.append(_section_from_canonical("dates", dates, emp_fact_ids))

    return sections


def build_manifest(
    base: dict[str, Any],
    base_path: Path,
    base_file_hash: str,
) -> dict[str, Any]:
    """``base_file_hash`` must be UTF-8 sha256(raw file body), matching :func:`assemble_final_resume`."""
    sections = build_locked_sections(base)
    return {
        "manifest_id": "locked_copy_manifest_v1",
        "base_resume_json_ref": str(base_path),
        "base_resume_json_hash": base_file_hash,
        "llm_generated": False,
        "rewrite_allowed": False,
        "provider_calls_made": False,
        "PROVIDER_MODEL_calls_made": False,
        "sections": [s.to_dict() for s in sections],
    }
