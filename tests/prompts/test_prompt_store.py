from prompts.cms.schemas import PromptSchema
from prompts.cms.store import save_prompt_version, get_prompt_version, list_versions


def test_store_round_trip(tmp_path, monkeypatch):
    # Redirect store directory to a temporary path
    from prompts.cms import store as store_mod

    monkeypatch.setattr(store_mod, "_STORE_DIR", tmp_path, raising=False)

    schema_dict = {
        "id": "test.prompt",
        "role": "system",
        "objective": "Test objective",
        "instructions": "Do the thing.",
        "version": "1.0.0",
    }

    saved = save_prompt_version("test.prompt", schema_dict, metadata={"author": "user"})
    assert isinstance(saved, PromptSchema)

    versions = list_versions("test.prompt")
    assert "1.0.0" in versions

    loaded = get_prompt_version("test.prompt", "1.0.0")
    assert loaded is not None
    assert loaded.id == "test.prompt"
