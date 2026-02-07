"""
Guardian Test: Folder Purity & Classification Hardening
=========================================================
Regression tests for all recent hardening changes to:
- structure_blueprint_config.py (COMPOUND_SUFFIX_CONFLICTS, FOLDER_PURITY_RULES,
  CLASSIFICATION_SUFFIX_PATTERNS)
- FileClassificationAgent.py (_detect_filename_tag_conflicts, PRIORITY 2.3
  dual-tag resolution, classify_file folder-context)

Coverage areas:
1. Compound suffix regression scan (zero violations in live codebase)
2. Folder purity: validators/ must have _validator suffix
3. Folder purity: utils/ must have _util suffix
4. Folder purity: types/ must have _types suffix (or *Error/*Exception/*Protocol)
5. Folder purity: enforcement/ must have Strategy/Adapter/Factory/guardrail etc.
6. Dual-tag conflict detection via _detect_filename_tag_conflicts()
7. classify_file() folder-context resolution for dual-tag files
8. Adapter/Strategy routing to enforcement/ across layers
9. runtime/types purity (no non-type files)
10. COMPOUND_SUFFIX_CONFLICTS config completeness

Run with: pytest tests/guardian/test_folder_purity_hardening.py -v
"""

import re
import sys
import tempfile
import textwrap
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L5_safety.config.structure_blueprint_config import (
    COMPOUND_SUFFIX_CONFLICTS,
    FOLDER_PURITY_RULES,
    KNOWN_ARCHITECTURAL_SUFFIXES,
)
from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
    FileClassificationAgent,
)

EXCLUDED_DIRS = {
    ".git", ".venv", "venv", "__pycache__", ".pytest_cache",
    "node_modules", "archives", ".sovereign_healing_backup",
}
AGENTIC_CORE = PROJECT_ROOT / "agentic_core"


@pytest.fixture(scope="module")
def agent():
    return FileClassificationAgent(
        project_root=PROJECT_ROOT, dry_run=True, validate_only=True,
    )


def _should_skip(path: Path) -> bool:
    return any(d in path.parts for d in EXCLUDED_DIRS)


# ============================================================================
# 1. Compound Suffix Regression Scan (live codebase)
# ============================================================================

class TestCompoundSuffixRegression:
    """BLOCKING: No file in agentic_core/ may have a compound classification suffix."""

    def test_zero_compound_suffix_violations(self, agent):
        """Scan entire agentic_core/ for compound suffix violations."""
        violations = []
        for f in AGENTIC_CORE.rglob("*.py"):
            if _should_skip(f):
                continue
            conflicts = agent._detect_filename_tag_conflicts(f)
            if conflicts:
                violations.append((f.name, conflicts))

        if violations:
            detail = "\n".join(f"  - {n}: {t}" for n, t in violations[:20])
            pytest.fail(
                f"BLOCKING: {len(violations)} compound suffix violations:\n{detail}"
            )

    def test_compound_suffix_config_has_agent_types(self):
        """COMPOUND_SUFFIX_CONFLICTS must include _agent_types pattern."""
        patterns = [p for p, *_ in COMPOUND_SUFFIX_CONFLICTS]
        assert any("_agent_types" in p for p in patterns), (
            "_agent_types pattern missing from COMPOUND_SUFFIX_CONFLICTS"
        )

    def test_compound_suffix_config_has_engine_types(self):
        """COMPOUND_SUFFIX_CONFLICTS must include _engine_types pattern."""
        patterns = [p for p, *_ in COMPOUND_SUFFIX_CONFLICTS]
        assert any("_engine_types" in p for p in patterns), (
            "_engine_types pattern missing from COMPOUND_SUFFIX_CONFLICTS"
        )

    def test_compound_suffix_config_has_strategy_config(self):
        """COMPOUND_SUFFIX_CONFLICTS must include _strategy_config pattern."""
        patterns = [p for p, *_ in COMPOUND_SUFFIX_CONFLICTS]
        assert any("_strategy_config" in p for p in patterns), (
            "_strategy_config pattern missing from COMPOUND_SUFFIX_CONFLICTS"
        )

    def test_compound_suffix_config_minimum_coverage(self):
        """COMPOUND_SUFFIX_CONFLICTS must have at least 30 patterns."""
        assert len(COMPOUND_SUFFIX_CONFLICTS) >= 30, (
            f"Only {len(COMPOUND_SUFFIX_CONFLICTS)} patterns — expected >= 30"
        )

    def test_all_compound_patterns_are_valid_regex(self):
        """Every pattern in COMPOUND_SUFFIX_CONFLICTS must compile as valid regex."""
        for pattern, tag_a, tag_b, example in COMPOUND_SUFFIX_CONFLICTS:
            try:
                re.compile(pattern)
            except re.error as e:
                pytest.fail(f"Invalid regex '{pattern}': {e}")


