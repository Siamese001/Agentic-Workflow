"""W9 — prompt registry, template inventory, profiles, and classification SSOT."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
import yaml

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

_PA = _REPO / "apps_rg" / "prompt_assembly"
_TEMPLATES = _PA / "templates"
_REGISTRY = _PA / "prompt_registry.yaml"
_CLASSIFICATION = _REPO / "artifacts" / "apps_rg" / "prompt_authority" / "template_classification.json"
_BYPASS = _REPO / "artifacts" / "apps_rg" / "prompt_authority" / "runtime_bypass_map.json"
_PROFILES = (
    _REPO / "apps_rg" / "rg_prompt_profile.yaml",
    _REPO / "apps_rg" / "rg_evidence_profile.yaml",
)
_SECTION_CONTRACT_DIR = _PA / "section_prompt_contracts"

_BAD_INLINE_MANDATES = (
    "end each bullet with [source:",
    "every proof point must carry [source:",
    "at least 1 [source:",
    "preserve all [source:",
    "max 2 proof points with [source:",
)


def _load_yaml(p: Path) -> dict:
    return yaml.safe_load(p.read_text(encoding="utf-8"))


def _template_files() -> list[Path]:
    return sorted(_TEMPLATES.glob("*.yaml"))


def test_template_classification_covers_every_template_file() -> None:
    data = json.loads(_CLASSIFICATION.read_text(encoding="utf-8"))
    rels = {e["relative_path"] for e in data["classifications"]}
    for path in _template_files():
        rel = f"templates/{path.name}"
        assert rel in rels, f"Missing W9 classification for {rel}"
    unknown = [e for e in data["classifications"] if e.get("classification") == "UNKNOWN"]
    assert not unknown, unknown
    assert not data.get("explicit_carry_forward") or isinstance(
        data["explicit_carry_forward"], list
    )


def test_classification_json_matches_disk_template_count() -> None:
    data = json.loads(_CLASSIFICATION.read_text(encoding="utf-8"))
    assert len(data["classifications"]) == len(_template_files())


def test_registry_paths_resolve_and_test_only_not_flow_routable() -> None:
    reg = _load_yaml(_REGISTRY)
    templates = reg.get("templates") or {}
    for tid, entry in templates.items():
        rel = entry.get("path") or ""
        assert rel, tid
        p = (_PA / rel).resolve()
        assert p.is_file(), f"registry path missing: {tid} -> {p}"
        cls = entry.get("w9_classification")
        rdr = entry.get("runtime_dispatch_reachable")
        if cls == "TEST_ONLY":
            assert rdr is False, tid

    bypass = json.loads(_BYPASS.read_text(encoding="utf-8"))
    forbidden = set(bypass.get("forbidden_in_l2_flow_bridge") or [])
    from apps_rg.l2_recipe import pa_context_bridge  # noqa: PLC0415 — apps_rg-local

    bridged = set(pa_context_bridge._FLOW_ROUTE_TO_TEMPLATE_ID.values())
    assert bridged == set(bypass["l2_flow_route_allowlist_template_ids"])
    assert bridged.isdisjoint(forbidden)


def test_active_registry_templates_skip_bad_inline_mandates() -> None:
    reg = _load_yaml(_REGISTRY)
    templates = reg.get("templates") or {}
    for tid, entry in templates.items():
        if entry.get("w9_classification") == "TEST_ONLY":
            continue
        rel = entry.get("path") or ""
        body = (_PA / rel).read_text(encoding="utf-8").lower()
        for phrase in _BAD_INLINE_MANDATES:
            assert phrase not in body, f"{tid} mandates inline display tags via {phrase!r}"


def test_generated_section_contracts_point_to_existing_templates() -> None:
    for p in sorted(_SECTION_CONTRACT_DIR.glob("*.contract.yaml")):
        row = _load_yaml(p)
        if not row.get("llm_generation_allowed"):
            continue
        ref = row.get("apps_rg_prompt_template_ref") or ""
        assert ref, p.name
        assert not ref.endswith("LOCKED_DETERMINISTIC_COPY")
        tpl = _REPO / ref
        assert tpl.is_file(), f"{p.name} -> {tpl}"


def test_rg_profiles_citation_posture_classified() -> None:
    for path in _PROFILES:
        doc = _load_yaml(path)
        if "truthfulness_markers" in doc:
            posture = doc["truthfulness_markers"].get("citation_posture") or {}
        else:
            posture = doc.get("citation_requirement", {}).get("citation_posture") or {}
        assert posture.get("w9_class") == "ACTIVE_PROMPT_AUTHORITY_LEDGER_ONLY", path.name


@pytest.mark.parametrize("profile_path", _PROFILES, ids=lambda p: p.name)
def test_no_legacy_flat_orphan_citation_format_string(profile_path: Path) -> None:
    """W8/W9: replace string citation_format with classified citation_posture."""
    text = profile_path.read_text(encoding="utf-8")
    assert '\ncitation_format: "[source:' not in text, profile_path.name

