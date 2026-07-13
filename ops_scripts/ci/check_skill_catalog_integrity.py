#!/usr/bin/env python3
"""Validate active-skill catalog integrity beyond frontmatter syntax."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from urllib.parse import unquote

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ops_scripts.ci.skill_contract import (  # noqa: E402
    iter_skill_directories,
    parse_skill_document,
)

SKILLS_ROOT = REPO_ROOT / ".codex" / "skills"
_MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
_FENCED_CODE_RE = re.compile(r"```.*?```", re.DOTALL)
_DEPRECATED_MARKERS = (
    re.compile(r"(?im)^\s*(?:#|>)?\s*(?:status:\s*)?deprecated\b"),
    re.compile(r"\bredirect(?:ed)?\s+(?:stub|to)\b", re.IGNORECASE),
    re.compile(r"\blegacy\s+skill\b", re.IGNORECASE),
)
_REPO_ROOT_PREFIXES = (
    ".codex/",
    ".github/",
    "agentic_core/",
    "apps_",
    "artifacts/",
    "config/",
    "docs/",
    "memory/",
    "ops_scripts/",
    "plans/",
    "scripts/",
    "tests/",
    "tools/",
)


@dataclass(slots=True)
class CatalogResult:
    skill: str
    path: str
    issues: list[str] = field(default_factory=list)


def _resolve_reference(target: str, *, skill_dir: Path, repo_root: Path) -> Path | None:
    target = unquote(target.strip())
    if not target or target.startswith(("#", "http://", "https://", "mailto:")):
        return None
    target = target.split("#", 1)[0].split("?", 1)[0]
    if not target or "<" in target or ">" in target:
        return None
    if target.startswith(_REPO_ROOT_PREFIXES):
        return repo_root / target
    return skill_dir / target


def _validate_openai_yaml(path: Path) -> list[str]:
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        return [f"agents/openai.yaml is unreadable or invalid YAML: {exc}"]
    if not isinstance(payload, dict):
        return ["agents/openai.yaml must be a YAML mapping"]
    interface = payload.get("interface")
    if not isinstance(interface, dict):
        return ["agents/openai.yaml must contain an 'interface' mapping"]
    issues: list[str] = []
    for field in ("display_name", "short_description", "default_prompt"):
        value = interface.get(field)
        if not isinstance(value, str) or not value.strip():
            issues.append(f"agents/openai.yaml interface.{field} must be a non-empty string")
    return issues


def evaluate_skill(skill_dir: Path, repo_root: Path) -> CatalogResult:
    skill_md = skill_dir / "SKILL.md"
    result = CatalogResult(skill=skill_dir.name, path=str(skill_md.relative_to(repo_root)))
    document, parse_issues = parse_skill_document(skill_md)
    if document is None:
        result.issues.extend(parse_issues)
        return result

    name = document.frontmatter.get("name")
    description = document.frontmatter.get("description")
    for field, value in (("name", name), ("description", description)):
        if isinstance(value, str) and ("<" in value or ">" in value):
            result.issues.append(f"frontmatter field '{field}' contains an unfilled placeholder")

    searchable_body = _FENCED_CODE_RE.sub("", document.body)
    for pattern in _DEPRECATED_MARKERS:
        if pattern.search(searchable_body):
            result.issues.append(
                "active SKILL.md contains deprecation/redirect language; archive the activation surface"
            )
            break

    for raw_target in _MARKDOWN_LINK_RE.findall(searchable_body):
        resolved = _resolve_reference(raw_target, skill_dir=skill_dir, repo_root=repo_root)
        if resolved is not None and not resolved.exists():
            result.issues.append(f"broken relative reference: {raw_target}")

    openai_yaml = skill_dir / "agents" / "openai.yaml"
    if openai_yaml.exists():
        result.issues.extend(_validate_openai_yaml(openai_yaml))

    return result


def evaluate_catalog(skills_root: Path) -> list[CatalogResult]:
    repo_root = skills_root.parents[1]
    results = [evaluate_skill(skill_dir, repo_root) for skill_dir in iter_skill_directories(skills_root)]

    active_names = {result.skill for result in results}
    for directory in sorted(path for path in skills_root.iterdir() if path.is_dir()):
        if directory.name in active_names:
            continue
        tracked_like_files = [path for path in directory.rglob("*") if path.is_file()]
        if tracked_like_files:
            results.append(
                CatalogResult(
                    skill=directory.name,
                    path=str(directory.relative_to(repo_root)),
                    issues=[
                        "orphan skill directory contains files but no SKILL.md; move resources to the "
                        "canonical skill or archive them"
                    ],
                )
            )
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--skills-root", type=Path, default=SKILLS_ROOT)
    args = parser.parse_args(argv)

    skills_root = args.skills_root.resolve()
    if not skills_root.is_dir():
        print(f"[skill_catalog] FAIL: skills root not found: {skills_root}")
        return 1

    results = evaluate_catalog(skills_root)
    failures = [result for result in results if result.issues]
    report = {
        "status": "FAIL" if failures else "PASS",
        "skills_total": len([r for r in results if r.path.endswith("SKILL.md")]),
        "entries_failed": len(failures),
        "results": [asdict(result) for result in results],
    }

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    elif failures:
        print("[skill_catalog] FAIL:")
        for result in failures:
            print(f"  {result.path}")
            for issue in result.issues:
                print(f"    - {issue}")
    else:
        print(f"[skill_catalog] OK: {report['skills_total']} active skills passed.")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
