"""Tests for truth_expansion_enricher._gate_self_check — A12 claim matching.

These tests pin the relaxed matching rule: a gate is consistent when the
intersection of docstring values and SQL values is non-empty. Only when
NO docstring value appears in SQL at all is the gate flagged as drift.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

from tools.generate.truth_expansion_enricher import PATH_REF_RE, _gate_self_check


def _write(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "check_fake_gate.py"
    p.write_text(textwrap.dedent(content), encoding="utf-8")
    return p


def test_path_ref_regex_captures_full_reference() -> None:
    match = PATH_REF_RE.search("target = 'tools/generate/truth_expansion_enricher.py'")
    assert match is not None
    assert match.group(1) == "tools/generate/truth_expansion_enricher.py"


# ---------- consistent cases (must NOT flag) ----------


def test_single_value_docstring_matches_sql(tmp_path: Path) -> None:
    p = _write(
        tmp_path,
        '''"""Gate — queries relation_type='imports' fan-in."""
def run(conn):
    return conn.execute(
        "SELECT * FROM edges WHERE relation_type = 'imports'"
    )
''',
    )
    result = _gate_self_check(p)
    assert result is not None
    consistent, _, _ = result
    assert consistent is True


def test_multi_value_docstring_any_match_is_consistent(tmp_path: Path) -> None:
    """The former bug: docstring mentions 'calls' and 'imports' for context;
    SQL queries only 'imports'. This must be treated as consistent because
    at least one docstring value is present in the SQL."""
    p = _write(
        tmp_path,
        '''"""Gate — resolves callers via relation_type='calls' and relation_type='imports' fan-in."""
def run(conn):
    return conn.execute(
        "SELECT * FROM edges WHERE relation_type = 'imports'"
    )
''',
    )
    result = _gate_self_check(p)
    assert result is not None
    consistent, claim_phrase, sql_snippet = result
    assert consistent is True, f"Expected consistent, got drift: {claim_phrase} vs {sql_snippet}"


def test_docstring_term_alias_matches(tmp_path: Path) -> None:
    """edge_kind and relation_type mentioned in docstring, SQL queries edge_kind."""
    p = _write(
        tmp_path,
        '''"""Gate — counts edges with edge_kind='dead_import' (also called unused_import).

    Detects relation_type='unused_import' for legacy callers.
    """
def run(conn):
    return conn.execute(
        "SELECT * FROM edges WHERE edge_kind = 'dead_import' AND relation_type = 'unused_import'"
    )
''',
    )
    result = _gate_self_check(p)
    assert result is not None
    consistent, _, _ = result
    assert consistent is True


# ---------- real drift cases (MUST flag) ----------


def test_no_overlap_flags_as_drift(tmp_path: Path) -> None:
    """Docstring claims 'calls', SQL only queries 'writes_to'. Real drift."""
    p = _write(
        tmp_path,
        '''"""Gate — queries relation_type='calls' for call-graph analysis."""
def run(conn):
    return conn.execute(
        "SELECT * FROM edges WHERE relation_type = 'writes_to'"
    )
''',
    )
    result = _gate_self_check(p)
    assert result is not None
    consistent, claim_phrase, sql_snippet = result
    assert consistent is False
    assert "calls" in claim_phrase
    assert "writes_to" in sql_snippet


def test_category_mismatch_flags_as_drift(tmp_path: Path) -> None:
    """Docstring claims category='hidden_write', SQL queries category='silent_swallow'."""
    p = _write(
        tmp_path,
        '''"""Gate — flags category='hidden_write' violations."""
def run(conn):
    return conn.execute(
        "SELECT * FROM violations WHERE category = 'silent_swallow'"
    )
''',
    )
    result = _gate_self_check(p)
    assert result is not None
    consistent, _, _ = result
    assert consistent is False


# ---------- degenerate cases (must return None, not raise) ----------


def test_no_docstring_claim_returns_none(tmp_path: Path) -> None:
    p = _write(
        tmp_path,
        '''"""Gate — just a generic gate with no claim phrases."""
def run(conn):
    return []
''',
    )
    result = _gate_self_check(p)
    assert result is None


def test_no_sql_returns_none(tmp_path: Path) -> None:
    p = _write(
        tmp_path,
        '''"""Gate — queries relation_type='imports'."""
# No SQL at all
def run():
    pass
''',
    )
    result = _gate_self_check(p)
    assert result is None


def test_unparseable_file_returns_none(tmp_path: Path) -> None:
    p = tmp_path / "check_broken.py"
    p.write_text("def broken( :\n  pass", encoding="utf-8")
    result = _gate_self_check(p)
    assert result is None


def test_unreadable_file_returns_none(tmp_path: Path) -> None:
    missing = tmp_path / "does_not_exist.py"
    result = _gate_self_check(missing)
    assert result is None


# ---------- regression pin: the two specific gates from the R5-W1 finding ----------


def test_check_exception_contract_pattern_is_consistent(tmp_path: Path) -> None:
    """Regression pin: docstring mentions 'calls' AND 'imports' (conceptually),
    SQL queries 'imports' (implementation). Must NOT flag."""
    p = _write(
        tmp_path,
        '''"""Gate: raise/catch symmetry on declared exception contracts.

    Resolves callers of ``raiser_symbol`` via the latest ADG SQLite snapshot
    (relation_type='calls' and relation_type='imports' fan-in).
    """
def run(conn):
    return conn.execute("SELECT * FROM edges WHERE relation_type = 'imports'")
''',
    )
    result = _gate_self_check(p)
    assert result is not None
    consistent, _, _ = result
    assert consistent is True


def test_check_unused_imports_ratchet_pattern_is_consistent(tmp_path: Path) -> None:
    """Regression pin: docstring mentions edge_kind='dead_import' AND
    relation_type='unused_import'. SQL queries one. Must NOT flag."""
    p = _write(
        tmp_path,
        '''"""Gate S4 — unused-import ratchet.

    Counts relation_type='unused_import' edges (edge_kind='dead_import')
    from production modules.
    """
def run(conn):
    return conn.execute("SELECT * FROM edges WHERE relation_type = 'unused_import'")
''',
    )
    result = _gate_self_check(p)
    assert result is not None
    consistent, _, _ = result
    assert consistent is True
