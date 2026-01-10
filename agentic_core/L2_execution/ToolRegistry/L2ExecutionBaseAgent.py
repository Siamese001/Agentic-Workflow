# NEW FILE: Unified L2 Execution Base Agent
# Location: agentic_core/L2_execution/base_agents/L2ExecutionBaseAgent.py
# Purpose: Single canonical base class replacing both:
#   - ExecutionCanonBaseAgent (heavyweight Gemini + subatomic features)
#   - SubAtomicAgent (lightweight async validation)
#
# Design Decisions (per Phase 2 Roadmap):
# - Dataclass pattern for consistent initialization (from CanonBaseAgent)
# - ValidationContext typing (from SubAtomicAgent - more precise than Any)
# - Async execute() mandatory + abstract enforcement
# - SubatomicTestingMixin mandatory (layer-specific testing)
# - HealerMixin mandatory (self-repair)
# - Gemini client + subatomic engine optional via enable_gemini flag
#   → Default: True (preserves behavior of ~50 Canon agents)
#   → Set False for lightweight former SubAtomic agents (~80)
# - get_validation_keys() optional - defaults to empty list
#   → Canon-style agents override it
#   → Validation agents return []
# - Common methods from both bases merged (can_run, run_with_broadcast, etc.)
# - Heavy Canon methods (check_negative_constraints, run_subatomic_critique, etc.)
#   guarded by if self.enable_gemini to avoid overhead in lightweight mode
# - BANNED_IMPORTS and negative constraint checking preserved (gated)

from __future__ import annotations

import ast
import asyncio
import json
import os
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dotenv import load_dotenv

# Core imports
from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)
from agentic_core.utils.mixins import SubatomicTestingMixin
from agentic_core.utils.core_extensions.timeout_decorator import timeout
from agentic_core.utils.core_extensions.mcp_hardened_mixin import MCPHardenedMixin

# NEW: Root inheritance
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.utils.core_extensions.redis_cache_mixin import RedisCacheMixin
from agentic_core.utils.core_extensions.pinecone_vector_mixin import PineconeVectorMixin

# Gemini optional import
try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None

load_dotenv()

# Placeholders (preserved from CanonBaseAgent)
class _SubatomicEnginePlaceholder:
    def __init__(self, gemini_client: Any):
        self.client = gemini_client

def get_subatomic_engine(gemini_client: Any) -> Any:
    return _SubatomicEnginePlaceholder(gemini_client)

