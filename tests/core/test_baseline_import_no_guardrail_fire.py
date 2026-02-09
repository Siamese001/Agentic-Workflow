"""Baseline import surface test: importing top-level packages must NOT trigger
guardrail ImportErrors even when infra deps are missing.

The guardrails wrap optional infra packages with try/except ImportError that
re-raise with an actionable message.  The key invariant is that importing
``agentic_core`` or ``apps_shared`` at the *package* level never triggers
those guardrails — the guarded modules are only reached via explicit
sub-module imports.

This test proves that invariant by importing the two top-level packages
and asserting no ImportError is raised.
"""

from __future__ import annotations


class TestBaselineImportSurface:
    def test_import_agentic_core(self):
        """Importing agentic_core must succeed without infra deps."""
        import agentic_core  # noqa: F401

    def test_import_apps_shared(self):
        """Importing apps_shared must succeed without infra deps."""
        import apps_shared  # noqa: F401

    def test_import_apps_lic(self):
        """Importing apps_lic must succeed without infra deps."""
        import apps_lic  # noqa: F401

    def test_import_apps_rg(self):
        """Importing apps_rg must succeed without infra deps."""
        import apps_rg  # noqa: F401
