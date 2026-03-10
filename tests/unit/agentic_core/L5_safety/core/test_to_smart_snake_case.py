"""Unit tests for FileClassificationAgent._to_smart_snake_case method.

Tests follow MECE principle: Mutually Exclusive, Collectively Exhaustive
coverage of _to_smart_snake_case helper method behavior.
"""

import sys
from pathlib import Path

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))


class TestToSmartSnakeCase:
    """Test _to_smart_snake_case method - acronym-preserving snake_case conversion."""

    def test_to_smart_snake_case_simple_pascal(self):
        """Test simple PascalCase to snake_case conversion."""
        from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
            FileClassificationAgent,
        )

        agent = object.__new__(FileClassificationAgent)

        # Basic PascalCase
        result = agent._to_smart_snake_case("MyClass")
        assert result == "my_class"

        # Single word
        result = agent._to_smart_snake_case("Class")
        assert result == "class"

        # Short word
        result = agent._to_smart_snake_case("Agent")
        assert result == "agent"

    def test_to_smart_snake_case_acronym_preservation(self):
        """Test that acronyms are preserved during conversion."""
        from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
            FileClassificationAgent,
        )

        agent = object.__new__(FileClassificationAgent)

        # Test common acronyms
        test_cases = [
            ("PDFLoader", "pdf_loader"),
            ("HTMLParser", "html_parser"),
            ("XMLReader", "xml_reader"),
            ("SQLExecutor", "sql_executor"),
            ("HTTPClient", "http_client"),
            ("URLBuilder", "url_builder"),
            ("JSONConverter", "json_converter"),
            ("CSVReader", "csv_reader"),
            ("PIISanitizer", "pii_sanitizer"),
            ("IDGenerator", "id_generator"),
            ("CPUProcessor", "cpu_processor"),
            ("GPUHandler", "gpu_handler"),
            ("RAMManager", "ram_manager"),
            ("OSInterface", "os_interface"),
            ("APIGateway", "api_gateway"),
        ]

        for input_name, expected in test_cases:
            result = agent._to_smart_snake_case(input_name)
            assert result == expected, f"Failed for {input_name}: expected {expected}, got {result}"

    def test_to_smart_snake_case_mixed_patterns(self):
        """Test mixed patterns with acronyms and regular words."""
        from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
            FileClassificationAgent,
        )

        agent = object.__new__(FileClassificationAgent)

        test_cases = [
            ("PDFDocumentProcessor", "pdf_document_processor"),
            ("HTMLToPDFConverter", "html_to_pdf_converter"),
            ("XMLToJSONTransformer", "xml_to_json_transformer"),
            ("SQLQueryBuilder", "sql_query_builder"),
            ("HTTPResponseHandler", "http_response_handler"),
            ("URLPathValidator", "url_path_validator"),
            ("JSONSchemaValidator", "json_schema_validator"),
            ("CSVDataProcessor", "csv_data_processor"),
            ("PIIDataExtractor", "pii_data_extractor"),
            ("IDValueGenerator", "id_value_generator"),
        ]

        for input_name, expected in test_cases:
            result = agent._to_smart_snake_case(input_name)
            assert result == expected, f"Failed for {input_name}: expected {expected}, got {result}"

    def test_to_smart_snake_case_numbers(self):
        """Test handling of numbers in names."""
        from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
            FileClassificationAgent,
        )

        agent = object.__new__(FileClassificationAgent)

        test_cases = [
            ("Class2Processor", "class2_processor"),
            ("Type3Converter", "type3_converter"),
            ("V1Engine", "v1_engine"),
            ("API2Gateway", "api2_gateway"),
            ("PDF3Reader", "pdf3_reader"),
            ("HTTP2Server", "http2_server"),
        ]

        for input_name, expected in test_cases:
            result = agent._to_smart_snake_case(input_name)
            assert result == expected, f"Failed for {input_name}: expected {expected}, got {result}"

    def test_to_smart_snake_case_already_snake_case(self):
        """Test that already snake_case input remains unchanged."""
        from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
            FileClassificationAgent,
        )

        agent = object.__new__(FileClassificationAgent)

        test_cases = [
            "my_class",
            "already_snake_case",
            "single",
            "pdf_loader",
            "html_parser",
            "api_gateway",
        ]

        for input_name in test_cases:
            result = agent._to_smart_snake_case(input_name)
            assert result == input_name, f"Failed for {input_name}: expected {input_name}, got {result}"

    def test_to_smart_snake_case_already_lowercase(self):
        """Test that already lowercase input remains unchanged."""
        from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
            FileClassificationAgent,
        )

        agent = object.__new__(FileClassificationAgent)

        test_cases = [
            "myclass",
            "lowercase",
            "singleword",
            "pdfloader",
            "htmlparser",
        ]

        for input_name in test_cases:
            result = agent._to_smart_snake_case(input_name)
            assert result == input_name, f"Failed for {input_name}: expected {input_name}, got {result}"

    def test_to_smart_snake_case_edge_cases(self):
        """Test edge cases and boundary conditions."""
        from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
            FileClassificationAgent,
        )

        agent = object.__new__(FileClassificationAgent)

        # Empty string
        result = agent._to_smart_snake_case("")
        assert result == ""

        # Single character
        result = agent._to_smart_snake_case("A")
        assert result == "a"

        # Single acronym
        result = agent._to_smart_snake_case("PDF")
        assert result == "pdf"

        # All uppercase acronym
        result = agent._to_smart_snake_case("API")
        assert result == "api"

        # Mixed single letters
        result = agent._to_smart_snake_case("ABC")
        assert result == "abc"

    def test_to_smart_snake_case_consecutive_acronyms(self):
        """Test consecutive acronyms in name."""
        from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
            FileClassificationAgent,
        )

        agent = object.__new__(FileClassificationAgent)

        test_cases = [
            ("PDFHTMLConverter", "pdfhtml_converter"),  # Consecutive acronyms not separated
            ("XMLJSONParser", "xmljson_parser"),  # Consecutive acronyms not separated
            ("HTTPSQLBridge", "httpsql_bridge"),  # Consecutive acronyms not separated
            ("APIURLBuilder", "apiurl_builder"),  # Consecutive acronyms not separated
            ("CSVXMLTransformer", "csvxml_transformer"),  # Consecutive acronyms not separated
        ]

        for input_name, expected in test_cases:
            result = agent._to_smart_snake_case(input_name)
            assert result == expected, f"Failed for {input_name}: expected {expected}, got {result}"

    def test_to_smart_snake_case_underscores_in_input(self):
        """Test handling of underscores in input."""
        from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
            FileClassificationAgent,
        )

        agent = object.__new__(FileClassificationAgent)

        # Input with underscores should remain unchanged
        test_cases = [
            "my_class_name",
            "pdf_loader_helper",
            "already_snake_case_input",
        ]

        for input_name in test_cases:
            result = agent._to_smart_snake_case(input_name)
            assert result == input_name, f"Failed for {input_name}: expected {input_name}, got {result}"

    def test_to_smart_snake_case_special_characters(self):
        """Test handling of special characters (should be treated as separators)."""
        from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
            FileClassificationAgent,
        )

        agent = object.__new__(FileClassificationAgent)

        # Note: The regex patterns might not handle all special characters
        # This test documents current behavior
        test_cases = [
            ("MyClass-Test", "my_class-_test"),  # Dash treated as separator before uppercase
            ("MyClass_Test", "my_class__test"),  # Underscore preserved
        ]

        for input_name, expected in test_cases:
            result = agent._to_smart_snake_case(input_name)
            assert result == expected, f"Failed for {input_name}: expected {expected}, got {result}"

    def test_to_smart_snake_case_real_world_examples(self):
        """Test real-world class name examples."""
        from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
            FileClassificationAgent,
        )

        agent = object.__new__(FileClassificationAgent)

        # Real-world examples from the codebase
        test_cases = [
            ("FileClassificationAgent", "file_classification_agent"),
            ("SovereignBaseAgent", "sovereign_base_agent"),
            ("AtomicExecutionMixin", "atomic_execution_mixin"),
            ("PDFProcessingEngine", "pdf_processing_engine"),
            ("HTTPResponseValidator", "http_response_validator"),
            ("JSONSchemaGenerator", "json_schema_generator"),
            ("SQLQueryOptimizer", "sql_query_optimizer"),
            ("XMLDocumentParser", "xml_document_parser"),
            ("CSVDataImporter", "csv_data_importer"),
            ("PIIDataMasker", "pii_data_masker"),
        ]

        for input_name, expected in test_cases:
            result = agent._to_smart_snake_case(input_name)
            assert result == expected, f"Failed for {input_name}: expected {expected}, got {result}"
