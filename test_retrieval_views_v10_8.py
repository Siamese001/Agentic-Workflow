import copy

from memory_views import get_evidence_view, get_retrieval_view


def test_evidence_view_keys_and_defaults():
    state = {}
    view = get_evidence_view(state)

    assert set(view.keys()) == {"rag_history", "world"}
    assert view["rag_history"] == []
    assert view["world"] == []
    assert state == {}


def test_evidence_view_deep_copy_behavior():
    state = {
        "rag_history": [{"doc": "a"}],
        "world": [{"fact": 1}],
    }
    original_state = copy.deepcopy(state)

    view = get_evidence_view(state)
    view["rag_history"][0]["doc"] = "changed"
    view["world"].append({"fact": 2})

    assert state == original_state


def test_retrieval_and_evidence_views_preserve_ordering():
    state = {
        "rag_history": ["first", "second", "third"],
        "world": ["alpha", "beta"],
    }

    retrieval_view = get_retrieval_view(state)
    evidence_view = get_evidence_view(state)

    assert retrieval_view["rag_history"] == state["rag_history"]
    assert retrieval_view["world"] == state["world"]
    assert evidence_view["rag_history"] == state["rag_history"]
    assert evidence_view["world"] == state["world"]
