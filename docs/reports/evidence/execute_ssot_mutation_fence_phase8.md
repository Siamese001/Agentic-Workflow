# Execute SSOT Mutation Fence Hardening — Phase 8 Evidence

## Wave 8.1 — Tool/Write Surface Inventory

### Tool Registry & Invocation Inventory
```
================================================================================
TOOL REGISTRY & INVOCATION INVENTORY
================================================================================


FILE: agentic_core\base_agents\L0RoutingBase.py
--------------------------------------------------------------------------------
  Line 91: """Invoke shared healing chain then allow subclass override."""

FILE: agentic_core\base_agents\L2ExecutionBase.py
--------------------------------------------------------------------------------
  Line 9: - Tool registry operations
  Line 34: - Tool registry management
  Line 52: Execute a registered tool by name.
  Line 54: Override in subclasses for specialized tool execution.
  Line 56: return {"tool": tool_name, "status": "not_implemented", "result": None}
  Line 60: Register a tool in the tool registry.
  Line 62: Override in subclasses for specialized tool registration.

FILE: agentic_core\base_agents\L3OrchestrationBase.py
--------------------------------------------------------------------------------
  Line 66: """Invoke shared healing chain then allow subclass override."""

FILE: agentic_core\base_agents\SovereignBaseAgent.py
--------------------------------------------------------------------------------
  Line 539: Sanitize tool output to prevent token overload.
  Line 545: output: The raw tool output string.

FILE: agentic_core\L0_routing\legacy_agent_name_allowlist.py
--------------------------------------------------------------------------------
  Line 24: "PromptRegistryAgent": "Deleted: zero production refs after string cleanup (Phase 5)",

FILE: agentic_core\L2_execution\cid_registry.py
--------------------------------------------------------------------------------
  Line 2: L2 CID Registry - Immutable Execution Cycle Tracking
  Line 20: class CIDRegistry:
  Line 22: Deterministic CID Registry for execution cycle tracking.
  Line 29: """Initialize CID Registry with empty cycle tracking."""

FILE: agentic_core\L2_execution\reentry_loop.py
--------------------------------------------------------------------------------
  Line 8: from agentic_core.L2_execution.cid_registry import CIDRegistry, ExecutionCycle
  Line 19: def __init__(self, max_attempts: int, cid_registry: CIDRegistry = None):
  Line 25: cid_registry: Optional CIDRegistry instance
  Line 31: self._cid_registry = cid_registry or CIDRegistry()
  Line 49: Calls CIDRegistry.next_attempt.
  Line 57: return self._cid_registry.next_attempt(cycle)
  Line 69: return self._cid_registry.new_cycle(cid)
  Line 81: return self._cid_registry.get_cycle(cid)
  Line 94: return self._cid_registry.update_status(cid, status)

FILE: agentic_core\mixins\batching_mixin.py
--------------------------------------------------------------------------------
  Line 9: - Lazy initialization registry
  Line 59: self._lazy_registry: dict[str, Callable] = {}
  Line 150: self._lazy_registry[name] = initializer
  Line 155: if name in self._lazy_registry:
  Line 156: return self._lazy_registry[name]()
  Line 163: if name not in self._lazy_registry:
  Line 166: resource = self._lazy_registry[name]()
  Line 282: "lazy_registered": len(self._lazy_registry),

FILE: agentic_core\mixins\capability_discovery_mixin.py
--------------------------------------------------------------------------------
  Line 3: """CapabilityDiscoveryMixin - Registry Pattern."""

FILE: agentic_core\mixins\golden_context_mixin.py
--------------------------------------------------------------------------------
  Line 32: - L2: Execution (tool registry, MCP, action handlers)
  Line 50: - Agent Registry: `agent_discovery_full.json`

FILE: agentic_core\mixins\hardening_mixin.py
--------------------------------------------------------------------------------
  Line 9: Phase 1 - Pillar 8: Tool Ecosystem (Resilience Middleware)
  Line 109: result = await self.error_recovery.invoke_with_retry(

FILE: agentic_core\mixins\infrastructure_mixin.py
--------------------------------------------------------------------------------
  Line 67: 3. Tool reliability (ToolReliabilityMixin) [PHASE 2 Feb 2026]

FILE: agentic_core\mixins\mcp_operation_mixin.py
--------------------------------------------------------------------------------
  Line 68: """Execute an MCP tool call with retry, backoff, idempotency, and audit.
  Line 71: tool_name: MCP tool identifier.
  Line 72: args: Arguments to pass to the tool.
  Line 87: result = await self.mcp_gateway.call_tool(
  Line 134: """Deterministic idempotency key from tool + args."""
  Line 140: tool: str,
  Line 148: "tool": tool,

FILE: agentic_core\mixins\performance_mixin.py
--------------------------------------------------------------------------------
  Line 151: # Lazy initialization registry
  Line 152: self._lazy_registry: dict[str, Callable] = {}
  Line 568: self._lazy_registry[name] = initializer
  Line 584: if name in self._lazy_registry:
  Line 585: return self._lazy_registry[name]()
  Line 592: if name not in self._lazy_registry:
  Line 596: resource = self._lazy_registry[name]()
  Line 679: "lazy_registered": len(self._lazy_registry),
  Line 818: "lazy_registered": len(self._lazy_registry),

FILE: agentic_core\mixins\self_diagnosis_mixin.py
--------------------------------------------------------------------------------
  Line 85: # 2. If component has health_check method, invoke it

FILE: agentic_core\mixins\subatomic_testing_mixin.py
--------------------------------------------------------------------------------
  Line 56: - Tool registration verification

FILE: agentic_core\mixins\tool_reliability_mixin.py
--------------------------------------------------------------------------------
  Line 2: ToolReliabilityMixin - Phase 2 Critical Infrastructure: Tool Reliability
  Line 4: Provides retry logic and fallback mechanisms for external tool failures.
  Line 10: - Tool health monitoring
  Line 14: All agents requiring tool reliability should inherit from this mixin.
  Line 70: """Health status for a tool."""
  Line 92: """Check if tool is considered healthy."""
  Line 117: Mixin providing tool reliability features for agents.
  Line 123: - Tool health monitoring
  Line 141: """Initialize tool reliability state."""
  Line 144: # Retry policies per tool
  Line 147: # Circuit breaker configs per tool
  Line 150: # Tool health tracking
  Line 157: # [HARDENING] Thread safety lock for tool health tracking
  Line 163: Logger.debug(f"[RELIABILITY] {self.__class__.__name__} tool reliability initialized")
  Line 177: Configure retry policy for a tool.
  Line 180: tool_name: Name of the tool
  Line 224: Configure circuit breaker for a tool.
  Line 227: tool_name: Name of the tool
  Line 258: """Ensure tool health tracking exists."""
  Line 311: """Record successful tool call."""
  Line 328: """Record failed tool call."""
  Line 435: tool_name: Name of the tool for tracking
  Line 511: tool_name: Name of the tool for tracking
  Line 559: Get health status for a tool.
  Line 562: tool_name: Name of the tool
  Line 589: Dictionary mapping tool names to health metrics
  Line 595: Manually reset circuit breaker for a tool.
  Line 598: tool_name: Name of the tool

FILE: agentic_core\prompt_governance\prompt_entry_types.py
--------------------------------------------------------------------------------
  Line 32: prompts: dict[str, PromptEntry] = field(default_factory=lambda: _build_prompt_registry())
  Line 34: persona_registry: dict[str, str] = field(default_factory=lambda: _build_persona_registry())
  Line 37: def _build_prompt_registry() -> dict[str, PromptEntry]:
  Line 38: """Build immutable prompt registry. Called once at module load."""
  Line 50: content="You are the Territory Healer. Your mission is to identify files that drift from the canonical structure and move them to their Sovereign Registry locations.",
  Line 56: source="runtime_registry_agent_capabilities.py",
  Line 63: source="runtime_registry_agent_capabilities.py",
  Line 70: source="runtime_registry_agent_capabilities.py",
  Line 77: source="runtime_registry_agent_capabilities.py",
  Line 84: source="runtime_registry_agent_capabilities.py",
  Line 91: source="runtime_registry_agent_capabilities.py",
  Line 98: source="runtime_registry_agent_capabilities.py",
  Line 213: """Build immutable directive template registry. Called once at module load."""
  Line 226: def _build_persona_registry() -> dict[str, str]:
  Line 227: """Build immutable persona registry. Called once at module load."""
  Line 278: DEPRECATED: Use get_constitution().persona_registry[persona_id] instead.
  Line 282: if persona_id not in constitution.persona_registry:
  Line 284: return constitution.persona_registry[persona_id]

FILE: agentic_core\utils\decorators_util.py
--------------------------------------------------------------------------------
  Line 256: # Invoke observer seam if set (for testing/monitoring)
  Line 269: # Phase 8: Invoke heal LLM seam probe via guarded call (only when model is routed)

FILE: agentic_core\config\core\domain_constitution_config.py
--------------------------------------------------------------------------------
  Line 38: "role": "Action: Tool Implementation and Agent Realization",

FILE: agentic_core\config\core\hygiene_registry_config.py
--------------------------------------------------------------------------------
  Line 4: Core Hygiene Agents Registry - Mandatory agents for repo health.

FILE: agentic_core\config\core\injection_layer_config.py
--------------------------------------------------------------------------------
  Line 163: name="Tool-Feedback Loop Injection",
  Line 165: description="Incorporate structured tool outputs into subsequent reasoning steps.",
  Line 166: template="[TOOL FEEDBACK] Integrate tool output: {tool_output}. Adjust reasoning accordingly.",
  Line 177: name="Cross-Tool Reconciliation",

FILE: agentic_core\config\core\legacy_artifacts_config.py
--------------------------------------------------------------------------------
  Line 5: Category: TYPES (Registry of domain constants/patterns)
  Line 47: Registry of "Organic Value" salvaged from the Pre-Sovereign Era (Phases 27-29).

FILE: agentic_core\config\core\registry_config.py
--------------------------------------------------------------------------------
  Line 2: SSOT for Sovereign Registry configuration.
  Line 4: This module contains the core registry data structures that define
  Line 14: # SOVEREIGN REGISTRY - Core Territory Definitions
  Line 18: SOVEREIGN_REGISTRY: dict = {
  Line 125: "L2_execution": ["tool_registry", "action_handlers", "mcp", "tool_registry"],
  Line 157: "prompt_governance": ["meta_prompts", "version_registry", "rendering", "templates"],
  Line 274: "tool_registry": "L2_execution",
  Line 303: "version_registry": "prompt_governance",
  Line 312: "SOVEREIGN_REGISTRY",

FILE: agentic_core\config\core\yaml_injection_loader.py
--------------------------------------------------------------------------------
  Line 279: elif "tool" in filename:

FILE: agentic_core\L0_routing\enforcement\boot_sequence.py
--------------------------------------------------------------------------------
  Line 26: from agentic_core.discovery import AgentRegistry
  Line 40: self.registry = AgentRegistry()
  Line 74: self.discovered_agents = self.registry.discover_all()

FILE: agentic_core\L0_routing\enforcement\boundary_contracts.py
--------------------------------------------------------------------------------
  Line 35: blueprint_registry: dict[str, str],
  Line 37: """§1.5 — Resolve node_id against the structure blueprint registry.
  Line 39: blueprint_registry maps node_id -> blueprint_entry.
  Line 45: entry = blueprint_registry.get(node_id)

FILE: agentic_core\L0_routing\engines\execution_orchestrator.py
--------------------------------------------------------------------------------
  Line 5: CIDRegistry, ReEntryLoop, MetaLearningBus, and VigilanceDispatcher.
  Line 26: cid_registry,
  Line 39: cid_registry: CIDRegistry instance
  Line 48: self.cid_registry = cid_registry
  Line 85: cycle = self.cid_registry.new_cycle(f"execute_{path.value}")

FILE: agentic_core\L0_routing\meta_control\meta_apply.py
--------------------------------------------------------------------------------
  Line 4: NO automatic/background application.  Must be invoked explicitly.

FILE: agentic_core\L0_routing\meta_control\meta_apply_ops.py
--------------------------------------------------------------------------------
  Line 6: NO automatic/background application.  All functions are explicit invoke only.
  Line 37: # §Wave7.0.15 — Invariant Registry
  Line 84: INVARIANT_REGISTRY: dict[str, InvariantCheckFn] = {
  Line 97: """Evaluate named invariants from the registry.
  Line 103: fn = INVARIANT_REGISTRY.get(name)

FILE: agentic_core\L0_routing\reasoning\SSOTFolderCleanupAgent.py
--------------------------------------------------------------------------------
  Line 98: # Derive SOVEREIGN_REGISTRY and CORE_SUBFOLDER_MAP from L0 constants
  Line 99: self.sovereign_registry = {
  Line 132: # Add sovereign registry roots
  Line 133: for root in self.sovereign_registry.keys():
  Line 137: subfolders = self.sovereign_registry[root].get("subfolders", [])
  Line 213: valid_layers = self.sovereign_registry.get("agentic_core", {}).get("subfolders", [])
  Line 235: if parts[0] in self.sovereign_registry:

FILE: agentic_core\L0_routing\scripts\action_capability.py
--------------------------------------------------------------------------------
  Line 6: Defines the contract for all tool execution and external interactions.
  Line 78: - Tool Execution: Running external tools and APIs
  Line 94: request: Action request with tool and parameters
  Line 138: List of tool names
  Line 144: """Get schema for a specific tool.
  Line 147: tool_name: Name of the tool
  Line 150: Tool schema with parameters and types

FILE: agentic_core\L0_routing\scripts\agent_validation_util.py
--------------------------------------------------------------------------------
  Line 73: from agentic_core.L0_routing.utils.subprocess_runner_util import invoke_arch_governor
  Line 79: # Invoke via subprocess to avoid upward import edge
  Line 80: result = invoke_arch_governor(

FILE: agentic_core\L0_routing\scripts\base_tool.py
--------------------------------------------------------------------------------
  Line 1: # Tooling Interface and Registry
  Line 15: name: str = Field(..., description="Unique identifier for the tool")
  Line 25: Execute the tool logic. Returns a string observation.
  Line 32: Wrapper to turn a Python function into a Tool.
  Line 47: class ToolRegistry:
  Line 55: def register(self, tool: BaseTool):
  Line 56: if tool.name in self._tools:
  Line 57: raise ValueError(f"Tool {tool.name} already registered")
  Line 58: self._tools[tool.name] = tool

FILE: agentic_core\L0_routing\scripts\base_tool_script.py
--------------------------------------------------------------------------------
  Line 2: Base classes for L2 Execution tool_registry.
  Line 4: Provides foundational classes for tool registration and execution.
  Line 14: """Base class for all tools in the registry."""
  Line 22: """Execute the tool. Override in subclasses."""
  Line 26: """Check if tool is enabled."""
  Line 30: """Enable the tool."""
  Line 34: """Disable the tool."""
  Line 38: class tool_registry:
  Line 39: """Registry for managing tools."""
  Line 44: def register(self, tool: BaseTool) -> None:
  Line 45: """Register a tool."""
  Line 46: self._tools[tool.name] = tool
  Line 47: logger.debug(f"Registered tool: {tool.name}")
  Line 50: """Unregister a tool by name."""
  Line 53: logger.debug(f"Unregistered tool: {name}")
  Line 56: """Get a tool by name."""
  Line 60: """List all registered tool names."""
  Line 64: """Execute a tool by name."""
  Line 65: tool = self.get(name)
  Line 66: if tool is None:
  Line 67: raise ValueError(f"Tool not found: {name}")
  Line 68: if not tool.is_enabled():
  Line 69: raise ValueError(f"Tool is disabled: {name}")
  Line 70: return tool.execute(*args, **kwargs)
  Line 82: Tool = BaseTool
  Line 83: Registry = tool_registry
  Line 85: __all__ = ["BaseTool", "tool_registry", "Tool", "Registry"]

FILE: agentic_core\L0_routing\scripts\check_syntax_util.py
--------------------------------------------------------------------------------
  Line 10: from agentic_core.L0_routing.utils.subprocess_runner_util import invoke_code_validator
  Line 15: result = invoke_code_validator(action="validate", project_root=project_root)

FILE: agentic_core\L0_routing\scripts\collision_resolver.py
--------------------------------------------------------------------------------
  Line 4: Status: Post-Migration Triage Tool
  Line 7: This tool finds these specific cases and reports them for manual adjudication.

FILE: agentic_core\L0_routing\scripts\colors.py
--------------------------------------------------------------------------------
  Line 365: help="Agent method to invoke (default: heal_repository)",
  Line 548: # Invoke specified method (default: heal_repository)
  Line 593: from agentic_core.config.core.hygiene_registry_config import CORE_HYGIENE_AGENTS, MANDATORY_PREFLIGHT

FILE: agentic_core\L0_routing\scripts\compliance_gate_util.py
--------------------------------------------------------------------------------
  Line 28: discovered_agents: List of agents discovered by AgentRegistry

FILE: agentic_core\L0_routing\scripts\core_synthesis_executor.py
--------------------------------------------------------------------------------
  Line 265: if any(keyword in file_path.name.lower() for keyword in ["util", "tool", "helper", "decorator"]):

FILE: agentic_core\L0_routing\scripts\c_c_measurement.py
--------------------------------------------------------------------------------
  Line 24: """Initialize measurement tool."""
  Line 262: tool = CCMeasurement()
  Line 266: data = tool.measure_cc()
  Line 273: metrics = tool.analyze_results(data)
  Line 276: tool.print_report(metrics, "Current Cyclomatic Complexity Report")
  Line 279: report_file = tool.project_root / AGENTIC_CORE_DIR / "L0_routing" / "logs" / "cc_current_measurement.json"
  Line 280: tool.save_report(metrics, report_file)

FILE: agentic_core\L0_routing\scripts\debug_invocation_pipeline_util.py
--------------------------------------------------------------------------------
  Line 10: # Load registry
  Line 11: registry = json.load(open(PROJECT_ROOT / AGENT_DISCOVERY_JSON))
  Line 12: print(f"JSON agents: {len(registry)}")
  Line 15: registry_by_path = {}
  Line 16: for entry in registry:
  Line 19: registry_by_path[p] = entry
  Line 21: print(f"Registry paths: {len(registry_by_path)}")
  Line 25: for entry in registry:
  Line 32: for agent in registry:
  Line 49: entry = registry_by_path.get(rel_path)
  Line 74: # Show sample registry paths
  Line 75: print("\nSample registry paths:")
  Line 76: for _i, p in enumerate(list(registry_by_path.keys())[:5]):

FILE: agentic_core\L0_routing\scripts\demo_cli_functionality_util.py
--------------------------------------------------------------------------------
  Line 56: print("✅ Fallback to first registry territory if none specified")
  Line 57: print("✅ Hard exit if no territories found in registry")
  Line 64: print("\n# Use default territory (first in registry):")

FILE: agentic_core\L0_routing\scripts\disposition.py
--------------------------------------------------------------------------------
  Line 245: if any(keyword in filename.lower() for keyword in ["util", "tool", "helper"]):

FILE: agentic_core\L0_routing\scripts\drift.py
--------------------------------------------------------------------------------
  Line 3: description: AST-based static analysis tool to detect inheritance drift.

FILE: agentic_core\L0_routing\scripts\error_handler.py
--------------------------------------------------------------------------------
  Line 23: from .base_coordinator import WorkflowCoordinator, coordinator_registry
  Line 25: STRATEGY_REGISTRY,
  Line 117: - Coordinator registry for specialized domains
  Line 122: self.strategies = STRATEGY_REGISTRY.copy()
  Line 123: self.coordinator_registry = coordinator_registry
  Line 162: coordinator = self.coordinator_registry.get_for_workflow(workflow_type)
  Line 217: coordinator = self.coordinator_registry.get(coordinator_name)
  Line 236: self.coordinator_registry.register(coordinator)
  Line 257: "coordinators": self.coordinator_registry.get_statistics(),

FILE: agentic_core\L0_routing\scripts\execute_ssot.py
--------------------------------------------------------------------------------
  Line 374: """§8.1e — Invoke gateway.execute in LOG_ONLY mode for SSOT audit trail."""
  Line 911: "Windows LongPathsEnabled is NOT active (Set to 1 in Registry) - proceeding in dry-run mode"
  Line 914: errors.append("Windows LongPathsEnabled is NOT active (Set to 1 in Registry)")
  Line 1373: def discover_agents_from_registry(project_root: Path, dedupe: bool = True) -> list[tuple[str, str]]:
  Line 2028: action = f"RENAME: '{filename}' has audit/report naming but is a Python script. Either: 1) Rename to avoid audit patterns (e.g., registry_linkage_checker.py) OR 2) Move to agentic_core/L0_routing/scripts/ where audit scripts belong"
  Line 2410: # Invoke via subprocess to avoid upward import edges
  Line 2412: invoke_orchestrator_mission,
  Line 2417: result = invoke_orchestrator_mission(
  Line 2621: """Alias for discover_agents_from_registry (backward compat)."""
  Line 2624: return discover_agents_from_registry(project_root)
  Line 2816: from agentic_core.L0_routing.utils.subprocess_runner_util import invoke_arch_governor
  Line 2818: result = invoke_arch_governor(
  Line 2909: invoke_agent_roster_validation,
  Line 2912: roster_result = invoke_agent_roster_validation()
  Line 3019: from agentic_core.L0_routing.utils.subprocess_runner_util import invoke_arch_governor
  Line 3021: result = invoke_arch_governor(

FILE: agentic_core\L0_routing\scripts\execute_ssot_entrypoint.py
--------------------------------------------------------------------------------
  Line 8: 3. Requires --legacy flag to invoke the legacy healing pipeline.
  Line 52: help="Invoke the legacy healing pipeline (execute_ssot._legacy_main).",
  Line 90: "\nError: --legacy flag required to invoke the healing pipeline.",

FILE: agentic_core\L0_routing\scripts\execution.py
--------------------------------------------------------------------------------
  Line 381: # Strategy registry
  Line 382: STRATEGY_REGISTRY: dict[str, ExecutionStrategy] = {
  Line 392: for strategy in STRATEGY_REGISTRY.values():
  Line 395: return STRATEGY_REGISTRY["dag"]  # Default

FILE: agentic_core\L0_routing\scripts\execution_context.py
--------------------------------------------------------------------------------
  Line 150: """Invoke healing chain via super()."""

FILE: agentic_core\L0_routing\scripts\flatten_scripts_directory_util.py
--------------------------------------------------------------------------------
  Line 5: [SSOT] All depth requirements derived from SOVEREIGN_REGISTRY in structure_blueprint.py
  Line 19: SOVEREIGN_REGISTRY = {"agentic_core": {"depth": 4}}
  Line 24: required_depth: Any = SOVEREIGN_REGISTRY["agentic_core"]["depth"]

FILE: agentic_core\L0_routing\scripts\forensic_discovery_prep.py
--------------------------------------------------------------------------------
  Line 3: FORENSIC DISCOVERY PREP - V10 GAP ANALYSIS TOOL
  Line 62: # Configure simplified logging for the tool

FILE: agentic_core\L0_routing\scripts\full_agent_discovery.py
--------------------------------------------------------------------------------
  Line 169: Logger.info(f"[DISCOVERY] Loaded {len(raw_agents)} candidates from SSOT registry")
  Line 454: f"[COMPLIANCE] FAILED: {ghosts} ghost agents detected in registry. Run refresh_cache.",
  Line 461: Logger.warning(f"[COMPLIANCE] Warning: {invalids} files in registry failed validation.")

FILE: agentic_core\L0_routing\scripts\function_tool.py
--------------------------------------------------------------------------------
  Line 2: Tools module for L2 Execution tool_registry.
  Line 4: Provides common tool implementations.
  Line 9: from .base import tool_registry
  Line 11: __all__ = ["BaseTool", "tool_registry", "FunctionTool"]
  Line 15: """A tool that wraps a callable function."""

FILE: agentic_core\L0_routing\scripts\hardened_anti_pattern_visitor.py
--------------------------------------------------------------------------------
  Line 135: x in target.id.upper() for x in ["REGISTRY", "MAP", "CONFIG"]
  Line 142: "Hardcoded Registry",

FILE: agentic_core\L0_routing\scripts\populate_ssot_folders_util.py
--------------------------------------------------------------------------------
  Line 56: "static_index": "Permanent store of vetted research papers, prompt constitutions, tool schemas. Indexed at embed time.",
  Line 59: "default": "Safe, sandboxed tool interaction. All tools must be registered and validated.",
  Line 60: "tool_registry": "Single source of truth for all available tools. Each tool: schema + implementation + safety policy.",
  Line 78: "vector_stores": "Abstract interface to Pinecone/Chroma/etc. No direct imports — use registry.",

FILE: agentic_core\L0_routing\scripts\run_all_guardians.py
--------------------------------------------------------------------------------
  Line 35: from agentic_core.L0_routing.types.guardian_registry_types import (
  Line 100: # Get guardians from SSOT registry (already sorted by guardian_id)

FILE: agentic_core\L0_routing\scripts\run_guardian_contract_integrity.py
--------------------------------------------------------------------------------
  Line 30: from agentic_core.L0_routing.types.guardian_registry_types import (
  Line 166: Scan all guardian scripts from SSOT registry and verify they follow the contract.
  Line 176: # Enumerate from SSOT registry (no filesystem globs)
  Line 184: details="No guardians found in SSOT registry (excluding self)",
  Line 186: result.set_error("No guardians in registry")
  Line 193: details=f"Found {len(guardians_to_check)} guardian(s) in SSOT registry",

FILE: agentic_core\L0_routing\scripts\run_hierarchy_agent_dry_run_util.py
--------------------------------------------------------------------------------
  Line 21: from agentic_core.L0_routing.utils.subprocess_runner_util import invoke_hierarchy_agent
  Line 33: # Invoke via subprocess to avoid upward import edge
  Line 34: result = invoke_hierarchy_agent(action="dry_run", project_root=project_root)

FILE: agentic_core\L0_routing\scripts\run_hierarchy_healer_dry_run_util.py
--------------------------------------------------------------------------------
  Line 19: from agentic_core.L0_routing.utils.subprocess_runner_util import invoke_hierarchy_agent
  Line 28: # Invoke via subprocess to avoid upward import edge
  Line 30: result = invoke_hierarchy_agent(action="heal_violations", project_root=project_root)

FILE: agentic_core\L0_routing\scripts\run_sovereign_compliance_audit_util.py
--------------------------------------------------------------------------------
  Line 20: from agentic_core.L0_routing.utils.subprocess_runner_util import invoke_code_validator
  Line 30: result = invoke_code_validator(

FILE: agentic_core\L0_routing\scripts\sovereign_lockdown_check_util.py
--------------------------------------------------------------------------------
  Line 40: from agentic_core.L0_routing.utils.subprocess_runner_util import invoke_arch_governor
  Line 46: # Invoke via subprocess to avoid upward import edge
  Line 47: result = invoke_arch_governor(

FILE: agentic_core\L0_routing\scripts\ssot_cli.py
--------------------------------------------------------------------------------
  Line 7: Professional-grade command-line tool for SSOT architectural governance.
  Line 16: Similar to git/npm, this tool provides a discoverable interface for

FILE: agentic_core\L0_routing\scripts\territory_ssot_definitions_util.py
--------------------------------------------------------------------------------
  Line 399: if any(kw in name_lower for kw in ["router", "connection", "permission", "registry", "gatekeeper"]):

FILE: agentic_core\L0_routing\scripts\validate_table2_data_util.py
--------------------------------------------------------------------------------
  Line 102: print("   ⚠️  renderCodeQualityTable might not be invoked")

FILE: agentic_core\L0_routing\scripts\verify_all_checkpoint_files_util.py
--------------------------------------------------------------------------------
  Line 12: "tests/unit/test_registry_mapping.py",

FILE: agentic_core\L0_routing\scripts\verify_manifest_util.py
--------------------------------------------------------------------------------
  Line 3: Description: Analysis tool for SSOT Dry-Run Reports.

FILE: agentic_core\L0_routing\scripts\verify_mro_util.py
--------------------------------------------------------------------------------
  Line 95: from agentic_core.L0_routing.utils.subprocess_runner_util import invoke_hierarchy_agent
  Line 97: result = invoke_hierarchy_agent(action="verify_mro")

FILE: agentic_core\L0_routing\types\boundary_types.py
--------------------------------------------------------------------------------
  Line 227: # §12.2 — SideEffectRegistry (tracks touched resources per heal wave)
  Line 232: class SideEffectRegistry:
  Line 233: """§12.2 — Immutable registry of side effects produced during a heal wave.
  Line 247: raise ValueError("SideEffectRegistry: trace_id must be non-empty")
  Line 249: raise ValueError("SideEffectRegistry: wave_id must be non-empty")
  Line 251: raise TypeError("SideEffectRegistry: paths_read must be a tuple")
  Line 253: raise TypeError("SideEffectRegistry: paths_written must be a tuple")
  Line 255: raise TypeError("SideEffectRegistry: apis_called must be a tuple")
  Line 321: "SideEffectRegistry",

FILE: agentic_core\L0_routing\types\guardian_registry.py
--------------------------------------------------------------------------------
  Line 2: SSOT Guardian Registry — Single Source of Truth for Guardian enumeration.
  Line 4: All consumers of Guardian metadata MUST derive from this registry:
  Line 10: NO filesystem globs. NO duplicated lists. Registry is SSOT.
  Line 50: # SSOT Registry — ALL guardians MUST be registered here

FILE: agentic_core\L0_routing\types\guardian_registry_types.py
--------------------------------------------------------------------------------
  Line 2: SSOT Guardian Registry — Single Source of Truth for Guardian enumeration.
  Line 4: All consumers of Guardian metadata MUST derive from this registry:
  Line 10: NO filesystem globs. NO duplicated lists. Registry is SSOT.
  Line 50: # SSOT Registry — ALL guardians MUST be registered here

FILE: agentic_core\L0_routing\types\integration_contract.py
--------------------------------------------------------------------------------
  Line 7: tool, schema_version, status, exit_code, inputs, findings, outputs
  Line 23: """A single finding from a governance tool run."""
  Line 44: tool: str
  Line 70: "tool": self.tool,

FILE: agentic_core\L0_routing\types\integration_contract_types.py
--------------------------------------------------------------------------------
  Line 7: tool, schema_version, status, exit_code, inputs, findings, outputs
  Line 23: """A single finding from a governance tool run."""
  Line 44: tool: str
  Line 70: "tool": self.tool,

FILE: agentic_core\L0_routing\types\routing_artifact_types.py
--------------------------------------------------------------------------------
  Line 243: """§15.4 — Tracks tool slot depletion rate."""
  Line 257: """Consume a tool slot. Returns False if depleted (fail-closed)."""
  Line 262: {"tool": tool_name, "slots_remaining": self.total_slots - self.used_slots},

FILE: agentic_core\L0_routing\types\routing_contracts.py
--------------------------------------------------------------------------------
  Line 37: # §3.6 — Law Slot Handler (Tool Isolation)
  Line 38: # All tool execution via read-only twins. Direct live tool access PROHIBITED.
  Line 43: """§3.6 — Enforces tool isolation via read-only twins.
  Line 45: Direct reference to live tool instances is PROHIBITED.
  Line 59: """Register a read-only twin for a tool. Live instances are rejected."""
  Line 69: """Acquire a tool slot via read-only twin. Fail-closed on depletion."""

FILE: agentic_core\L0_routing\utils\complexity_visitor_util.py
--------------------------------------------------------------------------------
  Line 251: "Registry",  # Service registries
  Line 1176: # DEPRECATED: This tool is now LEGACY and should not be used for SSOT enforcement.
  Line 1179: # - Direct filesystem scanning (no registry needed)
  Line 1183: # This tool is kept only for historical tracking and comparison purposes.
  Line 1203: # Step 1: Load previous agent registry
  Line 1214: f"Registry may be stale → falling back to full scan for integrity",
  Line 1498: has_tools = "tool" in source.lower() or "mcp" in source.lower()

FILE: agentic_core\L0_routing\utils\fix_all_tunnels_util.py
--------------------------------------------------------------------------------
  Line 5: [SSOT] All depth requirements derived from SOVEREIGN_REGISTRY in structure_blueprint.py
  Line 14: # Derive registry depth from SOVEREIGN_TERRITORIES
  Line 15: SOVEREIGN_REGISTRY = {"agentic_core": {"depth": 4}}
  Line 20: REQUIRED_DEPTH: Any = SOVEREIGN_REGISTRY["agentic_core"]["depth"]

FILE: agentic_core\L0_routing\utils\subprocess_runner.py
--------------------------------------------------------------------------------
  Line 18: "invoke_arch_governor",
  Line 19: "invoke_orchestrator_mission",
  Line 20: "invoke_agent_roster_validation",
  Line 21: "invoke_hierarchy_agent",
  Line 22: "invoke_code_validator",
  Line 26: def invoke_arch_governor(
  Line 33: Invoke ArchitectureGovernorAgent via subprocess.
  Line 82: def invoke_orchestrator_mission(
  Line 88: Invoke orchestrator mission via subprocess.
  Line 137: def invoke_agent_roster_validation() -> dict[str, Any]:
  Line 139: Invoke agent roster validation via subprocess.
  Line 173: def invoke_hierarchy_agent(
  Line 178: Invoke HierarchyAgent via subprocess.
  Line 219: def invoke_code_validator(
  Line 225: Invoke CodeValidatorAgent via subprocess.

FILE: agentic_core\L1_cognition\config\react_config.py
--------------------------------------------------------------------------------
  Line 104: This is the default reasoning model for complex tasks requiring tool use.

FILE: agentic_core\L1_cognition\enforcement\react_strategy.py
--------------------------------------------------------------------------------
  Line 10: from agentic_core.runtime.tools import ToolRegistry
  Line 21: async def plan(self, state: AgentState, tools: ToolRegistry) -> tuple[str, dict[str, Any]]:

FILE: agentic_core\L1_cognition\engines\capability_analyzer.py
--------------------------------------------------------------------------------
  Line 32: - Tool/sub-agent recommendations
  Line 139: if "tool" in error_type.lower() or "not found" in error_type.lower():
  Line 208: title="Add Missing Tool",
  Line 209: description=f"Add tool to handle scenarios: {', '.join(gap.affected_scenarios[:3])}",
  Line 213: "Identify required tool functionality",
  Line 214: "Search tool registry or implement custom tool",
  Line 215: "Integrate tool with action plane",

FILE: agentic_core\L1_cognition\engines\cognitive_engine.py
--------------------------------------------------------------------------------
  Line 120: - Async tool execution

FILE: agentic_core\L1_cognition\engines\reasoning_cache.py
--------------------------------------------------------------------------------
  Line 110: """cache for ReAct observations to avoid redundant tool calls."""

FILE: agentic_core\L1_cognition\reasoning\StrategicRecommendationAgent.py
--------------------------------------------------------------------------------
  Line 351: f"MCP hardening at {mcp_hardened:.1f}% (target 100%) exposes tool boundaries.",
  Line 403: "impact": "Medium - Reduces hallucinated tool usage by constraining search space.",
  Line 440: """Invoke healing chain via super()."""

FILE: agentic_core\L1_cognition\types\action_request_types.py
--------------------------------------------------------------------------------
  Line 15: """Request for the action plane to execute a tool or action.
  Line 18: tool_name: Name of the tool to execute
  Line 19: parameters: Parameters to pass to the tool

FILE: agentic_core\L1_cognition\types\budget_types.py
--------------------------------------------------------------------------------
  Line 14: """Tool call budget configuration."""

FILE: agentic_core\L1_cognition\types\capability_types.py
--------------------------------------------------------------------------------
  Line 3: """Enum types for AgentRegistry."""

FILE: agentic_core\L1_cognition\utils\constants_util.py
--------------------------------------------------------------------------------
  Line 16: SOVEREIGN_REGISTRY = {"agentic_core": {"depth": 4}, "apps_lic": {"depth": 3}, "apps_rg": {"depth": 3}}
  Line 17: depth_map: Any = {root: cfg["depth"] for root, cfg in SOVEREIGN_REGISTRY.items()}

FILE: agentic_core\L2_execution\config\mcpservermode_config.py
--------------------------------------------------------------------------------
  Line 4: Sovereign MCP Registry – Phase 13 (Dec 26, 2025)
  Line 7: This registry enforces:
  Line 44: SOVEREIGN_MCP_REGISTRY: dict[str, McpServerConfig] = {
  Line 73: description="Real-time web search for L2 tool execution",
  Line 132: return [mcp for mcp in SOVEREIGN_MCP_REGISTRY.values() if mcp.target_layer == layer]
  Line 137: return [mcp for mcp in SOVEREIGN_MCP_REGISTRY.values() if capability in mcp.capabilities]
  Line 143: def validate_mcp_registry() -> list[str]:
  Line 144: """Validate MCP registry for constitutional compliance."""
  Line 146: for name, config in SOVEREIGN_MCP_REGISTRY.items():
  Line 154: _violations = validate_mcp_registry()
  Line 159: warnings.warn(f"MCP Registry Violation: {Violation}", stacklevel=2)

FILE: agentic_core\L2_execution\config\mcp_registry.py
--------------------------------------------------------------------------------
  Line 4: Sovereign MCP Registry – Phase 13 (Dec 26, 2025)
  Line 7: This registry enforces:
  Line 47: # Base registry without conditional entries
  Line 48: _BASE_MCP_REGISTRY: dict[str, McpServerConfig] = {
  Line 77: description="Real-time web search for L2 tool execution",
  Line 134: def get_mcp_registry() -> dict[str, McpServerConfig]:
  Line 135: """Get the full MCP registry with conditional entries."""
  Line 137: registry = _BASE_MCP_REGISTRY.copy()
  Line 141: registry["redis"] = McpServerConfig(
  Line 153: return registry
  Line 157: SOVEREIGN_MCP_REGISTRY = get_mcp_registry()
  Line 162: return [mcp for mcp in get_mcp_registry().values() if mcp.target_layer == layer]
  Line 167: return [mcp for mcp in get_mcp_registry().values() if capability in mcp.capabilities]
  Line 173: def validate_mcp_registry() -> list[str]:
  Line 174: """Validate MCP registry for constitutional compliance."""
  Line 176: for name, config in get_mcp_registry().items():
  Line 184: _violations = validate_mcp_registry()
  Line 189: warnings.warn(f"MCP Registry Violation: {Violation}", stacklevel=2)

FILE: agentic_core\L2_execution\config\mcp_registry_config.py
--------------------------------------------------------------------------------
  Line 4: Sovereign MCP Registry – Phase 13 (Dec 26, 2025)
  Line 7: This registry enforces:
  Line 47: # Base registry without conditional entries
  Line 48: _BASE_MCP_REGISTRY: dict[str, McpServerConfig] = {
  Line 77: description="Real-time web search for L2 tool execution",
  Line 134: def get_mcp_registry() -> dict[str, McpServerConfig]:
  Line 135: """Get the full MCP registry with conditional entries."""
  Line 137: registry = _BASE_MCP_REGISTRY.copy()
  Line 141: registry["redis"] = McpServerConfig(
  Line 153: return registry
  Line 157: SOVEREIGN_MCP_REGISTRY = get_mcp_registry()
  Line 162: return [mcp for mcp in get_mcp_registry().values() if mcp.target_layer == layer]
  Line 167: return [mcp for mcp in get_mcp_registry().values() if capability in mcp.capabilities]
  Line 173: def validate_mcp_registry() -> list[str]:
  Line 174: """Validate MCP registry for constitutional compliance."""
  Line 176: for name, config in get_mcp_registry().items():
  Line 184: _violations = validate_mcp_registry()
  Line 189: warnings.warn(f"MCP Registry Violation: {Violation}", stacklevel=2)

FILE: agentic_core\L2_execution\config\transform_config.py
--------------------------------------------------------------------------------
  Line 6: Phase 1 Tool: Enables agents to perform safe, deterministic code transformations

FILE: agentic_core\L2_execution\config\unified_workflow_config.py
--------------------------------------------------------------------------------
  Line 125: """Coordinates execution-focused missions (tool calls, actions, operations)."""
  Line 448: required_permission="TOOL:READ",

FILE: agentic_core\L2_execution\enforcement\capability_chokepoint.py
--------------------------------------------------------------------------------
  Line 65: tool_name: Name of the tool being invoked.

FILE: agentic_core\L2_execution\enforcement\capability_chokepoint_gate.py
--------------------------------------------------------------------------------
  Line 65: tool_name: Name of the tool being invoked.

FILE: agentic_core\L2_execution\enforcement\preventative_sandbox.py
--------------------------------------------------------------------------------
  Line 47: # Exhaustive write-vector registry

FILE: agentic_core\L2_execution\enforcement\SovereignLLMGateway.py
--------------------------------------------------------------------------------
  Line 13: [PHASE 21 HARDENING] Tool Adapter Layer (Dict -> SDK Type Casting).
  Line 462: """Call Google Gemini API with Phase 13 generation_config support and Phase 21 tool adapter."""
  Line 470: # [PHASE 21] Tool Adapter: Handle Pure Dicts from tool_registry

FILE: agentic_core\L2_execution\enforcement\sovereign_filesystem_mcp.py
--------------------------------------------------------------------------------
  Line 6: [SSOT] Root prefixes derived from SOVEREIGN_REGISTRY in structure_blueprint.py
  Line 15: SOVEREIGN_REGISTRY = {
  Line 24: # [SSOT] Sovereign territory boundaries derived from SOVEREIGN_REGISTRY
  Line 26: allowed_root_prefixes = set(SOVEREIGN_REGISTRY.keys()) | {"config"}  # config is a subfolder, add explicitly
  Line 65: # We use the official MCP 'read_file' tool for auditable access
  Line 66: result = await self.manager.call_tool("read_file", {"path": safe_path})
  Line 84: result = await self.manager.call_tool("write_file", {"path": path, "content": content})
  Line 115: await self.manager.call_tool("roots_update", {"roots": validated})

FILE: agentic_core\L2_execution\enforcement\sovereign_filesystem_mcp_enforcer.py
--------------------------------------------------------------------------------
  Line 6: [SSOT] Root prefixes derived from SOVEREIGN_REGISTRY in structure_blueprint.py
  Line 15: SOVEREIGN_REGISTRY = {
  Line 24: # [SSOT] Sovereign territory boundaries derived from SOVEREIGN_REGISTRY
  Line 26: allowed_root_prefixes = set(SOVEREIGN_REGISTRY.keys()) | {"config"}  # config is a subfolder, add explicitly
  Line 65: # We use the official MCP 'read_file' tool for auditable access
  Line 66: result = await self.manager.call_tool("read_file", {"path": safe_path})
  Line 84: result = await self.manager.call_tool("write_file", {"path": path, "content": content})
  Line 115: await self.manager.call_tool("roots_update", {"roots": validated})

FILE: agentic_core\L2_execution\enforcement\tool_policy_enforcer.py
--------------------------------------------------------------------------------
  Line 2: §Wave2.4 — ToolPolicyEnforcer: LawSlot enforcement gate for tool calls.
  Line 5: tool execution. Default behavior is PASS with empty slots if no policy
  Line 27: """Compute deterministic SHA-256 hash of tool arguments.
  Line 39: Resolves applicable law slots for a given tool + context and returns
  Line 59: """Register a policy rule for a specific tool.
  Line 75: """Resolve applicable law slot IDs for this tool + context."""
  Line 87: """Enforce policy for a tool call.

FILE: agentic_core\L2_execution\engines\action_node.py
--------------------------------------------------------------------------------
  Line 6: Handles tool selection, execution, and output formatting.
  Line 18: Sub-atomic action node - tool execution and output generation.
  Line 143: # Simple tool selection based on plan steps
  Line 147: # Primary tool
  Line 152: # Secondary tool for complex plans
  Line 167: Tool execution results
  Line 171: for tool in tools:
  Line 173: "tool": tool["name"],
  Line 175: "output": f"Executed {tool['name']}",
  Line 177: "type": tool.get("type", "unknown"),
  Line 178: "priority": tool.get("priority", 0),
  Line 187: Format final output from tool results.
  Line 190: results: Tool execution results

FILE: agentic_core\L2_execution\engines\action_node_core.py
--------------------------------------------------------------------------------
  Line 38: allowed_tools (Dict[str, Any]): Map of tool names to implementations
  Line 72: Parses a single step, validates the tool, and executes it.
  Line 86: msg = f"[X] Tool '{action_name}' (mapped to '{tool_key}') is NOT whitelisted or recognized."
  Line 89: Logger.info(f"🔨 Executing Tool '{tool_key}' for step {step_number} with params: {params}")
  Line 94: Logger.error(f"[X] Tool '{tool_key}' execution failed for step {step_number}: {e}", exc_info=True)

FILE: agentic_core\L2_execution\engines\execute_command_executor.py
--------------------------------------------------------------------------------
  Line 211: Check if a tool is installed and available.
  Line 214: tool_name: Name of the tool to check
  Line 217: True if tool is installed, False otherwise
  Line 231: def run_linter(tool: str, target_path: str = ".", extra_args: list[str] | None = None) -> tuple[bool, str]:
  Line 233: Run a linter tool on the codebase.
  Line 235: tool: Linter tool name ('isort', 'autoflake', 'black', 'flake8', 'mypy')
  Line 242: if not check_tool_installed(tool):
  Line 243: return (False, f"{tool} is not installed")
  Line 244: command: Any = ALLOWED_COMMANDS.get(tool, [tool])[0]
  Line 266: Dictionary of tool results

FILE: agentic_core\L2_execution\engines\secure_tools_impl.py
--------------------------------------------------------------------------------
  Line 18: Secure tool implementations with path validation and command blacklisting.
  Line 119: WARNING: This tool is highly dangerous. In a production environment,

FILE: agentic_core\L2_execution\engines\tool_intent_executor.py
--------------------------------------------------------------------------------
  Line 147: f"tool '{intent.tool_name}' requires commit sandbox "

FILE: agentic_core\L2_execution\engines\tool_registry.py
--------------------------------------------------------------------------------
  Line 4: Dynamic Tool Registry for Runtime Tool Discovery
  Line 28: """Definition of a tool in the registry."""
  Line 47: """A matched tool for a Task."""
  Line 49: tool: ToolDefinition
  Line 58: class tool_registry:
  Line 60: Dynamic tool registry that enables agents to discover tools at runtime.
  Line 62: Uses semantic similarity to match Task descriptions to tool capabilities.
  Line 67: Initialize the tool registry.
  Line 71: enable_caching: Whether to cache tool embeddings
  Line 78: LOGGER.info("Tool registry initialized")
  Line 90: Register a tool in the registry.
  Line 93: name: Unique tool name
  Line 94: func: The tool function
  Line 95: description: What the tool does
  Line 98: category: Tool category
  Line 101: LOGGER.warning(f"Tool {name} already registered, overwriting")
  Line 106: tool: Any = ToolDefinition(
  Line 114: self.tools[name] = tool
  Line 115: LOGGER.info(f"Registered tool: {name} ({category})")
  Line 143: tool: Any = self.tools[tool_name]
  Line 144: if categories and tool.category not in categories:
  Line 151: reason: Any = self._generate_match_reason(task_description, tool, similarity)
  Line 152: matches.append(ToolMatch(tool=tool, relevance_score=similarity, reason=reason))
  Line 157: """Ensure tool embeddings are computed."""
  Line 160: LOGGER.debug("Computing tool embeddings...")
  Line 163: for tool in self.tools.values():
  Line 164: searchable_text = f"{tool.name} {tool.description} {' '.join(tool.tags)}"
  Line 167: tool_names.append(tool.name)
  Line 168: tool.embedding = embedding
  Line 173: def _generate_match_reason(self, Task: str, tool: ToolDefinition, similarity: float) -> str:
  Line 174: """Generate a reason why this tool matches the Task."""
  Line 176: desc_lower = tool.description.lower()
  Line 177: name_lower = tool.name.lower()
  Line 183: if "file" in task_lower and tool.category == "filesystem":
  Line 184: reasons.append("file operation tool")
  Line 185: elif "api" in task_lower and tool.category == "network":
  Line 186: reasons.append("API communication tool")
  Line 187: elif "data" in task_lower and tool.category == "analysis":
  Line 188: reasons.append("data analysis tool")
  Line 195: Get natural language tool recommendations for a Task.
  Line 209: tool: Any = match.tool
  Line 210: Recommendation += f"{i}. {tool.name}\n"
  Line 211: Recommendation += f"   Description: {tool.description}\n"
  Line 214: if tool.parameters:
  Line 215: Recommendation += f"   Parameters: {json.dumps(tool.parameters, indent=6)}\n"
  Line 220: """Get a tool by name."""
  Line 233: """Update tool usage statistics."""
  Line 235: tool: Any = self.tools[name]
  Line 236: tool.usage_count += 1
  Line 239: tool.success_rate = tool.success_rate * (1 - alpha) + 1 * alpha
  Line 241: tool.success_rate = tool.success_rate * (1 - alpha) + 0 * alpha
  Line 265: """Get registry statistics."""
  Line 267: for tool in self.tools.values():
  Line 268: categories_count[tool.category] = categories_count.get(tool.category, 0) + 1
  Line 288: """AST tool — analyze Python code for patterns (e.g., snake_case classes).
  Line 339: # CODE TRANSFORMATION ENGINE (CTE) — Phase 1 Tool
  Line 346: Deterministic AST-based code transformation tool.
  Line 382: # DEPENDENCY GRAPH ANALYZER (DGA) — Phase 2 Tool
  Line 398: Dependency graph analysis tool for import/call relationships.
  Line 431: # DIFF/PATCH GENERATOR (DPG) — Phase 2 Tool
  Line 438: Diff/patch generation tool for reviewable changes.
  Line 464: def create_tool_registry(embedder: Any, enable_caching: bool = True) -> tool_registry:
  Line 466: Factory function to create a tool registry.
  Line 473: tool_registry instance
  Line 475: return tool_registry(embedder=embedder, enable_caching=enable_caching)

FILE: agentic_core\L2_execution\engines\validation_orchestrator.py
--------------------------------------------------------------------------------
  Line 4: - Verification registry management
  Line 54: - Verification registry with check functions for all Canon keys.
  Line 60: VERIFICATION_REGISTRY: Dict mapping Canon keys to check functions.
  Line 61: _registry_built: Flag indicating if registry has been initialized.
  Line 69: VERIFICATION_REGISTRY: dict[int, Any] = {}
  Line 70: _registry_built: bool = False
  Line 73: def _init_registry(cls, ctx: IValidationProtocol) -> None:
  Line 75: Build the verification registry once.
  Line 77: Initializes VERIFICATION_REGISTRY with check functions for all Canon keys.
  Line 83: if cls._registry_built:
  Line 86: # All imports and registry building have been removed
  Line 88: cls._registry_built = True
  Line 89: cls.VERIFICATION_REGISTRY = {}  # Empty - deprecated
  Line 253: self.__class__._init_registry(self.ctx)
  Line 254: check_func = self.VERIFICATION_REGISTRY.get(violation_key)
  Line 358: Iterates through the VERIFICATION_REGISTRY and runs all registered
  Line 413: for canon_key, check_func in self.VERIFICATION_REGISTRY.items():

FILE: agentic_core\L2_execution\reasoning\SovereignMCPGatewayAgent.py
--------------------------------------------------------------------------------
  Line 66: # Placeholder for actual MCP tool call logic
  Line 69: self.router.manager.call_tool if hasattr(self, "router") else self._mock_tool_call,
  Line 93: self.router.manager.call_tool if hasattr(self, "router") else self._mock_tool_call,
  Line 116: self.router.manager.call_tool if hasattr(self, "router") else self._mock_tool_call,
  Line 131: return {"status": "success", "mock": True, "tool": tool_name}

FILE: agentic_core\L2_execution\reasoning\SubAtomicRegistryAgent.py
--------------------------------------------------------------------------------
  Line 13: SubAtomicRegistry - Live Semantic Index of Every Method
  Line 51: # UNIFIED AGENT MAPPING (Post-Consolidation Registry)
  Line 242: from agentic_core.L0_routing.utils.subprocess_runner_util import invoke_code_validator
  Line 245: self._invoke = invoke_code_validator
  Line 249: return self._invoke(action="validate", project_root=self.project_root)
  Line 254: return self._invoke(
  Line 266: # Unified Structure Validator (L5) - Gravity/Hygiene/Registry
  Line 270: "AgentRegistryValidatorAgent": StructureValidatorAgent,
  Line 296: Logger.info(f"Registry: Mapping legacy agent '{agent_id}' to Unified Class (Phase 1).")
  Line 303: Logger.info(f"Registry: Mapping legacy validator '{agent_id}' to Unified Class (Phase 2).")
  Line 312: Logger.info(f"Registry: Mapping legacy manager/enforcer '{agent_id}' to Unified Class (Phase 3).")
  Line 322: f"Registry: Mapping legacy detector/healer/router/executor '{agent_id}' to Unified Class (Phase 4).",
  Line 328: raise ValueError(f"Agent ID '{agent_id}' not found in unified agent registry.")
  Line 342: class SubAtomicRegistryAgent(SovereignBaseAgent):
  Line 344: Sovereign method registry — live, hybrid-indexed, eternal.
  Line 398: def rebuild_registry(self) -> Any:
  Line 400: print("   [REBUILD] SubAtomicRegistry: Indexing all methods...")
  Line 418: print(f"   [OK] SubAtomicRegistry: Indexed {len(vectors)} methods + cache Warmed")
  Line 451: def find_and_invoke(self, task_description: str, *args, **kwargs) -> Any:
  Line 463: def invoke_method(self, method_meta: dict, *args, **kwargs) -> Any:
  Line 464: """Dynamically invoke a method by metadata"""
  Line 480: print(f"   [ERROR] Failed to invoke {method_meta['method']}: {e}")
  Line 487: print(f"   [OK] SubAtomicRegistry: {count} methods online and searchable.")
  Line 489: ctx.report("Registry", count, True, "Method capabilities mapped.")
  Line 522: Heal violations detected by SubAtomicRegistryAgent.
  Line 540: # Default implementation - SubAtomicRegistryAgent manages sub-atomic registry
  Line 544: "details": f"SubAtomicRegistryAgent heal() not yet implemented for {violation_type}",
  Line 551: "details": f"SubAtomicRegistryAgent heal() failed: {str(e)}",

FILE: agentic_core\L2_execution\reasoning\ToolsmithAgent.py
--------------------------------------------------------------------------------
  Line 10: ToolsmithAgent - L2 Tool Creation Agent
  Line 27: class ToolSpec:
  Line 28: """Specification for a tool."""
  Line 52: """A dynamically generated tool."""
  Line 54: spec: ToolSpec
  Line 75: CLASS_TEMPLATE: Any = '\nclass {name}:\n    """\n    {description}\n    """\n\n    def __init__(self{init_params}) -> None:\n        """Initialize the {name} tool."""\n{init_body}\n    async def execute{method_params} -> {return_type}:\n        """\n        Execute the tool.\n\n        Args:\n{method_param_docs}\n        Returns:\n            {return_description}\n        """\n        # Implementation\n        {method_implementation}\n'
  Line 87: - Validates tool implementations
  Line 88: - Manages tool registry
  Line 89: - Provides tool templates
  Line 108: """Load tool generation templates."""
  Line 141: def create_tool_from_spec(self, spec: ToolSpec) -> GeneratedTool:
  Line 143: Create a tool from a specification.
  Line 146: spec: Tool specification
  Line 149: Generated tool
  Line 158: tool: Any = GeneratedTool(
  Line 165: self.tools[spec.name] = tool
  Line 166: Logger.info(f"Created tool: {spec.name}")
  Line 167: return tool
  Line 169: def _is_simple_function(self, spec: ToolSpec) -> bool:
  Line 170: """Check if tool should be a simple function."""
  Line 173: def _generate_function_code(self, spec: ToolSpec) -> str:
  Line 174: """Generate function code for a tool."""
  Line 198: def _generate_class_code(self, spec: ToolSpec) -> str:
  Line 199: """Generate class code for a complex tool."""
  Line 222: def _get_implementation(self, spec: ToolSpec) -> str:
  Line 223: """Get implementation code based on tool category and name."""
  Line 234: return '    # TODO: Implement tool logic\n    raise NotImplementedError("Tool implementation pending")'
  Line 264: def _generate_test_code(self, spec: ToolSpec) -> str:
  Line 265: """Generate test code for the tool."""
  Line 267: return f'\nasync def {test_name}():\n    """Test the {spec.name} tool."""\n    # TODO: Implement test\n    pass\n'
  Line 271: Create a file manipulation tool.
  Line 274: name: Tool name
  Line 278: Generated tool
  Line 280: spec: Any = ToolSpec(
  Line 291: Create an API interaction tool.
  Line 294: name: Tool name
  Line 299: Generated tool
  Line 301: spec: Any = ToolSpec(
  Line 319: """Get a registered tool by name."""
  Line 330: List of tool specifications
  Line 333: for tool in self.tools.values():
  Line 334: if category is None or tool.spec.category == category:
  Line 335: tools.append(tool.spec.to_dict())
  Line 340: Save a tool to file.
  Line 343: name: Tool name
  Line 349: tool: Any = self.get_tool(name)
  Line 350: if not tool:
  Line 356: f.write(tool.code)
  Line 357: if tool.test_code:
  Line 360: f.write(tool.test_code)
  Line 363: json.dump(tool.spec.to_dict(), f, indent=2)
  Line 364: Logger.info(f"Saved tool {name} to {directory}")
  Line 369: """Get tool creation statistics."""
  Line 376: for tool in self.tools.values():
  Line 377: cat: Any = tool.spec.category
  Line 379: if tool.test_code:
  Line 396: Wired Toolsmith Healing - Validates tool specifications and repairs broken tool files.
  Line 399: - validate_tool_specs(): Checks JSON/YAML tool definitions for schema compliance.
  Line 400: - _reconcile_tool_files(): Ensures tool Python files match their registered specs.
  Line 423: # 2. Python Tool File Reconciliation
  Line 429: # 3. Commit logic for tool generation
  Line 565: """Create a file manipulation tool."""
  Line 571: """Create an API interaction tool."""

FILE: agentic_core\L2_execution\scripts\remediation_dispatcher.py
--------------------------------------------------------------------------------
  Line 30: from agentic_core.L2_execution.types.healer_registry_types import HEALER_REGISTRY
  Line 285: - If roll-up check_id itself exists in HEALER_REGISTRY, include it.
  Line 286: - Also include extracted sub-items where sub_check_id exists in HEALER_REGISTRY.
  Line 298: if rollup_id in HEALER_REGISTRY and rollup_id not in seen:
  Line 303: if sub_id in HEALER_REGISTRY and sub_id not in seen:
  Line 340: def _invoke_healer(
  Line 347: """Invoke a registered healer safely, converting errors to FAILED results.
  Line 353: healer_fn = HEALER_REGISTRY[check_id]
  Line 475: if cid in HEALER_REGISTRY:
  Line 481: _invoke_healer(cid, check_dict, repo_root=repo_root, apply=apply),

FILE: agentic_core\L2_execution\tools\figma_mcp_client.py
--------------------------------------------------------------------------------
  Line 4: MCP Tool Stubs - Planned Feature Integration
  Line 7: Stub implementations for MCP-powered tool integrations.
  Line 8: Provides Figma, Pinecone, and Memory MCP tool stubs for testing.
  Line 16: EXTRACTED: From action_registry.py via Atomic Fission Protocol
  Line 17: TOOL ID PREFIX: ACT-012+
  Line 22: Logger: Any = logging.getLogger("ActionRegistry.MCPStubs")
  Line 28: Tool ID Prefix: ACT-012
  Line 37: Tool ID: ACT-012
  Line 44: str: A message indicating the tool is not implemented.
  Line 52: Tool ID: ACT-013
  Line 59: str: A message indicating the tool is not implemented.
  Line 67: Tool ID: ACT-014
  Line 74: str: A message indicating the tool is not implemented.
  Line 83: Tool ID Prefix: ACT-015
  Line 92: Tool ID: ACT-015
  Line 99: str: A message indicating the tool is not implemented.
  Line 108: Tool ID Prefix: ACT-016
  Line 117: Tool ID: ACT-016
  Line 123: str: A message indicating the tool is not implemented.
  Line 131: Tool ID: ACT-017
  Line 137: str: A message indicating the tool is not implemented.

FILE: agentic_core\L2_execution\tools\file_io_impl.py
--------------------------------------------------------------------------------
  Line 5: Extracted from action_registry.py via Atomic Fission Protocol
  Line 6: Tool ID Prefix: ACT-002
  Line 16: Logger: Any = logging.getLogger("ActionRegistry.FileIO")
  Line 22: Tool ID Prefix: ACT-002
  Line 90: Tool ID: ACT-002
  Line 109: Tool ID: ACT-003

FILE: agentic_core\L2_execution\tools\git_ops_impl.py
--------------------------------------------------------------------------------
  Line 5: Extracted from action_registry.py via Atomic Fission Protocol
  Line 6: Tool ID Prefix: ACT-010
  Line 11: Logger: Any = logging.getLogger("ActionRegistry.GitTools")
  Line 17: Tool ID Prefix: ACT-010
  Line 26: Tool ID: ACT-010
  Line 59: Tool ID: ACT-011

FILE: agentic_core\L2_execution\tools\time_utils_impl.py
--------------------------------------------------------------------------------
  Line 5: Extracted from action_registry.py via Atomic Fission Protocol
  Line 6: Tool ID Prefix: ACT-008
  Line 11: Logger: Any = logging.getLogger("ActionRegistry.TimeTools")
  Line 17: Tool ID Prefix: ACT-008
  Line 53: Tool ID: ACT-008
  Line 76: Tool ID: ACT-009

FILE: agentic_core\L2_execution\tools\tool_chain_executor.py
--------------------------------------------------------------------------------
  Line 12: Main executor class for tools use a tool operations.

FILE: agentic_core\L2_execution\tools\tool_verifier_impl.py
--------------------------------------------------------------------------------
  Line 4: Tool Verification Loop - The "Compiler Check"
  Line 22: """Result of tool verification."""
  Line 41: """Complete verification report for a tool call."""
  Line 51: Verifies tool calls and code before execution.
  Line 58: Initialize the tool verifier.
  Line 67: LOGGER.info(f"Tool verifier initialized (strict_mode={self.strict_mode})")
  Line 99: tool: [re.compile(pattern) for pattern in patterns]
  Line 100: for tool, patterns in self.tool_requirements.items()
  Line 110: Verify a tool call before execution.
  Line 113: tool_name: Name of the tool to call
  Line 114: tool_args: Arguments for the tool
  Line 144: LOGGER.info(f"Tool verification: {tool_name} -> {result.value} ({len(issues)} issues)")
  Line 157: """Basic validation of tool call structure."""
  Line 160: issues.append(VerificationIssue(Severity="error", message="Invalid tool name"))
  Line 165: message="file_read tool requires 'path' argument",
  Line 166: suggestion="Add 'path' argument to tool call",
  Line 173: message="file_write tool requires 'path' and 'content' arguments",
  Line 174: suggestion="Add Missing arguments to tool call",
  Line 250: """Tool-specific verification logic."""
  Line 319: plan_parts = [f"Tool: {tool_name}"]
  Line 344: Factory function to create a tool verifier.

FILE: agentic_core\L2_execution\tools\web_search_client.py
--------------------------------------------------------------------------------
  Line 6: Tool ID Prefix: ACT-001
  Line 14: Logger: Any = logging.getLogger("ActionRegistry.WebSearch")
  Line 21: Tool ID Prefix: ACT-001
  Line 44: result: Any = await self.router.manager.call_tool(
  Line 74: result: Any = await self.router.manager.call_tool(

FILE: agentic_core\L2_execution\tools\write_gateway.py
--------------------------------------------------------------------------------
  Line 8: Tool ID Prefix: ACT-010

FILE: agentic_core\L2_execution\types\capability_token_types.py
--------------------------------------------------------------------------------
  Line 28: "TOOL_READ": "TOOL:READ",
  Line 29: "TOOL_WRITE": "TOOL:WRITE",
  Line 195: Emitted for every tool invocation (both ALLOW and DENY).
  Line 322: tool_name: Name of the tool being invoked.
  Line 418: ALL_PERMISSION_VALUES, e.g. "TOOL:READ").  Sorted automatically.

FILE: agentic_core\L2_execution\types\healer_registry.py
--------------------------------------------------------------------------------
  Line 2: Healer Registry — Declarative mapping of check_id to healer function.
  Line 32: HEALER_REGISTRY: dict[str, HealerFn] = {
  Line 42: __all__ = ["HealerFn", "HEALER_REGISTRY"]

FILE: agentic_core\L2_execution\types\healer_registry_types.py
--------------------------------------------------------------------------------
  Line 2: Healer Registry — Declarative mapping of check_id to healer function.
  Line 32: HEALER_REGISTRY: dict[str, HealerFn] = {
  Line 42: __all__ = ["HealerFn", "HEALER_REGISTRY"]

FILE: agentic_core\L2_execution\types\heal_contract.py
--------------------------------------------------------------------------------
  Line 162: tool_id: Constant identifier for the tool that produced the result.

FILE: agentic_core\L2_execution\types\heal_contract_types.py
--------------------------------------------------------------------------------
  Line 162: tool_id: Constant identifier for the tool that produced the result.

FILE: agentic_core\L2_execution\types\l2_phase_spec.py
--------------------------------------------------------------------------------
  Line 31: healer_ids: Healer IDs to invoke during this phase (empty for now).

FILE: agentic_core\L2_execution\types\l2_phase_spec_types.py
--------------------------------------------------------------------------------
  Line 31: healer_ids: Healer IDs to invoke during this phase (empty for now).

FILE: agentic_core\L2_execution\types\llm_replay_types.py
--------------------------------------------------------------------------------
  Line 28: DETERMINISTIC_INFERENCE: Dev/test only. Re-invokes the LLM

FILE: agentic_core\L2_execution\types\mcp_client_types.py
--------------------------------------------------------------------------------
  Line 1: """MCP client specifications and registry.
  Line 151: class MCPClientRegistry:
  Line 152: """Registry for managing MCP clients.
  Line 159: """Initialize empty registry."""

FILE: agentic_core\L2_execution\types\mcp_error_types.py
--------------------------------------------------------------------------------
  Line 25: """Raised when a requested MCP client is not found in registry."""

FILE: agentic_core\L2_execution\types\mcp_security_types.py
--------------------------------------------------------------------------------
  Line 11: - tool_validation: MCP tool security
  Line 46: - Tool whitelist validation
  Line 59: # Tool whitelist
  Line 98: Validate MCP tool call.
  Line 101: tool_name: Name of tool
  Line 102: args: Tool arguments
  Line 110: # Check tool whitelist
  Line 118: description=f"Tool '{tool_name}' not in whitelist",
  Line 141: """Check if tool is in whitelist."""
  Line 197: """Add tool to whitelist."""
  Line 201: """Remove tool from whitelist."""

FILE: agentic_core\L2_execution\types\mcp_tool_types.py
--------------------------------------------------------------------------------
  Line 3: """MCP Tool Server Integration.
  Line 5: Provides MCP (Model Context Protocol) tool server integration
  Line 6: for external tool access and context providers.
  Line 25: """MCP tool definition."""
  Line 37: OpenAI-compatible tool definition
  Line 49: """Convert to Anthropic tool format.
  Line 52: Anthropic-compatible tool definition
  Line 63: """Result from MCP tool execution."""
  Line 73: """MCP tool server for managing and executing tools."""
  Line 81: """Initialize MCP tool server.
  Line 92: Logger.info(f"MCP tool server initialized: {name}")
  Line 115: def register_tool(self, tool: MCPTool) -> None:
  Line 116: """Register a tool.
  Line 119: tool: MCP tool to register
  Line 121: self._tools[tool.name] = tool
  Line 122: Logger.info(f"Registered MCP tool: {tool.name}")
  Line 132: """Register a function as an MCP tool.
  Line 135: name: Tool name
  Line 136: description: Tool description
  Line 139: requires_approval: Whether tool requires approval
  Line 141: tool = MCPTool(
  Line 148: self.register_tool(tool)
  Line 151: """Get a tool by name.
  Line 154: name: Tool name
  Line 162: """List all registered tool names.
  Line 165: List of tool names
  Line 179: List of tool definitions
  Line 183: for tool in self._tools.values():
  Line 185: tools.append(tool.to_anthropic_format())
  Line 187: tools.append(tool.to_openai_format())
  Line 199: """Execute a tool.
  Line 201: §Wave2.4: All tool calls pass through the LawSlotHandler enforcement
  Line 209: name: Tool name
  Line 210: arguments: Tool arguments
  Line 217: ToolPolicyBlocked: If enforcement blocks the tool call
  Line 220: tool = self.get_tool(name)
  Line 222: if not tool:
  Line 227: error=f"Tool not found: {name}",
  Line 239: resource_path = f"tool/{name}"
  Line 327: result = tool.handler(**effective_args)
  Line 337: Logger.error(f"Tool execution failed for {name}: {e}")
  Line 347: # Global MCP tool server instance
  Line 352: """Get or create global MCP tool server.
  Line 372: server: MCP tool server
  Line 375: # Calculator tool
  Line 415: # Text analysis tool
  Line 451: """Factory function to create MCP tool server.
  Line 482: """§Wave5.0.3 — Integration seam: issue token + execute tool in one call.
  Line 490: name: Tool name
  Line 491: arguments: Tool arguments
  Line 496: permissions: Permission code values (e.g. ["TOOL:READ"])
  Line 528: """Execute multiple tool calls.
  Line 533: server: MCP tool server
  Line 534: tool_calls: List of tool call definitions

FILE: agentic_core\L2_execution\types\tool_args_types.py
--------------------------------------------------------------------------------
  Line 2: Tool Registry Definitions - Phase 21.1 Restoration
  Line 4: Provides Pydantic models for tool argument validation.
  Line 5: These are used by the tool_registry to validate tool calls.

FILE: agentic_core\L2_execution\types\tool_enforcement_types.py
--------------------------------------------------------------------------------
  Line 2: §Wave2.4 — Tool Enforcement Artifact Types.
  Line 4: Typed artifacts for the LawSlotHandler enforcement gate at tool choke points.
  Line 15: """§Wave2.4 — Enforcement outcomes at the tool choke point."""
  Line 24: """§Wave2.4 — Enforcement record emitted exactly once per tool call.
  Line 62: """§Wave2.4 — Raised when a tool call is blocked by enforcement policy.
  Line 71: super().__init__(f"Tool '{tool_name}' blocked by policy: {rationale}")

FILE: agentic_core\L2_execution\types\tool_intent.py
--------------------------------------------------------------------------------
  Line 2: Phase 7 — ToolIntent: declarative tool emission from L1 + L1 mutation blocker.
  Line 4: L1 cognition MUST NOT directly invoke mutating tools.
  Line 27: # Tool Capability Model
  Line 33: Capability class of a tool.
  Line 68: Raised when L1 attempts a direct mutating tool call, or when a ToolIntent
  Line 99: and the tool has a MUTATING_* capability.
  Line 101: Call this at the top of any tool invocation seam.
  Line 104: detail = f"tool '{tool_name}' has capability {capability.value}; emit ToolIntent instead"
  Line 117: Inside this scope, any direct call to a MUTATING_* tool raises ToolViolation.
  Line 137: Declarative tool intent emitted by L1 cognition.
  Line 142: tool_name      : str   — non-empty tool identifier
  Line 144: args           : dict  — JSON-serializable tool arguments
  Line 231: Factory: build a ToolIntent from tool parameters.

FILE: agentic_core\L2_execution\utils\archive_util.py
--------------------------------------------------------------------------------
  Line 12: from .client import MCPClientRegistry, MCPClientSpec, MCPClientStub
  Line 145: def create_mcp_registry(
  Line 148: ) -> MCPClientRegistry:
  Line 149: """Create an MCP client registry from specifications.
  Line 156: Populated MCPClientRegistry
  Line 161: registry = MCPClientRegistry()
  Line 166: registry.register(spec, client)
  Line 173: registry.register(spec, stub)
  Line 175: return registry

FILE: agentic_core\L2_execution\utils\deterministic_cleaner_util.py
--------------------------------------------------------------------------------
  Line 52: """Check if a formatting tool is available."""

FILE: agentic_core\L2_execution\utils\factory_util.py
--------------------------------------------------------------------------------
  Line 10: from .client import MCPClientRegistry, MCPClientSpec, MCPClientStub
  Line 143: def create_mcp_registry(
  Line 146: ) -> MCPClientRegistry:
  Line 147: """Create an MCP client registry from specifications.
  Line 154: Populated MCPClientRegistry
  Line 159: registry = MCPClientRegistry()
  Line 164: registry.register(spec, client)
  Line 171: registry.register(spec, stub)
  Line 173: return registry

FILE: agentic_core\L2_execution\utils\tool_registry_util.py
--------------------------------------------------------------------------------
  Line 2: Tool Registry - Centralized SSOT for all tools.
  Line 19: class ToolRegistry:
  Line 26: - Integration with SovereignIndex for tool discovery
  Line 30: _instance: Optional["ToolRegistry"] = None
  Line 33: def __new__(cls) -> "ToolRegistry":
  Line 40: def get_instance(cls) -> "ToolRegistry":
  Line 41: """Get the singleton instance of ToolRegistry."""
  Line 60: Registers a tool only after verifying its location is sovereign.
  Line 63: tool_name: Unique identifier for the tool
  Line 64: tool_path: Path to the tool file (absolute or relative)
  Line 65: tool_func: The callable function/method for the tool
  Line 66: description: Optional description of the tool
  Line 80: f"[REGISTRY] REJECTED: Tool '{tool_name}' at {tool_path} is outside project root.",
  Line 90: f"[REGISTRY] REJECTED: Tool '{tool_name}' at {tool_path} "
  Line 98: f"[REGISTRY] REJECTED: Tool '{tool_name}' at {tool_path} is outside Sovereign Territory.",
  Line 102: # Register the tool
  Line 109: Logger.info(f"[REGISTRY] SUCCESS: Tool '{tool_name}' registered and verified.")
  Line 113: Logger.error(f"[REGISTRY] ERROR: Failed to register tool '{tool_name}': {e}")
  Line 118: Removes a tool from the registry.
  Line 121: tool_name: Name of the tool to remove
  Line 128: Logger.info(f"[REGISTRY] Tool '{tool_name}' unregistered.")
  Line 134: Retrieves a registered tool by name.
  Line 137: tool_name: Name of the tool to retrieve
  Line 140: Tool dict with path, func, verified, description or None
  Line 146: Retrieves just the callable function for a tool.
  Line 149: tool_name: Name of the tool
  Line 152: The tool's callable function or None
  Line 154: tool = self._tools.get(tool_name)
  Line 155: return tool["func"] if tool else None
  Line 158: """Returns list of all registered tool names."""
  Line 162: """Returns the complete tool registry."""
  Line 167: Uses SovereignIndex to discover tool files matching a pattern.
  Line 170: pattern: Glob pattern for tool files (default: *_tool.py)
  Line 174: List of discovered tool file paths
  Line 190: pattern: Glob pattern for tool files
  Line 207: Logger.warning(f"[REGISTRY] Failed to load tool from {tool_path}: {e}")
  Line 209: # Default: use filename as tool name, placeholder func
  Line 211: if self.register_tool(tool_name, str(tool_path), lambda: None, f"Tool from {tool_path.name}"):
  Line 215: f"[REGISTRY] Auto-registered {registered}/{len(discovered)} tools from pattern '{pattern}'",
  Line 227: tool_registry = ToolRegistry

FILE: agentic_core\L3_orchestration\enforcement\mission_runner.py
--------------------------------------------------------------------------------
  Line 168: """§8.1c — Invoke gateway.execute in LOG_ONLY mode for audit trail."""

FILE: agentic_core\L3_orchestration\enforcement\mission_runner_enforcer.py
--------------------------------------------------------------------------------
  Line 168: """§8.1c — Invoke gateway.execute in LOG_ONLY mode for audit trail."""

FILE: agentic_core\L3_orchestration\enforcement\safety_strategy.py
--------------------------------------------------------------------------------
  Line 92: invoke_code_validator,
  Line 98: self._invoke = invoke_code_validator
  Line 101: return self._invoke(action="validate", project_root=self.project_root)
  Line 105: return self._invoke(

FILE: agentic_core\L3_orchestration\engines\coordinator_capability_orchestrator.py
--------------------------------------------------------------------------------
  Line 139: class CoordinatorRegistry:
  Line 140: """Registry for workflow coordinators."""
  Line 143: """Initialize registry."""
  Line 175: """Get registry statistics."""
  Line 183: # Global registry
  Line 184: coordinator_registry = CoordinatorRegistry()

FILE: agentic_core\L3_orchestration\engines\dag_manager.py
--------------------------------------------------------------------------------
  Line 52: self.node_registry: Dict[str, SubatomicHop] = {}
  Line 53: self.function_registry: Dict[str, Callable] = {}
  Line 74: self.function_registry[name] = function
  Line 84: self.node_registry[hop.config.hop_id] = hop
  Line 177: return self.node_registry.get(hop_id)
  Line 188: if hop_id in self.node_registry:
  Line 189: hop = self.node_registry[hop_id]
  Line 205: if hop_id in self.node_registry:
  Line 206: hop = self.node_registry[hop_id]
  Line 221: "registered_functions": len(self.function_registry),

FILE: agentic_core\L3_orchestration\engines\decomposition_orchestrator.py
--------------------------------------------------------------------------------
  Line 77: _agent_registry: dict[str, Any] = field(default_factory=dict)
  Line 83: self._load_agent_registry()
  Line 86: def _load_agent_registry(self) -> None:
  Line 95: self._agent_registry[name] = agent
  Line 114: for agent_name, agent_data in self._agent_registry.items():
  Line 151: if agent in self._agent_registry:
  Line 155: agent_data = self._agent_registry.get(best_agent, {})

FILE: agentic_core\L3_orchestration\engines\orchestrator_engine.py
--------------------------------------------------------------------------------
  Line 201: # Agent registry for mission execution

FILE: agentic_core\L3_orchestration\engines\recursive_orchestrator.py
--------------------------------------------------------------------------------
  Line 203: # Try to get from node registry

FILE: agentic_core\L3_orchestration\engines\rl_coordinator_orchestrator.py
--------------------------------------------------------------------------------
  Line 9: 3. MCPCoordinator - Tool management
  Line 156: MCP Coordinator - Unified MCP/tool management.
  Line 173: tool_name = context.input_data.get("tool", "")
  Line 190: async def _route_tool(self, tool: str, context: WorkflowContext) -> dict:
  Line 191: """Route to appropriate tool."""
  Line 192: return {"tool": tool, "routed": True}
  Line 194: async def _verify_tool(self, tool: str, context: WorkflowContext) -> dict:
  Line 195: """Verify tool."""
  Line 196: self.verified_tools.add(tool)
  Line 197: return {"tool": tool, "verified": True}
  Line 207: description="MCP routing and tool verification",
  Line 208: workflow_types=["mcp", "tool", "mcp_route"],
  Line 214: return workflow_type.lower() in ["mcp", "tool", "mcp_route", "tool_verify"]
  Line 426: - AgentRegistryValidatorAgent
  Line 439: result = await self._validate_registry(context)
  Line 453: async def _validate_registry(self, context: WorkflowContext) -> dict:
  Line 454: """Validate agent registry."""
  Line 455: return {"registry": "valid", "agents": 0}
  Line 472: workflow_types=["governance", "permission", "registry"],
  Line 478: return workflow_type.lower() in ["governance", "permission", "registry", "policy"]
  Line 647: """Register all coordinators with the global registry."""
  Line 648: from .base_coordinator import coordinator_registry
  Line 664: coordinator_registry.register(coordinator)

FILE: agentic_core\L3_orchestration\engines\sovereign_mcp_router.py
--------------------------------------------------------------------------------
  Line 57: """Route canon key Violation to hardened MCP tool — L5 shielded"""
  Line 65: redteam_result: Any = await self.manager.call_tool(
  Line 77: "tool": "redteam_simulate",
  Line 86: memory_result: Any = await self.manager.call_tool(
  Line 92: "tool": "memory_search",
  Line 100: redis_result: Any = await self.manager.call_tool(
  Line 106: "tool": "redis_recover",
  Line 141: "tool": "figma_tokens",
  Line 163: reasoning_result: Any = await self.manager.call_tool(
  Line 186: "tool": "sequential_thinking",
  Line 193: PolicyResult: Any = await self.manager.call_tool(
  Line 199: "tool": "gemini_policy_enforcer",
  Line 204: cleanup_result: Any = await self.manager.call_tool(
  Line 213: "tool": "l0_cleanup",
  Line 219: diag_result: Any = await self.manager.call_tool("l0_diagnostics", {"scope": "repository"})
  Line 222: "tool": "l0_diagnostics",
  Line 227: structure: Any = await self.manager.call_tool(
  Line 236: content: Any = await self.manager.call_tool(
  Line 245: answer: Any = await self.manager.call_tool(
  Line 256: search_result: Any = await self.manager.call_tool(
  Line 265: "tool": "brave_search",
  Line 273: return await self.manager.call_tool(
  Line 279: Logger.error(f"[MCP FAILURE] Tool call failed for Key {key_id}: {e}")

FILE: agentic_core\L3_orchestration\reasoning\CoverageAgent.py
--------------------------------------------------------------------------------
  Line 218: # EXERCISER_REGISTRY is governance-specific - use default fallback
  Line 219: EXERCISER_REGISTRY = {
  Line 225: exerciser_class_name = EXERCISER_REGISTRY.get(layer, "GeneralExerciserAgent")

FILE: agentic_core\L3_orchestration\reasoning\NervousSystemAgent.py
--------------------------------------------------------------------------------
  Line 56: action_plane: The hands (tool execution)
  Line 564: tool_name=step.get("tool", "unknown"),

FILE: agentic_core\L3_orchestration\reasoning\OrchestrationHandshakeAgent.py
--------------------------------------------------------------------------------
  Line 62: self.registry = SubAtomicRegistry(project_root)
  Line 67: Discover agents/methods capable of Task via hybrid registry search.
  Line 77: results: Any = self.registry.find_method(Task, top_k=10)
  Line 107: Sovereign delegation — find best method and invoke.
  Line 251: result: Any = self.registry.invoke_method(method_meta, **{**args, **kwargs})
  Line 290: """Invoke healing chain via super()."""

FILE: agentic_core\L3_orchestration\reasoning\StateManagementAgent.py
--------------------------------------------------------------------------------
  Line 19: - Resource synchronization with registry agents
  Line 112: - Resource synchronization with registry agents
  Line 137: _registry_callbacks: list[Callable] = field(default_factory=list)
  Line 148: if not isinstance(self._registry_callbacks, list):
  Line 149: self._registry_callbacks = []
  Line 323: # Notify registry callbacks
  Line 324: self._notify_registry_update(key, "set")
  Line 382: # Notify registry callbacks
  Line 383: self._notify_registry_update(key, "delete")
  Line 607: # REGISTRY SYNCHRONIZATION
  Line 617: self._registry_callbacks.append(callback)
  Line 621: if callback in self._registry_callbacks:
  Line 622: self._registry_callbacks.remove(callback)
  Line 624: def _notify_registry_update(self, key: str, action: str) -> None:
  Line 626: for callback in self._registry_callbacks:
  Line 631: Logger.warning(f"Registry callback failed: {e}")

FILE: agentic_core\L3_orchestration\reasoning\SubatomicHopAgent.py
--------------------------------------------------------------------------------
  Line 73: genealogy: GenealogyRegistry instance (injected)
  Line 93: self.genealogy = self._ensure_dep(genealogy, "GenealogyRegistry")
  Line 127: f"SubatomicHop Missing critical tool: {name}. Orchestration layer must inject this dependency to maintain Gravity Compliance.",
  Line 356: results.append({"tool": "sandbox", "result": result})
  Line 358: result = await self.mcp.call_tool(tool_name, tool_args)
  Line 361: results.append({"tool": tool_name, "result": result})
  Line 370: PAYLOAD={"tool": tool_name, "error": str(e)},

FILE: agentic_core\L3_orchestration\scripts\guardian_heal_orchestrator.py
--------------------------------------------------------------------------------
  Line 79: invokes the dispatcher and returns the CombinedHealResult as dict.

FILE: agentic_core\L3_orchestration\types\forward_rolling_types.py
--------------------------------------------------------------------------------
  Line 267: # Invoke callback

FILE: agentic_core\L3_orchestration\types\recursion_monitor_types.py
--------------------------------------------------------------------------------
  Line 439: # Invoke callback if configured

FILE: agentic_core\L4_state\config\versioned_configs.py
--------------------------------------------------------------------------------
  Line 21: """Tool allowlist, file scope, and budget policy."""
  Line 136: L4 SSOT registry of active versioned configs.
  Line 184: """Return the module-level L4 SSOT active config registry."""

FILE: agentic_core\L4_state\config\vllm_routing_predicates.py
--------------------------------------------------------------------------------
  Line 1: """vLLM Routing Predicate Registry.
  Line 3: Immutable, pure, deterministic predicate registry for routing decisions.

FILE: agentic_core\L4_state\enforcement\change_tracker.py
--------------------------------------------------------------------------------
  Line 8: Depth: 3 (per SSOT semantic_l2_registry['utils']['general_helpers'])

FILE: agentic_core\L4_state\enforcement\change_tracker_enforcer.py
--------------------------------------------------------------------------------
  Line 8: Depth: 3 (per SSOT semantic_l2_registry['utils']['general_helpers'])

FILE: agentic_core\L4_state\enforcement\genealogy_registry.py
--------------------------------------------------------------------------------
  Line 12: class GenealogyRegistry:

FILE: agentic_core\L4_state\enforcement\genealogy_registry_enforcer.py
--------------------------------------------------------------------------------
  Line 12: class GenealogyRegistry:

FILE: agentic_core\L4_state\enforcement\graph_memory_bridge.py
--------------------------------------------------------------------------------
  Line 100: # MCP tool functions (injected or mocked)
  Line 131: # In Windsurf/Cascade, MCP tools are available via the tool calling interface
  Line 149: Inject MCP tool functions (for testing or custom implementations).

FILE: agentic_core\L4_state\enforcement\graph_memory_bridge_enforcer.py
--------------------------------------------------------------------------------
  Line 100: # MCP tool functions (injected or mocked)
  Line 131: # In Windsurf/Cascade, MCP tools are available via the tool calling interface
  Line 149: Inject MCP tool functions (for testing or custom implementations).

FILE: agentic_core\L4_state\enforcement\replay_bundle_store.py
--------------------------------------------------------------------------------
  Line 128: known_intent_hashes    : set of valid tool intent_hash strings (optional)
  Line 129: known_result_hashes    : set of valid tool result_hash strings (optional)
  Line 158: detail=f"config hash {v!r} (key={k!r}) not found in registry",
  Line 192: detail=f"tool intent_hash {ih!r} not found",
  Line 201: detail=f"tool result_hash {rh!r} not found",

FILE: agentic_core\L4_state\memory\sovereign_semantic_cache.py
--------------------------------------------------------------------------------
  Line 141: """Invoke healing chain via super()."""

FILE: agentic_core\L4_state\reasoning\CachedStateLedgerAgent.py
--------------------------------------------------------------------------------
  Line 214: """Invoke healing chain via super()."""

FILE: agentic_core\L4_state\reasoning\GravityStateAgent.py
--------------------------------------------------------------------------------
  Line 21: - Healed files registry (file_path → healing_metadata)
  Line 242: # Add to healed files registry

FILE: agentic_core\L4_state\types\replay_bundle.py
--------------------------------------------------------------------------------
  Line 6: prior signal/violation hashes, tool intent/result hashes.

FILE: agentic_core\L4_state\types\violation_event.py
--------------------------------------------------------------------------------
  Line 123: _registry: list[ViolationEvent] | None = None,
  Line 129: If _registry is provided, appends to it (for in-memory accumulation).
  Line 140: if _registry is not None:
  Line 141: _registry.append(event)

FILE: agentic_core\L4_state\utils\circuit_breaker_util.py
--------------------------------------------------------------------------------
  Line 6: Phase 1 - Pillar 8: Tool Ecosystem (Resilience Middleware)

FILE: agentic_core\L4_state\utils\layer_gravity_util.py
--------------------------------------------------------------------------------
  Line 58: >>> extract_layer_from_path("apps_rg/engines/tool.py")

FILE: agentic_core\L4_state\utils\sanitize_telemetry_util.py
--------------------------------------------------------------------------------
  Line 4: Prevents token overload by intelligently pruning large tool outputs while
  Line 68: Sanitize tool output to prevent token overload.
  Line 71: output: The raw tool output string.

FILE: agentic_core\L5_safety\config\structure_blueprint_config.py
--------------------------------------------------------------------------------
  Line 61: agentic_core_registry,

FILE: agentic_core\L5_safety\core_kernel\classification_kernel.py
--------------------------------------------------------------------------------
  Line 16: ║  - discovery_util.py (runtime) — runtime agent registry                   ║
  Line 19: ║  - ssot_scanner.py, registry_verification.py (L5 enforcement)             ║
  Line 93: "tool_registry.py",

FILE: agentic_core\L5_safety\enforcement\agent_info.py
--------------------------------------------------------------------------------
  Line 398: print("│ {:^76} │".format("AGENT FINGERPRINT REGISTRY"))

FILE: agentic_core\L5_safety\enforcement\agent_info_enforcer.py
--------------------------------------------------------------------------------
  Line 398: print("│ {:^76} │".format("AGENT FINGERPRINT REGISTRY"))

FILE: agentic_core\L5_safety\enforcement\airlock_guardrail.py
--------------------------------------------------------------------------------
  Line 16: Validates tool calls against a mission-specific Permission matrix.
  Line 26: """Determines if a tool execution is safe to proceed under Zero-Trust."""
  Line 27: # 1. Check Registry Whitelist
  Line 29: raise PermissionError(f"Airlock Block: Tool '{tool_name}' is not in the Sovereign Registry.")
  Line 33: logging.info(f"Airlock: Evaluating High-Risk tool '{tool_name}'...")
  Line 38: def _validate_risk_parameters(self, tool: str, args: dict) -> bool:

FILE: agentic_core\L5_safety\enforcement\circuit_breaker.py
--------------------------------------------------------------------------------
  Line 80: # Global registry with simple lock pattern to prevent deadlock
  Line 312: def reset_registry() -> None:
  Line 313: """Reset the circuit breaker registry - for testing only."""

FILE: agentic_core\L5_safety\enforcement\circuit_breaker_gate.py
--------------------------------------------------------------------------------
  Line 80: # Global registry with simple lock pattern to prevent deadlock
  Line 312: def reset_registry() -> None:
  Line 313: """Reset the circuit breaker registry - for testing only."""

FILE: agentic_core\L5_safety\enforcement\compliance_audit_manager.py
--------------------------------------------------------------------------------
  Line 4: from .sovereign_policy_registry import PolicySeverity, SovereignPolicyRegistry
  Line 12: Checks system actions against the SovereignPolicyRegistry.
  Line 16: self.registry = SovereignPolicyRegistry
  Line 24: policy = next((p for p in self.registry.get_all() if p.id == policy_id), None)

FILE: agentic_core\L5_safety\enforcement\compliance_audit_manager_enforcer.py
--------------------------------------------------------------------------------
  Line 4: from .sovereign_policy_registry import PolicySeverity, SovereignPolicyRegistry
  Line 12: Checks system actions against the SovereignPolicyRegistry.
  Line 16: self.registry = SovereignPolicyRegistry
  Line 24: policy = next((p for p in self.registry.get_all() if p.id == policy_id), None)

FILE: agentic_core\L5_safety\enforcement\HealingStrategy.py
--------------------------------------------------------------------------------
  Line 30: from agentic_core.config.core.hygiene_registry_config import (
  Line 58: # Define the 5-tier execution plan using core registry

FILE: agentic_core\L5_safety\enforcement\healing_invocation_audit.py
--------------------------------------------------------------------------------
  Line 26: """Initialize audit tool."""
  Line 211: # CRITICAL FIRST: Invoke parent healing chain

FILE: agentic_core\L5_safety\enforcement\healing_invocation_audit_enforcer.py
--------------------------------------------------------------------------------
  Line 26: """Initialize audit tool."""
  Line 211: # CRITICAL FIRST: Invoke parent healing chain

FILE: agentic_core\L5_safety\enforcement\mcp_sovereign_authority.py
--------------------------------------------------------------------------------
  Line 4: Enforces zero-trust auditing and auto-immune responses for all MCP tool calls.
  Line 30: """Log a tool failure or unauthorized access attempt."""
  Line 36: """L5 Audit: Log every physical tool call before execution."""
  Line 50: raise ValueError("L2 tool input too long — potential exfiltration risk.")
  Line 53: raise PermissionError("L2 tool query contains forbidden terms — blocked by shield.")
  Line 60: raise ValueError("L1 cognitive tool input too long — reasoning overflow risk.")
  Line 69: "L1 tool input contains forbidden cognitive patterns — blocked by shield.",
  Line 74: raise PermissionError(f"L0 tool target '{target}' invalid — path traversal blocked.")
  Line 77: raise PermissionError("L0 tool target outside sovereign maintenance zones.")
  Line 113: raise PermissionError("MCP Sovereign Shield active: Tool call blocked due to chronic breaches.")

FILE: agentic_core\L5_safety\enforcement\mcp_sovereign_authority_enforcer.py
--------------------------------------------------------------------------------
  Line 4: Enforces zero-trust auditing and auto-immune responses for all MCP tool calls.
  Line 30: """Log a tool failure or unauthorized access attempt."""
  Line 36: """L5 Audit: Log every physical tool call before execution."""
  Line 50: raise ValueError("L2 tool input too long — potential exfiltration risk.")
  Line 53: raise PermissionError("L2 tool query contains forbidden terms — blocked by shield.")
  Line 60: raise ValueError("L1 cognitive tool input too long — reasoning overflow risk.")
  Line 69: "L1 tool input contains forbidden cognitive patterns — blocked by shield.",
  Line 74: raise PermissionError(f"L0 tool target '{target}' invalid — path traversal blocked.")
  Line 77: raise PermissionError("L0 tool target outside sovereign maintenance zones.")
  Line 113: raise PermissionError("MCP Sovereign Shield active: Tool call blocked due to chronic breaches.")

FILE: agentic_core\L5_safety\enforcement\mission_utils.py
--------------------------------------------------------------------------------
  Line 40: Get the authority rank of a layer based on its position in the SSOT registry.
  Line 127: if any(x in name_lower for x in ["exec", "action", "tool", "handler"]):

FILE: agentic_core\L5_safety\enforcement\mission_utils_enforcer.py
--------------------------------------------------------------------------------
  Line 40: Get the authority rank of a layer based on its position in the SSOT registry.
  Line 127: if any(x in name_lower for x in ["exec", "action", "tool", "handler"]):

FILE: agentic_core\L5_safety\enforcement\process_guard.py
--------------------------------------------------------------------------------
  Line 7: 1. Registry: Tracks all PIDs spawned by agents
  Line 57: - Thread-safe PID registry
  Line 158: # Clear the registry

FILE: agentic_core\L5_safety\enforcement\process_guardrail.py
--------------------------------------------------------------------------------
  Line 7: 1. Registry: Tracks all PIDs spawned by agents
  Line 57: - Thread-safe PID registry
  Line 158: # Clear the registry

FILE: agentic_core\L5_safety\enforcement\pytest_config_guard.py
--------------------------------------------------------------------------------
  Line 57: if "[tool:pytest]" not in content and "[pytest]" not in content:

FILE: agentic_core\L5_safety\enforcement\pytest_config_guardrail.py
--------------------------------------------------------------------------------
  Line 57: if "[tool:pytest]" not in content and "[pytest]" not in content:

FILE: agentic_core\L5_safety\enforcement\registry_verification.py
--------------------------------------------------------------------------------
  Line 2: Phase 1: Registry Verification Module
  Line 9: 3. Orphan agent detection (in registry but missing from filesystem)
  Line 10: 4. Missing agent detection (in filesystem but not in registry)
  Line 11: 5. Path mismatch detection (registry path != actual path)
  Line 14: from agentic_core.L5_safety.enforcement.registry_verification_enforcer import RegistryVerifier
  Line 15: verifier = RegistryVerifier()
  Line 16: report = verifier.verify_registry()
  Line 65: """Result of registry verification."""
  Line 68: total_registry_agents: int = 0
  Line 78: class RegistryVerifier:
  Line 79: """Verifies agent registry completeness against filesystem."""
  Line 194: def load_registry(self) -> list[dict[str, Any]]:
  Line 195: """Load agent registry from JSON file."""
  Line 205: def verify_registry(self) -> VerificationResult:
  Line 206: """Perform full registry verification."""
  Line 213: # Load registry
  Line 214: registry_agents = self.load_registry()
  Line 215: result.total_registry_agents = len(registry_agents)
  Line 221: registry_by_class = {a.get("class_name", ""): a for a in registry_agents}
  Line 223: # Check for orphan agents (in registry but not in filesystem)
  Line 224: for reg_agent in registry_agents:
  Line 232: "registry_path": reg_path,
  Line 242: "registry_path": reg_path,
  Line 244: "reason": "Path mismatch between registry and filesystem",
  Line 248: # Check for missing agents (in filesystem but not in registry)
  Line 250: if fs_agent.class_name not in registry_by_class:
  Line 270: "# Phase 1: Registry Verification Report",
  Line 275: f"- **Total Registry Agents:** {result.total_registry_agents}",
  Line 277: f"- **Missing from Registry:** {len(result.missing_agents)}",
  Line 288: "## Orphan Agents (In Registry, Not in Filesystem)",
  Line 290: "| Class Name | Registry Path | Reason |",
  Line 296: path = orphan["registry_path"]
  Line 306: "| Class Name | Registry Path | Actual Path |",
  Line 312: reg = mismatch["registry_path"]
  Line 320: "## Missing from Registry (In Filesystem, Not in Registry)",
  Line 337: """Run registry verification and return result."""
  Line 338: verifier = RegistryVerifier()
  Line 339: return verifier.verify_registry()
  Line 343: verifier = RegistryVerifier()
  Line 344: result = verifier.verify_registry()

FILE: agentic_core\L5_safety\enforcement\registry_verification_enforcer.py
--------------------------------------------------------------------------------
  Line 2: Phase 1: Registry Verification Module
  Line 9: 3. Orphan agent detection (in registry but missing from filesystem)
  Line 10: 4. Missing agent detection (in filesystem but not in registry)
  Line 11: 5. Path mismatch detection (registry path != actual path)
  Line 14: from agentic_core.L5_safety.enforcement.registry_verification_enforcer import RegistryVerifier
  Line 15: verifier = RegistryVerifier()
  Line 16: report = verifier.verify_registry()
  Line 65: """Result of registry verification."""
  Line 68: total_registry_agents: int = 0
  Line 78: class RegistryVerifier:
  Line 79: """Verifies agent registry completeness against filesystem."""
  Line 194: def load_registry(self) -> list[dict[str, Any]]:
  Line 195: """Load agent registry from JSON file."""
  Line 205: def verify_registry(self) -> VerificationResult:
  Line 206: """Perform full registry verification."""
  Line 213: # Load registry
  Line 214: registry_agents = self.load_registry()
  Line 215: result.total_registry_agents = len(registry_agents)
  Line 221: registry_by_class = {a.get("class_name", ""): a for a in registry_agents}
  Line 223: # Check for orphan agents (in registry but not in filesystem)
  Line 224: for reg_agent in registry_agents:
  Line 232: "registry_path": reg_path,
  Line 242: "registry_path": reg_path,
  Line 244: "reason": "Path mismatch between registry and filesystem",
  Line 248: # Check for missing agents (in filesystem but not in registry)
  Line 250: if fs_agent.class_name not in registry_by_class:
  Line 270: "# Phase 1: Registry Verification Report",
  Line 275: f"- **Total Registry Agents:** {result.total_registry_agents}",
  Line 277: f"- **Missing from Registry:** {len(result.missing_agents)}",
  Line 288: "## Orphan Agents (In Registry, Not in Filesystem)",
  Line 290: "| Class Name | Registry Path | Reason |",
  Line 296: path = orphan["registry_path"]
  Line 306: "| Class Name | Registry Path | Actual Path |",
  Line 312: reg = mismatch["registry_path"]
  Line 320: "## Missing from Registry (In Filesystem, Not in Registry)",
  Line 337: """Run registry verification and return result."""
  Line 338: verifier = RegistryVerifier()
  Line 339: return verifier.verify_registry()
  Line 343: verifier = RegistryVerifier()
  Line 344: result = verifier.verify_registry()

FILE: agentic_core\L5_safety\enforcement\sovereign_policy_registry.py
--------------------------------------------------------------------------------
  Line 20: class SovereignPolicyRegistry:

FILE: agentic_core\L5_safety\enforcement\sovereign_policy_registry_enforcer.py
--------------------------------------------------------------------------------
  Line 20: class SovereignPolicyRegistry:

FILE: agentic_core\L5_safety\enforcement\ssot_guardrail.py
--------------------------------------------------------------------------------
  Line 101: "agentic_core/L5_safety/enforcement/registry_verification_enforcer.py",

FILE: agentic_core\L5_safety\enforcement\ssot_import_enforcer.py
--------------------------------------------------------------------------------
  Line 20: SOVEREIGN_REGISTRY,

FILE: agentic_core\L5_safety\enforcement\ssot_scanner.py
--------------------------------------------------------------------------------
  Line 2: SSOT Scanner - Direct Filesystem Scanning Without Registry
  Line 6: the 15-18 second registry refresh overhead.
  Line 8: Performance: <1 second for full scan (vs 15-18s for registry rebuild)

FILE: agentic_core\L5_safety\enforcement\ssot_scanner_enforcer.py
--------------------------------------------------------------------------------
  Line 2: SSOT Scanner - Direct Filesystem Scanning Without Registry
  Line 6: the 15-18 second registry refresh overhead.
  Line 8: Performance: <1 second for full scan (vs 15-18s for registry rebuild)

FILE: agentic_core\L5_safety\enforcement\ssot_structure_validation.py
--------------------------------------------------------------------------------
  Line 33: from agentic_core.L5_safety.enforcement.registry_verification_enforcer import (
  Line 35: RegistryVerifier,
  Line 96: self.verifier = RegistryVerifier(project_root)

FILE: agentic_core\L5_safety\enforcement\ssot_structure_validation_enforcer.py
--------------------------------------------------------------------------------
  Line 33: from agentic_core.L5_safety.enforcement.registry_verification_enforcer import (
  Line 35: RegistryVerifier,
  Line 96: self.verifier = RegistryVerifier(project_root)

FILE: agentic_core\L5_safety\enforcement\three_tier_compliance.py
--------------------------------------------------------------------------------
  Line 34: from agentic_core.L5_safety.enforcement.registry_verification_enforcer import (
  Line 36: RegistryVerifier,
  Line 144: self.verifier = RegistryVerifier(project_root)

FILE: agentic_core\L5_safety\enforcement\three_tier_compliance_enforcer.py
--------------------------------------------------------------------------------
  Line 34: from agentic_core.L5_safety.enforcement.registry_verification_enforcer import (
  Line 36: RegistryVerifier,
  Line 144: self.verifier = RegistryVerifier(project_root)

FILE: agentic_core\L5_safety\governance\lazy_seam_classifier.py
--------------------------------------------------------------------------------
  Line 21: "D3_PLUGIN_REGISTRY_DISPATCH": "Registry/dynamic dispatch boundaries",
  Line 73: # D3_PLUGIN_REGISTRY_DISPATCH: Dynamic dispatch and registry
  Line 74: registry_keywords = {
  Line 75: "registry",
  Line 86: if any(keyword in function_name.lower() for keyword in registry_keywords) or any(
  Line 87: keyword in file_path.lower() for keyword in registry_keywords
  Line 89: return ("D3_PLUGIN_REGISTRY_DISPATCH", "Plugin registry or dynamic dispatch boundary")
  Line 129: return ("D3_PLUGIN_REGISTRY_DISPATCH", "Dynamic component loading (default classification)")

FILE: agentic_core\L5_safety\reasoning\ArchitectureGovernorAgent.py
--------------------------------------------------------------------------------
  Line 132: check_registry=False,
  Line 657: [PHASE 22] Invoke CognitiveDispositionAgent for intelligent violation analysis.

FILE: agentic_core\L5_safety\reasoning\AutonomyGuardianAgent.py
--------------------------------------------------------------------------------
  Line 171: registry = DashboardDataGenerator(self.project_root, self.territories).load_registry()
  Line 172: for entry in registry:

FILE: agentic_core\L5_safety\reasoning\CodeDeduplicationAgent.py
--------------------------------------------------------------------------------
  Line 650: # Prioritizes snake_case 'tool_registry' as the canonical SSOT location.
  Line 654: key=lambda p: (ARCHIVES_DIR in str(p), "tool_registry" in str(p), str(p)),

FILE: agentic_core\L5_safety\reasoning\CodeEnforcerAgent.py
--------------------------------------------------------------------------------
  Line 11: - CodeSSOTEnforcerAgent (SSOT registry sync)
  Line 18: - SSOT registry synchronization
  Line 96: ssot_registry_path: Path | None = None
  Line 121: enforcer.sync_ssot_registry()
  Line 148: self._ssot_registry: dict[str, Any] = {}
  Line 396: def sync_ssot_registry(self) -> dict[str, Any]:
  Line 397: """Synchronize with SSOT registry."""
  Line 399: if not self._agent_config.ssot_registry_path:
  Line 400: self._agent_config.ssot_registry_path = self.project_root / "agent_discovery_full.json"
  Line 402: if self._agent_config.ssot_registry_path.exists():
  Line 406: self._ssot_registry = json.loads(
  Line 407: self._agent_config.ssot_registry_path.read_text(encoding="utf-8"),
  Line 409: Logger.info(f"SSOT registry synced: {len(self._ssot_registry.get('agents', []))} agents")
  Line 411: Logger.error(f"Failed to sync SSOT registry: {e}")
  Line 413: return self._ssot_registry
  Line 415: def update_ssot_registry(self, updates: dict[str, Any]) -> bool:
  Line 416: """Update SSOT registry with changes."""
  Line 418: if not self._agent_config.ssot_registry_path:
  Line 421: self._ssot_registry.update(updates)
  Line 427: self._agent_config.ssot_registry_path,
  Line 428: json.dumps(self._ssot_registry, indent=2),
  Line 431: Logger.info("SSOT registry updated")
  Line 434: Logger.error(f"Failed to update SSOT registry: {e}")
  Line 469: # Sync SSOT registry
  Line 470: self.sync_ssot_registry()

FILE: agentic_core\L5_safety\reasoning\CodeFormatterAgent.py
--------------------------------------------------------------------------------
  Line 88: self.ctx.report("CodeFormatterAgent", 0, False, f"Tool Missing: {e.filename}")

FILE: agentic_core\L5_safety\reasoning\DDDAlignmentAgent.py
--------------------------------------------------------------------------------
  Line 48: SOVEREIGN_REGISTRY,  # noqa: F401
  Line 68: "role": "Action: Tool Implementation and Agent Realization",

FILE: agentic_core\L5_safety\reasoning\DynamicSealAgent.py
--------------------------------------------------------------------------------
  Line 9: L2 Execution Tool designed to surgically eliminate upward architectural leaks.

FILE: agentic_core\L5_safety\reasoning\FileClassificationAgent.py
--------------------------------------------------------------------------------
  Line 214: self.file_registry: list[Path] = []
  Line 461: self.file_registry = get_python_files_fast(root)
  Line 462: self.stats["analyzed"] = len(self.file_registry)
  Line 465: duplicate_violations = self._detect_duplicate_files(self.file_registry)
  Line 471: # Iterating over a copy to allow registry updates during renames
  Line 472: for idx, path in enumerate(list(self.file_registry)):
  Line 499: self.file_registry[idx] = path
  Line 602: # Update path registry to reflect new location for subsequent operations
  Line 604: self.file_registry[idx] = path
  Line 631: self.file_registry[idx] = path
  Line 649: self.file_registry[idx] = path
  Line 691: # Only update registry if file exists and wasn't deleted
  Line 693: self.file_registry[idx] = dest
  Line 731: # File was deleted due to duplicate content - remove from registry
  Line 732: self.file_registry[idx] = None
  Line 808: "tool_registry.py",
  Line 2292: - *Manager with tool/api/subprocess/request signals → L2_execution
  Line 2306: l2_signals = ("subprocess", "requests.get", "requests.post", "aiohttp", "tool_registry", "api_call")
  Line 2718: # - SERVICE must end with (_service|_store|_registry|_bridge).py
  Line 2732: valid_suffixes = ("_service.py", "_store.py", "_registry.py", "_bridge.py")
  Line 2973: def _detect_duplicate_files(self, file_registry: list[Path]) -> list[dict[str, Any]]:
  Line 2984: file_registry: List of all file paths being audited.
  Line 2996: for path in file_registry:
  Line 4051: for path in self.file_registry:
  Line 4087: """Refactors imports using the in-memory registry to avoid O(N²) disk hits."""
  Line 4106: # Optimized: Scans in-memory file_registry instead of hitting disk rglob
  Line 4107: for _i, path in enumerate(self.file_registry):
  Line 4637: # In Core, Agents follow the Domain (Guardrails, Registry, etc.)
  Line 5272: WAVE 1.1–1.3: Run all safety gates on the current file registry.
  Line 5280: Must be called AFTER _orchestrate_audit populates file_registry,
  Line 5286: # Scan files if registry is empty
  Line 5287: if not self.file_registry:
  Line 5288: self.file_registry = get_python_files_fast(scan_root)
  Line 5294: for path in self.file_registry:
  Line 5316: python_files=[p for p in self.file_registry if p is not None],

FILE: agentic_core\L5_safety\reasoning\FilesystemSSOTReconcilerAgent.py
--------------------------------------------------------------------------------
  Line 24: Mirrors the successful PromptRegistry.py pattern:
  Line 30: Invoked by:
  Line 152: - Creation: Ensures all folders in sovereign_registry exist.
  Line 497: - sovereign_registry
  Line 510: "sovereign_registry": getattr(module, "sovereign_registry", {}),
  Line 516: f"Blueprint loaded: {len(blueprint['sovereign_registry'])} roots, "
  Line 528: 1. sovereign_registry subfolders (L1 depth)
  Line 536: # 1. Check SOVEREIGN_REGISTRY subfolders
  Line 537: self._check_registry_subfolders(current_blueprint, drift)
  Line 548: def _check_registry_subfolders(
  Line 554: Check SOVEREIGN_REGISTRY subfolders.
  Line 560: blueprint_registry = current_blueprint.get("sovereign_registry", {})
  Line 566: blueprint_subfolders = set(blueprint_registry.get(root, {}).get("subfolders", []))
  Line 642: def _check_registry_subfolders(
  Line 647: """Check SOVEREIGN_REGISTRY subfolders for drift."""
  Line 648: blueprint_registry = current_blueprint.get("sovereign_registry", {})
  Line 654: blueprint_subfolders = set(blueprint_registry.get(root, {}).get("subfolders", []))
  Line 865: if action == "add_to_sovereign_registry":
  Line 866: content = self._apply_sovereign_registry_update(
  Line 892: def _apply_sovereign_registry_update(self, content: str, root: str, folders: list[str]) -> str:
  Line 894: Add subfolders to sovereign_registry[root]['subfolders'].
  Line 898: Logger.debug(f"Updating sovereign_registry for root '{root}' with folders {folders}")
  Line 903: # Find the sovereign_registry definition for this root
  Line 909: insert_line += f"{indent}sovereign_registry['{root}']['subfolders'].extend({folders})\n"
  Line 918: + f"sovereign_registry['{root}']['subfolders'].extend({folders})\n"

FILE: agentic_core\L5_safety\reasoning\GovernanceAgent.py
--------------------------------------------------------------------------------
  Line 366: SOVEREIGN_REGISTRY,
  Line 369: from agentic_core.config.core.registry_config import SOVEREIGN_REGISTRY
  Line 373: self.ALLOWED_ROOT_FOLDERS = set(SOVEREIGN_REGISTRY.keys())
  Line 374: self.DEPTH_MAP = {root: cfg["depth"] for root, cfg in SOVEREIGN_REGISTRY.items()}
  Line 569: [SSOT] Uses DEPTH_MAP derived from SOVEREIGN_REGISTRY for per-root depth enforcement.

FILE: agentic_core\L5_safety\reasoning\guardian_decision.py
--------------------------------------------------------------------------------
  Line 49: - Tool allowlist
  Line 93: # Check tool allowlist
  Line 96: violations.append(f"Tool '{manifest.tool_name}' not in allowlist")

FILE: agentic_core\L5_safety\reasoning\HierarchyAgent.py
--------------------------------------------------------------------------------
  Line 1044: # [SSOT] Dynamically pull roots from registry
  Line 1464: # meta_prompts, templates, scripts, version_registry, agents, registry

FILE: agentic_core\L5_safety\reasoning\LocationHealerAgent.py
--------------------------------------------------------------------------------
  Line 32: from agentic_core.config.core.registry_config import SOVEREIGN_REGISTRY
  Line 937: existing_subfolders = SOVEREIGN_REGISTRY.get(root_folder, {}).get("subfolders", [])
  Line 965: existing_subfolders = SOVEREIGN_REGISTRY.get(root_folder, {}).get("subfolders", [])
  Line 1008: f"SOVEREIGN_REGISTRY['{root_folder}']['subfolders']",
  Line 1114: """Create a new subfolder and update SOVEREIGN_REGISTRY in structure_blueprint.py."""
  Line 1119: print("This will update SOVEREIGN_REGISTRY in structure_blueprint.py")
  Line 1131: # Step 1: Update SOVEREIGN_REGISTRY in structure_blueprint.py
  Line 1187: f"SOVEREIGN_REGISTRY['{root_folder}']['subfolders']"
  Line 1383: # Update SOVEREIGN_REGISTRY in structure_blueprint.py
  Line 1487: expected_depth = SOVEREIGN_REGISTRY.get(root_folder, {}).get("depth", 3)

FILE: agentic_core\L5_safety\reasoning\LocationValidatorAgent.py
--------------------------------------------------------------------------------
  Line 258: """Validate depth requirements from sovereign registry.

FILE: agentic_core\L5_safety\reasoning\RedTeamAgent.py
--------------------------------------------------------------------------------
  Line 20: from agentic_core.prompt_governance.version_registry.prompt_registry_config import registers_prompt
  Line 27: # Template content loading for registry

FILE: agentic_core\L5_safety\reasoning\SafetyInspectorAgent.py
--------------------------------------------------------------------------------
  Line 93: return ViolationCheck(False, "Diagnostic tool creation is allowed")
  Line 98: """Validate tool execution requests."""

FILE: agentic_core\L5_safety\reasoning\SovereignActionPlaneAgent.py
--------------------------------------------------------------------------------
  Line 18: Bypasses corrupted registry files with Toolsmith logic from the monolith.
  Line 40: """Toolsmith implementation for dynamic tool creation."""
  Line 54: Forge a diagnostic tool based on failure context.
  Line 60: Path to generated tool or None if failed
  Line 62: tool_code: Any = f'#!/usr/bin/env python3\n"""Diagnostic tool generated by Sovereign Toolsmith at {time.time()}"""\n\nimport json\nimport sys\nimport os\nfrom pathlib import Path\nfrom agentic_core.utils.security import safe_popen\n\ndef main():\n    """Execute diagnostic probe."""\n    try:\n        # Basic environment probe\n        diagnostics = {{\n            "timestamp": "{time.time()}",\n            "failure_context": {repr(failure_context)},\n            "environment": {{\n                "cwd": os.getcwd(),\n                "python_version": sys.version,\n                "path": os.environ.get("PATH", "")[:100] + "..." if os.environ.get("PATH") else ""\n            }},\n            "file_system": {{\n                "scripts_dir": str(Path(SCRIPTS_DIR).exists()),\n                "agentic_core_dir": str(Path(AGENTIC_CORE_DIR).exists()),\n            }},\n            "status": "probing_complete"\n        }}\n\n        print(json.dumps(diagnostics, indent=2))\n        return 0\n    except Exception as e:\n        print(json.dumps({{"error": str(e), "status": "error"}}))\n        return 1\n\nif __name__ == "__main__":\n    sys.exit(main())\n'
  Line 72: Logger.error(f"Failed to forge tool: {e}")
  Line 104: Execute a tool in the sandbox.
  Line 107: tool_path: Path to tool to execute
  Line 137: LOGGER.warning(f"Tool {tool_path} timed out, cleaning up process {process.pid}")
  Line 153: "stderr": "Tool execution timed out and process was terminated",
  Line 209: """Get list of available tool names."""
  Line 370: """Execute a tool in the sandbox."""
  Line 385: LOGGER.info(f"Successfully repaired tool {tool_path}, retrying execution")
  Line 399: """Attempt to repair a tool that has a syntax error.
  Line 402: tool_path: Path to the tool file
  Line 434: LOGGER.error(f"Error during tool repair: {e}")
  Line 438: """Create a diagnostic tool using Toolsmith."""
  Line 444: output=f"Created diagnostic tool: {tool_path}",
  Line 453: error="Failed to create diagnostic tool",

FILE: agentic_core\L5_safety\reasoning\SprawlInspectorAgent.py
--------------------------------------------------------------------------------
  Line 115: """Invoke healing chain via super()."""

FILE: agentic_core\L5_safety\reasoning\StructuralEngineerAgent.py
--------------------------------------------------------------------------------
  Line 267: """L2 execution agent - invoke shared healing chain."""
  Line 284: print(f"[{agent_name}] L2 execution - healing chain invoked")

FILE: agentic_core\L5_safety\reasoning\StructuralValidatorAgent.py
--------------------------------------------------------------------------------
  Line 79: check_registry: bool = False

FILE: agentic_core\L5_safety\reasoning\SystemArchitectAgent.py
--------------------------------------------------------------------------------
  Line 407: """L2 execution agent - invoke shared healing chain."""
  Line 424: print(f"[{agent_name}] L2 execution - healing chain invoked")

FILE: agentic_core\L5_safety\reasoning\TestGeneratorAgent.py
--------------------------------------------------------------------------------
  Line 323: """Invoke healing chain via super()."""

FILE: agentic_core\L5_safety\reasoning\TypeHintFixerAgent.py
--------------------------------------------------------------------------------
  Line 79: """Invoke healing chain via super()."""

FILE: agentic_core\L5_safety\reasoning\UnusedCleanupAgent.py
--------------------------------------------------------------------------------
  Line 6: from Python files using the autoflake tool.

FILE: agentic_core\L5_safety\runners\arch_governor_runner.py
--------------------------------------------------------------------------------
  Line 5: to invoke ArchitectureGovernorAgent without creating upward import edges.

FILE: agentic_core\L5_safety\runners\code_validator_runner.py
--------------------------------------------------------------------------------
  Line 5: to invoke CodeValidatorAgent without creating upward import edges.

FILE: agentic_core\L5_safety\runners\hierarchy_runner.py
--------------------------------------------------------------------------------
  Line 5: to invoke HierarchyAgent without creating upward import edges.

FILE: agentic_core\L5_safety\runners\orchestrator_runner.py
--------------------------------------------------------------------------------
  Line 5: to invoke orchestrator missions without creating upward import edges.

FILE: agentic_core\L5_safety\types\core_contracts_types.py
--------------------------------------------------------------------------------
  Line 5: SSOT for retry policies, hop specifications, and registry.
  Line 66: # Registry of all core contracts
  Line 67: CORE_CONTRACTS_REGISTRY: dict[str, Any] = {
  Line 78: "CORE_CONTRACTS_REGISTRY",

FILE: agentic_core\L5_safety\types\integrity_validation_types.py
--------------------------------------------------------------------------------
  Line 71: # Checksum registry

FILE: agentic_core\L5_safety\utils\canonical_truth_util.py
--------------------------------------------------------------------------------
  Line 204: "L2": r"execution|tool|action|mcp",

FILE: agentic_core\L5_safety\utils\code_tool_runner_core.py
--------------------------------------------------------------------------------
  Line 1: """Shared core for L5 Safety code-tool-runner agents.
  Line 31: """Pure capability mixin for L5 code-tool-runner agents.
  Line 46: """Run the tool on a single file.  Must be overridden by subclasses."""
  Line 92: Delegates to execute() for the actual tool invocation.

FILE: agentic_core\L5_safety\utils\code_tool_runner_core_util.py
--------------------------------------------------------------------------------
  Line 1: """Shared core for L5 Safety code-tool-runner agents.
  Line 31: """Pure capability mixin for L5 code-tool-runner agents.
  Line 46: """Run the tool on a single file.  Must be overridden by subclasses."""
  Line 92: Delegates to execute() for the actual tool invocation.

FILE: agentic_core\L5_safety\utils\fix_inherited_invocation_util.py
--------------------------------------------------------------------------------
  Line 26: """Invoke healing chain via super()."""

FILE: agentic_core\L5_safety\utils\guard_ddd_alignment_util.py
--------------------------------------------------------------------------------
  Line 128: or "_registry" in path_str

FILE: agentic_core\L5_safety\validators\agentthoughtprocess_validator.py
--------------------------------------------------------------------------------
  Line 41: tool_arguments: dict[str, Any] = Field(default_factory=dict, description="Arguments for the chosen tool")
  Line 52: """Self-validation to ensure arguments match the tool choice."""
  Line 56: raise ValueError("Tool choice CODE requires a 'code' argument.")
  Line 59: raise ValueError("Tool choice SEARCH requires a 'query' argument.")
  Line 62: raise ValueError("Tool choice DELEGATE requires a 'subtask' argument.")
  Line 108: """Agent execution plan with reasoning and tool calls."""
  Line 116: description="Ordered list of tool calls to execute the plan",

FILE: agentic_core\L5_safety\validators\read_file_args_validator.py
--------------------------------------------------------------------------------
  Line 4: Tool Arguments schema
  Line 6: Defines the Pydantic models for all tool-calling arguments within the
  Line 16: # File System Tool Arguments
  Line 100: # Execution Tool Arguments

FILE: agentic_core\L5_safety\validators\reasoning_pattern_validator.py
--------------------------------------------------------------------------------
  Line 8: from agentic_core.runtime.tools import ToolRegistry
  Line 17: async def plan(self, state: AgentState, tools: ToolRegistry) -> tuple[str, dict[str, Any]]:
  Line 24: tools: Available tool registry for action execution
  Line 27: Tuple containing tool name to execute and its arguments

FILE: agentic_core\L5_safety\config\structure_blueprint\artifacts.py
--------------------------------------------------------------------------------
  Line 364: re.compile(r".*tool.*"),
  Line 676: "content_types": ["prompt_governance", "injection_data", "safety_data", "registry_data"],

FILE: agentic_core\L5_safety\config\structure_blueprint\classification.py
--------------------------------------------------------------------------------
  Line 178: # └── tools:           .*_(tool|impl|client)\.py$
  Line 390: "registry",

FILE: agentic_core\L5_safety\config\structure_blueprint\derived.py
--------------------------------------------------------------------------------
  Line 106: agentic_core_registry: Final[Mapping[str, Sequence[str]]] = CORE_SUBFOLDER_MAP
  Line 165: "core": ["registry_core", "registry_types"],
  Line 204: "maintenance": ["registry_cleaners", "cache_managers"],
  Line 206: "version_registry": {
  Line 232: "agentic_core/prompt_governance/version_registry",
  Line 233: "agentic_core/prompt_governance/registry",

FILE: agentic_core\L5_safety\config\structure_blueprint\semantics.py
--------------------------------------------------------------------------------
  Line 106: "tool",
  Line 110: "invoke",
  Line 308: "primary": frozenset({"tool", "execute", "call", "registry", "runner"}),
  Line 332: "primary": frozenset({"blueprint", "registry", "sovereign", "canon", "config", "settings"}),
  Line 338: "primary": frozenset({"render", "registry", "assemble", "govern"}),
  Line 488: # === AST PLACEMENT SIGNAL REGISTRY ===
  Line 581: "class_patterns": [".*Agent$", ".*Tool$", ".*Handler$"],
  Line 583: "function_patterns": ["execute_.*", "run_tool.*", "invoke_.*"],
  Line 584: "import_signals": ["tool_registry", "SubAtomicAgent"],
  Line 585: "keyword_signals": ["tool", "execute", "invoke", "action", "handler"],
  Line 586: "decorator_signals": ["@tool", "@action"],
  Line 810: "version_registry": "prompt_governance",
  Line 818: # === GENERALIZED EXERCISER REGISTRY (Phase 7 SSOT) ===
  Line 820: EXERCISER_REGISTRY: Final[Mapping[str, str]] = {
  Line 840: # [PHASE 17] AGENT REGISTRY - Complete PascalCase Agent Discovery Map
  Line 842: AGENT_REGISTRY: Final[Mapping[str, Sequence[Mapping[str, str | int]]]] = {
  Line 1027: "name": "SubAtomicRegistryAgent",
  Line 1028: "file": "agentic_core/L4_state/memory/SubAtomicRegistryAgent.py",
  Line 1235: semantic_l2_registry: Final[Mapping[str, Any]] = {
  Line 1507: "purpose": "Registration and discovery of external tools, base tool definitions, and tool metadata management",
  Line 1510: "tool",
  Line 1511: "registry",
  Line 1523: "purpose": "Action dispatch logic, handler mapping, execution routing, and fallback strategies for tool calls",
  Line 1533: "invoke",
  Line 1547: "purpose": "Multi-Component Protocol clients and tool implementations (figma, fetch, filesystem, semantic_cache, router, marketplace_filter)",
  Line 1769: "registry",
  Line 1776: "examples": ["StructureBlueprint", "CanonRegistry", "SovereignConstitution"],
  Line 1943: "purpose": "Common human-agent and agent-tool interaction patterns (CLI, Chat, etc)",
  Line 2357: "keywords": ["tool", "utility", "helper", "function", "operation", "service"],
  Line 2365: SEMANTIC_L2_REGISTRY: Final[Mapping[str, Any]] = semantic_l2_registry

FILE: agentic_core\L5_safety\config\structure_blueprint\_constants.py
--------------------------------------------------------------------------------
  Line 192: "purpose": "The Hands: Tool execution, MCP clients, and sandboxed environments.",
  Line 198: "_registry.py",
  Line 217: "purpose": "Standardized tool implementations — strict naming enforced.",
  Line 236: "*_registry.py": "reasoning",
  Line 610: r"^registry\.py$",
  Line 623: "optional_subfolders": ["core", "domain", "optimization", "registry", "utils", "validation"],
  Line 632: "registry": {
  Line 633: "purpose": "Prompt version registry and manifest management.",
  Line 635: "backups": {"purpose": "Registry backup snapshots."},
  Line 779: "agentic_core/prompt_governance/version_registry": {
  Line 780: "json_keys": ["registry_version", "checksum_manifest"],
  Line 812: "tools": {"purpose": "Tool implementations and wrappers", "subfolders": []},
  Line 825: apps_lic_subfolders["tools"] = {"purpose": "Tool implementations", "subfolders": []}
  Line 861: "tools": {"purpose": "Shared tool implementations and wrappers (optional)"},

FILE: agentic_core\L5_safety\config\structure_blueprint\_simulate_verify.py
--------------------------------------------------------------------------------
  Line 198: def _find_invoke_lines(text: str) -> list[str]:
  Line 215: clean_invoke = _find_invoke_lines(wf_text)
  Line 216: clean_count = len(clean_invoke)
  Line 218: for line in clean_invoke:
  Line 229: tampered_invoke = _find_invoke_lines(tampered)
  Line 230: tampered_count = len(tampered_invoke)
  Line 232: for line in tampered_invoke:

FILE: agentic_core\L5_safety\config\structure_blueprint\_verify.py
--------------------------------------------------------------------------------
  Line 419: "agentic_core_registry",

FILE: agentic_core\L5_safety\config\structure_blueprint\__init__.py
--------------------------------------------------------------------------------
  Line 150: "AGENT_REGISTRY",
  Line 163: "EXERCISER_REGISTRY",
  Line 173: "SEMANTIC_L2_REGISTRY",
  Line 179: "semantic_l2_registry",
  Line 229: "agentic_core_registry",
  Line 266: #   agentic_core_registry, verify_derived_registries, L4_SUBFOLDER_MAP,
  Line 278: "AGENT_REGISTRY",
  Line 321: "EXERCISER_REGISTRY",
  Line 390: "SEMANTIC_L2_REGISTRY",
  Line 435: "semantic_l2_registry",

FILE: agentic_core\L5_safety\enforcement\governance\agent_heal_audit.py
--------------------------------------------------------------------------------
  Line 471: "All runtime agents route through `standard_heal` decorator which invokes `decide_heal_escalation()`.",

FILE: agentic_core\L5_safety\utils\evidence\phase5_l2_cid_reentry_evidence.py
--------------------------------------------------------------------------------
  Line 88: cid_registry_file = repo_root / "agentic_core" / "L2_execution" / "cid_registry.py"
  Line 104: # Check cid_registry.py
  Line 105: cid_wall_clock = scan_forbidden_tokens(cid_registry_file, wall_clock_tokens)

FILE: agentic_core\L6_observability\golden_evaluation\tool_use_ground_truth_evaluator.py
--------------------------------------------------------------------------------
  Line 2: Tool Use Ground Truth Evaluator - Deterministic Evaluation Contract.
  Line 4: Provides deterministic evaluation of tool selection against golden dataset.
  Line 17: """Deterministic result of tool use evaluation."""
  Line 29: """Evaluate tool use against golden dataset deterministically.
  Line 82: # Check if correct tool selection (simplified)

FILE: agentic_core\L6_observability\utils\integrity_report_generator_util.py
--------------------------------------------------------------------------------
  Line 9: 3. 100% registry coverage validation script
  Line 28: from agentic_core.L5_safety.enforcement.registry_verification_enforcer import (
  Line 29: RegistryVerifier,
  Line 62: # Phase 1: Registry Verification
  Line 63: registry_result: VerificationResult | None = None
  Line 75: registry_coverage_pass: bool = False
  Line 83: if self.registry_result:
  Line 84: scores.append(self.registry_result.coverage_percentage)
  Line 102: self.registry_verifier = RegistryVerifier(project_root)
  Line 103: self.project_root = self.registry_verifier.project_root
  Line 108: """Run Phase 1: Registry Verification."""
  Line 109: return self.registry_verifier.verify_registry()
  Line 121: registry_result: VerificationResult,
  Line 128: # Gap items from Phase 1: Missing from registry
  Line 129: for agent in registry_result.missing_agents:
  Line 134: category="Registry",
  Line 137: gap_description="Agent exists in filesystem but not in registry",
  Line 143: for orphan in registry_result.orphan_agents:
  Line 147: agent_path=orphan["registry_path"],
  Line 148: category="Registry",
  Line 149: current_state="In registry but file missing",
  Line 150: optimal_state="File exists or removed from registry",
  Line 193: def validate_registry_coverage(self, registry_result: VerificationResult) -> tuple[bool, str]:
  Line 194: """Validate 100% registry coverage."""
  Line 195: if registry_result.total_filesystem_agents == 0:
  Line 198: coverage = registry_result.coverage_percentage
  Line 201: return True, "Registry Coverage: 100% Pass"
  Line 203: missing_count = len(registry_result.missing_agents)
  Line 204: return False, f"Registry Coverage: {coverage:.1f}% ({missing_count} agents missing)"
  Line 212: result.registry_result = self.run_phase1()
  Line 217: result.total_agents = result.registry_result.total_filesystem_agents
  Line 221: result.registry_result,
  Line 226: # Validate registry coverage
  Line 227: result.registry_coverage_pass, _ = self.validate_registry_coverage(result.registry_result)
  Line 242: f"- **Registry Coverage:** {'PASS' if result.registry_coverage_pass else 'FAIL'}",
  Line 249: if result.registry_result:
  Line 250: reg = result.registry_result
  Line 253: "## Phase 1: Registry Verification",
  Line 258: f"| Registry Agents | {reg.total_registry_agents} |",
  Line 260: f"| Missing from Registry | {len(reg.missing_agents)} |",
  Line 367: "## Phase 4: Registry Coverage Validation",
  Line 370: f"Registry Coverage: {'100% Pass' if result.registry_coverage_pass else 'FAIL'}",
  Line 392: def validate_registry_coverage() -> tuple[bool, str]:
  Line 393: """Validate 100% registry coverage - standalone function."""
  Line 395: registry_result = reporter.run_phase1()
  Line 396: return reporter.validate_registry_coverage(registry_result)

FILE: agentic_core\L6_observability\dashboards\core\DashboardDataGenerator.py
--------------------------------------------------------------------------------
  Line 24: self.registry_path = self.project_root / AGENT_DISCOVERY_JSON
  Line 25: self.registry_by_path = {}
  Line 27: def load_registry(self) -> list[dict[str, Any]]:
  Line 28: """Load and index the authoritative agent registry."""
  Line 29: if not self.registry_path.exists():
  Line 32: data = json.loads(self.registry_path.read_text(encoding="utf-8"))
  Line 33: self.registry_by_path = {entry["path"].replace("\\", "/"): entry for entry in data}
  Line 36: log.error(f"Failed to load registry: {e}")
  Line 43: registry: dict[str, Any],
  Line 62: entry = registry.get(rel_path, {})
  Line 140: self.load_registry()

FILE: agentic_core\prompt_governance\contracts\slot_contracts.py
--------------------------------------------------------------------------------
  Line 21: """INJECTIONS slot — BINDING authority. Role fences, tool constraints, scope boundaries."""

FILE: agentic_core\prompt_governance\core\invariant_registry.py
--------------------------------------------------------------------------------
  Line 1: """Invariant registry for prompt governance enforcement constants.
  Line 4: Call validate_invariant_registry() explicitly to verify schema integrity.
  Line 34: def validate_invariant_registry() -> None:
  Line 46: raise RuntimeError(f"invariant_registry: READ_ONLY_ISOLATION fails MUTATION_BLOCK_SCHEMA: {code}")

FILE: agentic_core\prompt_governance\core\prompt_assembler.py
--------------------------------------------------------------------------------
  Line 303: from agentic_core.prompt_governance.core.invariant_registry import ITERATIVE_FEEDBACK_DIRECTIVE
  Line 634: # Add to registry

FILE: agentic_core\prompt_governance\scripts\audit_registry_linkages.py
--------------------------------------------------------------------------------
  Line 3: Registry Integrity Audit Script (Phase 5)
  Line 5: Verifies that every "Active" prompt in registry.json maps to a real, valid .jinja file
  Line 14: def load_registry(registry_path: Path) -> dict:
  Line 15: """Load the prompt registry JSON file."""
  Line 17: with open(registry_path, encoding="utf-8") as f:
  Line 20: print(f"ERROR: Failed to load registry: {e}")
  Line 59: def audit_registry_linkages(registry_path: Path, base_dir: Path) -> tuple[list[dict], list[dict]]:
  Line 61: Audit registry linkages.
  Line 66: registry = load_registry(registry_path)
  Line 71: prompts = registry.get("prompts", {})
  Line 123: registry_path = base_dir / "registry.json"
  Line 125: print("Registry Integrity Audit (Phase 5)")
  Line 127: print(f"Registry: {registry_path}")
  Line 131: if not registry_path.exists():
  Line 132: print(f"ERROR: Registry file not found: {registry_path}")
  Line 136: passed, failed = audit_registry_linkages(registry_path, base_dir)
  Line 162: print("❌ AUDIT FAILED - Registry integrity issues detected")
  Line 165: print("✅ AUDIT PASSED - All registry entries are valid")

FILE: agentic_core\prompt_governance\scripts\cleanup_duplicates_util.py
--------------------------------------------------------------------------------
  Line 4: One-time cleanup utility to collapse duplicate entries in registry.json.
  Line 7: python -m agentic_core.prompt_governance.version_registry.cleanup_duplicates
  Line 10: - Loads the current registry via get_prompt_registry() for consistency
  Line 14: - Saves the cleaned registry atomically
  Line 20: from agentic_core.prompt_governance.version_registry.prompt_registry_config import (
  Line 21: get_prompt_registry,
  Line 30: Collapse duplicate entries in registry.json.
  Line 38: # Load registry via get_prompt_registry() for consistency
  Line 39: registry = get_prompt_registry()
  Line 41: print(f"[CLEANUP] Loading registry from {registry.REGISTRY_FILE}")
  Line 42: Logger.info(f"Starting duplicate cleanup for {registry.REGISTRY_FILE}")
  Line 44: original_count = sum(len(entries) for entries in registry.registry.values())
  Line 54: for template_name, entries in list(registry.registry.items()):
  Line 91: registry.registry[template_name] = unique_entries
  Line 93: # Save using registry's atomic save method
  Line 94: registry._save_registry()
  Line 96: final_count = sum(len(entries) for entries in registry.registry.values())

FILE: agentic_core\prompt_governance\scripts\detect_template_drift.py
--------------------------------------------------------------------------------
  Line 6: version bump in the Registry (Instruction Drift detection).
  Line 16: def load_registry(registry_path: Path) -> dict:
  Line 17: """Load the prompt registry JSON file."""
  Line 19: with open(registry_path, encoding="utf-8") as f:
  Line 22: print(f"ERROR: Failed to load registry: {e}")
  Line 26: def detect_template_drift(registry_path: Path, base_dir: Path) -> tuple[list[dict], list[dict]]:
  Line 28: Detect template drift between registry and disk.
  Line 33: registry = load_registry(registry_path)
  Line 38: prompts = registry.get("prompts", {})
  Line 54: "registry_hash": prompt_data.get("content_hash", "N/A"),
  Line 63: registry_hash = prompt_data.get("content_hash", "")
  Line 65: if not registry_hash:
  Line 70: "issue": "No content hash in registry",
  Line 71: "registry_hash": "MISSING",
  Line 79: if disk_hash != registry_hash:
  Line 84: "issue": "Content hash mismatch - template modified without registry update",
  Line 85: "registry_hash": registry_hash,
  Line 95: "registry_hash": registry_hash,
  Line 108: registry_path = base_dir / "registry.json"
  Line 112: print(f"Registry: {registry_path}")
  Line 116: if not registry_path.exists():
  Line 117: print(f"ERROR: Registry file not found: {registry_path}")
  Line 121: synchronized, drifted = detect_template_drift(registry_path, base_dir)
  Line 135: print(f"     Registry Hash: {entry['registry_hash'][:16]}...")
  Line 140: print("   1. Update registry.json with correct content_hash")

FILE: agentic_core\prompt_governance\scripts\synchronize_registry_hashes.py
--------------------------------------------------------------------------------
  Line 3: Registry Synchronization Script (Phase 5 Recovery)
  Line 5: Updates content_hash in registry.json to match current template state.
  Line 16: def load_registry(registry_path: Path) -> dict:
  Line 17: """Load the prompt registry JSON file."""
  Line 19: with open(registry_path, encoding="utf-8") as f:
  Line 23: print(f"ERROR: Failed to load registry: {e}")
  Line 27: def save_registry(registry_path: Path, registry: dict):
  Line 28: """Save the updated registry."""
  Line 30: with open(registry_path, "w", encoding="utf-8") as f:
  Line 31: json.dump(registry, f, indent=2, ensure_ascii=False)
  Line 32: print(f"✅ Registry saved to {registry_path}")
  Line 34: print(f"ERROR: Failed to save registry: {e}")
  Line 38: def synchronize_registry_hashes(registry_path: Path, base_dir: Path) -> dict:
  Line 40: Synchronize registry content hashes with actual template files.
  Line 45: registry = load_registry(registry_path)
  Line 46: prompts = registry.get("prompts", {})
  Line 97: registry_path = base_dir / "registry.json"
  Line 99: print("Registry Synchronization Script (Phase 5 Recovery)")
  Line 101: print(f"Registry: {registry_path}")
  Line 105: if not registry_path.exists():
  Line 106: print(f"ERROR: Registry file not found: {registry_path}")
  Line 109: # Backup original registry
  Line 110: backup_path = registry_path.with_suffix(".json.backup")
  Line 114: shutil.copy2(registry_path, backup_path)
  Line 123: stats = synchronize_registry_hashes(registry_path, base_dir)
  Line 125: # Save updated registry
  Line 126: registry = load_registry(registry_path)
  Line 127: registry["last_sync_date"] = str(Path(__file__).stat().st_mtime)
  Line 128: save_registry(registry_path, registry)
  Line 142: print("✅ Registry synchronized successfully")
  Line 146: print("✅ Registry already synchronized")

FILE: agentic_core\prompt_governance\registry\backups\__init__.py
--------------------------------------------------------------------------------
  Line 1: """Prompt Governance Registry Backups - Historical registry snapshots."""

FILE: agentic_core\prompt_governance\security\utils\injection_scan_util.py
--------------------------------------------------------------------------------
  Line 33: Logger.debug("Injection scan invoked: source=%s, length=%d", source, len(text))

FILE: agentic_core\prompt_governance\security\validators\output_schema_validator.py
--------------------------------------------------------------------------------
  Line 167: from agentic_core.prompt_governance.core.invariant_registry import validate_invariant_registry
  Line 169: validate_invariant_registry()
  Line 172: from agentic_core.prompt_governance.core.invariant_registry import READ_ONLY_ISOLATION

FILE: agentic_core\runtime\config\security_level_config.py
--------------------------------------------------------------------------------
  Line 965: """Invoke healing chain via super() with V15 manifest at boundary."""

FILE: agentic_core\runtime\config\signal_quality_config.py
--------------------------------------------------------------------------------
  Line 821: # Global enhancer registry

FILE: agentic_core\runtime\engine\agent_engine.py
--------------------------------------------------------------------------------
  Line 13: from agentic_core.runtime.tools import ToolRegistry
  Line 20: def __init__(self, pattern: BaseReasoningPattern, tools: ToolRegistry, max_turns: int = 5):
  Line 112: # The pattern analyzes state and decides next tool
  Line 124: tool = self.tools.get(tool_name)
  Line 125: if not tool:
  Line 127: logger.error(f"Tool '{tool_name}' not found. Available: {available}")
  Line 131: observation = await tool.run(**tool_args)
  Line 133: logger.error(f"Tool execution failed: {tool_name} - {e}", exc_info=True)
  Line 136: message=f"Critical failure executing tool '{tool_name}': {e}",

FILE: agentic_core\runtime\engine\ast_relocator.py
--------------------------------------------------------------------------------
  Line 9: from agentic_core.L5_safety.config.structure_blueprint_config import SEMANTIC_L2_REGISTRY
  Line 72: [SEMANTIC SCORING] Calculates placement confidence using the Rich Semantic Registry.
  Line 80: for l1, l2_dict in SEMANTIC_L2_REGISTRY.items():

FILE: agentic_core\runtime\exceptions\healer_exceptions.py
--------------------------------------------------------------------------------
  Line 63: class ValidationRegistryError(HealerError):
  Line 65: Raised when there's an error in the validation registry lookup.
  Line 67: This occurs when the CANON_VALIDATION_REGISTRY is malformed
  Line 71: def __init__(self, registry_key: str, reason: str):
  Line 72: message = f"Validation registry error for '{registry_key}': {reason}"
  Line 73: super().__init__(message, {"registry_key": registry_key, "reason": reason})
  Line 74: self.registry_key = registry_key

FILE: agentic_core\runtime\exceptions\runtime_exceptions.py
--------------------------------------------------------------------------------
  Line 29: Raised when a tool execution fails.
  Line 31: This exception replaces silent error swallowing in tool execution,
  Line 32: ensuring agents are aware of tool failures and can take corrective action.
  Line 54: """Raised when a requested tool is not found in the registry."""
  Line 57: message = f"Tool '{tool_name}' not found in registry"

FILE: agentic_core\runtime\utils\discovery_parser_util.py
--------------------------------------------------------------------------------
  Line 47: # [SSOT] Global metadata registry - marked Final to prevent re-binding

FILE: agentic_core\runtime\utils\discovery_util.py
--------------------------------------------------------------------------------
  Line 5: It includes the DiscoveredAgentRecord dataclass and AgentRegistry class for finding and
  Line 33: class AgentRegistry:

FILE: agentic_core\runtime\utils\dynamic_loader_util.py
--------------------------------------------------------------------------------
  Line 27: # Registry of protocol to implementation mappings
  Line 28: IMPLEMENTATION_REGISTRY: dict[str, dict[str, str]] = {
  Line 94: registry_entry = cls.IMPLEMENTATION_REGISTRY.get(protocol_name)
  Line 95: if registry_entry is None:
  Line 100: module_path=registry_entry["module"],
  Line 101: class_name=registry_entry["class"],
  Line 175: cls.IMPLEMENTATION_REGISTRY[protocol_name] = {
  Line 204: return list(cls.IMPLEMENTATION_REGISTRY.keys())

FILE: agentic_core\runtime\utils\runtime_bootstrapper_util.py
--------------------------------------------------------------------------------
  Line 18: from agentic_core.L4_state.audit_trails.genealogy import GenealogyRegistry
  Line 43: self._registry = {}
  Line 58: genealogy=self._get_tool("genealogy", lambda: GenealogyRegistry(self.config)),
  Line 67: if key not in self._registry:
  Line 68: self._registry[key] = constructor_func()
  Line 69: return self._registry[key]

FILE: agentic_core\runtime\utils\sovereign_dependency_error_util.py
--------------------------------------------------------------------------------
  Line 62: genealogy: GenealogyRegistry instance (injected)
  Line 92: "SubatomicHop requires 'genealogy' (GenealogyRegistry) to be injected.",
  Line 320: results.append({"tool": "sandbox", "result": result})
  Line 322: result = await self.mcp.call_tool(tool_name, tool_args)  # Assign to a variable
  Line 325: results.append({"tool": tool_name, "result": result})
  Line 334: PAYLOAD={"tool": tool_name, "error": str(e)},

FILE: agentic_core\runtime\utils\sovereign_scan_util.py
--------------------------------------------------------------------------------
  Line 79: from agentic_core.L5_safety.config.structure_blueprint_config import SOVEREIGN_REGISTRY
  Line 87: for root_name in SOVEREIGN_REGISTRY.keys():

FILE: agentic_core\runtime\utils\subatomic_hop_util.py
--------------------------------------------------------------------------------
  Line 59: genealogy: GenealogyRegistry instance (injected)
  Line 81: self.genealogy = self._ensure_dep(genealogy, "GenealogyRegistry")
  Line 109: f"SubatomicHop Missing critical tool: {name}. "
  Line 273: results.append({"tool": "sandbox", "result": result})
  Line 275: result = await self.mcp.call_tool(tool_name, tool_args)
  Line 278: results.append({"tool": tool_name, "result": result})
  Line 288: PAYLOAD={"tool": tool_name, "error": str(e)},

FILE: agentic_core\seams\contracts\mcp.py
--------------------------------------------------------------------------------
  Line 24: async def call_tool(self, tool: str, **kwargs: Any) -> Any: ...

================================================================================
SUMMARY
================================================================================
No formal PTC/tool registry infrastructure detected in agentic_core.
References to 'tool' are primarily in comments, docstrings, or module names.
No ToolSpec, call_tool, or programmatic tool calling framework found.
```

