"""
Unit tests for NamingAgent - Comprehensive naming validation across all file types.

Tests cover:
- Word counting (PascalCase and snake_case)
- File type detection
- Naming pattern validation
- Word count limits
- High-signal requirement enforcement
- Agent class matching
- Multi-file-type support (.py, .jinja, .json, .yaml, .md, .txt)
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from agentic_core.utils.core_extensions.NamingAgent import NamingAgent


@pytest.fixture
def naming_agent(tmp_path):
    """Create a NamingAgent instance with a temporary project root."""
    return NamingAgent(tmp_path)


class TestWordCounting:
    """Test word counting in filenames."""
    
    def test_count_words_pascal_case(self, naming_agent):
        """Test word counting in PascalCase names."""
        assert naming_agent._count_words_in_name("HealerAgent.py") == 2
        assert naming_agent._count_words_in_name("CodeDeduplicationAgent.py") == 3
        assert naming_agent._count_words_in_name("NamingAgent.py") == 2
        assert naming_agent._count_words_in_name("DuplicateCodeDetectorAgent.py") == 4
    
    def test_count_words_snake_case(self, naming_agent):
        """Test word counting in snake_case names."""
        assert naming_agent._count_words_in_name("sovereign_ingestion.py") == 2
        assert naming_agent._count_words_in_name("canon_validator_base.py") == 3
        assert naming_agent._count_words_in_name("semantic_cache.py") == 2
        assert naming_agent._count_words_in_name("hybrid_retriever.py") == 2
    
    def test_count_words_single_word(self, naming_agent):
        """Test single-word filenames."""
        assert naming_agent._count_words_in_name("config.py") == 1
        assert naming_agent._count_words_in_name("utils.py") == 1


class TestFileTypeDetection:
    """Test file type category detection."""
    
    def test_detect_agent_file(self, naming_agent, tmp_path):
        """Test detection of Agent files."""
        agent_file = tmp_path / "agentic_core/L2_execution/tool_registry/HealerAgent.py"
        assert naming_agent._get_file_type(agent_file) == "agent"
    
    def test_detect_base_class_file(self, naming_agent, tmp_path):
        """Test detection of base class files."""
        base_file = tmp_path / "apps_lic/engines/outreach_engine/autonomous/outreach_base.py"
        assert naming_agent._get_file_type(base_file) == "base_class"
    
    def test_detect_script_file(self, naming_agent, tmp_path):
        """Test detection of script files."""
        script_file = tmp_path / "agentic_core/L0_maintenance/scripts/sovereign_ingestion.py"
        assert naming_agent._get_file_type(script_file) == "script"
    
    def test_detect_core_module_file(self, naming_agent, tmp_path):
        """Test detection of core module files."""
        module_file = tmp_path / "agentic_core/runtime/shared_runtime/semantic_cache.py"
        assert naming_agent._get_file_type(module_file) == "core_module"
    
    def test_detect_jinja_template(self, naming_agent, tmp_path):
        """Test detection of Jinja templates."""
        jinja_file = tmp_path / "templates/resume_template.jinja"
        assert naming_agent._get_file_type(jinja_file) == "jinja_template"
        
        jinja2_file = tmp_path / "templates/email_outreach.jinja2"
        assert naming_agent._get_file_type(jinja2_file) == "jinja_template"
    
    def test_detect_json_config(self, naming_agent, tmp_path):
        """Test detection of JSON config files."""
        json_file = tmp_path / "config/agent_config.json"
        assert naming_agent._get_file_type(json_file) == "json_config"
    
    def test_detect_yaml_config(self, naming_agent, tmp_path):
        """Test detection of YAML config files."""
        yaml_file = tmp_path / "config/config.yaml"
        assert naming_agent._get_file_type(yaml_file) == "yaml_config"
        
        yml_file = tmp_path / "config/settings.yml"
        assert naming_agent._get_file_type(yml_file) == "yaml_config"
    
    def test_detect_markdown_doc(self, naming_agent, tmp_path):
        """Test detection of Markdown files."""
        md_file = tmp_path / "docs/api_reference.md"
        assert naming_agent._get_file_type(md_file) == "markdown_doc"
    
    def test_detect_text_file(self, naming_agent, tmp_path):
        """Test detection of text files."""
        txt_file = tmp_path / "requirements.txt"
        assert naming_agent._get_file_type(txt_file) == "text_file"


class TestAgentFileValidation:
    """Test validation of Agent files."""
    
    def test_valid_agent_file(self, naming_agent, tmp_path):
        """Test validation of correctly named Agent file."""
        agent_file = tmp_path / "HealerAgent.py"
        agent_file.write_text("class HealerAgent:\n    pass")
        
        valid, reason = naming_agent.validate_file_naming(agent_file)
        assert valid is True
        assert "Valid PascalCase agent file" in reason
    
    def test_agent_file_wrong_case(self, naming_agent, tmp_path):
        """Test Agent file with wrong casing."""
        agent_file = tmp_path / "healerAgent.py"
        agent_file.write_text("class HealerAgent:\n    pass")
        
        valid, reason = naming_agent.validate_file_naming(agent_file)
        assert valid is False
        assert "AGENT NAMING VIOLATION" in reason
    
    def test_agent_file_class_mismatch(self, naming_agent, tmp_path):
        """Test Agent file where class name doesn't match filename."""
        agent_file = tmp_path / "HealerAgent.py"
        agent_file.write_text("class WrongAgent:\n    pass")
        
        valid, reason = naming_agent.validate_file_naming(agent_file)
        assert valid is False
        assert "AGENT NAMING MISMATCH" in reason
    
    def test_agent_file_no_agent_class(self, naming_agent, tmp_path):
        """Test Agent file without an Agent class."""
        agent_file = tmp_path / "HealerAgent.py"
        agent_file.write_text("class Healer:\n    pass")
        
        valid, reason = naming_agent.validate_file_naming(agent_file)
        assert valid is False
        assert "AGENT CLASS VIOLATION" in reason
    
    def test_agent_file_word_count_too_few(self, naming_agent, tmp_path):
        """Test Agent file with too few words (1 word)."""
        agent_file = tmp_path / "Agent.py"
        agent_file.write_text("class Agent:\n    pass")
        
        valid, reason = naming_agent.validate_file_naming(agent_file)
        assert valid is False
        assert "has 1 word(s), minimum is 2" in reason
    
    def test_agent_file_word_count_too_many(self, naming_agent, tmp_path):
        """Test Agent file with too many words (5 words)."""
        agent_file = tmp_path / "VeryLongComplexAgentNameAgent.py"
        agent_file.write_text("class VeryLongComplexAgentNameAgent:\n    pass")
        
        valid, reason = naming_agent.validate_file_naming(agent_file)
        assert valid is False
        assert "has 5 word(s), maximum is 4" in reason


