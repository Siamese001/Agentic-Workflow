"""Tests for the read-only Codex governance surface manifest validator."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "ops_scripts" / "ci"))

import check_governance_surface_manifest as mod  # noqa: E402


def _manifest() -> dict:
    return {
        "schema_version": "codex-governance-surface/v1",
        "rule_defaults": {
            "owner": "platform-governance",
            "scope": "repo_global",
            "load_mode": "always_on",
            "enforcement_mode": "instruction",
            "lifecycle": "active",
            "canonical_source": "self",
        },
        "rule_overrides": {},
        "hook_defaults": {
            "owner": "platform-governance",
            "scope": "repo_global",
            "load_mode": "event_driven",
            "enforcement_mode": "runtime_hook",
            "lifecycle": "active",
            "canonical_source": "self",
        },
        "hook_overrides": {},
        "legacy_reference_policy": {
            "scan_roots": [".codex/rules", ".codex/hooks", ".codex/governance/scripts"],
            "historical_prefixes": ["docs/archive/"],
            "compatibility_prefixes": [".codex/hooks/", ".codex/governance/scripts/"],
            "remediation_required_paths": [],
            "active_terms": ["GitKraken"],
            "legacy_terms": ["Claude", "Cursor", "Windsurf", "Cascade"],
            "policy": "test fixture",
        },
    }


def _root(tmp_path: Path) -> Path:
    for relative in (".codex/rules", ".codex/hooks", ".codex/governance/scripts"):
        (tmp_path / relative).mkdir(parents=True, exist_ok=True)
    (tmp_path / ".codex/rules/rule.md").write_text("# rule\n", encoding="utf-8")
    (tmp_path / ".codex/hooks.json").write_text(json.dumps({"hooks": {}}), encoding="utf-8")
    manifest = _manifest()
    (tmp_path / mod.MANIFEST_RELATIVE).write_text(json.dumps(manifest), encoding="utf-8")
    return tmp_path


def test_repo_manifest_resolves_every_rule_and_hook() -> None:
    result = mod.validate(REPO_ROOT)

    assert result["status"] == "PASS"
    assert len(result["rules"]) == 42
    assert len(result["hooks"]) == 22
    assert {item["load_mode"] for item in result["rules"]} == {"always_on"}
    assert result["legacy_references"]["remediation_required"] == 0


def test_unregistered_hook_requires_explicit_nonactive_lifecycle(tmp_path: Path) -> None:
    root = _root(tmp_path)
    (root / ".codex/hooks/manual.py").write_text("# utility\n", encoding="utf-8")

    result = mod.validate(root)

    assert result["status"] == "FAIL"
    assert any("unregistered hook manual.py" in error for error in result["errors"])


def test_rule_canonical_source_must_exist(tmp_path: Path) -> None:
    root = _root(tmp_path)
    manifest_path = root / mod.MANIFEST_RELATIVE
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["rule_overrides"] = {"rule.md": {"canonical_source": "docs/missing.md"}}
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    result = mod.validate(root)

    assert result["status"] == "FAIL"
    assert any("canonical_source missing" in error for error in result["errors"])


def test_unclassified_legacy_reference_fails(tmp_path: Path) -> None:
    root = _root(tmp_path)
    (root / ".codex/rules/rule.md").write_text("Claude-only legacy wording\n", encoding="utf-8")

    result = mod.validate(root)

    assert result["status"] == "FAIL"
    assert any("unclassified legacy reference" in error for error in result["errors"])
