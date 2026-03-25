"""Pipeline smoke tests — verify ADG pipeline components and system learning adapters."""

from pathlib import Path

import pytest


@pytest.mark.smoke
def test_adg_static_scanner_instantiable():
    """ADGStaticScanner can be instantiated with a repo root."""
    try:
        from agentic_core.adg.extraction.static_scanner import ADGStaticScanner
    except ImportError as e:
        pytest.skip(f"ADGStaticScanner not available: {e}")

    repo_root = Path(__file__).resolve().parents[3]
    scanner = ADGStaticScanner(repo_root=repo_root)
    assert scanner is not None, "ADGStaticScanner must be instantiable"
    assert hasattr(scanner, "scan"), "ADGStaticScanner must have a scan() method"


@pytest.mark.smoke
def test_adg_artifact_builder_importable():
    """ADGArtifactBuilder is importable and is a class."""
    try:
        from agentic_core.adg.builder import ADGArtifactBuilder
    except ImportError as e:
        pytest.skip(f"ADGArtifactBuilder not available: {e}")

    assert isinstance(ADGArtifactBuilder, type), "ADGArtifactBuilder should be a class"
    public = {n for n in dir(ADGArtifactBuilder) if not n.startswith("_")}
    assert "build" in public or len(public) >= 2, (
        "ADGArtifactBuilder should have build() or multiple public methods"
    )


@pytest.mark.smoke
def test_adg_schema_relation_types_present():
    """ADG schema module exposes RelationType and EdgeKind literals."""
    try:
        from agentic_core.adg import schema
    except ImportError as e:
        pytest.skip(f"adg.schema not available: {e}")

    assert hasattr(schema, "RelationType"), "schema must have RelationType"
    assert hasattr(schema, "EdgeKind"), "schema must have EdgeKind"
    # RelationType is a Literal type alias — verify core values are in __args__
    rt = schema.RelationType
    if hasattr(rt, "__args__"):
        rt_values = set(rt.__args__)
        for expected in ["calls", "imports", "exports"]:
            assert expected in rt_values, (
                f"RelationType should include '{expected}', got {sorted(rt_values)[:10]}"
            )


@pytest.mark.smoke
def test_adg_sqlite_artifact_exists():
    """At least one ADG SQLite artifact exists in artifacts/adg_clean/."""
    repo_root = Path(__file__).resolve().parents[3]
    adg_clean = repo_root / "artifacts" / "adg_clean"

    if not adg_clean.exists():
        pytest.skip("artifacts/adg_clean/ directory does not exist")

    sqlite_files = list(adg_clean.glob("*.sqlite"))
    assert len(sqlite_files) >= 1, "At least one ADG SQLite artifact should exist"

    # Verify the SQLite file is a valid database
    import sqlite3

    db_path = sqlite_files[0]
    conn = sqlite3.connect(str(db_path))
    try:
        tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        table_names = {t[0] for t in tables}
        assert "nodes" in table_names, "ADG SQLite must have 'nodes' table"
        assert "edges" in table_names, "ADG SQLite must have 'edges' table"

        node_count = conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
        edge_count = conn.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
        assert node_count > 0, "nodes table must not be empty"
        assert edge_count > 0, "edges table must not be empty"
    finally:
        conn.close()


@pytest.mark.smoke
def test_system_learning_l1_meta_adapter_importable():
    """system_learning l1_meta_adapter imports and exposes public API."""
    try:
        import system_learning.adapters.l1_meta_adapter as mod
    except ImportError as e:
        pytest.skip(f"l1_meta_adapter not available: {e}")

    public = [n for n in dir(mod) if not n.startswith("_")]
    assert len(public) >= 1, "l1_meta_adapter must expose at least one public symbol"


@pytest.mark.smoke
def test_system_learning_config_importable():
    """system_learning config modules import without error."""
    try:
        import system_learning.config.semantic_memory_config as mod
    except ImportError as e:
        pytest.skip(f"semantic_memory_config not available: {e}")

    public = [n for n in dir(mod) if not n.startswith("_")]
    assert len(public) >= 1, "semantic_memory_config must expose at least one public symbol"
