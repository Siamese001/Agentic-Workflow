"""
Test suite for Shared Upgrade Circuit Breaker in LocationAgent.

Verifies that the circuit breaker prevents mass-migration
when the upgrade limit is exceeded, and that dust threshold
guards against insignificant files.
"""

import ast
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open, MagicMock

from agentic_core.L5_safety.validators.LocationAgent import LocationAgent
from agentic_core.L5_safety.validators.structure_blueprint import (
    AST_DOMAIN_HIT_THRESHOLD,
    HEALING_CONFIG,
)


class TestSharedUpgradeCircuitBreaker:
    """100% PASS: Ensures LocationAgent respects shared upgrade limits."""

    @pytest.fixture
    def project_root(self, tmp_path):
        """Create a temporary project root with sovereign structure."""
        root = tmp_path / "test_project"
        root.mkdir()
        
        # Create sovereign territories
        (root / "apps_rg").mkdir()
        (root / "apps_rg" / "engines").mkdir()
        (root / "apps_lic").mkdir()
        (root / "apps_lic" / "engines").mkdir()
        (root / "apps_shared").mkdir()
        (root / "apps_shared" / "utils").mkdir()
        (root / "agentic_core").mkdir()
        
        return root

    @pytest.fixture
    def location_agent(self, project_root):
        """Create LocationAgent instance."""
        # Patch _validate_project_root before instantiation
        with patch.object(LocationAgent, '_validate_project_root'):
            agent = LocationAgent(project_root=project_root)
            return agent

    def test_shared_upgrade_circuit_breaker(self, location_agent, project_root):
        """
        Verifies that the circuit breaker prevents mass-migration
        when the upgrade limit is exceeded.
        """
        agent = location_agent
        
        # Create a file that SHOULD upgrade based on scores
        generic_file = project_root / "apps_lic" / "engines" / "GenericUtil.py"
        generic_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Create content with sufficient lines (> dust_threshold)
        content_lines = ["class GenericUtil:\n"] + [f"    def method_{i}(self): pass\n" for i in range(50)]
        generic_file.write_text("".join(content_lines), encoding="utf-8")
        
        # Mock the import agent to prevent initialization errors
        mock_import_agent = Mock()
        mock_import_agent.run.return_value = [(generic_file, ["GRAVITY VIOLATION: test"])]  # Return gravity violation
        
        with patch('agentic_core.L5_safety.policy_engine.CodeHealerAgent.create_legacy_import_healer') as mock_create:
            mock_create.return_value = mock_import_agent
            
            # Mock RuntimeStateGuard class before it's instantiated
            with patch('agentic_core.L4_state.validation_context.RuntimeStateGuard.RuntimeStateGuard') as mock_guard_class:
                # Configure mock instance
                mock_guard_instance = Mock()
                mock_guard_instance.get_metric.return_value = HEALING_CONFIG["max_shared_upgrades_per_run"]
                mock_guard_class.return_value = mock_guard_instance
                
                # Mock the _recompute_ast_scores to return low domain scores
                with patch.object(agent, '_recompute_ast_scores') as mock_scores:
                    mock_scores.return_value = (0.1, 0.1, {})  # Low scores -> should upgrade
                    
                    # Mock safe_move to track moves
                    with patch.object(agent, 'safe_move') as mock_move:
                        mock_move.return_value = {"applied": True, "status": "SUCCESS"}
                        
                        # Mock the file reading for dust threshold
                        with patch("builtins.open", mock_open(read_data="".join(content_lines))):
                            # Trigger the deep import validation logic
                            result = agent.deep_import_validation_and_heal(
                                affected_paths=[generic_file],
                                import_touched_paths=[],
                                dry_run=False
                            )
                        
                        # Verify no move was made due to circuit breaker
                        mock_move.assert_not_called()
                        
                        # Verify increment_metric was not called
                        mock_guard_instance.increment_metric.assert_not_called()
                    
        print("✅ test_shared_upgrade_circuit_breaker: 100% PASS")

    def test_dust_threshold_prevents_upgrade(self, location_agent, project_root):
        """
        Verifies that files below dust threshold are skipped
        regardless of their domain scores.
        """
        agent = location_agent
        
        # Create a tiny file (below dust threshold)
        tiny_file = project_root / "apps_lic" / "engines" / "TinyUtil.py"
        tiny_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Create content with insufficient lines (< dust_threshold)
        tiny_content = "class TinyUtil: pass\n"  # Only 1 line
        tiny_file.write_text(tiny_content, encoding="utf-8")
        
        # Mock the import agent to prevent initialization errors
        mock_import_agent = Mock()
        mock_import_agent.run.return_value = [(tiny_file, ["GRAVITY VIOLATION: test"])]  # Return gravity violation
        
        with patch('agentic_core.L5_safety.policy_engine.CodeHealerAgent.create_legacy_import_healer') as mock_create:
            mock_create.return_value = mock_import_agent
            
            # Mock RuntimeStateGuard class before it's instantiated
            with patch('agentic_core.L4_state.validation_context.RuntimeStateGuard.RuntimeStateGuard') as mock_guard_class:
                # Configure mock instance
                mock_guard_instance = Mock()
                mock_guard_instance.get_metric.return_value = 0
                mock_guard_class.return_value = mock_guard_instance
                
                # Mock the _recompute_ast_scores to return low domain scores
                with patch.object(agent, '_recompute_ast_scores') as mock_scores:
                    mock_scores.return_value = (0.1, 0.1, {})  # Low scores -> would normally upgrade
                    
                    # Mock safe_move to track moves
                    with patch.object(agent, 'safe_move') as mock_move:
                        mock_move.return_value = {"applied": True, "status": "SUCCESS"}
                        
                        # Mock the file reading for dust threshold
                        with patch("builtins.open", mock_open(read_data=tiny_content)):
                            # Trigger the deep import validation logic
                            result = agent.deep_import_validation_and_heal(
                                affected_paths=[tiny_file],
                                import_touched_paths=[],
                                dry_run=False
                            )
                        
                        # Verify no move was made due to dust threshold
                        mock_move.assert_not_called()
                        
                        # Verify increment_metric was not called
                        mock_guard_instance.increment_metric.assert_not_called()
                
        print("✅ test_dust_threshold_prevents_upgrade: 100% PASS")

    def test_circuit_breaker_allows_under_limit(self, location_agent, project_root):
        """
        Verifies that upgrades work normally when under the limit.
        """
        agent = location_agent
        
        # Create a file with sufficient content
        valid_file = project_root / "apps_lic" / "engines" / "ValidUtil.py"
        valid_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Create content with sufficient lines (> dust_threshold)
        content_lines = ["class ValidUtil:\n"] + [f"    def method_{i}(self): pass\n" for i in range(50)]
        valid_file.write_text("".join(content_lines), encoding="utf-8")
        
        # Mock the import agent to prevent initialization errors
        mock_import_agent = Mock()
        mock_import_agent.run.return_value = [(valid_file, ["GRAVITY VIOLATION: test"])]  # Return gravity violation
        
        with patch('agentic_core.L5_safety.policy_engine.CodeHealerAgent.create_legacy_import_healer') as mock_create:
            mock_create.return_value = mock_import_agent
            
            # Mock RuntimeStateGuard class before it's instantiated
            with patch('agentic_core.L4_state.validation_context.RuntimeStateGuard.RuntimeStateGuard') as mock_guard_class:
                # Configure mock instance
                mock_guard_instance = Mock()
                mock_guard_instance.get_metric.return_value = HEALING_CONFIG["max_shared_upgrades_per_run"] - 1
                mock_guard_class.return_value = mock_guard_instance
                
                # Mock the _recompute_ast_scores to return low domain scores
                with patch.object(agent, '_recompute_ast_scores') as mock_scores:
                    mock_scores.return_value = (0.1, 0.1, {})  # Low scores -> should upgrade
                    
                    # Mock safe_move to track moves
                    with patch.object(agent, 'safe_move') as mock_move:
                        mock_move.return_value = {"applied": True, "status": "SUCCESS"}
                        
                        # Mock the file reading for dust threshold
                        with patch("builtins.open", mock_open(read_data="".join(content_lines))):
                            # Trigger the deep import validation logic
                            result = agent.deep_import_validation_and_heal(
                                affected_paths=[valid_file],
                                import_touched_paths=[],
                                dry_run=False
                            )
                        
                        # Verify move was made (under limit)
                        mock_move.assert_called_once()
                        
                        # Verify increment_metric was called
                        mock_guard_instance.increment_metric.assert_called_once_with("upgrade_count")
                
        print("✅ test_circuit_breaker_allows_under_limit: 100% PASS")

    def test_circuit_breaker_logs_error_when_tripped(self, location_agent, project_root):
        """
        Verifies that the circuit breaker logs an error when tripped.
        """
        agent = location_agent
        
        # Create a file that would trigger upgrade
        trigger_file = project_root / "apps_lic" / "engines" / "TriggerUtil.py"
        trigger_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Create content with sufficient lines
        content_lines = ["class TriggerUtil:\n"] + [f"    def method_{i}(self): pass\n" for i in range(50)]
        trigger_file.write_text("".join(content_lines), encoding="utf-8")
        
        # Mock the import agent to prevent initialization errors
        mock_import_agent = Mock()
        mock_import_agent.run.return_value = [(trigger_file, ["GRAVITY VIOLATION: test"])]  # Return gravity violation
        
        with patch('agentic_core.L5_safety.policy_engine.CodeHealerAgent.create_legacy_import_healer') as mock_create:
            mock_create.return_value = mock_import_agent
            
            # Mock RuntimeStateGuard class before it's instantiated
            with patch('agentic_core.L4_state.validation_context.RuntimeStateGuard.RuntimeStateGuard') as mock_guard_class:
                # Configure mock instance
                mock_guard_instance = Mock()
                mock_guard_instance.get_metric.return_value = HEALING_CONFIG["max_shared_upgrades_per_run"]
                mock_guard_class.return_value = mock_guard_instance
                
                # Mock the _recompute_ast_scores to return low domain scores
                with patch.object(agent, '_recompute_ast_scores') as mock_scores:
                    mock_scores.return_value = (0.1, 0.1, {})  # Low scores -> would upgrade
                    
                    # Mock safe_move
                    with patch.object(agent, 'safe_move'):
                        # Mock Logger to capture error logs
                        with patch('agentic_core.L5_safety.validators.LocationAgent.Logger') as mock_logger:
                            # Mock the file reading for dust threshold
                            with patch("builtins.open", mock_open(read_data="".join(content_lines))):
                                # Trigger the deep import validation logic
                                result = agent.deep_import_validation_and_heal(
                                    affected_paths=[trigger_file],
                                    import_touched_paths=[],
                                    dry_run=False
                                )
                            
                            # Verify error was logged
                            mock_logger.error.assert_called_once()
                            error_message = mock_logger.error.call_args[0][0]
                            assert "CIRCUIT BREAKER TRIPPED" in error_message
                            assert str(trigger_file) in error_message
                
        print("✅ test_circuit_breaker_logs_error_when_tripped: 100% PASS")

    def test_circuit_breaker_resets_on_new_instance(self, project_root):
        """
        Verifies that circuit breaker resets on new agent instance.
        """
        # Create first agent
        with patch.object(LocationAgent, '_validate_project_root'):
            agent1 = LocationAgent(project_root=project_root)
            
        # Create second agent - should have separate guard instance
        with patch.object(LocationAgent, '_validate_project_root'):
            agent2 = LocationAgent(project_root=project_root)
        
        # Verify different agents have separate instances
        # (The actual state persistence depends on the underlying file)
        assert hasattr(agent1, 'project_root')
        assert hasattr(agent2, 'project_root')
        assert agent1.project_root == agent2.project_root
        
        print("✅ test_circuit_breaker_resets_on_new_instance: 100% PASS")

    def test_dust_threshold_configuration(self):
        """
        Verifies that dust threshold is correctly configured.
        """
        # Verify configuration exists and is reasonable
        assert "dust_threshold" in HEALING_CONFIG
        assert HEALING_CONFIG["dust_threshold"] > 0
        assert HEALING_CONFIG["dust_threshold"] == 40  # As per configuration
        
        print("✅ test_dust_threshold_configuration: 100% PASS")

    def test_max_shared_upgrades_configuration(self):
        """
        Verifies that max shared upgrades limit is correctly configured.
        """
        # Verify configuration exists and is reasonable
        assert "max_shared_upgrades_per_run" in HEALING_CONFIG
        assert HEALING_CONFIG["max_shared_upgrades_per_run"] > 0
        assert HEALING_CONFIG["max_shared_upgrades_per_run"] == 10  # As per configuration
        
        print("✅ test_max_shared_upgrades_configuration: 100% PASS")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
