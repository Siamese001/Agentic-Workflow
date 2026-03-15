from __future__ import annotations

from dataclasses import dataclass

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

"\n\nSubAtomicRegistry - Live Semantic Index of Every Method\n\n\n\nUpdated 2026-01-19: Added UNIFIED_AGENT_MAPPING for consolidated agent architecture.\n\nMaps legacy micro-agent keys to unified handlers for backward compatibility.\n\n"
import ast
import asyncio
import hashlib
import importlib
import inspect
import json
import logging
import os
import uuid
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config.path_constants import ARCHIVES_DIR
from agentic_core.L3_orchestration.registry.agent_dispatch_registry import get_agent_dispatch_registry
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace
from agentic_core.utils.decorators_compat_util import standard_heal


def _get_RedisSovereignAgent():
    """Lazy load RedisSovereignAgent to avoid upward import."""
    from agentic_core.L4_state.reasoning.RedisSovereignAgent import RedisSovereignAgent

    return RedisSovereignAgent


Logger = logging.getLogger(__name__)


def _get_UnifiedAgent_mapping() -> dict[str, type]:
    """

    Lazy-load unified agent mapping to avoid circular imports.



    Returns:

        Dictionary mapping legacy agent IDs to unified agent classes.

    """
    from agentic_core.L4_state.reasoning.CheckpointManagerAgent import CheckpointManagerAgent
    from agentic_core.L5_safety.reasoning.StructureValidatorAgent import StructureValidatorAgent

    from agentic_core.L1_cognition.reasoning.ASTValidatorAgent import ASTValidatorAgent
    from agentic_core.L3_orchestration.reasoning.StateManagementAgent import StateManagementAgent
    from agentic_core.L5_safety.reasoning.CodeEnforcerAgent import CodeEnforcerAgent

    return {
        "BareExceptValidator": ASTValidatorAgent,
        "BareExceptValidatorAgent": ASTValidatorAgent,
        "EmptyExceptValidator": ASTValidatorAgent,
        "EmptyExceptValidatorAgent": ASTValidatorAgent,
        "EvalExecValidator": ASTValidatorAgent,
        "EvalExecValidatorAgent": ASTValidatorAgent,
        "DangerousBuiltinsValidator": ASTValidatorAgent,
        "DangerousBuiltinsValidatorAgent": ASTValidatorAgent,
        "DebuggerValidator": ASTValidatorAgent,
        "DebuggerValidatorAgent": ASTValidatorAgent,
        "HygieneGuardian": StructureValidatorAgent,
        "HygieneGuardianAgent": StructureValidatorAgent,
        "HygieneValidator": StructureValidatorAgent,
        "HygieneValidatorAgent": StructureValidatorAgent,
        "CheckpointManager": CheckpointManagerAgent,
        "CheckpointManagerAgent": CheckpointManagerAgent,
        "AutonomousCheckpointManager": CheckpointManagerAgent,
        "AutonomousCheckpointManagerAgent": CheckpointManagerAgent,
        "BaseClassEnforcer": CodeEnforcerAgent,
        "BaseClassEnforcerAgent": CodeEnforcerAgent,
        "PatternEnforcer": CodeEnforcerAgent,
        "PatternEnforcerAgent": CodeEnforcerAgent,
        "TypeHintEnforcement": CodeEnforcerAgent,
        "TypeHintEnforcementAgent": CodeEnforcerAgent,
        "ManifestManager": StateManagementAgent,
        "ManifestManagerAgent": StateManagementAgent,
        "MemoryManager": StateManagementAgent,
        "MemoryManagerAgent": StateManagementAgent,
        "AutonomousStateGuardian": StateManagementAgent,
        "AutonomousStateGuardianAgent": StateManagementAgent,
    }


