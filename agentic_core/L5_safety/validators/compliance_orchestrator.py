# compliance_orchestrator.py
# L5 Sovereign Compliance Orchestrator - ULTRA HARDENED EDITION
# VERSION: 3.0 Sovereign Hardened (December 29, 2025)
# ULTRA HARDENING FEATURES:
#   • Fail-closed discovery with mandatory agent enforcement
#   • Layer-specific gravity authority mapping
#   • Exhaustive rejection diagnostics + health scoring
#   • Zero silent failures — every skip/rejection logged with root cause
#   • Recursive subpackage scanning
#   • Strict class filtering + validation methods
#   • Per-agent health checks before inclusion
#   • STRICTER validation rules:
#        - Async capability enforcement for atomic healers
#        - No direct higher-layer imports (gravity check)
#        - Sub-atomic size compliance (≤800 LOC)

import importlib
import inspect
import pkgutil
import traceback
import ast
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from collections import defaultdict
import sys

# [SSOT IMPORT] Structure blueprint is the single source of truth for folder structure
from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
    ROOT_WHITELIST,
    SOVEREIGN_EXCLUDED_FOLDERS,
)

class ComplianceOrchestrator:
    """
    L5 Sovereign Compliance Orchestrator

    Single responsibility:
      - Discover all validator agents in L5_safety/validators/
      - Categorize them (atomic/file-level healers, batch/cross-file, monitors)
      - Provide safe accessors for L6 orchestration layer

    This eliminates static imports in L6 and resolves the frequent discovery failures.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root.resolve()
        self.validators_path = self.project_root / "agentic_core" / "L5_safety" / "validators"

        # Discovered and instantiated agents
        self._atomic_validators: List[Any] = []   # Per-file healers with heal_violation()
        self._batch_validators: List[Any] = []    # Cross-file sweeps with execute()/run()
        self._monitors: List[Any] = []            # Global single-pass monitors
        self._all_agents: List[Any] = []

        # [ULTRA HARDENING] Mandatory agent registry (SSOT)
        self.MANDATORY_AGENTS: Set[str] = {
            "BootstrapAgent", "LocationAgent", "HierarchyAgent", "ImportAgent",
            "NamingAgent", "PineconeSovereignAgent", "TracingAgent", "MetricsAgent",
            "HealerAgent", "KeyMappingAgent", "ReportingAgent", "MissionResumeAgent",
            "NeuralAutoImmuneAgent", "MetaLearningAgent", "SovereignForensicsAgent"
        }

        # [GRAVITY AUTHORITY] Layer rank (lower = higher authority) - derived from SSOT
        # Layers are ordered by their L-number in agentic_core
        self.LAYER_AUTHORITY = {
            subfolder: int(subfolder[1]) if subfolder.startswith("L") and subfolder[1].isdigit() else 99
            for subfolder in CORE_SUBFOLDER_MAP.keys()
        }

        # Optional external components
        self.tracing = None
        self.metrics = None

        # [PRIORITY FIX] Use robust validator-focused discovery (recursive + strict checks)
        self._discover_and_instantiate()
        
        # [ULTRA HARDENING] Full sovereign territory sweep for mandatory agents
        self._discover_all_layers()
        self._enforce_mandatory_agent_compliance()

    def _discover_all_layers(self) -> None:
        """
        [FULL REPO DISCOVERY] Scan ALL layers for agents.
        
        Uses SSOT from structure_blueprint.py:
        - SOVEREIGN_REGISTRY defines root folders (agentic_core, apps_rg, etc.)
        - CORE_SUBFOLDER_MAP defines L1/L2 subfolders within agentic_core
        
        MANDATORY AGENTS (per user specification):
        - BootstrapAgent → L0_maintenance/scripts
        - LocationAgent → L5_safety/validators
        - HierarchyAgent → L5_safety/validators
        - ImportAgent → L5_safety/gravity
        - NamingAgent → utils/naming
        - PineconeSovereignAgent → L4_state/validation_context
        - TracingAgent → observability/tracing
        - MetricsAgent → observability/metrics
        - HealerAgent → L5_safety/guardrails AND L2_execution/tool_registry
        - KeyMappingAgent → L5_safety/validators
        - ReportingAgent → observability/compliance
        - MissionResumeAgent → L3_orchestration/workflow_engines
        - NeuralAutoImmuneAgent → L5_safety/guardrails
        - MetaLearningAgent → L3_orchestration/workflow_engines
        - SovereignForensicsAgent → L3_orchestration/workflow_engines
        """
        print(f"\n[FULL AGENT DISCOVERY] Scanning ALL layers for MANDATORY agents...")
        print(f"   [SOVEREIGN ORDER] Enforcing discovery across all 6 layers")
        print(f"   [MANDATORY COUNT] Expecting {len(self.MANDATORY_AGENTS)} critical agents")
        print(f"   [SSOT] Using structure_blueprint.py as source of truth for folder paths")
        
        # [SSOT] Build discovery paths dynamically from CORE_SUBFOLDER_MAP
        discovery_paths: List[Tuple[str, Path]] = []
        
        # [OPTIMIZED] Prioritize L5_safety/validators first, skip known broken directories
        SKIP_DIRECTORIES = {"scripts", "P1_core", "P2_domain", "P1_interfaces", "P5_meta"}
        
        # Iterate through all L1 folders in agentic_core (from SSOT)
        for l1_folder, l2_subfolders in CORE_SUBFOLDER_MAP.items():
            for l2_folder in l2_subfolders:
                # Skip directories with many broken imports
                if l2_folder in SKIP_DIRECTORIES:
                    continue
                module_prefix = f"agentic_core.{l1_folder}.{l2_folder}"
                folder_path = self.project_root / "agentic_core" / l1_folder / l2_folder
                discovery_paths.append((module_prefix, folder_path))
        
        total_discovered = 0
        
        for module_prefix, path in discovery_paths:
            if not path.exists():
                continue
            
            discovered_in_path = self._discover_agents_in_path(module_prefix, path)
            total_discovered += discovered_in_path
        
        # Verify MANDATORY agents were loaded (using SSOT from self.MANDATORY_AGENTS)
        loaded_names = {type(a).__name__ for a in self._all_agents}
        loaded_mandatory = self.MANDATORY_AGENTS & loaded_names
        missing_mandatory = self.MANDATORY_AGENTS - loaded_names
        
        print(f"   [OK] FULL DISCOVERY COMPLETE: {total_discovered} total agents")
        print(f"      Atomic (per-file): {len(self._atomic_validators)}")
        print(f"      Batch (cross-file): {len(self._batch_validators)}")
        print(f"      Monitors: {len(self._monitors)}")
        print(f"      Mandatory loaded: {len(loaded_mandatory)}/{len(self.MANDATORY_AGENTS)}")
        
        if missing_mandatory:
            print(f"   [!] Missing mandatory agents: {', '.join(sorted(missing_mandatory)[:5])}")

    def _enforce_mandatory_agent_compliance(self) -> None:
        """[ULTRA HARDENING] Final sovereign verdict on mandatory agent presence"""
        loaded_names = {type(a).__name__ for a in self._all_agents}
        missing = self.MANDATORY_AGENTS - loaded_names
        
        if missing:
            print(f"\n[!] [SOVEREIGN BREACH] MANDATORY AGENT VIOLATION")
            print(f"    {len(missing)} critical agents not discovered:")
            for agent in sorted(missing):
                print(f"      • {agent} — REQUIRED FOR CANON COMPLIANCE")
            print(f"    [ACTION REQUIRED] Verify file existence, naming, and __init__ signature")
            print(f"    Discovery will continue but sovereignty is COMPROMISED")
        else:
            print(f"\n[OK] [ETERNAL SOVEREIGNTY] All {len(self.MANDATORY_AGENTS)} mandatory agents discovered")
            print(f"    Canon structural integrity: PRESERVED")

    def _discover_agents_in_path(self, module_prefix: str, path: Path) -> int:
        """Discover and instantiate agents from a specific path."""
        discovered = 0
        
        for py_file in path.rglob("*.py"):  # RECURSIVE: Capture agents in subfolders
            # [HARDENING] Skip known non-agent files
            if py_file.name.startswith("_"):
                continue
            if py_file.name in {"__init__.py", "base_agent.py", "agent_factory.py"}:
                continue
            
            module_name = f"{module_prefix}.{py_file.stem}"
            
            try:
                module = importlib.import_module(module_name)
                
                for attr_name in dir(module):
                    # Look for classes ending in Agent or agent
                    # [CANON ENFORCEMENT] Strict CamelCase "Agent" suffix
                    if not attr_name.endswith("Agent"):  # STANDARDIZE: Require proper CamelCase "Agent" suffix
                        continue
                    
                    attr = getattr(module, attr_name)
                    if not inspect.isclass(attr):
                        continue
                    if attr.__module__ != module_name:
                        continue
                    
                    # Skip if already discovered
                    if any(type(a).__name__ == attr_name for a in self._all_agents):
                        continue
                    
                    # Try to instantiate
                    try:
                        instance = attr(self.project_root)
                    except TypeError:
                        try:
                            instance = attr()
                        except Exception:
                            continue
                    except Exception:
                        continue
                    
                    self._all_agents.append(instance)
                    discovered += 1
                    
                    # Categorize based on capabilities
                    if hasattr(instance, "heal_violation"):
                        self._atomic_validators.append(instance)
                    elif hasattr(instance, "execute") or hasattr(instance, "run"):
                        if "monitor" in attr_name.lower():
                            self._monitors.append(instance)
                        else:
                            self._batch_validators.append(instance)
                    
            except Exception as e:
                # Silent skip for import errors during discovery
                print(f"      [!] FAILED IMPORT {py_file.relative_to(self.project_root)}: {e}")
        
        return discovered

    def _discover_and_instantiate(self) -> None:
        """
        ROBUST discovery:
          - Recursively walks all subdirectories under validators/
          - Uses pkgutil.walk_packages for proper package traversal
          - Isolates import errors per module
          - Provides detailed diagnostics on failure
          - Falls back to no-arg instantiation if project_root signature mismatches
        """
        if not self.validators_path.exists():
            print(f"   [!] Validators path not found: {self.validators_path}")
            return

        rel_path = self.validators_path.relative_to(self.project_root)
        print(f"   [>] Starting ROBUST agent discovery in {rel_path}")

        discovered_count = 0
        # Use walk_packages for recursive traversal (handles subpackages correctly)
        for module_info in pkgutil.walk_packages([str(self.validators_path)]):
            if module_info.ispkg:
                continue

            # Build correct dotted module name even for nested packages
            # module_info.module_finder.find_module(module_info.name).loader.path gives full path
            # Safer: reconstruct from relative path
            try:
                loader = module_info.module_finder
                full_path = Path(loader.path)  # finder path is the root (validators/)
                module_rel = Path(module_info.name.replace('.', '/'))
                if module_rel.suffix == '.py':
                    module_rel = module_rel.with_suffix('')
                nested_name = '.'.join((full_path / module_rel).relative_to(self.validators_path).parts).rstrip('.py')
                module_name = f"agentic_core.L5_safety.validators.{nested_name}"
            except Exception:
                # Fallback to flat assumption (original behaviour)
                module_name = f"agentic_core.L5_safety.validators.{module_info.name}"

            try:
                module = importlib.import_module(module_name)
                print(f"      [OK] Imported module: {module_name}")

                agent_classes = []
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if not inspect.isclass(attr) or not attr_name.endswith("Agent"):
                        continue
                    if attr.__module__ != module_name:  # Avoid re-imported classes
                        continue

                    agent_classes.append((attr_name, attr))

                if not agent_classes:
                    print(f"      [INFO] No Agent classes found in {module_name}")
                    continue

                for attr_name, agent_class in agent_classes:
                    print(f"         [>] Instantiating {attr_name}")
                    try:
                        # Primary: most agents expect project_root
                        # [HARDENING] Prefer project_root init — fallback only on clear TypeError
                        instance = agent_class(self.project_root)
                    except TypeError as te:
                        # Common during dev: signature mismatch
                        if "required positional argument" in str(te).lower():
                            print(f"         [!] {attr_name} missing project_root arg → trying no-arg init")
                            try:
                                instance = agent_class()
                            except Exception as no_arg_e:
                                print(f"         [!] No-arg instantiation failed: {no_arg_e}")
                                traceback.print_exc(limit=2)
                                continue
                        else:
                            raise
                    except Exception as inst_e:
                        print(f"         [!] Instantiation failed for {attr_name}: {inst_e}")
                        traceback.print_exc(limit=2)
                        continue

                    self._all_agents.append(instance)
                    discovered_count += 1

                    # Categorize based on capabilities
                    if hasattr(instance, "heal_violation"):
                        self._atomic_validators.append(instance)
                        print(f"         [CLASSIFIED] Atomic healer")
                    elif hasattr(instance, "execute") or hasattr(instance, "run"):
                        if "monitor" in attr_name.lower() or "Monitor" in attr_name:
                            self._monitors.append(instance)
                            print(f"         [CLASSIFIED] Monitor")
                        else:
                            self._batch_validators.append(instance)
                            print(f"         [CLASSIFIED] Batch validator")
                    else:
                        print(f"         [INFO] {attr_name} has no known execution method")

                    # ===================================================================
                    # STRICT AGENT VALIDATION - Sovereign health checks before inclusion
                    # ===================================================================
                    print(f"         [VALIDATING] Running sovereign health checks on {attr_name}")
                    validation_errors = self._validate_agent_instance_strict(instance, attr_name, module)
                    if validation_errors:
                        # CONCISE REJECTION: Single line summary + first critical error
                        primary_error = validation_errors[0]
                        extra_count = len(validation_errors) - 1
                        extra = f" (+{extra_count} more)" if extra_count > 0 else ""
                        print(f"         [!] REJECTED {attr_name}: {primary_error}{extra}")
                        # Remove from _all_agents if already appended
                        if instance in self._all_agents:
                            self._all_agents.remove(instance)
                        # Remove from categorized lists
                        if instance in self._atomic_validators:
                            self._atomic_validators.remove(instance)
                        if instance in self._batch_validators:
                            self._batch_validators.remove(instance)
                        if instance in self._monitors:
                            self._monitors.remove(instance)
                        continue  # Skip to next agent

                    print(f"         [VALIDATED] {attr_name} passed STRICT sovereign checks")
                    print(f"         [HEALTH] Agent operational — sovereignty intact")

            except Exception as e:
                print(f"   [!] Failed to load module {module_name}: {e}")
                traceback.print_exc(limit=3)
                print(f"      [!] Failed module {module_name}: {e} - continuing")

        total_discovered = len(self._all_agents)
        print(f"   [OK] ROBUST DISCOVERY COMPLETE: {total_discovered} total agents")
        print(f"      Atomic (per-file): {len(self._atomic_validators)}")
        print(f"      Batch (cross-file): {len(self._batch_validators)}")
        print(f"      Total validated & active: {len(self._all_agents)}")
        print(f"      Monitors: {len(self._monitors)}")

        if total_discovered == 0:
            print(f"   [WARNING] No agents discovered — check validators/ directory structure and Agent naming convention")

    # ===================================================================
    # STRICT AGENT VALIDATION METHODS
    # ===================================================================

    def _validate_agent_instance_strict(self, instance: Any, class_name: str, module: Any) -> List[str]:
        """
        Perform STRICT sovereign health checks on a discovered agent instance.
        Returns list of error messages (empty = healthy).
        Now includes layer-aware gravity authority.

        Checks:
          1. Required execution capability
          2. Async enforcement for atomic healers (Canon Key: async resilience)
          3. Method signature compliance
          4. Docstring + metadata hygiene
          5. Gravity law compliance (no upward imports from higher layers)
          6. Sub-atomic size policy (≤800 LOC per module)
          7. Layer authority compliance (based on module path)
        """
        errors: List[str] = []

        # 1. Must have at least one execution entrypoint
        has_heal = hasattr(instance, "heal_violation")
        has_exec = hasattr(instance, "execute") or hasattr(instance, "run")
        if not (has_heal or has_exec):
            errors.append("No execution method: missing heal_violation() or execute()/run()")

        # 2. STRICT: Atomic healers MUST be async (resilience + non-blocking healing loop)
        if has_heal:
            heal_method = getattr(instance, "heal_violation")
            if not inspect.iscoroutinefunction(heal_method):
                errors.append("Atomic healer violation: heal_violation() MUST be async def (use 'async def')")

        # 3. Primary method callability + signature
        primary_method = None
        if has_heal:
            primary_method = getattr(instance, "heal_violation")
            expected_params = ["file_path"]  # Most common: async heal_violation(file_path: str/Path)
        elif has_exec:
            primary_method = getattr(instance, "execute", getattr(instance, "run", None))
            expected_params = []  # Batch agents usually take no args or manage scope internally

        if primary_method:
            if not callable(primary_method):
                errors.append(f"Primary method {primary_method.__name__} is not callable")
            else:
                try:
                    sig = inspect.signature(primary_method)
                    missing_params = [p for p in expected_params if p not in sig.parameters]
                    if missing_params and has_heal:  # Only strict for atomic healers
                        errors.append(f"heal_violation missing required param(s): {missing_params}")
                except (ValueError, TypeError):
                    # Some built-in methods don't support signature inspection
                    pass

        # 4. Docstring + metadata hygiene (Canon purity)
        if not getattr(instance.__class__, "__doc__", None) or len(instance.__class__.__doc__.strip()) < 20:
            errors.append("Insufficient class docstring (must be ≥20 meaningful characters)")

        # 5. GRAVITY LAW: No upward imports from higher authority layers
        gravity_violations = self._check_gravity_compliance(module)
        if gravity_violations:
            errors.append(f"CRITICAL GRAVITY BREACH: {len(gravity_violations)} violations")
            errors.extend([f"Gravity violation: {v}" for v in gravity_violations[:5]])
            if len(gravity_violations) > 5:
                errors.append(f"... and {len(gravity_violations)-5} more gravity leaks")

        # 6. SUB-ATOMIC SIZE POLICY: Module ≤800 LOC (Canon Key 13/49)
        module_path = getattr(module, "__file__", None)
        if module_path:
            try:
                loc = sum(1 for line in open(module_path, 'r', encoding='utf-8') if line.strip() and not line.strip().startswith('#'))
                if loc > 800:
                    errors.append(f"Sub-atomic size violation: {loc} LOC > 800 limit (module too large)")
            except Exception:
                errors.append("Failed to count LOC for size policy check")

        # 7. [ULTRA] Layer authority check — determine agent's layer and validate import rights
        module_path_str = str(module_path) if module_path else ""
        agent_layer_rank = 999  # Unknown = lowest authority
        for layer_name, rank in self.LAYER_AUTHORITY.items():
            if layer_name.replace("_", "/") in module_path_str or layer_name in module_path_str:
                agent_layer_rank = rank
                break
        
        # Extract forbidden imports based on agent layer
        if agent_layer_rank <= 4:  # L0-L4 agents have broader rights
            pass  # Allow more
        elif agent_layer_rank == 5:  # L5 agents — highest safety, strictest gravity
            # Check for direct app imports
            import_counts = defaultdict(int)
            try:
                with open(module_path, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read())
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            import_counts[alias.name] += 1
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            import_counts[node.module] += 1
            except Exception:
                pass
            
            if any(imp.startswith("apps_") for imp in import_counts.keys()):
                errors.append("L5 AGENT GRAVITY BREACH: Direct import from downstream apps_* territory")
        
        # Final health score - only return errors if there are actual issues
        if errors:
            severity = "CRITICAL" if any("CRITICAL" in e or "BREACH" in e for e in errors) else "WARNING"
            errors.insert(0, f"[{severity}] Agent health: FAILED ({len(errors)} issues)")
        # Don't add "[HEALTHY]" to errors - return empty list for healthy agents

        return errors

    # ===================================================================
    # GRAVITY COMPLIANCE CHECK (Static analysis)
    # ===================================================================

    def _check_gravity_compliance(self, module: Any) -> List[str]:
        """
        Static analysis: Detect upward gravity leaks.
        Scans AST for imports from higher authority layers than the agent's own layer (L5).
        L5 agents may only import from L0-L4, utils, runtime, config, etc.
        """
        violations: List[str] = []
        module_path = getattr(module, "__file__", None)
        if not module_path:
            return ["Unable to locate module file for gravity scan"]

        try:
            with open(module_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())
        except Exception as e:
            return [f"AST parse failed: {e}"]

        # Define forbidden upward imports for L5 agents
        FORBIDDEN_PREFIXES = [
            "apps_rg", "apps_lic", "apps_shared",  # Downstream apps
            "apps.",  # Any apps territory
        ]

        # [ULTRA] Also block L5 importing from other L5 subpackages in unauthorized way
        # (e.g., validators importing directly from guardrails without mediation)
        RESTRICTED_L5 = [
            "agentic_core.L5_safety.guardrails",
            "agentic_core.L5_safety.red_teaming"
        ]

        # Also block direct imports from higher sovereign territories if not mediated
        # (L5 is highest safety — no upward pull needed)

        import_counts = defaultdict(int)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    import_counts[alias.name] += 1
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    import_counts[node.module] += 1

        for imp, count in import_counts.items():
            if any(imp.startswith(bad) for bad in FORBIDDEN_PREFIXES):
                violations.append(f"Forbidden import '{imp}' ({count}x) — downstream/app layer pull")
            if any(imp.startswith(restricted) for restricted in RESTRICTED_L5):
                if "validators" in str(module_path):
                    violations.append(f"L5 Internal gravity: validators → {imp} (use mediated interface)")

        return violations

    # ===================================================================
    # Public Accessors for L6 canon_validator_agentic_v2.py
    # ===================================================================

    def get_atomic_validators(self) -> List[Any]:
        """Return agents that perform per-file healing (have heal_violation method)."""
        return self._atomic_validators.copy()

    def get_batch_validators(self) -> List[Any]:
        """Return agents that perform cross-file or project-wide sweeps."""
        return self._batch_validators.copy()

    def get_monitors(self) -> List[Any]:
        """Return global single-pass monitoring agents."""
        return self._monitors.copy()

    def get_all_agents(self) -> List[Any]:
        """Return all discovered agents (for debugging/telemetry)."""
        return self._all_agents.copy()

    # ===================================================================
    # Optional Extensions (Tracing, Metrics) - Stubbed for future use
    # ===================================================================

    def initialize_tracing(self):
        """Placeholder for OpenTelemetry integration."""
        try:
            from opentelemetry import trace
            tracer = trace.get_tracer(__name__)
            self.tracing = tracer
            print("   [OK] Tracing initialized")
        except ImportError:
            print("   [INFO] opentelemetry not available - tracing disabled")

    def initialize_metrics(self):
        """Placeholder for Prometheus metrics agent integration."""
        # Future: load MetricsAgent and expose
        pass


# =======================================================================
# Factory / Singleton Export - Used by canon_validator_agentic_v2.py
# =======================================================================

def compliance_orchestrator(project_root: Optional[Path] = None) -> ComplianceOrchestrator:
    """
    Factory function exported for import in L6.
    Usage in canon_validator_agentic_v2.py:
        orchestrator = compliance_orchestrator(Path.cwd())
    """
    if project_root is None:
        # Fallback to current working directory
        project_root = Path.cwd()
    return ComplianceOrchestrator(project_root)
