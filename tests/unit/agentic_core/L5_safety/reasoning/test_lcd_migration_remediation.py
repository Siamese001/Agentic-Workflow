"""
Tests for LCD+ Migration Remediation (docs/reports/audit/RCA_LCD_MIGRATION_FAILURES_2026-02-07.md).

Covers:
- Phase 1: Compound suffix pre-validation
- Phase 2: Content-weighted classification scoring
- Phase 3: Recursive territory enforcement
- Phase 4: Global mixin routing
- Phase 5: Folder-suffix consistency
- Phase 6: Pre-commit hook (check_compound_suffix.py)
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def agent():
    """Create a FileClassificationAgent instance for testing."""
    from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
        FileClassificationAgent,
    )

    a = FileClassificationAgent(
        project_root=Path.cwd(),
        dry_run=True,
        validate_only=True,
    )
    return a


# ===========================================================================
# Phase 1: Compound Suffix Pre-Validation
# ===========================================================================


class TestCompoundSuffixValidation:
    """Tests for validate_single_suffix() — Phase 1 (P0)."""

    def test_single_suffix_passes(self, agent):
        """Files with one architectural suffix should pass validation."""
        assert agent.validate_single_suffix("model_provider_config.py") is None
        assert agent.validate_single_suffix("user_profile_types.py") is None
        assert agent.validate_single_suffix("cache_invalidation_util.py") is None
        assert agent.validate_single_suffix("audit_trail_mixin.py") is None

    def test_no_suffix_passes(self, agent):
        """Files without any architectural suffix should pass."""
        assert agent.validate_single_suffix("SovereignBaseAgent.py") is None
        assert agent.validate_single_suffix("decorators.py") is None

    def test_compound_types_config_detected(self, agent):
        """Files with _types_config should be flagged as compound violation."""
        result = agent.validate_single_suffix("model_provider_types_config.py")
        assert result is not None
        assert "_types" in result["found_suffixes"]
        assert "_config" in result["found_suffixes"]
        assert result["suggested_name"].endswith(".py")

    def test_compound_validator_util_detected(self, agent):
        """Files with _validator_util should be flagged."""
        result = agent.validate_single_suffix("cache_invalidation_validator_util.py")
        assert result is not None
        assert "_validator" in result["found_suffixes"]
        assert "_util" in result["found_suffixes"]

    def test_compound_types_validator_detected(self, agent):
        """Files with _types_validator should be flagged."""
        result = agent.validate_single_suffix("healing_orchestration_types_validator.py")
        assert result is not None
        assert len(result["found_suffixes"]) >= 2

    def test_compound_config_util_detected(self, agent):
        """Files with _config_util should be flagged."""
        result = agent.validate_single_suffix("dashboard_ssot_definitions_config_util.py")
        assert result is not None
        assert "_config" in result["found_suffixes"]
        assert "_util" in result["found_suffixes"]

    def test_exempt_files_pass(self, agent):
        """Critical files (__init__.py, __main__.py, conftest.py) should always pass."""
        assert agent.validate_single_suffix("__init__.py") is None
        assert agent.validate_single_suffix("__main__.py") is None
        assert agent.validate_single_suffix("conftest.py") is None

    def test_non_python_files_pass(self, agent):
        """Non-.py files should always pass."""
        assert agent.validate_single_suffix("config.yaml") is None
        assert agent.validate_single_suffix("README.md") is None

    def test_suggested_name_has_single_suffix(self, agent):
        """The suggested name should have exactly one architectural suffix."""
        from agentic_core.L5_safety.config.structure_blueprint_config import (
            KNOWN_ARCHITECTURAL_SUFFIXES,
        )

        result = agent.validate_single_suffix("code_detection_types_config.py")
        assert result is not None
        suggested_stem = result["suggested_name"][:-3]  # Remove .py
        found_in_suggested = [s for s in KNOWN_ARCHITECTURAL_SUFFIXES if s in suggested_stem]
        assert len(found_in_suggested) == 1, (
            f"Suggested name '{result['suggested_name']}' still has compound suffixes: {found_in_suggested}"
        )


# ===========================================================================
# Phase 2: Content-Weighted Classification Scoring
# ===========================================================================


class TestContentScoring:
    """Tests for _compute_content_scores() and classify_file_with_confidence()."""

    def test_dataclass_file_scores_types(self, agent, tmp_path):
        """A file with multiple @dataclass definitions should score TYPES highest."""
        test_file = tmp_path / "user_profile_config.py"
        test_file.write_text(
            textwrap.dedent("""\
            from dataclasses import dataclass

            @dataclass
            class UserProfile:
                name: str
                email: str

            @dataclass
            class UserSettings:
                theme: str
                language: str

            @dataclass
            class UserPreferences:
                notifications: bool
        """),
        )

        scores = agent._compute_content_scores(test_file)
        assert scores["TYPES"] > scores["CONFIG"]
        assert scores["TYPES"] >= 30  # 3 dataclasses * 10

    def test_constants_file_scores_config(self, agent, tmp_path):
        """A file with UPPER_CASE constants should score CONFIG highest."""
        test_file = tmp_path / "app_settings_config.py"
        test_file.write_text(
            textwrap.dedent("""\
            MAX_RETRIES = 3
            TIMEOUT_SECONDS = 30
            DEFAULT_PORT = 8080
            API_VERSION = "v2"
            DEBUG_MODE = False
            LOG_LEVEL = "INFO"
            CACHE_TTL = 3600
        """),
        )

        scores = agent._compute_content_scores(test_file)
        assert scores["CONFIG"] > scores["TYPES"]
        assert scores["CONFIG"] >= 35  # 7 constants * 5

    def test_agent_file_scores_agent(self, agent, tmp_path):
        """A file with an Agent class should score AGENT highest."""
        test_file = tmp_path / "HealerAgent.py"
        test_file.write_text(
            textwrap.dedent("""\
            class HealerAgent:
                def heal(self):
                    pass
        """),
        )

        scores = agent._compute_content_scores(test_file)
        assert scores["AGENT"] > scores["UTILITY"]
        assert scores["AGENT"] >= 20

    def test_utility_file_scores_utility(self, agent, tmp_path):
        """A file with standalone functions should score UTILITY highest."""
        test_file = tmp_path / "string_formatter_util.py"
        test_file.write_text(
            textwrap.dedent("""\
            def format_name(name: str) -> str:
                return name.title()

            def truncate(text: str, length: int) -> str:
                return text[:length]

            def slugify(text: str) -> str:
                return text.lower().replace(" ", "-")
        """),
        )

        scores = agent._compute_content_scores(test_file)
        assert scores["UTILITY"] > scores["CONFIG"]
        assert scores["UTILITY"] >= 9  # 3 functions * 3

    def test_validator_file_scores_validator(self, agent, tmp_path):
        """A file with validate_ functions should score VALIDATOR highest."""
        test_file = tmp_path / "input_validator.py"
        test_file.write_text(
            textwrap.dedent("""\
            def validate_email(email: str) -> bool:
                return "@" in email

            def check_password_strength(password: str) -> bool:
                return len(password) >= 8

            def verify_token(token: str) -> bool:
                return len(token) == 32
        """),
        )

        scores = agent._compute_content_scores(test_file)
        assert scores["VALIDATOR"] > scores["UTILITY"]
        assert scores["VALIDATOR"] >= 15  # 3 validate/check functions * 5

    def test_confidence_high_for_pure_types(self, agent, tmp_path):
        """A pure types file should have high confidence."""
        test_file = tmp_path / "model_types.py"
        test_file.write_text(
            textwrap.dedent("""\
            from dataclasses import dataclass
            from enum import Enum

            class Color(Enum):
                RED = "red"
                BLUE = "blue"

            @dataclass
            class Point:
                x: float
                y: float
        """),
        )

        result = agent.classify_file_with_confidence(test_file)
        assert result.file_type == "TYPES"
        assert result.confidence >= 0.6

    def test_confidence_low_for_mixed_file(self, agent, tmp_path):
        """A file with mixed signals should have lower confidence."""
        test_file = tmp_path / "hybrid.py"
        test_file.write_text(
            textwrap.dedent("""\
            from dataclasses import dataclass

            MAX_RETRIES = 3
            TIMEOUT = 30
            DEFAULT = True

            @dataclass
            class Config:
                name: str

            @dataclass
            class Settings:
                value: int

            def validate_input(x):
                return x > 0
        """),
        )

        result = agent.classify_file_with_confidence(test_file)
        # Mixed signals — confidence should be moderate
        assert result.confidence < 0.9

    def test_empty_file_returns_utility(self, agent, tmp_path):
        """An empty/unparseable file should return UTILITY with low confidence."""
        test_file = tmp_path / "empty.py"
        test_file.write_text("")

        result = agent.classify_file_with_confidence(test_file)
        assert result.file_type == "UTILITY"
        assert result.confidence == 0.5


# ===========================================================================
# Phase 2.4: Content-Score Tiebreaker in classify_file()
# ===========================================================================


class TestContentScoreTiebreaker:
    """Tests for CONFIG->TYPES override when content is overwhelmingly types."""

    def test_config_named_file_with_dataclasses_becomes_types(self, agent, tmp_path):
        """A file named *_config.py but containing only @dataclass should be classified as TYPES."""
        test_file = tmp_path / "code_detection_types_config.py"
        test_file.write_text(
            textwrap.dedent("""\
            from dataclasses import dataclass

            @dataclass
            class DetectorConfig:
                threshold: float
                max_depth: int

            @dataclass
            class DetectorResult:
                score: float
                findings: list

            @dataclass
            class DetectorOptions:
                verbose: bool
                strict: bool
        """),
        )

        ftype = agent.classify_file(test_file)
        assert ftype == "TYPES", f"Expected TYPES but got {ftype} for dataclass-only _config file"


# ===========================================================================
# Phase 3: Recursive Territory Enforcement
# ===========================================================================


class TestRecursiveTerritoryEnforcement:
    """Tests for enforce_kernel_structure() recursive validation."""

    def test_agent_in_enforcement_gets_moved_to_reasoning(self, agent, tmp_path):
        """An Agent file in enforcement/ should be routed to reasoning/."""
        layer = tmp_path / "agentic_core" / "L5_safety"
        enforcement = layer / "enforcement"
        enforcement.mkdir(parents=True)
        f = enforcement / "AdversarialRedTeamerAgent.py"
        f.write_text(
            "class SovereignBaseAgent: pass\nclass AdversarialRedTeamerAgent(SovereignBaseAgent):\n    def run(self): pass\n",
        )

        result = agent.enforce_kernel_structure(f, layer)
        assert result is not None
        assert result.parent.name == "reasoning"
        assert result.name == "AdversarialRedTeamerAgent.py"

    def test_types_in_config_gets_moved_to_types(self, agent, tmp_path):
        """A types file in config/ should be routed to types/."""
        layer = tmp_path / "agentic_core" / "L5_safety"
        cfg = layer / "config"
        cfg.mkdir(parents=True)
        f = cfg / "safety_detection_types.py"
        f.write_text(
            "from typing import TypedDict\nclass SafetyDetectorTypes(TypedDict):\n    name: str\n    severity: int\n",
        )

        result = agent.enforce_kernel_structure(f, layer)
        assert result is not None
        assert result.parent.name == "types"
        assert result.name == "safety_detection_types.py"

    def test_util_in_enforcement_gets_moved_to_utils(self, agent, tmp_path):
        """A utility file in enforcement/ should be routed to utils/."""
        layer = tmp_path / "agentic_core" / "L5_safety"
        enforcement = layer / "enforcement"
        enforcement.mkdir(parents=True)
        f = enforcement / "gravity_visitor_util.py"
        f.write_text(
            "def compute_gravity(path):\n    return len(path.parts)\ndef visit_tree(root):\n    pass\n",
        )

        result = agent.enforce_kernel_structure(f, layer)
        assert result is not None
        assert result.parent.name == "utils"

    def test_correctly_placed_config_stays(self, agent, tmp_path):
        """A config file already in config/ should return None."""
        layer = tmp_path / "agentic_core" / "L5_safety"
        cfg = layer / "config"
        cfg.mkdir(parents=True)
        f = cfg / "safety_config.py"
        f.write_text(
            "MAX_RETRIES = 3\nTIMEOUT = 30\nLOG_LEVEL = 'INFO'\nENABLE = True\nclass SafetyConfig:\n    def load(self): pass\n",
        )

        result = agent.enforce_kernel_structure(f, layer)
        assert result is None

    def test_agent_in_validators_gets_moved_to_reasoning(self, agent, tmp_path):
        """An Agent in validators/ should be moved to reasoning/."""
        layer = tmp_path / "agentic_core" / "L5_safety"
        validators = layer / "validators"
        validators.mkdir(parents=True)
        f = validators / "LocationAgent.py"
        f.write_text(
            "class SovereignBaseAgent: pass\nclass LocationAgent(SovereignBaseAgent):\n    def validate_location(self): pass\n",
        )

        result = agent.enforce_kernel_structure(f, layer)
        assert result is not None
        assert result.parent.name == "reasoning"

    def test_agent_in_memory_gets_moved_to_reasoning(self, agent, tmp_path):
        """An Agent in memory/ should be moved to reasoning/."""
        layer = tmp_path / "agentic_core" / "L4_state"
        memory = layer / "memory"
        memory.mkdir(parents=True)
        f = memory / "ExampleStateAgent.py"
        f.write_text(
            "class SovereignBaseAgent: pass\nclass ExampleStateAgent(SovereignBaseAgent):\n    def map_territory(self): pass\n",
        )

        result = agent.enforce_kernel_structure(f, layer)
        assert result is not None
        assert result.parent.name == "reasoning"

    def test_script_in_l0_goes_to_scripts(self, agent, tmp_path):
        """A script file in L0 enforcement/ should go to scripts/."""
        layer = tmp_path / "agentic_core" / "L0_routing"
        scripts = layer / "scripts"
        scripts.mkdir(parents=True)
        enforcement = layer / "enforcement"
        enforcement.mkdir(parents=True)
        f = enforcement / "heal_script.py"
        f.write_text(
            "import sys\ndef main():\n    print('healing')\nif __name__ == '__main__':\n    main()\n",
        )

        result = agent.enforce_kernel_structure(f, layer)
        assert result is not None
        assert result.parent.name == "scripts"

    def test_critical_files_exempt(self, agent, tmp_path):
        """__init__.py and conftest.py should never be moved."""
        layer = tmp_path / "agentic_core" / "L5_safety"
        enforcement = layer / "enforcement"
        enforcement.mkdir(parents=True)

        init_path = enforcement / "__init__.py"
        init_path.write_text("")
        assert agent.enforce_kernel_structure(init_path, layer) is None

        conftest_path = enforcement / "conftest.py"
        conftest_path.write_text("")
        assert agent.enforce_kernel_structure(conftest_path, layer) is None


# ===========================================================================
# Phase 4: Global Mixin Routing
# ===========================================================================


class TestGlobalMixinRouting:
    """Tests for mixin routing to agentic_core/mixins/."""

    def test_mixin_in_layer_utils_moves_to_global(self, agent):
        """A mixin in L5/utils/ should be routed to agentic_core/mixins/."""
        file_path = Path("C:/repo/agentic_core/L5_safety/utils/ast_enforcement_mixin.py")
        layer_root = Path("C:/repo/agentic_core/L5_safety")

        result = agent.enforce_kernel_structure(file_path, layer_root)
        assert result is not None
        assert "mixins" in result.parts
        assert "L5_safety" not in result.parts

    def test_mixin_in_validators_moves_to_global(self, agent):
        """A mixin in L5/validators/core/ should be routed to agentic_core/mixins/."""
        file_path = Path("C:/repo/agentic_core/L5_safety/validators/core/validator_mixin.py")
        layer_root = Path("C:/repo/agentic_core/L5_safety")

        result = agent.enforce_kernel_structure(file_path, layer_root)
        assert result is not None
        assert result.parent.name == "mixins"

    def test_mixin_already_in_global_stays(self, agent):
        """A mixin already in agentic_core/mixins/ should not be moved."""
        file_path = Path("C:/repo/agentic_core/mixins/caching_mixin.py")
        layer_root = Path("C:/repo/agentic_core/L5_safety")  # Doesn't matter, global override

        result = agent.enforce_kernel_structure(file_path, layer_root)
        assert result is None


# ===========================================================================
# Phase 5: Folder-Suffix Consistency
# ===========================================================================


class TestFolderSuffixConsistency:
    """Tests for validate_folder_suffix_consistency()."""

    def test_types_folder_file_without_types_suffix(self, agent):
        """A file in types/ without _types.py or _protocol.py suffix should be flagged."""
        path = Path("C:/repo/agentic_core/L1_cognition/types/memory_item_schema.py")
        result = agent.validate_folder_suffix_consistency(path)
        assert result is not None
        assert result["folder"] == "types"
        assert result["suggested_name"] == "memory_item_schema_types.py"

    def test_types_folder_with_correct_suffix_passes(self, agent):
        """A file in types/ with _types.py suffix should pass."""
        path = Path("C:/repo/agentic_core/L1_cognition/types/validation_types.py")
        result = agent.validate_folder_suffix_consistency(path)
        assert result is None

    def test_types_folder_protocol_suffix_passes(self, agent):
        """A file in types/ with _protocol.py suffix should pass."""
        path = Path("C:/repo/agentic_core/L1_cognition/types/mcp_client_protocol.py")
        result = agent.validate_folder_suffix_consistency(path)
        assert result is None

    def test_types_folder_interface_protocol_exempt(self, agent):
        """I*Protocol.py files in types/ are exempt (interface convention)."""
        path = Path("C:/repo/agentic_core/L1_cognition/types/IOrchestratorProtocol.py")
        result = agent.validate_folder_suffix_consistency(path)
        assert result is None

    def test_utils_folder_file_without_util_suffix(self, agent):
        """A file in utils/ without _util.py suffix should be flagged."""
        path = Path("C:/repo/agentic_core/L4_state/utils/circuit_breaker.py")
        result = agent.validate_folder_suffix_consistency(path)
        assert result is not None
        assert result["folder"] == "utils"
        assert result["suggested_name"] == "circuit_breaker_util.py"

    def test_utils_folder_with_correct_suffix_passes(self, agent):
        """A file in utils/ with _util.py suffix should pass."""
        path = Path("C:/repo/agentic_core/L5_safety/utils/security_controls_util.py")
        result = agent.validate_folder_suffix_consistency(path)
        assert result is None

    def test_utils_folder_mixin_suffix_passes(self, agent):
        """A file in utils/ with _mixin.py suffix should pass."""
        path = Path("C:/repo/agentic_core/L5_safety/utils/healing_mixin.py")
        result = agent.validate_folder_suffix_consistency(path)
        assert result is None

    def test_config_folder_file_without_config_suffix(self, agent):
        """A file in config/ without _config.py suffix should be flagged."""
        path = Path("C:/repo/agentic_core/L5_safety/config/safety_constants.py")
        result = agent.validate_folder_suffix_consistency(path)
        assert result is not None
        assert result["folder"] == "config"
        assert result["suggested_name"] == "safety_constants_config.py"

    def test_config_folder_with_correct_suffix_passes(self, agent):
        """A file in config/ with _config.py suffix should pass."""
        path = Path("C:/repo/agentic_core/L5_safety/config/structure_blueprint_config.py")
        result = agent.validate_folder_suffix_consistency(path)
        assert result is None

    def test_reasoning_folder_not_enforced(self, agent):
        """reasoning/ folder is not in the folder_suffix_rules and should pass."""
        path = Path("C:/repo/agentic_core/L5_safety/reasoning/HealerAgent.py")
        result = agent.validate_folder_suffix_consistency(path)
        assert result is None

    def test_init_file_exempt(self, agent):
        """__init__.py should always be exempt."""
        path = Path("C:/repo/agentic_core/L5_safety/types/__init__.py")
        result = agent.validate_folder_suffix_consistency(path)
        assert result is None


# ===========================================================================
# Phase 6: Pre-commit Hook
# ===========================================================================


class TestPreCommitHook:
    """Tests for the check_compound_suffix.py hook logic."""

    def test_hook_detects_compound(self):
        """Hook function should detect compound suffixes."""
        from ops_scripts.hooks.check_compound_suffix import check_compound_suffix

        result = check_compound_suffix("model_types_config.py")
        assert result is not None
        assert "_types" in result
        assert "_config" in result

    def test_hook_passes_single_suffix(self):
        """Hook function should pass single-suffix files."""
        from ops_scripts.hooks.check_compound_suffix import check_compound_suffix

        assert check_compound_suffix("model_config.py") is None
        assert check_compound_suffix("user_types.py") is None
        assert check_compound_suffix("HealerAgent.py") is None

    def test_hook_passes_exempt_files(self):
        """Hook function should pass exempt files."""
        from ops_scripts.hooks.check_compound_suffix import check_compound_suffix

        assert check_compound_suffix("__init__.py") is None
        assert check_compound_suffix("conftest.py") is None

    def test_hook_passes_non_python(self):
        """Hook function should pass non-Python files."""
        from ops_scripts.hooks.check_compound_suffix import check_compound_suffix

        assert check_compound_suffix("config.yaml") is None
        assert check_compound_suffix("README.md") is None


# ===========================================================================
# Blueprint Config Constants
# ===========================================================================


class TestBlueprintConfigConstants:
    """Tests that new constants in structure_blueprint_config.py are well-formed."""

    def test_known_suffixes_all_start_with_underscore(self):
        """All KNOWN_ARCHITECTURAL_SUFFIXES should start with underscore."""
        from agentic_core.L5_safety.config.structure_blueprint_config import (
            KNOWN_ARCHITECTURAL_SUFFIXES,
        )

        for suffix in KNOWN_ARCHITECTURAL_SUFFIXES:
            assert suffix.startswith("_"), f"Suffix '{suffix}' should start with underscore"

    def test_suffix_to_folder_has_valid_folders(self):
        """All SUFFIX_TO_FOLDER values should be valid LCD folders or global sentinels."""
        from agentic_core.L5_safety.config.structure_blueprint_config import (
            STANDARD_LAYER_STRUCTURE,
            SUFFIX_TO_FOLDER,
        )

        valid_folders = set(STANDARD_LAYER_STRUCTURE) | {"GLOBAL_MIXINS", "GLOBAL_INTERFACES", "scripts"}
        for suffix, folder in SUFFIX_TO_FOLDER.items():
            assert folder in valid_folders, (
                f"SUFFIX_TO_FOLDER['{suffix}'] = '{folder}' is not a valid LCD folder. Valid: {valid_folders}"
            )

    def test_forbidden_compound_patterns_are_valid_regex(self):
        """All FORBIDDEN_COMPOUND_PATTERNS should be valid regex."""
        import re

        from agentic_core.L5_safety.config.structure_blueprint_config import (
            FORBIDDEN_COMPOUND_PATTERNS,
        )

        for pattern in FORBIDDEN_COMPOUND_PATTERNS:
            try:
                re.compile(pattern)
            except re.error as e:
                pytest.fail(f"Invalid regex in FORBIDDEN_COMPOUND_PATTERNS: '{pattern}' — {e}")

    def test_l5_enforcement_suffixes_not_empty(self):
        """L5_ENFORCEMENT_ALLOWED_SUFFIXES should be a non-empty list."""
        from agentic_core.L5_safety.config.structure_blueprint_config import (
            L5_ENFORCEMENT_ALLOWED_SUFFIXES,
        )

        assert len(L5_ENFORCEMENT_ALLOWED_SUFFIXES) > 0
        assert "_guardrail.py" in L5_ENFORCEMENT_ALLOWED_SUFFIXES
        assert "_gate.py" in L5_ENFORCEMENT_ALLOWED_SUFFIXES


# ===========================================================================
# _get_correct_folder_for_type (AST-based routing)
# ===========================================================================


def _make_file(tmp_path, name, content):
    """Helper: create a temp Python file with given content."""
    f = tmp_path / name
    f.write_text(content, encoding="utf-8")
    return f


class TestGetCorrectFolderForTypeAST:
    """Tests for _get_correct_folder_for_type() — AST-based routing via classify_file()."""

    def test_config_class_routes_to_config(self, agent, tmp_path):
        """A file with config class and load/save methods routes to config/."""
        f = _make_file(
            tmp_path,
            "safety_config.py",
            textwrap.dedent("""\
            import os
            DEFAULT_TIMEOUT = 30
            MAX_RETRIES = 3
            LOG_LEVEL = "INFO"
            ENABLE_CACHE = True
            class SafetyConfig:
                def __init__(self):
                    self.timeout = DEFAULT_TIMEOUT
                    self.retries = MAX_RETRIES
                def load(self):
                    pass
                def save(self):
                    pass
        """),
        )
        assert agent._get_correct_folder_for_type(f, tmp_path) == "config"

    def test_types_file_routes_to_types(self, agent, tmp_path):
        """A file with TypedDict/dataclass models routes to types/."""
        f = _make_file(
            tmp_path,
            "model_types.py",
            textwrap.dedent("""\
            from typing import TypedDict
            class ModelTypes(TypedDict):
                name: str
                value: int
        """),
        )
        assert agent._get_correct_folder_for_type(f, tmp_path) == "types"

    def test_protocol_class_routes_to_types(self, agent, tmp_path):
        """A file with Protocol class routes to types/."""
        f = _make_file(
            tmp_path,
            "validator_protocol.py",
            textwrap.dedent("""\
            from typing import Protocol
            class ValidatorProtocol(Protocol):
                def validate(self) -> bool: ...
        """),
        )
        assert agent._get_correct_folder_for_type(f, tmp_path) == "types"

    def test_utility_function_routes_to_utils(self, agent, tmp_path):
        """A file with only functions (no classes) routes to utils/."""
        f = _make_file(
            tmp_path,
            "string_util.py",
            textwrap.dedent("""\
            def strip_prefix(s: str, prefix: str) -> str:
                return s[len(prefix):] if s.startswith(prefix) else s
            def clean_whitespace(s: str) -> str:
                return ' '.join(s.split())
        """),
        )
        assert agent._get_correct_folder_for_type(f, tmp_path) == "utils"

    def test_agent_class_routes_to_reasoning(self, agent, tmp_path):
        """A file with Agent class (inheriting SovereignBaseAgent) routes to reasoning/."""
        f = _make_file(
            tmp_path,
            "HealerAgent.py",
            textwrap.dedent("""\
            class SovereignBaseAgent: pass
            class HealerAgent(SovereignBaseAgent):
                def heal_repository(self): pass
        """),
        )
        assert agent._get_correct_folder_for_type(f, tmp_path) == "reasoning"

    def test_mixin_returns_none_handled_by_global_override(self, agent, tmp_path):
        """Mixin routing returns None (handled by global override in enforce_kernel_structure)."""
        f = _make_file(
            tmp_path,
            "caching_mixin.py",
            textwrap.dedent("""\
            class CachingMixin:
                def cache_get(self, key): pass
                def cache_set(self, key, value): pass
        """),
        )
        assert agent._get_correct_folder_for_type(f, tmp_path) is None

    def test_init_file_returns_none(self, agent, tmp_path):
        f = _make_file(tmp_path, "__init__.py", "")
        assert agent._get_correct_folder_for_type(f, tmp_path) is None

    def test_blueprint_config_stays_in_config(self, agent, tmp_path):
        f = _make_file(tmp_path, "structure_blueprint_config.py", "X = 1")
        assert agent._get_correct_folder_for_type(f, tmp_path) == "config"

    def test_class_fallback_returns_none(self, agent, tmp_path):
        """A plain class with no architectural signals stays where it is (CLASS -> None)."""
        f = _make_file(
            tmp_path,
            "random_file.py",
            textwrap.dedent("""\
            class SomeHelper:
                def do_thing(self): pass
        """),
        )
        assert agent._get_correct_folder_for_type(f, tmp_path) is None

    def test_agent_primary_wins_over_strategy_name(self, agent, tmp_path):
        """FooStrategyAgent: primary class is Agent -> reasoning (AST detects Agent inheritance)."""
        f = _make_file(
            tmp_path,
            "FooStrategyAgent.py",
            textwrap.dedent("""\
            class SovereignBaseAgent: pass
            class FooStrategyAgent(SovereignBaseAgent):
                def execute(self): pass
        """),
        )
        assert agent._get_correct_folder_for_type(f, tmp_path) == "reasoning"

    def test_strategy_class_routes_to_enforcement(self, agent, tmp_path):
        """A file with Strategy class routes to enforcement/."""
        f = _make_file(
            tmp_path,
            "HealingStrategy.py",
            textwrap.dedent("""\
            class HealingStrategy:
                def select_tier(self, violations): pass
                def execute_healing(self): pass
        """),
        )
        assert agent._get_correct_folder_for_type(f, tmp_path) == "enforcement"

    def test_adapter_class_routes_to_enforcement(self, agent, tmp_path):
        """A file with Adapter class routes to enforcement/."""
        f = _make_file(
            tmp_path,
            "SurgicalHealingAdapter.py",
            textwrap.dedent("""\
            class SurgicalHealingAdapter:
                def adapt(self, source, target): pass
        """),
        )
        assert agent._get_correct_folder_for_type(f, tmp_path) == "enforcement"

    def test_exception_class_routes_to_types(self, agent, tmp_path):
        """A file with Exception class routes to types/."""
        f = _make_file(
            tmp_path,
            "BudgetExceededError.py",
            textwrap.dedent("""\
            class BudgetExceededError(Exception):
                def __init__(self, message, spend=None):
                    super().__init__(message)
                    self.spend = spend
        """),
        )
        assert agent._get_correct_folder_for_type(f, tmp_path) == "types"

    def test_validator_class_routes_to_validators(self, agent, tmp_path):
        """A file with Validator class routes to validators/."""
        f = _make_file(
            tmp_path,
            "schema_validator.py",
            textwrap.dedent("""\
            class SchemaValidator:
                def validate(self, data): pass
                def check_schema(self, schema): pass
        """),
        )
        result = agent._get_correct_folder_for_type(f, tmp_path)
        assert result == "validators"


# ===========================================================================
# Folder Purity Enforcement (Bidirectional)
# ===========================================================================


class TestFolderPurityEnforcement:
    """Tests for _enforce_folder_purity() — evicting misplaced files."""

    def test_agent_in_reasoning_passes(self, agent):
        """An *Agent.py file in reasoning/ should pass purity check."""
        path = Path("C:/repo/agentic_core/L5_safety/reasoning/HealerAgent.py")
        assert agent._enforce_folder_purity(path) is None

    def test_guardrail_in_reasoning_fails(self, agent):
        """A *_guardrail.py file in reasoning/ should be evicted."""
        path = Path("C:/repo/agentic_core/L5_safety/reasoning/error_recovery_guardrail.py")
        result = agent._enforce_folder_purity(path)
        assert result is not None
        assert result["type"] == "FOLDER_PURITY_VIOLATION"
        assert result["current_folder"] == "reasoning"
        assert result["suggested_folder"] == "enforcement"

    def test_strategy_in_reasoning_fails(self, agent):
        """A *Strategy.py file in reasoning/ should be evicted."""
        path = Path("C:/repo/agentic_core/L5_safety/reasoning/HealingStrategy.py")
        result = agent._enforce_folder_purity(path)
        assert result is not None
        assert result["suggested_folder"] == "enforcement"

    def test_adapter_in_reasoning_fails(self, agent):
        """An *Adapter.py file in reasoning/ should be evicted."""
        path = Path("C:/repo/agentic_core/L5_safety/reasoning/SurgicalHealingAdapter.py")
        result = agent._enforce_folder_purity(path)
        assert result is not None
        assert result["suggested_folder"] == "enforcement"

    def test_utility_in_reasoning_fails(self, agent):
        """A snake_case utility in reasoning/ should be evicted."""
        path = Path("C:/repo/agentic_core/L5_safety/reasoning/agent_categorizer_util.py")
        result = agent._enforce_folder_purity(path)
        assert result is not None
        assert result["current_folder"] == "reasoning"

    def test_init_in_reasoning_passes(self, agent):
        """__init__.py should always pass purity checks."""
        path = Path("C:/repo/agentic_core/L5_safety/reasoning/__init__.py")
        assert agent._enforce_folder_purity(path) is None

    def test_config_in_config_passes(self, agent):
        """A *_config.py file in config/ should pass."""
        path = Path("C:/repo/agentic_core/L5_safety/config/structure_blueprint_config.py")
        assert agent._enforce_folder_purity(path) is None

    def test_agent_in_config_fails(self, agent):
        """An *Agent.py file in config/ should be evicted."""
        path = Path("C:/repo/agentic_core/L5_safety/config/MisplacedAgent.py")
        result = agent._enforce_folder_purity(path)
        assert result is not None
        assert result["suggested_folder"] == "reasoning"

    def test_validator_in_validators_passes(self, agent):
        """A *_validator.py in validators/ should pass."""
        path = Path("C:/repo/agentic_core/L5_safety/validators/structure_validator.py")
        assert agent._enforce_folder_purity(path) is None

    def test_non_purity_folder_skipped(self, agent):
        """Folders not in FOLDER_PURITY_RULES should be skipped (no violation)."""
        path = Path("C:/repo/agentic_core/L5_safety/guardrails/something.py")
        assert agent._enforce_folder_purity(path) is None


# ===========================================================================
# Cross-Domain Violation Detection
# ===========================================================================


class TestCrossDomainViolation:
    """Tests for _detect_cross_domain_violation()."""

    def test_lic_agent_in_core_detected(self, agent):
        """A Lic* agent in agentic_core should be flagged."""
        path = Path("C:/repo/agentic_core/L5_safety/reasoning/LicS2SupervisorAgent.py")
        result = agent._detect_cross_domain_violation(path)
        assert result is not None
        assert result["type"] == "CROSS_DOMAIN_VIOLATION"
        assert result["prefix"] == "Lic"
        assert "apps_lic" in result["suggested_domain"]

    def test_campaign_agent_in_core_detected(self, agent):
        """A Campaign* agent in agentic_core should be flagged."""
        path = Path("C:/repo/agentic_core/L2_execution/reasoning/CampaignOrchestratorAgent.py")
        result = agent._detect_cross_domain_violation(path)
        assert result is not None
        assert result["prefix"] == "Campaign"

    def test_normal_agent_in_core_passes(self, agent):
        """A regular agent in agentic_core should pass."""
        path = Path("C:/repo/agentic_core/L5_safety/reasoning/HealerAgent.py")
        assert agent._detect_cross_domain_violation(path) is None

    def test_lic_agent_in_apps_passes(self, agent):
        """A Lic* agent in apps_lic/ should pass (correct location)."""
        path = Path("C:/repo/apps_lic/engines/LicS2SupervisorAgent.py")
        assert agent._detect_cross_domain_violation(path) is None

    def test_non_python_in_core_passes(self, agent):
        """Non-agent files with prefixes should still be flagged if in core."""
        path = Path("C:/repo/agentic_core/L5_safety/config/LicConfig.py")
        result = agent._detect_cross_domain_violation(path)
        assert result is not None


# ===========================================================================
# Layer Affinity Scoring
# ===========================================================================


class TestLayerAffinity:
    """Tests for _compute_layer_affinity()."""

    def test_maintenance_agent_scores_l0(self, agent, tmp_path):
        """A file with cleanup/maintenance keywords should score highest for L0."""
        test_file = tmp_path / "SSOTFolderCleanupAgent.py"
        test_file.write_text(
            textwrap.dedent('''\
            """SSOT Folder Cleanup Agent - Automated SSOT Compliance Enforcement.
            Provides automated cleanup of non-SSOT-approved folders.
            Identifies files, reconciles locations, performs maintenance healing.
            """
            class SSOTFolderCleanupAgent:
                def cleanup_repository(self):
                    pass
                def heal_repository(self):
                    pass
                def reconcile_folders(self):
                    pass
        '''),
        )

        scores = agent._compute_layer_affinity(test_file)
        assert scores["L0_routing"] > scores["L5_safety"]
        assert scores["L0_routing"] > scores["L6_observability"]

    def test_safety_agent_scores_l5(self, agent, tmp_path):
        """A file with safety/guard/enforce keywords should score highest for L5."""
        test_file = tmp_path / "AdversarialRedTeamerAgent.py"
        test_file.write_text(
            textwrap.dedent('''\
            """Adversarial Red Team Agent for safety and threat analysis.
            Enforces guardrail compliance and adversarial protection.
            Validates sentinel behavior under threat conditions.
            """
            class AdversarialRedTeamerAgent:
                def enforce_safety(self):
                    pass
                def validate_compliance(self):
                    pass
                def detect_threat(self):
                    pass
        '''),
        )

        scores = agent._compute_layer_affinity(test_file)
        assert scores["L5_safety"] > scores["L0_routing"]

    def test_monitor_scores_l6(self, agent, tmp_path):
        """A file with monitor/telemetry/report keywords should score highest for L6."""
        test_file = tmp_path / "SovereignHealthMonitor.py"
        test_file.write_text(
            textwrap.dedent('''\
            """Sovereign Health Monitor - Historical Health Persistence.
            Persists health metrics for monitoring and telemetry.
            Generates reports and dashboard data.
            """
            class SovereignHealthMonitor:
                def report_health(self):
                    pass
                def log_metrics(self):
                    pass
        '''),
        )

        scores = agent._compute_layer_affinity(test_file)
        assert scores["L6_observability"] > scores["L5_safety"]

    def test_empty_file_returns_zero_scores(self, agent, tmp_path):
        """An empty file should return all zero scores."""
        test_file = tmp_path / "empty.py"
        test_file.write_text("")

        scores = agent._compute_layer_affinity(test_file)
        assert all(v == 0.0 for v in scores.values())

    def test_scores_are_normalized(self, agent, tmp_path):
        """All scores should sum to approximately 1.0 (when there are hits)."""
        test_file = tmp_path / "mixed.py"
        test_file.write_text(
            textwrap.dedent('''\
            """Safety monitor with validation and reporting."""
            class SafetyMonitor:
                def validate(self): pass
                def report(self): pass
        '''),
        )

        scores = agent._compute_layer_affinity(test_file)
        total = sum(scores.values())
        if total > 0:
            assert abs(total - 1.0) < 0.01


# ===========================================================================
# New Config Constants Validation
# ===========================================================================


class TestNewConfigConstants:
    """Tests for FOLDER_PURITY_RULES, APP_DOMAIN_PREFIXES, LAYER_KEYWORD_AFFINITY."""

    def test_folder_purity_rules_has_reasoning(self):
        from agentic_core.L5_safety.config.structure_blueprint_config import FOLDER_PURITY_RULES

        assert "reasoning" in FOLDER_PURITY_RULES
        # reasoning/ should only allow *Agent.py
        patterns = FOLDER_PURITY_RULES["reasoning"]
        assert any("Agent" in p for p in patterns)

    def test_folder_purity_rules_patterns_are_valid_regex(self):
        import re as re_mod

        from agentic_core.L5_safety.config.structure_blueprint_config import FOLDER_PURITY_RULES

        for folder, patterns in FOLDER_PURITY_RULES.items():
            for pattern in patterns:
                try:
                    re_mod.compile(pattern)
                except re_mod.error as e:
                    pytest.fail(f"Invalid regex in FOLDER_PURITY_RULES['{folder}']: '{pattern}' — {e}")

    def test_app_domain_prefixes_not_empty(self):
        from agentic_core.L5_safety.config.structure_blueprint_config import APP_DOMAIN_PREFIXES

        assert len(APP_DOMAIN_PREFIXES) > 0
        assert "Lic" in APP_DOMAIN_PREFIXES

    def test_layer_keyword_affinity_covers_all_layers(self):
        from agentic_core.L5_safety.config.structure_blueprint_config import LAYER_KEYWORD_AFFINITY

        expected_layers = {
            "L0_routing",
            "L1_cognition",
            "L2_execution",
            "L3_orchestration",
            "L4_state",
            "L5_safety",
            "L6_observability",
        }
        assert set(LAYER_KEYWORD_AFFINITY.keys()) == expected_layers

    def test_suffix_to_folder_strategy_routes_to_enforcement(self):
        """Strategy.py should now route to enforcement/, not reasoning/."""
        from agentic_core.L5_safety.config.structure_blueprint_config import SUFFIX_TO_FOLDER

        assert SUFFIX_TO_FOLDER["Strategy.py"] == "enforcement"

    def test_suffix_to_folder_adapter_routes_to_enforcement(self):
        """Adapter.py should now route to enforcement/, not reasoning/."""
        from agentic_core.L5_safety.config.structure_blueprint_config import SUFFIX_TO_FOLDER

        assert SUFFIX_TO_FOLDER["Adapter.py"] == "enforcement"

    def test_suffix_to_folder_agent_still_routes_to_reasoning(self):
        """Agent.py should still route to reasoning/."""
        from agentic_core.L5_safety.config.structure_blueprint_config import SUFFIX_TO_FOLDER

        assert SUFFIX_TO_FOLDER["Agent.py"] == "reasoning"

    def test_suffix_to_folder_protocol_routes_to_global_interfaces(self):
        """Protocol.py should route to GLOBAL_INTERFACES sentinel."""
        from agentic_core.L5_safety.config.structure_blueprint_config import SUFFIX_TO_FOLDER

        assert SUFFIX_TO_FOLDER["Protocol.py"] == "GLOBAL_INTERFACES"

    def test_interface_filename_pattern_is_valid_regex(self):
        """INTERFACE_FILENAME_PATTERN should be a valid regex."""
        import re as re_mod

        from agentic_core.L5_safety.config.structure_blueprint_config import INTERFACE_FILENAME_PATTERN

        re_mod.compile(INTERFACE_FILENAME_PATTERN)

    def test_interface_pattern_matches_i_protocols(self):
        """INTERFACE_FILENAME_PATTERN should match I*Protocol.py files."""
        import re as re_mod

        from agentic_core.L5_safety.config.structure_blueprint_config import INTERFACE_FILENAME_PATTERN

        assert re_mod.match(INTERFACE_FILENAME_PATTERN, "IHealerProtocol.py")
        assert re_mod.match(INTERFACE_FILENAME_PATTERN, "IOrchestratorProtocol.py")
        assert re_mod.match(INTERFACE_FILENAME_PATTERN, "IValidatorProtocol.py")
        assert not re_mod.match(INTERFACE_FILENAME_PATTERN, "healing_protocol.py")
        assert not re_mod.match(INTERFACE_FILENAME_PATTERN, "input_config.py")

    def test_global_interfaces_folder_defined(self):
        """GLOBAL_INTERFACES_FOLDER should point to agentic_core/interfaces."""
        from agentic_core.L5_safety.config.structure_blueprint_config import GLOBAL_INTERFACES_FOLDER

        assert GLOBAL_INTERFACES_FOLDER == "agentic_core/interfaces"


# ===========================================================================
# Global Interface Routing (enforce_kernel_structure)
# ===========================================================================


class TestGlobalInterfaceRouting:
    """Tests for I*Protocol.py global routing to agentic_core/interfaces/."""

    def test_i_protocol_in_layer_types_routes_to_interfaces(self, agent):
        """I*Protocol.py in L5/types/ should be routed to agentic_core/interfaces/."""
        path = Path("C:/repo/agentic_core/L5_safety/types/IHealerProtocol.py")
        result = agent.enforce_kernel_structure(path)
        assert result is not None
        assert result.parent.name == "interfaces"
        assert "agentic_core" in str(result)

    def test_i_protocol_already_in_interfaces_stays(self, agent):
        """I*Protocol.py already in interfaces/ should not be moved."""
        path = Path("C:/repo/agentic_core/interfaces/IHealerProtocol.py")
        result = agent.enforce_kernel_structure(path)
        assert result is None

    def test_i_protocol_in_any_layer_routes_globally(self, agent):
        """I*Protocol.py in any layer types/ should route to global interfaces/."""
        path = Path("C:/repo/agentic_core/L2_execution/types/IToolProtocol.py")
        result = agent.enforce_kernel_structure(path)
        assert result is not None
        assert result.parent.name == "interfaces"

    def test_regular_protocol_not_routed_globally(self, agent):
        """A regular _protocol.py (no I prefix) should stay in types/."""
        path = Path("C:/repo/agentic_core/L5_safety/types/validation_protocol.py")
        result = agent.enforce_kernel_structure(path)
        # Should NOT be routed to interfaces (no I prefix)
        assert result is None or (result is not None and result.parent.name != "interfaces")

    def test_get_correct_folder_returns_none_for_global_interfaces(self, agent, tmp_path):
        """_get_correct_folder_for_type should return None for I*Protocol.py (global sentinel)."""
        f = _make_file(
            tmp_path,
            "IHealerProtocol.py",
            textwrap.dedent("""\
            from typing import Protocol, runtime_checkable
            @runtime_checkable
            class IHealerProtocol(Protocol):
                def heal_repository(self, dry_run: bool = True) -> dict: ...
        """),
        )
        result = agent._get_correct_folder_for_type(f, tmp_path)
        # PROTOCOL type but I*Protocol.py triggers GLOBAL_INTERFACES sentinel -> None
        # (handled by enforce_kernel_structure global override)
        assert result is None or result == "types"

    def test_get_correct_folder_still_routes_regular_protocol(self, agent, tmp_path):
        """_get_correct_folder_for_type should route a Protocol class to types/."""
        f = _make_file(
            tmp_path,
            "validation_protocol.py",
            textwrap.dedent("""\
            from typing import Protocol
            class ValidationProtocol(Protocol):
                def validate(self) -> bool: ...
        """),
        )
        result = agent._get_correct_folder_for_type(f, tmp_path)
        assert result == "types"


# ===========================================================================
# Ephemeral Script Detection
# ===========================================================================


class TestEphemeralScriptDetection:
    """Tests for _detect_ephemeral_scripts() — flagging phase/wave/sprint scripts."""

    def test_phase_numbered_detected(self, agent):
        """phase10_ssot_purification_util.py should be flagged."""
        path = Path("C:/repo/ops_scripts/maintenance/phase10_ssot_purification_util.py")
        result = agent._detect_ephemeral_scripts(path)
        assert result is not None
        assert result["type"] == "EPHEMERAL_SCRIPT"

    def test_execute_phase_detected(self, agent):
        """execute_phase14_surgery.py should be flagged."""
        path = Path("C:/repo/ops_scripts/maintenance/execute_phase14_surgery.py")
        result = agent._detect_ephemeral_scripts(path)
        assert result is not None

    def test_run_phase_detected(self, agent):
        """run_phase1_tests.py should be flagged."""
        path = Path("C:/repo/ops_scripts/general/run_phase1_tests.py")
        result = agent._detect_ephemeral_scripts(path)
        assert result is not None

    def test_wave_numbered_detected(self, agent):
        """wave_9_integrity_test.py should be flagged."""
        path = Path("C:/repo/ops_scripts/simulations/wave_9_integrity_test.py")
        result = agent._detect_ephemeral_scripts(path)
        assert result is not None

    def test_sprint_numbered_detected(self, agent):
        """sprint4_phase1_l3_dynamic_seal_util.py should be flagged."""
        path = Path("C:/repo/agentic_core/L0_routing/scripts/sprint4_phase1_l3_dynamic_seal_util.py")
        result = agent._detect_ephemeral_scripts(path)
        assert result is not None

    def test_two_phase_exempted(self, agent):
        """TwoPhaseDeduplicationAgent.py should be exempted (algorithm name)."""
        path = Path("C:/repo/apps_lic/engines/TwoPhaseDeduplicationAgent.py")
        assert agent._detect_ephemeral_scripts(path) is None

    def test_execution_phase_types_exempted(self, agent):
        """execution_phase_types.py should be exempted (domain concept)."""
        path = Path("C:/repo/agentic_core/L1_cognition/types/execution_phase_types.py")
        assert agent._detect_ephemeral_scripts(path) is None

    def test_mutation_phase_exempted(self, agent):
        """mutation_phase.py should be exempted (pipeline concept)."""
        path = Path("C:/repo/apps_shared/utils/mutation_phase.py")
        assert agent._detect_ephemeral_scripts(path) is None

    def test_regular_file_passes(self, agent):
        """A normal file without phase/wave should pass."""
        path = Path("C:/repo/agentic_core/L5_safety/reasoning/HealerAgent.py")
        assert agent._detect_ephemeral_scripts(path) is None

    def test_non_python_passes(self, agent):
        """Non-Python files should pass."""
        path = Path("C:/repo/docs/phase1_design.md")
        assert agent._detect_ephemeral_scripts(path) is None


class TestEphemeralConfigConstants:
    """Tests for FORBIDDEN_EPHEMERAL_PATTERNS and exemptions."""

    def test_forbidden_patterns_not_empty(self):
        from agentic_core.L5_safety.config.structure_blueprint_config import FORBIDDEN_EPHEMERAL_PATTERNS

        assert len(FORBIDDEN_EPHEMERAL_PATTERNS) >= 3

    def test_forbidden_patterns_are_valid_regex(self):
        import re as re_mod

        from agentic_core.L5_safety.config.structure_blueprint_config import FORBIDDEN_EPHEMERAL_PATTERNS

        for pattern in FORBIDDEN_EPHEMERAL_PATTERNS:
            re_mod.compile(pattern)

    def test_exemptions_not_empty(self):
        from agentic_core.L5_safety.config.structure_blueprint_config import EPHEMERAL_PATTERN_EXEMPTIONS

        assert len(EPHEMERAL_PATTERN_EXEMPTIONS) >= 3

    def test_exemptions_are_valid_regex(self):
        import re as re_mod

        from agentic_core.L5_safety.config.structure_blueprint_config import EPHEMERAL_PATTERN_EXEMPTIONS

        for pattern in EPHEMERAL_PATTERN_EXEMPTIONS:
            re_mod.compile(pattern)


# ===========================================================================
# Cross-Layer Naming Violation Detection
# ===========================================================================


class TestCrossLayerNamingViolation:
    """Tests for _detect_cross_layer_naming_violation()."""

    def test_l5_file_in_l6_detected(self, agent):
        """l5_streamer.py in L6_observability/ should be flagged."""
        path = Path("C:/repo/agentic_core/L6_observability/enforcement/l5_streamer.py")
        result = agent._detect_cross_layer_naming_violation(path)
        assert result is not None
        assert result["type"] == "CROSS_LAYER_NAMING_VIOLATION"
        assert result["filename_layer"] == "L5"
        assert result["actual_layer"] == "L6"

    def test_l0_file_in_l5_detected(self, agent):
        """l0_bootstrap_util.py in L5_safety/ should be flagged."""
        path = Path("C:/repo/agentic_core/L5_safety/utils/l0_bootstrap_util.py")
        result = agent._detect_cross_layer_naming_violation(path)
        assert result is not None
        assert result["filename_layer"] == "L0"
        assert result["actual_layer"] == "L5"

    def test_l5_file_in_l5_passes(self, agent):
        """l5_safety_util.py in L5_safety/ should pass (matching layers)."""
        path = Path("C:/repo/agentic_core/L5_safety/utils/l5_safety_util.py")
        assert agent._detect_cross_layer_naming_violation(path) is None

    def test_file_without_layer_indicator_passes(self, agent):
        """A normal file without layer indicators should pass."""
        path = Path("C:/repo/agentic_core/L5_safety/reasoning/HealerAgent.py")
        assert agent._detect_cross_layer_naming_violation(path) is None

    def test_file_not_in_layer_folder_passes(self, agent):
        """A file with layer indicator not in a layer folder should pass."""
        path = Path("C:/repo/agentic_core/mixins/l5_helper_mixin.py")
        assert agent._detect_cross_layer_naming_violation(path) is None

    def test_uppercase_L_detected(self, agent):
        """L3_orchestrator_util.py in L5_safety/ should be detected."""
        path = Path("C:/repo/agentic_core/L5_safety/utils/L3_orchestrator_util.py")
        result = agent._detect_cross_layer_naming_violation(path)
        assert result is not None
        assert result["filename_layer"] == "L3"

    def test_message_suggests_action(self, agent):
        """Violation message should suggest rename or move."""
        path = Path("C:/repo/agentic_core/L6_observability/enforcement/l5_streamer.py")
        result = agent._detect_cross_layer_naming_violation(path)
        assert "rename" in result["message"].lower() or "move" in result["message"].lower()


class TestLayerPrefixPatternConfig:
    """Tests for LAYER_PREFIX_PATTERN constant."""

    def test_pattern_is_valid_regex(self):
        import re as re_mod

        from agentic_core.L5_safety.config.structure_blueprint_config import LAYER_PREFIX_PATTERN

        re_mod.compile(LAYER_PREFIX_PATTERN)

    def test_pattern_matches_l5_prefix(self):
        import re as re_mod

        from agentic_core.L5_safety.config.structure_blueprint_config import LAYER_PREFIX_PATTERN

        assert re_mod.search(LAYER_PREFIX_PATTERN, "l5_streamer.py")
        assert re_mod.search(LAYER_PREFIX_PATTERN, "L5_safety_util.py")

    def test_pattern_matches_mid_word(self):
        import re as re_mod

        from agentic_core.L5_safety.config.structure_blueprint_config import LAYER_PREFIX_PATTERN

        assert re_mod.search(LAYER_PREFIX_PATTERN, "my_l3_thing.py")

    def test_pattern_does_not_match_non_layer(self):
        import re as re_mod

        from agentic_core.L5_safety.config.structure_blueprint_config import LAYER_PREFIX_PATTERN

        # "healer" contains "l" but no layer pattern
        assert not re_mod.search(LAYER_PREFIX_PATTERN, "healer_agent.py")


# ===========================================================================
# Duplicate File Detection
# ===========================================================================


class TestDuplicateFileDetection:
    """Tests for _detect_duplicate_files()."""

    def test_detects_same_filename_in_two_locations(self, agent):
        """Two files with same name should be flagged."""
        registry = [
            Path("C:/repo/agentic_core/runtime/types/BudgetExceededError.py"),
            Path("C:/repo/agentic_core/L5_safety/types/BudgetExceededError.py"),
        ]
        violations = agent._detect_duplicate_files(registry)
        assert len(violations) == 1
        assert violations[0]["type"] == "DUPLICATE_FILE"
        assert violations[0]["filename"] == "BudgetExceededError.py"

    def test_canonical_is_higher_priority_location(self, agent):
        """The copy in runtime/ should be canonical over L5_safety/."""
        registry = [
            Path("C:/repo/agentic_core/L5_safety/types/BudgetExceededError.py"),
            Path("C:/repo/agentic_core/runtime/types/BudgetExceededError.py"),
        ]
        violations = agent._detect_duplicate_files(registry)
        assert len(violations) == 1
        # runtime is higher priority than L5_safety
        assert "runtime" in violations[0]["canonical_path"]
        assert "L5_safety" in violations[0]["duplicate_path"]

    def test_triple_duplicate_yields_two_violations(self, agent):
        """Three copies of a file should produce two violations."""
        registry = [
            Path("C:/repo/agentic_core/utils/decorators_util.py"),
            Path("C:/repo/agentic_core/L0_routing/utils/decorators_util.py"),
            Path("C:/repo/agentic_core/L5_safety/utils/decorators_util.py"),
        ]
        violations = agent._detect_duplicate_files(registry)
        assert len(violations) == 2

    def test_init_files_exempt(self, agent):
        """__init__.py should NOT be flagged as duplicate."""
        registry = [
            Path("C:/repo/agentic_core/L0_routing/__init__.py"),
            Path("C:/repo/agentic_core/L5_safety/__init__.py"),
        ]
        violations = agent._detect_duplicate_files(registry)
        assert len(violations) == 0

    def test_conftest_exempt(self, agent):
        """conftest.py should NOT be flagged as duplicate."""
        registry = [
            Path("C:/repo/tests/conftest.py"),
            Path("C:/repo/tests/unit/conftest.py"),
        ]
        violations = agent._detect_duplicate_files(registry)
        assert len(violations) == 0

    def test_unique_files_no_violations(self, agent):
        """Unique filenames should produce no violations."""
        registry = [
            Path("C:/repo/agentic_core/L5_safety/types/safety_types.py"),
            Path("C:/repo/agentic_core/L1_cognition/types/cognition_types.py"),
        ]
        violations = agent._detect_duplicate_files(registry)
        assert len(violations) == 0

    def test_non_python_files_skipped(self, agent):
        """Non-Python files should be skipped."""
        registry = [
            Path("C:/repo/docs/README.md"),
            Path("C:/repo/README.md"),
        ]
        violations = agent._detect_duplicate_files(registry)
        assert len(violations) == 0

    def test_violation_message_contains_locations(self, agent):
        """Violation message should mention both canonical and duplicate locations."""
        registry = [
            Path("C:/repo/agentic_core/runtime/types/BudgetExceededError.py"),
            Path("C:/repo/agentic_core/L5_safety/types/BudgetExceededError.py"),
        ]
        violations = agent._detect_duplicate_files(registry)
        assert "Canonical" in violations[0]["message"]
        assert "Duplicate" in violations[0]["message"]


class TestDuplicateDetectionConfig:
    """Tests for CANONICAL_LOCATION_PRIORITY and DUPLICATE_DETECTION_EXEMPT."""

    def test_priority_not_empty(self):
        from agentic_core.L5_safety.config.structure_blueprint_config import CANONICAL_LOCATION_PRIORITY

        assert len(CANONICAL_LOCATION_PRIORITY) >= 10

    def test_runtime_is_highest_priority(self):
        from agentic_core.L5_safety.config.structure_blueprint_config import CANONICAL_LOCATION_PRIORITY

        assert CANONICAL_LOCATION_PRIORITY[0] == "runtime"

    def test_exempt_contains_init(self):
        from agentic_core.L5_safety.config.structure_blueprint_config import DUPLICATE_DETECTION_EXEMPT

        assert "__init__.py" in DUPLICATE_DETECTION_EXEMPT

    def test_exempt_contains_conftest(self):
        from agentic_core.L5_safety.config.structure_blueprint_config import DUPLICATE_DETECTION_EXEMPT

        assert "conftest.py" in DUPLICATE_DETECTION_EXEMPT