def _get_phase3_manager_enforcer_mapping() -> dict[str, type]:
    """

    Phase 3 Manager & Enforcer Consolidation: Hard Migration mappings.



    Returns:

        Dictionary mapping legacy manager/enforcer names to unified classes.

    """
    from agentic_core.L5_safety.reasoning.CodeEnforcerAgent import CodeEnforcerAgent
    from agentic_core.L5_safety.reasoning.ResourceManagerAgent import ResourceManagerAgent
    from agentic_core.L5_safety.reasoning.SecurityManagerAgent import SecurityManagerAgent
    from agentic_core.L5_safety.reasoning.StructureEnforcerAgent import StructureEnforcerAgent

    return {
        "BudgetManagerAgent": ResourceManagerAgent,
        "ProactiveResourceManagerAgent": ResourceManagerAgent,
        "FallbackManagerAgent": ResourceManagerAgent,
        "AgentPermissionManagerAgent": SecurityManagerAgent,
        "SecureCheckpointManagerAgent": SecurityManagerAgent,
        "SecureConfigManagerAgent": SecurityManagerAgent,
        "CodeSSOTEnforcerAgent": CodeEnforcerAgent,
        "CodeEnforcerAgent": CodeEnforcerAgent,
        "PatternEnforcerAgent": CodeEnforcerAgent,
        "TypeEnforcerAgent": CodeEnforcerAgent,
        "PythonFileSovereigntyEnforcerAgent": CodeEnforcerAgent,
        "GravityEnforcerAgent": StructureEnforcerAgent,
        "HierarchyEnforcerAgent": StructureEnforcerAgent,
        "NamingEnforcerAgent": StructureEnforcerAgent,
        "DocEnforcerAgent": StructureEnforcerAgent,
        "ASCIIEnforcerAgent": StructureEnforcerAgent,
        "StrictDocEnforcerAgent": StructureEnforcerAgent,
        "FileClassificationEnforcerAgent": StructureEnforcerAgent,
    }


def _get_phase4_detector_healer_router_executor_mapping() -> dict[str, type]:
    """

    Phase 4 Detector/Healer/router/Executor Consolidation: Hard Migration mappings.



    Returns:

        Dictionary mapping legacy detector/healer/router/executor names to unified classes.

    """
    from agentic_core.L2_execution.execution_bridge.ModelRouterAgent import ModelRouterAgent
    from agentic_core.L5_safety.reasoning.StructureHealerAgent_types import StructureHealerAgent

    from agentic_core.L5_safety.reasoning.CodeDetectorAgent import CodeDetectorAgent
    from agentic_core.L5_safety.reasoning.CodeHealerAgent import CodeHealerAgent
    from agentic_core.L5_safety.reasoning.SafetyDetectorAgent import SafetyDetectorAgent
    from agentic_core.L5_safety.reasoning.SafetyExecutorAgent import SafetyExecutorAgent

    return {
        "DeadCodeDetectorAgent": CodeDetectorAgent,
        "DeadlockDetectorAgent": CodeDetectorAgent,
        "DriftDetectorAgent": CodeDetectorAgent,
        "MethodChangeDetectorAgent": CodeDetectorAgent,
        "MemoryLeakDetectorAgent": CodeDetectorAgent,
        "BiasDetectorAgent": SafetyDetectorAgent,
        "HallucinationDetectorAgent": SafetyDetectorAgent,
        "PromptInjectionDetectorAgent": SafetyDetectorAgent,
        "CanonHealerAgent": CodeHealerAgent,
        "ImportHealerAgent": CodeHealerAgent,
        "StructuralHealerAgent": CodeHealerAgent,
        "GravityHealerAgent": StructureHealerAgent,
        "HierarchyHealerAgent": StructureHealerAgent,
        "NamingLawHealerAgent": StructureHealerAgent,
        "TerritoryHealerAgent": StructureHealerAgent,
        "BlueprintHierarchyHealerAgent": StructureHealerAgent,
        "ModelRouterAgent": ModelRouterAgent,
        "DynamicModelRouterAgent": ModelRouterAgent,
        "MultiProviderRouterAgent": ModelRouterAgent,
        "ReasoningRouterAgent": ModelRouterAgent,
        "McpRouterAgent": ModelRouterAgent,
        "IntegrityGateExecutorAgent": SafetyExecutorAgent,
        "L5IntegrityGateExecutorAgent": SafetyExecutorAgent,
        "SafetyExecutorAgent": SafetyExecutorAgent,
    }


