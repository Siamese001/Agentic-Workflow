"""p3.2 DoD-1 — canonical apps_rg route_profiles.yaml exists."""
from __future__ import annotations

from pathlib import Path


def test_canonical_route_profiles_yaml_exists() -> None:
    root = Path(__file__).resolve().parents[2]
    path = root / "apps_rg" / "config" / "domain_contract" / "route_profiles.yaml"
    assert path.is_file(), f"missing canonical route profile: {path}"
    text = path.read_text(encoding="utf-8")
    assert "rg_route_profile.yaml" not in text, "stale rg_route_profile reference must not appear"


def test_stale_profile_path_not_in_l0_binding() -> None:
    root = Path(__file__).resolve().parents[2]
    src = (root / "apps_rg" / "runtime" / "bindings" / "l0_binding.py").read_text(encoding="utf-8")
    assert "profiles/rg_route_profile.yaml" not in src
