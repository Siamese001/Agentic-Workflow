"""ADG-driven tests for L0 safety seam modules — fan_in=6 each.

Covers:
  agentic_core/L0_routing/seams/safety_reasoning_seam.py   fan_in=6
  agentic_core/L0_routing/seams/safety_validators_seam.py  fan_in=6

Seams provide lazy importlib loaders to avoid upward L0→L5 direct imports.
Tests verify: all loaders are callable, return a class on success,
and raise ImportError cleanly when the target module is absent.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


class TestSafetyReasoningSeam:
    def test_module_importable(self):
        import agentic_core.L0_routing.seams.safety_reasoning_seam  # noqa: F401

    def test_load_naming_agent_callable(self):
        from agentic_core.L0_routing.seams.safety_reasoning_seam import load_naming_agent
        assert callable(load_naming_agent)

    def test_load_structure_enforcer_agent_callable(self):
        from agentic_core.L0_routing.seams.safety_reasoning_seam import load_structure_enforcer_agent
        assert callable(load_structure_enforcer_agent)

    def test_load_cognitive_disposition_agent_callable(self):
        from agentic_core.L0_routing.seams.safety_reasoning_seam import load_cognitive_disposition_agent
        assert callable(load_cognitive_disposition_agent)

    def test_load_file_classification_agent_callable(self):
        from agentic_core.L0_routing.seams.safety_reasoning_seam import load_file_classification_agent
        assert callable(load_file_classification_agent)

    def test_load_location_validator_agent_callable(self):
        from agentic_core.L0_routing.seams.safety_reasoning_seam import load_location_validator_agent
        assert callable(load_location_validator_agent)

    def test_load_verification_gate_adapter_callable(self):
        from agentic_core.L0_routing.seams.safety_reasoning_seam import load_verification_gate_adapter
        assert callable(load_verification_gate_adapter)

    def test_load_naming_agent_returns_class(self):
        from agentic_core.L0_routing.seams.safety_reasoning_seam import load_naming_agent
        cls = load_naming_agent()
        assert isinstance(cls, type)

    def test_load_structure_enforcer_returns_class(self):
        from agentic_core.L0_routing.seams.safety_reasoning_seam import load_structure_enforcer_agent
        cls = load_structure_enforcer_agent()
        assert isinstance(cls, type)

    def test_load_file_classification_returns_class(self):
        from agentic_core.L0_routing.seams.safety_reasoning_seam import load_file_classification_agent
        cls = load_file_classification_agent()
        assert isinstance(cls, type)

    def test_missing_module_raises_import_error(self, monkeypatch):
        """Seam must propagate ImportError if the L5 module is unavailable."""
        import importlib
        original = importlib.import_module

        def _fail_import(name, *args, **kwargs):
            if "NamingAgent" in name:
                raise ImportError(f"Simulated missing module: {name}")
            return original(name, *args, **kwargs)

        monkeypatch.setattr(importlib, "import_module", _fail_import)
        from agentic_core.L0_routing.seams.safety_reasoning_seam import load_naming_agent
        with pytest.raises(ImportError):
            load_naming_agent()


class TestSafetyKernelSeam:
    """safety_kernel_seam.py — fan_in=3."""

    def test_module_importable(self):
        import agentic_core.L0_routing.seams.safety_kernel_seam  # noqa: F401

    def test_load_classification_kernel_callable(self):
        from agentic_core.L0_routing.seams.safety_kernel_seam import load_classification_kernel
        assert callable(load_classification_kernel)

    def test_get_classification_cache_context_callable(self):
        from agentic_core.L0_routing.seams.safety_kernel_seam import get_classification_cache_context
        assert callable(get_classification_cache_context)

    def test_load_classification_kernel_returns_module_or_raises(self):
        import types
        from agentic_core.L0_routing.seams.safety_kernel_seam import load_classification_kernel
        try:
            mod = load_classification_kernel()
            assert isinstance(mod, types.ModuleType)
        except ImportError:
            pass

    def test_missing_module_raises_import_error(self, monkeypatch):
        import importlib
        original = importlib.import_module

        def _fail(name, *args, **kwargs):
            if "classification_kernel" in name:
                raise ImportError(f"Simulated: {name}")
            return original(name, *args, **kwargs)

        monkeypatch.setattr(importlib, "import_module", _fail)
        from agentic_core.L0_routing.seams.safety_kernel_seam import load_classification_kernel
        with pytest.raises(ImportError):
            load_classification_kernel()


class TestSafetyEnforcementSeam:
    """safety_enforcement_seam.py — fan_in=4."""

    def test_module_importable(self):
        import agentic_core.L0_routing.seams.safety_enforcement_seam  # noqa: F401

    def test_load_code_deduplication_agent_callable(self):
        from agentic_core.L0_routing.seams.safety_enforcement_seam import load_code_deduplication_agent
        assert callable(load_code_deduplication_agent)

    def test_load_archival_gatekeeper_callable(self):
        from agentic_core.L0_routing.seams.safety_enforcement_seam import load_archival_gatekeeper
        assert callable(load_archival_gatekeeper)

    def test_load_ssot_scanner_callable(self):
        from agentic_core.L0_routing.seams.safety_enforcement_seam import load_ssot_scanner
        assert callable(load_ssot_scanner)

    def test_load_activation_gate_callable(self):
        from agentic_core.L0_routing.seams.safety_enforcement_seam import load_activation_gate
        assert callable(load_activation_gate)

    def test_load_code_deduplication_returns_class_or_raises(self):
        from agentic_core.L0_routing.seams.safety_enforcement_seam import load_code_deduplication_agent
        try:
            cls = load_code_deduplication_agent()
            assert isinstance(cls, type)
        except ImportError:
            pass

    def test_load_activation_gate_returns_module_or_raises(self):
        import types
        from agentic_core.L0_routing.seams.safety_enforcement_seam import load_activation_gate
        try:
            mod = load_activation_gate()
            assert isinstance(mod, types.ModuleType)
        except ImportError:
            pass

    def test_missing_module_raises_import_error(self, monkeypatch):
        import importlib
        original = importlib.import_module

        def _fail_import(name, *args, **kwargs):
            if "CodeDeduplication" in name:
                raise ImportError(f"Simulated missing: {name}")
            return original(name, *args, **kwargs)

        monkeypatch.setattr(importlib, "import_module", _fail_import)
        from agentic_core.L0_routing.seams.safety_enforcement_seam import load_code_deduplication_agent
        with pytest.raises(ImportError):
            load_code_deduplication_agent()


class TestSafetyValidatorsSeam:
    def test_module_importable(self):
        import agentic_core.L0_routing.seams.safety_validators_seam  # noqa: F401

    def test_load_hygiene_guardian_callable(self):
        from agentic_core.L0_routing.seams.safety_validators_seam import load_hygiene_guardian
        assert callable(load_hygiene_guardian)

    def test_load_autonomy_guardian_callable(self):
        from agentic_core.L0_routing.seams.safety_validators_seam import load_autonomy_guardian
        assert callable(load_autonomy_guardian)

    def test_load_healing_strategy_callable(self):
        from agentic_core.L0_routing.seams.safety_validators_seam import load_healing_strategy
        assert callable(load_healing_strategy)

    def test_load_canonical_truth_validator_callable(self):
        from agentic_core.L0_routing.seams.safety_validators_seam import load_canonical_truth_validator
        assert callable(load_canonical_truth_validator)

    def test_load_cognitive_disposition_agent_callable(self):
        from agentic_core.L0_routing.seams.safety_validators_seam import load_cognitive_disposition_agent
        assert callable(load_cognitive_disposition_agent)

    def test_load_dashboard_ssot_definitions_callable(self):
        from agentic_core.L0_routing.seams.safety_validators_seam import load_dashboard_ssot_definitions
        assert callable(load_dashboard_ssot_definitions)

    def test_load_hygiene_guardian_returns_class_or_raises_import_error(self):
        from agentic_core.L0_routing.seams.safety_validators_seam import load_hygiene_guardian
        try:
            cls = load_hygiene_guardian()
            assert isinstance(cls, type)
        except ImportError:
            pass  # optional L5 module absent — acceptable

    def test_load_autonomy_guardian_returns_class_or_raises_import_error(self):
        from agentic_core.L0_routing.seams.safety_validators_seam import load_autonomy_guardian
        try:
            cls = load_autonomy_guardian()
            assert isinstance(cls, type)
        except ImportError:
            pass

    def test_load_healing_strategy_returns_module_or_raises_import_error(self):
        import types
        from agentic_core.L0_routing.seams.safety_validators_seam import load_healing_strategy
        try:
            mod = load_healing_strategy()
            assert isinstance(mod, types.ModuleType)
        except ImportError:
            pass

    def test_missing_module_raises_import_error(self, monkeypatch):
        import importlib
        original = importlib.import_module

        def _fail_import(name, *args, **kwargs):
            if "HygieneGuardian" in name:
                raise ImportError(f"Simulated missing module: {name}")
            return original(name, *args, **kwargs)

        monkeypatch.setattr(importlib, "import_module", _fail_import)
        from agentic_core.L0_routing.seams.safety_validators_seam import load_hygiene_guardian
        with pytest.raises(ImportError):
            load_hygiene_guardian()
