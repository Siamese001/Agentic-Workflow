from __future__ import annotations

import ast
import sqlite3
from pathlib import Path
from typing import Any, cast

from agentic_core.adg.artifact import multi_writer
from agentic_core.adg.extraction.visitors import VisitorContext, _AntipatternVisitor
from agentic_core.adg.processing.phase3_auto_remediation import (
    AutoRemediationEngine,
    RemediationAction,
    RemediationStrategy,
)


def _build_minimal_phase3_db(
    db_path: Path, file_path: Path, edge_kind: str = "broad_exception_catch"
) -> None:
    conn = sqlite3.connect(str(db_path))
    conn.execute(
        """
        CREATE TABLE edges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            edge_kind TEXT NOT NULL DEFAULT '',
            relation_type TEXT NOT NULL DEFAULT 'antipattern'
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE violations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            edge_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            evidence TEXT NOT NULL,
            file_path TEXT NOT NULL,
            line_no INTEGER NOT NULL,
            severity TEXT NOT NULL,
            disposition TEXT NOT NULL
        )
        """
    )
    conn.execute("INSERT INTO edges (edge_kind, relation_type) VALUES (?, 'antipattern')", (edge_kind,))
    conn.execute(
        """
        INSERT INTO violations (edge_id, category, evidence, file_path, line_no, severity, disposition)
        VALUES (1, 'antipattern', 'ValueError', ?, 2, 'HIGH', 'untriaged')
        """,
        (str(file_path),),
    )
    conn.commit()
    conn.close()


def test_return_none_swallow_anchors_to_except_header_line() -> None:
    code = """
def sample():
    try:
        return 1
    except ValueError:  # guardian: allow-return-none-swallow -- detector fixture for except-site anchoring
        return None
"""
    tree = ast.parse(code)
    visitor = _AntipatternVisitor(VisitorContext(module_adg_name="m", source_file="x.py"))
    visitor.visit(tree)
    edges = [e for e in visitor.extract_edges() if e.edge_kind == "return_none_swallow"]
    assert len(edges) == 1
    assert edges[0].line_no == 5


def test_guardian_matches_inline_and_above_and_multiline_header(tmp_path: Path) -> None:
    source = tmp_path / "guarded.py"
    source.write_text(
        """
def inline():
    try:
        pass
    except ValueError:  # guardian: allow-silent-swallow -- fixture inline guardian
        pass


def above():
    try:
        pass
    except ValueError:  # guardian: allow-log-and-swallow -- fixture above-header guardian
        logger.error('x')
        pass


def multi():
    try:
        pass
    except (
        ValueError,
        TypeError,
    ) as exc:  # guardian: allow-return-none-swallow -- fixture multiline closing-line guardian
        return None
""".strip()
        + "\n",
        encoding="utf-8",
    )

    assert multi_writer.has_guardian_for_violation(str(source), 4, "silent_exception_swallow")
    assert multi_writer.has_guardian_for_violation(str(source), 12, "log_and_swallow")
    assert multi_writer.has_guardian_for_violation(str(source), 22, "return_none_swallow")


def test_phase3_loads_persisted_symbol_evidence_rows(tmp_path: Path) -> None:
    source = tmp_path / "candidate.py"
    source.write_text(
        """
def f():
    try:
        parse()
    except ValueError:  # guardian: allow-return-none-swallow -- fixture handler for persisted evidence selection
        return None
""".strip()
        + "\n",
        encoding="utf-8",
    )
    db_path = tmp_path / "adg.sqlite"
    _build_minimal_phase3_db(db_path, source, edge_kind="return_none_swallow")

    with AutoRemediationEngine(db_path) as engine:
        # pylint: disable=protected-access
        candidates = engine._load_remediation_candidates()

    assert len(candidates) == 1
    assert candidates[0].evidence == "ValueError"
    assert candidates[0].edge_kind == "return_none_swallow"


def test_phase3_apply_remediation_rejects_wrong_line_target(tmp_path: Path) -> None:
    source = tmp_path / "apply_target.py"
    source.write_text(
        """
def g():
    try:
        parse()
    except ValueError:  # guardian: allow-log-and-swallow -- fixture handler for patch-target verification
        return None
""".strip()
        + "\n",
        encoding="utf-8",
    )
    db_path = tmp_path / "apply.sqlite"
    _build_minimal_phase3_db(db_path, source)

    action = RemediationAction(
        strategy=RemediationStrategy.NARROW_TO_SPECIFIC,
        file_path=str(source),
        line_no=5,
        original_line="    except ValueError:",
        suggested_line="    except RuntimeError:",
        exception_types=[],
        risk_score=0.9,
        confidence=0.9,
    )

    with AutoRemediationEngine(db_path) as engine:
        assert engine.apply_remediation(action, dry_run=False) is False


def test_multi_writer_delegates_to_artifactpaths(monkeypatch, tmp_path: Path) -> None:
    captured = {"called": False}

    def _fake_canonical(*_args, **_kwargs):
        captured["called"] = True
        return multi_writer.ArtifactPaths(
            snapshot=tmp_path / "s.json",
            sqlite=tmp_path / "i.sqlite",
            file_graph=tmp_path / "f.json",
            symbol_graph=tmp_path / "y.json",
            governance_graph=tmp_path / "g.json",
        )

    monkeypatch.setattr("agentic_core.adg.artifact.ArtifactPaths.write_all_artifacts", _fake_canonical)
    result = multi_writer.write_all_artifacts(artifact=cast(Any, object()), out_dir=tmp_path, ts="x")
    assert captured["called"] is True
    assert isinstance(result, multi_writer.ArtifactPaths)
