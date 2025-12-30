# compliance_orchestrator.py
# L5 Sovereign Compliance Orchestrator - Full Stub Implementation
# PURPOSE: Owns dynamic discovery, categorization, and provisioning of all validator agents
# VERSION: 2.9 Compatible - Enables true dynamic agent loading in canon_validator_agentic_v2.py

import importlib
import inspect
import pkgutil
from pathlib import Path
from typing import Any, Dict, List, Optional

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
        """Scan validators directory and instantiate agent classes."""
        if not self.validators_path.exists():
            print(f"   [!] Validators path not found: {self.validators_path}")
            return

        print(f"   [>] Discovering agents in {self.validators_path.relative_to(self.project_root)}")

        discovered_count = 0
        for module_info in pkgutil.iter_modules([str(self.validators_path)]):
            if module_info.ispkg:
                continue

            module_name = f"agentic_core.L5_safety.validators.{module_info.name}"
            try:
                module = importlib.import_module(module_name)
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if not inspect.isclass(attr) or not attr_name.endswith("Agent"):
                        continue
                    if attr.__module__ != module_name:  # Avoid re-imported classes
                        continue

                    # Instantiate with project_root (most agents expect it)
                    try:
                        instance = attr(self.project_root)
                    except TypeError:
                        # Fallback: try no-arg init for agents that don't need root
                        instance = attr()

                    self._all_agents.append(instance)
                    discovered_count += 1

                    # Categorize based on capabilities
                    if hasattr(instance, "heal_violation"):
                        self._atomic_validators.append(instance)
                    elif hasattr(instance, "execute") or hasattr(instance, "run"):
                        if "monitor" in attr_name.lower() or "Monitor" in attr_name:
                            self._monitors.append(instance)
                        else:
                            self._batch_validators.append(instance)

            except Exception as e:
                print(f"   [!] Failed to load {module_info.name}: {e}")

        print(f"   [OK] Discovered and instantiated {discovered_count} agents")
        print(f"      Atomic (per-file): {len(self._atomic_validators)}")
        print(f"      Batch (cross-file): {len(self._batch_validators)}")
        print(f"      Monitors: {len(self._monitors)}")

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
