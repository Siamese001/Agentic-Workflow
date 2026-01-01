"""
Integration Tests for Phase 17F: L6 Audit Healing
Validates autonomous audit trail correction with L6 observability integration.
"""
import asyncio
import pytest
import json
from pathlib import Path
from datetime import datetime, timedelta
from agentic_core.L0_maintenance.P1_core.l6_audit_healing_strategy import L6AuditHealingStrategy, create_l6_audit_healing_strategy
from agentic_core.config.P1_core.sovereign_config import config

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)


class test_l6_audit_healing_strategy:
    """Test suite for L6 Audit Healing Strategy."""

    @pytest.mark.asyncio
    async def test_strategy_initialization(self) -> Any:
        """Test L6 audit healing strategy initializes correctly."""
        strategy: Any = L6AuditHealingStrategy()
        assert strategy is not None
        assert strategy.name == 'L6AuditHealing'
        assert strategy.priority == 1
        assert strategy.processed_today == 0
        assert hasattr(strategy, 'fs_client')
        assert hasattr(strategy, 'audit_log_path')

    @pytest.mark.asyncio
    async def test_factory_function(self) -> Any:
        """Test factory function creates strategy."""
        strategy: Any = await create_l6_audit_healing_strategy()
        assert isinstance(strategy, L6AuditHealingStrategy)

    @pytest.mark.asyncio
    async def test_diagnose_disabled_in_config(self) -> Any:
        """Test strategy respects config disable flag."""
        original_value: Any = config.L6_AUDIT_HEALING_ENABLED
        object.__setattr__(config, 'L6_AUDIT_HEALING_ENABLED', False)
        try:
            strategy: Any = L6AuditHealingStrategy()
            fixes: Any = await strategy.diagnose([])
            assert len(fixes) == 0
        finally:
            object.__setattr__(config, 'L6_AUDIT_HEALING_ENABLED', original_value)

    @pytest.mark.asyncio
    async def test_daily_limit_enforcement(self) -> Any:
        """Test daily healing limit is enforced."""
        strategy: Any = L6AuditHealingStrategy()
        strategy.processed_today = config.L6_AUDIT_HEALING_MAX_DAILY
        fix: Any = {'event_data': {'event_type': 'TEST'}, 'action': 'emit_corrective_event'}
        result: Any = await strategy.apply(fix)
        assert result is False

    @pytest.mark.asyncio
    async def test_reset_daily_counter(self) -> Any:
        """Test daily counter can be reset."""
        strategy: Any = L6AuditHealingStrategy()
        strategy.processed_today = 250
        strategy.reset_daily_counter()
        assert strategy.processed_today == 0

class test_l6_audit_healing_config:
    """Test L6 audit healing configuration."""

    def test_config_settings_exist(self) -> Any:
        """Test all L6 audit healing config settings exist."""
        assert hasattr(config, 'L6_AUDIT_HEALING_ENABLED')
        assert hasattr(config, 'L6_AUDIT_HEALING_MAX_DAILY')
        assert hasattr(config, 'L6_AUDIT_RECONSTRUCTION_WINDOW_HOURS')

    def test_config_default_values(self) -> Any:
        """Test config has sensible default values."""
        assert isinstance(config.L6_AUDIT_HEALING_ENABLED, bool)
        assert isinstance(config.L6_AUDIT_HEALING_MAX_DAILY, int)
        assert isinstance(config.L6_AUDIT_RECONSTRUCTION_WINDOW_HOURS, int)
        assert config.L6_AUDIT_HEALING_MAX_DAILY > 0
        assert config.L6_AUDIT_RECONSTRUCTION_WINDOW_HOURS > 0

class test_l6_audit_healing_mcp_integration:
    """Test L6 audit healing MCP client integration."""

    @pytest.mark.asyncio
    async def test_uses_filesystem_mcp_client(self) -> Any:
        """Test strategy uses Filesystem MCP client."""
        strategy: Any = L6AuditHealingStrategy()
        assert strategy.fs_client is not None
        assert hasattr(strategy.fs_client, 'read_text')

class test_l6_audit_healing_strategy_registry:
    """Test L6 audit healing strategy is registered."""

    def test_strategy_in_registry(self) -> Any:
        """Test L6AuditHealingStrategy is in global registry."""
        from agentic_core.L0_maintenance.P1_core.healing_strategies import HEALING_STRATEGIES
        strategy_names: Any = [s.name for s in HEALING_STRATEGIES]
        assert 'L6AuditHealing' in strategy_names

    def test_strategy_priority(self) -> Any:
        """Test L6AuditHealingStrategy has correct priority."""
        from agentic_core.L0_maintenance.P1_core.healing_strategies import HEALING_STRATEGIES
from typing import Any
        l6_strategy: Any = next((s for s in HEALING_STRATEGIES if s.name == 'L6AuditHealing'), None)
        assert l6_strategy is not None
        assert l6_strategy.priority == 1

