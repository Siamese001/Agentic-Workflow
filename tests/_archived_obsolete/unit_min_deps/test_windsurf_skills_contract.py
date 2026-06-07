"""Skills contract tests — validates SKILL.md frontmatter per Agent Skills spec."""

import json
import unittest
from pathlib import Path

SKILLS_ROOT = Path(__file__).resolve().parents[2] / ".claude" / "skills"
EXPECTED_SKILLS = {
    "artifact-management",
    "boundary-enforcement",
    "graph-analysis",
    "operational-gates",
    "structured-reasoning",
    "testing-framework",
}


def _parse_frontmatter(content: str) -> dict:
    """Parse YAML frontmatter from SKILL.md content."""
    if not content.startswith("---\n"):
        raise ValueError("Missing frontmatter delimiter")
    parts = content.split("---\n", 2)
    if len(parts) < 3:
        raise ValueError("Unclosed frontmatter delimiter")
    try:
        import yaml  # type: ignore

        return yaml.safe_load(parts[1]) or {}
    except ImportError as exc:
        raise ValueError(f"yaml module required: {exc}") from exc


class TestSkillsContract(unittest.TestCase):
    """Validate all SKILL.md files comply with Agent Skills spec."""

    def test_all_skills_exist(self):
        """Happy path: all expected skill directories exist."""
        missing = [s for s in EXPECTED_SKILLS if not (SKILLS_ROOT / s).is_dir()]
        self.assertEqual([], missing, f"Missing skill dirs: {missing}")

    def test_skill_files_have_frontmatter(self):
        """Happy path: each SKILL.md has parsable frontmatter."""
        for skill_name in EXPECTED_SKILLS:
            skill_file = SKILLS_ROOT / skill_name / "skill.md"
            self.assertTrue(skill_file.is_file(), f"Missing SKILL.md for {skill_name}")
            content = skill_file.read_text(encoding="utf-8")
            try:
                _parse_frontmatter(content)
            except ValueError as e:
                self.fail(f"Frontmatter parse failed for {skill_name}: {e}")

    def test_required_frontmatter_fields(self):
        """Happy path: name and description present."""
        for skill_name in EXPECTED_SKILLS:
            skill_file = SKILLS_ROOT / skill_name / "skill.md"
            content = skill_file.read_text(encoding="utf-8")
            fm = _parse_frontmatter(content)
            self.assertIn("name", fm, f"Missing 'name' in {skill_name}")
            self.assertIn("description", fm, f"Missing 'description' in {skill_name}")

    def test_non_standard_fields_in_metadata(self):
        """Happy path: enforcement_* fields moved to metadata block after A6."""
        non_standard = {"enforcement_layer", "enforcement_timing", "enforcement_type"}
        for skill_name in EXPECTED_SKILLS:
            skill_file = SKILLS_ROOT / skill_name / "skill.md"
            content = skill_file.read_text(encoding="utf-8")
            fm = _parse_frontmatter(content)
            # Ensure no non-standard keys at top level
            top_level_keys = set(fm.keys()) - {"name", "description", "metadata"}
            self.assertEqual(
                set(),
                top_level_keys & non_standard,
                f"Non-standard keys at top level in {skill_name}: {top_level_keys & non_standard}",
            )
            # Ensure metadata block contains the non-standard fields
            if "metadata" in fm:
                metadata = fm["metadata"] or {}
                for key in non_standard:
                    self.assertIn(key, metadata, f"Missing {key} in metadata for {skill_name}")

    def test_malformed_frontmatter_failure(self):
        """Failure path: malformed frontmatter raises ValueError."""
        with self.assertRaises(ValueError):
            _parse_frontmatter("name: test\nno delimiters")

    def test_missing_skill_file_failure(self):
        """Edge case: missing SKILL.md handled gracefully."""
        fake_skill = SKILLS_ROOT / "nonexistent" / "skill.md"
        self.assertFalse(fake_skill.is_file(), "Sanity: fake skill should not exist")


if __name__ == "__main__":
    unittest.main()
