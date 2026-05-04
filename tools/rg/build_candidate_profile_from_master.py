"""Build candidate_profile.yaml from master_resume.json.

Extracts key metadata (name, contact, summary, skills) from the canonical
master resume to seed a candidate profile for R1B cache targeting.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml


def build_profile(master_resume_path: Path) -> dict:
    """Extract candidate profile from master resume."""
    with open(master_resume_path, encoding="utf-8") as f:
        master = json.load(f)

    owner = master.get("owner", {})
    competencies = master.get("engineering_and_platform_competencies", [])
    
    # Extract top-level skills from competency areas
    skills = []
    for comp in competencies[:5]:  # Top 5 competency areas
        area = comp.get("area", "")
        skills.append(area)
        # Also grab first skill phrase from each area
        skill_text = comp.get("skills", "")
        if skill_text:
            first_skill = skill_text.split(",")[0].strip()
            if first_skill and first_skill not in skills:
                skills.append(first_skill)

    # Extract education summary
    education_entries = master.get("education", [])
    education = []
    for edu in education_entries[:2]:  # Top 2 degrees
        degree = edu.get("degree", "")
        school = edu.get("school", "")
        if degree and school:
            education.append(f"{degree}, {school}")

    # Build experience summary (just company/title from most recent)
    experience = master.get("professional_experience", [])
    exp_summary = []
    for exp in experience[:3]:  # Most recent 3
        company = exp.get("company", "")
        title = exp.get("title", "")
        if company and title:
            exp_summary.append(f"{title} at {company}")

    # Executive summary as bio
    bio = master.get("executive_summary", "")
    # Truncate to first sentence or 200 chars
    if bio:
        bio = bio.split(".")[0] + "." if "." in bio else bio[:200]

    profile = {
        "name": owner.get("name", ""),
        "email": owner.get("email", ""),
        "phone": owner.get("phone", ""),
        "location": owner.get("location", ""),
        "linkedIn": owner.get("linkedin", ""),
        "summary": bio,
        "skills": skills[:8],  # Cap at 8 skills
        "experience_summary": exp_summary,
        "education_summary": education,
        "level": "senior",  # Default, user should adjust
        "target_roles": ["Senior ML Engineer", "Staff Engineer", "VP Engineering"],
    }

    return profile


def main() -> int:
    master_path = Path("apps_shared/data/master_resume.json")
    if not master_path.exists():
        print(f"Master resume not found: {master_path}", file=sys.stderr)
        return 1

    profile = build_profile(master_path)

    # Write to default candidate profile location
    output_path = Path("apps_rg/scripts/candidate_profile.yaml")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        yaml.dump(profile, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    print(f"Candidate profile written to: {output_path}")
    print(f"  Name: {profile['name']}")
    print(f"  Skills: {', '.join(profile['skills'][:5])}...")
    print(f"  Roles: {', '.join(profile['target_roles'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
