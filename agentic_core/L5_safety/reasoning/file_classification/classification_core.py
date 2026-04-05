"""Pure classification analysis functions.

This module contains the core classification logic extracted from
FileClassificationAgent. Functions here should be pure or near-pure
with no side effects (no file moves, no import rewrites, no mutations).
"""

import ast
import logging
import re
from pathlib import Path
from typing import Literal

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    TESTS_DIR,
)
from agentic_core.L5_safety.config.structure_blueprint.classification import (
    CLASSIFICATION_SUFFIX_PATTERNS,
)
from agentic_core.L5_safety.reasoning.core_kernel.classification_kernel import FileType

from .models import ClassificationResult

logger = logging.getLogger(__name__)

# Critical files that are exempt from classification
_CRITICAL_IGNORES = frozenset(
    {
        "conftest.py",
        "__init__.py",
        "__main__.py",
        "setup.py",
        "tool_registry.py",
    },
)


def classify_file(path: Path) -> FileType:
    """
    Analyze file AST to determine architectural role with STRICT PRIORITY ORDERING.

    This is the main classification entrypoint. For now, it delegates to the
    original FileClassificationAgent implementation to maintain compatibility.

    TODO: Extract full pure implementation here.
    """
    # Temporary: delegate to original implementation
    from agentic_core.L5_safety.reasoning.FileClassificationAgent import FileClassificationHealerAgent

    # Create a temporary instance to call the method
    # Note: This is a transitional step - eventually this will be pure
    classifier = FileClassificationHealerAgent(project_root=path.parent)
    return classifier.classify_file(path)


def classify_file_with_signals(path: Path) -> ClassificationResult:
    """Classify a file and enrich the result with ADG behavioral signals.

    TODO: Extract full implementation.
    """
    from agentic_core.L5_safety.reasoning.FileClassificationAgent import FileClassificationHealerAgent

    classifier = FileClassificationHealerAgent(project_root=path.parent)
    return classifier.classify_file_with_signals(path)


def classify_file_with_confidence(path: Path) -> ClassificationResult:
    """Content-weighted classification with confidence scoring.

    TODO: Extract full implementation.
    """
    from agentic_core.L5_safety.reasoning.FileClassificationAgent import FileClassificationHealerAgent

    classifier = FileClassificationHealerAgent(project_root=path.parent)
    return classifier.classify_file_with_confidence(path)


# Helper functions to be extracted
# TODO: Extract these from FileClassificationAgent.py


def _detect_test_patterns(tree: ast.AST, path: Path) -> dict[str, bool]:
    """
    Enhanced test detection using AST analysis.

    Detects:
    - Classes inheriting from unittest.TestCase
    - pytest fixtures and test functions
    - Test methods (starting with test_)
    - Mock/patch usage
    """
    indicators = {"is_test": False}

    # Check for unittest imports
    has_unittest = False
    has_pytest = False
    test_methods = 0
    fixtures = 0

    for node in ast.walk(tree):
        # Check imports
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "unittest":
                    has_unittest = True
                elif alias.name == "pytest":
                    has_pytest = True
        elif isinstance(node, ast.ImportFrom):
            if node.module and ("unittest" in node.module or "pytest" in node.module):
                has_unittest = has_unittest or "unittest" in node.module
                has_pytest = has_pytest or "pytest" in node.module

        # Check classes
        elif isinstance(node, ast.ClassDef):
            # Check unittest.TestCase inheritance
            for base in node.bases:
                if isinstance(base, ast.Name) and base.id == "TestCase":
                    indicators["is_test"] = True
                elif isinstance(base, ast.Attribute) and base.attr == "TestCase":
                    indicators["is_test"] = True

            # Count test methods
            for item in node.body:
                if isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef):
                    if item.name.startswith("test_"):
                        test_methods += 1

        # Check functions
        elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            # Check for pytest fixtures
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Name) and decorator.id == "fixture":
                    fixtures += 1
                elif isinstance(decorator, ast.Attribute) and decorator.attr == "fixture":
                    fixtures += 1

            # Check test functions at module level
            if node.name.startswith("test_"):
                indicators["is_test"] = True

    # Determine if test file based on patterns
    if has_unittest or has_pytest or test_methods > 0 or fixtures > 0:
        indicators["is_test"] = True

    return indicators


