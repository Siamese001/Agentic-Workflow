"""Micro-eval for the canonical SQLite seal at the GraphDB boundary."""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import networkx as nx

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.graphdb import project_graph as project_graph_module  # noqa: E402


def test_project_graph_seals_before_opening_projector(tmp_path: Path, monkeypatch) -> None:
    sqlite_path = tmp_path / "adg.sqlite"
    sqlite_path.touch()
    output_dir = tmp_path / "out"
    events: list[str] = []

    def _refresh_health(path: Path):
        assert path == sqlite_path
        events.append("phase_g")
        return {
            "mv_repo_health_signals": 21,
            "mv_repo_health_hotspots": 2,
        }

    def _seal(path: Path):
        assert path == sqlite_path
        events.append("seal")
        return SimpleNamespace(
            quick_check="ok",
            journal_mode="wal",
            wal_busy=0,
            user_version=2,
        )

    class _Projector:
        def __init__(self, path: Path) -> None:
            assert path == sqlite_path
            events.append("projector")

        def project_graph(self) -> nx.DiGraph:
            graph = nx.DiGraph()
            graph.add_edge("a", "b")
            return graph

        def validate_projection(self, _graph: nx.DiGraph) -> list[str]:
            return []

    class _Snapshots:
        def __init__(self, path: Path) -> None:
            assert path == output_dir

        def create_metadata(self, **kwargs):
            assert kwargs["schema_version"] == "adg-sqlite-v2"
            return SimpleNamespace(
                commit_sha="sha",
                run_id="run",
                timestamp="timestamp",
                node_count=2,
                edge_count=1,
            )

        def save_snapshot(self, _graph, _metadata) -> Path:
            return output_dir / "graph.json"

        def cleanup_old_snapshots(self, *, keep_count: int) -> list[Path]:
            assert keep_count == 30
            return []

    monkeypatch.setattr(project_graph_module, "materialize_phase_g", _refresh_health)
    monkeypatch.setattr(project_graph_module, "seal_sqlite_path", _seal)
    monkeypatch.setattr(project_graph_module, "GraphProjector", _Projector)
    monkeypatch.setattr(project_graph_module, "SnapshotManager", _Snapshots)
    monkeypatch.setattr(project_graph_module, "get_git_info", lambda _root: ("sha", "tree"))
    monkeypatch.setattr(project_graph_module, "get_scanner_digest", lambda: "scanner")

    graph, metadata = project_graph_module.project_graph(sqlite_path, output_dir, run_id="run")

    assert events[:3] == ["phase_g", "seal", "projector"]
    assert graph.number_of_nodes() == 2
    assert metadata.commit_sha == "sha"