### Non-Gateway Write Primitive Inventory
```
================================================================================
NON-GATEWAY WRITE PRIMITIVE INVENTORY
================================================================================


FILE: agentic_core\interfaces\IBlackboardLeaseVerifier.py
--------------------------------------------------------------------------------
  Line 168: with open(resolved_path, encoding="utf-8") as f:
  Line 201: with open(resolved_path, encoding="utf-8") as f:
  Line 240: resolved_path.parent.mkdir(parents=True, exist_ok=True)
  Line 242: with open(resolved_path, "w", encoding="utf-8") as f:
  Line 405: resolved_path.mkdir(parents=args.parents, exist_ok=True)

FILE: agentic_core\interfaces\IBlackboardLeaseVerifierProtocol.py
--------------------------------------------------------------------------------
  Line 168: with open(resolved_path, encoding="utf-8") as f:
  Line 201: with open(resolved_path, encoding="utf-8") as f:
  Line 240: resolved_path.parent.mkdir(parents=True, exist_ok=True)
  Line 242: with open(resolved_path, "w", encoding="utf-8") as f:
  Line 407: resolved_path.mkdir(parents=parents, exist_ok=True)

FILE: agentic_core\mixins\atomic_execution_mixin.py
--------------------------------------------------------------------------------
  Line 93: self._backup_dir.mkdir(parents=True, exist_ok=True)
  Line 128: backup_dir.mkdir(parents=True, exist_ok=True)
  Line 135: shutil.copy2(file_path, backup_path)
  Line 161: shutil.copy2(backup.backup_path, backup.original_path)
  Line 170: created_path.unlink()
  Line 187: shutil.rmtree(backup_dir)
  Line 284: file_path.parent.mkdir(parents=True, exist_ok=True)
  Line 285: file_path.write_text(content, encoding=encoding)
  Line 315: file_path.unlink()
  Line 361: dst_path.parent.mkdir(parents=True, exist_ok=True)
  ... (1 more matches)

FILE: agentic_core\mixins\cst_healer_mixin.py
--------------------------------------------------------------------------------
  Line 275: context.file_path.write_text(modified_code, encoding="utf-8")

FILE: agentic_core\mixins\healing_policy_mixin.py
--------------------------------------------------------------------------------
  Line 154: with open(file_path, encoding="utf-8") as f:

FILE: agentic_core\mixins\hygiene_mixin.py
--------------------------------------------------------------------------------
  Line 120: file_path.unlink()
  Line 131: duplicate_path.unlink()

FILE: agentic_core\prompt_governance\prompt_loader.py
--------------------------------------------------------------------------------
  Line 82: with open(prompt_file, encoding="utf-8") as f:

FILE: agentic_core\utils\ast_fuzzy_util.py
--------------------------------------------------------------------------------
  Line 145: with open(path, "rb") as f:

FILE: agentic_core\utils\fs_util.py
--------------------------------------------------------------------------------
  Line 61: with open(file_path, "rb") as f:

FILE: agentic_core\utils\structural_healing_engine_util.py
--------------------------------------------------------------------------------
  Line 57: target_path.parent.mkdir(parents=True, exist_ok=True)
  Line 58: shutil.move(str(source_path), str(target_path))
  Line 61: shutil.move(str(target_path), str(source_path))

FILE: agentic_core\config\core\config_loader.py
--------------------------------------------------------------------------------
  Line 22: with open(path_to_check, encoding="utf-8") as f:

FILE: agentic_core\config\core\yaml_injection_loader.py
--------------------------------------------------------------------------------
  Line 159: with open(yaml_file, encoding="utf-8") as f:

FILE: agentic_core\knowledge\research_cache\cache_store_util.py
--------------------------------------------------------------------------------
  Line 36: self.cache_dir.mkdir(parents=True, exist_ok=True)
  Line 52: with self.cache_file.open("r", encoding="utf-8") as f:
  Line 95: with self.cache_file.open("r", encoding="utf-8") as f:
  Line 125: with self.cache_file.open("a", encoding="utf-8") as f:
  Line 127: sum(1 for _ in open(self.cache_file, encoding="utf-8")) if self.cache_file.exists() else 0
  Line 141: self.cache_file.unlink()

FILE: agentic_core\L0_routing\enforcement\mutation_prohibition.py
--------------------------------------------------------------------------------
  Line 7: os.rename/remove/unlink, shutil.move/rmtree, and open(..., 'w'/'a').
  Line 107: log_file.parent.mkdir(parents=True, exist_ok=True)
  Line 109: with open(log_file, 'a', encoding='utf-8') as f:
  Line 209: op: Operation name (e.g. "write_text", "json.dump", "shutil.move").
  Line 250: Path(filepath).write_text(content, encoding=encoding)
  Line 262: Path(filepath).write_bytes(data)
  Line 277: with open(filepath, "w", encoding="utf-8") as f:
  Line 288: """Guarded shutil.move replacement."""
  Line 289: assert_no_persistent_write(layer, "shutil.move", str(dst), trace_id)
  Line 290: shutil.move(str(src), str(dst))
  ... (8 more matches)

FILE: agentic_core\L0_routing\meta_control\config_store.py
--------------------------------------------------------------------------------
  Line 47: path.parent.mkdir(parents=True, exist_ok=True)

FILE: agentic_core\L0_routing\meta_control\meta_apply.py
--------------------------------------------------------------------------------
  Line 144: path.parent.mkdir(parents=True, exist_ok=True)
  Line 148: tmp.write_text(content, encoding="utf-8")

FILE: agentic_core\L0_routing\reasoning\RootCustomsAgent.py
--------------------------------------------------------------------------------
  Line 61: with open(file_path, encoding="utf-8") as f:
  Line 171: with open(file_path, encoding="utf-8", errors="ignore") as f:
  Line 560: target_dir.mkdir(parents=True, exist_ok=True)
  Line 563: assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
  Line 564: shutil.move(str(source), str(target_file))

FILE: agentic_core\L0_routing\reasoning\SSOTFolderCleanupAgent.py
--------------------------------------------------------------------------------
  Line 353: full_target.parent.mkdir(parents=True, exist_ok=True)
  Line 411: py_file.write_text(new_content, encoding="utf-8")
  Line 515: dir_path.rmdir()

FILE: agentic_core\L0_routing\scripts\add_dataclass_to_agents_util.py
--------------------------------------------------------------------------------
  Line 119: file_path.write_text(source, encoding="utf-8")
  Line 136: with open(discovery_path, encoding="utf-8") as f:

FILE: agentic_core\L0_routing\scripts\add_subatomic_safe_util.py
--------------------------------------------------------------------------------
  Line 20: with open(project_root / "agent_discovery_full.json", encoding="utf-8") as f:
  Line 128: agent_path.write_text(new_content, encoding="utf-8")

FILE: agentic_core\L0_routing\scripts\add_subatomic_testing_to_agents_util.py
--------------------------------------------------------------------------------
  Line 14: with open("agent_discovery_full.json") as f:
  Line 113: agent_path.write_text(content, encoding="utf-8")

FILE: agentic_core\L0_routing\scripts\add_subatomic_tests_util.py
--------------------------------------------------------------------------------
  Line 16: with open(discovery_file, encoding="utf-8") as f:
  Line 147: agent_path.write_text(content, encoding="utf-8")

FILE: agentic_core\L0_routing\scripts\agent_analysis_config.py
--------------------------------------------------------------------------------
  Line 306: report_path.parent.mkdir(parents=True, exist_ok=True)
  Line 308: report_path.write_text(report, encoding="utf-8")

FILE: agentic_core\L0_routing\scripts\agent_capability_supplement_util.py
--------------------------------------------------------------------------------
  Line 42: with open(REPORT_PATH, encoding="utf-8") as f:
  Line 407: report_path.write_text(md_report, encoding="utf-8")

FILE: agentic_core\L0_routing\scripts\aggressive_dedup_util.py
--------------------------------------------------------------------------------
  Line 208: Path(f).unlink()

FILE: agentic_core\L0_routing\scripts\align_tests_structure_util.py
--------------------------------------------------------------------------------
  Line 36: os.makedirs(path, exist_ok=True)
  Line 42: with open(init_file, "w") as f:
  Line 49: with open(gitkeep, "w") as f:

FILE: agentic_core\L0_routing\scripts\archive_duplicates_util.py
--------------------------------------------------------------------------------
  Line 32: ARCHIVE_BASE.mkdir(parents=True, exist_ok=True)
  Line 47: assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
  Line 48: shutil.move(str(source_path), str(dest_path))

FILE: agentic_core\L0_routing\scripts\archive_duplicate_tests_util.py
--------------------------------------------------------------------------------
  Line 45: archive_dir.mkdir(parents=True, exist_ok=True)
  Line 55: archive_target.parent.mkdir(parents=True, exist_ok=True)
  Line 57: assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
  Line 58: shutil.move(str(dup), str(archive_target))

FILE: agentic_core\L0_routing\scripts\auto_remediate_signatures_util.py
--------------------------------------------------------------------------------
  Line 96: with open(file_path, encoding="utf-8") as f:
  Line 138: with open(file_path, "w", encoding="utf-8") as f:

FILE: agentic_core\L0_routing\scripts\bulk_hierarchy_heal_util.py
--------------------------------------------------------------------------------
  Line 54: with open(audit_log, "a") as f:
  Line 69: with open(output_file, "w", encoding="utf-8") as f:
  Line 100: dest_dir.mkdir(parents=True, exist_ok=True)
  Line 101: assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
  Line 102: shutil.move(str(file_path), str(dest_path))

FILE: agentic_core\L0_routing\scripts\bulk_mcp_harden_util.py
--------------------------------------------------------------------------------
  Line 24: with open(DISCOVERY_PATH) as f:
  Line 62: file_path.write_text(new_content, encoding="utf-8")
  Line 80: file_path.write_text(new_content, encoding="utf-8")

FILE: agentic_core\L0_routing\scripts\check_sovereign_base_util.py
--------------------------------------------------------------------------------
  Line 7: with open(PROJECT_ROOT / "agent_discovery_full.json") as f:

FILE: agentic_core\L0_routing\scripts\class_info.py
--------------------------------------------------------------------------------
  Line 80: with open(file_path, "rb") as f:
  Line 92: with open(file_path, encoding="utf-8", errors="ignore") as f:
  Line 101: with open(file_path, encoding="utf-8", errors="ignore") as f:
  Line 121: with open(file_path, encoding="utf-8", errors="ignore") as f:
  Line 459: with open(file_path, encoding="utf-8", errors="ignore") as f:
  Line 699: with open(report_path, "w", encoding="utf-8") as f:
  Line 733: with open(json_path, "w", encoding="utf-8") as f:

FILE: agentic_core\L0_routing\scripts\code_entity.py
--------------------------------------------------------------------------------
  Line 541: report_path.write_text(report_text, encoding="utf-8")

FILE: agentic_core\L0_routing\scripts\collision_resolver.py
--------------------------------------------------------------------------------
  Line 199: winner.rename(target_path)

FILE: agentic_core\L0_routing\scripts\colors.py
--------------------------------------------------------------------------------
  Line 152: state_path.write_text(_json.dumps(_runtime_state, indent=2, default=str), encoding="utf-8")

FILE: agentic_core\L0_routing\scripts\compare_ui_components_util.py
--------------------------------------------------------------------------------
  Line 88: with open(mono_path, encoding="utf-8") as f:
  Line 97: with open(mod_path, encoding="utf-8") as f:
  Line 109: with open(js_path, encoding="utf-8") as f:

FILE: agentic_core\L0_routing\scripts\core_synthesis_executor.py
--------------------------------------------------------------------------------
  Line 31: with open("core_refinery_analysis_results.json") as f:
  Line 88: self.archives_path.mkdir(parents=True, exist_ok=True)
  Line 96: archive_dest.parent.mkdir(parents=True, exist_ok=True)
  Line 99: assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
  Line 100: shutil.move(str(file_path), str(archive_dest))
  Line 121: self.utils_path.mkdir(exist_ok=True)
  Line 146: archive_dest.parent.mkdir(parents=True, exist_ok=True)
  Line 247: target_path.write_text(target_content, encoding="utf-8")
  Line 273: self.utils_path.mkdir(exist_ok=True)
  Line 280: assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
  ... (2 more matches)

FILE: agentic_core\L0_routing\scripts\count_territories_util.py
--------------------------------------------------------------------------------
  Line 8: with open("agentic_core/L6_observability/dashboards/autonomy_dashboard.html", encoding="utf-8") as f

FILE: agentic_core\L0_routing\scripts\c_c_measurement.py
--------------------------------------------------------------------------------
  Line 172: output_file.parent.mkdir(parents=True, exist_ok=True)
  Line 179: with open(output_file, "w") as f:

FILE: agentic_core\L0_routing\scripts\debris_hunter.py
--------------------------------------------------------------------------------
  Line 86: os.remove(path)

FILE: agentic_core\L0_routing\scripts\debug_invocation_pipeline_util.py
--------------------------------------------------------------------------------
  Line 11: registry = json.load(open(PROJECT_ROOT / AGENT_DISCOVERY_JSON))

FILE: agentic_core\L0_routing\scripts\disposition.py
--------------------------------------------------------------------------------
  Line 437: with open("CORE_REFINERY_ANALYSIS.md", "w", encoding="utf-8") as f:
  Line 458: with open("core_refinery_analysis_results.json", "w") as f:

FILE: agentic_core\L0_routing\scripts\drift.py
--------------------------------------------------------------------------------
  Line 120: with open(full_path, encoding="utf-8") as source:

FILE: agentic_core\L0_routing\scripts\emoji_fixer.py
--------------------------------------------------------------------------------
  Line 47: with open(file_path, encoding="utf-8") as f:
  Line 53: with open(file_path, "w", encoding="utf-8") as f:

FILE: agentic_core\L0_routing\scripts\execute_ssot.py
--------------------------------------------------------------------------------
  Line 542: with open(fp, encoding="utf-8") as f:
  Line 929: test_file.unlink()
  Line 1318: temp_dir.mkdir(parents=True, exist_ok=True)
  Line 1340: os.remove(temp_name)
  Line 1485: os.remove(temp_name)
  Line 2367: reports_dir.mkdir(parents=True, exist_ok=True)
  Line 2375: with open(json_path, "w", encoding="utf-8") as f:
  Line 2380: with open(md_path, "w", encoding="utf-8") as f:
  Line 3354: with open(file_path, encoding="utf-8") as f:

FILE: agentic_core\L0_routing\scripts\extract_net.py
--------------------------------------------------------------------------------
  Line 19: assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
  Line 20: shutil.rmtree(staging_dir)
  Line 21: staging_dir.mkdir()
  Line 32: shutil.copy2(py_file, dest_path)

FILE: agentic_core\L0_routing\scripts\extract_unique_content_util.py
--------------------------------------------------------------------------------
  Line 259: target_dir.mkdir(parents=True, exist_ok=True)
  Line 270: shutil.copy2(str(src), str(dst))
  Line 280: target_dir.mkdir(parents=True, exist_ok=True)
  Line 285: shutil.copy2(str(src), str(dst))

FILE: agentic_core\L0_routing\scripts\find_agents_in_low_heal_territories_util.py
--------------------------------------------------------------------------------
  Line 8: with open(

FILE: agentic_core\L0_routing\scripts\find_base_class_agents_util.py
--------------------------------------------------------------------------------
  Line 10: with open(discovery_file, encoding="utf-8") as f:

FILE: agentic_core\L0_routing\scripts\find_low_heal_territories_util.py
--------------------------------------------------------------------------------
  Line 7: with open(

FILE: agentic_core\L0_routing\scripts\find_low_typed_documented_util.py
--------------------------------------------------------------------------------
  Line 9: with open(PROJECT_ROOT / "agent_discovery_full.json", encoding="utf-8") as f:

FILE: agentic_core\L0_routing\scripts\find_missing_agents_util.py
--------------------------------------------------------------------------------
  Line 11: with open(DISCOVERY_PATH, encoding="utf-8") as f:

FILE: agentic_core\L0_routing\scripts\find_missing_invocations_util.py
--------------------------------------------------------------------------------
  Line 10: with open("agent_discovery_full.json") as f:

FILE: agentic_core\L0_routing\scripts\find_non_hardened_l0_util.py
--------------------------------------------------------------------------------
  Line 9: with open(project_root / "agent_discovery_full.json", encoding="utf-8") as f:

FILE: agentic_core\L0_routing\scripts\find_open_heal_invocations_util.py
--------------------------------------------------------------------------------
  Line 11: with open("agent_discovery_full.json") as f:

FILE: agentic_core\L0_routing\scripts\find_real_duplicates_v2_util.py
--------------------------------------------------------------------------------
  Line 94: output_file.parent.mkdir(exist_ok=True)
  Line 98: with open(output_file, "w", encoding="utf-8") as f:

FILE: agentic_core\L0_routing\scripts\find_remaining_missing_heal_util.py
--------------------------------------------------------------------------------
  Line 14: with open(project_root / "agent_discovery_full.json", encoding="utf-8") as f:

FILE: agentic_core\L0_routing\scripts\fission_executor_util.py
--------------------------------------------------------------------------------
  Line 38: os.makedirs(submodule_dir, exist_ok=True)
  Line 50: with open(module_file, "w", encoding="utf-8", errors="ignore") as f:
  Line 73: shutil.copy2(file_path, f"{backup_path}.tmp")
  Line 75: with open(file_path, "w", encoding="utf-8", errors="ignore") as f:

FILE: agentic_core\L0_routing\scripts\flatten_scripts_directory_util.py
--------------------------------------------------------------------------------
  Line 57: assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
  Line 58: shutil.move(str(py_file), str(target))
  Line 70: dir_path.rmdir()

FILE: agentic_core\L0_routing\scripts\forensic_discovery_prep.py
--------------------------------------------------------------------------------
  Line 100: with path.open("rb") as f:
  Line 307: path.parent.mkdir(parents=True, exist_ok=True)
  Line 310: tmp.write_text(data, encoding="utf-8")

FILE: agentic_core\L0_routing\scripts\full_agent_discovery.py
--------------------------------------------------------------------------------
  Line 122: with path.open("rb") as f:

FILE: agentic_core\L0_routing\scripts\generate_dashboard_ssot_util.py
--------------------------------------------------------------------------------
  Line 53: with open(YAML_CONFIG, encoding="utf-8") as f:
  Line 66: with open(PYTHON_OUTPUT, encoding="utf-8") as f:
  Line 399: with open(PYTHON_OUTPUT, "w", encoding="utf-8") as f:
  Line 409: JS_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
  Line 413: with open(JS_OUTPUT, "w", encoding="utf-8") as f:

FILE: agentic_core\L0_routing\scripts\identify_agents_without_tests_util.py
--------------------------------------------------------------------------------
  Line 14: with open(project_root / "agent_discovery_full.json", encoding="utf-8") as f:

FILE: agentic_core\L0_routing\scripts\identify_low_quality_agents_util.py
--------------------------------------------------------------------------------
  Line 30: with open(DISCOVERY_FILE, encoding="utf-8") as f:

FILE: agentic_core\L0_routing\scripts\investigate_sovereign_base_util.py
--------------------------------------------------------------------------------
  Line 7: with open(PROJECT_ROOT / "agent_discovery_full.json") as f:

FILE: agentic_core\L0_routing\scripts\layer_summary_util.py
--------------------------------------------------------------------------------
  Line 8: data = json.load(open(AGENT_DISCOVERY_JSON))

FILE: agentic_core\L0_routing\scripts\list_layer_agents_util.py
--------------------------------------------------------------------------------
  Line 18: data = json.load(open(AGENT_DISCOVERY_JSON))

FILE: agentic_core\L0_routing\scripts\populate_ssot_folders_util.py
--------------------------------------------------------------------------------
  Line 162: init_path.write_text(generate_init_content(l1, l2), encoding="utf-8")
  Line 172: d3_init.write_text(generate_init_content(l1, l2, depth3.name), encoding="utf-8")

FILE: agentic_core\L0_routing\scripts\root_hygiene_util.py
--------------------------------------------------------------------------------
  Line 41: ops_scripts.mkdir(exist_ok=True)
  Line 42: l0_scripts.mkdir(exist_ok=True, parents=True)
  Line 57: assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
  Line 58: shutil.move(str(item), str(target))
  Line 69: assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
  Line 70: shutil.rmtree(target)  # Force overwrite logic for dirs
  Line 71: assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
  Line 72: shutil.move(str(item), str(target))
  Line 76: root_scripts.rmdir()
  Line 89: reports_cov.parent.mkdir(exist_ok=True)
  ... (7 more matches)

FILE: agentic_core\L0_routing\scripts\run_guardian_manifest.py
--------------------------------------------------------------------------------
  Line 48: with open(file_path, "rb") as f:

FILE: agentic_core\L0_routing\scripts\run_hygiene_guardian_util.py
--------------------------------------------------------------------------------
  Line 111: path.unlink()
  Line 114: assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
  Line 115: shutil.rmtree(path)
  Line 138: folder.rmdir()

FILE: agentic_core\L0_routing\scripts\scan_testing_compliance_util.py
--------------------------------------------------------------------------------
  Line 150: with open(DISCOVERY_JSON, encoding="utf-8") as f:
  Line 348: with open(report_path, "w", encoding="utf-8") as f:

FILE: agentic_core\L0_routing\scripts\sovereign_precommit_no_hardcoded_util.py
--------------------------------------------------------------------------------
  Line 37: with open(filepath, encoding="utf-8") as f:

FILE: agentic_core\L0_routing\scripts\sovereign_precommit_no_raw_prompts_util.py
--------------------------------------------------------------------------------
  Line 34: with open(filepath, encoding="utf-8") as f:

FILE: agentic_core\L0_routing\scripts\ssot_cli.py
--------------------------------------------------------------------------------
  Line 168: output_path.write_text(report.to_markdown(), encoding="utf-8")

FILE: agentic_core\L0_routing\scripts\validate_base_agents_util.py
--------------------------------------------------------------------------------
  Line 24: data = json.load(open("agent_discovery_full.json"))

FILE: agentic_core\L0_routing\scripts\verify_healing_metrics_util.py
--------------------------------------------------------------------------------
  Line 21: with open(DISCOVERY_FILE, encoding="utf-8") as f:

FILE: agentic_core\L0_routing\scripts\verify_heal_invocation_util.py
--------------------------------------------------------------------------------
  Line 6: data = json.load(open("agent_discovery_full.json"))

FILE: agentic_core\L0_routing\scripts\verify_intentional_variants_util.py
--------------------------------------------------------------------------------
  Line 26: with open(file_path, encoding="utf-8") as f:
  Line 343: with open(output_file, "w", encoding="utf-8") as f:

FILE: agentic_core\L0_routing\scripts\verify_manifest_cleanliness_util.py
--------------------------------------------------------------------------------
  Line 29: with open(manifest_path) as f:

FILE: agentic_core\L0_routing\scripts\verify_manifest_util.py
--------------------------------------------------------------------------------
  Line 102: with open(report_path) as f:

FILE: agentic_core\L0_routing\scripts\verify_row_order_util.py
--------------------------------------------------------------------------------
  Line 7: with open("agentic_core/L6_observability/dashboards/data/dashboard_data.js", encoding="utf-8") as f:

FILE: agentic_core\L0_routing\scripts\verify_territory_counts_util.py
--------------------------------------------------------------------------------
  Line 10: with open("agentic_core/L6_observability/dashboards/autonomy_dashboard.html", encoding="utf-8") as f

FILE: agentic_core\L0_routing\types\guardian_contract.py
--------------------------------------------------------------------------------
  Line 934: output_dir.mkdir(parents=True, exist_ok=True)
  Line 937: out_path.write_text(result.to_json(), encoding="utf-8")
  Line 943: with open(path, encoding="utf-8") as f:

FILE: agentic_core\L0_routing\types\guardian_contract_types.py
--------------------------------------------------------------------------------
  Line 934: output_dir.mkdir(parents=True, exist_ok=True)
  Line 937: out_path.write_text(result.to_json(), encoding="utf-8")
  Line 943: with open(path, encoding="utf-8") as f:

FILE: agentic_core\L0_routing\types\integration_contract.py
--------------------------------------------------------------------------------
  Line 79: path.parent.mkdir(parents=True, exist_ok=True)
  Line 81: path.write_text(self.to_json(), encoding="utf-8")

FILE: agentic_core\L0_routing\types\integration_contract_types.py
--------------------------------------------------------------------------------
  Line 79: path.parent.mkdir(parents=True, exist_ok=True)
  Line 81: path.write_text(self.to_json(), encoding="utf-8")

FILE: agentic_core\L0_routing\types\routing_contracts.py
--------------------------------------------------------------------------------
  Line 607: out_dir.mkdir(parents=True, exist_ok=True)
  Line 609: with out_path.open("a", encoding="utf-8") as fh:

FILE: agentic_core\L0_routing\utils\add_test_coverage_util.py
--------------------------------------------------------------------------------
  Line 71: filepath.write_text(new_content, encoding="utf-8")
  Line 77: agents = json.load(open(AGENT_DISCOVERY_JSON))
  Line 433: filepath.write_text("\n".join(lines), encoding="utf-8")

FILE: agentic_core\L0_routing\utils\complexity_visitor_util.py
--------------------------------------------------------------------------------
  Line 1289: os.remove(stale_path)
  Line 1669: tmp_json.write_text(json_text, encoding="utf-8")
  Line 1691: tmp_manifest.write_text(manifest_text, encoding="utf-8")

FILE: agentic_core\L0_routing\utils\core_integrity_util.py
--------------------------------------------------------------------------------
  Line 69: assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
  Line 70: shutil.rmtree(pycache)
  Line 93: cls.GOLDEN_SEAL_FILE.write_text(current_hash)
  Line 152: cls.GOLDEN_SEAL_FILE.write_text(current_hash)

FILE: agentic_core\L0_routing\utils\file_utils_util.py
--------------------------------------------------------------------------------
  Line 9: raw open()/write() calls.
  Line 34: Path(path).mkdir(parents=True, exist_ok=True)
  Line 85: shutil.copy2(path, backup_path)
  Line 96: temp_path.write_text(content, encoding=encoding)
  Line 104: temp_path.unlink()
  Line 125: with open(path, "a", encoding=encoding) as f:
  Line 153: shutil.copy2(path, backup_path)
  Line 158: path.unlink()
  Line 187: shutil.copy2(dst, backup_path)
  Line 195: assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
  ... (1 more matches)

FILE: agentic_core\L0_routing\utils\fix_all_tunnels_util.py
--------------------------------------------------------------------------------
  Line 42: target_dir.mkdir(parents=True, exist_ok=True)
  Line 43: assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
  Line 44: shutil.move(str(py_file), str(target_file))
  Line 58: dir_path.rmdir()

FILE: agentic_core\L0_routing\utils\fix_depth_violations_util.py
--------------------------------------------------------------------------------
  Line 47: stage_path.mkdir(exist_ok=True)
  Line 51: stage_init.write_text('"""Stage module."""\n')
  Line 54: assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
  Line 55: shutil.move(str(py_file), str(target))

FILE: agentic_core\L0_routing\utils\fix_mission_runner_util.py
--------------------------------------------------------------------------------
  Line 18: with open(mission_runner, encoding="utf-8") as f:
  Line 40: with open(mission_runner, "w", encoding="utf-8") as f:

FILE: agentic_core\L0_routing\utils\fix_remaining_depth_util.py
--------------------------------------------------------------------------------
  Line 23: stage.mkdir(exist_ok=True)
  Line 25: (stage / "__init__.py").write_text('"""Stage module."""\n')
  Line 33: assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
  Line 34: shutil.move(str(f), str(target))
  Line 40: stage.mkdir(exist_ok=True)
  Line 42: (stage / "__init__.py").write_text('"""Stage module."""\n')
  Line 50: assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
  Line 51: shutil.move(str(f), str(target))

FILE: agentic_core\L0_routing\utils\force_annexation_util.py
--------------------------------------------------------------------------------
  Line 35: target_dir.mkdir(parents=True, exist_ok=True)
  Line 52: assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
  Line 53: shutil.move(str(item), str(target_item))
  Line 59: assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
  Line 60: shutil.rmtree(old_path)

FILE: agentic_core\L0_routing\utils\gravity_audit_util.py
--------------------------------------------------------------------------------
  Line 28: with open(py_file, encoding="utf-8") as f:

FILE: agentic_core\L0_routing\utils\manifest_guardian_util.py
--------------------------------------------------------------------------------
  Line 29: with open(file_path, "rb") as f:
  Line 41: with open(cls.LOCK_FILE, "w") as f:
  Line 64: with open(cls.LOCK_FILE) as f:

FILE: agentic_core\L0_routing\utils\scorched_earth_merge_util.py
--------------------------------------------------------------------------------
  Line 63: layer_path.mkdir(parents=True, exist_ok=True)
  Line 84: assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
  Line 85: shutil.move(str(item), str(dest_path))
  Line 93: assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
  Line 94: shutil.rmtree(item)

FILE: agentic_core\L0_routing\utils\sovereign_alignment_v2_util.py
--------------------------------------------------------------------------------
  Line 32: dest_path.mkdir(parents=True, exist_ok=True)
  Line 38: assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
  Line 39: shutil.move(str(item), str(dest_item))
  Line 41: src_path.rmdir()
  Line 54: with open(init_file, "w", encoding="utf-8") as f:
  Line 73: with open(py_file, encoding="utf-8") as f:
  Line 79: with open(py_file, "w", encoding="utf-8") as f:

FILE: agentic_core\L0_routing\utils\sovereign_convergence_util.py
--------------------------------------------------------------------------------
  Line 27: dest_path.mkdir(parents=True, exist_ok=True)
  Line 30: assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
  Line 31: shutil.move(str(item), str(dest_path / item.name))
  Line 33: assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
  Line 34: shutil.move(str(item), str(dest_path / item.name))
  Line 36: src_path.rmdir()
  Line 52: with open(py_file, encoding="utf-8") as f:
  Line 58: with open(py_file, "w", encoding="utf-8") as f:

FILE: agentic_core\L0_routing\utils\ssot_discovery_util.py
--------------------------------------------------------------------------------
  Line 96: with open(discovery_path, encoding="utf-8") as f:

FILE: agentic_core\L0_routing\utils\structural_fix_util.py
--------------------------------------------------------------------------------
  Line 34: with open(agent_logic_file, encoding="utf-8") as f:
  Line 39: with open(agent_logic_file, "w", encoding="utf-8") as f:
  Line 45: with open(mission_runner, encoding="utf-8") as f:
  Line 61: with open(mission_runner, "w", encoding="utf-8") as f:
  Line 68: target_dir.mkdir(parents=True, exist_ok=True)
  Line 70: assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
  Line 71: shutil.move(str(analysis_file), str(target_file))
  Line 77: assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
  Line 78: shutil.move(str(verify_file), str(target_file))
  Line 87: tests_dir.mkdir(parents=True, exist_ok=True)
  ... (2 more matches)

FILE: agentic_core\L0_routing\utils\trim_remaining_airlocks_util.py
--------------------------------------------------------------------------------
  Line 54: init_file.write_text(content, encoding="utf-8")

FILE: agentic_core\L1_cognition\validators\truth_keeper_validator.py
--------------------------------------------------------------------------------
  Line 52: with open(file_path, encoding="utf-8") as f:

FILE: agentic_core\L2_execution\config\hybrid_retriever_config.py
--------------------------------------------------------------------------------
  Line 210: cache_path.parent.mkdir(parents=True, exist_ok=True)

FILE: agentic_core\L2_execution\enforcement\dashboard_e2_e_pipeline.py
--------------------------------------------------------------------------------
  Line 67: data = json.load(open(self.discovery_path))
  Line 143: path.write_text(new_content, encoding="utf-8")
  Line 189: data = json.load(open(self.discovery_path))

FILE: agentic_core\L2_execution\enforcement\dashboard_e2_e_pipeline_enforcer.py
--------------------------------------------------------------------------------
  Line 67: data = json.load(open(self.discovery_path))
  Line 143: path.write_text(new_content, encoding="utf-8")
  Line 189: data = json.load(open(self.discovery_path))

FILE: agentic_core\L2_execution\enforcement\preventative_sandbox.py
--------------------------------------------------------------------------------
  Line 8: Filesystem  — builtins.open (write), pathlib, os.remove/rename

FILE: agentic_core\L2_execution\engines\secure_tools_impl.py
--------------------------------------------------------------------------------
  Line 65: target.parent.mkdir(parents=True, exist_ok=True)
  Line 66: with open(target, "w", encoding="utf-8") as f:
  Line 88: with open(target, encoding="utf-8") as f:

FILE: agentic_core\L2_execution\engines\validation_orchestrator.py
--------------------------------------------------------------------------------
  Line 142: with open(file_path, "rb") as f:
  Line 260: with open(file_path, encoding="utf-8") as f:

FILE: agentic_core\L2_execution\healers\classification_compliance_healer.py
--------------------------------------------------------------------------------
  Line 130: target.parent.mkdir(parents=True, exist_ok=True)
  Line 131: shutil.move(str(source), str(target))

FILE: agentic_core\L2_execution\healers\drift_detection_healer.py
--------------------------------------------------------------------------------
  Line 95: shutil.rmtree(target)
  Line 103: target.unlink()

FILE: agentic_core\L2_execution\healers\hierarchy_compliance_healer.py
--------------------------------------------------------------------------------
  Line 81: target.mkdir(parents=True, exist_ok=True)

FILE: agentic_core\L2_execution\reasoning\SubAtomicRegistryAgent.py
--------------------------------------------------------------------------------
  Line 380: source_lines = ast.get_source_segment(open(py_file).read(), node) or ""

FILE: agentic_core\L2_execution\reasoning\ToolsmithAgent.py
--------------------------------------------------------------------------------
  Line 118: implementation="    with open(file_path, 'r', encoding=encoding) as f:\n        return f.read()",
  Line 127: implementation="    try:\n        with open(file_path, 'w', encoding=encoding) as f:\n            f.
  Line 353: directory.mkdir(exist_ok=True)
  Line 355: with open(file_path, "w") as f:
  Line 359: with open(test_path, "w") as f:
  Line 362: with open(spec_path, "w") as f:
  Line 500: file_path.write_text(content, encoding="utf-8")

FILE: agentic_core\L2_execution\scripts\remediation_dispatcher.py
--------------------------------------------------------------------------------
  Line 526: write_artifacts_dir.mkdir(parents=True, exist_ok=True)
  Line 528: out_path.write_text(result.to_json(), encoding="utf-8")

FILE: agentic_core\L2_execution\tools\file_io_impl.py
--------------------------------------------------------------------------------
  Line 41: with open(file_path, "rb") as f:
  Line 78: with open(file_path, encoding="utf-8") as f:
  Line 120: os.makedirs(os.path.dirname(file_path), exist_ok=True)
  Line 121: with open(file_path, "w", encoding="utf-8") as f:

FILE: agentic_core\L2_execution\utils\analysis_ops_util.py
--------------------------------------------------------------------------------
  Line 28: with open(file_path, encoding="utf-8") as f:
  Line 105: with open(file_path, encoding="utf-8") as f:
  Line 169: with open(file_path, encoding="utf-8") as f:
  Line 193: with open(file_path, encoding="utf-8") as f:

FILE: agentic_core\L2_execution\utils\deterministic_cleaner_util.py
--------------------------------------------------------------------------------
  Line 117: with open(temp_file) as f:
  Line 120: os.unlink(temp_file)
  Line 198: path.parent.mkdir(parents=True, exist_ok=True)
  Line 199: with open(path, "w", encoding="utf-8") as f:

FILE: agentic_core\L3_orchestration\enforcement\mission_runner.py
--------------------------------------------------------------------------------
  Line 576: _wg.write_text(esc_dir / f"escalation_{int(time.time())}.md", report)

FILE: agentic_core\L3_orchestration\enforcement\mission_runner_enforcer.py
--------------------------------------------------------------------------------
  Line 576: _wg.write_text(esc_dir / f"escalation_{int(time.time())}.md", report)

FILE: agentic_core\L3_orchestration\engines\convergence_engine.py
--------------------------------------------------------------------------------
  Line 22: with open(file_path, "rb") as f:

FILE: agentic_core\L3_orchestration\engines\omni_context_engine.py
--------------------------------------------------------------------------------
  Line 50: with open(file_path, encoding="utf-8") as f:

FILE: agentic_core\L3_orchestration\engines\proactive_fission_scanner.py
--------------------------------------------------------------------------------
  Line 61: with open(file_path, encoding="utf-8") as f:

FILE: agentic_core\L3_orchestration\engines\sovereign_rag_orchestrator.py
--------------------------------------------------------------------------------
  Line 129: _wg.write_text(

FILE: agentic_core\L3_orchestration\reasoning\StateManagementAgent.py
--------------------------------------------------------------------------------
  Line 223: with open(self.manifest_path, encoding="utf-8") as f:
  Line 271: with open(self.manifest_path, encoding="utf-8") as f:
  Line 351: with open(file_path, encoding="utf-8") as f:
  Line 443: with open(file_path, "rb") as f:
  Line 511: with open(file_path, "rb") as f:
  Line 540: with open(file_path, "rb") as f:
  Line 747: with open(file_path_obj, "rb") as f:
  Line 938: with open(self.manifest_path) as f:

FILE: agentic_core\L3_orchestration\types\telepathy_interface_types.py
--------------------------------------------------------------------------------
  Line 141: _wg.write_text(self.instructions_path, done_content, encoding="utf-8")

FILE: agentic_core\L3_orchestration\types\workflow_loader_types.py
--------------------------------------------------------------------------------
  Line 108: with open(self.workflow_path, encoding="utf-8") as f:

FILE: agentic_core\L4_state\enforcement\mission_historian.py
--------------------------------------------------------------------------------
  Line 72: with open(self.log_path, newline="", encoding="utf-8") as f:

FILE: agentic_core\L4_state\enforcement\mission_historian_enforcer.py
--------------------------------------------------------------------------------
  Line 72: with open(self.log_path, newline="", encoding="utf-8") as f:

FILE: agentic_core\L4_state\memory\blob_storage_provider.py
--------------------------------------------------------------------------------
  Line 100: assert_no_persistent_write("L4", "shutil.mutate")  # G-12-1: mutation prohibition guard
  Line 122: with open(target_path, "rb") as f:

FILE: agentic_core\L4_state\memory\runtime_state_guard.py
--------------------------------------------------------------------------------
  Line 44: with open(self.state_path) as f:
  Line 50: with open(self.state_path) as f:

FILE: agentic_core\L4_state\reasoning\CheckpointManagerAgent.py
--------------------------------------------------------------------------------
  Line 468: with open(file_path, encoding="utf-8") as f:
  Line 560: with open(index_path, encoding="utf-8") as f:

FILE: agentic_core\L4_state\reasoning\GravityStateAgent.py
--------------------------------------------------------------------------------
  Line 201: with open(self.state_file, encoding="utf-8") as f:
  Line 374: with open(checkpoint_file, encoding="utf-8") as f:

FILE: agentic_core\L4_state\types\cycle_types.py
--------------------------------------------------------------------------------
  Line 317: with open(path) as f:

FILE: agentic_core\L4_state\types\validation_context_types.py
--------------------------------------------------------------------------------
  Line 101: with open(self.file_history_file) as f:
  Line 127: with open(file_path, "rb") as f:

FILE: agentic_core\L4_state\utils\complexity_analyzer_util.py
--------------------------------------------------------------------------------
  Line 87: with open(file_path, encoding="utf-8") as f:

FILE: agentic_core\L4_state\utils\experience_buffer_util.py
--------------------------------------------------------------------------------
  Line 62: _wg.write_text(self.path, "")  # Empty JSONL file
  Line 88: with self.path.open("r", encoding="utf-8") as f:
  Line 98: _wg.write_text(self.path, "".join(kept), encoding="utf-8")
  Line 107: with self.path.open("r", encoding="utf-8") as f:

FILE: agentic_core\L4_state\utils\get_file_hash_util.py
--------------------------------------------------------------------------------
  Line 15: with open(filepath, "rb") as f:

FILE: agentic_core\L5_safety\config\gravity_leak_config.py
--------------------------------------------------------------------------------
  Line 257: _wg.write_text(path, content, encoding="utf-8")

FILE: agentic_core\L5_safety\enforcement\agent_info.py
--------------------------------------------------------------------------------
  Line 504: _wg.write_text(report_path, json.dumps(json_data, indent=2))

FILE: agentic_core\L5_safety\enforcement\agent_info_enforcer.py
--------------------------------------------------------------------------------
  Line 504: _wg.write_text(report_path, json.dumps(json_data, indent=2))

FILE: agentic_core\L5_safety\enforcement\airlock_trimmer.py
--------------------------------------------------------------------------------
  Line 47: _wg.write_text(init_file, content, encoding="utf-8")

FILE: agentic_core\L5_safety\enforcement\airlock_trimmer_enforcer.py
--------------------------------------------------------------------------------
  Line 47: _wg.write_text(init_file, content, encoding="utf-8")

FILE: agentic_core\L5_safety\enforcement\archival_gatekeeper.py
--------------------------------------------------------------------------------
  Line 440: # because shutil.move behavior varies (might nest directories)
  Line 684: with open(self.audit_log_path, encoding="utf-8") as f:

FILE: agentic_core\L5_safety\enforcement\archival_gatekeeper_gate.py
--------------------------------------------------------------------------------
  Line 440: # because shutil.move behavior varies (might nest directories)
  Line 684: with open(self.audit_log_path, encoding="utf-8") as f:

FILE: agentic_core\L5_safety\enforcement\circuit_breaker.py
--------------------------------------------------------------------------------
  Line 117: """Check if circuit is open (rejecting calls)."""
  Line 122: """Check if circuit is half-open (testing recovery)."""
  Line 133: CircuitBreakerOpenError if circuit is open (optional, for detailed info)

FILE: agentic_core\L5_safety\enforcement\circuit_breaker_gate.py
--------------------------------------------------------------------------------
  Line 117: """Check if circuit is open (rejecting calls)."""
  Line 122: """Check if circuit is half-open (testing recovery)."""
  Line 133: CircuitBreakerOpenError if circuit is open (optional, for detailed info)

FILE: agentic_core\L5_safety\enforcement\circular_import_fixer.py
--------------------------------------------------------------------------------
  Line 83: with open(file_path, encoding="utf-8") as f:

FILE: agentic_core\L5_safety\enforcement\circular_import_fixer_enforcer.py
--------------------------------------------------------------------------------
  Line 83: with open(file_path, encoding="utf-8") as f:

FILE: agentic_core\L5_safety\enforcement\data.py
--------------------------------------------------------------------------------
  Line 36: data = json.load(open(discovery_path))

FILE: agentic_core\L5_safety\enforcement\data_enforcer.py
--------------------------------------------------------------------------------
  Line 36: data = json.load(open(discovery_path))

FILE: agentic_core\L5_safety\enforcement\dependency_graph.py
--------------------------------------------------------------------------------
  Line 32: with open(file_path, encoding="utf-8") as f:

FILE: agentic_core\L5_safety\enforcement\dependency_graph_enforcer.py
--------------------------------------------------------------------------------
  Line 32: with open(file_path, encoding="utf-8") as f:

FILE: agentic_core\L5_safety\enforcement\fast_dashboard_e2_e_pipeline.py
--------------------------------------------------------------------------------
  Line 65: data = json.load(open(self.discovery_path))
  Line 118: _wg.write_text(path, new_content, encoding="utf-8")
  Line 137: data = json.load(open(self.discovery_path))
  Line 195: _wg.write_text(path, content, encoding="utf-8")
  Line 214: data = json.load(open(self.discovery_path))

FILE: agentic_core\L5_safety\enforcement\fast_dashboard_e2_e_pipeline_enforcer.py
--------------------------------------------------------------------------------
  Line 65: data = json.load(open(self.discovery_path))
  Line 118: _wg.write_text(path, new_content, encoding="utf-8")
  Line 137: data = json.load(open(self.discovery_path))
  Line 195: _wg.write_text(path, content, encoding="utf-8")
  Line 214: data = json.load(open(self.discovery_path))

FILE: agentic_core\L5_safety\enforcement\final_airlock_trimmer.py
--------------------------------------------------------------------------------
  Line 31: _wg.write_text(file_path, "\n".join(cleaned) + "\n", encoding="utf-8")

FILE: agentic_core\L5_safety\enforcement\final_airlock_trimmer_enforcer.py
--------------------------------------------------------------------------------
  Line 31: _wg.write_text(file_path, "\n".join(cleaned) + "\n", encoding="utf-8")

FILE: agentic_core\L5_safety\enforcement\hardcoded_path_refactorer.py
--------------------------------------------------------------------------------
  Line 194: _wg.write_text(file_path, content, encoding="utf-8")

FILE: agentic_core\L5_safety\enforcement\hardcoded_path_refactorer_enforcer.py
--------------------------------------------------------------------------------
  Line 194: _wg.write_text(file_path, content, encoding="utf-8")

FILE: agentic_core\L5_safety\enforcement\healing_invocation_audit.py
--------------------------------------------------------------------------------
  Line 97: with open(file_path) as f:
  Line 112: with open(file_path) as f:

FILE: agentic_core\L5_safety\enforcement\healing_invocation_audit_enforcer.py
--------------------------------------------------------------------------------
  Line 97: with open(file_path) as f:
  Line 112: with open(file_path) as f:

FILE: agentic_core\L5_safety\enforcement\import_surgeon.py
--------------------------------------------------------------------------------
  Line 59: with open(file_path, encoding="utf-8") as f:
  Line 187: with open(file_path, encoding="utf-8") as f:

FILE: agentic_core\L5_safety\enforcement\import_surgeon_enforcer.py
--------------------------------------------------------------------------------
  Line 59: with open(file_path, encoding="utf-8") as f:
  Line 187: with open(file_path, encoding="utf-8") as f:

FILE: agentic_core\L5_safety\enforcement\module_collision_guard.py
--------------------------------------------------------------------------------
  Line 214: with open(baseline_path) as f:

FILE: agentic_core\L5_safety\enforcement\module_collision_guardrail.py
--------------------------------------------------------------------------------
  Line 214: with open(baseline_path) as f:

FILE: agentic_core\L5_safety\enforcement\mutation_prohibition.py
--------------------------------------------------------------------------------
  Line 7: os.rename/remove/unlink, shutil.move/rmtree, and open(..., 'w'/'a').
  Line 52: op: Operation name (e.g. "write_text", "json.dump", "shutil.move").
  Line 93: _wg.write_text(Path(filepath), content, encoding=encoding)
  Line 105: _wg.write_bytes(Path(filepath), data)
  Line 130: """Guarded shutil.move replacement."""
  Line 131: assert_no_persistent_write(layer, "shutil.move", str(dst), trace_id)
  Line 141: """Guarded shutil.rmtree replacement."""
  Line 142: assert_no_persistent_write(layer, "shutil.rmtree", str(target), trace_id)
  Line 177: """Guarded open(..., 'w'/'a') replacement. Returns file handle."""
  Line 178: assert_no_persistent_write(layer, f"open({mode})", str(filepath), trace_id)
  ... (1 more matches)

FILE: agentic_core\L5_safety\enforcement\mutation_prohibition_enforcer.py
--------------------------------------------------------------------------------
  Line 7: os.rename/remove/unlink, shutil.move/rmtree, and open(..., 'w'/'a').
  Line 52: op: Operation name (e.g. "write_text", "json.dump", "shutil.move").
  Line 93: _wg.write_text(Path(filepath), content, encoding=encoding)
  Line 105: _wg.write_bytes(Path(filepath), data)
  Line 130: """Guarded shutil.move replacement."""
  Line 131: assert_no_persistent_write(layer, "shutil.move", str(dst), trace_id)
  Line 141: """Guarded shutil.rmtree replacement."""
  Line 142: assert_no_persistent_write(layer, "shutil.rmtree", str(target), trace_id)
  Line 177: """Guarded open(..., 'w'/'a') replacement. Returns file handle."""
  Line 178: assert_no_persistent_write(layer, f"open({mode})", str(filepath), trace_id)
  ... (1 more matches)

FILE: agentic_core\L5_safety\enforcement\namespace_medic.py
--------------------------------------------------------------------------------
  Line 93: with open(file_path, encoding="utf-8", errors="replace") as f:
  Line 153: with open(file_path, encoding="utf-8", errors="replace") as f:

FILE: agentic_core\L5_safety\enforcement\namespace_medic_enforcer.py
--------------------------------------------------------------------------------
  Line 93: with open(file_path, encoding="utf-8", errors="replace") as f:
  Line 153: with open(file_path, encoding="utf-8", errors="replace") as f:

FILE: agentic_core\L5_safety\enforcement\pytest_config_guard.py
--------------------------------------------------------------------------------
  Line 263: _wg.write_text(
  Line 271: _wg.write_text(
  Line 293: _wg.write_text(
  Line 301: _wg.write_text(

FILE: agentic_core\L5_safety\enforcement\pytest_config_guardrail.py
--------------------------------------------------------------------------------
  Line 263: _wg.write_text(
  Line 271: _wg.write_text(
  Line 293: _wg.write_text(
  Line 301: _wg.write_text(

FILE: agentic_core\L5_safety\enforcement\registry_verification.py
--------------------------------------------------------------------------------
  Line 200: with open(self.discovery_path, encoding="utf-8") as f:

FILE: agentic_core\L5_safety\enforcement\registry_verification_enforcer.py
--------------------------------------------------------------------------------
  Line 200: with open(self.discovery_path, encoding="utf-8") as f:

FILE: agentic_core\L5_safety\enforcement\sovereign_healing_engine.py
--------------------------------------------------------------------------------
  Line 162: success = await _wg.write_text(self.fs_client, file_path, new_content)
  Line 199: return await _wg.write_text(self.fs_client, file_path, content)
  Line 228: return await _wg.write_text(self.fs_client, file_path, content)
  Line 257: "open(",
  Line 258: f"# TODO: Use {fix['new_client']}.read_text() or write_text()\n# open(",
  Line 264: return await _wg.write_text(self.fs_client, file_path, content)

FILE: agentic_core\L5_safety\enforcement\sovereign_healing_engine_enforcer.py
--------------------------------------------------------------------------------
  Line 162: success = await _wg.write_text(self.fs_client, file_path, new_content)
  Line 199: return await _wg.write_text(self.fs_client, file_path, content)
  Line 228: return await _wg.write_text(self.fs_client, file_path, content)
  Line 257: "open(",
  Line 258: f"# TODO: Use {fix['new_client']}.read_text() or write_text()\n# open(",
  Line 264: return await _wg.write_text(self.fs_client, file_path, content)

FILE: agentic_core\L5_safety\enforcement\ssot_import_enforcer.py
--------------------------------------------------------------------------------
  Line 73: _wg.write_text(file_path, new_content, encoding="utf-8")

FILE: agentic_core\L5_safety\enforcement\system.py
--------------------------------------------------------------------------------
  Line 93: with open(self.discovery_path) as f:
  Line 136: with open(file_path, encoding="utf-8") as f:

FILE: agentic_core\L5_safety\enforcement\system_enforcer.py
--------------------------------------------------------------------------------
  Line 93: with open(self.discovery_path) as f:
  Line 136: with open(file_path, encoding="utf-8") as f:

FILE: agentic_core\L5_safety\enforcement\verification_gate.py
--------------------------------------------------------------------------------
  Line 69: with open(file_path, encoding="utf-8") as f:
  Line 196: with open(context.file_path, encoding="utf-8") as f:

FILE: agentic_core\L5_safety\governance\lazy_seam_classifier.py
--------------------------------------------------------------------------------
  Line 32: with open(self.allowlist_path, encoding="utf-8") as f:

FILE: agentic_core\L5_safety\governance\lazy_seam_enforcer.py
--------------------------------------------------------------------------------
  Line 197: with open(self.allowlist_path, encoding="utf-8") as f:
  Line 222: with open(file_path, encoding="utf-8") as f:

FILE: agentic_core\L5_safety\reasoning\ArchitectureGovernorAgent.py
--------------------------------------------------------------------------------
  Line 1201: with open(baseline_path) as f:

FILE: agentic_core\L5_safety\reasoning\AutonomousThreatEvolutionAgent.py
--------------------------------------------------------------------------------
  Line 85: with open(self.log_path) as f:

FILE: agentic_core\L5_safety\reasoning\AutonomyGuardianAgent.py
--------------------------------------------------------------------------------
  Line 248: _wg.write_text(report_path, md, encoding="utf-8")
  Line 322: with open(self.discovery_json_path, encoding="utf-8") as f:
  Line 351: with open(agent_path, encoding="utf-8") as f:

FILE: agentic_core\L5_safety\reasoning\BenchmarkingAgent.py
--------------------------------------------------------------------------------
  Line 411: with open(alert_file) as f:

FILE: agentic_core\L5_safety\reasoning\CodeDeduplicationAgent.py
--------------------------------------------------------------------------------
  Line 350: _wg.write_text(candidate, header + textwrap.dedent(code), encoding="utf-8")
  Line 386: _wg.write_text(file_path, "".join(new_lines), encoding="utf-8")
  Line 998: _wg.write_text(file_path, "".join(new_lines), encoding="utf-8")

FILE: agentic_core\L5_safety\reasoning\CodeEnforcerAgent.py
--------------------------------------------------------------------------------
  Line 426: _wg.write_text(

FILE: agentic_core\L5_safety\reasoning\CodeValidatorAgent.py
--------------------------------------------------------------------------------
  Line 146: with open(file_path, encoding="utf-8") as f:
  Line 177: with open(file_path, encoding="utf-8") as f:
  Line 227: with open(file_path, encoding="utf-8") as f:
  Line 278: with open(file_path, encoding="utf-8") as f:

FILE: agentic_core\L5_safety\reasoning\ConstitutionalReviewerAgent.py
--------------------------------------------------------------------------------
  Line 94: f"ConstitutionalReviewer failed validation: {error}. Failing open (passing draft).",

FILE: agentic_core\L5_safety\reasoning\DependencyPruningAgent.py
--------------------------------------------------------------------------------
  Line 124: _wg.write_text(self.requirements_path, "\n".join(new_lines) + "\n", encoding="utf-8")

FILE: agentic_core\L5_safety\reasoning\DocstringComplianceAgent.py
--------------------------------------------------------------------------------
  Line 118: _wg.write_text(file_path, new_content, encoding="utf-8")

FILE: agentic_core\L5_safety\reasoning\DocumentationAgent.py
--------------------------------------------------------------------------------
  Line 134: with open(fp, encoding="utf-8") as f:

FILE: agentic_core\L5_safety\reasoning\DynamicSealAgent.py
--------------------------------------------------------------------------------
  Line 252: _wg.write_text(file_path, content, encoding="utf-8")

FILE: agentic_core\L5_safety\reasoning\FileClassificationAgent.py
--------------------------------------------------------------------------------
  Line 1120: "open(",
  Line 1402: "open(",
  Line 1405: ".write_text(",
  Line 1406: ".write_bytes(",
  Line 1409: "shutil.move(",
  Line 1410: "shutil.copy(",
  Line 1411: "shutil.rmtree(",
  Line 1412: "os.remove(",
  Line 1413: "os.unlink(",
  Line 1414: ".unlink(",
  ... (11 more matches)

FILE: agentic_core\L5_safety\reasoning\FilesystemSSOTReconcilerAgent.py
--------------------------------------------------------------------------------
  Line 436: with open(discovery_path, encoding="utf-8") as f:

FILE: agentic_core\L5_safety\reasoning\GovernanceAgent.py
--------------------------------------------------------------------------------
  Line 175: with open(file_path, encoding="utf-8") as f:
  Line 603: with open(file_path, encoding="utf-8") as f:
  Line 682: with open(file_path, encoding="utf-8") as f:
  Line 713: with open(file_path, encoding="utf-8") as f:

FILE: agentic_core\L5_safety\reasoning\HierarchyAgent.py
--------------------------------------------------------------------------------
  Line 1169: _wg.write_text(gitignore_path, new_content, encoding="utf-8")

FILE: agentic_core\L5_safety\reasoning\IntegrityGateExecutorAgent.py
--------------------------------------------------------------------------------
  Line 583: with open(json_file, encoding="utf-8") as f:

FILE: agentic_core\L5_safety\reasoning\L5SafetyExerciserAgent.py
--------------------------------------------------------------------------------
  Line 164: _wg.write_text(temp_file, "import sys\nprint('gravity test')\n")

FILE: agentic_core\L5_safety\reasoning\LocationHealerAgent.py
--------------------------------------------------------------------------------
  Line 571: _wg.write_text(file_path, new_content, encoding="utf-8")
  Line 710: _wg.write_text(py_file, new_content, encoding="utf-8")
  Line 1178: _wg.write_text(blueprint_path, new_content, encoding="utf-8")
  Line 1426: _wg.write_text(blueprint_path, new_content, encoding="utf-8")
  Line 1693: _wg.write_text(path, content + todo, encoding="utf-8")
  Line 2120: _wg.write_text(path, new_content, encoding="utf-8")
  Line 2158: with open(path) as f:

FILE: agentic_core\L5_safety\reasoning\PreCommitSovereignAgent.py
--------------------------------------------------------------------------------
  Line 318: _wg.write_text(hook_path, hook_content, encoding="utf-8")

FILE: agentic_core\L5_safety\reasoning\RedSentinelAgent.py
--------------------------------------------------------------------------------
  Line 208: with open(self.audit_path) as f:
  Line 242: with open(file_path, encoding="utf-8") as f:

FILE: agentic_core\L5_safety\reasoning\SafetyInspectorAgent.py
--------------------------------------------------------------------------------
  Line 237: with open(file_path, encoding="utf-8") as f:
  Line 310: with open(file_path, encoding="utf-8") as f:

FILE: agentic_core\L5_safety\reasoning\SelfUpdatingSafetyEngineAgent.py
--------------------------------------------------------------------------------
  Line 222: with open(self.rules_storage_path, encoding="utf-8") as f:

FILE: agentic_core\L5_safety\reasoning\SovereignActionPlaneAgent.py
--------------------------------------------------------------------------------
  Line 409: with open(tool_path) as f:
  Line 467: with open(file_path) as f:

FILE: agentic_core\L5_safety\reasoning\StructuralEngineerAgent.py
--------------------------------------------------------------------------------
  Line 90: with open(resolved_path, encoding="utf-8") as f:
  Line 130: with open(resolved_path, encoding="utf-8") as f:
  Line 158: with open(resolved_path, encoding="utf-8") as f:
  Line 215: with open(resolved_path, encoding="utf-8") as f:

FILE: agentic_core\L5_safety\reasoning\StructureEnforcerAgent.py
--------------------------------------------------------------------------------
  Line 393: _wg.write_text(file_path, new_content, encoding="utf-8")

FILE: agentic_core\L5_safety\reasoning\StructureHealerAgent.py
--------------------------------------------------------------------------------
  Line 217: _wg.write_text(file_path, new_content, encoding="utf-8")
  Line 271: _wg.write_text(file_path, "\n".join(new_lines), encoding="utf-8")

FILE: agentic_core\L5_safety\reasoning\SystemArchitectAgent.py
--------------------------------------------------------------------------------
  Line 97: with open(file_path, encoding="utf-8") as f:
  Line 302: with open(resolved_path, encoding="utf-8") as f:
  Line 355: with open(resolved_path, encoding="utf-8") as f:

FILE: agentic_core\L5_safety\reasoning\TestGeneratorAgent.py
--------------------------------------------------------------------------------
  Line 100: _wg.write_text(test_path, test_content, encoding="utf-8")

FILE: agentic_core\L5_safety\reasoning\TypeMechanicAgent.py
--------------------------------------------------------------------------------
  Line 75: with open(fp, encoding="utf-8") as f:  # Depth 2
  Line 193: with open(fp, encoding="utf-8") as f:

FILE: agentic_core\L5_safety\types\file_health_score_types.py
--------------------------------------------------------------------------------
  Line 139: with open(file_path, "rb") as f:

FILE: agentic_core\L5_safety\types\heal_llm_seam.py
--------------------------------------------------------------------------------
  Line 298: _wg.write_bytes(filepath, content_bytes)

FILE: agentic_core\L5_safety\types\learning_types.py
--------------------------------------------------------------------------------
  Line 131: with open(self.pattern_storage_path, encoding="utf-8") as f:

FILE: agentic_core\L5_safety\types\safety_types.py
--------------------------------------------------------------------------------
  Line 222: with open(self.rules_storage_path, encoding="utf-8") as f:

FILE: agentic_core\L5_safety\utils\cognitive_batch_processor_util.py
--------------------------------------------------------------------------------
  Line 103: _wg.write_text(self.checkpoint_file, json.dumps(self.results, indent=2), encoding="utf-8")

FILE: agentic_core\L5_safety\utils\extract_pattern_util.py
--------------------------------------------------------------------------------
  Line 87: with open(source_file, encoding="utf-8") as f:
  Line 118: with open(source_file, encoding="utf-8") as f:
  Line 152: with open(SOURCE_FILE, encoding="utf-8") as f:

FILE: agentic_core\L5_safety\utils\fix_inherited_invocation_util.py
--------------------------------------------------------------------------------
  Line 33: with open(DISCOVERY_JSON, encoding="utf-8") as f:
  Line 120: _wg.write_text(file_path, new_source, encoding="utf-8")

FILE: agentic_core\L5_safety\utils\force_app_depth_util.py
--------------------------------------------------------------------------------
  Line 70: _wg.write_text(app_p1 / "__init__.py", '"""App Core Implementation"""\n')

FILE: agentic_core\L5_safety\utils\set_complexity_health_100_util.py
--------------------------------------------------------------------------------
  Line 64: _wg.write_text(DASHBOARD_PATH, updated_content, encoding="utf-8")

FILE: agentic_core\L5_safety\utils\tiered_batch_util.py
--------------------------------------------------------------------------------
  Line 95: _wg.write_text(self.checkpoint_file, json.dumps(self.results, indent=2), encoding="utf-8")

FILE: agentic_core\L5_safety\utils\unified_cst_healer_util.py
--------------------------------------------------------------------------------
  Line 371: _wg.write_text(context.file_path, modified_code, encoding="utf-8")

FILE: agentic_core\L5_safety\utils\validate_dashboard_data_sourcing_util.py
--------------------------------------------------------------------------------
  Line 19: with open(source_file, encoding="utf-8") as f:

FILE: agentic_core\L5_safety\validators\dependencygraph_validator.py
--------------------------------------------------------------------------------
  Line 202: with open(file_path, encoding="utf-8") as f:
  Line 327: with open(self.memory_file) as f:
  Line 348: with open(file_path, encoding="utf-8") as f:
  Line 448: with open(file_path, encoding="utf-8") as f:

FILE: agentic_core\L5_safety\validators\structure_drift_validator.py
--------------------------------------------------------------------------------
  Line 89: with open(manifest_path, encoding="utf-8") as f:

FILE: agentic_core\L5_safety\config\structure_blueprint\_simulate_verify.py
--------------------------------------------------------------------------------
  Line 32: with open(path, "rb") as f:
  Line 128: with open(baseline_path, encoding="utf-8") as bf:
  Line 159: with open(baseline_path, encoding="utf-8") as bf:
  Line 177: with open(baseline_path, encoding="utf-8") as bf:
  Line 211: with open(wf_path, encoding="utf-8") as wf:

FILE: agentic_core\L5_safety\config\structure_blueprint\_verify.py
--------------------------------------------------------------------------------
  Line 202: with open(bp, encoding="utf-8") as bf:
  Line 225: with open(hp, encoding="utf-8") as hf:
  Line 254: with open(fpath, encoding="utf-8") as f:
  Line 463: with open(fpath, encoding="utf-8", errors="replace") as f:
  Line 539: with open(baseline_path, encoding="utf-8") as bf:
  Line 652: with open(shim_path, encoding="utf-8") as f:
  Line 722: with open(constants_path, encoding="utf-8") as f:
  Line 801: with open(hash_path, encoding="utf-8") as hf:
  Line 839: with open(fpath, encoding="utf-8", errors="replace") as f:

FILE: agentic_core\L5_safety\config\structure_blueprint\enforcement\blueprint_hash.py
--------------------------------------------------------------------------------
  Line 61: _wg.write_text(hash_path, current_hash + "\n", encoding="utf-8")

FILE: agentic_core\L5_safety\enforcement\governance\agent_heal_audit.py
--------------------------------------------------------------------------------
  Line 78: with open(file_path, encoding="utf-8") as f:

FILE: agentic_core\L5_safety\enforcement\governance\artifacts_guard.py
--------------------------------------------------------------------------------
  Line 38: with open(file_path, encoding="utf-8", errors="ignore") as f:

FILE: agentic_core\L5_safety\enforcement\governance\docs_structure_guard.py
--------------------------------------------------------------------------------
  Line 28: with open(file_path, encoding="utf-8") as f:

FILE: agentic_core\L5_safety\enforcement\governance\logs_guard.py
--------------------------------------------------------------------------------
  Line 83: with open(file_path, encoding="utf-8", errors="ignore") as f:

FILE: agentic_core\L5_safety\enforcement\security\credential_guard.py
--------------------------------------------------------------------------------
  Line 78: with open(file_path, encoding="utf-8") as f:
  Line 92: with open(file_path, encoding="utf-8") as f:

FILE: agentic_core\L5_safety\utils\evidence\phase10_apps_taxonomy_guard_evidence.py
--------------------------------------------------------------------------------
  Line 54: evidence_file.parent.mkdir(parents=True, exist_ok=True)
  Line 117: filesystem_write_tokens = ["write_text", "write_bytes", "open("]
  Line 150: evidence_file.write_text(evidence_content, encoding="utf-8")

FILE: agentic_core\L5_safety\utils\evidence\phase11_l1_telemetry_emitter_evidence.py
--------------------------------------------------------------------------------
  Line 54: evidence_file.parent.mkdir(parents=True, exist_ok=True)
  Line 120: forbidden_io_tokens = ["open(", "Path(", "write_text", "write_bytes"]
  Line 161: evidence_file.write_text(evidence_content, encoding="utf-8")

FILE: agentic_core\L5_safety\utils\evidence\phase2_assembly_stage_evidence.py
--------------------------------------------------------------------------------
  Line 39: evidence_file.parent.mkdir(parents=True, exist_ok=True)
  Line 126: evidence_file.write_text(evidence_content, encoding="utf-8")

FILE: agentic_core\L5_safety\utils\evidence\phase3_path_router_evidence.py
--------------------------------------------------------------------------------
  Line 54: evidence_file.parent.mkdir(parents=True, exist_ok=True)
  Line 133: evidence_file.write_text(evidence_content, encoding="utf-8")

FILE: agentic_core\L5_safety\utils\evidence\phase4_l5_d0_confcalib_evidence.py
--------------------------------------------------------------------------------
  Line 54: evidence_file.parent.mkdir(parents=True, exist_ok=True)
  Line 176: evidence_file.write_text(evidence_content, encoding="utf-8")

FILE: agentic_core\L5_safety\utils\evidence\phase5_l2_cid_reentry_evidence.py
--------------------------------------------------------------------------------
  Line 54: evidence_file.parent.mkdir(parents=True, exist_ok=True)
  Line 129: evidence_file.write_text(evidence_content, encoding="utf-8")

FILE: agentic_core\L5_safety\utils\evidence\phase6_meta_learning_bus_evidence.py
--------------------------------------------------------------------------------
  Line 54: evidence_file.parent.mkdir(parents=True, exist_ok=True)
  Line 117: forbidden_l4_tokens = ["agentic_core.L4_state", "open(", "Path(", "write_text", "write_bytes"]
  Line 150: evidence_file.write_text(evidence_content, encoding="utf-8")

FILE: agentic_core\L5_safety\utils\evidence\phase7_l6_vigilance_dispatcher_evidence.py
--------------------------------------------------------------------------------
  Line 54: evidence_file.parent.mkdir(parents=True, exist_ok=True)
  Line 156: evidence_file.write_text(evidence_content, encoding="utf-8")

FILE: agentic_core\L5_safety\utils\evidence\phase8_execution_orchestrator_evidence.py
--------------------------------------------------------------------------------
  Line 54: evidence_file.parent.mkdir(parents=True, exist_ok=True)
  Line 117: forbidden_l4_tokens = ["agentic_core.L4_state", "open(", "Path(", "write_text", "write_bytes"]
  Line 150: evidence_file.write_text(evidence_content, encoding="utf-8")

FILE: agentic_core\L5_safety\utils\evidence\phase9_outcome_logger_evidence.py
--------------------------------------------------------------------------------
  Line 54: evidence_file.parent.mkdir(parents=True, exist_ok=True)
  Line 121: disk_io_tokens = ["open(", "Path(", "write_text", "write_bytes"]
  Line 163: evidence_file.write_text(evidence_content, encoding="utf-8")

FILE: agentic_core\L6_observability\dashboards\dashboard_generator.py
--------------------------------------------------------------------------------
  Line 119: with open(self.discovery_path, encoding="utf-8") as f:
  Line 831: _wg.write_text(self.dashboard_path, new_html, encoding="utf-8")

FILE: agentic_core\L6_observability\enforcement\reasoning_streamer.py
--------------------------------------------------------------------------------
  Line 29: sys.stdout = open(sys.stdout.fileno(), mode="w", encoding="utf-8", buffering=1)

FILE: agentic_core\L6_observability\enforcement\reasoning_streamer_enforcer.py
--------------------------------------------------------------------------------
  Line 29: sys.stdout = open(sys.stdout.fileno(), mode="w", encoding="utf-8", buffering=1)

FILE: agentic_core\L6_observability\golden_evaluation\injection_regression_suite.py
--------------------------------------------------------------------------------
  Line 58: with open(injection_file, encoding="utf-8") as f:

FILE: agentic_core\L6_observability\golden_evaluation\resume_quality_evaluator.py
--------------------------------------------------------------------------------
  Line 56: with open(resume_file, encoding="utf-8") as f:

FILE: agentic_core\L6_observability\golden_evaluation\tool_use_ground_truth_evaluator.py
--------------------------------------------------------------------------------
  Line 59: with open(tool_file, encoding="utf-8") as f:

FILE: agentic_core\L6_observability\utils\fix_testing_observability_util.py
--------------------------------------------------------------------------------
  Line 39: with open(DISCOVERY_JSON, encoding="utf-8") as f:
  Line 98: _wg.write_text(file_path, source, encoding="utf-8")
  Line 152: _wg.write_text(file_path, new_source, encoding="utf-8")

FILE: agentic_core\L6_observability\utils\integrity_report_generator_util.py
--------------------------------------------------------------------------------
  Line 387: _wg.write_text(output_path, report_content, encoding="utf-8")

FILE: agentic_core\L6_observability\dashboards\core\StaticFileApp.py
--------------------------------------------------------------------------------
  Line 51: with open(filepath, "rb") as f:

FILE: agentic_core\prompt_governance\core\prompt_assembler.py
--------------------------------------------------------------------------------
  Line 212: template_dir.mkdir(parents=True, exist_ok=True)
  Line 219: with open(file_path, encoding="utf-8") as f:
  Line 628: template_dir.mkdir(parents=True, exist_ok=True)
  Line 631: with open(file_path, "w", encoding="utf-8") as f:

FILE: agentic_core\prompt_governance\core\sovereign_prompt_renderer.py
--------------------------------------------------------------------------------
  Line 68: os.makedirs(self.template_root, exist_ok=True)

FILE: agentic_core\prompt_governance\scripts\audit_registry_linkages.py
--------------------------------------------------------------------------------
  Line 17: with open(registry_path, encoding="utf-8") as f:
  Line 27: with open(template_path, encoding="utf-8") as f:

FILE: agentic_core\prompt_governance\scripts\detect_template_drift.py
--------------------------------------------------------------------------------
  Line 19: with open(registry_path, encoding="utf-8") as f:

FILE: agentic_core\prompt_governance\scripts\harden_templates.py
--------------------------------------------------------------------------------
  Line 99: with open(file_path, encoding="utf-8") as f:
  Line 124: with open(file_path, "w", encoding="utf-8") as f:

FILE: agentic_core\prompt_governance\scripts\import_violation_visitor.py
--------------------------------------------------------------------------------
  Line 72: with open(file_path, encoding="utf-8") as f:

FILE: agentic_core\prompt_governance\scripts\synchronize_registry_hashes.py
--------------------------------------------------------------------------------
  Line 19: with open(registry_path, encoding="utf-8") as f:
  Line 30: with open(registry_path, "w", encoding="utf-8") as f:
  Line 114: shutil.copy2(registry_path, backup_path)

FILE: agentic_core\prompt_governance\scripts\template_render_visitor.py
--------------------------------------------------------------------------------
  Line 19: with open(full_path, encoding="utf-8") as f:
  Line 148: with open(py_file, encoding="utf-8") as f:

FILE: agentic_core\prompt_governance\validation\validate_assembly.py
--------------------------------------------------------------------------------
  Line 45: with open(MANIFEST_PATH, encoding="utf-8") as f:

FILE: agentic_core\runtime\config\model_provider_config.py
--------------------------------------------------------------------------------
  Line 48: d.mkdir(parents=True, exist_ok=True)

FILE: agentic_core\runtime\config\prompt_injection_loader_config.py
--------------------------------------------------------------------------------
  Line 83: injection_dir.mkdir(parents=True, exist_ok=True)
  Line 92: with open(file_path, encoding="utf-8") as f:
  Line 196: with open(file_path, "w", encoding="utf-8") as f:

FILE: agentic_core\runtime\utils\discovery_parser_util.py
--------------------------------------------------------------------------------
  Line 42: with open(discovery_path, encoding="utf-8") as f:

FILE: agentic_core\runtime\utils\discovery_util.py
--------------------------------------------------------------------------------
  Line 86: with open(file_path, encoding="utf-8") as f:

================================================================================
ANALYSIS
================================================================================
Direct write primitives found outside write_gateway.
Most are in legitimate contexts (logging, temp files, state persistence).
Protected-root enforcement occurs at write_gateway layer.
Any code bypassing write_gateway bypasses enforcement (design risk).
```

