"""Unit tests for discovery canonical identity fields.

Ensures every ACTIVE agent record emitted by full_agent_discovery has:
  - canonical_class (AST-verified, non-empty)
  - canonical_file (forward-slash normalized, no backslashes)
  - canonical_agent_id (non-empty)

Outcome 1 of post-consolidation hardening.
"""

from __future__ import annotations

import pytest

from agentic_core.L0_routing.scripts.full_agent_discovery import (
    perform_deep_integrity_scan,
)
from agentic_core.L0_routing.utils.ssot_discovery_util import (
    load_agent_discovery,
)
from agentic_core.L5_safety.config.structure_blueprint import (
    get_validated_project_root,
)


@pytest.fixture(scope="module")
def verified_agents():
    """Run discovery once and return verified agent list."""
    project_root = get_validated_project_root()
    raw = load_agent_discovery(project_root, force_reload=True)
    verified, _stats = perform_deep_integrity_scan(raw, project_root)
    return verified


class TestCanonicalClassPresent:
    """Every verified agent must have canonical_class."""

    def test_all_records_have_canonical_class(self, verified_agents):
        missing = [
            a.get("class_name", a.get("canonical_file", "?"))
            for a in verified_agents
            if not a.get("canonical_class")
        ]
        assert not missing, f"{len(missing)} agent(s) missing canonical_class: {missing[:10]}"

    def test_canonical_class_matches_verification_status(self, verified_agents):
        mismatches = []
        for a in verified_agents:
            vs_class = (a.get("verification_status") or {}).get("class", "")
            cc = a.get("canonical_class", "")
            if cc and vs_class and cc != vs_class:
                mismatches.append((cc, vs_class))
        assert not mismatches, f"canonical_class != verification_status.class: {mismatches[:10]}"


class TestCanonicalFileNormalized:
    """canonical_file must be forward-slash normalized (§20)."""

    def test_all_records_have_canonical_file(self, verified_agents):
        missing = [a.get("canonical_class", "?") for a in verified_agents if not a.get("canonical_file")]
        assert not missing, f"{len(missing)} agent(s) missing canonical_file: {missing[:10]}"

    def test_no_backslashes_in_canonical_file(self, verified_agents):
        bad = [a["canonical_file"] for a in verified_agents if "\\" in a.get("canonical_file", "")]
        assert not bad, f"{len(bad)} canonical_file(s) contain backslashes: {bad[:10]}"

    def test_no_dot_segments_in_canonical_file(self, verified_agents):
        bad = [
            a["canonical_file"]
            for a in verified_agents
            if a.get("canonical_file", "").startswith("./") or "/../" in a.get("canonical_file", "")
        ]
        assert not bad, f"{len(bad)} canonical_file(s) contain dot segments: {bad[:10]}"


class TestCanonicalAgentId:
    """canonical_agent_id must be present and non-empty."""

    def test_all_records_have_canonical_agent_id(self, verified_agents):
        missing = [a.get("canonical_class", "?") for a in verified_agents if not a.get("canonical_agent_id")]
        assert not missing, f"{len(missing)} agent(s) missing canonical_agent_id: {missing[:10]}"


class TestClassNameDivergence:
    """If class_name differs from canonical_class, canonical_class must still exist."""

    def test_divergent_class_name_still_has_canonical(self, verified_agents):
        divergent_missing = []
        for a in verified_agents:
            cn = a.get("class_name", "")
            cc = a.get("canonical_class", "")
            if cn and cn != cc and not cc:
                divergent_missing.append(cn)
        assert not divergent_missing, (
            f"class_name != canonical_class but canonical_class missing: {divergent_missing[:10]}"
        )
