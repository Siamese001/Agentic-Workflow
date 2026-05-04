"""W5 T-suite — Provider / gateway governance tests (3 tests).

Verifies that apps_rg's prompt-assembly surface is correctly canonical:
1. rg_pa_compiler.py (W3 P6) re-exports the canonical surface cleanly.
2. No raw Anthropic client instantiation outside the governed PA path.
3. AbstainRecommendedError is raised when envelope.abstain_recommended is True
   (i.e. the PA compiler respects the abstain signal).

All tests are static source analysis or in-process module loading —
no live Anthropic API call required.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
PA_COMPILER = REPO_ROOT / "apps_rg" / "prompt_assembly" / "rg_pa_compiler.py"
ORIGINAL_ENTRYPOINT = REPO_ROOT / "apps_rg" / "utils" / "anthropic_rag_entrypoint.py"
APPS_RG_DIR = REPO_ROOT / "apps_rg"


# ---------------------------------------------------------------------------
# Test 1: rg_pa_compiler.py exports the canonical PA surface
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_rg_pa_compiler_exports_canonical_surface() -> None:
    """rg_pa_compiler.py must re-export AbstainRecommendedError, AnthropicRagPayload,
    and build_anthropic_rag_payload (W3 P6)."""
    assert PA_COMPILER.exists(), (
        f"rg_pa_compiler.py not found at {PA_COMPILER}. W3 P6 required."
    )
    src = PA_COMPILER.read_text(encoding="utf-8")

    required = [
        "AbstainRecommendedError",
        "AnthropicRagPayload",
        "build_anthropic_rag_payload",
    ]
    missing = [r for r in required if r not in src]
    assert not missing, (
        f"rg_pa_compiler.py is missing re-exports: {missing}. "
        "W3 P6 requires re-exporting all three canonical PA names."
    )

    # Must import FROM the original module (compat wrapper, not reimplementation)
    assert "from apps_rg.utils.anthropic_rag_entrypoint import" in src, (
        "rg_pa_compiler.py must import from apps_rg.utils.anthropic_rag_entrypoint "
        "(compat wrapper — do not reimplement the PA logic here)."
    )


# ---------------------------------------------------------------------------
# Test 2: No raw anthropic.Anthropic() instantiation outside PA path
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_rg_no_raw_anthropic_client_outside_pa() -> None:
    """apps_rg must not instantiate anthropic.Anthropic() outside the governed PA path."""
    allowed_files = {
        "anthropic_rag_entrypoint.py",
        "rg_pa_compiler.py",
    }
    violations = []
    for py_file in APPS_RG_DIR.rglob("*.py"):
        if py_file.name in allowed_files:
            continue
        src = py_file.read_text(encoding="utf-8")
        if "anthropic.Anthropic()" in src or "Anthropic(api_key" in src:
            violations.append(str(py_file.relative_to(REPO_ROOT)))

    assert not violations, (
        f"Raw Anthropic client instantiation found outside the governed PA path: "
        f"{violations}. All Anthropic calls must go through "
        f"build_anthropic_rag_payload (rg_pa_compiler / anthropic_rag_entrypoint)."
    )


# ---------------------------------------------------------------------------
# Test 3: AbstainRecommendedError raised when envelope.abstain_recommended=True
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_rg_pa_compiler_raises_abstain_on_weak_evidence() -> None:
    """build_anthropic_rag_payload must raise AbstainRecommendedError when
    envelope.abstain_recommended is True."""
    assert ORIGINAL_ENTRYPOINT.exists(), (
        f"anthropic_rag_entrypoint.py not found: {ORIGINAL_ENTRYPOINT}"
    )

    # Load the module
    spec = importlib.util.spec_from_file_location(
        "anthropic_rag_entrypoint", ORIGINAL_ENTRYPOINT
    )
    assert spec and spec.loader

    # Import dependencies first — if agentic_core isn't importable, skip gracefully
    try:
        import sys  # noqa: PLC0415
        if str(REPO_ROOT) not in sys.path:
            sys.path.insert(0, str(REPO_ROOT))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
    except ImportError as exc:
        pytest.skip(
            f"Cannot import anthropic_rag_entrypoint dependencies: {exc}. "
            "Run with full agentic_core installed."
        )

    # Construct a minimal stub envelope with abstain_recommended=True
    class _StubEnvelope:
        envelope_id = "test-envelope-001"
        abstain_recommended = True
        contradiction_status = "CONTRADICTED"

    with pytest.raises(mod.AbstainRecommendedError):
        mod.build_anthropic_rag_payload(
            _StubEnvelope(),
            query="test query",
        )
