"""W3 c0-policy-rectification-deferred-f7b2a9 — Entrypoint C0 bypass audit tests.

Verifies that R4-like entrypoints use typed C0 bypass reasons, not hardcoded
legacy strings like "GROUNDING_NOT_REQUIRED".

Test categories:
1. integrated_r4_lic_pipeline_run uses BYPASS_PRELOADED_CONTEXT
2. integrated_safe_reuse_run uses BYPASS_CACHE_RETURN
3. No hardcoded GROUNDING_NOT_REQUIRED in entrypoints
4. All bypass reasons are in ALLOWED_C0_BYPASS_REASONS
"""

from __future__ import annotations

import ast
import inspect
import re
from pathlib import Path

import pytest

from agentic_core.runtime.contracts.c0_bypass_receipt import (
    ALLOWED_C0_BYPASS_REASONS,
    build_c0_bypass_receipt,
)


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def typed_bypass_reasons() -> frozenset[str]:
    """Typed bypass reasons (preferred over legacy)."""
    return frozenset({
        "BYPASS_PRELOADED_CONTEXT",
        "BYPASS_CACHE_RETURN",
        "BYPASS_FALLBACK",
        "NOT_REQUIRED",
    })


@pytest.fixture
def legacy_bypass_reasons() -> frozenset[str]:
    """Legacy bypass reasons (deprecated but still allowed for compatibility)."""
    return frozenset({
        "GROUNDING_NOT_REQUIRED",
        "TERMINAL_SHORTCIRCUIT_NO_RETRIEVAL",
        "CACHE_REUSE_PRIOR_EVIDENCE",
        "FALLBACK_NO_RETRIEVAL",
    })


# =============================================================================
# Test Category 1-2: Entrypoints use typed bypass reasons
# =============================================================================


class TestEntrypointC0BypassReasons:
    """R4-like entrypoints use typed C0 bypass reasons."""

    def test_allowed_bypass_reasons_include_typed(self, typed_bypass_reasons):
        """ALLOWED_C0_BYPASS_REASONS includes all typed bypass reasons."""
        for reason in typed_bypass_reasons:
            assert reason in ALLOWED_C0_BYPASS_REASONS, (
                f"Typed bypass reason '{reason}' not in ALLOWED_C0_BYPASS_REASONS"
            )

    def test_no_grounding_not_required_in_codebase(self):
        """Hardcoded GROUNDING_NOT_REQUIRED string not found in entrypoints."""
        # Check that the legacy string isn't hardcoded in entrypoint files
        entrypoints_dir = Path(__file__).parent.parent.parent.parent / "agentic_core" / "runtime" / "entrypoints"

        hardcoded_pattern = re.compile(r'c0_bypass_reason\s*=\s*"GROUNDING_NOT_REQUIRED"')

        issues = []
        for py_file in entrypoints_dir.glob("*.py"):
            content = py_file.read_text()
            if hardcoded_pattern.search(content):
                issues.append(f"{py_file.name}: hardcoded GROUNDING_NOT_REQUIRED")

        assert not issues, f"Found hardcoded legacy bypass reasons: {issues}"

    def test_entrypoints_use_typed_bypass_or_variable(self):
        """Entrypoints use typed bypass reasons or variable references."""
        # Read the entrypoint files and verify they use typed reasons
        entrypoints_dir = Path(__file__).parent.parent.parent.parent / "agentic_core" / "runtime" / "entrypoints"

        # These are the known-good typed reasons we expect
        typed_reasons = {
            "BYPASS_PRELOADED_CONTEXT",
            "BYPASS_CACHE_RETURN",
            "BYPASS_FALLBACK",
            "NOT_REQUIRED",
        }

        issues = []
        for py_file in entrypoints_dir.glob("integrated_*.py"):
            content = py_file.read_text()

            # Find all c0_bypass_reason assignments
            pattern = re.compile(r'c0_bypass_reason\s*=\s*"([^"]+)"')
            matches = pattern.findall(content)

            for reason in matches:
                if reason not in typed_reasons and reason not in ALLOWED_C0_BYPASS_REASONS:
                    issues.append(f"{py_file.name}: unknown reason '{reason}'")

        assert not issues, f"Found unknown bypass reasons: {issues}"


# =============================================================================
# Test Category 3-4: Verify specific entrypoint files
# =============================================================================


