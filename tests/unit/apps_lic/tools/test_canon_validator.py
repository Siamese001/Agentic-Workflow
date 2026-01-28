import unittest
from apps_lic.tools.canon_validator import CanonValidator
from apps_lic.engines.HOP1ProfileAnalysisAgent import HOP1ProfileAnalysisAgent

class TestCanonValidator(unittest.TestCase):
    """
    MANDATORY: 100% Pass Required.
    Tests the Validator itself to ensure it correctly polices the architecture.
    """

    def test_validator_detects_compliance(self):
        """
        Happy Path: Verify compliant agents pass validation.
        """
        # HOP1 is known compliant from Phase 1-3
        try:
            CanonValidator._check_mro(HOP1ProfileAnalysisAgent)
            CanonValidator._check_seal_contract(HOP1ProfileAnalysisAgent)
            CanonValidator._check_serialization(HOP1ProfileAnalysisAgent)
        except Exception as e:
            self.fail(f"Validator rejected compliant HOP1: {e}")
        print("SUCCESS: Validator confirms HOP1 compliance.")

    def test_validator_detects_mro_violation(self):
        """
        Edge Case: Verify Validator catches MRO deviations.
        """
        class BadAgent: 
            pass
            
        with self.assertRaises(TypeError) as cm:
            CanonValidator._check_mro(BadAgent)
        self.assertIn("MRO Violation", str(cm.exception))
        print("SUCCESS: Validator caught MRO violation.")

    def test_validator_detects_open_seal(self):
        """
        Edge Case: Verify Validator catches agents that forgot to seal.
        """
        # Mock class that mimics LICAgentBase but forgets to seal
        class UnsealedAgent(HOP1ProfileAnalysisAgent):
            def __post_init__(self):
                # Skip the parent's __post_init__ which would seal the agent
                # Just call the grandparent to avoid seal engagement
                from apps_lic.shared.core.LICAgentBaseAgent import LICAgentBase
                LICAgentBase.__post_init__(self)
                
        try:
            # This should fail because the agent isn't sealed
            CanonValidator._check_seal_contract(UnsealedAgent)
            self.fail("Validator should have caught unsealed agent")
        except RuntimeError as e:
            self.assertIn("Sovereign Seal not engaged", str(e))
            
        print("SUCCESS: Validator caught Unsealed Agent (Simulated).")

if __name__ == "__main__":
    unittest.main()