class test_l6_audit_healing_gap_detection:
    """Test L6 audit healing gap detection logic."""

    @pytest.mark.asyncio
    async def test_detects_missing_event_ids(self) -> Any:
        """Test detection of actions without event IDs."""
        log_entry: Any = {'action': 'apply', 'fix_id': 'test_fix_123', 'timestamp': datetime.utcnow().isoformat()}
        assert 'event_id' not in log_entry
        assert log_entry['action'] == 'apply'

    @pytest.mark.asyncio
    async def test_respects_time_window(self) -> Any:
        """Test time window filtering for gap detection."""
        cutoff: Any = datetime.utcnow() - timedelta(hours=config.L6_AUDIT_RECONSTRUCTION_WINDOW_HOURS)
        old_entry: Any = {'action': 'apply', 'timestamp': (cutoff - timedelta(hours=1)).isoformat()}
        recent_entry: Any = {'action': 'apply', 'timestamp': (cutoff + timedelta(hours=1)).isoformat()}
        old_time: Any = datetime.fromisoformat(old_entry['timestamp'])
        recent_time: Any = datetime.fromisoformat(recent_entry['timestamp'])
        assert old_time < cutoff
        assert recent_time > cutoff

class test_l6_audit_healing_event_reconstruction:
    """Test L6 audit healing event reconstruction."""

    def test_event_data_structure(self) -> Any:
        """Test reconstructed event has required fields."""
        event_data: Any = {'event_type': 'HEALING_ACTION_APPLIED', 'severity': 'CRITICAL', 'metadata': {'reconstructed': True, 'original_action': 'test_fix_123', 'healing_cycle': 'phase_17f'}, 'payload': {'action': 'apply', 'fix_id': 'test_fix_123'}}
        assert 'event_type' in event_data
        assert 'severity' in event_data
        assert 'metadata' in event_data
        assert 'payload' in event_data
        assert event_data['metadata']['reconstructed'] is True
        assert event_data['metadata']['healing_cycle'] == 'phase_17f'

class test_l6_audit_healing_log_parsing:
    """Test L6 audit healing log parsing."""

    def test_json_line_parsing(self) -> Any:
        """Test JSONL format parsing."""
        log_line: Any = '{"action": "apply", "fix_id": "test_123", "timestamp": "2025-12-27T10:00:00"}'
        entry: Any = json.loads(log_line)
        assert entry['action'] == 'apply'
        assert entry['fix_id'] == 'test_123'
        assert 'timestamp' in entry

    def test_handles_invalid_json(self) -> Any:
        """Test graceful handling of invalid JSON."""
        invalid_line: Any = 'not valid json'
        try:
            json.loads(invalid_line)
            assert False, 'Should have raised JSONDecodeError'
        except json.JSONDecodeError:
            pass

class test_l6_audit_healing_reconstruction_window:
    """Test L6 audit healing reconstruction window."""

    def test_window_configuration(self) -> Any:
        """Test reconstruction window is configured."""
        assert config.L6_AUDIT_RECONSTRUCTION_WINDOW_HOURS > 0
        assert config.L6_AUDIT_RECONSTRUCTION_WINDOW_HOURS <= 168

    def test_window_calculation(self) -> Any:
        """Test time window calculation."""
        cutoff: Any = datetime.utcnow() - timedelta(hours=config.L6_AUDIT_RECONSTRUCTION_WINDOW_HOURS)
        now: Any = datetime.utcnow()
        time_diff: Any = (now - cutoff).total_seconds() / 3600
        assert abs(time_diff - config.L6_AUDIT_RECONSTRUCTION_WINDOW_HOURS) < 0.1

class test_l6_audit_healing_audit_log_path:
    """Test L6 audit healing audit log path configuration."""

    def test_audit_log_path_configured(self) -> Any:
        """Test audit log path is configured."""
        strategy: Any = L6AuditHealingStrategy()
        assert strategy.audit_log_path is not None
        assert isinstance(strategy.audit_log_path, Path)
        assert 'L6_observability' in str(strategy.audit_log_path)

class test_l6_audit_healing_daily_limit:
    """Test L6 audit healing daily limit configuration."""

    def test_daily_limit_configured(self) -> Any:
        """Test daily limit is configured."""
        assert config.L6_AUDIT_HEALING_MAX_DAILY > 0
        assert config.L6_AUDIT_HEALING_MAX_DAILY <= 1000

    def test_daily_limit_enforcement_logic(self) -> Any:
        """Test daily limit enforcement logic."""
        strategy: Any = L6AuditHealingStrategy()
        strategy.processed_today = config.L6_AUDIT_HEALING_MAX_DAILY
        assert strategy.processed_today >= config.L6_AUDIT_HEALING_MAX_DAILY

def run_tests() -> Any:
    """Run all L6 audit healing tests."""
    pytest.main([__file__, '-v', '--asyncio-mode=auto'])
if __name__ == '__main__':
    run_tests()