def _detect_script_patterns(tree: ast.AST, path: Path) -> dict[str, bool]:
    """
    Enhanced script detection using AST analysis.

    Detects:
    - if __name__ == "__main__" patterns
    - argparse or click usage
    - Direct execution patterns
    - Script-like function names (main, run, execute, start)
    """
    indicators = {"is_script": False}

    has_main_guard = False
    has_argparse = False
    has_click = False
    script_functions = 0

    for node in ast.walk(tree):
        # Check imports
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in ("argparse", "click", "sys", "os"):
                    if alias.name == "argparse":
                        has_argparse = True
                    elif alias.name == "click":
                        has_click = True

        # Check for if __name__ == "__main__"
        elif isinstance(node, ast.If):
            if (
                isinstance(node.test, ast.Compare)
                and len(node.test.ops) == 1
                and isinstance(node.test.ops[0], ast.Eq)
            ):
                left = node.test.left
                comparators = node.test.comparators
                if (
                    isinstance(left, ast.Name)
                    and left.id == "__name__"
                    and len(comparators) == 1
                    and isinstance(comparators[0], ast.Constant)
                    and comparators[0].value == "__main__"
                ):
                    has_main_guard = True

        # Check functions
        elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            script_names = {"main", "run", "execute", "start", "cli", "script"}
            if node.name in script_names:
                script_functions += 1

    # Determine if script based on patterns
    if has_main_guard or has_argparse or has_click or script_functions > 0:
        indicators["is_script"] = True

    return indicators


def _detect_type_patterns(tree: ast.AST, path: Path) -> dict[str, bool]:
    """
    Enhanced type collection detection using AST analysis.

    Detects:
    - Multiple enum classes
    - TypeVar usage
    - Protocol definitions
    - Abstract base classes
    - Data model patterns
    """
    indicators = {"is_types": False}

    enum_count = 0
    typevar_count = 0
    protocol_count = 0
    dataclass_count = 0
    model_count = 0

    for node in ast.walk(tree):
        # Check classes
        if isinstance(node, ast.ClassDef):
            # Check enum inheritance
            for base in node.bases:
                if isinstance(base, ast.Name):
                    if base.id == "Enum":
                        enum_count += 1
                    elif base.id == "Protocol":
                        protocol_count += 1
                    elif base.id in ("ABC", "abstractmethod"):
                        indicators["is_types"] = True
                elif isinstance(base, ast.Attribute):
                    if base.attr == "Enum":
                        enum_count += 1
                    elif base.attr == "Protocol":
                        protocol_count += 1

            # Check dataclass decorators
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Name) and decorator.id == "dataclass":
                    dataclass_count += 1
                elif isinstance(decorator, ast.Call):
                    if isinstance(decorator.func, ast.Name) and decorator.func.id == "dataclass":
                        dataclass_count += 1

            # Check model naming patterns
            if any(suffix in node.name for suffix in ("Model", "Schema", "DTO", "Type")):
                model_count += 1

        # Check TypeVar usage
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and "TypeVar" in str(node.value):
                    typevar_count += 1

    # Determine if type collection based on patterns
    if (
        enum_count > 1
        or typevar_count > 0
        or protocol_count > 0
        or dataclass_count > 1
        or model_count > 1
    ):
        indicators["is_types"] = True

    return indicators


def _detect_config_patterns(
    tree: ast.AST,
    path: Path,
    content: str,
    indicators: list[str],
    patterns: set[str],
) -> bool:
    """Detect configuration module patterns.

    TODO: Extract implementation.
    """
    return False


def _detect_validator_patterns(
    tree: ast.AST,
    path: Path,
    content: str,
    patterns: list[str],
) -> bool:
    """Detect validator patterns.

    TODO: Extract implementation.
    """
    return False


def _detect_orchestrator_patterns(
    tree: ast.AST,
    path: Path,
    content: str,
    primary_name: str,
) -> bool:
    """Detect orchestration patterns.

    TODO: Extract implementation.
    """
    return False


def _detect_enforcer_control_signal(tree: ast.AST, content: str) -> bool:
    """Detect enforcer control signal patterns.

    TODO: Extract implementation.
    """
    return False


