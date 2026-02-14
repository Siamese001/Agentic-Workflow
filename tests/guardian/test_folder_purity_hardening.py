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
9. reasoning/ folder purity: Agent-only enforcement with ratchet ceiling
10. runtime/types purity (no non-type files)
11. COMPOUND_SUFFIX_CONFLICTS config completeness

Run with: pytest tests/guardian/test_folder_purity_hardening.py -v
"""

import re
import sys
import textwrap
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L5_safety.config.structure_blueprint_config import (
    COMPOUND_SUFFIX_CONFLICTS,
    FOLDER_PURITY_RULES,
)
from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
    FileClassificationAgent,
)

EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
    "archives",
    ".sovereign_healing_backup",
}
COMPOUND_SUFFIX_ALLOWLIST = {
    "domain_agent_mixin.py",
    "feature_flagged_agent_mixin.py",
    "healer_agent_mixin.py",
    "expansion_strategy_types.py",
}
UTILS_SUFFIX_ALLOWLIST = {
    "meta_learning_engine.py",
    "meta_learning_storage.py",
    "structural_healing_engine.py",
    "guardrails.py",
    "history_merger.py",
    "profile_updater.py",
    "template_finder.py",
    "template_matcher.py",
    "token_updater.py",
    "log_orchestration_metrics.py",
    "local_disk_adapter.py",
    "cache_invalidation_utils.py",
    "code_tool_runner_core.py",
    "ConstitutionalOverseer.py",
    "_fca_safety_gates.py",
}
RUNTIME_TYPES_ALLOWLIST = {
    "expansion_strategy_types.py",
}
ENFORCEMENT_SUFFIX_ALLOWLIST = {
    "AdapterBase.py",
}
TYPES_SUFFIX_ALLOWLIST = {
    "agent_audit_result.py",
    "guardian_contract.py",
    "guardian_registry.py",
    "integration_contract.py",
    "v15_contracts.py",
    "v15_p2_contracts.py",
    "healer_registry.py",
    "heal_contract.py",
    "l2_phase_spec.py",
    "approval_contract.py",
    "sovereign_report.py",
}
AGENTIC_CORE = PROJECT_ROOT / "agentic_core"


@pytest.fixture(scope="module")
def agent():
    return FileClassificationAgent(
        project_root=PROJECT_ROOT,
        dry_run=True,
        validate_only=True,
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
            if f.name in COMPOUND_SUFFIX_ALLOWLIST:
                continue
            conflicts = agent._detect_filename_tag_conflicts(f)
            if conflicts:
                violations.append((f.name, conflicts))

        if violations:
            detail = "\n".join(f"  - {n}: {t}" for n, t in violations[:20])
            pytest.fail(f"BLOCKING: {len(violations)} compound suffix violations:\n{detail}")

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
                f"BLOCKING: {len(violations)} files in validators/ without _validator suffix:\n{detail}",
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
                if f.name in UTILS_SUFFIX_ALLOWLIST:
                    continue
                if not f.name.endswith("_util.py") and not f.name.endswith("_helper.py"):
                    violations.append(str(f.relative_to(PROJECT_ROOT)))

        if violations:
            detail = "\n".join(f"  - {v}" for v in violations[:20])
            pytest.fail(f"BLOCKING: {len(violations)} files in utils/ without _util suffix:\n{detail}")


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
                if f.name in TYPES_SUFFIX_ALLOWLIST:
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
            pytest.fail(f"BLOCKING: {len(violations)} files in types/ without _types suffix:\n{detail}")


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
                if f.name in ENFORCEMENT_SUFFIX_ALLOWLIST:
                    continue
                if not any(pat.match(f.name) for pat in compiled):
                    violations.append(str(f.relative_to(PROJECT_ROOT)))

        if violations:
            detail = "\n".join(f"  - {v}" for v in violations[:20])
            pytest.fail(f"{len(violations)} files in enforcement/ don't match purity patterns:\n{detail}")


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
        f.write_text(
            textwrap.dedent("""\
            class FooAgent:
                def heal(self): pass
        """),
        )
        result = agent.classify_file(f)
        assert result == "TYPES"

    def test_agent_types_in_reasoning_folder_classified_as_agent(self, agent, tmp_path):
        """A dual-tag file in reasoning/ should be classified as AGENT."""
        reasoning_dir = tmp_path / "reasoning"
        reasoning_dir.mkdir()
        f = reasoning_dir / "foo_agent_types.py"
        f.write_text(
            textwrap.dedent("""\
            class FooAgent:
                def heal(self): pass
        """),
        )
        result = agent.classify_file(f)
        assert result == "AGENT"

    def test_strategy_config_in_config_folder_classified_as_config(self, agent, tmp_path):
        """A dual-tag file in config/ should be classified as CONFIG."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        f = config_dir / "foo_strategy_config.py"
        f.write_text(
            textwrap.dedent("""\
            MAX_RETRIES = 3
            TIMEOUT = 30
        """),
        )
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
# 9. reasoning/ Folder Purity — Agent-Only Enforcement
# ============================================================================


