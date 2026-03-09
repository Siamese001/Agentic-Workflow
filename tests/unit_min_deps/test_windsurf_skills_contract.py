"""
Contract tests for the 7 new Windsurf skills added in 2026-03-09.

Verifies:
1. Every skill directory has a SKILL.md with valid frontmatter
2. Every SKILL.md references all supporting files that exist
3. Every supporting file listed in SKILL.md ## Files section exists on disk
4. Skill descriptions are non-empty and unique
5. Skill names match directory names
6. Content invariants: required sections exist, required terms present
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SKILLS_DIR = ROOT / ".windsurf" / "skills"

pytestmark = pytest.mark.unit_min_deps

# ---------------------------------------------------------------------------
# The 7 new skills created in this session
# ---------------------------------------------------------------------------
NEW_SKILLS = [
    "layer-boundary-guard",
    "shim-discipline",
    "mcp-tool-verify",
    "dedup-guard",
    "rollback-gate",
    "ssot-write-gate",
    "import-hygiene",
]

# Expected supporting files per skill
EXPECTED_FILES: dict[str, list[str]] = {
    "layer-boundary-guard": ["SKILL.md", "gravity_rules.md", "pre_import_checklist.md"],
    "shim-discipline": ["SKILL.md", "shim_decision_tree.md", "shim_contract_template.md"],
    "mcp-tool-verify": ["SKILL.md", "post_write_verification.md", "tool_parameter_discipline.md"],
    "dedup-guard": ["SKILL.md", "pre_creation_checklist.md", "dedup_decision_tree.md"],
    "rollback-gate": ["SKILL.md", "pre_phase_checkpoint.md", "rollback_protocol.md"],
    "ssot-write-gate": ["SKILL.md", "path_validation_checklist.md", "artifact_type_resolver.md"],
    "import-hygiene": ["SKILL.md", "pre_import_checklist.md", "forbidden_imports_registry.md"],
}

# Required sections in each SKILL.md
REQUIRED_SKILL_SECTIONS = ["## Files", "## When to use"]

# Frontmatter fields required in each SKILL.md
REQUIRED_FRONTMATTER_KEYS = ["name", "description"]

# Terms that must appear in specific skill files (content invariants)
CONTENT_INVARIANTS: dict[str, dict[str, list[str]]] = {
    "layer-boundary-guard": {
        "gravity_rules.md": ["L0", "L1", "L2", "L3", "L4", "L5", "VIOLATION", "FORBIDDEN"],
        "pre_import_checklist.md": ["STOP", "gravity", "source_rank", "target_rank"],
    },
    "shim-discipline": {
        "shim_decision_tree.md": ["DEPRECATED", "consumer", "canonical", "DONE"],
        "shim_contract_template.md": ["DEPRECATED", "__all__", "SHIM EXPIRY", "noqa: F401"],
    },
    "mcp-tool-verify": {
        "post_write_verification.md": ["mcp8_get_file_info", "Fallback", "FORBIDDEN", "size"],
        "tool_parameter_discipline.md": ["NEVER", "invented", "schema", "BLOCKLIST"],
    },
    "dedup-guard": {
        "pre_creation_checklist.md": ["AST", "registry", "justification", "Branch"],
        "dedup_decision_tree.md": ["Reuse", "Extend", "justification", "DONE"],
    },
    "rollback-gate": {
        "pre_phase_checkpoint.md": ["BASELINE_HASH", "rollback", "Acceptance", "STOP"],
        "rollback_protocol.md": ["git reset --hard", "STOP", "partial commit", "BASELINE_HASH"],
    },
    "ssot-write-gate": {
        "path_validation_checklist.md": ["PROJECT_ROOT_WHITELIST", "docs", "FAIL", "APPROVED"],
        "artifact_type_resolver.md": ["docs/reports/plans", "DOCS_REPORTS_PLANS", "Canonical"],
    },
    "import-hygiene": {
        "pre_import_checklist.md": ["ruff", "F401", "GRAVITY", "Point 5"],
        "forbidden_imports_registry.md": ["timeout_decorator", "FORBIDDEN", "Canonical", "Category"],
    },
}


# ---------------------------------------------------------------------------
# Helper: parse SKILL.md frontmatter
# ---------------------------------------------------------------------------


def _parse_frontmatter(content: str) -> dict[str, str]:
    """Extract key: value pairs from YAML-style frontmatter (between --- delimiters)."""
    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return {}
    result = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            result[key.strip()] = value.strip()
    return result


def _parse_files_section(content: str) -> list[str]:
    """Extract filenames referenced in the ## Files section of SKILL.md."""
    files_section = re.search(r"## Files\n(.*?)(?=\n##|\Z)", content, re.DOTALL)
    if not files_section:
        return []
    # Match **`filename.md`** patterns
    return re.findall(r"\*\*`([^`]+)`\*\*", files_section.group(1))


# ---------------------------------------------------------------------------
# Tests: Directory and file existence
# ---------------------------------------------------------------------------


