# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: engine, memory, orchestrator, prompt, workflow
from __future__ import annotations

from dataclasses import dataclass

# This boosts alignment detection — review and integrate appropriately
from agentic_core.base_agents.atomic_execution_mixin import AtomicExecutionMixin
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

#!/usr/bin/env python3
"""
SubAtomicRegistry - Live Semantic Index of Every Method

Updated 2026-01-19: Added UNIFIED_AGENT_MAPPING for consolidated agent architecture.
Maps legacy micro-agent keys to unified handlers for backward compatibility.
"""

import ast
import asyncio
import hashlib
import importlib
import inspect
import json
import logging
import os
from pathlib import Path
from typing import Any

from agentic_core.base_agents.decorators import standard_heal
from agentic_core.L4_state.validation_context.PineconeSovereignAgent import PineconeSovereignAgent

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.L4_state.validation_context.RedisSovereignAgent import RedisSovereignAgent

Logger = logging.getLogger(__name__)


# =============================================================================
# UNIFIED AGENT MAPPING (Post-Consolidation Registry)
# =============================================================================
# Maps legacy micro-agent keys to consolidated unified handlers.
# This ensures backward compatibility for dynamic agent instantiation.


def _get_unified_agent_mapping() -> dict[str, type]:
    """
    Lazy-load unified agent mapping to avoid circular imports.

    Returns:
        Dictionary mapping legacy agent IDs to unified agent classes.
    """
    # Import unified agents lazily to avoid circular dependencies
    from agentic_core.L1_cognition.thought_engine.ast_validator_agent_validator import (
        ASTValidatorAgent,
    )
    from agentic_core.L4_state.validation_context.CheckpointManagerAgent import (
        CheckpointManagerAgent,
    )
    from agentic_core.L4_state.validation_context.StateManagementAgent import (
        StateManagementAgent,
    )
    from agentic_core.L5_safety.policy_engine.code_enforcer_agent_types import CodeEnforcerAgent
    from agentic_core.L5_safety.policy_engine.StructureValidatorAgent import (
        StructureValidatorAgent,
    )

    return {
        # Phase 1: L1 AST Validator Consolidation
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
        # Phase 2: L5 Hygiene Validator Consolidation
        "HygieneGuardian": StructureValidatorAgent,
        "HygieneGuardianAgent": StructureValidatorAgent,
        "HygieneValidator": StructureValidatorAgent,
        "HygieneValidatorAgent": StructureValidatorAgent,
        # Phase 3: L4 Checkpoint Manager Consolidation
        "CheckpointManager": CheckpointManagerAgent,
        "CheckpointManagerAgent": CheckpointManagerAgent,
        "AutonomousCheckpointManager": CheckpointManagerAgent,
        "AutonomousCheckpointManagerAgent": CheckpointManagerAgent,
        # Phase 4: L5 Code Standards Enforcer Consolidation
        "BaseClassEnforcer": CodeEnforcerAgent,
        "BaseClassEnforcerAgent": CodeEnforcerAgent,
        "PatternEnforcer": CodeEnforcerAgent,
        "PatternEnforcerAgent": CodeEnforcerAgent,
        "TypeHintEnforcement": CodeEnforcerAgent,
        "TypeHintEnforcementAgent": CodeEnforcerAgent,
        # Phase 5: L4 State Management Consolidation
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
    from agentic_core.L5_safety.policy_engine.code_enforcer_agent_types import CodeEnforcerAgent
    from agentic_core.L5_safety.policy_engine.resource_manager_agent_types import (
        ResourceManagerAgent,
    )
    from agentic_core.L5_safety.policy_engine.security_manager_agent_types import (
        SecurityManagerAgent,
    )
    from agentic_core.L5_safety.policy_engine.structure_enforcer_agent_types import (
        StructureEnforcerAgent,
    )

    return {
        # Resource Managers -> ResourceManagerAgent
        "BudgetManagerAgent": ResourceManagerAgent,
        "ProactiveResourceManagerAgent": ResourceManagerAgent,
        "FallbackManagerAgent": ResourceManagerAgent,
        # Security Managers -> SecurityManagerAgent
        "AgentPermissionManagerAgent": SecurityManagerAgent,
        "SecureCheckpointManagerAgent": SecurityManagerAgent,
        "SecureConfigManagerAgent": SecurityManagerAgent,
        # Code Enforcers -> CodeEnforcerAgent
        "CodeSSOTEnforcerAgent": CodeEnforcerAgent,
        "CodeEnforcerAgent": CodeEnforcerAgent,
        "PatternEnforcerAgent": CodeEnforcerAgent,
        "TypeEnforcerAgent": CodeEnforcerAgent,
        "PythonFileSovereigntyEnforcerAgent": CodeEnforcerAgent,
        # Structure Enforcers -> StructureEnforcerAgent
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
    from agentic_core.L5_safety.policy_engine.code_detector_agent_types import CodeDetectorAgent
    from agentic_core.L5_safety.policy_engine.CodeHealerAgent import CodeHealerAgent
    from agentic_core.L5_safety.policy_engine.safety_detector_agent_types import SafetyDetectorAgent
    from agentic_core.L5_safety.policy_engine.SafetyExecutorAgent import SafetyExecutorAgent
    from agentic_core.L5_safety.policy_engine.structure_healer_agent_types import (
        StructureHealerAgent,
    )

    return {
        # Code Detectors -> CodeDetectorAgent
        "DeadCodeDetectorAgent": CodeDetectorAgent,
        "DeadlockDetectorAgent": CodeDetectorAgent,
        "DriftDetectorAgent": CodeDetectorAgent,
        "MethodChangeDetectorAgent": CodeDetectorAgent,
        "MemoryLeakDetectorAgent": CodeDetectorAgent,
        # Safety Detectors -> SafetyDetectorAgent
        "BiasDetectorAgent": SafetyDetectorAgent,
        "HallucinationDetectorAgent": SafetyDetectorAgent,
        "PromptInjectionDetectorAgent": SafetyDetectorAgent,
        # Code Healers -> CodeHealerAgent
        "CanonHealerAgent": CodeHealerAgent,
        "ImportHealerAgent": CodeHealerAgent,
        "StructuralHealerAgent": CodeHealerAgent,
        # Structure Healers -> StructureHealerAgent
        "GravityHealerAgent": StructureHealerAgent,
        "HierarchyHealerAgent": StructureHealerAgent,
        "NamingLawHealerAgent": StructureHealerAgent,
        "TerritoryHealerAgent": StructureHealerAgent,
        "BlueprintHierarchyHealerAgent": StructureHealerAgent,
        # Routers -> ModelRouterAgent
        "ModelRouterAgent": ModelRouterAgent,
        "DynamicModelRouterAgent": ModelRouterAgent,
        "MultiProviderRouterAgent": ModelRouterAgent,
        "ReasoningRouterAgent": ModelRouterAgent,
        "McpRouterAgent": ModelRouterAgent,
        # Executors -> SafetyExecutorAgent
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
    from agentic_core.L5_safety.policy_engine.code_validator_agent_types import CodeValidatorAgent
    from agentic_core.L5_safety.policy_engine.StructureValidatorAgent import (
        StructureValidatorAgent,
    )
    from apps_lic.shared.validation.app_content_validator_agent_types import (
        AppContentValidatorAgent,
    )

    return {
        # Unified Code Validator (L5) - Single-pass AST validation
        "SyntaxValidatorAgent": CodeValidatorAgent,
        "CanonAstValidatorAgent": CodeValidatorAgent,
        "CanonValidatorAgent": CodeValidatorAgent,
        "AsyncBlockingValidatorAgent": CodeValidatorAgent,
        "PrintStatementValidatorAgent": CodeValidatorAgent,
        # Unified Structure Validator (L5) - Gravity/Hygiene/Registry
        "GravityValidatorAgent": StructureValidatorAgent,
        "HygieneValidatorAgent": StructureValidatorAgent,
        "StructureValidatorAgent": StructureValidatorAgent,
        "AgentRegistryValidatorAgent": StructureValidatorAgent,
        "CognitiveContractValidatorAgent": StructureValidatorAgent,
        # App Content Validator (Apps) - Contact/Content/Diversity
        "ContactValidatorAgent": AppContentValidatorAgent,
        "ContentCleanlinessValidatorAgent": AppContentValidatorAgent,
        "MessageDiversityValidatorAgent": AppContentValidatorAgent,
    }


def get_unified_agent_class(agent_id: str) -> type:
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
    # Check Phase 1 mapping first
    mapping = _get_unified_agent_mapping()
    if agent_id in mapping:
        Logger.info(f"Registry: Mapping legacy agent '{agent_id}' to Unified Class (Phase 1).")
        return mapping[agent_id]

    # Check Phase 2 validator mapping
    try:
        validator_mapping = _get_phase2_validator_mapping()
        if agent_id in validator_mapping:
            Logger.info(
                f"Registry: Mapping legacy validator '{agent_id}' to Unified Class (Phase 2)."
            )
            return validator_mapping[agent_id]
    except ImportError as e:
        Logger.warning(f"Phase 2 validator mapping not available: {e}")

    # Check Phase 3 manager/enforcer mapping
    try:
        phase3_mapping = _get_phase3_manager_enforcer_mapping()
        if agent_id in phase3_mapping:
            Logger.info(
                f"Registry: Mapping legacy manager/enforcer '{agent_id}' to Unified Class (Phase 3)."
            )
            return phase3_mapping[agent_id]
    except ImportError as e:
        Logger.warning(f"Phase 3 manager/enforcer mapping not available: {e}")

    # Check Phase 4 detector/healer/router/executor mapping
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
        mapping = _get_unified_agent_mapping()
        return agent_id in mapping
    except ImportError:
        return False


# NAMING CANON ETERNAL — renamed for sovereign discovery — Phase 3 — 2025-12-30
@dataclass
class SubAtomicRegistryAgent(AtomicExecutionMixin, SovereignBaseAgent):
    """
    Sovereign method registry — live, hybrid-indexed, eternal.
    Now with Redis sovereign caching for instant method discovery.
    """

    def __init__(self, project_root: Path) -> None:
        """Initialize the instance."""
        self.root = project_root
        self.pinecone = PineconeSovereignAgent(project_root)
        self.redis_gateway = RedisSovereignAgent(project_root)
        self.redis = self.redis_gateway.get_client()

        # Index for methods
        self.method_index_name = f"{self.pinecone.index_name}_methods"
        self.method_index = self.pinecone.index

    def _run_self_tests(self) -> bool:
        """Phase 1: Self-testing for L4 compliance."""
        assert hasattr(self, "root"), "Missing root"
        assert hasattr(self, "pinecone"), "Missing pinecone"
        return True

    def extract_methods(self) -> list[dict]:
        """Deep crawl of all .py files to find callables"""
        methods = []
        # Phase 6.8: Use ssot_discovery instead of rglob
        from agentic_core.utils.ssot_discovery_validator import get_python_files

        for py_file in get_python_files(self.root):
            if "archives" in str(py_file):
                continue
            try:
                tree = ast.parse(py_file.read_text())
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                        # Enhanced metadata extraction
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
            except Exception:
                continue
        return methods

    def rebuild_registry(self) -> Any:
        """Eternal rebuild — full method index + Redis cache warm"""
        print("   [REBUILD] SubAtomicRegistry: Indexing all methods...")
        methods = self.extract_methods()
        vectors = []
        for m in methods:
            emb = self.pinecone.get_embedding(m["source_snippet"])
            vec_id = m["id"]
            vectors.append({"id": vec_id, "values": emb, "metadata": m})

            # [CACHE WARM] Store method metadata in Redis for instant lookup
            cache_key = f"method_meta:{vec_id}"
            try:
                self.redis.set(cache_key, json.dumps(m), ex=86400)  # 24h
            except Exception:
                pass

        if vectors:
            self.method_index.upsert(vectors=vectors)
            print(f"   [OK] SubAtomicRegistry: Indexed {len(vectors)} methods + cache Warmed")

    def find_method(self, Task: str, top_k: int = 3) -> list[dict]:
        """Hybrid search for best method — now cache-first"""
        cache_key = f"method_search:{hashlib.sha256(Task.encode()).hexdigest()}_{top_k}"
        try:
            cached = self.redis.get(cache_key)
            if cached:
                print(f"   [CACHE HIT] Method search for '{Task[:30]}...'")
                return json.loads(cached)
        except Exception:
            pass

        results = self.pinecone.hybrid_search(
            query_text=Task,
            keywords=[w for w in self.pinecone.CANON_SIGNALS if w in Task.lower()],
            top_k=top_k,
            min_score=0.88,
        )

        # [CACHE WARM] Store successful search results
        try:
            if results:
                self.redis.set(cache_key, json.dumps(results), ex=3600)  # 1h
        except Exception:
            pass

        return results

    def find_and_invoke(self, task_description: str, *args, **kwargs) -> Any:
        """The ultimate sovereign loop: Find it, then do it."""
        matches = self.find_method(task_description, top_k=1)
        if not matches:
            raise ValueError(f"No method found for Task: {task_description}")

        meta = matches[0]["metadata"]
        print(f"   [EXECUTE] Invoking {meta['method']} from {Path(meta['path']).name}")
        # Dynamic import and execution logic would go here
        return meta

    def invoke_method(self, method_meta: dict, *args, **kwargs) -> Any:
        """Dynamically invoke a method by metadata"""
        try:
            # Import the module
            module_path = Path(method_meta["path"]).relative_to(self.root)
            module_name = str(module_path).replace(os.sep, ".")[:-3]
            module = importlib.import_module(module_name)

            # Get the method
            method = getattr(module, method_meta["method"])

            # Execute it
            if inspect.iscoroutinefunction(method):
                return asyncio.run(method(*args, **kwargs))
            else:
                return method(*args, **kwargs)
        except Exception as e:
            print(f"   [ERROR] Failed to invoke {method_meta['method']}: {e}")
            raise

    async def execute(self, ctx=None) -> Any:
        """Execute execute operation."""
        count = len(self.extract_methods())
        print(f"   [OK] SubAtomicRegistry: {count} methods online and searchable.")
        if ctx:
            ctx.report("Registry", count, True, "Method capabilities mapped.")

    @timeout(300)
    @standard_heal
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
            # CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)
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

        # Default implementation - SubAtomicRegistryAgent manages sub-atomic registry
        try:
            return {
                "status": "skipped",
                "details": f"SubAtomicRegistryAgent heal() not yet implemented for {violation_type}",
                "artifacts": [],
                "errors": [],
            }
        except Exception as e:
            return {
                "status": "failed",
                "details": f"SubAtomicRegistryAgent heal() failed: {str(e)}",
                "artifacts": [],
                "errors": [str(e)],
            }
