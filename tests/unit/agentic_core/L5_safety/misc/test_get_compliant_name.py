"""Unit tests for FileClassificationAgent.get_compliant_name method.

Tests follow MECE principle: Mutually Exclusive, Collectively Exhaustive
coverage of get_compliant_name method behavior.
"""

import tempfile
from pathlib import Path
import pytest
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))


class TestGetCompliantName:
    """Test get_compliant_name method - naming convention logic."""

    def test_get_compliant_name_ignore_types(self):
        """Test that IGNORE, TYPES, UTILITY return None."""
        from agentic_core.L5_safety.validators.core.FileClassificationAgent import (
            FileClassificationAgent,
        )

        agent = object.__new__(FileClassificationAgent)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            test_file = tmpdir / "test.py"
            test_file.write_text("class Test: pass")
            
            # Test IGNORE returns None
            result = agent.get_compliant_name(test_file, "IGNORE")
            assert result is None
            
            # Test TYPES returns None
            result = agent.get_compliant_name(test_file, "TYPES")
            assert result is None
            
            # Test UTILITY returns None
            result = agent.get_compliant_name(test_file, "UTILITY")
            assert result is None

    def test_get_compliant_name_script_snake_case(self):
        """Test SCRIPT files are converted to snake_case."""
        from agentic_core.L5_safety.validators.core.FileClassificationAgent import (
            FileClassificationAgent,
        )

        agent = object.__new__(FileClassificationAgent)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Test PascalCase to snake_case
            test_file = tmpdir / "MyScript.py"
            test_file.write_text("class MyScript: pass")
            
            result = agent.get_compliant_name(test_file, "SCRIPT")
            assert result == "my_script.py"
            
            # Test already snake_case returns None
            test_file2 = tmpdir / "already_snake.py"
            test_file2.write_text("class AlreadySnake: pass")
            
            result = agent.get_compliant_name(test_file2, "SCRIPT")
            assert result is None
            
            # Test acronym preservation
            test_file3 = tmpdir / "PDFLoader.py"
            test_file3.write_text("class PDFLoader: pass")
            
            result = agent.get_compliant_name(test_file3, "SCRIPT")
            assert result == "pdf_loader.py"

    def test_get_compliant_name_test_prefix(self):
        """Test TEST files get test_ prefix."""
        from agentic_core.L5_safety.validators.core.FileClassificationAgent import (
            FileClassificationAgent,
        )

        agent = object.__new__(FileClassificationAgent)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Test PascalCase to test_ prefix
            test_file = tmpdir / "MyClassTest.py"
            test_file.write_text("class MyClassTest: pass")
            
            result = agent.get_compliant_name(test_file, "TEST")
            assert result == "test_my_class.py"
            
            # Test already with test_ prefix
            test_file2 = tmpdir / "test_already.py"
            test_file2.write_text("class TestAlready: pass")
            
            result = agent.get_compliant_name(test_file2, "TEST")
            assert result is None

    def test_get_compliant_name_mixin_snake_case(self):
        """Test MIXIN files use snake_case with _mixin suffix."""
        from agentic_core.L5_safety.validators.core.FileClassificationAgent import (
            FileClassificationAgent,
        )

        agent = object.__new__(FileClassificationAgent)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Test PascalCase to snake_case
            test_file = tmpdir / "LoggingMixin.py"
            test_file.write_text("class LoggingMixin: pass")
            
            result = agent.get_compliant_name(test_file, "MIXIN")
            assert result == "logging_mixin.py"
            
            # Test acronym preservation
            test_file2 = tmpdir / "PDFProcessorMixin.py"
            test_file2.write_text("class PDFProcessorMixin: pass")
            
            result = agent.get_compliant_name(test_file2, "MIXIN")
            assert result == "pdf_processor_mixin.py"
            
            # Test adding _mixin suffix if missing
            test_file3 = tmpdir / "Helper.py"
            test_file3.write_text("class Helper: pass")
            
            # Mock classify_file to return MIXIN
            agent.classify_file = lambda x: "MIXIN"
            result = agent.get_compliant_name(test_file3, "MIXIN")
            # This would use the primary class from AST, which is "Helper"
            # and add _mixin suffix
            assert result == "helper_mixin.py"

    def test_get_compliant_name_agent_suffix(self):
        """Test AGENT files get Agent suffix."""
        from agentic_core.L5_safety.validators.core.FileClassificationAgent import (
            FileClassificationAgent,
        )

        agent = object.__new__(FileClassificationAgent)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Test without Agent suffix
            test_file = tmpdir / "Processor.py"
            test_file.write_text("class Processor: pass")
            
            result = agent.get_compliant_name(test_file, "AGENT")
            assert result == "ProcessorAgent.py"
            
            # Test already with Agent suffix
            test_file2 = tmpdir / "WorkerAgent.py"
            test_file2.write_text("class WorkerAgent: pass")
            
            result = agent.get_compliant_name(test_file2, "AGENT")
            assert result is None

    def test_get_compliant_name_protocol_passthrough(self):
        """Test PROTOCOL files remain PascalCase."""
        from agentic_core.L5_safety.validators.core.FileClassificationAgent import (
            FileClassificationAgent,
        )

        agent = object.__new__(FileClassificationAgent)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Test protocol remains unchanged
            test_file = tmpdir / "IMyProtocol.py"
            test_file.write_text("class IMyProtocol: pass")
            
            result = agent.get_compliant_name(test_file, "PROTOCOL")
            assert result is None  # No change needed

    def test_get_compliant_name_engine_passthrough(self):
        """Test ENGINE files remain PascalCase."""
        from agentic_core.L5_safety.validators.core.FileClassificationAgent import (
            FileClassificationAgent,
        )

        agent = object.__new__(FileClassificationAgent)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Test engine remains unchanged
            test_file = tmpdir / "ProcessEngine.py"
            test_file.write_text("class ProcessEngine: pass")
            
            result = agent.get_compliant_name(test_file, "ENGINE")
            assert result is None  # No change needed

    def test_get_compliant_name_gateway_passthrough(self):
        """Test GATEWAY files remain PascalCase."""
        from agentic_core.L5_safety.validators.core.FileClassificationAgent import (
            FileClassificationAgent,
        )

        agent = object.__new__(FileClassificationAgent)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Test gateway remains unchanged
            test_file = tmpdir / "ApiGateway.py"
            test_file.write_text("class ApiGateway: pass")
            
            result = agent.get_compliant_name(test_file, "GATEWAY")
            assert result is None  # No change needed

    def test_get_compliant_name_stub_agent_replacement(self):
        """Test STUB files replace Agent with Stub."""
        from agentic_core.L5_safety.validators.core.FileClassificationAgent import (
            FileClassificationAgent,
        )

        agent = object.__new__(FileClassificationAgent)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Test Agent replaced with Stub
            test_file = tmpdir / "TestAgent.py"
            test_file.write_text("class TestAgent: pass")
            
            result = agent.get_compliant_name(test_file, "STUB")
            assert result == "TestStub.py"
            
            # Test adding Stub suffix if no Agent
            test_file2 = tmpdir / "Mock.py"
            test_file2.write_text("class Mock: pass")
            
            result = agent.get_compliant_name(test_file2, "STUB")
            assert result == "MockStub.py"

    def test_get_compliant_name_orchestrator_suffix_fix(self):
        """Test ORCHESTRATOR strips Agent/Service and adds Orchestrator."""
        from agentic_core.L5_safety.validators.core.FileClassificationAgent import (
            FileClassificationAgent,
        )

        agent = object.__new__(FileClassificationAgent)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Test strip Agent suffix
            test_file = tmpdir / "WorkflowAgent.py"
            test_file.write_text("class WorkflowAgent: pass")
            
            result = agent.get_compliant_name(test_file, "ORCHESTRATOR")
            assert result == "WorkflowOrchestrator.py"
            
            # Test strip Service suffix
            test_file2 = tmpdir / "TaskService.py"
            test_file2.write_text("class TaskService: pass")
            
            result = agent.get_compliant_name(test_file2, "ORCHESTRATOR")
            assert result == "TaskOrchestrator.py"
            
            # Test add Orchestrator if missing
            test_file3 = tmpdir / "Coordinator.py"
            test_file3.write_text("class Coordinator: pass")
            
            result = agent.get_compliant_name(test_file3, "ORCHESTRATOR")
            assert result == "CoordinatorOrchestrator.py"

    def test_get_compliant_name_adapter_suffix_fix(self):
        """Test ADAPTER strips Agent and adds Strategy."""
        from agentic_core.L5_safety.validators.core.FileClassificationAgent import (
            FileClassificationAgent,
        )

        agent = object.__new__(FileClassificationAgent)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Test strip Agent suffix
            test_file = tmpdir / "DatabaseAgent.py"
            test_file.write_text("class DatabaseAgent: pass")
            
            result = agent.get_compliant_name(test_file, "ADAPTER")
            assert result == "DatabaseStrategy.py"
            
            # Test add Strategy if missing
            test_file2 = tmpdir / "Cache.py"
            test_file2.write_text("class Cache: pass")
            
            result = agent.get_compliant_name(test_file2, "ADAPTER")
            assert result == "CacheStrategy.py"

    def test_get_compliant_name_factory_suffix(self):
        """Test FACTORY files get Factory suffix."""
        from agentic_core.L5_safety.validators.core.FileClassificationAgent import (
            FileClassificationAgent,
        )

        agent = object.__new__(FileClassificationAgent)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Test add Factory suffix
            test_file = tmpdir / "Widget.py"
            test_file.write_text("class Widget: pass")
            
            result = agent.get_compliant_name(test_file, "FACTORY")
            assert result == "WidgetFactory.py"
            
            # Test already with Factory suffix
            test_file2 = tmpdir / "CarFactory.py"
            test_file2.write_text("class CarFactory: pass")
            
            result = agent.get_compliant_name(test_file2, "FACTORY")
            assert result is None

    def test_get_compliant_name_validator_snake_case(self):
        """Test VALIDATOR files use snake_case with _validator suffix."""
        from agentic_core.L5_safety.validators.core.FileClassificationAgent import (
            FileClassificationAgent,
        )

        agent = object.__new__(FileClassificationAgent)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Test PascalCase to snake_case
            test_file = tmpdir / "InputValidator.py"
            test_file.write_text("class InputValidator: pass")
            
            result = agent.get_compliant_name(test_file, "VALIDATOR")
            assert result == "input_validator.py"
            
            # Test acronym preservation
            test_file2 = tmpdir / "PDFValidator.py"
            test_file2.write_text("class PDFValidator: pass")
            
            result = agent.get_compliant_name(test_file2, "VALIDATOR")
            assert result == "pdf_validator.py"
            
            # Test add _validator suffix if missing
            test_file3 = tmpdir / "Checker.py"
            test_file3.write_text("class Checker: pass")
            
            result = agent.get_compliant_name(test_file3, "VALIDATOR")
            assert result == "checker_validator.py"

    def test_get_compliant_name_config_snake_case(self):
        """Test CONFIG files use snake_case with _config suffix."""
        from agentic_core.L5_safety.validators.core.FileClassificationAgent import (
            FileClassificationAgent,
        )

        agent = object.__new__(FileClassificationAgent)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Test PascalCase to snake_case
            test_file = tmpdir / "AppConfig.py"
            test_file.write_text("class AppConfig: pass")
            
            result = agent.get_compliant_name(test_file, "CONFIG")
            assert result == "app_config.py"
            
            # Test acronym preservation
            test_file2 = tmpdir / "PDFConfig.py"
            test_file2.write_text("class PDFConfig: pass")
            
            result = agent.get_compliant_name(test_file2, "CONFIG")
            assert result == "pdf_config.py"
            
            # Test add _config suffix if missing
            test_file3 = tmpdir / "Settings.py"
            test_file3.write_text("class Settings: pass")
            
            result = agent.get_compliant_name(test_file3, "CONFIG")
            assert result == "settings_config.py"

    def test_get_compliant_name_handles_ast_parsing_errors(self):
        """Test that AST parsing errors are handled gracefully."""
        from agentic_core.L5_safety.validators.core.FileClassificationAgent import (
            FileClassificationAgent,
        )

        agent = object.__new__(FileClassificationAgent)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Test invalid Python file
            test_file = tmpdir / "invalid.py"
            test_file.write_text("class Invalid\n    missing colon\n")
            
            # Should not crash, return None
            result = agent.get_compliant_name(test_file, "AGENT")
            assert result == "IGNORE"

    def test_get_compliant_name_no_classes_in_file(self):
        """Test behavior when file has no classes."""
        from agentic_core.L5_safety.validators.core.FileClassificationAgent import (
            FileClassificationAgent,
        )

        agent = object.__new__(FileClassificationAgent)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Test file with no classes
            test_file = tmpdir / "no_classes.py"
            test_file.write_text("def func(): pass\nCONSTANT = 42\n")
            
            result = agent.get_compliant_name(test_file, "AGENT")
            assert result is None