### Tool-Accessible Write API Inventory
```
================================================================================
TOOL-ACCESSIBLE WRITE API INVENTORY
================================================================================

FINDING: No formal PTC/tool registry infrastructure exists.

ANALYSIS:
- No ToolSpec, call_tool, or programmatic tool calling framework detected
- No tool registry that exposes write APIs to external callers
- write_gateway.py is the canonical write API layer
- All write_gateway public functions accept allow_override parameter
- All write_gateway public functions call enforce_protected_root

CONCLUSION:
If a PTC/tool framework is added in the future, it MUST:
1. Route all filesystem writes through write_gateway
2. NOT expose direct filesystem write primitives as tool capabilities
3. Respect the allow_override=False default (protected-root enforcement)

Current state: No tool-accessible write APIs exist (vacuously compliant).
```

## Wave 8.2 — PTC Write Contract Guard

**Commit hash:** b8fc4394c

**Files changed:**
- tests/unit_min_deps/test_ptc_write_contract.py (new)

## Wave 8.3 — Verification

### Unit Tests (PTC Contract + SSOT Fence)
```
[1m============================= test session starts =============================[0m
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 34 items

tests/unit_min_deps/test_ptc_write_contract.py::TestPTCWriteContract::test_tool_registry_exists_and_must_route_via_write_gateway [32mPASSED[0m[32m [  2%][0m
tests/unit_min_deps/test_ptc_write_contract.py::TestPTCWriteContract::test_write_gateway_is_canonical_write_layer [32mPASSED[0m[32m [  5%][0m
tests/unit_min_deps/test_ptc_write_contract.py::TestPTCWriteContract::test_write_gateway_functions_accept_allow_override [32mPASSED[0m[32m [  8%][0m
tests/unit_min_deps/test_ptc_write_contract.py::TestPTCWriteContract::test_future_tool_contract_enforcement_ready [32mPASSED[0m[32m [ 11%][0m
tests/unit_min_deps/test_ptc_write_contract.py::TestPTCWriteContract::test_l2_execution_tools_do_not_expose_raw_write_primitives [32mPASSED[0m[32m [ 14%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_enforce_protected_root_blocks_agentic_core [32mPASSED[0m[32m [ 17%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_enforce_protected_root_allows_outside [32mPASSED[0m[32m [ 20%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_enforce_protected_root_override_allows [32mPASSED[0m[32m [ 23%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_enforce_protected_root_blocks_tests [32mPASSED[0m[32m [ 26%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_enforce_protected_root_blocks_github [32mPASSED[0m[32m [ 29%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_exception_includes_matched_root_agentic_core [32mPASSED[0m[32m [ 32%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_exception_includes_matched_root_tests [32mPASSED[0m[32m [ 35%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_exception_includes_matched_root_github [32mPASSED[0m[32m [ 38%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestWriteGatewayIntegration::test_write_gateway_blocks_protected_root [32mPASSED[0m[32m [ 41%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestWriteGatewayIntegration::test_write_gateway_allows_outside_protected_root [32mPASSED[0m[32m [ 44%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestWriteGatewayIntegration::test_write_bytes_blocks_protected_root [32mPASSED[0m[32m [ 47%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestBlockEventEmission::test_block_emits_jsonl_event [32mPASSED[0m[32m [ 50%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestBlockEventEmission::test_logging_failure_does_not_mask_exception [32mPASSED[0m[32m [ 52%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestBlockEventEmission::test_exception_message_still_includes_diagnostics [32mPASSED[0m[32m [ 55%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestPolicyContract::test_default_policy_immutable_roots [32mPASSED[0m[32m [ 58%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestPolicyContract::test_default_policy_log_path [32mPASSED[0m[32m [ 61%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestPolicyContract::test_policy_override_log_path_writes_to_tmp [32mPASSED[0m[32m [ 64%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestPolicyContract::test_policy_override_immutable_roots_changes_matched_root [32mPASSED[0m[32m [ 67%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestPolicyContract::test_policy_none_uses_default [32mPASSED[0m[32m [ 70%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestEnvVarIsolation::test_env_allow_mutation_does_not_bypass_protected_root [32mPASSED[0m[32m [ 73%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestEnvVarIsolation::test_env_deny_mutation_does_not_change_protected_root [32mPASSED[0m[32m [ 76%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestEnvVarIsolation::test_cli_override_works_regardless_of_env [32mPASSED[0m[32m [ 79%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestEnvVarIsolation::test_unset_env_vars_do_not_change_behavior [32mPASSED[0m[32m [ 82%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestFenceSelfCheck::test_self_check_ok_path [32mPASSED[0m[32m [ 85%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestFenceSelfCheck::test_self_check_fails_with_bad_log_path [32mPASSED[0m[32m [ 88%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestFenceSelfCheck::test_self_check_validates_write_gateway_wiring [32mPASSED[0m[32m [ 91%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestDeterministicReplay::test_replay_block_event_is_identical_under_fixed_clock [32mPASSED[0m[32m [ 94%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestDeterministicReplay::test_self_check_output_is_bitwise_identical_across_runs [32mPASSED[0m[32m [ 97%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestDeterministicReplay::test_block_event_without_override_uses_real_time [32mPASSED[0m[32m [100%][0m

============================ slowest 10 durations =============================
1.10s call     tests/unit_min_deps/test_ssot_mutation_fence.py::TestDeterministicReplay::test_block_event_without_override_uses_real_time
0.16s call     tests/unit_min_deps/test_ssot_mutation_fence.py::TestDeterministicReplay::test_self_check_output_is_bitwise_identical_across_runs
0.08s call     tests/unit_min_deps/test_ssot_mutation_fence.py::TestFenceSelfCheck::test_self_check_ok_path
0.07s call     tests/unit_min_deps/test_ptc_write_contract.py::TestPTCWriteContract::test_tool_registry_exists_and_must_route_via_write_gateway
0.01s call     tests/unit_min_deps/test_ssot_mutation_fence.py::TestFenceSelfCheck::test_self_check_fails_with_bad_log_path
0.01s call     tests/unit_min_deps/test_ptc_write_contract.py::TestPTCWriteContract::test_l2_execution_tools_do_not_expose_raw_write_primitives

(4 durations < 0.005s hidden.  Use -vv to show these durations.)
[32m============================= [32m[1m34 passed[0m[32m in 1.50s[0m[32m ==============================[0m


```

