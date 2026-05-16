"""Guard: generic bindings subtree must stay free of direct apps_* imports."""

from __future__ import annotations

from agentic_core.runtime.bindings.app_binding_validation import scan_generic_bindings_tree_for_apps_imports


def test_no_apps_specific_imports_under_runtime_bindings() -> None:
    hits = scan_generic_bindings_tree_for_apps_imports()
    assert hits == [], "; ".join(hits)
