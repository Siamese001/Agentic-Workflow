"""
File: C:/Git/Agentic-Workflow/tests/test_ast_disposition.py
Context: Mandatory rigorous testing for the AST analyzer to ensure it detects agents accurately before we trust it to refactor.
"""

import unittest
import ast
from scripts.ast_disposition_analyzer import AgentVisitor

class TestAgentVisitor(unittest.TestCase):
    
    def test_detects_langchain_import(self):
        """Test Case 1: Must detect direct langchain imports as Agentic."""
        code = "import langchain\nfrom langchain.chat_models import ChatOpenAI"
        tree = ast.parse(code)
        visitor = AgentVisitor()
        visitor.visit(tree)
        self.assertTrue(visitor.is_agent, "Failed to detect langchain import")
        self.assertIn("Import detected: langchain", visitor.signals)

    def test_detects_agent_inheritance(self):
        """Test Case 2: Must detect inheritance from BaseAgent."""
        code = "class MyWorker(BaseAgent):\n    pass"
        tree = ast.parse(code)
        visitor = AgentVisitor()
        visitor.visit(tree)
        self.assertTrue(visitor.is_agent, "Failed to detect BaseAgent inheritance")

    def test_detects_tool_decorator(self):
        """Test Case 3: Must detect @tool decorators."""
        code = "@tool\ndef my_tool():\n    pass"
        tree = ast.parse(code)
        visitor = AgentVisitor()
        visitor.visit(tree)
        self.assertTrue(visitor.is_agent, "Failed to detect @tool decorator")

    def test_ignores_pure_utils(self):
        """Test Case 4: Must NOT flag pure math/string utilities (Edge Case)."""
        code = "import math\n\ndef add(a, b):\n    return a + b"
        tree = ast.parse(code)
        visitor = AgentVisitor()
        visitor.visit(tree)
        self.assertFalse(visitor.is_agent, "False positive on pure utility code")
        
    def test_detects_openai_import_from(self):
        """Test Case 5: Must detect specific 'from' imports from openai."""
        code = "from openai import OpenAI"
        tree = ast.parse(code)
        visitor = AgentVisitor()
        visitor.visit(tree)
        self.assertTrue(visitor.is_agent, "Failed to detect openai import")

if __name__ == "__main__":
    unittest.main()
