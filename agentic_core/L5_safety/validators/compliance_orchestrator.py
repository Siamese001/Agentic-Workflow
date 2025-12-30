# compliance_orchestrator.py
# L5 Sovereign Compliance Orchestrator - Full Stub Implementation
# PURPOSE: Owns ROBUST dynamic discovery, STRICT VALIDATION, categorization, and provisioning of all validator agents
# VERSION: 2.9+ Strict Edition
# HARDENING: 
#   • Recursive subpackage scanning
#   • Strict class filtering + validation methods
#   • Per-agent health checks before inclusion
#   • Better error isolation and diagnostics
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
from typing import Any, Dict, List, Optional
from collections import defaultdict

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

        # Optional external components
        self.tracing = None
        self.metrics = None

        self._discover_and_instantiate()

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

            except Exception as e:
                print(f"   [!] Failed to load module {module_name}: {e}")
                traceback.print_exc(limit=3)

        total_discovered = len(self._all_agents)
        print(f"   [OK] ROBUST DISCOVERY COMPLETE: {total_discovered} total agents")
        print(f"      Atomic (per-file): {len(self._atomic_validators)}")
        print(f"      Batch (cross-file): {len(self._batch_validators)}")
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

        Checks:
          1. Required execution capability
          2. Async enforcement for atomic healers (Canon Key: async resilience)
          3. Method signature compliance
          4. Docstring + metadata hygiene
          5. Gravity law compliance (no upward imports from higher layers)
          6. Sub-atomic size policy (≤800 LOC per module)
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
            # L5 cannot import from itself in upward way, but allow internal
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