class TestScriptFileValidation:
    """Test validation of script files."""
    
    def test_valid_script_file(self, naming_agent, tmp_path):
        """Test validation of correctly named script file."""
        script_dir = tmp_path / "agentic_core/L0_maintenance/scripts"
        script_dir.mkdir(parents=True)
        script_file = script_dir / "sovereign_ingestion.py"
        script_file.write_text("# Script with high-signal keywords\ndef main():\n    pass")
        
        valid, reason = naming_agent.validate_file_naming(script_file)
        # May fail on signal check, but pattern should pass
        assert "NAMING VIOLATION" not in reason or "weak canon signal" in reason
    
    def test_script_file_wrong_case(self, naming_agent, tmp_path):
        """Test script file with uppercase letters."""
        script_dir = tmp_path / "agentic_core/L0_maintenance/scripts"
        script_dir.mkdir(parents=True)
        script_file = script_dir / "SovereignIngestion.py"
        script_file.write_text("def main():\n    pass")
        
        valid, reason = naming_agent.validate_file_naming(script_file)
        assert valid is False
        assert "uppercase letters" in reason
    
    def test_script_file_too_few_words(self, naming_agent, tmp_path):
        """Test script file with only 1 word."""
        script_dir = tmp_path / "agentic_core/L0_maintenance/scripts"
        script_dir.mkdir(parents=True)
        script_file = script_dir / "ingestion.py"
        script_file.write_text("def main():\n    pass")
        
        valid, reason = naming_agent.validate_file_naming(script_file)
        assert valid is False
        assert "has 1 word(s), minimum is 2" in reason
    
    def test_script_file_too_many_words(self, naming_agent, tmp_path):
        """Test script file with 4 words (max is 3)."""
        script_dir = tmp_path / "agentic_core/L0_maintenance/scripts"
        script_dir.mkdir(parents=True)
        script_file = script_dir / "sovereign_ingestion_mission_runner.py"
        script_file.write_text("def main():\n    pass")
        
        valid, reason = naming_agent.validate_file_naming(script_file)
        assert valid is False
        assert "has 4 word(s), maximum is 3" in reason


