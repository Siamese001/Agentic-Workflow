#!/usr/bin/env python3
"""Tests for execute_ssot.py exception handling paths."""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock


# Lazy import fixture
@pytest.fixture
def execute_ssot_main():
    """Lazily import execute_ssot main function."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "agentic_core" / "L0_routing" / "scripts"))
    try:
        from execute_ssot import main
        return main, True
    except ImportError as e:
        print(f"Cannot import execute_ssot: {e}")
        return None, False


class TestExecuteSsotExceptionHandling:
    """Test exception handling in execute_ssot.py."""

    def test_missing_file_error_handling(self, execute_ssot_main):
        """Test proper error handling for missing configuration files."""
        main, can_import = execute_ssot_main
        if not can_import:
            pytest.skip("Cannot import execute_ssot")
            
        with tempfile.TemporaryDirectory() as temp_dir:
            # Use non-existent config file
            config_path = Path(temp_dir) / "non_existent.json"

            # Mock sys.argv to pass the config path
            with patch('sys.argv', ['execute_ssot', str(config_path)]):
                # Should raise specific error, not crash silently
                with pytest.raises((FileNotFoundError, SystemExit)):
                    main()

    def test_invalid_json_error_handling(self, execute_ssot_main):
        """Test proper error handling for invalid JSON configuration."""
        main, can_import = execute_ssot_main
        if not can_import:
            pytest.skip("Cannot import execute_ssot")
            
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create invalid JSON file
            config_path = Path(temp_dir) / "invalid.json"
            config_path.write_text("{ invalid json content")

            # Mock sys.argv to pass the config path
            with patch('sys.argv', ['execute_ssot', str(config_path)]):
                # Should raise specific error, not crash silently
                with pytest.raises((ValueError, SystemExit)):  # JSON parsing error
                    main()

    def test_logging_error_visibility(self, execute_ssot_main):
        """Test that errors are properly logged, not silently swallowed."""
        main, can_import = execute_ssot_main
        if not can_import:
            pytest.skip("Cannot import execute_ssot")
            
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.json"
            config_path.write_text('{"pipeline_type": "test"}')

            # Mock logger to capture error messages
            with patch('execute_ssot.logging.getLogger') as mock_logger:
                mock_logger_instance = MagicMock()
                mock_logger.return_value = mock_logger_instance

                # Mock sys.argv
                with patch('sys.argv', ['execute_ssot', str(config_path)]):
                    # Force an error in main execution
                    with patch('execute_ssot._load_config') as mock_load:
                        mock_load.side_effect = RuntimeError("Test error")

                        # Should handle error with logging
                        with pytest.raises((RuntimeError, SystemExit)):
                            main()

                    # Verify error was logged
                    mock_logger_instance.error.assert_called()
                    error_call_args = str(mock_logger_instance.error.call_args)
                    assert "Test error" in error_call_args


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
