from __future__ import annotations

from pathlib import Path

import yaml

from ops_scripts.ci.audit_required_checks import active_check_contexts, audit_local


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_active_check_contexts_use_workflow_and_job_display_names(tmp_path: Path) -> None:
    write(
        tmp_path / ".github/workflows/ci-self-check.yml",
        """
name: ci-self-check
on:
  pull_request:
jobs:
  workflow-reference-check:
    name: workflow-reference-check
    runs-on: ubuntu-latest
    steps:
      - run: echo ok
""",
    )

    assert active_check_contexts(tmp_path) == {"ci-self-check / workflow-reference-check"}


def test_audit_local_accepts_target_required_checks(tmp_path: Path) -> None:
    write(
        tmp_path / ".github/workflows/runtime-smokes.yml",
        """
name: runtime-smokes
on:
  pull_request:
jobs:
  smoke-summary:
    name: smoke-summary
    runs-on: ubuntu-latest
    steps:
      - run: echo ok
""",
    )
    config = {"branch_protection": {"required_checks": ["runtime-smokes / smoke-summary"]}}

    assert audit_local(tmp_path, config) == 0


def test_audit_local_rejects_missing_required_check(tmp_path: Path) -> None:
    write(
        tmp_path / ".github/workflows/runtime-smokes.yml",
        """
name: runtime-smokes
on:
  pull_request:
jobs:
  smoke-summary:
    runs-on: ubuntu-latest
    steps:
      - run: echo ok
""",
    )
    config = {"branch_protection": {"required_checks": ["contract-gates / contract-summary"]}}

    assert audit_local(tmp_path, config) == 1


def test_workflow_config_required_checks_match_active_workflows() -> None:
    root = Path.cwd()
    config = yaml.safe_load((root / ".github/workflow-config.yaml").read_text(encoding="utf-8"))

    assert audit_local(root, config) == 0