# ============================================================================
# 2. Folder Purity: validators/ must have _validator suffix
# ============================================================================

class TestValidatorsFolderPurity:
    """BLOCKING: All .py files in validators/ folders must end with _validator.py."""

    def test_all_validators_have_suffix(self):
        """Every .py file in a validators/ folder must have _validator suffix or Validator in name."""
        violations = []
        for d in AGENTIC_CORE.rglob("validators"):
            if not d.is_dir() or _should_skip(d):
                continue
            for f in d.glob("*.py"):
                if f.name in ("__init__.py", "conftest.py"):
                    continue
                if not f.name.endswith("_validator.py") and "Validator" not in f.name:
                    violations.append(str(f.relative_to(PROJECT_ROOT)))

        if violations:
            detail = "\n".join(f"  - {v}" for v in violations[:20])
            pytest.fail(
                f"BLOCKING: {len(violations)} files in validators/ without _validator suffix:\n{detail}"
            )


# ============================================================================
# 3. Folder Purity: utils/ must have _util suffix
# ============================================================================

class TestUtilsFolderPurity:
    """BLOCKING: All .py files in utils/ folders must end with _util.py."""

    def test_all_utils_have_suffix(self):
        """Every .py file in a utils/ folder must have _util or _helper suffix."""
        violations = []
        for d in AGENTIC_CORE.rglob("utils"):
            if not d.is_dir() or _should_skip(d):
                continue
            for f in d.glob("*.py"):
                if f.name in ("__init__.py", "conftest.py"):
                    continue
                if not f.name.endswith("_util.py") and not f.name.endswith("_helper.py"):
                    violations.append(str(f.relative_to(PROJECT_ROOT)))

        if violations:
            detail = "\n".join(f"  - {v}" for v in violations[:20])
            pytest.fail(
                f"BLOCKING: {len(violations)} files in utils/ without _util suffix:\n{detail}"
            )


# ============================================================================
# 4. Folder Purity: types/ must have _types suffix (or Error/Exception/Protocol)
# ============================================================================

class TestTypesFolderPurity:
    """BLOCKING: All .py files in types/ must have _types suffix or be Error/Exception/Protocol."""

    def test_all_types_have_suffix(self):
        """Every .py file in a types/ folder must have _types, _protocol, Error, Exception, or I*Protocol."""
        violations = []
        for d in AGENTIC_CORE.rglob("types"):
            if not d.is_dir() or _should_skip(d):
                continue
            for f in d.glob("*.py"):
                if f.name in ("__init__.py", "conftest.py"):
                    continue
                ok = (
                    f.name.endswith("_types.py")
                    or f.name.endswith("_protocol.py")
                    or "Error" in f.name
                    or "Exception" in f.name
                    or (f.name.startswith("I") and "Protocol" in f.name)
                )
                if not ok:
                    violations.append(str(f.relative_to(PROJECT_ROOT)))

        if violations:
            detail = "\n".join(f"  - {v}" for v in violations[:20])
            pytest.fail(
                f"BLOCKING: {len(violations)} files in types/ without _types suffix:\n{detail}"
            )


