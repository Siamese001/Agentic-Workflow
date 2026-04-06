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
    """Enhanced config detection using AST analysis.

    Detects:
    - Classes with config-like attributes
    - Constant definitions
    - Configuration loading patterns
    - Settings management
    """
    # Check filename patterns
    if any(indicator in path.name.lower() for indicator in indicators):
        return True

    config_attributes = 0
    constant_assignments = 0
    config_methods = 0

    for node in ast.walk(tree):
        # Check classes
        if isinstance(node, ast.ClassDef):
            # Check naming
            if any(node.name.endswith(suffix) for suffix in ("Config", "Settings", "Options")):
                return True

            # Check for config-like attributes
            for item in node.body:
                if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                    attr_name = item.target.id.lower()
                    if attr_name in patterns:
                        config_attributes += 1

                # Check for config methods
                elif isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef):
                    if item.name in ("load", "save", "configure", "get_setting", "from_env"):
                        config_methods += 1

        # Check module-level constants
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    if target.id.isupper() and len(target.id) > 1:
                        constant_assignments += 1

    # Determine if config based on patterns
    if config_attributes > 2 or constant_assignments > 3 or config_methods > 0:
        return True

    return False


def _detect_validator_patterns(
    tree: ast.AST,
    path: Path,
    content: str,
    patterns: list[str],
) -> bool:
    """Enhanced validator detection using AST analysis.

    Detects:
    - Validation methods
    - Check functions
    - Verification patterns
    - Schema validation
    """
    # Check filename patterns (but exclude self)
    if path.name != "FileClassificationAgent.py":
        if any(pattern in path.name for pattern in patterns):
            return True

    validation_methods = 0
    check_functions = 0
    assert_usage = 0

    for node in ast.walk(tree):
        # Check classes
        if isinstance(node, ast.ClassDef):
            if any(pattern in node.name for pattern in patterns):
                return True

            # Check for validation methods
            for item in node.body:
                if isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef):
                    method_name = item.name.lower()
                    if any(
                        word in method_name
                        for word in ("validate", "check", "verify", "ensure", "assert")
                    ):
                        validation_methods += 1

        # Check functions
        elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            func_name = node.name.lower()
            if any(word in func_name for word in ("validate", "check", "verify", "ensure")):
                check_functions += 1

            # Check for assert statements
            for stmt in ast.walk(node):
                if isinstance(stmt, ast.Assert):
                    assert_usage += 1

    # CONSOLIDATED VALIDATOR HARDENING IN GUARDRAILS
    if "guardrails" in str(path).lower():
        validation_methods = sum(
            1
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and any(
                w in node.name.lower()
                for w in ("validate", "check", "verify", "ensure", "scrub", "sanitize")
            )
        )
        if validation_methods < 4:
            return False

    # Determine if validator based on patterns
    if validation_methods > 0 or check_functions > 0 or assert_usage > 2:
        return True

    return False


def _detect_orchestrator_patterns(
    tree: ast.AST, path: Path, content: str, primary_name: str
) -> bool:
    """Distinguish between L0 routers and L3 orchestrators based on behavioral patterns.

    Phase 2 hardened: inheritance signals, broader tokens, multi-class coordinator,
    relaxed threshold for exact suffix match.

    Returns:
        True if file exhibits orchestrator behavior, False if router or neither.
    """
    orchestrator_base_classes = {
        "WorkflowCoordinator",
        "Coordinator",
        "L3OrchestrationBase",
        "IOrchestratorProtocol",
    }
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for base in node.bases:
                base_name = ""
                if isinstance(base, ast.Name):
                    base_name = base.id
                elif isinstance(base, ast.Attribute):
                    base_name = base.attr
                if base_name in orchestrator_base_classes:
                    return True

    coordinator_class_count = sum(
        1
        for node in ast.walk(tree)
        if isinstance(node, ast.ClassDef) and node.name.endswith("Coordinator")
    )
    if coordinator_class_count >= 3:
        return True

    orchestrator_name_patterns = [
        "Orchestrator",
        "orchestrator",
        "orchestrate",
        "Coordinator",
        "Pipeline",
    ]
    has_orchestrator_name = any(p in primary_name for p in orchestrator_name_patterns)
    has_exact_suffix = primary_name.endswith(("Orchestrator", "Coordinator"))

    orchestrator_behavior_signals = [
        "run_pipeline",
        "_run_guardians",
        "_run_dispatcher",
        "_run_healers",
        "stage_1",
        "stage_2",
        "stage_3",
        "phase_1",
        "phase_2",
        "coordinate",
        "orchestrate",
        "workflow",
        "write_artifacts_dir",
        "intermediate_result",
        "aggregate_result",
        "apply_mode",
        "dry_run_mode",
        "execution_policy",
        "allow_mutation",
        "run_stages",
        "execute_workflow",
        "run_phases",
        "dispatch_to_agents",
        "agent_roster",
        "mission_context",
        "run_all_guardians",
        "run_healers",
    ]

    behavior_signal_count = sum(1 for signal in orchestrator_behavior_signals if signal in content)

    router_patterns = [
        "select_handler",
        "route_to",
        "dispatch_single",
        "thin_wrapper",
        "route_request",
        "get_handler",
        "resolve_route",
        "match_route",
        "dispatch_to",
        "forward_to",
    ]
    has_router_pattern = any(p in content for p in router_patterns)

    function_nodes = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    stage_functions = [
        f for f in function_nodes if any(stage in f.name.lower() for stage in ["stage", "phase", "step"])
    ]
    has_multi_stage_functions = len(stage_functions) >= 2

    pipeline_methods = [
        f
        for f in function_nodes
        if any(kw in f.name.lower() for kw in ["pipeline", "workflow", "orchestrate", "coordinate"])
    ]
    has_pipeline_method = len(pipeline_methods) > 0

    is_in_l0_scripts = "L0_routing" in path.parts and "scripts" in path.parts
    is_in_l3 = "L3_orchestration" in path.parts

    if is_in_l3 and has_orchestrator_name:
        return True

    if has_multi_stage_functions and behavior_signal_count >= 3:
        return True

    if has_pipeline_method and behavior_signal_count >= 2:
        return True

    if is_in_l0_scripts and has_orchestrator_name and behavior_signal_count >= 3:
        return True

    if has_router_pattern and not has_multi_stage_functions:
        return False

    if has_exact_suffix and behavior_signal_count >= 1:
        return True

    return has_orchestrator_name and behavior_signal_count >= 2


