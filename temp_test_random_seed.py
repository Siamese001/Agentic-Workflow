import ast

code = """
import random
random.seed(42)
"""

tree = ast.parse(code)

# Test the symbol extraction
class TestVisitor(ast.NodeVisitor):
    def visit_Call(self, node):
        sym = self._extract_symbol(node.func)
        print(f"Found call: {sym}")

    @staticmethod
    def _extract_symbol(node):
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            parts = []
            curr = node
            while isinstance(curr, ast.Attribute):
                parts.append(curr.attr)
                curr = curr.value
            if isinstance(curr, ast.Name):
                parts.append(curr.id)
            return ".".join(reversed(parts))
        return ""

TestVisitor().visit(tree)
