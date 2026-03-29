#!/usr/bin/env python3
"""Tests for execute_ssot.py exception handling paths."""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import the module we're testing
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "agentic_core" / "L0_routing" / "scripts"))

try:
    from execute_ssot import main
    CAN_IMPORT = True
except ImportError as e:
    print(f"Cannot import execute_ssot: {e}")
    CAN_IMPORT = False


class TestExecuteSsotExceptionHandling:
    """Test exception handling in execute_ssot.py."""

    @pytest.mark.skipif(not CAN_IMPORT, reason="Cannot import execute_ssot")
    def test_missing_file_error_handling(self):
        """Test proper error handling for missing configuration files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Use non-existent config file
            config_path = Path(temp_dir) / "non_existent.json"

            # Mock sys.argv to pass the config path
            with patch('sys.argv', ['execute_ssot', str(config_path)]):
                # Should raise specific error, not crash silently
                with pytest.raises((FileNotFoundError, SystemExit)):
                    main()

    @pytest.mark.skipif(not CAN_IMPORT, reason="Cannot import execute_ssot")
    def test_invalid_json_error_handling(self):
        """Test proper error handling for invalid JSON configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create invalid JSON file
            config_path = Path(temp_dir) / "invalid.json"
            config_path.write_text("{ invalid json content")

            # Mock sys.argv to pass the config path
            with patch('sys.argv', ['execute_ssot', str(config_path)]):
                # Should raise specific error, not crash silently
                with pytest.raises((ValueError, SystemExit)):  # JSON parsing error
                    main()

    @pytest.mark.skipif(not CAN_IMPORT, reason="Cannot import execute_ssot")
    def test_logging_error_visibility(self):
        """Test that errors are properly logged, not silently swallowed."""
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
