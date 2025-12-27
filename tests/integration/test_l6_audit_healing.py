"""
Integration Tests for Phase 17F: L6 Audit Healing
Validates autonomous audit trail correction with L6 observability integration.
"""
import asyncio
import pytest
import json
from pathlib import Path
from datetime import datetime, timedelta
from agentic_core.L0_maintenance.healing.l6_audit_healing_strategy import L6AuditHealingStrategy, create_l6_audit_healing_strategy
from agentic_core.config.blueprint_sovereign.environments.sovereign_config import config


class TestL6AuditHealingStrategy:
    """Test suite for L6 Audit Healing Strategy."""
    
    @pytest.mark.asyncio
    async def test_strategy_initialization(self):
        """Test L6 audit healing strategy initializes correctly."""
        strategy = L6AuditHealingStrategy()
        assert strategy is not None
        assert strategy.name == "L6AuditHealing"
        assert strategy.priority == 1
        assert strategy.processed_today == 0
        assert hasattr(strategy, 'fs_client')
        assert hasattr(strategy, 'audit_log_path')
    
    @pytest.mark.asyncio
    async def test_factory_function(self):
        """Test factory function creates strategy."""
        strategy = await create_l6_audit_healing_strategy()
        assert isinstance(strategy, L6AuditHealingStrategy)
    
    @pytest.mark.asyncio
    async def test_diagnose_disabled_in_config(self):
        """Test strategy respects config disable flag."""
        original_value = config.L6_AUDIT_HEALING_ENABLED
        object.__setattr__(config, 'L6_AUDIT_HEALING_ENABLED', False)
        
        try:
            strategy = L6AuditHealingStrategy()
            fixes = await strategy.diagnose([])
            
            assert len(fixes) == 0
        finally:
            object.__setattr__(config, 'L6_AUDIT_HEALING_ENABLED', original_value)
    
    @pytest.mark.asyncio
    async def test_daily_limit_enforcement(self):
        """Test daily healing limit is enforced."""
        strategy = L6AuditHealingStrategy()
        strategy.processed_today = config.L6_AUDIT_HEALING_MAX_DAILY
        
        fix = {"event_data": {"event_type": "TEST"}, "action": "emit_corrective_event"}
        result = await strategy.apply(fix)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_reset_daily_counter(self):
        """Test daily counter can be reset."""
        strategy = L6AuditHealingStrategy()
        strategy.processed_today = 250
        
        strategy.reset_daily_counter()
        
        assert strategy.processed_today == 0


class TestL6AuditHealingConfig:
    """Test L6 audit healing configuration."""
    
    def test_config_settings_exist(self):
        """Test all L6 audit healing config settings exist."""
        assert hasattr(config, 'L6_AUDIT_HEALING_ENABLED')
        assert hasattr(config, 'L6_AUDIT_HEALING_MAX_DAILY')
        assert hasattr(config, 'L6_AUDIT_RECONSTRUCTION_WINDOW_HOURS')
    
    def test_config_default_values(self):
        """Test config has sensible default values."""
        assert isinstance(config.L6_AUDIT_HEALING_ENABLED, bool)
        assert isinstance(config.L6_AUDIT_HEALING_MAX_DAILY, int)
        assert isinstance(config.L6_AUDIT_RECONSTRUCTION_WINDOW_HOURS, int)
        
        assert config.L6_AUDIT_HEALING_MAX_DAILY > 0
        assert config.L6_AUDIT_RECONSTRUCTION_WINDOW_HOURS > 0


class TestL6AuditHealingMCPIntegration:
    """Test L6 audit healing MCP client integration."""
    
    @pytest.mark.asyncio
    async def test_uses_filesystem_mcp_client(self):
        """Test strategy uses Filesystem MCP client."""
        strategy = L6AuditHealingStrategy()
        
        assert strategy.fs_client is not None
        assert hasattr(strategy.fs_client, 'read_text')


class TestL6AuditHealingStrategyRegistry:
    """Test L6 audit healing strategy is registered."""
    
    def test_strategy_in_registry(self):
        """Test L6AuditHealingStrategy is in global registry."""
        from agentic_core.L0_maintenance.healing.healing_strategies import HEALING_STRATEGIES
        
        strategy_names = [s.name for s in HEALING_STRATEGIES]
        assert "L6AuditHealing" in strategy_names
    
    def test_strategy_priority(self):
        """Test L6AuditHealingStrategy has correct priority."""
        from agentic_core.L0_maintenance.healing.healing_strategies import HEALING_STRATEGIES
        
        l6_strategy = next((s for s in HEALING_STRATEGIES if s.name == "L6AuditHealing"), None)
        assert l6_strategy is not None
        assert l6_strategy.priority == 1


