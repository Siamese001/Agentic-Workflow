"""Tests for ops_scripts/ci/annotate_consumer_mode.py.

Tier: unit
Plan: .windsurf/plans/three-bucket-otel-view-5db409.md (W6)
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

__adg_consumer_mode__ = "inventory"

# Import the annotator helpers directly; we don't need the CLI driver for unit tests.
ANNOTATOR_PATH = REPO_ROOT / "ops_scripts" / "ci" / "annotate_consumer_mode.py"
sys.path.insert(0, str(ANNOTATOR_PATH.parent))
import annotate_consumer_mode as ann  # noqa: E402


class TestInferMode:
    def test_proof_view_wins(self) -> None:
        src = "x = 'SELECT * FROM proof_view'\n"
        mode, _ = ann.infer_mode(src)
        assert mode == "proof"

    def test_risk_view(self) -> None:
        src = "x = 'SELECT * FROM risk_view'\n"
        mode, _ = ann.infer_mode(src)
        assert mode == "risk"

    def test_proof_overrides_risk(self) -> None:
        # Proof claim is stricter; if both views are queried, declare proof.
        src = "x = 'FROM proof_view JOIN risk_view'\n"
        mode, _ = ann.infer_mode(src)
        assert mode == "proof"

    def test_default_is_inventory(self) -> None:
        src = "rows = conn.execute('SELECT * FROM edges').fetchall()\n"
        mode, _ = ann.infer_mode(src)
        assert mode == "inventory"


class TestHasExistingDeclaration:
    def test_detects_simple_assignment(self) -> None:
        src = '__adg_consumer_mode__ = "proof"\n'
        assert ann.has_existing_declaration(src) is True

    def test_detects_annotated_assignment(self) -> None:
        src = '__adg_consumer_mode__: str = "proof"\n'
        assert ann.has_existing_declaration(src) is True

    def test_no_declaration(self) -> None:
        src = "x = 42\n"
        assert ann.has_existing_declaration(src) is False

    def test_unparseable_returns_false(self) -> None:
        src = "def x(:\n  bad\n"
        assert ann.has_existing_declaration(src) is False


class TestFindInsertionLine:
    def test_empty_file(self) -> None:
        assert ann.find_insertion_line("") == 0

    def test_after_docstring(self) -> None:
        src = '"""docstring"""\nimport os\n'
        # Docstring is line 1; insertion AFTER => line index 1.
        assert ann.find_insertion_line(src) == 1

    def test_after_future_import(self) -> None:
        src = "from __future__ import annotations\nimport os\n"
        assert ann.find_insertion_line(src) == 1

    def test_docstring_plus_future(self) -> None:
        src = '"""doc"""\nfrom __future__ import annotations\nimport os\n'
        assert ann.find_insertion_line(src) == 2

    def test_no_prelude(self) -> None:
        src = "import os\n"
        # No docstring or __future__ — last_prelude_line stays 0.
        assert ann.find_insertion_line(src) == 0


class TestInsertDeclaration:
    def test_inserts_after_docstring_and_future(self) -> None:
        src = '"""doc"""\nfrom __future__ import annotations\n\nimport os\n'
        new_src = ann.insert_declaration(src, "inventory")
        assert new_src is not None
        assert '__adg_consumer_mode__ = "inventory"' in new_src
        # Declaration appears after `from __future__` and before `import os`.
        future_idx = new_src.index("from __future__")
        decl_idx = new_src.index("__adg_consumer_mode__")
        os_idx = new_src.index("import os")
        assert future_idx < decl_idx < os_idx

    def test_inserts_at_top_when_no_prelude(self) -> None:
        src = "import os\n"
        new_src = ann.insert_declaration(src, "proof")
        assert new_src is not None
        assert new_src.startswith("# W6")
        assert '__adg_consumer_mode__ = "proof"' in new_src

    def test_unparseable_returns_none(self) -> None:
        src = "def bad(:\n  pass\n"
        assert ann.insert_declaration(src, "inventory") is None

    def test_idempotent_via_has_existing(self) -> None:
        src = (
            'from __future__ import annotations\n'
            '\n'
            '__adg_consumer_mode__ = "proof"\n'
        )
        # The driver checks has_existing_declaration before inserting; this
        # test simulates that contract.
        assert ann.has_existing_declaration(src) is True


class TestAnnotateOneIntegration:
    def test_dry_run_does_not_write(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        target = tmp_path / "consumer.py"
        target.write_text("import os\nx = 'FROM edges'\n", encoding="utf-8")
        monkeypatch.setattr(ann, "REPO_ROOT", tmp_path)
        plan = ann.annotate_one("consumer.py", apply=False)
        assert plan.inferred_mode == "inventory"
        assert plan.will_skip is False
        # File untouched.
        assert "__adg_consumer_mode__" not in target.read_text(encoding="utf-8")

    def test_apply_writes_declaration(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        target = tmp_path / "consumer.py"
        target.write_text(
            'from __future__ import annotations\n'
            'import os\n'
            'x = "SELECT * FROM proof_view"\n',
            encoding="utf-8",
        )
        monkeypatch.setattr(ann, "REPO_ROOT", tmp_path)
        plan = ann.annotate_one("consumer.py", apply=True)
        assert plan.inferred_mode == "proof"
        assert plan.will_skip is False
        text = target.read_text(encoding="utf-8")
        assert '__adg_consumer_mode__ = "proof"' in text

    def test_already_declared_skipped(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        target = tmp_path / "consumer.py"
        target.write_text(
            '__adg_consumer_mode__ = "inventory"\n'
            'x = "FROM edges"\n',
            encoding="utf-8",
        )
        monkeypatch.setattr(ann, "REPO_ROOT", tmp_path)
        plan = ann.annotate_one("consumer.py", apply=True)
        assert plan.will_skip is True
        assert plan.skip_reason == "already declared"

    def test_force_mode_overrides_inference(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        target = tmp_path / "consumer.py"
        target.write_text("import os\nx = 'FROM edges'\n", encoding="utf-8")
        monkeypatch.setattr(ann, "REPO_ROOT", tmp_path)
        plan = ann.annotate_one("consumer.py", apply=True, force_mode="proof")
        assert plan.inferred_mode == "proof"
        assert "forced via" in plan.reason
        assert '__adg_consumer_mode__ = "proof"' in target.read_text(encoding="utf-8")

    def test_missing_file_skipped(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(ann, "REPO_ROOT", tmp_path)
        plan = ann.annotate_one("not_real.py", apply=True)
        assert plan.will_skip is True
        assert "not found" in plan.skip_reason