# ============================================================================
# 5. Folder Purity: enforcement/ must have enforcement-pattern names
# ============================================================================

class TestEnforcementFolderPurity:
    """Files in enforcement/ must match enforcement naming patterns."""

    def test_enforcement_files_have_valid_patterns(self):
        """Every .py in enforcement/ should match at least one FOLDER_PURITY_RULES['enforcement'] pattern."""
        enforcement_patterns = FOLDER_PURITY_RULES.get("enforcement", [])
        compiled = [re.compile(p) for p in enforcement_patterns]
        violations = []

        for d in AGENTIC_CORE.rglob("enforcement"):
            if not d.is_dir() or _should_skip(d):
                continue
            for f in d.glob("*.py"):
                if f.name in ("__init__.py", "conftest.py"):
                    continue
                if not any(pat.match(f.name) for pat in compiled):
                    violations.append(str(f.relative_to(PROJECT_ROOT)))

        if violations:
            detail = "\n".join(f"  - {v}" for v in violations[:20])
            pytest.fail(
                f"{len(violations)} files in enforcement/ don't match purity patterns:\n{detail}"
            )


# ============================================================================
# 6. Dual-Tag Conflict Detection (unit tests)
# ============================================================================

class TestDualTagConflictDetection:
    """Unit tests for _detect_filename_tag_conflicts()."""

    def test_agent_types_detected(self, agent, tmp_path):
        """_agent_types compound should be detected."""
        f = tmp_path / "types" / "foo_agent_types.py"
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text("x = 1")
        conflicts = agent._detect_filename_tag_conflicts(f)
        assert len(conflicts) >= 2
        assert "AGENT" in conflicts
        assert "TYPES" in conflicts

    def test_engine_types_detected(self, agent, tmp_path):
        """_engine_types compound should be detected."""
        f = tmp_path / "safety_engine_types.py"
        f.write_text("x = 1")
        conflicts = agent._detect_filename_tag_conflicts(f)
        assert len(conflicts) >= 2

    def test_strategy_config_detected(self, agent, tmp_path):
        """_strategy_config compound should be detected."""
        f = tmp_path / "foo_strategy_config.py"
        f.write_text("x = 1")
        conflicts = agent._detect_filename_tag_conflicts(f)
        assert len(conflicts) >= 2

    def test_validator_util_detected(self, agent, tmp_path):
        """_validator_util compound should be detected."""
        f = tmp_path / "check_validator_util.py"
        f.write_text("x = 1")
        conflicts = agent._detect_filename_tag_conflicts(f)
        assert len(conflicts) >= 2

    def test_clean_file_not_flagged(self, agent, tmp_path):
        """A file with a single suffix should NOT be flagged."""
        f = tmp_path / "user_profile_types.py"
        f.write_text("x = 1")
        conflicts = agent._detect_filename_tag_conflicts(f)
        assert len(conflicts) == 0

    def test_domain_word_agent_not_flagged(self, agent, tmp_path):
        """Files with 'agent' as domain word (e.g., find_misnamed_agents_util.py) should NOT be flagged."""
        f = tmp_path / "find_misnamed_agents_util.py"
        f.write_text("x = 1")
        conflicts = agent._detect_filename_tag_conflicts(f)
        assert len(conflicts) == 0

    def test_no_suffix_not_flagged(self, agent, tmp_path):
        """Files without any classification suffix should NOT be flagged."""
        f = tmp_path / "SovereignBaseAgent.py"
        f.write_text("class SovereignBaseAgent: pass")
        conflicts = agent._detect_filename_tag_conflicts(f)
        assert len(conflicts) == 0


# ============================================================================
# 7. classify_file() Folder-Context Resolution
# ============================================================================

