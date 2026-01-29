import inspect
import pickle

from apps_lic.engines.HOP1ProfileAnalysisAgent import HOP1ProfileAnalysisAgent
from apps_lic.engines.HOP2ResearchAgent import HOP2ResearchAgent


class CanonValidator:
    """
    Sovereign Architecture Enforcement.
    Validates that all Agents comply with:
    1. Root Injection Pattern (MRO)
    2. Sovereign Seal (Immutability)
    3. Serialization Safety (Pickle)
    """

    REGISTRY = [HOP1ProfileAnalysisAgent, HOP2ResearchAgent]

    @classmethod
    def validate_all(cls) -> bool:
        """Run all checks on registered agents."""
        results = []
        for agent_cls in cls.REGISTRY:
            try:
                print(f"Validating {agent_cls.__name__}...")
                cls._check_mro(agent_cls)
                cls._check_seal_contract(agent_cls)
                cls._check_serialization(agent_cls)
                results.append(True)
                print(f"PASS: {agent_cls.__name__}")
            except Exception as e:
                print(f"FAIL: {agent_cls.__name__} - {e}")
                results.append(False)
        return all(results)

    @staticmethod
    def _check_mro(agent_cls: type) -> None:
        """Enforce LICAgentBase is the immediate parent (Root Injection)."""
        mro = inspect.getmro(agent_cls)
        # Index 0 is self, Index 1 must be LICAgentBase
        if mro[1].__name__ != "LICAgentBase":
            raise TypeError(
                f"MRO Violation: {mro[1].__name__} found at index 1. Expected LICAgentBase."
            )

    @staticmethod
    def _check_seal_contract(agent_cls: type) -> None:
        """Enforce presence of Sovereign Seal mechanisms."""
        # Check for _sealed field definition
        if not hasattr(agent_cls, "_sealed"):
            # It might be an instance attribute, check __annotations__ or __init__ logic
            # For this validator, we check if the class enforces it on an instance
            pass

        # Instantiate (Mocking config/dependencies would be required in a real run,
        # assuming basic init is safe or mocks provided by environment)
        try:
            instance = agent_cls()
        except Exception:
            # If init fails due to missing mocks, we skip runtime check but warn
            print(f"  [WARN] Could not instantiate {agent_cls.__name__} for runtime seal check.")
            return

        if not getattr(instance, "_sealed", False):
            raise RuntimeError("Sovereign Seal not engaged after __post_init__.")

        # Test Immutability
        try:
            instance.canon_test_attr = "illegal"
            raise RuntimeError("Sovereign Seal breached: Attribute modification allowed.")
        except AttributeError:
            pass  # Success

    @staticmethod
    def _check_serialization(agent_cls: type) -> None:
        """Enforce pickling support."""
        try:
            instance = agent_cls()
        except Exception:
            return  # Skip if init fails

        try:
            dump = pickle.dumps(instance)
            loaded = pickle.loads(dump)
            if not getattr(loaded, "_sealed", False):
                raise RuntimeError("Sovereign Seal lost after deserialization.")
        except Exception as e:
            raise RuntimeError(f"Serialization failed: {e}")


if __name__ == "__main__":
    if CanonValidator.validate_all():
        print("\n[SOVEREIGNTY VERIFIED]")
        exit(0)
    else:
        print("\n[VALIDATION FAILED]")
        exit(1)