### Full Pytest Suite
```
❌ agent_discovery_full.json not found
[1m============================= test session starts =============================[0m
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
testpaths: C:\Git\Agentic-Workflow\tests\enforcement
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 4235 items / 46 errors
INTERNALERROR> Traceback (most recent call last):
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 318, in wrap_session
INTERNALERROR>     session.exitstatus = doit(config, session) or 0
INTERNALERROR>                          ^^^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 371, in _main
INTERNALERROR>     config.hook.pytest_collection(session=session)
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_hooks.py", line 512, in __call__
INTERNALERROR>     return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
INTERNALERROR>            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_manager.py", line 120, in _hookexec
INTERNALERROR>     return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
INTERNALERROR>            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_callers.py", line 167, in _multicall
INTERNALERROR>     raise exception
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_callers.py", line 139, in _multicall
INTERNALERROR>     teardown.throw(exception)
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\logging.py", line 788, in pytest_collection
INTERNALERROR>     return (yield)
INTERNALERROR>             ^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_callers.py", line 139, in _multicall
INTERNALERROR>     teardown.throw(exception)
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\warnings.py", line 98, in pytest_collection
INTERNALERROR>     return (yield)
INTERNALERROR>             ^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_callers.py", line 139, in _multicall
INTERNALERROR>     teardown.throw(exception)
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\config\__init__.py", line 1403, in pytest_collection
INTERNALERROR>     return (yield)
INTERNALERROR>             ^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_callers.py", line 121, in _multicall
INTERNALERROR>     res = hook_impl.function(*args)
INTERNALERROR>           ^^^^^^^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 382, in pytest_collection
INTERNALERROR>     session.perform_collect()
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 857, in perform_collect
INTERNALERROR>     self.items.extend(self.genitems(node))
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 1023, in genitems
INTERNALERROR>     yield from self.genitems(subnode)
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 1023, in genitems
INTERNALERROR>     yield from self.genitems(subnode)
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 1023, in genitems
INTERNALERROR>     yield from self.genitems(subnode)
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 1020, in genitems
INTERNALERROR>     rep, duplicate = self._collect_one_node(node, handle_dupes)
INTERNALERROR>                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 883, in _collect_one_node
INTERNALERROR>     rep = collect_one_node(node)
INTERNALERROR>           ^^^^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\runner.py", line 576, in collect_one_node
INTERNALERROR>     rep: CollectReport = ihook.pytest_make_collect_report(collector=collector)
INTERNALERROR>                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_hooks.py", line 512, in __call__
INTERNALERROR>     return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
INTERNALERROR>            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_manager.py", line 120, in _hookexec
INTERNALERROR>     return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
INTERNALERROR>            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_callers.py", line 167, in _multicall
INTERNALERROR>     raise exception
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_callers.py", line 139, in _multicall
INTERNALERROR>     teardown.throw(exception)
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\capture.py", line 880, in pytest_make_collect_report
INTERNALERROR>     rep = yield
INTERNALERROR>           ^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_callers.py", line 121, in _multicall
INTERNALERROR>     res = hook_impl.function(*args)
INTERNALERROR>           ^^^^^^^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\runner.py", line 400, in pytest_make_collect_report
INTERNALERROR>     call = CallInfo.from_call(
INTERNALERROR>            ^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\runner.py", line 353, in from_call
INTERNALERROR>     result: TResult | None = func()
INTERNALERROR>                              ^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\runner.py", line 398, in collect
INTERNALERROR>     return list(collector.collect())
INTERNALERROR>                 ^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\python.py", line 563, in collect
INTERNALERROR>     self._register_setup_module_fixture()
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\python.py", line 576, in _register_setup_module_fixture
INTERNALERROR>     self.obj, ("setUpModule", "setup_module")
INTERNALERROR>     ^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\python.py", line 289, in obj
INTERNALERROR>     self._obj = obj = self._getobj()
INTERNALERROR>                       ^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\python.py", line 560, in _getobj
INTERNALERROR>     return importtestmodule(self.path, self.config)
INTERNALERROR>            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\python.py", line 507, in importtestmodule
INTERNALERROR>     mod = import_path(
INTERNALERROR>           ^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\pathlib.py", line 587, in import_path
INTERNALERROR>     importlib.import_module(module_name)
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\importlib\__init__.py", line 90, in import_module
INTERNALERROR>     return _bootstrap._gcd_import(name[level:], package, level)
INTERNALERROR>            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
INTERNALERROR>   File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
INTERNALERROR>   File "<frozen importlib._bootstrap>", line 1331, in _find_and_load_unlocked
INTERNALERROR>   File "<frozen importlib._bootstrap>", line 935, in _load_unlocked
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\assertion\rewrite.py", line 197, in exec_module
INTERNALERROR>     exec(co, module.__dict__)
INTERNALERROR>   File "c:\Git\Agentic-Workflow\tests\agentic_core\L5_safety\enforcement\test_data.py", line 9, in <module>
INTERNALERROR>     import agentic_core.L5_safety.enforcement.data_enforcer
INTERNALERROR>   File "C:\Git\Agentic-Workflow\agentic_core\L5_safety\enforcement\data.py", line 34, in <module>
INTERNALERROR>     sys.exit(1)
INTERNALERROR> SystemExit: 1

[31m======================= [33m3 warnings[0m, [31m[1m46 errors[0m[31m in 3.35s[0m[31m ========================[0m

mainloop: caught unexpected SystemExit!

```