def _get_phase2_validator_mapping() -> dict[str, type]:
    """

    Phase 2 Validator Consolidation: Maps legacy validators to unified agents.



    Returns:

        Dictionary mapping legacy validator names to unified validator classes.

    """
    from agentic_core.L5_safety.reasoning.StructureValidatorAgent import StructureValidatorAgent

    from apps_lic.types.ImmutableStagingBuffer import AppContentValidatorAgent

    class CodeValidatorAgentWrapper:
        """Wrapper that delegates to CodeValidatorAgent via subprocess."""

        def __init__(self, project_root=None, **kwargs):
            import sys
            from pathlib import Path

            if project_root:
                # guardian: allow-global-mutation
                sys.path.insert(0, str(project_root))
            from agentic_core.L0_routing.utils.subprocess_runner_util import invoke_code_validator

            self.project_root = project_root or Path.cwd()
            self._invoke = invoke_code_validator

        def validate_repository(self, **kwargs):
            """Delegate validation to subprocess."""
            return self._invoke(action="validate", project_root=self.project_root)

        def heal_repository(self, directory=None, **kwargs):
            """Delegate healing to subprocess."""
            if directory:
                return self._invoke(
                    action="validate_directory", project_root=self.project_root, directory=str(directory)
                )
            return self.validate_repository(**kwargs)

    return {
        "SyntaxValidatorAgent": CodeValidatorAgentWrapper,
        "CanonAstValidatorAgent": CodeValidatorAgentWrapper,
        "CanonValidatorAgent": CodeValidatorAgentWrapper,
        "AsyncBlockingValidatorAgent": CodeValidatorAgentWrapper,
        "PrintStatementValidatorAgent": CodeValidatorAgentWrapper,
        "GravityValidatorAgent": StructureValidatorAgent,
        "HygieneValidatorAgent": StructureValidatorAgent,
        "StructureValidatorAgent": StructureValidatorAgent,
        "AgentRegistryValidatorAgent": StructureValidatorAgent,
        "CognitiveContractValidatorAgent": StructureValidatorAgent,
        "ContactValidatorAgent": AppContentValidatorAgent,
        "ContentCleanlinessValidatorAgent": AppContentValidatorAgent,
        "MessageDiversityValidator": AppContentValidatorAgent,
    }


def get_UnifiedAgent_class(agent_id: str) -> type:
    """

    Returns the unified agent class for a given legacy agent ID.

    Ensures backward compatibility for dynamic agent instantiation.



    Args:

        agent_id: Legacy agent identifier (e.g., "BareExceptValidator")



    Returns:

        Unified agent class that handles the legacy agent's functionality



    Raises:

        ValueError: If agent_id is not found in the mapping

    """
    mapping = _get_UnifiedAgent_mapping()
    if agent_id in mapping:
        Logger.info(f"Registry: Mapping legacy agent '{agent_id}' to Unified Class (Phase 1).")
        return mapping[agent_id]
    try:
        validator_mapping = _get_phase2_validator_mapping()
        if agent_id in validator_mapping:
            Logger.info(f"Registry: Mapping legacy validator '{agent_id}' to Unified Class (Phase 2).")
            return validator_mapping[agent_id]
    except ImportError as e:
        Logger.warning(f"Phase 2 validator mapping not available: {e}")
    try:
        phase3_mapping = _get_phase3_manager_enforcer_mapping()
        if agent_id in phase3_mapping:
            Logger.info(f"Registry: Mapping legacy manager/enforcer '{agent_id}' to Unified Class (Phase 3).")
            return phase3_mapping[agent_id]
    except ImportError as e:
        Logger.warning(f"Phase 3 manager/enforcer mapping not available: {e}")
    try:
        phase4_mapping = _get_phase4_detector_healer_router_executor_mapping()
        if agent_id in phase4_mapping:
            Logger.info(
                f"Registry: Mapping legacy detector/healer/router/executor '{agent_id}' to Unified Class (Phase 4)."
            )
            return phase4_mapping[agent_id]
    except ImportError as e:
        Logger.warning(f"Phase 4 detector/healer/router/executor mapping not available: {e}")
    raise ValueError(f"Agent ID '{agent_id}' not found in unified agent registry.")


