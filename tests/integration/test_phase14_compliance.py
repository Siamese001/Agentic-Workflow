"""
Phase 14 Compliance Test

Verifies that forbidden imports are physically removed from Phase 14 targets.
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent


def test_imports_purged():
    """Verify that forbidden imports are physically removed from Phase 14 targets."""

    targets = [
        "agentic_core/L3_orchestration/workflow_engines/FissionManagerAgent.py",
        "agentic_core/L5_safety/guardrails/HallucinationHunterAgent.py",
        "agentic_core/L3_orchestration/fission_logic/subatomic_engine.py",
    ]

    forbidden = ["import google.genai", "from google import genai", "from google.genai"]

    for rel_path in targets:
        full_path = PROJECT_ROOT / rel_path
        assert full_path.exists(), f"File missing: {rel_path}"

        content = full_path.read_text(encoding="utf-8")
        for term in forbidden:
            assert term not in content, f"FAILED: {rel_path} still contains '{term}'"


def test_gateway_usage():
    """Verify that targets now import the Gateway."""

    # SubAtomic check
    path = PROJECT_ROOT / "agentic_core/L3_orchestration/fission_logic/subatomic_engine.py"
    content = path.read_text(encoding="utf-8")
    assert "SovereignLLMGateway" in content or "get_llm_gateway" in content

    # Fission check
    path = PROJECT_ROOT / "agentic_core/L3_orchestration/workflow_engines/FissionManagerAgent.py"
    content = path.read_text(encoding="utf-8")
    assert "SovereignBaseAgent" in content
    assert "llm_generate" in content
