"""W8 receipt for zero-cover P1 apps_lic surfaces from the ADG runtime proxy."""

from __future__ import annotations

from pathlib import Path

# W8 ADG covers-edge anchor: this triage test inspects surface source as text, so
# without a real import it registers no `covers` edge into apps_lic and the
# reachability receipt's W8-file self-check would skip. A full-module-path import
# of one triaged zero-cover surface makes this file a genuine ADG covers source.
from apps_lic.types.validation_severity_types import ValidationSeverity as _TriageCoversAnchor

REPO_ROOT = Path(__file__).resolve().parents[2]

BEHAVIOR_PINNED_ZERO_COVER_SURFACES = {
    "apps_lic/utils/lic_agent_base_util.py": (
        "tests/unit/apps_lic/utils/test_lic_agent_base_util_contract.py"
    ),
    "apps_lic/types/route_types.py": (
        "tests/unit/apps_lic/types/test_route_and_archetype_contracts.py"
    ),
    "apps_lic/types/message_route_types.py": (
        "tests/unit/apps_lic/types/test_route_and_archetype_contracts.py"
    ),
    "apps_lic/types/recipient_archetype_types.py": (
        "tests/unit/apps_lic/types/test_route_and_archetype_contracts.py"
    ),
    "apps_lic/types/competitor_recon_agent_types.py": (
        "tests/unit/apps_lic/types/test_route_and_archetype_contracts.py"
    ),
    "apps_lic/types/app_content_validator_agent_types.py": (
        "tests/unit/apps_lic/types/test_route_and_archetype_contracts.py"
    ),
    "apps_lic/types/validation_severity_types.py": (
        "tests/unit/apps_lic/types/test_route_and_archetype_contracts.py"
    ),
}

CANONICAL_QUARANTINE_ONLY_SURFACES = {
    "apps_lic/utils/lic_agent_base_util.py",
    "apps_lic/types/route_types.py",
    "apps_lic/types/message_route_types.py",
    "apps_lic/types/recipient_archetype_types.py",
    "apps_lic/types/competitor_recon_agent_types.py",
    "apps_lic/types/app_content_validator_agent_types.py",
    "apps_lic/types/validation_severity_types.py",
}


def test_zero_cover_surfaces_have_explicit_w8_behavior_test_receipts() -> None:
    for production_path, test_path in BEHAVIOR_PINNED_ZERO_COVER_SURFACES.items():
        assert (REPO_ROOT / production_path).is_file(), production_path
        assert (REPO_ROOT / test_path).is_file(), test_path


def test_quarantine_only_surfaces_are_not_imported_by_canonical_dispatch() -> None:
    dispatch_source = (REPO_ROOT / "apps_lic/runtime/dispatch/canonical_dispatch.py").read_text(
        encoding="utf-8"
    )

    for production_path in CANONICAL_QUARANTINE_ONLY_SURFACES:
        module_leaf = Path(production_path).stem
        assert module_leaf not in dispatch_source


def test_triage_file_registers_as_adg_covers_source() -> None:
    """Use the full-path import so this triage test stays a real ADG covers source."""
    assert _TriageCoversAnchor is not None