# Unified Base Class
@dataclass
class L2ExecutionBaseAgent(SovereignBaseAgent, SubatomicTestingMixin, RedisCacheMixin, PineconeVectorMixin):
    """Unified L2 base class - replaces CanonBaseAgent + SubAtomicAgent.
    
    HARDENED: Now with Redis caching + Pinecone vector support.
    
    Features:
    - Async execution (mandatory)
    - Gemini client (optional via enable_gemini flag)
    - Subatomic testing (mandatory via mixin)
    - Healing infrastructure (mandatory - from SovereignBaseAgent)
    - Real logging (from SovereignBaseAgent)
    - Standardized self-tests & heal_repository (from SovereignBaseAgent)
    - ValidationContext (mandatory)
    - Redis caching (RedisCacheMixin) - with graceful degradation
    - Pinecone vectors (PineconeVectorMixin) - with graceful degradation
    """
    ctx: ValidationContext
    enable_gemini: bool = True  # Feature flag - True for former Canon agents, False for lightweight
    
    # [PHASE 2] Redis/Pinecone integration
    _cache_prefix: str = "l2_execution"
    _namespace: str = "l2_tools"
    
    name: str = field(init=False)
    role: str = field(init=False)
    _client: Optional[Any] = field(default=None, init=False)
    _subatomic_engine: Optional[Any] = field(default=None, init=False)
    BANNED_IMPORTS: List[str] = field(default_factory=lambda: ['base', 'context', 'L3_orchestration', 'ConversationalRepair'], init=False)

    def __post_init__(self) -> None:
        """Shared initialization logic."""
        # Call root for name + universal setup
        super().__post_init__()
        
        self.role = re.sub('(?<!^)(?=[A-Z])', '_', self.name).lower()
        
        # Conditional Gemini + subatomic initialization
        if self.enable_gemini:
            api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
            if genai and api_key:
                self._client = genai.Client(api_key=api_key)
                self.log_info("connected to Gemini")
                try:
                    self._subatomic_engine = get_subatomic_engine(self._client)
                    self.log_info("Sub-Atomic Engine initialized")
                except Exception as e:
                    self.log_error(f"Failed to init Sub-Atomic Engine: {e}")
            else:
                self.log_warning(f"Gemini not available (API key: {'found' if api_key else 'missing'})")

    def can_run(self) -> bool:
        """From SubAtomicAgent - default run unless critical failure."""
        return 'CRITICAL_FAIL' not in self.ctx.signals

    async def run_with_broadcast(self) -> Any:
        """From SubAtomicAgent - lifecycle broadcast wrapper."""
        self.ctx._current_agent = self.name
        try:
            return await self.execute()
        except Exception as e:
            self.log_error(f"Execution error: {e}")
            raise

    @abstractmethod
    async def execute(self) -> Any:
        """Mandatory async execution - all L2 agents must implement."""
        raise NotImplementedError(f'{self.name} must implement async execute()')

    def get_validation_keys(self) -> List[int]:
        """Optional for Canon-style agents - defaults to empty."""
        return []

    # --- Heavy features gated behind enable_gemini ---
    def check_negative_constraints(self, code: str) -> Tuple[bool, List[str]]:
        """From CanonBaseAgent - only active if enable_gemini."""
        if not self.enable_gemini:
            return True, []
        violations: List[str] = []
        for banned in self.BANNED_IMPORTS:
            pattern = f'(?:import\\s+{re.escape(banned)}|from\\s+{re.escape(banned)}\\s+import|from\\s+{re.escape(banned)}\\.)'
            if re.search(pattern, code):
                violations.append(f'Banned import: {banned}')
        return (len(violations) == 0, violations)

    # run_subatomic_critique and related methods can be added here similarly if needed
    # For now omitted to keep base lean - subclasses can implement or import if required

    # =========================================================================
    # L2-SPECIFIC LAYER METHODS: Tool Execution
    # =========================================================================
    
    def act(self, plan: List[str]) -> Dict[str, Any]:
        """L2-specific: Execute tools from plan with parallel support and error handling.
        
        Args:
            plan: List of tool actions to execute
            
        Returns:
            Dict with aggregated results and any errors
        """
        tools = self._extract_tools_from_plan(plan)
        results = []
        errors = []
        
        for tool in tools:
            try:
                result = self._execute_tool(tool)
                results.append({"tool": tool, "result": result, "success": True})
            except Exception as e:
                errors.append({"tool": tool, "error": str(e), "type": type(e).__name__})
                results.append({"tool": tool, "result": None, "success": False, "error": str(e)})
        
        # Trigger healing on errors
        if errors:
            clustered = self.cluster_errors(errors)
            self.log_warning(f"Tool execution errors: {clustered}")
            super().heal_repository()
        
        return {
            "results": results,
            "errors": errors,
            "success_count": sum(1 for r in results if r.get("success")),
            "error_count": len(errors)
        }
    
    async def act_async(self, plan: List[str]) -> Dict[str, Any]:
        """L2-specific: Async parallel tool execution with rate-limit healing.
        
        Args:
            plan: List of tool actions to execute
            
        Returns:
            Dict with aggregated results and clustered errors
        """
        tools = self._extract_tools_from_plan(plan)
        
        async def execute_one(tool: str) -> Dict[str, Any]:
            try:
                result = await self._execute_tool_async(tool)
                return {"tool": tool, "result": result, "success": True}
            except Exception as e:
                return {"tool": tool, "result": None, "success": False, "error": str(e), "type": type(e).__name__}
        
        # Parallel execution
        results = await asyncio.gather(*[execute_one(t) for t in tools], return_exceptions=True)
        
        # Handle exceptions from gather
        processed_results = []
        for i, r in enumerate(results):
            if isinstance(r, Exception):
                processed_results.append({"tool": tools[i], "success": False, "error": str(r), "type": type(r).__name__})
            else:
                processed_results.append(r)
        
        errors = [r for r in processed_results if not r.get("success")]
        
        if errors:
            clustered = self.cluster_errors(errors)
            self.log_warning(f"Async execution errors: {clustered}")
            super().heal_repository()
        
        return {
            "results": processed_results,
            "errors": errors,
            "clustered_errors": self.cluster_errors(errors) if errors else {},
            "success_count": sum(1 for r in processed_results if r.get("success")),
            "error_count": len(errors)
        }
    
    def cluster_errors(self, errors: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """L2-specific: Group errors by type for efficient targeted healing.
        
        Args:
            errors: List of error dicts with 'type' and 'error' keys
            
        Returns:
            Dict mapping error types to list of error messages
        """
        from collections import defaultdict
        groups: Dict[str, List[str]] = defaultdict(list)
        
        for e in errors:
            error_type = e.get("type", "Unknown")
            error_msg = e.get("error", str(e))
            groups[error_type].append(error_msg)
        
        return dict(groups)
    
    def _extract_tools_from_plan(self, plan: List[str]) -> List[str]:
        """Extract tool names/actions from plan steps."""
        tools = []
        for step in plan:
            # Simple extraction - subclasses can override for complex parsing
            if isinstance(step, str):
                tools.append(step)
            elif isinstance(step, dict):
                tools.append(step.get("tool", step.get("action", str(step))))
        return tools
    
    def _execute_tool(self, tool: str) -> Any:
        """Execute a single tool - override in subclasses for actual implementation."""
        self.log_info(f"Executing tool: {tool}")
        return {"executed": tool, "status": "placeholder"}
    
    async def _execute_tool_async(self, tool: str) -> Any:
        """Async tool execution - override in subclasses for actual implementation."""
        self.log_info(f"Async executing tool: {tool}")
        return {"executed": tool, "status": "placeholder", "async": True}

    @timeout(300)
    def heal_repository(self, dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: Optional[set] = None) -> Dict[str, int]:
        """Shared healing stub - operational for L2."""
        if _call_path is None:
            _call_path = set()
        agent_name = self.name
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            # CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)
            super().heal_repository()
            self.log_info("L2 execution - operational healing")
            return {"healed": 1}
        finally:
            _call_path.discard(agent_name)