def _detect_filename_tag_conflicts(path: Path) -> set[str]:
    """
    Detect conflicting classification tags in a filename.

    Uses COMPOUND_SUFFIX_CONFLICTS from blueprint config to match specific
    compound suffix patterns (e.g., "_agent_types", "_config_script") that
    indicate two classification tags in one filename.

    Returns empty set if clean, or the set of conflicting tags if found.
    Does NOT flag domain words (e.g., "agents" in "find_misnamed_agents_util.py").
    """
    from agentic_core.L5_safety.config.structure_blueprint.classification import (
        COMPOUND_SUFFIX_CONFLICTS,
    )

    stem = path.stem  # filename without .py
    detected_tags: set[str] = set()

    for pattern, tag_a, tag_b, _example in COMPOUND_SUFFIX_CONFLICTS:
        if re.search(pattern, stem):
            detected_tags.add(tag_a)
            detected_tags.add(tag_b)
            return detected_tags

    return set()


def _compute_content_scores(path: Path) -> dict[str, int]:
    """Compute content-based classification scores.

    TODO: Extract implementation.
    """
    return {}


def _compute_layer_affinity(path: Path) -> dict[str, float]:
    """
    Compute semantic layer affinity scores using AST analysis.

    Analyzes:
    1. Module/class docstrings for layer keywords
    2. Class names for domain indicators
    3. Method names for behavioral patterns
    4. Import targets for dependency affinity

    Returns:
        Dict mapping layer names (L0-L6) to affinity scores (0.0-1.0).
    """
    from agentic_core.L0_routing.config import (
        LAYER_KEYWORD_AFFINITY,
    )

    scores: dict[str, float] = dict.fromkeys(LAYER_KEYWORD_AFFINITY, 0.0)

    try:
        content = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(content)
    except (SyntaxError, OSError):
        return scores

    # Combine all text signals: module docstring + class names + method names + docstrings
    text_signals: list[str] = []

    # Module docstring
    module_doc = ast.get_docstring(tree)
    if module_doc:
        text_signals.append(module_doc.lower())

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            text_signals.append(node.name.lower())
            class_doc = ast.get_docstring(node)
            if class_doc:
                text_signals.append(class_doc.lower())

        elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            text_signals.append(node.name.lower())

        elif isinstance(node, ast.ImportFrom) and node.module:
            text_signals.append(node.module.lower())

    combined_text = " ".join(text_signals)

    # Score each layer based on keyword matches
    total_hits = 0
    for layer, keywords in LAYER_KEYWORD_AFFINITY.items():
        hits = 0
        for keyword in keywords:
            # Use word boundary-ish matching (keyword appears as substring)
            count = combined_text.count(keyword.lower())
            hits += count
        scores[layer] = float(hits)
        total_hits += hits

    # Normalize to 0.0-1.0
    if total_hits > 0:
        for layer in scores:
            scores[layer] = round(scores[layer] / total_hits, 3)

    return scores


def _load_adg_behavioral_profile(path: Path) -> tuple[float, list[str]]:
    """Load ADG behavioral profile for a file.

    TODO: Extract implementation.
    """
    return (0.5, [])


def _fuzzy_match_name_or_content(
    name: str, path: Path, content: str, patterns: list[str]
) -> bool:
    """Fuzzy match patterns against name or content.

    TODO: Extract implementation.
    """
    return False


def _is_true_agent(node: ast.ClassDef, file_path: Path) -> bool:
    """Check if class is a true agent.

    TODO: Extract implementation.
    """
    return False


def _is_service_class(node: ast.ClassDef, file_path: Path) -> bool:
    """Check if class is a service.

    TODO: Extract implementation.
    """
    return False


def _is_service_singleton(node: ast.ClassDef, class_name: str) -> bool:
    """Check if class is a service singleton.

    TODO: Extract implementation.
    """
    return False


def _is_factory_class(node: ast.ClassDef) -> bool:
    """Check if class is a factory.

    TODO: Extract implementation.
    """
    return False


def _is_async_agent(node: ast.ClassDef, file_path: Path) -> bool:
    """Check if class is an async agent.

    TODO: Extract implementation.
    """
    return False


def _is_adapter_class(node: ast.ClassDef) -> bool:
    """Check if class is an adapter.

    TODO: Extract implementation.
    """
    return False


def _is_config_class(node: ast.ClassDef, file_path: Path) -> bool:
    """Check if class is a config.

    TODO: Extract implementation.
    """
    return False


def _is_model_class(node: ast.ClassDef) -> bool:
    """Check if class is a model.

    TODO: Extract implementation.
    """
    return False


def _is_repository_class(node: ast.ClassDef) -> bool:
    """Check if class is a repository.

    TODO: Extract implementation.
    """
    return False
