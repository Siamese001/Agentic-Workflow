"""
Canon Keys Loader for L5 Meta-Learning System

Loads the 50 Canon Keys (golden patterns) into L1 cache (Redis) for
immediate availability during canon validation checks.
"""

import ast
import hashlib
import logging
from typing import Dict, Any

from schemas.canon_models import CanonEntry
from core.semantic_gatekeeper import SemanticGatekeeper

logger = logging.getLogger(__name__)


class CanonKeysLoader:
    """
    Loads and manages the 50 Canon Keys in the hybrid semantic cache.

    Canon Keys are golden patterns that are always available in L1 cache
    and marked with `is_canon_key: true` for special treatment.
    """

    # The 50 Canon Keys with their policy keys, descriptions, and example code
    CANON_KEYS = [
        {
            "policy_key": "canon:rule:00",
            "description": "Sovereign directory protection - never modify sovereign directories",
            "code": "# Sovereign directories are protected\ndef protect_sovereign_dirs():\n    sovereign = ['agentic_core', 'apps_lic', 'apps_rg', 'apps_shared', 'schemas', 'prompt_governance', 'observability', 'config', 'data', 'archives']\n    return sovereign",
            "pattern_type": "sovereign_protection",
            "risk_score": 100
        },
        {
            "policy_key": "canon:rule:01",
            "description": "Light Canon depth limit - max 3 levels for non-sovereign code",
            "code": "def check_depth(path):\n    parts = path.split('/')\n    depth = len(parts) - 1\n    return depth <= 3",
            "pattern_type": "depth_validation",
            "risk_score": 80
        },
        {
            "policy_key": "canon:rule:02",
            "description": "No global variable encapsulation without explicit consent",
            "code": "# Global variables require explicit consent\nGLOBAL_VARS = {}\n\ndef encapsulate_global(name, value, consent=False):\n    if not consent:\n        raise PermissionError(\"Global encapsulation requires consent\")\n    GLOBAL_VARS[name] = value",
            "pattern_type": "global_protection",
            "risk_score": 90
        },
        {
            "policy_key": "canon:rule:03",
            "description": "Preserve functional hierarchies in sovereign directories",
            "code": "def preserve_hierarchy(structure):\n    # Never flatten sovereign directory structures\n    if structure.is_sovereign:\n        return structure.original_hierarchy\n    return structure.optimized_hierarchy",
            "pattern_type": "hierarchy_preservation",
            "risk_score": 85
        },
        {
            "policy_key": "canon:rule:04",
            "description": "Zero-loss merge - never drop real .py for __init__.py",
            "code": "def merge_files(source, target):\n    if source.endswith('.py') and not source.endswith('__init__.py'):\n        # Never drop real Python files\n        raise ValueError(\"Cannot merge real .py file\")\n    return safe_merge(source, target)",
            "pattern_type": "merge_safety",
            "risk_score": 95
        },
        {
            "policy_key": "canon:rule:05",
            "description": "Subatomic perfection - all 50 keys must pass",
            "code": "def validate_all_keys(checks):\n    if len(checks) != 50:\n        raise ValueError(\"Missing Canon Keys\")\n    if any(not check for check in checks):\n        raise ValueError(\"Canon validation failed\")\n    return True",
            "pattern_type": "completeness_check",
            "risk_score": 100
        },
        {
            "policy_key": "canon:rule:06",
            "description": "Atomic operations - all or nothing",
            "code": "def atomic_operation(operations):\n    results = []\n    try:\n        for op in operations:\n            results.append(op.execute())\n        return results\n    except Exception as e:\n        # Rollback all operations\n        for op in reversed(operations):\n            op.rollback()\n        raise e",
            "pattern_type": "atomicity",
            "risk_score": 75
        },
        {
            "policy_key": "canon:rule:07",
            "description": "Immutable core - never modify core framework",
            "code": "def protect_core(core_module):\n    if core_module.is_core:\n        raise PermissionError(\"Core modules are immutable\")\n    return core_module",
            "pattern_type": "core_protection",
            "risk_score": 90
        },
        {
            "policy_key": "canon:rule:08",
            "description": "Preserve imports during refactoring",
            "code": "def refactor_with_imports(code):\n    imports = extract_imports(code)\n    refactored = refactor_body(code)\n    return restore_imports(refactored, imports)",
            "pattern_type": "import_preservation",
            "risk_score": 70
        },
        {
            "policy_key": "canon:rule:09",
            "description": "No circular dependencies",
            "code": "def check_circular_deps(module_graph):\n    if has_cycle(module_graph):\n        raise ValueError(\"Circular dependency detected\")\n    return True",
            "pattern_type": "dependency_check",
            "risk_score": 80
        },
        {
            "policy_key": "canon:rule:10",
            "description": "Preserve docstrings and comments",
            "code": "def preserve_documentation(node):\n    if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):\n        return node.docstring or \"\"\n    return \"\"",
            "pattern_type": "documentation_preservation",
            "risk_score": 60
        },
        {
            "policy_key": "canon:rule:11",
            "description": "Type annotations must be preserved",
            "code": "def preserve_types(annotation):\n    if annotation is None:\n        return \"Any\"\n    return annotation",
            "pattern_type": "type_preservation",
            "risk_score": 65
        },
        {
            "policy_key": "canon:rule:12",
            "description": "No breaking changes without version bump",
            "code": "def check_compatibility(changes, version):\n    if changes.has_breaking and not version.is_bumped:\n        raise ValueError(\"Breaking change requires version bump\")\n    return True",
            "pattern_type": "version_compatibility",
            "risk_score": 85
        },
        {
            "policy_key": "canon:rule:13",
            "description": "Preserve test coverage",
            "code": "def check_test_coverage(changes):\n    coverage = calculate_coverage(changes)\n    if coverage < 0.8:\n        raise ValueError(\"Insufficient test coverage\")\n    return True",
            "pattern_type": "test_coverage",
            "risk_score": 70
        },
        {
            "policy_key": "canon:rule:14",
            "description": "No hardcoded secrets",
            "code": "def check_secrets(code):\n    if contains_secret(code):\n        raise ValueError(\"Hardcoded secrets detected\")\n    return True",
            "pattern_type": "secret_protection",
            "risk_score": 95
        },
        {
            "policy_key": "canon:rule:15",
            "description": "Preserve error handling",
            "code": "def preserve_error_handling(node):\n    handlers = extract_handlers(node)\n    transformed = transform_node(node)\n    return restore_handlers(transformed, handlers)",
            "pattern_type": "error_preservation",
            "risk_score": 75
        },
        {
            "policy_key": "canon:rule:16",
            "description": "No infinite recursion",
            "code": "def check_recursion(call_graph):\n    if has_infinite_recursion(call_graph):\n        raise RecursionError(\"Infinite recursion detected\")\n    return True",
            "pattern_type": "recursion_check",
            "risk_score": 80
        },
        {
            "policy_key": "canon:rule:17",
            "description": "Preserve logging statements",
            "code": "def preserve_logging(node):\n    logs = extract_logging(node)\n    transformed = transform_node(node)\n    return restore_logging(transformed, logs)",
            "pattern_type": "logging_preservation",
            "risk_score": 50
        },
        {
            "policy_key": "canon:rule:18",
            "description": "No SQL injection vulnerabilities",
            "code": "def check_sql_injection(query):\n    if has_unsafe_params(query):\n        raise SecurityError(\"SQL injection vulnerability\")\n    return safe_query(query)",
            "pattern_type": "sql_injection_protection",
            "risk_score": 100
        },
        {
            "policy_key": "canon:rule:19",
            "description": "Preserve configuration values",
            "code": "def preserve_config(config):\n    # Never modify configuration without explicit request\n    if not config.explicitly_requested:\n        return config.original\n    return config",
            "pattern_type": "config_preservation",
            "risk_score": 70
        },
        {
            "policy_key": "canon:rule:20",
            "description": "No memory leaks in transformations",
            "code": "def check_memory_leaks(transformation):\n    if has_leak(transformation):\n        raise MemoryError(\"Memory leak detected\")\n    return transformation",
            "pattern_type": "memory_safety",
            "risk_score": 85
        },
        {
            "policy_key": "canon:rule:21",
            "description": "Preserve async/await semantics",
            "code": "def preserve_async(node):\n    if node.is_async:\n        return transform_async(node)\n    return node",
            "pattern_type": "async_preservation",
            "risk_score": 75
        },
        {
            "policy_key": "canon:rule:22",
            "description": "No race conditions in concurrent code",
            "code": "def check_race_conditions(code):\n    if has_race_condition(code):\n        raise ConcurrencyError(\"Race condition detected\")\n    return safe_concurrent_code(code)",
            "pattern_type": "concurrency_safety",
            "risk_score": 90
        },
        {
            "policy_key": "canon:rule:23",
            "description": "Preserve function signatures",
            "code": "def preserve_signature(func):\n    sig = inspect.signature(func)\n    transformed = transform_body(func)\n    return restore_signature(transformed, sig)",
            "pattern_type": "signature_preservation",
            "risk_score": 80
        },
        {
            "policy_key": "canon:rule:24",
            "description": "No dead code elimination without consent",
            "code": "def eliminate_dead_code(code, consent=False):\n    if not consent:\n        return code  # Preserve without consent\n    return remove_unreachable(code)",
            "pattern_type": "dead_code_policy",
            "risk_score": 65
        },
        {
            "policy_key": "canon:rule:25",
            "description": "Preserve class inheritance",
            "code": "def preserve_inheritance(cls):\n    bases = cls.__bases__\n    transformed = transform_class(cls)\n    return transformed.with_bases(bases)",
            "pattern_type": "inheritance_preservation",
            "risk_score": 75
        },
        {
            "policy_key": "canon:rule:26",
            "description": "No breaking API changes",
            "code": "def check_api_compatibility(old_api, new_api):\n    if not is_compatible(old_api, new_api):\n        raise APIError(\"Breaking API change detected\")\n    return True",
            "pattern_type": "api_compatibility",
            "risk_score": 90
        },
        {
            "policy_key": "canon:rule:27",
            "description": "Preserve environment variables",
            "code": "def preserve_env_vars(code):\n    env_vars = extract_env_vars(code)\n    transformed = transform_code(code)\n    return restore_env_vars(transformed, env_vars)",
            "pattern_type": "env_preservation",
            "risk_score": 70
        },
        {
            "policy_key": "canon:rule:28",
            "description": "No hardcoded paths",
            "code": "def check_hardcoded_paths(code):\n    if has_hardcoded_path(code):\n        raise ValueError(\"Hardcoded path detected\")\n    return code",
            "pattern_type": "path_safety",
            "risk_score": 80
        },
        {
            "policy_key": "canon:rule:29",
            "description": "Preserve metadata decorators",
            "code": "def preserve_decorators(node):\n    decorators = node.decorator_list\n    transformed = transform_node(node)\n    transformed.decorator_list = decorators\n    return transformed",
            "pattern_type": "decorator_preservation",
            "risk_score": 60
        },
        {
            "policy_key": "canon:rule:30",
            "description": "No buffer overflows",
            "code": "def check_buffer_overflow(operation):\n    if exceeds_buffer(operation):\n        raise BufferError(\"Buffer overflow risk\")\n    return safe_operation(operation)",
            "pattern_type": "buffer_safety",
            "risk_score": 95
        },
        {
            "policy_key": "canon:rule:31",
            "description": "Preserve generator functions",
            "code": "def preserve_generator(func):\n    if is_generator(func):\n        return transform_generator(func)\n    return func",
            "pattern_type": "generator_preservation",
            "risk_score": 70
        },
        {
            "policy_key": "canon:rule:32",
            "description": "No privilege escalation",
            "code": "def check_privileges(operation):\n    if escalates_privileges(operation):\n        raise SecurityError(\"Privilege escalation detected\")\n    return operation",
            "pattern_type": "privilege_safety",
            "risk_score": 100
        },
        {
            "policy_key": "canon:rule:33",
            "description": "Preserve context managers",
            "code": "def preserve_context_manager(node):\n    if is_context_manager(node):\n        return transform_context_manager(node)\n    return node",
            "pattern_type": "context_preservation",
            "risk_score": 65
        },
        {
            "policy_key": "canon:rule:34",
            "description": "No resource leaks",
            "code": "def check_resource_leaks(code):\n    if has_resource_leak(code):\n        raise ResourceError(\"Resource leak detected\")\n    return code",
            "pattern_type": "resource_safety",
            "risk_score": 85
        },
        {
            "policy_key": "canon:rule:35",
            "description": "Preserve exception hierarchies",
            "code": "def preserve_exceptions(exc):\n    bases = exc.__bases__\n    transformed = transform_exception(exc)\n    return transformed.with_bases(bases)",
            "pattern_type": "exception_preservation",
            "risk_score": 75
        },
        {
            "policy_key": "canon:rule:36",
            "description": "No timing attacks",
            "code": "def check_timing_attack(code):\n    if has_timing_vulnerability(code):\n        raise SecurityError(\"Timing attack vulnerability\")\n    return safe_code(code)",
            "pattern_type": "timing_safety",
            "risk_score": 90
        },
        {
            "policy_key": "canon:rule:37",
            "description": "Preserve property decorators",
            "code": "def preserve_property(node):\n    if is_property(node):\n        return transform_property(node)\n    return node",
            "pattern_type": "property_preservation",
            "risk_score": 60
        },
        {
            "policy_key": "canon:rule:38",
            "description": "No data corruption",
            "code": "def check_data_integrity(data):\n    if is_corrupted(data):\n        raise DataError(\"Data corruption detected\")\n    return data",
            "pattern_type": "data_integrity",
            "risk_score": 95
        },
        {
            "policy_key": "canon:rule:39",
            "description": "Preserve lambda functions",
            "code": "def preserve_lambda(node):\n    if isinstance(node, ast.Lambda):\n        return transform_lambda(node)\n    return node",
            "pattern_type": "lambda_preservation",
            "risk_score": 55
        },
        {
            "policy_key": "canon:rule:40",
            "description": "No side effects in pure functions",
            "code": "def check_purity(func):\n    if has_side_effects(func):\n        raise PurityError(\"Side effects in pure function\")\n    return func",
            "pattern_type": "purity_check",
            "risk_score": 80
        },
        {
            "policy_key": "canon:rule:41",
            "description": "Light Canon: Validate directory structure",
            "code": "def validate_structure(path):\n    parts = Path(path).parts\n    return len(parts) <= 4  # Max 4 from root",
            "pattern_type": "structure_validation",
            "risk_score": 70
        },
        {
            "policy_key": "canon:rule:42",
            "description": "Light Canon: Check file naming conventions",
            "code": "def check_naming(filename):\n    if not filename.isidentifier():\n        raise ValueError(\"Invalid filename\")\n    return True",
            "pattern_type": "naming_convention",
            "risk_score": 50
        },
        {
            "policy_key": "canon:rule:43",
            "description": "Light Canon: Preserve module boundaries",
            "code": "def check_module_boundary(module):\n    if module.crosses_boundary:\n        raise ModuleError(\"Boundary violation\")\n    return True",
            "pattern_type": "module_boundary",
            "risk_score": 65
        },
        {
            "policy_key": "canon:rule:44",
            "description": "Light Canon: Validate imports",
            "code": "def validate_imports(imports):\n    for imp in imports:\n        if not is_valid_import(imp):\n            raise ImportError(f\"Invalid import: {imp}\")\n    return True",
            "pattern_type": "import_validation",
            "risk_score": 60
        },
        {
            "policy_key": "canon:rule:45",
            "description": "Light Canon: Check line length",
            "code": "def check_line_length(line):\n    if len(line) > 100:\n        raise ValueError(\"Line too long\")\n    return True",
            "pattern_type": "line_length_check",
            "risk_score": 40
        },
        {
            "policy_key": "canon:rule:46",
            "description": "Light Canon: Preserve whitespace",
            "code": "def preserve_whitespace(code):\n    # Preserve meaningful whitespace\n    return normalize_whitespace(code)",
            "pattern_type": "whitespace_preservation",
            "risk_score": 30
        },
        {
            "policy_key": "canon:rule:47",
            "description": "Light Canon: Check encoding",
            "code": "def check_encoding(file):\n    if file.encoding != 'utf-8':\n        raise UnicodeError(\"Invalid encoding\")\n    return True",
            "pattern_type": "encoding_check",
            "risk_score": 50
        },
        {
            "policy_key": "canon:rule:49",
            "description": "Universal Max 5 Levels from Root",
            "code": "def check_universal_depth(path):\n    parts = path.strip('/').split('/')\n    depth = len(parts) - 1\n    if depth > 5:\n        raise ValueError(f\"Path depth {depth} exceeds maximum of 5\")\n    return True",
            "pattern_type": "universal_depth",
            "risk_score": 100
        }
    ]

    def __init__(self, gatekeeper: SemanticGatekeeper):
        """Initialize the Canon Keys loader."""
        self.gatekeeper = gatekeeper
        logger.info("Canon Keys loader initialized")

    def load_all_keys(self) -> int:
        """
        Load all 50 Canon Keys into L1 cache.

        Returns:
            Number of keys loaded
        """
        logger.info("Loading 50 Canon Keys into L1 cache...")

        loaded_count = 0
        for key_data in self.CANON_KEYS:
            try:
                entry = self._create_canon_entry(key_data)
                self.gatekeeper._store_l1_entry(entry)
                loaded_count += 1
                logger.debug(f"Loaded Canon Key: {key_data['policy_key']}")
            except Exception as e:
                logger.error(
                    f"Failed to load Canon Key {key_data['policy_key']}: {e}")

        logger.info(f"Successfully loaded {loaded_count}/50 Canon Keys")
        return loaded_count

    def _create_canon_entry(self, key_data: Dict[str, Any]) -> CanonEntry:
        """Create a CanonEntry from key data."""
        # Parse AST
        try:
            tree = ast.parse(key_data["code"])
            ast_json = ast.dump(tree, include_attributes=True)
            ast_hash = hashlib.sha256(ast_json.encode()).hexdigest()
        except SyntaxError as e:
            logger.error(
                f"Syntax error in Canon Key {key_data['policy_key']}: {e}")
            ast_json = {"error": str(e)}
            ast_hash = hashlib.sha256(f"SYNTAX_ERROR:{e}".encode()).hexdigest()

        # Create entry with Canon Key flag
        entry = CanonEntry(
            vector=self.gatekeeper.embed_action(key_data["description"]),
            ast_json=ast_json,
            ast_hash=ast_hash,
            policy_key=key_data["policy_key"],
            failure_count=0,
            success_count=100,  # Canon Keys are highly successful
            latency_ms=1,  # Canon Keys are fast
            project_tag="canon",  # Special project tag
            metadata={
                "risk_score": key_data["risk_score"],
                "max_files_touched": 0,
                "pattern_type": key_data["pattern_type"],
                "agent_name": "CanonValidator",
                "validation_status": "validated",
                "is_canon_key": True,  # Mark as Canon Key
                "description": key_data["description"],
                "promoted_to_l2": "true"  # Canon Keys are always in L2
            }
        )

        return entry

    def verify_keys_loaded(self) -> bool:
        """
        Verify all 50 Canon Keys are loaded in L1 cache.

        Returns:
            True if all keys are loaded
        """
        # Search for Canon Keys in L1
        results = self.gatekeeper._search_l1_cache(
            query_vector=[0.0] * 768,  # Dummy vector
            threshold=0.0,
            max_results=100,
            include_canon_keys=True
        )

        canon_keys = [
            e for e in results.entries if e.metadata.get("is_canon_key")]

        if len(canon_keys) != 50:
            logger.warning(f"Expected 50 Canon Keys, found {len(canon_keys)}")
            return False

        logger.info("All 50 Canon Keys verified in L1 cache")
        return True


def load_canon_keys(gatekeeper: SemanticGatekeeper) -> bool:
    """
    Convenience function to load all Canon Keys.

    Args:
        gatekeeper: The SemanticGatekeeper instance

    Returns:
        True if successful
    """
    loader = CanonKeysLoader(gatekeeper)
    loaded = loader.load_all_keys()
    verified = loader.verify_keys_loaded()

    return loaded == 50 and verified