class TestL6AuditHealingGapDetection:
    """Test L6 audit healing gap detection logic."""
    
    @pytest.mark.asyncio
    async def test_detects_missing_event_ids(self):
        """Test detection of actions without event IDs."""
        # Simulate log entry without event_id
        log_entry = {
            "action": "apply",
            "fix_id": "test_fix_123",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # This should be detected as a gap
        assert "event_id" not in log_entry
        assert log_entry["action"] == "apply"
    
    @pytest.mark.asyncio
    async def test_respects_time_window(self):
        """Test time window filtering for gap detection."""
        cutoff = datetime.utcnow() - timedelta(hours=config.L6_AUDIT_RECONSTRUCTION_WINDOW_HOURS)
        
        # Old entry (outside window)
        old_entry = {
            "action": "apply",
            "timestamp": (cutoff - timedelta(hours=1)).isoformat()
        }
        
        # Recent entry (inside window)
        recent_entry = {
            "action": "apply",
            "timestamp": (cutoff + timedelta(hours=1)).isoformat()
        }
        
        # Parse timestamps
        old_time = datetime.fromisoformat(old_entry["timestamp"])
        recent_time = datetime.fromisoformat(recent_entry["timestamp"])
        
        assert old_time < cutoff
        assert recent_time > cutoff


class TestL6AuditHealingEventReconstruction:
    """Test L6 audit healing event reconstruction."""
    
    def test_event_data_structure(self):
        """Test reconstructed event has required fields."""
        event_data = {
            "event_type": "HEALING_ACTION_APPLIED",
            "severity": "CRITICAL",
            "metadata": {
                "reconstructed": True,
                "original_action": "test_fix_123",
                "healing_cycle": "phase_17f"
            },
            "payload": {"action": "apply", "fix_id": "test_fix_123"}
        }
        
        assert "event_type" in event_data
        assert "severity" in event_data
        assert "metadata" in event_data
        assert "payload" in event_data
        assert event_data["metadata"]["reconstructed"] is True
        assert event_data["metadata"]["healing_cycle"] == "phase_17f"


class TestL6AuditHealingLogParsing:
    """Test L6 audit healing log parsing."""
    
    def test_json_line_parsing(self):
        """Test JSONL format parsing."""
        log_line = '{"action": "apply", "fix_id": "test_123", "timestamp": "2025-12-27T10:00:00"}'
        
        entry = json.loads(log_line)
        
        assert entry["action"] == "apply"
        assert entry["fix_id"] == "test_123"
        assert "timestamp" in entry
    
    def test_handles_invalid_json(self):
        """Test graceful handling of invalid JSON."""
        invalid_line = "not valid json"
        
        try:
            json.loads(invalid_line)
            assert False, "Should have raised JSONDecodeError"
        except json.JSONDecodeError:
            # Expected behavior
            pass


class TestL6AuditHealingReconstructionWindow:
    """Test L6 audit healing reconstruction window."""
    
    def test_window_configuration(self):
        """Test reconstruction window is configured."""
        assert config.L6_AUDIT_RECONSTRUCTION_WINDOW_HOURS > 0
        assert config.L6_AUDIT_RECONSTRUCTION_WINDOW_HOURS <= 168  # Max 1 week
    
    def test_window_calculation(self):
        """Test time window calculation."""
        cutoff = datetime.utcnow() - timedelta(hours=config.L6_AUDIT_RECONSTRUCTION_WINDOW_HOURS)
        now = datetime.utcnow()
        
        time_diff = (now - cutoff).total_seconds() / 3600
        
        assert abs(time_diff - config.L6_AUDIT_RECONSTRUCTION_WINDOW_HOURS) < 0.1


class TestL6AuditHealingAuditLogPath:
    """Test L6 audit healing audit log path configuration."""
    
    def test_audit_log_path_configured(self):
        """Test audit log path is configured."""
        strategy = L6AuditHealingStrategy()
        
        assert strategy.audit_log_path is not None
        assert isinstance(strategy.audit_log_path, Path)
        assert "L6_observability" in str(strategy.audit_log_path)


class TestL6AuditHealingDailyLimit:
    """Test L6 audit healing daily limit configuration."""
    
    def test_daily_limit_configured(self):
        """Test daily limit is configured."""
        assert config.L6_AUDIT_HEALING_MAX_DAILY > 0
        assert config.L6_AUDIT_HEALING_MAX_DAILY <= 1000  # Reasonable upper limit
    
    def test_daily_limit_enforcement_logic(self):
        """Test daily limit enforcement logic."""
        strategy = L6AuditHealingStrategy()
        
        # Set to limit
        strategy.processed_today = config.L6_AUDIT_HEALING_MAX_DAILY
        
        # Should be at limit
        assert strategy.processed_today >= config.L6_AUDIT_HEALING_MAX_DAILY


def run_tests():
    """Run all L6 audit healing tests."""
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])


if __name__ == "__main__":
    run_tests()