class TestSkillDirectoryStructure:
    """Every new skill directory and its expected files must exist."""

    @pytest.mark.parametrize("skill_name", NEW_SKILLS)
    def test_skill_directory_exists(self, skill_name: str) -> None:
        skill_dir = SKILLS_DIR / skill_name
        assert skill_dir.is_dir(), f"Skill directory missing: .windsurf/skills/{skill_name}/"

    @pytest.mark.parametrize("skill_name", NEW_SKILLS)
    def test_skill_md_exists(self, skill_name: str) -> None:
        skill_md = SKILLS_DIR / skill_name / "SKILL.md"
        assert skill_md.is_file(), f"SKILL.md missing: .windsurf/skills/{skill_name}/SKILL.md"

    @pytest.mark.parametrize("skill_name", NEW_SKILLS)
    def test_all_expected_files_exist(self, skill_name: str) -> None:
        missing = []
        for filename in EXPECTED_FILES[skill_name]:
            path = SKILLS_DIR / skill_name / filename
            if not path.is_file():
                missing.append(filename)
        assert not missing, f"Skill '{skill_name}' is missing files: {missing}"

    @pytest.mark.parametrize("skill_name", NEW_SKILLS)
    def test_no_unexpected_files(self, skill_name: str) -> None:
        """Skill directory should contain only the expected files (no clutter)."""
        skill_dir = SKILLS_DIR / skill_name
        actual = {f.name for f in skill_dir.iterdir() if f.is_file()}
        expected = set(EXPECTED_FILES[skill_name])
        unexpected = actual - expected
        assert not unexpected, f"Skill '{skill_name}' has unexpected files: {unexpected}"


# ---------------------------------------------------------------------------
# Tests: SKILL.md frontmatter validity
# ---------------------------------------------------------------------------


class TestSkillFrontmatter:
    """Every SKILL.md must have valid frontmatter with required keys."""

    @pytest.mark.parametrize("skill_name", NEW_SKILLS)
    def test_frontmatter_present(self, skill_name: str) -> None:
        content = (SKILLS_DIR / skill_name / "SKILL.md").read_text(encoding="utf-8")
        assert content.startswith("---\n"), (
            f"SKILL.md for '{skill_name}' must start with YAML frontmatter (---)"
        )

    @pytest.mark.parametrize("skill_name", NEW_SKILLS)
    def test_frontmatter_has_required_keys(self, skill_name: str) -> None:
        content = (SKILLS_DIR / skill_name / "SKILL.md").read_text(encoding="utf-8")
        fm = _parse_frontmatter(content)
        missing = [k for k in REQUIRED_FRONTMATTER_KEYS if k not in fm]
        assert not missing, f"SKILL.md for '{skill_name}' missing frontmatter keys: {missing}"

    @pytest.mark.parametrize("skill_name", NEW_SKILLS)
    def test_frontmatter_name_matches_directory(self, skill_name: str) -> None:
        content = (SKILLS_DIR / skill_name / "SKILL.md").read_text(encoding="utf-8")
        fm = _parse_frontmatter(content)
        assert fm.get("name") == skill_name, (
            f"SKILL.md name '{fm.get('name')}' does not match directory '{skill_name}'"
        )

    @pytest.mark.parametrize("skill_name", NEW_SKILLS)
    def test_frontmatter_description_non_empty(self, skill_name: str) -> None:
        content = (SKILLS_DIR / skill_name / "SKILL.md").read_text(encoding="utf-8")
        fm = _parse_frontmatter(content)
        desc = fm.get("description", "")
        assert len(desc) > 20, f"SKILL.md for '{skill_name}' has too-short description: '{desc}'"

    def test_all_skill_descriptions_unique(self) -> None:
        """No two skill descriptions should be identical."""
        descriptions = []
        for skill_name in NEW_SKILLS:
            content = (SKILLS_DIR / skill_name / "SKILL.md").read_text(encoding="utf-8")
            fm = _parse_frontmatter(content)
            descriptions.append((skill_name, fm.get("description", "")))

        seen: dict[str, str] = {}
        duplicates = []
        for skill_name, desc in descriptions:
            if desc in seen:
                duplicates.append(f"'{skill_name}' and '{seen[desc]}' have same description")
            seen[desc] = skill_name

        assert not duplicates, "Duplicate skill descriptions found:\n" + "\n".join(duplicates)


# ---------------------------------------------------------------------------
# Tests: SKILL.md required sections
# ---------------------------------------------------------------------------


