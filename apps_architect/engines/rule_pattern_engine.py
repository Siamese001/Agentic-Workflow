"""Rule pattern extractor — parses .claude/rules/*.md for hardening patterns.

Plan: ``.claude/plans/apps-architect-pattern-hardening-d7e4f9.md`` W2.P3.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Tuple

from apps_architect.types.architect_types import Pattern, PatternType

_log = logging.getLogger(__name__)

_RULES_DIR = Path(__file__).resolve().parents[2] / ".windsurf" / "rules"
_TRIGGER_RE = re.compile(r"trigger:\s*(\S+)")
_ALWAYS_ON_RE = re.compile(r"always_on|always-on")
_PRE_HOOK_RE = re.compile(r"pre_\w+\.py")
_POST_HOOK_RE = re.compile(r"post_\w+\.py")
_MCP_RE = re.compile(r"`(mcp\d+_|adg_|redis_|memory_|otel_)")
_SKILL_RE = re.compile(r"\.claude/skills/(\w[\w-]*)/")


class RulePatternEngine:
    """Extracts hardening patterns from rule markdown files."""

    def __init__(self, rules_dir: str | Path | None = None) -> None:
        self._rules_dir = Path(rules_dir) if rules_dir else _RULES_DIR

    def extract_from_file(self, filepath: Path) -> list[Pattern]:
        try:
            text = filepath.read_text(encoding="utf-8")
        except Exception:
            return []

        patterns: list[Pattern] = []
        rel = str(filepath.relative_to(filepath.parents[2]))

        trigger_m = _TRIGGER_RE.search(text)
        trigger = trigger_m.group(1) if trigger_m else "unknown"

        if _ALWAYS_ON_RE.search(text):
            patterns.append(Pattern.from_source(
                pattern_type=PatternType.RULE,
                source_ref=rel,
                content=f"trigger={trigger}",
                summary=f"Always-on rule: {filepath.stem}",
                tags=("always_on", trigger),
            ))
        else:
            patterns.append(Pattern.from_source(
                pattern_type=PatternType.RULE,
                source_ref=rel,
                content=f"trigger={trigger}",
                summary=f"Conditional rule: {filepath.stem}",
                tags=("conditional", trigger),
            ))

        hook_count = len(_PRE_HOOK_RE.findall(text)) + len(_POST_HOOK_RE.findall(text))
        if hook_count > 0:
            patterns.append(Pattern.from_source(
                pattern_type=PatternType.RULE,
                source_ref=rel,
                content=f"hooks={hook_count}",
                summary=f"Enforcement hooks: {hook_count} referenced",
                tags=("hooks", "enforcement"),
            ))

        mcp_count = len(_MCP_RE.findall(text))
        if mcp_count > 0:
            patterns.append(Pattern.from_source(
                pattern_type=PatternType.RULE,
                source_ref=rel,
                content=f"mcp_refs={mcp_count}",
                summary=f"MCP usage: {mcp_count} references",
                tags=("mcp",),
            ))

        skill_refs = set(_SKILL_RE.findall(text))
        if skill_refs:
            patterns.append(Pattern.from_source(
                pattern_type=PatternType.SKILL,
                source_ref=rel,
                content=f"skills={','.join(sorted(skill_refs))}",
                summary=f"Skill references: {len(skill_refs)} skills",
                tags=("skill",),
            ))

        return patterns

    def extract_all(self) -> Tuple[Pattern, ...]:
        all_patterns: list[Pattern] = []
        for fp in sorted(self._rules_dir.glob("*.md")):
            all_patterns.extend(self.extract_from_file(fp))
        return tuple(all_patterns)


__all__ = ["RulePatternEngine"]