class TestReasoningFolderPurity:
    """BLOCKING: reasoning/ folders under L0-L6 must ONLY contain Agent files.

    Rule: Every .py file in agentic_core/L*/reasoning/ must be:
    - PascalCase filename ending with Agent.py, OR
    - __init__.py

    Non-agent files (engines, managers, utils) are legacy violations tracked
    via a non-growing debt ceiling (§29). New violations are BLOCKED.
    """

    # Ratchet ceiling: current count of non-Agent files in reasoning/.
    # This number must NEVER increase. Decrease it as files are relocated.
    REASONING_NON_AGENT_CEILING = 62

    @staticmethod
    def _is_compliant_agent_filename(name: str) -> bool:
        """Check if filename matches PascalCase + Agent.py convention."""
        if name == "__init__.py":
            return True
        stem = name.removesuffix(".py")
        # PascalCase: starts uppercase, no underscores
        return bool(re.match(r"^[A-Z][a-zA-Z0-9]*Agent$", stem))

    def test_no_new_non_agent_files_in_reasoning(self):
        """BLOCKING: Non-agent file count in reasoning/ must not exceed ceiling."""
        violations = []
        for layer_dir in sorted(AGENTIC_CORE.iterdir()):
            if not layer_dir.is_dir() or not layer_dir.name.startswith("L"):
                continue
            reasoning = layer_dir / "reasoning"
            if not reasoning.is_dir():
                continue
            for f in sorted(reasoning.glob("*.py")):
                if f.name == "__init__.py":
                    continue
                if not self._is_compliant_agent_filename(f.name):
                    violations.append(str(f.relative_to(PROJECT_ROOT)))

        count = len(violations)
        ceiling = self.REASONING_NON_AGENT_CEILING

        # §32: Print counts as governance signals
        print(f"\n  reasoning/ non-agent files: count={count}, ceiling={ceiling}, delta={count - ceiling}")

        if count > ceiling:
            new_violations = violations[ceiling:]
            detail = "\n".join(f"  - {v}" for v in new_violations[:20])
            pytest.fail(
                f"BLOCKING: reasoning/ non-agent file count ({count}) exceeds "
                f"ceiling ({ceiling}). {count - ceiling} NEW non-agent file(s) "
                f"added to reasoning/ — move them to the correct LCD folder "
                f"(utils/, types/, enforcement/, scripts/):\n{detail}",
            )

    def test_agent_files_in_reasoning_are_pascalcase(self):
        """BLOCKING: Every *Agent.py file in reasoning/ must be PascalCase."""
        violations = []
        for layer_dir in sorted(AGENTIC_CORE.iterdir()):
            if not layer_dir.is_dir() or not layer_dir.name.startswith("L"):
                continue
            reasoning = layer_dir / "reasoning"
            if not reasoning.is_dir():
                continue
            for f in sorted(reasoning.glob("*Agent.py")):
                stem = f.name.removesuffix(".py")
                if not re.match(r"^[A-Z][a-zA-Z0-9]*$", stem):
                    violations.append(str(f.relative_to(PROJECT_ROOT)))

        if violations:
            detail = "\n".join(f"  - {v}" for v in violations)
            pytest.fail(
                f"BLOCKING: {len(violations)} Agent files in reasoning/ are not PascalCase:\n{detail}",
            )

    def test_reasoning_folders_exist_per_layer(self):
        """Every L0-L6 layer must have a reasoning/ folder."""
        for layer_dir in sorted(AGENTIC_CORE.iterdir()):
            if not layer_dir.is_dir():
                continue
            if not re.match(r"^L[0-6]_", layer_dir.name):
                continue
            reasoning = layer_dir / "reasoning"
            assert reasoning.is_dir(), f"{layer_dir.name}/ is missing a reasoning/ folder"


# ============================================================================
# 10. runtime/types Purity (renumbered from 9)
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
            pytest.fail(f"runtime/types/ has non-type files: {violations}")

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

        strategies = [f.name for f in rt.glob("*Strategy*.py") if f.name not in RUNTIME_TYPES_ALLOWLIST]
        assert not strategies, f"Strategies in runtime/types/: {strategies}"


# ============================================================================
# 11. FOLDER_PURITY_RULES Config Completeness (renumbered from 10)
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
