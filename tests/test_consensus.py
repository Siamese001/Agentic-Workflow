import pytest
from consensus_engine import ConsensusEngine

def test_unanimous_pass():
    """All Big Three reasoning models should agree on clean code."""
    jury = ConsensusEngine()
    artifact = "def calculate_sum(a, b): return a + b"
    result = jury.judge_artifact(artifact)
    assert result["status"] == "PASS"
    assert result["score"] == 1.0

def test_gpt_5_1_logic_catch():
    """GPT-5.1 catches a functional regression (infinite loop)."""
    jury = ConsensusEngine()
    artifact = "while True: pass # infinite loop risk"
    
    result = jury.judge_artifact(artifact)
    
    no_votes = [v for v in result["votes"] if v["verdict"] == "NO"]
    assert any("gpt-5.1" in v["model"] for v in no_votes)

def test_claude_sonnet_4_5_safety_catch():
    """Claude Sonnet 4.5 catches a safety issue (race condition)."""
    jury = ConsensusEngine()
    artifact = "global_var += 1 # possible race condition"
    
    result = jury.judge_artifact(artifact)
    
    no_votes = [v for v in result["votes"] if v["verdict"] == "NO"]
    assert any("claude-sonnet-4-5" in v["model"] for v in no_votes)

def test_gemini_3_pro_hallucination_catch():
    """Gemini 3 Pro catches a hallucination using Deep Think."""
    jury = ConsensusEngine()
    artifact = "import non_existent_lib # hallucination risk"
    
    result = jury.judge_artifact(artifact)
    
    no_votes = [v for v in result["votes"] if v["verdict"] == "NO"]
    assert any("gemini-3-pro" in v["model"] for v in no_votes)

def test_majority_fail_complex_bug():
    """
    Simulates a complex bug that triggers 2 out of 3 reasoning models.
    (e.g., Infinite Loop + Race Condition) -> FAIL
    """
    jury = ConsensusEngine()
    artifact = "while True: global_var += 1 # infinite loop and race condition"
    
    result = jury.judge_artifact(artifact)
    
    # Expected failure as GPT-5.1 and Sonnet 4.5 dissent.
    assert result["status"] == "FAIL"
    assert result["score"] < 0.66
