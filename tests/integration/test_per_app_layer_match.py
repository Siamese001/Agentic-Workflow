"""Per-app layer-match validation — closes the L2↔L3 loop end-to-end.

For every manifest entry, asserts that the actual class.method's
``__adg_traces_layer__`` attribute matches the layer declared in
``required_spans.yaml``. This is parametric per-method (not just one
synthetic test), so each apps_* method is independently verified.

Plan: docs/archive/windsurf/legacy-tree/plans/apps-svp-plus-hardening-7c4e3a.md (P4 NEXT_STEP)
"""
from __future__ import annotations

import importlib
import sys
import unittest
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


def _load_manifest() -> dict:
    p = REPO / "config" / "observability" / "required_spans.yaml"
    with p.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _find_method_marker(app: str, qual_name: str) -> tuple[str | None, str | None]:
    """Return (qualname_marker, layer_marker) by walking app modules."""
    for sub in ("engines", "integrations", "outputs"):
        d = REPO / app / sub
        if not d.is_dir():
            continue
        for f in sorted(d.glob("*.py")):
            if f.name.startswith(("_", ".")) or f.name == "__init__.py":
                continue
            mod_id = f"{app}.{sub}.{f.stem}"
            try:
                mod = importlib.import_module(mod_id)
            except ImportError:
                continue
            for name in dir(mod):
                try:
                    obj = getattr(mod, name, None)
                except Exception:  # noqa: BLE001
                    continue
                if not isinstance(obj, type):
                    continue
                for attr_name, attr in vars(obj).items():
                    marker = getattr(attr, "__adg_traces_execute__", None)
                    if not marker:
                        continue
                    if qual_name in marker:
                        layer = getattr(attr, "__adg_traces_layer__", None)
                        return (qual_name, layer)
    return (None, None)


class TestPerAppLayerMatch(unittest.TestCase):
    """One assertion per manifest entry — runtime layer matches manifest."""


def _make_test(app: str, qual_name: str, expected_layer: str):
    def test(self) -> None:
        found, actual = _find_method_marker(app, qual_name)
        self.assertEqual(
            found, qual_name,
            f"{app}: manifest declares '{qual_name}' but no @traces_execute marker found",
        )
        self.assertEqual(
            actual, expected_layer,
            f"{app}: '{qual_name}' decorator layer is '{actual}' but manifest declares '{expected_layer}'",
        )
    return test


# Dynamically generate one test method per manifest entry (parametric).
# Each test name is `test_<app>_<safe-qual>` so failures are pinpointed.
def _populate_tests() -> int:
    manifest = _load_manifest()
    count = 0
    for app, spec in manifest.items():
        if not isinstance(spec, dict):
            continue
        for entry in spec.get("required_spans", []) or []:
            if isinstance(entry, str):
                continue  # legacy form has no expected layer; skip
            if not isinstance(entry, dict):
                continue
            qual = entry.get("name")
            layer = entry.get("layer")
            if not qual or not layer:
                continue
            safe = qual.replace(".", "_").replace("-", "_")
            test_name = f"test_{app}_{safe}_layer_match"
            setattr(TestPerAppLayerMatch, test_name, _make_test(app, qual, layer))
            count += 1
    return count


_GENERATED = _populate_tests()


class TestPerAppLayerMatchMeta(unittest.TestCase):
    """Sanity check that the dynamic test generation actually populated tests."""

    def test_at_least_one_test_generated(self) -> None:
        self.assertGreater(
            _GENERATED, 0,
            "no parametric tests generated — manifest may be empty or malformed",
        )

    def test_generated_count_matches_manifest_dict_entries(self) -> None:
        manifest = _load_manifest()
        expected = sum(
            1
            for spec in manifest.values()
            if isinstance(spec, dict)
            for entry in spec.get("required_spans", []) or []
            if isinstance(entry, dict) and entry.get("name") and entry.get("layer")
        )
        self.assertEqual(_GENERATED, expected)


if __name__ == "__main__":
    unittest.main()
