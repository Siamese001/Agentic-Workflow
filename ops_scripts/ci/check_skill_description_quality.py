#!/usr/bin/env python3
"""
CI gate: check_skill_description_quality.py

W4 cursor-governance-two-tier — progressive-disclosure hygiene for
``.cursor/skills/<name>/SKILL.md`` (Cursor SSOT).

Enforces (beyond check_skill_frontmatter.py):
  1. Description length in a concise band (default 60–420 chars).
  2. Description includes a when-to-use trigger.
  3. Description is not a near-copy of the opening body (procedure duplication).
  4. ``mcp-integration/SKILL.md`` body size ≤ 8 KB (indexed companions allowed).

Exit 0: all skills pass (warnings allowed unless SKILL_DESC_FAIL_ON_WARN=1).
Exit 1: one or more FAIL severities.

Usage:
  python ops_scripts/ci/check_skill_description_quality.py
  python ops_scripts/ci/check_skill_description_quality.py --json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILLS_ROOT = REPO_ROOT / ".cursor" / "skills"
EXCEPTIONS_FILE = REPO_ROOT / "ops_scripts" / "ci" / "baselines" / "skill_description_exceptions.json"

DESC_MIN = 60
DESC_MAX = 420
MCP_INTEGRATION_MAX_BYTES = 8192

WHEN_TRIGGER_PATTERNS = (
    re.compile(r"\buse when\b", re.IGNORECASE),
    re.compile(r"\binvoke when\b", re.IGNORECASE),
    re.compile(r"\binvoke for\b", re.IGNORECASE),
    re.compile(r"\binvoke\b", re.IGNORECASE),
    re.compile(r"\bwhen the user\b", re.IGNORECASE),
    re.compile(r"\bwhen \w+\b", re.IGNORECASE),
    re.compile(r"\bbefore \w+\b", re.IGNORECASE),
    re.compile(r"\bafter \w+\b", re.IGNORECASE),
)

_FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_WORD_RE = re.compile(r"[a-z0-9]{3,}", re.IGNORECASE)
_DUP_THRESHOLD = 0.55  # fraction of description tokens found in body opener


@dataclass
class SkillResult:
    skill: str
    path: str
    status: str  # pass | warn | fail
    issues: list[str] = field(default_factory=list)
    description_chars: int = 0
    skill_bytes: int = 0


def _load_exceptions() -> dict[str, list[str]]:
    if not EXCEPTIONS_FILE.exists():
        return {}
    try:
        data = json.loads(EXCEPTIONS_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    raw = data.get("intentional_exceptions", {})
    return raw if isinstance(raw, dict) else {}


def _parse_frontmatter_fields(text: str) -> tuple[dict[str, str], str]:
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    block = m.group(1)
    body = text[m.end() :]
    fields: dict[str, str] = {}
    lines = block.splitlines()
    i = 0
    while i < len(lines):
        raw = lines[i]
        if not raw.strip():
            i += 1
            continue
        fm = re.match(r"^([a-z_][a-z0-9_]*)\s*:\s*(.*)$", raw)
        if not fm:
            i += 1
            continue
        key, val = fm.group(1), fm.group(2).strip()
        if val in {"|", ">"}:
            parts: list[str] = []
            i += 1
            while i < len(lines) and (lines[i].startswith(" ") or lines[i].startswith("\t")):
                parts.append(lines[i].strip())
                i += 1
            fields[key] = " ".join(parts)
            continue
        fields[key] = val
        i += 1
    return fields, body


def _parse_description(text: str) -> tuple[str, str]:
    fields, body = _parse_frontmatter_fields(text)
    return fields.get("description", "").strip(), body


def _body_opener_tokens(body: str, *, max_lines: int = 40) -> set[str]:
    lines: list[str] = []
    for line in body.splitlines():
        if line.strip().startswith("#"):
            continue
        if not line.strip():
            if lines:
                break
            continue
        lines.append(line)
        if len(lines) >= max_lines:
            break
    return set(_WORD_RE.findall(" ".join(lines)))


def _description_duplicates_body(desc: str, body: str) -> bool:
    desc_tokens = set(_WORD_RE.findall(desc))
    if len(desc_tokens) < 8:
        return False
    opener = _body_opener_tokens(body)
    if not opener:
        return False
    overlap = len(desc_tokens & opener) / len(desc_tokens)
    return overlap >= _DUP_THRESHOLD


def _evaluate_skill(skill_dir: Path, exceptions: dict[str, list[str]]) -> SkillResult:
    skill_md = skill_dir / "SKILL.md"
    rel = str(skill_md.relative_to(REPO_ROOT)).replace("\\", "/")
    result = SkillResult(skill=skill_dir.name, path=rel, status="pass")
    exempt_codes = set(exceptions.get(skill_dir.name, []))

    if not skill_md.exists():
        result.status = "fail"
        result.issues.append("missing_skill_md")
        return result

    try:
        text = skill_md.read_text(encoding="utf-8")
    except OSError as exc:
        result.status = "fail"
        result.issues.append(f"read_error:{exc}")
        return result

    result.skill_bytes = len(text.encode("utf-8"))
    desc, body = _parse_description(text)
    result.description_chars = len(desc)

    if not desc:
        if "missing_description" not in exempt_codes:
            result.status = "fail"
            result.issues.append("missing_description")
        return result

    if len(desc) < DESC_MIN and "desc_too_short" not in exempt_codes:
        result.status = "fail"
        result.issues.append(f"desc_too_short:{len(desc)}<min_{DESC_MIN}")
    elif len(desc) > DESC_MAX and "desc_too_long" not in exempt_codes:
        result.status = "fail"
        result.issues.append(f"desc_too_long:{len(desc)}>max_{DESC_MAX}")

    if not any(p.search(desc) for p in WHEN_TRIGGER_PATTERNS):
        if "missing_when_trigger" not in exempt_codes:
            result.status = "fail"
            result.issues.append("missing_when_trigger")

    if _description_duplicates_body(desc, body) and "desc_duplicates_body" not in exempt_codes:
        if result.status == "pass":
            result.status = "warn"
        result.issues.append("desc_duplicates_body_opener")

    if skill_dir.name == "mcp-integration":
        if result.skill_bytes > MCP_INTEGRATION_MAX_BYTES and "mcp_integration_size" not in exempt_codes:
            result.status = "fail"
            result.issues.append(
                f"mcp_integration_skill_bytes:{result.skill_bytes}>max_{MCP_INTEGRATION_MAX_BYTES}"
            )

    if result.issues and result.status == "pass":
        result.status = "pass"
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="Emit machine-readable report on stdout")
    args = parser.parse_args()

    fail_on_warn = __import__("os").environ.get("SKILL_DESC_FAIL_ON_WARN", "") == "1"
    exceptions = _load_exceptions()

    if not SKILLS_ROOT.is_dir():
        print(f"[skill_description_quality] SKIP: {SKILLS_ROOT} not found")
        return 0

    results: list[SkillResult] = []
    for skill_dir in sorted(d for d in SKILLS_ROOT.iterdir() if d.is_dir()):
        results.append(_evaluate_skill(skill_dir, exceptions))

    pass_n = sum(1 for r in results if r.status == "pass" and not r.issues)
    warn_n = sum(1 for r in results if r.status == "warn" or (r.status == "pass" and r.issues))
    fail_n = sum(1 for r in results if r.status == "fail")

    mcp_path = SKILLS_ROOT / "mcp-integration" / "SKILL.md"
    mcp_bytes = mcp_path.stat().st_size if mcp_path.exists() else 0

    report = {
        "skills_total": len(results),
        "skills_pass": pass_n,
        "skills_warn": warn_n,
        "skills_fail": fail_n,
        "mcp_integration_bytes": mcp_bytes,
        "description_rules": {
            "desc_min": DESC_MIN,
            "desc_max": DESC_MAX,
            "mcp_integration_max_bytes": MCP_INTEGRATION_MAX_BYTES,
            "dup_threshold": _DUP_THRESHOLD,
        },
        "intentional_exceptions_file": str(EXCEPTIONS_FILE.relative_to(REPO_ROOT)).replace("\\", "/"),
        "results": [asdict(r) for r in results],
    }

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(
            f"[skill_description_quality] total={len(results)} pass={pass_n} warn={warn_n} fail={fail_n} "
            f"mcp_integration_bytes={mcp_bytes}"
        )
        for r in results:
            if r.status == "fail" or (fail_on_warn and r.issues):
                print(f"  FAIL {r.skill} ({r.path})")
                for issue in r.issues:
                    print(f"    - {issue}")
            elif r.issues:
                print(f"  WARN {r.skill}: {', '.join(r.issues)}")

    if fail_n:
        return 1
    if fail_on_warn and warn_n:
        return 1
    if not args.json:
        print("[skill_description_quality] OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
