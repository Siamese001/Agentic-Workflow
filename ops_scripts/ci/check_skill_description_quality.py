#!/usr/bin/env python3
"""Check active skill descriptions for concise, intent-focused triggering language."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ops_scripts.ci.skill_contract import (  # noqa: E402
    iter_skill_directories,
    parse_skill_document,
)

SKILLS_ROOT = REPO_ROOT / ".codex" / "skills"
DESC_MIN = 60
DESC_MAX = 420
_WORD_RE = re.compile(r"[a-z0-9]{3,}", re.IGNORECASE)
_TRIGGER_PATTERNS = (
    re.compile(r"\buse (?:this )?skill when\b", re.IGNORECASE),
    re.compile(r"\buse when\b", re.IGNORECASE),
    re.compile(r"\binvoke when\b", re.IGNORECASE),
    re.compile(r"\bwhen \w+\b", re.IGNORECASE),
    re.compile(r"\bbefore \w+\b", re.IGNORECASE),
    re.compile(r"\bafter \w+\b", re.IGNORECASE),
    re.compile(r"\binvoke\b", re.IGNORECASE),
)
_LEGACY_PRODUCT_RE = re.compile(r"\b(?:Claude Code|Windsurf|Cursor)\b", re.IGNORECASE)


@dataclass(slots=True)
class SkillDescriptionResult:
    skill: str
    path: str
    status: str = "pass"
    description_chars: int = 0
    issues: list[str] = field(default_factory=list)


def _body_opener_tokens(body: str, max_lines: int = 30) -> set[str]:
    lines: list[str] = []
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            if lines and not stripped:
                break
            continue
        lines.append(stripped)
        if len(lines) >= max_lines:
            break
    return set(_WORD_RE.findall(" ".join(lines).lower()))


def evaluate_skill(skill_dir: Path) -> SkillDescriptionResult:
    skill_md = skill_dir / "SKILL.md"
    result = SkillDescriptionResult(skill=skill_dir.name, path=str(skill_md))
    document, parse_issues = parse_skill_document(skill_md)
    if document is None:
        result.status = "fail"
        result.issues.extend(parse_issues)
        return result

    description = document.description.strip()
    result.description_chars = len(description)
    if len(description) < DESC_MIN:
        result.issues.append(f"description_too_short:{len(description)}<min_{DESC_MIN}")
    if len(description) > DESC_MAX:
        result.issues.append(f"description_too_long:{len(description)}>max_{DESC_MAX}")
    if not any(pattern.search(description) for pattern in _TRIGGER_PATTERNS):
        result.issues.append("missing_explicit_when_to_use_trigger")
    if _LEGACY_PRODUCT_RE.search(description):
        result.issues.append("legacy_product_term_in_description")

    description_tokens = set(_WORD_RE.findall(description.lower()))
    opener_tokens = _body_opener_tokens(document.body)
    if len(description_tokens) >= 8:
        overlap = len(description_tokens & opener_tokens) / len(description_tokens)
        if overlap >= 0.60:
            result.issues.append(f"description_duplicates_body_opener:{overlap:.2f}")

    if result.issues:
        result.status = "fail"
    return result


def evaluate_skills(skills_root: Path) -> list[SkillDescriptionResult]:
    return [evaluate_skill(skill_dir) for skill_dir in iter_skill_directories(skills_root)]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--skills-root", type=Path, default=SKILLS_ROOT)
    args = parser.parse_args(argv)

    skills_root = args.skills_root.resolve()
    results = evaluate_skills(skills_root)
    failures = [result for result in results if result.status == "fail"]
    report = {
        "status": "FAIL" if failures else "PASS",
        "skills_total": len(results),
        "skills_failed": len(failures),
        "description_rules": {
            "min_chars": DESC_MIN,
            "max_chars": DESC_MAX,
            "requires_when_to_use_trigger": True,
            "legacy_product_terms_blocked": True,
        },
        "results": [asdict(result) for result in results],
    }

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    elif failures:
        print("[skill_description_quality] FAIL:")
        for result in failures:
            print(f"  {result.skill}: {', '.join(result.issues)}")
    else:
        print(f"[skill_description_quality] OK: {len(results)} descriptions passed.")

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
