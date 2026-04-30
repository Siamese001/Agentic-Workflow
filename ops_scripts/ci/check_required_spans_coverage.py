#!/usr/bin/env python3
"""Required-spans coverage gate — Layer 3 of apps_* OTEL strategy.

Loads ``config/observability/required_spans.yaml`` and verifies that
every listed method carries the ``__adg_traces_execute__`` marker
populated by ``@traces_execute`` (see ADR-075). The gate inspects the
decorated functions via import — it does not run the engines.

Failure modes flagged:
  * Manifest lists ``Engine.method`` but no class with that name and a
    ``traces_execute``-marked method exists in the app's engines/.
  * Module containing the manifest target raises ImportError (likely a
    real bug, since L1 + L2 gates passed).
  * Manifest YAML is malformed.

Plan: .windsurf/plans/apps-svp-plus-hardening-7c4e3a.md (P4 NEXT_STEP)
"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import Iterable

import yaml

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "config" / "observability" / "required_spans.yaml"

# Ensure repo root is on sys.path so apps_* / agentic_core resolve when
# this script is invoked directly (not via `python -m`).
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


def _load_manifest() -> dict[str, dict[str, list[str]]]:
    with MANIFEST.open(encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise SystemExit(f"manifest is not a mapping: {MANIFEST}")
    return data


def _candidate_modules(app: str) -> list[str]:
    """Return dotted module ids in `<app>/engines/`."""
    out: list[str] = []
    d = REPO / app / "engines"
    if not d.is_dir():
        return out
    for f in sorted(d.glob("*.py")):
        if f.name.startswith(("_", ".")) or f.name == "__init__.py":
            continue
        out.append(f"{app}.engines.{f.stem}")
    return out


def _collect_decorated_qualnames(modules: Iterable[str]) -> set[str]:
    """Return the set of ``ClassName.method`` strings that carry the
    ``__adg_traces_execute__`` marker across the given modules.

    Uses ``vars(cls)`` rather than ``getattr(cls, attr)`` to avoid
    invoking descriptors / Pydantic field machinery that can throw
    DeprecationWarnings or recursion. The marker is set directly on the
    function object inside the class ``__dict__``, so vars() is the
    canonical lookup.
    """
    found: set[str] = set()
    for mod_id in modules:
        try:
            mod = importlib.import_module(mod_id)
        except ImportError:
            # Heavy-deps modules can fail import in some envs; skip rather
            # than fail. The L2 runtime probe also tolerates this.
            continue

        for name in dir(mod):
            try:
                obj = getattr(mod, name, None)
            except Exception:  # noqa: BLE001 — getattr can raise on dynamic descriptors
                continue
            if not isinstance(obj, type):
                continue
            cls_vars = vars(obj)
            for attr_name, attr in cls_vars.items():
                marker = getattr(attr, "__adg_traces_execute__", None)
                if marker:
                    for qual in marker:
                        found.add(qual)
                        parts = qual.split(".")
                        if len(parts) >= 2:
                            found.add(".".join(parts[-2:]))
    return found


def main() -> int:
    manifest = _load_manifest()
    print("[B_required_spans] verifying Layer 3 contract")
    failures: list[str] = []
    total = 0
    for app, spec in manifest.items():
        if not isinstance(spec, dict):
            failures.append(f"{app}: malformed manifest entry (expected mapping)")
            continue
        required = spec.get("required_spans") or []
        if not required:
            print(f"  {app:<24} (no required_spans declared)")
            continue
        modules = _candidate_modules(app)
        decorated = _collect_decorated_qualnames(modules)
        ok = 0
        for span in required:
            total += 1
            if span in decorated:
                ok += 1
            else:
                failures.append(f"{app}: required span '{span}' has no @traces_execute marker")
        print(f"  {app:<24} {ok}/{len(required)}")

    if failures:
        print(f"\n[B_required_spans] tier=B status=fail violations={len(failures)} total={total}")
        for f in failures[:30]:
            print(f"  {f}")
        if len(failures) > 30:
            print(f"  ... and {len(failures) - 30} more")
        print(
            "\n  Remediation: either add `@traces_execute(layer=...)` to the\n"
            "  named method, OR remove the entry from required_spans.yaml\n"
            "  (the latter requires Author-Gate approval — removing a row is\n"
            "  a breaking observability contract change)."
        )
        return 1

    print(f"\n[B_required_spans] tier=B status=pass coverage={total}/{total} (100%)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
