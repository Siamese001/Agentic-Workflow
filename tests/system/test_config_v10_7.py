import pytest

from core_v10_7 import ConfigV10_7


def test_config_provides_nested_sections(config: ConfigV10_7) -> None:
    assert config.logging_config.log_level == "INFO"
    assert config.agent_stacks.enable_constitutional_review is True
    assert config.agent_stacks.conductor_max_steps == 10


def test_config_missing_section_raises_attribute_error(config: ConfigV10_7) -> None:
    with pytest.raises(AttributeError):
        _ = config.this_section_does_not_exist
