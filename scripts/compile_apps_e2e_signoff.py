from importlib import import_module
import sys

_impl = import_module("tools.cert.compile_apps_e2e_signoff")

if __name__ != "__main__":
    sys.modules[__name__] = _impl
else:
    raise SystemExit(_impl.main())
