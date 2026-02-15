"""Unit tests for prompt loading infrastructure."""

from pathlib import Path

import pytest

from agentic_core.prompt_governance.prompt_loader import (
    PromptLoader,
    PromptLoadError,
    PromptSchemaError,
)


class TestPromptLoader:
    """Test suite for PromptLoader with deterministic behavior."""

    def test_init_with_valid_directory(self, tmp_path: Path) -> None:
        """Test successful initialization with valid directory."""
        loader = PromptLoader(tmp_path)
        assert loader._prompt_dir == tmp_path.resolve()
        assert loader.cache_info()["cached_items"] == 0

    def test_init_with_invalid_directory(self) -> None:
        """Test initialization fails with non-existent directory."""
        with pytest.raises(ValueError, match="prompt_dir must be a directory"):
            PromptLoader(Path("/non/existent/path"))

    def test_init_with_file(self, tmp_path: Path) -> None:
        """Test initialization fails with file instead of directory."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        with pytest.raises(ValueError, match="prompt_dir must be a directory"):
            PromptLoader(test_file)

    def test_init_with_wrong_type(self) -> None:
        """Test initialization fails with wrong type."""
        with pytest.raises(TypeError, match="prompt_dir must be a Path object"):
            PromptLoader("/string/path")  # type: ignore

    def test_load_prompt_success(self, tmp_path: Path) -> None:
        """Test successful prompt loading."""
        # Create test prompt structure
        (tmp_path / "test_domain").mkdir()
        prompt_file = tmp_path / "test_domain" / "test_prompt.yaml"
        prompt_file.write_text("""
template: "Hello {name}!"
constraints:
  - "constraint 1"
  - "constraint 2"
""")

        loader = PromptLoader(tmp_path)
        result = loader.load_prompt("test_domain", "test_prompt")

        assert result["template"] == "Hello {name}!"
        assert result["constraints"] == ["constraint 1", "constraint 2"]
        assert loader.cache_info()["cached_items"] == 1

    def test_load_prompt_missing_file(self, tmp_path: Path) -> None:
        """Test error when prompt file is missing."""
        loader = PromptLoader(tmp_path)

        with pytest.raises(PromptLoadError, match="Prompt file not found"):
            loader.load_prompt("missing", "missing")

    def test_load_prompt_path_is_directory(self, tmp_path: Path) -> None:
        """Test error when path is directory instead of file."""
        # Create directory where file should be
        (tmp_path / "test_domain").mkdir()
        (tmp_path / "test_domain" / "test_prompt").mkdir()  # Directory, not file

        loader = PromptLoader(tmp_path)

        with pytest.raises(PromptLoadError):
            loader.load_prompt("test_domain", "test_prompt")

    def test_load_prompt_invalid_yaml(self, tmp_path: Path) -> None:
        """Test error with invalid YAML."""
        (tmp_path / "test_domain").mkdir()
        prompt_file = tmp_path / "test_domain" / "invalid.yaml"
        prompt_file.write_text("invalid: yaml: content: [")

        loader = PromptLoader(tmp_path)

        with pytest.raises(PromptLoadError, match="Invalid YAML"):
            loader.load_prompt("test_domain", "invalid")

    def test_load_prompt_missing_template_key(self, tmp_path: Path) -> None:
        """Test error when template key is missing."""
        (tmp_path / "test_domain").mkdir()
        prompt_file = tmp_path / "test_domain" / "no_template.yaml"
        prompt_file.write_text("name: test")

        loader = PromptLoader(tmp_path)

        with pytest.raises(PromptSchemaError, match="Missing required 'template' key"):
            loader.load_prompt("test_domain", "no_template")

    def test_load_prompt_template_not_string(self, tmp_path: Path) -> None:
        """Test error when template is not a string."""
        (tmp_path / "test_domain").mkdir()
        prompt_file = tmp_path / "test_domain" / "bad_template.yaml"
        prompt_file.write_text("template: 123")

        loader = PromptLoader(tmp_path)

        with pytest.raises(PromptSchemaError, match="'template' must be a string"):
            loader.load_prompt("test_domain", "bad_template")

    def test_load_prompt_not_dict(self, tmp_path: Path) -> None:
        """Test error when prompt is not a dict."""
        (tmp_path / "test_domain").mkdir()
        prompt_file = tmp_path / "test_domain" / "not_dict.yaml"
        prompt_file.write_text('"string instead of dict"')

        loader = PromptLoader(tmp_path)

        with pytest.raises(PromptSchemaError, match="Prompt must be a dict"):
            loader.load_prompt("test_domain", "not_dict")

    def test_load_prompt_invalid_domain(self, tmp_path: Path) -> None:
        """Test error with invalid domain parameter."""
        loader = PromptLoader(tmp_path)

        with pytest.raises(ValueError, match="domain must be a non-empty string"):
            loader.load_prompt("", "test")

        with pytest.raises(ValueError, match="domain must be a non-empty string"):
            loader.load_prompt(None, "test")  # type: ignore

    def test_load_prompt_invalid_name(self, tmp_path: Path) -> None:
        """Test error with invalid name parameter."""
        loader = PromptLoader(tmp_path)

        with pytest.raises(ValueError, match="name must be a non-empty string"):
            loader.load_prompt("test", "")

        with pytest.raises(ValueError, match="name must be a non-empty string"):
            loader.load_prompt("test", None)  # type: ignore

    def test_get_template_success(self, tmp_path: Path) -> None:
        """Test successful template formatting."""
        (tmp_path / "test_domain").mkdir()
        prompt_file = tmp_path / "test_domain" / "test_prompt.yaml"
        prompt_file.write_text("""
