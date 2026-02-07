"""Unit tests for FileClassificationAgent.classify_file method.

Tests follow MECE principle: Mutually Exclusive, Collectively Exhaustive
coverage of classify_file method behavior.
"""

import ast
import tempfile
from pathlib import Path
import pytest
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))


class TestClassifyFile:
    """Test classify_file method - primary classification logic."""

    def test_classify_file_critical_ignores(self):
        """Test that critical ignore patterns work."""
        from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
            FileClassificationAgent,
        )

        agent = object.__new__(FileClassificationAgent)

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Test __pycache__ is ignored
            pycache_file = tmpdir / "__pycache__" / "test.py"
            pycache_file.parent.mkdir(parents=True)
            pycache_file.write_text("class Test: pass")

            result = agent.classify_file(pycache_file)
            assert result == "IGNORE"

    def test_classify_file_stub_detection_preempts_all(self):
        """Test that STUB detection has highest priority."""
        from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
            FileClassificationAgent,
        )

        agent = object.__new__(FileClassificationAgent)

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # File with NOT_AN_AGENT should be STUB even if it looks like Agent
            test_file = tmpdir / "TestAgent.py"
            test_file.write_text("# NOT_AN_AGENT\nclass TestAgent: pass\n")

            result = agent.classify_file(test_file)
            assert result == "STUB"

    def test_classify_file_base_agent_detection(self):
        """Test BASE_AGENT detection."""
        from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
            FileClassificationAgent,
        )

        agent = object.__new__(FileClassificationAgent)

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Test SovereignBaseAgent detection
            base_file = tmpdir / "SovereignBaseAgent.py"
            base_file.write_text("class SovereignBaseAgent: pass\n")

            result = agent.classify_file(base_file)
            assert result == "BASE_AGENT"

    def test_classify_file_self_detection(self):
        """Test self-detection for FileClassificationAgent."""
        from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
            FileClassificationAgent,
        )

        agent = object.__new__(FileClassificationAgent)

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Test self-detection
            self_file = tmpdir / "FileClassificationAgent.py"
            self_file.write_text("class FileClassificationAgent: pass\n")

            result = agent.classify_file(self_file)
            assert result == "SELF"

    def test_classify_file_blueprint_detection(self):
        """Test blueprint file detection."""
        from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
            FileClassificationAgent,
        )

        agent = object.__new__(FileClassificationAgent)

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Test blueprint detection
            blueprint_file = tmpdir / "structure_blueprint.py"
            blueprint_file.write_text("# Blueprint file\nclass Config: pass\n")

            result = agent.classify_file(blueprint_file)
            assert result == "BLUEPRINT"

    def test_classify_file_test_detection(self):
        """Test TEST detection with various patterns."""
        from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
            FileClassificationAgent,
        )

        agent = object.__new__(FileClassificationAgent)

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Test test_ prefix
            test_file1 = tmpdir / "test_something.py"
            test_file1.write_text("def test_case(): pass\n")

            result = agent.classify_file(test_file1)
            assert result == "TEST"

            # Test _test suffix
            test_file2 = tmpdir / "something_test.py"
            test_file2.write_text("class SomethingTest: pass\n")

            result = agent.classify_file(test_file2)
            assert result == "TEST"

            # Test unittest.TestCase inheritance
            test_file3 = tmpdir / "my_test.py"
            test_file3.write_text(
                "import unittest\nclass MyTestCase(unittest.TestCase):\n    def test_something(self): pass\n"
            )

            result = agent.classify_file(test_file3)
            assert result == "TEST"

    def test_classify_file_script_detection(self):
        """Test SCRIPT detection."""
        from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
            FileClassificationAgent,
        )

        agent = object.__new__(FileClassificationAgent)

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Test if __name__ == "__main__"
            script_file = tmpdir / "my_script.py"
            script_file.write_text("def main():\n    pass\nif __name__ == '__main__':\n    main()\n")

            result = agent.classify_file(script_file)
            assert result == "SCRIPT"

    def test_classify_file_types_detection(self):
        """Test TYPES detection."""
        from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
            FileClassificationAgent,
        )

        agent = object.__new__(FileClassificationAgent)

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Test types.py file
            types_file = tmpdir / "types.py"
            types_file.write_text("class MyType: pass\n")

            result = agent.classify_file(types_file)
            assert result == "TYPES"

            # Test private module
            private_file = tmpdir / "_internal.py"
            private_file.write_text("class Internal: pass\n")

            result = agent.classify_file(private_file)
            assert result == "TYPES"

    def test_classify_file_primary_class_centric_detection(self):
        """Test primary-class-centric detection logic."""
        from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
            FileClassificationAgent,
        )

        agent = object.__new__(FileClassificationAgent)

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Test primary class matches filename
            test_file = tmpdir / "MyClass.py"
            test_file.write_text("class MyClass:\n    pass\nclass OtherClass:\n    pass\n")

            result = agent.classify_file(test_file)
            # Should be CLASS since MyClass doesn't match special patterns
            assert result == "CLASS"

    def test_classify_file_exception_classification(self):
        """Test that Exception/Error classes are classified as CLASS."""
        from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
            FileClassificationAgent,
        )

        agent = object.__new__(FileClassificationAgent)

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Test Exception suffix
            exc_file1 = tmpdir / "MyException.py"
            exc_file1.write_text("class MyException(Exception): pass\n")

            result = agent.classify_file(exc_file1)
            assert result == "CLASS"

            # Test Error suffix
            exc_file2 = tmpdir / "MyError.py"
            exc_file2.write_text("class MyError(RuntimeError): pass\n")

            result = agent.classify_file(exc_file2)
            assert result == "CLASS"

            # Test inheritance from Exception
            exc_file3 = tmpdir / "CustomFail.py"
            exc_file3.write_text("class CustomFail(BaseException): pass\n")

            result = agent.classify_file(exc_file3)
            assert result == "CLASS"

    def test_classify_file_mixin_priority_elevation(self):
        """Test that MIXIN has elevated priority."""
        from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
            FileClassificationAgent,
        )

        agent = object.__new__(FileClassificationAgent)

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Test Mixin with orchestrator patterns - should be MIXIN
            mixin_file = tmpdir / "OrchestratorMixin.py"
            mixin_file.write_text("class OrchestratorMixin: pass\n")

            result = agent.classify_file(mixin_file)
            assert result == "MIXIN"

    def test_classify_file_agent_not_misclassified_as_script(self):
        """Test that Agents are not misclassified as SCRIPTs."""
        from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
            FileClassificationAgent,
        )

        agent = object.__new__(FileClassificationAgent)

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Agent with main guard should still be AGENT
            agent_file = tmpdir / "MyAgent.py"
            agent_file.write_text(
                "class MyAgent:\n    def run(self): pass\nif __name__ == '__main__':\n    MyAgent().run()\n"
            )

            result = agent.classify_file(agent_file)
            assert result == "AGENT"

    def test_classify_file_orchestrator_detection(self):
        """Test ORCHESTRATOR detection."""
        from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
            FileClassificationAgent,
        )

        agent = object.__new__(FileClassificationAgent)

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Test various orchestrator patterns
            patterns = [
                ("WorkflowOrchestrator.py", "class WorkflowOrchestrator: pass"),
                ("TaskCoordinator.py", "class TaskCoordinator: pass"),
                ("PipelineManager.py", "class PipelineManager: pass"),
            ]

            for filename, content in patterns:
                test_file = tmpdir / filename
                test_file.write_text(content)

                result = agent.classify_file(test_file)
                assert result == "ORCHESTRATOR", f"Failed for {filename}"

    def test_classify_file_adapter_detection(self):
        """Test ADAPTER detection."""
        from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
            FileClassificationAgent,
        )

        agent = object.__new__(FileClassificationAgent)

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Test various adapter patterns
            patterns = [
                ("DatabaseAdapter.py", "class DatabaseAdapter: pass"),
                ("PaymentStrategy.py", "class PaymentStrategy: pass"),
                ("CacheStrategy.py", "class CacheStrategy: pass"),
            ]

            for filename, content in patterns:
                test_file = tmpdir / filename
                test_file.write_text(content)

                result = agent.classify_file(test_file)
                assert result == "ADAPTER", f"Failed for {filename}"

    def test_classify_file_config_detection(self):
        """Test CONFIG detection."""
        from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
            FileClassificationAgent,
        )

        agent = object.__new__(FileClassificationAgent)

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Test config patterns
            patterns = [
                ("app_config.py", "class AppConfig: pass"),
                ("settings.py", "DATABASE = 'sqlite'"),
                ("manifest.py", "VERSION = '1.0'"),
            ]

            for filename, content in patterns:
                test_file = tmpdir / filename
                test_file.write_text(content)

                result = agent.classify_file(test_file)
                assert result == "CONFIG", f"Failed for {filename}"

    def test_classify_file_validator_detection(self):
        """Test VALIDATOR detection."""
        from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
            FileClassificationAgent,
        )

        agent = object.__new__(FileClassificationAgent)

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Test validator patterns
            patterns = [
                ("input_validator.py", "class InputValidator: pass"),
                ("data_validator.py", "def validate_data(): pass"),
                ("check_rules.py", "def check_compliance(): pass"),
            ]

            for filename, content in patterns:
                test_file = tmpdir / filename
                test_file.write_text(content)

                result = agent.classify_file(test_file)
                assert result == "VALIDATOR", f"Failed for {filename}"

    def test_classify_file_protocol_detection(self):
        """Test PROTOCOL detection."""
        from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
            FileClassificationAgent,
        )

        agent = object.__new__(FileClassificationAgent)

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Test Protocol inheritance
            protocol_file = tmpdir / "MyProtocol.py"
            protocol_file.write_text(
                "from typing import Protocol\n"
                "class MyProtocol(Protocol):\n"
                "    def method(self) -> None: ...\n"
            )

            result = agent.classify_file(protocol_file)
            assert result == "PROTOCOL"

    def test_classify_file_factory_detection(self):
        """Test FACTORY detection."""
        from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
            FileClassificationAgent,
        )

        agent = object.__new__(FileClassificationAgent)

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Test Factory suffix
            factory_file = tmpdir / "WidgetFactory.py"
            factory_file.write_text("class WidgetFactory: pass\n")

            result = agent.classify_file(factory_file)
            assert result == "FACTORY"

    def test_classify_file_agent_detection(self):
        """Test AGENT detection."""
        from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
            FileClassificationAgent,
        )

        agent = object.__new__(FileClassificationAgent)

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Test Agent suffix
            agent_file1 = tmpdir / "ProcessorAgent.py"
            agent_file1.write_text("class ProcessorAgent: pass\n")

            result = agent.classify_file(agent_file1)
            assert result == "AGENT"

            # Test Agent inheritance
            agent_file2 = tmpdir / "Worker.py"
            agent_file2.write_text("from some.base import BaseAgent\nclass Worker(BaseAgent): pass\n")

            result = agent.classify_file(agent_file2)
            assert result == "AGENT"

    def test_classify_file_gateway_detection(self):
        """Test GATEWAY detection."""
        from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
            FileClassificationAgent,
        )

        agent = object.__new__(FileClassificationAgent)

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Test Gateway suffix
            gateway_file = tmpdir / "ApiGateway.py"
            gateway_file.write_text("class ApiGateway: pass\n")

            result = agent.classify_file(gateway_file)
            assert result == "GATEWAY"

    def test_classify_file_engine_detection(self):
        """Test ENGINE detection."""
        from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
            FileClassificationAgent,
        )

        agent = object.__new__(FileClassificationAgent)

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Test Engine suffix
            engine_file = tmpdir / "ProcessEngine.py"
            engine_file.write_text("class ProcessEngine: pass\n")

            result = agent.classify_file(engine_file)
            assert result == "ENGINE"

    def test_classify_file_fallback_to_class(self):
        """Test fallback to CLASS for non-matching patterns."""
        from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
            FileClassificationAgent,
        )

        agent = object.__new__(FileClassificationAgent)

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Test generic class
            generic_file = tmpdir / "GenericClass.py"
            generic_file.write_text("class GenericClass: pass\n")

            result = agent.classify_file(generic_file)
            assert result == "CLASS"

    def test_classify_file_empty_file(self):
        """Test classification of empty Python files."""
        from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
            FileClassificationAgent,
        )

        agent = object.__new__(FileClassificationAgent)

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Test empty file
            empty_file = tmpdir / "empty.py"
            empty_file.write_text("")

            result = agent.classify_file(empty_file)
            assert result == "UTILITY"

    def test_classify_file_no_classes(self):
        """Test classification of files with no classes."""
        from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
            FileClassificationAgent,
        )

        agent = object.__new__(FileClassificationAgent)

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Test file with only functions
            func_file = tmpdir / "functions.py"
            func_file.write_text("def func1(): pass\ndef func2(): pass\nCONSTANT = 42\n")

            result = agent.classify_file(func_file)
            assert result == "UTILITY"
