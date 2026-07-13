from __future__ import annotations

import json
from pathlib import Path

from ops_scripts.ci.check_skill_catalog_integrity import evaluate_catalog
from ops_scripts.ci.check_skill_description_quality import evaluate_skill as evaluate_description
from ops_scripts.ci.check_skill_eval_coverage import evaluate_required_skills
from ops_scripts.ci.skill_contract import parse_skill_document, validate_skill_document


def _write_skill(
    root: Path,
    name: str,
    *,
    description: str | None = None,
    extra_frontmatter: str = "",
    body: str = "# Workflow\n\nFollow the documented procedure.\n",
) -> Path:
    skill_dir = root / name
    skill_dir.mkdir(parents=True)
    description = description or (
        f"Use this skill when running the {name} workflow, validating its outputs, "
        "or reviewing a related change."
    )
    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text(
        "---\n"
        f"name: {name}\n"
        f"description: {description}\n"
        f"{extra_frontmatter}"
        "---\n\n"
        f"{body}",
        encoding="utf-8",
    )
    return skill_dir


def _write_eval_files(skill_dir: Path) -> None:
    eval_dir = skill_dir / "evals"
    eval_dir.mkdir(parents=True)
    queries = []
    for index in range(6):
        queries.append(
            {
                "query": f"Run the {skill_dir.name} workflow for case {index}",
                "should_trigger": True,
                "split": "train" if index < 3 else "validation",
            }
        )
        queries.append(
            {
                "query": f"Near miss outside {skill_dir.name} case {index}",
                "should_trigger": False,
                "split": "train" if index < 3 else "validation",
            }
        )
    (eval_dir / "trigger_queries.json").write_text(json.dumps(queries), encoding="utf-8")
    (eval_dir / "evals.json").write_text(
        json.dumps(
            {
                "skill_name": skill_dir.name,
                "evals": [
                    {
                        "id": "happy-path",
                        "prompt": "Perform the workflow.",
                        "expected_output": "A validated workflow result.",
                        "files": [],
                    },
                    {
                        "id": "boundary",
                        "prompt": "Handle an ambiguous boundary case.",
                        "expected_output": "A bounded result or explicit stop condition.",
                        "files": [],
                    },
                ],
            }
        ),
        encoding="utf-8",
    )


def test_valid_skill_contract(tmp_path: Path) -> None:
    skill_dir = _write_skill(
        tmp_path,
        "valid-skill",
        extra_frontmatter='compatibility: "Requires Python 3.12"\nmetadata:\n  owner: platform\n  version: "1.0"\n',
    )
    document, parse_issues = parse_skill_document(skill_dir / "SKILL.md")
    assert parse_issues == []
    assert document is not None
    assert validate_skill_document(document) == []


def test_rejects_unsupported_trigger_field(tmp_path: Path) -> None:
    skill_dir = _write_skill(tmp_path, "invalid-trigger", extra_frontmatter="trigger: manual\n")
    document, _ = parse_skill_document(skill_dir / "SKILL.md")
    assert document is not None
    issues = validate_skill_document(document)
    assert any("unsupported frontmatter" in issue and "trigger" in issue for issue in issues)


def test_rejects_name_mismatch_and_consecutive_hyphen(tmp_path: Path) -> None:
    skill_dir = _write_skill(tmp_path, "folder-name")
    text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    (skill_dir / "SKILL.md").write_text(text.replace("name: folder-name", "name: bad--name"), encoding="utf-8")
    document, _ = parse_skill_document(skill_dir / "SKILL.md")
    assert document is not None
    issues = validate_skill_document(document)
    assert any("single hyphens" in issue for issue in issues)
    assert any("must match parent directory" in issue for issue in issues)


def test_rejects_non_string_metadata_value(tmp_path: Path) -> None:
    skill_dir = _write_skill(tmp_path, "metadata-skill", extra_frontmatter="metadata:\n  version: 1\n")
    document, _ = parse_skill_document(skill_dir / "SKILL.md")
    assert document is not None
    issues = validate_skill_document(document)
    assert "metadata value for 'version' must be a string" in issues


def test_description_quality_requires_trigger_and_blocks_legacy_product(tmp_path: Path) -> None:
    skill_dir = _write_skill(
        tmp_path,
        "legacy-description",
        description=(
            "Routes Claude Code through a repository workflow and validates the generated result "
            "without stating an activation condition."
        ),
    )
    result = evaluate_description(skill_dir)
    assert result.status == "fail"
    assert "missing_explicit_when_to_use_trigger" in result.issues
    assert "legacy_product_term_in_description" in result.issues


def test_catalog_rejects_redirect_language_and_broken_links(tmp_path: Path) -> None:
    skills_root = tmp_path / ".codex" / "skills"
    skill_dir = _write_skill(
        skills_root,
        "redirect-skill",
        body="# Redirect\n\nDeprecated redirect stub. See [missing](references/missing.md).\n",
    )
    assert skill_dir.exists()
    results = evaluate_catalog(skills_root)
    issues = results[0].issues
    assert any("deprecation/redirect" in issue for issue in issues)
    assert "broken relative reference: references/missing.md" in issues


def test_catalog_validates_openai_interface(tmp_path: Path) -> None:
    skills_root = tmp_path / ".codex" / "skills"
    skill_dir = _write_skill(skills_root, "ui-skill")
    agents = skill_dir / "agents"
    agents.mkdir()
    (agents / "openai.yaml").write_text("interface:\n  display_name: UI Skill\n", encoding="utf-8")
    results = evaluate_catalog(skills_root)
    issues = results[0].issues
    assert any("short_description" in issue for issue in issues)
    assert any("default_prompt" in issue for issue in issues)


def test_eval_coverage_accepts_balanced_train_validation_sets(tmp_path: Path) -> None:
    skills_root = tmp_path / ".codex" / "skills"
    skill_dir = _write_skill(skills_root, "core-skill")
    _write_eval_files(skill_dir)
    results = evaluate_required_skills(skills_root, required_skills=("core-skill",))
    assert results[0].issues == []
    assert results[0].trigger_queries == 12
    assert results[0].output_evals == 2


def test_eval_coverage_rejects_missing_fixtures(tmp_path: Path) -> None:
    skills_root = tmp_path / ".codex" / "skills"
    _write_skill(skills_root, "core-skill")
    results = evaluate_required_skills(skills_root, required_skills=("core-skill",))
    assert "missing trigger_queries.json" in results[0].issues
    assert "missing evals.json" in results[0].issues
