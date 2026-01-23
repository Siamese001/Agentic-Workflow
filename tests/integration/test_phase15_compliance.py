"""
Phase 15 Compliance Test

Verifies L2Base and CDA are free of google.genai.
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent


def test_phase15_imports_purged():
    """Verify L2Base and CDA are free of google.genai."""

    targets = [
        "agentic_core/L2_execution/L2ExecutionBaseAgent.py",
        "agentic_core/L5_safety/validators/CognitiveDispositionAgent.py",
    ]

    forbidden = ["google.genai", "import genai", "from google"]

    for rel_path in targets:
        full_path = PROJECT_ROOT / rel_path
        assert full_path.exists(), f"File missing: {rel_path}"

        content = full_path.read_text(encoding="utf-8")
        for term in forbidden:
            assert term not in content, f"FAILED: {rel_path} still contains '{term}'"


def test_phase15_gateway_usage():
    """Verify Native Capabilities are used."""

    l2_path = PROJECT_ROOT / "agentic_core/L2_execution/L2ExecutionBaseAgent.py"
    l2_content = l2_path.read_text(encoding="utf-8")
    assert "SovereignBaseAgent" in l2_content
    assert "RedisCacheMixin" in l2_content

    cda_path = PROJECT_ROOT / "agentic_core/L5_safety/validators/CognitiveDispositionAgent.py"
    cda_content = cda_path.read_text(encoding="utf-8")
    assert "llm_generate" in cda_content
    assert "cache_get" in cda_content