class TestSpecificEntrypoints:
    """Verify specific entrypoint files use correct bypass reasons."""

    def test_r4_lic_uses_preloaded_context(self):
        """integrated_r4_lic_pipeline_run uses BYPASS_PRELOADED_CONTEXT."""
        entrypoints_dir = Path(__file__).parent.parent.parent.parent / "agentic_core" / "runtime" / "entrypoints"
        file_path = entrypoints_dir / "integrated_r4_lic_pipeline_run.py"

        if not file_path.exists():
            pytest.skip("integrated_r4_lic_pipeline_run.py not found")

        content = file_path.read_text()

        # Should have BYPASS_PRELOADED_CONTEXT
        assert 'c0_bypass_reason="BYPASS_PRELOADED_CONTEXT"' in content, (
            "integrated_r4_lic_pipeline_run should use BYPASS_PRELOADED_CONTEXT"
        )

        # Should NOT have legacy GROUNDING_NOT_REQUIRED
        assert 'c0_bypass_reason="GROUNDING_NOT_REQUIRED"' not in content, (
            "integrated_r4_lic_pipeline_run should not use legacy GROUNDING_NOT_REQUIRED"
        )

    def test_safe_reuse_uses_cache_return(self):
        """integrated_safe_reuse_run uses BYPASS_CACHE_RETURN."""
        entrypoints_dir = Path(__file__).parent.parent.parent.parent / "agentic_core" / "runtime" / "entrypoints"
        file_path = entrypoints_dir / "integrated_safe_reuse_run.py"

        if not file_path.exists():
            pytest.skip("integrated_safe_reuse_run.py not found")

        content = file_path.read_text()

        # Should have BYPASS_CACHE_RETURN
        assert 'c0_bypass_reason="BYPASS_CACHE_RETURN"' in content, (
            "integrated_safe_reuse_run should use BYPASS_CACHE_RETURN"
        )

        # Should NOT have legacy CACHE_REUSE_PRIOR_EVIDENCE
        # Note: W3 should have updated this to BYPASS_CACHE_RETURN
        assert 'c0_bypass_reason="CACHE_REUSE_PRIOR_EVIDENCE"' not in content, (
            "integrated_safe_reuse_run should use BYPASS_CACHE_RETURN, not CACHE_REUSE_PRIOR_EVIDENCE"
        )


# =============================================================================
# Test Category 5: build_c0_bypass_receipt contract
# =============================================================================


class TestC0BypassReceiptContract:
    """build_c0_bypass_receipt enforces typed bypass reasons."""

    def test_build_c0_bypass_receipt_accepts_typed_reason(self):
        """build_c0_bypass_receipt accepts typed bypass reasons."""
        receipt = build_c0_bypass_receipt(
            run_id="run-001",
            request_id="req-001",
            trace_root="trace-001",
            route_contract_id="route-001",
            route_id="R4_SINGLE_ACTION",
            c0_bypass_reason="BYPASS_PRELOADED_CONTEXT",
            preloaded_context_ref="preload-001",
        )

        assert receipt.c0_bypass_reason == "BYPASS_PRELOADED_CONTEXT"
        assert receipt.preloaded_context_ref == "preload-001"

    def test_build_c0_bypass_receipt_accepts_cache_return(self):
        """build_c0_bypass_receipt accepts BYPASS_CACHE_RETURN."""
        receipt = build_c0_bypass_receipt(
            run_id="run-001",
            request_id="req-001",
            trace_root="trace-001",
            route_contract_id="route-001",
            route_id="R1B_SEMANTIC_CACHE",
            c0_bypass_reason="BYPASS_CACHE_RETURN",
        )

        assert receipt.c0_bypass_reason == "BYPASS_CACHE_RETURN"

    def test_build_c0_bypass_receipt_accepts_legacy_reasons(self):
        """build_c0_bypass_receipt still accepts legacy reasons (backward compat)."""
        # Legacy reasons are still in ALLOWED_C0_BYPASS_REASONS for transition period
        receipt = build_c0_bypass_receipt(
            run_id="run-001",
            request_id="req-001",
            trace_root="trace-001",
            route_contract_id="route-001",
            route_id="R1_TERMINAL",
            c0_bypass_reason="TERMINAL_SHORTCIRCUIT_NO_RETRIEVAL",  # Legacy
        )

        assert receipt.c0_bypass_reason == "TERMINAL_SHORTCIRCUIT_NO_RETRIEVAL"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
