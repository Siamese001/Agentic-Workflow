from tools.otel.otel_projection import convert_snapshot_to_adg_edges


def test_convert_snapshot_to_adg_edges_projects_parent_child_edges():
    snapshot = {
        "nodes": [
            {
                "span_id": "root",
                "name": "root.span",
                "layer": "L3",
                "component": "Root",
                "started_at_utc": 100,
            },
            {
                "span_id": "child",
                "parent_span_id": "root",
                "name": "child.span",
                "layer": "L2",
                "component": "Child",
                "started_at_utc": 200,
                "status": "ok",
                "duration_ms": 11,
            },
        ]
    }

    edges = convert_snapshot_to_adg_edges(snapshot)

    assert len(edges) == 1
    assert edges[0]["source"] == "root.span"
    assert edges[0]["target"] == "child.span"
    assert edges[0]["relation_type"] == "parent_child"
