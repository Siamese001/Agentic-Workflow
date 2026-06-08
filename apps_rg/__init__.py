"""apps_rg package."""
from __future__ import annotations

__version__ = "0.1.0"


def _autoload_dotenv() -> None:
    """Load the repo-root ``.env`` once, on package import, for every real invocation.

    Why: credential loading used to be per-entry-point opt-in — each path (CLI main, the
    judge LLM client, the external provider) had to remember to call
    ``bootstrap_apps_rg_env()``. Any path that read an API key before bootstrapping saw an
    empty ``os.environ`` and reported BLOCKED even though ``.env`` held the key. Loading here
    makes credentials available to *every* entry point (CLI, lanes, judges, ad-hoc imports).

    Skipped under pytest (and ``APPS_RG_TEST_HARNESS``) so the unit/contract suite never picks
    up real API keys. ``bootstrap_apps_rg_env`` uses ``override=False``, so an explicitly
    exported shell credential still wins. Disable with ``APPS_RG_SKIP_DOTENV_AUTOLOAD=1``.
    """
    import os
    import sys

    if "pytest" in sys.modules:
        return
    if os.environ.get("APPS_RG_TEST_HARNESS"):
        return
    if os.environ.get("APPS_RG_SKIP_DOTENV_AUTOLOAD"):
        return
    try:
        from apps_rg.runtime.env_bootstrap import bootstrap_apps_rg_env

        bootstrap_apps_rg_env()
    except Exception:  # noqa: BLE001  # guardian: allow-broad-exception -- .env autoload is best-effort and must never break `import apps_rg`
        pass


_autoload_dotenv()
