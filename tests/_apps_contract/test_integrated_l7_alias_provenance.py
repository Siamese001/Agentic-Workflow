"""Contract: integrated L7 compatibility aliases declare core provenance."""
from __future__ import annotations

from agentic_core.runtime.entrypoints.integrated_single_action_spine_run import (
    _l7_compat_alias_fields,
)


def test_l7_compat_alias_fields_are_core_owned() -> None:
    fields = _l7_compat_alias_fields()
    assert fields["producer_component"].startswith("agentic_core")
    assert fields["artifact_role"] == "core_compat_alias_for_l7_projection"
    assert fields["canonical_source_artifact"] == "r4_run_manifest.json"
    assert fields["runtime_subject"] == "agentic_core"
    assert fields["app_subject"] == "apps_rg"
    assert fields["app_subject"] != fields["runtime_subject"]
