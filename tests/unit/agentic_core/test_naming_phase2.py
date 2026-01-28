import pytest
import re
from pathlib import Path

@pytest.fixture
def disable_path_shield(): return True

PROTECTED_SUBSTRINGS = ("Engine", "router", "Fusion", "Wrapper")
VERB_PATTERN = re.compile(r"^(Add|Collect|Phase|Sprint|Track|Guard)(?=[A-Z0-9])")

class TestPhase2Heuristics:
    def test_expanded_protection(self, disable_path_shield):
        """Ensure partial matches like 'ValidatorEngineZlm' are protected."""
        cases = [
            "CanonValidatorEngineZlm.py", "control_plane_judge_engine.py",
            "graphrag_fusion.py", "l5_autonomous_orchestrator_wrapper.py"
        ]
        for c in cases:
            assert any(s in c for s in PROTECTED_SUBSTRINGS), f"{c} should be protected"

    def test_expanded_verbs(self, disable_path_shield):
        """Ensure new verbs are caught."""
        cases = [
            "add_test_coverage.py", "collect_metrics.py", "Phase4Batch1.py",
            "Sprint4Phase2.py", "guard_no_inline_models.py"
        ]
        for c in cases:
            assert VERB_PATTERN.match(c), f"{c} should be flagged for rename"
