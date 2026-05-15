"""
STOP 4A validation test for strategic_tailor_v2 executive_summary section_budget.
Verifies no word-count targets exist (target_words, max_words, etc.).
"""
import re
import pytest
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent
TEMPLATE_PATH = REPO_ROOT / "apps_rg" / "prompt_assembly" / "templates" / "strategic_tailor_v2.yaml"

# Forbidden word-count patterns for executive_summary per STOP 4
FORBIDDEN_PATTERNS = [
    r'target_words\s*:\s*"?\d+',  # target_words: 40 or target_words: "40-80"
    r'max_words\s*:\s*\d+',  # max_words: 80
    r'min_words\s*:\s*\d+',  # min_words: 40
    r'target_lines\s*:\s*\d+',  # target_lines: 4
    r'max_lines\s*:\s*\d+',  # max_lines: 4
    r'word_range\s*:\s*\[?\d+\s*[-,]\s*\d+',  # word_range: 40-80 or [40, 80]
    r'word_count\s*:\s*\d+',  # word_count: 60
]

# Required fit-based patterns
REQUIRED_PATTERNS = [
    r'length_policy\s*:\s*"fit_to_evidence"',
]


def load_template() -> str:
    """Load strategic_tailor_v2.yaml content."""
    if not TEMPLATE_PATH.exists():
        pytest.fail(f"Template not found: {TEMPLATE_PATH}")
    return TEMPLATE_PATH.read_text(encoding="utf-8")


def extract_executive_summary_section_budget(content: str) -> str:
    """Extract the executive_summary section_budget entry from the template."""
    # Find the section_budget block and extract executive_summary line
    section_budget_pattern = r'<section_budget>.*?</section_budget>'
    match = re.search(section_budget_pattern, content, re.DOTALL)
    if not match:
        pytest.fail("section_budget block not found in template")
    
    section_budget_content = match.group(0)
    
    # Find the executive_summary line within section_budget
    exec_summary_pattern = r'- executive_summary:\s*\{[^}]+\}'
    exec_match = re.search(exec_summary_pattern, section_budget_content)
    if not exec_match:
        pytest.fail("executive_summary section_budget entry not found")
    
    return exec_match.group(0)


class TestExecutiveSummarySectionBudget:
    """STOP 4 enforcement: executive_summary must use fit-based length only."""

    def test_no_target_words_in_executive_summary(self):
        """FAIL if executive_summary section_budget contains target_words."""
        content = load_template()
        exec_summary = extract_executive_summary_section_budget(content)
        
        pattern = re.compile(r'target_words\s*:\s*"?[^"\s]+')
        match = pattern.search(exec_summary)
        
        assert match is None, (
            f"STOP 4 VIOLATION: executive_summary contains target_words.\n"
            f"Found: {match.group(0) if match else 'N/A'}\n"
            f"STOP 4 requires: no target_words, no max_words, fit-based length only."
        )

    def test_no_max_words_in_executive_summary(self):
        """FAIL if executive_summary section_budget contains max_words."""
        content = load_template()
        exec_summary = extract_executive_summary_section_budget(content)
        
        pattern = re.compile(r'max_words\s*:\s*\d+')
        match = pattern.search(exec_summary)
        
        assert match is None, (
            f"STOP 4 VIOLATION: executive_summary contains max_words.\n"
            f"Found: {match.group(0) if match else 'N/A'}\n"
            f"STOP 4 requires: no max_words, fit-based length only."
        )

    def test_no_word_range_in_executive_summary(self):
        """FAIL if executive_summary section_budget contains word range patterns."""
        content = load_template()
        exec_summary = extract_executive_summary_section_budget(content)
        
        # Check for patterns like "40-80", "40 to 80", "min 40 max 80"
        range_patterns = [
            r'"?\d+\s*[-–]\s*\d+"?',  # 40-80 or 40–80
            r'min\s*\d+.*max\s*\d+',  # min 40 max 80
            r'\d+\s*to\s*\d+\s*words?',  # 40 to 80 words
        ]
        
        for pattern_str in range_patterns:
            pattern = re.compile(pattern_str, re.IGNORECASE)
            match = pattern.search(exec_summary)
            assert match is None, (
                f"STOP 4 VIOLATION: executive_summary contains word range.\n"
                f"Found: {match.group(0)}\n"
                f"STOP 4 requires: no word ranges, fit-based length only."
            )

    def test_has_length_policy_fit_to_evidence(self):
        """PASS if executive_summary section_budget has length_policy: fit_to_evidence."""
        content = load_template()
        exec_summary = extract_executive_summary_section_budget(content)
        
        pattern = re.compile(r'length_policy\s*:\s*"fit_to_evidence"')
        match = pattern.search(exec_summary)
        
        assert match is not None, (
            f"STOP 4 REQUIREMENT MISSING: executive_summary must have length_policy: fit_to_evidence.\n"
            f"Found section_budget: {exec_summary}\n"
            f"STOP 4 requires: length_policy: fit_to_evidence."
        )

    def test_max_tokens_is_allowed(self):
        """PASS if executive_summary has max_tokens (runtime budget, not writing target)."""
        content = load_template()
        exec_summary = extract_executive_summary_section_budget(content)
        
        pattern = re.compile(r'max_tokens\s*:\s*\d+')
        match = pattern.search(exec_summary)
        
        assert match is not None, (
            f"STOP 4 CONCERN: executive_summary should have max_tokens as runtime budget.\n"
            f"Found section_budget: {exec_summary}"
        )

    def test_no_forbidden_word_count_targets(self):
        """Comprehensive test: no forbidden word-count targets in executive_summary."""
        content = load_template()
        exec_summary = extract_executive_summary_section_budget(content)
        
        forbidden_found = []
        for pattern_str in FORBIDDEN_PATTERNS:
            pattern = re.compile(pattern_str, re.IGNORECASE)
            match = pattern.search(exec_summary)
            if match:
                forbidden_found.append(match.group(0))
        
        assert len(forbidden_found) == 0, (
            f"STOP 4 VIOLATIONS: executive_summary contains forbidden word-count targets:\n"
            f"Found: {forbidden_found}\n"
            f"STOP 4 requires: fit-based length only (length_policy: fit_to_evidence)."
        )


class TestStrategicTailorV2SchemaCompliance:
    """Additional STOP 2 and STOP 4 compliance tests for strategic_tailor_v2."""

    def test_planning_only_no_resume_prose(self):
        """Verify template contains planning-only constraint (no resume prose generation)."""
        content = load_template()
        
        # Check for v4_planning_schema marker
        assert "v4_planning_schema" in content, (
            "strategic_tailor_v2 must use v4_planning_schema"
        )
        
        # Check for planning-only prohibition
        prose_prohibition = "NO resume prose" in content or "no_resume_prose" in content
        assert prose_prohibition, (
            "strategic_tailor_v2 must prohibit resume prose in output"
        )

    def test_temperature_profile_low_range(self):
        """Verify temperature profile is 0.1-0.2 (low, consistent)."""
        content = load_template()
        
        temp_pattern = re.compile(r'range\s*:\s*"0\.\d+\s*-\s*0\.\d+"')
        match = temp_pattern.search(content)
        
        if match:
            range_str = match.group(0)
            # Extract numbers
            nums = re.findall(r'0\.\d+', range_str)
            if nums:
                low, high = float(nums[0]), float(nums[1])
                assert low <= 0.2 and high <= 0.25, (
                    f"strategic_tailor_v2 temperature should be low (0.1-0.2). Found: {range_str}"
                )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
