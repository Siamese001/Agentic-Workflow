"""Unit tests for ``ops_scripts/ci/check_apps_spine_delegation.py`` (ADR-078).

Plan: ``docs/archive/windsurf/legacy-tree/plans/adg-three-bucket-unified-c4f8e2.md`` (W3 P3.2).

Tests build a synthetic ADG SQLite database in a tmp directory + a synthetic
apps_*/ directory tree, then invoke the gate's pure functions against that
fixture. No live snapshot or live filesystem dependency.
"""

from __future__ import annotations

# Test consumes ADG via the gate's pure functions; producer-side test, not a
# graph-evidence consumer.
__adg_consumer_mode__ = "inventory"

import sqlite3
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ops_scripts.ci.check_apps_spine_delegation import (  # noqa: E402
    _is_expired,
    count_spine_imports,
    count_total_imports,
    discover_apps_packages,
    evaluate,
    find_latest_snapshot,
    load_allowlist,
    main,
)


# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------


SCHEMA = """
CREATE TABLE nodes (
    id INTEGER PRIMARY KEY,
    adg_name TEXT NOT NULL,
    entity_type TEXT NOT NULL DEFAULT 'module',
    layer TEXT NOT NULL DEFAULT '',
    identity_kind TEXT NOT NULL DEFAULT 'module',
    confidence TEXT NOT NULL DEFAULT 'verified',
    resolved_path TEXT NOT NULL DEFAULT ''
);
CREATE TABLE edges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    src_id INTEGER NOT NULL,
    dst_id INTEGER NOT NULL,
    relation_type TEXT NOT NULL,
    edge_kind TEXT NOT NULL DEFAULT 'static',
    source_file TEXT NOT NULL,
    line_no INTEGER NOT NULL DEFAULT 1,
    symbol TEXT NOT NULL DEFAULT ''
);
"""


def _seed_node(con: sqlite3.Connection, adg_name: str, resolved_path: str) -> int:
    cur = con.execute(
        "INSERT INTO nodes (adg_name, resolved_path) VALUES (?, ?)",
        (adg_name, resolved_path),
    )
    return int(cur.lastrowid)


def _seed_edge(
    con: sqlite3.Connection,
    src_id: int,
    dst_id: int,
    source_file: str,
    relation_type: str = "imports",
) -> None:
    con.execute(
        "INSERT INTO edges (src_id, dst_id, relation_type, source_file) "
        "VALUES (?, ?, ?, ?)",
        (src_id, dst_id, relation_type, source_file),
    )


@pytest.fixture
def synthetic_snapshot(tmp_path: Path) -> Path:
    """Build a temp ADG SQLite with two compliant + one violator package."""
    snap = tmp_path / "adg_indexed_test.sqlite"
    con = sqlite3.connect(snap)
    con.executescript(SCHEMA)

    # Spine targets (resolved_path style + adg_name style).
    l0 = _seed_node(con, "agentic_core.L0_routing.dispatch", "agentic_core/L0_routing/dispatch.py")
    l1 = _seed_node(con, "agentic_core.L1_cognition.brief", "agentic_core/L1_cognition/brief.py")
    l2 = _seed_node(con, "agentic_core.L2_execution.runner", "agentic_core/L2_execution/runner.py")
    # Non-spine target.
    other = _seed_node(con, "agentic_core.L6_observability.otel", "agentic_core/L6_observability/otel.py")

    # apps_compliant has 1 spine import (L0) + 2 non-spine imports.
    src_a = _seed_node(con, "apps_compliant.adapter", "apps_compliant/adapter.py")
    _seed_edge(con, src_a, l0, "apps_compliant/adapter.py")
    _seed_edge(con, src_a, other, "apps_compliant/adapter.py")
    _seed_edge(con, src_a, other, "apps_compliant/adapter.py")

    # apps_compliant_two has 3 spine imports.
    src_b = _seed_node(con, "apps_compliant_two.engine", "apps_compliant_two/engine.py")
    _seed_edge(con, src_b, l0, "apps_compliant_two/engine.py")
    _seed_edge(con, src_b, l1, "apps_compliant_two/engine.py")
    _seed_edge(con, src_b, l2, "apps_compliant_two/engine.py")

    # apps_violator has only non-spine imports.
    src_c = _seed_node(con, "apps_violator.standalone", "apps_violator/standalone.py")
    _seed_edge(con, src_c, other, "apps_violator/standalone.py")
    _seed_edge(con, src_c, other, "apps_violator/standalone.py")

    con.commit()
    con.close()
    return snap


