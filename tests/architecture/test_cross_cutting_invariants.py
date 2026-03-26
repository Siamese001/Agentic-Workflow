"""Plan 6 — Cross-Cutting Architecture Invariants (AST-based).

Five deterministic invariants that prevent the highest-risk cross-cutting
regressions from silently re-entering the codebase:

1. Single threshold source — HEALING_CONFIDENCE_X/Y defined only in
   healing_tier_config.py, not re-defined in qwen_meta_learning.py.

2. No bare except-pass — every `except` handler whose body is only `pass`
   (or only `...`) must carry a `# guardian: allow-silent-swallow` comment.

3. No ghost-import swallowing — `except ImportError: <name> = None` patterns
   without an adjacent `logger.critical` or `_logger.critical` call.

4. MetaLearningChangePackage constructor — DefaultMetaOutcomeBusHook must
   use the `.create()` factory, not direct dataclass construction.

5. Response capture — `invoke_qwen_vllm` and `invoke_gemini` must assign the
   API return value to a local variable (not discard it).
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

#  # MOVED: from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_SHARED_DIR,
    SYSTEM_LEARNING_DIR,
)
#  # MOVED: from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    DISCOVERY_EXCLUDED_TERRITORIES,
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)

pytestmark = pytest.mark.architecture

_ROOT = Path(__file__).parents[2]


def _parse(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


# ---------------------------------------------------------------------------
# Invariant 1: Single threshold source
# ---------------------------------------------------------------------------


class TestSingleThresholdSource:
    _TIER_CFG = _ROOT / "agentic_core/L1_cognition/config/healing_tier_config.py"
    _QWEN_ML = _ROOT / "agentic_core/L1_cognition/engines/qwen_meta_learning.py"

    def _assignment_names(self, path: Path) -> set[str]:
        if not path.exists():
            return set()
        tree = _parse(path)
        return {
            node.targets[0].id
            for node in ast.walk(tree)
            if isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
        }

    def test_healing_confidence_x_defined_only_in_tier_config(self):
                from agentic_core.L0_routing.config.path_constants import (
                from agentic_core.L5_safety.config.structure_blueprint.ssot import (
                qwen_names = self._assignment_names(self._QWEN_ML)
                assert "HEALING_CONFIDENCE_X" not in qwen_names, (
                    "HEALING_CONFIDENCE_X must not be re-defined in qwen_meta_learning.py; "
                    "import from healing_tier_config.py"
                )


    def test_healing_confidence_y_defined_only_in_tier_config(self):
        qwen_names = self._assignment_names(self._QWEN_ML)
        assert "HEALING_CONFIDENCE_Y" not in qwen_names, (
            "HEALING_CONFIDENCE_Y must not be re-defined in qwen_meta_learning.py; "
            "import from healing_tier_config.py"
        )


# ---------------------------------------------------------------------------
# Invariant 2: No bare except-pass without guardian comment
# ---------------------------------------------------------------------------


class TestNoBareExceptPass:
    _SCAN_DIRS = [
        _ROOT / AGENTIC_CORE_DIR,
        _ROOT / SYSTEM_LEARNING_DIR,
        _ROOT / APPS_SHARED_DIR,
    ]
    _EXCLUDE_DIRS = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES

    def _collect_bare_except_pass(self) -> list[tuple[str, int]]:
        """Return (filepath, lineno) for each bare except-pass without guardian."""
        violations: list[tuple[str, int]] = []
        for scan_dir in self._SCAN_DIRS:
            if not scan_dir.exists():
                continue
            for py_file in scan_dir.rglob("*.py"):
                if any(d in py_file.parts for d in self._EXCLUDE_DIRS):
                    continue
                try:
                    source = py_file.read_text(encoding="utf-8")
                    tree = ast.parse(source, filename=str(py_file))
                    source_lines = source.splitlines()
                except (SyntaxError, UnicodeDecodeError):
                    continue

                for node in ast.walk(tree):
                    if not isinstance(node, ast.ExceptHandler):
                        continue
                    body = node.body
                    if len(body) == 1 and isinstance(body[0], (ast.Pass, ast.Expr)):
                        if isinstance(body[0], ast.Expr) and not isinstance(body[0].value, ast.Constant):
                            continue
                        handler_line = node.lineno - 1
                        comment_text = ""
                        if 0 <= handler_line < len(source_lines):
                            comment_text = source_lines[handler_line]
                        for offset in range(min(3, len(source_lines) - handler_line)):
                            comment_text += source_lines[handler_line + offset]
                        if "guardian: allow-silent-swallow" not in comment_text:
                            violations.append((str(py_file.relative_to(_ROOT)), node.lineno))
        return violations

    _BASELINE_CEILING = 222  # §29 non-growing debt: current count at Plan 6 commit

    def test_no_bare_except_pass_count_does_not_grow(self):
        """Assert bare except-pass count never exceeds the Plan-6 baseline.

        Fix violations by adding '# guardian: allow-silent-swallow' and a
        _logger.debug() call. Decrease this ceiling as debt is paid down.
        """
        violations = self._collect_bare_except_pass()
        current_count = len(violations)
        print(f"bare-except-pass count: {current_count} (ceiling: {self._BASELINE_CEILING})")
        assert current_count <= self._BASELINE_CEILING, (
            f"bare except-pass without guardian GREW: {current_count} > "
            f"{self._BASELINE_CEILING} (baseline). "
            f"New violations:\n  "
            + "\n  ".join(f"{f}:{ln}" for f, ln in sorted(violations)[self._BASELINE_CEILING :])
        )


# ---------------------------------------------------------------------------
# Invariant 3: No ghost import swallowing without logger.critical
# ---------------------------------------------------------------------------


class TestNoGhostImportSwallowing:
    _SCAN_DIRS = [
        _ROOT / AGENTIC_CORE_DIR,
        _ROOT / SYSTEM_LEARNING_DIR,
    ]
    _EXCLUDE_DIRS = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES

    def _collect_ghost_swallowers(self) -> list[tuple[str, int]]:
        """Find except ImportError handlers that set names to None/empty without logging."""
        violations: list[tuple[str, int]] = []
        for scan_dir in self._SCAN_DIRS:
            if not scan_dir.exists():
                continue
            for py_file in scan_dir.rglob("*.py"):
                if any(d in py_file.parts for d in self._EXCLUDE_DIRS):
                    continue
                try:
                    source = py_file.read_text(encoding="utf-8")
                    tree = ast.parse(source, filename=str(py_file))
                    source_lines = source.splitlines()
                except (SyntaxError, UnicodeDecodeError):
                    continue

                for node in ast.walk(tree):
                    if not isinstance(node, ast.ExceptHandler):
                        continue
                    if not (
                        node.type is not None
                        and isinstance(node.type, ast.Name)
                        and node.type.id == "ImportError"
                    ):
                        continue
                    has_none_assign = any(
                        isinstance(stmt, ast.Assign)
                        and any(isinstance(val, ast.Constant) and val.value is None for val in [stmt.value])
                        for stmt in node.body
                    )
                    if not has_none_assign:
                        continue
                    handler_line = node.lineno - 1
                    block_text = ""
                    end_line = min(handler_line + 20, len(source_lines))
                    for i in range(handler_line, end_line):
                        block_text += source_lines[i]
                    has_critical = (
                        "logger.critical" in block_text
                        or "_logger.critical" in block_text
                        or "guardian: allow-silent-swallow" in block_text
                    )
                    if not has_critical:
                        violations.append((str(py_file.relative_to(_ROOT)), node.lineno))
        return violations

    _BASELINE_CEILING = 37  # §29 non-growing debt: count at Plan 6 commit

    def test_ghost_import_swallowers_count_does_not_grow(self):
        """Assert ghost-import swallower count never exceeds the Plan-6 baseline.

        Fix violations by adding logger.critical() before the fallback assignment,
        or add '# guardian: allow-silent-swallow'. Decrease ceiling as debt clears.
        """
        violations = self._collect_ghost_swallowers()
        current_count = len(violations)
        print(f"ghost-import-swallower count: {current_count} (ceiling: {self._BASELINE_CEILING})")
        assert current_count <= self._BASELINE_CEILING, (
            f"Ghost import swallowers GREW: {current_count} > "
            f"{self._BASELINE_CEILING} (baseline). "
            f"New violations:\n  "
            + "\n  ".join(f"{f}:{ln}" for f, ln in sorted(violations)[self._BASELINE_CEILING :])
        )


# ---------------------------------------------------------------------------
# Invariant 4: MetaLearningChangePackage uses .create() factory
# ---------------------------------------------------------------------------


class TestMetaLearningChangePackageFactory:
    _BUS_HOOK = _ROOT / "system_learning/ports/meta_outcome_bus_hook.py"

    def _find_direct_constructions(self) -> list[int]:
        """Find MetaLearningChangePackage(...) calls that are NOT .create(...)."""
        if not self._BUS_HOOK.exists():
            return []
        tree = _parse(self._BUS_HOOK)
        violations = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            if isinstance(func, ast.Name) and func.id == "MetaLearningChangePackage":
                violations.append(node.lineno)
            if isinstance(func, ast.Attribute) and func.attr == "MetaLearningChangePackage":
                violations.append(node.lineno)
        return violations

    def test_meta_learning_change_package_no_direct_construction(self):
        violations = self._find_direct_constructions()
        assert violations == [], (
            f"meta_outcome_bus_hook.py directly constructs MetaLearningChangePackage "
            f"at lines {violations}; use MetaLearningChangePackage.create() instead"
        )


# ---------------------------------------------------------------------------
# Invariant 5: Response capture in healing_provider_adapters.py
# ---------------------------------------------------------------------------


class TestHealingAdapterResponseCapture:
    _ADAPTERS = _ROOT / "agentic_core/L2_execution/healers/healing_provider_adapters.py"

    def _find_uncaptured_completions_create(self) -> list[int]:
        """Find completions.create() calls not assigned to a variable."""
        if not self._ADAPTERS.exists():
            return []
        tree = _parse(self._ADAPTERS)
        violations = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.Expr):
                continue
            val = node.value
            if not isinstance(val, ast.Call):
                continue
            func = val.func
            if not isinstance(func, ast.Attribute):
                continue
            if func.attr in ("create", "generate") and isinstance(func.value, ast.Attribute):
                parent = func.value
                if isinstance(parent, ast.Attribute) and parent.attr in (
                    "completions",
                    "messages",
                ):
                    violations.append(node.lineno)
        return violations

    def test_adapter_completions_create_is_captured(self):
        violations = self._find_uncaptured_completions_create()
        assert violations == [], (
            f"healing_provider_adapters.py discards API response at lines {violations}; "
            f"assign completions.create() / messages.create() return value"
        )