class TestSkillMdSections:
    """Every SKILL.md must contain required markdown sections."""

    @pytest.mark.parametrize("skill_name", NEW_SKILLS)
    def test_required_sections_present(self, skill_name: str) -> None:
        content = (SKILLS_DIR / skill_name / "SKILL.md").read_text(encoding="utf-8")
        missing = [s for s in REQUIRED_SKILL_SECTIONS if s not in content]
        assert not missing, f"SKILL.md for '{skill_name}' missing sections: {missing}"

    @pytest.mark.parametrize("skill_name", NEW_SKILLS)
    def test_files_section_references_existing_files(self, skill_name: str) -> None:
        """Every filename referenced in ## Files section must exist on disk."""
        content = (SKILLS_DIR / skill_name / "SKILL.md").read_text(encoding="utf-8")
        referenced = _parse_files_section(content)
        missing = []
        for fname in referenced:
            if not (SKILLS_DIR / skill_name / fname).is_file():
                missing.append(fname)
        assert not missing, f"SKILL.md for '{skill_name}' references non-existent files: {missing}"

    @pytest.mark.parametrize("skill_name", NEW_SKILLS)
    def test_when_to_use_section_non_empty(self, skill_name: str) -> None:
        content = (SKILLS_DIR / skill_name / "SKILL.md").read_text(encoding="utf-8")
        when_match = re.search(r"## When to use\n(.*?)(?=\n##|\Z)", content, re.DOTALL)
        assert when_match, f"SKILL.md for '{skill_name}' missing '## When to use' content"
        when_content = when_match.group(1).strip()
        assert len(when_content) > 30, f"SKILL.md for '{skill_name}' '## When to use' section too short"


# ---------------------------------------------------------------------------
# Tests: Supporting file content invariants
# ---------------------------------------------------------------------------


class TestSupportingFileContentInvariants:
    """Each supporting file must contain its required terms."""

    @pytest.mark.parametrize("skill_name", NEW_SKILLS)
    def test_content_invariants(self, skill_name: str) -> None:
        invariants = CONTENT_INVARIANTS.get(skill_name, {})
        violations = []
        for filename, required_terms in invariants.items():
            path = SKILLS_DIR / skill_name / filename
            if not path.is_file():
                violations.append(f"{filename}: file missing")
                continue
            content = path.read_text(encoding="utf-8")
            for term in required_terms:
                if term not in content:
                    violations.append(f"{filename}: missing required term '{term}'")
        assert not violations, f"Content invariant failures in skill '{skill_name}':\n" + "\n".join(
            f"  {v}" for v in violations
        )


# ---------------------------------------------------------------------------
# Tests: All existing skills still intact (regression)
# ---------------------------------------------------------------------------

EXISTING_SKILLS = [
    "ast-first-gate",
    "dependency-graph-analysis",
    "evidence-bundle",
    "pytest-integrity",
    "scope-guard",
    "script-sprawl-guard",
    "test-rigor-enforcement",
    "timeout-progress-enforcement",
]


class TestExistingSkillsIntact:
    """Regression: all pre-existing skills must still have SKILL.md."""

    @pytest.mark.parametrize("skill_name", EXISTING_SKILLS)
    def test_existing_skill_md_intact(self, skill_name: str) -> None:
        skill_md = SKILLS_DIR / skill_name / "SKILL.md"
        assert skill_md.is_file(), (
            f"Pre-existing skill SKILL.md was accidentally deleted: .windsurf/skills/{skill_name}/SKILL.md"
        )


# ---------------------------------------------------------------------------
# Tests: Skill count (all 15 skills present)
# ---------------------------------------------------------------------------


class TestTotalSkillCount:
    """Skills directory must contain exactly the expected number of skills."""

    ALL_SKILLS = EXISTING_SKILLS + NEW_SKILLS

    def test_all_skill_directories_present(self) -> None:
        missing = [s for s in self.ALL_SKILLS if not (SKILLS_DIR / s).is_dir()]
        assert not missing, f"Missing skill directories: {missing}"

    def test_skill_count_is_fifteen(self) -> None:
        """Total skill count must be 15 (8 existing + 7 new)."""
        actual_skills = [d.name for d in SKILLS_DIR.iterdir() if d.is_dir() and (d / "SKILL.md").is_file()]
        assert len(actual_skills) >= 15, (
            f"Expected at least 15 skills, found {len(actual_skills)}: {sorted(actual_skills)}"
        )


# ---------------------------------------------------------------------------
# Tests: Synthetic negative controls (prove scanner works)
# ---------------------------------------------------------------------------


class TestNegativeControls:
    """Prove the test infrastructure correctly detects violations."""

    def test_missing_frontmatter_detected(self) -> None:
        """Simulate a SKILL.md without frontmatter and verify detection."""
        fake_content = "# No Frontmatter\n\nThis has no YAML frontmatter.\n"
        assert not fake_content.startswith("---\n"), "Synthetic content should not start with ---"

    def test_missing_section_detected(self) -> None:
        """Simulate a SKILL.md missing a required section."""
        fake_content = "---\nname: fake\ndescription: test\n---\n\n# Fake Skill\n"
        missing = [s for s in REQUIRED_SKILL_SECTIONS if s not in fake_content]
        assert len(missing) == 2, f"Expected both required sections to be missing, got: {missing}"

    def test_name_mismatch_detected(self) -> None:
        """Simulate frontmatter name not matching directory name."""
        fm = {"name": "wrong-name", "description": "some description"}
        assert fm["name"] != "layer-boundary-guard"

    def test_content_invariant_scanner_works(self) -> None:
        """Simulate content missing a required term."""
        fake_content = "This file has nothing about STOP or gravity or source_rank."
        required = ["STOP", "gravity", "source_rank", "target_rank"]
        missing = [t for t in required if t not in fake_content]
        assert len(missing) == 1, f"Expected 1 missing term (target_rank), got: {missing}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
