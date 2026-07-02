"""Tests for scripts/governance/verify_codex_enforcement_home.py."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "governance"))

import verify_codex_enforcement_home as mod  # noqa: E402


def _write(path: Path, text: str = "placeholder") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _handoff_toml_block(automation_id: str, **overrides: object) -> str:
    expected = mod.ADG_HANDOFF_CONTRACTS.get(automation_id)
    if expected is None:
        return ""
    handoff = dict(expected)
    handoff.update(overrides)
    lines = ["", "[handoff]"]
    for field in expected:
        lines.append(f"{field} = {json.dumps(handoff[field])}")
    return "\n".join(lines)


def _publication_runtime_toml_block(**overrides: object) -> str:
    runtime = dict(mod.PUBLICATION_RUNTIME_OPTIMIZATION_CONTRACT)
    runtime.update(overrides)
    lines = ["", "[runtime_optimization]"]
    for field in mod.PUBLICATION_RUNTIME_OPTIMIZATION_CONTRACT:
        lines.append(f"{field} = {json.dumps(runtime[field])}")
    return "\n".join(lines)


def _automation_toml(
    automation_id: str,
    prompt: str,
    root: Path,
    include_publication_runtime: bool = True,
    **handoff_overrides: object,
) -> str:
    escaped_prompt = prompt.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    escaped_root = str(root).replace("\\", "\\\\")
    manual = automation_id in mod.MANUAL_AUTOMATION_IDS
    kind = "manual" if manual else "cron"
    status = "ON_DEMAND" if manual else "ACTIVE"
    lines = [
        "version = 1",
        f'id = "{automation_id}"',
        f'kind = "{kind}"',
        f'name = "{automation_id}"',
        f'prompt = "{escaped_prompt}"',
        f'status = "{status}"',
    ]
    if not manual:
        lines.append('rrule = "RRULE:FREQ=WEEKLY;BYHOUR=22;BYMINUTE=0;BYDAY=SU,MO,TU,WE,TH,FR,SA"')
    lines.extend(
        [
            'model = "gpt-5.4-mini"',
            'reasoning_effort = "xhigh"',
            'execution_environment = "local"',
            f'cwds = ["{escaped_root}"]',
            "created_at = 1",
            "updated_at = 1",
        ]
    )
    text = "\n".join(lines)
    if automation_id == "on-demand-pr-main-publisher" and include_publication_runtime:
        text += _publication_runtime_toml_block()
    return text + _handoff_toml_block(automation_id, **handoff_overrides)


def _projection_toml(root: Path, automation_id: str, **overrides: object) -> str:
    projection = mod.build_user_profile_projection(root, automation_id)
    assert projection is not None
    projection.update(overrides)
    lines = ["version = 1"]
    emitted = set()
    for field in mod.AUTOMATION_PROJECTION_FIELDS:
        lines.append(f"{field} = {json.dumps(projection[field])}")
        emitted.add(field)
    for field in sorted(set(projection) - emitted):
        lines.append(f"{field} = {json.dumps(projection[field])}")
    lines.extend(["created_at = 1", "updated_at = 1"])
    return "\n".join(lines)


def _publication_prompt() -> str:
    return "\n".join(mod.PUBLICATION_REQUIRED_PROMPT_SNIPPETS)


def _adg_prompt() -> str:
    return "\n".join(mod.ADG_REQUIRED_PROMPT_SNIPPETS)


def _adg_p0_prompt() -> str:
    return "\n".join(mod.ADG_P0_REQUIRED_PROMPT_SNIPPETS)


def _adg_p1_prompt() -> str:
    return "\n".join(mod.ADG_P1_REQUIRED_PROMPT_SNIPPETS)


def _adg_p2_prompt() -> str:
    return "\n".join(mod.ADG_P2_REQUIRED_PROMPT_SNIPPETS)


def _adg_p3_prompt() -> str:
    return "\n".join(mod.ADG_P3_REQUIRED_PROMPT_SNIPPETS)


def _svp_docs_prompt() -> str:
    return "\n".join(mod.SVP_DOCS_REQUIRED_PROMPT_SNIPPETS)


def _apps_rg_s2e_prompt() -> str:
    return "\n".join(mod.APPS_RG_S2E_REQUIRED_PROMPT_SNIPPETS)


def _valid_root(tmp_path: Path) -> Path:
    prompt_by_id = {
        "on-demand-pr-main-publisher": _publication_prompt(),
        "on-demand-apps-rg-anthropic-partnership-fresh-s2e": _apps_rg_s2e_prompt(),
        "weekly-adg-audit-and-burndown": _adg_prompt(),
        "adg-p0-blocker-burndown": _adg_p0_prompt(),
        "adg-p1-ratchet-burndown": _adg_p1_prompt(),
        "adg-bcg-p2-next-action": _adg_p2_prompt(),
        "adg-p3-promotion-hygiene": _adg_p3_prompt(),
        "weekly-svp-readme-documentation-refresh": _svp_docs_prompt(),
    }
    for automation_id in mod.AUTOMATION_IDS:
        _write(
            mod._automation_path(tmp_path, automation_id),
            _automation_toml(automation_id, prompt_by_id.get(automation_id, "placeholder prompt"), tmp_path),
        )
    for skill_id in mod.REPO_SKILL_IDS:
        _write(tmp_path / ".codex" / "skills" / skill_id / "SKILL.md")
    return tmp_path


def test_repo_owned_enforcement_passes(tmp_path: Path) -> None:
    root = _valid_root(tmp_path)
    user_codex_home = tmp_path / "user-codex"

    assert mod.validate(root, user_codex_home) == []


def test_user_profile_automation_fails(tmp_path: Path) -> None:
    root = _valid_root(tmp_path / "repo")
    user_codex_home = tmp_path / "user-codex"
    _write(user_codex_home / "automations" / "on-demand-pr-main-publisher" / "automation.toml")

    issues = mod.validate(root, user_codex_home)

    assert any(issue.code == "user_profile_enforcement_artifact" for issue in issues)


def test_user_profile_thin_automation_launcher_fails(tmp_path: Path) -> None:
    root = _valid_root(tmp_path / "repo")
    user_codex_home = tmp_path / "user-codex"
    launcher = user_codex_home / "automations" / "weekly-adg-audit-and-burndown" / "automation.toml"
    prompt = (
        "Run the Agentic-Workflow ADG Audit and Burndown automation. "
        f"Use the repo-owned contract at \"{root / '.codex' / 'automations' / 'adg-audit-and-burndown' / 'automation.toml'}\" "
        "as the source of truth."
    )
    _write(launcher, _automation_toml("weekly-adg-audit-and-burndown", prompt, root))

    issues = mod.validate(root, user_codex_home)

    assert any(issue.code == "user_profile_enforcement_artifact" for issue in issues)


def test_user_profile_generated_projection_passes(tmp_path: Path) -> None:
    root = _valid_root(tmp_path / "repo")
    user_codex_home = tmp_path / "user-codex"
    launcher = user_codex_home / "automations" / "adg-p0-blocker-burndown" / "automation.toml"
    _write(launcher, _projection_toml(root, "adg-p0-blocker-burndown"))

    issues = mod.validate(root, user_codex_home)

    assert issues == []


def test_user_profile_projection_detects_contract_digest_drift(tmp_path: Path) -> None:
    root = _valid_root(tmp_path / "repo")
    user_codex_home = tmp_path / "user-codex"
    launcher = user_codex_home / "automations" / "adg-p0-blocker-burndown" / "automation.toml"
    _write(launcher, _projection_toml(root, "adg-p0-blocker-burndown"))
    automation = mod._automation_path(root, "adg-p0-blocker-burndown")
    automation.write_text(
        _automation_toml("adg-p0-blocker-burndown", _adg_p0_prompt() + "\nNew source contract line.", root),
        encoding="utf-8",
    )

    issues = mod.validate(root, user_codex_home)

    assert any(issue.code == "user_profile_enforcement_artifact" for issue in issues)


def test_user_profile_projection_rejects_schedule_drift(tmp_path: Path) -> None:
    root = _valid_root(tmp_path / "repo")
    user_codex_home = tmp_path / "user-codex"
    launcher = user_codex_home / "automations" / "adg-p0-blocker-burndown" / "automation.toml"
    _write(
        launcher,
        _projection_toml(
            root,
            "adg-p0-blocker-burndown",
            rrule="RRULE:FREQ=WEEKLY;BYHOUR=7;BYMINUTE=45;BYDAY=MO",
        ),
    )

    issues = mod.validate(root, user_codex_home)

    assert any(issue.code == "user_profile_enforcement_artifact" for issue in issues)


def test_user_profile_projection_rejects_contract_path_drift(tmp_path: Path) -> None:
    root = _valid_root(tmp_path / "repo")
    user_codex_home = tmp_path / "user-codex"
    launcher = user_codex_home / "automations" / "adg-p0-blocker-burndown" / "automation.toml"
    _write(
        launcher,
        _projection_toml(root, "adg-p0-blocker-burndown", contract_path=str(root / "stale" / "automation.toml")),
    )

    issues = mod.validate(root, user_codex_home)

    assert any(issue.code == "user_profile_enforcement_artifact" for issue in issues)


def test_user_profile_projection_rejects_prompt_payload(tmp_path: Path) -> None:
    root = _valid_root(tmp_path / "repo")
    user_codex_home = tmp_path / "user-codex"
    launcher = user_codex_home / "automations" / "adg-p0-blocker-burndown" / "automation.toml"
    _write(
        launcher,
        _projection_toml(root, "adg-p0-blocker-burndown", prompt="Copied repo-owned automation prompt."),
    )

    issues = mod.validate(root, user_codex_home)

    assert any(issue.code == "user_profile_enforcement_artifact" for issue in issues)


def test_user_profile_memory_only_known_automation_dir_fails(tmp_path: Path) -> None:
    root = _valid_root(tmp_path / "repo")
    user_codex_home = tmp_path / "user-codex"
    _write(user_codex_home / "automations" / "on-demand-pr-main-publisher" / "memory.md")

    issues = mod.validate(root, user_codex_home)

    assert any(issue.code == "user_profile_enforcement_artifact" for issue in issues)


def test_user_profile_unknown_repo_referencing_automation_fails(tmp_path: Path) -> None:
    root = _valid_root(tmp_path / "repo")
    user_codex_home = tmp_path / "user-codex"
    automation = user_codex_home / "automations" / "custom-agentic-workflow" / "automation.toml"
    _write(automation, _automation_toml("custom-agentic-workflow", f"Run Agentic-Workflow in {root}", root))

    issues = mod.validate(root, user_codex_home)

    assert any(issue.code == "user_profile_enforcement_artifact" for issue in issues)


def test_user_profile_copied_automation_contract_fails(tmp_path: Path) -> None:
    root = _valid_root(tmp_path / "repo")
    user_codex_home = tmp_path / "user-codex"
    copied_contract = user_codex_home / "automations" / "adg-p0-blocker-burndown" / "automation.toml"
    _write(copied_contract, _automation_toml("adg-p0-blocker-burndown", _adg_p0_prompt(), root))

    issues = mod.validate(root, user_codex_home)

    assert any(issue.code == "user_profile_enforcement_artifact" for issue in issues)


def test_repo_local_singular_automation_tree_fails(tmp_path: Path) -> None:
    root = _valid_root(tmp_path / "repo")
    _write(root / ".codex" / "automation" / "misplaced.toml")

    issues = mod.validate(root, tmp_path / "user-codex")

    assert any(issue.code == "repo_duplicate_enforcement_home" for issue in issues)


def test_repo_local_agent_instruction_tree_fails(tmp_path: Path) -> None:
    root = _valid_root(tmp_path / "repo")
    _write(root / ".codex" / "agent-instructions" / "boundary-auditor.md")

    issues = mod.validate(root, tmp_path / "user-codex")

    assert any(issue.code == "repo_duplicate_enforcement_home" for issue in issues)


def test_user_profile_skill_fails(tmp_path: Path) -> None:
    root = _valid_root(tmp_path / "repo")
    user_codex_home = tmp_path / "user-codex"
    _write(user_codex_home / "skills" / "agentic-workflow-governance" / "SKILL.md")

    issues = mod.validate(root, user_codex_home)

    assert any(issue.code == "user_profile_enforcement_artifact" for issue in issues)


def test_publication_prompt_requires_strict_single_main_contract(tmp_path: Path) -> None:
    root = _valid_root(tmp_path)
    automation = root / ".codex" / "automations" / "on-demand-pr-main-publisher" / "automation.toml"
    automation.write_text(
        _automation_toml("on-demand-pr-main-publisher", "HEAD == origin/main", root),
        encoding="utf-8",
    )

    issues = mod.validate(root, tmp_path / "user-codex")

    assert any(issue.code == "publication_prompt_missing" for issue in issues)


def test_publication_prompt_requires_dirty_preservation_not_publication(tmp_path: Path) -> None:
    root = _valid_root(tmp_path)
    automation = root / ".codex" / "automations" / "on-demand-pr-main-publisher" / "automation.toml"
    required = (
        "Dirty preservation is not publication; incoherent, local_or_config_scope, and "
        "unsafe_or_unknown_scope files must be stashed or retained, not merged to main."
    )
    automation.write_text(
        _automation_toml("on-demand-pr-main-publisher", _publication_prompt().replace(required, ""), root),
        encoding="utf-8",
    )

    issues = mod.validate(root, tmp_path / "user-codex")

    assert any(issue.code == "publication_prompt_missing" and required in issue.detail for issue in issues)


def test_publication_prompt_requires_review_thread_gate(tmp_path: Path) -> None:
    root = _valid_root(tmp_path)
    automation = root / ".codex" / "automations" / "on-demand-pr-main-publisher" / "automation.toml"
    required = "Before merge, block on unresolved GitHub review threads with P1 or P2 findings for the PR head."
    automation.write_text(
        _automation_toml("on-demand-pr-main-publisher", _publication_prompt().replace(required, ""), root),
        encoding="utf-8",
    )

    issues = mod.validate(root, tmp_path / "user-codex")

    assert any(issue.code == "publication_prompt_missing" and required in issue.detail for issue in issues)


def test_publication_prompt_requires_branch_reuse_guard(tmp_path: Path) -> None:
    root = _valid_root(tmp_path)
    automation = root / ".codex" / "automations" / "on-demand-pr-main-publisher" / "automation.toml"
    required = (
        "Do not reuse a head branch that already had a merged or closed PR unless this run is explicitly "
        "an ancestry-recording PR."
    )
    automation.write_text(
        _automation_toml("on-demand-pr-main-publisher", _publication_prompt().replace(required, ""), root),
        encoding="utf-8",
    )

    issues = mod.validate(root, tmp_path / "user-codex")

    assert any(issue.code == "publication_prompt_missing" and required in issue.detail for issue in issues)


def test_publication_prompt_rejects_obsolete_dirty_success_wording(tmp_path: Path) -> None:
    root = _valid_root(tmp_path)
    automation = root / ".codex" / "automations" / "on-demand-pr-main-publisher" / "automation.toml"
    automation.write_text(
        _automation_toml(
            "on-demand-pr-main-publisher",
            _publication_prompt() + "\ndirty protected worktrees reported and preserved",
            root,
        ),
        encoding="utf-8",
    )

    issues = mod.validate(root, tmp_path / "user-codex")

    assert any(issue.code == "publication_prompt_obsolete" for issue in issues)


def test_publication_prompt_rejects_obsolete_whole_dirty_merge_wording(tmp_path: Path) -> None:
    root = _valid_root(tmp_path)
    automation = root / ".codex" / "automations" / "on-demand-pr-main-publisher" / "automation.toml"
    automation.write_text(
        _automation_toml(
            "on-demand-pr-main-publisher",
            _publication_prompt() + "\ncommit all non-disposable dirty files there",
            root,
        ),
        encoding="utf-8",
    )

    issues = mod.validate(root, tmp_path / "user-codex")

    assert any(issue.code == "publication_prompt_obsolete" for issue in issues)


def test_publication_runtime_optimization_metadata_required(tmp_path: Path) -> None:
    root = _valid_root(tmp_path)
    automation = root / ".codex" / "automations" / "on-demand-pr-main-publisher" / "automation.toml"
    automation.write_text(
        _automation_toml(
            "on-demand-pr-main-publisher",
            _publication_prompt(),
            root,
            include_publication_runtime=False,
        ),
        encoding="utf-8",
    )

    issues = mod.validate(root, tmp_path / "user-codex")

    assert any(issue.code == "publication_runtime_optimization_missing" for issue in issues)


def test_publication_runtime_optimization_rejects_always_rerun_policy(tmp_path: Path) -> None:
    root = _valid_root(tmp_path)
    automation = root / ".codex" / "automations" / "on-demand-pr-main-publisher" / "automation.toml"
    text = _automation_toml("on-demand-pr-main-publisher", _publication_prompt(), root)
    automation.write_text(
        text.replace('rerun_policy = "mutation_triggered"', 'rerun_policy = "always"'),
        encoding="utf-8",
    )

    issues = mod.validate(root, tmp_path / "user-codex")

    assert any(issue.code == "publication_runtime_optimization_contract" for issue in issues)


def test_on_demand_publication_rejects_cron_schedule(tmp_path: Path) -> None:
    root = _valid_root(tmp_path)
    automation = root / ".codex" / "automations" / "on-demand-pr-main-publisher" / "automation.toml"
    cron_text = (
        _automation_toml("on-demand-pr-main-publisher", _publication_prompt(), root)
        .replace('kind = "manual"', 'kind = "cron"')
        .replace(
            'status = "ON_DEMAND"',
            'status = "ACTIVE"\nrrule = "RRULE:FREQ=WEEKLY;BYHOUR=22;BYMINUTE=0;BYDAY=SU,MO,TU,WE,TH,FR,SA"',
        )
    )
    automation.write_text(cron_text, encoding="utf-8")

    issues = mod.validate(root, tmp_path / "user-codex")

    assert any(issue.code == "automation_kind" for issue in issues)
    assert any(issue.code == "automation_status" for issue in issues)
    assert any(issue.code == "automation_rrule" for issue in issues)


def test_apps_rg_s2e_automation_is_required(tmp_path: Path) -> None:
    root = _valid_root(tmp_path)
    automation = mod._automation_path(root, "on-demand-apps-rg-anthropic-partnership-fresh-s2e")
    automation.unlink()

    issues = mod.validate(root, tmp_path / "user-codex")

    assert any(
        issue.code == "automation_missing"
        and "on-demand-apps-rg-anthropic-partnership-fresh-s2e" in issue.detail
        for issue in issues
    )


def test_apps_rg_s2e_rejects_cron_schedule(tmp_path: Path) -> None:
    root = _valid_root(tmp_path)
    automation = mod._automation_path(root, "on-demand-apps-rg-anthropic-partnership-fresh-s2e")
    cron_text = (
        _automation_toml(
            "on-demand-apps-rg-anthropic-partnership-fresh-s2e",
            _apps_rg_s2e_prompt(),
            root,
        )
        .replace('kind = "manual"', 'kind = "cron"')
        .replace(
            'status = "ON_DEMAND"',
            'status = "ACTIVE"\nrrule = "RRULE:FREQ=WEEKLY;BYHOUR=2;BYMINUTE=10;BYDAY=SU,MO,TU,WE,TH,FR,SA"',
        )
    )
    automation.write_text(cron_text, encoding="utf-8")

    issues = mod.validate(root, tmp_path / "user-codex")

    assert any(issue.code == "automation_kind" for issue in issues)
    assert any(issue.code == "automation_status" for issue in issues)
    assert any(issue.code == "automation_rrule" for issue in issues)


def test_apps_rg_s2e_prompt_requires_real_e2e_command(tmp_path: Path) -> None:
    root = _valid_root(tmp_path)
    automation = mod._automation_path(root, "on-demand-apps-rg-anthropic-partnership-fresh-s2e")
    automation.write_text(
        _automation_toml(
            "on-demand-apps-rg-anthropic-partnership-fresh-s2e",
            "Run apps_rg eventually.",
            root,
        ),
        encoding="utf-8",
    )

    issues = mod.validate(root, tmp_path / "user-codex")

    assert any(issue.code == "apps_rg_s2e_prompt_missing" for issue in issues)


def test_wrong_cwd_fails(tmp_path: Path) -> None:
    root = _valid_root(tmp_path)
    automation = mod._automation_path(root, "weekly-adg-audit-and-burndown")
    automation.write_text(
        _automation_toml("weekly-adg-audit-and-burndown", _adg_prompt(), tmp_path / "other"),
        encoding="utf-8",
    )

    issues = mod.validate(root, tmp_path / "user-codex")

    assert any(issue.code == "automation_cwd" for issue in issues)


def test_registered_worktree_accepts_canonical_repo_cwd(
    monkeypatch,
    tmp_path: Path,
) -> None:
    worktree = _valid_root(tmp_path / "repo-worktree")
    primary = tmp_path / "repo-primary"
    user_codex_home = tmp_path / "user-codex"
    monkeypatch.setattr(mod, "_git_common_repo_root", lambda root: primary)
    for automation_id in mod.AUTOMATION_IDS:
        path = mod._automation_path(worktree, automation_id)
        text = path.read_text(encoding="utf-8")
        text = text.replace(str(worktree).replace("\\", "\\\\"), str(primary).replace("\\", "\\\\"))
        path.write_text(text, encoding="utf-8")

    issues = mod.validate(worktree, user_codex_home)

    assert not any(issue.code == "automation_cwd" for issue in issues)


def test_adg_handoff_graph_requires_producer_to_unblock_p0(tmp_path: Path) -> None:
    root = _valid_root(tmp_path)
    automation = mod._automation_path(root, "weekly-adg-audit-and-burndown")
    automation.write_text(
        _automation_toml(
            "weekly-adg-audit-and-burndown",
            _adg_prompt(),
            root,
            unblocks=[],
        ),
        encoding="utf-8",
    )

    issues = mod.validate(root, tmp_path / "user-codex")

    assert any(issue.code == "adg_handoff_contract" for issue in issues)
    assert any(issue.code == "adg_handoff_graph_edge" for issue in issues)


def test_adg_handoff_graph_requires_p0_to_unblock_p1(tmp_path: Path) -> None:
    root = _valid_root(tmp_path)
    automation = mod._automation_path(root, "adg-p0-blocker-burndown")
    automation.write_text(
        _automation_toml(
            "adg-p0-blocker-burndown",
            _adg_p0_prompt(),
            root,
            unblocks=[],
        ),
        encoding="utf-8",
    )

    issues = mod.validate(root, tmp_path / "user-codex")

    assert any(issue.code == "adg_handoff_contract" for issue in issues)
    assert any(issue.code == "adg_handoff_graph_edge" for issue in issues)


def test_adg_handoff_graph_requires_p1_to_unblock_p2(tmp_path: Path) -> None:
    root = _valid_root(tmp_path)
    automation = mod._automation_path(root, "adg-p1-ratchet-burndown")
    automation.write_text(
        _automation_toml(
            "adg-p1-ratchet-burndown",
            _adg_p1_prompt(),
            root,
            unblocks=[],
        ),
        encoding="utf-8",
    )

    issues = mod.validate(root, tmp_path / "user-codex")

    assert any(issue.code == "adg_handoff_contract" for issue in issues)
    assert any(issue.code == "adg_handoff_graph_edge" for issue in issues)


def test_adg_handoff_graph_requires_p2_to_depend_on_p0_and_p1(tmp_path: Path) -> None:
    root = _valid_root(tmp_path)
    automation = mod._automation_path(root, "adg-bcg-p2-next-action")
    automation.write_text(
        _automation_toml(
            "adg-bcg-p2-next-action",
            _adg_p2_prompt(),
            root,
            depends_on=["weekly-adg-audit-and-burndown"],
            requires_prior_lane_clean=[],
        ),
        encoding="utf-8",
    )

    issues = mod.validate(root, tmp_path / "user-codex")

    assert any(issue.code == "adg_handoff_contract" for issue in issues)
    assert any(issue.code == "adg_handoff_graph_dependency" for issue in issues)


def test_adg_handoff_graph_requires_p2_to_unblock_p3(tmp_path: Path) -> None:
    root = _valid_root(tmp_path)
    automation = mod._automation_path(root, "adg-bcg-p2-next-action")
    automation.write_text(
        _automation_toml(
            "adg-bcg-p2-next-action",
            _adg_p2_prompt(),
            root,
            unblocks=[],
        ),
        encoding="utf-8",
    )

    issues = mod.validate(root, tmp_path / "user-codex")

    assert any(issue.code == "adg_handoff_contract" for issue in issues)
    assert any(issue.code == "adg_handoff_graph_edge" for issue in issues)


def test_adg_handoff_graph_requires_p3_to_wait_for_p2_not_actionable(tmp_path: Path) -> None:
    root = _valid_root(tmp_path)
    automation = mod._automation_path(root, "adg-p3-promotion-hygiene")
    automation.write_text(
        _automation_toml(
            "adg-p3-promotion-hygiene",
            _adg_p3_prompt(),
            root,
            requires_prior_lane_not_actionable=[],
        ),
        encoding="utf-8",
    )

    issues = mod.validate(root, tmp_path / "user-codex")

    assert any(issue.code == "adg_handoff_contract" for issue in issues)


def test_p2_prompt_requires_p0_p1_clean_same_generation_gate(tmp_path: Path) -> None:
    root = _valid_root(tmp_path)
    automation = mod._automation_path(root, "adg-bcg-p2-next-action")
    automation.write_text(
        _automation_toml("adg-bcg-p2-next-action", "artifact_status=certified or artifact_status=repair_ready", root),
        encoding="utf-8",
    )

    issues = mod.validate(root, tmp_path / "user-codex")

    assert any(issue.code == "adg_p2_prompt_missing" for issue in issues)


def test_p3_prompt_requires_p2_precedence_gate(tmp_path: Path) -> None:
    root = _valid_root(tmp_path)
    automation = mod._automation_path(root, "adg-p3-promotion-hygiene")
    automation.write_text(
        _automation_toml("adg-p3-promotion-hygiene", "artifact_status=certified or artifact_status=repair_ready", root),
        encoding="utf-8",
    )

    issues = mod.validate(root, tmp_path / "user-codex")

    assert any(issue.code == "adg_p3_prompt_missing" for issue in issues)


def test_svp_docs_prompt_requires_x1d_x2_x3_contract(tmp_path: Path) -> None:
    root = _valid_root(tmp_path)
    automation = mod._automation_path(root, "weekly-svp-readme-documentation-refresh")
    automation.write_text(
        _automation_toml("weekly-svp-readme-documentation-refresh", "svp_docs_x1d/v1", root),
        encoding="utf-8",
    )

    issues = mod.validate(root, tmp_path / "user-codex")

    assert any(issue.code == "svp_docs_prompt_missing" for issue in issues)
