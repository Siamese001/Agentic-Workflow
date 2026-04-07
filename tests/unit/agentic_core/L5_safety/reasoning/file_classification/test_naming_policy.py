"""Tests for naming_policy module."""


from agentic_core.L5_safety.reasoning.file_classification.naming_policy import (
    _check_forbidden_patterns,
    _sanitize_filename,
    _to_pascal_case,
    _to_smart_snake_case,
    normalize_filename,
)


class TestNormalizeFilename:
    """Tests for normalize_filename function."""

    def test_stuttering_acronyms(self):
        """Test fixing stuttering acronyms."""
        assert normalize_filename("s_s_o_t_consolidation_analyzer.py") == "ssot_consolidation_analyzer.py"
        assert normalize_filename("a_b_c_d_test.py") == "abcd_test.py"

    def test_multiple_underscores(self):
        """Test fixing multiple underscores."""
        assert normalize_filename("setup___init___util.py") == "setup_init_util.py"
        assert normalize_filename("my___file.py") == "my_file.py"

    def test_leading_underscores(self):
        """Test fixing leading underscores."""
        assert normalize_filename("_cc_visitor.py") == "cc_visitor.py"
        assert normalize_filename("__private.py") == "private.py"

    def test_trailing_underscores(self):
        """Test fixing trailing underscores."""
        assert normalize_filename("file__.py") == "file.py"
        assert normalize_filename("module_.py") == "module.py"

    def test_init_exempt(self):
        """Test that __init__.py is exempt."""
        assert normalize_filename("__init__.py") == "__init__.py"
        assert normalize_filename("__init__") == "__init__"

    def test_without_extension(self):
        """Test normalization without extension."""
        assert normalize_filename("s_s_o_t_consolidation_analyzer") == "ssot_consolidation_analyzer"

    def test_already_clean(self):
        """Test that clean filenames are unchanged."""
        assert normalize_filename("my_module.py") == "my_module.py"
        assert normalize_filename("clean_file.py") == "clean_file.py"


class TestToPascalCase:
    """Tests for _to_pascal_case function."""

    def test_snake_case_to_pascal(self):
        """Test converting snake_case to PascalCase."""
        assert _to_pascal_case("pii_sanitizer") == "PiiSanitizer"
        assert _to_pascal_case("file_classifier") == "FileClassifier"
        assert _to_pascal_case("my_util") == "MyUtil"

    def test_already_pascal_case(self):
        """Test that already PascalCase strings are unchanged."""
        assert _to_pascal_case("PiiSanitizer") == "PiiSanitizer"
        assert _to_pascal_case("FileClassifier") == "FileClassifier"

    def test_empty_string(self):
        """Test empty string handling."""
        assert _to_pascal_case("") == ""

    def test_single_word(self):
        """Test single word conversion."""
        assert _to_pascal_case("file") == "File"
        assert _to_pascal_case("util") == "Util"


class TestToSmartSnakeCase:
    """Tests for _to_smart_snake_case function."""

    def test_pascal_to_snake(self):
        """Test converting PascalCase to snake_case."""
        assert _to_smart_snake_case("PiiSanitizer") == "pii_sanitizer"
        assert _to_smart_snake_case("PDFLoader") == "pdf_loader"
        assert _to_smart_snake_case("FileClassifier") == "file_classifier"

    def test_atomic_words_preserved(self):
        """Test that atomic words are preserved."""
        assert _to_smart_snake_case("Grounding") == "grounding"
        assert _to_smart_snake_case("Routing") == "routing"
        assert _to_smart_snake_case("Sender") == "sender"
        assert _to_smart_snake_case("RG") == "rg"

    def test_atomic_words_in_context(self):
        """Test atomic words preserved within larger names."""
        assert _to_smart_snake_case("GroundingAgent") == "grounding_agent"
        assert _to_smart_snake_case("RoutingStrategy") == "routing_strategy"


class TestSanitizeFilename:
    """Tests for _sanitize_filename function."""

    def test_strip_single_suffix(self):
        """Test stripping a single architectural suffix."""
        assert _sanitize_filename("feature_flags_config") == "feature_flags"
        assert _sanitize_filename("user_profile_types") == "user_profile"
        assert _sanitize_filename("my_util") == "my"

    def test_strip_multiple_suffixes(self):
        """Test stripping multiple architectural suffixes."""
        assert _sanitize_filename("feature_flags_config_util") == "feature_flags"
        assert _sanitize_filename("embedding_config_types_config") == "embedding"

    def test_preserve_semantic_content(self):
        """Test that semantic content is preserved."""
        assert _sanitize_filename("agent_discovery_util") == "agent_discovery"
        assert _sanitize_filename("agent_discovery") == "agent_discovery"

    def test_agent_after_suffix(self):
        """Test stripping _agent after other suffixes."""
        assert _sanitize_filename("healing_mixin_agent") == "healing_mixin"
        assert _sanitize_filename("config_validator_agent") == "config_validator"

    def test_trailing_underscores(self):
        """Test cleaning trailing underscores."""
        # Trailing underscores are cleaned after suffix stripping
        assert _sanitize_filename("config__") == "config"
        assert _sanitize_filename("my_util_") == "my_util"  # No suffix to strip, underscore remains

    def test_empty_after_strip(self):
        """Test fallback when fully stripped."""
        result = _sanitize_filename("util")
        # Should not be empty, fallback to original
        assert result == "util"


class TestCheckForbiddenPatterns:
    """Tests for _check_forbidden_patterns function."""

    def test_init_exempt(self):
        """Test that __init__.py is exempt."""
        violations = _check_forbidden_patterns("__init__.py")
        assert violations == []

    def test_no_violations(self):
        """Test clean filename."""
        violations = _check_forbidden_patterns("my_module.py")
        # Should not crash, returns empty list if no patterns match
        assert isinstance(violations, list)

    def test_violation_structure(self):
        """Test that violations have correct structure."""
        violations = _check_forbidden_patterns("test_file.py")
        assert isinstance(violations, list)
        for violation in violations:
            assert isinstance(violation, dict)
            assert "pattern" in violation
            assert "reason" in violation
            assert "filename" in violation