class TestNonPythonFileValidation:
    """Test validation of non-Python files."""
    
    def test_valid_jinja_template(self, naming_agent, tmp_path):
        """Test validation of Jinja template."""
        jinja_file = tmp_path / "resume_template.jinja"
        jinja_file.write_text("{{ content }}")
        
        valid, reason = naming_agent.validate_file_naming(jinja_file)
        assert valid is True
        assert "Valid jinja_template naming" in reason
    
    def test_jinja_template_too_few_words(self, naming_agent, tmp_path):
        """Test Jinja template with only 1 word."""
        jinja_file = tmp_path / "template.jinja"
        jinja_file.write_text("{{ content }}")
        
        valid, reason = naming_agent.validate_file_naming(jinja_file)
        assert valid is False
        assert "has 1 word(s), minimum is 2" in reason
    
    def test_valid_json_config(self, naming_agent, tmp_path):
        """Test validation of JSON config file."""
        json_file = tmp_path / "agent_config.json"
        json_file.write_text('{"key": "value"}')
        
        valid, reason = naming_agent.validate_file_naming(json_file)
        assert valid is True
        assert "Valid json_config naming" in reason
    
    def test_valid_yaml_config(self, naming_agent, tmp_path):
        """Test validation of YAML config file."""
        yaml_file = tmp_path / "config.yaml"
        yaml_file.write_text("key: value")
        
        valid, reason = naming_agent.validate_file_naming(yaml_file)
        assert valid is True
        assert "Valid yaml_config naming" in reason
    
    def test_valid_markdown_doc(self, naming_agent, tmp_path):
        """Test validation of Markdown file."""
        md_file = tmp_path / "api_reference.md"
        md_file.write_text("# API Reference")
        
        valid, reason = naming_agent.validate_file_naming(md_file)
        assert valid is True
        assert "Valid markdown_doc naming" in reason


class TestExemptions:
    """Test file and directory exemptions."""
    
    def test_exempt_file(self, naming_agent, tmp_path):
        """Test that exempt files are skipped."""
        init_file = tmp_path / "__init__.py"
        init_file.write_text("")
        
        valid, reason = naming_agent.validate_file_naming(init_file)
        assert valid is True
        assert "Exempt infrastructure file" in reason
    
    def test_exempt_directory(self, naming_agent, tmp_path):
        """Test that files in exempt directories are skipped."""
        archives_dir = tmp_path / "archives"
        archives_dir.mkdir()
        old_file = archives_dir / "old_code.py"
        old_file.write_text("# old code")
        
        valid, reason = naming_agent.validate_file_naming(old_file)
        assert valid is True
        assert "exempt directory" in reason


class TestRunMethod:
    """Test the run() method for scanning multiple files."""
    
    def test_run_scans_all_extensions(self, naming_agent, tmp_path):
        """Test that run() scans all validated extensions."""
        # Create test files
        (tmp_path / "test.py").write_text("pass")
        (tmp_path / "test.json").write_text("{}")
        (tmp_path / "test.yaml").write_text("key: value")
        
        violations = naming_agent.run()
        
        # Should find violations for all these files (they don't meet naming requirements)
        assert len(violations) > 0
    
    def test_run_with_specific_extensions(self, naming_agent, tmp_path):
        """Test that run() can scan specific extensions only."""
        # Create test files
        (tmp_path / "test.py").write_text("pass")
        (tmp_path / "test.json").write_text("{}")
        
        violations = naming_agent.run(extensions={'.json'})
        
        # Should only scan .json files
        assert all(str(path).endswith('.json') for path, _ in violations)
    
    def test_run_skips_exempt_dirs(self, naming_agent, tmp_path):
        """Test that run() skips exempt directories."""
        # Create file in exempt directory
        archives_dir = tmp_path / "archives"
        archives_dir.mkdir()
        (archives_dir / "old.py").write_text("pass")
        
        violations = naming_agent.run()
        
        # Should not include files from archives
        assert not any("archives" in str(path) for path, _ in violations)


class TestBasicNamingValidation:
    """Test basic naming validation for unknown file types."""
    
    def test_basic_naming_no_hyphens(self, naming_agent, tmp_path):
        """Test that hyphens are rejected."""
        file_with_hyphen = tmp_path / "my-file.xyz"
        file_with_hyphen.write_text("content")
        
        valid, reason = naming_agent._validate_basic_naming(file_with_hyphen)
        assert valid is False
        assert "hyphens" in reason
    
    def test_basic_naming_no_spaces(self, naming_agent, tmp_path):
        """Test that spaces are rejected."""
        file_with_space = tmp_path / "my file.xyz"
        file_with_space.write_text("content")
        
        valid, reason = naming_agent._validate_basic_naming(file_with_space)
        assert valid is False
        assert "spaces" in reason


def heal_repository(dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path = None):
    """Test file - operational stub only."""
    if _call_path is None:
        _call_path = set()
    agent_name = "TestNamingAgent"
    if agent_name in _call_path:
        return {"errors": 1, "cycle_detected": True}
    if depth > max_depth:
        return {"errors": 1, "depth_limited": True}
    _call_path.add(agent_name)
    try:
        print(f"[{agent_name}] Test file - operational stub only")
        return {"skipped": 1}
    finally:
        _call_path.discard(agent_name)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
