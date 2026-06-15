"""Guard (config-ssot plan W4): EnvironmentConfig.HIVE_MIND_STRICT_MODE's declared default stays
aligned to the canonical STRICT (True) default.

The live runtime consumer is agentic_core/L4_state/utils/memory/semantic_cache_manager.py, which
reads os.environ["HIVE_MIND_STRICT_MODE"] directly with default "true" (fail-fast on infra failure).
This pydantic field is currently UNREAD; it previously declared default=False, contradicting the real
default. This test prevents re-introducing that contradiction. Operators degrade gracefully by setting
HIVE_MIND_STRICT_MODE=false in the environment (an explicit override, not the default)."""
from __future__ import annotations

from apps_shared.config.environment_config import EnvironmentConfig


def test_hive_mind_strict_mode_declared_default_is_strict():
    field = EnvironmentConfig.model_fields["HIVE_MIND_STRICT_MODE"]
    assert field.default is True, (
        "HIVE_MIND_STRICT_MODE declared default must stay True (strict) to match the canonical "
        "runtime default in semantic_cache_manager (os.environ default 'true'); do not revert to False."
    )
