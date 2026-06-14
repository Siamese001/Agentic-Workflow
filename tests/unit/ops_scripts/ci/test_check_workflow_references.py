from __future__ import annotations

from pathlib import Path

from ops_scripts.ci.check_workflow_references import find_reference_issues


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def messages(root: Path, *files: str) -> list[str]:
    return [issue.message for issue in find_reference_issues(root, [Path(file) for file in files])]


def test_flags_missing_requirements_and_common_setup(tmp_path: Path) -> None:
    workflow = tmp_path / ".github/workflows/stale.yml"
    write(
        workflow,
        """
name: stale
on:
  pull_request:
    paths: ["x/**"]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: ./.github/actions/common-setup
      - run: pip install -r requirements.txt || true
""",
    )

    found = messages(tmp_path, ".github/workflows/stale.yml")

    assert "references requirements.txt, but requirements.txt is absent" in found
    assert "references deleted common-setup action" in found


def test_flags_broad_pr_trigger_without_changes_job(tmp_path: Path) -> None:
    write(
        tmp_path / ".github/workflows/broad.yml",
        """
name: broad
on:
  pull_request:
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: echo ok
""",
    )

    found = messages(tmp_path, ".github/workflows/broad.yml")

    assert "has broad pull_request trigger without paths or a changes job" in found


def test_accepts_broad_pr_trigger_with_changes_job(tmp_path: Path) -> None:
    write(
        tmp_path / ".github/workflows/diff.yml",
        """
name: diff
on:
  pull_request:
jobs:
  changes:
    runs-on: ubuntu-latest
    steps:
      - run: echo changed
  summary:
    needs: changes
    runs-on: ubuntu-latest
    steps:
      - run: echo ok
""",
    )

    assert messages(tmp_path, ".github/workflows/diff.yml") == []


def test_accepts_broad_pr_trigger_with_changed_only_command(tmp_path: Path) -> None:
    write(
        tmp_path / ".github/workflows/self-check.yml",
        """
name: self-check
on:
  pull_request:
jobs:
  workflow-reference-check:
    runs-on: ubuntu-latest
    steps:
      - run: python ops_scripts/ci/check_workflow_references.py --changed-only --base-sha abc --head-sha def
""",
    )
    write(tmp_path / "ops_scripts/ci/check_workflow_references.py", "print('ok')\n")

    assert messages(tmp_path, ".github/workflows/self-check.yml") == []


def test_flags_missing_python_and_pytest_paths(tmp_path: Path) -> None:
    write(
        tmp_path / ".github/workflows/missing-paths.yml",
        """
name: missing-paths
on:
  pull_request:
    paths: ["x/**"]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: python ops_scripts/ci/missing.py
      - run: python -m pytest tests/missing/test_nope.py -q
""",
    )

    found = messages(tmp_path, ".github/workflows/missing-paths.yml")

    assert "runs missing python script ops_scripts/ci/missing.py" in found
    assert "runs pytest against missing path tests/missing/test_nope.py" in found


def test_changed_file_scope_ignores_untouched_stale_workflows(tmp_path: Path) -> None:
    write(
        tmp_path / ".github/workflows/stale.yml",
        """
name: stale
on:
  pull_request:
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: ./.github/actions/common-setup
""",
    )
    write(
        tmp_path / ".github/workflows/changed.yml",
        """
name: changed
on:
  pull_request:
    paths: [".github/workflows/changed.yml"]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: echo ok
""",
    )

    assert messages(tmp_path, ".github/workflows/changed.yml") == []
