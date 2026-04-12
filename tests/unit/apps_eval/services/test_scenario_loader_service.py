"""Test ScenarioLoaderService functionality."""

import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestScenarioLoaderService:
    """Test ScenarioLoaderService functionality."""

    def test_init_with_config(self):
        """Test initialization with config."""
        from apps_eval.services.scenario_loader_service import ScenarioLoaderService

        config = {"max_scenarios": 100}
        service = ScenarioLoaderService(config)
        assert service.config == config

    def test_init_without_config(self):
        """Test initialization without config."""
        from apps_eval.services.scenario_loader_service import ScenarioLoaderService

        service = ScenarioLoaderService()
        assert service.config == {}
        assert service._scenarios == {}

    def test_load_from_file_valid(self):
        """Test loading scenarios from a valid JSON file."""
        from apps_eval.services.scenario_loader_service import ScenarioLoaderService

        with TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "scenarios.json"
            test_data = {
                "scenarios": [
                    {
                        "scenario_id": "test_1",
                        "description": "Test scenario 1",
                        "expected_behavior": "Pass",
                    },
                    {
                        "scenario_id": "test_2",
                        "description": "Test scenario 2",
                        "expected_behavior": "Fail",
                    },
                ],
            }
            file_path.write_text(json.dumps(test_data), encoding="utf-8")

            service = ScenarioLoaderService()
            scenarios = service.load_from_file(str(file_path))

            assert len(scenarios) == 2
            assert scenarios[0]["scenario_id"] == "test_1"
            assert len(service._scenarios) == 2

    def test_load_from_file_not_found(self):
        """Test loading from non-existent file raises FileNotFoundError."""
        from apps_eval.services.scenario_loader_service import ScenarioLoaderService

        service = ScenarioLoaderService()
        with pytest.raises(FileNotFoundError, match="Scenario file not found"):
            service.load_from_file("/nonexistent/path.json")

    def test_load_from_file_invalid_json(self):
        """Test loading from invalid JSON raises JSONDecodeError."""
        from apps_eval.services.scenario_loader_service import ScenarioLoaderService

        with TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "invalid.json"
            file_path.write_text("{ invalid json }", encoding="utf-8")

            service = ScenarioLoaderService()
            with pytest.raises(json.JSONDecodeError):
                service.load_from_file(str(file_path))

    def test_load_from_file_empty_scenarios(self):
        """Test loading file with empty scenarios list."""
        from apps_eval.services.scenario_loader_service import ScenarioLoaderService

        with TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "empty.json"
            test_data = {"scenarios": []}
            file_path.write_text(json.dumps(test_data), encoding="utf-8")

            service = ScenarioLoaderService()
            scenarios = service.load_from_file(str(file_path))

            assert len(scenarios) == 0
            assert len(service._scenarios) == 0

    def test_load_from_file_missing_scenarios_key(self):
        """Test loading file without scenarios key returns empty list."""
        from apps_eval.services.scenario_loader_service import ScenarioLoaderService

        with TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "no_scenarios.json"
            test_data = {"other_key": "value"}
            file_path.write_text(json.dumps(test_data), encoding="utf-8")

            service = ScenarioLoaderService()
            scenarios = service.load_from_file(str(file_path))

            assert len(scenarios) == 0

    def test_load_from_file_scenario_without_id(self):
        """Test loading scenarios without explicit IDs auto-generates them."""
        from apps_eval.services.scenario_loader_service import ScenarioLoaderService

        with TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "no_id.json"
            test_data = {
                "scenarios": [
                    {
                        "description": "Test scenario",
                        "expected_behavior": "Pass",
                    },
                ],
            }
            file_path.write_text(json.dumps(test_data), encoding="utf-8")

            service = ScenarioLoaderService()
            scenarios = service.load_from_file(str(file_path))

            assert len(scenarios) == 1
            assert "scen_0" in service._scenarios

    def test_load_from_directory_valid(self):
        """Test loading scenarios from a directory."""
        from apps_eval.services.scenario_loader_service import ScenarioLoaderService

        with TemporaryDirectory() as tmpdir:
            file1 = Path(tmpdir) / "scenarios1.json"
            file2 = Path(tmpdir) / "scenarios2.json"

            test_data1 = {
                "scenarios": [{"scenario_id": "test_1", "description": "Test 1", "expected_behavior": "Pass"}]
            }
            test_data2 = {
                "scenarios": [{"scenario_id": "test_2", "description": "Test 2", "expected_behavior": "Pass"}]
            }

            file1.write_text(json.dumps(test_data1), encoding="utf-8")
            file2.write_text(json.dumps(test_data2), encoding="utf-8")

            service = ScenarioLoaderService()
            scenarios = service.load_from_directory(tmpdir)

            assert len(scenarios) == 2

    def test_load_from_directory_not_found(self):
        """Test loading from non-existent directory raises FileNotFoundError."""
        from apps_eval.services.scenario_loader_service import ScenarioLoaderService

        service = ScenarioLoaderService()
        with pytest.raises(FileNotFoundError, match="Scenario directory not found"):
            service.load_from_directory("/nonexistent/directory")

    def test_load_from_directory_empty(self):
        """Test loading from empty directory returns empty list."""
        from apps_eval.services.scenario_loader_service import ScenarioLoaderService

        with TemporaryDirectory() as tmpdir:
            service = ScenarioLoaderService()
            scenarios = service.load_from_directory(tmpdir)
            assert len(scenarios) == 0

    def test_load_from_directory_with_non_json_files(self):
        """Test loading from directory with non-JSON files ignores them."""
        from apps_eval.services.scenario_loader_service import ScenarioLoaderService

        with TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "readme.txt").write_text("Not a JSON file")

            service = ScenarioLoaderService()
            scenarios = service.load_from_directory(tmpdir)
            assert len(scenarios) == 0

    def test_get_scenario_existing(self):
        """Test getting an existing scenario by ID."""
        from apps_eval.services.scenario_loader_service import ScenarioLoaderService

        with TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "scenarios.json"
            test_data = {
                "scenarios": [
                    {
                        "scenario_id": "test_1",
                        "description": "Test scenario 1",
                        "expected_behavior": "Pass",
                    },
                ],
            }
            file_path.write_text(json.dumps(test_data), encoding="utf-8")

            service = ScenarioLoaderService()
            service.load_from_file(str(file_path))

            scenario = service.get_scenario("test_1")
            assert scenario is not None
            assert scenario["description"] == "Test scenario 1"

    def test_get_scenario_nonexistent(self):
        """Test getting a non-existent scenario returns None."""
        from apps_eval.services.scenario_loader_service import ScenarioLoaderService

        service = ScenarioLoaderService()
        scenario = service.get_scenario("nonexistent")
        assert scenario is None

    def test_get_all_scenarios(self):
        """Test getting all loaded scenarios."""
        from apps_eval.services.scenario_loader_service import ScenarioLoaderService

        with TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "scenarios.json"
            test_data = {
                "scenarios": [
                    {
                        "scenario_id": "test_1",
                        "description": "Test scenario 1",
                        "expected_behavior": "Pass",
                    },
                    {
                        "scenario_id": "test_2",
                        "description": "Test scenario 2",
                        "expected_behavior": "Fail",
                    },
                ],
            }
            file_path.write_text(json.dumps(test_data), encoding="utf-8")

            service = ScenarioLoaderService()
            service.load_from_file(str(file_path))

            all_scenarios = service.get_all_scenarios()
            assert len(all_scenarios) == 2

    def test_validate_scenario_valid(self):
        """Test validating a valid scenario."""
        from apps_eval.services.scenario_loader_service import ScenarioLoaderService

        service = ScenarioLoaderService()
        scenario = {
            "scenario_id": "test_1",
            "description": "Test scenario",
            "expected_behavior": "Pass",
        }
        is_valid, errors = service.validate_scenario(scenario)
        assert is_valid is True
        assert len(errors) == 0

    def test_validate_scenario_missing_id(self):
        """Test validating scenario missing scenario_id."""
        from apps_eval.services.scenario_loader_service import ScenarioLoaderService

        service = ScenarioLoaderService()
        scenario = {
            "description": "Test scenario",
            "expected_behavior": "Pass",
        }
        is_valid, errors = service.validate_scenario(scenario)
        assert is_valid is False
        assert "Missing required field: scenario_id" in errors

    def test_validate_scenario_missing_description(self):
        """Test validating scenario missing description."""
        from apps_eval.services.scenario_loader_service import ScenarioLoaderService

        service = ScenarioLoaderService()
        scenario = {
            "scenario_id": "test_1",
            "expected_behavior": "Pass",
        }
        is_valid, errors = service.validate_scenario(scenario)
        assert is_valid is False
        assert "Missing required field: description" in errors

    def test_validate_scenario_missing_expected_behavior(self):
        """Test validating scenario missing expected_behavior."""
        from apps_eval.services.scenario_loader_service import ScenarioLoaderService

        service = ScenarioLoaderService()
        scenario = {
            "scenario_id": "test_1",
            "description": "Test scenario",
        }
        is_valid, errors = service.validate_scenario(scenario)
        assert is_valid is False
        assert "Missing required field: expected_behavior" in errors

    def test_validate_scenario_all_missing(self):
        """Test validating scenario with all required fields missing."""
        from apps_eval.services.scenario_loader_service import ScenarioLoaderService

        service = ScenarioLoaderService()
        scenario = {}
        is_valid, errors = service.validate_scenario(scenario)
        assert is_valid is False
        assert len(errors) == 3

    def test_validate_scenario_empty_string_fields(self):
        """Test validating scenario with empty string fields."""
        from apps_eval.services.scenario_loader_service import ScenarioLoaderService

        service = ScenarioLoaderService()
        scenario = {
            "scenario_id": "",
            "description": "",
            "expected_behavior": "",
        }
        # Empty strings are present, so validation passes
        is_valid, _errors = service.validate_scenario(scenario)
        assert is_valid is True

    @patch("apps_eval.services.scenario_loader_service._emit_snapshots_state")
    def test_init_emits_state_snapshot(self, mock_emit):
        """Test that initialization emits state snapshot."""
        from apps_eval.services.scenario_loader_service import ScenarioLoaderService

        ScenarioLoaderService()
        mock_emit.assert_called_once_with("p0", "scenario_loader", "init")
