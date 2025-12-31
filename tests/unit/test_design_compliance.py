#!/usr/bin/env python3
"""
Test script for the validate_design_compliance function.
This demonstrates the Canon Validator's highest-value use case.
"""

import json
import pytest

from canon_validator import CanonValidator


# Mock MCP Tools for testing
# NAMING FIXED: MockMCPTools → mock_mcp_tools
class mock_mcp_tools:
    '''Brief description of functionality and purpose.'''
    
    def read_text_file(self, path):
                    
        if path == "src/Button.tsx":
            return "import React from 'react';\nconst Button = () => <button style={{color: '#FF0000', backgroundColor: '#00FF00'}}>Click</button>;\nexport default Button;"
        elif path == "src/CleanButton.tsx":
            return "import React from 'react';\nconst Button = () => <button style={{color: 'theme.colors.danger'}}>Click</button>;\nexport default Button;"
        raise FileNotFoundError(f"File {path} not found")

    def get_variable_defs(self, node_id):
                    
        return json.dumps([
            {"name": "color-primary", "value": "#007AFF",
                "replacement": "theme.colors.primary"},
            {"name": "color-danger", "value": "#FF0000",
                "replacement": "theme.colors.danger"},
            {"name": "color-success", "value": "#00FF00",
                "replacement": "theme.colors.success"}
        ])

    def search_records(self, query, index, top_k, namespace):
                    
        # Simulating Pinecone finding the canonical replacement pattern
        return json.dumps([
            {"id": "fix-hex-to-token",
                "metadata": {"replacement_snippet": "theme.colors.danger"}}
        ])

    def edit_file(self, path, edits):
                    
        # Simulating the Filesystem MCP writing the change
        return f"File {path} edited successfully. Applied {len(edits)} edit(s): {edits}"

    def string_set(self, key, value):
                    
        # print(f"[REDIS MOCK] Cached key: {key} -> {value}")  # [Security Fix]
        return "OK"

# Mock Logger


# NAMING FIXED: MockLogger → mock_logger
class mock_logger:
    '''Brief description of functionality and purpose.'''
    
    pass
    # def info(self, msg): print(f"[INFO] {msg}")  # [Security Fix]
    # def warning(self, msg): print(f"[WARN] {msg}")  # [Security Fix]
    # def error(self, msg): print(f"[ERROR] {msg}")  # [Security Fix]


def test_design_compliance():
    """Test the validate_design_compliance function with mock data."""

    # print("=" * 60)  # [Security Fix]
    # print("🧪 Testing Canon Validator - Design Compliance Check")  # [Security Fix]
    # print("=" * 60)  # [Security Fix]

    # Initialize validator and mock tools
    validator = CanonValidator()
    mock_tools = MockMCPTools()
    logger = MockLogger()

    # Pass tools as dictionary (not object)
    tools = {
        'read_text_file': mock_tools.read_text_file,
        'get_variable_defs': mock_tools.get_variable_defs,
        'search_records': mock_tools.search_records,
        'edit_file': mock_tools.edit_file,
        'string_set': mock_tools.string_set
    }

    # Test Case 1: File with hardcoded hex values
    # print("\n--- Test Case 1: File with Hardcoded Values ---")  # [Security Fix]
    result = validator.validate_design_compliance(
        file_path="src/Button.tsx",
        component_id="FigmaNode-12345",
        tools=tools,
        logger=logger
    )
    # print("\nResult:", json.dumps(result, indent=2))  # [Security Fix]

    # Test Case 2: Clean file without hardcoded values
    # print("\n" + "=" * 60)  # [Security Fix]
    # print("\n--- Test Case 2: Clean File (No Hardcoded Values) ---")  # [Security Fix]
    result = validator.validate_design_compliance(
        file_path="src/CleanButton.tsx",
        component_id="FigmaNode-12345",
        tools=tools,
        logger=logger
    )
    # print("\nResult:", json.dumps(result, indent=2))  # [Security Fix]

    # Test Case 3: Non-existent file
    # print("\n" + "=" * 60)  # [Security Fix]
    # print("\n--- Test Case 3: File Not Found ---")  # [Security Fix]
    result = validator.validate_design_compliance(
        file_path="src/NonExistent.tsx",
        component_id="FigmaNode-12345",
        tools=tools,
        logger=logger
    )
    # print("\nResult:", json.dumps(result, indent=2))  # [Security Fix]

    # print("\n" + "=" * 60)  # [Security Fix]
    # print("✅ Test completed!")  # [Security Fix]


if __name__ == "__main__":
    test_design_compliance()

