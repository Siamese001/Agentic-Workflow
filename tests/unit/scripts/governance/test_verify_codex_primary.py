"""Tests for scripts/governance/verify_codex_primary.py."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "governance"))

import verify_codex_primary as mod  # noqa: E402


def _write(path: Path, text: str = "placeholder") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _automation_toml(automation_id: str, prompt: str, root: Path) -> str:
    escaped_prompt = prompt.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    escaped_root = str(root).replace("\\", "\\\\")
    return "\n".join(
        [
            "version = 1",
            f'id = "{automation_id}"',
            'kind = "cron"',
            f'name = "{automation_id}"',
            f'prompt = "{escaped_prompt}"',
            'status = "ACTIVE"',
            'rrule = "RRULE:FREQ=WEEKLY;BYHOUR=22;BYMINUTE=0;BYDAY=SU,MO,TU,WE,TH,FR,SA"',
            'model = "gpt-5.5"',
            'reasoning_effort = "xhigh"',
            'execution_environment = "local"',
            f'cwds = ["{escaped_root}"]',
            "created_at = 1",
            "updated_at = 1",
        ]
    )


def _valid_root(tmp_path: Path) -> Path:
    for relative in mod.REQUIRED_FILES:
        _write(tmp_path / relative)

    _write(
        tmp_path / ".codex" / "automations" / "on-demand-pr-main-publisher" / "automation.toml",
        _automation_toml(
            "on-demand-pr-main-publisher",
            "\n".join(mod.verify_codex_enforcement_home.PUBLICATION_REQUIRED_PROMPT_SNIPPETS),
            tmp_path,
        ),
    )
    _write(
        tmp_path / ".codex" / "automations" / "weekly-adg-audit-and-burndown" / "automation.toml",
        _automation_toml(
            "weekly-adg-audit-and-burndown",
            "\n".join(mod.verify_codex_enforcement_home.ADG_REQUIRED_PROMPT_SNIPPETS),
            tmp_path,
        ),
    )
    _write(
        tmp_path / ".codex" / "automations" / "adg-p0-blocker-burndown" / "automation.toml",
        _automation_toml(
            "adg-p0-blocker-burndown",
            "\n".join(mod.verify_codex_enforcement_home.ADG_P0_REQUIRED_PROMPT_SNIPPETS),
            tmp_path,
        ),
    )
    _write(
        tmp_path / ".codex" / "automations" / "adg-p1-ratchet-burndown" / "automation.toml",
        _automation_toml(
            "adg-p1-ratchet-burndown",
            "\n".join(mod.verify_codex_enforcement_home.ADG_P1_REQUIRED_PROMPT_SNIPPETS),
            tmp_path,
        ),
    )

    weekly_path = tmp_path / ".codex" / "automations" / "svp-readme-documentation-refresh" / "automation.toml"
    weekly_anchors = mod.REQUIRED_ANCHORS[str(weekly_path.relative_to(tmp_path)).replace("\\", "/")]
    weekly_prompt = "\n".join(
        [
            *mod.verify_codex_enforcement_home.SVP_DOCS_REQUIRED_PROMPT_SNIPPETS,
            *weekly_anchors,
        ]
    )
    _write(
        weekly_path,
        _automation_toml("weekly-svp-readme-documentation-refresh", weekly_prompt, tmp_path)
        + "\n\n[svp_docs]\n"
        + 'mode = "audit_only"\n'
        + "require_approval_receipt = false\n"
        + "allow_edits = false\n"
        + "allow_publication = false\n"
        + 'publication_handoff = "on-demand-pr-main-publisher"\n',
    )

    _write(tmp_path / ".codex" / "hooks.json", json.dumps({"hooks": {}}))
    _write(tmp_path / ".codex" / "config.toml", "[features]\nhooks = true\n")
    _write(
        tmp_path / "AGENTS.md",
        "\n".join(mod.REQUIRED_ANCHORS["AGENTS.md"]),
    )
    _write(
        tmp_path / "docs/codex-primary-execution.md",
        "\n".join(mod.REQUIRED_ANCHORS["docs/codex-primary-execution.md"]),
    )

    for relative, anchors in mod.REQUIRED_ANCHORS.items():
        if relative in {
            "AGENTS.md",
            "docs/codex-primary-execution.md",
            ".codex/automations/svp-readme-documentation-refresh/automation.toml",
        }:
            continue
        _write(tmp_path / relative, "\n".join(anchors))
    return tmp_path


def test_valid_primary_contract_passes(tmp_path: Path) -> None:
    assert mod.validate(_valid_root(tmp_path), repo_only=True) == []


def test_p0_and_p1_automations_are_not_default_primary_requirements() -> None:
    assert ".codex/automations/adg-p0-blocker-burndown/automation.toml" not in mod.REQUIRED_FILES
    assert ".codex/automations/adg-p1-ratchet-burndown/automation.toml" not in mod.REQUIRED_FILES


def test_parse_args_accepts_repo_only_flag() -> None:
    args = mod.parse_args(["--repo-only"])

    assert args.repo_only is True
    assert args.root == mod.REPO_ROOT


def test_main_labels_the_result_as_static_and_discloses_hook_runtime_limit(tmp_path: Path, capsys) -> None:
    assert mod.main(["--root", str(_valid_root(tmp_path)), "--repo-only"]) == 0

    output = capsys.readouterr().out
    assert "static contract verification passed" in output
    assert "local hook trust/registration" in output


def test_repo_only_skips_enforcement_home_checks(tmp_path: Path, monkeypatch) -> None:
    root = _valid_root(tmp_path)
    monkeypatch.setattr(
        mod.verify_codex_enforcement_home,
        "validate",
        lambda _root: [SimpleNamespace(code="sentinel", detail="boom")],
    )

    assert mod.validate(root, repo_only=True) == []
    assert any("sentinel" in failure for failure in mod.validate(root))


def test_missing_anchor_fails(tmp_path: Path) -> None:
    root = _valid_root(tmp_path)
    (root / "AGENTS.md").write_text("## Codex primary execution adapter\n", encoding="utf-8")

    failures = mod.validate(root)
    assert any("missing anchor" in failure for failure in failures)


def test_missing_svp_schema_fails(tmp_path: Path) -> None:
    root = _valid_root(tmp_path)
    target = root / ".codex" / "schemas" / "svp_docs_x3_v1.schema.json"
    target.unlink()

    failures = mod.validate(root, repo_only=True)
    assert any("svp_docs_x3_v1.schema.json" in failure for failure in failures)


def test_missing_governance_surface_manifest_fails(tmp_path: Path) -> None:
    root = _valid_root(tmp_path)
    (root / ".codex/governance/governance_surface_manifest.json").unlink()

    failures = mod.validate(root, repo_only=True)
    assert any("governance_surface_manifest.json" in failure for failure in failures)
