"""L6 observability utils — regular package (added 2026-05-02 per deferred-scope-closeout-2026-05-02-e4f8a1 W3).

Converts this directory from an implicit namespace package to a regular package.
This matches the convention used by sibling directories (enforcement/, execution/,
reasoning/, runtime_trace/, semconv/, shadow_eval/, types/) — all of which have
__init__.py.

Motivation: pytest's --import-mode=importlib mode interacts poorly with implicit
namespace packages when a leaf module is a re-export shim. Real consumer tests
pass either way; scaffold tests that do ``importlib.import_module(leaf_path)``
fail with ModuleNotFoundError in the namespace-package configuration. Adding
__init__.py makes the import path unambiguous.
"""