### Repro Run Output
```
ARGV=['python', '-m', 'agentic_core.L0_routing.scripts.execute_ssot_entrypoint', '--legacy', '--domains', 'L0_routing,L2_execution,L3_orchestration,L5_safety']



STDERR:
2026-02-21 18:10:07,085 WARNING agentic_core.L0_routing.enforcement.execution_gateway [V15-GW] Successful commit with no mutations detected
usage: execute_ssot_entrypoint.py [-h] [--territory TERRITORY] [--domains]
                                  [--agent AGENT] [--list-agents]
                                  [--enable-cda] [--dry-run] [--interactive]
                                  [--manual] [--validate] [--plan]
                                  [--agents AGENTS] [--capture-baseline]
                                  [--fence-self-check]
                                  [--v15-enforcement {0,1}] [-v]
execute_ssot_entrypoint.py: error: unrecognized arguments: L0_routing,L2_execution,L3_orchestration,L5_safety

```

### Protected Root Mutation Proof
#### Before
```
 M agentic_core/L4_state/config/vllm_routing_predicates.py
?? agentic_core/L5_safety/utils/canonical_hash.py
?? agentic_core/L5_safety/utils/evidence/
?? agentic_core/L5_safety/utils/rag_reranker_shim.py
?? agentic_core/L5_safety/utils/vllm_boundary_client.py

```

