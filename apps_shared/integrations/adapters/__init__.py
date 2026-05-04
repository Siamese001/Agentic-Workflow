"""apps_shared.adapters \u2014 single boundary facade layer for cross-tree dependencies.

Modules in this package centralize controlled cross-boundary imports so that:

- The ADG records ONE ``apps_shared.integrations.adapters.* \u2192 <peer>`` edge per facade,
  instead of N edges scattered across app code.
- Refactoring the upstream peer (system_learning, apps_rg, ...) becomes a
  single-file change at the facade boundary.
- Apps must explicitly opt in to a facade; the dependency is documented here
  rather than buried in deep app modules.

Each facade module uses PEP 562 ``__getattr__`` to lazily resolve symbols on
first access so that environments without the upstream peer installed can
still import the facade without ``ImportError`` at module load time. The
original lazy-import semantics from the pre-refactor call sites are preserved.

Plan: ``.windsurf/plans/apps-runtime-first-principles-e6ba58.md`` W3.
"""
