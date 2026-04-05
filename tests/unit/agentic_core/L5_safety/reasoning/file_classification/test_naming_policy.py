"""Tests for naming_policy module."""

import pytest

from agentic_core.L5_safety.reasoning.file_classification.naming_policy import (
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
