"""Wave 5 ADG testing-hotspots — apps_eval.registry.loader validation surface.

The loaders read JSON registries off disk; this module exercises the pure
validation/guard logic (old-suite rejection, app-allowlist enforcement, type
guards) by monkeypatching the single private file reader ``_load_registry``
with in-memory payloads — no real disk fixtures, no mocks of behavior under
test.
"""

from __future__ import annotations

import pytest

from apps_eval.registry import loader


class TestConstants:
    def test_allowed_apps(self):
        assert loader.ALLOWED_APPS == {"apps_rg", "apps_lic"}

    def test_old_suite_names_present(self):
        assert "routing_enforcement" in loader.OLD_SUITE_NAMES
        assert "determinism_contracts" in loader.OLD_SUITE_NAMES
        assert len(loader.OLD_SUITE_NAMES) == 6


class TestLoadAppsRegistry:
    def test_valid(self, monkeypatch):
        monkeypatch.setattr(
            loader, "_load_registry", lambda name: {"apps": {"apps_rg": {}, "apps_lic": {}}}
        )
        assert set(loader.load_apps_registry()) == {"apps_rg", "apps_lic"}

    def test_wrong_app_set_rejected(self, monkeypatch):
        monkeypatch.setattr(
            loader, "_load_registry", lambda name: {"apps": {"apps_rg": {}}}
        )
        with pytest.raises(ValueError, match="must contain only"):
            loader.load_apps_registry()


class TestLoadSuitesRegistry:
    def test_valid(self, monkeypatch):
        monkeypatch.setattr(
            loader,
            "_load_registry",
            lambda name: {"suites": {"s1": {"app_id": "apps_rg"}}},
        )
        suites = loader.load_suites_registry()
        assert "s1" in suites

    def test_old_suite_name_rejected(self, monkeypatch):
        monkeypatch.setattr(
            loader,
            "_load_registry",
            lambda name: {"suites": {"routing_enforcement": {"app_id": "apps_rg"}}},
        )
        with pytest.raises(ValueError, match="old suite name is not allowed"):
            loader.load_suites_registry()

    def test_unsupported_app_rejected(self, monkeypatch):
        monkeypatch.setattr(
            loader,
            "_load_registry",
            lambda name: {"suites": {"s1": {"app_id": "apps_nope"}}},
        )
        with pytest.raises(ValueError, match="unsupported app"):
            loader.load_suites_registry()

    def test_non_dict_suites_rejected(self, monkeypatch):
        monkeypatch.setattr(loader, "_load_registry", lambda name: {"suites": []})
        with pytest.raises(ValueError, match="suites mapping"):
            loader.load_suites_registry()


class TestLoadSuite:
    def test_old_suite_name_rejected_eagerly(self):
        with pytest.raises(ValueError, match="old suite name is rejected"):
            loader.load_suite("orchestration_hop")

    def test_unknown_suite_raises_keyerror(self, monkeypatch):
        monkeypatch.setattr(
            loader, "_load_registry", lambda name: {"suites": {"known": {"app_id": "apps_rg"}}}
        )
        with pytest.raises(KeyError, match="unknown suite"):
            loader.load_suite("missing")

    def test_returns_copy_with_injected_id(self, monkeypatch):
        monkeypatch.setattr(
            loader,
            "_load_registry",
            lambda name: {"suites": {"s1": {"app_id": "apps_lic", "scenarios": ["a"]}}},
        )
        suite = loader.load_suite("s1")
        assert suite["suite_id"] == "s1"
        assert suite["app_id"] == "apps_lic"


class TestLoadGradersRegistry:
    def test_valid_list_of_strings(self, monkeypatch):
        monkeypatch.setattr(
            loader, "_load_registry", lambda name: {"graders": ["schema", "provenance"]}
        )
        assert loader.load_graders_registry() == ["schema", "provenance"]

    def test_non_string_entries_rejected(self, monkeypatch):
        monkeypatch.setattr(
            loader, "_load_registry", lambda name: {"graders": ["schema", 1]}
        )
        with pytest.raises(ValueError, match="list of strings"):
            loader.load_graders_registry()


class TestLoadThresholdsRegistry:
    def test_valid(self, monkeypatch):
        monkeypatch.setattr(
            loader, "_load_registry", lambda name: {"thresholds": {"s1": {"pass_score": 0.9}}}
        )
        assert loader.load_thresholds_registry()["s1"]["pass_score"] == 0.9

    def test_non_dict_rejected(self, monkeypatch):
        monkeypatch.setattr(loader, "_load_registry", lambda name: {"thresholds": []})
        with pytest.raises(ValueError, match="thresholds mapping"):
            loader.load_thresholds_registry()
