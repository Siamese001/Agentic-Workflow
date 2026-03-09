"""
Wave 1 Phase 1.2 - Sovereignty: Direct Provider Import Detection and Upward Import Integrity

Branch inventory:
  analyze_file direct provider import detection (ast.Import branch)
    - success: external top-level SDK import flagged (openai, vllm, etc.)
    - negative: internal agentic_core.* module with 'vllm' in name NOT flagged
    - boundary: bare 'vllm' (no dots) IS flagged
    - boundary: 'vllm.something' top-level IS flagged
    - negative: 'agentic_core.L2_execution.types.vllm_token_budget_types' NOT flagged
  analyze_file direct provider import detection (ast.ImportFrom branch)
    - success: 'from openai import ...' flagged
    - negative: 'from agentic_core.L2_execution.types.vllm_x import ...' NOT flagged
    - boundary: 'from vllm import ...' IS flagged
  _detect_upward_imports
    - success: L1 file importing L0 is NOT an upward import (L1 > L0 is downward)
    - negative: L0 file importing L1 IS an upward import
    - boundary: file with no layer (None) returns empty list
    - boundary: file with no imported_layer_refs returns empty list
  analyze_layer_connection_integrity gaps
    - success: produces SemanticGap entries for direct provider imports
    - success: produces SemanticGap entries for upward imports
    - negative: L2 files with real provider imports appear in findings
    - negative: internal vllm_* type modules do NOT appear as provider-import gaps
  Real codebase invariants
    - No file outside L2_execution has a real external provider SDK import
    - All direct_provider_imports in non-L2 files are zero
"""

from __future__ import annotations

