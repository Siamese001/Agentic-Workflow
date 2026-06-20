from importlib import import_module

_impl = import_module("tools.cert.compile_apps_e2e_signoff")
globals().update(
    {
        name: getattr(_impl, name)
        for name in dir(_impl)
        if not (name.startswith("__") and name.endswith("__"))
    }
)
main = _impl.main


if __name__ == "__main__":
    raise SystemExit(main())