class TestClassifyFileFolderContext:
    """PRIORITY 2.3: When dual tags detected, folder context wins."""

    def test_agent_types_in_types_folder_classified_as_types(self, agent, tmp_path):
        """A dual-tag file in types/ should be classified as TYPES."""
        types_dir = tmp_path / "types"
        types_dir.mkdir()
        f = types_dir / "foo_agent_types.py"
        f.write_text(textwrap.dedent("""\
            class FooAgent:
                def heal(self): pass
        """))
        result = agent.classify_file(f)
        assert result == "TYPES"

    def test_agent_types_in_reasoning_folder_classified_as_agent(self, agent, tmp_path):
        """A dual-tag file in reasoning/ should be classified as AGENT."""
        reasoning_dir = tmp_path / "reasoning"
        reasoning_dir.mkdir()
        f = reasoning_dir / "foo_agent_types.py"
        f.write_text(textwrap.dedent("""\
            class FooAgent:
                def heal(self): pass
        """))
        result = agent.classify_file(f)
        assert result == "AGENT"

    def test_strategy_config_in_config_folder_classified_as_config(self, agent, tmp_path):
        """A dual-tag file in config/ should be classified as CONFIG."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        f = config_dir / "foo_strategy_config.py"
        f.write_text(textwrap.dedent("""\
            MAX_RETRIES = 3
            TIMEOUT = 30
        """))
        result = agent.classify_file(f)
        assert result == "CONFIG"


# ============================================================================
# 8. Adapter/Strategy Routing to enforcement/ Across Layers
# ============================================================================

class TestEnforcementRouting:
    """Adapter, Strategy, Factory files must be in enforcement/ folders."""

    def test_no_adapters_in_reasoning(self):
        """No *Adapter*.py or *_adapter.py files should be in reasoning/ folders."""
        violations = []
        for d in AGENTIC_CORE.rglob("reasoning"):
            if not d.is_dir() or _should_skip(d):
                continue
            for f in d.glob("*.py"):
                if "Adapter" in f.name or "_adapter" in f.name:
                    violations.append(str(f.relative_to(PROJECT_ROOT)))

        if violations:
            detail = "\n".join(f"  - {v}" for v in violations)
            pytest.fail(f"{len(violations)} Adapter files in reasoning/:\n{detail}")

    def test_no_strategies_in_reasoning(self):
        """No *Strategy*.py or *_strategy.py files should be in reasoning/ folders."""
        violations = []
        for d in AGENTIC_CORE.rglob("reasoning"):
            if not d.is_dir() or _should_skip(d):
                continue
            for f in d.glob("*.py"):
                if f.name == "__init__.py":
                    continue
                if "Strategy" in f.name or "_strategy" in f.name:
                    violations.append(str(f.relative_to(PROJECT_ROOT)))

        if violations:
            detail = "\n".join(f"  - {v}" for v in violations)
            pytest.fail(f"{len(violations)} Strategy files in reasoning/:\n{detail}")

    def test_l3_enforcement_not_empty(self):
        """L3_orchestration/enforcement/ must have at least 1 non-init file."""
        enf = AGENTIC_CORE / "L3_orchestration" / "enforcement"
        if not enf.exists():
            pytest.fail("L3_orchestration/enforcement/ directory does not exist")
        files = [f for f in enf.glob("*.py") if f.name != "__init__.py"]
        assert len(files) >= 1, "L3_orchestration/enforcement/ is empty"


# ============================================================================
# 9. runtime/types Purity
# ============================================================================

class TestRuntimeTypesPurity:
    """runtime/types/ must only contain type definitions."""

    def test_no_non_type_files_in_runtime_types(self):
        """Every file in runtime/types/ must be _types, Error, Exception, or Protocol."""
        rt = AGENTIC_CORE / "runtime" / "types"
        if not rt.exists():
            pytest.skip("runtime/types/ does not exist")

        violations = []
        for f in rt.glob("*.py"):
            if f.name == "__init__.py":
                continue
            ok = (
                f.name.endswith("_types.py")
                or "Error" in f.name
                or "Exception" in f.name
                or "Protocol" in f.name
            )
            if not ok:
                violations.append(f.name)

        if violations:
            pytest.fail(
                f"runtime/types/ has non-type files: {violations}"
            )

    def test_no_factories_in_runtime_types(self):
        """No *Factory.py files should be in runtime/types/."""
        rt = AGENTIC_CORE / "runtime" / "types"
        if not rt.exists():
            pytest.skip("runtime/types/ does not exist")

        factories = [f.name for f in rt.glob("*Factory*.py")]
        assert not factories, f"Factories in runtime/types/: {factories}"

    def test_no_strategies_in_runtime_types(self):
        """No *Strategy.py files should be in runtime/types/."""
        rt = AGENTIC_CORE / "runtime" / "types"
        if not rt.exists():
            pytest.skip("runtime/types/ does not exist")

        strategies = [f.name for f in rt.glob("*Strategy*.py")]
        assert not strategies, f"Strategies in runtime/types/: {strategies}"


# ============================================================================
# 10. FOLDER_PURITY_RULES Config Completeness
# ============================================================================

class TestFolderPurityConfig:
    """Validate FOLDER_PURITY_RULES config is complete and correct."""

    REQUIRED_FOLDERS = ["reasoning", "validators", "config", "types", "utils", "scripts", "enforcement"]

    def test_all_lcd_folders_have_rules(self):
        """Every LCD folder must have purity rules defined."""
        for folder in self.REQUIRED_FOLDERS:
            assert folder in FOLDER_PURITY_RULES, (
                f"Missing purity rules for '{folder}' in FOLDER_PURITY_RULES"
            )

    def test_types_allows_error_files(self):
        """FOLDER_PURITY_RULES['types'] must allow *Error.py."""
        patterns = FOLDER_PURITY_RULES["types"]
        compiled = [re.compile(p) for p in patterns]
        assert any(p.match("BudgetExceededError.py") for p in compiled), (
            "types/ purity rules don't allow *Error.py files"
        )

    def test_types_allows_exception_files(self):
        """FOLDER_PURITY_RULES['types'] must allow *Exception.py."""
        patterns = FOLDER_PURITY_RULES["types"]
        compiled = [re.compile(p) for p in patterns]
        assert any(p.match("WorkflowException.py") for p in compiled), (
            "types/ purity rules don't allow *Exception.py files"
        )

    def test_enforcement_allows_factory(self):
        """FOLDER_PURITY_RULES['enforcement'] must allow *Factory.py."""
        patterns = FOLDER_PURITY_RULES["enforcement"]
        compiled = [re.compile(p) for p in patterns]
        assert any(p.match("EnvelopeFactory.py") for p in compiled), (
            "enforcement/ purity rules don't allow *Factory.py files"
        )

    def test_enforcement_allows_adapter(self):
        """FOLDER_PURITY_RULES['enforcement'] must allow *Adapter.py."""
        patterns = FOLDER_PURITY_RULES["enforcement"]
        compiled = [re.compile(p) for p in patterns]
        assert any(p.match("DomainPlannerAdapter.py") for p in compiled), (
            "enforcement/ purity rules don't allow *Adapter.py files"
        )

    def test_enforcement_allows_strategy(self):
        """FOLDER_PURITY_RULES['enforcement'] must allow *Strategy.py."""
        patterns = FOLDER_PURITY_RULES["enforcement"]
        compiled = [re.compile(p) for p in patterns]
        assert any(p.match("ExpansionStrategy.py") for p in compiled), (
            "enforcement/ purity rules don't allow *Strategy.py files"
        )

    def test_all_purity_patterns_are_valid_regex(self):
        """Every pattern in FOLDER_PURITY_RULES must compile as valid regex."""
        for folder, patterns in FOLDER_PURITY_RULES.items():
            for pat in patterns:
                try:
                    re.compile(pat)
                except re.error as e:
                    pytest.fail(f"Invalid regex in FOLDER_PURITY_RULES['{folder}']: '{pat}' — {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