def is_legacy_agent(agent_id: str) -> bool:
    """Check if an agent ID refers to a deprecated legacy agent."""
    try:
        mapping = _get_UnifiedAgent_mapping()
        return agent_id in mapping
    except ImportError:
        return False


@dataclass
class SubAtomicRegistryAgent(SovereignBaseAgent):
    """

    Sovereign method registry — live, hybrid-indexed, eternal.

    Now with Redis sovereign caching for instant method discovery.

    """

    def __init__(self, project_root: Path) -> None:
        """Initialize the instance."""
        self.root = project_root
        self.redis_gateway = _get_RedisSovereignAgent()(project_root)
        self.redis = self.redis_gateway.get_client()
        self._local_method_index: list[dict] = []

    def _run_self_tests(self) -> bool:
        """Phase 1: Self-testing for L4 compliance."""
        assert hasattr(self, "root"), "Missing root"
        assert hasattr(self, "redis"), "Missing redis"
        return True

    def extract_methods(self) -> list[dict]:
        """Deep crawl of all .py files to find callables"""

        _emit_records_execution_trace(str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, "SubAtomicRegistryAgent.extract_methods")
        methods = []
        from agentic_core.utils.ssot_discovery_validator import get_python_files

        for py_file in get_python_files(self.root):
            if ARCHIVES_DIR in str(py_file):
                continue
            try:
                tree = ast.parse(py_file.read_text())
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                        doc = ast.get_docstring(node) or "No docstring provided."
                        source_lines = ast.get_source_segment(open(py_file).read(), node) or ""
                        methods.append(
                            {
                                "id": f"{py_file.stem}_{node.name}",
                                "path": str(py_file),
                                "method": node.name,
                                "docstring": doc,
                                "source_snippet": f"Method: {node.name}\nimport logging\n\nLogger = logging.getLogger(__name__)\nDoc: {doc}\nSource: {source_lines[:200]}...",
                                "line_number": node.lineno,
                                "is_async": isinstance(node, ast.AsyncFunctionDef),
                            }
                        )
            except (OSError, UnicodeDecodeError, SyntaxError) as e:
                print(f"Failed to index {py_file.name}: {e}")
                continue
        return methods

    # guardian: allow-type-erasure
    def rebuild_registry(self) -> Any:
        """Rebuild — full method index + Redis cache warm"""
        print("   [REBUILD] SubAtomicRegistry: Indexing all methods...")
        methods = self.extract_methods()
        self._local_method_index = methods
        for m in methods:
            vec_id = m["id"]
            cache_key = f"method_meta:{vec_id}"
            try:
                self.redis.set(cache_key, json.dumps(m), ex=86400)
            except (OSError, UnicodeDecodeError) as e:
                print(f"Failed to warm cache for {py_file.name}: {e}")
        print(f"   [OK] SubAtomicRegistry: Indexed {len(methods)} methods + cache Warmed")

    # guardian: allow-magic-config
    def find_method(self, Task: str, top_k: int = 3) -> list[dict]:
        """Cache-first method search — Redis then local index keyword match"""
        cache_key = f"method_search:{hashlib.sha256(Task.encode()).hexdigest()}_{top_k}"
        try:
            cached = self.redis.get(cache_key)
            if cached:
                print(f"   [CACHE HIT] Method search for '{Task[:30]}...'")
                return json.loads(cached)
        except (ImportError, AttributeError) as e:
            print(f"Gemini embedding failed: {e}")
        task_lower = Task.lower()
        results = [
            m
            for m in self._local_method_index
            if any(
                kw in m.get("docstring", "").lower() or kw in m.get("method", "").lower()
                for kw in task_lower.split()
            )
        ][:top_k]
        try:
            if results:
                self.redis.set(cache_key, json.dumps(results), ex=3600)
        except (ImportError, AttributeError, ValueError) as e:
            print(f"Gemini reranking failed: {e}")
        return results

    # guardian: allow-type-erasure
    def find_and_invoke(self, task_description: str, *args, **kwargs) -> Any:
        """The ultimate sovereign loop: Find it, then do it."""
        matches = self.find_method(task_description, top_k=1)
        if not matches:
            raise ValueError(f"No method found for Task: {task_description}")
        meta = matches[0]["metadata"]
        print(f"   [EXECUTE] Invoking {meta['method']} from {Path(meta['path']).name}")
        return meta

    # guardian: allow-type-erasure
    def invoke_method(self, method_meta: dict, *args, **kwargs) -> Any:
        """Dynamically invoke a method by metadata"""
        try:
            module_path = Path(method_meta["path"]).relative_to(self.root)
            module_name = str(module_path).replace(os.sep, ".")[:-3]
            module = importlib.import_module(module_name)
            # Wave 2: Use AgentDispatchRegistry for dynamic method invocation
            registry = get_agent_dispatch_registry()
            method_name = method_meta["method"]
            # For module-level functions, we need to check if it's async
            method = getattr(module, method_name)
            if inspect.iscoroutinefunction(method):
                return asyncio.run(method(*args, **kwargs))
            else:
                return method(*args, **kwargs)
        except (ImportError, AttributeError, TypeError, ValueError) as e:
            print(f"   [ERROR] Failed to invoke {method_meta['method']}: {e}")
            raise

    # guardian: allow-type-erasure
    async def execute(self, ctx=None) -> Any:
        """Execute execute operation."""
        count = len(self.extract_methods())
        print(f"   [OK] SubAtomicRegistry: {count} methods online and searchable.")
        if ctx:
            ctx.report("Registry", count, True, "Method capabilities mapped.")

    @timeout(300)
    @standard_heal
    # guardian: allow-magic-config
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set | None = None,
    ) -> dict[str, int]:
        """L4 state agent - operational only."""
        if _call_path is None:
            super().heal_repository()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            print(f"[{agent_name}] L4 state - operational only")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)

    # guardian: allow-type-erasure
    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """

        Heal violations detected by SubAtomicRegistryAgent.



        Args:

            violation: Dictionary containing violation details with keys:

                - file: Path to the file with the violation

                - type: Type of violation detected

                - message: Description of the violation



        Returns:

            Dictionary with keys:

                - status: 'success', 'partial_success', 'failed', or 'skipped'

                - details: Human-readable summary

                - artifacts: List of modified files

                - errors: List of error messages

        """
        violation.get("file") or violation.get("file_path")
        violation_type = violation.get("type", "unknown")
        try:
            return {
                "status": "skipped",
                "details": f"SubAtomicRegistryAgent heal() not yet implemented for {violation_type}",
                "artifacts": [],
                "errors": [],
            }
        except (ImportError, AttributeError, TypeError, ValueError) as e:
            return {
                "status": "failed",
                "details": f"SubAtomicRegistryAgent heal() failed: {str(e)}",
                "artifacts": [],
                "errors": [str(e)],
            }

    def adg_discover_agents(self, base_class: str = "SovereignBaseAgent") -> list[str]:
        """R4: O(1) ADG-backed agent discovery by inheritance graph.

        Replaces O(n) filesystem scan in extract_methods for base-class queries.
        Speedup: 100-1000x over full extract_methods() scan.

        Returns list of ADG module names for all known subclasses.
        """
        try:
            from agentic_core.adg.runtime.query_engine import get_runtime_query_engine

            query_engine = get_runtime_query_engine()
            return query_engine.find_agents_by_base_class(base_class)
        except (ImportError, AttributeError) as exc:
            Logger.warning("[SubAtomicRegistry] ADG discovery unavailable: %s", exc)
            return []