@pytest.fixture
def synthetic_repo(tmp_path: Path) -> Path:
    """Build a temp repo root with three apps_* dirs matching the snapshot."""
    repo = tmp_path / "repo"
    repo.mkdir()
    for name in ("apps_compliant", "apps_compliant_two", "apps_violator"):
        (repo / name).mkdir()
    return repo


@pytest.fixture
def empty_allowlist(tmp_path: Path) -> Path:
    p = tmp_path / "allowlist.yaml"
    p.write_text("allowed_packages: []\n", encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# discover_apps_packages
# ---------------------------------------------------------------------------


def test_discover_apps_packages_returns_sorted(synthetic_repo: Path) -> None:
    pkgs = discover_apps_packages(synthetic_repo)
    assert pkgs == ["apps_compliant", "apps_compliant_two", "apps_violator"]


def test_discover_apps_packages_skips_dunder(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "apps_real").mkdir()
    (repo / "apps__hidden").mkdir()
    pkgs = discover_apps_packages(repo)
    assert pkgs == ["apps_real"]


def test_discover_apps_packages_ignores_non_apps(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "apps_x").mkdir()
    (repo / "agentic_core").mkdir()
    (repo / "tools").mkdir()
    pkgs = discover_apps_packages(repo)
    assert pkgs == ["apps_x"]


# ---------------------------------------------------------------------------
# count_spine_imports / count_total_imports
# ---------------------------------------------------------------------------


def test_count_spine_imports_compliant(synthetic_snapshot: Path) -> None:
    con = sqlite3.connect(synthetic_snapshot)
    try:
        assert count_spine_imports(con, "apps_compliant") == 1
        assert count_spine_imports(con, "apps_compliant_two") == 3
    finally:
        con.close()


def test_count_spine_imports_violator(synthetic_snapshot: Path) -> None:
    con = sqlite3.connect(synthetic_snapshot)
    try:
        assert count_spine_imports(con, "apps_violator") == 0
    finally:
        con.close()


def test_count_total_imports(synthetic_snapshot: Path) -> None:
    con = sqlite3.connect(synthetic_snapshot)
    try:
        assert count_total_imports(con, "apps_compliant") == 3
        assert count_total_imports(con, "apps_compliant_two") == 3
        assert count_total_imports(con, "apps_violator") == 2
    finally:
        con.close()


# ---------------------------------------------------------------------------
# Allowlist
# ---------------------------------------------------------------------------


def test_load_allowlist_empty(empty_allowlist: Path) -> None:
    assert load_allowlist(empty_allowlist) == {}


def test_load_allowlist_valid_entry(tmp_path: Path) -> None:
    p = tmp_path / "allowlist.yaml"
    p.write_text(
        "allowed_packages:\n"
        "  - package: apps_violator\n"
        "    reason: 'Pending remediation'\n"
        "    expires: '2026-12-31'\n",
        encoding="utf-8",
    )
    out = load_allowlist(p)
    assert "apps_violator" in out
    assert out["apps_violator"]["reason"] == "Pending remediation"
    assert out["apps_violator"]["expires"] == "2026-12-31"


def test_load_allowlist_rejects_empty_reason(tmp_path: Path, capsys) -> None:
    p = tmp_path / "allowlist.yaml"
    p.write_text(
        "allowed_packages:\n"
        "  - package: apps_x\n"
        "    reason: ''\n"
        "    expires: '2026-12-31'\n",
        encoding="utf-8",
    )
    out = load_allowlist(p)
    assert out == {}
    captured = capsys.readouterr()
    assert "missing required field" in captured.err.lower()


def test_load_allowlist_rejects_missing_expires(tmp_path: Path, capsys) -> None:
    p = tmp_path / "allowlist.yaml"
    p.write_text(
        "allowed_packages:\n"
        "  - package: apps_x\n"
        "    reason: 'reason'\n",
        encoding="utf-8",
    )
    out = load_allowlist(p)
    assert out == {}


def test_is_expired_past_date() -> None:
    assert _is_expired("2020-01-01") is True


def test_is_expired_future_date() -> None:
    assert _is_expired("2099-01-01") is False


def test_is_expired_malformed_returns_true() -> None:
    """Fail-closed: malformed expires → treated as expired."""
    assert _is_expired("not-a-date") is True
    assert _is_expired("") is True


# ---------------------------------------------------------------------------
# evaluate (end-to-end pure function)
# ---------------------------------------------------------------------------


def test_evaluate_flags_violator(
    synthetic_snapshot: Path, synthetic_repo: Path, empty_allowlist: Path
) -> None:
    result = evaluate(
        snapshot=synthetic_snapshot,
        repo_root=synthetic_repo,
        allowlist_path=empty_allowlist,
    )
    assert result.packages_scanned == 3
    assert result.violations == 1
    assert result.status == "violations_present"
    pkgs = {r["package"]: r for r in result.per_package}
    assert pkgs["apps_compliant"]["is_violation"] is False
    assert pkgs["apps_compliant_two"]["is_violation"] is False
    assert pkgs["apps_violator"]["is_violation"] is True


def test_evaluate_allowlist_suppresses_violation(
    synthetic_snapshot: Path, synthetic_repo: Path, tmp_path: Path
) -> None:
    allow = tmp_path / "allow.yaml"
    allow.write_text(
        "allowed_packages:\n"
        "  - package: apps_violator\n"
        "    reason: 'Soak window — pending remediation'\n"
        "    expires: '2099-12-31'\n",
        encoding="utf-8",
    )
    result = evaluate(
        snapshot=synthetic_snapshot,
        repo_root=synthetic_repo,
        allowlist_path=allow,
    )
    assert result.violations == 0
    assert result.allowlist_active == 1
    assert result.allowlist_expired == 0
    pkgs = {r["package"]: r for r in result.per_package}
    assert pkgs["apps_violator"]["allowlisted"] is True
    assert pkgs["apps_violator"]["is_violation"] is False


def test_evaluate_expired_allowlist_does_not_suppress(
    synthetic_snapshot: Path, synthetic_repo: Path, tmp_path: Path
) -> None:
    allow = tmp_path / "allow.yaml"
    allow.write_text(
        "allowed_packages:\n"
        "  - package: apps_violator\n"
        "    reason: 'Past-expiry entry'\n"
        "    expires: '2020-01-01'\n",
        encoding="utf-8",
    )
    result = evaluate(
        snapshot=synthetic_snapshot,
        repo_root=synthetic_repo,
        allowlist_path=allow,
    )
    assert result.violations == 1
    assert result.allowlist_expired == 1
    pkgs = {r["package"]: r for r in result.per_package}
    assert pkgs["apps_violator"]["allowlisted"] is True
    assert pkgs["apps_violator"]["allowlist_expired"] is True
    assert pkgs["apps_violator"]["is_violation"] is True


# ---------------------------------------------------------------------------
# find_latest_snapshot
# ---------------------------------------------------------------------------


def test_find_latest_snapshot_skips_sentinel(tmp_path: Path) -> None:
    art = tmp_path / "artifacts" / "adg"
    art.mkdir(parents=True)
    sentinel = art / "adg_indexed_99999999_9999.sqlite"
    sentinel.write_bytes(b"")
    real = art / "adg_indexed_04302026_1319.sqlite"
    real.write_bytes(b"")
    found = find_latest_snapshot(tmp_path)
    assert found.name == "adg_indexed_04302026_1319.sqlite"


def test_find_latest_snapshot_raises_when_none(tmp_path: Path) -> None:
    (tmp_path / "artifacts" / "adg").mkdir(parents=True)
    with pytest.raises(FileNotFoundError):
        find_latest_snapshot(tmp_path)


# ---------------------------------------------------------------------------
# main() — CLI integration (advisory + strict modes)
# ---------------------------------------------------------------------------


def test_main_default_is_strict_after_w5_p51(
    synthetic_snapshot: Path, synthetic_repo: Path, empty_allowlist: Path, tmp_path: Path, monkeypatch
) -> None:
    """W5 P5.1 (2026-04-30): APPS_SPINE_DELEGATION_GATE_MODE default flipped
    advisory → strict. With no env override and no --strict flag, a real
    violation must now exit 1 (was 0 pre-P5.1)."""
    # Ensure no inherited env override leaks in from the shell / parent test.
    monkeypatch.delenv("APPS_SPINE_DELEGATION_GATE_MODE", raising=False)
    monkeypatch.delenv("APPS_SPINE_DELEGATION_GATE_BYPASS", raising=False)
    report = tmp_path / "report.json"
    rc = main([
        "--snapshot", str(synthetic_snapshot),
        "--repo-root", str(synthetic_repo),
        "--allowlist-path", str(empty_allowlist),
        "--report-path", str(report),
    ])
    assert rc == 1, "strict-by-default must exit 1 on violation"
    assert report.is_file()
    import json
    data = json.loads(report.read_text(encoding="utf-8"))
    assert data["violations"] == 1
    assert data["mode"] == "strict"


def test_main_advisory_env_rollback_returns_zero_on_violation(
    synthetic_snapshot: Path, synthetic_repo: Path, empty_allowlist: Path, tmp_path: Path, monkeypatch
) -> None:
    """W5 P5.1 rollback knob: APPS_SPINE_DELEGATION_GATE_MODE=advisory must
    revert the gate to the pre-P5.1 behavior (exit 0 on violation)."""
    monkeypatch.setenv("APPS_SPINE_DELEGATION_GATE_MODE", "advisory")
    monkeypatch.delenv("APPS_SPINE_DELEGATION_GATE_BYPASS", raising=False)
    report = tmp_path / "report.json"
    rc = main([
        "--snapshot", str(synthetic_snapshot),
        "--repo-root", str(synthetic_repo),
        "--allowlist-path", str(empty_allowlist),
        "--report-path", str(report),
    ])
    assert rc == 0, "advisory env override must exit 0 on violation"
    assert report.is_file()
    import json
    data = json.loads(report.read_text(encoding="utf-8"))
    assert data["violations"] == 1
    assert data["mode"] == "advisory"


def test_main_strict_returns_one_on_violation(
    synthetic_snapshot: Path, synthetic_repo: Path, empty_allowlist: Path, tmp_path: Path
) -> None:
    report = tmp_path / "report.json"
    rc = main([
        "--snapshot", str(synthetic_snapshot),
        "--repo-root", str(synthetic_repo),
        "--allowlist-path", str(empty_allowlist),
        "--report-path", str(report),
        "--strict",
    ])
    assert rc == 1
    data = __import__("json").loads(report.read_text(encoding="utf-8"))
    assert data["mode"] == "strict"
    assert data["violations"] == 1


def test_main_strict_returns_zero_when_clean(
    synthetic_repo: Path, empty_allowlist: Path, tmp_path: Path
) -> None:
    """If only compliant packages exist, strict mode also exits 0."""
    # Build a snapshot with no violator package.
    snap = tmp_path / "clean.sqlite"
    con = sqlite3.connect(snap)
    con.executescript(SCHEMA)
    l0 = _seed_node(con, "agentic_core.L0_routing.x", "agentic_core/L0_routing/x.py")
    src = _seed_node(con, "apps_compliant.x", "apps_compliant/x.py")
    _seed_edge(con, src, l0, "apps_compliant/x.py")
    con.commit()
    con.close()

    # Restrict repo to the compliant package.
    repo = tmp_path / "clean_repo"
    repo.mkdir()
    (repo / "apps_compliant").mkdir()

    report = tmp_path / "clean_report.json"
    rc = main([
        "--snapshot", str(snap),
        "--repo-root", str(repo),
        "--allowlist-path", str(empty_allowlist),
        "--report-path", str(report),
        "--strict",
    ])
    assert rc == 0
    data = __import__("json").loads(report.read_text(encoding="utf-8"))
    assert data["violations"] == 0


def test_main_bypass_env_returns_zero(
    synthetic_snapshot: Path, synthetic_repo: Path, empty_allowlist: Path, tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setenv("APPS_SPINE_DELEGATION_GATE_BYPASS", "1")
    report = tmp_path / "bypass.json"
    rc = main([
        "--snapshot", str(synthetic_snapshot),
        "--repo-root", str(synthetic_repo),
        "--allowlist-path", str(empty_allowlist),
        "--report-path", str(report),
        "--strict",
    ])
    # Bypass: even with --strict and a real violator, exit 0.
    assert rc == 0


def test_main_mode_env_strict(
    synthetic_snapshot: Path, synthetic_repo: Path, empty_allowlist: Path, tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setenv("APPS_SPINE_DELEGATION_GATE_MODE", "strict")
    monkeypatch.delenv("APPS_SPINE_DELEGATION_GATE_BYPASS", raising=False)
    report = tmp_path / "envstrict.json"
    rc = main([
        "--snapshot", str(synthetic_snapshot),
        "--repo-root", str(synthetic_repo),
        "--allowlist-path", str(empty_allowlist),
        "--report-path", str(report),
    ])
    assert rc == 1
