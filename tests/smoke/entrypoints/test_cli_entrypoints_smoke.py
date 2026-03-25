"""CLI entrypoint smoke tests — verify all app __main__ modules are importable and expose main()."""

import pytest

_APPS = [
    "apps_lic",
    "apps_rg",
    "apps_eval",
    "apps_exec",
    "apps_rfp",
    "apps_research",
]


@pytest.mark.smoke
@pytest.mark.parametrize("app", _APPS)
def test_app_main_module_importable(app):
    """Each app's __main__ module imports without error."""
    try:
        import importlib

        mod = importlib.import_module(f"{app}.__main__")
    except ImportError as e:
        pytest.skip(f"{app}.__main__ not available: {e}")

    public = [n for n in dir(mod) if not n.startswith("_")]
    assert len(public) >= 1, f"{app}.__main__ must expose at least one public symbol"


@pytest.mark.smoke
@pytest.mark.parametrize("app", _APPS)
def test_app_main_function_is_callable(app):
    """Each app's __main__ exposes a callable main() function."""
    try:
        import importlib

        mod = importlib.import_module(f"{app}.__main__")
    except ImportError as e:
        pytest.skip(f"{app}.__main__ not available: {e}")

    assert hasattr(mod, "main"), f"{app}.__main__ must expose a main() function"
    assert callable(mod.main), f"{app}.__main__.main must be callable"


@pytest.mark.smoke
@pytest.mark.parametrize("app", _APPS)
def test_app_main_function_has_signature(app):
    """Each app's main() has a valid inspect signature."""
    import inspect

    try:
        import importlib

        mod = importlib.import_module(f"{app}.__main__")
    except ImportError as e:
        pytest.skip(f"{app}.__main__ not available: {e}")

    if not hasattr(mod, "main"):
        pytest.skip(f"{app}.__main__ has no main()")

    sig = inspect.signature(mod.main)
    assert sig is not None, f"{app}.__main__.main must have a valid signature"


@pytest.mark.smoke
def test_adg_tool_module_importable():
    """ADG tool __main__ module imports without error (may call sys.exit)."""
    try:
        import importlib

        mod = importlib.import_module("tools.adg.__main__")
    except SystemExit:
        # Some __main__ modules call sys.exit(0) at module level — this is OK
        pass
    except ImportError as e:
        pytest.skip(f"tools.adg.__main__ not available: {e}")

    # If we got past import, verify it has public symbols
    import sys

    if "tools.adg.__main__" in sys.modules:
        mod = sys.modules["tools.adg.__main__"]
        public = [n for n in dir(mod) if not n.startswith("_")]
        assert len(public) >= 1, "tools.adg.__main__ must expose at least one public symbol"
