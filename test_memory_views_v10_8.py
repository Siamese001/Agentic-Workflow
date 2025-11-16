import copy

from memory_views import (
    get_conversational_view,
    get_prompt_context_view,
    get_retrieval_view,
)


def test_conversational_view_defaults_and_keys():
    state = {}
    view = get_conversational_view(state)

    assert set(view.keys()) == {"messages", "summary"}
    assert view["messages"] == []
    assert view["summary"] == ""
    assert state == {}


def test_retrieval_view_defaults_and_keys():
    state = {}
    view = get_retrieval_view(state)

    assert set(view.keys()) == {"rag_history", "world"}
    assert view["rag_history"] == []
    assert view["world"] == []
    assert state == {}


def test_prompt_context_view_combines_all_fields_without_mutation():
    state = {
        "messages": ["hello"],
        "summary": "s",
        "rag_history": ["rag"],
        "world": ["w"],
    }
    original_state = copy.deepcopy(state)

    view = get_prompt_context_view(state)

    assert set(view.keys()) == {"messages", "summary", "rag_history", "world"}
    assert view["messages"] == ["hello"]
    assert view["summary"] == "s"
    assert view["rag_history"] == ["rag"]
    assert view["world"] == ["w"]
    assert state == original_state


def test_views_deep_copy_list_fields():
    state = {
        "messages": [{"role": "user", "content": "hi"}],
        "rag_history": [{"doc": "a"}],
        "world": [{"fact": 1}],
    }

    conversational = get_conversational_view(state)
    retrieval = get_retrieval_view(state)
    prompt_context = get_prompt_context_view(state)

    conversational["messages"][0]["content"] = "changed"
    retrieval["rag_history"][0]["doc"] = "changed"
    retrieval["world"].append({"fact": 2})
    prompt_context["messages"].append({"role": "assistant", "content": "reply"})

    assert state["messages"][0]["content"] == "hi"
    assert state["rag_history"][0]["doc"] == "a"
    assert state["world"] == [{"fact": 1}]