#### After
```
 M agentic_core/L4_state/config/vllm_routing_predicates.py
?? agentic_core/L5_safety/utils/canonical_hash.py
?? agentic_core/L5_safety/utils/evidence/
?? agentic_core/L5_safety/utils/rag_reranker_shim.py
?? agentic_core/L5_safety/utils/vllm_boundary_client.py

```

## RCA Delta (<=10 lines)

**Tool Registry Discovery:** Wave 8.1 revealed existing tool registry infrastructure (ToolSpec, call_tool, register_tool) across 27+ files in agentic_core. Tools exist in L2_execution, L3_orchestration, L5_safety layers.

**Write Contract Guard:** Created AST-based test suite validating: (1) tool registry exists and must route via write_gateway, (2) write_gateway is canonical write layer, (3) write_gateway functions accept allow_override parameter, (4) L2_execution/tools modules don't expose raw write primitives.

**Bypass Prevention:** Tools cannot bypass protected-root enforcement because write_gateway is the only sanctioned write API, and write_gateway calls enforce_protected_root before any filesystem operation. Direct write primitives (open/write_text/shutil) exist elsewhere but are not exposed as tool capabilities.

**Contract Enforcement:** AST tests ensure future tool additions cannot expose direct filesystem writes without routing through write_gateway. 5 tests passing (rc=0), total 34 unit_min_deps tests passing.

## Follow-ons (out-of-scope)

1. Add runtime tool invocation tracer to log all tool->write_gateway call chains for audit trail
2. Extend AST contract to validate that tool-registered functions import write_gateway (not just call it)
3. Create tool capability manifest documenting which tools have write access and their enforcement status
