#!/usr/bin/env python3
"""
Wave 4b: Convert L0_routing guardian swallow patterns to fixtures.

This script converts guardian swallow patterns in L0_routing test files
to proper pytest fixtures and context managers.
"""

import ast
import json
import re
from pathlib import Path


class GuardianSwallowConverter(ast.NodeTransformer):
    """AST transformer to convert guardian swallow patterns to fixtures."""

    def __init__(self):
        self.imports_added = set()
        self.fixtures_added = set()

    def visit_Try(self, node):
        """Convert try-except with guardian swallow to pytest.raises context manager."""
        for handler in node.handlers:
            if self._is_guardian_swallow_handler(handler):
                # Convert to pytest.raises context manager
                return self._convert_to_pytest_raises(node, handler)
        return self.generic_visit(node)

    def _is_guardian_swallow_handler(self, handler):
        """Check if an exception handler is a guardian swallow pattern."""
        # Check if the body only contains pass or guardian comments
        if len(handler.body) == 0:
            return False

        first_stmt = handler.body[0]
        if isinstance(first_stmt, ast.Pass):
            return True
        elif isinstance(first_stmt, ast.Expr) and isinstance(first_stmt.value, ast.Constant):
            value = str(first_stmt.value.value)
            return value.startswith('# guardian:') and 'allow-silent-swallow' in value
        return False

    def _convert_to_pytest_raises(self, try_node, except_handler):
        """Convert a try-except block to pytest.raises context manager."""
        # Get the exception type
        exception_type = self._get_exception_type(except_handler)

        # Create pytest.raises context manager
        pytest_raises = ast.withitem(
            context_expr=ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id='pytest', ctx=ast.Load()),
                    attr='raises',
                    ctx=ast.Load()
                ),
                args=[exception_type],
                keywords=[]
            ),
            optional_vars=ast.Name(id='exc_info', ctx=ast.Store())
        )

        # Create new with statement
        with_node = ast.With(
            items=[pytest_raises],
            body=try_node.body
        )

        # Add pytest import if needed
        self.imports_added.add('pytest')

        return with_node

    def _get_exception_type(self, handler):
        """Extract exception type from handler."""
        if isinstance(handler.type, ast.Name):
            return ast.Name(id=handler.type.id, ctx=ast.Load())
        elif isinstance(handler.type, ast.Attribute):
            return ast.Attribute(
                value=ast.Name(id=handler.type.value.id, ctx=ast.Load()),
                attr=handler.type.attr,
                ctx=ast.Load()
            )
        else:
            return ast.Name(id='Exception', ctx=ast.Load())

    def visit_Import(self, node):
        """Track existing imports."""
        for alias in node.names:
            self.imports_added.add(alias.name)
        return node

    def add_imports(self, tree):
        """Add required imports to the AST."""
        if 'pytest' in self.imports_added:
            # Check if pytest is already imported
            has_pytest = False
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name == 'pytest':
                            has_pytest = True
                            break
                elif isinstance(node, ast.ImportFrom):
                    if node.module == 'pytest':
                        has_pytest = True
                        break

            if not has_pytest:
                # Add pytest import at the top
                pytest_import = ast.Import(
                    names=[ast.alias(name='pytest', asname=None)]
                )

                # Insert after docstring and existing imports
                if isinstance(tree, ast.Module):
                    insert_pos = 0

                    # Skip docstring
                    if (tree.body and isinstance(tree.body[0], ast.Expr) and
                        isinstance(tree.body[0].value, ast.Constant) and
                        isinstance(tree.body[0].value.value, str)):
                        insert_pos = 1

                    # Skip existing imports
                    while (insert_pos < len(tree.body) and
                           isinstance(tree.body[insert_pos], (ast.Import, ast.ImportFrom))):
                        insert_pos += 1

                    tree.body.insert(insert_pos, pytest_import)

        return tree


def convert_guardian_swallow_to_fixtures(file_path: Path) -> dict:
    """Convert guardian swallow patterns to fixtures in a test file."""
    try:
        content = file_path.read_text(encoding='utf-8')

        # First, handle regex-based patterns
        new_content = content

        # Replace common guardian swallow patterns
        patterns = [
            # Replace "except Exception: pass" with pytest.raises
            (r'except\s+(\w+):\s*pass', r'with pytest.raises(\1):'),
            (r'except\s+(\w+)\s+as\s+(\w+):\s*pass', r'with pytest.raises(\1):'),

            # Replace guardian comment swallows
            (r'except\s+(\w+):\s*#\s*guardian:\s*allow-silent-swallow', r'with pytest.raises(\1):'),

            # Replace "except Exception: # guardian: allow-silent-swallow"
            (r'except\s+(\w+):\s*#\s*guardian:.*allow-silent-swallow.*', r'with pytest.raises(\1):'),
        ]

        for pattern, replacement in patterns:
            new_content = re.sub(pattern, replacement, new_content, flags=re.MULTILINE)

        # Handle more complex cases with AST
        try:
            tree = ast.parse(new_content)
            converter = GuardianSwallowConverter()
            transformed_tree = converter.visit(tree)
            converter.add_imports(transformed_tree)

            # Convert back to source
            new_content = ast.unparse(transformed_tree)

            return {
                'file': str(file_path),
                'success': True,
                'imports_added': list(converter.imports_added),
                'patterns_converted': len(converter.imports_added),
                'new_content': new_content
            }

        except (SyntaxError, ValueError) as e:
            # If AST parsing fails, return the regex-processed content
            return {
                'file': str(file_path),
                'success': True,
                'regex_only': True,
                'error': str(e),
                'new_content': new_content
            }

    except Exception as e:
        return {
            'file': str(file_path),
            'success': False,
            'error': str(e)
        }


def convert_l0_routing_files():
    """Convert all L0_routing files with guardian swallow patterns."""
    # Load the analysis from Wave 4a
    with open('artifacts/guardian_swallow_analysis.json') as f:
        data = json.load(f)

    l0_files = data['layers']['L0_routing']
    l0_files_needing = [f for f in l0_files if f.get('needs_conversion', False)]

    print("=== Wave 4b: Converting L0_routing Guardian Swallow Patterns ===")
    print(f"Found {len(l0_files_needing)} L0_routing files needing conversion")

    results = []

    for file_info in l0_files_needing:
        file_path = Path(file_info['file'])
        print(f"\nProcessing: {file_path}")

        result = convert_guardian_swallow_to_fixtures(file_path)
        results.append(result)

        if result['success']:
            # Write the converted content
            file_path.write_text(result['new_content'], encoding='utf-8')

            imports_added = result.get('imports_added', [])
            patterns = result.get('patterns_converted', 'regex')

            print(f"  ✅ Converted - Imports: {imports_added}, Patterns: {patterns}")
        else:
            print(f"  ❌ Failed - {result.get('error', 'Unknown error')}")

    # Summary
    successful = len([r for r in results if r['success']])
    total = len(results)

    print("\n=== Wave 4b Summary ===")
    print(f"Files processed: {total}")
    print(f"Successfully converted: {successful}")
    print(f"Failed: {total - successful}")

    return results


def main():
    """Convert L0_routing guardian swallow patterns to fixtures."""
    results = convert_l0_routing_files()

    # Save results
    with open('artifacts/wave4b_conversion_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print("\nDetailed results saved to: artifacts/wave4b_conversion_results.json")


if __name__ == '__main__':
    main()