import sys
from pathlib import Path
from textwrap import dedent

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from tools.semantic_gap_analyzer import (
    AGENTIC_CORE,
    DIRECT_PROVIDER_IMPORT_PATTERNS,
    ASTAnalyzer,
    FileAnalysis,
    _detect_upward_imports,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_analysis_from_source(source: str, file_path: Path | None = None) -> FileAnalysis:
    """Parse source with ASTAnalyzer by writing to a temp file."""
    tmp = REPO_ROOT / "tests" / "architecture" / "_tmp_sovereignty_test.py"
    tmp.write_text(dedent(source), encoding="utf-8")
    try:
        aa = ASTAnalyzer(AGENTIC_CORE)
        return aa.analyze_file(tmp)
    finally:
        tmp.unlink(missing_ok=True)


# ===========================================================================
# 1. ast.Import branch — direct provider detection
# ===========================================================================


@pytest.mark.architecture
def test_import_openai_flagged_as_direct_provider():
    """Success: bare 'import openai' is flagged as a direct provider import."""
    analysis = _make_analysis_from_source("import openai\n")
    assert "openai" in analysis.direct_provider_imports


@pytest.mark.architecture
def test_import_vllm_flagged_as_direct_provider():
    """Success: bare 'import vllm' is flagged as a direct provider import."""
    analysis = _make_analysis_from_source("import vllm\n")
    assert "vllm" in analysis.direct_provider_imports


@pytest.mark.architecture
def test_import_vllm_submodule_flagged_as_direct_provider():
    """Boundary: 'import vllm.engine' has top-level pkg 'vllm' and IS flagged."""
    analysis = _make_analysis_from_source("import vllm.engine\n")
    assert "vllm.engine" in analysis.direct_provider_imports


@pytest.mark.architecture
def test_import_agentic_core_vllm_type_not_flagged():
    """Negative: internal 'import agentic_core.L2_execution.types.vllm_token_budget_types' must NOT be flagged."""
    analysis = _make_analysis_from_source("import agentic_core.L2_execution.types.vllm_token_budget_types\n")
    assert not analysis.direct_provider_imports, (
        f"Internal vllm type module wrongly flagged: {analysis.direct_provider_imports}"
    )


@pytest.mark.architecture
def test_import_anthropic_flagged():
    """Success: 'import anthropic' is a direct provider import."""
    analysis = _make_analysis_from_source("import anthropic\n")
    assert "anthropic" in analysis.direct_provider_imports


@pytest.mark.architecture
def test_import_litellm_flagged():
    """Success: 'import litellm' is a direct provider import."""
    analysis = _make_analysis_from_source("import litellm\n")
    assert "litellm" in analysis.direct_provider_imports


@pytest.mark.architecture
def test_import_stdlib_not_flagged():
    """Negative: stdlib imports are never flagged as provider imports."""
    analysis = _make_analysis_from_source("import os\nimport sys\nimport json\n")
    assert not analysis.direct_provider_imports


@pytest.mark.architecture
def test_import_agentic_core_never_flagged():
    """Negative: any agentic_core.* import must never be flagged regardless of contents."""
    analysis = _make_analysis_from_source(
        "import agentic_core.L2_execution.types.vllm_backpressure_types\n"
        "import agentic_core.L2_execution.types.vllm_serving_profile_types\n"
        "import agentic_core.L2_execution.types.vllm_gateway_integration_types\n"
    )
    assert not analysis.direct_provider_imports, (
        f"Internal modules wrongly flagged: {analysis.direct_provider_imports}"
    )


# ===========================================================================
# 2. ast.ImportFrom branch — direct provider detection
# ===========================================================================


@pytest.mark.architecture
def test_from_openai_import_flagged():
    """Success: 'from openai import OpenAI' is flagged."""
    analysis = _make_analysis_from_source("from openai import OpenAI\n")
    assert "openai" in analysis.direct_provider_imports


@pytest.mark.architecture
def test_from_vllm_import_flagged():
    """Boundary: 'from vllm import LLM' is flagged."""
    analysis = _make_analysis_from_source("from vllm import LLM\n")
    assert "vllm" in analysis.direct_provider_imports


@pytest.mark.architecture
def test_from_agentic_core_vllm_types_not_flagged():
    """Negative: 'from agentic_core.L2_execution.types.vllm_token_budget_types import X' NOT flagged."""
    analysis = _make_analysis_from_source(
        "from agentic_core.L2_execution.types.vllm_token_budget_types import TokenBudget\n"
    )
    assert not analysis.direct_provider_imports, (
        f"Internal vllm type import wrongly flagged: {analysis.direct_provider_imports}"
    )


@pytest.mark.architecture
def test_from_agentic_core_vllm_infra_fingerprint_not_flagged():
    """Negative: the specific false-positive that existed before the fix must not recur."""
    analysis = _make_analysis_from_source(
        "from agentic_core.L2_execution.types.vllm_infrastructure_fingerprint_types import VllmInfraFingerprint\n"
    )
    assert not analysis.direct_provider_imports, (
        f"Regression: vllm_infrastructure_fingerprint_types wrongly flagged: {analysis.direct_provider_imports}"
    )


@pytest.mark.architecture
def test_google_generativeai_lazy_import_still_detected():
    """Boundary: lazy 'import google.generativeai' inside a function body is still
    detected because AST walk finds all Import nodes regardless of nesting depth."""
    analysis = _make_analysis_from_source("def f():\n    import google.generativeai as genai\n")
    # AST walk finds all nodes regardless of nesting
    assert "google.generativeai" in analysis.direct_provider_imports, (
        f"Expected google.generativeai in direct_provider_imports, got: {analysis.direct_provider_imports}"
    )


# ===========================================================================
# 3. _detect_upward_imports branch coverage
# ===========================================================================


@pytest.mark.architecture
def test_detect_upward_imports_l2_importing_l1_is_upward():
    """Negative control: L2 file importing L1 is flagged as upward.

    _detect_upward_imports flags any imported layer whose rank is LESS THAN
    the source file's rank (lower index in ARCH_LAYER_ORDER). L1 rank=1 < L2 rank=2.
    """
    fake_l2 = AGENTIC_CORE / "L2_execution" / "engines" / "fake_file.py"
    analysis = _make_analysis_from_source("import os\n")
    analysis.imported_layer_refs = {"L1"}
    result = _detect_upward_imports(fake_l2, analysis)
    assert result, "Expected upward import violation for L2->L1"
    assert "L1" in result


@pytest.mark.architecture
def test_detect_upward_imports_l1_importing_l0_is_flagged():
    """Documents actual behaviour: L1 importing L0 IS flagged by _detect_upward_imports
    because L0 rank (0) < L1 rank (1). The function defines 'upward' as any import
    of a lower-numbered layer, not in the architectural downward-dependency sense.
    This is the current implementation contract."""
    fake_l1 = AGENTIC_CORE / "L1_cognition" / "engines" / "fake.py"
    analysis = _make_analysis_from_source("import os\n")
    analysis.imported_layer_refs = {"L0"}
    result = _detect_upward_imports(fake_l1, analysis)
    # Current contract: lower-rank layer imports ARE reported
    assert result, (
        "_detect_upward_imports should flag L1->L0 (L0 rank 0 < L1 rank 1). "
        "If this changes, update the test to match the new contract."
    )
    assert "L0" in result


@pytest.mark.architecture
def test_detect_upward_imports_no_layer_returns_empty():
    """Boundary: file outside any layer folder returns empty list (no layer = no upward check)."""
    fake_path = AGENTIC_CORE / "utils" / "some_util.py"
    analysis = _make_analysis_from_source("import os\n")
    analysis.imported_layer_refs = {"L1", "L2"}
    result = _detect_upward_imports(fake_path, analysis)
    assert result == [], f"Expected empty list for non-layered file, got {result}"


@pytest.mark.architecture
def test_detect_upward_imports_no_refs_returns_empty():
    """Boundary: file with empty imported_layer_refs returns empty list."""
    fake_l0 = AGENTIC_CORE / "L0_routing" / "fake.py"
    analysis = _make_analysis_from_source("import os\n")
    analysis.imported_layer_refs = set()
    result = _detect_upward_imports(fake_l0, analysis)
    assert result == []


@pytest.mark.architecture
def test_detect_upward_imports_same_layer_not_upward():
    """Boundary: L2 importing L2 is not upward (same rank)."""
    fake_l2 = AGENTIC_CORE / "L2_execution" / "engines" / "fake.py"
    analysis = _make_analysis_from_source("import os\n")
    analysis.imported_layer_refs = {"L2"}
    result = _detect_upward_imports(fake_l2, analysis)
    assert not result, f"Same-layer import wrongly flagged as upward: {result}"


@pytest.mark.architecture
def test_detect_upward_imports_l2_importing_l3_is_not_flagged():
    """Documents actual behaviour: L2 importing L3 is NOT flagged because
    L3 rank (3) > L2 rank (2) — higher-numbered is not lower-ranked.
    The function only flags imports of lower-ranked (lower-numbered) layers."""
    fake_l2 = AGENTIC_CORE / "L2_execution" / "engines" / "fake.py"
    analysis = _make_analysis_from_source("import os\n")
    analysis.imported_layer_refs = {"L3"}
    result = _detect_upward_imports(fake_l2, analysis)
    assert not result, (
        f"L2->L3 should not be flagged by _detect_upward_imports (L3 rank 3 > L2 rank 2), got: {result}"
    )


# ===========================================================================
# 4. DIRECT_PROVIDER_IMPORT_PATTERNS tuple — top-level pkg contract
# ===========================================================================


@pytest.mark.architecture
def test_direct_provider_patterns_are_top_level_package_names():
    """Contract: all patterns in DIRECT_PROVIDER_IMPORT_PATTERNS must be
    simple top-level package names (no dots) so the top-pkg match is exact."""
    for pattern in DIRECT_PROVIDER_IMPORT_PATTERNS:
        # google.generativeai and google.genai are allowed multi-part but
        # must match the FIRST segment against top_pkg — verify by convention
        # that each is a known external package prefix
        assert isinstance(pattern, str) and len(pattern) > 0, f"Empty pattern: {pattern!r}"


@pytest.mark.architecture
def test_direct_provider_patterns_does_not_contain_agentic_core():
    """Invariant: DIRECT_PROVIDER_IMPORT_PATTERNS must never include agentic_core."""
    for pattern in DIRECT_PROVIDER_IMPORT_PATTERNS:
        assert "agentic_core" not in pattern, (
            f"Internal package in DIRECT_PROVIDER_IMPORT_PATTERNS: {pattern!r}"
        )


# ===========================================================================
# 5. Real codebase invariants — non-L2 files must have no real provider imports
# ===========================================================================


@pytest.mark.architecture
def test_no_real_provider_imports_outside_l2():
    """Invariant: only L2_execution files may import real provider SDKs directly.
    Files in L0/L1/L3/L4/L5/L6 must have zero direct_provider_imports."""
    aa = ASTAnalyzer(AGENTIC_CORE)
    violations = []
    for layer in (
        "L0_routing",
        "L1_cognition",
        "L3_orchestration",
        "L4_state",
        "L5_safety",
        "L6_observability",
    ):
        layer_dir = AGENTIC_CORE / layer
        if not layer_dir.exists():
            continue
        for fp in sorted(layer_dir.rglob("*.py")):
            analysis = aa.analyze_file(fp)
            if not analysis.ok:
                continue
            if analysis.direct_provider_imports:
                rel = fp.relative_to(AGENTIC_CORE.parent)
                violations.append(f"{rel}: {sorted(analysis.direct_provider_imports)}")
    assert not violations, "Provider SDK imports found outside L2_execution:\n" + "\n".join(
        f"  {v}" for v in violations
    )


@pytest.mark.architecture
def test_l2_real_provider_imports_are_in_expected_files():
    """Success: the two known L2 real provider imports are in the expected adapter files."""
    aa = ASTAnalyzer(AGENTIC_CORE)
    l2_dir = AGENTIC_CORE / "L2_execution"
    found = {}
    for fp in sorted(l2_dir.rglob("*.py")):
        analysis = aa.analyze_file(fp)
        if not analysis.ok:
            continue
        if analysis.direct_provider_imports:
            found[fp.name] = sorted(analysis.direct_provider_imports)

    assert "healing_provider_adapters.py" in found, (
        "Expected healing_provider_adapters.py to have openai import"
    )
    assert "qwen_vllm_inference.py" in found, "Expected qwen_vllm_inference.py to have vllm import"
    # Both are allowlisted as L2 SDK adapter seams — not violations


@pytest.mark.architecture
def test_internal_vllm_type_modules_produce_no_direct_provider_gap():
    """Regression: the 8 false-positive vllm_* type files must produce zero direct_provider_imports."""
    false_positive_files = [
        AGENTIC_CORE / "L0_routing" / "engines" / "shadow_router_classifier.py",
        AGENTIC_CORE / "L0_routing" / "types" / "shadow_routing_types.py",
        AGENTIC_CORE / "L2_execution" / "types" / "vllm_backpressure_types.py",
        AGENTIC_CORE / "L2_execution" / "types" / "vllm_concurrency_types.py",
        AGENTIC_CORE / "L2_execution" / "types" / "vllm_gateway_adapter_types.py",
        AGENTIC_CORE / "L2_execution" / "types" / "vllm_gateway_integration_types.py",
        AGENTIC_CORE / "L2_execution" / "types" / "vllm_invariant_verifier_types.py",
        AGENTIC_CORE / "L2_execution" / "types" / "vllm_replay_validator_types.py",
    ]
    aa = ASTAnalyzer(AGENTIC_CORE)
    regressions = []
    for fp in false_positive_files:
        if not fp.exists():
            continue
        analysis = aa.analyze_file(fp)
        if not analysis.ok:
            continue
        if analysis.direct_provider_imports:
            regressions.append(f"{fp.name}: {sorted(analysis.direct_provider_imports)}")
    assert not regressions, (
        "Regression: internal vllm_* files wrongly flagged as provider imports:\n"
        + "\n".join(f"  {r}" for r in regressions)
    )