template: "Hello {user_name}! Constraints: {constraints}"
constraints:
  - "be nice"
  - "be professional"
""")

        loader = PromptLoader(tmp_path)
        result = loader.get_template("test_domain", "test_prompt", user_name="World")

        assert result == "Hello World! Constraints: be nice\nbe professional"

    def test_get_template_missing_variable(self, tmp_path: Path) -> None:
        """Test error when template variable is missing."""
        (tmp_path / "test_domain").mkdir()
        prompt_file = tmp_path / "test_domain" / "test_prompt.yaml"
        prompt_file.write_text("template: 'Hello {missing}!'")

        loader = PromptLoader(tmp_path)

        with pytest.raises(PromptSchemaError, match="Missing template variable"):
            loader.get_template("test_domain", "test_prompt")

    def test_get_template_no_constraints(self, tmp_path: Path) -> None:
        """Test template formatting without constraints."""
        (tmp_path / "test_domain").mkdir()
        prompt_file = tmp_path / "test_domain" / "test_prompt.yaml"
        prompt_file.write_text("template: 'Hello {user_name}!'")

        loader = PromptLoader(tmp_path)
        result = loader.get_template("test_domain", "test_prompt", user_name="World")

        assert result == "Hello World!"

    def test_get_template_invalid_constraints_type(self, tmp_path: Path) -> None:
        """Test error when constraints is not a list."""
        (tmp_path / "test_domain").mkdir()
        prompt_file = tmp_path / "test_domain" / "test_prompt.yaml"
        prompt_file.write_text("""
template: "Hello {user_name}!"
constraints: "not a list"
""")

        loader = PromptLoader(tmp_path)

        with pytest.raises(PromptSchemaError, match="'constraints' must be a list"):
            loader.get_template("test_domain", "test_prompt", user_name="World")

    def test_cache_behavior(self, tmp_path: Path) -> None:
        """Test caching behavior."""
        (tmp_path / "test_domain").mkdir()
        prompt_file = tmp_path / "test_domain" / "test_prompt.yaml"
        prompt_file.write_text("template: 'Hello {user_name}!'")

        loader = PromptLoader(tmp_path)

        # First load - cache miss
        result1 = loader.load_prompt("test_domain", "test_prompt")
        assert loader.cache_info()["cached_items"] == 1

        # Second load - cache hit
        result2 = loader.load_prompt("test_domain", "test_prompt")
        assert loader.cache_info()["cached_items"] == 1
        assert result1 is result2  # Same object from cache

    def test_clear_cache(self, tmp_path: Path) -> None:
        """Test cache clearing."""
        (tmp_path / "test_domain").mkdir()
        prompt_file = tmp_path / "test_domain" / "test_prompt.yaml"
        prompt_file.write_text("template: 'Hello {user_name}!'")

        loader = PromptLoader(tmp_path)
        loader.load_prompt("test_domain", "test_prompt")

        assert loader.cache_info()["cached_items"] == 1

        loader.clear_cache()
        assert loader.cache_info()["cached_items"] == 0

    def test_cache_info_structure(self, tmp_path: Path) -> None:
        """Test cache info returns correct structure."""
        loader = PromptLoader(tmp_path)
        info = loader.cache_info()

        assert isinstance(info, dict)
        assert "cached_items" in info
        assert "cache_keys" in info
        assert isinstance(info["cached_items"], int)
        assert isinstance(info["cache_keys"], list)