def _detect_enforcer_control_signal(tree: ast.AST, content: str) -> bool:
    """Detect control outcome signal for ENFORCER AND-gate.

    Returns True if file contains:
    - raise *Error inside validate_* or assert_*_allowed
    - OR function returning (False, "...") pattern
    """
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name.startswith(("validate_", "assert_")) or node.name.startswith("verify_"):
                for child in ast.walk(node):
                    if isinstance(child, ast.Raise):
                        return True
                    if isinstance(child, ast.Return) and isinstance(child.value, ast.Tuple):
                        if len(child.value.elts) >= 2:
                            first = child.value.elts[0]
                            if isinstance(first, ast.Constant) and first.value is False:
                                return True
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
    """AST-based content scoring to determine true file type by content analysis.

    Walks the AST and assigns weighted scores to each classification category
    based on actual code patterns, NOT filename suffixes.

    Scoring weights:
    - TYPES:     +10 per @dataclass, +10 per BaseModel, +10 per Enum, +15 per Protocol
    - CONFIG:    +5 per UPPER_CASE constant, +3 per settings dict pattern
    - AGENT:     +20 per class ending in 'Agent' or inheriting from *Agent
    - UTILITY:   +3 per standalone function (not a class method)
    - VALIDATOR: +5 per validate_/check_ function

    Args:
        path: File path to analyze

    Returns:
        Dict mapping category names to integer scores.
    """
    scores: dict[str, int] = {
        "TYPES": 0,
        "CONFIG": 0,
        "AGENT": 0,
        "UTILITY": 0,
        "VALIDATOR": 0,
    }

    try:
        content = path.read_text(encoding="utf-8")
        tree = ast.parse(content)
    except (SyntaxError, UnicodeDecodeError, OSError):
        return scores

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            # Agent indicators
            if node.name.endswith("Agent"):
                scores["AGENT"] += 20
            for base in node.bases:
                if isinstance(base, ast.Name) and "Agent" in base.id:
                    scores["AGENT"] += 20
                elif isinstance(base, ast.Attribute) and "Agent" in base.attr:
                    scores["AGENT"] += 20

            # Type indicators: @dataclass
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Name) and decorator.id == "dataclass":
                    scores["TYPES"] += 10
                elif isinstance(decorator, ast.Call):
                    if isinstance(decorator.func, ast.Name) and decorator.func.id == "dataclass":
                        scores["TYPES"] += 10

            # Type indicators: BaseModel, Enum, Protocol inheritance
            for base in node.bases:
                if isinstance(base, ast.Name):
                    if base.id == "BaseModel":
                        scores["TYPES"] += 10
                    elif base.id == "Enum":
                        scores["TYPES"] += 10
                    elif base.id == "Protocol":
                        scores["TYPES"] += 15
                elif isinstance(base, ast.Attribute):
                    if base.attr == "BaseModel":
                        scores["TYPES"] += 10
                    elif base.attr == "Enum":
                        scores["TYPES"] += 10
                    elif base.attr == "Protocol":
                        scores["TYPES"] += 15

        # Config indicators: UPPER_CASE constant assignments
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id.isupper() and len(target.id) > 1:
                    scores["CONFIG"] += 5

        # Utility indicators: standalone functions (module-level)
        elif isinstance(node, ast.FunctionDef) and not isinstance(node, ast.AsyncFunctionDef):
            # Validator indicators
            if node.name.startswith(("validate_", "check_", "verify_", "ensure_")):
                scores["VALIDATOR"] += 5
            else:
                scores["UTILITY"] += 3

        elif isinstance(node, ast.AsyncFunctionDef):
            if node.name.startswith(("validate_", "check_", "verify_", "ensure_")):
                scores["VALIDATOR"] += 5
            else:
                scores["UTILITY"] += 3

    return scores


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
    """Fuzzy matching for names and content patterns.

    Uses multiple strategies:
    - Exact name matching
    - Partial name matching
    - Content pattern matching (excluding comments)
    """
    if any(pattern in name for pattern in patterns):
        return True

    try:
        tree = ast.parse(content)
        content_lower = content.lower()

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
                if any(pattern.lower() in node.name.lower() for pattern in patterns):
                    return True

            elif isinstance(node, ast.Constant) and isinstance(node.value, str):
                if any(pattern.lower() in node.value.lower() for pattern in patterns):
                    if len(node.value) > 10:
                        return True

            elif isinstance(node, ast.Attribute):
                if any(pattern.lower() in node.attr.lower() for pattern in patterns):
                    return True

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
                if (
                    hasattr(node, "doc_string")
                    and node.doc_string
                    and any(pattern.lower() in node.doc_string.lower() for pattern in patterns)
                ):
                    return True

    except SyntaxError:
        content_lower = content.lower()
        for pattern in patterns:
            if pattern.lower() in content_lower:
                pattern_count = content_lower.count(pattern.lower())
                if pattern_count > 5:
                    return True

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
