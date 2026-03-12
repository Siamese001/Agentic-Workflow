"""ADG-driven tests for agentic_core/config/core/base_entity_config.py — fan_in=2.

Contract tests: BaseEntity and AgentConfig Pydantic models.
"""
from __future__ import annotations

import pytest
from uuid import UUID
from datetime import datetime

pytestmark = pytest.mark.unit

from agentic_core.config.core.base_entity_config import BaseEntity, AgentConfig


class TestBaseEntity:
    def test_importable(self):
        assert callable(BaseEntity)

    def test_creates_with_defaults(self):
        entity = BaseEntity()
        assert entity is not None

    def test_id_is_uuid(self):
        entity = BaseEntity()
        assert isinstance(entity.id, UUID)

    def test_created_at_is_datetime(self):
        entity = BaseEntity()
        assert isinstance(entity.created_at, datetime)

    def test_updated_at_is_datetime(self):
        entity = BaseEntity()
        assert isinstance(entity.updated_at, datetime)

    def test_id_is_frozen(self):
        entity = BaseEntity()
        original_id = entity.id
        with pytest.raises(Exception):
            entity.id = UUID("00000000-0000-0000-0000-000000000000")
        assert entity.id == original_id

    def test_extra_fields_forbidden(self):
        with pytest.raises(Exception):
            BaseEntity(nonexistent_field="value")

    def test_two_entities_have_different_ids(self):
        a = BaseEntity()
        b = BaseEntity()
        assert a.id != b.id


class TestAgentConfig:
    def test_importable(self):
        assert callable(AgentConfig)

    def test_creates_valid(self):
        cfg = AgentConfig(name="test_agent", role="executor")
        assert cfg.name == "test_agent"
        assert cfg.role == "executor"

    def test_name_min_length_enforced(self):
        with pytest.raises(Exception):
            AgentConfig(name="", role="executor")

    def test_name_max_length_enforced(self):
        with pytest.raises(Exception):
            AgentConfig(name="a" * 65, role="executor")

    def test_inherits_base_entity(self):
        cfg = AgentConfig(name="agent", role="healer")
        assert isinstance(cfg, BaseEntity)
        assert isinstance(cfg.id, UUID)

    def test_extra_fields_forbidden(self):
        with pytest.raises(Exception):
            AgentConfig(name="agent", role="healer", unknown="x")
