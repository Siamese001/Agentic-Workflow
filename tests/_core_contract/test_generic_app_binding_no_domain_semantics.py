"""Generic binding validators must remain domain-agnostic (no lane vocabulary)."""

from __future__ import annotations

from pathlib import Path

FORBIDDEN_FRAGMENTS = (
    "executive_summary_dispatch",
    "ibm_bullet_tailor_dispatch_v1",
    "competencies_dispatch",
)


def test_core_binding_validators_avoid_apps_rg_lane_identifiers() -> None:
    root = Path(__file__).resolve().parents[2] / "agentic_core/runtime/bindings"
    targets = [
        "profile_validators.py",
        "ref_validators.py",
        "evidence_policy_validator.py",
        "exit_binding_validator.py",
        "app_binding_validation.py",
        "app_binding_loader.py",
    ]
    for name in targets:
        text = (root / name).read_text(encoding="utf-8")
        for frag in FORBIDDEN_FRAGMENTS:
            assert frag not in text, f"{name} leaked domain token {frag!r}"
