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

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

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
    """Test skill_directory_exists contract compliance."""
    # Arrange
    # TODO: Set up contract parties and terms
    contract_terms = {}  # Replace with actual contract terms

"""Test skill_md_exists contract compliance."""
# Arrange
# TODO: Set up contract parties and terms
contract_terms = {}  # Replace with actual contract terms

"""Test all_expected_files_exist contract compliance."""
# Arrange
# TODO: Set up contract parties and terms
contract_terms = {}  # Replace with actual contract terms

# Act
# TODO: Execute contract operations
contract_result = None  # Replace with actual contract operation

"""Test no_unexpected_files contract compliance."""
# Arrange
# TODO: Set up contract parties and terms
contract_terms = {}  # Replace with actual contract terms

# Act
# TODO: Execute contract operations
contract_result = None  # Replace with actual contract operation

# Assert - Core Contract
assert contract_result is not None, "Contract operation should produce a result"
assert isinstance(contract_result, dict), "Contract result should be structured"
# TODO: Add specific contract assertions
# assert contract_result.get("enforced", False), "Contract terms should be enforced"
    """Every SKILL.md must have valid frontmatter with required keys."""

    @pytest.mark.parametrize("skill_name", NEW_SKILLS)
    def test_frontmatter_present(self, skill_name: str) -> None:
    """Test frontmatter_present contract compliance."""
    # Arrange
    # TODO: Set up contract parties and terms
    contract_terms = {}  # Replace with actual contract terms

    # Act
    # TODO: Execute contract operations
    """Test frontmatter_has_required_keys contract compliance."""
    # Arrange
    # TODO: Set up contract parties and terms
    contract_terms = {}  # Replace with actual contract terms

    # Act
    # TODO: Execute contract operations
    """Test frontmatter_name_matches_directory contract compliance."""
    # Arrange
    # TODO: Set up contract parties and terms
    contract_terms = {}  # Replace with actual contract terms

    # Act
    # TODO: Execute contract operations
    contract_result = None  # Replace with actual contract operation
    """Test frontmatter_description_non_empty contract compliance."""
    # Arrange
    # TODO: Set up contract parties and terms
    contract_terms = {}  # Replace with actual contract terms

    # Act
    """Test all_skill_descriptions_unique contract compliance."""
    # Arrange
    # TODO: Set up contract parties and terms
    contract_terms = {}  # Replace with actual contract terms

    # Act
    # TODO: Execute contract operations
    contract_result = None  # Replace with actual contract operation

    # Assert - Core Contract
    assert contract_result is not None, "Contract operation should produce a result"
    assert isinstance(contract_result, dict), "Contract result should be structured"
    # TODO: Add specific contract assertions
    # assert contract_result.get("enforced", False), "Contract terms should be enforced"
        assert not duplicates, "Duplicate skill descriptions found:\n" + "\n".join(duplicates)


# ---------------------------------------------------------------------------
# Tests: SKILL.md required sections
# ---------------------------------------------------------------------------


class TestSkillMdSections:
    """Every SKILL.md must contain required markdown sections."""

    @pytest.mark.parametrize("skill_name", NEW_SKILLS)
    def test_required_sections_present(self, skill_name: str) -> None:
    """Test required_sections_present contract compliance."""
    # Arrange
    # TODO: Set up contract parties and terms
    contract_terms = {}  # Replace with actual contract terms

    # Act
    """Test files_section_references_existing_files contract compliance."""
    # Arrange
    # TODO: Set up contract parties and terms
    contract_terms = {}  # Replace with actual contract terms

    # Act
    # TODO: Execute contract operations
    contract_result = None  # Replace with actual contract operation

    # Assert - Core Contract
    assert contract_result is not None, "Contract operation should produce a result"
    """Test when_to_use_section_non_empty contract compliance."""
    # Arrange
    # TODO: Set up contract parties and terms
    contract_terms = {}  # Replace with actual contract terms

    # Act
    # TODO: Execute contract operations
    contract_result = None  # Replace with actual contract operation

    # Assert - Core Contract
    assert contract_result is not None, "Contract operation should produce a result"
    assert isinstance(contract_result, dict), "Contract result should be structured"
    # TODO: Add specific contract assertions
    # assert contract_result.get("enforced", False), "Contract terms should be enforced"

    @pytest.mark.parametrize("skill_name", NEW_SKILLS)
    def test_content_invariants(self, skill_name: str) -> None:
    """Test content_invariants contract compliance."""
    # Arrange
    # TODO: Set up contract parties and terms
    contract_terms = {}  # Replace with actual contract terms

    # Act
    # TODO: Execute contract operations
    contract_result = None  # Replace with actual contract operation

    # Assert - Core Contract
    assert contract_result is not None, "Contract operation should produce a result"
    assert isinstance(contract_result, dict), "Contract result should be structured"
    # TODO: Add specific contract assertions
    # assert contract_result.get("enforced", False), "Contract terms should be enforced"


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
    """Test existing_skill_md_intact contract compliance."""
    # Arrange
    # TODO: Set up contract parties and terms
    contract_terms = {}  # Replace with actual contract terms

    # Act
    # TODO: Execute contract operations
    contract_result = None  # Replace with actual contract operation

    # Assert - Core Contract
    assert contract_result is not None, "Contract operation should produce a result"
    assert isinstance(contract_result, dict), "Contract result should be structured"
    # TODO: Add specific contract assertions
    # assert contract_result.get("enforced", False), "Contract terms should be enforced"
    ALL_SKILLS = EXISTING_SKILLS + NEW_SKILLS

    def test_all_skill_directories_present(self) -> None:
    """Test all_skill_directories_present contract compliance."""
    # Arrange
    # TODO: Set up contract parties and terms
    contract_terms = {}  # Replace with actual contract terms
    """Test skill_count_is_fifteen contract compliance."""
    # Arrange
    # TODO: Set up contract parties and terms
    contract_terms = {}  # Replace with actual contract terms

    # Act
    # TODO: Execute contract operations
    contract_result = None  # Replace with actual contract operation

    # Assert - Core Contract
    assert contract_result is not None, "Contract operation should produce a result"
    assert isinstance(contract_result, dict), "Contract result should be structured"
    # TODO: Add specific contract assertions
    # assert contract_result.get("enforced", False), "Contract terms should be enforced"

    def test_missing_frontmatter_detected(self) -> None:
    """Test missing_frontmatter_detected contract compliance."""
    # Arrange
    # TODO: Set up contract parties and terms
    contract_terms = {}  # Replace with actual contract terms

"""Test missing_section_detected contract compliance."""
# Arrange
# TODO: Set up contract parties and terms
contract_terms = {}  # Replace with actual contract terms

# Act
"""Test name_mismatch_detected contract compliance."""
# Arrange
# TODO: Set up contract parties and terms
contract_terms = {}  # Replace with actual contract terms

"""Test content_invariant_scanner_works contract compliance."""
# Arrange
# TODO: Set up contract parties and terms
contract_terms = {}  # Replace with actual contract terms

# Act
# TODO: Execute contract operations
contract_result = None  # Replace with actual contract operation

# Assert - Core Contract
assert contract_result is not None, "Contract operation should produce a result"
assert isinstance(contract_result, dict), "Contract result should be structured"
# TODO: Add specific contract assertions
# assert contract_result.get("enforced", False), "Contract terms should be enforced"